#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化权限检查中间件
只保留最基础的登录验证和创建者/管理员权限判断
"""

from functools import wraps
from flask import session, jsonify, g
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'knowledge_base.db'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    获取当前登录用户的基本信息

    Returns:
        用户信息字典,包含:
        - user_id: 用户ID
        - username: 用户名
        - role_id: 角色ID
        - role_name: 角色名称
        - company_id: 关联公司ID (可选)

        如果未登录或用户不存在,返回None
    """
    # 如果已经在g对象中缓存,直接返回
    if hasattr(g, 'current_user'):
        return g.current_user

    # 检查session
    if 'user_id' not in session:
        return None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户基本信息
        cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role_id,
                u.company_id,
                u.is_active,
                r.role_name
            FROM users u
            LEFT JOIN user_roles r ON u.role_id = r.role_id
            WHERE u.user_id = ? AND u.is_active = 1
        """, (session['user_id'],))

        user_row = cursor.fetchone()
        conn.close()

        if not user_row:
            return None

        user = dict(user_row)

        # 缓存到g对象中
        g.current_user = user

        return user

    except Exception as e:
        print(f"获取当前用户失败: {e}")
        return None


def require_auth(f):
    """
    要求用户已登录

    使用方式:
        @app.route('/api/data')
        @require_auth
        def get_data():
            user = get_current_user()
            return jsonify({'user': user['username']})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                'code': -1,
                'message': '请先登录'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def is_admin(user: Dict[str, Any]) -> bool:
    """
    检查用户是否是管理员

    Args:
        user: 用户信息字典

    Returns:
        bool: True表示是管理员
    """
    return user.get('role_name') == '高级管理'


def is_owner_or_admin(user: Dict[str, Any], resource_creator_id: int) -> bool:
    """
    检查用户是否是资源的创建者或管理员

    Args:
        user: 用户信息字典
        resource_creator_id: 资源创建者的user_id

    Returns:
        bool: True表示是创建者或管理员
    """
    # 管理员可以访问所有资源
    if is_admin(user):
        return True

    # 检查是否是创建者
    return user.get('user_id') == resource_creator_id


def require_admin(f):
    """
    要求管理员权限

    使用方式:
        @app.route('/api/admin')
        @require_admin
        def admin_function():
            return jsonify({'message': '管理功能'})
    """
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not is_admin(user):
            return jsonify({
                'code': -1,
                'message': '需要管理员权限'
            }), 403

        return f(*args, **kwargs)
    return decorated_function


__all__ = [
    'get_current_user',
    'require_auth',
    'is_admin',
    'is_owner_or_admin',
    'require_admin'
]
