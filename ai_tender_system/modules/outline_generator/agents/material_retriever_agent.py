#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材检索智能体 - MaterialRetrieverAgent

基于评分策略，从素材库中检索相关内容：
1. 从标书素材库检索历史中标标书的优秀片段
2. 从产品文档库检索技术说明和参数
3. 从案例库检索相关项目案例
4. 组装成"素材包"供内容生成使用

设计原则：
- 优先检索中标标书的内容
- 按评分点关联度排序
- 提供素材来源追溯
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent


class MaterialRetrieverAgent(BaseAgent):
    """
    素材检索智能体

    在评分策略之后运行，为内容生成准备素材。
    """

    def __init__(self, model_name: str = "gpt-4o-mini", db_path: str = None):
        """
        初始化素材检索智能体

        Args:
            model_name: LLM 模型名称
            db_path: 数据库路径
        """
        super().__init__(model_name)
        self.prompt_module = 'material_retriever_agent'

        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent.parent / "data" / "knowledge_base.db")
        self.db_path = db_path

    def generate(
        self,
        scoring_strategy: Dict[str, Any],
        company_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        检索素材

        Args:
            scoring_strategy: 评分策略（来自 ScoringStrategyAgent）
            company_id: 企业ID

        Returns:
            素材包
        """
        return self.retrieve_materials(
            scoring_strategy=scoring_strategy,
            company_id=company_id,
            **kwargs
        )

    def retrieve_materials(
        self,
        scoring_strategy: Dict[str, Any],
        company_id: int,
        include_excerpts: bool = True,
        include_capabilities: bool = True,
        include_cases: bool = True,
        max_per_dimension: int = 5
    ) -> Dict[str, Any]:
        """
        根据评分策略检索素材

        Args:
            scoring_strategy: 评分策略
            company_id: 企业ID
            include_excerpts: 是否包含标书片段
            include_capabilities: 是否包含产品能力
            include_cases: 是否包含案例
            max_per_dimension: 每个维度最多检索的素材数

        Returns:
            {
                "dimension_materials": [...],
                "summary": {...},
                "recommendations": [...]
            }
        """
        self.logger.info(f"【素材检索智能体】开始检索，企业ID: {company_id}")

        dimension_strategies = scoring_strategy.get('dimension_strategies', [])
        dimension_materials = []

        total_excerpts = 0
        total_capabilities = 0
        total_cases = 0

        for dim_strategy in dimension_strategies:
            dim_name = dim_strategy.get('dimension', '')
            criteria = dim_strategy.get('criteria_analysis', [])

            # 提取搜索关键词
            search_terms = self._extract_search_terms(dim_name, criteria)

            materials = {
                "dimension": dim_name,
                "priority": dim_strategy.get('priority', 'medium'),
                "excerpts": [],
                "capabilities": [],
                "cases": []
            }

            # 1. 检索标书片段
            if include_excerpts:
                excerpts = self._retrieve_excerpts(
                    company_id, search_terms, max_per_dimension
                )
                materials['excerpts'] = excerpts
                total_excerpts += len(excerpts)

            # 2. 检索产品能力
            if include_capabilities:
                capabilities = self._retrieve_capabilities(
                    company_id, search_terms, max_per_dimension
                )
                materials['capabilities'] = capabilities
                total_capabilities += len(capabilities)

            # 3. 检索案例
            if include_cases:
                cases = self._retrieve_cases(
                    company_id, search_terms, max_per_dimension // 2
                )
                materials['cases'] = cases
                total_cases += len(cases)

            # 生成素材使用建议
            materials['usage_suggestions'] = self._generate_usage_suggestions(
                materials, dim_strategy
            )

            dimension_materials.append(materials)

        # 生成总体建议
        recommendations = self._generate_recommendations(
            dimension_materials, scoring_strategy
        )

        result = {
            "dimension_materials": dimension_materials,
            "summary": {
                "total_dimensions": len(dimension_materials),
                "total_excerpts": total_excerpts,
                "total_capabilities": total_capabilities,
                "total_cases": total_cases,
                "coverage": self._calculate_coverage(dimension_materials)
            },
            "recommendations": recommendations
        }

        self.logger.info(
            f"素材检索完成: {total_excerpts}个片段, "
            f"{total_capabilities}个能力, {total_cases}个案例"
        )

        return result

    def _extract_search_terms(
        self,
        dimension_name: str,
        criteria: List[Dict]
    ) -> List[str]:
        """提取搜索关键词"""
        terms = [dimension_name]

        for crit in criteria:
            item = crit.get('item', '')
            if item:
                terms.append(item)

        # 添加常见同义词
        term_synonyms = {
            '技术架构': ['系统架构', '架构设计', '技术选型'],
            '安全': ['安全保障', '信息安全', '数据安全'],
            '运维': ['运维保障', '运维服务', '监控告警'],
            '项目管理': ['项目组织', '进度管理', '质量管理'],
            '实施': ['实施方案', '部署方案', '上线计划']
        }

        expanded_terms = []
        for term in terms:
            expanded_terms.append(term)
            for key, synonyms in term_synonyms.items():
                if key in term:
                    expanded_terms.extend(synonyms)

        return list(set(expanded_terms))

    def _retrieve_excerpts(
        self,
        company_id: int,
        search_terms: List[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """从标书素材库检索片段"""
        try:
            from ai_tender_system.modules.tender_library import ExcerptManager
            manager = ExcerptManager(self.db_path)

            all_excerpts = []
            seen_ids = set()

            for term in search_terms[:5]:  # 限制搜索词数量
                excerpts = manager.search_by_keyword(
                    company_id=company_id,
                    keyword=term,
                    won_only=True,
                    limit=limit
                )

                for exc in excerpts:
                    if exc['excerpt_id'] not in seen_ids:
                        seen_ids.add(exc['excerpt_id'])
                        all_excerpts.append({
                            "excerpt_id": exc['excerpt_id'],
                            "title": exc.get('chapter_title', ''),
                            "content_preview": exc.get('content', '')[:200] + '...' if exc.get('content') else '',
                            "category": exc.get('category', ''),
                            "quality_score": exc.get('quality_score', 0),
                            "source_doc": exc.get('doc_name', ''),
                            "bid_result": exc.get('bid_result', ''),
                            "match_term": term
                        })

            # 按质量分排序
            all_excerpts.sort(key=lambda x: x['quality_score'], reverse=True)
            return all_excerpts[:limit]

        except Exception as e:
            self.logger.warning(f"检索标书片段失败: {e}")
            return []

    def _retrieve_capabilities(
        self,
        company_id: int,
        search_terms: List[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """从产品能力索引检索"""
        try:
            from ai_tender_system.modules.product_capability import CapabilitySearcher
            searcher = CapabilitySearcher(self.db_path)

            all_capabilities = []
            seen_ids = set()

            for term in search_terms[:5]:
                results = searcher.search(
                    query=term,
                    company_id=company_id,
                    method='hybrid',
                    top_k=limit,
                    min_score=0.4
                )

                for cap in results:
                    if cap['capability_id'] not in seen_ids:
                        seen_ids.add(cap['capability_id'])
                        all_capabilities.append({
                            "capability_id": cap['capability_id'],
                            "name": cap.get('capability_name', ''),
                            "description": cap.get('capability_description', ''),
                            "type": cap.get('capability_type', ''),
                            "evidence": cap.get('original_text', ''),
                            "doc_name": cap.get('doc_name', ''),
                            "match_score": cap.get('match_score', 0),
                            "match_term": term
                        })

            # 按匹配分排序
            all_capabilities.sort(key=lambda x: x['match_score'], reverse=True)
            return all_capabilities[:limit]

        except Exception as e:
            self.logger.warning(f"检索产品能力失败: {e}")
            return []

    def _retrieve_cases(
        self,
        company_id: int,
        search_terms: List[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """从案例库检索"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # 构建搜索条件
            conditions = []
            params = [company_id]

            for term in search_terms[:3]:
                conditions.append(
                    "(case_title LIKE ? OR customer_name LIKE ? OR industry LIKE ?)"
                )
                params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])

            sql = f"""
                SELECT case_id, case_title, customer_name, industry,
                       contract_amount, case_status, contract_type
                FROM case_studies
                WHERE company_id = ? AND ({' OR '.join(conditions)})
                ORDER BY created_at DESC
                LIMIT {limit}
            """

            cursor = conn.execute(sql, params)
            cases = []

            for row in cursor.fetchall():
                cases.append({
                    "case_id": row['case_id'],
                    "title": row['case_title'],
                    "customer": row['customer_name'],
                    "industry": row['industry'],
                    "amount": row['contract_amount'],
                    "status": row['case_status'],
                    "type": row['contract_type']
                })

            conn.close()
            return cases

        except Exception as e:
            self.logger.warning(f"检索案例失败: {e}")
            return []

    def _generate_usage_suggestions(
        self,
        materials: Dict,
        dim_strategy: Dict
    ) -> List[str]:
        """生成素材使用建议"""
        suggestions = []

        excerpts = materials.get('excerpts', [])
        capabilities = materials.get('capabilities', [])
        cases = materials.get('cases', [])

        if excerpts:
            high_quality = [e for e in excerpts if e.get('quality_score', 0) >= 80]
            if high_quality:
                suggestions.append(
                    f"有{len(high_quality)}个高质量历史片段可直接引用，注意调整为当前项目"
                )

        if capabilities:
            suggestions.append(
                f"检索到{len(capabilities)}个产品能力描述，可用于技术响应"
            )

        if cases:
            suggestions.append(
                f"有{len(cases)}个相关案例可引用作为项目经验"
            )

        strategy = dim_strategy.get('strategy', '')
        if strategy == 'alternative_response':
            suggestions.append(
                "该维度能力较弱，建议重点使用案例和通用能力描述"
            )

        if not excerpts and not capabilities:
            suggestions.append(
                "未找到直接相关素材，需要基于产品文档重新整理内容"
            )

        return suggestions

    def _generate_recommendations(
        self,
        dimension_materials: List[Dict],
        scoring_strategy: Dict
    ) -> List[Dict[str, str]]:
        """生成总体建议"""
        recommendations = []

        # 统计素材覆盖情况
        dims_with_excerpts = sum(
            1 for d in dimension_materials if d.get('excerpts')
        )
        dims_with_caps = sum(
            1 for d in dimension_materials if d.get('capabilities')
        )
        total_dims = len(dimension_materials)

        if dims_with_excerpts < total_dims * 0.5:
            recommendations.append({
                "type": "material_gap",
                "priority": "high",
                "title": "标书素材覆盖不足",
                "action": "建议上传更多历史中标标书以丰富素材库"
            })

        if dims_with_caps < total_dims * 0.7:
            recommendations.append({
                "type": "capability_gap",
                "priority": "medium",
                "title": "产品能力索引覆盖不足",
                "action": "建议上传更多产品文档并触发能力提取"
            })

        # 高优先级维度的素材检查
        high_priority = [
            d for d in dimension_materials
            if d.get('priority') == 'high'
        ]

        for dim in high_priority:
            if not dim.get('excerpts') and not dim.get('capabilities'):
                recommendations.append({
                    "type": "priority_gap",
                    "priority": "high",
                    "title": f"高权重维度「{dim['dimension']}」素材不足",
                    "action": "需要手动准备该章节内容"
                })

        return recommendations

    def _calculate_coverage(
        self,
        dimension_materials: List[Dict]
    ) -> Dict[str, float]:
        """计算素材覆盖率"""
        total = len(dimension_materials)
        if total == 0:
            return {"overall": 0, "excerpts": 0, "capabilities": 0, "cases": 0}

        has_excerpts = sum(1 for d in dimension_materials if d.get('excerpts'))
        has_caps = sum(1 for d in dimension_materials if d.get('capabilities'))
        has_cases = sum(1 for d in dimension_materials if d.get('cases'))
        has_any = sum(
            1 for d in dimension_materials
            if d.get('excerpts') or d.get('capabilities') or d.get('cases')
        )

        return {
            "overall": round(has_any / total, 2),
            "excerpts": round(has_excerpts / total, 2),
            "capabilities": round(has_caps / total, 2),
            "cases": round(has_cases / total, 2)
        }

    def get_material_for_chapter(
        self,
        chapter_title: str,
        company_id: int,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        为特定章节检索素材（简化接口）

        Args:
            chapter_title: 章节标题
            company_id: 企业ID
            max_results: 最大返回数

        Returns:
            该章节的素材
        """
        search_terms = [chapter_title]

        return {
            "chapter": chapter_title,
            "excerpts": self._retrieve_excerpts(company_id, search_terms, max_results),
            "capabilities": self._retrieve_capabilities(company_id, search_terms, max_results),
            "cases": self._retrieve_cases(company_id, search_terms, max_results // 2)
        }
