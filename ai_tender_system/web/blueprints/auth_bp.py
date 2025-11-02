#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证蓝图
处理用户登录、登出和会话管理
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger

# 创建蓝图
# CSRFProtect will be applied at app level, but we need to exempt login route
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 创建CSRF保护实例（用于装饰器）
csrf = CSRFProtect()

# 日志记录器
logger = get_module_logger("web.auth")


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
@csrf.exempt
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

        # 获取用户名和密码，添加类型检查
        username = data.get('username', '')
        password = data.get('password', '')

        # 类型检查和健壮性处理
        if not isinstance(username, str) or not isinstance(password, str):
            logger.warning(f"登录请求数据格式错误: username={type(username)}, password={type(password)}")
            return jsonify({
                'success': False,
                'message': '用户名或密码格式错误'
            }), 400

        username = username.strip()
        password = password.strip()

        # 简单的用户名密码验证
        # TODO: 替换为真实的用户认证系统
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            logger.info(f"用户 {username} 登录成功")

            # 返回用户信息和token（前端期望的格式）
            return jsonify({
                'success': True,
                'message': '登录成功',
                'data': {
                    'user': {
                        'id': 1,
                        'username': username,
                        'email': 'admin@example.com',
                        'role': 'admin'
                    },
                    'token': 'fake-jwt-token-for-development'  # TODO: 生成真实JWT token
                }
            })
        else:
            logger.warning(f"用户 {username} 登录失败：密码错误")
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    # GET请求: 如果已登录则重定向到仪表板
    if 'logged_in' in session:
        return redirect(url_for('pages.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    退出登录（API版本）

    POST: 清除session，返回JSON
    """
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"用户 {username} 已退出登录")
    return jsonify({'success': True, 'message': '退出登录成功'})


@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    """
    验证token有效性

    Returns:
        JSON响应 {"success": true, "data": {"valid": true, "user": {...}}}
    """
    # 检查session中是否有登录信息
    if 'logged_in' in session and session.get('logged_in'):
        username = session.get('username', '')

        return jsonify({
            'success': True,
            'data': {
                'valid': True,
                'user': {
                    'id': 1,
                    'username': username,
                    'email': 'admin@example.com',
                    'role': 'admin'
                }
            }
        })
    else:
        return jsonify({
            'success': True,
            'data': {
                'valid': False
            }
        })


__all__ = ['auth_bp']
