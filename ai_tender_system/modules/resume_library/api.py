#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历库API接口
提供简历管理的RESTful API
"""

import os
import json
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
from typing import Dict, Any

from .manager import ResumeLibraryManager
from .resume_parser import ResumeParser
from .export_handler import ResumeExportHandler
from ai_tender_system.core.storage_service import storage_service
from ai_tender_system.web.utils.response_helper import success_response, error_response

# 创建蓝图
resume_library_bp = Blueprint('resume_library', __name__, url_prefix='/api/resume_library')

# 初始化管理器
resume_manager = None
resume_parser = None
export_handler = None


def init_managers():
    """初始化管理器实例"""
    global resume_manager, resume_parser, export_handler
    if not resume_manager:
        resume_manager = ResumeLibraryManager()
    if not resume_parser:
        resume_parser = ResumeParser()
    if not export_handler:
        export_handler = ResumeExportHandler()


# ==================== 简历管理接口 ====================

@resume_library_bp.route('/list', methods=['GET'])
def get_resume_list():
    """获取简历列表"""
    try:
        init_managers()

        # 获取查询参数
        company_id = request.args.get('company_id', type=int)
        status = request.args.get('status')
        search_keyword = request.args.get('search')
        education_level = request.args.get('education_level')
        position = request.args.get('position')
        tags = request.args.getlist('tags')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        order_by = request.args.get('order_by', 'created_at')
        order_dir = request.args.get('order_dir', 'DESC')

        # 查询简历列表
        result = resume_manager.get_resumes(
            company_id=company_id,
            status=status,
            search_keyword=search_keyword,
            education_level=education_level,
            position=position,
            tags=tags,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir
        )

        return success_response(result)

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/detail/<int:resume_id>', methods=['GET'])
def get_resume_detail(resume_id):
    """获取简历详情"""
    try:
        init_managers()

        resume = resume_manager.get_resume_by_id(resume_id)
        if not resume:
            return error_response("简历不存在", code=404)

        return success_response(resume)

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/create', methods=['POST'])
def create_resume():
    """创建简历"""
    try:
        init_managers()

        data = request.get_json()
        if not data:
            return error_response("请提供简历数据")

        # 验证必填字段
        if not data.get('name'):
            return error_response("姓名不能为空")

        # 创建简历
        resume = resume_manager.create_resume(data)

        return success_response(resume, message="简历创建成功")

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/update/<int:resume_id>', methods=['PUT'])
def update_resume(resume_id):
    """更新简历"""
    try:
        init_managers()

        data = request.get_json()
        if not data:
            return error_response("请提供更新数据")

        # 更新简历
        resume = resume_manager.update_resume(resume_id, data)

        return success_response(resume, message="简历更新成功")

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/delete/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    """删除简历"""
    try:
        init_managers()

        success = resume_manager.delete_resume(resume_id)
        if success:
            return success_response(None, message="简历删除成功")
        else:
            return error_response("删除失败")

    except Exception as e:
        return error_response(str(e))


# ==================== 简历解析接口 ====================

@resume_library_bp.route('/parse-resume', methods=['POST'])
def parse_resume():
    """解析上传的简历文件"""
    try:
        init_managers()

        # 检查是否有文件
        if 'file' not in request.files:
            return error_response("请上传简历文件")

        file = request.files['file']
        if file.filename == '':
            return error_response("请选择文件")

        # 检查文件类型
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return error_response(f"不支持的文件格式，请上传 {', '.join(allowed_extensions)} 格式的文件")

        # 保存临时文件
        temp_dir = 'ai_tender_system/data/temp'
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"resume_{timestamp}{file_ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        file.save(temp_path)

        try:
            # 解析简历
            parsed_data = resume_parser.parse_resume(temp_path)

            # 如果请求包含auto_create参数，直接创建简历
            if request.form.get('auto_create') == 'true':
                # 添加公司ID（如果提供）
                company_id = request.form.get('company_id', type=int)
                if company_id:
                    parsed_data['company_id'] = company_id

                # 创建简历
                resume = resume_manager.create_resume(parsed_data)

                # 将原始简历文件作为附件保存
                if resume:
                    storage_info = storage_service.save_file(
                        temp_path,
                        category='resume_attachments',
                        metadata={
                            'resume_id': resume['resume_id'],
                            'attachment_category': 'resume',
                            'original_filename': file.filename
                        }
                    )

                    # 保存附件记录
                    resume_manager.upload_attachment(
                        resume_id=resume['resume_id'],
                        file_path=storage_info['filepath'],
                        original_filename=file.filename,
                        attachment_category='resume',
                        attachment_description='原始简历文件',
                        uploaded_by=request.form.get('uploaded_by')
                    )

                return success_response({
                    'parsed_data': parsed_data,
                    'resume': resume
                }, message="简历解析并创建成功")
            else:
                return success_response({
                    'parsed_data': parsed_data
                }, message="简历解析成功")

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/parse-text', methods=['POST'])
def parse_resume_text():
    """解析简历文本"""
    try:
        init_managers()

        data = request.get_json()
        if not data or not data.get('text'):
            return error_response("请提供简历文本")

        # 解析文本
        parsed_data = resume_parser.extract_from_text(data['text'])

        return success_response({
            'parsed_data': parsed_data
        }, message="文本解析成功")

    except Exception as e:
        return error_response(str(e))


# ==================== 附件管理接口 ====================

@resume_library_bp.route('/upload-attachment', methods=['POST'])
def upload_attachment():
    """上传简历附件"""
    try:
        init_managers()

        # 验证参数
        resume_id = request.form.get('resume_id', type=int)
        if not resume_id:
            return error_response("请提供简历ID")

        attachment_category = request.form.get('attachment_category')
        if not attachment_category:
            return error_response("请指定附件类别")

        # 验证附件类别
        valid_categories = ['resume', 'id_card', 'education', 'degree',
                          'qualification', 'award', 'other']
        if attachment_category not in valid_categories:
            return error_response(f"无效的附件类别，有效类别: {', '.join(valid_categories)}")

        # 检查文件
        if 'file' not in request.files:
            return error_response("请上传文件")

        file = request.files['file']
        if file.filename == '':
            return error_response("请选择文件")

        # 保存临时文件
        temp_dir = 'ai_tender_system/data/temp'
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = os.path.splitext(file.filename)[1]
        temp_filename = f"attachment_{resume_id}_{timestamp}{file_ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        file.save(temp_path)

        try:
            # 上传附件
            attachment_info = resume_manager.upload_attachment(
                resume_id=resume_id,
                file_path=temp_path,
                original_filename=file.filename,
                attachment_category=attachment_category,
                attachment_description=request.form.get('description'),
                uploaded_by=request.form.get('uploaded_by')
            )

            return success_response(attachment_info, message="附件上传成功")

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/attachments/<int:resume_id>', methods=['GET'])
def get_attachments(resume_id):
    """获取简历附件列表"""
    try:
        init_managers()

        category = request.args.get('category')
        attachments = resume_manager.get_attachments(resume_id, category)

        return success_response(attachments)

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/attachment/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id):
    """删除附件"""
    try:
        init_managers()

        success = resume_manager.delete_attachment(attachment_id)
        if success:
            return success_response(None, message="附件删除成功")
        else:
            return error_response("删除失败")

    except Exception as e:
        return error_response(str(e))


# ==================== 批量导出接口 ====================

@resume_library_bp.route('/export', methods=['POST'])
def export_resumes():
    """批量导出简历"""
    try:
        init_managers()

        data = request.get_json()
        if not data or not data.get('resume_ids'):
            return error_response("请选择要导出的简历")

        resume_ids = data['resume_ids']
        export_options = data.get('options', {})

        # 执行导出
        result = export_handler.export_resumes(resume_ids, export_options)

        if result['format'] == 'zip':
            # 返回下载链接
            return success_response({
                'download_url': f"/api/resume_library/download/{os.path.basename(result['file_path'])}",
                'file_name': result['file_name'],
                'stats': result['stats']
            }, message="导出成功")
        else:
            return success_response(result, message="导出成功")

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/download/<filename>', methods=['GET'])
def download_export(filename):
    """下载导出文件"""
    try:
        init_managers()

        file_path = os.path.join('ai_tender_system/data/exports', filename)
        if not os.path.exists(file_path):
            return error_response("文件不存在", code=404)

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/export-history', methods=['GET'])
def get_export_history():
    """获取导出历史"""
    try:
        init_managers()

        limit = request.args.get('limit', 20, type=int)
        history = export_handler.get_export_history(limit)

        return success_response(history)

    except Exception as e:
        return error_response(str(e))


# ==================== 搜索和统计接口 ====================

@resume_library_bp.route('/search', methods=['GET'])
def search_resumes():
    """快速搜索简历"""
    try:
        init_managers()

        keyword = request.args.get('keyword')
        if not keyword:
            return error_response("请提供搜索关键词")

        limit = request.args.get('limit', 10, type=int)
        results = resume_manager.search_resumes(keyword, limit)

        return success_response(results)

    except Exception as e:
        return error_response(str(e))


@resume_library_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取简历统计信息"""
    try:
        init_managers()

        company_id = request.args.get('company_id', type=int)
        stats = resume_manager.get_statistics(company_id)

        return success_response(stats)

    except Exception as e:
        return error_response(str(e))


# ==================== 辅助接口 ====================

@resume_library_bp.route('/categories', methods=['GET'])
def get_attachment_categories():
    """获取附件类别列表"""
    categories = [
        {'value': 'resume', 'label': '简历文件'},
        {'value': 'id_card', 'label': '身份证'},
        {'value': 'education', 'label': '学历证书'},
        {'value': 'degree', 'label': '学位证书'},
        {'value': 'qualification', 'label': '资质证书'},
        {'value': 'award', 'label': '获奖证书'},
        {'value': 'other', 'label': '其他材料'}
    ]

    return success_response(categories)


@resume_library_bp.route('/education-levels', methods=['GET'])
def get_education_levels():
    """获取学历级别列表"""
    levels = [
        {'value': '博士', 'label': '博士'},
        {'value': '硕士', 'label': '硕士'},
        {'value': '本科', 'label': '本科'},
        {'value': '大专', 'label': '大专'},
        {'value': '高中', 'label': '高中'},
        {'value': '中专', 'label': '中专'},
        {'value': '其他', 'label': '其他'}
    ]

    return success_response(levels)


@resume_library_bp.route('/cleanup', methods=['POST'])
def cleanup_old_exports():
    """清理旧的导出文件"""
    try:
        init_managers()

        data = request.get_json()
        days = data.get('days', 7) if data else 7

        export_handler.cleanup_old_exports(days)

        return success_response(None, message=f"已清理{days}天前的导出文件")

    except Exception as e:
        return error_response(str(e))