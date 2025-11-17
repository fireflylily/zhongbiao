#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证蓝图
处理用户登录、登出和会话管理
"""

import sys
import sqlite3
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

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'knowledge_base.db'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@auth_bp.route('/')
def index():
    """
    主页 - 检查登录状态并重定向

    逻辑:
    - 已登录: 重定向到仪表板
    - 未登录: 重定向到登录页
    """
    if 'logged_in' in session:
        return redirect(url_for('vue_app.serve_vue_app'))
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

        # 查询数据库验证用户
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 查询用户及其角色信息
            cursor.execute("""
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    u.role_id,
                    u.company_id,
                    u.is_active,
                    r.role_name,
                    r.role_description,
                    r.privacy_level_access,
                    r.can_upload,
                    r.can_delete,
                    r.can_modify_privacy,
                    r.can_manage_users
                FROM users u
                LEFT JOIN user_roles r ON u.role_id = r.role_id
                WHERE u.username = ? AND u.is_active = 1
            """, (username,))

            user_row = cursor.fetchone()
            conn.close()

            # 检查用户是否存在
            if not user_row:
                logger.warning(f"用户 {username} 不存在或已禁用")
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

            user = dict(user_row)

            # 简单密码验证 (TODO: 使用加密密码验证)
            # 当前: admin账号密码为admin123, 其他用户密码为: 用户名123
            valid_password = False
            if username == 'admin' and password == 'admin123':
                valid_password = True
            elif password == f"{username}123":  # 临时方案: 用户名+123
                valid_password = True

            if not valid_password:
                logger.warning(f"用户 {username} 登录失败：密码错误")
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

            # 保存完整的session信息
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role_id'] = user['role_id']
            session['role_name'] = user['role_name']
            session['privacy_level_access'] = user['privacy_level_access']
            session['company_id'] = user['company_id']

            # 更新最后登录时间
            try:
                from datetime import datetime
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (datetime.now(), user['user_id'])
                )
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"更新最后登录时间失败: {e}")

            logger.info(f"用户 {username} (ID:{user['user_id']}, 角色:{user['role_name']}) 登录成功")

            # 返回用户信息和token（前端期望的格式）
            return jsonify({
                'success': True,
                'message': '登录成功',
                'data': {
                    'user': {
                        'id': user['user_id'],
                        'username': user['username'],
                        'email': user['email'] or '',
                        'role': user['role_name'],
                        'role_id': user['role_id'],
                        'company_id': user['company_id'],
                        'permissions': {
                            'can_upload': bool(user['can_upload']),
                            'can_delete': bool(user['can_delete']),
                            'can_modify_privacy': bool(user['can_modify_privacy']),
                            'can_manage_users': bool(user['can_manage_users']),
                            'privacy_level_access': user['privacy_level_access']
                        }
                    },
                    'token': 'fake-jwt-token-for-development'  # TODO: 生成真实JWT token
                }
            })

        except Exception as e:
            logger.error(f"登录过程发生错误: {e}")
            return jsonify({'success': False, 'message': '登录失败,请稍后重试'}), 500

    # GET请求: 重定向到Vue应用（Vue Router会处理登录和仪表板路由）
    return redirect(url_for('vue_app.serve_vue_app'))


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
        user_id = session.get('user_id')
        username = session.get('username', '')

        # 如果session中有完整信息,直接返回
        if user_id:
            return jsonify({
                'success': True,
                'data': {
                    'valid': True,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'email': session.get('email', ''),
                        'role': session.get('role_name', 'admin'),
                        'role_id': session.get('role_id'),
                        'company_id': session.get('company_id'),
                        'permissions': {
                            'privacy_level_access': session.get('privacy_level_access', 4)
                        }
                    }
                }
            })
        else:
            # 兼容旧session(只有username的情况)
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
