#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书智能处理API蓝图
提供标书处理流程的启动、继续、状态查询、数据导出等API
包含8个核心路由和2个同步路由
"""

import sys
import os
import json
import time
import asyncio
import threading
import traceback
import tempfile
from pathlib import Path
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from common.database import get_knowledge_base_db
from common.constants import (
    TASK_START_MAX_RETRIES, TASK_START_RETRY_INTERVAL,
    STEP_EXECUTION_MAX_RETRIES, STEP_EXECUTION_RETRY_INTERVAL,
    STEP_3
)

# 创建蓝图
api_tender_processing_bp = Blueprint('api_tender_processing', __name__, url_prefix='/api/tender-processing')

# 日志记录器
logger = get_module_logger("web.api_tender_processing")


@api_tender_processing_bp.route('/start', methods=['POST'])
def start_tender_processing():
    """
    启动标书智能处理流程

    Form Data:
        project_id: 项目ID
        filter_model: 筛选模型名称
        extract_model: 提取模型名称
        step: 执行步骤（默认1）
        file: 上传的标书文档文件

    Returns:
        {
            "success": true,
            "task_id": "...",
            "message": "处理任务已启动"
        }
    """
    try:
        # 获取表单数据
        project_id = request.form.get('project_id')
        filter_model = request.form.get('filter_model', 'gpt-4o-mini')
        extract_model = request.form.get('extract_model', 'yuanjing-deepseek-v3')
        step = int(request.form.get('step', 1))  # 默认只执行第1步（分块）

        if not project_id:
            return jsonify({'success': False, 'error': '缺少project_id参数'}), 400

        # 检查文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未上传文件'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': '文件名为空'}), 400

        # 保存文件到临时目录
        temp_dir = Path(tempfile.gettempdir()) / 'tender_processing'
        temp_dir.mkdir(exist_ok=True)

        file_ext = Path(file.filename).suffix
        temp_file = temp_dir / f"tender_{project_id}{file_ext}"
        file.save(str(temp_file))

        logger.info(f"文件已保存: {temp_file}")

        # 使用ParserManager解析文档
        from modules.document_parser.parser_manager import ParserManager

        async def parse_document():
            parser = ParserManager()
            result = await parser.parse_document(doc_id=int(project_id), file_path=str(temp_file))
            return result

        # 运行异步解析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        parse_result = loop.run_until_complete(parse_document())
        loop.close()

        if parse_result.status.value != 'completed':
            return jsonify({
                'success': False,
                'error': f'文档解析失败: {parse_result.error_message}'
            }), 500

        document_text = parse_result.content
        logger.info(f"启动标书智能处理 - 项目ID: {project_id}, 文档长度: {len(document_text)}")

        # 导入处理流程
        from modules.tender_processing.processing_pipeline import TenderProcessingPipeline

        # 创建流程实例（异步处理需要在后台线程中运行）
        result_holder = {'project_id': None, 'error': None}

        def run_pipeline():
            try:
                from web.shared.instances import set_pipeline_instance

                pipeline = TenderProcessingPipeline(
                    project_id=int(project_id),
                    document_text=document_text,
                    filter_model=filter_model,
                    extract_model=extract_model
                )
                result_holder['project_id'] = pipeline.project_id

                # 保存pipeline实例到全局存储（使用project_id作为key）
                set_pipeline_instance(pipeline.project_id, pipeline)

                # 运行指定步骤
                result = pipeline.run_step(step)
                result_holder['result'] = result

                logger.info(f"步骤 {step} 处理完成 - 项目ID: {pipeline.project_id}, 成功: {result['success']}")
            except Exception as e:
                logger.error(f"处理流程执行失败: {e}")
                result_holder['error'] = str(e)

        # 启动后台线程
        thread = threading.Thread(target=run_pipeline, daemon=True)
        thread.start()

        # 等待project_id确认
        for _ in range(TASK_START_MAX_RETRIES):
            if result_holder['project_id'] or result_holder['error']:
                break
            time.sleep(TASK_START_RETRY_INTERVAL)

        if result_holder['error']:
            return jsonify({'success': False, 'error': result_holder['error']}), 500

        if not result_holder['project_id']:
            return jsonify({'success': False, 'error': '任务启动超时'}), 500

        return jsonify({
            'success': True,
            'project_id': result_holder['project_id'],
            'message': '处理任务已启动，请使用project_id查询进度'
        })

    except Exception as e:
        logger.error(f"启动标书处理失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/continue/<int:project_id>', methods=['POST'])
def continue_tender_processing(project_id):
    """
    继续执行下一步骤

    Args:
        project_id: 项目ID

    Request Body:
        {
            "step": 2  # 要执行的步骤号
        }

    Returns:
        {
            "success": true,
            "project_id": 123,
            "result": {...},
            "message": "步骤处理完成"
        }
    """
    try:
        from web.shared.instances import get_pipeline_instance, remove_pipeline_instance

        # 获取参数
        data = request.get_json()
        step = data.get('step', 2)  # 默认执行第2步

        # 从全局存储中获取pipeline实例（使用project_id）
        pipeline = get_pipeline_instance(project_id)
        if pipeline is None:
            return jsonify({'success': False, 'error': f'找不到项目 {project_id} 的pipeline实例或已过期'}), 404

        # 在后台线程中执行步骤
        result_holder = {'result': None, 'error': None}

        def run_step():
            try:
                result = pipeline.run_step(step)
                result_holder['result'] = result
                logger.info(f"步骤 {step} 处理完成 - 项目ID: {project_id}, 成功: {result['success']}")
            except Exception as e:
                logger.error(f"步骤 {step} 执行失败: {e}")
                result_holder['error'] = str(e)

        # 启动后台线程
        thread = threading.Thread(target=run_step, daemon=True)
        thread.start()

        # 等待步骤完成
        for _ in range(STEP_EXECUTION_MAX_RETRIES):
            if result_holder['result'] or result_holder['error']:
                break
            time.sleep(STEP_EXECUTION_RETRY_INTERVAL)

        if result_holder['error']:
            return jsonify({'success': False, 'error': result_holder['error']}), 500

        if not result_holder['result']:
            # 步骤仍在执行中，返回处理中状态
            return jsonify({
                'success': True,
                'project_id': project_id,
                'message': f'步骤 {step} 正在处理中，请查询状态'
            })

        # 如果是最后一步，清理pipeline实例（线程安全）
        if step == STEP_3:
            remove_pipeline_instance(project_id)
            logger.info(f"项目 {project_id} 处理已完成，清理pipeline实例")

        return jsonify({
            'success': True,
            'project_id': project_id,
            'result': result_holder['result'],
            'message': f'步骤 {step} 处理完成'
        })

    except Exception as e:
        logger.error(f"继续处理失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/status/<int:project_id>', methods=['GET'])
def get_processing_status(project_id):
    """
    查询处理进度

    Args:
        project_id: 项目ID

    Returns:
        {
            "success": true,
            "task": {...},
            "logs": [...],
            "statistics": {...}
        }
    """
    try:
        db = get_knowledge_base_db()

        # 获取任务信息
        task = db.get_processing_task(project_id)

        if not task:
            return jsonify({'success': False, 'error': '任务不存在'}), 404

        # 获取处理日志
        logs = db.get_processing_logs(project_id)

        # 获取统计信息
        stats = db.get_processing_statistics(project_id)

        return jsonify({
            'success': True,
            'task': dict(task),
            'logs': [dict(log) for log in logs],
            'statistics': dict(stats) if stats else None
        })

    except Exception as e:
        logger.error(f"查询处理状态失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/chunks/<int:project_id>', methods=['GET'])
def get_tender_chunks(project_id):
    """
    获取文档分块列表

    Args:
        project_id: 项目ID

    Query Parameters:
        valuable_only: 是否只返回有价值的分块 (true/false)

    Returns:
        {
            "success": true,
            "chunks": [...],
            "total": 100
        }
    """
    try:
        valuable_only = request.args.get('valuable_only', 'false').lower() == 'true'

        db = get_knowledge_base_db()
        chunks = db.get_tender_chunks(project_id, valuable_only=valuable_only)

        # 解析metadata JSON
        for chunk in chunks:
            if chunk.get('metadata'):
                try:
                    chunk['metadata'] = json.loads(chunk['metadata'])
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"解析chunk metadata失败: {e}")
                    chunk['metadata'] = {}

        return jsonify({
            'success': True,
            'chunks': chunks,
            'total': len(chunks)
        })

    except Exception as e:
        logger.error(f"获取分块列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/requirements/<int:project_id>', methods=['GET'])
def get_tender_requirements(project_id):
    """
    获取提取的要求列表

    Args:
        project_id: 项目ID

    Query Parameters:
        constraint_type: 约束类型过滤 (可选)
        category: 分类过滤 (可选)

    Returns:
        {
            "success": true,
            "requirements": [...],
            "total": 50,
            "summary": {...},
            "has_extracted": true
        }
    """
    try:
        constraint_type = request.args.get('constraint_type')
        category = request.args.get('category')

        db = get_knowledge_base_db()
        requirements = db.get_tender_requirements(
            project_id=project_id,
            constraint_type=constraint_type,
            category=category
        )

        # 获取汇总统计
        summary = db.get_requirements_summary(project_id)

        return jsonify({
            'success': True,
            'requirements': requirements,
            'total': len(requirements),
            'summary': summary,
            'has_extracted': len(requirements) > 0
        })

    except Exception as e:
        logger.error(f"获取要求列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/analytics/<int:project_id>', methods=['GET'])
def get_processing_analytics(project_id):
    """
    获取处理统计分析

    Args:
        project_id: 项目ID

    Returns:
        {
            "success": true,
            "analytics": {
                "chunks": {...},
                "requirements": {...}
            }
        }
    """
    try:
        db = get_knowledge_base_db()

        # 获取分块统计
        all_chunks = db.get_tender_chunks(project_id)
        valuable_chunks = db.get_tender_chunks(project_id, valuable_only=True)

        # 获取要求统计
        requirements = db.get_tender_requirements(project_id)
        summary = db.get_requirements_summary(project_id)

        # 计算分块类型分布
        chunk_type_dist = {}
        for chunk in all_chunks:
            chunk_type = chunk.get('chunk_type', 'unknown')
            chunk_type_dist[chunk_type] = chunk_type_dist.get(chunk_type, 0) + 1

        # 计算筛选效果
        filter_rate = (len(all_chunks) - len(valuable_chunks)) / len(all_chunks) * 100 if all_chunks else 0

        analytics = {
            'chunks': {
                'total': len(all_chunks),
                'valuable': len(valuable_chunks),
                'filtered': len(all_chunks) - len(valuable_chunks),
                'filter_rate': round(filter_rate, 2),
                'type_distribution': chunk_type_dist
            },
            'requirements': {
                'total': len(requirements),
                'by_type': summary.get('by_type', {}),
                'by_category': summary.get('by_category', {})
            }
        }

        return jsonify({
            'success': True,
            'analytics': analytics
        })

    except Exception as e:
        logger.error(f"获取处理统计失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/export/<int:project_id>', methods=['GET'])
def export_requirements(project_id):
    """
    导出提取的要求为Excel

    Args:
        project_id: 项目ID

    Returns:
        Excel文件下载
    """
    try:
        import pandas as pd

        db = get_knowledge_base_db()
        requirements = db.get_tender_requirements(project_id)

        if not requirements:
            return jsonify({'success': False, 'error': '没有可导出的数据'}), 404

        # 转换为DataFrame
        df = pd.DataFrame(requirements)

        # 选择需要的列
        columns = [
            'requirement_id', 'constraint_type', 'category', 'subcategory',
            'detail', 'source_location', 'priority', 'extraction_confidence',
            'is_verified', 'extracted_at'
        ]
        df = df[[col for col in columns if col in df.columns]]

        # 重命名列（中文）
        df.columns = [
            '要求ID', '类型', '分类', '子分类', '详情', '来源',
            '优先级', '置信度', '已验证', '提取时间'
        ][:len(df.columns)]

        # 生成Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='投标要求', index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'项目{project_id}_投标要求.xlsx'
        )

    except ImportError:
        return jsonify({
            'success': False,
            'error': '缺少pandas或openpyxl库，请安装：pip install pandas openpyxl'
        }), 500
    except Exception as e:
        logger.error(f"导出要求失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_processing_bp.route('/sync-point-to-point/<int:project_id>', methods=['POST'])
def sync_point_to_point_to_hitl(project_id):
    """
    同步点对点应答文件到HITL投标项目

    Args:
        project_id: 项目ID

    Request Body:
        {
            "file_path": "/path/to/file.docx"
        }

    Returns:
        {
            "success": true,
            "message": "文件已成功同步",
            "file_path": "...",
            "filename": "...",
            "file_size": 12345
        }
    """
    try:
        import shutil

        data = request.get_json()
        source_file_path = data.get('file_path')

        if not source_file_path:
            return jsonify({
                'success': False,
                'error': '未提供文件路径'
            }), 400

        # 如果传入的是下载URL(以/api/downloads/或/downloads/开头),转换为实际文件路径
        if source_file_path.startswith('/api/downloads/') or source_file_path.startswith('/downloads/'):
            filename = source_file_path.replace('/api/downloads/', '').replace('/downloads/', '')
            # 使用URL解码处理中文文件名
            from urllib.parse import unquote
            filename = unquote(filename)
            source_file_path = os.path.join(project_root, 'data/outputs', filename)
            logger.info(f"从下载URL转换为文件路径: {source_file_path}")

        # 检查源文件是否存在
        if not os.path.exists(source_file_path):
            return jsonify({
                'success': False,
                'error': '源文件不存在'
            }), 404

        logger.info(f"同步点对点应答文件到HITL项目: project_id={project_id}, file_path={source_file_path}")

        # 获取数据库实例
        db = get_knowledge_base_db()

        # 查询任务信息
        task_data = db.execute_query("""
            SELECT step1_data FROM tender_projects
            WHERE project_id = ?
        """, (project_id,), fetch_one=True)

        if not task_data:
            return jsonify({
                'success': False,
                'error': '任务不存在'
            }), 404

        step1_data = json.loads(task_data['step1_data'])

        # 创建存储目录
        now = datetime.now()
        save_dir = os.path.join(
            project_root,
            'data/uploads/completed_response_files',
            str(now.year),
            f"{now.month:02d}",
            task_id
        )
        os.makedirs(save_dir, exist_ok=True)

        # 生成文件名
        source_filename = os.path.basename(source_file_path)
        # 从源文件名提取,如果包含时间戳则保留,否则添加时间戳
        if '_' in source_filename:
            base_name = source_filename.rsplit('.', 1)[0]
            filename = f"{base_name}_应答完成.docx"
        else:
            filename = f"点对点应答_{now.strftime('%Y%m%d_%H%M%S')}_应答完成.docx"

        # 复制文件到目标位置
        target_path = os.path.join(save_dir, filename)
        shutil.copy2(source_file_path, target_path)

        # 计算文件大小
        file_size = os.path.getsize(target_path)

        # 更新任务的step1_data - 使用独立字段存储点对点应答文件
        point_to_point_file_info = {
            "file_path": target_path,
            "filename": filename,
            "file_size": file_size,
            "saved_at": now.isoformat(),
            "source_file": source_file_path
        }
        step1_data['technical_point_to_point_file'] = point_to_point_file_info

        db.execute_query("""
            UPDATE tender_projects
            SET step1_data = ?
            WHERE project_id = ?
        """, (json.dumps(step1_data), project_id))

        logger.info(f"同步点对点应答文件到HITL项目: {project_id}, 文件: {filename} ({file_size} bytes)")

        return jsonify({
            'success': True,
            'message': '点对点应答文件已成功同步到投标项目',
            'file_path': target_path,
            'filename': filename,
            'file_size': file_size,
            'saved_at': point_to_point_file_info['saved_at']
        })

    except Exception as e:
        logger.error(f"同步点对点应答文件失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'同步失败: {str(e)}'
        }), 500


@api_tender_processing_bp.route('/sync-tech-proposal/<int:project_id>', methods=['POST'])
def sync_tech_proposal_to_hitl(project_id):
    """
    同步技术方案文件到HITL投标项目

    Args:
        project_id: 项目ID

    Request Body:
        {
            "file_path": "/path/to/file.docx",
            "output_files": {...}  # 可选，额外的输出文件信息
        }

    Returns:
        {
            "success": true,
            "message": "文件已成功同步",
            "file_path": "...",
            "filename": "...",
            "file_size": 12345
        }
    """
    try:
        import shutil

        data = request.get_json()
        source_file_path = data.get('file_path')
        output_files = data.get('output_files', {})  # 可能包含多个输出文件

        if not source_file_path:
            return jsonify({
                'success': False,
                'error': '未提供文件路径'
            }), 400

        # 如果传入的是下载URL(以/api/downloads/开头),转换为实际文件路径
        if source_file_path.startswith('/api/downloads/'):
            filename = source_file_path.replace('/api/downloads/', '')
            # 使用URL解码处理中文文件名
            from urllib.parse import unquote
            filename = unquote(filename)
            source_file_path = os.path.join(project_root, 'data/outputs', filename)
            logger.info(f"从下载URL转换为文件路径: {source_file_path}")

        # 检查源文件是否存在
        if not os.path.exists(source_file_path):
            return jsonify({
                'success': False,
                'error': '源文件不存在'
            }), 404

        logger.info(f"同步技术方案文件到HITL项目: project_id={project_id}, file_path={source_file_path}")

        # 获取数据库实例
        db = get_knowledge_base_db()

        # 查询任务信息
        task_data = db.execute_query("""
            SELECT step1_data FROM tender_projects
            WHERE project_id = ?
        """, (project_id,), fetch_one=True)

        if not task_data:
            return jsonify({
                'success': False,
                'error': '任务不存在'
            }), 404

        step1_data = json.loads(task_data['step1_data'])

        # 创建存储目录
        now = datetime.now()
        save_dir = os.path.join(
            project_root,
            'data/uploads/completed_response_files',
            str(now.year),
            f"{now.month:02d}",
            str(project_id)
        )
        os.makedirs(save_dir, exist_ok=True)

        # 生成文件名
        source_filename = os.path.basename(source_file_path)
        # 从源文件名提取,如果包含时间戳则保留,否则添加时间戳
        if '_' in source_filename:
            base_name = source_filename.rsplit('.', 1)[0]
            filename = f"{base_name}_应答完成.docx"
        else:
            filename = f"技术方案_{now.strftime('%Y%m%d_%H%M%S')}_应答完成.docx"

        # 复制文件到目标位置
        target_path = os.path.join(save_dir, filename)
        shutil.copy2(source_file_path, target_path)

        # 计算文件大小
        file_size = os.path.getsize(target_path)

        # 更新任务的step1_data - 使用独立字段存储技术方案文件
        tech_proposal_file_info = {
            "file_path": target_path,
            "filename": filename,
            "file_size": file_size,
            "saved_at": now.isoformat(),
            "source_file": source_file_path,
            "output_files": output_files  # 保存所有输出文件信息
        }
        step1_data['technical_proposal_file'] = tech_proposal_file_info

        db.execute_query("""
            UPDATE tender_projects
            SET step1_data = ?
            WHERE project_id = ?
        """, (json.dumps(step1_data), project_id))

        logger.info(f"同步技术方案文件到HITL项目: {project_id}, 文件: {filename} ({file_size} bytes)")

        return jsonify({
            'success': True,
            'message': '技术方案文件已成功同步到投标项目',
            'file_path': target_path,
            'filename': filename,
            'file_size': file_size,
            'saved_at': tech_proposal_file_info['saved_at']
        })

    except Exception as e:
        logger.error(f"同步技术方案文件失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'同步失败: {str(e)}'
        }), 500


__all__ = ['api_tender_processing_bp']
