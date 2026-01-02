#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词管理器 - 统一管理标书宝 5.0 的所有提示词模板
"""

import json
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

from .prompts.toc_navigator import PROMPT_A_TOC_NAVIGATOR, TOC_NAVIGATOR_SYSTEM
from .prompts.bid_evaluator import (
    PROMPT_B_BID_EVALUATOR,
    BID_EVALUATOR_SYSTEM,
    TOC_HINT_NO_TOC,
    TOC_HINT_WITH_TOC
)
from .prompts.todo_generator import PROMPT_C_TODO_GENERATOR, TODO_GENERATOR_SYSTEM
from .prompts.compliance_auditor import PROMPT_D_COMPLIANCE_AUDITOR, COMPLIANCE_AUDITOR_SYSTEM

logger = get_module_logger("risk_analyzer.prompt_manager")


class PromptType(Enum):
    """提示词类型枚举"""
    TOC_NAVIGATOR = "A"       # 目录导航员
    BID_EVALUATOR = "B"       # 资深评标组长
    TODO_GENERATOR = "C"      # 投标执行秘书
    COMPLIANCE_AUDITOR = "D"  # 合规审计法务


class PromptConfig:
    """提示词配置"""

    # 各提示词推荐的温度设置
    TEMPERATURE = {
        PromptType.TOC_NAVIGATOR: 0.1,      # 目录解析需要精确
        PromptType.BID_EVALUATOR: 0.1,      # 风险识别需要严谨
        PromptType.TODO_GENERATOR: 0.5,     # Todo 生成可以稍灵活
        PromptType.COMPLIANCE_AUDITOR: 0.1, # 合规审计需要严谨
    }

    # 各提示词推荐的最大 token 数
    MAX_TOKENS = {
        PromptType.TOC_NAVIGATOR: 2000,
        PromptType.BID_EVALUATOR: 3000,
        PromptType.TODO_GENERATOR: 2000,
        PromptType.COMPLIANCE_AUDITOR: 2000,
    }

    # 提示词用途描述（用于日志）
    PURPOSE = {
        PromptType.TOC_NAVIGATOR: "目录结构解析",
        PromptType.BID_EVALUATOR: "风险项提取",
        PromptType.TODO_GENERATOR: "Todo动作生成",
        PromptType.COMPLIANCE_AUDITOR: "合规性审计",
    }


class PromptManager:
    """
    提示词管理器 - 统一管理所有提示词模板

    使用示例:
        pm = PromptManager()

        # 获取填充后的提示词
        prompt = pm.get_prompt(
            PromptType.BID_EVALUATOR,
            chapter_title="第三章 评标办法",
            chapter_content="..."
        )

        # 获取系统提示词
        system_prompt = pm.get_system_prompt(PromptType.BID_EVALUATOR)

        # 获取配置
        temperature = pm.get_temperature(PromptType.BID_EVALUATOR)
    """

    def __init__(self):
        """初始化提示词管理器"""
        self._templates: Dict[PromptType, str] = {}
        self._system_prompts: Dict[PromptType, str] = {}
        self._load_templates()
        logger.info("提示词管理器初始化完成")

    def _load_templates(self):
        """加载所有提示词模板"""
        self._templates = {
            PromptType.TOC_NAVIGATOR: PROMPT_A_TOC_NAVIGATOR,
            PromptType.BID_EVALUATOR: PROMPT_B_BID_EVALUATOR,
            PromptType.TODO_GENERATOR: PROMPT_C_TODO_GENERATOR,
            PromptType.COMPLIANCE_AUDITOR: PROMPT_D_COMPLIANCE_AUDITOR,
        }

        self._system_prompts = {
            PromptType.TOC_NAVIGATOR: TOC_NAVIGATOR_SYSTEM,
            PromptType.BID_EVALUATOR: BID_EVALUATOR_SYSTEM,
            PromptType.TODO_GENERATOR: TODO_GENERATOR_SYSTEM,
            PromptType.COMPLIANCE_AUDITOR: COMPLIANCE_AUDITOR_SYSTEM,
        }

        logger.debug(f"加载了 {len(self._templates)} 个提示词模板")

    def get_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """
        获取填充后的提示词

        Args:
            prompt_type: 提示词类型
            **kwargs: 用于填充模板的变量

        Returns:
            填充后的提示词字符串
        """
        template = self._templates.get(prompt_type)
        if not template:
            raise ValueError(f"未知的提示词类型: {prompt_type}")

        try:
            # 特殊处理：BID_EVALUATOR 需要处理 toc_hint
            if prompt_type == PromptType.BID_EVALUATOR:
                has_toc = kwargs.pop('has_toc', True)
                kwargs['toc_hint'] = TOC_HINT_WITH_TOC if has_toc else TOC_HINT_NO_TOC

            # 使用 format 填充变量
            filled_prompt = template.format(**kwargs)
            return filled_prompt

        except KeyError as e:
            logger.error(f"提示词模板缺少必要参数: {e}")
            raise ValueError(f"提示词模板缺少必要参数: {e}")

    def get_system_prompt(self, prompt_type: PromptType) -> str:
        """
        获取系统提示词

        Args:
            prompt_type: 提示词类型

        Returns:
            系统提示词字符串
        """
        system_prompt = self._system_prompts.get(prompt_type)
        if not system_prompt:
            raise ValueError(f"未知的提示词类型: {prompt_type}")
        return system_prompt

    def get_temperature(self, prompt_type: PromptType) -> float:
        """获取推荐的温度设置"""
        return PromptConfig.TEMPERATURE.get(prompt_type, 0.3)

    def get_max_tokens(self, prompt_type: PromptType) -> int:
        """获取推荐的最大 token 数"""
        return PromptConfig.MAX_TOKENS.get(prompt_type, 2000)

    def get_purpose(self, prompt_type: PromptType) -> str:
        """获取提示词用途描述"""
        return PromptConfig.PURPOSE.get(prompt_type, "LLM调用")

    def get_config(self, prompt_type: PromptType) -> Dict[str, Any]:
        """
        获取提示词的完整配置

        Returns:
            {
                'system_prompt': str,
                'temperature': float,
                'max_tokens': int,
                'purpose': str
            }
        """
        return {
            'system_prompt': self.get_system_prompt(prompt_type),
            'temperature': self.get_temperature(prompt_type),
            'max_tokens': self.get_max_tokens(prompt_type),
            'purpose': self.get_purpose(prompt_type),
        }


# 全局单例
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """获取提示词管理器单例"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
