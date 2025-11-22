#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片插入模块 - 处理商务应答模板中的图片插入
包括公司公章、资质证明等图片的插入
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from docx import Document
from docx.shared import Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, resolve_file_path

class ImageHandler:
    """图片处理器"""

    def __init__(self):
        self.logger = get_module_logger("image_handler")

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
            'gov_procurement_creditchina': ['政府采购严重违法失信', '政府采购信用记录'],
            'gov_procurement_ccgp': ['政府采购严重违法失信行为信息记录', '政府采购网查询'],
            'audit_report': ['审计报告', '财务审计报告', '年度审计报告', '会计师事务所出具']
        }

        # 默认图片尺寸（英寸）
        self.default_sizes = {
            'license': (6, 0),    # 营业执照：宽6英寸（约15.24厘米）
            'qualification': (6, 0),  # 资质证书：宽6英寸（约15.24厘米）
            'authorization': (6, 0),   # 授权书：宽6英寸（约15.24厘米）
            'certificate': (6, 0),      # 其他证书：宽6英寸（约15.24厘米）
            'legal_id': (4.5, 0),  # 法人身份证：宽4.5英寸（约11.43厘米）
            'auth_id': (4.5, 0),    # 被授权人身份证：宽4.5英寸（约11.43厘米）
            'dishonest_executor': (6, 0),              # 失信被执行人查询截图：宽6英寸
            'tax_violation_check': (6, 0),             # 税收违法查询截图：宽6英寸
            'gov_procurement_creditchina': (6, 0),     # 信用中国政采查询截图：宽6英寸
            'gov_procurement_ccgp': (6, 0),            # 政府采购网查询截图：宽6英寸
            'audit_report': (6, 0)                     # 审计报告：宽6英寸
        }

    def _resolve_file_path(self, file_path: str) -> str:
        """
        解析文件路径（支持相对路径和绝对路径）

        使用公共的resolve_file_path函数处理路径解析
        """
        if not file_path:
            return file_path

        resolved = resolve_file_path(file_path)
        if resolved:
            self.logger.debug(f"路径解析: {file_path} -> {resolved}")
            return str(resolved)
        else:
            self.logger.warning(f"无法解析文件路径: {file_path}")
            return file_path
    
    def insert_images(self, doc: Document, image_config: Dict[str, Any],
                     required_quals: List[Dict] = None) -> Dict[str, Any]:
        """
        插入图片主方法（模板驱动 + 统计追踪）

        核心逻辑：
        1. 扫描模板占位符
        2. 填充所有有文件的占位符（成功填充）
        3. 记录有占位符但无文件的资质（缺失资质）
        4. 追加项目要求但模板没有占位符的资质（追加资质）

        Args:
            doc: Word文档对象
            image_config: 图片配置信息，包含所有资质
                {
                    'license_path': '营业执照路径',
                    'qualification_paths': ['资质证书路径列表'],
                    'qualification_details': [  # 资质详细信息
                        {
                            'qual_key': 'iso9001',
                            'file_path': '/path/to/iso9001.jpg',
                            'insert_hint': 'ISO9001质量管理体系'
                        }
                    ]
                }
            required_quals: 项目资格要求列表（可选，用于追加和统计）

        Returns:
            详细统计信息：
            {
                'images_inserted': 10,
                'images_types': ['营业执照', 'iso9001', ...],
                'errors': [],
                'filled_qualifications': [{'qual_key': 'iso9001', 'qual_name': '...'}],
                'missing_qualifications': [{'qual_key': 'cmmi', 'qual_name': '...'}],
                'appended_qualifications': [{'qual_key': 'level_protection', ...}]
            }
        """
        # 初始化统计数据
        stats = {
            'images_inserted': 0,
            'images_types': [],
            'errors': [],
            'filled_qualifications': [],      # 成功填充的资质
            'missing_qualifications': [],     # 缺失的资质（有占位符无文件）
            'appended_qualifications': []     # 追加的资质（项目要求但无占位符）
        }

        # 扫描文档，查找图片插入位置
        insert_points = self._scan_insert_points(doc, image_config)

        # 从qualification_matcher导入映射表（用于获取资质名称）
        from .qualification_matcher import QUALIFICATION_MAPPING

        # 【重构】构建统一的资质列表
        all_resources = self._build_resource_list(image_config)
        self.logger.info(f"📋 构建资质列表完成，共 {len(all_resources)} 项资质待插入")

        # 【重构】统一循环插入所有资质
        for idx, resource in enumerate(all_resources):
            resource_key = resource.get('key')
            # 查找插入点（优先使用具体key，降级使用通用key）
            insert_point = insert_points.get(resource_key)
            if not insert_point and resource.get('type') == 'single_image' and resource_key != 'license':
                # 资质证书可以降级使用通用 'qualification' 插入点
                insert_point = insert_points.get('qualification')

            # 调用统一分发方法
            self._insert_resource(doc, resource, insert_point, stats, idx)

        # 步骤：检测缺失的资质（模板有占位符但公司无文件）
        self._detect_missing_qualifications(insert_points, image_config, stats, QUALIFICATION_MAPPING)

        # 步骤：追加项目要求但模板没有占位符的资质
        if required_quals:
            self._append_required_qualifications(
                doc, required_quals, insert_points, image_config, stats, QUALIFICATION_MAPPING
            )

        # 输出统计摘要
        self.logger.info(f"📊 图片插入完成:")
        self.logger.info(f"  - 插入图片: {stats['images_inserted']}张")
        self.logger.info(f"  - 成功填充资质: {len(stats['filled_qualifications'])}个")
        self.logger.info(f"  - 缺失资质: {len(stats['missing_qualifications'])}个")
        self.logger.info(f"  - 追加资质: {len(stats['appended_qualifications'])}个")

        return stats

    def _classify_paragraph(self, text: str, para_idx: int, total_paras: int,
                           style_name: str = '') -> str:
        """
        段落分类（符合人的判断逻辑）

        分类优先级（从高到低）：
        1. exclude       - 绝对排除（招标要求、页眉页脚、附件清单）
        2. strong_attach - 强附件标记（编号附件、附件标题）
        3. weak_attach   - 弱附件标记（说明性文字、"后附"）
        4. neutral       - 中性位置（普通段落）
        5. chapter       - 章节标题（不理想但可接受）
        6. toc           - 目录（很不理想）
        7. reference     - 正文引用（最不理想）

        Args:
            text: 段落文本
            para_idx: 段落索引
            total_paras: 文档总段落数
            style_name: Word样式名（可选）

        Returns:
            分类字符串
        """
        import re

        # ========== 1. exclude（绝对排除）==========

        # 招标文件的要求条款
        if any(pattern in text for pattern in [
            "须在响应文件中提供",
            "应在投标文件中提供",
        ]):
            return 'exclude'

        if ("如响应方" in text or "如投标人" in text) and "须" in text:
            return 'exclude'

        if any(pattern in text for pattern in [
            "投标人须提供", "响应方须提供",
            "投标人需提供", "响应方需提供",
        ]):
            return 'exclude'

        # 页眉页脚（通过样式名或位置判断）
        if style_name and ('Header' in style_name or 'Footer' in style_name):
            return 'exclude'

        if len(text) < 10 and para_idx < 3:  # 文档开头的极短文本
            return 'exclude'

        # 附件清单标题（不是插入点）
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

        # ========== 7. neutral（中性位置）==========

        return 'neutral'

    def _scan_insert_points(self, doc: Document, image_config: Dict[str, Any] = None) -> Dict[str, Any]:
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

            # ===== 5. 查找具体资质类型（ISO9001, CMMI等）=====
            for qual_key, qual_info in QUALIFICATION_MAPPING.items():
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
            'strong_attach': 100,  # 强附件标记
            'weak_attach': 80,     # 弱附件标记
            'neutral': 50,         # 中性位置
            'chapter': 30,         # 章节标题
            'toc': 10,             # 目录
            'reference': 5,        # 正文引用
            'exclude': -999,       # 不应该出现在候选中
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
                x['index']                                # 位置越靠后越好
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
            else:
                self.logger.warning(
                    f"⚠️ {img_type}: 仅找到低质量位置 [{best_category}] "
                    f"'{best_candidate['text']}' (共{len(candidate_list)}个候选)"
                )

        # 输出扫描总结
        self.logger.info(f"📊 扫描完成: 找到 {len(insert_points)} 个插入点 - {list(insert_points.keys())}")
        return insert_points

    def _insert_paragraph_after(self, target_para):
        """在目标段落后插入新段落

        Args:
            target_para: 目标段落对象

        Returns:
            新创建的段落对象
        """
        try:
            from lxml.etree import QName
            from docx.text.paragraph import Paragraph

            # 使用底层XML操作在目标段落后插入新段落
            # 注意：makeelement 需要使用 QName 来指定带命名空间的标签
            w_namespace = target_para._element.nsmap.get('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
            new_p_element = target_para._element.makeelement(QName(w_namespace, 'p'), nsmap=target_para._element.nsmap)
            target_para._element.addnext(new_p_element)

            # 将新创建的 XML 元素包装为 Paragraph 对象并返回
            parent = target_para._parent
            new_paragraph = Paragraph(new_p_element, parent)

            return new_paragraph

        except Exception as e:
            # 输出详细错误信息用于调试
            self.logger.error(f"❌ 在段落后插入新段落失败: {e}")
            self.logger.error(f"  目标段落文本: '{target_para.text[:100] if target_para.text else ''}'")
            self.logger.error(f"  父容器类型: {type(target_para._parent).__name__}")
            self.logger.error(f"  段落对象: {target_para}")
            raise

    def _find_next_table_after_paragraph(self, paragraph):
        """查找段落后面的第一个表格

        Args:
            paragraph: 目标段落对象

        Returns:
            Table对象，如果没有找到返回None
        """
        try:
            from docx.table import Table

            # 获取段落的XML元素
            para_element = paragraph._element

            # 遍历段落后面的兄弟元素
            for sibling in para_element.itersiblings():
                # 检查是否是表格元素 (<w:tbl>)
                if sibling.tag.endswith('}tbl'):
                    # 找到表格，包装成Table对象返回
                    parent = paragraph._parent
                    table = Table(sibling, parent)
                    return table
                # 如果遇到段落或其他元素，停止搜索
                elif sibling.tag.endswith('}p'):
                    # 遇到其他段落，说明表格不是紧跟着的
                    break

            return None

        except Exception as e:
            self.logger.error(f"查找段落后表格失败: {e}")
            return None

    def _insert_id_card(self, doc: Document, front_path: str, back_path: str,
                        insert_point: Optional[Dict], id_type: str) -> bool:
        """
        插入身份证图片（正面和反面并排显示）

        支持两种模式：
        1. 如果段落后有现有表格，插入到表格单元格中
        2. 如果没有表格，创建新表格

        Args:
            doc: Word文档对象
            front_path: 身份证正面图片路径
            back_path: 身份证反面图片路径
            insert_point: 插入点信息
            id_type: 身份证类型（如 '法定代表人' 或 '被授权人'）

        Returns:
            bool: 插入是否成功
        """
        try:
            # 解析并验证图片路径（支持相对路径）
            if not front_path:
                self.logger.error(f"{id_type}身份证正面图片路径为空")
                return False

            front_path_resolved = self._resolve_file_path(front_path)
            if not os.path.exists(front_path_resolved):
                self.logger.error(f"{id_type}身份证正面图片不存在: {front_path} (resolved: {front_path_resolved})")
                return False

            if not back_path:
                self.logger.error(f"{id_type}身份证反面图片路径为空")
                return False

            back_path_resolved = self._resolve_file_path(back_path)
            if not os.path.exists(back_path_resolved):
                self.logger.error(f"{id_type}身份证反面图片不存在: {back_path} (resolved: {back_path_resolved})")
                return False

            # 使用解析后的路径
            front_path = front_path_resolved
            back_path = back_path_resolved

            # 使用7厘米宽度
            id_width_cm = 7

            if insert_point and insert_point['type'] == 'paragraph':
                # 在找到的段落位置插入
                target_para = insert_point['paragraph']

                # 检查段落后是否有现有表格
                existing_table = self._find_next_table_after_paragraph(target_para)

                if existing_table:
                    # 模式1：使用现有表格
                    self.logger.info(f"检测到段落后有现有表格，将插入到表格中")
                    return self._insert_id_into_existing_table(
                        existing_table, front_path, back_path, id_width_cm, id_type
                    )
                else:
                    # 模式2：创建新表格
                    self.logger.info(f"段落后没有表格，将创建新表格")

                    # 【修复】先验证图片文件，避免后续失败
                    try:
                        from PIL import Image
                        # 验证正面图片
                        img_front = Image.open(front_path)
                        front_size = img_front.size
                        self.logger.info(f"  验证正面图片: {Path(front_path).name}, 尺寸={front_size}")
                        img_front.close()

                        # 验证反面图片
                        img_back = Image.open(back_path)
                        back_size = img_back.size
                        self.logger.info(f"  验证反面图片: {Path(back_path).name}, 尺寸={back_size}")
                        img_back.close()
                    except Exception as e:
                        self.logger.error(f"❌ 图片验证失败: {e}")
                        self.logger.error(f"  正面图片: {front_path}, 存在={os.path.exists(front_path)}")
                        self.logger.error(f"  反面图片: {back_path}, 存在={os.path.exists(back_path)}")
                        return False

                    # 【修复】使用简化的表格创建逻辑（避免复杂DOM操作）
                    try:
                        # 插入分页符
                        page_break_para = self._insert_paragraph_after(target_para)
                        page_break_para.add_run().add_break()
                        self.logger.info(f"  ✓ 已插入分页符")

                        # 插入标题
                        title = self._insert_paragraph_after(page_break_para)
                        title.text = f"{id_type}身份证"
                        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        if title.runs:
                            title.runs[0].font.bold = True
                        self.logger.info(f"  ✓ 已插入标题: {id_type}身份证")

                        # 【关键修复】使用最简单可靠的方法：在文档末尾创建表格，然后移动到正确位置
                        # 这种方法避免了复杂的DOM操作，更加稳定
                        from docx.table import Table
                        from docx.oxml import OxmlElement

                        # 【修复】确保文档有section（节），python-docx创建表格需要section信息
                        if len(doc.sections) == 0:
                            self.logger.warning(f"  ⚠️ 文档缺少section定义，正在添加默认section")
                            doc.add_section()
                            self.logger.info(f"  ✓ 已添加默认section")

                        # 方法1：直接在title后添加表格（最简单）
                        # 先创建一个临时段落
                        temp_para = self._insert_paragraph_after(title)

                        # 在文档末尾创建表格
                        table = doc.add_table(rows=2, cols=2)
                        table.alignment = WD_ALIGN_PARAGRAPH.CENTER

                        # 将表格移动到临时段落的位置
                        table._element.getparent().remove(table._element)
                        temp_para._element.addprevious(table._element)

                        # 删除临时段落
                        temp_para._element.getparent().remove(temp_para._element)

                        self.logger.info(f"  ✓ 已创建表格 (2行x2列)")

                        # 第一行：标签
                        table.rows[0].cells[0].text = "正面"
                        table.rows[0].cells[1].text = "反面"
                        for cell in table.rows[0].cells:
                            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                            if cell.paragraphs[0].runs:
                                cell.paragraphs[0].runs[0].font.bold = True
                        self.logger.info(f"  ✓ 已设置表格标题行")

                        # 第二行：图片
                        self.logger.info(f"  开始插入图片...")

                        # 插入正面图片
                        front_cell = table.rows[1].cells[0]
                        front_cell.text = ""
                        front_para = front_cell.paragraphs[0]
                        front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        front_run = front_para.add_run()
                        front_run.add_picture(front_path, width=Cm(id_width_cm))
                        self.logger.info(f"  ✓ 正面图片已插入: {Path(front_path).name}")

                        # 插入反面图片
                        back_cell = table.rows[1].cells[1]
                        back_cell.text = ""
                        back_para = back_cell.paragraphs[0]
                        back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        back_run = back_para.add_run()
                        back_run.add_picture(back_path, width=Cm(id_width_cm))
                        self.logger.info(f"  ✓ 反面图片已插入: {Path(back_path).name}")

                        self.logger.info(f"✅ 成功在指定位置插入{id_type}身份证（新建表格）")
                        return True

                    except Exception as table_error:
                        self.logger.error(f"❌ 创建表格或插入图片失败: {table_error}")
                        self.logger.error(f"  错误类型: {type(table_error).__name__}")
                        import traceback
                        self.logger.error(f"  完整堆栈:\n{traceback.format_exc()}")

                        # 【TODO】理想情况下应该回滚已插入的标题和分页符，但由于复杂性暂时保留
                        # 至少在日志中清晰标记失败
                        return False

            elif insert_point and insert_point['type'] == 'table_cell':
                # 【修复】处理表格单元格类型的插入点
                # 通过 table_index 从 doc.tables 获取表格对象
                table_idx = insert_point['table_index']
                self.logger.info(f"检测到table_cell类型插入点，表格索引={table_idx}")

                # 从文档中获取表格对象
                table = doc.tables[table_idx]

                # 直接使用现有的表格插入方法
                self.logger.info(f"将使用现有表格插入身份证图片")
                return self._insert_id_into_existing_table(
                    table, front_path, back_path, id_width_cm, id_type
                )

            else:
                # 降级：添加到文档末尾
                self.logger.info(f"未找到插入点，将在文档末尾创建{id_type}身份证")

                # 【修复】先验证图片文件
                try:
                    from PIL import Image
                    # 验证正面图片
                    img_front = Image.open(front_path)
                    front_size = img_front.size
                    self.logger.info(f"  验证正面图片: {Path(front_path).name}, 尺寸={front_size}")
                    img_front.close()

                    # 验证反面图片
                    img_back = Image.open(back_path)
                    back_size = img_back.size
                    self.logger.info(f"  验证反面图片: {Path(back_path).name}, 尺寸={back_size}")
                    img_back.close()
                except Exception as e:
                    self.logger.error(f"❌ 图片验证失败: {e}")
                    self.logger.error(f"  正面图片: {front_path}, 存在={os.path.exists(front_path)}")
                    self.logger.error(f"  反面图片: {back_path}, 存在={os.path.exists(back_path)}")
                    return False

                # 【修复】添加详细的步骤日志
                try:
                    doc.add_page_break()
                    self.logger.info(f"  ✓ 已添加分页符")

                    title = doc.add_paragraph(f"{id_type}身份证")
                    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if title.runs:
                        title.runs[0].font.bold = True
                    self.logger.info(f"  ✓ 已添加标题: {id_type}身份证")

                    # 【修复】确保文档有section（节），python-docx创建表格需要section信息
                    if len(doc.sections) == 0:
                        self.logger.warning(f"  ⚠️ 文档缺少section定义，正在添加默认section")
                        doc.add_section()
                        self.logger.info(f"  ✓ 已添加默认section")

                    # 创建表格（2行2列）
                    table = doc.add_table(rows=2, cols=2)
                    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    self.logger.info(f"  ✓ 已创建表格 (2行x2列)")

                    # 第一行：标签
                    table.rows[0].cells[0].text = "正面"
                    table.rows[0].cells[1].text = "反面"
                    for cell in table.rows[0].cells:
                        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        if cell.paragraphs[0].runs:
                            cell.paragraphs[0].runs[0].font.bold = True
                    self.logger.info(f"  ✓ 已设置表格标题行")

                    # 第二行：图片
                    self.logger.info(f"  开始插入图片...")

                    # 插入正面图片
                    front_cell = table.rows[1].cells[0]
                    front_cell.text = ""
                    front_para = front_cell.paragraphs[0]
                    front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    front_run = front_para.add_run()
                    front_run.add_picture(front_path, width=Cm(id_width_cm))
                    self.logger.info(f"  ✓ 正面图片已插入: {Path(front_path).name}")

                    # 插入反面图片
                    back_cell = table.rows[1].cells[1]
                    back_cell.text = ""
                    back_para = back_cell.paragraphs[0]
                    back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    back_run = back_para.add_run()
                    back_run.add_picture(back_path, width=Cm(id_width_cm))
                    self.logger.info(f"  ✓ 反面图片已插入: {Path(back_path).name}")

                    self.logger.info(f"✅ 在文档末尾插入{id_type}身份证成功")
                    return True

                except Exception as fallback_error:
                    self.logger.error(f"❌ 在文档末尾插入身份证失败: {fallback_error}")
                    self.logger.error(f"  错误类型: {type(fallback_error).__name__}")
                    import traceback
                    self.logger.error(f"  完整堆栈:\n{traceback.format_exc()}")
                    return False

        except Exception as e:
            self.logger.error(f"❌ 插入{id_type}身份证失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _insert_id_into_existing_table(self, table, front_path: str, back_path: str,
                                       id_width_cm: float, id_type: str) -> bool:
        """
        将身份证图片插入到现有表格中

        Args:
            table: 现有表格对象
            front_path: 身份证正面图片路径
            back_path: 身份证反面图片路径
            id_width_cm: 图片宽度（厘米）
            id_type: 身份证类型

        Returns:
            bool: 插入是否成功
        """
        try:
            # 【修复】增强边界检查：验证表格结构
            if not table or not hasattr(table, 'columns') or not hasattr(table, 'rows'):
                self.logger.error(f"❌ 无效的表格对象")
                return False

            num_cols = len(table.columns)
            num_rows = len(table.rows)

            # 【修复】检查表格是否为空
            if num_cols == 0 or num_rows == 0:
                self.logger.error(f"❌ 表格为空: {num_rows}行 x {num_cols}列")
                return False

            self.logger.info(f"现有表格结构: {num_rows}行 x {num_cols}列")

            # 输出表格第一行的内容（标题行）
            if num_rows > 0:
                try:
                    header_texts = [cell.text.strip() for cell in table.rows[0].cells]
                    self.logger.info(f"表格标题行: {header_texts}")
                except Exception as e:
                    self.logger.warning(f"⚠️ 无法读取表格标题行: {e}")

            if num_cols >= 2:
                # 情况1: 表格有2列或更多列
                # 智能识别"头像面"和"国徽面"列
                front_col_idx = None
                back_col_idx = None

                # 扫描第一行，识别列标题
                if num_rows > 0:
                    for col_idx, cell in enumerate(table.rows[0].cells):
                        cell_text = cell.text.strip()

                        # 识别正面列（头像面）
                        if any(keyword in cell_text for keyword in ['头像面', '正面', '人像面']):
                            front_col_idx = col_idx
                            self.logger.info(f"✅ 识别到正面列: 第{col_idx}列 ('{cell_text}')")

                        # 识别反面列（国徽面）
                        if any(keyword in cell_text for keyword in ['国徽面', '反面', '国徽']):
                            back_col_idx = col_idx
                            self.logger.info(f"✅ 识别到反面列: 第{col_idx}列 ('{cell_text}')")

                # 降级策略：如果无法识别列标题，使用默认索引
                if front_col_idx is None or back_col_idx is None:
                    if num_cols == 2:
                        # 2列表格：假设 [正面, 反面]
                        front_col_idx = 0
                        back_col_idx = 1
                        self.logger.warning(f"⚠️ 无法识别列标题，使用默认2列模式: 正面=列0, 反面=列1")
                    else:
                        # 3+列表格：假设 [序号, 正面, 反面]（跳过第一列）
                        front_col_idx = 1
                        back_col_idx = 2
                        self.logger.warning(f"⚠️ 无法识别列标题，使用默认3+列模式: 正面=列1, 反面=列2")

                # 确定插入的行（优先第二行，即索引1）
                target_row_idx = 1 if num_rows >= 2 else 0

                # 【修复】边界检查：确保目标行存在
                if target_row_idx >= num_rows:
                    self.logger.error(f"❌ 目标行索引{target_row_idx}超出范围(总行数={num_rows})")
                    return False

                target_row = table.rows[target_row_idx]

                # 【修复】边界检查：确保列索引有效
                if front_col_idx >= num_cols or back_col_idx >= num_cols:
                    self.logger.error(
                        f"❌ 列索引超出范围: 正面列{front_col_idx}, 反面列{back_col_idx}, "
                        f"总列数={num_cols}"
                    )
                    return False

                self.logger.info(f"📍 将插入到: 行{target_row_idx}, 正面列{front_col_idx}, 反面列{back_col_idx}")

                # 【修复】增强错误处理：插入正面图片
                try:
                    front_cell = target_row.cells[front_col_idx]
                    front_cell.text = ""  # 清空现有文本
                    front_para = front_cell.paragraphs[0] if front_cell.paragraphs else front_cell.add_paragraph()
                    front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    front_run = front_para.add_run()
                    front_run.add_picture(front_path, width=Cm(id_width_cm))
                    self.logger.info(f"  ✅ 正面图片已插入到列{front_col_idx}")
                except IndexError as e:
                    self.logger.error(
                        f"❌ 访问单元格失败: 行{target_row_idx}, 列{front_col_idx}, "
                        f"表格结构={num_rows}x{num_cols}, 错误: {e}"
                    )
                    return False
                except Exception as e:
                    self.logger.error(f"❌ 插入正面图片失败: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    return False

                # 【修复】增强错误处理：插入反面图片
                try:
                    back_cell = target_row.cells[back_col_idx]
                    back_cell.text = ""  # 清空现有文本
                    back_para = back_cell.paragraphs[0] if back_cell.paragraphs else back_cell.add_paragraph()
                    back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    back_run = back_para.add_run()
                    back_run.add_picture(back_path, width=Cm(id_width_cm))
                    self.logger.info(f"  ✅ 反面图片已插入到列{back_col_idx}")
                except IndexError as e:
                    self.logger.error(
                        f"❌ 访问单元格失败: 行{target_row_idx}, 列{back_col_idx}, "
                        f"表格结构={num_rows}x{num_cols}, 错误: {e}"
                    )
                    return False
                except Exception as e:
                    self.logger.error(f"❌ 插入反面图片失败: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    return False

                self.logger.info(f"✅ 已将{id_type}身份证插入到现有表格（行{target_row_idx}，正面=列{front_col_idx}，反面=列{back_col_idx}）")
                return True

            elif num_cols == 1:
                # 情况2: 表格只有1列（垂直布局）
                # 需要找到"人像面"和"国徽面"标题行，分别在它们下方插入图片
                front_row_idx = None
                back_row_idx = None

                # 扫描表格，查找"人像面"和"国徽面"标题行
                for row_idx, row in enumerate(table.rows):
                    cell_text = row.cells[0].text.strip()

                    # 识别"人像面"标题行
                    if any(keyword in cell_text for keyword in ['人像面', '头像面', '正面']):
                        front_row_idx = row_idx
                        self.logger.info(f"✅ 识别到正面标题行: 第{row_idx}行 ('{cell_text}')")

                    # 识别"国徽面"标题行
                    if any(keyword in cell_text for keyword in ['国徽面', '反面', '国徽']):
                        back_row_idx = row_idx
                        self.logger.info(f"✅ 识别到反面标题行: 第{row_idx}行 ('{cell_text}')")

                # 【修复】增强错误处理：插入正面图片（在"人像面"标题的下一行）
                if front_row_idx is not None and front_row_idx + 1 < num_rows:
                    try:
                        front_cell = table.rows[front_row_idx + 1].cells[0]
                        front_cell.text = ""  # 清空现有文本
                        front_para = front_cell.paragraphs[0] if front_cell.paragraphs else front_cell.add_paragraph()
                        front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        front_run = front_para.add_run()
                        front_run.add_picture(front_path, width=Cm(id_width_cm))
                        self.logger.info(f"✅ 已插入正面图片到第{front_row_idx + 1}行")
                    except IndexError as e:
                        self.logger.error(
                            f"❌ 访问单元格失败: 行{front_row_idx + 1}, 列0, "
                            f"表格结构={num_rows}x{num_cols}, 错误: {e}"
                        )
                    except Exception as e:
                        self.logger.error(f"❌ 插入正面图片失败: {e}")
                        import traceback
                        self.logger.error(traceback.format_exc())
                else:
                    self.logger.warning(f"⚠️ 未找到正面插入位置 (front_row_idx={front_row_idx}, num_rows={num_rows})")

                # 【修复】增强错误处理：插入反面图片（在"国徽面"标题的下一行）
                if back_row_idx is not None and back_row_idx + 1 < num_rows:
                    try:
                        back_cell = table.rows[back_row_idx + 1].cells[0]
                        back_cell.text = ""  # 清空现有文本
                        back_para = back_cell.paragraphs[0] if back_cell.paragraphs else back_cell.add_paragraph()
                        back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        back_run = back_para.add_run()
                        back_run.add_picture(back_path, width=Cm(id_width_cm))
                        self.logger.info(f"✅ 已插入反面图片到第{back_row_idx + 1}行")
                    except IndexError as e:
                        self.logger.error(
                            f"❌ 访问单元格失败: 行{back_row_idx + 1}, 列0, "
                            f"表格结构={num_rows}x{num_cols}, 错误: {e}"
                        )
                    except Exception as e:
                        self.logger.error(f"❌ 插入反面图片失败: {e}")
                        import traceback
                        self.logger.error(traceback.format_exc())
                else:
                    self.logger.warning(f"⚠️ 未找到反面插入位置 (back_row_idx={back_row_idx}, num_rows={num_rows})")

                self.logger.info(f"✅ 已将{id_type}身份证插入到现有表格（1列垂直模式）")
                return True

            else:
                self.logger.error(f"表格列数异常: {num_cols}")
                return False

        except Exception as e:
            self.logger.error(f"插入到现有表格失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def validate_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """验证图片文件"""
        validation_result = {
            'valid': [],
            'invalid': [],
            'missing': []
        }
        
        for path in image_paths:
            if not path:
                continue
                
            if not os.path.exists(path):
                validation_result['missing'].append(path)
            elif not self._is_valid_image(path):
                validation_result['invalid'].append(path)
            else:
                validation_result['valid'].append(path)
        
        return validation_result
    
    def _is_valid_image(self, path: str) -> bool:
        """检查是否为有效的图片文件"""
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        ext = Path(path).suffix.lower()
        return ext in valid_extensions

    def _detect_missing_qualifications(self, insert_points: Dict, image_config: Dict,
                                      stats: Dict, qual_mapping: Dict) -> None:
        """
        检测缺失的资质（模板有占位符但公司无对应文件）

        Args:
            insert_points: 扫描到的插入点字典
            image_config: 图片配置（包含公司已上传的资质）
            stats: 统计信息字典（会被修改）
            qual_mapping: 资质映射表（QUALIFICATION_MAPPING）
        """
        # 获取公司已上传的资质keys
        uploaded_qual_keys = set()
        qualification_details = image_config.get('qualification_details', [])
        for qual_detail in qualification_details:
            qual_key = qual_detail.get('qual_key')
            if qual_key:
                uploaded_qual_keys.add(qual_key)

        # 遍历所有发现的占位符
        for placeholder_key in insert_points.keys():
            # 跳过基础类型（license, legal_id等，这些不是资质证书）
            if placeholder_key in ['license', 'qualification', 'legal_id', 'auth_id',
                                   'authorization', 'certificate']:
                continue

            # 检查该占位符是否有对应的公司资质文件
            if placeholder_key not in uploaded_qual_keys:
                # 有占位符但无文件 → 缺失资质
                qual_name = qual_mapping.get(placeholder_key, {}).get('category', placeholder_key)
                stats['missing_qualifications'].append({
                    'qual_key': placeholder_key,
                    'qual_name': qual_name,
                    'placeholder': insert_points[placeholder_key].get('matched_keyword', '')
                })
                self.logger.warning(f"⚠️  缺失资质: {placeholder_key} ({qual_name}) - 模板有占位符但公司未上传")

    def _append_required_qualifications(self, doc: Document, required_quals: List[Dict],
                                       insert_points: Dict, image_config: Dict,
                                       stats: Dict, qual_mapping: Dict) -> None:
        """
        追加项目要求但模板没有占位符的资质

        Args:
            doc: Word文档对象
            required_quals: 项目资格要求列表
            insert_points: 已扫描的插入点
            image_config: 图片配置
            stats: 统计信息字典（会被修改）
            qual_mapping: 资质映射表
        """
        # 获取公司已上传的资质（key -> file_path映射）
        uploaded_quals_map = {}
        qualification_details = image_config.get('qualification_details', [])
        for qual_detail in qualification_details:
            qual_key = qual_detail.get('qual_key')
            file_path = qual_detail.get('file_path')
            if qual_key and file_path:
                uploaded_quals_map[qual_key] = qual_detail

        # 遍历项目要求的资质
        for req_qual in required_quals:
            qual_key = req_qual.get('qual_key')
            if not qual_key:
                continue

            # 判断条件：项目要求 + 公司有文件 + 模板无占位符
            has_file = qual_key in uploaded_quals_map
            has_placeholder = (qual_key in insert_points or 'qualification' in insert_points)

            if has_file and not has_placeholder:
                # 需要追加：项目要求且公司有文件，但模板没有对应占位符
                qual_detail = uploaded_quals_map[qual_key]
                file_path = qual_detail['file_path']
                insert_hint = req_qual.get('source_detail', '')
                qual_name = qual_mapping.get(qual_key, {}).get('category', qual_key)

                # 在文档末尾追加该资质
                try:
                    if self._append_qualification_to_end(doc, file_path, qual_key, insert_hint):
                        stats['images_inserted'] += 1
                        stats['images_types'].append(f'{qual_key}_appended')
                        stats['appended_qualifications'].append({
                            'qual_key': qual_key,
                            'qual_name': qual_name,
                            'file_path': file_path,
                            'reason': '项目要求但模板无占位符'
                        })
                        self.logger.info(f"✅ 追加资质: {qual_key} ({qual_name}) - 项目要求但模板无占位符")
                    else:
                        self.logger.error(f"❌ 追加资质失败: {qual_key}")
                except Exception as e:
                    self.logger.error(f"❌ 追加资质异常: {qual_key}, 错误: {e}")

    def _append_qualification_to_end(self, doc: Document, image_path: str,
                                    qual_key: str, insert_hint: str = None) -> bool:
        """
        在文档末尾追加资质证书

        Args:
            doc: Word文档对象
            image_path: 图片路径
            qual_key: 资质键
            insert_hint: 插入提示（用于生成标题）

        Returns:
            bool: 是否成功
        """
        try:
            # 解析路径（支持相对路径）
            resolved_path = self._resolve_file_path(image_path)
            if not os.path.exists(resolved_path):
                self.logger.error(f"资质图片不存在: {image_path} (resolved: {resolved_path})")
                return False
            image_path = resolved_path  # 使用解析后的路径

            # 生成标题（优先级: display_title > insert_hint > category + "认证证书"）
            from .qualification_matcher import QUALIFICATION_MAPPING
            if qual_key in QUALIFICATION_MAPPING:
                qual_info = QUALIFICATION_MAPPING[qual_key]
                # 优先使用 display_title（如果存在）
                if 'display_title' in qual_info:
                    title_text = qual_info['display_title']
                elif insert_hint:
                    title_text = insert_hint[:50]
                else:
                    title_text = f"{qual_info['category']}认证证书"
            elif insert_hint:
                title_text = insert_hint[:50]
            else:
                title_text = f"资质证书 ({qual_key})"

            # 添加分页符
            doc.add_page_break()

            # 添加标题
            title = doc.add_paragraph(title_text)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if title.runs:
                title.runs[0].font.bold = True

            # 添加图片
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run()
            run.add_picture(image_path, width=Inches(self.default_sizes.get(qual_key, (6, 0))[0]))

            self.logger.info(f"✅ 已在文档末尾追加资质: {title_text}")
            return True

        except Exception as e:
            self.logger.error(f"❌ 追加资质到文档末尾失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _build_resource_list(self, image_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        构建统一的资质列表（用于循环插入）

        将image_config转换为统一格式的资质列表，每个资质包含：
        - type: 资质类型 ('single_image' 或 'id_card')
        - key: 资质键（用于查找插入点）
        - title: 显示标题
        - metadata: 其他信息（路径、页码等）

        Args:
            image_config: 图片配置字典

        Returns:
            统一格式的资质列表
        """
        resources = []

        # 1. 营业执照
        if image_config.get('license_path'):
            resources.append({
                'type': 'single_image',
                'key': 'license',
                'path': image_config['license_path'],
                'title': '营业执照副本',
                'qual_key': 'license',
                'insert_hint': None,
                'is_first_page': True,
                'page_num': 1
            })

        # 2. 法人身份证
        legal_id = image_config.get('legal_id')
        if legal_id and isinstance(legal_id, dict):
            front = legal_id.get('front')
            back = legal_id.get('back')
            if front and back:
                resources.append({
                    'type': 'id_card',
                    'key': 'legal_id',
                    'front': front,
                    'back': back,
                    'title': '法定代表人身份证',
                    'id_type': '法定代表人'
                })

        # 3. 被授权人身份证
        auth_id = image_config.get('auth_id')
        if auth_id and isinstance(auth_id, dict):
            front = auth_id.get('front')
            back = auth_id.get('back')
            if front and back:
                resources.append({
                    'type': 'id_card',
                    'key': 'auth_id',
                    'front': front,
                    'back': back,
                    'title': '被授权人身份证',
                    'id_type': '被授权人'
                })

        # 4. 资质证书（分组处理多页PDF）
        qualification_details = image_config.get('qualification_details', [])
        if qualification_details:
            # 按qual_key分组
            grouped_quals = {}
            for qual_detail in qualification_details:
                qual_key = qual_detail.get('qual_key')
                if qual_key:
                    if qual_key not in grouped_quals:
                        grouped_quals[qual_key] = []
                    grouped_quals[qual_key].append(qual_detail)

            # 对每组内的页面按page_num排序
            for qual_key, details in grouped_quals.items():
                details.sort(key=lambda x: x.get('page_num', 0))

            # 为每一页创建resource
            for qual_key, details_group in grouped_quals.items():
                is_multi_page = len(details_group) > 1

                for page_idx, qual_detail in enumerate(details_group):
                    resources.append({
                        'type': 'single_image',
                        'key': qual_key,
                        'path': qual_detail.get('file_path'),
                        'title': None,  # 由插入方法生成
                        'qual_key': qual_key,
                        'insert_hint': qual_detail.get('insert_hint', ''),
                        'is_first_page': (page_idx == 0),
                        'is_multi_page': is_multi_page,
                        'page_num': qual_detail.get('page_num', page_idx + 1),
                        'total_pages': len(details_group)
                    })

        return resources

    def _insert_single_image(self, doc: Document, resource: Dict[str, Any],
                            insert_point: Optional[Dict], index: int = 0) -> bool:
        """
        插入单张图片（营业执照、资质证书通用方法）

        合并了 _insert_license 和 _insert_qualification 的公共逻辑

        Args:
            doc: Word文档对象
            resource: 资质信息字典
            insert_point: 插入点信息
            index: 索引（用于生成默认标题）

        Returns:
            bool: 插入是否成功
        """
        try:
            # 提取资质信息
            image_path = resource.get('path')
            qual_key = resource.get('qual_key', resource.get('key'))
            insert_hint = resource.get('insert_hint')
            is_first_page = resource.get('is_first_page', True)
            page_num = resource.get('page_num', 1)

            # 解析路径（支持相对路径）
            resolved_path = self._resolve_file_path(image_path)
            if not os.path.exists(resolved_path):
                self.logger.error(f"{qual_key}图片不存在: {image_path} (resolved: {resolved_path})")
                return False
            image_path = resolved_path

            # 生成标题
            if resource.get('title'):
                # 使用预设标题（如"营业执照副本"）
                title_text = resource['title']
            else:
                # 智能生成标题（资质证书）
                from .qualification_matcher import QUALIFICATION_MAPPING
                if qual_key and qual_key in QUALIFICATION_MAPPING:
                    qual_info = QUALIFICATION_MAPPING[qual_key]
                    if 'display_title' in qual_info:
                        title_text = qual_info['display_title']
                    elif insert_hint:
                        title_text = insert_hint[:50]
                    else:
                        title_text = f"{qual_info['category']}认证证书"
                elif insert_hint:
                    title_text = insert_hint[:50]
                else:
                    title_text = f"资质证书 {index + 1}"

            # 获取图片宽度
            width_inches = self.default_sizes.get(qual_key, (6, 0))[0]

            # 插入逻辑
            if insert_point and insert_point['type'] == 'paragraph':
                # 在找到的段落位置插入
                target_para = insert_point['paragraph']

                # 多页优化：只在第一页插入分页符和标题
                if is_first_page:
                    # 插入分页符
                    page_break_para = self._insert_paragraph_after(target_para)
                    page_break_para.add_run().add_break()

                    # 插入标题
                    title = self._insert_paragraph_after(page_break_para)
                    title.text = title_text
                    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if title.runs:
                        title.runs[0].font.bold = True

                    # 记录位置供后续页使用
                    self._last_insert_para = title
                    log_msg = f"✅ 在指定位置插入 {qual_key} 标题: {title_text}"
                else:
                    # 后续页：从上次插入位置继续
                    if hasattr(self, '_last_insert_para'):
                        title = self._last_insert_para
                    else:
                        title = target_para
                    log_msg = f"✅ 继续插入 {qual_key} 第{page_num}页"

                # 插入图片
                img_para = self._insert_paragraph_after(title)
                img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = img_para.add_run()
                run.add_picture(image_path, width=Inches(width_inches))

                # 更新插入位置
                self._last_insert_para = img_para

                self.logger.info(log_msg)
                return True

            else:
                # 降级：添加到文档末尾
                if is_first_page:
                    doc.add_page_break()

                    title = doc.add_paragraph(title_text)
                    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if title.runs:
                        title.runs[0].font.bold = True

                    self._last_insert_para = title
                    log_msg = f"✅ 在文档末尾插入 {qual_key} 标题: {title_text}"
                else:
                    log_msg = f"✅ 继续在文档末尾插入 {qual_key} 第{page_num}页"

                # 插入图片
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(width_inches))

                # 更新插入位置
                self._last_insert_para = paragraph

                self.logger.info(log_msg)
                return True

        except Exception as e:
            self.logger.error(f"❌ 插入{resource.get('key')}失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _insert_resource(self, doc: Document, resource: Dict[str, Any],
                        insert_point: Optional[Dict], stats: Dict, index: int = 0) -> None:
        """
        统一的资质插入分发方法

        根据资质类型分发到具体的插入方法，并统一更新统计信息

        Args:
            doc: Word文档对象
            resource: 资质信息字典
            insert_point: 插入点信息
            stats: 统计信息字典（会被修改）
            index: 索引（用于生成默认标题）
        """
        resource_type = resource.get('type')
        resource_key = resource.get('key')

        try:
            # 根据类型分发
            if resource_type == 'single_image':
                # 单张图片（营业执照、资质证书）
                success = self._insert_single_image(doc, resource, insert_point, index)

                if success:
                    stats['images_inserted'] += 1
                    page_num = resource.get('page_num', 1)
                    stats['images_types'].append(f"{resource_key}_p{page_num}" if page_num > 1 else resource_key)

                    # 只在第一页记录到 filled_qualifications
                    if resource.get('is_first_page', True) and resource_key != 'license':
                        from .qualification_matcher import QUALIFICATION_MAPPING
                        qual_name = QUALIFICATION_MAPPING.get(resource_key, {}).get('category', resource_key)
                        stats['filled_qualifications'].append({
                            'qual_key': resource_key,
                            'qual_name': qual_name,
                            'file_path': resource.get('path'),
                            'total_pages': resource.get('total_pages', 1)
                        })
                        total_pages = resource.get('total_pages', 1)
                        self.logger.info(f"✅ 填充资质: {resource_key} ({qual_name}), {total_pages}页")
                else:
                    page_num = resource.get('page_num', 1)
                    stats['errors'].append(f"{resource_key}_p{page_num}插入失败" if page_num > 1 else f"{resource_key}插入失败")

            elif resource_type == 'id_card':
                # 身份证（正反面表格）
                front_path = resource.get('front')
                back_path = resource.get('back')
                id_type = resource.get('id_type', '身份证')

                success = self._insert_id_card(doc, front_path, back_path, insert_point, id_type)

                if success:
                    stats['images_inserted'] += 2  # 正反两面
                    stats['images_types'].append(f"{id_type}身份证")
                else:
                    stats['errors'].append(f"{id_type}身份证插入失败")

        except Exception as e:
            self.logger.error(f"❌ 插入资质 {resource_key} 异常: {e}")
            stats['errors'].append(f"{resource_key}插入异常")