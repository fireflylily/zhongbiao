#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标信息提取API蓝图
处理招标文件的信息提取和分步处理
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config, format_error_response
from web.shared.instances import get_kb_manager

# 创建蓝图
api_tender_bp = Blueprint('api_tender', __name__)

# 日志记录器
logger = get_module_logger("web.api_tender")

# 获取配置和知识库管理器
config = get_config()
kb_manager = get_kb_manager()

# 检查招标信息提取模块可用性
TENDER_INFO_AVAILABLE = False
try:
    from modules.tender_info.extractor import TenderInfoExtractor
    TENDER_INFO_AVAILABLE = True
except ImportError:
    pass


def enrich_qualification_with_company_status(tender_requirements: dict, company_id: str = None) -> dict:
    """
    整合招标资质要求与公司资质上传状态

    Args:
        tender_requirements: 招标文件中提取的资质要求
        company_id: 公司ID，如果为None则只返回招标要求信息

    Returns:
        dict: 包含资质要求和公司上传状态的整合数据
    """
    logger.info(f"开始整合资质数据，company_id: {company_id}")

    # 获取所有资质类型定义（包括活跃和非活跃的）
    all_qualifications = kb_manager.get_qualification_types(include_inactive=True)

    # 初始化结果结构
    enriched_data = {
        'summary': {
            'total_types': len(all_qualifications),
            'required_count': 0,
            'uploaded_count': 0,
            'missing_count': 0
        },
        'qualifications': {}
    }

    # 获取公司已上传的资质（如果提供了company_id）
    company_qualifications = {}
    if company_id:
        try:
            company_id_int = int(company_id)
            uploaded_quals = kb_manager.get_company_qualifications(company_id_int)

            # 按qualification_key建立索引
            for qual in uploaded_quals:
                qual_key = qual.get('qualification_key')
                if qual_key:
                    company_qualifications[qual_key] = {
                        'uploaded': True,
                        'file_path': qual.get('file_path'),
                        'file_size': qual.get('file_size'),
                        'uploaded_at': qual.get('uploaded_at'),
                        'expire_date': qual.get('expire_date')
                    }

            logger.info(f"公司 {company_id} 已上传资质数: {len(company_qualifications)}")
        except Exception as e:
            logger.error(f"获取公司资质失败: {e}")

    # 处理每个资质类型
    for qual_type in all_qualifications:
        qual_key = qual_type['qualification_key']

        # 从招标要求中查找该资质
        tender_qual = tender_requirements.get('qualifications', {}).get(qual_key, {})

        # 是否在招标文件中要求
        is_required = bool(tender_qual.get('required', False))

        # 构建整合数据
        qual_data = {
            # 基础信息
            'qualification_key': qual_key,
            'qualification_name': qual_type['qualification_name'],
            'category': qual_type['category'],

            # 招标要求
            'required_by_tender': is_required,
            'tender_description': tender_qual.get('description', ''),

            # 公司上传状态
            'uploaded_by_company': qual_key in company_qualifications,
            'upload_info': company_qualifications.get(qual_key, {}),

            # 状态判定
            'status': 'missing' if (is_required and qual_key not in company_qualifications) else
                     'uploaded' if qual_key in company_qualifications else
                     'not_required'
        }

        enriched_data['qualifications'][qual_key] = qual_data

        # 更新统计
        if is_required:
            enriched_data['summary']['required_count'] += 1
            if qual_key not in company_qualifications:
                enriched_data['summary']['missing_count'] += 1

        if qual_key in company_qualifications:
            enriched_data['summary']['uploaded_count'] += 1

    logger.info(f"资质整合完成 - 总数: {enriched_data['summary']['total_types']}, "
                f"要求: {enriched_data['summary']['required_count']}, "
                f"已传: {enriched_data['summary']['uploaded_count']}, "
                f"缺失: {enriched_data['summary']['missing_count']}")

    return enriched_data


@api_tender_bp.route('/extract-tender-info', methods=['POST'])
def extract_tender_info():
    """
    招标信息提取API (一体化流程)

    设计架构说明：
    1. 当前实现：直接文件上传 → AI处理 → 返回结果 (一体化流程)
    2. 目标架构：统一存储 → AI处理 → 结果存储 (分离式流程)

    POST参数:
    - file: 招标文档文件（multipart/form-data）
    - api_key: AI服务API密钥（可选，优先使用此值，否则使用默认配置）

    Returns:
        {
            "success": true,
            "data": {...},  # 提取的招标信息
            "message": "招标信息提取成功"
        }
    """
    if not TENDER_INFO_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '招标信息提取模块不可用'
        })

    try:
        # 获取上传的文件
        if 'file' not in request.files:
            raise ValueError("没有选择文件")

        file = request.files['file']
        if file.filename == '':
            raise ValueError("文件名为空")

        # 获取API密钥
        api_key = request.form.get('api_key') or config.get_default_api_key()
        if not api_key:
            raise ValueError("API密钥未配置。请在环境变量中设置DEFAULT_API_KEY或在页面中输入API密钥")

        # 保存上传文件 - 使用统一存储服务
        from core.storage_service import storage_service
        file_metadata = storage_service.store_file(
            file_obj=file,
            original_name=file.filename,
            category='tender_documents',
            business_type='tender_info_extraction'
        )

        logger.info(f"开始提取招标信息: {file_metadata.original_name}")

        # 执行信息提取
        extractor = TenderInfoExtractor(api_key=api_key)
        result = extractor.process_document(file_metadata.file_path)

        logger.info("招标信息提取完成")
        return jsonify({
            'success': True,
            'data': result,
            'message': '招标信息提取成功'
        })

    except Exception as e:
        logger.error(f"招标信息提取失败: {e}")
        return jsonify(format_error_response(e))


@api_tender_bp.route('/extract-tender-info-step', methods=['POST'])
def extract_tender_info_step():
    """
    分步招标信息提取API

    支持分步骤提取招标信息，允许用户分阶段获取数据

    POST参数 (支持JSON和FormData):
    - step: 步骤编号 ('1'=基本信息, '2'=资质要求, '3'=技术评分)
    - file_path: 招标文档路径
    - ai_model: AI模型名称（可选，默认'gpt-4o-mini'）
    - api_key: API密钥（可选）
    - company_id: 公司ID（步骤2需要，用于资质对比）

    Returns:
        {
            "success": true,
            "step": 1,
            "data": {...},
            "message": "基本信息提取成功"
        }
    """
    if not TENDER_INFO_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '招标信息提取模块不可用'
        })

    try:
        # 支持两种格式：JSON 和 FormData
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            step = data.get('step', '1')
            file_path = data.get('file_path', '')
            ai_model = data.get('ai_model', 'gpt-4o-mini')
            api_key = data.get('api_key') or config.get_default_api_key()
        else:
            # FormData 格式
            step = request.form.get('step', '1')
            file_path = request.form.get('file_path', '')
            ai_model = request.form.get('ai_model', 'gpt-4o-mini')
            api_key = request.form.get('api_key') or config.get_default_api_key()

        if not file_path or not Path(file_path).exists():
            raise ValueError("文件路径无效")

        if not api_key:
            raise ValueError("API密钥未配置。请在环境变量中设置DEFAULT_API_KEY或在页面中输入API密钥")

        # 使用选择的AI模型创建提取器
        extractor = TenderInfoExtractor(api_key=api_key, model_name=ai_model)

        if step == '1':
            # 第一步：提取基本信息
            text = extractor.read_document(file_path)
            basic_info = extractor.extract_basic_info(text)

            return jsonify({
                'success': True,
                'step': 1,
                'data': basic_info,
                'message': '基本信息提取成功'
            })

        elif step == '2':
            # 第二步：提取资质要求并对比公司资质状态
            text = extractor.read_document(file_path)
            tender_requirements = extractor.extract_qualification_requirements(text)

            # 获取公司ID - 支持FormData和JSON两种方式
            company_id = None
            if request.content_type and 'multipart/form-data' in request.content_type:
                company_id = request.form.get('company_id')
            elif request.is_json:
                company_id = request.get_json().get('company_id')
            else:
                # 尝试从form中获取
                company_id = request.form.get('company_id')

            logger.info(f"处理资质要求 - 公司ID: {company_id}, 类型: {type(company_id)}")

            # 确保company_id是整数或None
            if company_id:
                try:
                    company_id = int(company_id)
                except (ValueError, TypeError):
                    logger.warning(f"无效的公司ID: {company_id}")
                    company_id = None

            # 整合公司资质状态
            enriched_data = enrich_qualification_with_company_status(tender_requirements, company_id)

            logger.info(f"资质要求提取完成，返回数据包含 {len(enriched_data.get('qualifications', {}))} 项资质")

            return jsonify({
                'success': True,
                'step': 2,
                'data': enriched_data,
                'message': '资质要求提取成功'
            })

        elif step == '3':
            # 第三步：提取技术评分
            text = extractor.read_document(file_path)
            scoring_info = extractor.extract_technical_scoring(text)

            return jsonify({
                'success': True,
                'step': 3,
                'data': scoring_info,
                'message': '技术评分提取成功'
            })

        else:
            raise ValueError(f"无效的步骤: {step}")

    except Exception as e:
        logger.error(f"分步招标信息提取失败: {e}")
        return jsonify(format_error_response(e))


__all__ = ['api_tender_bp']
