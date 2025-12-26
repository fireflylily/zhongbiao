#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品能力管理API蓝图

提供产品能力索引和标签的管理功能：
1. 能力标签 CRUD
2. 能力索引查询和管理
3. 能力提取触发
4. 需求匹配分析
"""

from pathlib import Path
from flask import Blueprint, request, jsonify, g

# 导入公共组件
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from web.middleware.permission import require_auth

# 创建logger
logger = get_module_logger('api_capability')

# 创建蓝图
api_capability_bp = Blueprint('api_capability', __name__, url_prefix='/api/capability')


def get_tag_manager():
    """获取标签管理器实例"""
    from modules.product_capability import TagManager
    return TagManager()


def get_capability_extractor():
    """获取能力提取器实例"""
    from modules.product_capability import CapabilityExtractor
    return CapabilityExtractor()


def get_capability_searcher():
    """获取能力搜索器实例"""
    from modules.product_capability import CapabilitySearcher
    return CapabilitySearcher()


def get_product_match_agent():
    """获取产品匹配智能体"""
    from modules.outline_generator.agents import ProductMatchAgent
    return ProductMatchAgent()


# ===================
# 能力标签管理 API
# ===================

@api_capability_bp.route('/tags', methods=['GET'])
def list_capability_tags():
    """
    获取企业的所有能力标签

    Query params:
        company_id: 企业ID（必填）
        include_children: 是否包含子标签（默认true）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        include_children = request.args.get('include_children', 'true').lower() == 'true'

        manager = get_tag_manager()
        tags = manager.get_tags_tree(company_id)

        # 如果不需要子标签，展平结构
        if not include_children:
            flat_tags = []
            for tag in tags:
                flat_tags.append({
                    'tag_id': tag['tag_id'],
                    'tag_name': tag['tag_name'],
                    'tag_code': tag['tag_code'],
                    'description': tag.get('description'),
                    'parent_tag_id': tag.get('parent_tag_id')
                })
            tags = flat_tags

        return jsonify({
            'success': True,
            'data': tags,
            'total': len(tags)
        })

    except Exception as e:
        logger.error(f"获取能力标签列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/tags', methods=['POST'])
@require_auth
def create_capability_tag():
    """
    创建新的能力标签

    Body:
        company_id: 企业ID
        tag_name: 标签名称
        tag_code: 标签代码
        parent_tag_id: 父标签ID（可选）
        description: 描述（可选）
        example_keywords: 示例关键词列表（可选）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供标签信息'}), 400

        company_id = data.get('company_id')
        tag_name = data.get('tag_name', '').strip()
        tag_code = data.get('tag_code', '').strip()

        if not company_id or not tag_name or not tag_code:
            return jsonify({'success': False, 'error': '企业ID、标签名称和代码不能为空'}), 400

        manager = get_tag_manager()
        tag_id = manager.create_tag(
            company_id=company_id,
            tag_name=tag_name,
            tag_code=tag_code,
            parent_tag_id=data.get('parent_tag_id'),
            description=data.get('description'),
            example_keywords=data.get('example_keywords'),
            tag_order=data.get('tag_order', 999)
        )

        logger.info(f"创建能力标签成功: {tag_name} (ID: {tag_id})")
        return jsonify({
            'success': True,
            'data': {'tag_id': tag_id},
            'message': '标签创建成功'
        })

    except Exception as e:
        error_msg = str(e)
        if '已存在' in error_msg or 'UNIQUE' in error_msg:
            return jsonify({'success': False, 'error': '标签代码已存在'}), 400
        logger.error(f"创建能力标签失败: {e}")
        return jsonify({'success': False, 'error': error_msg}), 500


@api_capability_bp.route('/tags/<int:tag_id>', methods=['GET'])
def get_capability_tag(tag_id):
    """获取指定能力标签详情"""
    try:
        manager = get_tag_manager()
        tag = manager.get_tag(tag_id)

        if not tag:
            return jsonify({'success': False, 'error': '标签不存在'}), 404

        return jsonify({'success': True, 'data': tag})

    except Exception as e:
        logger.error(f"获取能力标签详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/tags/<int:tag_id>', methods=['PUT'])
@require_auth
def update_capability_tag(tag_id):
    """更新能力标签"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供标签信息'}), 400

        manager = get_tag_manager()

        # 检查标签是否存在
        existing = manager.get_tag(tag_id)
        if not existing:
            return jsonify({'success': False, 'error': '标签不存在'}), 404

        success = manager.update_tag(
            tag_id=tag_id,
            tag_name=data.get('tag_name'),
            description=data.get('description'),
            example_keywords=data.get('example_keywords'),
            tag_order=data.get('tag_order'),
            is_active=data.get('is_active')
        )

        if success:
            logger.info(f"更新能力标签成功: ID={tag_id}")
            return jsonify({'success': True, 'message': '标签更新成功'})
        else:
            return jsonify({'success': False, 'error': '更新失败'}), 500

    except Exception as e:
        logger.error(f"更新能力标签失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@require_auth
def delete_capability_tag(tag_id):
    """删除能力标签（软删除）"""
    try:
        manager = get_tag_manager()

        # 检查标签是否存在
        existing = manager.get_tag(tag_id)
        if not existing:
            return jsonify({'success': False, 'error': '标签不存在'}), 404

        success = manager.delete_tag(tag_id)

        if success:
            logger.info(f"删除能力标签成功: ID={tag_id}")
            return jsonify({'success': True, 'message': '标签删除成功'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500

    except Exception as e:
        logger.error(f"删除能力标签失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/tags/init-defaults', methods=['POST'])
@require_auth
def init_default_tags():
    """
    为企业初始化默认标签

    Body:
        company_id: 企业ID
    """
    try:
        data = request.get_json()
        company_id = data.get('company_id') if data else None

        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        manager = get_tag_manager()
        tag_ids = manager.init_default_tags(company_id)

        logger.info(f"初始化默认标签成功: 企业ID={company_id}, 标签数={len(tag_ids)}")
        return jsonify({
            'success': True,
            'data': {'tag_ids': tag_ids},
            'message': f'成功初始化 {len(tag_ids)} 个默认标签'
        })

    except Exception as e:
        logger.error(f"初始化默认标签失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================
# 能力索引管理 API
# ===================

@api_capability_bp.route('/capabilities', methods=['GET'])
def list_capabilities():
    """
    获取企业的产品能力列表

    Query params:
        company_id: 企业ID（必填）
        tag_id: 按标签筛选（可选）
        verified_only: 只返回已审核的（可选，默认false）
        page: 页码（默认1）
        page_size: 每页数量（默认20）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        tag_id = request.args.get('tag_id', type=int)
        verified_only = request.args.get('verified_only', 'false').lower() == 'true'

        searcher = get_capability_searcher()
        capabilities = searcher.get_company_capabilities(
            company_id=company_id,
            tag_id=tag_id,
            verified_only=verified_only
        )

        # 移除 embedding 字段（太大）
        for cap in capabilities:
            if 'capability_embedding' in cap:
                del cap['capability_embedding']

        return jsonify({
            'success': True,
            'data': capabilities,
            'total': len(capabilities)
        })

    except Exception as e:
        logger.error(f"获取能力列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/capabilities/stats', methods=['GET'])
def get_capability_stats():
    """
    获取企业能力统计信息

    Query params:
        company_id: 企业ID（必填）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        searcher = get_capability_searcher()
        stats = searcher.get_capability_stats(company_id)

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"获取能力统计失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/capabilities/extract', methods=['POST'])
@require_auth
def extract_capabilities():
    """
    从文档中提取产品能力

    Body:
        doc_id: 文档ID
        company_id: 企业ID
        tag_id: 关联的能力标签ID（可选）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供参数'}), 400

        doc_id = data.get('doc_id')
        company_id = data.get('company_id')

        if not doc_id or not company_id:
            return jsonify({'success': False, 'error': '文档ID和企业ID不能为空'}), 400

        extractor = get_capability_extractor()
        result = extractor.extract_from_document(
            doc_id=doc_id,
            company_id=company_id,
            tag_id=data.get('tag_id')
        )

        logger.info(f"能力提取完成: 文档ID={doc_id}, 提取={result['capabilities_extracted']}, 保存={result['capabilities_saved']}")
        return jsonify({
            'success': True,
            'data': result,
            'message': f"成功提取 {result['capabilities_saved']} 个能力"
        })

    except Exception as e:
        logger.error(f"能力提取失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/capabilities/search', methods=['POST'])
def search_capabilities():
    """
    搜索匹配的产品能力

    Body:
        query: 搜索查询（需求描述）
        company_id: 企业ID
        tag_id: 限定能力标签（可选）
        method: 搜索方法 - semantic/keyword/hybrid（默认hybrid）
        top_k: 返回数量（默认10）
        min_score: 最小匹配分数（默认0.5）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供参数'}), 400

        query = data.get('query', '').strip()
        company_id = data.get('company_id')

        if not query or not company_id:
            return jsonify({'success': False, 'error': '查询内容和企业ID不能为空'}), 400

        searcher = get_capability_searcher()
        results = searcher.search(
            query=query,
            company_id=company_id,
            tag_id=data.get('tag_id'),
            method=data.get('method', 'hybrid'),
            top_k=data.get('top_k', 10),
            min_score=data.get('min_score', 0.5)
        )

        # 移除 embedding 字段
        for r in results:
            if 'capability_embedding' in r:
                del r['capability_embedding']

        return jsonify({
            'success': True,
            'data': results,
            'total': len(results)
        })

    except Exception as e:
        logger.error(f"能力搜索失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================
# 需求匹配分析 API
# ===================

@api_capability_bp.route('/match', methods=['POST'])
def match_requirements():
    """
    分析招标需求与产品能力的匹配情况

    Body:
        tender_doc: 招标文件内容
        company_id: 企业ID
        extract_requirements: 是否使用AI提取需求（默认true）
        match_threshold: 匹配阈值（默认0.6）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供参数'}), 400

        tender_doc = data.get('tender_doc', '').strip()
        company_id = data.get('company_id')

        if not tender_doc or not company_id:
            return jsonify({'success': False, 'error': '招标文件内容和企业ID不能为空'}), 400

        agent = get_product_match_agent()
        result = agent.analyze_and_match(
            tender_doc=tender_doc,
            company_id=company_id,
            extract_requirements=data.get('extract_requirements', True),
            match_threshold=data.get('match_threshold', 0.6)
        )

        logger.info(f"需求匹配分析完成: 企业ID={company_id}, 覆盖率={result['summary']['coverage_rate']}")
        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"需求匹配分析失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_capability_bp.route('/match/batch', methods=['POST'])
def match_requirements_batch():
    """
    批量匹配需求列表

    Body:
        requirements: 需求列表（字符串数组）
        company_id: 企业ID
        tender_project_id: 招标项目ID（可选，用于记录历史）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供参数'}), 400

        requirements = data.get('requirements', [])
        company_id = data.get('company_id')

        if not requirements or not company_id:
            return jsonify({'success': False, 'error': '需求列表和企业ID不能为空'}), 400

        searcher = get_capability_searcher()
        result = searcher.match_requirements_batch(
            requirements=requirements,
            company_id=company_id,
            tender_project_id=data.get('tender_project_id')
        )

        logger.info(f"批量需求匹配完成: 企业ID={company_id}, 需求数={len(requirements)}, 覆盖率={result['coverage_rate']}")
        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"批量需求匹配失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 导出蓝图
__all__ = ['api_capability_bp']
