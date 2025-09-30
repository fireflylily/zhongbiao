#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库API接口
功能：提供REST API接口供前端调用
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
from typing import Dict, Any

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .manager import KnowledgeBaseManager
from common.logger import get_module_logger

logger = get_module_logger("knowledge_base.api")


class KnowledgeBaseAPI:
    """知识库API类"""

    def __init__(self):
        self.manager = KnowledgeBaseManager()
        self.blueprint = Blueprint('knowledge_base', __name__, url_prefix='/api/knowledge_base')
        self._register_routes()

        logger.info("知识库API初始化完成")

    def _register_routes(self):
        """注册API路由"""

        # =========================
        # 公司管理API
        # =========================

        @self.blueprint.route('/companies', methods=['GET'])
        def get_companies():
            """获取公司列表"""
            try:
                companies = self.manager.get_companies()
                return jsonify({
                    'success': True,
                    'data': companies
                })
            except Exception as e:
                logger.error(f"获取公司列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies', methods=['POST'])
        def create_company():
            """创建公司"""
            try:
                data = request.get_json()

                # 验证必需字段
                if not data or not data.get('company_name'):
                    return jsonify({
                        'success': False,
                        'error': '公司名称不能为空'
                    }), 400

                result = self.manager.create_company(
                    company_name=data['company_name'],
                    company_code=data.get('company_code'),
                    industry_type=data.get('industry_type'),
                    description=data.get('description')
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建公司失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies/<int:company_id>', methods=['GET'])
        def get_company_detail(company_id):
            """获取公司详细信息"""
            try:
                company = self.manager.get_company_detail(company_id)
                if company:
                    return jsonify({
                        'success': True,
                        'data': company
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '公司不存在'
                    }), 404

            except Exception as e:
                logger.error(f"获取公司详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies/<int:company_id>', methods=['PUT'])
        def update_company(company_id):
            """更新公司信息"""
            try:
                data = request.get_json()

                # 验证必需字段
                if not data:
                    return jsonify({
                        'success': False,
                        'error': '请求数据不能为空'
                    }), 400

                # 调用管理器更新公司信息
                result = self.manager.update_company(company_id, data)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"更新公司信息失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 产品管理API
        # =========================

        @self.blueprint.route('/companies/<int:company_id>/products', methods=['GET'])
        def get_products(company_id):
            """获取公司的产品列表"""
            try:
                products = self.manager.get_products(company_id)
                return jsonify({
                    'success': True,
                    'data': products
                })
            except Exception as e:
                logger.error(f"获取产品列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies/<int:company_id>/products', methods=['POST'])
        def create_product(company_id):
            """创建产品"""
            try:
                data = request.get_json()

                # 验证必需字段
                if not data or not data.get('product_name'):
                    return jsonify({
                        'success': False,
                        'error': '产品名称不能为空'
                    }), 400

                result = self.manager.create_product(
                    company_id=company_id,
                    product_name=data['product_name'],
                    product_code=data.get('product_code'),
                    product_category=data.get('product_category'),
                    description=data.get('description')
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建产品失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/products/<int:product_id>', methods=['GET'])
        def get_product_detail(product_id):
            """获取产品详细信息"""
            try:
                product = self.manager.get_product_detail(product_id)
                if product:
                    return jsonify({
                        'success': True,
                        'data': product
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '产品不存在'
                    }), 404

            except Exception as e:
                logger.error(f"获取产品详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 文档库管理API
        # =========================

        @self.blueprint.route('/libraries', methods=['POST'])
        def create_document_library():
            """创建文档库"""
            try:
                data = request.get_json()

                # 验证必需字段
                required_fields = ['owner_type', 'owner_id', 'library_name', 'library_type']
                for field in required_fields:
                    if not data or not data.get(field):
                        return jsonify({
                            'success': False,
                            'error': f'{field} 不能为空'
                        }), 400

                result = self.manager.create_document_library(
                    owner_type=data['owner_type'],
                    owner_id=data['owner_id'],
                    library_name=data['library_name'],
                    library_type=data['library_type'],
                    privacy_level=data.get('privacy_level', 1),
                    is_shared=data.get('is_shared', False),
                    share_scope=data.get('share_scope'),
                    share_products=data.get('share_products')
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建文档库失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/<owner_type>/<int:owner_id>/libraries', methods=['GET'])
        def get_document_libraries(owner_type, owner_id):
            """获取文档库列表"""
            try:
                libraries = self.manager.get_document_libraries(owner_type, owner_id)
                return jsonify({
                    'success': True,
                    'data': libraries
                })
            except Exception as e:
                logger.error(f"获取文档库列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 文档管理API
        # =========================

        @self.blueprint.route('/libraries/<int:library_id>/documents', methods=['POST'])
        def upload_document(library_id):
            """上传文档到文档库"""
            try:
                # 检查文件是否存在
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': '没有选择文件'
                    }), 400

                file = request.files['file']
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': '文件名不能为空'
                    }), 400

                # 获取其他参数
                privacy_classification = int(request.form.get('privacy_classification', 1))
                tags = request.form.get('tags')
                metadata = request.form.get('metadata')

                # 解析JSON字段
                if tags:
                    try:
                        tags = json.loads(tags)
                    except:
                        tags = []

                if metadata:
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}

                # 验证文件类型
                allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if file_ext not in allowed_extensions:
                    return jsonify({
                        'success': False,
                        'error': f'不支持的文件类型: {file_ext}。支持的类型: {", ".join(allowed_extensions)}'
                    }), 400

                result = self.manager.upload_document(
                    library_id=library_id,
                    file_obj=file,
                    original_filename=secure_filename(file.filename),
                    privacy_classification=privacy_classification,
                    tags=tags,
                    metadata=metadata
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"文档上传失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/libraries/<int:library_id>/documents', methods=['GET'])
        def get_documents(library_id):
            """获取文档库的文档列表"""
            try:
                privacy_level = request.args.get('privacy_level', type=int)
                documents = self.manager.get_documents(library_id, privacy_level)

                return jsonify({
                    'success': True,
                    'data': documents
                })
            except Exception as e:
                logger.error(f"获取文档列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>/status', methods=['PUT'])
        def update_document_status(doc_id):
            """更新文档处理状态"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': '请求数据不能为空'
                    }), 400

                parse_status = data.get('parse_status')
                vector_status = data.get('vector_status')

                if not parse_status and not vector_status:
                    return jsonify({
                        'success': False,
                        'error': '至少需要提供一个状态字段'
                    }), 400

                result = self.manager.update_document_status(doc_id, parse_status, vector_status)

                if result:
                    return jsonify({
                        'success': True,
                        'message': '文档状态更新成功'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '更新文档状态失败'
                    }), 400

            except Exception as e:
                logger.error(f"更新文档状态失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>', methods=['DELETE'])
        def delete_document(doc_id):
            """删除文档"""
            try:
                result = self.manager.delete_document(doc_id)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"删除文档失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 统计和仪表板API
        # =========================

        @self.blueprint.route('/dashboard/stats', methods=['GET'])
        def get_dashboard_stats():
            """获取仪表板统计信息"""
            try:
                company_id = request.args.get('company_id', type=int)
                stats = self.manager.get_dashboard_stats(company_id)

                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                logger.error(f"获取统计信息失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/statistics', methods=['GET'])
        def get_statistics():
            """获取知识库整体统计数据"""
            try:
                stats = self.manager.get_knowledge_base_statistics()
                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                logger.error(f"获取统计数据失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/search', methods=['POST'])
        def search_documents():
            """智能文档搜索"""
            try:
                data = request.get_json()
                if not data or not data.get('query'):
                    return jsonify({
                        'success': False,
                        'error': '搜索查询不能为空'
                    }), 400

                query = data['query']
                category = data.get('category')
                privacy_level = data.get('privacy_level', 1)

                results = self.manager.search_documents(
                    query=query,
                    category=category,
                    privacy_level=int(privacy_level)
                )

                return jsonify({
                    'success': True,
                    'data': results
                })

            except Exception as e:
                logger.error(f"文档搜索失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 权限验证API
        # =========================

        @self.blueprint.route('/documents/<int:doc_id>/access', methods=['POST'])
        def check_document_access(doc_id):
            """检查文档访问权限并记录日志"""
            try:
                data = request.get_json()
                user_role = data.get('user_role', 'guest')
                doc_privacy_level = data.get('doc_privacy_level', 1)
                action_type = data.get('action_type', 'view')

                # 检查访问权限
                access_granted = self.manager.check_document_access(user_role, doc_privacy_level)

                # 记录访问日志
                log_id = self.manager.log_document_access(
                    user_id=data.get('user_id', 'anonymous'),
                    user_role=user_role,
                    action_type=action_type,
                    doc_id=doc_id,
                    privacy_level=doc_privacy_level,
                    access_granted=access_granted,
                    access_reason=data.get('access_reason'),
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    session_id=session.get('session_id')
                )

                return jsonify({
                    'success': True,
                    'access_granted': access_granted,
                    'log_id': log_id
                })

            except Exception as e:
                logger.error(f"检查文档访问权限失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

    def get_blueprint(self):
        """获取Flask蓝图"""
        return self.blueprint


# 创建全局API实例
knowledge_base_api = KnowledgeBaseAPI()