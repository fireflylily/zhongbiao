#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业征信API蓝图
提供企业信息查询功能(基于第三方征信API)
"""

from pathlib import Path
from flask import Blueprint, request, jsonify

# 导入公共组件
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config
from web.middleware.permission import require_auth
from services.enterprise_credit_service import create_enterprise_credit_service

# 创建logger
logger = get_module_logger('api_enterprise_credit')

# 创建蓝图
api_enterprise_credit_bp = Blueprint('api_enterprise_credit', __name__, url_prefix='/api')

# 获取配置
config = get_config()

# 创建企业征信服务实例
try:
    enterprise_credit_service = create_enterprise_credit_service(config)
    logger.info("企业征信服务初始化成功")
except Exception as e:
    logger.error(f"企业征信服务初始化失败: {e}")
    enterprise_credit_service = None


@api_enterprise_credit_bp.route('/enterprise/search', methods=['POST'])
@require_auth
def search_enterprises():
    """
    搜索企业列表

    请求体:
    {
        "keyword": "企业名称或统一社会信用代码"
    }

    响应:
    {
        "success": true,
        "data": [
            {
                "company_ss_id": "123456",
                "company_name": "示例企业",
                "usc_code": "统一社会信用代码"
            }
        ]
    }
    """
    try:
        # 检查服务是否可用
        if not enterprise_credit_service:
            return jsonify({
                'success': False,
                'error': '企业征信服务未配置或初始化失败'
            }), 503

        # 获取请求参数
        data = request.get_json()
        if not data or 'keyword' not in data:
            return jsonify({
                'success': False,
                'error': '请提供搜索关键词'
            }), 400

        keyword = data['keyword'].strip()
        if not keyword:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400

        # 关键词长度限制
        if len(keyword) < 2:
            return jsonify({
                'success': False,
                'error': '搜索关键词至少需要2个字符'
            }), 400

        # 调用企业征信服务
        try:
            enterprises = enterprise_credit_service.search_enterprises(keyword)

            logger.info(f"搜索企业成功: 关键词={keyword}, 结果数={len(enterprises)}")
            return jsonify({
                'success': True,
                'data': enterprises,
                'total': len(enterprises)
            })

        except Exception as e:
            logger.error(f"调用第三方API失败: {e}")
            return jsonify({
                'success': False,
                'error': f'查询企业信息失败: {str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"搜索企业失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_enterprise_credit_bp.route('/enterprise/detail/<company_ss_id>')
@require_auth
def get_enterprise_detail(company_ss_id):
    """
    获取企业详情

    路径参数:
    - company_ss_id: 企业ID (足迹ID)

    响应:
    {
        "success": true,
        "data": {
            "company_ss_id": "123456",
            "company_name": "示例企业",
            "legal_person": "张三",
            "reg_addr": "北京市...",
            ...
        }
    }
    """
    try:
        # 检查服务是否可用
        if not enterprise_credit_service:
            return jsonify({
                'success': False,
                'error': '企业征信服务未配置或初始化失败'
            }), 503

        # 参数验证
        if not company_ss_id or not company_ss_id.strip():
            return jsonify({
                'success': False,
                'error': '企业ID不能为空'
            }), 400

        # 调用企业征信服务
        try:
            detail = enterprise_credit_service.get_enterprise_detail(company_ss_id.strip())

            if detail:
                logger.info(f"获取企业详情成功: 企业ID={company_ss_id}")
                return jsonify({
                    'success': True,
                    'data': detail
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '未找到企业信息'
                }), 404

        except Exception as e:
            logger.error(f"调用第三方API失败: {e}")
            return jsonify({
                'success': False,
                'error': f'获取企业详情失败: {str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"获取企业详情失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 导出蓝图
__all__ = ['api_enterprise_credit_bp']
