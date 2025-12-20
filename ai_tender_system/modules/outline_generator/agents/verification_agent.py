#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证智能体 - 确保生成内容覆盖所有需求点"""

from typing import Dict, List, Any
import re

from .base_agent import BaseAgent


class VerificationAgent(BaseAgent):
    """
    验证智能体

    核心功能:
    1. 验证内容覆盖率
    2. 识别遗漏的要点
    3. 生成补充建议
    4. 质量评分

    目标: 确保覆盖率≥90%
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__(model_name)
        self.prompt_module = 'verification_agent'

    def verify_coverage(self, generated_chapters: List[Dict],
                       expected_hints: List[str]) -> Dict:
        """
        验证覆盖率

        Args:
            generated_chapters: 生成的章节列表
                [
                    {"title": "...", "content": "...", "word_count": 1000},
                    ...
                ]
            expected_hints: 期望的要点列表
                ["要点1", "要点2", "要点3", ...]

        Returns:
            {
                "coverage_rate": 0.94,  # 94%
                "missing_hints": ["容灾方案", "性能优化"],
                "covered_hints": ["系统架构", "技术选型", ...],
                "recommendations": [...]
            }
        """
        self.logger.info(
            f"【验证智能体】开始验证，期望要点: {len(expected_hints)} 个"
        )

        # 1. 提取生成内容中的关键词
        generated_keywords = self._extract_keywords(generated_chapters)

        # 2. 计算覆盖率
        covered_hints = []
        missing_hints = []

        for hint in expected_hints:
            if self._is_covered(hint, generated_keywords, generated_chapters):
                covered_hints.append(hint)
            else:
                missing_hints.append(hint)

        coverage_rate = len(covered_hints) / len(expected_hints) if expected_hints else 1.0

        # 3. 生成补充建议
        recommendations = []
        if coverage_rate < 0.9:
            recommendations = self._generate_补充_suggestions(
                missing_hints,
                generated_chapters
            )

        result = {
            "coverage_rate": coverage_rate,
            "covered_hints": covered_hints,
            "missing_hints": missing_hints,
            "recommendations": recommendations,
            "total_hints": len(expected_hints),
            "covered_count": len(covered_hints),
            "missing_count": len(missing_hints)
        }

        self.logger.info(
            f"验证完成，覆盖率: {coverage_rate:.1%} "
            f"({len(covered_hints)}/{len(expected_hints)})"
        )

        return result

    def _extract_keywords(self, chapters: List[Dict]) -> List[str]:
        """
        从章节内容中提取关键词

        Args:
            chapters: 章节列表

        Returns:
            关键词列表
        """
        keywords = []

        for chapter in chapters:
            content = chapter.get('content', '')

            # 简单的分词（按空格、标点符号）
            words = re.findall(r'[\u4e00-\u9fa5]+', content)  # 提取中文词语
            keywords.extend(words)

        return keywords

    def _is_covered(self, hint: str, keywords: List[str],
                   chapters: List[Dict]) -> bool:
        """
        判断要点是否被覆盖

        算法:
        1. 直接匹配：要点完整出现在内容中
        2. 关键词匹配：要点的主要关键词出现在内容中
        3. 语义匹配：使用同义词判断

        Args:
            hint: 要点文本
            keywords: 内容关键词列表
            chapters: 章节列表

        Returns:
            是否被覆盖
        """
        # 方法1: 直接匹配
        for chapter in chapters:
            content = chapter.get('content', '')
            if hint in content:
                return True

        # 方法2: 关键词匹配
        hint_keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', hint)  # 提取中文词（2字以上）

        if not hint_keywords:
            return False

        # 至少50%的关键词出现
        matched_count = sum(
            1 for kw in hint_keywords
            if any(kw in content for content in [c.get('content', '') for c in chapters])
        )

        coverage_ratio = matched_count / len(hint_keywords)

        return coverage_ratio >= 0.5

    def _generate_补充_suggestions(self, missing_hints: List[str],
                                  chapters: List[Dict]) -> List[str]:
        """
        生成补充建议

        Args:
            missing_hints: 遗漏的要点
            chapters: 已生成的章节

        Returns:
            补充建议列表
        """
        if not missing_hints:
            return []

        suggestions = []

        # 按章节分组遗漏的要点
        for i, hint in enumerate(missing_hints[:5], 1):  # 最多5条建议
            # 简单策略：建议添加到第一章或最相关的章节
            suggestions.append(
                f"建议在相关章节补充内容，体现'{hint}'"
            )

        return suggestions

    def calculate_quality_score(self, chapters: List[Dict],
                               coverage_rate: float,
                               target_words: int) -> Dict:
        """
        计算质量评分

        评分维度:
        1. 覆盖率 (40%)
        2. 字数达标率 (30%)
        3. 章节平衡度 (30%)

        Args:
            chapters: 章节列表
            coverage_rate: 覆盖率
            target_words: 目标字数

        Returns:
            {
                "overall_score": 85.5,
                "dimension_scores": {...}
            }
        """
        # 1. 覆盖率得分
        coverage_score = coverage_rate * 100

        # 2. 字数达标率
        total_words = sum(c.get('word_count', 0) for c in chapters)
        word_rate = min(total_words / target_words, 1.2)  # 最多120%
        word_score = 100 if 0.9 <= word_rate <= 1.1 else max(0, 100 - abs(word_rate - 1.0) * 100)

        # 3. 章节平衡度
        if chapters:
            avg_words = total_words / len(chapters)
            variance = sum(
                abs(c.get('word_count', 0) - avg_words) / avg_words
                for c in chapters
            ) / len(chapters)
            balance_score = max(0, 100 - variance * 100)
        else:
            balance_score = 0

        # 综合得分
        overall_score = (
            coverage_score * 0.4 +
            word_score * 0.3 +
            balance_score * 0.3
        )

        return {
            "overall_score": round(overall_score, 1),
            "dimension_scores": {
                "coverage": round(coverage_score, 1),
                "word_compliance": round(word_score, 1),
                "chapter_balance": round(balance_score, 1)
            }
        }

    def generate(self, *args, **kwargs) -> Dict[str, Any]:
        """
        实现抽象方法

        Returns:
            验证结果
        """
        return self.verify_coverage(*args, **kwargs)
