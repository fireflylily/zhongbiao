#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析模块
提供标书废标风险识别功能，可被小程序和Web端共用

V5.0 新增功能：
- 专家接力式提示词架构 (A/B/C/D)
- 目录感知 + 智能降级切片策略
- 双向对账引擎
- 增强版 Excel 导出
"""

from .schemas import RiskItem, RiskAnalysisResult, ReconcileResult, TodoItem
from .analyzer import RiskAnalyzer
from .task_manager import RiskTaskManager

# V5 新增模块
try:
    from .analyzer_v5 import RiskAnalyzerV5
    from .reconciler import Reconciler, reconcile_response
    from .toc_extractor import TocExtractor, extract_toc
    from .smart_chunker import SmartChunker, smart_chunk
    from .prompt_manager import PromptManager, PromptType, get_prompt_manager
    from .excel_exporter import ExcelExporterV5, export_risk_report
    V5_AVAILABLE = True
except ImportError as e:
    V5_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"V5 模块加载失败: {e}")

__all__ = [
    # 核心类
    'RiskItem',
    'RiskAnalysisResult',
    'RiskAnalyzer',
    'RiskTaskManager',

    # V5 新增
    'ReconcileResult',
    'TodoItem',
    'V5_AVAILABLE',
]

# 动态添加 V5 模块到 __all__
if V5_AVAILABLE:
    __all__.extend([
        'RiskAnalyzerV5',
        'Reconciler',
        'reconcile_response',
        'TocExtractor',
        'extract_toc',
        'SmartChunker',
        'smart_chunk',
        'PromptManager',
        'PromptType',
        'get_prompt_manager',
        'ExcelExporterV5',
        'export_risk_report',
    ])
