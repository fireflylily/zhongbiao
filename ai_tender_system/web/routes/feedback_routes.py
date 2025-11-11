#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户反馈API路由
提供用户反馈的创建、查询、更新等功能
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from common.database import get_knowledge_base_db

logger = get_module_logger("feedback_api")

# 创建Blueprint
feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')


@feedback_bp.route('/submit', methods=['POST'])
def submit_feedback():
    """
    提交用户反馈

    请求体：
    {
        "content": "用户反馈内容",
        "username": "用户名（可选）",
        "userId": 用户ID（可选）,
        "projectId": 项目ID（可选）,
        "projectName": "项目名称（可选）",
        "companyId": 公司ID（可选）,
        "companyName": "公司名称（可选）",
        "pageRoute": "页面路由（可选）",
        "pageTitle": "页面标题（可选）",
        "feedbackType": "反馈类型（bug/suggestion/general）",
        "priority": "优先级（low/medium/high）"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        # 必填字段
        content = data.get('content', '').strip()
        if not content:
            return jsonify({
                'success': False,
                'error': '反馈内容不能为空'
            }), 400

        # 可选字段
        username = data.get('username')
        user_id = data.get('userId')
        project_id = data.get('projectId')
        project_name = data.get('projectName')
        company_id = data.get('companyId')
        company_name = data.get('companyName')
        page_route = data.get('pageRoute')
        page_title = data.get('pageTitle')
        feedback_type = data.get('feedbackType', 'general')
        priority = data.get('priority', 'medium')

        # 验证枚举值
        valid_feedback_types = ['bug', 'suggestion', 'general']
        valid_priorities = ['low', 'medium', 'high']

        if feedback_type not in valid_feedback_types:
            feedback_type = 'general'

        if priority not in valid_priorities:
            priority = 'medium'

        # 插入数据库
        db = get_knowledge_base_db()

        insert_query = """
            INSERT INTO user_feedbacks (
                content, username, user_id, project_id, project_name,
                company_id, company_name, page_route, page_title,
                feedback_type, priority, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            content, username, user_id, project_id, project_name,
            company_id, company_name, page_route, page_title,
            feedback_type, priority, 'pending'
        )

        feedback_id = db.execute_query(insert_query, params)

        logger.info(f"用户反馈提交成功 - ID: {feedback_id}, 用户: {username}, 类型: {feedback_type}")

        return jsonify({
            'success': True,
            'feedbackId': feedback_id,
            'message': '反馈提交成功，感谢您的宝贵意见！'
        }), 201

    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'提交失败: {str(e)}'
        }), 500


@feedback_bp.route('/list', methods=['GET'])
def list_feedbacks():
    """
    获取反馈列表

    查询参数：
    - page: 页码（默认1）
    - pageSize: 每页数量（默认20）
    - status: 状态筛选（pending/processing/resolved/closed）
    - feedbackType: 类型筛选（bug/suggestion/general）
    - priority: 优先级筛选（low/medium/high）
    - username: 用户名筛选
    - projectId: 项目ID筛选
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        status = request.args.get('status')
        feedback_type = request.args.get('feedbackType')
        priority = request.args.get('priority')
        username = request.args.get('username')
        project_id = request.args.get('projectId', type=int)

        # 构建查询条件
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if feedback_type:
            conditions.append("feedback_type = ?")
            params.append(feedback_type)

        if priority:
            conditions.append("priority = ?")
            params.append(priority)

        if username:
            conditions.append("username = ?")
            params.append(username)

        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # 查询总数
        db = get_knowledge_base_db()
        count_query = f"SELECT COUNT(*) as total FROM user_feedbacks {where_clause}"
        count_result = db.execute_query(count_query, tuple(params), fetch_one=True)
        total = count_result['total']

        # 查询数据
        offset = (page - 1) * page_size
        data_query = f"""
            SELECT
                id, content, username, user_id, project_id, project_name,
                company_id, company_name, page_route, page_title,
                feedback_type, priority, status, assigned_to, resolution,
                created_at, updated_at, resolved_at
            FROM user_feedbacks
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """

        data_params = params + [page_size, offset]
        feedbacks = db.execute_query(data_query, tuple(data_params))

        return jsonify({
            'success': True,
            'data': feedbacks,
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'total': total,
                'totalPages': (total + page_size - 1) // page_size
            }
        }), 200

    except Exception as e:
        logger.error(f"获取反馈列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'获取失败: {str(e)}'
        }), 500


@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    """获取单个反馈详情"""
    try:
        db = get_knowledge_base_db()

        query = """
            SELECT
                id, content, username, user_id, project_id, project_name,
                company_id, company_name, page_route, page_title,
                feedback_type, priority, status, assigned_to, resolution,
                created_at, updated_at, resolved_at
            FROM user_feedbacks
            WHERE id = ?
        """

        feedback = db.execute_query(query, (feedback_id,), fetch_one=True)

        if not feedback:
            return jsonify({
                'success': False,
                'error': '反馈不存在'
            }), 404

        return jsonify({
            'success': True,
            'data': feedback
        }), 200

    except Exception as e:
        logger.error(f"获取反馈详情失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'获取失败: {str(e)}'
        }), 500


@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
def update_feedback(feedback_id):
    """
    更新反馈（管理员功能）

    请求体：
    {
        "status": "处理状态",
        "priority": "优先级",
        "assignedTo": "负责人",
        "resolution": "处理结果"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        # 构建更新语句
        update_fields = []
        params = []

        if 'status' in data:
            update_fields.append("status = ?")
            params.append(data['status'])

            # 如果状态变为resolved，记录解决时间
            if data['status'] == 'resolved':
                update_fields.append("resolved_at = ?")
                params.append(datetime.now().isoformat())

        if 'priority' in data:
            update_fields.append("priority = ?")
            params.append(data['priority'])

        if 'assignedTo' in data:
            update_fields.append("assigned_to = ?")
            params.append(data['assignedTo'])

        if 'resolution' in data:
            update_fields.append("resolution = ?")
            params.append(data['resolution'])

        if not update_fields:
            return jsonify({
                'success': False,
                'error': '没有可更新的字段'
            }), 400

        # 执行更新
        db = get_knowledge_base_db()
        params.append(feedback_id)

        update_query = f"""
            UPDATE user_feedbacks
            SET {', '.join(update_fields)}
            WHERE id = ?
        """

        db.execute_query(update_query, tuple(params))

        logger.info(f"反馈更新成功 - ID: {feedback_id}")

        return jsonify({
            'success': True,
            'message': '更新成功'
        }), 200

    except Exception as e:
        logger.error(f"更新反馈失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500


@feedback_bp.route('/stats', methods=['GET'])
def get_feedback_stats():
    """获取反馈统计信息"""
    try:
        db = get_knowledge_base_db()

        # 按状态统计
        status_stats_query = """
            SELECT status, COUNT(*) as count
            FROM user_feedbacks
            GROUP BY status
        """
        status_stats = db.execute_query(status_stats_query, fetch_all=True)

        # 按类型统计
        type_stats_query = """
            SELECT feedback_type, COUNT(*) as count
            FROM user_feedbacks
            GROUP BY feedback_type
        """
        type_stats = db.execute_query(type_stats_query, fetch_all=True)

        # 按优先级统计
        priority_stats_query = """
            SELECT priority, COUNT(*) as count
            FROM user_feedbacks
            GROUP BY priority
        """
        priority_stats = db.execute_query(priority_stats_query, fetch_all=True)

        # 总数
        total_query = "SELECT COUNT(*) as total FROM user_feedbacks"
        total_result = db.execute_query(total_query, fetch_one=True)

        return jsonify({
            'success': True,
            'stats': {
                'total': total_result['total'],
                'byStatus': {item['status']: item['count'] for item in status_stats},
                'byType': {item['feedback_type']: item['count'] for item in type_stats},
                'byPriority': {item['priority']: item['count'] for item in priority_stats}
            }
        }), 200

    except Exception as e:
        logger.error(f"获取反馈统计失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'获取失败: {str(e)}'
        }), 500


def get_blueprint():
    """获取Blueprint对象"""
    return feedback_bp
