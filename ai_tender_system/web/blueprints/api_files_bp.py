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
api_files_bp = Blueprint('api_files', __name__)

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


__all__ = ['api_files_bp']
