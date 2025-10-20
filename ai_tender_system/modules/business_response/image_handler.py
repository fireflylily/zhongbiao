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
            'certificate': ['证书', '认证', '资格证']
        }

        # 默认图片尺寸（英寸）
        self.default_sizes = {
            'license': (6, 0),    # 营业执照：宽6英寸（约15.24厘米）
            'qualification': (6, 0),  # 资质证书：宽6英寸（约15.24厘米）
            'authorization': (6, 0),   # 授权书：宽6英寸（约15.24厘米）
            'certificate': (6, 0)      # 其他证书：宽6英寸（约15.24厘米）
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

        self.logger.info(f"图片插入完成: 插入了{stats['images_inserted']}张图片")

        return stats
    
    def _scan_insert_points(self, doc: Document, image_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        扫描文档，查找图片插入点（支持智能匹配）

        Args:
            doc: Word文档对象
            image_config: 图片配置（可选），包含qualification_details用于精确匹配

        Returns:
            插入点字典，键可以是通用类型(license/qualification)或具体资质(iso9001/cmmi等)
        """
        insert_points = {}

        # 获取资质详细信息（用于精确匹配）
        qualification_details = []
        if image_config:
            qualification_details = image_config.get('qualification_details', [])

        # 构建关键词映射（包含具体资质类型）
        # 从qualification_matcher导入映射表
        from .qualification_matcher import QUALIFICATION_MAPPING

        for para_idx, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()

            # 查找营业执照位置
            for keyword in self.image_keywords['license']:
                if keyword in text:
                    insert_points['license'] = {
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph
                    }
                    self.logger.info(f"✅ 找到营业执照插入点: 段落#{para_idx}, 文本='{text[:50]}'")
                    break

            # 查找资质证书位置（通用）
            for keyword in self.image_keywords['qualification']:
                if keyword in text and 'qualification' not in insert_points:
                    insert_points['qualification'] = {
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph
                    }
                    self.logger.info(f"✅ 找到资质证书插入点（通用）: 段落#{para_idx}, 文本='{text[:50]}'")
                    break

            # 查找具体资质类型的位置（ISO9001, CMMI等）
            for qual_key, qual_info in QUALIFICATION_MAPPING.items():
                if qual_key in insert_points:
                    continue  # 已找到,跳过

                for keyword in qual_info.get('keywords', []):
                    if keyword in text:
                        insert_points[qual_key] = {
                            'type': 'paragraph',
                            'index': para_idx,
                            'paragraph': paragraph,
                            'matched_keyword': keyword
                        }
                        self.logger.info(f"✅ 找到{qual_key}插入点: 段落#{para_idx}, 关键词='{keyword}'")
                        break

        # 扫描表格中的插入点
        for table_idx, table in enumerate(doc.tables):
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()

                    # 在表格中查找通用关键词
                    for img_type, keywords in self.image_keywords.items():
                        for keyword in keywords:
                            if keyword in cell_text and img_type not in insert_points:
                                insert_points[img_type] = {
                                    'type': 'table_cell',
                                    'table_index': table_idx,
                                    'cell': cell
                                }
                                self.logger.info(f"✅ 找到{img_type}插入点: 表格#{table_idx}, 单元格文本='{cell_text[:30]}'")

                    # 在表格中查找具体资质类型
                    for qual_key, qual_info in QUALIFICATION_MAPPING.items():
                        if qual_key in insert_points:
                            continue

                        for keyword in qual_info.get('keywords', []):
                            if keyword in cell_text:
                                insert_points[qual_key] = {
                                    'type': 'table_cell',
                                    'table_index': table_idx,
                                    'cell': cell,
                                    'matched_keyword': keyword
                                }
                                self.logger.info(f"✅ 找到{qual_key}插入点: 表格#{table_idx}, 关键词='{keyword}'")
                                break

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