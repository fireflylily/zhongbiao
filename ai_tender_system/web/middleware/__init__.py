#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中间件模块
提供认证、授权等中间件功能
"""

from .auth import login_required

__all__ = ['login_required']
