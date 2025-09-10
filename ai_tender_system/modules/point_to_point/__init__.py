#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点对点应答模块
"""

try:
    from .processor import PointToPointProcessor, DocumentProcessor, TableProcessor
    POINT_TO_POINT_AVAILABLE = True
except ImportError as e:
    print(f"点对点应答模块导入失败: {e}")
    POINT_TO_POINT_AVAILABLE = False

__all__ = ['PointToPointProcessor', 'DocumentProcessor', 'TableProcessor', 'POINT_TO_POINT_AVAILABLE']