#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分策略智能体 - ScoringStrategyAgent

基于产品能力匹配结果，制定评分策略：
1. 分析评分点结构和权重分布
2. 评估每个评分点的得分可能性
3. 识别得分亮点和风险点
4. 制定针对性的响应策略

设计原则：
- 策略基于实际产品能力，不做虚假承诺
- 对弱项评分点提供替代方案建议
- 优先保障高权重评分点
"""

import json
import logging
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent


class ScoringStrategyAgent(BaseAgent):
    """
    评分策略智能体

    在产品匹配之后运行，为技术方案内容生成提供策略指导。
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化评分策略智能体

        Args:
            model_name: LLM 模型名称
        """
        super().__init__(model_name)
        self.prompt_module = 'scoring_strategy_agent'

    def generate(
        self,
        scoring_points: List[Dict],
        product_match_result: Dict[str, Any],
        tender_doc: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成评分策略

        Args:
            scoring_points: 评分点列表（来自 ScoringPointAgent）
            product_match_result: 产品匹配结果（来自 ProductMatchAgent）
            tender_doc: 招标文件内容（可选，用于上下文）

        Returns:
            评分策略
        """
        return self.analyze_and_strategize(
            scoring_points=scoring_points,
            product_match_result=product_match_result,
            tender_doc=tender_doc
        )

    def analyze_and_strategize(
        self,
        scoring_points: List[Dict],
        product_match_result: Dict[str, Any],
        tender_doc: str = None
    ) -> Dict[str, Any]:
        """
        分析评分点并制定策略

        Args:
            scoring_points: 评分点列表
            product_match_result: 产品匹配结果
            tender_doc: 招标文件内容

        Returns:
            {
                "total_score": 100,
                "estimated_score": 82,
                "confidence": 0.75,
                "dimension_strategies": [...],
                "highlights": [...],
                "risks": [...],
                "recommendations": [...],
                "content_allocation": {...}
            }
        """
        self.logger.info("【评分策略智能体】开始分析评分策略...")

        # 获取产品能力覆盖情况
        coverage = product_match_result.get('requirement_coverage', [])
        summary = product_match_result.get('summary', {})

        # 第1步: 分析各维度得分可能性
        dimension_strategies = []
        total_weight = sum(d.get('weight', 0) for d in scoring_points)
        estimated_total = 0

        for dimension in scoring_points:
            strategy = self._analyze_dimension(
                dimension=dimension,
                coverage=coverage,
                total_weight=total_weight
            )
            dimension_strategies.append(strategy)
            estimated_total += strategy['estimated_score']

        # 第2步: 识别亮点和风险
        highlights = self._identify_highlights(dimension_strategies, coverage)
        risks = self._identify_risks(dimension_strategies, coverage)

        # 第3步: 生成内容分配建议
        content_allocation = self._allocate_content(
            dimension_strategies,
            target_pages=100  # 默认100页
        )

        # 第4步: 生成总体建议
        recommendations = self._generate_recommendations(
            dimension_strategies,
            risks,
            summary
        )

        # 计算信心度
        coverage_rate = summary.get('coverage_rate', 0)
        high_weight_coverage = self._calculate_high_weight_coverage(
            dimension_strategies
        )
        confidence = (coverage_rate * 0.6 + high_weight_coverage * 0.4)

        result = {
            "total_score": total_weight,
            "estimated_score": round(estimated_total, 1),
            "confidence": round(confidence, 2),
            "dimension_strategies": dimension_strategies,
            "highlights": highlights,
            "risks": risks,
            "recommendations": recommendations,
            "content_allocation": content_allocation
        }

        self.logger.info(
            f"评分策略分析完成: 预估得分 {result['estimated_score']}/{total_weight}, "
            f"信心度 {result['confidence']}"
        )

        return result

    def _analyze_dimension(
        self,
        dimension: Dict,
        coverage: List[Dict],
        total_weight: float
    ) -> Dict[str, Any]:
        """
        分析单个评分维度的策略

        Args:
            dimension: 评分维度
            coverage: 需求覆盖情况
            total_weight: 总权重

        Returns:
            维度策略
        """
        dim_name = dimension.get('dimension', '')
        weight = dimension.get('weight', 0)
        criteria = dimension.get('criteria', [])

        # 分析该维度下的评分细项
        criteria_analysis = []
        supported_count = 0
        partial_count = 0
        total_criteria = len(criteria)

        for criterion in criteria:
            item_name = criterion.get('item', '')
            item_score = criterion.get('score', 0)
            requirement = criterion.get('requirement', '')

            # 检查该评分项是否有匹配的能力
            match_status = self._find_capability_match(
                item_name, requirement, coverage
            )

            criteria_analysis.append({
                "item": item_name,
                "score": item_score,
                "match_status": match_status['status'],
                "match_confidence": match_status['confidence'],
                "capability": match_status.get('capability', ''),
                "strategy": self._get_item_strategy(match_status)
            })

            if match_status['status'] == 'supported':
                supported_count += 1
            elif match_status['status'] == 'partial':
                partial_count += 1

        # 计算维度得分预估
        if total_criteria > 0:
            support_rate = (supported_count + partial_count * 0.5) / total_criteria
        else:
            support_rate = 0.7  # 默认

        estimated_score = weight * support_rate * 0.9  # 保守估计

        # 确定响应策略
        if support_rate >= 0.8:
            strategy = "full_response"
            strategy_desc = "全面响应，突出优势"
        elif support_rate >= 0.5:
            strategy = "selective_response"
            strategy_desc = "选择性响应，强化已有能力"
        else:
            strategy = "alternative_response"
            strategy_desc = "提供替代方案，说明改进计划"

        return {
            "dimension": dim_name,
            "weight": weight,
            "weight_ratio": round(weight / total_weight * 100, 1) if total_weight > 0 else 0,
            "estimated_score": round(estimated_score, 1),
            "support_rate": round(support_rate, 2),
            "strategy": strategy,
            "strategy_description": strategy_desc,
            "criteria_count": total_criteria,
            "supported_count": supported_count,
            "partial_count": partial_count,
            "criteria_analysis": criteria_analysis,
            "priority": "high" if weight >= 20 else ("medium" if weight >= 10 else "low")
        }

    def _find_capability_match(
        self,
        item_name: str,
        requirement: str,
        coverage: List[Dict]
    ) -> Dict[str, Any]:
        """
        查找评分项对应的能力匹配

        Args:
            item_name: 评分项名称
            requirement: 评分要求
            coverage: 需求覆盖列表

        Returns:
            匹配结果
        """
        # 在覆盖列表中搜索相关匹配
        search_text = f"{item_name} {requirement}".lower()

        best_match = {
            "status": "uncertain",
            "confidence": 0.3
        }

        for cov in coverage:
            req_text = cov.get('requirement', '').lower()
            capability = cov.get('capability', '')
            status = cov.get('status', 'uncertain')
            score = cov.get('match_score', 0)

            # 简单的关键词匹配
            if any(kw in search_text for kw in req_text.split()[:3]):
                if score > best_match['confidence']:
                    best_match = {
                        "status": status,
                        "confidence": score,
                        "capability": capability,
                        "evidence": cov.get('evidence', '')
                    }

        return best_match

    def _get_item_strategy(self, match_status: Dict) -> str:
        """获取评分项响应策略"""
        status = match_status.get('status', 'uncertain')

        if status == 'supported':
            return "详细阐述产品能力，提供技术参数和案例"
        elif status == 'partial':
            return "说明现有能力，补充定制开发或扩展计划"
        elif status == 'not_supported':
            return "提供替代方案或合作伙伴支持说明"
        else:
            return "基于产品通用能力进行响应"

    def _identify_highlights(
        self,
        dimension_strategies: List[Dict],
        coverage: List[Dict]
    ) -> List[Dict[str, str]]:
        """识别得分亮点"""
        highlights = []

        # 高权重且高支持率的维度
        for dim in dimension_strategies:
            if dim['priority'] == 'high' and dim['support_rate'] >= 0.8:
                highlights.append({
                    "type": "strong_dimension",
                    "title": f"{dim['dimension']} - 核心优势",
                    "description": f"该维度权重{dim['weight']}分，产品能力覆盖率{dim['support_rate']:.0%}，建议重点展示",
                    "impact": "high"
                })

        # 完全支持的高分评分项
        for dim in dimension_strategies:
            for crit in dim.get('criteria_analysis', []):
                if crit['match_status'] == 'supported' and crit['score'] >= 5:
                    highlights.append({
                        "type": "strong_item",
                        "title": crit['item'],
                        "description": f"产品完全支持，可得{crit['score']}分",
                        "impact": "medium"
                    })

        return highlights[:10]  # 最多返回10个亮点

    def _identify_risks(
        self,
        dimension_strategies: List[Dict],
        coverage: List[Dict]
    ) -> List[Dict[str, str]]:
        """识别得分风险"""
        risks = []

        # 高权重但低支持率的维度
        for dim in dimension_strategies:
            if dim['priority'] == 'high' and dim['support_rate'] < 0.5:
                risks.append({
                    "type": "weak_dimension",
                    "title": f"{dim['dimension']} - 能力不足",
                    "description": f"该维度权重{dim['weight']}分，但产品能力覆盖率仅{dim['support_rate']:.0%}",
                    "impact": "high",
                    "mitigation": "建议准备替代方案或合作伙伴支持"
                })

        # 不支持的高分评分项
        for dim in dimension_strategies:
            for crit in dim.get('criteria_analysis', []):
                if crit['match_status'] == 'not_supported' and crit['score'] >= 5:
                    risks.append({
                        "type": "unsupported_item",
                        "title": crit['item'],
                        "description": f"产品不支持该功能，可能损失{crit['score']}分",
                        "impact": "medium",
                        "mitigation": crit.get('strategy', '')
                    })

        return risks[:10]

    def _allocate_content(
        self,
        dimension_strategies: List[Dict],
        target_pages: int
    ) -> Dict[str, Any]:
        """
        分配内容篇幅

        Args:
            dimension_strategies: 维度策略列表
            target_pages: 目标页数

        Returns:
            内容分配建议
        """
        allocations = []
        total_weight = sum(d['weight'] for d in dimension_strategies)

        for dim in dimension_strategies:
            # 基础分配：按权重比例
            base_ratio = dim['weight'] / total_weight if total_weight > 0 else 0

            # 调整系数：高优先级和高支持率的多分配
            if dim['priority'] == 'high':
                adjust = 1.2
            elif dim['support_rate'] >= 0.8:
                adjust = 1.1
            elif dim['support_rate'] < 0.5:
                adjust = 0.8  # 低支持率的适当减少
            else:
                adjust = 1.0

            adjusted_ratio = base_ratio * adjust
            pages = int(target_pages * adjusted_ratio)

            allocations.append({
                "dimension": dim['dimension'],
                "pages": max(2, pages),  # 至少2页
                "word_count": max(2, pages) * 700,
                "priority": dim['priority'],
                "content_focus": self._get_content_focus(dim)
            })

        # 归一化，确保总页数接近目标
        total_pages = sum(a['pages'] for a in allocations)
        if total_pages > 0:
            scale = target_pages / total_pages
            for alloc in allocations:
                alloc['pages'] = max(2, int(alloc['pages'] * scale))
                alloc['word_count'] = alloc['pages'] * 700

        return {
            "target_pages": target_pages,
            "allocations": allocations,
            "total_allocated": sum(a['pages'] for a in allocations)
        }

    def _get_content_focus(self, dim_strategy: Dict) -> List[str]:
        """获取内容重点"""
        focus = []

        if dim_strategy['support_rate'] >= 0.8:
            focus.append("详细展示产品功能和技术优势")
            focus.append("提供具体的技术参数和性能指标")
            focus.append("引用相关案例和客户评价")
        elif dim_strategy['support_rate'] >= 0.5:
            focus.append("突出已有能力的优势")
            focus.append("说明定制开发或扩展计划")
            focus.append("强调技术架构的可扩展性")
        else:
            focus.append("提供替代解决方案")
            focus.append("说明合作伙伴支持能力")
            focus.append("展示类似项目的成功经验")

        return focus

    def _generate_recommendations(
        self,
        dimension_strategies: List[Dict],
        risks: List[Dict],
        summary: Dict
    ) -> List[Dict[str, str]]:
        """生成总体建议"""
        recommendations = []

        coverage_rate = summary.get('coverage_rate', 0)

        # 整体策略建议
        if coverage_rate >= 0.8:
            recommendations.append({
                "type": "overall",
                "priority": "high",
                "title": "产品匹配度高，建议积极投标",
                "action": "重点展示产品优势，用详实的数据和案例支撑"
            })
        elif coverage_rate >= 0.6:
            recommendations.append({
                "type": "overall",
                "priority": "medium",
                "title": "产品匹配度中等，需要针对性准备",
                "action": "强化优势领域，为弱项准备替代方案"
            })
        else:
            recommendations.append({
                "type": "overall",
                "priority": "low",
                "title": "产品匹配度较低，建议谨慎评估",
                "action": "评估投标成本效益，考虑联合投标或放弃"
            })

        # 针对风险的建议
        high_risks = [r for r in risks if r.get('impact') == 'high']
        if high_risks:
            recommendations.append({
                "type": "risk_mitigation",
                "priority": "high",
                "title": f"存在{len(high_risks)}个高风险点需要重点应对",
                "action": "提前准备替代方案说明，必要时咨询技术团队"
            })

        # 内容准备建议
        high_priority_dims = [d for d in dimension_strategies if d['priority'] == 'high']
        recommendations.append({
            "type": "content",
            "priority": "high",
            "title": f"重点准备{len(high_priority_dims)}个高权重评分维度的内容",
            "action": "优先完成高权重章节，确保内容充实且有证据支撑"
        })

        return recommendations

    def _calculate_high_weight_coverage(
        self,
        dimension_strategies: List[Dict]
    ) -> float:
        """计算高权重评分点的覆盖率"""
        high_weight_dims = [d for d in dimension_strategies if d['priority'] == 'high']

        if not high_weight_dims:
            return 0.7

        total_support = sum(d['support_rate'] for d in high_weight_dims)
        return total_support / len(high_weight_dims)
