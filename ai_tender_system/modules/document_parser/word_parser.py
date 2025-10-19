#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word文档解析器
使用python-docx解析Word文档（DOCX格式）
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re
import tempfile
import os

try:
    from docx import Document
    from docx.shared import RGBColor, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    print("需要安装python-docx: pip install python-docx")
    raise

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("document_parser.word")


class WordParser:
    """Word文档解析器"""

    def __init__(self):
        self.logger = logger
        self.max_file_size = 100 * 1024 * 1024  # 100MB限制

    async def parse(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析Word文档

        Args:
            file_path: Word文件路径

        Returns:
            Tuple[str, Dict]: (提取的文本内容, 元数据)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Word文件不存在: {file_path}")

        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"文件过大: {file_size / (1024*1024):.1f}MB > {self.max_file_size / (1024*1024)}MB")

        # 检查文件格式
        if file_path.suffix.lower() not in ['.docx', '.doc']:
            raise ValueError(f"不支持的Word格式: {file_path.suffix}")

        self.logger.info(f"开始解析Word文档: {file_path}")

        try:
            # 在线程池中运行解析，避免阻塞
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._parse_document, str(file_path))

            content, metadata = result

            # 增强元数据
            metadata.update({
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'extraction_time': datetime.now().isoformat(),
                'parser_version': 'python-docx-1.0'
            })

            self.logger.info(f"Word解析完成: paragraphs={metadata.get('paragraph_count', 0)}, "
                           f"tables={metadata.get('table_count', 0)}")

            return content, metadata

        except Exception as e:
            self.logger.error(f"Word解析失败: {file_path}, error={e}")
            raise

    def _convert_doc_to_docx(self, file_path: str) -> str:
        """将.doc文件转换为.docx"""
        try:
            import doc2docx

            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            temp_docx = os.path.join(temp_dir, f"temp_{os.getpid()}_{Path(file_path).stem}.docx")

            self.logger.info(f"开始转换.doc文件: {file_path} -> {temp_docx}")

            # 转换文件
            doc2docx.convert(file_path, temp_docx)

            self.logger.info(f".doc文件转换成功: {temp_docx}")
            return temp_docx

        except ImportError:
            raise ValueError("缺少doc2docx库，无法转换.doc文件。请运行: pip install doc2docx")
        except Exception as e:
            self.logger.error(f".doc文件转换失败: {str(e)}")
            raise ValueError(f"无法转换.doc文件: {e}")

    def _parse_document(self, file_path: str) -> Tuple[str, Dict]:
        """解析Word文档的核心方法"""
        temp_file = None

        try:
            # 检查是否是.doc格式
            if Path(file_path).suffix.lower() == '.doc':
                # 转换为.docx
                temp_file = self._convert_doc_to_docx(file_path)
                file_path = temp_file
                self.logger.info(f"使用转换后的临时文件: {file_path}")

            # 现在使用python-docx处理
            doc = Document(file_path)

        except Exception as e:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    self.logger.info(f"已清理临时文件: {temp_file}")
                except (OSError, PermissionError) as e:
                    self.logger.warning(f"清理临时文件失败 {temp_file}: {e}")
            raise ValueError(f"无法打开Word文档: {e}")

        # 提取文档内容
        content_parts = []
        structure_info = {
            'headings': [],
            'tables': [],
            'images': [],
            'hyperlinks': [],
            'paragraph_count': 0,
            'table_count': 0,
            'image_count': 0
        }

        # 遍历文档元素
        for element in doc.element.body:
            if element.tag.endswith('p'):  # 段落
                paragraph = Paragraph(element, doc)
                para_info = self._process_paragraph(paragraph)
                if para_info['text'].strip():
                    content_parts.append(para_info['text'])
                    structure_info['paragraph_count'] += 1

                    # 检查是否是标题
                    if para_info['is_heading']:
                        structure_info['headings'].append({
                            'text': para_info['text'],
                            'level': para_info['heading_level'],
                            'style': para_info['style_name']
                        })

                    # 收集超链接
                    structure_info['hyperlinks'].extend(para_info['hyperlinks'])

            elif element.tag.endswith('tbl'):  # 表格
                table = Table(element, doc)
                table_info = self._process_table(table, len(structure_info['tables']))
                content_parts.append(f"\n[表格 {table_info['index'] + 1}]")
                content_parts.append(table_info['text_representation'])
                content_parts.append("")

                structure_info['tables'].append(table_info)
                structure_info['table_count'] += 1

        # 处理图片（通过关系文件）
        image_info = self._extract_image_info(doc)
        structure_info['images'] = image_info
        structure_info['image_count'] = len(image_info)

        # 合并内容
        full_content = '\n'.join(content_parts)

        # 提取文档属性
        doc_metadata = self._extract_document_properties(doc)
        doc_metadata.update(structure_info)

        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                self.logger.info(f"已清理临时文件: {temp_file}")
            except Exception as cleanup_error:
                self.logger.warning(f"清理临时文件失败: {cleanup_error}")

        return full_content, doc_metadata

    def _process_paragraph(self, paragraph: Paragraph) -> Dict:
        """处理段落，提取文本和格式信息"""
        para_info = {
            'text': paragraph.text,
            'style_name': paragraph.style.name if paragraph.style else 'Normal',
            'is_heading': False,
            'heading_level': 0,
            'alignment': str(paragraph.alignment) if paragraph.alignment else 'LEFT',
            'hyperlinks': []
        }

        # 检查是否是标题样式
        style_name = para_info['style_name'].lower()
        if 'heading' in style_name:
            para_info['is_heading'] = True
            # 提取标题级别
            level_match = re.search(r'heading\s*(\d+)', style_name)
            if level_match:
                para_info['heading_level'] = int(level_match.group(1))
            else:
                para_info['heading_level'] = 1

        # 检查字体格式（粗体、大字体可能是标题）
        if not para_info['is_heading'] and paragraph.runs:
            first_run = paragraph.runs[0]
            if hasattr(first_run, 'font'):
                font = first_run.font
                if font.bold or (font.size and font.size.pt > 14):
                    # 进一步检查是否符合标题特征
                    if self._is_likely_heading(paragraph.text):
                        para_info['is_heading'] = True
                        para_info['heading_level'] = self._determine_heading_level_by_format(font)

        # 提取超链接
        hyperlinks = self._extract_hyperlinks_from_paragraph(paragraph)
        para_info['hyperlinks'] = hyperlinks

        return para_info

    def _process_table(self, table: Table, table_index: int) -> Dict:
        """处理表格，提取数据和格式"""
        table_data = []

        for row in table.rows:
            row_data = []
            for cell in row.cells:
                # 合并单元格内的所有段落
                cell_text = '\n'.join(paragraph.text.strip() for paragraph in cell.paragraphs)
                row_data.append(cell_text)
            table_data.append(row_data)

        # 过滤空行
        filtered_data = []
        for row in table_data:
            if any(cell.strip() for cell in row):
                filtered_data.append(row)

        table_info = {
            'index': table_index,
            'rows': len(filtered_data),
            'columns': len(filtered_data[0]) if filtered_data else 0,
            'data': filtered_data,
            'text_representation': self._table_to_text(filtered_data)
        }

        return table_info

    def _extract_image_info(self, doc: Document) -> List[Dict]:
        """提取图片信息"""
        images = []

        try:
            # 通过文档的关系获取图片信息
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    image_info = {
                        'id': rel.rId,
                        'target': rel.target_ref,
                        'type': rel.reltype,
                        'filename': Path(rel.target_ref).name if rel.target_ref else 'unknown'
                    }
                    images.append(image_info)
        except Exception as e:
            self.logger.warning(f"提取图片信息失败: {e}")

        return images

    def _extract_document_properties(self, doc: Document) -> Dict:
        """提取文档属性"""
        properties = {}

        try:
            core_props = doc.core_properties
            properties.update({
                'title': core_props.title or '',
                'author': core_props.author or '',
                'subject': core_props.subject or '',
                'keywords': core_props.keywords or '',
                'comments': core_props.comments or '',
                'category': core_props.category or '',
                'created': core_props.created.isoformat() if core_props.created else '',
                'modified': core_props.modified.isoformat() if core_props.modified else '',
                'last_modified_by': core_props.last_modified_by or '',
                'revision': core_props.revision or 0
            })
        except Exception as e:
            self.logger.warning(f"提取文档属性失败: {e}")
            properties['extraction_error'] = str(e)

        return properties

    def _extract_hyperlinks_from_paragraph(self, paragraph: Paragraph) -> List[Dict]:
        """从段落中提取超链接"""
        hyperlinks = []

        try:
            # 遍历段落中的超链接
            for run in paragraph.runs:
                # 这里需要更复杂的逻辑来提取超链接
                # python-docx对超链接的处理比较复杂
                pass
        except Exception as e:
            self.logger.debug(f"提取超链接失败: {e}")

        return hyperlinks

    def _is_likely_heading(self, text: str) -> bool:
        """判断文本是否可能是标题"""
        if not text or len(text.strip()) > 100:
            return False

        text = text.strip()

        # 标题模式检测
        heading_patterns = [
            r'^第[一二三四五六七八九十\d]+[章节条]',
            r'^\d+\.?\d*\s*.{1,50}',
            r'^[一二三四五六七八九十]+[、\.]',
            r'^(摘要|概述|引言|结论|总结|附录|目录)',
            r'^[A-Z][A-Z\s]{2,30}$',  # 全大写英文标题
        ]

        for pattern in heading_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _determine_heading_level_by_format(self, font) -> int:
        """根据字体格式确定标题级别"""
        if not font or not font.size:
            return 4

        size_pt = font.size.pt
        if size_pt >= 18:
            return 1
        elif size_pt >= 16:
            return 2
        elif size_pt >= 14:
            return 3
        else:
            return 4

    def _table_to_text(self, table_data: List[List[str]]) -> str:
        """将表格数据转换为文本表示"""
        if not table_data:
            return ""

        # 计算每列的最大宽度
        max_widths = []
        for row in table_data:
            for i, cell in enumerate(row):
                if i >= len(max_widths):
                    max_widths.append(0)
                cell_lines = str(cell).split('\n')
                max_line_width = max(len(line) for line in cell_lines) if cell_lines else 0
                max_widths[i] = max(max_widths[i], max_line_width)

        # 生成表格文本
        text_lines = []
        for row in table_data:
            formatted_row = []
            for i, cell in enumerate(row):
                width = max_widths[i] if i < len(max_widths) else 10
                # 处理多行单元格
                cell_lines = str(cell).split('\n')
                if len(cell_lines) == 1:
                    formatted_row.append(cell_lines[0].ljust(width))
                else:
                    # 对多行内容，只取第一行并标记
                    first_line = cell_lines[0][:width-3] + "..." if len(cell_lines[0]) > width-3 else cell_lines[0]
                    formatted_row.append(first_line.ljust(width))

            text_lines.append(" | ".join(formatted_row))

        return "\n".join(text_lines)