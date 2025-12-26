#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书素材库模块

用于管理历史标书文档和优秀片段：
1. TenderDocumentManager - 标书文档管理
2. ExcerptManager - 片段/章节管理
3. MaterialRetriever - 素材检索
"""

from .document_manager import TenderDocumentManager
from .excerpt_manager import ExcerptManager

__all__ = [
    'TenderDocumentManager',
    'ExcerptManager'
]
