#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词管理器
"""

from enum import Enum
from typing import Dict, Any

from .prompts import (
    COMPLETENESS_CHECK_PROMPT, COMPLETENESS_CHECK_SYSTEM,
    SEAL_CHECK_PROMPT, SEAL_CHECK_SYSTEM,
    PAGE_CHECK_PROMPT, PAGE_CHECK_SYSTEM,
    INDEX_CHECK_PROMPT, INDEX_CHECK_SYSTEM,
    DATE_CHECK_PROMPT, DATE_CHECK_SYSTEM,
    PRICE_CHECK_PROMPT, PRICE_CHECK_SYSTEM,
    PERFORMANCE_CHECK_PROMPT, PERFORMANCE_CHECK_SYSTEM,
)


class PromptType(Enum):
    """提示词类型"""
    COMPLETENESS = "completeness"
    SEAL = "seal"
    PAGE = "page"
    INDEX = "index"
    DATE = "date"
    PRICE = "price"
    PERFORMANCE = "performance"


class ResponseCheckPromptManager:
    """
    应答文件自检查提示词管理器
    """

    # 提示词配置
    PROMPTS = {
        PromptType.COMPLETENESS: {
            'system': COMPLETENESS_CHECK_SYSTEM,
            'user': COMPLETENESS_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1500
        },
        PromptType.SEAL: {
            'system': SEAL_CHECK_SYSTEM,
            'user': SEAL_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1500
        },
        PromptType.PAGE: {
            'system': PAGE_CHECK_SYSTEM,
            'user': PAGE_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1000
        },
        PromptType.INDEX: {
            'system': INDEX_CHECK_SYSTEM,
            'user': INDEX_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1000
        },
        PromptType.DATE: {
            'system': DATE_CHECK_SYSTEM,
            'user': DATE_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1000
        },
        PromptType.PRICE: {
            'system': PRICE_CHECK_SYSTEM,
            'user': PRICE_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1500
        },
        PromptType.PERFORMANCE: {
            'system': PERFORMANCE_CHECK_SYSTEM,
            'user': PERFORMANCE_CHECK_PROMPT,
            'temperature': 0.1,
            'max_tokens': 1500
        },
    }

    def get_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """
        获取格式化后的提示词

        Args:
            prompt_type: 提示词类型
            **kwargs: 格式化参数

        Returns:
            格式化后的提示词
        """
        if prompt_type not in self.PROMPTS:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        template = self.PROMPTS[prompt_type]['user']
        return template.format(**kwargs)

    def get_system_prompt(self, prompt_type: PromptType) -> str:
        """
        获取系统提示词

        Args:
            prompt_type: 提示词类型

        Returns:
            系统提示词
        """
        if prompt_type not in self.PROMPTS:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        return self.PROMPTS[prompt_type]['system']

    def get_config(self, prompt_type: PromptType) -> Dict[str, Any]:
        """
        获取提示词配置

        Args:
            prompt_type: 提示词类型

        Returns:
            配置字典
        """
        if prompt_type not in self.PROMPTS:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        config = self.PROMPTS[prompt_type]
        return {
            'system_prompt': config['system'],
            'temperature': config['temperature'],
            'max_tokens': config['max_tokens']
        }
