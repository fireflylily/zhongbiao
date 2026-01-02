#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录提取器 - 智能识别招标文件的目录结构
用于实现「目录感知 + 智能降级」切片策略
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.llm_client import LLMClient

from .prompt_manager import PromptManager, PromptType

logger = get_module_logger("risk_analyzer.toc_extractor")


@dataclass
class TocEntry:
    """目录条目"""
    title: str                      # 章节标题
    page: Optional[str] = None      # 页码
    level: int = 1                  # 层级 (1=章, 2=节, 3=条)
    entry_type: str = 'normal'      # core|exclude|normal
    reason: str = ''                # 分类原因

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TocResult:
    """目录解析结果"""
    has_toc: bool = False                           # 是否有目录
    entries: List[TocEntry] = field(default_factory=list)  # 目录条目
    exclude_chapters: List[str] = field(default_factory=list)  # 需排除的章节
    core_chapters: List[str] = field(default_factory=list)     # 核心章节
    exclude_page_ranges: List[Dict] = field(default_factory=list)  # 排除页码范围
    raw_toc_text: str = ''                          # 原始目录文本

    def to_dict(self) -> Dict:
        return {
            'has_toc': self.has_toc,
            'entries': [e.to_dict() for e in self.entries],
            'exclude_chapters': self.exclude_chapters,
            'core_chapters': self.core_chapters,
            'exclude_page_ranges': self.exclude_page_ranges,
        }


class TocExtractor:
    """
    目录提取器 - 智能识别文档目录结构

    支持两种模式：
    1. 规则提取：使用正则表达式快速识别标准目录格式
    2. AI 提取：使用 LLM 深度分析复杂目录结构
    """

    # 需要排除的章节关键词
    EXCLUDE_KEYWORDS = [
        '合同', '协议', '范本', '格式', '附件格式', '模板',
        '投标文件格式', '响应文件格式', '合同条款', '合同样书',
        '通用条款', '专用条款', '合同条件', '附录'
    ]

    # 核心章节关键词
    CORE_KEYWORDS = [
        '评标', '评分', '投标人须知', '资格', '要求',
        '技术规格', '商务', '服务要求', '废标', '否决',
        '评审', '招标公告', '投标须知', '资格审查',
        '技术条款', '商务条款', '供货范围'
    ]

    # 目录标记关键词
    TOC_MARKERS = ['目录', '目 录', 'CONTENTS', 'TABLE OF CONTENTS']

    def __init__(self, use_ai: bool = True, model_name: str = 'deepseek-v3'):
        """
        初始化目录提取器

        Args:
            use_ai: 是否使用 AI 进行深度解析
            model_name: AI 模型名称
        """
        self.use_ai = use_ai
        self.model_name = model_name
        self.prompt_manager = PromptManager()

        if use_ai:
            self.llm = LLMClient(model_name)

        logger.info(f"目录提取器初始化完成, use_ai={use_ai}")

    def extract(self, text: str, max_chars: int = 15000) -> TocResult:
        """
        提取文档目录结构

        Args:
            text: 文档全文
            max_chars: 用于目录识别的最大字符数（只分析前面部分）

        Returns:
            TocResult: 目录解析结果
        """
        # 1. 首先尝试规则提取
        result = self._extract_by_rules(text[:max_chars])

        if result.has_toc and len(result.entries) >= 3:
            logger.info(f"规则提取成功，发现 {len(result.entries)} 个目录项")
            return result

        # 2. 如果规则提取失败且开启 AI，使用 AI 提取
        if self.use_ai:
            logger.info("规则提取失败，尝试 AI 提取...")
            ai_result = self._extract_by_ai(text[:max_chars])
            if ai_result.has_toc:
                return ai_result

        # 3. 都失败，返回无目录结果
        logger.info("未能识别目录结构，将使用智能降级策略")
        return TocResult(has_toc=False)

    def _extract_by_rules(self, text: str) -> TocResult:
        """使用规则提取目录"""
        # 查找目录区域
        toc_text, toc_start = self._find_toc_section(text)
        if not toc_text:
            return TocResult(has_toc=False)

        # 解析目录行
        entries = []

        # 模式1: 标准目录格式 (章节名...页码)
        pattern1 = r'^(.+?)[\.…\s·]{2,}(\d+)\s*$'

        # 模式2: 编号目录格式 (第X章/X.Y 章节名)
        pattern2 = r'^(第[一二三四五六七八九十\d]+[章节篇卷]|[\d\.]+)\s*[、．.\s]*(.+?)(?:[\.…\s·]+(\d+))?\s*$'

        for line in toc_text.split('\n'):
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # 尝试模式1
            match = re.match(pattern1, line)
            if match:
                title = match.group(1).strip()
                page = match.group(2)
                entry = self._create_entry(title, page)
                if entry:
                    entries.append(entry)
                continue

            # 尝试模式2
            match = re.match(pattern2, line)
            if match:
                num = match.group(1)
                title_part = match.group(2).strip()
                page = match.group(3)
                full_title = f"{num} {title_part}" if title_part else num
                entry = self._create_entry(full_title, page)
                if entry:
                    entries.append(entry)

        if len(entries) < 3:
            return TocResult(has_toc=False)

        # 生成排除和核心章节列表
        exclude_chapters = [e.title for e in entries if e.entry_type == 'exclude']
        core_chapters = [e.title for e in entries if e.entry_type == 'core']

        # 计算排除页码范围
        exclude_page_ranges = self._calculate_exclude_ranges(entries)

        return TocResult(
            has_toc=True,
            entries=entries,
            exclude_chapters=exclude_chapters,
            core_chapters=core_chapters,
            exclude_page_ranges=exclude_page_ranges,
            raw_toc_text=toc_text
        )

    def _find_toc_section(self, text: str) -> Tuple[Optional[str], int]:
        """查找目录区域"""
        # 查找目录起始位置
        toc_start = -1
        for marker in self.TOC_MARKERS:
            pos = text.find(marker)
            if pos != -1:
                toc_start = pos
                break

        if toc_start == -1:
            # 没有明确的目录标记，尝试识别结构化文本
            return self._find_implicit_toc(text)

        # 提取目录区域（目录标记后的 5000-10000 字符）
        toc_text = text[toc_start:toc_start + 10000]

        # 尝试找到目录结束位置（通常是第一章/正文开始）
        end_markers = ['第一章', '第1章', '一、', '1、', '1.', '1．']
        toc_end = len(toc_text)

        for marker in end_markers:
            # 跳过目录中的引用，找正文中的标记
            pos = toc_text.find(marker, 200)  # 跳过前200字符（目录本身）
            if pos != -1 and pos < toc_end:
                # 检查是否是正文开始（不是目录中的条目）
                before_text = toc_text[max(0, pos-20):pos]
                if '\n' in before_text and not re.search(r'[\d\.…]+\s*$', before_text):
                    toc_end = pos
                    break

        return toc_text[:toc_end], toc_start

    def _find_implicit_toc(self, text: str) -> Tuple[Optional[str], int]:
        """识别隐式目录结构（没有明确目录标记的情况）"""
        # 查找连续的编号行
        lines = text[:8000].split('\n')
        numbered_lines = []
        start_idx = -1

        for i, line in enumerate(lines):
            line = line.strip()
            if re.match(r'^(第[一二三四五六七八九十\d]+[章节]|[\d\.]+[、．.\s])', line):
                if start_idx == -1:
                    start_idx = i
                numbered_lines.append(line)
            elif numbered_lines and len(numbered_lines) >= 3:
                # 已收集到足够的目录行
                break

        if len(numbered_lines) >= 5:
            return '\n'.join(numbered_lines), 0

        return None, -1

    def _create_entry(self, title: str, page: Optional[str]) -> Optional[TocEntry]:
        """创建目录条目并分类"""
        if not title or len(title) < 2:
            return None

        # 检测层级
        level = self._detect_level(title)

        # 分类
        entry_type, reason = self._classify_chapter(title)

        return TocEntry(
            title=title,
            page=page,
            level=level,
            entry_type=entry_type,
            reason=reason
        )

    def _detect_level(self, title: str) -> int:
        """检测章节层级"""
        if re.match(r'^第[一二三四五六七八九十\d]+章', title):
            return 1
        elif re.match(r'^第[一二三四五六七八九十\d]+节', title):
            return 2
        elif re.match(r'^第[一二三四五六七八九十\d]+条', title):
            return 3
        elif re.match(r'^\d+\.\d+\.\d+', title):
            return 3
        elif re.match(r'^\d+\.\d+', title):
            return 2
        elif re.match(r'^\d+[\.、]', title):
            return 1
        elif re.match(r'^[一二三四五六七八九十]+[、．.]', title):
            return 1
        return 2

    def _classify_chapter(self, title: str) -> Tuple[str, str]:
        """分类章节类型"""
        title_lower = title.lower()

        # 检查是否需要排除
        for kw in self.EXCLUDE_KEYWORDS:
            if kw in title_lower:
                return 'exclude', f'包含关键词"{kw}"'

        # 检查是否为核心章节
        for kw in self.CORE_KEYWORDS:
            if kw in title_lower:
                return 'core', f'包含关键词"{kw}"'

        return 'normal', ''

    def _calculate_exclude_ranges(self, entries: List[TocEntry]) -> List[Dict]:
        """计算需要排除的页码范围"""
        ranges = []
        sorted_entries = [e for e in entries if e.page and e.page.isdigit()]
        sorted_entries.sort(key=lambda x: int(x.page))

        for i, entry in enumerate(sorted_entries):
            if entry.entry_type != 'exclude':
                continue

            start_page = int(entry.page)

            # 找到下一个非排除章节的起始页
            end_page = start_page + 50  # 默认假设50页

            for j in range(i + 1, len(sorted_entries)):
                next_entry = sorted_entries[j]
                if next_entry.entry_type != 'exclude':
                    end_page = int(next_entry.page) - 1
                    break

            ranges.append({
                'title': entry.title,
                'start': start_page,
                'end': end_page
            })

        return ranges

    def _extract_by_ai(self, text: str) -> TocResult:
        """使用 AI 提取目录结构"""
        try:
            # 获取提示词
            prompt = self.prompt_manager.get_prompt(
                PromptType.TOC_NAVIGATOR,
                toc_content=text[:8000]  # 限制输入长度
            )

            config = self.prompt_manager.get_config(PromptType.TOC_NAVIGATOR)

            # 调用 LLM
            response = self.llm.call(
                prompt=prompt,
                system_prompt=config['system_prompt'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                purpose=config['purpose']
            )

            # 解析响应
            return self._parse_ai_response(response)

        except Exception as e:
            logger.error(f"AI 目录提取失败: {e}")
            return TocResult(has_toc=False)

    def _parse_ai_response(self, response: str) -> TocResult:
        """解析 AI 响应"""
        if not response:
            return TocResult(has_toc=False)

        # 清理 markdown 代码块
        response = re.sub(r'^\s*```json\s*', '', response.strip())
        response = re.sub(r'\s*```\s*$', '', response.strip())

        try:
            data = json.loads(response)

            # 解析章节条目
            entries = []
            for ch in data.get('chapters', []):
                entry = TocEntry(
                    title=ch.get('title', ''),
                    page=ch.get('page'),
                    level=1,
                    entry_type=ch.get('type', 'normal'),
                    reason=ch.get('reason', '')
                )
                entries.append(entry)

            return TocResult(
                has_toc=data.get('has_toc', False),
                entries=entries,
                exclude_chapters=data.get('exclude_chapters', []),
                core_chapters=data.get('core_chapters', []),
                exclude_page_ranges=data.get('exclude_page_ranges', [])
            )

        except json.JSONDecodeError as e:
            logger.warning(f"AI 响应 JSON 解析失败: {e}")
            return TocResult(has_toc=False)


# 便捷函数
def extract_toc(text: str, use_ai: bool = True) -> TocResult:
    """
    便捷函数：提取文档目录

    Args:
        text: 文档文本
        use_ai: 是否使用 AI

    Returns:
        TocResult
    """
    extractor = TocExtractor(use_ai=use_ai)
    return extractor.extract(text)
