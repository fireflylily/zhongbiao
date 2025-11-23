#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文档解析器
使用PyMuPDF和pdfplumber进行高质量PDF解析
支持OCR识别扫描PDF
"""

import fitz  # PyMuPDF
import pdfplumber
import re
import asyncio
import os
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
    """PDF文档解析器 - 支持原生PDF和扫描PDF(OCR)"""

    def __init__(self, enable_ocr: bool = None, ocr_min_chars: int = None):
        """
        初始化PDF解析器

        Args:
            enable_ocr: 是否启用OCR（None=从环境变量读取，默认True）
            ocr_min_chars: 触发OCR的最小字符数阈值（None=从环境变量读取，默认50）
        """
        self.logger = logger
        self.max_file_size = 100 * 1024 * 1024  # 100MB限制

        # OCR配置
        if enable_ocr is None:
            enable_ocr = os.getenv('ENABLE_OCR', 'true').lower() == 'true'
        if ocr_min_chars is None:
            ocr_min_chars = int(os.getenv('OCR_MIN_CHARS_PER_PAGE', '50'))

        self.enable_ocr = enable_ocr
        self.ocr_min_chars = ocr_min_chars
        self._ocr_parser = None

        if self.enable_ocr:
            self.logger.info(f"OCR功能已启用 (阈值: {self.ocr_min_chars}字符/页)")

    def _get_ocr_parser(self):
        """延迟初始化OCR解析器（仅在需要时加载）"""
        if self._ocr_parser is None and self.enable_ocr:
            try:
                from .ocr_parser import OCRParser

                use_gpu = os.getenv('OCR_USE_GPU', 'false').lower() == 'true'
                lang = os.getenv('OCR_LANG', 'ch')

                self._ocr_parser = OCRParser(use_gpu=use_gpu, lang=lang)
                self.logger.info("OCR解析器初始化完成")
            except Exception as e:
                self.logger.warning(f"OCR解析器初始化失败，将禁用OCR: {e}")
                self.enable_ocr = False

        return self._ocr_parser

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
        """使用PyMuPDF提取文本和结构信息，对扫描页自动启用OCR"""

        def extract_text():
            doc = fitz.open(file_path)
            text_content = ""
            structure_info = {
                'pages': [],
                'headings': [],
                'total_chars': 0,
                'scanned_pages': []  # 记录扫描页
            }

            try:
                for page_num in range(len(doc)):
                    page = doc[page_num]

                    # 提取文本
                    page_text = page.get_text()

                    # 提取页面结构信息
                    page_info = {
                        'page_num': page_num + 1,
                        'char_count': len(page_text),
                        'images': len(page.get_images()),
                        'links': len(page.get_links()),
                        'is_scanned': False
                    }

                    # 检测是否为扫描页（文字过少）
                    if len(page_text.strip()) < self.ocr_min_chars:
                        page_info['is_scanned'] = True
                        structure_info['scanned_pages'].append(page_num)
                        self.logger.debug(f"🔍 检测到扫描页: 第{page_num + 1}页 (仅{len(page_text)}字符)")

                    text_content += f"\n--- 第{page_num + 1}页 ---\n"
                    text_content += page_text

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
        text_content, structure_info = await loop.run_in_executor(None, extract_text)

        # 如果检测到扫描页且OCR已启用，进行OCR识别
        scanned_pages = structure_info.get('scanned_pages', [])
        if scanned_pages and self.enable_ocr:
            self.logger.info(f"🔄 检测到 {len(scanned_pages)} 个扫描页面，启动OCR识别...")

            ocr_parser = self._get_ocr_parser()
            if ocr_parser:
                try:
                    # 对扫描页进行OCR识别
                    ocr_results = await ocr_parser.ocr_pdf(file_path, scanned_pages)

                    # 将OCR结果合并到文本中
                    if ocr_results:
                        text_content = self._merge_ocr_results(
                            text_content,
                            ocr_results,
                            structure_info
                        )

                        # 更新字符统计
                        total_ocr_chars = sum(len(text) for text in ocr_results.values())
                        structure_info['total_chars'] += total_ocr_chars
                        structure_info['ocr_chars'] = total_ocr_chars

                        self.logger.info(f"✅ OCR识别完成，额外提取 {total_ocr_chars} 字符")

                except Exception as e:
                    self.logger.error(f"OCR识别失败: {e}")

        return text_content, structure_info

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

    def _merge_ocr_results(self, text_content: str, ocr_results: Dict[int, str], structure_info: Dict) -> str:
        """
        将OCR识别结果合并到原文本中

        Args:
            text_content: 原始文本内容
            ocr_results: OCR识别结果 {页码: OCR文本}
            structure_info: 结构信息

        Returns:
            str: 合并后的文本
        """
        lines = text_content.split('\n')
        merged_lines = []

        for line in lines:
            merged_lines.append(line)

            # 检查是否是页面分割线
            if line.startswith('--- 第') and line.endswith('页 ---'):
                # 提取页码
                page_match = re.search(r'第(\d+)页', line)
                if page_match:
                    page_num = int(page_match.group(1)) - 1  # 转换为从0开始的索引

                    # 如果该页有OCR结果，插入OCR文本
                    if page_num in ocr_results:
                        ocr_text = ocr_results[page_num]
                        if ocr_text.strip():
                            merged_lines.append(f"\n[OCR识别内容]")
                            merged_lines.append(ocr_text)
                            merged_lines.append("")
                            self.logger.debug(f"已插入第{page_num + 1}页的OCR内容 ({len(ocr_text)}字符)")

        return '\n'.join(merged_lines)

    def identify_audit_report_key_pages(self, pdf_path: str, max_pages: int = 20) -> List[int]:
        """
        智能识别审计报告中的关键页

        关键页包括：
        1. 封面（第1页）
        2. 审计报告正文页（审计意见、审计基础等）
        3. 主要财务报表（资产负债表、利润表、现金流量表、所有者权益变动表）
        4. 会计师签字页

        Args:
            pdf_path: PDF文件路径
            max_pages: 最多提取的关键页数（防止误判）

        Returns:
            关键页码列表（从1开始），如 [1, 2, 5, 6, 7, 8, 9, 10]
        """
        try:
            doc = fitz.open(pdf_path)
            key_pages = set()

            # 封面（必选）
            key_pages.add(1)

            # 定义关键内容标识词（优先级排序）
            critical_keywords = [
                # 审计报告核心部分（最重要）
                '审计报告',
                '审计意见',
                '保留意见',
                '无保留意见',
                '否定意见',
                '无法表示意见',
                '形成审计意见的基础',
                '管理层.*责任',
                '注册会计师.*责任',

                # 主要财务报表（重要）
                '资产负债表',
                '利润表',
                '现金流量表',
                '所有者权益变动表',
                '合并资产负债表',
                '合并利润表',

                # 签字页（重要）
                '会计师事务所',
                '注册会计师.*签字',
                '中国注册会计师',
            ]

            # 次要关键词（补充）
            secondary_keywords = [
                '财务报表附注',
                '主要会计政策',
                '重要会计估计',
                '或有事项',
                '承诺事项',
            ]

            # 扫描每一页
            for page_num in range(min(len(doc), 50)):  # 只扫描前50页
                page = doc[page_num]
                text = page.get_text()

                if not text.strip():
                    continue

                # 检查是否包含关键内容
                page_score = 0
                matched_keywords = []

                for keyword in critical_keywords:
                    if re.search(keyword, text, re.IGNORECASE):
                        page_score += 10
                        matched_keywords.append(keyword)

                for keyword in secondary_keywords:
                    if re.search(keyword, text, re.IGNORECASE):
                        page_score += 2
                        matched_keywords.append(keyword)

                # 如果得分足够高，标记为关键页
                if page_score >= 10:
                    key_pages.add(page_num + 1)
                    self.logger.debug(f"关键页: 第{page_num + 1}页 (得分:{page_score}, 关键词:{matched_keywords[:3]})")

                # 限制最多提取的页数
                if len(key_pages) >= max_pages:
                    self.logger.info(f"已达到最大关键页数 {max_pages}，停止扫描")
                    break

            doc.close()

            # 排序并返回
            result = sorted(list(key_pages))
            self.logger.info(f"✅ 识别出 {len(result)} 个关键页: {result}")

            return result

        except Exception as e:
            self.logger.error(f"识别审计报告关键页失败: {e}")
            # 降级策略：返回前10页
            return list(range(1, 11))