#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型管理API蓝图
提供AI模型列表查询、配置验证等API
"""

import sys
from pathlib import Path
from flask import Blueprint, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger

# 创建蓝图
api_models_bp = Blueprint('api_models', __name__, url_prefix='/api')

# 日志记录器
logger = get_module_logger("web.api_models")


@api_models_bp.route('/models', methods=['GET'])
def get_available_models():
    """
    获取可用的AI模型列表

    Returns:
        {
            "success": true,
            "models": [...],
            "count": 10
        }
    """
    try:
        from common.llm_client import get_available_models

        models = get_available_models()

        # 添加模型状态检查
        for model in models:
            try:
                # 这里可以添加模型可用性检查的逻辑
                model['status'] = 'available' if model['has_api_key'] else 'no_api_key'
                model['status_message'] = '已配置' if model['has_api_key'] else '未配置API密钥'
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning(f"处理模型状态时出错: {e}")
                model['status'] = 'unknown'
                model['status_message'] = '状态未知'

        logger.info(f"获取模型列表成功，共 {len(models)} 个模型")
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        })

    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_models_bp.route('/models/<model_name>/validate', methods=['POST'])
def validate_model_config(model_name):
    """
    验证指定模型的配置

    Args:
        model_name: 模型名称

    Returns:
        {
            "success": true,
            "validation": {
                "valid": true,
                "message": "..."
            }
        }
    """
    try:
        from common.llm_client import create_llm_client

        # 创建模型客户端并验证配置
        client = create_llm_client(model_name)
        validation_result = client.validate_config()

        logger.info(f"模型 {model_name} 配置验证结果: {validation_result['valid']}")
        return jsonify({
            'success': True,
            'validation': validation_result
        })

    except Exception as e:
        logger.error(f"验证模型 {model_name} 配置失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


__all__ = ['api_models_bp']
