#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术需求点对点回复模块
用于处理招标文件中的技术需求，生成对应的技术响应
"""

try:
    from .tech_responder import TechResponder
    TECH_RESPONDER_AVAILABLE = True
except ImportError as e:
    print(f"技术需求回复模块导入失败: {e}")
    TECH_RESPONDER_AVAILABLE = False

__all__ = ['TechResponder', 'TECH_RESPONDER_AVAILABLE']