#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证蓝图
处理用户登录、登出和会话管理
"""

import sys
import sqlite3
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, current_app
from flask_wtf.csrf import CSRFProtect

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger

# 导入bcrypt用于密码验证
try:
    import bcrypt
except ImportError:
    bcrypt = None
    logger = get_module_logger("web.auth")
    logger.warning("bcrypt未安装，将使用备用密码验证方式")

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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 加密的密码哈希

    Returns:
        bool: 密码是否匹配
    """
    if not hashed_password:
        return False

    if bcrypt:
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    else:
        # 备用方式：简单比较（不推荐用于生产环境）
        logger.warning("使用不安全的密码验证方式")
        return plain_password == hashed_password


def hash_password(plain_password: str) -> str:
    """加密密码

    Args:
        plain_password: 明文密码

    Returns:
        str: 加密后的密码哈希
    """
    if bcrypt:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    else:
        # 备用方式：不加密（不推荐用于生产环境）
        logger.warning("bcrypt未安装，密码未加密")
        return plain_password


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
            logger.info(f"开始处理用户 {username} 的登录请求")

            # 检查数据库文件是否存在
            if not DB_PATH.exists():
                logger.error(f"数据库文件不存在: {DB_PATH}")
                return jsonify({'success': False, 'message': '系统配置错误，请联系管理员'}), 500

            logger.info(f"数据库路径: {DB_PATH}")
            conn = get_db_connection()
            cursor = conn.cursor()
            logger.info("数据库连接成功")

            # 查询用户及其角色信息（包括密码）
            cursor.execute("""
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    u.password,
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
            logger.info(f"数据库查询完成，找到用户: {user_row is not None}")

            # 检查用户是否存在
            if not user_row:
                logger.warning(f"用户 {username} 不存在或已禁用")
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

            user = dict(user_row)
            logger.info(f"用户信息: user_id={user['user_id']}, role={user['role_name']}")

            # 验证密码（使用bcrypt）
            if not verify_password(password, user.get('password', '')):
                logger.warning(f"用户 {username} 登录失败：密码错误")
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

            # 保存完整的session信息
            logger.info("开始保存session信息")
            try:
                session['logged_in'] = True
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role_id'] = user['role_id']
                session['role_name'] = user['role_name']
                session['privacy_level_access'] = user['privacy_level_access']
                session['company_id'] = user['company_id']
                logger.info("session信息保存成功")
            except Exception as session_error:
                logger.error(f"保存session失败: {session_error}")
                raise

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
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"登录过程发生错误: {e}")
            logger.error(f"详细错误信息:\n{error_detail}")
            return jsonify({
                'success': False,
                'message': '登录失败,请稍后重试',
                'error': str(e) if current_app.debug else None  # 开发环境返回详细错误
            }), 500

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


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    修改当前用户密码

    POST请求格式:
    {
        "old_password": "旧密码",
        "new_password": "新密码",
        "confirm_password": "确认新密码"
    }

    Returns:
        JSON响应 {"success": true/false, "message": "..."}
    """
    # 检查是否已登录
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'success': False, 'message': '请先登录'}), 401

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '会话信息不完整，请重新登录'}), 401

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据格式错误'}), 400

    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    # 验证输入
    if not old_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': '所有字段都是必填的'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的新密码不一致'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少为6个字符'}), 400

    if old_password == new_password:
        return jsonify({'success': False, 'message': '新密码不能与旧密码相同'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户当前密码
        cursor.execute("SELECT password, username FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()

        if not user_row:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        current_password_hash = user_row['password']
        username = user_row['username']

        # 验证旧密码
        if not verify_password(old_password, current_password_hash):
            conn.close()
            logger.warning(f"用户 {username} (ID:{user_id}) 修改密码失败：旧密码错误")
            return jsonify({'success': False, 'message': '旧密码错误'}), 401

        # 加密新密码
        new_password_hash = hash_password(new_password)

        # 更新密码
        cursor.execute(
            "UPDATE users SET password = ? WHERE user_id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()
        conn.close()

        logger.info(f"用户 {username} (ID:{user_id}) 成功修改密码")

        return jsonify({
            'success': True,
            'message': '密码修改成功，请使用新密码重新登录'
        })

    except Exception as e:
        logger.error(f"修改密码过程发生错误: {e}")
        return jsonify({'success': False, 'message': '修改密码失败，请稍后重试'}), 500


__all__ = ['auth_bp']
