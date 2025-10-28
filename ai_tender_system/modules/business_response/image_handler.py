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
from common import get_module_logger

class ImageHandler:
    """图片处理器"""
    
    def __init__(self):
        self.logger = get_module_logger("image_handler")
        
        # 图片类型关键词映射
        self.image_keywords = {
            'license': ['营业执照', '营业执照副本', '执照'],
            'qualification': ['资质证书', '资质', '认证证书'],
            'authorization': ['授权书', '授权委托书', '法人授权'],
            'certificate': ['证书', '认证', '资格证'],
            'legal_id': ['法定代表人身份证复印件', '法定代表人身份证', '法人身份证', '法定代表人身份证明'],
            'auth_id': ['授权代表身份证', '授权人身份证', '被授权人身份证'],
            'dishonest_executor': ['失信被执行人', '失信被执行人名单'],
            'tax_violation_check': ['重大税收违法', '税收违法案件当事人名单'],
            'gov_procurement_creditchina': ['政府采购严重违法失信', '政府采购信用记录'],
            'gov_procurement_ccgp': ['政府采购严重违法失信行为信息记录', '政府采购网查询']
        }

        # 默认图片尺寸（英寸）
        self.default_sizes = {
            'license': (6, 0),    # 营业执照：宽6英寸（约15.24厘米）
            'qualification': (6, 0),  # 资质证书：宽6英寸（约15.24厘米）
            'authorization': (6, 0),   # 授权书：宽6英寸（约15.24厘米）
            'certificate': (6, 0),      # 其他证书：宽6英寸（约15.24厘米）
            'legal_id': (4.5, 0),  # 法人身份证：宽4.5英寸（约11.43厘米）
            'auth_id': (4.5, 0),    # 授权代表身份证：宽4.5英寸（约11.43厘米）
            'dishonest_executor': (6, 0),              # 失信被执行人查询截图：宽6英寸
            'tax_violation_check': (6, 0),             # 税收违法查询截图：宽6英寸
            'gov_procurement_creditchina': (6, 0),     # 信用中国政采查询截图：宽6英寸
            'gov_procurement_ccgp': (6, 0)             # 政府采购网查询截图：宽6英寸
        }
    
    def insert_images(self, doc: Document, image_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        插入图片主方法（支持智能匹配插入位置）

        Args:
            doc: Word文档对象
            image_config: 图片配置信息，包含图片路径和插入位置
                {
                    'seal_path': '公章图片路径',
                    'license_path': '营业执照路径',
                    'qualification_paths': ['资质证书路径列表'],
                    'qualification_details': [  # 新增：资质详细信息
                        {
                            'qual_key': 'iso9001',
                            'file_path': '/path/to/iso9001.jpg',
                            'insert_hint': 'ISO9001质量管理体系'
                        }
                    ]
                }

        Returns:
            处理统计信息
        """
        stats = {
            'images_inserted': 0,
            'images_types': [],
            'errors': []
        }

        # 扫描文档，查找图片插入位置
        insert_points = self._scan_insert_points(doc, image_config)

        # 插入营业执照
        if image_config.get('license_path'):
            if self._insert_license(doc, image_config['license_path'], insert_points.get('license')):
                stats['images_inserted'] += 1
                stats['images_types'].append('营业执照')
            else:
                stats['errors'].append('营业执照插入失败')

        # 插入资质证书（使用详细信息进行精确插入）
        qualification_details = image_config.get('qualification_details', [])
        if qualification_details:
            # 使用新的智能插入逻辑
            for idx, qual_detail in enumerate(qualification_details):
                qual_key = qual_detail.get('qual_key')
                file_path = qual_detail.get('file_path')
                insert_hint = qual_detail.get('insert_hint', '')

                # 查找该资质的插入点
                insert_point = insert_points.get(qual_key) or insert_points.get('qualification')

                if self._insert_qualification(doc, file_path, insert_point, idx, qual_key, insert_hint):
                    stats['images_inserted'] += 1
                    stats['images_types'].append(f'{qual_key}')
                else:
                    stats['errors'].append(f'{qual_key}插入失败')
        else:
            # 降级：使用旧逻辑（无详细信息）
            qualification_paths = image_config.get('qualification_paths', [])
            for idx, path in enumerate(qualification_paths):
                if self._insert_qualification(doc, path, insert_points.get('qualification'), idx):
                    stats['images_inserted'] += 1
                    stats['images_types'].append(f'资质证书{idx+1}')
                else:
                    stats['errors'].append(f'资质证书{idx+1}插入失败')

        # 插入法人身份证（正面和反面）
        legal_id = image_config.get('legal_id')
        if legal_id and isinstance(legal_id, dict):
            front_path = legal_id.get('front')
            back_path = legal_id.get('back')
            if self._insert_id_card(doc, front_path, back_path, insert_points.get('legal_id'), '法定代表人'):
                stats['images_inserted'] += 2  # 正反两面
                stats['images_types'].append('法人身份证')
            else:
                stats['errors'].append('法人身份证插入失败')

        # 插入授权代表身份证（正面和反面）
        auth_id = image_config.get('auth_id')
        if auth_id and isinstance(auth_id, dict):
            front_path = auth_id.get('front')
            back_path = auth_id.get('back')
            if self._insert_id_card(doc, front_path, back_path, insert_points.get('auth_id'), '授权代表'):
                stats['images_inserted'] += 2  # 正反两面
                stats['images_types'].append('授权代表身份证')
            else:
                stats['errors'].append('授权代表身份证插入失败')

        self.logger.info(f"图片插入完成: 插入了{stats['images_inserted']}张图片")

        return stats

    def _calculate_insert_priority(self, para_idx: int, text: str, total_paragraphs: int) -> int:
        """
        计算插入位置的优先级分数（分数越高越优先）

        评分规则：
        1. 包含"附件"字样：+100分（最重要的特征）
        2. 包含附件编号模式（如"5-1"、"附件1"等）：+50分
        3. 段落文本简短（<50字符）：+30分（标题特征）
        4. 在文档后半部分：+20分（附件通常在后面）
        5. 段落索引：+para_idx（越后面的位置分数越高）

        Args:
            para_idx: 段落索引
            text: 段落文本
            total_paragraphs: 文档总段落数

        Returns:
            优先级分数
        """
        import re

        score = 0

        # 规则1：包含"附件"字样（最重要）
        if '附件' in text:
            score += 100
            self.logger.debug(f"  [优先级] '附件'关键词 +100分")

        # 规则2：包含附件编号模式
        # 匹配: "5-1"、"附件1"、"附件一"、"附件 5-1"等
        if re.search(r'附件\s*[\d一二三四五六七八九十]+[-\d]*|^\d+[-\d]+\s+', text):
            score += 50
            self.logger.debug(f"  [优先级] 附件编号模式 +50分")

        # 规则3：段落文本简短（标题特征）
        if len(text) < 50:
            score += 30
            self.logger.debug(f"  [优先级] 文本简短(<50字符) +30分")

        # 规则4：在文档后半部分
        if total_paragraphs > 0 and para_idx > total_paragraphs / 2:
            score += 20
            self.logger.debug(f"  [优先级] 后半部分 +20分")

        # 规则5：段落索引（越后面越优先）
        score += para_idx
        self.logger.debug(f"  [优先级] 段落索引#{para_idx} +{para_idx}分")

        self.logger.debug(f"  [优先级] 总分: {score}")
        return score

    def _scan_insert_points(self, doc: Document, image_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        扫描文档，查找图片插入点（支持智能优先级匹配）

        Args:
            doc: Word文档对象
            image_config: 图片配置（可选），包含qualification_details用于精确匹配

        Returns:
            插入点字典，键可以是通用类型(license/qualification)或具体资质(iso9001/cmmi等)
        """
        # 候选位置字典：{img_type: [(para_idx, paragraph, keyword, score), ...]}
        candidates = {}

        # 获取资质详细信息（用于精确匹配）
        qualification_details = []
        if image_config:
            qualification_details = image_config.get('qualification_details', [])

        # 构建关键词映射（包含具体资质类型）
        # 从qualification_matcher导入映射表
        from .qualification_matcher import QUALIFICATION_MAPPING

        # 获取文档总段落数（用于优先级计算）
        total_paragraphs = len(doc.paragraphs)

        # 第一步：扫描所有段落，收集所有候选位置
        self.logger.info(f"📄 开始扫描文档（共{total_paragraphs}个段落）")

        for para_idx, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()

            # 扫描所有通用图片类型（包括 legal_id, auth_id 等）
            for img_type, keywords in self.image_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        # 计算该位置的优先级分数
                        score = self._calculate_insert_priority(para_idx, text, total_paragraphs)

                        # 添加到候选列表
                        if img_type not in candidates:
                            candidates[img_type] = []

                        candidates[img_type].append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'matched_keyword': keyword,
                            'score': score,
                            'text': text[:50]  # 保存文本片段用于调试
                        })

                        self.logger.info(f"🔍 发现{img_type}候选位置: 段落#{para_idx}, 关键词='{keyword}', 分数={score}, 文本='{text[:50]}'")
                        break  # 找到关键词后停止搜索其他关键词（同一图片类型）

            # 查找具体资质类型的位置（ISO9001, CMMI等）
            for qual_key, qual_info in QUALIFICATION_MAPPING.items():
                for keyword in qual_info.get('keywords', []):
                    if keyword in text:
                        # 计算该位置的优先级分数
                        score = self._calculate_insert_priority(para_idx, text, total_paragraphs)

                        # 添加到候选列表
                        if qual_key not in candidates:
                            candidates[qual_key] = []

                        candidates[qual_key].append({
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'matched_keyword': keyword,
                            'score': score,
                            'text': text[:50]
                        })

                        self.logger.info(f"🔍 发现{qual_key}候选位置: 段落#{para_idx}, 关键词='{keyword}', 分数={score}")
                        break  # 找到关键词后停止搜索其他关键词

        # 扫描表格中的插入点（表格位置不计算优先级，优先级设为0）
        for table_idx, table in enumerate(doc.tables):
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()

                    # 在表格中查找通用关键词
                    for img_type, keywords in self.image_keywords.items():
                        for keyword in keywords:
                            if keyword in cell_text:
                                # 表格位置的优先级固定为0（段落位置更优先）
                                if img_type not in candidates:
                                    candidates[img_type] = []

                                candidates[img_type].append({
                                    'type': 'table_cell',
                                    'table_index': table_idx,
                                    'cell': cell,
                                    'matched_keyword': keyword,
                                    'score': 0,  # 表格位置优先级较低
                                    'text': cell_text[:30]
                                })

                                self.logger.info(f"🔍 发现{img_type}候选位置(表格): 表格#{table_idx}, 关键词='{keyword}', 分数=0")
                                break  # 找到关键词后停止

                    # 在表格中查找具体资质类型
                    for qual_key, qual_info in QUALIFICATION_MAPPING.items():
                        for keyword in qual_info.get('keywords', []):
                            if keyword in cell_text:
                                if qual_key not in candidates:
                                    candidates[qual_key] = []

                                candidates[qual_key].append({
                                    'type': 'table_cell',
                                    'table_index': table_idx,
                                    'cell': cell,
                                    'matched_keyword': keyword,
                                    'score': 0,  # 表格位置优先级较低
                                    'text': cell_text[:30]
                                })

                                self.logger.info(f"🔍 发现{qual_key}候选位置(表格): 表格#{table_idx}, 关键词='{keyword}', 分数=0")
                                break

        # 第二步：为每个图片类型选择最佳位置（分数最高的候选）
        insert_points = {}

        for img_type, candidate_list in candidates.items():
            if not candidate_list:
                continue

            # 按分数排序，选择分数最高的候选
            best_candidate = max(candidate_list, key=lambda x: x['score'])

            # 构建插入点信息
            insert_point = {
                'type': best_candidate['type'],
                'matched_keyword': best_candidate['matched_keyword']
            }

            if best_candidate['type'] == 'paragraph':
                insert_point['index'] = best_candidate['index']
                insert_point['paragraph'] = best_candidate['paragraph']
            elif best_candidate['type'] == 'table_cell':
                insert_point['table_index'] = best_candidate['table_index']
                insert_point['cell'] = best_candidate['cell']

            insert_points[img_type] = insert_point

            # 输出选择结果
            if len(candidate_list) > 1:
                self.logger.info(
                    f"✅ {img_type}最佳位置: {best_candidate['type']}, "
                    f"分数={best_candidate['score']}, "
                    f"文本='{best_candidate['text']}' "
                    f"(共{len(candidate_list)}个候选位置)"
                )
            else:
                self.logger.info(
                    f"✅ {img_type}插入点: {best_candidate['type']}, "
                    f"分数={best_candidate['score']}, "
                    f"文本='{best_candidate['text']}'"
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

    def _insert_license(self, doc: Document, image_path: str, insert_point: Optional[Dict]) -> bool:
        """插入营业执照"""
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"营业执照图片不存在: {image_path}")
                return False

            if insert_point and insert_point['type'] == 'paragraph':
                # 在找到的段落位置插入
                target_para = insert_point['paragraph']

                # 插入分页符
                page_break_para = self._insert_paragraph_after(target_para)
                page_break_para.add_run().add_break()

                # 插入标题
                title = self._insert_paragraph_after(page_break_para)
                title.text = "营业执照副本"
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                # 插入图片
                img_para = self._insert_paragraph_after(title)
                img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = img_para.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['license'][0]))

                self.logger.info(f"成功在指定位置插入营业执照: {image_path}")
                return True
            else:
                # 降级：添加到文档末尾
                doc.add_page_break()

                title = doc.add_paragraph("营业执照副本")
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['license'][0]))

                self.logger.info(f"在文档末尾插入营业执照: {image_path}")
                return True

        except Exception as e:
            self.logger.error(f"插入营业执照失败: {e}")
            return False
    
    def _insert_qualification(self, doc: Document, image_path: str,
                            insert_point: Optional[Dict], index: int,
                            qual_key: str = None, insert_hint: str = None) -> bool:
        """
        插入资质证书（支持智能标题和精确位置）

        Args:
            doc: Word文档对象
            image_path: 图片路径
            insert_point: 插入点信息
            index: 索引（用于排序）
            qual_key: 资质键（如iso9001, cmmi），用于生成更好的标题
            insert_hint: 插入提示（来自项目要求），用于生成标题
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"资质证书图片不存在: {image_path}")
                return False

            # 生成标题（优先使用insert_hint，其次使用qual_key）
            from .qualification_matcher import QUALIFICATION_MAPPING

            if insert_hint:
                title_text = insert_hint[:50]  # 使用项目要求描述作为标题
            elif qual_key and qual_key in QUALIFICATION_MAPPING:
                qual_info = QUALIFICATION_MAPPING[qual_key]
                title_text = f"{qual_info['category']}认证证书"
            else:
                title_text = f"资质证书 {index + 1}"

            if insert_point and insert_point['type'] == 'paragraph' and index == 0:
                # 第一个资质证书：在找到的段落位置插入
                target_para = insert_point['paragraph']

                # 插入分页符
                page_break_para = self._insert_paragraph_after(target_para)
                page_break_para.add_run().add_break()

                # 插入标题
                title = self._insert_paragraph_after(page_break_para)
                title.text = title_text
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                # 插入图片
                img_para = self._insert_paragraph_after(title)
                img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = img_para.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))

                self.logger.info(f"✅ 在指定位置插入 {qual_key or '资质证书'}: {title_text}")
                return True

            elif index > 0:
                # 后续资质证书：直接添加到文档末尾（跟在第一个资质证书后面）
                title = doc.add_paragraph(title_text)
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))

                self.logger.info(f"✅ 插入 {qual_key or '资质证书'}: {title_text}")
                return True

            else:
                # 降级：第一个资质证书但没找到插入点，添加到文档末尾
                doc.add_page_break()

                title = doc.add_paragraph(title_text)
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))

                self.logger.info(f"✅ 在文档末尾插入 {qual_key or '资质证书'}: {title_text}")
                return True

        except Exception as e:
            self.logger.error(f"❌ 插入资质证书失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

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
            id_type: 身份证类型（如 '法定代表人' 或 '授权代表'）

        Returns:
            bool: 插入是否成功
        """
        try:
            # 验证图片是否存在
            if not front_path or not os.path.exists(front_path):
                self.logger.error(f"{id_type}身份证正面图片不存在: {front_path}")
                return False

            if not back_path or not os.path.exists(back_path):
                self.logger.error(f"{id_type}身份证反面图片不存在: {back_path}")
                return False

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

                    # 插入分页符
                    page_break_para = self._insert_paragraph_after(target_para)
                    page_break_para.add_run().add_break()

                    # 插入标题
                    title = self._insert_paragraph_after(page_break_para)
                    title.text = f"{id_type}身份证"
                    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if title.runs:
                        title.runs[0].font.bold = True

                    # 创建表格（1行2列，用于并排显示正反面）
                    from lxml.etree import QName
                    from docx.table import Table

                    # 在title后插入一个段落作为表格占位符
                    table_placeholder = self._insert_paragraph_after(title)

                    # 使用文档的add_table方法创建表格
                    temp_table = doc.add_table(rows=2, cols=2)

                    # 移动表格到正确位置
                    table_element = temp_table._element
                    table_placeholder._element.addprevious(table_element)
                    table_placeholder._element.getparent().remove(table_placeholder._element)

                    # 创建Table对象
                    table = Table(table_element, doc)
                    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

                    # 第一行：标签
                    table.rows[0].cells[0].text = "正面"
                    table.rows[0].cells[1].text = "反面"
                    for cell in table.rows[0].cells:
                        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        if cell.paragraphs[0].runs:
                            cell.paragraphs[0].runs[0].font.bold = True

                    # 第二行：图片
                    front_cell = table.rows[1].cells[0]
                    front_cell.text = ""
                    front_para = front_cell.paragraphs[0]
                    front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    front_run = front_para.add_run()
                    front_run.add_picture(front_path, width=Cm(id_width_cm))

                    back_cell = table.rows[1].cells[1]
                    back_cell.text = ""
                    back_para = back_cell.paragraphs[0]
                    back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    back_run = back_para.add_run()
                    back_run.add_picture(back_path, width=Cm(id_width_cm))

                    self.logger.info(f"✅ 成功在指定位置插入{id_type}身份证（新建表格）: 正面={front_path}, 反面={back_path}")
                    return True

            else:
                # 降级：添加到文档末尾
                doc.add_page_break()

                title = doc.add_paragraph(f"{id_type}身份证")
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                # 创建表格（2行2列）
                table = doc.add_table(rows=2, cols=2)
                table.alignment = WD_ALIGN_PARAGRAPH.CENTER

                # 第一行：标签
                table.rows[0].cells[0].text = "正面"
                table.rows[0].cells[1].text = "反面"
                for cell in table.rows[0].cells:
                    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if cell.paragraphs[0].runs:
                        cell.paragraphs[0].runs[0].font.bold = True

                # 第二行：图片
                front_cell = table.rows[1].cells[0]
                front_cell.text = ""
                front_para = front_cell.paragraphs[0]
                front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                front_run = front_para.add_run()
                front_run.add_picture(front_path, width=Cm(id_width_cm))

                back_cell = table.rows[1].cells[1]
                back_cell.text = ""
                back_para = back_cell.paragraphs[0]
                back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                back_run = back_para.add_run()
                back_run.add_picture(back_path, width=Cm(id_width_cm))

                self.logger.info(f"✅ 在文档末尾插入{id_type}身份证（并排）: 正面={front_path}, 反面={back_path}")
                return True

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
            num_cols = len(table.columns)
            num_rows = len(table.rows)

            self.logger.info(f"现有表格结构: {num_rows}行 x {num_cols}列")

            # 输出表格第一行的内容（标题行）
            if num_rows > 0:
                header_texts = [cell.text.strip() for cell in table.rows[0].cells]
                self.logger.info(f"表格标题行: {header_texts}")

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
                target_row = table.rows[target_row_idx]

                self.logger.info(f"📍 将插入到: 行{target_row_idx}, 正面列{front_col_idx}, 反面列{back_col_idx}")

                # 插入正面图片
                front_cell = target_row.cells[front_col_idx]
                front_cell.text = ""  # 清空现有文本
                front_para = front_cell.paragraphs[0] if front_cell.paragraphs else front_cell.add_paragraph()
                front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                front_run = front_para.add_run()
                front_run.add_picture(front_path, width=Cm(id_width_cm))

                # 插入反面图片
                back_cell = target_row.cells[back_col_idx]
                back_cell.text = ""  # 清空现有文本
                back_para = back_cell.paragraphs[0] if back_cell.paragraphs else back_cell.add_paragraph()
                back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                back_run = back_para.add_run()
                back_run.add_picture(back_path, width=Cm(id_width_cm))

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

                # 插入正面图片（在"人像面"标题的下一行）
                if front_row_idx is not None and front_row_idx + 1 < num_rows:
                    front_cell = table.rows[front_row_idx + 1].cells[0]
                    front_cell.text = ""  # 清空现有文本
                    front_para = front_cell.paragraphs[0] if front_cell.paragraphs else front_cell.add_paragraph()
                    front_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    front_run = front_para.add_run()
                    front_run.add_picture(front_path, width=Cm(id_width_cm))
                    self.logger.info(f"✅ 已插入正面图片到第{front_row_idx + 1}行")
                else:
                    self.logger.warning(f"⚠️ 未找到正面插入位置")

                # 插入反面图片（在"国徽面"标题的下一行）
                if back_row_idx is not None and back_row_idx + 1 < num_rows:
                    back_cell = table.rows[back_row_idx + 1].cells[0]
                    back_cell.text = ""  # 清空现有文本
                    back_para = back_cell.paragraphs[0] if back_cell.paragraphs else back_cell.add_paragraph()
                    back_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    back_run = back_para.add_run()
                    back_run.add_picture(back_path, width=Cm(id_width_cm))
                    self.logger.info(f"✅ 已插入反面图片到第{back_row_idx + 1}行")
                else:
                    self.logger.warning(f"⚠️ 未找到反面插入位置")

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