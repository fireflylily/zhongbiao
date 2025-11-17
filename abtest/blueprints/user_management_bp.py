"""
用户管理 API Blueprint
提供用户增删改查和角色管理功能
"""

from flask import Blueprint, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

user_management_bp = Blueprint('user_management', __name__,
                              template_folder='../templates')

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                       'ai_tender_system', 'data', 'knowledge_base.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==================== 前端页面路由 ====================

@user_management_bp.route('/', methods=['GET'])
@user_management_bp.route('/management', methods=['GET'])
def user_management_page():
    """用户管理页面"""
    return render_template('user_management.html')


# ==================== 用户管理 API ====================

@user_management_bp.route('/users', methods=['GET'])
def get_users():
    """
    获取用户列表
    支持分页和搜索
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        search = request.args.get('search', '', type=str)
        role_id = request.args.get('role_id', type=int)
        is_active = request.args.get('is_active', type=str)

        conn = get_db_connection()
        cursor = conn.cursor()

        # 构建查询语句
        where_clauses = []
        params = []

        if search:
            where_clauses.append("(u.username LIKE ? OR u.email LIKE ?)")
            params.extend([f'%{search}%', f'%{search}%'])

        if role_id:
            where_clauses.append("u.role_id = ?")
            params.append(role_id)

        if is_active:
            where_clauses.append("u.is_active = ?")
            params.append(1 if is_active.lower() == 'true' else 0)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # 获取总数
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM users u
            WHERE {where_sql}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # 获取用户列表
        offset = (page - 1) * page_size
        params.extend([page_size, offset])

        query_sql = f"""
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role_id,
                r.role_name,
                u.company_id,
                c.company_name,
                u.is_active,
                u.last_login,
                u.created_at
            FROM users u
            LEFT JOIN user_roles r ON u.role_id = r.role_id
            LEFT JOIN companies c ON u.company_id = c.company_id
            WHERE {where_sql}
            ORDER BY u.created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query_sql, params)
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': {
                'users': users,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500


@user_management_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role_id,
                r.role_name,
                r.role_description,
                u.company_id,
                c.company_name,
                u.is_active,
                u.last_login,
                u.created_at
            FROM users u
            LEFT JOIN user_roles r ON u.role_id = r.role_id
            LEFT JOIN companies c ON u.company_id = c.company_id
            WHERE u.user_id = ?
        """, (user_id,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                'code': -1,
                'message': '用户不存在'
            }), 404

        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': dict(user)
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取用户详情失败: {str(e)}'
        }), 500


@user_management_bp.route('/users', methods=['POST'])
def create_user():
    """
    创建新用户
    请求体:
    {
        "username": "用户名",
        "email": "邮箱",
        "role_id": 角色ID,
        "company_id": 公司ID (可选),
        "is_active": true/false
    }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['username', 'role_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': -1,
                    'message': f'缺少必填字段: {field}'
                }), 400

        username = data['username']
        email = data.get('email')
        role_id = data['role_id']
        company_id = data.get('company_id')
        is_active = data.get('is_active', True)

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '用户名已存在'
            }), 400

        # 验证角色是否存在
        cursor.execute("SELECT role_id FROM user_roles WHERE role_id = ?", (role_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '角色不存在'
            }), 400

        # 如果提供了公司ID,验证公司是否存在
        if company_id:
            cursor.execute("SELECT company_id FROM companies WHERE company_id = ?", (company_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({
                    'code': -1,
                    'message': '公司不存在'
                }), 400

        # 插入用户
        cursor.execute("""
            INSERT INTO users (username, email, role_id, company_id, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, role_id, company_id, is_active, datetime.now()))

        user_id = cursor.lastrowid
        conn.commit()

        # 获取创建的用户信息
        cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role_id,
                r.role_name,
                u.company_id,
                c.company_name,
                u.is_active,
                u.created_at
            FROM users u
            LEFT JOIN user_roles r ON u.role_id = r.role_id
            LEFT JOIN companies c ON u.company_id = c.company_id
            WHERE u.user_id = ?
        """, (user_id,))

        user = dict(cursor.fetchone())
        conn.close()

        return jsonify({
            'code': 0,
            'message': '用户创建成功',
            'data': user
        }), 201

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'创建用户失败: {str(e)}'
        }), 500


@user_management_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    更新用户信息
    请求体:
    {
        "username": "用户名" (可选),
        "email": "邮箱" (可选),
        "role_id": 角色ID (可选),
        "company_id": 公司ID (可选),
        "is_active": true/false (可选)
    }
    """
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '用户不存在'
            }), 404

        # 构建更新语句
        update_fields = []
        params = []

        if 'username' in data:
            # 检查新用户名是否已被其他用户使用
            cursor.execute("SELECT user_id FROM users WHERE username = ? AND user_id != ?",
                          (data['username'], user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({
                    'code': -1,
                    'message': '用户名已被使用'
                }), 400
            update_fields.append("username = ?")
            params.append(data['username'])

        if 'email' in data:
            update_fields.append("email = ?")
            params.append(data['email'])

        if 'role_id' in data:
            # 验证角色是否存在
            cursor.execute("SELECT role_id FROM user_roles WHERE role_id = ?", (data['role_id'],))
            if not cursor.fetchone():
                conn.close()
                return jsonify({
                    'code': -1,
                    'message': '角色不存在'
                }), 400
            update_fields.append("role_id = ?")
            params.append(data['role_id'])

        if 'company_id' in data:
            if data['company_id']:
                # 验证公司是否存在
                cursor.execute("SELECT company_id FROM companies WHERE company_id = ?",
                              (data['company_id'],))
                if not cursor.fetchone():
                    conn.close()
                    return jsonify({
                        'code': -1,
                        'message': '公司不存在'
                    }), 400
            update_fields.append("company_id = ?")
            params.append(data['company_id'])

        if 'is_active' in data:
            update_fields.append("is_active = ?")
            params.append(data['is_active'])

        if not update_fields:
            conn.close()
            return jsonify({
                'code': -1,
                'message': '没有要更新的字段'
            }), 400

        # 执行更新
        params.append(user_id)
        update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
        cursor.execute(update_sql, params)
        conn.commit()

        # 获取更新后的用户信息
        cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role_id,
                r.role_name,
                u.company_id,
                c.company_name,
                u.is_active,
                u.last_login,
                u.created_at
            FROM users u
            LEFT JOIN user_roles r ON u.role_id = r.role_id
            LEFT JOIN companies c ON u.company_id = c.company_id
            WHERE u.user_id = ?
        """, (user_id,))

        user = dict(cursor.fetchone())
        conn.close()

        return jsonify({
            'code': 0,
            'message': '用户更新成功',
            'data': user
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'更新用户失败: {str(e)}'
        }), 500


@user_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '用户不存在'
            }), 404

        # 删除用户
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '用户删除成功'
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'删除用户失败: {str(e)}'
        }), 500


# ==================== 角色管理 API ====================

@user_management_bp.route('/roles', methods=['GET'])
def get_roles():
    """获取所有角色列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                r.role_id,
                r.role_name,
                r.role_description,
                r.privacy_level_access,
                r.can_upload,
                r.can_delete,
                r.can_modify_privacy,
                r.can_manage_users,
                r.created_at,
                COUNT(u.user_id) as user_count
            FROM user_roles r
            LEFT JOIN users u ON r.role_id = u.role_id
            GROUP BY r.role_id
            ORDER BY r.role_id
        """)

        roles = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': roles
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取角色列表失败: {str(e)}'
        }), 500


@user_management_bp.route('/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    """获取单个角色详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                r.role_id,
                r.role_name,
                r.role_description,
                r.privacy_level_access,
                r.can_upload,
                r.can_delete,
                r.can_modify_privacy,
                r.can_manage_users,
                r.created_at
            FROM user_roles r
            WHERE r.role_id = ?
        """, (role_id,))

        role = cursor.fetchone()
        conn.close()

        if not role:
            return jsonify({
                'code': -1,
                'message': '角色不存在'
            }), 404

        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': dict(role)
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取角色详情失败: {str(e)}'
        }), 500


@user_management_bp.route('/roles', methods=['POST'])
def create_role():
    """
    创建新角色
    请求体:
    {
        "role_name": "角色名称",
        "role_description": "角色描述",
        "privacy_level_access": 1-4,
        "can_upload": true/false,
        "can_delete": true/false,
        "can_modify_privacy": true/false,
        "can_manage_users": true/false
    }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        if 'role_name' not in data:
            return jsonify({
                'code': -1,
                'message': '缺少必填字段: role_name'
            }), 400

        role_name = data['role_name']
        role_description = data.get('role_description', '')
        privacy_level_access = data.get('privacy_level_access', 1)
        can_upload = data.get('can_upload', False)
        can_delete = data.get('can_delete', False)
        can_modify_privacy = data.get('can_modify_privacy', False)
        can_manage_users = data.get('can_manage_users', False)

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查角色名是否已存在
        cursor.execute("SELECT role_id FROM user_roles WHERE role_name = ?", (role_name,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '角色名已存在'
            }), 400

        # 插入角色
        cursor.execute("""
            INSERT INTO user_roles (
                role_name, role_description, privacy_level_access,
                can_upload, can_delete, can_modify_privacy, can_manage_users,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (role_name, role_description, privacy_level_access,
              can_upload, can_delete, can_modify_privacy, can_manage_users,
              datetime.now()))

        role_id = cursor.lastrowid
        conn.commit()

        # 获取创建的角色信息
        cursor.execute("""
            SELECT
                role_id, role_name, role_description, privacy_level_access,
                can_upload, can_delete, can_modify_privacy, can_manage_users,
                created_at
            FROM user_roles
            WHERE role_id = ?
        """, (role_id,))

        role = dict(cursor.fetchone())
        conn.close()

        return jsonify({
            'code': 0,
            'message': '角色创建成功',
            'data': role
        }), 201

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'创建角色失败: {str(e)}'
        }), 500


@user_management_bp.route('/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    """更新角色信息"""
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查角色是否存在
        cursor.execute("SELECT role_id FROM user_roles WHERE role_id = ?", (role_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '角色不存在'
            }), 404

        # 构建更新语句
        update_fields = []
        params = []

        allowed_fields = [
            'role_name', 'role_description', 'privacy_level_access',
            'can_upload', 'can_delete', 'can_modify_privacy', 'can_manage_users'
        ]

        for field in allowed_fields:
            if field in data:
                if field == 'role_name':
                    # 检查新角色名是否已被其他角色使用
                    cursor.execute("SELECT role_id FROM user_roles WHERE role_name = ? AND role_id != ?",
                                  (data[field], role_id))
                    if cursor.fetchone():
                        conn.close()
                        return jsonify({
                            'code': -1,
                            'message': '角色名已被使用'
                        }), 400
                update_fields.append(f"{field} = ?")
                params.append(data[field])

        if not update_fields:
            conn.close()
            return jsonify({
                'code': -1,
                'message': '没有要更新的字段'
            }), 400

        # 执行更新
        params.append(role_id)
        update_sql = f"UPDATE user_roles SET {', '.join(update_fields)} WHERE role_id = ?"
        cursor.execute(update_sql, params)
        conn.commit()

        # 获取更新后的角色信息
        cursor.execute("""
            SELECT
                role_id, role_name, role_description, privacy_level_access,
                can_upload, can_delete, can_modify_privacy, can_manage_users,
                created_at
            FROM user_roles
            WHERE role_id = ?
        """, (role_id,))

        role = dict(cursor.fetchone())
        conn.close()

        return jsonify({
            'code': 0,
            'message': '角色更新成功',
            'data': role
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'更新角色失败: {str(e)}'
        }), 500


@user_management_bp.route('/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    """删除角色"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查角色是否存在
        cursor.execute("SELECT role_id FROM user_roles WHERE role_id = ?", (role_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'code': -1,
                'message': '角色不存在'
            }), 404

        # 检查是否有用户正在使用该角色
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role_id = ?", (role_id,))
        count = cursor.fetchone()['count']
        if count > 0:
            conn.close()
            return jsonify({
                'code': -1,
                'message': f'无法删除角色,还有 {count} 个用户正在使用该角色'
            }), 400

        # 删除角色
        cursor.execute("DELETE FROM user_roles WHERE role_id = ?", (role_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'code': 0,
            'message': '角色删除成功'
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'删除角色失败: {str(e)}'
        }), 500


# ==================== 统计 API ====================

@user_management_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取用户管理统计信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 总用户数
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']

        # 活跃用户数
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()['total']

        # 角色统计
        cursor.execute("""
            SELECT
                r.role_name,
                COUNT(u.user_id) as user_count
            FROM user_roles r
            LEFT JOIN users u ON r.role_id = u.role_id
            GROUP BY r.role_id, r.role_name
        """)
        role_stats = [dict(row) for row in cursor.fetchall()]

        # 最近登录用户
        cursor.execute("""
            SELECT
                u.username,
                u.last_login,
                r.role_name
            FROM users u
            LEFT JOIN user_roles r ON u.role_id = r.role_id
            WHERE u.last_login IS NOT NULL
            ORDER BY u.last_login DESC
            LIMIT 5
        """)
        recent_logins = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'role_stats': role_stats,
                'recent_logins': recent_logins
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500
