#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享资源模块
提供全局实例和辅助函数
"""

from .instances import get_kb_manager, PIPELINE_INSTANCES

__all__ = ['get_kb_manager', 'PIPELINE_INSTANCES']
