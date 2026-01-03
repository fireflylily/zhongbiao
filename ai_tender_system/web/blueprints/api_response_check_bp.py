#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应答文件自检API蓝图

Web端接口：
- POST /api/response-check/upload          上传应答文件并开始检查
- GET  /api/response-check/status/<id>     查询检查状态
- GET  /api/response-check/result/<id>     获取检查结果
- GET  /api/response-check/history         历史检查列表
- DELETE /api/response-check/<id>          删除检查记录
- GET  /api/response-check/export/<id>     导出Excel报告

小程序接口：
- POST /api/mp/response-check/upload       小程序上传
- GET  /api/mp/response-check/status/<id>  小程序查询状态
- GET  /api/mp/response-check/result/<id>  小程序获取结果
- GET  /api/mp/response-check/export/<id>  小程序导出Excel
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, g, send_file
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# 创建Web端蓝图
api_response_check_bp = Blueprint('api_response_check', __name__, url_prefix='/api/response-check')

# 创建小程序端蓝图
api_mp_response_check_bp = Blueprint('api_mp_response_check', __name__, url_prefix='/api/mp/response-check')


# ============================================================
# 辅助函数
# ============================================================

def get_upload_dir() -> Path:
    """获取上传目录"""
    base_dir = Path(__file__).parent.parent.parent
    upload_dir = base_dir / 'data' / 'uploads' / 'response_check'
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_uploaded_file(file) -> dict:
    """
    保存上传的文件

    Args:
        file: Flask文件对象

    Returns:
        文件元数据
    """
    upload_dir = get_upload_dir()

    # 生成安全文件名
    original_filename = file.filename
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_id = str(uuid.uuid4())[:8]
    safe_filename = f"{timestamp}_{file_id}.{ext}"

    # 保存文件
    file_path = upload_dir / safe_filename
    file.save(str(file_path))

    # 获取文件大小
    file_size = file_path.stat().st_size

    return {
        'file_id': file_id,
        'file_path': str(file_path),
        'original_name': original_filename,
        'safe_name': safe_filename,
        'file_size': file_size
    }


# ============================================================
# Web端接口
# ============================================================

@api_response_check_bp.route('/upload', methods=['POST'])
def upload_and_check():
    """
    上传应答文件并创建检查任务

    POST: multipart/form-data
    - file: 应答文档文件 (PDF/Word)
    - model: AI模型名称 (可选，默认deepseek-v3)

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "uuid-xxx",
                "status": "pending",
                "message": "检查任务已创建"
            }
        }
    """
    try:
        # 验证文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未上传文件'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'message': '文件名为空'}), 400

        original_filename = request.form.get('filename') or file.filename

        # 检查文件类型
        allowed_extensions = {'pdf', 'doc', 'docx'}
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if ext not in allowed_extensions:
            return jsonify({'success': False, 'message': f'不支持的文件格式: {ext}'}), 400

        # 保存文件
        file_metadata = save_uploaded_file(file)

        # 获取模型配置
        model_name = request.form.get('model', 'deepseek-v3')

        # 创建任务
        from modules.response_checker import ResponseCheckTaskManager
        task_manager = ResponseCheckTaskManager()

        task_id = task_manager.create_task(
            file_id=file_metadata['file_id'],
            file_path=file_metadata['file_path'],
            original_filename=file_metadata['original_name'],
            user_id=getattr(g, 'user_id', None),
            openid=getattr(g, 'openid', ''),
            file_size=file_metadata['file_size'],
            model_name=model_name
        )

        # 异步启动检查
        task_manager.start_check(task_id)

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'status': 'pending',
                'message': '检查任务已创建，正在分析中'
            }
        })

    except Exception as e:
        logger.error(f"创建检查任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_response_check_bp.route('/status/<task_id>', methods=['GET'])
def get_check_status(task_id: str):
    """
    查询检查任务状态（支持边检查边显示）

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "xxx",
                "status": "checking",
                "progress": 45,
                "current_step": "正在进行签字盖章检查...",
                "categories": [...],
                "statistics": {...}
            }
        }
    """
    try:
        from modules.response_checker import ResponseCheckTaskManager
        import json

        task_manager = ResponseCheckTaskManager()
        task = task_manager.get_task(task_id)

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        # 解析已完成的检查类别
        categories = []
        if task.get('check_categories'):
            try:
                categories = json.loads(task['check_categories'])
            except:
                categories = []

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'file_name': task.get('original_filename', ''),
                'status': task['status'],
                'progress': task['progress'],
                'current_step': task.get('current_step', ''),
                'current_category': task.get('current_category', ''),
                'error_message': task.get('error_message', ''),
                'categories': categories,
                'statistics': {
                    'total_items': task.get('total_items', 0),
                    'pass_count': task.get('pass_count', 0),
                    'fail_count': task.get('fail_count', 0),
                    'unknown_count': task.get('unknown_count', 0)
                }
            }
        })

    except Exception as e:
        logger.error(f"查询任务状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_response_check_bp.route('/result/<task_id>', methods=['GET'])
def get_check_result(task_id: str):
    """
    获取完整检查结果

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "xxx",
                "file_name": "xxx.pdf",
                "check_time": "2024-01-15 14:30:00",
                "categories": [...],
                "statistics": {...},
                "extracted_info": {...}
            }
        }
    """
    try:
        from modules.response_checker import ResponseCheckTaskManager
        task_manager = ResponseCheckTaskManager()

        result = task_manager.get_task_result(task_id)
        if not result:
            return jsonify({'success': False, 'message': '任务不存在或未完成'}), 404

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"获取检查结果失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_response_check_bp.route('/export/<task_id>', methods=['GET'])
def export_excel(task_id: str):
    """
    导出检查结果为Excel文件

    Returns:
        Excel文件下载
    """
    try:
        from modules.response_checker import ResponseCheckTaskManager
        from modules.response_checker.excel_exporter import ResponseCheckExcelExporter

        task_manager = ResponseCheckTaskManager()
        result = task_manager.get_task_result(task_id)

        if not result:
            return jsonify({'success': False, 'message': '任务不存在或未完成'}), 404

        # 生成Excel
        exporter = ResponseCheckExcelExporter()
        output = exporter.export(result)

        # 设置下载文件名
        filename = result.get('file_name', '检查报告')
        filename = filename.rsplit('.', 1)[0] if '.' in filename else filename
        download_name = f"{filename}_自检报告.xlsx"

        return send_file(
            output,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"导出Excel失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_response_check_bp.route('/history', methods=['GET'])
def list_history():
    """
    获取历史检查记录

    Query params:
    - page: 页码（默认1）
    - page_size: 每页数量（默认10）

    Returns:
        {
            "success": true,
            "data": {
                "tasks": [...],
                "total": 100,
                "page": 1,
                "page_size": 10
            }
        }
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        from modules.response_checker import ResponseCheckTaskManager
        task_manager = ResponseCheckTaskManager()

        result = task_manager.list_tasks(
            user_id=getattr(g, 'user_id', None),
            openid=getattr(g, 'openid', None),
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_response_check_bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id: str):
    """
    删除检查记录

    Returns:
        {"success": true, "message": "删除成功"}
    """
    try:
        from modules.response_checker import ResponseCheckTaskManager
        task_manager = ResponseCheckTaskManager()

        success = task_manager.delete_task(
            task_id,
            user_id=getattr(g, 'user_id', None)
        )

        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '任务不存在或无权删除'}), 404

    except Exception as e:
        logger.error(f"删除任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 小程序接口
# ============================================================

def require_mp_auth(f):
    """
    小程序鉴权装饰器

    从请求头中获取token并验证
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'message': '未提供认证信息'}), 401

            token = auth_header[7:]

            # 尝试导入JWT验证
            try:
                from common.jwt_utils import verify_jwt_token
                from common.config import Config

                config = Config()
                secret_key = config.get('JWT_SECRET_KEY', 'default_secret')
                payload = verify_jwt_token(token, secret_key)

                g.openid = payload.get('openid', '')
                g.user_id = payload.get('user_id')

            except ImportError:
                # 如果没有JWT模块，使用简单验证
                g.openid = token
                g.user_id = None

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"小程序认证失败: {e}")
            return jsonify({'success': False, 'message': '认证失败'}), 401

    return decorated


@api_mp_response_check_bp.route('/upload', methods=['POST'])
@require_mp_auth
def mp_upload_and_check():
    """小程序上传应答文件"""
    return upload_and_check()


@api_mp_response_check_bp.route('/status/<task_id>', methods=['GET'])
@require_mp_auth
def mp_get_status(task_id: str):
    """小程序查询状态"""
    return get_check_status(task_id)


@api_mp_response_check_bp.route('/result/<task_id>', methods=['GET'])
@require_mp_auth
def mp_get_result(task_id: str):
    """小程序获取结果"""
    return get_check_result(task_id)


@api_mp_response_check_bp.route('/export/<task_id>', methods=['GET'])
@require_mp_auth
def mp_export_excel(task_id: str):
    """小程序导出Excel"""
    return export_excel(task_id)


@api_mp_response_check_bp.route('/history', methods=['GET'])
@require_mp_auth
def mp_list_history():
    """小程序历史记录"""
    return list_history()


@api_mp_response_check_bp.route('/<task_id>', methods=['DELETE'])
@require_mp_auth
def mp_delete_task(task_id: str):
    """小程序删除任务"""
    return delete_task(task_id)
