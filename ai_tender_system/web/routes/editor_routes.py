#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
富文本编辑器API路由

提供Word↔HTML转换、文档保存等功能
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 导入转换器
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, get_config
from common.document_converter import DocumentConverter

# 创建蓝图
editor_bp = Blueprint('editor', __name__, url_prefix='/api/editor')

# 全局变量
logger = get_module_logger("editor_routes")
config = get_config()


@editor_bp.route('/convert-word-to-html', methods=['POST'])
def convert_word_to_html():
    """
    将Word文档转换为HTML（用于编辑器加载）

    请求体（JSON）:
    {
        "file_path": "/path/to/document.docx"
    }

    返回:
    {
        "success": true,
        "html_content": "<h1>标题</h1><p>内容...</p>"
    }
    """
    try:
        data = request.json
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({
                'success': False,
                'error': '缺少file_path参数'
            }), 400

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return jsonify({
                'success': False,
                'error': f'文件不存在: {file_path}'
            }), 404

        # 转换
        converter = DocumentConverter(config)
        html_content = converter.word_to_html(file_path)

        logger.info(f"Word转HTML成功: {file_path}")

        return jsonify({
            'success': True,
            'html_content': html_content
        })

    except ImportError as e:
        logger.error(f"依赖库未安装: {e}")
        return jsonify({
            'success': False,
            'error': f'依赖库未安装: {str(e)}',
            'hint': '请运行: pip install mammoth'
        }), 500

    except Exception as e:
        logger.error(f"Word转HTML失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@editor_bp.route('/save-html-to-word', methods=['POST'])
def save_html_to_word():
    """
    将HTML内容保存为Word文档

    请求体（JSON）:
    {
        "html_content": "<h1>标题</h1><p>内容...</p>",
        "project_id": 123,
        "document_type": "business_response",  // business_response / point_to_point / tech_proposal
        "original_file": "/path/to/original.docx"  // 可选，原始文件路径
    }

    返回:
    {
        "success": true,
        "output_file": "/path/to/output.docx",
        "download_url": "/api/downloads/xxx.docx"
    }
    """
    try:
        data = request.json
        html_content = data.get('html_content')
        project_id = data.get('project_id')
        document_type = data.get('document_type', 'document')
        original_file = data.get('original_file')

        if not html_content:
            return jsonify({
                'success': False,
                'error': '缺少html_content参数'
            }), 400

        # 转换
        converter = DocumentConverter(config)
        output_path = converter.html_to_word(
            html_content,
            project_id=project_id,
            document_type=document_type
        )

        # 生成下载URL
        filename = os.path.basename(output_path)
        download_url = f'/api/downloads/{filename}'

        logger.info(f"HTML转Word成功: {output_path}")

        return jsonify({
            'success': True,
            'output_file': output_path,
            'download_url': download_url,
            'message': '保存成功'
        })

    except ImportError as e:
        logger.error(f"依赖库未安装: {e}")
        return jsonify({
            'success': False,
            'error': f'依赖库未安装: {str(e)}',
            'hint': '请运行: pip install python-docx beautifulsoup4'
        }), 500

    except Exception as e:
        logger.error(f"HTML转Word失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@editor_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口

    返回:
    {
        "success": true,
        "dependencies": {
            "mammoth": true,
            "python-docx": true,
            "beautifulsoup4": true
        }
    }
    """
    try:
        import mammoth
        mammoth_ok = True
    except ImportError:
        mammoth_ok = False

    try:
        from docx import Document
        python_docx_ok = True
    except ImportError:
        python_docx_ok = False

    try:
        from bs4 import BeautifulSoup
        bs4_ok = True
    except ImportError:
        bs4_ok = False

    all_ok = mammoth_ok and python_docx_ok and bs4_ok

    return jsonify({
        'success': all_ok,
        'dependencies': {
            'mammoth': mammoth_ok,
            'python-docx': python_docx_ok,
            'beautifulsoup4': bs4_ok
        },
        'message': '所有依赖正常' if all_ok else '部分依赖缺失，请检查'
    })


# 导出蓝图
__all__ = ['editor_bp']
