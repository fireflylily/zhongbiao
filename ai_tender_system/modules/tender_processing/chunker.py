#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档智能分块处理器
功能：
- 识别章节结构（标题层级）
- 提取表格内容
- 智能分块（按语义、大小）
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import tiktoken

from common import get_module_logger

logger = get_module_logger("document_chunker")


@dataclass
class DocumentChunk:
    """文档分块数据类"""
    chunk_index: int
    chunk_type: str  # title/paragraph/table/list
    content: str
    metadata: Dict

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'chunk_index': self.chunk_index,
            'chunk_type': self.chunk_type,
            'content': self.content,
            'metadata': self.metadata
        }


class DocumentChunker:
    """文档智能分块处理器"""

    def __init__(self, max_chunk_size: int = 800, overlap_size: int = 100):
        """
        初始化分块处理器

        Args:
            max_chunk_size: 最大分块大小（token数）
            overlap_size: 分块重叠大小（token数）
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

        # 初始化tokenizer（用于计算token数）
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4使用的编码
        except Exception as e:
            logger.warning(f"初始化tokenizer失败，使用简单字符计数: {e}")
            self.tokenizer = None

        # 标题识别模式
        self.title_patterns = [
            # 一级标题：第一章、第1章、一、1、1.、（一）等
            r'^(?:第[一二三四五六七八九十百]+章|第\d+章|[一二三四五六七八九十]+、|\d+、|\d+\.|（[一二三四五六七八九十]+）)',
            # 二级标题：1.1、1.1.、（1）等
            r'^\d+\.\d+\.?|^（\d+）',
            # 三级标题：1.1.1、（一）等
            r'^\d+\.\d+\.\d+\.?|^[①②③④⑤⑥⑦⑧⑨⑩]',
        ]

        # 表格识别模式
        self.table_indicators = [
            '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼',  # 表格边框字符
            '│', '─', '╭', '╮', '╰', '╯',
        ]

        # 章节重要性关键词（用于基于目录的过滤）
        # 需要提取的章节关键词
        self.RELEVANT_SECTION_KEYWORDS = [
            # 投标要求类
            "投标须知", "供应商须知", "投标人须知", "资格要求", "资质要求",
            "投标邀请", "招标公告", "项目概况",
            # 技术要求类
            "技术要求", "技术规格", "技术参数", "性能指标", "项目需求",
            "需求说明", "技术标准", "功能要求", "技术规范", "技术方案",
            # 商务要求类
            "商务要求", "商务条款", "付款方式", "交付要求", "质保要求",
            "价格要求", "报价要求",
            # 评分标准类
            "评分标准", "评标办法", "评分细则", "打分标准", "综合评分",
            "评审标准", "评审办法",
        ]

        # 无需提取的章节关键词（优先级更高）
        self.SKIP_SECTION_KEYWORDS = [
            # 合同类
            "合同条款", "合同文本", "合同范本", "合同格式", "合同协议",
            "通用条款", "专用条款", "合同主要条款", "合同草稿", "拟签合同",
            # 格式类
            "投标文件格式", "文件格式", "格式要求", "编制要求", "封装要求",
            "响应文件格式", "资料清单", "包装要求", "密封要求",
            # 法律声明类
            "法律声明", "免责声明", "投标承诺", "廉政承诺", "保密协议",
            "诚信承诺", "声明函",
            # 附件类
            "附件", "附表", "附录", "样表", "模板", "格式范本", "空白表格",
        ]

    def count_tokens(self, text: str) -> int:
        """计算文本的token数"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except (AttributeError, TypeError, ValueError):
                pass  # Tokenizer失败时使用估算方法
        # 简单估算：中文1字约1.5 token，英文1词约1 token
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return int(chinese_chars * 1.5 + english_words)

    def detect_chunk_type(self, text: str) -> str:
        """
        检测文本块类型

        Args:
            text: 文本内容

        Returns:
            chunk_type: title/paragraph/table/list
        """
        text_stripped = text.strip()

        # 检测标题
        for pattern in self.title_patterns:
            if re.match(pattern, text_stripped):
                return 'title'

        # 检测表格
        if any(indicator in text_stripped for indicator in self.table_indicators):
            return 'table'

        # 检测列表（多个项目符号或编号）
        list_patterns = [
            r'^[•·○●]\s',  # 项目符号
            r'^\d+[\.、）]\s',  # 数字编号
            r'^[①②③④⑤⑥⑦⑧⑨⑩]\s',  # 圆圈数字
            r'^[（\(][一二三四五六七八九十\d]+[）\)]\s',  # 括号编号
        ]
        list_items = sum(1 for line in text_stripped.split('\n')
                        if any(re.match(p, line.strip()) for p in list_patterns))
        if list_items >= 2:
            return 'list'

        return 'paragraph'

    def extract_sections(self, text: str) -> List[Dict]:
        """
        提取文档章节结构

        Args:
            text: 文档全文

        Returns:
            sections: 章节列表，每个章节包含标题、内容、层级等信息
        """
        sections = []
        lines = text.split('\n')

        current_section = None
        current_content = []
        current_level = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                if current_content:
                    current_content.append(line)
                continue

            # 检测是否为标题
            title_level = self._detect_title_level(stripped)

            if title_level > 0:
                # 保存上一个章节
                if current_section:
                    current_section['content'] = '\n'.join(current_content)
                    current_section['end_line'] = line_num - 1
                    sections.append(current_section)

                # 开始新章节
                current_section = {
                    'title': stripped,
                    'level': title_level,
                    'start_line': line_num,
                    'content': ''
                }
                current_content = []
                current_level = title_level
            else:
                # 内容行
                current_content.append(line)

        # 保存最后一个章节
        if current_section:
            current_section['content'] = '\n'.join(current_content)
            current_section['end_line'] = len(lines)
            sections.append(current_section)

        logger.info(f"识别到 {len(sections)} 个章节")
        return sections

    def _detect_title_level(self, text: str) -> int:
        """
        检测标题层级

        Returns:
            0: 不是标题
            1-3: 标题层级
        """
        for level, pattern in enumerate(self.title_patterns, 1):
            if re.match(pattern, text):
                return level
        return 0

    def extract_tables(self, text: str) -> List[Dict]:
        """
        提取文档中的表格

        Args:
            text: 文档内容

        Returns:
            tables: 表格列表
        """
        tables = []
        lines = text.split('\n')

        in_table = False
        table_lines = []
        table_start = 0

        for line_num, line in enumerate(lines, 1):
            # 检测表格开始
            if any(indicator in line for indicator in self.table_indicators):
                if not in_table:
                    in_table = True
                    table_start = line_num
                    table_lines = [line]
                else:
                    table_lines.append(line)
            elif in_table:
                # 检测表格结束（连续2行无表格字符）
                if table_lines and len(table_lines) >= 2:
                    # 保存表格
                    tables.append({
                        'content': '\n'.join(table_lines),
                        'start_line': table_start,
                        'end_line': line_num - 1,
                        'rows': len([l for l in table_lines if l.strip()])
                    })

                in_table = False
                table_lines = []

        logger.info(f"识别到 {len(tables)} 个表格")
        return tables

    def extract_table_of_contents(self, text: str) -> List[Dict]:
        """
        提取文档目录

        Args:
            text: 文档全文

        Returns:
            toc: 目录列表，每个条目包含标题、层级、是否需要提取等信息
        """
        toc = []
        lines = text.split('\n')

        # 1. 找到"目录"开始位置
        toc_start = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.search(r'^目\s*录|^CONTENTS|^Table of Contents', stripped, re.I):
                toc_start = i
                logger.info(f"找到目录起始位置：第{i+1}行")
                break

        if toc_start == -1:
            logger.warning("未找到目录，将使用普通章节识别")
            return []

        # 2. 提取目录项（直到遇到正文）
        toc_end = -1
        for i in range(toc_start + 1, min(toc_start + 200, len(lines))):  # 限制搜索范围
            line = lines[i].strip()

            # 目录结束标志（遇到第一部分/第一章等正文标题）
            if self._is_content_start(line):
                toc_end = i
                logger.info(f"目录结束位置：第{i+1}行")
                break

            # 解析目录项
            # 匹配格式：第一部分 xxx、第1部分 xxx、一、xxx等
            patterns = [
                r'(第[一二三四五六七八九十百]+部分)\s*(.+?)(?:\s*\.{2,}.*)?$',
                r'(第\d+部分)\s*(.+?)(?:\s*\.{2,}.*)?$',
                r'(第[一二三四五六七八九十百]+章)\s*(.+?)(?:\s*\.{2,}.*)?$',
                r'(第\d+章)\s*(.+?)(?:\s*\.{2,}.*)?$',
                r'([一二三四五六七八九十]+)、\s*(.+?)(?:\s*\.{2,}.*)?$',
                r'(\d+)、\s*(.+?)(?:\s*\.{2,}.*)?$',
            ]

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    section_num = match.group(1)
                    section_title = match.group(2).strip()
                    full_title = f"{section_num} {section_title}"

                    # 判断是否需要提取
                    is_relevant = self._is_relevant_section(full_title)

                    toc.append({
                        'title': full_title,
                        'section_num': section_num,
                        'section_name': section_title,
                        'level': 1,
                        'is_relevant': is_relevant,
                        'toc_line': i,
                        'start_position': None,
                        'end_position': None
                    })

                    status = "✅ 需要提取" if is_relevant else "❌ 跳过"
                    logger.info(f"  目录项: {full_title} {status}")
                    break

        logger.info(f"从目录中识别到 {len(toc)} 个章节")
        return toc

    def _is_content_start(self, line: str) -> bool:
        """判断是否为正文开始（用于目录结束判断）"""
        # 正文通常以"第X部分"、"第X章"等开头，且后面有实质内容
        patterns = [
            r'^第[一二三四五六七八九十百]+部分\s+\S{2,}',
            r'^第\d+部分\s+\S{2,}',
            r'^第[一二三四五六七八九十百]+章\s+\S{2,}',
            r'^第\d+章\s+\S{2,}',
        ]
        return any(re.match(p, line) for p in patterns)

    def _is_relevant_section(self, section_title: str) -> bool:
        """
        判断章节是否需要提取

        Args:
            section_title: 章节标题

        Returns:
            bool: True表示需要提取，False表示跳过
        """
        title_lower = section_title.lower()

        # 1. 先检查跳过规则（优先级高）
        for keyword in self.SKIP_SECTION_KEYWORDS:
            if keyword in section_title:
                return False

        # 2. 再检查需要提取的规则
        for keyword in self.RELEVANT_SECTION_KEYWORDS:
            if keyword in section_title:
                return True

        # 3. 默认保留（让后续filter判断）
        return True

    def locate_sections_in_content(self, text: str, toc: List[Dict]) -> List[Dict]:
        """
        在正文中定位每个章节的起始位置

        Args:
            text: 文档全文
            toc: 目录列表

        Returns:
            toc: 更新后的目录列表（包含位置信息）
        """
        lines = text.split('\n')

        for section in toc:
            # 在全文中搜索章节标题（从目录位置之后开始搜索）
            search_start = section.get('toc_line', 0) + 1

            for i in range(search_start, len(lines)):
                line = lines[i].strip()

                # 匹配章节标题（支持多种格式）
                # 完全匹配
                if section['title'] == line:
                    section['start_position'] = i
                    logger.debug(f"定位章节 '{section['title']}' 在第{i+1}行")
                    break

                # 包含章节编号和名称
                if section['section_num'] in line and section['section_name'] in line:
                    section['start_position'] = i
                    logger.debug(f"定位章节 '{section['title']}' 在第{i+1}行")
                    break

        # 计算每个章节的结束位置（下一章节的开始-1）
        for i, section in enumerate(toc):
            if section['start_position'] is None:
                logger.warning(f"未能定位章节: {section['title']}")
                continue

            if i < len(toc) - 1:
                # 找到下一个有位置信息的章节
                next_position = None
                for next_section in toc[i+1:]:
                    if next_section['start_position'] is not None:
                        next_position = next_section['start_position']
                        break

                if next_position:
                    section['end_position'] = next_position - 1
                else:
                    section['end_position'] = len(lines) - 1
            else:
                section['end_position'] = len(lines) - 1

        # 统计定位成功的章节
        located_count = sum(1 for s in toc if s['start_position'] is not None)
        logger.info(f"成功定位 {located_count}/{len(toc)} 个章节")

        return toc

    def chunk_document(self, text: str, metadata: Dict = None) -> List[DocumentChunk]:
        """
        智能分块文档

        Args:
            text: 文档全文
            metadata: 文档元数据

        Returns:
            chunks: 分块列表
        """
        logger.info("开始文档分块处理...")

        # 1. 尝试提取目录（基于目录的章节过滤）
        toc = self.extract_table_of_contents(text)

        if toc:
            # 使用基于目录的分块逻辑
            logger.info("使用基于目录的智能分块...")
            return self._chunk_document_with_toc(text, toc, metadata)
        else:
            # 使用传统的章节识别分块逻辑
            logger.info("使用传统章节识别分块...")
            return self._chunk_document_traditional(text, metadata)

    def _chunk_document_with_toc(self, text: str, toc: List[Dict], metadata: Dict = None) -> List[DocumentChunk]:
        """
        基于目录的智能分块

        Args:
            text: 文档全文
            toc: 目录列表
            metadata: 文档元数据

        Returns:
            chunks: 分块列表
        """
        # 1. 定位章节在正文中的位置
        toc = self.locate_sections_in_content(text, toc)

        # 2. 提取表格
        tables = self.extract_tables(text)

        # 3. 分块处理
        chunks = []
        chunk_index = 0
        lines = text.split('\n')

        for section in toc:
            # 跳过不相关的章节
            if not section['is_relevant']:
                logger.info(f"⏭️  跳过无关章节: {section['title']}")
                continue

            # 跳过无法定位的章节
            if section['start_position'] is None:
                logger.warning(f"⚠️  无法定位章节: {section['title']}")
                continue

            logger.info(f"📝 处理章节: {section['title']}")

            # 提取该章节的内容
            start = section['start_position']
            end = section['end_position']
            section_content = '\n'.join(lines[start:end + 1])

            # 为章节标题创建独立分块
            chunk_metadata = {
                'section_title': section['title'],
                'section_level': section['level'],
                'start_line': start,
                'end_line': start,
                'token_count': self.count_tokens(section['title']),
                'is_from_toc': True
            }
            if metadata:
                chunk_metadata.update(metadata)

            chunks.append(DocumentChunk(
                chunk_index=chunk_index,
                chunk_type='title',
                content=section['title'],
                metadata=chunk_metadata
            ))
            chunk_index += 1

            # 处理章节内容
            if section_content.strip():
                # 检查是否包含表格
                section_tables = [t for t in tables
                                 if start <= t['start_line'] <= end]

                if section_tables:
                    # 分段处理（表格前、表格、表格后）
                    content_chunks = self._chunk_content_with_tables(
                        section_content, section_tables, section['title'], section['level']
                    )
                else:
                    # 普通内容分块
                    content_chunks = self._chunk_content(
                        section_content, section['title'], section['level']
                    )

                for chunk in content_chunks:
                    chunk.chunk_index = chunk_index
                    chunk.metadata['is_from_toc'] = True
                    if metadata:
                        chunk.metadata.update(metadata)
                    chunks.append(chunk)
                    chunk_index += 1

        logger.info(f"✅ 基于目录分块完成，共生成 {len(chunks)} 个分块")
        return chunks

    def _chunk_document_traditional(self, text: str, metadata: Dict = None) -> List[DocumentChunk]:
        """
        传统的章节识别分块（不使用目录）

        Args:
            text: 文档全文
            metadata: 文档元数据

        Returns:
            chunks: 分块列表
        """
        # 1. 提取章节结构
        sections = self.extract_sections(text)

        # 2. 提取表格
        tables = self.extract_tables(text)

        # 3. 生成分块
        chunks = []
        chunk_index = 0

        for section in sections:
            section_title = section['title']
            section_content = section['content']
            section_level = section['level']

            # 为标题创建独立分块
            if section_title:
                chunk_metadata = {
                    'section_title': section_title,
                    'section_level': section_level,
                    'start_line': section['start_line'],
                    'end_line': section['start_line'],
                    'token_count': self.count_tokens(section_title)
                }
                if metadata:
                    chunk_metadata.update(metadata)

                chunks.append(DocumentChunk(
                    chunk_index=chunk_index,
                    chunk_type='title',
                    content=section_title,
                    metadata=chunk_metadata
                ))
                chunk_index += 1

            # 处理章节内容
            if section_content.strip():
                # 检查是否包含表格
                section_tables = [t for t in tables
                                 if section['start_line'] <= t['start_line'] <= section['end_line']]

                if section_tables:
                    # 分段处理（表格前、表格、表格后）
                    content_chunks = self._chunk_content_with_tables(
                        section_content, section_tables, section_title, section_level
                    )
                else:
                    # 普通内容分块
                    content_chunks = self._chunk_content(
                        section_content, section_title, section_level
                    )

                for chunk in content_chunks:
                    chunk.chunk_index = chunk_index
                    if metadata:
                        chunk.metadata.update(metadata)
                    chunks.append(chunk)
                    chunk_index += 1

        logger.info(f"文档分块完成，共生成 {len(chunks)} 个分块")
        return chunks

    def _chunk_content(self, content: str, section_title: str, section_level: int) -> List[DocumentChunk]:
        """
        对普通内容进行分块

        Args:
            content: 内容文本
            section_title: 所属章节标题
            section_level: 章节层级

        Returns:
            chunks: 分块列表
        """
        chunks = []

        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        current_chunk_content = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # 如果单个段落超过最大大小，需要进一步分割
            if para_tokens > self.max_chunk_size:
                # 先保存当前累积的内容
                if current_chunk_content:
                    chunks.append(self._create_chunk(
                        '\n\n'.join(current_chunk_content),
                        'paragraph',
                        section_title,
                        section_level
                    ))
                    current_chunk_content = []
                    current_tokens = 0

                # 分割长段落
                para_chunks = self._split_long_paragraph(para, section_title, section_level)
                chunks.extend(para_chunks)

            elif current_tokens + para_tokens > self.max_chunk_size:
                # 当前块已满，保存并开始新块
                chunks.append(self._create_chunk(
                    '\n\n'.join(current_chunk_content),
                    'paragraph',
                    section_title,
                    section_level
                ))

                # 添加重叠内容（最后一个段落）
                if current_chunk_content:
                    overlap_content = current_chunk_content[-1]
                    current_chunk_content = [overlap_content, para]
                    current_tokens = self.count_tokens(overlap_content) + para_tokens
                else:
                    current_chunk_content = [para]
                    current_tokens = para_tokens
            else:
                # 添加到当前块
                current_chunk_content.append(para)
                current_tokens += para_tokens

        # 保存最后一个块
        if current_chunk_content:
            chunks.append(self._create_chunk(
                '\n\n'.join(current_chunk_content),
                'paragraph',
                section_title,
                section_level
            ))

        return chunks

    def _split_long_paragraph(self, paragraph: str, section_title: str, section_level: int) -> List[DocumentChunk]:
        """分割超长段落"""
        chunks = []

        # 按句子分割
        sentences = re.split(r'([。！？；\n])', paragraph)
        sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]

        current_content = []
        current_tokens = 0

        for sent in sentences:
            sent_tokens = self.count_tokens(sent)

            if current_tokens + sent_tokens > self.max_chunk_size:
                if current_content:
                    chunks.append(self._create_chunk(
                        ''.join(current_content),
                        'paragraph',
                        section_title,
                        section_level
                    ))

                current_content = [sent]
                current_tokens = sent_tokens
            else:
                current_content.append(sent)
                current_tokens += sent_tokens

        if current_content:
            chunks.append(self._create_chunk(
                ''.join(current_content),
                'paragraph',
                section_title,
                section_level
            ))

        return chunks

    def _chunk_content_with_tables(self, content: str, tables: List[Dict],
                                   section_title: str, section_level: int) -> List[DocumentChunk]:
        """处理包含表格的内容"""
        chunks = []

        # TODO: 实现表格和文本混合的分块逻辑
        # 简化版本：将表格单独提取为chunk，其余内容正常分块
        for table in tables:
            chunks.append(self._create_chunk(
                table['content'],
                'table',
                section_title,
                section_level,
                {'table_rows': table['rows']}
            ))

        # 处理非表格内容
        # （这里简化处理，实际应该根据表格位置切分文本）
        text_content = content
        for table in tables:
            text_content = text_content.replace(table['content'], '')

        if text_content.strip():
            text_chunks = self._chunk_content(text_content, section_title, section_level)
            chunks.extend(text_chunks)

        return chunks

    def _create_chunk(self, content: str, chunk_type: str, section_title: str,
                     section_level: int, extra_metadata: Dict = None) -> DocumentChunk:
        """创建分块对象"""
        metadata = {
            'section_title': section_title,
            'section_level': section_level,
            'token_count': self.count_tokens(content),
            'char_count': len(content)
        }

        if extra_metadata:
            metadata.update(extra_metadata)

        return DocumentChunk(
            chunk_index=0,  # 将在外部设置
            chunk_type=chunk_type,
            content=content,
            metadata=metadata
        )


if __name__ == '__main__':
    # 测试代码
    sample_text = """
第一章 项目概述

本项目是一个智能标书处理系统，主要功能包括：

1. 文档智能分块
2. AI筛选
3. 要求提取

第二章 技术要求

2.1 硬件要求
投标方应提供以下硬件设备：
- 服务器：不少于2台
- 存储：不少于10TB

2.2 软件要求
（1）操作系统：Linux或Windows Server
（2）数据库：MySQL 8.0及以上
（3）编程语言：Python 3.8及以上
"""

    chunker = DocumentChunker(max_chunk_size=200)
    chunks = chunker.chunk_document(sample_text)

    for chunk in chunks:
        print(f"\n【分块 {chunk.chunk_index}】类型: {chunk.chunk_type}")
        print(f"内容: {chunk.content[:100]}...")
        print(f"元数据: {chunk.metadata}")
