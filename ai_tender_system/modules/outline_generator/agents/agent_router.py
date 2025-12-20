#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能体路由器 - 根据用户选择分发到不同智能体"""

import logging
from typing import Dict, Any

from .scoring_point_agent import ScoringPointAgent
from .requirement_response_agent import RequirementResponseAgent
from .template_agent import TemplateAgent


class AgentRouter:
    """
    智能体路由器

    职责:
    根据用户选择的生成模式，将请求路由到对应的智能体

    支持的模式:
    - "按评分点写" → ScoringPointAgent
    - "按招标书目录写" → RequirementResponseAgent
    - "编写专项章节" → TemplateAgent (使用固定模板)
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化路由器

        Args:
            model_name: LLM 模型名称
        """
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)

        # 初始化所有智能体
        self.scoring_agent = ScoringPointAgent(model_name=model_name)
        self.requirement_agent = RequirementResponseAgent(model_name=model_name)
        self.template_agent = TemplateAgent(model_name=model_name)

        self.logger.info("智能体路由器初始化完成")

    def route(self, generation_mode: str, **kwargs) -> Dict[str, Any]:
        """
        路由请求到对应的智能体

        Args:
            generation_mode: 生成模式
                - "按评分点写"
                - "按招标书目录写"
                - "编写专项章节"
            **kwargs: 传递给智能体的参数

        Returns:
            生成结果字典

        Raises:
            ValueError: 未知的生成模式
        """
        self.logger.info(f"【路由器】收到请求，生成模式: {generation_mode}")

        if generation_mode == "按评分点写":
            return self._route_to_scoring_agent(**kwargs)

        elif generation_mode == "按招标书目录写":
            return self._route_to_requirement_agent(**kwargs)

        elif generation_mode == "编写专项章节":
            return self._route_to_template_agent(**kwargs)

        else:
            raise ValueError(
                f"未知的生成模式: {generation_mode}。"
                f"支持的模式: 按评分点写, 按招标书目录写, 编写专项章节"
            )

    def _route_to_scoring_agent(self, **kwargs) -> Dict[str, Any]:
        """
        路由到评分点智能体

        必需参数:
        - tender_doc: 招标文档
        - scoring_points: 评分点列表（可选，如果没有则自动提取）
        - page_count: 目标页数
        - content_style: 内容风格
        """
        self.logger.info("→ 路由到评分点智能体")

        tender_doc = kwargs.get('tender_doc', '')
        scoring_points = kwargs.get('scoring_points')
        page_count = kwargs.get('page_count', 200)
        content_style = kwargs.get('content_style', {})

        # 如果没有提供评分点，先提取
        if not scoring_points:
            self.logger.info("未提供评分点，开始自动提取...")
            scoring_points = self.scoring_agent.extract_scoring_points(tender_doc)

        # 生成方案
        result = self.scoring_agent.generate_proposal_by_scoring(
            tender_doc=tender_doc,
            scoring_points=scoring_points,
            page_count=page_count,
            content_style=content_style
        )

        return result

    def _route_to_requirement_agent(self, **kwargs) -> Dict[str, Any]:
        """
        路由到需求应答智能体

        必需参数:
        - tender_doc: 招标文档
        - page_count: 目标页数
        - content_style: 内容风格
        """
        self.logger.info("→ 路由到需求应答智能体")

        result = self.requirement_agent.generate(
            tender_doc=kwargs.get('tender_doc', ''),
            page_count=kwargs.get('page_count', 200),
            content_style=kwargs.get('content_style', {})
        )

        return result

    def _route_to_template_agent(self, **kwargs) -> Dict[str, Any]:
        """
        路由到模板智能体

        必需参数:
        - tender_doc: 招标文档
        - template_name: 模板名称
        - page_count: 目标页数
        - content_style: 内容风格
        """
        self.logger.info("→ 路由到模板智能体")

        result = self.template_agent.generate(
            tender_doc=kwargs.get('tender_doc', ''),
            template_name=kwargs.get('template_name', '政府采购标准'),
            page_count=kwargs.get('page_count', 200),
            content_style=kwargs.get('content_style', {})
        )

        return result

    def get_available_modes(self) -> Dict[str, Any]:
        """
        获取可用的生成模式

        Returns:
            {
                "modes": [
                    {
                        "id": "按评分点写",
                        "name": "按评分点写",
                        "description": "...",
                        "agent": "ScoringPointAgent"
                    },
                    ...
                ],
                "templates": [...]  # 可用模板列表
            }
        """
        return {
            "modes": [
                {
                    "id": "按评分点写",
                    "name": "按评分点写",
                    "description": "根据招标评分标准生成方案，确保每个评分点都有针对性应答",
                    "agent": "ScoringPointAgent",
                    "recommended_for": ["竞争激烈的项目", "评分标准明确的招标"]
                },
                {
                    "id": "按招标书目录写",
                    "name": "按招标书目录写",
                    "description": "智能分析招标需求，动态生成章节，确保需求完整覆盖",
                    "agent": "RequirementResponseAgent",
                    "recommended_for": ["需求复杂的项目", "表格内容多的招标"]
                },
                {
                    "id": "编写专项章节",
                    "name": "使用固定模板",
                    "description": "使用预定义模板快速生成标准格式方案",
                    "agent": "TemplateAgent",
                    "recommended_for": ["快速起草", "有固定格式要求的项目"]
                }
            ],
            "templates": TemplateAgent.list_templates()
        }
