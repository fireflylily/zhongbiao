#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心API蓝图
提供健康检查、配置查询等核心系统API
"""

import sys
from pathlib import Path
from datetime import datetime
from flask import Blueprint, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config, format_error_response

# 创建蓝图
api_core_bp = Blueprint('api_core', __name__, url_prefix='/api')

# 日志记录器
logger = get_module_logger("web.api_core")

# 获取配置
config = get_config()

# 检查各个模块的可用性
TENDER_INFO_AVAILABLE = False
BUSINESS_RESPONSE_AVAILABLE = False
POINT_TO_POINT_AVAILABLE = False
TECH_RESPONDER_AVAILABLE = False

try:
    from modules.tender_info.extractor import TenderInfoExtractor
    TENDER_INFO_AVAILABLE = True
except ImportError:
    pass

try:
    from modules.business_response.processor import BusinessResponseProcessor, PointToPointProcessor
    BUSINESS_RESPONSE_AVAILABLE = True
    POINT_TO_POINT_AVAILABLE = True  # 保持向后兼容
except ImportError:
    pass

try:
    from modules.point_to_point.tech_responder import TechResponder
    TECH_RESPONDER_AVAILABLE = True
except ImportError:
    pass


@api_core_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    获取CSRF token（兼容性端点）

    注意: 当前系统已禁用CSRF保护（内部系统），此端点返回空token以保持前端兼容性

    Returns:
        JSON响应 {"csrf_token": ""}
    """
    return jsonify({'csrf_token': ''})


@api_core_bp.route('/health')
def health_check():
    """
    健康检查API

    返回系统健康状态和各模块可用性

    Returns:
        {
            "status": "healthy",
            "version": "2.1.0",
            "timestamp": "2025-10-19T20:00:00",
            "tender_info_available": true,
            "business_response_available": true,
            "point_to_point_available": true,
            "tech_responder_available": true,
            "vector_search_available": true,
            "knowledge_base_available": true
        }
    """
    # 检查向量搜索功能是否可用
    vector_search_available = False
    try:
        from modules.vector_search_api import vector_search_api
        vector_search_available = True
    except ImportError:
        pass

    return jsonify({
        'status': 'healthy',
        'version': '2.1.0',  # 版本升级
        'timestamp': datetime.now().isoformat(),
        'tender_info_available': TENDER_INFO_AVAILABLE,
        'business_response_available': BUSINESS_RESPONSE_AVAILABLE,
        'point_to_point_available': POINT_TO_POINT_AVAILABLE,  # 向后兼容
        'tech_responder_available': TECH_RESPONDER_AVAILABLE,
        'vector_search_available': vector_search_available,
        'knowledge_base_available': True  # 知识库功能总是可用
    })


@api_core_bp.route('/config')
def get_api_config():
    """
    获取API配置信息

    返回安全的配置信息（已过滤敏感数据）

    Returns:
        {
            "success": true,
            "config": {
                "api_endpoint": "...",
                "model_name": "...",
                "max_completion_tokens": 4096,
                "has_api_key": true
            }
        }
    """
    try:
        api_config = config.get_api_config()

        # 隐藏敏感信息
        safe_config = {
            'api_endpoint': api_config['api_endpoint'],
            'model_name': api_config['model_name'],
            'max_completion_tokens': api_config['max_tokens'],
            'has_api_key': bool(api_config.get('api_key'))
        }

        return jsonify({'success': True, 'config': safe_config})

    except Exception as e:
        logger.error(f"获取API配置失败: {e}")
        return jsonify(format_error_response(e))


__all__ = ['api_core_bp']
