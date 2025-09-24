#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文档解析器
使用PyMuPDF和pdfplumber进行高质量PDF解析
"""

import fitz  # PyMuPDF
import pdfplumber
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("document_parser.pdf")


class PDFParser:
    """PDF文档解析器"""

    def __init__(self):
        self.logger = logger
        self.max_file_size = 100 * 1024 * 1024  # 100MB限制

    async def parse(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析PDF文档

        Args:
            file_path: PDF文件路径

        Returns:
            Tuple[str, Dict]: (提取的文本内容, 元数据)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {file_path}")

        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"文件过大: {file_size / (1024*1024):.1f}MB > {self.max_file_size / (1024*1024)}MB")

        self.logger.info(f"开始解析PDF文档: {file_path}")

        try:
            # 并行执行文本提取和表格提取
            text_task = asyncio.create_task(self._extract_text_with_fitz(str(file_path)))
            table_task = asyncio.create_task(self._extract_tables_with_pdfplumber(str(file_path)))
            metadata_task = asyncio.create_task(self._extract_metadata(str(file_path)))

            # 等待所有任务完成
            text_content, structure_info = await text_task
            tables = await table_task
            metadata = await metadata_task

            # 合并文本和表格内容
            full_content = self._merge_content_and_tables(text_content, tables, structure_info)

            # 增强元数据
            metadata.update({
                'total_pages': len(structure_info.get('pages', [])),
                'tables_count': len(tables),
                'has_images': any(page.get('images', 0) > 0 for page in structure_info.get('pages', [])),
                'extraction_time': datetime.now().isoformat(),
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            })

            self.logger.info(f"PDF解析完成: pages={metadata['total_pages']}, tables={len(tables)}")

            return full_content, metadata

        except Exception as e:
            self.logger.error(f"PDF解析失败: {file_path}, error={e}")
            raise

    async def _extract_text_with_fitz(self, file_path: str) -> Tuple[str, Dict]:
        """使用PyMuPDF提取文本和结构信息"""

        def extract_text():
            doc = fitz.open(file_path)
            text_content = ""
            structure_info = {
                'pages': [],
                'headings': [],
                'total_chars': 0
            }

            try:
                for page_num in range(len(doc)):
                    page = doc[page_num]

                    # 提取文本
                    page_text = page.get_text()
                    text_content += f"\n--- 第{page_num + 1}页 ---\n"
                    text_content += page_text

                    # 提取页面结构信息
                    page_info = {
                        'page_num': page_num + 1,
                        'char_count': len(page_text),
                        'images': len(page.get_images()),
                        'links': len(page.get_links())
                    }

                    # 提取标题（基于字体大小和样式）
                    blocks = page.get_text("dict")
                    page_headings = self._extract_headings_from_blocks(blocks, page_num + 1)
                    structure_info['headings'].extend(page_headings)

                    structure_info['pages'].append(page_info)
                    structure_info['total_chars'] += len(page_text)

            finally:
                doc.close()

            return text_content, structure_info

        # 在线程池中运行，避免阻塞
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract_text)

    async def _extract_tables_with_pdfplumber(self, file_path: str) -> List[Dict]:
        """使用pdfplumber提取表格"""

        def extract_tables():
            tables = []

            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取页面中的表格
                    page_tables = page.extract_tables()

                    for table_index, table in enumerate(page_tables):
                        if table and len(table) > 1:  # 确保表格有数据
                            # 清理表格数据
                            cleaned_table = []
                            for row in table:
                                cleaned_row = [cell.strip() if cell else "" for cell in row]
                                # 过滤空行
                                if any(cell for cell in cleaned_row):
                                    cleaned_table.append(cleaned_row)

                            if cleaned_table:
                                table_info = {
                                    'page': page_num,
                                    'table_index': table_index,
                                    'rows': len(cleaned_table),
                                    'columns': len(cleaned_table[0]) if cleaned_table else 0,
                                    'data': cleaned_table,
                                    'text_representation': self._table_to_text(cleaned_table)
                                }
                                tables.append(table_info)

            return tables

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract_tables)

    async def _extract_metadata(self, file_path: str) -> Dict:
        """提取PDF元数据"""

        def extract_metadata():
            metadata = {}

            try:
                doc = fitz.open(file_path)

                # 获取文档属性
                doc_metadata = doc.metadata
                metadata.update({
                    'title': doc_metadata.get('title', ''),
                    'author': doc_metadata.get('author', ''),
                    'subject': doc_metadata.get('subject', ''),
                    'creator': doc_metadata.get('creator', ''),
                    'producer': doc_metadata.get('producer', ''),
                    'creation_date': doc_metadata.get('creationDate', ''),
                    'modification_date': doc_metadata.get('modDate', ''),
                    'format': doc_metadata.get('format', 'PDF'),
                    'encrypted': doc.is_encrypted,
                    'pages': doc.page_count
                })

                doc.close()

            except Exception as e:
                logger.warning(f"提取PDF元数据失败: {e}")
                metadata['error'] = str(e)

            return metadata

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract_metadata)

    def _extract_headings_from_blocks(self, blocks: Dict, page_num: int) -> List[Dict]:
        """从文本块中提取标题"""
        headings = []

        if 'blocks' not in blocks:
            return headings

        for block in blocks['blocks']:
            if 'lines' not in block:
                continue

            for line in block['lines']:
                if 'spans' not in line:
                    continue

                # 分析字体大小和样式
                for span in line['spans']:
                    text = span.get('text', '').strip()
                    if not text:
                        continue

                    font_size = span.get('size', 0)
                    font_flags = span.get('flags', 0)
                    is_bold = font_flags & 2 ** 4  # 粗体标志

                    # 判断是否为标题（基于字体大小和样式）
                    if font_size > 14 or is_bold:
                        # 进一步检查是否符合标题模式
                        if self._is_likely_heading(text):
                            heading = {
                                'page': page_num,
                                'text': text,
                                'font_size': font_size,
                                'is_bold': bool(is_bold),
                                'level': self._determine_heading_level(font_size, is_bold)
                            }
                            headings.append(heading)

        return headings

    def _is_likely_heading(self, text: str) -> bool:
        """判断文本是否可能是标题"""
        # 标题特征检测
        if len(text) > 100:  # 标题通常不会太长
            return False

        # 检查是否包含标题关键词
        title_patterns = [
            r'第[一二三四五六七八九十\d]+[章节条]',
            r'\d+\.?\d*\s*.{1,50}',
            r'[一二三四五六七八九十]+[、\.]',
            r'^(摘要|概述|引言|结论|总结|附录)',
            r'^[A-Z][A-Z\s]{2,20}$',  # 全大写英文标题
        ]

        for pattern in title_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _determine_heading_level(self, font_size: float, is_bold: bool) -> int:
        """确定标题级别"""
        if font_size >= 18:
            return 1
        elif font_size >= 16:
            return 2
        elif font_size >= 14:
            return 3
        elif is_bold:
            return 4
        else:
            return 5

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
                max_widths[i] = max(max_widths[i], len(str(cell)))

        # 生成表格文本
        text_lines = []
        for row in table_data:
            formatted_row = []
            for i, cell in enumerate(row):
                width = max_widths[i] if i < len(max_widths) else 10
                formatted_row.append(str(cell).ljust(width))
            text_lines.append(" | ".join(formatted_row))

        return "\n".join(text_lines)

    def _merge_content_and_tables(self, text_content: str, tables: List[Dict], structure_info: Dict) -> str:
        """合并文本内容和表格内容"""
        if not tables:
            return text_content

        # 将表格内容插入到相应的页面位置
        lines = text_content.split('\n')
        merged_lines = []
        current_page = 0

        for line in lines:
            merged_lines.append(line)

            # 检查是否是页面分割线
            if line.startswith('--- 第') and line.endswith('页 ---'):
                # 提取页码
                page_match = re.search(r'第(\d+)页', line)
                if page_match:
                    current_page = int(page_match.group(1))

                    # 插入该页面的所有表格
                    page_tables = [t for t in tables if t['page'] == current_page]
                    for table in page_tables:
                        merged_lines.append(f"\n[表格 {table['table_index'] + 1}]")
                        merged_lines.append(table['text_representation'])
                        merged_lines.append("")

        return '\n'.join(merged_lines)