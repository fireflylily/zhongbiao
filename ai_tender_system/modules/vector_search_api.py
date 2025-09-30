#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量搜索API接口
提供语义搜索、文档向量化和搜索分析功能
"""

from flask import Blueprint, request, jsonify, session
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.database import get_knowledge_base_db
from modules.vector_engine.simple_embedding import SimpleEmbeddingService
from modules.vector_engine.chroma_adapter import ChromaVectorStore, ChromaVectorDocument
from modules.document_parser.parser_manager import ParserManager, ParseResult

logger = get_module_logger("vector_search.api")


class VectorSearchAPI:
    """向量搜索API类"""

    def __init__(self):
        self.db = get_knowledge_base_db()
        self.blueprint = Blueprint('vector_search', __name__, url_prefix='/api/vector_search')

        # 初始化向量引擎组件（延迟初始化）
        self.embedding_service = None
        self.vector_store = None
        self.parser_manager = None
        self.is_initialized = False

        self._register_routes()
        logger.info("向量搜索API初始化完成")

    async def _ensure_initialized(self):
        """确保向量引擎组件已初始化"""
        if self.is_initialized:
            return True

        try:
            logger.info("初始化向量搜索组件...")

            # 初始化嵌入服务
            self.embedding_service = SimpleEmbeddingService(dimension=100)
            await self.embedding_service.initialize()

            # 初始化向量存储（使用Chroma）
            self.vector_store = ChromaVectorStore(dimension=100)
            await self.vector_store.initialize()

            # 初始化文档解析器
            self.parser_manager = ParserManager()

            self.is_initialized = True
            logger.info("向量搜索组件初始化完成")
            return True

        except Exception as e:
            logger.error(f"向量搜索组件初始化失败: {e}")
            return False

    def _run_async(self, coro):
        """在同步环境中运行异步代码"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def _register_routes(self):
        """注册API路由"""

        # =========================
        # 系统状态和配置API
        # =========================

        @self.blueprint.route('/status', methods=['GET'])
        def get_system_status():
            """获取向量搜索系统状态"""
            try:
                # 检查系统初始化状态
                init_status = self._run_async(self._ensure_initialized())

                status = {
                    'initialized': init_status,
                    'components': {
                        'embedding_service': self.embedding_service is not None,
                        'vector_store': self.vector_store is not None,
                        'parser_manager': self.parser_manager is not None
                    },
                    'database_status': 'connected'
                }

                if init_status and self.embedding_service:
                    status['embedding_model'] = self.embedding_service.get_model_info()

                if init_status and self.vector_store:
                    status['vector_store'] = self.vector_store.get_stats()

                return jsonify({
                    'success': True,
                    'data': status
                })

            except Exception as e:
                logger.error(f"获取系统状态失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/models', methods=['GET'])
        def get_vector_models():
            """获取可用的向量模型列表"""
            try:
                models = self.db.get_vector_models()
                return jsonify({
                    'success': True,
                    'data': models
                })
            except Exception as e:
                logger.error(f"获取向量模型失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/models/<int:model_id>/activate', methods=['POST'])
        def activate_vector_model(model_id):
            """激活指定的向量模型"""
            try:
                success = self.db.set_active_vector_model(model_id)

                if success:
                    return jsonify({
                        'success': True,
                        'message': f'向量模型 {model_id} 已激活'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '激活模型失败'
                    }), 400

            except Exception as e:
                logger.error(f"激活向量模型失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 语义搜索API
        # =========================

        @self.blueprint.route('/search', methods=['POST'])
        def semantic_search():
            """执行语义搜索"""
            try:
                data = request.get_json()
                if not data or not data.get('query'):
                    return jsonify({
                        'success': False,
                        'error': '搜索查询不能为空'
                    }), 400

                # 确保系统已初始化
                if not self._run_async(self._ensure_initialized()):
                    return jsonify({
                        'success': False,
                        'error': '向量搜索系统初始化失败'
                    }), 500

                query = data['query']
                top_k = min(data.get('top_k', 10), 50)  # 限制最大返回数量
                threshold = max(data.get('threshold', 0.3), 0.1)  # 最低相似度阈值
                filters = data.get('filters', {})

                start_time = time.time()

                # 执行搜索
                results = self._run_async(self._perform_search(
                    query, top_k, threshold, filters
                ))

                search_time = time.time() - start_time

                # 记录搜索历史
                user_id = data.get('user_id', 0)
                if user_id:
                    try:
                        self.db.create_search_history(
                            user_id=user_id,
                            query_text=query,
                            model_id=1,  # 简化版模型ID
                            search_type='semantic',
                            filter_conditions=json.dumps(filters) if filters else None,
                            result_count=len(results),
                            top_k=top_k,
                            threshold=threshold,
                            search_time=search_time
                        )
                    except Exception as history_error:
                        logger.warning(f"搜索历史记录失败: {history_error}")

                return jsonify({
                    'success': True,
                    'data': {
                        'results': results,
                        'total_results': len(results),
                        'search_time': round(search_time, 3),
                        'query': query,
                        'parameters': {
                            'top_k': top_k,
                            'threshold': threshold,
                            'filters': filters
                        }
                    }
                })

            except Exception as e:
                logger.error(f"语义搜索失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

    async def _perform_search(self, query: str, top_k: int, threshold: float, filters: Dict) -> List[Dict]:
        """执行实际的搜索操作"""
        try:
            # 查询向量化
            query_vector = await self.embedding_service.embed_query(query)

            # 执行向量搜索
            results = await self.vector_store.search(
                query_vector=query_vector,
                top_k=top_k,
                threshold=threshold,
                filter_metadata=filters
            )

            # 格式化搜索结果
            formatted_results = []
            for result in results:
                formatted_result = {
                    'document_id': result.document.id,
                    'content': result.document.content,
                    'metadata': result.document.metadata,
                    'similarity_score': result.score,
                    'rank': result.rank if hasattr(result, 'rank') else len(formatted_results) + 1,
                    'snippet': result.document.content[:200] + '...' if len(result.document.content) > 200 else result.document.content
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            logger.error(f"执行搜索失败: {e}")
            return []

        @self.blueprint.route('/similar/<doc_id>', methods=['GET'])
        def find_similar_documents(doc_id):
            """查找相似文档"""
            try:
                # 确保系统已初始化
                if not self._run_async(self._ensure_initialized()):
                    return jsonify({
                        'success': False,
                        'error': '向量搜索系统初始化失败'
                    }), 500

                top_k = min(request.args.get('top_k', 5, type=int), 20)

                # 执行相似文档搜索
                results = self._run_async(self._find_similar_documents(doc_id, top_k))

                return jsonify({
                    'success': True,
                    'data': {
                        'source_document_id': doc_id,
                        'similar_documents': results,
                        'total_found': len(results)
                    }
                })

            except Exception as e:
                logger.error(f"查找相似文档失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        async def _find_similar_documents(self, doc_id: str, top_k: int) -> List[Dict]:
            """查找相似文档的实现"""
            try:
                # 检查文档是否存在于向量存储中
                if doc_id not in self.vector_store.documents:
                    return []

                source_doc = self.vector_store.documents[doc_id]

                # 使用文档向量搜索相似文档
                results = await self.vector_store.search(
                    query_vector=source_doc.vector,
                    top_k=top_k + 1,  # 多获取一个（排除自己）
                    threshold=0.1
                )

                # 排除源文档本身
                similar_docs = []
                for result in results:
                    if result.document.id != doc_id:
                        similar_doc = {
                            'document_id': result.document.id,
                            'similarity_score': result.score,
                            'content_preview': result.document.content[:150] + '...',
                            'metadata': result.document.metadata
                        }
                        similar_docs.append(similar_doc)

                        if len(similar_docs) >= top_k:
                            break

                return similar_docs

            except Exception as e:
                logger.error(f"查找相似文档实现失败: {e}")
                return []

        # =========================
        # 文档向量化API
        # =========================

        @self.blueprint.route('/documents/vectorize', methods=['POST'])
        def vectorize_document():
            """对文档进行向量化处理"""
            try:
                data = request.get_json()
                if not data or not data.get('doc_id'):
                    return jsonify({
                        'success': False,
                        'error': '文档ID不能为空'
                    }), 400

                doc_id = data['doc_id']
                force_reprocess = data.get('force_reprocess', False)

                # 确保系统已初始化
                if not self._run_async(self._ensure_initialized()):
                    return jsonify({
                        'success': False,
                        'error': '向量搜索系统初始化失败'
                    }), 500

                # 执行向量化
                result = self._run_async(self._vectorize_document(doc_id, force_reprocess))

                if result['success']:
                    return jsonify(result), 200
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"文档向量化失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        async def _vectorize_document(self, doc_id: int, force_reprocess: bool = False) -> Dict:
            """执行文档向量化的实现"""
            try:
                # 获取文档信息
                documents = self.db.get_documents()
                doc_info = next((d for d in documents if d['doc_id'] == doc_id), None)

                if not doc_info:
                    return {
                        'success': False,
                        'error': f'文档不存在: {doc_id}'
                    }

                # 检查是否已经向量化
                if not force_reprocess and doc_info.get('vector_status') == 'completed':
                    return {
                        'success': True,
                        'message': '文档已完成向量化',
                        'doc_id': doc_id,
                        'status': 'already_vectorized'
                    }

                # 解析文档内容
                if doc_info.get('parse_status') != 'completed':
                    # 需要先解析文档
                    parse_result = await self.parser_manager.parse_document(doc_id, doc_info['file_path'])

                    if parse_result.status != 'success':
                        return {
                            'success': False,
                            'error': f'文档解析失败: {parse_result.error_message}'
                        }

                    # 更新解析状态
                    self.db.update_document_status(doc_id, parse_status='completed')
                else:
                    # 获取已解析的内容
                    chunks = self.db.get_document_chunks(doc_id)
                    if not chunks:
                        return {
                            'success': False,
                            'error': '文档未找到解析后的分块内容'
                        }

                # 创建向量文档
                chunks = self.db.get_document_chunks(doc_id)
                vector_documents = []

                for i, chunk in enumerate(chunks):
                    # 文本向量化
                    embedding_result = await self.embedding_service.embed_texts([chunk['content']])
                    vector = embedding_result.vectors[0]

                    # 创建向量文档
                    vector_doc = ChromaVectorDocument(
                        id=f"doc_{doc_id}_chunk_{i}",
                        content=chunk['content'],
                        vector=vector,
                        metadata={
                            'doc_id': doc_id,
                            'chunk_id': chunk['chunk_id'],
                            'chunk_index': chunk['chunk_index'],
                            'content_type': chunk.get('content_type', 'text'),
                            'page_number': chunk.get('page_number'),
                            'document_category': doc_info.get('document_category', 'tech'),
                            'privacy_classification': doc_info.get('privacy_classification', 1)
                        }
                    )
                    vector_documents.append(vector_doc)

                # 添加到向量存储
                success = await self.vector_store.add_documents(vector_documents)

                if success:
                    # 更新文档向量化状态
                    self.db.update_document_status(doc_id, vector_status='completed')

                    return {
                        'success': True,
                        'message': f'文档向量化完成',
                        'doc_id': doc_id,
                        'chunks_processed': len(vector_documents),
                        'status': 'vectorized'
                    }
                else:
                    return {
                        'success': False,
                        'error': '向量存储失败'
                    }

            except Exception as e:
                logger.error(f"文档向量化实现失败: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        @self.blueprint.route('/documents/batch_vectorize', methods=['POST'])
        def batch_vectorize_documents():
            """批量向量化文档"""
            try:
                data = request.get_json()
                if not data or not data.get('doc_ids'):
                    return jsonify({
                        'success': False,
                        'error': '文档ID列表不能为空'
                    }), 400

                doc_ids = data['doc_ids']
                if not isinstance(doc_ids, list) or len(doc_ids) == 0:
                    return jsonify({
                        'success': False,
                        'error': '请提供有效的文档ID列表'
                    }), 400

                # 限制批量处理数量
                if len(doc_ids) > 10:
                    return jsonify({
                        'success': False,
                        'error': '批量处理数量不能超过10个文档'
                    }), 400

                # 确保系统已初始化
                if not self._run_async(self._ensure_initialized()):
                    return jsonify({
                        'success': False,
                        'error': '向量搜索系统初始化失败'
                    }), 500

                # 执行批量向量化
                results = self._run_async(self._batch_vectorize_documents(doc_ids))

                return jsonify({
                    'success': True,
                    'data': {
                        'total_documents': len(doc_ids),
                        'results': results,
                        'summary': {
                            'successful': len([r for r in results if r['success']]),
                            'failed': len([r for r in results if not r['success']])
                        }
                    }
                })

            except Exception as e:
                logger.error(f"批量向量化失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        async def _batch_vectorize_documents(self, doc_ids: List[int]) -> List[Dict]:
            """批量向量化文档的实现"""
            results = []

            for doc_id in doc_ids:
                try:
                    result = await self._vectorize_document(doc_id, force_reprocess=False)
                    result['doc_id'] = doc_id
                    results.append(result)
                except Exception as e:
                    results.append({
                        'doc_id': doc_id,
                        'success': False,
                        'error': str(e)
                    })

            return results

        # =========================
        # 搜索分析和统计API
        # =========================

        @self.blueprint.route('/analytics/search_stats', methods=['GET'])
        def get_search_analytics():
            """获取搜索分析数据"""
            try:
                days = request.args.get('days', 30, type=int)
                days = min(max(days, 1), 365)  # 限制在1-365天之间

                analytics = self.db.get_search_analytics(days)

                return jsonify({
                    'success': True,
                    'data': analytics
                })

            except Exception as e:
                logger.error(f"获取搜索分析失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/analytics/vectorization_stats', methods=['GET'])
        def get_vectorization_stats():
            """获取向量化统计信息"""
            try:
                stats = self.db.get_vectorization_stats()

                return jsonify({
                    'success': True,
                    'data': stats
                })

            except Exception as e:
                logger.error(f"获取向量化统计失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/analytics/system_metrics', methods=['GET'])
        def get_system_metrics():
            """获取系统性能指标"""
            try:
                component = request.args.get('component')
                limit = min(request.args.get('limit', 100, type=int), 500)

                metrics = self.db.get_system_metrics(component, limit)

                return jsonify({
                    'success': True,
                    'data': metrics
                })

            except Exception as e:
                logger.error(f"获取系统指标失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 标签管理API
        # =========================

        @self.blueprint.route('/tags', methods=['GET'])
        def get_document_tags():
            """获取文档标签列表"""
            try:
                category = request.args.get('category')
                tags = self.db.get_document_tags(category)

                return jsonify({
                    'success': True,
                    'data': tags
                })

            except Exception as e:
                logger.error(f"获取文档标签失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/tags', methods=['POST'])
        def create_document_tag():
            """创建文档标签"""
            try:
                data = request.get_json()
                if not data or not data.get('tag_name'):
                    return jsonify({
                        'success': False,
                        'error': '标签名称不能为空'
                    }), 400

                tag_id = self.db.create_document_tag(
                    tag_name=data['tag_name'],
                    tag_category=data.get('tag_category'),
                    tag_color=data.get('tag_color', '#007bff'),
                    description=data.get('description')
                )

                return jsonify({
                    'success': True,
                    'data': {'tag_id': tag_id},
                    'message': '标签创建成功'
                }), 201

            except Exception as e:
                logger.error(f"创建文档标签失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>/tags', methods=['POST'])
        def add_document_tag(doc_id):
            """为文档添加标签"""
            try:
                data = request.get_json()
                if not data or not data.get('tag_id'):
                    return jsonify({
                        'success': False,
                        'error': '标签ID不能为空'
                    }), 400

                relation_id = self.db.add_document_tag(
                    doc_id=doc_id,
                    tag_id=data['tag_id'],
                    confidence=data.get('confidence', 1.0),
                    is_auto_tagged=data.get('is_auto_tagged', False),
                    tagged_by=data.get('tagged_by')
                )

                return jsonify({
                    'success': True,
                    'data': {'relation_id': relation_id},
                    'message': '标签添加成功'
                })

            except Exception as e:
                logger.error(f"添加文档标签失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

    def get_blueprint(self):
        """获取Flask蓝图"""
        return self.blueprint


# 创建全局API实例
vector_search_api = VectorSearchAPI()