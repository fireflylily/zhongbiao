#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标项目管理API蓝图
提供招标项目的CRUD操作

路由列表:
- GET  /api/tender-projects - 获取招标项目列表
- POST /api/tender-projects - 创建招标项目
- GET  /api/tender-projects/<int:project_id> - 获取项目详情
- PUT  /api/tender-projects/<int:project_id> - 更新项目
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入共享实例
from web.shared.instances import get_kb_manager

# 导入公共组件
from common import get_module_logger

# 创建蓝图
api_projects_bp = Blueprint('api_projects', __name__, url_prefix='/api')

# 获取日志器
logger = get_module_logger("api_projects_bp")

# 获取知识库管理器
kb_manager = get_kb_manager()


# ===================
# 招标项目管理API
# ===================

@api_projects_bp.route('/tender-projects', methods=['GET'])
def get_tender_projects():
    """获取招标项目列表"""
    try:
        company_id = request.args.get('company_id')
        status = request.args.get('status')

        query = "SELECT * FROM tender_projects WHERE 1=1"
        params = []

        if company_id:
            query += " AND company_id = ?"
            params.append(company_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT 100"

        projects = kb_manager.db.execute_query(query, params)

        return jsonify({
            'success': True,
            'data': projects or []
        })
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        })


@api_projects_bp.route('/tender-projects', methods=['POST'])
def create_tender_project():
    """创建新招标项目"""
    try:
        import json
        data = request.get_json()

        # 【新增】检查是否存在相同项目（防止重复创建）
        company_id = data.get('company_id')
        project_name = data.get('project_name')
        project_number = data.get('project_number')

        if company_id and project_name:
            check_query = """
                SELECT project_id FROM tender_projects
                WHERE company_id = ? AND project_name = ?
            """
            check_params = [company_id, project_name]

            if project_number:
                check_query += " AND project_number = ?"
                check_params.append(project_number)

            existing = kb_manager.db.execute_query(check_query, check_params, fetch_one=True)

            if existing:
                logger.warning(f"项目已存在，返回已有项目ID: {existing['project_id']}")
                return jsonify({
                    'success': True,
                    'project_id': existing['project_id'],
                    'message': '项目已存在',
                    'is_existing': True
                })

        # 序列化资质和评分数据为JSON
        qualifications_json = None
        scoring_json = None

        if data.get('qualifications_data'):
            qualifications_json = json.dumps(data.get('qualifications_data'), ensure_ascii=False)
        if data.get('scoring_data'):
            scoring_json = json.dumps(data.get('scoring_data'), ensure_ascii=False)

        query = """
            INSERT INTO tender_projects (
                project_name, project_number, tenderer, agency,
                bidding_method, bidding_location, bidding_time,
                tender_document_path, original_filename,
                company_id, qualifications_data, scoring_data,
                status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = [
            data.get('project_name'),
            data.get('project_number'),
            data.get('tenderer'),
            data.get('agency'),
            data.get('bidding_method'),
            data.get('bidding_location'),
            data.get('bidding_time'),
            data.get('tender_document_path'),
            data.get('original_filename'),
            data.get('company_id'),
            qualifications_json,
            scoring_json,
            'draft',
            'system'
        ]

        project_id = kb_manager.db.execute_query(query, params)

        logger.info(f"创建项目成功，ID: {project_id}")

        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': '项目创建成功'
        })
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })


@api_projects_bp.route('/tender-projects/<int:project_id>', methods=['GET'])
def get_tender_project(project_id):
    """获取单个项目详情"""
    try:
        query = "SELECT * FROM tender_projects WHERE project_id = ?"
        projects = kb_manager.db.execute_query(query, [project_id])

        if projects and len(projects) > 0:
            return jsonify({
                'success': True,
                'data': projects[0]
            })
        else:
            return jsonify({
                'success': False,
                'message': '项目不存在'
            })
    except Exception as e:
        logger.error(f"获取项目详情失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })


@api_projects_bp.route('/tender-projects/<int:project_id>', methods=['PUT'])
def update_tender_project(project_id):
    """更新招标项目（只更新提供的字段，避免覆盖未提供的字段）"""
    try:
        import json
        data = request.get_json()

        # 定义可更新的字段映射（数据库字段名 -> 请求字段名）
        field_mapping = {
            'project_name': 'project_name',
            'project_number': 'project_number',
            'tenderer': 'tenderer',
            'agency': 'agency',
            'bidding_method': 'bidding_method',
            'bidding_location': 'bidding_location',
            'bidding_time': 'bidding_time',
            'tender_document_path': 'tender_document_path',
            'original_filename': 'original_filename',
            'company_id': 'company_id',
            'winner_count': 'winner_count',
            'authorized_person_name': 'authorized_person_name',
            'authorized_person_id': 'authorized_person_id',
            'authorized_person_position': 'authorized_person_position',
            'status': 'status',
            'qualifications_data': 'qualifications_data',
            'scoring_data': 'scoring_data',
            'technical_data': 'technical_data'
        }

        # 构建动态更新语句
        update_fields = []
        params = []

        for db_field, request_field in field_mapping.items():
            if request_field in data:
                value = data[request_field]

                # 特殊处理：JSON字段需要序列化
                if request_field in ['qualifications_data', 'scoring_data', 'technical_data']:
                    if value is not None:
                        value = json.dumps(value, ensure_ascii=False)

                update_fields.append(f"{db_field} = ?")
                params.append(value)

        # 如果没有任何字段需要更新
        if not update_fields:
            logger.warning(f"更新项目 {project_id} 时未提供任何字段")
            return jsonify({
                'success': True,
                'project_id': project_id,
                'message': '未提供需要更新的字段'
            })

        # 添加 updated_at 字段
        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        # 构建完整的SQL语句
        query = f"""
            UPDATE tender_projects SET
                {', '.join(update_fields)}
            WHERE project_id = ?
        """
        params.append(project_id)

        logger.info(f"更新项目 {project_id}，字段: {list(data.keys())}")

        kb_manager.db.execute_query(query, params)

        logger.info(f"更新项目成功，ID: {project_id}")

        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': '项目更新成功'
        })
    except Exception as e:
        logger.error(f"更新项目失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })


__all__ = ['api_projects_bp']
