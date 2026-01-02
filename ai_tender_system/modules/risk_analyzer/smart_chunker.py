#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能切片器 - 实现「目录感知 + 智能降级」切片策略
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from .toc_extractor import TocResult, TocEntry

logger = get_module_logger("risk_analyzer.smart_chunker")


@dataclass
class DocumentChunk:
    """文档切片"""
    title: str                          # 切片标题
    content: str                        # 切片内容
    chunk_index: int = 0                # 切片索引
    page_range: Optional[str] = None    # 页码范围（如 "P12-P15"）
    chunk_type: str = 'size_based'      # toc_based | size_based
    is_core: bool = False               # 是否为核心章节
    char_count: int = 0                 # 字符数

    def to_dict(self) -> Dict:
        return asdict(self)


class SmartChunker:
    """
    智能切片器 - 目录感知 + 智能降级

    工作模式：
    1. 有目录时：按章节边界切片，自动跳过合同等排除章节
    2. 无目录时：按固定字数切片，但在提示词中告诉 AI 忽略合同内容
    """

    # 默认切片配置
    DEFAULT_CHUNK_SIZE = 5000       # 默认切片大小（字符）
    MIN_CHUNK_SIZE = 1000           # 最小切片大小
    MAX_CHUNK_SIZE = 8000           # 最大切片大小
    CHUNK_OVERLAP = 200             # 切片重叠

    # 用于识别章节边界的模式
    CHAPTER_PATTERNS = [
        r'^第[一二三四五六七八九十\d]+[章节篇卷]',
        r'^\d+\.\s+',
        r'^[一二三四五六七八九十]+[、．.]',
    ]

    def __init__(self,
                 toc_result: Optional[TocResult] = None,
                 chunk_size: int = DEFAULT_CHUNK_SIZE):
        """
        初始化智能切片器

        Args:
            toc_result: 目录解析结果（可选）
            chunk_size: 目标切片大小
        """
        self.toc_result = toc_result
        self.chunk_size = max(self.MIN_CHUNK_SIZE, min(chunk_size, self.MAX_CHUNK_SIZE))
        self.has_toc = toc_result is not None and toc_result.has_toc

        logger.info(f"智能切片器初始化, has_toc={self.has_toc}, chunk_size={self.chunk_size}")

    def chunk_document(self, text: str) -> List[DocumentChunk]:
        """
        智能切片文档

        Args:
            text: 文档全文

        Returns:
            切片列表
        """
        if self.has_toc:
            chunks = self._chunk_by_toc(text)
            if chunks:
                return chunks
            logger.warning("目录切片失败，降级为按字数切片")

        return self._chunk_by_size(text)

    def _chunk_by_toc(self, text: str) -> List[DocumentChunk]:
        """基于目录切片（排除合同章节）"""
        if not self.toc_result or not self.toc_result.entries:
            return []

        chunks = []
        chunk_index = 0

        # 过滤出需要分析的章节
        valid_entries = [
            e for e in self.toc_result.entries
            if e.entry_type != 'exclude'
        ]

        if not valid_entries:
            return []

        logger.info(f"目录切片: 共 {len(self.toc_result.entries)} 个章节, "
                   f"过滤后 {len(valid_entries)} 个待分析章节")

        for i, entry in enumerate(valid_entries):
            # 确定章节边界
            start_marker = entry.title
            end_marker = None
            if i + 1 < len(valid_entries):
                end_marker = valid_entries[i + 1].title

            # 提取章节内容
            content = self._extract_section(text, start_marker, end_marker)

            if not content or len(content.strip()) < self.MIN_CHUNK_SIZE:
                continue

            # 如果章节太长，进一步分割
            if len(content) > self.MAX_CHUNK_SIZE:
                sub_chunks = self._split_large_section(
                    content,
                    entry.title,
                    chunk_index,
                    is_core=(entry.entry_type == 'core')
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
            else:
                chunks.append(DocumentChunk(
                    title=entry.title,
                    content=content,
                    chunk_index=chunk_index,
                    page_range=f"P{entry.page}" if entry.page else None,
                    chunk_type='toc_based',
                    is_core=(entry.entry_type == 'core'),
                    char_count=len(content)
                ))
                chunk_index += 1

        logger.info(f"目录切片完成: 生成 {len(chunks)} 个切片")
        return chunks

    def _chunk_by_size(self, text: str) -> List[DocumentChunk]:
        """基于字数切片（无目录时使用）"""
        # 首先尝试移除明显的合同部分
        cleaned_text = self._remove_contract_sections(text)

        total_length = len(cleaned_text)
        if total_length < self.MIN_CHUNK_SIZE:
            return []

        # 计算目标切片数
        target_chunks = max(3, min(20, total_length // self.chunk_size))
        actual_chunk_size = total_length // target_chunks

        chunks = []
        start = 0
        chunk_index = 0

        while start < total_length:
            end = min(start + actual_chunk_size, total_length)

            # 尝试在自然边界处切分
            if end < total_length:
                boundary = self._find_natural_boundary(cleaned_text, start, end)
                if boundary > start:
                    end = boundary

            content = cleaned_text[start:end].strip()

            if len(content) > 100:  # 过滤太短的片段
                chunks.append(DocumentChunk(
                    title=f"第{chunk_index + 1}部分",
                    content=content,
                    chunk_index=chunk_index,
                    page_range=None,
                    chunk_type='size_based',
                    is_core=False,  # 无目录时无法判断
                    char_count=len(content)
                ))
                chunk_index += 1

            start = end

        logger.info(f"按字数切片完成: {total_length}字 -> {len(chunks)}个切片, "
                   f"平均每块 {total_length // max(1, len(chunks))} 字")
        return chunks

    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """从文本中提取指定章节"""
        # 清理标记中的特殊字符
        start_pattern = re.escape(start_marker.strip())

        # 查找起始位置
        match = re.search(start_pattern, text)
        if not match:
            # 尝试模糊匹配
            start_pos = self._fuzzy_find(text, start_marker)
            if start_pos == -1:
                return ""
        else:
            start_pos = match.start()

        # 确定结束位置
        if end_marker:
            end_pattern = re.escape(end_marker.strip())
            end_match = re.search(end_pattern, text[start_pos + len(start_marker):])
            if end_match:
                end_pos = start_pos + len(start_marker) + end_match.start()
            else:
                end_pos = len(text)
        else:
            end_pos = len(text)

        return text[start_pos:end_pos]

    def _fuzzy_find(self, text: str, marker: str) -> int:
        """模糊查找章节标记"""
        # 提取标记中的关键部分
        keywords = re.findall(r'[\u4e00-\u9fa5]+', marker)

        for keyword in keywords:
            if len(keyword) >= 2:
                pos = text.find(keyword)
                if pos != -1:
                    # 回退到行首
                    line_start = text.rfind('\n', 0, pos)
                    return line_start + 1 if line_start != -1 else 0

        return -1

    def _split_large_section(self,
                             content: str,
                             title: str,
                             base_index: int,
                             is_core: bool) -> List[DocumentChunk]:
        """将大章节进一步分割"""
        chunks = []
        part_num = 1
        start = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))

            # 在自然边界切分
            if end < len(content):
                boundary = self._find_natural_boundary(content, start, end)
                if boundary > start:
                    end = boundary

            sub_content = content[start:end].strip()

            if len(sub_content) > 100:
                chunks.append(DocumentChunk(
                    title=f"{title} (Part {part_num})",
                    content=sub_content,
                    chunk_index=base_index + part_num - 1,
                    page_range=None,
                    chunk_type='toc_based',
                    is_core=is_core,
                    char_count=len(sub_content)
                ))
                part_num += 1

            start = end

        return chunks

    def _find_natural_boundary(self, text: str, start: int, end: int) -> int:
        """在自然边界处切分（段落、句子）"""
        search_start = max(start, end - 500)
        search_end = min(len(text), end + 500)
        segment = text[search_start:search_end]

        # 优先在段落边界切分
        para_pos = segment.rfind('\n\n')
        if para_pos > 0:
            return search_start + para_pos + 2

        # 其次在换行符处切分
        newline_pos = segment.rfind('\n')
        if newline_pos > 0:
            return search_start + newline_pos + 1

        # 最后在句号处切分
        for punct in ['。', '；', '！', '？', '.']:
            punct_pos = segment.rfind(punct)
            if punct_pos > 0:
                return search_start + punct_pos + 1

        return end

    def _remove_contract_sections(self, text: str) -> str:
        """尝试移除明显的合同部分"""
        # 合同章节的常见标记
        contract_markers = [
            (r'第[一二三四五六七八九十\d]+[章节]\s*合同', r'第[一二三四五六七八九十\d]+[章节](?!.*合同)'),
            (r'合同协议书', None),
            (r'通用合同条款', None),
            (r'专用合同条款', None),
        ]

        cleaned = text

        for start_marker, end_marker_pattern in contract_markers:
            match = re.search(start_marker, cleaned)
            if match:
                start_pos = match.start()

                # 找结束位置
                if end_marker_pattern:
                    end_match = re.search(end_marker_pattern, cleaned[start_pos + 10:])
                    if end_match:
                        end_pos = start_pos + 10 + end_match.start()
                    else:
                        # 假设合同部分最多 20000 字符
                        end_pos = min(start_pos + 20000, len(cleaned))
                else:
                    end_pos = min(start_pos + 15000, len(cleaned))

                # 移除这部分
                logger.debug(f"移除合同部分: {start_pos}-{end_pos}")
                cleaned = cleaned[:start_pos] + "\n[合同部分已跳过]\n" + cleaned[end_pos:]

        return cleaned

    def get_exclude_info(self) -> Dict:
        """获取排除信息（用于前端显示）"""
        if not self.has_toc or not self.toc_result:
            return {
                'has_toc': False,
                'exclude_chapters': [],
                'core_chapters': [],
                'message': '未识别到目录结构，已使用智能切片并在分析时自动过滤合同内容'
            }

        return {
            'has_toc': True,
            'exclude_chapters': self.toc_result.exclude_chapters,
            'core_chapters': self.toc_result.core_chapters,
            'exclude_page_ranges': self.toc_result.exclude_page_ranges,
            'message': f'已识别目录结构，将跳过 {len(self.toc_result.exclude_chapters)} 个合同相关章节'
        }


# 便捷函数
def smart_chunk(text: str,
                toc_result: Optional[TocResult] = None,
                chunk_size: int = SmartChunker.DEFAULT_CHUNK_SIZE) -> List[DocumentChunk]:
    """
    便捷函数：智能切片文档

    Args:
        text: 文档文本
        toc_result: 目录解析结果
        chunk_size: 切片大小

    Returns:
        切片列表
    """
    chunker = SmartChunker(toc_result=toc_result, chunk_size=chunk_size)
    return chunker.chunk_document(text)
