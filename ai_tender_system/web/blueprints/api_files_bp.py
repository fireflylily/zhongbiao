#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理API蓝图
处理文件上传、下载等文件操作
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config, format_error_response

# 创建蓝图
api_files_bp = Blueprint('api_files', __name__, url_prefix='/api/files')

# 日志记录器
logger = get_module_logger("web.api_files")

# 获取配置
config = get_config()


@api_files_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    通用文件上传API - 使用统一存储服务

    POST参数:
    - file: 上传的文件对象（multipart/form-data）
    - type: 文件类型（可选，默认'tender_info'）

    Returns:
        {
            "success": true,
            "filename": "safe_filename.pdf",
            "original_filename": "原始文件名.pdf",
            "file_path": "/path/to/file",
            "file_size": 123456,
            "file_size_mb": 0.12,
            "file_id": "uuid",
            "message": "文件上传成功"
        }
    """
    try:
        from core.storage_service import storage_service

        if 'file' not in request.files:
            raise ValueError("没有选择文件")

        file = request.files['file']
        if not file.filename:
            raise ValueError("文件名为空")

        # 获取文件类型
        file_type = request.form.get('type', 'tender_info')

        # 使用统一存储服务
        file_metadata = storage_service.store_file(
            file_obj=file,
            original_name=file.filename,
            category='tender_documents',
            business_type=file_type
        )

        logger.info(f"文件上传成功: {file.filename} -> {file_metadata.safe_name}")

        return jsonify({
            'success': True,
            'filename': file_metadata.safe_name,
            'original_filename': file_metadata.original_name,
            'file_path': file_metadata.file_path,
            'file_size': file_metadata.file_size,
            'file_size_mb': round(file_metadata.file_size / (1024 * 1024), 2),
            'file_id': file_metadata.file_id,
            'message': '文件上传成功'
        })

    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify(format_error_response(e))


@api_files_bp.route('/download/<filename>')
def download_file(filename):
    """
    文件下载API

    Args:
        filename: 要下载的文件名

    Returns:
        文件内容（attachment形式）

    Raises:
        404: 文件不存在
    """
    try:
        output_dir = config.get_path('output')
        file_path = output_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {filename}")

        logger.info(f"文件下载: {filename}")
        return send_file(str(file_path), as_attachment=True)

    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        return jsonify(format_error_response(e))


@api_files_bp.route('/serve/<path:filepath>')
def serve_file(filepath):
    """
    通用文件访问API - 用于访问uploads目录下的文件

    Args:
        filepath: 相对于uploads目录的文件路径

    Query参数:
        download: 是否作为下载（可选，默认False，即在线预览）

    Returns:
        文件内容

    Raises:
        404: 文件不存在
    """
    try:
        import os
        from pathlib import Path

        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent

        # 构建完整文件路径
        # 处理可能的路径格式：
        # 1. ai_tender_system/data/uploads/...
        # 2. data/uploads/...
        # 3. uploads/...
        # 4. download/... (output目录)

        if filepath.startswith('ai_tender_system/'):
            full_path = project_root / filepath
        elif filepath.startswith('data/'):
            full_path = project_root / 'ai_tender_system' / filepath
        elif filepath.startswith('uploads/'):
            full_path = project_root / 'ai_tender_system' / 'data' / filepath
        elif filepath.startswith('download/'):
            # download/ 路径指向 outputs 目录
            filename = filepath[9:]  # 移除 'download/' 前缀
            full_path = project_root / 'ai_tender_system' / 'data' / 'outputs' / filename
        else:
            # 假设是相对于 uploads 目录
            full_path = project_root / 'ai_tender_system' / 'data' / 'uploads' / filepath

        # 安全检查：确保文件路径在允许的目录内（防止路径遍历攻击）
        uploads_dir = project_root / 'ai_tender_system' / 'data' / 'uploads'
        outputs_dir = project_root / 'ai_tender_system' / 'data' / 'outputs'
        try:
            full_path = full_path.resolve()
            uploads_dir = uploads_dir.resolve()
            outputs_dir = outputs_dir.resolve()
            # 允许访问 uploads 或 outputs 目录
            if not (str(full_path).startswith(str(uploads_dir)) or str(full_path).startswith(str(outputs_dir))):
                raise PermissionError("访问被拒绝：文件路径超出允许范围")
        except Exception as e:
            logger.error(f"路径安全检查失败: {e}")
            raise PermissionError("访问被拒绝")

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        # 检查是否为下载模式
        as_attachment = request.args.get('download', 'false').lower() == 'true'

        logger.info(f"文件访问: {filepath} (下载模式: {as_attachment})")
        return send_file(str(full_path), as_attachment=as_attachment)

    except FileNotFoundError as e:
        logger.error(f"文件不存在: {filepath}")
        return jsonify({'success': False, 'error': str(e)}), 404
    except PermissionError as e:
        logger.error(f"访问被拒绝: {filepath}")
        return jsonify({'success': False, 'error': str(e)}), 403
    except Exception as e:
        logger.error(f"文件访问失败: {e}")
        return jsonify(format_error_response(e)), 500


__all__ = ['api_files_bp']
