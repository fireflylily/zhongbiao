#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理模块
功能：企业信息库、产品知识库、文档管理
"""

from .api import KnowledgeBaseAPI
from .manager import KnowledgeBaseManager

__all__ = ['KnowledgeBaseAPI', 'KnowledgeBaseManager']