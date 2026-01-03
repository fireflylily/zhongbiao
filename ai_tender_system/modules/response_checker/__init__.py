#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应答文件自检查模块

功能：对投标应答文件进行28项自动化检查，包括：
- 完整性检查（3项）
- 签字盖章检查（3项）
- 页码检查（2项）
- 索引表检查（2项）
- 法人身份证检查（3项）
- 被授权人身份证检查（3项）
- 营业执照检查（3项）
- 应答日期检查（2项）
- 报价检查（3项）
- 业绩检查（4项）
"""

from .schemas import (
    CheckItem,
    CheckCategory,
    ExtractedInfo,
    ResponseCheckResult,
    ResponseCheckTask,
    CheckStatus,
    CheckCategoryType
)
from .checker import ResponseChecker
from .task_manager import ResponseCheckTaskManager
from .excel_exporter import ResponseCheckExcelExporter

__all__ = [
    'CheckItem',
    'CheckCategory',
    'ExtractedInfo',
    'ResponseCheckResult',
    'ResponseCheckTask',
    'CheckStatus',
    'CheckCategoryType',
    'ResponseChecker',
    'ResponseCheckTaskManager',
    'ResponseCheckExcelExporter'
]
