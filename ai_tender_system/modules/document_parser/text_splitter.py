#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文本分块器
基于语义和结构的高质量文档分块系统
"""

import re
import jieba
import tiktoken
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("document_parser.text_splitter")


class SplitStrategy(Enum):
    """分块策略枚举"""
    HIERARCHICAL = "hierarchical"  # 基于标题层级
    SEMANTIC = "semantic"          # 基于语义完整性
    FIXED_SIZE = "fixed_size"      # 固定大小
    TABLE_AWARE = "table_aware"    # 表格感知
    HYBRID = "hybrid"              # 混合策略


@dataclass
class TextChunk:
    """文本块数据类"""
    index: int
    content: str
    start_pos: int
    end_pos: int
    token_count: int
    chunk_type: str = "text"      # text, table, heading, list
    metadata: Dict = None
    embedding: Optional[List[float]] = None
    heading_context: List[str] = None  # 标题上下文

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.heading_context is None:
            self.heading_context = []


class IntelligentTextSplitter:
    """智能文本分块器"""

    def __init__(self,
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 min_chunk_size: int = 100,
                 max_chunk_size: int = 1000):
        """
        初始化文本分块器

        Args:
            chunk_size: 目标块大小（token数）
            chunk_overlap: 重叠token数
            min_chunk_size: 最小块大小
            max_chunk_size: 最大块大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

        self.logger = logger

        # 初始化tokenizer
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            self.logger.warning(f"无法加载tiktoken，使用简单字符计数: {e}")
            self.tokenizer = None

        # 初始化中文分词器
        jieba.setLogLevel(jieba.logging.INFO)

        self.logger.info("智能文本分块器初始化完成")

    def split_text(self, content: str, metadata: Dict = None, strategy: str = "hybrid") -> List[Dict]:
        """
        分割文本的主要方法

        Args:
            content: 待分割的文本内容
            metadata: 文档元数据
            strategy: 分割策略

        Returns:
            List[Dict]: 分块结果列表
        """
        if not content or not content.strip():
            return []

        strategy_enum = SplitStrategy(strategy)
        metadata = metadata or {}

        self.logger.info(f"开始文本分块: strategy={strategy}, content_length={len(content)}")

        try:
            if strategy_enum == SplitStrategy.HIERARCHICAL:
                chunks = self._split_by_hierarchy(content, metadata)
            elif strategy_enum == SplitStrategy.SEMANTIC:
                chunks = self._split_by_semantics(content, metadata)
            elif strategy_enum == SplitStrategy.TABLE_AWARE:
                chunks = self._split_table_aware(content, metadata)
            elif strategy_enum == SplitStrategy.FIXED_SIZE:
                chunks = self._split_fixed_size(content, metadata)
            elif strategy_enum == SplitStrategy.HYBRID:
                chunks = self._split_hybrid(content, metadata)
            else:
                chunks = self._split_fixed_size(content, metadata)

            # 后处理：添加上下文和验证
            processed_chunks = self._post_process_chunks(chunks, content)

            self.logger.info(f"文本分块完成: chunks={len(processed_chunks)}")

            return [chunk.to_dict() for chunk in processed_chunks]

        except Exception as e:
            self.logger.error(f"文本分块失败: {e}")
            # 降级到简单分块
            return self._fallback_split(content, metadata)

    def _split_by_hierarchy(self, content: str, metadata: Dict) -> List[TextChunk]:
        """基于标题层级的分块"""
        chunks = []

        # 提取标题信息
        headings = self._extract_headings(content)

        if not headings:
            # 没有标题，降级到语义分块
            return self._split_by_semantics(content, metadata)

        # 按标题分段
        sections = self._split_by_headings(content, headings)

        chunk_index = 0
        for section in sections:
            # 检查段落大小
            token_count = self._count_tokens(section['content'])

            if token_count <= self.max_chunk_size:
                # 整个段落作为一个块
                chunk = TextChunk(
                    index=chunk_index,
                    content=section['content'],
                    start_pos=section['start_pos'],
                    end_pos=section['end_pos'],
                    token_count=token_count,
                    chunk_type="section",
                    heading_context=section.get('heading_context', []),
                    metadata={
                        'heading_level': section.get('heading_level', 0),
                        'section_title': section.get('title', ''),
                        'split_strategy': 'hierarchical'
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # 大段落需要进一步分割
                sub_chunks = self._split_large_section(section, chunk_index)
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)

        return chunks

    def _split_by_semantics(self, content: str, metadata: Dict) -> List[TextChunk]:
        """基于语义完整性的分块"""
        chunks = []

        # 按段落分割
        paragraphs = self._split_into_paragraphs(content)

        current_chunk = ""
        current_start = 0
        chunk_index = 0

        for i, para in enumerate(paragraphs):
            para_tokens = self._count_tokens(para['content'])
            current_tokens = self._count_tokens(current_chunk)

            # 检查是否应该开始新块
            if (current_tokens + para_tokens > self.chunk_size and
                current_tokens >= self.min_chunk_size):

                # 创建当前块
                if current_chunk.strip():
                    chunk = TextChunk(
                        index=chunk_index,
                        content=current_chunk.strip(),
                        start_pos=current_start,
                        end_pos=para['start_pos'],
                        token_count=current_tokens,
                        chunk_type="semantic",
                        metadata={'split_strategy': 'semantic'}
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                # 开始新块（包含重叠）
                overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + para['content']
                current_start = para['start_pos'] - len(overlap_text)

            else:
                # 添加到当前块
                if current_chunk:
                    current_chunk += "\n\n" + para['content']
                else:
                    current_chunk = para['content']
                    current_start = para['start_pos']

        # 处理最后一个块
        if current_chunk.strip():
            chunk = TextChunk(
                index=chunk_index,
                content=current_chunk.strip(),
                start_pos=current_start,
                end_pos=len(content),
                token_count=self._count_tokens(current_chunk),
                chunk_type="semantic",
                metadata={'split_strategy': 'semantic'}
            )
            chunks.append(chunk)

        return chunks

    def _split_table_aware(self, content: str, metadata: Dict) -> List[TextChunk]:
        """表格感知的分块"""
        chunks = []

        # 识别表格区域
        table_regions = self._identify_table_regions(content)

        if not table_regions:
            return self._split_by_semantics(content, metadata)

        # 按表格边界分割内容
        current_pos = 0
        chunk_index = 0

        for table in table_regions:
            # 处理表格前的文本
            if current_pos < table['start']:
                pre_text = content[current_pos:table['start']].strip()
                if pre_text:
                    pre_chunks = self._split_by_semantics(pre_text, metadata)
                    for chunk in pre_chunks:
                        chunk.index = chunk_index
                        chunk_index += 1
                    chunks.extend(pre_chunks)

            # 处理表格本身
            table_content = content[table['start']:table['end']]
            table_chunk = TextChunk(
                index=chunk_index,
                content=table_content,
                start_pos=table['start'],
                end_pos=table['end'],
                token_count=self._count_tokens(table_content),
                chunk_type="table",
                metadata={
                    'split_strategy': 'table_aware',
                    'table_info': table.get('info', {})
                }
            )
            chunks.append(table_chunk)
            chunk_index += 1
            current_pos = table['end']

        # 处理最后部分的文本
        if current_pos < len(content):
            post_text = content[current_pos:].strip()
            if post_text:
                post_chunks = self._split_by_semantics(post_text, metadata)
                for chunk in post_chunks:
                    chunk.index = chunk_index
                    chunk_index += 1
                chunks.extend(post_chunks)

        return chunks

    def _split_fixed_size(self, content: str, metadata: Dict) -> List[TextChunk]:
        """固定大小分块"""
        chunks = []

        # 简单的字符分割
        sentences = self._split_into_sentences(content)

        current_chunk = ""
        current_start = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            current_tokens = self._count_tokens(current_chunk)

            if current_tokens + sentence_tokens > self.chunk_size and current_tokens > 0:
                # 创建块
                chunk = TextChunk(
                    index=chunk_index,
                    content=current_chunk.strip(),
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    token_count=current_tokens,
                    chunk_type="fixed_size",
                    metadata={'split_strategy': 'fixed_size'}
                )
                chunks.append(chunk)
                chunk_index += 1

                # 处理重叠
                overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + sentence
                current_start += len(current_chunk) - len(overlap_text) - len(sentence)
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                    current_start = content.find(sentence)

        # 最后一个块
        if current_chunk.strip():
            chunk = TextChunk(
                index=chunk_index,
                content=current_chunk.strip(),
                start_pos=current_start,
                end_pos=len(content),
                token_count=self._count_tokens(current_chunk),
                chunk_type="fixed_size",
                metadata={'split_strategy': 'fixed_size'}
            )
            chunks.append(chunk)

        return chunks

    def _split_hybrid(self, content: str, metadata: Dict) -> List[TextChunk]:
        """混合分块策略"""
        # 优先使用层级分块
        headings = self._extract_headings(content)
        tables = self._identify_table_regions(content)

        if headings:
            return self._split_by_hierarchy(content, metadata)
        elif tables:
            return self._split_table_aware(content, metadata)
        else:
            return self._split_by_semantics(content, metadata)

    def _extract_headings(self, content: str) -> List[Dict]:
        """提取标题"""
        headings = []

        # 标题模式
        heading_patterns = [
            (r'^(第[一二三四五六七八九十\d]+[章节条].*)', 1),
            (r'^(\d+\.?\d*\s+.{1,100})', 2),
            (r'^([一二三四五六七八九十]+[、\.]\s*.{1,80})', 3),
            (r'^(#{1,6}\s+.+)', None),  # Markdown标题
            (r'^([A-Z][A-Z\s]{5,50})\s*$', 2),  # 全大写标题
        ]

        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            for pattern, level in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    # Markdown标题的级别检测
                    if level is None:
                        level = len(re.match(r'^#+', line).group())

                    headings.append({
                        'text': match.group(1),
                        'level': level,
                        'line_number': i,
                        'start_pos': content.find(line),
                        'pattern': pattern
                    })
                    break

        return headings

    def _split_by_headings(self, content: str, headings: List[Dict]) -> List[Dict]:
        """按标题分割内容"""
        sections = []
        lines = content.split('\n')

        for i, heading in enumerate(headings):
            start_line = heading['line_number']
            end_line = headings[i + 1]['line_number'] if i + 1 < len(headings) else len(lines)

            section_lines = lines[start_line:end_line]
            section_content = '\n'.join(section_lines).strip()

            if section_content:
                sections.append({
                    'title': heading['text'],
                    'content': section_content,
                    'start_pos': content.find(section_content),
                    'end_pos': content.find(section_content) + len(section_content),
                    'heading_level': heading['level'],
                    'heading_context': [heading['text']]
                })

        return sections

    def _split_into_paragraphs(self, content: str) -> List[Dict]:
        """分割成段落"""
        paragraphs = []
        current_pos = 0

        # 按双换行符分割段落
        para_texts = re.split(r'\n\s*\n', content)

        for para_text in para_texts:
            para_text = para_text.strip()
            if para_text:
                start_pos = content.find(para_text, current_pos)
                paragraphs.append({
                    'content': para_text,
                    'start_pos': start_pos,
                    'end_pos': start_pos + len(para_text)
                })
                current_pos = start_pos + len(para_text)

        return paragraphs

    def _split_into_sentences(self, content: str) -> List[str]:
        """分割成句子"""
        # 中英文句子边界检测
        sentence_endings = r'[。！？；.!?;]\s*'
        sentences = re.split(sentence_endings, content)

        # 清理空句子
        return [s.strip() for s in sentences if s.strip()]

    def _identify_table_regions(self, content: str) -> List[Dict]:
        """识别表格区域"""
        table_regions = []

        # 查找表格标记
        table_patterns = [
            r'\[表格\s*\d*\]',
            r'┌.*┐',  # 表格边框
            r'\|.*\|.*\|',  # Markdown表格
        ]

        for pattern in table_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                # 扩展表格区域（向前向后查找相关内容）
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 500)

                table_regions.append({
                    'start': start,
                    'end': end,
                    'pattern': pattern,
                    'info': {'type': 'detected_table'}
                })

        return table_regions

    def _count_tokens(self, text: str) -> int:
        """计算token数量"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except:
                pass

        # 简单估算：中文字符按1.5个token计算，英文单词按1个token
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return int(chinese_chars * 1.5 + english_words)

    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """获取重叠文本"""
        if overlap_tokens <= 0:
            return ""

        # 从文本末尾获取指定token数量的内容
        sentences = self._split_into_sentences(text)
        overlap_text = ""

        for sentence in reversed(sentences):
            if self._count_tokens(overlap_text + sentence) <= overlap_tokens:
                overlap_text = sentence + " " + overlap_text
            else:
                break

        return overlap_text.strip()

    def _split_large_section(self, section: Dict, start_index: int) -> List[TextChunk]:
        """分割大段落"""
        content = section['content']
        sub_chunks = self._split_by_semantics(content, {})

        # 更新索引和上下文
        for i, chunk in enumerate(sub_chunks):
            chunk.index = start_index + i
            chunk.heading_context = section.get('heading_context', [])
            chunk.metadata.update({
                'parent_section': section.get('title', ''),
                'section_part': i + 1,
                'total_parts': len(sub_chunks)
            })

        return sub_chunks

    def _post_process_chunks(self, chunks: List[TextChunk], original_content: str) -> List[TextChunk]:
        """后处理分块结果"""
        processed_chunks = []

        for chunk in chunks:
            # 验证块的有效性
            if chunk.token_count < self.min_chunk_size and chunk.chunk_type != "table":
                # 尝试与相邻块合并
                if processed_chunks:
                    last_chunk = processed_chunks[-1]
                    if (last_chunk.token_count + chunk.token_count <= self.max_chunk_size and
                        last_chunk.chunk_type == chunk.chunk_type):
                        # 合并块
                        last_chunk.content += "\n\n" + chunk.content
                        last_chunk.end_pos = chunk.end_pos
                        last_chunk.token_count += chunk.token_count
                        continue

            # 添加额外的元数据
            chunk.metadata.update({
                'token_count': chunk.token_count,
                'char_count': len(chunk.content),
                'chunk_quality': self._assess_chunk_quality(chunk)
            })

            processed_chunks.append(chunk)

        # 重新编号
        for i, chunk in enumerate(processed_chunks):
            chunk.index = i

        return processed_chunks

    def _assess_chunk_quality(self, chunk: TextChunk) -> float:
        """评估块质量"""
        score = 0.0
        content = chunk.content

        # 长度适中性
        if self.min_chunk_size <= chunk.token_count <= self.chunk_size:
            score += 0.3

        # 语义完整性（句子完整性）
        if content.strip().endswith(('.', '。', '!', '！', '?', '？')):
            score += 0.2

        # 结构完整性（段落完整性）
        if '\n\n' in content or chunk.chunk_type == "section":
            score += 0.2

        # 信息密度
        if len(content.strip()) > 50:  # 不是过短的内容
            score += 0.3

        return min(1.0, score)

    def _fallback_split(self, content: str, metadata: Dict) -> List[Dict]:
        """降级分块策略"""
        self.logger.warning("使用降级分块策略")

        # 简单的固定长度分块
        chunks = []
        chunk_size_chars = self.chunk_size * 4  # 粗略估算

        for i in range(0, len(content), chunk_size_chars):
            chunk_content = content[i:i + chunk_size_chars]
            chunks.append({
                'index': len(chunks),
                'content': chunk_content,
                'start_pos': i,
                'end_pos': i + len(chunk_content),
                'token_count': self._count_tokens(chunk_content),
                'chunk_type': 'fallback',
                'metadata': {'split_strategy': 'fallback'},
                'heading_context': []
            })

        return chunks

    def to_dict(self, chunk: TextChunk) -> Dict:
        """将TextChunk转换为字典"""
        return {
            'index': chunk.index,
            'content': chunk.content,
            'start_pos': chunk.start_pos,
            'end_pos': chunk.end_pos,
            'token_count': chunk.token_count,
            'chunk_type': chunk.chunk_type,
            'metadata': chunk.metadata,
            'heading_context': chunk.heading_context
        }

# 为TextChunk添加to_dict方法
TextChunk.to_dict = lambda self: {
    'index': self.index,
    'content': self.content,
    'start_pos': self.start_pos,
    'end_pos': self.end_pos,
    'token_count': self.token_count,
    'chunk_type': self.chunk_type,
    'metadata': self.metadata,
    'heading_context': self.heading_context
}