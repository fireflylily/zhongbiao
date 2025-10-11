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
        插入图片主方法
        
        Args:
            doc: Word文档对象
            image_config: 图片配置信息，包含图片路径和插入位置
                {
                    'seal_path': '公章图片路径',
                    'license_path': '营业执照路径',
                    'qualification_paths': ['资质证书路径列表'],
                    'insert_positions': {
                        'seal': 'inline',  # inline或specific_position
                        'license': 'appendix'  # 附录
                    }
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
        insert_points = self._scan_insert_points(doc)

        # 插入营业执照
        if image_config.get('license_path'):
            if self._insert_license(doc, image_config['license_path'], insert_points.get('license')):
                stats['images_inserted'] += 1
                stats['images_types'].append('营业执照')
            else:
                stats['errors'].append('营业执照插入失败')
        
        # 插入资质证书
        qualification_paths = image_config.get('qualification_paths', [])
        for idx, path in enumerate(qualification_paths):
            if self._insert_qualification(doc, path, insert_points.get('qualification'), idx):
                stats['images_inserted'] += 1
                stats['images_types'].append(f'资质证书{idx+1}')
            else:
                stats['errors'].append(f'资质证书{idx+1}插入失败')
        
        self.logger.info(f"图片插入完成: 插入了{stats['images_inserted']}张图片")
        
        return stats
    
    def _scan_insert_points(self, doc: Document) -> Dict[str, Any]:
        """扫描文档，查找图片插入点"""
        insert_points = {}
        
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

            # 查找资质证书位置
            for keyword in self.image_keywords['qualification']:
                if keyword in text:
                    insert_points['qualification'] = {
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph
                    }
                    self.logger.info(f"✅ 找到资质证书插入点: 段落#{para_idx}, 文本='{text[:50]}'")
                    break
        
        # 扫描表格中的插入点
        for table_idx, table in enumerate(doc.tables):
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    
                    # 在表格中查找关键词
                    for img_type, keywords in self.image_keywords.items():
                        for keyword in keywords:
                            if keyword in cell_text:
                                if img_type not in insert_points:
                                    insert_points[img_type] = {
                                        'type': 'table_cell',
                                        'table_index': table_idx,
                                        'cell': cell
                                    }
                                    self.logger.info(f"✅ 找到{img_type}插入点: 表格#{table_idx}, 单元格文本='{cell_text[:30]}'")

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
                            insert_point: Optional[Dict], index: int) -> bool:
        """插入资质证书"""
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"资质证书图片不存在: {image_path}")
                return False

            if insert_point and insert_point['type'] == 'paragraph' and index == 0:
                # 第一个资质证书：在找到的段落位置插入
                target_para = insert_point['paragraph']

                # 插入分页符
                page_break_para = self._insert_paragraph_after(target_para)
                page_break_para.add_run().add_break()

                # 插入标题
                title = self._insert_paragraph_after(page_break_para)
                title.text = f"资质证书 {index + 1}"
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                # 插入图片
                img_para = self._insert_paragraph_after(title)
                img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = img_para.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))

                self.logger.info(f"成功在指定位置插入资质证书{index+1}: {image_path}")
                return True

            elif index > 0:
                # 后续资质证书：直接添加到文档末尾（跟在第一个资质证书后面）
                title = doc.add_paragraph(f"资质证书 {index + 1}")
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))

                self.logger.info(f"成功插入资质证书{index+1}: {image_path}")
                return True

            else:
                # 降级：第一个资质证书但没找到插入点，添加到文档末尾
                doc.add_page_break()

                title = doc.add_paragraph(f"资质证书 {index + 1}")
                title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if title.runs:
                    title.runs[0].font.bold = True

                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))

                self.logger.info(f"在文档末尾插入资质证书{index+1}: {image_path}")
                return True

        except Exception as e:
            self.logger.error(f"插入资质证书失败: {e}")
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