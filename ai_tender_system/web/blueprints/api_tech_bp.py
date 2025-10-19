#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术需求处理API蓝图
处理技术需求回复文档生成
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import (
    get_module_logger, get_config, format_error_response,
    safe_filename, ensure_dir
)
from web.shared.instances import get_kb_manager

# 创建蓝图
api_tech_bp = Blueprint('api_tech', __name__)

# 日志记录器
logger = get_module_logger("web.api_tech")

# 获取配置和知识库管理器
config = get_config()
kb_manager = get_kb_manager()

# 检查技术需求回复模块可用性
TECH_RESPONDER_AVAILABLE = False
try:
    from modules.point_to_point.tech_responder import TechResponder
    TECH_RESPONDER_AVAILABLE = True
except ImportError:
    pass


# ===================
# 辅助函数
# ===================

def generate_output_filename(project_name: str, file_type: str, timestamp: str = None) -> str:
    """
    生成统一格式的输出文件名: {项目名称}_{类型}_{时间戳}.docx

    Args:
        project_name: 项目名称
        file_type: 文件类型（如：商务应答、点对点应答、技术方案）
        timestamp: 时间戳，如果未提供则自动生成

    Returns:
        格式化的文件名
    """
    if not timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 使用safe_filename确保项目名称安全，但不添加时间戳（避免重复）
    safe_project = safe_filename(project_name, timestamp=False) if project_name else "未命名项目"

    return f"{safe_project}_{file_type}_{timestamp}.docx"


# ===================
# 技术需求回复路由
# ===================

@api_tech_bp.route('/process-tech-requirements', methods=['POST'])
def process_tech_requirements():
    """处理技术需求回复"""
    if not TECH_RESPONDER_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '技术需求回复模块不可用'
        })

    try:
        # 获取上传的文件
        if 'requirements_file' not in request.files:
            raise ValueError("没有选择需求文件")

        file = request.files['requirements_file']
        if file.filename == '':
            raise ValueError("文件名为空")

        # 获取表单数据
        data = request.form.to_dict()
        company_id = data.get('company_id', '')
        response_strategy = data.get('response_strategy', 'comprehensive')

        # 验证必填字段
        if not company_id:
            raise ValueError("请选择应答公司")

        # 保存上传的文件 - 使用统一服务
        from core.storage_service import storage_service
        file_metadata = storage_service.store_file(
            file_obj=file,
            original_name=file.filename,
            category='tech_proposals',
            business_type='tech_requirements',
            company_id=int(company_id)
        )
        requirements_path = Path(file_metadata.file_path)

        # 从数据库获取公司信息
        company_id_int = int(company_id)
        company_db_data = kb_manager.get_company_detail(company_id_int)
        if not company_db_data:
            raise ValueError(f"未找到公司数据: {company_id}")

        # 使用现有字段映射反向转换为业务处理器期望的格式
        field_mapping = {
            'companyName': 'company_name',
            'establishDate': 'establish_date',
            'legalRepresentative': 'legal_representative',
            'legalRepresentativePosition': 'legal_representative_position',
            'legalRepresentativeGender': 'legal_representative_gender',
            'legalRepresentativeAge': 'legal_representative_age',
            'socialCreditCode': 'social_credit_code',
            'registeredCapital': 'registered_capital',
            'companyType': 'company_type',
            'registeredAddress': 'registered_address',
            'businessScope': 'business_scope',
            'companyDescription': 'description',
            'fixedPhone': 'fixed_phone',
            'fax': 'fax',
            'postalCode': 'postal_code',
            'email': 'email',
            'officeAddress': 'office_address',
            'employeeCount': 'employee_count',
            'bankName': 'bank_name',
            'bankAccount': 'bank_account'
        }
        reverse_mapping = {v: k for k, v in field_mapping.items()}
        company_data = {reverse_mapping.get(k, k): v for k, v in company_db_data.items()}

        logger.info(f"开始处理技术需求: {file_metadata.original_name}")

        # 创建技术需求回复处理器
        responder = TechResponder()

        # 生成输出文件路径
        output_dir = ensure_dir(config.get_path('output'))
        # 使用新的文件命名规则：{项目名称}_技术方案_{时间戳}.docx
        # 对于技术需求回复，使用原文件名作为项目名称（因为没有单独的project_name字段）
        base_name = Path(file_metadata.original_name).stem
        output_filename = generate_output_filename(base_name, "技术方案")
        output_path = output_dir / output_filename

        # 处理技术需求
        result_stats = responder.process_tech_requirements(
            str(requirements_path),
            str(output_path),
            company_data,
            response_strategy
        )

        if result_stats.get('success'):
            logger.info(f"技术需求处理成功: {result_stats.get('message')}")
            result = {
                'success': True,
                'message': result_stats.get('message', '技术需求处理完成'),
                'output_file': str(output_path),
                'download_url': f'/download/{os.path.basename(output_path)}',
                'stats': {
                    'requirements_count': result_stats.get('requirements_count', 0),
                    'responses_count': result_stats.get('responses_count', 0)
                }
            }
        else:
            logger.error(f"技术需求处理失败: {result_stats.get('error')}")
            result = {
                'success': False,
                'error': result_stats.get('error', '处理失败'),
                'message': result_stats.get('message', '技术需求处理失败')
            }

        return jsonify(result)

    except Exception as e:
        logger.error(f"技术需求处理异常: {e}")
        return jsonify(format_error_response(e))


__all__ = ['api_tech_bp']
