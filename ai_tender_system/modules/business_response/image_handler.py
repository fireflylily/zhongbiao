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
            'seal': ['公章', '盖章', '印章', '公司章'],
            'license': ['营业执照', '营业执照副本', '执照'],
            'qualification': ['资质证书', '资质', '认证证书'],
            'authorization': ['授权书', '授权委托书', '法人授权'],
            'certificate': ['证书', '认证', '资格证']
        }
        
        # 默认图片尺寸（英寸）
        self.default_sizes = {
            'seal': (1.5, 1.5),  # 公章
            'license': (4, 5),    # 营业执照
            'qualification': (4, 5),  # 资质证书
            'authorization': (4, 5),   # 授权书
            'certificate': (4, 5)      # 其他证书
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
        
        # 插入公章
        if image_config.get('seal_path'):
            if self._insert_seal(doc, image_config['seal_path'], insert_points.get('seal')):
                stats['images_inserted'] += 1
                stats['images_types'].append('公章')
            else:
                stats['errors'].append('公章插入失败')
        
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
            
            # 查找公章位置
            for keyword in self.image_keywords['seal']:
                if keyword in text and '处' in text:
                    insert_points['seal'] = {
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph
                    }
                    self.logger.debug(f"找到公章插入点: 段落#{para_idx}")
                    break
            
            # 查找营业执照位置
            for keyword in self.image_keywords['license']:
                if keyword in text:
                    insert_points['license'] = {
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph
                    }
                    self.logger.debug(f"找到营业执照插入点: 段落#{para_idx}")
                    break
            
            # 查找资质证书位置
            for keyword in self.image_keywords['qualification']:
                if keyword in text:
                    insert_points['qualification'] = {
                        'type': 'paragraph',
                        'index': para_idx,
                        'paragraph': paragraph
                    }
                    self.logger.debug(f"找到资质证书插入点: 段落#{para_idx}")
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
                                    self.logger.debug(f"找到{img_type}插入点: 表格#{table_idx}")
        
        return insert_points
    
    def _insert_seal(self, doc: Document, image_path: str, insert_point: Optional[Dict]) -> bool:
        """插入公章"""
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"公章图片不存在: {image_path}")
                return False
            
            if insert_point:
                if insert_point['type'] == 'paragraph':
                    # 在段落后插入
                    paragraph = insert_point['paragraph']
                    # 添加新段落用于插入图片
                    new_para = doc.add_paragraph()
                    new_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT  # 公章通常右对齐
                    run = new_para.add_run()
                    run.add_picture(image_path, width=Inches(self.default_sizes['seal'][0]))
                    
                    # 将新段落移动到目标位置
                    self._move_paragraph_after(doc, new_para, paragraph)
                    
                elif insert_point['type'] == 'table_cell':
                    # 在表格单元格中插入
                    cell = insert_point['cell']
                    # 清空单元格
                    for paragraph in cell.paragraphs:
                        paragraph.clear()
                    # 添加图片
                    paragraph = cell.add_paragraph()
                    run = paragraph.add_run()
                    run.add_picture(image_path, width=Inches(self.default_sizes['seal'][0]))
                
                self.logger.info(f"成功插入公章: {image_path}")
                return True
            else:
                # 没有找到特定位置，在文档末尾添加
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(self.default_sizes['seal'][0]))
                self.logger.info(f"在文档末尾插入公章: {image_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"插入公章失败: {e}")
            return False
    
    def _insert_license(self, doc: Document, image_path: str, insert_point: Optional[Dict]) -> bool:
        """插入营业执照"""
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"营业执照图片不存在: {image_path}")
                return False
            
            # 添加分页符
            doc.add_page_break()
            
            # 添加标题
            title = doc.add_paragraph("营业执照副本")
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if title.runs:
                title.runs[0].font.bold = True
            
            # 插入图片
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run()
            run.add_picture(image_path, width=Inches(self.default_sizes['license'][0]))
            
            self.logger.info(f"成功插入营业执照: {image_path}")
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
            
            # 添加分页符（如果不是第一个资质证书）
            if index == 0:
                doc.add_page_break()
            
            # 添加标题
            title = doc.add_paragraph(f"资质证书 {index + 1}")
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if title.runs:
                title.runs[0].font.bold = True
            
            # 插入图片
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run()
            run.add_picture(image_path, width=Inches(self.default_sizes['qualification'][0]))
            
            self.logger.info(f"成功插入资质证书{index+1}: {image_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"插入资质证书失败: {e}")
            return False
    
    def _move_paragraph_after(self, doc: Document, para_to_move, target_para):
        """将段落移动到目标段落之后"""
        # 这是一个简化的实现，实际可能需要更复杂的XML操作
        # 由于python-docx的限制，这里只是将段落添加到文档末尾
        pass
    
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