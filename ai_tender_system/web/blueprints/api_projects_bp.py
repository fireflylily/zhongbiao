#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标项目管理API蓝图
提供招标项目的CRUD操作

路由列表:
- GET    /api/tender-projects - 获取招标项目列表
- POST   /api/tender-projects - 创建招标项目
- GET    /api/tender-projects/<int:project_id> - 获取项目详情
- PUT    /api/tender-projects/<int:project_id> - 更新项目
- DELETE /api/tender-projects/<int:project_id> - 删除项目
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

# 导入权限检查
from web.middleware.permission import require_auth, get_current_user, is_admin, is_owner_or_admin

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
@require_auth
def get_tender_projects():
    """
    获取招标项目列表
    权限规则：
    - 所有用户（包括admin）：只能查看自己创建的项目
    """
    try:
        # 获取当前用户
        user = get_current_user()

        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        company_id = request.args.get('company_id')
        status = request.args.get('status')

        # 使用 LEFT JOIN 获取公司名称
        query = """
            SELECT
                p.*,
                c.company_name
            FROM tender_projects p
            LEFT JOIN companies c ON p.company_id = c.company_id
            WHERE 1=1
        """
        params = []

        # 权限过滤：所有用户（包括admin）只能看到自己创建的项目
        query += " AND p.created_by_user_id = ?"
        params.append(user['user_id'])

        if company_id:
            query += " AND p.company_id = ?"
            params.append(company_id)

        if status:
            query += " AND p.status = ?"
            params.append(status)

        # 计算总数
        count_query = query.replace("SELECT\n                p.*,\n                c.company_name", "SELECT COUNT(*) as total")
        count_result = kb_manager.db.execute_query(count_query, params, fetch_one=True)
        total = count_result['total'] if count_result else 0

        # 添加分页
        offset = (page - 1) * page_size
        query += f" ORDER BY p.created_at DESC LIMIT {page_size} OFFSET {offset}"

        projects = kb_manager.db.execute_query(query, params)

        # 字段映射：将 project_id 映射为 id（符合前端 Project 接口）
        if projects:
            import json
            for project in projects:
                if 'project_id' in project:
                    project['id'] = project['project_id']
                    del project['project_id']  # 删除重复字段，避免混淆

                # 解析 step1_data JSON 并提取文档状态信息
                step1_data_raw = project.get('step1_data')
                if step1_data_raw:
                    try:
                        step1_data = json.loads(step1_data_raw) if isinstance(step1_data_raw, str) else step1_data_raw

                        # 提取文档状态信息作为顶层字段，供前端判断
                        if isinstance(step1_data, dict):
                            # 商务应答文件
                            if 'business_response_file' in step1_data:
                                project['business_response_file'] = step1_data['business_response_file']

                            # 技术方案文件
                            if 'technical_proposal_file' in step1_data:
                                project['tech_proposal_file'] = step1_data['technical_proposal_file']

                            # 点对点应答文件
                            if 'technical_point_to_point_file' in step1_data:
                                project['point_to_point_file'] = step1_data['technical_point_to_point_file']
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"解析项目 {project.get('project_id')} 的 step1_data 失败: {e}")

                # 🆕 检查最终融合文档 - 从 tender_processing_tasks 的 options 字段中查询
                try:
                    task_data = kb_manager.db.execute_query(
                        "SELECT options FROM tender_processing_tasks WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
                        (project.get('id'),),  # 使用映射后的id字段
                        fetch_one=True
                    )

                    if task_data and task_data.get('options'):
                        task_options = json.loads(task_data['options'])
                        if task_options.get('merged_document_path'):
                            # 找到最终融合文档
                            project['final_merge_file'] = {
                                'file_path': task_options.get('merged_document_path'),
                                'file_size': task_options.get('file_size'),
                                'stats': task_options.get('stats')
                            }
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"检查项目 {project.get('id')} 的最终融合文档失败: {e}")

        # 返回符合前端期望的格式
        return jsonify({
            'success': True,
            'data': {
                'items': projects or [],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
        })
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {
                'items': [],
                'pagination': {
                    'page': 1,
                    'page_size': 20,
                    'total': 0,
                    'total_pages': 0
                }
            }
        })


@api_projects_bp.route('/tender-projects', methods=['POST'])
@require_auth
def create_tender_project():
    """
    创建新招标项目
    权限规则：所有登录用户都可以创建项目
    """
    try:
        # 获取当前用户
        user = get_current_user()
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
                status, created_by, created_by_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            user['username'],  # created_by
            user['user_id']    # created_by_user_id - 记录创建者ID
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


def _build_chapter_tree(chapters_flat):
    """
    构建章节树结构（从扁平列表）

    Args:
        chapters_flat: 扁平的章节列表，按para_start_idx排序

    Returns:
        章节树（层级结构）
    """
    if not chapters_flat:
        return []

    # 构建chapter_id映射（使用chapter_id作为key，因为parent_chapter_id引用的是chapter_id）
    chapter_map = {}
    for ch in chapters_flat:
        chapter_map[ch['chapter_id']] = ch
        ch['children'] = []  # 初始化children字段

    # 构建树结构
    root_chapters = []

    for ch in chapters_flat:
        parent_id = ch.get('parent_chapter_id')
        if parent_id and parent_id in chapter_map:
            # 有父章节，添加到父章节的children中
            chapter_map[parent_id]['children'].append(ch)
        else:
            # 没有父章节，是根级章节
            root_chapters.append(ch)

    return root_chapters


@api_projects_bp.route('/tender-projects/<int:project_id>', methods=['GET'])
@require_auth
def get_tender_project(project_id):
    """
    获取单个项目详情
    权限规则：只有创建者可以查看
    """
    try:
        # 获取当前用户
        user = get_current_user()
        # 查询项目数据（HITL数据已合并到项目表）
        query = """
            SELECT
                p.*,
                c.company_name
            FROM tender_projects p
            LEFT JOIN companies c ON p.company_id = c.company_id
            WHERE p.project_id = ?
        """
        projects = kb_manager.db.execute_query(query, [project_id])

        if projects and len(projects) > 0:
            project_data = projects[0]

            # 权限检查：只有创建者可以查看
            if user['user_id'] != project_data.get('created_by_user_id'):
                return jsonify({
                    'success': False,
                    'message': '您没有权限查看此项目'
                }), 403

            # 解析 JSON 字段（step1_data, step2_data, step3_data, qualifications_data, scoring_data）
            import json
            for field in ['step1_data', 'step2_data', 'step3_data', 'qualifications_data', 'scoring_data']:
                if project_data.get(field):
                    try:
                        project_data[field] = json.loads(project_data[field])
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，保持原值
                        pass

            # 确保step1_data至少是一个空字典（为后续章节数据提供容器）
            if not project_data.get('step1_data') or not isinstance(project_data.get('step1_data'), dict):
                project_data['step1_data'] = {}

            # 无条件加载章节数据（章节数据存储在独立的表中，不依赖step1_data）
            try:
                logger.info(f"🔍 开始为项目 {project_id} 加载章节数据...")
                # 从tender_document_chapters表查询章节
                chapters_query = """
                    SELECT
                        chapter_id,
                        chapter_node_id,
                        level,
                        title,
                        para_start_idx,
                        para_end_idx,
                        word_count,
                        preview_text,
                        is_selected,
                        auto_selected,
                        skip_recommended,
                        parent_chapter_id
                    FROM tender_document_chapters
                    WHERE project_id = ?
                    ORDER BY para_start_idx ASC
                """
                chapters_raw = kb_manager.db.execute_query(chapters_query, [project_id])
                logger.info(f"🔍 数据库返回 {len(chapters_raw) if chapters_raw else 0} 条章节记录")

                if chapters_raw:
                    # 转换为前端期望的格式
                    chapters_flat = []
                    for ch in chapters_raw:
                        chapter_dict = {
                            'id': ch['chapter_node_id'],
                            'chapter_id': ch['chapter_id'],
                            'level': ch['level'],
                            'title': ch['title'],
                            'para_start_idx': ch['para_start_idx'],
                            'para_end_idx': ch['para_end_idx'],
                            'word_count': ch['word_count'] or 0,
                            'preview_text': ch.get('preview_text', ''),
                            'auto_selected': bool(ch.get('auto_selected', 0)),
                            'skip_recommended': bool(ch.get('skip_recommended', 0)),
                            'parent_chapter_id': ch.get('parent_chapter_id'),
                            'chapter_node_id': ch['chapter_node_id']
                        }
                        chapters_flat.append(chapter_dict)

                    # 构建章节树
                    chapter_tree = _build_chapter_tree(chapters_flat)

                    # 将章节数据添加到step1_data
                    project_data['step1_data']['chapters'] = chapter_tree

                    logger.info(f"为项目 {project_id} 加载了 {len(chapters_flat)} 个章节")
            except Exception as e:
                logger.error(f"加载章节数据失败: {e}")
                # 不中断流程，继续返回项目数据

            # 字段映射：将 project_id 映射为 id（与列表API保持一致）
            if 'project_id' in project_data:
                project_data['id'] = project_data['project_id']
                del project_data['project_id']  # 删除重复字段，避免混淆

            return jsonify({
                'success': True,
                'data': project_data
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
@require_auth
def update_tender_project(project_id):
    """
    更新招标项目
    权限规则：只有创建者可以更新
    """
    try:
        # 获取当前用户
        user = get_current_user()

        # 检查项目是否存在并获取创建者
        check_query = "SELECT created_by_user_id FROM tender_projects WHERE project_id = ?"
        project = kb_manager.db.execute_query(check_query, [project_id], fetch_one=True)

        if not project:
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404

        # 权限检查：只有创建者可以更新
        if user['user_id'] != project.get('created_by_user_id'):
            return jsonify({
                'success': False,
                'message': '您没有权限修改此项目'
            }), 403
        import json
        data = request.get_json()

        # 【新增】检查唯一性约束：如果更新了 company_id, project_name, project_number
        # 确保更新后的组合不与其他项目（不包括当前项目）重复
        if any(key in data for key in ['company_id', 'project_name', 'project_number']):
            # 获取当前项目的信息
            current_query = "SELECT company_id, project_name, project_number FROM tender_projects WHERE project_id = ?"
            current = kb_manager.db.execute_query(current_query, [project_id], fetch_one=True)

            if current:
                # 确定更新后的值（使用请求中的新值或保持原值）
                check_company_id = data.get('company_id', current['company_id'])
                check_project_name = data.get('project_name', current['project_name'])
                check_project_number = data.get('project_number', current['project_number'])

                # 检查是否与其他项目冲突（排除当前项目本身）
                check_query = """
                    SELECT project_id, project_name FROM tender_projects
                    WHERE company_id = ?
                      AND project_name = ?
                      AND project_number = ?
                      AND project_id != ?
                """
                conflict = kb_manager.db.execute_query(
                    check_query,
                    [check_company_id, check_project_name, check_project_number, project_id],
                    fetch_one=True
                )

                if conflict:
                    logger.warning(f"项目更新失败：与项目ID {conflict['project_id']} 重复")
                    return jsonify({
                        'success': False,
                        'message': f'项目名称"{check_project_name}"和编号"{check_project_number}"的组合已被使用，请使用不同的名称或编号',
                        'code': 200,
                        'details': {
                            'conflict_project_id': conflict['project_id'],
                            'conflict_project_name': conflict['project_name']
                        }
                    })

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
            'technical_data': 'technical_data',
            # 保留的新增字段
            'budget_amount': 'budget_amount',
            'business_contact_name': 'business_contact_name',
            'business_contact_phone': 'business_contact_phone',
            # 联系人信息字段
            'tenderer_contact_person': 'tenderer_contact_person',
            'tenderer_contact_method': 'tenderer_contact_method',
            'agency_contact_person': 'agency_contact_person',
            'agency_contact_method': 'agency_contact_method'
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
        # 检查是否是UNIQUE约束错误
        error_msg = str(e)
        if 'UNIQUE constraint failed' in error_msg:
            return jsonify({
                'success': False,
                'message': '项目名称和编号的组合已被使用，请使用不同的名称或编号',
                'code': 200
            })
        return jsonify({
            'success': False,
            'message': str(e)
        })


@api_projects_bp.route('/tender-projects/<int:project_id>', methods=['DELETE'])
@require_auth
def delete_tender_project(project_id):
    """
    删除招标项目（级联删除相关数据）
    权限规则：只有创建者可以删除
    """
    try:
        import os

        # 获取当前用户
        user = get_current_user()

        # 1. 检查项目是否存在并获取创建者
        check_query = "SELECT project_id, tender_document_path, created_by_user_id FROM tender_projects WHERE project_id = ?"
        project = kb_manager.db.execute_query(check_query, [project_id], fetch_one=True)

        if not project:
            return jsonify({
                'success': False,
                'message': f'项目 ID {project_id} 不存在'
            }), 404

        # 权限检查：只有创建者可以删除
        if user['user_id'] != project.get('created_by_user_id'):
            return jsonify({
                'success': False,
                'message': '您没有权限删除此项目'
            }), 403

        # 2. HITL数据现已合并到tender_projects表中，无需单独删除
        #    将在删除项目时一并删除

        # 3. 删除相关的文件存储记录（从 file_storage 表）
        try:
            # 查询所有相关文件
            file_query = "SELECT file_path FROM file_storage WHERE project_id = ?"
            files = kb_manager.db.execute_query(file_query, [project_id])

            if files:
                # 删除物理文件
                for file_record in files:
                    file_path = file_record.get('file_path')
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            logger.info(f"已删除文件: {file_path}")
                        except Exception as e:
                            logger.warning(f"删除文件失败: {file_path}, 错误: {e}")

                # 删除数据库记录
                delete_files_query = "DELETE FROM file_storage WHERE project_id = ?"
                kb_manager.db.execute_query(delete_files_query, [project_id])
                logger.info(f"已删除项目 {project_id} 的 {len(files)} 个文件记录")
        except Exception as e:
            logger.warning(f"删除文件存储记录失败: {e}")

        # 4. 删除招标文档文件（如果存在）
        tender_doc_path = project.get('tender_document_path')
        if tender_doc_path and os.path.exists(tender_doc_path):
            try:
                os.remove(tender_doc_path)
                logger.info(f"已删除招标文档: {tender_doc_path}")
            except Exception as e:
                logger.warning(f"删除招标文档失败: {tender_doc_path}, 错误: {e}")

        # 5. 删除项目本身
        delete_query = "DELETE FROM tender_projects WHERE project_id = ?"
        kb_manager.db.execute_query(delete_query, [project_id])

        logger.info(f"项目 {project_id} 及其所有相关数据已成功删除")

        return jsonify({
            'success': True,
            'message': f'项目 {project_id} 已成功删除'
        })

    except Exception as e:
        logger.error(f"删除项目 {project_id} 失败: {e}")
        return jsonify({
            'success': False,
            'message': f'删除项目失败: {str(e)}'
        }), 500


__all__ = ['api_projects_bp']
