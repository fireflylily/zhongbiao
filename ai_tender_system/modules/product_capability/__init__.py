#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品能力模块

提供产品能力索引的构建、管理和搜索功能：
- TagManager: 核心能力标签管理
- CapabilityExtractor: AI从文档提取能力
- CapabilityIndexer: 能力索引构建
- CapabilitySearcher: 能力搜索匹配
"""

from .tag_manager import TagManager
from .capability_extractor import CapabilityExtractor
from .capability_searcher import CapabilitySearcher

__all__ = [
    'TagManager',
    'CapabilityExtractor',
    'CapabilitySearcher',
]
