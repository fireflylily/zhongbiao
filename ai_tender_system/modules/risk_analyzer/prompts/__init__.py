#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书宝 5.0 提示词模板模块
实现专家接力式提示词架构
"""

from .toc_navigator import PROMPT_A_TOC_NAVIGATOR, TOC_NAVIGATOR_SYSTEM
from .bid_evaluator import PROMPT_B_BID_EVALUATOR, BID_EVALUATOR_SYSTEM
from .todo_generator import PROMPT_C_TODO_GENERATOR, TODO_GENERATOR_SYSTEM
from .compliance_auditor import PROMPT_D_COMPLIANCE_AUDITOR, COMPLIANCE_AUDITOR_SYSTEM

__all__ = [
    'PROMPT_A_TOC_NAVIGATOR',
    'TOC_NAVIGATOR_SYSTEM',
    'PROMPT_B_BID_EVALUATOR',
    'BID_EVALUATOR_SYSTEM',
    'PROMPT_C_TODO_GENERATOR',
    'TODO_GENERATOR_SYSTEM',
    'PROMPT_D_COMPLIANCE_AUDITOR',
    'COMPLIANCE_AUDITOR_SYSTEM',
]
