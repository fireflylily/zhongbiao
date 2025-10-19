#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档编辑器和表格处理API蓝图
提供文档加载、保存、图片上传和表格处理功能

路由列表:
- POST /api/editor/load-document - 加载文档
- POST /api/editor/save-document - 保存文档
- POST /api/editor/upload-image - 上传图片
- POST /api/table/analyze - 分析表格
- POST /api/table/process - 处理表格
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入公共组件
from common import (
    get_config, get_module_logger,
    format_error_response, ensure_dir
)

# 创建蓝图
api_editor_bp = Blueprint('api_editor', __name__, url_prefix='/api')

# 获取配置和日志器
config = get_config()
logger = get_module_logger("api_editor_bp")

# 检查表格处理模块可用性
try:
    from modules.business_response.table_processor import TableProcessor
    POINT_TO_POINT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"表格处理模块加载失败: {e}")
    POINT_TO_POINT_AVAILABLE = False


# ===================
# 文档编辑器API
# ===================

@api_editor_bp.route('/editor/load-document', methods=['POST'])
def load_document_for_edit():
    """加载文档用于编辑"""
    try:
        from docx import Document
        from markupsafe import Markup

        if 'file' not in request.files:
            raise ValueError("没有选择文件")

        file = request.files['file']
        if file.filename == '':
            raise ValueError("文件名为空")

        # 读取Word文档
        doc = Document(file)

        # 转换为HTML格式用于编辑器
        html_content = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                style_name = paragraph.style.name if paragraph.style else ''

                if 'Heading 1' in style_name:
                    html_content.append(f'<h1>{paragraph.text}</h1>')
                elif 'Heading 2' in style_name:
                    html_content.append(f'<h2>{paragraph.text}</h2>')
                elif 'Heading 3' in style_name:
                    html_content.append(f'<h3>{paragraph.text}</h3>')
                else:
                    html_content.append(f'<p>{paragraph.text}</p>')

        # 处理表格
        for table in doc.tables:
            html_content.append('<table>')
            for row in table.rows:
                html_content.append('<tr>')
                for cell in row.cells:
                    html_content.append(f'<td>{cell.text}</td>')
                html_content.append('</tr>')
            html_content.append('</table>')

        return jsonify({
            'success': True,
            'html_content': ''.join(html_content),
            'original_filename': file.filename
        })

    except Exception as e:
        logger.error(f"文档加载失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@api_editor_bp.route('/editor/save-document', methods=['POST'])
def save_edited_document():
    """保存编辑后的文档"""
    try:
        from docx import Document
        from bs4 import BeautifulSoup
        import re

        data = request.get_json()
        html_content = data.get('html_content', '')
        filename = data.get('filename', 'document')

        if not html_content:
            raise ValueError("文档内容为空")

        # 创建新文档
        doc = Document()

        # 解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')

        # 处理各种HTML元素
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'table']):
            if element.name == 'h1':
                doc.add_heading(element.get_text(), level=1)
            elif element.name == 'h2':
                doc.add_heading(element.get_text(), level=2)
            elif element.name == 'h3':
                doc.add_heading(element.get_text(), level=3)
            elif element.name == 'p':
                text = element.get_text()
                if text.strip():
                    doc.add_paragraph(text)
            elif element.name == 'table':
                # 计算表格行列数
                rows = element.find_all('tr')
                if rows:
                    cols = len(rows[0].find_all(['td', 'th']))
                    table = doc.add_table(rows=len(rows), cols=cols)
                    table.style = 'Table Grid'

                    for i, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        for j, cell in enumerate(cells):
                            if j < cols:
                                table.cell(i, j).text = cell.get_text()

        # 保存文档
        output_dir = ensure_dir(config.get_path('output'))
        output_path = output_dir / f"{filename}.docx"
        doc.save(str(output_path))

        # 返回文件供下载
        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=f"{filename}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"文档保存失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@api_editor_bp.route('/editor/upload-image', methods=['POST'])
def upload_editor_image():
    """上传编辑器图片"""
    try:
        if 'image' not in request.files:
            raise ValueError("没有选择图片")

        file = request.files['image']
        if file.filename == '':
            raise ValueError("文件名为空")

        # 保存图片 - 使用统一服务
        from core.storage_service import storage_service
        file_metadata = storage_service.store_file(
            file_obj=file,
            original_name=file.filename,
            category='processed_results',  # 编辑器图片属于处理结果
            business_type='editor_image'
        )
        file_path = Path(file_metadata.file_path)
        filename = file_metadata.safe_name

        # 返回图片URL
        image_url = f'/static/uploads/images/{filename}'

        return jsonify({
            'success': True,
            'location': image_url
        })

    except Exception as e:
        logger.error(f"图片上传失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


# ===================
# 表格处理API
# ===================

@api_editor_bp.route('/table/analyze', methods=['POST'])
def analyze_table():
    """分析表格"""
    if not POINT_TO_POINT_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '表格处理模块不可用'
        })

    try:
        data = request.get_json()
        table_data = data.get('table_data', {})

        processor = TableProcessor()
        result = processor.analyze_table(table_data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"表格分析失败: {e}")
        return jsonify(format_error_response(e))


@api_editor_bp.route('/table/process', methods=['POST'])
def process_table():
    """处理表格"""
    if not POINT_TO_POINT_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '表格处理模块不可用'
        })

    try:
        data = request.get_json()
        table_data = data.get('table_data', {})
        options = data.get('options', {})

        processor = TableProcessor()
        result = processor.process_table(table_data, options)

        return jsonify(result)

    except Exception as e:
        logger.error(f"表格处理失败: {e}")
        return jsonify(format_error_response(e))


__all__ = ['api_editor_bp']
