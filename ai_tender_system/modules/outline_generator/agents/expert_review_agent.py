#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专家评审智能体 - ExpertReviewAgent

模拟评审专家对技术方案进行评审：
1. 评估各评分点的响应质量
2. 识别内容缺陷和改进建议
3. 预估得分并给出评审意见
4. 生成修改建议清单

设计原则：
- 评审标准与招标评分标准一致
- 提供具体、可操作的改进建议
- 区分关键问题和一般问题
"""

import json
import logging
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent


class ExpertReviewAgent(BaseAgent):
    """
    专家评审智能体

    在内容撰写之后运行，对生成的技术方案进行质量评审。
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化专家评审智能体

        Args:
            model_name: LLM 模型名称
        """
        super().__init__(model_name)
        self.prompt_module = 'expert_review_agent'

    def generate(
        self,
        proposal_content: Dict[str, Any],
        scoring_points: List[Dict],
        scoring_strategy: Dict[str, Any],
        tender_doc: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        评审技术方案

        Args:
            proposal_content: 技术方案内容（来自 ContentWriterAgent）
            scoring_points: 评分点列表（来自 ScoringPointAgent）
            scoring_strategy: 评分策略（来自 ScoringStrategyAgent）
            tender_doc: 招标文件内容（可选）

        Returns:
            评审结果
        """
        return self.review_proposal(
            proposal_content=proposal_content,
            scoring_points=scoring_points,
            scoring_strategy=scoring_strategy,
            tender_doc=tender_doc
        )

    def review_proposal(
        self,
        proposal_content: Dict[str, Any],
        scoring_points: List[Dict],
        scoring_strategy: Dict[str, Any],
        tender_doc: str = None
    ) -> Dict[str, Any]:
        """
        评审技术方案

        Args:
            proposal_content: 技术方案内容
            scoring_points: 评分点列表
            scoring_strategy: 评分策略
            tender_doc: 招标文件

        Returns:
            {
                "overall_score": 85,
                "dimension_scores": [...],
                "strengths": [...],
                "weaknesses": [...],
                "improvement_suggestions": [...],
                "critical_issues": [...],
                "pass_recommendation": True
            }
        """
        self.logger.info("【专家评审智能体】开始评审技术方案...")

        chapters = proposal_content.get('chapters', [])
        total_words = proposal_content.get('total_words', 0)

        # 第1步: 评估各评分维度
        dimension_scores = []
        for dimension in scoring_points:
            dim_score = self._evaluate_dimension(
                dimension=dimension,
                chapters=chapters,
                strategy=self._get_dimension_strategy(dimension, scoring_strategy)
            )
            dimension_scores.append(dim_score)

        # 第2步: 计算总分
        overall_score = self._calculate_overall_score(dimension_scores)

        # 第3步: 识别优势和不足
        strengths = self._identify_strengths(dimension_scores, chapters)
        weaknesses = self._identify_weaknesses(dimension_scores, chapters)

        # 第4步: 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(
            weaknesses=weaknesses,
            dimension_scores=dimension_scores,
            scoring_strategy=scoring_strategy
        )

        # 第5步: 识别关键问题
        critical_issues = self._identify_critical_issues(
            dimension_scores=dimension_scores,
            weaknesses=weaknesses
        )

        # 第6步: 给出评审建议
        pass_recommendation = overall_score >= 70 and len(critical_issues) == 0

        result = {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": improvement_suggestions,
            "critical_issues": critical_issues,
            "pass_recommendation": pass_recommendation,
            "review_summary": self._generate_review_summary(
                overall_score=overall_score,
                strengths=strengths,
                weaknesses=weaknesses,
                critical_issues=critical_issues
            ),
            "metadata": {
                "reviewed_chapters": len(chapters),
                "total_words": total_words,
                "dimension_count": len(dimension_scores)
            }
        }

        self.logger.info(
            f"【专家评审智能体】评审完成: "
            f"总分{overall_score}分, "
            f"{len(strengths)}个优势, "
            f"{len(weaknesses)}个不足, "
            f"{len(critical_issues)}个关键问题"
        )

        return result

    def _get_dimension_strategy(
        self,
        dimension: Dict,
        scoring_strategy: Dict
    ) -> Dict:
        """获取维度对应的策略"""
        dim_name = dimension.get('dimension', '')
        for strategy in scoring_strategy.get('dimension_strategies', []):
            if strategy.get('dimension') == dim_name:
                return strategy
        return {}

    def _evaluate_dimension(
        self,
        dimension: Dict,
        chapters: List[Dict],
        strategy: Dict
    ) -> Dict[str, Any]:
        """
        评估单个评分维度

        Args:
            dimension: 评分维度
            chapters: 章节内容
            strategy: 维度策略

        Returns:
            维度评分结果
        """
        dim_name = dimension.get('dimension', '')
        weight = dimension.get('weight', 0)
        criteria = dimension.get('criteria', [])

        # 查找相关章节
        relevant_chapters = self._find_relevant_chapters(dim_name, chapters)

        # 评估各评分项
        criteria_scores = []
        for criterion in criteria:
            item_score = self._evaluate_criterion(
                criterion=criterion,
                chapters=relevant_chapters
            )
            criteria_scores.append(item_score)

        # 计算维度得分
        if criteria_scores:
            avg_score_rate = sum(c.get('score_rate', 0) for c in criteria_scores) / len(criteria_scores)
        else:
            avg_score_rate = 0.7  # 默认

        estimated_score = weight * avg_score_rate

        # 确定评审等级
        if avg_score_rate >= 0.9:
            grade = "优秀"
        elif avg_score_rate >= 0.75:
            grade = "良好"
        elif avg_score_rate >= 0.6:
            grade = "合格"
        else:
            grade = "需改进"

        return {
            "dimension": dim_name,
            "weight": weight,
            "estimated_score": round(estimated_score, 1),
            "score_rate": round(avg_score_rate, 2),
            "grade": grade,
            "criteria_scores": criteria_scores,
            "relevant_chapter_count": len(relevant_chapters),
            "comments": self._generate_dimension_comments(
                dim_name, avg_score_rate, relevant_chapters
            )
        }

    def _find_relevant_chapters(
        self,
        dimension_name: str,
        chapters: List[Dict]
    ) -> List[Dict]:
        """查找与维度相关的章节"""
        relevant = []

        dim_keywords = self._extract_dimension_keywords(dimension_name)

        for chapter in chapters:
            title = chapter.get('title', '')
            scoring_points = chapter.get('scoring_points', [])

            # 检查标题或评分点是否相关
            is_relevant = any(kw in title for kw in dim_keywords)
            is_relevant = is_relevant or any(
                kw in point for kw in dim_keywords for point in scoring_points
            )

            if is_relevant:
                relevant.append(chapter)

            # 递归检查子章节
            for child in chapter.get('children', []):
                child_relevant = self._find_relevant_chapters(dimension_name, [child])
                relevant.extend(child_relevant)

        return relevant

    def _extract_dimension_keywords(self, dimension_name: str) -> List[str]:
        """提取维度关键词"""
        # 常见维度关键词映射
        keyword_map = {
            '技术方案': ['技术', '方案', '设计', '架构', '功能'],
            '实施方案': ['实施', '部署', '交付', '进度', '计划'],
            '售后服务': ['售后', '运维', '维保', '培训', '支持'],
            '项目管理': ['项目', '管理', '团队', '进度', '质量'],
            '企业资质': ['企业', '资质', '案例', '经验', '实力'],
            '安全方案': ['安全', '保障', '防护', '备份', '恢复'],
        }

        # 尝试精确匹配
        for key, keywords in keyword_map.items():
            if key in dimension_name:
                return keywords

        # 提取维度名称中的关键词
        return [dimension_name.replace('方案', '').replace('设计', '')]

    def _evaluate_criterion(
        self,
        criterion: Dict,
        chapters: List[Dict]
    ) -> Dict[str, Any]:
        """
        评估单个评分项

        Args:
            criterion: 评分项
            chapters: 相关章节

        Returns:
            评分项评估结果
        """
        item_name = criterion.get('item', '')
        max_score = criterion.get('score', 0)
        requirement = criterion.get('requirement', '')

        # 检查内容覆盖情况
        coverage = self._check_content_coverage(item_name, requirement, chapters)

        # 评估得分率
        if coverage['fully_covered']:
            score_rate = 0.9
        elif coverage['partially_covered']:
            score_rate = 0.7
        else:
            score_rate = 0.4

        return {
            "item": item_name,
            "max_score": max_score,
            "estimated_score": round(max_score * score_rate, 1),
            "score_rate": score_rate,
            "coverage": coverage,
            "feedback": self._generate_criterion_feedback(item_name, coverage)
        }

    def _check_content_coverage(
        self,
        item_name: str,
        requirement: str,
        chapters: List[Dict]
    ) -> Dict[str, Any]:
        """检查内容覆盖情况"""
        item_keywords = item_name.split()

        # 检查是否有章节内容涉及该评分项
        found_in_chapters = []
        for chapter in chapters:
            content = chapter.get('content', '')
            title = chapter.get('title', '')

            # 检查关键词
            matches = sum(1 for kw in item_keywords if kw in content or kw in title)

            if matches > 0:
                found_in_chapters.append({
                    'title': title,
                    'match_count': matches,
                    'content_length': len(content)
                })

        if found_in_chapters:
            # 有覆盖
            best_match = max(found_in_chapters, key=lambda x: x['match_count'])
            if best_match['content_length'] > 500 and best_match['match_count'] >= 2:
                return {
                    "fully_covered": True,
                    "partially_covered": False,
                    "found_in": [c['title'] for c in found_in_chapters],
                    "detail": f"在{len(found_in_chapters)}个章节中找到相关内容"
                }
            else:
                return {
                    "fully_covered": False,
                    "partially_covered": True,
                    "found_in": [c['title'] for c in found_in_chapters],
                    "detail": "内容覆盖不够充分"
                }
        else:
            return {
                "fully_covered": False,
                "partially_covered": False,
                "found_in": [],
                "detail": "未找到相关内容"
            }

    def _generate_criterion_feedback(
        self,
        item_name: str,
        coverage: Dict
    ) -> str:
        """生成评分项反馈"""
        if coverage['fully_covered']:
            return f"'{item_name}'响应充分，内容完整"
        elif coverage['partially_covered']:
            return f"'{item_name}'有涉及但不够深入，建议补充具体细节"
        else:
            return f"'{item_name}'缺少响应，建议补充相关内容"

    def _calculate_overall_score(self, dimension_scores: List[Dict]) -> float:
        """计算总分"""
        total_estimated = sum(d.get('estimated_score', 0) for d in dimension_scores)
        total_weight = sum(d.get('weight', 0) for d in dimension_scores)

        if total_weight > 0:
            # 按百分制转换
            return round(total_estimated / total_weight * 100, 1)
        return 0

    def _identify_strengths(
        self,
        dimension_scores: List[Dict],
        chapters: List[Dict]
    ) -> List[Dict[str, str]]:
        """识别优势"""
        strengths = []

        # 高分维度
        for dim in dimension_scores:
            if dim.get('grade') in ['优秀', '良好'] and dim.get('weight', 0) >= 15:
                strengths.append({
                    "type": "dimension",
                    "title": f"{dim['dimension']} - 表现出色",
                    "description": f"该维度预估得分率{dim['score_rate']:.0%}，评级为{dim['grade']}",
                    "impact": "high" if dim['grade'] == '优秀' else "medium"
                })

        # 内容充实的章节
        for chapter in chapters:
            if chapter.get('actual_words', 0) > 3000:
                strengths.append({
                    "type": "content",
                    "title": f"{chapter.get('title', '')} - 内容详实",
                    "description": f"该章节内容丰富，共{chapter.get('actual_words', 0)}字",
                    "impact": "medium"
                })

        return strengths[:8]  # 最多8个

    def _identify_weaknesses(
        self,
        dimension_scores: List[Dict],
        chapters: List[Dict]
    ) -> List[Dict[str, str]]:
        """识别不足"""
        weaknesses = []

        # 低分维度
        for dim in dimension_scores:
            if dim.get('grade') == '需改进':
                weaknesses.append({
                    "type": "dimension",
                    "title": f"{dim['dimension']} - 需要改进",
                    "description": f"该维度预估得分率仅{dim['score_rate']:.0%}，存在明显不足",
                    "impact": "high" if dim.get('weight', 0) >= 15 else "medium",
                    "dimension": dim['dimension']
                })

        # 内容不足的章节
        for chapter in chapters:
            target = chapter.get('target_words', 2000)
            actual = chapter.get('actual_words', 0)
            if actual < target * 0.5:
                weaknesses.append({
                    "type": "content",
                    "title": f"{chapter.get('title', '')} - 内容不足",
                    "description": f"该章节实际{actual}字，仅达到目标{target}字的{actual/target*100:.0f}%",
                    "impact": "medium"
                })

        # 低分评分项
        for dim in dimension_scores:
            for crit in dim.get('criteria_scores', []):
                if crit.get('score_rate', 1) < 0.5:
                    weaknesses.append({
                        "type": "criterion",
                        "title": f"{crit['item']} - 响应不足",
                        "description": crit.get('feedback', ''),
                        "impact": "medium" if crit.get('max_score', 0) >= 5 else "low"
                    })

        return weaknesses[:10]

    def _generate_improvement_suggestions(
        self,
        weaknesses: List[Dict],
        dimension_scores: List[Dict],
        scoring_strategy: Dict
    ) -> List[Dict[str, str]]:
        """生成改进建议"""
        suggestions = []

        # 针对维度不足的建议
        for weakness in weaknesses:
            if weakness.get('type') == 'dimension':
                dim_name = weakness.get('dimension', '')
                suggestions.append({
                    "priority": "high" if weakness.get('impact') == 'high' else "medium",
                    "target": dim_name,
                    "suggestion": f"建议增强'{dim_name}'相关内容的深度和专业性",
                    "action": "补充具体的技术方案、实施案例或产品参数"
                })

            elif weakness.get('type') == 'content':
                suggestions.append({
                    "priority": "medium",
                    "target": weakness.get('title', '').replace(' - 内容不足', ''),
                    "suggestion": "建议扩充该章节内容",
                    "action": "补充更多细节描述、表格或示意图"
                })

            elif weakness.get('type') == 'criterion':
                suggestions.append({
                    "priority": "medium",
                    "target": weakness.get('title', '').replace(' - 响应不足', ''),
                    "suggestion": "建议针对性补充响应内容",
                    "action": "查阅相关素材，增加具体响应内容"
                })

        return suggestions[:8]

    def _identify_critical_issues(
        self,
        dimension_scores: List[Dict],
        weaknesses: List[Dict]
    ) -> List[Dict[str, str]]:
        """识别关键问题（必须解决才能通过）"""
        critical = []

        # 高权重维度得分过低
        for dim in dimension_scores:
            if dim.get('weight', 0) >= 20 and dim.get('score_rate', 1) < 0.5:
                critical.append({
                    "type": "scoring_risk",
                    "title": f"高权重维度'{dim['dimension']}'得分不足",
                    "description": f"该维度权重{dim['weight']}分，但预估得分率仅{dim['score_rate']:.0%}",
                    "suggestion": "必须重点改进该维度的响应内容"
                })

        # 关键评分项完全缺失
        for dim in dimension_scores:
            for crit in dim.get('criteria_scores', []):
                if crit.get('max_score', 0) >= 10 and crit.get('score_rate', 1) < 0.3:
                    critical.append({
                        "type": "missing_content",
                        "title": f"重要评分项'{crit['item']}'缺少响应",
                        "description": f"该项最高{crit['max_score']}分，但几乎没有响应",
                        "suggestion": "必须补充该评分项的响应内容"
                    })

        return critical[:5]

    def _generate_dimension_comments(
        self,
        dim_name: str,
        score_rate: float,
        relevant_chapters: List[Dict]
    ) -> str:
        """生成维度评审意见"""
        if score_rate >= 0.9:
            return f"'{dim_name}'维度响应出色，内容全面且专业"
        elif score_rate >= 0.75:
            return f"'{dim_name}'维度响应良好，个别细节可以进一步完善"
        elif score_rate >= 0.6:
            return f"'{dim_name}'维度基本合格，但深度不够，建议补充具体细节"
        else:
            chapter_count = len(relevant_chapters)
            if chapter_count == 0:
                return f"'{dim_name}'维度缺少相关章节，需要重点补充"
            else:
                return f"'{dim_name}'维度虽有{chapter_count}个相关章节，但内容不够充分"

    def _generate_review_summary(
        self,
        overall_score: float,
        strengths: List[Dict],
        weaknesses: List[Dict],
        critical_issues: List[Dict]
    ) -> str:
        """生成评审总结"""
        if overall_score >= 85 and not critical_issues:
            rating = "优秀"
            recommendation = "建议直接提交"
        elif overall_score >= 70 and not critical_issues:
            rating = "良好"
            recommendation = "建议进行小幅优化后提交"
        elif overall_score >= 60:
            rating = "合格"
            recommendation = "建议进行重点改进后再提交"
        else:
            rating = "需改进"
            recommendation = "建议进行全面修改后再评审"

        summary = f"""## 评审总结

**总体评分**: {overall_score}分 ({rating})

**优势方面**:
{chr(10).join(f"- {s['title']}" for s in strengths[:3]) if strengths else "- 暂无明显优势"}

**不足方面**:
{chr(10).join(f"- {w['title']}" for w in weaknesses[:3]) if weaknesses else "- 暂无明显不足"}

**关键问题**:
{chr(10).join(f"- {c['title']}" for c in critical_issues) if critical_issues else "- 无关键问题"}

**评审建议**: {recommendation}
"""

        return summary

    def quick_review(
        self,
        proposal_content: Dict[str, Any],
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        快速评审（只检查特定方面）

        Args:
            proposal_content: 技术方案内容
            focus_areas: 关注领域列表

        Returns:
            快速评审结果
        """
        chapters = proposal_content.get('chapters', [])
        focus_areas = focus_areas or ['字数', '章节完整性', '内容质量']

        issues = []
        suggestions = []

        # 字数检查
        if '字数' in focus_areas:
            total_words = proposal_content.get('total_words', 0)
            if total_words < 30000:
                issues.append("总字数不足（少于3万字）")
                suggestions.append("建议扩充各章节内容")

        # 章节完整性检查
        if '章节完整性' in focus_areas:
            for chapter in chapters:
                if not chapter.get('content'):
                    issues.append(f"章节'{chapter.get('title', '')}'内容为空")
                    suggestions.append(f"请补充'{chapter.get('title', '')}'的内容")

        # 内容质量检查
        if '内容质量' in focus_areas:
            for chapter in chapters:
                content = chapter.get('content', '')
                if len(content) < 500:
                    issues.append(f"章节'{chapter.get('title', '')}'内容过少")

        return {
            "issues": issues,
            "suggestions": suggestions,
            "pass": len(issues) == 0
        }
