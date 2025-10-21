#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面蓝图
处理所有静态HTML页面的路由
"""

import sys
from pathlib import Path
from flask import Blueprint, render_template

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.middleware.auth import login_required

# 创建蓝图
pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/dashboard')
@login_required
def dashboard():
    """
    主仪表板页面

    需要登录才能访问
    """
    return render_template('index.html')


@pages_bp.route('/help.html')
def help():
    """帮助页面"""
    return render_template('help.html')


@pages_bp.route('/system_status.html')
def system_status():
    """系统状态页面"""
    return render_template('system_status.html')


@pages_bp.route('/tender_processing.html')
def tender_processing_html():
    """标书智能处理页面（.html路径）"""
    return render_template('tender_processing.html')


@pages_bp.route('/tender_processing')
def tender_processing():
    """标书智能处理页面（简洁路径）"""
    return render_template('tender_processing.html')


__all__ = ['pages_bp']
