#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品匹配智能体 - ProductMatchAgent

技术方案生成流程的最前端智能体，核心职责：
1. 从招标文件中提取技术需求
2. 将需求与企业产品能力进行匹配
3. 明确标识：能做什么 / 不能做什么
4. 为后续智能体提供产品边界约束

设计原则：
- 只输出有证据支撑的能力匹配
- 对不确定的需求明确标记，避免AI编造
- 支持多企业隔离
"""

import json
import logging
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent
from ai_tender_system.modules.product_capability import CapabilitySearcher


class ProductMatchAgent(BaseAgent):
    """
    产品匹配智能体

    在技术方案生成流程最前端运行，确定产品能力边界。
    """

    def __init__(self, model_name: str = "gpt-4o-mini", db_path: str = None):
        """
        初始化产品匹配智能体

        Args:
            model_name: LLM 模型名称
            db_path: 数据库路径
        """
        super().__init__(model_name)
        self.prompt_module = 'product_match_agent'
        self.capability_searcher = CapabilitySearcher(db_path)

    def generate(self, tender_doc: str, company_id: int, **kwargs) -> Dict[str, Any]:
        """
        执行产品匹配分析

        Args:
            tender_doc: 招标文件内容
            company_id: 企业ID

        Returns:
            产品匹配结果
        """
        return self.analyze_and_match(tender_doc, company_id, **kwargs)

    def analyze_and_match(
        self,
        tender_doc: str,
        company_id: int,
        extract_requirements: bool = True,
        match_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        分析招标文件并匹配产品能力

        Args:
            tender_doc: 招标文件内容
            company_id: 企业ID
            extract_requirements: 是否使用AI提取需求（否则使用简单分句）
            match_threshold: 匹配阈值

        Returns:
            {
                "matched_products": ["风控产品", "位置服务"],
                "requirement_coverage": [...],
                "summary": {...},
                "risk_points": [...],
                "recommendations": [...]
            }
        """
        self.logger.info(f"【产品匹配智能体】开始分析，企业ID: {company_id}")

        # 第1步: 提取技术需求
        if extract_requirements:
            requirements = self._extract_requirements_with_llm(tender_doc)
        else:
            requirements = self._extract_requirements_simple(tender_doc)

        self.logger.info(f"提取到 {len(requirements)} 条技术需求")

        if not requirements:
            return self._empty_result("未能从招标文件中提取到技术需求")

        # 第2步: 逐条匹配能力
        coverage_results = []
        matched_tags = set()
        risk_points = []

        for req in requirements:
            match_result = self.capability_searcher.match_requirement(
                requirement=req['requirement'] if isinstance(req, dict) else req,
                company_id=company_id,
                threshold=match_threshold
            )

            # 记录匹配的产品标签
            if match_result.get('matched_capabilities'):
                for cap in match_result['matched_capabilities']:
                    if cap.get('tag_name'):
                        matched_tags.add(cap['tag_name'])

            # 整理结果
            coverage_item = {
                "requirement": req['requirement'] if isinstance(req, dict) else req,
                "category": req.get('category', '技术需求') if isinstance(req, dict) else '技术需求',
                "priority": req.get('priority', 'medium') if isinstance(req, dict) else 'medium',
                "status": match_result['status'],
                "match_score": match_result.get('match_score', 0),
                "capability": match_result.get('capability', ''),
                "capability_description": match_result.get('capability_description', ''),
                "evidence": match_result.get('evidence', ''),
                "doc_name": match_result.get('doc_name', ''),
                "doc_id": match_result.get('doc_id'),
                "note": match_result.get('note', '')
            }
            coverage_results.append(coverage_item)

            # 识别风险点
            if match_result['status'] == 'not_supported':
                req_text = req['requirement'] if isinstance(req, dict) else req
                risk_points.append({
                    "type": "capability_gap",
                    "description": f"需求「{req_text[:50]}...」无法满足",
                    "suggestion": "建议说明替代方案或明确不支持"
                })

        # 第3步: 汇总统计
        summary = self._generate_summary(coverage_results)

        # 第4步: 生成建议
        recommendations = self._generate_recommendations(
            coverage_results, risk_points
        )

        result = {
            "matched_products": list(matched_tags),
            "requirement_coverage": coverage_results,
            "summary": summary,
            "risk_points": risk_points,
            "recommendations": recommendations
        }

        self.logger.info(
            f"匹配完成: 支持 {summary['supported']}，"
            f"部分支持 {summary['partial']}，"
            f"不支持 {summary['not_supported']}"
        )

        return result

    def _extract_requirements_with_llm(self, tender_doc: str) -> List[Dict[str, Any]]:
        """
        使用LLM从招标文件中提取技术需求

        Returns:
            [
                {
                    "requirement": "需求描述",
                    "category": "分类",
                    "priority": "high/medium/low"
                },
                ...
            ]
        """
        # 截断过长文档
        truncated_doc = tender_doc[:20000]

        prompt = f"""请从以下招标文件中提取所有技术需求，包括功能需求、性能需求、安全需求、接口需求等。

【招标文件】
{truncated_doc}

【输出要求】
请以JSON格式返回，格式如下：
{{
    "requirements": [
        {{
            "requirement": "具体需求描述",
            "category": "需求分类（功能/性能/安全/接口/部署/其他）",
            "priority": "优先级（high/medium/low）"
        }}
    ]
}}

【提取原则】
1. 提取具体、可验证的技术需求
2. 保留需求的原文表述，不要过度概括
3. 识别关键技术指标（如响应时间、并发数、可用性等）
4. 对模糊的需求也要提取，标记为medium优先级
5. 每条需求独立，避免合并多个需求

请严格按照JSON格式返回。"""

        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        return result.get('requirements', [])

    def _extract_requirements_simple(self, tender_doc: str) -> List[str]:
        """
        简单分句提取需求（降级方案）
        """
        import re

        # 需求关键词
        keywords = [
            '应具备', '应支持', '需要', '必须', '要求',
            '应能', '需实现', '应包含', '应提供'
        ]

        sentences = re.split(r'[。；\n]', tender_doc)
        requirements = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10 or len(sentence) > 500:
                continue

            for kw in keywords:
                if kw in sentence:
                    requirements.append(sentence)
                    break

        return requirements[:100]  # 限制数量

    def _generate_summary(self, coverage_results: List[Dict]) -> Dict[str, Any]:
        """
        生成匹配摘要统计
        """
        total = len(coverage_results)
        supported = sum(1 for r in coverage_results if r['status'] == 'supported')
        partial = sum(1 for r in coverage_results if r['status'] == 'partial')
        not_supported = sum(1 for r in coverage_results if r['status'] == 'not_supported')
        uncertain = sum(1 for r in coverage_results if r['status'] == 'uncertain')

        # 计算覆盖率（支持 + 部分支持*0.5）
        coverage_rate = (supported + partial * 0.5) / total if total > 0 else 0

        # 按分类统计
        by_category = {}
        for r in coverage_results:
            cat = r.get('category', '其他')
            if cat not in by_category:
                by_category[cat] = {'total': 0, 'supported': 0}
            by_category[cat]['total'] += 1
            if r['status'] in ('supported', 'partial'):
                by_category[cat]['supported'] += 1

        return {
            "total": total,
            "supported": supported,
            "partial": partial,
            "not_supported": not_supported,
            "uncertain": uncertain,
            "coverage_rate": round(coverage_rate, 2),
            "by_category": by_category
        }

    def _generate_recommendations(
        self,
        coverage_results: List[Dict],
        risk_points: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        基于匹配结果生成建议
        """
        recommendations = []

        # 1. 不支持的需求建议
        not_supported = [r for r in coverage_results if r['status'] == 'not_supported']
        if not_supported:
            recommendations.append({
                "type": "capability_gap",
                "priority": "high",
                "title": f"有 {len(not_supported)} 项需求当前产品无法满足",
                "action": "建议在方案中明确说明替代方案或合作伙伴支持"
            })

        # 2. 部分支持的需求建议
        partial = [r for r in coverage_results if r['status'] == 'partial']
        if partial:
            recommendations.append({
                "type": "partial_match",
                "priority": "medium",
                "title": f"有 {len(partial)} 项需求仅部分满足",
                "action": "建议突出已有能力，补充定制开发或扩展计划"
            })

        # 3. 高匹配需求建议
        high_match = [r for r in coverage_results
                      if r['status'] == 'supported' and r.get('match_score', 0) > 0.8]
        if high_match:
            recommendations.append({
                "type": "strength",
                "priority": "low",
                "title": f"有 {len(high_match)} 项需求与产品能力高度匹配",
                "action": "这些是得分亮点，建议在方案中重点展示"
            })

        return recommendations

    def _empty_result(self, message: str) -> Dict[str, Any]:
        """
        返回空结果
        """
        return {
            "matched_products": [],
            "requirement_coverage": [],
            "summary": {
                "total": 0,
                "supported": 0,
                "partial": 0,
                "not_supported": 0,
                "uncertain": 0,
                "coverage_rate": 0,
                "by_category": {}
            },
            "risk_points": [{
                "type": "extraction_failed",
                "description": message,
                "suggestion": "请检查招标文件内容是否完整"
            }],
            "recommendations": []
        }

    # =========================================================================
    # 批量处理和缓存
    # =========================================================================

    def match_requirements_batch(
        self,
        requirements: List[str],
        company_id: int,
        tender_project_id: int = None
    ) -> Dict[str, Any]:
        """
        批量匹配需求（直接调用CapabilitySearcher）

        用于已经提取好需求列表的场景
        """
        return self.capability_searcher.match_requirements_batch(
            requirements=requirements,
            company_id=company_id,
            tender_project_id=tender_project_id
        )

    def get_company_capability_summary(self, company_id: int) -> Dict[str, Any]:
        """
        获取企业能力概览

        用于在匹配前展示企业已有能力
        """
        return self.capability_searcher.get_capability_stats(company_id)
