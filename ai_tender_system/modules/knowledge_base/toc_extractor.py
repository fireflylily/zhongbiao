#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档目录提取器 (Table of Contents Extractor)
功能：从各类文档中提取标题层级结构，构建导航目录
支持：Word文档、PDF文档、TXT文档
"""

import re
import json
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.text.paragraph import CT_P
    from docx.text.paragraph import Paragraph
    from docx.shared import Pt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import jieba
    jieba.setLogLevel(logging.WARNING)  # 禁用jieba的日志输出
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

logger = logging.getLogger(__name__)


class TOCExtractor:
    """文档目录提取器"""

    def __init__(self):
        """初始化"""
        # 章节号正则表达式模式
        self.section_patterns = [
            r'^\s*(\d+(?:\.\d+)*)',  # 1.1.1, 3.1.101
            r'^\s*第([一二三四五六七八九十百千]+)[章节部分篇]',  # 第一章, 第三节
            r'^\s*第(\d+)[章节部分篇]',  # 第1章
            r'^\s*([IVX]+)\.?\s*',  # I. II. III. (罗马数字)
        ]

        # 关键词正则表达式
        self.keyword_patterns = {
            'interface_code': r'\b\d{6}\b',  # 6位接口编号
            'api_code': r'\b\d{3,6}\b',  # 3-6位数字编号
            'version': r'v?\d+\.\d+(?:\.\d+)?',  # 版本号 v1.0, 2.1.0
        }

        logger.info("TOC提取器初始化完成")

    def extract_toc(self, file_path: str, doc_id: int) -> List[Dict]:
        """
        提取文档目录

        Args:
            file_path: 文档路径
            doc_id: 文档ID

        Returns:
            目录条目列表
        """
        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext in ['.docx', '.doc']:
                return self._extract_from_docx(file_path, doc_id)
            elif file_ext == '.pdf':
                return self._extract_from_pdf(file_path, doc_id)
            elif file_ext == '.txt':
                return self._extract_from_txt(file_path, doc_id)
            else:
                logger.warning(f"不支持的文件格式: {file_ext}")
                return []

        except Exception as e:
            logger.error(f"提取目录失败: {file_path}, 错误: {e}")
            return []

    def _extract_from_docx(self, file_path: str, doc_id: int) -> List[Dict]:
        """从Word文档提取目录"""
        if not DOCX_AVAILABLE:
            logger.error("python-docx未安装，无法处理Word文档")
            return []

        doc = Document(file_path)
        toc_entries = []
        sequence = 0

        for element in doc.element.body:
            if not isinstance(element, CT_P):
                continue

            paragraph = Paragraph(element, doc)
            text = paragraph.text.strip()

            if not text:
                continue

            # 判断是否为标题
            heading_level = self._is_heading_docx(paragraph)
            if heading_level == 0:
                continue

            # 提取章节号
            section_number = self._extract_section_number(text)

            # 提取关键词
            keywords = self._extract_keywords(text)

            # 创建目录条目
            toc_entry = {
                'doc_id': doc_id,
                'heading_level': heading_level,
                'heading_text': text,
                'section_number': section_number,
                'keywords': json.dumps(keywords, ensure_ascii=False) if keywords else None,
                'page_number': None,  # Word文档难以准确获取页码
                'parent_toc_id': None,  # 稍后构建层级关系
                'sequence_order': sequence
            }

            toc_entries.append(toc_entry)
            sequence += 1

        logger.info(f"从Word文档提取了 {len(toc_entries)} 个目录条目")
        return self._build_hierarchy(toc_entries)

    def _is_heading_docx(self, paragraph: 'Paragraph') -> int:
        """
        判断段落是否为标题，返回标题级别

        Args:
            paragraph: Word段落对象

        Returns:
            0: 不是标题
            1-4: 标题级别
        """
        # 方法1: 样式名称判断
        style_name = paragraph.style.name
        if style_name.startswith('Heading'):
            try:
                level = int(style_name.split()[-1])
                return min(level, 4)  # 最多4级
            except (ValueError, IndexError):
                pass  # 无法解析标题级别时使用其他方法

        # 方法2: 字体大小+加粗判断
        if paragraph.runs:
            run = paragraph.runs[0]
            if run.bold and run.font.size:
                size_pt = run.font.size.pt
                if size_pt >= 16:
                    return 1
                elif size_pt >= 14:
                    return 2
                elif size_pt >= 12:
                    return 3
                elif size_pt >= 10.5:
                    return 4

        return 0

    def _extract_from_pdf(self, file_path: str, doc_id: int) -> List[Dict]:
        """从PDF文档提取目录"""
        # TODO: 实现PDF目录提取
        # 需要使用 pdfplumber 或 PyPDF2
        logger.warning("PDF目录提取功能尚未实现")
        return []

    def _extract_from_txt(self, file_path: str, doc_id: int) -> List[Dict]:
        """从TXT文档提取目录"""
        toc_entries = []
        sequence = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                text = line.strip()
                if not text:
                    continue

                # 尝试识别标题（基于章节号）
                section_number = self._extract_section_number(text)
                if not section_number:
                    continue

                # 判断标题级别（根据章节号深度）
                heading_level = section_number.count('.') + 1
                heading_level = min(heading_level, 4)

                # 提取关键词
                keywords = self._extract_keywords(text)

                toc_entry = {
                    'doc_id': doc_id,
                    'heading_level': heading_level,
                    'heading_text': text,
                    'section_number': section_number,
                    'keywords': json.dumps(keywords, ensure_ascii=False) if keywords else None,
                    'page_number': None,
                    'parent_toc_id': None,
                    'sequence_order': sequence
                }

                toc_entries.append(toc_entry)
                sequence += 1

        logger.info(f"从TXT文档提取了 {len(toc_entries)} 个目录条目")
        return self._build_hierarchy(toc_entries)

    def _extract_section_number(self, text: str) -> Optional[str]:
        """
        提取章节号

        Args:
            text: 标题文本

        Returns:
            章节号字符串，如 "3.1.101" 或 "第一章"
        """
        for pattern in self.section_patterns:
            match = re.match(pattern, text)
            if match:
                return match.group(1)
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词

        Args:
            text: 文本

        Returns:
            关键词列表
        """
        keywords = []

        # 1. 提取接口编号（6位数字）
        interface_codes = re.findall(self.keyword_patterns['interface_code'], text)
        keywords.extend(interface_codes)

        # 2. 提取API编号（3-6位数字）
        api_codes = re.findall(self.keyword_patterns['api_code'], text)
        keywords.extend(api_codes)

        # 3. 使用jieba提取中文关键词（2-8个字的词组）
        if JIEBA_AVAILABLE:
            # 移除数字和特殊符号
            clean_text = re.sub(r'[\d\.]+', '', text)
            # 分词
            words = jieba.cut(clean_text)
            # 过滤：保留2-8个字的中文词组
            chinese_keywords = [
                w for w in words
                if len(w) >= 2 and len(w) <= 8 and re.match(r'^[\u4e00-\u9fa5]+$', w)
            ]
            keywords.extend(chinese_keywords)

        # 去重并返回
        return list(dict.fromkeys(keywords))  # 保持顺序的去重

    def _build_hierarchy(self, toc_entries: List[Dict]) -> List[Dict]:
        """
        构建层级关系（设置parent_toc_id）

        Args:
            toc_entries: 目录条目列表

        Returns:
            带有层级关系的目录条目列表
        """
        if not toc_entries:
            return []

        # 使用栈维护各级别的最新标题
        level_stack = []  # [(level, index), ...]

        for i, entry in enumerate(toc_entries):
            level = entry['heading_level']

            # 弹出所有大于等于当前级别的元素
            while level_stack and level_stack[-1][0] >= level:
                level_stack.pop()

            # 如果栈不为空，栈顶元素就是父级
            if level_stack:
                parent_idx = level_stack[-1][1]
                # 注意：parent_toc_id需要在插入数据库后才能设置
                # 这里先标记parent的序号，后续处理
                entry['_parent_sequence'] = toc_entries[parent_idx]['sequence_order']
            else:
                entry['_parent_sequence'] = None

            # 当前元素入栈
            level_stack.append((level, i))

        return toc_entries


# 导出
__all__ = ['TOCExtractor']
