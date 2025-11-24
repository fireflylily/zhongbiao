#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档扫描器 - 扫描Word文档查找图片插入位置
"""

import sys
from pathlib import Path
from typing import Dict, Any
from docx import Document

sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger


class DocumentScanner:
    """文档扫描器 - 负责扫描Word文档查找图片插入位置"""

    def __init__(self):
        self.logger = get_module_logger("document_scanner")

        # 图片类型关键词映射
        self.image_keywords = {
            'license': ['营业执照', '营业执照副本', '执照'],
            'qualification': [],  # 清空通用关键词，只使用具体资质类型匹配（避免误匹配"相关资质证书"等泛指文字）
            'authorization': ['授权书', '授权委托书', '法人授权'],
            'certificate': ['证书', '认证', '资格证'],
            'legal_id': [
                '法定代表人身份证复印件', '法定代表人身份证', '法人身份证', '法定代表人身份证明',
                '法人代表身份证', '法人代表身份证复印件',
                '法定代表人居民身份证',  # 新增：正式表述
                '法人居民身份证'  # 新增：简化表述
            ],
            'auth_id': [
                '授权代表身份证', '授权人身份证', '被授权人身份证',
                '授权代表身份证复印件', '被授权人身份证复印件',
                '委托代理人身份证', '代理人身份证复印件',
                '被授权代表身份证', '被授权代表身份证复印件',  # 新增：被授权代表变体
                '授权代表人身份证', '授权代表人身份证复印件',  # 新增：授权代表人变体
                '授权代表居民身份证', '被授权人居民身份证',  # 新增：正式表述
                '身份证复印件',  # 新增：通用表述（优先级低，会在法人身份证后匹配）
                '身份证',  # 新增：最简化表述（优先级最低）
                '居民身份证'  # 新增：正式简化表述
            ],
            'dishonest_executor': ['失信被执行人', '失信被执行人名单'],
            'tax_violation_check': ['重大税收违法', '税收违法案件当事人名单'],
            # 注意：gov_procurement_creditchina 和 gov_procurement_ccgp 使用特殊AND逻辑处理，见下方扫描代码
            'audit_report': ['审计报告', '财务审计报告', '年度审计报告', '会计师事务所出具']
        }

    def scan_insert_points(self, doc: Document, image_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        扫描文档，查找图片插入点（两阶段识别法：核心词+上下文分类）

        Args:
            doc: Word文档对象
            image_config: 图片配置（可选），包含qualification_details用于精确匹配

        Returns:
            插入点字典，键可以是通用类型(license/qualification)或具体资质(iso9001/cmmi等)
        """
        import re

        # 候选位置字典：{img_type: [candidate_dict, ...]}
        candidates = {}

        # 从qualification_matcher导入映射表
        from .qualification_matcher import QUALIFICATION_MAPPING

        # 获取文档总段落数
        total_paragraphs = len(doc.paragraphs)

        # ===== 阶段1：扫描段落，基于核心词识别 =====
        self.logger.info(f"📄 开始扫描文档（共{total_paragraphs}个段落）")

        for para_idx, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if not text:
                continue

            # 获取段落样式名
            style_name = paragraph.style.name if paragraph.style else ''

            # ===== 1. 营业执照识别 =====
            if "营业执照" in text:
                category = self._classify_paragraph(text, para_idx, total_paragraphs, style_name)
                if category != 'exclude':
                    candidates.setdefault('license', []).append({
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph,
                        'category': category,
                        'text': text[:60]
                    })
                    self.logger.info(f"🔍 营业执照候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

            # ===== 2. 身份证识别（支持组合判断）=====
            if "身份证" in text:
                category = self._classify_paragraph(text, para_idx, total_paragraphs, style_name)
                if category != 'exclude':
                    # 判断是哪种身份证
                    has_legal = any(kw in text for kw in ["法定代表人", "法人", "法人代表"])
                    has_auth = any(kw in text for kw in ["授权", "被授权", "代理人", "委托"])

                    # 法人身份证
                    if has_legal:
                        candidates.setdefault('legal_id', []).append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'category': category,
                            'text': text[:60]
                        })
                        self.logger.info(f"🔍 法人身份证候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

                    # 被授权人身份证
                    if has_auth:
                        candidates.setdefault('auth_id', []).append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'category': category,
                            'text': text[:60]
                        })
                        self.logger.info(f"🔍 被授权人身份证候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

                    # 如果两者都没有，可能是通用身份证要求（两者都需要）
                    if not has_legal and not has_auth:
                        # 同时为两种身份证添加候选
                        for id_type in ['legal_id', 'auth_id']:
                            candidates.setdefault(id_type, []).append({
                                'type': 'paragraph',
                                'index': para_idx,
                                'paragraph': paragraph,
                                'category': category,
                                'text': text[:60]
                            })
                        self.logger.info(f"🔍 通用身份证候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

            # ===== 4. 授权书识别 =====
            if "授权" in text and ("授权书" in text or "授权委托书" in text):
                category = self._classify_paragraph(text, para_idx, total_paragraphs, style_name)
                if category != 'exclude':
                    candidates.setdefault('authorization', []).append({
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph,
                        'category': category,
                        'text': text[:60]
                    })
                    self.logger.info(f"🔍 授权书候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

            # ===== 5. 特殊处理：政府采购资质（使用AND逻辑）=====
            if "政府采购严重违法失信" in text:
                category = self._classify_paragraph(text, para_idx, total_paragraphs, style_name)
                if category != 'exclude':
                    # 判断是信用中国还是政府采购网
                    if "信用中国" in text or "creditchina" in text.lower():
                        candidates.setdefault('gov_procurement_creditchina', []).append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'category': category,
                            'text': text[:60]
                        })
                        self.logger.info(f"🔍 政府采购-信用中国候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

                    if "政府采购网" in text or "ccgp" in text.lower():
                        candidates.setdefault('gov_procurement_ccgp', []).append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'category': category,
                            'text': text[:60]
                        })
                        self.logger.info(f"🔍 政府采购-政采网候选: 段落#{para_idx}, 类别={category}, 文本='{text[:60]}'")

            # ===== 6. 查找具体资质类型（ISO9001, CMMI等）=====
            for qual_key, qual_info in QUALIFICATION_MAPPING.items():
                # 跳过已特殊处理的政府采购资质
                if qual_key in ['gov_procurement_creditchina', 'gov_procurement_ccgp']:
                    continue

                keywords = qual_info.get('keywords', [])
                if any(keyword in text for keyword in keywords):
                    category = self._classify_paragraph(text, para_idx, total_paragraphs, style_name)
                    if category != 'exclude':
                        candidates.setdefault(qual_key, []).append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'category': category,
                            'text': text[:60]
                        })
                        matched_kw = next((kw for kw in keywords if kw in text), keywords[0])
                        self.logger.info(f"🔍 {qual_key}候选: 段落#{para_idx}, 类别={category}, 关键词='{matched_kw}'")
                    break  # 找到后停止

        # ===== 扫描表格中的身份证插入点（特殊处理）=====
        self.logger.info(f"📋 开始扫描表格（共{len(doc.tables)}个表格）")

        for table_idx, table in enumerate(doc.tables):
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if not cell_text:
                        continue

                    # 身份证表格特殊处理（检测表格特征）
                    if "身份证" in cell_text:
                        # 检测是否为身份证表格（包含"正反面"、"头像面"等特征）
                        id_table_features = ['正、反面', '正反面', '头像面', '国徽面', '人像面']
                        is_id_table = any(feature in cell_text for feature in id_table_features)

                        if is_id_table:
                            # 判断是哪种身份证
                            has_legal = any(kw in cell_text for kw in ["法定代表人", "法人"])
                            has_auth = any(kw in cell_text for kw in ["授权", "被授权", "代理"])

                            # 法人身份证表格（优先级高）
                            if has_legal:
                                candidates.setdefault('legal_id', []).append({
                                    'type': 'table_cell',
                                    'table_index': table_idx,
                                    'cell': cell,
                                    'category': 'strong_attach',  # 表格特征明确，设为强附件
                                    'text': cell_text[:60]
                                })
                                self.logger.info(f"🔍 法人身份证表格: 表格#{table_idx}, 文本='{cell_text[:60]}'")

                            # 被授权人身份证表格
                            if has_auth:
                                candidates.setdefault('auth_id', []).append({
                                    'type': 'table_cell',
                                    'table_index': table_idx,
                                    'cell': cell,
                                    'category': 'strong_attach',
                                    'text': cell_text[:60]
                                })
                                self.logger.info(f"🔍 被授权人身份证表格: 表格#{table_idx}, 文本='{cell_text[:60]}'")

                            # 通用身份证表格
                            if not has_legal and not has_auth:
                                for id_type in ['legal_id', 'auth_id']:
                                    candidates.setdefault(id_type, []).append({
                                        'type': 'table_cell',
                                        'table_index': table_idx,
                                        'cell': cell,
                                        'category': 'strong_attach',
                                        'text': cell_text[:60]
                                    })
                                self.logger.info(f"🔍 通用身份证表格: 表格#{table_idx}, 文本='{cell_text[:60]}'")

        # ===== 阶段2：选择最佳位置（基于分类优先级）=====
        self.logger.info(f"📊 开始选择最佳插入位置...")

        # 定义分类优先级（数字越大越优先）
        category_priority = {
            'strong_attach': 100,        # 强附件标记（最优）
            'weak_attach': 80,           # 弱附件标记
            'neutral': 50,               # 中性位置
            'chapter': 30,               # 章节标题
            'toc': 10,                   # 目录
            'reference': 5,              # 正文引用
            'requirement_clause': -10,   # 招标要求条款（可用但不推荐）
            'header_noise': -50,         # 文档标题噪音（基本不用）
            'exclude': -999,             # 绝对排除（页眉页脚、附件清单标题）
        }

        insert_points = {}

        for img_type, candidate_list in candidates.items():
            if not candidate_list:
                self.logger.warning(f"⚠️ {img_type}未找到任何候选位置，将使用降级策略（文档末尾）")
                continue

            # 按优先级选择最佳候选
            # 排序规则：1. 类别优先级（高优先） 2. 文本简短（简短优先） 3. 位置靠后（靠后优先）
            best_candidate = max(candidate_list, key=lambda x: (
                category_priority.get(x['category'], 0),  # 先按类别优先级
                -len(x['text']),                          # 文本越短越好（负号实现）
                x.get('index', 0)                         # 位置越靠后越好
            ))

            best_category = best_candidate['category']
            best_priority = category_priority.get(best_category, 0)

            # 构建插入点信息
            insert_point = {
                'type': best_candidate['type'],
                'category': best_category,
                'matched_keyword': best_candidate.get('text', '')[:30]
            }

            if best_candidate['type'] == 'paragraph':
                insert_point['index'] = best_candidate['index']
                insert_point['paragraph'] = best_candidate['paragraph']
            elif best_candidate['type'] == 'table_cell':
                insert_point['table_index'] = best_candidate['table_index']
                insert_point['cell'] = best_candidate['cell']

            insert_points[img_type] = insert_point

            # 友好的日志输出（根据质量级别）
            if best_priority >= 80:
                self.logger.info(
                    f"✅ {img_type}: 找到优质位置 [{best_category}] "
                    f"'{best_candidate['text']}' (共{len(candidate_list)}个候选)"
                )
            elif best_priority >= 30:
                self.logger.info(
                    f"☑️ {img_type}: 找到可用位置 [{best_category}] "
                    f"'{best_candidate['text']}' (共{len(candidate_list)}个候选)"
                )
            elif best_priority >= 0:
                self.logger.warning(
                    f"⚠️ {img_type}: 找到次优位置 [{best_category}] "
                    f"'{best_candidate['text']}' (共{len(candidate_list)}个候选)"
                )
            else:
                self.logger.warning(
                    f"🔻 {img_type}: 仅找到低质量位置 [{best_category}] (评分:{best_priority}) "
                    f"'{best_candidate['text']}' (共{len(candidate_list)}个候选)"
                )

        # 输出扫描总结
        self.logger.info(f"📊 扫描完成: 找到 {len(insert_points)} 个插入点 - {list(insert_points.keys())}")
        return insert_points

    def _classify_paragraph(self, text: str, para_idx: int, total_paras: int,
                           style_name: str = '') -> str:
        """
        段落分类（符合人的判断逻辑）

        分类优先级（从高到低）：
        1. strong_attach      - 强附件标记（编号附件、附件标题） 100分
        2. weak_attach        - 弱附件标记（说明性文字、"后附"） 80分
        3. neutral            - 中性位置（普通段落） 50分
        4. chapter            - 章节标题（不理想但可接受） 30分
        5. toc                - 目录（很不理想） 10分
        6. reference          - 正文引用（最不理想） 5分
        7. requirement_clause - 招标要求条款（可用但不推荐） -10分
        8. header_noise       - 文档标题噪音（基本不用） -50分
        9. exclude            - 绝对排除（页眉页脚、附件清单标题） -999分

        Args:
            text: 段落文本
            para_idx: 段落索引
            total_paras: 文档总段落数
            style_name: Word样式名（可选）

        Returns:
            分类字符串
        """
        import re

        # ========== 1. exclude（绝对排除 - 仅保留技术性禁区）==========

        # 页眉页脚（技术禁区）
        if style_name and ('Header' in style_name or 'Footer' in style_name):
            return 'exclude'

        # 附件清单标题（语义禁区）
        if "附件清单" in text or "附件目录" in text:
            return 'exclude'

        # ========== 2. strong_attach（强附件标记）==========

        # 编号附件（最强信号）- "5-1 营业执照"
        if re.match(r'^\d+[-.]?\d*\s+', text):
            return 'strong_attach'

        # 附件标题 - "附件：营业执照"、"附：营业执照"
        if (text.startswith("附件") or text.startswith("附：")) and len(text) < 50:
            return 'strong_attach'

        # ========== 3. weak_attach（弱附件标记）==========

        # 说明性指示
        if any(pattern in text for pattern in [
            "后附", "如下", "见下", "以下为", "如下所示", "见后"
        ]) and len(text) < 50:
            return 'weak_attach'

        # 包含"附件"但较长（可能是附件说明）
        if "附件" in text and 20 < len(text) < 80:
            return 'weak_attach'

        # ========== 4. chapter（章节标题）==========

        # 检测章节标题
        is_chapter = any([
            text.startswith("第") and ("章" in text or "节" in text or "部分" in text),
            re.match(r'^[一二三四五六七八九十]+[、．.]', text),
            'Heading' in style_name,  # Word样式为标题
        ])

        if is_chapter:
            # 特殊情况：小节标题且简短，可能是插入点
            # 如 "5.1 营业执照副本"
            if re.match(r'^\d+\.\d+', text) and len(text) < 30:
                return 'weak_attach'  # 升级为弱附件
            return 'chapter'

        # ========== 5. toc（目录）==========

        if any([
            "目录" in text,
            "......" in text or "…………" in text,  # 目录特征
            para_idx < total_paras * 0.05,  # 文档前5%
            "TOC" in style_name,  # Word目录样式
        ]):
            return 'toc'

        # ========== 6. reference（正文引用）==========

        # 正文中的引用/描述
        if any(keyword in text for keyword in [
            "根据", "依据", "按照", "参照",
            "记载", "所示", "显示", "颁发的",
        ]) and len(text) > 30:  # 较长的句子
            return 'reference'

        # ========== 7. requirement_clause（招标要求条款 -10分）==========
        # 📌 从exclude降级为负分评分项

        # 招标文件的要求条款
        if any(pattern in text for pattern in [
            "须在响应文件中提供",
            "应在投标文件中提供",
            "投标人须提供", "响应方须提供",
            "投标人需提供", "响应方需提供",
        ]):
            return 'requirement_clause'

        if ("如响应方" in text or "如投标人" in text) and "须" in text:
            return 'requirement_clause'

        # ========== 8. header_noise（文档标题噪音 -50分）==========

        # 文档开头的极短文本
        if len(text) < 10 and para_idx < 3:
            # 如果是关键词标题，正常评分
            if any(kw in text for kw in ['营业执照', '身份证', '授权书', '资质', '证书']):
                return 'neutral'
            else:
                return 'header_noise'

        # ========== 9. neutral（中性位置 - 默认）==========

        return 'neutral'
