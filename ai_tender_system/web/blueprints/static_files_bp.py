#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态文件蓝图
处理CSS、JavaScript和图片等静态资源的服务
"""

import sys
from pathlib import Path
from flask import Blueprint, send_from_directory

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_config

# 创建蓝图
static_files_bp = Blueprint('static_files', __name__)

# 获取配置
config = get_config()


@static_files_bp.route('/css/<path:filename>')
def serve_css(filename):
    """
    提供CSS文件

    Args:
        filename: CSS文件路径（相对于static/css目录）

    Returns:
        CSS文件内容
    """
    return send_from_directory(config.get_path('static') / 'css', filename)


@static_files_bp.route('/js/<path:filename>')
def serve_js(filename):
    """
    提供JavaScript文件

    Args:
        filename: JS文件路径（相对于static/js目录）

    Returns:
        JavaScript文件内容
    """
    return send_from_directory(config.get_path('static') / 'js', filename)


@static_files_bp.route('/images/<path:filename>')
def serve_images(filename):
    """
    提供图片文件

    Args:
        filename: 图片文件路径（相对于static/images目录）

    Returns:
        图片文件内容

    Notes:
        支持常见图片格式: jpg, png, gif, svg, ico等
    """
    return send_from_directory(config.get_path('static') / 'images', filename)


__all__ = ['static_files_bp']
