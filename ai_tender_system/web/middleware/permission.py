#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限检查中间件
提供完整的权限控制装饰器和辅助函数
"""

from functools import wraps
from flask import session, jsonify, g
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List


# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'knowledge_base.db'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    获取当前登录用户的完整信息

    Returns:
        用户信息字典,包含:
        - user_id: 用户ID
        - username: 用户名
        - role_id: 角色ID
        - role_name: 角色名称
        - privacy_level_access: 可访问的隐私级别
        - can_upload: 是否可上传
        - can_delete: 是否可删除
        - can_modify_privacy: 是否可修改隐私级别
        - can_manage_users: 是否可管理用户
        - company_id: 关联公司ID

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

        # 查询用户完整信息(包含角色权限)
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


def require_permission(permission: str):
    """
    要求特定权限

    参数:
        permission: 权限名称
            - 'upload': 上传权限
            - 'delete': 删除权限
            - 'modify_privacy': 修改隐私级别权限
            - 'manage_users': 管理用户权限

    使用方式:
        @app.route('/api/upload')
        @require_permission('upload')
        def upload_file():
            return jsonify({'message': '上传成功'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    'code': -1,
                    'message': '请先登录'
                }), 401

            # 检查权限
            permission_field = f'can_{permission}'
            if not user.get(permission_field, False):
                return jsonify({
                    'code': -1,
                    'message': f'您没有{permission}权限'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(allowed_roles: List[str]):
    """
    要求特定角色

    参数:
        allowed_roles: 允许的角色名称列表

    使用方式:
        @app.route('/api/admin')
        @require_role(['高级管理', '项目经理'])
        def admin_function():
            return jsonify({'message': '管理功能'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    'code': -1,
                    'message': '请先登录'
                }), 401

            if user.get('role_name') not in allowed_roles:
                return jsonify({
                    'code': -1,
                    'message': f'需要以下角色之一: {", ".join(allowed_roles)}'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_privacy_level(min_level: int):
    """
    要求最小隐私访问级别

    参数:
        min_level: 最小隐私级别 (1-4)
            1: 公开
            2: 内部
            3: 机密
            4: 绝密

    使用方式:
        @app.route('/api/confidential-data')
        @require_privacy_level(3)
        def get_confidential_data():
            return jsonify({'data': '机密数据'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    'code': -1,
                    'message': '请先登录'
                }), 401

            user_level = user.get('privacy_level_access', 1)
            if user_level < min_level:
                level_names = {1: '公开', 2: '内部', 3: '机密', 4: '绝密'}
                return jsonify({
                    'code': -1,
                    'message': f'需要{level_names.get(min_level)}级别权限'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def can_access_resource(user: Dict[str, Any], resource_privacy_level: int) -> bool:
    """
    检查用户是否可以访问指定隐私级别的资源

    Args:
        user: 用户信息字典
        resource_privacy_level: 资源的隐私级别(1-4)

    Returns:
        bool: True表示可以访问
    """
    user_level = user.get('privacy_level_access', 1)
    return user_level >= resource_privacy_level


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
    if user.get('role_name') in ['高级管理', '项目经理']:
        return True

    # 检查是否是创建者
    return user.get('user_id') == resource_creator_id


def filter_by_permission(user: Dict[str, Any], include_created_by: bool = True) -> Dict[str, Any]:
    """
    根据用户权限生成数据过滤条件

    Args:
        user: 用户信息字典
        include_created_by: 是否包含创建者过滤(普通用户只看自己的数据)

    Returns:
        过滤条件字典:
        - where_clause: SQL WHERE子句
        - params: SQL参数列表
        - user_id: 当前用户ID
        - role_name: 角色名称
    """
    role_name = user.get('role_name', '普通用户')
    user_id = user.get('user_id')

    # 高级管理和项目经理: 可以看到所有数据
    if role_name in ['高级管理', '项目经理']:
        return {
            'where_clause': '1=1',  # 无限制
            'params': [],
            'user_id': user_id,
            'role_name': role_name,
            'is_admin': True
        }

    # 普通用户和内部员工: 只能看到自己创建的数据
    if include_created_by:
        return {
            'where_clause': 'created_by_user_id = ?',
            'params': [user_id],
            'user_id': user_id,
            'role_name': role_name,
            'is_admin': False
        }
    else:
        return {
            'where_clause': '1=1',
            'params': [],
            'user_id': user_id,
            'role_name': role_name,
            'is_admin': False
        }


# ==================== 便捷的组合装饰器 ====================

def require_upload_permission(f):
    """要求上传权限"""
    @wraps(f)
    @require_permission('upload')
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def require_delete_permission(f):
    """要求删除权限"""
    @wraps(f)
    @require_permission('delete')
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """要求管理员权限"""
    @wraps(f)
    @require_role(['高级管理'])
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def require_manager(f):
    """要求项目经理或以上权限"""
    @wraps(f)
    @require_role(['高级管理', '项目经理'])
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


__all__ = [
    'get_current_user',
    'require_auth',
    'require_permission',
    'require_role',
    'require_privacy_level',
    'can_access_resource',
    'is_owner_or_admin',
    'filter_by_permission',
    'require_upload_permission',
    'require_delete_permission',
    'require_admin',
    'require_manager'
]
