#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证蓝图
处理用户登录、登出和会话管理
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 日志记录器
logger = get_module_logger("web.auth")

# CSRF豁免装饰器
def csrf_exempt(f):
    """CSRF豁免装饰器"""
    f.csrf_exempt = True
    return f


@auth_bp.route('/')
def index():
    """
    主页 - 检查登录状态并重定向

    逻辑:
    - 已登录: 重定向到仪表板
    - 未登录: 重定向到登录页
    """
    if 'logged_in' in session:
        return redirect(url_for('pages.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf_exempt
def login():
    """
    登录页面和登录处理

    GET: 显示登录页面
    POST: 处理登录请求（JSON格式）

    POST请求格式:
    {
        "username": "admin",
        "password": "admin123"
    }

    Returns:
        GET: 登录页面HTML
        POST: JSON响应 {"success": true/false, "message": "..."}
    """
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 简单的用户名密码验证
        # TODO: 替换为真实的用户认证系统
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            logger.info(f"用户 {username} 登录成功")
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            logger.warning(f"用户 {username} 登录失败：密码错误")
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    # GET请求: 如果已登录则重定向到仪表板
    if 'logged_in' in session:
        return redirect(url_for('pages.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    退出登录

    清除会话数据并重定向到登录页
    """
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"用户 {username} 已退出登录")
    return redirect(url_for('auth.login'))


__all__ = ['auth_bp']
