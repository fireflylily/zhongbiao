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
from common import get_module_logger, get_config, resolve_file_path
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

        # 使用智能路径解析（兼容多种环境）
        resolved_path = resolve_file_path(file_path)
        if not resolved_path:
            logger.error(f"文件路径解析失败: {file_path}")
            return jsonify({
                'success': False,
                'error': f'文件不存在: {file_path}'
            }), 404

        file_path = str(resolved_path)  # 使用解析后的绝对路径

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


@editor_bp.route('/upload-temp', methods=['POST'])
def upload_temp_file():
    """
    临时文件上传接口（用于测试）

    返回:
    {
        "success": true,
        "file_path": "/path/to/uploaded/file.docx"
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400

        # 保存到临时目录
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / 'tender_uploads'
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = secure_filename(file.filename)
        file_path = temp_dir / f"{timestamp}_{safe_filename}"

        # 保存文件
        file.save(str(file_path))

        logger.info(f"临时文件已上传: {file_path}")

        return jsonify({
            'success': True,
            'file_path': str(file_path)
        })

    except Exception as e:
        logger.error(f"临时文件上传失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@editor_bp.route('/temp-images/<doc_hash>/<filename>', methods=['GET'])
def serve_temp_image(doc_hash, filename):
    """
    提供临时图片服务（用于Word→HTML转换时的外部图片）

    优化：使用外部链接代替Base64，减少90%的HTML大小和传输时间

    Args:
        doc_hash: 文档哈希（8位）
        filename: 图片文件名

    返回:
        图片文件流
    """
    try:
        # 验证参数安全性
        if '..' in doc_hash or '/' in doc_hash or '..' in filename or '/' in filename:
            logger.warning(f"非法参数: doc_hash={doc_hash}, filename={filename}")
            return jsonify({'error': '非法参数'}), 400

        # 构建图片路径
        image_path = Path('/tmp/word_images') / doc_hash / filename

        if not image_path.exists():
            logger.warning(f"临时图片不存在: {image_path}")
            return jsonify({'error': '图片不存在'}), 404

        # 确定MIME类型
        ext = image_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        mimetype = mime_types.get(ext, 'image/jpeg')

        # 返回图片文件
        return send_file(
            image_path,
            mimetype=mimetype,
            as_attachment=False,
            max_age=3600  # 缓存1小时
        )

    except Exception as e:
        logger.error(f"提供临时图片失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@editor_bp.route('/cleanup-temp-images', methods=['POST'])
def cleanup_temp_images():
    """
    清理临时图片文件（可选：可以被定时任务调用）

    清理策略：
    - 删除24小时前创建的临时图片目录
    - 保留最近24小时的文件（用户可能还在编辑）

    返回:
    {
        "success": true,
        "cleaned_count": 5,
        "freed_size": "125.5 MB"
    }
    """
    try:
        import time
        import shutil

        temp_base_dir = Path('/tmp/word_images')
        if not temp_base_dir.exists():
            return jsonify({
                'success': True,
                'cleaned_count': 0,
                'freed_size': '0 B',
                'message': '临时目录不存在'
            })

        # 24小时前的时间戳
        cutoff_time = time.time() - (24 * 3600)

        cleaned_count = 0
        freed_size = 0

        # 遍历所有文档哈希目录
        for doc_dir in temp_base_dir.iterdir():
            if not doc_dir.is_dir():
                continue

            # 检查目录的修改时间
            dir_mtime = doc_dir.stat().st_mtime

            if dir_mtime < cutoff_time:
                # 计算目录大小
                dir_size = sum(f.stat().st_size for f in doc_dir.rglob('*') if f.is_file())

                # 删除目录
                shutil.rmtree(doc_dir)

                cleaned_count += 1
                freed_size += dir_size

                logger.info(f"清理临时图片目录: {doc_dir.name} ({dir_size / 1024 / 1024:.2f} MB)")

        # 格式化大小
        if freed_size < 1024:
            size_str = f"{freed_size} B"
        elif freed_size < 1024 * 1024:
            size_str = f"{freed_size / 1024:.1f} KB"
        else:
            size_str = f"{freed_size / 1024 / 1024:.1f} MB"

        logger.info(f"临时图片清理完成: 清理了{cleaned_count}个目录，释放{size_str}")

        return jsonify({
            'success': True,
            'cleaned_count': cleaned_count,
            'freed_size': size_str,
            'message': f'清理了{cleaned_count}个临时目录'
        })

    except Exception as e:
        logger.error(f"清理临时图片失败: {e}", exc_info=True)
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
