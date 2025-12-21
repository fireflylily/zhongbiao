#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基础智能体类 - 所有智能体的基类"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from ai_tender_system.common import get_prompt_manager, create_llm_client


class BaseAgent(ABC):
    """
    基础智能体类

    提供通用功能:
    1. 提示词加载 (通过 prompt_manager)
    2. LLM 调用
    3. JSON 解析
    4. 日志记录
    5. 页数/字数计算
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化智能体

        Args:
            model_name: LLM 模型名称
        """
        self.model_name = model_name
        self.prompt_manager = get_prompt_manager()
        self.llm_client = create_llm_client(model_name)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _call_llm(self, prompt: str, response_format: str = None) -> str:
        """
        调用LLM

        Args:
            prompt: 提示词
            response_format: 响应格式 ("json_object" 或 None)

        Returns:
            LLM响应文本
        """
        # 如果需要JSON格式，在提示词中明确要求
        if response_format == "json_object":
            prompt = prompt + "\n\n请严格按照JSON格式返回，不要包含任何其他文本。"

        # ✅ 不传递temperature参数，让LLMClient内部根据模型配置处理
        # 因为某些模型（如shihuang-gpt4o-mini）不支持自定义temperature
        # LLMClient.call()会根据model_config['supports_temperature']自动处理
        return self.llm_client.call(
            prompt=prompt,
            purpose=f"{self.__class__.__name__} 调用"
        )

    def _get_prompt(self, module: str, prompt_key: str, **kwargs) -> str:
        """
        从 prompt_manager 获取并格式化提示词

        支持从 prompts/agent_prompts/ 子目录加载智能体专用提示词

        Args:
            module: 提示词模块名 (如 "scoring_point_agent")
            prompt_key: 提示词键名
            **kwargs: 格式化参数

        Returns:
            格式化后的提示词
        """
        # 尝试从 agent_prompts 子目录加载
        import json
        from pathlib import Path

        prompts_dir = Path(__file__).parent.parent.parent.parent / "prompts"
        agent_prompts_file = prompts_dir / "agent_prompts" / f"{module}.json"

        template = f"[提示词缺失: {module}.{prompt_key}]"

        if agent_prompts_file.exists():
            try:
                with open(agent_prompts_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    template = config.get('prompts', {}).get(prompt_key, template)
            except Exception as e:
                self.logger.warning(f"加载智能体提示词失败: {e}")
        else:
            # 回退到 PromptManager（用于共享提示词）
            template = self.prompt_manager.get_prompt(
                module,
                prompt_key,
                default=template
            )

        # 格式化提示词
        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                self.logger.warning(f"提示词格式化失败: {e}, 返回原始模板")
                return template

        return template

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 返回的 JSON 响应

        Args:
            response: LLM 响应文本

        Returns:
            解析后的字典
        """
        try:
            # 移除可能的 markdown 代码块标记
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {e}\n响应内容: {response[:200]}...")
            return {}

    def calculate_word_count(self, page_count: int, content_style: Dict) -> int:
        """
        计算目标字数

        基准: 1页 = 700字 (A4纸，小四号字，1.5倍行距)

        调整系数:
        - 表格: 无(1.0) / 少量(0.9) / 适量(0.8) / 大量(0.7)
        - 流程图: 无(1.0) / 流程图(0.9) / SmartArt(0.85)
        - 图片: 无(1.0) / 少量(0.95) / 大量(0.85)

        Args:
            page_count: 页数
            content_style: 内容风格配置

        Returns:
            目标字数
        """
        base_words = page_count * 700

        # 表格系数
        table_factor = {
            '无': 1.0,
            '少量': 0.9,
            '适量': 0.8,
            '大量': 0.7
        }.get(content_style.get('tables', '适量'), 0.8)

        # 流程图系数
        flowchart_factor = {
            '无': 1.0,
            '流程图': 0.9,
            'SmartArt': 0.85
        }.get(content_style.get('flowcharts', '流程图'), 0.9)

        # 图片系数
        image_factor = {
            '无': 1.0,
            '少量': 0.95,
            '大量': 0.85
        }.get(content_style.get('images', '少量'), 0.95)

        # 综合系数
        final_factor = table_factor * flowchart_factor * image_factor

        target_words = int(base_words * final_factor)

        self.logger.info(
            f"页数控制: {page_count}页 × 700字 × {final_factor:.2f} = {target_words}字"
        )

        return target_words

    def _validate_required_fields(self, data: Dict, required_fields: List[str]) -> bool:
        """
        验证必填字段

        Args:
            data: 待验证的数据
            required_fields: 必填字段列表

        Returns:
            是否通过验证
        """
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            self.logger.error(f"缺少必填字段: {missing_fields}")
            return False

        return True

    @abstractmethod
    def generate(self, *args, **kwargs) -> Dict[str, Any]:
        """
        生成内容 - 子类必须实现

        Returns:
            生成结果字典
        """
        pass
