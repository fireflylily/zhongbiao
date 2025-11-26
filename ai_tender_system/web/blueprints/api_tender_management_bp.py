#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书管理API蓝图
提供标书管理列表、统计信息查询、项目删除等API
"""

import sys
import json
import traceback
from pathlib import Path
from flask import Blueprint, request, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from common.database import get_knowledge_base_db

# 创建蓝图
api_tender_management_bp = Blueprint('api_tender_management', __name__, url_prefix='/api/tender-management')

# 日志记录器
logger = get_module_logger("web.api_tender_management")


@api_tender_management_bp.route('/list', methods=['GET'])
def get_tender_management_list():
    """
    获取标书管理列表 (带分页、搜索、状态过滤)

    Query Parameters:
        page: 页码 (默认1)
        page_size: 每页数量 (默认20)
        search: 搜索关键词 (可选)
        status: 状态过滤 (all/in_progress/completed)

    Returns:
        {
            "success": true,
            "data": {
                "projects": [...],
                "page": 1,
                "page_size": 20,
                "total": 100,
                "total_pages": 5
            }
        }
    """
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search_keyword = request.args.get('search', '')
        status_filter = request.args.get('status', '')  # all, in_progress, completed

        db = get_knowledge_base_db()

        # 构建查询条件
        where_conditions = []
        params = []

        # 搜索条件
        if search_keyword:
            where_conditions.append("""
                (p.project_name LIKE ? OR c.company_name LIKE ?)
            """)
            params.extend([f'%{search_keyword}%', f'%{search_keyword}%'])

        # 状态筛选
        if status_filter == 'in_progress':
            where_conditions.append("t.overall_status IN ('pending', 'running')")
        elif status_filter == 'completed':
            where_conditions.append("t.overall_status = 'completed'")

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # 查询总数
        count_query = f"""
            SELECT COUNT(DISTINCT p.project_id) as total
            FROM tender_projects p
            LEFT JOIN companies c ON p.company_id = c.company_id
            LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
            LEFT JOIN (SELECT project_id, step1_status, step2_status, step3_status, step1_data, hitl_overall_status as overall_status, hitl_current_step as current_step FROM tender_projects) h ON h.project_id = p.project_id
            WHERE {where_clause}
        """

        total_result = db.execute_query(count_query, params, fetch_one=True)
        total_count = total_result['total'] if total_result else 0

        # 计算分页
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # 查询列表数据
        list_query = f"""
            SELECT
                p.project_id,
                p.project_name,
                p.project_number,
                p.created_at as project_created_at,
                p.updated_at as project_updated_at,
                c.company_name,
                p.authorized_person_name as authorized_person,
                p.authorized_person_id,
                c.company_id,

                -- 处理任务信息
                t.task_id,
                t.overall_status as task_status,
                t.current_step,
                t.progress_percentage,
                t.total_chunks,
                t.valuable_chunks,
                t.total_requirements,

                -- HITL任务信息
                h.step1_status,
                h.step1_data,
                h.step2_status,
                h.step3_status,
                h.current_step as hitl_current_step,
                h.overall_status as hitl_status

            FROM tender_projects p
            LEFT JOIN companies c ON p.company_id = c.company_id
            LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
            LEFT JOIN (SELECT project_id, step1_status, step2_status, step3_status, step1_data, hitl_overall_status as overall_status, hitl_current_step as current_step FROM tender_projects) h ON h.project_id = p.project_id
            WHERE {where_clause}
            ORDER BY p.updated_at DESC, p.created_at DESC
            LIMIT ? OFFSET ?
        """

        params.extend([page_size, offset])
        results = db.execute_query(list_query, params)

        # 处理结果，计算各阶段完成情况
        projects = []
        for row in results:
            # 解析step1_data来获取文件信息
            step1_data = {}
            if row['step1_data']:
                try:
                    step1_data = json.loads(row['step1_data'])
                except json.JSONDecodeError:
                    pass

            # 计算商务应答完成情况
            business_response_status = '未开始'
            business_response_progress = 0
            if step1_data.get('business_response_file'):  # 检查商务应答文件
                business_response_status = '已完成'
                business_response_progress = 100
            elif row['step1_status'] == 'in_progress':
                business_response_status = '进行中'
                business_response_progress = 50

            # 计算技术点对点应答完成情况
            tech_response_status = '未开始'
            tech_response_progress = 0
            if step1_data.get('technical_point_to_point_file'):  # 检查点对点应答文件
                tech_response_status = '已完成'
                tech_response_progress = 100
            elif row['step2_status'] == 'in_progress':
                tech_response_status = '进行中'
                tech_response_progress = 50

            # 计算技术方案情况
            tech_proposal_status = '未开始'
            tech_proposal_progress = 0
            if step1_data.get('technical_proposal_file'):
                tech_proposal_status = '已完成'
                tech_proposal_progress = 100
            elif row['hitl_current_step'] and row['hitl_current_step'] >= 2:
                tech_proposal_status = '进行中'
                tech_proposal_progress = 50

            # 🆕 检查最后融合情况 - 从 tender_processing_tasks 的 options 字段中检查是否有 merged_document_path
            fusion_status = '未开始'
            fusion_progress = 0
            final_merge_file = None

            # 查询该项目的处理任务options，检查是否已生成最终融合文档
            task_data = db.execute_query(
                "SELECT options FROM tender_processing_tasks WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
                (row['project_id'],),
                fetch_one=True
            )

            if task_data and task_data.get('options'):
                try:
                    task_options = json.loads(task_data['options'])
                    if task_options.get('merged_document_path'):
                        # 有最终融合文档路径，说明已完成融合
                        fusion_status = '已完成'
                        fusion_progress = 100
                        final_merge_file = {
                            'file_path': task_options.get('merged_document_path'),
                            'file_size': task_options.get('file_size'),
                            'stats': task_options.get('stats')
                        }
                except (json.JSONDecodeError, TypeError):
                    pass

            # 提取文件路径信息
            business_response_file = step1_data.get('business_response_file', {})
            tech_point_to_point_file = step1_data.get('technical_point_to_point_file', {})
            tech_proposal_file = step1_data.get('technical_proposal_file', {})

            projects.append({
                'project_id': row['project_id'],
                'project_name': row['project_name'] or '未命名项目',
                'project_number': row['project_number'],
                'company_id': row['company_id'],
                'company_name': row['company_name'] or '未设置',
                'authorized_person': row['authorized_person'] or '未设置',
                'authorized_person_id': row['authorized_person_id'],
                'business_response': {
                    'status': business_response_status,
                    'progress': business_response_progress,
                    'file_name': business_response_file.get('file_name'),
                    'file_path': business_response_file.get('file_path'),
                    'file_url': business_response_file.get('file_url')
                },
                'tech_response': {
                    'status': tech_response_status,
                    'progress': tech_response_progress,
                    'file_name': tech_point_to_point_file.get('file_name'),
                    'file_path': tech_point_to_point_file.get('file_path'),
                    'file_url': tech_point_to_point_file.get('file_url')
                },
                'tech_proposal': {
                    'status': tech_proposal_status,
                    'progress': tech_proposal_progress,
                    'file_name': tech_proposal_file.get('file_name'),
                    'file_path': tech_proposal_file.get('file_path'),
                    'file_url': tech_proposal_file.get('file_url')
                },
                'fusion': {
                    'status': fusion_status,
                    'progress': round(fusion_progress, 1),
                    'file_path': final_merge_file.get('file_path') if final_merge_file else None,
                    'file_size': final_merge_file.get('file_size') if final_merge_file else None,
                    'stats': final_merge_file.get('stats') if final_merge_file else None
                },
                'created_at': row['project_created_at'],
                'updated_at': row['project_updated_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'projects': projects,
                'page': page,
                'page_size': page_size,
                'total': total_count,
                'total_pages': total_pages
            }
        })

    except Exception as e:
        logger.error(f"获取标书管理列表失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_management_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_statistics():
    """
    获取工作台全局统计数据

    Returns:
        {
            "success": true,
            "data": {
                "totalProjects": 156,
                "inProgressProjects": 23,
                "wonThisMonth": 8,
                "pendingTasks": 12
            }
        }
    """
    try:
        db = get_knowledge_base_db()

        # 1. 总项目数
        total_projects_query = """
            SELECT COUNT(*) as count FROM tender_projects
        """
        total_result = db.execute_query(total_projects_query, fetch_one=True)
        total_projects = total_result['count'] if total_result else 0

        # 2. 进行中的项目数 (状态为 pending 或 running)
        in_progress_query = """
            SELECT COUNT(DISTINCT p.project_id) as count
            FROM tender_projects p
            LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
            WHERE t.overall_status IN ('pending', 'running')
               OR p.hitl_overall_status IN ('pending', 'in_progress')
        """
        in_progress_result = db.execute_query(in_progress_query, fetch_one=True)
        in_progress_projects = in_progress_result['count'] if in_progress_result else 0

        # 3. 本月中标数 (暂时用已完成项目数代替，后续可以添加中标状态字段)
        from datetime import datetime
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

        won_this_month_query = """
            SELECT COUNT(*) as count
            FROM tender_projects
            WHERE status = 'won'
              AND updated_at >= ?
        """
        won_result = db.execute_query(won_this_month_query, (current_month_start,), fetch_one=True)
        won_this_month = won_result['count'] if won_result else 0

        # 4. 待处理任务数 (需要人工干预的HITL任务)
        pending_tasks_query = """
            SELECT COUNT(*) as count
            FROM tender_projects
            WHERE hitl_overall_status = 'pending'
               OR (hitl_overall_status = 'in_progress'
                   AND (step1_status = 'pending' OR step2_status = 'pending' OR step3_status = 'pending'))
        """
        pending_result = db.execute_query(pending_tasks_query, fetch_one=True)
        pending_tasks = pending_result['count'] if pending_result else 0

        return jsonify({
            'success': True,
            'data': {
                'totalProjects': total_projects,
                'inProgressProjects': in_progress_projects,
                'wonThisMonth': won_this_month,
                'pendingTasks': pending_tasks
            }
        })

    except Exception as e:
        logger.error(f"获取工作台统计数据失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_management_bp.route('/stats/<int:project_id>', methods=['GET'])
def get_tender_project_stats(project_id):
    """
    获取项目详细统计信息

    Args:
        project_id: 项目ID

    Returns:
        {
            "success": true,
            "stats": {
                "project_info": {...},
                "processing_stats": {...},
                "files": {...},
                "status": {...}
            }
        }
    """
    try:
        db = get_knowledge_base_db()

        # 获取项目基本信息和处理统计
        stats_query = """
            SELECT
                p.*,
                c.company_name,
                t.overall_status,
                t.total_chunks,
                t.valuable_chunks,
                t.total_requirements,
                h.step1_status,
                h.step2_status,
                h.step3_status,
                h.step1_data
            FROM tender_projects p
            LEFT JOIN companies c ON p.company_id = c.company_id
            LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
            LEFT JOIN (SELECT project_id, step1_status, step2_status, step3_status, step1_data, hitl_overall_status as overall_status, hitl_current_step as current_step FROM tender_projects) h ON h.project_id = p.project_id
            WHERE p.project_id = ?
        """

        result = db.execute_query(stats_query, (project_id,), fetch_one=True)

        if not result:
            return jsonify({'success': False, 'error': '项目不存在'}), 404

        # 解析step1_data
        step1_data = {}
        if result['step1_data']:
            try:
                step1_data = json.loads(result['step1_data'])
            except json.JSONDecodeError:
                pass

        stats = {
            'project_info': {
                'project_id': result['project_id'],
                'project_name': result['project_name'],
                'company_name': result['company_name']
            },
            'processing_stats': {
                'total_chunks': result['total_chunks'] or 0,
                'valuable_chunks': result['valuable_chunks'] or 0,
                'total_requirements': result['total_requirements'] or 0
            },
            'files': {
                'business_response': step1_data.get('technical_point_to_point_file'),
                'tech_proposal': step1_data.get('technical_proposal_file')
            },
            'status': {
                'overall': result['overall_status'],
                'step1': result['step1_status'],
                'step2': result['step2_status'],
                'step3': result['step3_status']
            }
        }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"获取项目统计信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_management_bp.route('/project/<int:project_id>', methods=['DELETE'])
def delete_tender_project(project_id):
    """
    删除项目及其关联数据 (级联删除)

    Args:
        project_id: 项目ID

    Returns:
        {
            "success": true,
            "message": "项目 'xxx' 已成功删除",
            "deleted_counts": {...},
            "project_id": 123
        }
    """
    try:
        db = get_knowledge_base_db()

        # 1. 检查项目是否存在
        project_check = db.execute_query("""
            SELECT project_id, project_name, tender_document_path
            FROM tender_projects
            WHERE project_id = ?
        """, (project_id,), fetch_one=True)

        if not project_check:
            return jsonify({'success': False, 'error': '项目不存在'}), 404

        logger.info(f"开始删除项目: project_id={project_id}, project_name={project_check['project_name']}")

        # 2. 获取关联的任务ID (用于级联删除)
        task_info = db.execute_query("""
            SELECT task_id FROM tender_processing_tasks
            WHERE project_id = ?
        """, (project_id,), fetch_one=True)

        task_id = task_info['task_id'] if task_info else None

        # 3. 删除关联数据 (按外键依赖顺序)
        deleted_counts = {}

        # 3.1 HITL数据现已合并到tender_projects表中，无需单独删除
        #     将在删除项目时一并删除
        deleted_counts['hitl_tasks'] = 0  # HITL数据已合并到项目表

        if task_id:

            # 删除处理日志
            result = db.execute_query("""
                DELETE FROM tender_processing_logs WHERE task_id = ?
            """, (task_id,))
            deleted_counts['processing_logs'] = result if result else 0

            # 删除要求提取结果
            result = db.execute_query("""
                DELETE FROM tender_requirements WHERE chunk_id IN (
                    SELECT chunk_id FROM tender_chunks WHERE project_id = ?
                )
            """, (project_id,))
            deleted_counts['requirements'] = result if result else 0

            # 删除文档分块
            result = db.execute_query("""
                DELETE FROM tender_chunks WHERE project_id = ?
            """, (project_id,))
            deleted_counts['chunks'] = result if result else 0

            # 删除处理任务
            result = db.execute_query("""
                DELETE FROM tender_processing_tasks WHERE task_id = ?
            """, (task_id,))
            deleted_counts['processing_tasks'] = result if result else 0

        # 3.2 删除项目本身
        result = db.execute_query("""
            DELETE FROM tender_projects WHERE project_id = ?
        """, (project_id,))
        deleted_counts['projects'] = result if result else 0

        # 4. 可选: 删除关联文件 (暂时不删除物理文件，避免误删)
        # if project_check['tender_document_path']:
        #     try:
        #         os.remove(project_check['tender_document_path'])
        #         logger.info(f"已删除标书文件: {project_check['tender_document_path']}")
        #     except Exception as e:
        #         logger.warning(f"删除标书文件失败: {e}")

        logger.info(f"项目删除完成: project_id={project_id}, 删除统计={deleted_counts}")

        return jsonify({
            'success': True,
            'message': f"项目 '{project_check['project_name']}' 已成功删除",
            'deleted_counts': deleted_counts,
            'project_id': project_id
        })

    except Exception as e:
        logger.error(f"删除项目失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'删除失败: {str(e)}'}), 500


__all__ = ['api_tender_management_bp']
