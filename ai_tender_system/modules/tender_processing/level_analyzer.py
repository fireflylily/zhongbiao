#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节层级分析器

职责：
1. 整体分析目录编号格式，建立层级映射
2. 检测单个标题的层级
3. 校验Word大纲级别的准确性

核心算法：
- 基于编号格式的点号计数（1.=1级，1.1=2级，1.1.1=3级）
- 识别中文章节格式（第X章=1级，第X节=2级）
- 作为辅助的缩进距离判断
"""

import re
from typing import List, Dict, Optional
from common import get_module_logger

logger = get_module_logger("level_analyzer")


class LevelAnalyzer:
    """章节层级分析器"""

    def __init__(self):
        self.logger = get_module_logger("level_analyzer")

    def extract_numbering_pattern(self, title: str) -> Dict:
        """
        提取标题的编号模式

        Args:
            title: 标题文本，如 "1.1 背景介绍"

        Returns:
            {
                "type": "numeric_dot" | "chinese_chapter" | "chinese_enum" | "none",
                "depth": 2,  # 点号数量（对于numeric_dot）
                "pattern": "1.1",  # 原始编号
                "level": 2  # 推断的层级
            }
        """
        title = title.strip()

        # 模式1: 数字点号格式 (1., 1.1, 1.1.1)
        match = re.match(r'^(\d+(?:\.\d+)*)', title)
        if match:
            pattern = match.group(1)
            dots = pattern.count('.')
            return {
                "type": "numeric_dot",
                "depth": dots,
                "pattern": pattern,
                "level": min(dots + 1, 3)  # 1.=1级, 1.1=2级, 1.1.1=3级
            }

        # 模式2: 中文章节格式
        # "第X章" / "第X部分" -> 1级
        if re.match(r'^第[一二三四五六七八九十\d]+[章部分]', title):
            return {
                "type": "chinese_chapter",
                "depth": 0,
                "pattern": "第X章",
                "level": 1
            }

        # "第X节" -> 2级
        if re.match(r'^第[一二三四五六七八九十\d]+节', title):
            return {
                "type": "chinese_section",
                "depth": 1,
                "pattern": "第X节",
                "level": 2
            }

        # "第X条" -> 3级
        if re.match(r'^第[一二三四五六七八九十\d]+条', title):
            return {
                "type": "chinese_item",
                "depth": 2,
                "pattern": "第X条",
                "level": 3
            }

        # 模式3: 中文序号
        # "一、" "二、" -> 1级
        if re.match(r'^[一二三四五六七八九十]+、', title):
            return {
                "type": "chinese_enum",
                "depth": 0,
                "pattern": "X、",
                "level": 1
            }

        # "（一）" "（二）" -> 2级
        if re.match(r'^[（(][一二三四五六七八九十]+[）)]', title):
            return {
                "type": "chinese_enum_paren",
                "depth": 1,
                "pattern": "（X）",
                "level": 2
            }

        # 无法识别的格式
        return {
            "type": "none",
            "depth": 0,
            "pattern": "",
            "level": 1  # 默认1级
        }

    def detect_single_level(self, title: str, indent_pt: float = 0) -> int:
        """
        检测单个标题的层级（从structure_parser._detect_toc_level迁移）

        优先级：
        1. 点号计数（最可靠）
        2. 中文格式
        3. 缩进距离（作为辅助）

        Args:
            title: 标题文本
            indent_pt: 缩进距离（磅）

        Returns:
            1-3: 标题层级
        """
        # 优先使用编号模式分析
        pattern_info = self.extract_numbering_pattern(title)
        if pattern_info['type'] != 'none':
            return pattern_info['level']

        # 如果无法从编号识别，使用缩进距离
        if indent_pt > 40:
            return 3
        elif indent_pt > 20:
            return 2

        # 默认1级
        return 1

    def analyze_toc_hierarchy(self, toc_items: List[Dict]) -> List[int]:
        """
        整体分析目录层级（核心方法）

        策略：
        1. 提取所有条目的编号模式
        2. 统计每种模式的出现次数和层级分布
        3. 建立智能的"模式→层级"映射表
        4. 返回每个条目的修正层级

        Args:
            toc_items: 目录项列表，格式：[{'title': '...', 'page_num': 1, 'level': 1}, ...]

        Returns:
            每个目录项的修正层级列表，如 [1, 2, 3, 2, 1, ...]
        """
        if not toc_items:
            return []

        self.logger.info(f"开始整体分析 {len(toc_items)} 个目录项的层级")

        # 步骤1: 提取所有编号模式
        patterns = []
        for item in toc_items:
            pattern_info = self.extract_numbering_pattern(item['title'])
            patterns.append(pattern_info)

        # 步骤2: 统计模式类型分布
        type_counts = {}
        for p in patterns:
            ptype = p['type']
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

        self.logger.debug(f"编号模式统计: {type_counts}")

        # 步骤3: 识别主要编号风格
        # 找出最常见的编号类型（排除'none'）
        valid_types = {k: v for k, v in type_counts.items() if k != 'none'}
        if valid_types:
            dominant_type = max(valid_types, key=valid_types.get)
            self.logger.info(f"主要编号风格: {dominant_type} (出现{valid_types[dominant_type]}次)")
        else:
            dominant_type = None
            self.logger.warning("未检测到明确的编号风格")

        # 步骤4: 建立层级映射
        # 对于numeric_dot类型，使用点号计数
        # 对于其他类型，使用预定义的层级
        corrected_levels = []
        for i, (item, pattern_info) in enumerate(zip(toc_items, patterns)):
            # 如果有明确的编号模式，使用模式推断的层级
            if pattern_info['type'] != 'none':
                level = pattern_info['level']
            else:
                # 没有编号模式时，使用原有层级或默认1级
                level = item.get('level', 1)

            corrected_levels.append(level)

            # 调试日志
            if pattern_info['type'] != 'none':
                self.logger.debug(
                    f"  [{i+1}] '{item['title'][:30]}...' -> "
                    f"{pattern_info['type']}({pattern_info['pattern']}) = {level}级"
                )

        # 步骤5: 后处理 - 检查层级连续性
        corrected_levels = self._smooth_level_sequence(corrected_levels, toc_items)

        # 统计修正结果
        level_counts = {}
        for level in corrected_levels:
            level_counts[level] = level_counts.get(level, 0) + 1

        self.logger.info(f"层级分析完成: {level_counts}")

        return corrected_levels

    def _smooth_level_sequence(self, levels: List[int], toc_items: List[Dict]) -> List[int]:
        """
        平滑层级序列，修正异常跳跃

        规则：
        1. 层级不能跳跃（1->3 是不合理的，应该是 1->2）
        2. 如果出现跳跃，插入中间层级

        Args:
            levels: 原始层级列表
            toc_items: 目录项（用于日志）

        Returns:
            平滑后的层级列表
        """
        if not levels:
            return levels

        smoothed = [levels[0]]  # 第一项保持不变

        for i in range(1, len(levels)):
            current = levels[i]
            previous = smoothed[-1]

            # 检查跳跃
            if current > previous + 1:
                # 出现跳跃，限制为 previous + 1
                corrected = previous + 1
                self.logger.debug(
                    f"修正层级跳跃: '{toc_items[i]['title'][:30]}...' "
                    f"({current}级 -> {corrected}级)"
                )
                smoothed.append(corrected)
            else:
                smoothed.append(current)

        return smoothed

    def validate_outline_levels(self, chapters: List) -> Dict:
        """
        校验Word大纲级别的准确性

        对比：
        - Word的outlineLevel（存储在chapter.level）
        - 基于编号格式的推断级别

        Args:
            chapters: ChapterNode列表

        Returns:
            {
                "is_valid": True/False,
                "mismatch_count": 5,  # 不一致的数量
                "mismatch_rate": 0.3,  # 不一致率
                "total_chapters": 20,
                "warning": "Word大纲级别可能设置不正确，建议使用'精确识别'方法"
            }
        """
        if not chapters:
            return {
                "is_valid": True,
                "mismatch_count": 0,
                "mismatch_rate": 0.0,
                "total_chapters": 0,
                "warning": None
            }

        # 扁平化章节列表
        flat_chapters = []

        def flatten(chs):
            for ch in chs:
                flat_chapters.append(ch)
                if hasattr(ch, 'children') and ch.children:
                    flatten(ch.children)

        flatten(chapters)

        total = len(flat_chapters)
        if total == 0:
            return {
                "is_valid": True,
                "mismatch_count": 0,
                "mismatch_rate": 0.0,
                "total_chapters": 0,
                "warning": None
            }

        # 比对Word大纲级别和推断级别
        mismatch_count = 0
        for ch in flat_chapters:
            outline_level = ch.level  # Word的大纲级别
            pattern_info = self.extract_numbering_pattern(ch.title)
            inferred_level = pattern_info['level']

            if outline_level != inferred_level:
                mismatch_count += 1
                self.logger.debug(
                    f"层级不一致: '{ch.title}' "
                    f"(Word大纲={outline_level}级, 编号推断={inferred_level}级)"
                )

        mismatch_rate = mismatch_count / total

        # 判断是否有效
        is_valid = mismatch_rate < 0.3  # 不一致率低于30%认为有效

        warning = None
        if not is_valid:
            warning = (
                f"Word大纲级别与编号格式不一致率为{mismatch_rate:.1%}，"
                f"可能是作者设置不正确。建议使用'精确识别'方法以获得更准确的层级。"
            )

        self.logger.info(
            f"Word大纲级别校验: {total}个章节, "
            f"{mismatch_count}个不一致 ({mismatch_rate:.1%})"
        )

        return {
            "is_valid": is_valid,
            "mismatch_count": mismatch_count,
            "mismatch_rate": mismatch_rate,
            "total_chapters": total,
            "warning": warning
        }

    def _extract_prefix(self, title: str) -> Optional[str]:
        """
        提取标题的序号前缀

        Args:
            title: 标题文本

        Returns:
            序号前缀字符串，如 "第一章"、"一、"、"1."，无法识别返回None
        """
        title = title.strip()

        patterns = [
            r'^第[一二三四五六七八九十百千\d]+(章|部分|篇|节|条|册)',  # 第一章、第二部分、第三节、第一册
            r'^附[件表录图]\d+\.?',                        # 附表1.、附件2
            r'^[一二三四五六七八九十]+[、\s]',              # 一、二、
            r'^\([一二三四五六七八九十]+\)',                # (一)(二)
            r'^\d+\.\d+\.?\d*',                           # 1.1、1.1.1
            r'^\d+[\.、\s]',                              # 1.、2、
        ]

        for pattern in patterns:
            match = re.match(pattern, title)
            if match:
                return match.group(0).strip()

        return None

    def _normalize_prefix(self, prefix: str) -> str:
        """
        将具体序号归一化为模式类型

        Args:
            prefix: 具体的序号前缀，如 "第一章"、"一、"、"1."

        Returns:
            归一化的模式类型，如 "第X章"、"X、"、"N."
        """
        if not prefix:
            return ""

        # 章节格式
        if re.match(r'^第[一二三四五六七八九十百千\d]+章', prefix):
            return "第X章"
        if re.match(r'^第[一二三四五六七八九十百千\d]+部分', prefix):
            return "第X部分"
        if re.match(r'^第[一二三四五六七八九十百千\d]+册', prefix):
            return "第X册"
        if re.match(r'^第[一二三四五六七八九十百千\d]+节', prefix):
            return "第X节"
        if re.match(r'^第[一二三四五六七八九十百千\d]+条', prefix):
            return "第X条"

        # 附件格式
        if re.match(r'^附件\d+', prefix):
            return "附件N"
        if re.match(r'^附表\d+', prefix):
            return "附表N"
        if re.match(r'^附录\d+', prefix):
            return "附录N"
        if re.match(r'^附图\d+', prefix):
            return "附图N"

        # 中文序号
        if re.match(r'^[一二三四五六七八九十]+[、\s]', prefix):
            return "X、"
        if re.match(r'^\([一二三四五六七八九十]+\)', prefix):
            return "(X)"
        if re.match(r'^[（(][一二三四五六七八九十]+[）)]', prefix):
            return "（X）"

        # 数字编号 - 精确匹配层级
        if re.match(r'^\d+\.\d+\.\d+', prefix):
            return "N.N.N"  # 三级：1.1.1
        if re.match(r'^\d+\.\d+', prefix):
            return "N.N"    # 二级：1.1
        if re.match(r'^\d+[\.、\s]', prefix):
            return "N."     # 一级：1.

        # 其他格式保持原样
        return prefix

    def _analyze_prefix_frequency(self, toc_items: List[Dict]) -> Dict:
        """
        统计序号模式频率（使用归一化后的模式）

        Args:
            toc_items: 目录项列表

        Returns:
            {
                'prefixes': [...],               # 每个条目的原始序号前缀
                'normalized_prefixes': [...],    # 每个条目的归一化前缀
                'counts': Counter(...),          # 归一化模式出现次数统计
                'unique': {...},                 # 唯一模式集合（出现1次）
                'rare': {...},                   # 低频模式集合（2-5次）
                'common': {...}                  # 高频模式集合（>5次）
            }
        """
        from collections import Counter

        prefixes = []
        normalized_prefixes = []

        for item in toc_items:
            prefix = self._extract_prefix(item['title'])
            prefixes.append(prefix)

            # 归一化前缀（用于频率统计）
            normalized = self._normalize_prefix(prefix) if prefix else None
            normalized_prefixes.append(normalized)

        # ⭐️ 使用归一化后的前缀统计频率
        prefix_counts = Counter([p for p in normalized_prefixes if p])

        # 按频率分类
        unique = {p for p, cnt in prefix_counts.items() if cnt == 1}
        rare = {p for p, cnt in prefix_counts.items() if 2 <= cnt <= 5}
        common = {p for p, cnt in prefix_counts.items() if cnt > 5}

        self.logger.debug(f"序号频率统计（归一化后）: 唯一={len(unique)}, 低频={len(rare)}, 高频={len(common)}")
        self.logger.debug(f"  唯一模式: {unique}")
        self.logger.debug(f"  高频模式: {common}")

        return {
            'prefixes': prefixes,                   # 原始前缀
            'normalized_prefixes': normalized_prefixes,  # 归一化前缀
            'counts': prefix_counts,                # 归一化后的频率
            'unique': unique,
            'rare': rare,
            'common': common
        }

    def _is_stronger_prefix(self, prefix1: str, prefix2: str) -> bool:
        """
        判断prefix1是否比prefix2更"强"（层级更高）

        强度排序（从强到弱）：
        1. 第X章 > 第X部分 > 第X节
        2. 附表/附件
        3. 一、二、三、
        4. 1.1、1.1.1（多级数字）
        5. 1.、2.（单级数字）

        Args:
            prefix1: 序号前缀1
            prefix2: 序号前缀2

        Returns:
            True表示prefix1层级更高
        """
        strength_order = [
            r'^第[一二三四五六七八九十百千\d]+章',      # 最强：章
            r'^第[一二三四五六七八九十百千\d]+部分',    # 次强：部分
            r'^第[一二三四五六七八九十百千\d]+节',      # 较强：节
            r'^附[件表录图]\d+',                       # 中等：附表
            r'^[一二三四五六七八九十]+、',              # 较弱：中文序号
            r'^\([一二三四五六七八九十]+\)',            # 更弱：括号序号
            r'^\d+\.\d+',                              # 很弱：多级数字
            r'^\d+[\.、]',                             # 最弱：单级数字
        ]

        def get_strength(prefix):
            if not prefix:
                return len(strength_order)
            for i, pattern in enumerate(strength_order):
                if re.match(pattern, prefix):
                    return i
            return len(strength_order)

        return get_strength(prefix1) < get_strength(prefix2)

    def analyze_toc_hierarchy_contextual(self, toc_items: List[Dict]) -> List[int]:
        """
        基于统计频率的上下文层级分析（改进版：使用归一化前缀）

        核心思想：
        1. 统计每个序号模式（归一化后）的出现频率
        2. 唯一模式（出现1次）可能是高层级
        3. 高频模式（出现多次）可能是低层级
        4. 结合序号出现的位置和前后关系推断层级

        Args:
            toc_items: 目录项列表，格式：[{'title': '...', 'page_num': 1, 'level': 1}, ...]

        Returns:
            每个目录项的层级列表，如 [1, 1, 2, 2, 3, 3, ...]
        """
        if not toc_items:
            return []

        self.logger.info(f"使用contextual方法分析 {len(toc_items)} 个目录项的层级")

        # 步骤1：统计分析（使用归一化前缀）
        freq_info = self._analyze_prefix_frequency(toc_items)
        prefixes = freq_info['prefixes']                    # 原始前缀
        normalized_prefixes = freq_info['normalized_prefixes']  # 归一化前缀
        unique = freq_info['unique']    # 归一化后的唯一模式
        common = freq_info['common']    # 归一化后的高频模式

        levels = []
        current_level = 1
        last_normalized = None
        pattern_level_map = {}  # 记录每个归一化模式对应的层级

        for i, (prefix, normalized) in enumerate(zip(prefixes, normalized_prefixes)):
            title = toc_items[i]['title']

            # --- 情况A：无序号前缀（新增逻辑）---
            if not normalized:
                # 保险：如果标题过长(>40字)，可能不是真正的章节标题
                if len(title) > 40:
                    level = current_level
                    self.logger.debug(f"无序号但过长(>{40}字): '{title[:20]}...' → L{level}")
                # 核心降级逻辑
                elif current_level == 1:
                    level = 2
                    self.logger.debug(f"无序号跟随L1: '{title}' → L2")
                elif current_level == 2:
                    level = 3
                    self.logger.debug(f"无序号跟随L2: '{title}' → L3")
                else:
                    level = current_level

                levels.append(level)
                current_level = level
                last_normalized = None
                continue

            # --- 情况B：有序号前缀 ---

            # 规则1：章节模式（第X章/第X部分/第X册）始终是1级或2级
            if normalized == "第X章" or normalized == "第X部分":
                level = 1
                pattern_level_map[normalized] = 1
            elif normalized == "第X册":
                level = 2  # "第X册"通常是二级(在"第X部分"之下)
                pattern_level_map[normalized] = 2

            # 规则2：已见过的归一化模式，使用记录的层级
            elif normalized in pattern_level_map:
                level = pattern_level_map[normalized]

            # 规则3：首次出现的归一化模式
            else:
                # 特殊规则：附件类无论频率都是2级
                if normalized in ["附表N", "附件N", "附录N", "附图N"]:
                    level = 2
                    self.logger.debug(f"附件类模式: '{normalized}' (原:{prefix}) → L2")

                # 3a. 唯一模式 + 在前10项内 → 优先判定为1级
                elif normalized in unique and i < 10:
                    level = 1
                    self.logger.debug(f"唯一模式在前10项: '{normalized}' (原:{prefix}) → L1")

                # 3b. 高频模式 → 判定为2级或3级
                elif normalized in common:
                    # 特殊规则：根据模式类型确定基础层级
                    if normalized == "X、":
                        level = 2  # "一、二、三、" 固定为2级
                    elif normalized == "N.":
                        # "1. 2. 3." 的层级取决于上下文
                        level = 3 if current_level >= 2 else 2
                    elif normalized == "N.N":
                        level = 2  # "1.1 1.2" 固定为2级
                    elif normalized == "N.N.N":
                        level = 3  # "1.1.1" 固定为3级
                    elif normalized in ["附表N", "附件N", "附录N", "附图N"]:
                        level = 2  # 附件类固定为2级
                    else:
                        # 其他高频模式：根据当前层级判断
                        if current_level == 1:
                            level = 2
                        else:
                            level = 3
                    self.logger.debug(f"高频模式: '{normalized}' (原:{prefix}) → L{level}")

                # 3c. 低频模式 → 根据位置和序号强度判断
                else:
                    # 序号变化 → 可能是平级或升降级
                    if last_normalized and last_normalized != normalized:
                        # 判断是否是"更强"的序号格式
                        if self._is_stronger_prefix(prefix, prefixes[i-1] if i > 0 else ""):
                            # 更强的序号 → 升级（回到更高层）
                            level = max(1, current_level - 1)
                            self.logger.debug(f"序号变强: '{normalized}' vs '{last_normalized}' → L{level}")
                        else:
                            # 更弱的序号 → 降级（进入更深层）
                            level = min(3, current_level + 1)
                            self.logger.debug(f"序号变弱: '{normalized}' vs '{last_normalized}' → L{level}")
                    else:
                        # 第一次出现或重复序号，保持当前层级
                        level = current_level

                pattern_level_map[normalized] = level

            levels.append(level)
            current_level = level
            last_normalized = normalized

        # 步骤2：平滑处理（避免1→3跳跃）
        levels = self._smooth_level_sequence(levels, toc_items)

        # 统计结果
        from collections import Counter
        level_counts = Counter(levels)
        self.logger.info(f"Contextual层级分析完成: {dict(level_counts)}")

        return levels


# 便捷函数
def analyze_levels(toc_items: List[Dict]) -> List[int]:
    """便捷函数：快速分析目录层级"""
    analyzer = LevelAnalyzer()
    return analyzer.analyze_toc_hierarchy(toc_items)


def detect_level(title: str, indent_pt: float = 0) -> int:
    """便捷函数：快速检测单个标题层级"""
    analyzer = LevelAnalyzer()
    return analyzer.detect_single_level(title, indent_pt)
