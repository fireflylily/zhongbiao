#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vue 前端应用蓝图
服务构建后的 Vue SPA 应用
"""

import sys
from pathlib import Path
from flask import Blueprint, send_from_directory, abort

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("vue_app_bp")

# 创建蓝图 - 移除url_prefix,直接在根路径提供服务
vue_app_bp = Blueprint('vue_app', __name__)


@vue_app_bp.route('/')
@vue_app_bp.route('/<path:path>')
def serve_vue_app(path=''):
    """
    服务 Vue SPA 应用

    所有 /app/* 路径都返回 index.html，让 Vue Router 处理路由
    """
    from common import get_config
    config = get_config()

    # Vue 构建输出目录
    dist_dir = config.get_path('static') / 'dist'

    if not dist_dir.exists():
        logger.error(f"Vue 应用未构建，找不到目录: {dist_dir}")
        abort(404, description="Vue 应用未构建，请先运行 'cd frontend && npm run build'")

    # 如果请求的是具体文件（有扩展名），尝试返回该文件
    if path and '.' in path.split('/')[-1]:
        file_path = dist_dir / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(dist_dir, path)

    # 否则返回 index.html，让 Vue Router 处理
    index_file = dist_dir / 'index.html'
    if not index_file.exists():
        logger.error(f"找不到 index.html: {index_file}")
        abort(404, description="找不到 index.html，请检查构建配置")

    return send_from_directory(dist_dir, 'index.html')


__all__ = ['vue_app_bp']
