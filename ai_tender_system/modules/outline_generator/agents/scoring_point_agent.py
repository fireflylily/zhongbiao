#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""评分点智能体 - 统一处理评分提取、评估、方案生成"""

from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent


class ScoringPointAgent(BaseAgent):
    """
    评分点智能体

    核心功能:
    1. extract_scoring_points - 从招标文档中提取评分点 (场景1: 新建项目)
    2. evaluate_tender_document - 根据评分标准评估标书 (场景2: AI评分)
    3. generate_proposal_by_scoring - 按评分点生成方案 (场景3: 技术方案生成)
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__(model_name)
        self.prompt_module = 'scoring_point_agent'

    # ========== 场景1: 评分提取 (替代 extractor.py) ==========

    def extract_scoring_points(self, tender_doc: str) -> List[Dict]:
        """
        从招标文档中提取评分点

        Args:
            tender_doc: 招标文档文本

        Returns:
            评分点列表
            [
                {
                    "dimension": "技术方案",
                    "weight": 40,
                    "description": "技术方案的完整性和创新性",
                    "criteria": [
                        {"item": "系统架构设计", "score": 10, "requirement": "..."},
                        {"item": "技术选型合理性", "score": 8, "requirement": "..."}
                    ]
                },
                ...
            ]
        """
        self.logger.info("【评分点智能体】开始提取评分点...")

        # 截断过长文档
        truncated_doc = tender_doc[:15000]

        # 加载提示词
        prompt = self._get_prompt(
            self.prompt_module,
            'extract_scoring_points',
            tender_doc=truncated_doc
        )

        # 调用 LLM
        response = self._call_llm(prompt, response_format="json_object")

        # 解析结果
        scoring_data = self._parse_json_response(response)
        scoring_points = scoring_data.get('scoring_dimensions', [])

        # 验证和标准化
        validated_points = self._validate_scoring_points(scoring_points)

        self.logger.info(f"提取到 {len(validated_points)} 个评分维度")
        return validated_points

    def _validate_scoring_points(self, scoring_points: List[Dict]) -> List[Dict]:
        """验证和标准化评分点"""
        validated = []
        total_weight = 0

        for point in scoring_points:
            if not isinstance(point, dict):
                continue

            # 确保必填字段
            if 'dimension' not in point or 'weight' not in point:
                self.logger.warning(f"评分点缺少必填字段，已跳过: {point}")
                continue

            # 标准化格式
            validated_point = {
                "dimension": point['dimension'],
                "weight": float(point['weight']),
                "description": point.get('description', ''),
                "criteria": point.get('criteria', [])
            }

            validated.append(validated_point)
            total_weight += validated_point['weight']

        # 检查权重总和
        if total_weight > 0 and abs(total_weight - 100) > 5:
            self.logger.warning(
                f"评分权重总和为 {total_weight}，与100分存在偏差"
            )

        return validated

    # ========== 场景2: AI评分 (为 Scoring.vue 提供API) ==========

    def evaluate_tender_document(self, tender_doc: str,
                                 scoring_points: List[Dict]) -> Dict:
        """
        根据评分标准评估标书质量

        Args:
            tender_doc: 标书文档
            scoring_points: 评分点列表

        Returns:
            {
                "overall_score": 85.5,
                "dimension_scores": [...],
                "risk_analysis": {...},
                "improvement_suggestions": [...]
            }
        """
        self.logger.info("【评分点智能体】开始评估标书...")

        results = {
            "dimension_scores": [],
            "overall_score": 0.0
        }

        # 1. 逐个维度评分
        for dimension in scoring_points:
            score_result = self._evaluate_dimension(tender_doc, dimension)
            results["dimension_scores"].append(score_result)

        # 2. 计算总分
        results["overall_score"] = sum(
            d["score"] for d in results["dimension_scores"]
        )

        # 3. 风险分析
        results["risk_analysis"] = self._analyze_risks(
            tender_doc,
            results["dimension_scores"]
        )

        # 4. 改进建议
        results["improvement_suggestions"] = self._generate_suggestions(
            results["dimension_scores"]
        )

        self.logger.info(f"评估完成，总分: {results['overall_score']:.1f}")
        return results

    def _evaluate_dimension(self, tender_doc: str, dimension: Dict) -> Dict:
        """评估单个维度"""
        prompt = self._get_prompt(
            self.prompt_module,
            'evaluate_dimension',
            tender_doc=tender_doc[:10000],
            dimension_name=dimension['dimension'],
            dimension_weight=dimension['weight'],
            criteria=self._format_criteria(dimension.get('criteria', []))
        )

        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        return {
            "dimension": dimension['dimension'],
            "score": result.get('score', 0),
            "max_score": dimension['weight'],
            "strengths": result.get('strengths', []),
            "weaknesses": result.get('weaknesses', []),
            "suggestions": result.get('suggestions', [])
        }

    def _format_criteria(self, criteria: List[Dict]) -> str:
        """格式化评分细项"""
        if not criteria:
            return "无具体评分细项"

        lines = []
        for i, item in enumerate(criteria, 1):
            lines.append(
                f"{i}. {item.get('item', '未知')}: "
                f"{item.get('score', 0)}分 - {item.get('requirement', '')}"
            )

        return '\n'.join(lines)

    def _analyze_risks(self, tender_doc: str,
                      dimension_scores: List[Dict]) -> Dict:
        """分析整体风险"""
        # 识别低分维度
        low_scores = [
            d for d in dimension_scores
            if d['score'] / d['max_score'] < 0.7
        ]

        if not low_scores:
            return {
                "risk_level": "低",
                "description": "各维度得分均衡，风险较低"
            }

        return {
            "risk_level": "中" if len(low_scores) <= 2 else "高",
            "weak_dimensions": [d['dimension'] for d in low_scores],
            "description": f"存在 {len(low_scores)} 个弱项维度，需要重点改进"
        }

    def _generate_suggestions(self, dimension_scores: List[Dict]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        for dimension in dimension_scores:
            if dimension['suggestions']:
                suggestions.extend(dimension['suggestions'])

        return suggestions[:10]  # 最多返回10条建议

    # ========== 场景3: 按评分点生成方案 (新功能) ==========

    def generate_proposal_by_scoring(self, tender_doc: str,
                                     scoring_points: List[Dict],
                                     page_count: int = 200,
                                     content_style: Dict = None) -> Dict:
        """
        根据评分点生成技术方案

        Args:
            tender_doc: 招标文档
            scoring_points: 评分点列表
            page_count: 目标页数
            content_style: 内容风格配置

        Returns:
            {
                "outline": {...},
                "chapters": [...],
                "metadata": {...}
            }
        """
        content_style = content_style or {
            'tables': '适量',
            'flowcharts': '流程图',
            'images': '少量'
        }

        self.logger.info(
            f"【评分点智能体】开始生成方案，目标页数: {page_count}"
        )

        # 第1步: 规划大纲
        outline = self._plan_outline_by_scoring(
            scoring_points,
            page_count,
            content_style
        )

        # 第2步: 生成章节内容
        chapters = []
        for chapter_plan in outline['chapters']:
            chapter_content = self._generate_chapter_for_scoring(
                tender_doc=tender_doc,
                chapter_plan=chapter_plan,
                content_style=content_style
            )
            chapters.append(chapter_content)

        # 第3步: 验证和补充
        verified_result = self._verify_and_supplement(
            chapters,
            scoring_points
        )

        return {
            "outline": outline,
            "chapters": verified_result['chapters'],
            "metadata": {
                "generation_mode": "按评分点生成",
                "total_pages": verified_result['estimated_pages'],
                "coverage_rate": verified_result['coverage_rate'],
                "word_count": sum(c['word_count'] for c in verified_result['chapters'])
            }
        }

    def _plan_outline_by_scoring(self, scoring_points: List[Dict],
                                 page_count: int,
                                 content_style: Dict) -> Dict:
        """根据评分点规划大纲"""
        # 按权重分配页数
        total_weight = sum(d['weight'] for d in scoring_points)

        chapters = []
        for i, dimension in enumerate(scoring_points):
            weight_ratio = dimension['weight'] / total_weight
            allocated_pages = int(page_count * weight_ratio)

            # 提取评分细项作为 content_hints
            content_hints = [
                item.get('item', '') for item in dimension.get('criteria', [])
            ]

            if not content_hints:
                content_hints = [dimension.get('description', '')]

            chapters.append({
                "chapter_number": i + 1,
                "title": dimension['dimension'],
                "description": dimension.get('description', ''),
                "allocated_pages": allocated_pages,
                "content_hints": content_hints,
                "priority": "high" if dimension['weight'] >= 20 else "normal",
                "target_score": dimension['weight']
            })

        self.logger.info(f"大纲规划完成，共 {len(chapters)} 章")

        return {
            "chapters": chapters,
            "total_pages": page_count
        }

    def _generate_chapter_for_scoring(self, tender_doc: str,
                                      chapter_plan: Dict,
                                      content_style: Dict) -> Dict:
        """为评分维度生成章节内容"""
        content_hints = chapter_plan.get('content_hints', [])
        allocated_pages = chapter_plan.get('allocated_pages', 10)

        # 计算目标字数
        target_words = self.calculate_word_count(
            allocated_pages,
            content_style
        )

        # 构建提示词
        hints_text = '\n'.join([f"  - {hint}" for hint in content_hints])
        target_score = chapter_plan.get('target_score', 0)

        prompt = f"""为技术方案章节"{chapter_plan['title']}"撰写 {target_words}字 专业应答内容。

【评分要求】
本章节评分权重: {target_score}分，是{chapter_plan.get('priority', 'normal')}优先级章节。

【核心要点】
{hints_text}

【招标背景】
{tender_doc[:5000]}

【撰写要求】
1. **针对评分**: 紧扣评分标准，确保每个评分细项都有明确应答
2. **完整性**: 必须涵盖所有核心要点
3. **专业性**: 使用行业术语，体现技术深度和创新性
4. **字数**: {target_words}字左右（±10%）
5. **结构**: 开头概述 + 分点阐述 + 总结优势

请直接输出方案内容，不需要输出章节标题。"""

        # 调用 LLM 生成
        response = self._call_llm(prompt)
        generated_content = response.strip()

        return {
            "title": chapter_plan['title'],
            "content": generated_content,
            "word_count": len(generated_content),
            "allocated_pages": allocated_pages,
            "target_score": target_score
        }

    def _verify_and_supplement(self, chapters: List[Dict],
                               scoring_points: List[Dict]) -> Dict:
        """验证并补充内容"""
        # 收集所有期望的要点
        expected_hints = []
        for dimension in scoring_points:
            for criterion in dimension.get('criteria', []):
                if criterion.get('item'):
                    expected_hints.append(criterion['item'])

        # 简化的覆盖率检查
        covered_count = 0
        for hint in expected_hints:
            for chapter in chapters:
                if hint in chapter['content']:
                    covered_count += 1
                    break

        coverage_rate = covered_count / len(expected_hints) if expected_hints else 1.0

        # 估算页数
        total_words = sum(c['word_count'] for c in chapters)
        estimated_pages = int(total_words / 700)

        self.logger.info(f"验证完成，覆盖率: {coverage_rate:.1%}")

        return {
            "chapters": chapters,
            "estimated_pages": estimated_pages,
            "coverage_rate": coverage_rate
        }

    # ========== 实现抽象方法 ==========

    def generate(self, *args, **kwargs) -> Dict[str, Any]:
        """
        通用生成方法 - 默认调用按评分点生成

        Returns:
            生成结果
        """
        return self.generate_proposal_by_scoring(*args, **kwargs)
