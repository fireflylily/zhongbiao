#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品分类管理API蓝图
处理产品分类和分类项的CRUD操作
"""

from pathlib import Path
from flask import Blueprint, request, jsonify

# 导入公共组件
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, format_error_response
from web.shared.instances import get_kb_manager
from web.middleware.permission import require_auth

# 创建logger
logger = get_module_logger('api_product_categories')

# 创建蓝图
api_product_categories_bp = Blueprint('api_product_categories', __name__, url_prefix='/api')

# 获取知识库管理器实例
kb_manager = get_kb_manager()


# ===================
# 产品分类管理API
# ===================

@api_product_categories_bp.route('/product-categories')
def list_product_categories():
    """
    获取所有产品分类及其项
    返回格式：
    [
        {
            "category_id": 1,
            "category_name": "网络基建类",
            "category_code": "network_infra",
            "items": [
                {"item_id": 1, "item_name": "基站", ...},
                ...
            ]
        },
        ...
    ]
    """
    try:
        # 获取所有分类
        categories_query = """
            SELECT
                category_id,
                category_name,
                category_code,
                category_description,
                category_order,
                is_active
            FROM product_categories
            WHERE is_active = 1
            ORDER BY category_order, category_id
        """
        categories = kb_manager.db.execute_query(categories_query)

        # 获取所有分类项
        items_query = """
            SELECT
                item_id,
                category_id,
                item_name,
                item_code,
                item_description,
                item_order,
                is_active
            FROM product_category_items
            WHERE is_active = 1
            ORDER BY item_order, item_id
        """
        items = kb_manager.db.execute_query(items_query)

        # 组织数据结构
        result = []
        for category in categories:
            category_data = {
                'category_id': category['category_id'],
                'category_name': category['category_name'],
                'category_code': category['category_code'],
                'category_description': category.get('category_description'),
                'category_order': category.get('category_order'),
                'items': []
            }

            # 添加属于该分类的项
            for item in items:
                if item['category_id'] == category['category_id']:
                    category_data['items'].append({
                        'item_id': item['item_id'],
                        'item_name': item['item_name'],
                        'item_code': item.get('item_code'),
                        'item_description': item.get('item_description'),
                        'item_order': item.get('item_order')
                    })

            result.append(category_data)

        logger.info(f"获取产品分类列表成功，共 {len(result)} 个分类")
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })

    except Exception as e:
        logger.error(f"获取产品分类列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_product_categories_bp.route('/product-categories/<int:category_id>')
def get_product_category(category_id):
    """获取指定产品分类的详细信息"""
    try:
        # 获取分类信息
        category_query = """
            SELECT
                category_id,
                category_name,
                category_code,
                category_description,
                category_order,
                is_active,
                created_at,
                updated_at
            FROM product_categories
            WHERE category_id = ?
        """
        categories = kb_manager.db.execute_query(category_query, [category_id])

        if not categories:
            return jsonify({'success': False, 'error': '分类不存在'}), 404

        category = categories[0]

        # 获取分类项
        items_query = """
            SELECT
                item_id,
                item_name,
                item_code,
                item_description,
                item_order,
                is_active
            FROM product_category_items
            WHERE category_id = ?
            ORDER BY item_order, item_id
        """
        items = kb_manager.db.execute_query(items_query, [category_id])

        result = {
            'category_id': category['category_id'],
            'category_name': category['category_name'],
            'category_code': category['category_code'],
            'category_description': category.get('category_description'),
            'category_order': category.get('category_order'),
            'is_active': category.get('is_active'),
            'created_at': category.get('created_at'),
            'updated_at': category.get('updated_at'),
            'items': [
                {
                    'item_id': item['item_id'],
                    'item_name': item['item_name'],
                    'item_code': item.get('item_code'),
                    'item_description': item.get('item_description'),
                    'item_order': item.get('item_order'),
                    'is_active': item.get('is_active')
                }
                for item in items
            ]
        }

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        logger.error(f"获取产品分类详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_product_categories_bp.route('/product-categories', methods=['POST'])
@require_auth
def create_product_category():
    """创建新的产品分类"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': '请提供分类信息'}), 400

        category_name = data.get('category_name', '').strip()
        category_code = data.get('category_code', '').strip()

        if not category_name or not category_code:
            return jsonify({'success': False, 'error': '分类名称和代码不能为空'}), 400

        # 检查分类代码是否已存在
        existing = kb_manager.db.execute_query(
            "SELECT category_id FROM product_categories WHERE category_code = ?",
            [category_code]
        )
        if existing:
            return jsonify({'success': False, 'error': '分类代码已存在'}), 400

        # 插入新分类
        insert_query = """
            INSERT INTO product_categories
            (category_name, category_code, category_description, category_order, is_active)
            VALUES (?, ?, ?, ?, ?)
        """
        kb_manager.db.execute_query(insert_query, [
            category_name,
            category_code,
            data.get('category_description', ''),
            data.get('category_order', 999),
            data.get('is_active', True)
        ])

        # 获取新创建的分类ID
        result = kb_manager.db.execute_query(
            "SELECT category_id FROM product_categories WHERE category_code = ?",
            [category_code]
        )

        category_id = result[0]['category_id'] if result else None

        logger.info(f"创建产品分类成功: {category_name} (ID: {category_id})")
        return jsonify({
            'success': True,
            'data': {'category_id': category_id},
            'message': '分类创建成功'
        })

    except Exception as e:
        logger.error(f"创建产品分类失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_product_categories_bp.route('/product-categories/<int:category_id>', methods=['PUT'])
@require_auth
def update_product_category(category_id):
    """更新产品分类"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': '请提供分类信息'}), 400

        # 检查分类是否存在
        existing = kb_manager.db.execute_query(
            "SELECT category_id FROM product_categories WHERE category_id = ?",
            [category_id]
        )
        if not existing:
            return jsonify({'success': False, 'error': '分类不存在'}), 404

        # 构建更新语句
        update_fields = []
        params = []

        if 'category_name' in data:
            update_fields.append('category_name = ?')
            params.append(data['category_name'])

        if 'category_description' in data:
            update_fields.append('category_description = ?')
            params.append(data['category_description'])

        if 'category_order' in data:
            update_fields.append('category_order = ?')
            params.append(data['category_order'])

        if 'is_active' in data:
            update_fields.append('is_active = ?')
            params.append(data['is_active'])

        if not update_fields:
            return jsonify({'success': False, 'error': '没有需要更新的字段'}), 400

        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        params.append(category_id)

        update_query = f"""
            UPDATE product_categories
            SET {', '.join(update_fields)}
            WHERE category_id = ?
        """

        kb_manager.db.execute_query(update_query, params)

        logger.info(f"更新产品分类成功: ID={category_id}")
        return jsonify({'success': True, 'message': '分类更新成功'})

    except Exception as e:
        logger.error(f"更新产品分类失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_product_categories_bp.route('/product-categories/<int:category_id>', methods=['DELETE'])
@require_auth
def delete_product_category(category_id):
    """删除产品分类（软删除）"""
    try:
        # 检查分类是否存在
        existing = kb_manager.db.execute_query(
            "SELECT category_id FROM product_categories WHERE category_id = ?",
            [category_id]
        )
        if not existing:
            return jsonify({'success': False, 'error': '分类不存在'}), 404

        # 软删除：设置is_active为False
        kb_manager.db.execute_query(
            "UPDATE product_categories SET is_active = 0 WHERE category_id = ?",
            [category_id]
        )

        # 同时软删除该分类下的所有项
        kb_manager.db.execute_query(
            "UPDATE product_category_items SET is_active = 0 WHERE category_id = ?",
            [category_id]
        )

        logger.info(f"删除产品分类成功: ID={category_id}")
        return jsonify({'success': True, 'message': '分类删除成功'})

    except Exception as e:
        logger.error(f"删除产品分类失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================
# 产品分类项管理API
# ===================

@api_product_categories_bp.route('/product-categories/<int:category_id>/items', methods=['POST'])
@require_auth
def create_category_item(category_id):
    """创建新的分类项"""
    try:
        # 检查分类是否存在
        existing_category = kb_manager.db.execute_query(
            "SELECT category_id FROM product_categories WHERE category_id = ?",
            [category_id]
        )
        if not existing_category:
            return jsonify({'success': False, 'error': '分类不存在'}), 404

        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': '请提供项信息'}), 400

        item_name = data.get('item_name', '').strip()

        if not item_name:
            return jsonify({'success': False, 'error': '项名称不能为空'}), 400

        # 检查项名称是否已存在
        existing = kb_manager.db.execute_query(
            "SELECT item_id FROM product_category_items WHERE category_id = ? AND item_name = ?",
            [category_id, item_name]
        )
        if existing:
            return jsonify({'success': False, 'error': '项名称已存在'}), 400

        # 插入新项
        insert_query = """
            INSERT INTO product_category_items
            (category_id, item_name, item_code, item_description, item_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        kb_manager.db.execute_query(insert_query, [
            category_id,
            item_name,
            data.get('item_code', ''),
            data.get('item_description', ''),
            data.get('item_order', 999),
            data.get('is_active', True)
        ])

        # 获取新创建的项ID
        result = kb_manager.db.execute_query(
            "SELECT item_id FROM product_category_items WHERE category_id = ? AND item_name = ?",
            [category_id, item_name]
        )

        item_id = result[0]['item_id'] if result else None

        logger.info(f"创建分类项成功: {item_name} (ID: {item_id})")
        return jsonify({
            'success': True,
            'data': {'item_id': item_id},
            'message': '项创建成功'
        })

    except Exception as e:
        logger.error(f"创建分类项失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_product_categories_bp.route('/product-category-items/<int:item_id>', methods=['PUT'])
@require_auth
def update_category_item(item_id):
    """更新分类项"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': '请提供项信息'}), 400

        # 检查项是否存在
        existing = kb_manager.db.execute_query(
            "SELECT item_id FROM product_category_items WHERE item_id = ?",
            [item_id]
        )
        if not existing:
            return jsonify({'success': False, 'error': '项不存在'}), 404

        # 构建更新语句
        update_fields = []
        params = []

        if 'item_name' in data:
            update_fields.append('item_name = ?')
            params.append(data['item_name'])

        if 'item_code' in data:
            update_fields.append('item_code = ?')
            params.append(data['item_code'])

        if 'item_description' in data:
            update_fields.append('item_description = ?')
            params.append(data['item_description'])

        if 'item_order' in data:
            update_fields.append('item_order = ?')
            params.append(data['item_order'])

        if 'is_active' in data:
            update_fields.append('is_active = ?')
            params.append(data['is_active'])

        if not update_fields:
            return jsonify({'success': False, 'error': '没有需要更新的字段'}), 400

        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        params.append(item_id)

        update_query = f"""
            UPDATE product_category_items
            SET {', '.join(update_fields)}
            WHERE item_id = ?
        """

        kb_manager.db.execute_query(update_query, params)

        logger.info(f"更新分类项成功: ID={item_id}")
        return jsonify({'success': True, 'message': '项更新成功'})

    except Exception as e:
        logger.error(f"更新分类项失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_product_categories_bp.route('/product-category-items/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_category_item(item_id):
    """删除分类项（软删除）"""
    try:
        # 检查项是否存在
        existing = kb_manager.db.execute_query(
            "SELECT item_id FROM product_category_items WHERE item_id = ?",
            [item_id]
        )
        if not existing:
            return jsonify({'success': False, 'error': '项不存在'}), 404

        # 软删除：设置is_active为False
        kb_manager.db.execute_query(
            "UPDATE product_category_items SET is_active = 0 WHERE item_id = ?",
            [item_id]
        )

        logger.info(f"删除分类项成功: ID={item_id}")
        return jsonify({'success': True, 'message': '项删除成功'})

    except Exception as e:
        logger.error(f"删除分类项失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 导出蓝图
__all__ = ['api_product_categories_bp']
