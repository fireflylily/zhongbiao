#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量引擎管理器
统一管理嵌入服务、向量存储和语义搜索
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from .embedding_service import EmbeddingService
from .vector_store import VectorStore, VectorDocument
from .semantic_search import SemanticSearch, SearchQuery, EnhancedSearchResult

logger = get_module_logger("vector_engine.engine_manager")


class VectorEngineManager:
    """向量引擎管理器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化向量引擎管理器

        Args:
            config: 配置参数
        """
        self.logger = logger
        self.config = config or self._get_default_config()

        # 核心组件
        self.embedding_service = None
        self.vector_store = None
        self.semantic_search = None

        # 状态管理
        self.is_initialized = False
        self.initialization_time = 0.0

        # 性能监控
        self.performance_stats = {
            "initialization_time": 0.0,
            "total_documents_added": 0,
            "total_searches": 0,
            "avg_search_time": 0.0,
            "last_activity": ""
        }

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "embedding": {
                "model_type": "chinese",
                "cache_dir": "data/models"
            },
            "vector_store": {
                "store_path": "data/vector_store",
                "dimension": 384,
                "index_type": "flat"
            },
            "search": {
                "default_top_k": 10,
                "default_threshold": 0.3
            }
        }

    async def initialize(self) -> bool:
        """初始化向量引擎"""
        if self.is_initialized:
            self.logger.info("向量引擎已初始化")
            return True

        try:
            self.logger.info("开始初始化向量引擎")
            start_time = time.time()

            # 1. 初始化嵌入服务
            self.logger.info("初始化嵌入服务...")
            self.embedding_service = EmbeddingService(
                model_type=self.config["embedding"]["model_type"],
                cache_dir=self.config["embedding"]["cache_dir"]
            )

            embedding_success = await self.embedding_service.initialize()
            if not embedding_success:
                raise RuntimeError("嵌入服务初始化失败")

            # 获取向量维度
            model_info = self.embedding_service.get_model_info()
            vector_dimension = model_info.get("dimensions", 384)

            # 2. 初始化向量存储
            self.logger.info("初始化向量存储...")
            self.vector_store = VectorStore(
                store_path=self.config["vector_store"]["store_path"],
                dimension=vector_dimension,
                index_type=self.config["vector_store"]["index_type"]
            )

            store_success = await self.vector_store.initialize()
            if not store_success:
                raise RuntimeError("向量存储初始化失败")

            # 3. 初始化语义搜索
            self.logger.info("初始化语义搜索...")
            self.semantic_search = SemanticSearch(
                embedding_service=self.embedding_service,
                vector_store=self.vector_store
            )

            # 完成初始化
            self.initialization_time = time.time() - start_time
            self.performance_stats["initialization_time"] = self.initialization_time
            self.is_initialized = True

            self.logger.info(f"向量引擎初始化完成: time={self.initialization_time:.2f}s")

            return True

        except Exception as e:
            self.logger.error(f"向量引擎初始化失败: {e}")
            await self.cleanup()
            return False

    async def add_documents(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        添加文档到向量引擎

        Args:
            documents: 文档列表

        Returns:
            Dict: 添加结果
        """
        if not self.is_initialized:
            raise RuntimeError("向量引擎未初始化")

        if not documents:
            return {"success": True, "added_count": 0, "message": "没有文档需要添加"}

        try:
            self.logger.info(f"开始添加文档: {len(documents)} 个文档")
            start_time = time.time()

            # 使用语义搜索服务添加文档（内部会处理向量化和存储）
            success = await self.semantic_search.add_documents(documents)

            processing_time = time.time() - start_time

            if success:
                # 更新统计
                self.performance_stats["total_documents_added"] += len(documents)
                self.performance_stats["last_activity"] = datetime.now().isoformat()

                result = {
                    "success": True,
                    "added_count": len(documents),
                    "processing_time": processing_time,
                    "message": f"成功添加 {len(documents)} 个文档"
                }

                self.logger.info(f"文档添加完成: {result}")
                return result

            else:
                return {
                    "success": False,
                    "added_count": 0,
                    "error": "文档添加失败",
                    "processing_time": processing_time
                }

        except Exception as e:
            self.logger.error(f"添加文档失败: {e}")
            return {
                "success": False,
                "added_count": 0,
                "error": str(e)
            }

    async def search(self,
                    query: str,
                    top_k: int = None,
                    threshold: float = None,
                    filters: Optional[Dict] = None,
                    **kwargs) -> List[Dict]:
        """
        执行语义搜索

        Args:
            query: 搜索查询
            top_k: 返回结果数量
            threshold: 相似度阈值
            filters: 过滤条件
            **kwargs: 其他参数

        Returns:
            List[Dict]: 搜索结果
        """
        if not self.is_initialized:
            raise RuntimeError("向量引擎未初始化")

        try:
            start_time = time.time()

            # 构建搜索查询
            search_query = SearchQuery(
                text=query,
                top_k=top_k or self.config["search"]["default_top_k"],
                threshold=threshold or self.config["search"]["default_threshold"],
                filters=filters,
                **kwargs
            )

            # 执行搜索
            results = await self.semantic_search.search(search_query)

            search_time = time.time() - start_time

            # 更新统计
            self._update_search_stats(search_time)

            # 转换结果格式
            formatted_results = []
            for result in results:
                formatted_result = {
                    "document_id": result.document_id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score,
                    "rank": result.rank,
                    "matched_segments": result.matched_segments,
                    "explanation": result.explanation
                }
                formatted_results.append(formatted_result)

            self.logger.info(f"搜索完成: query='{query[:50]}...', "
                           f"results={len(formatted_results)}, time={search_time:.3f}s")

            return formatted_results

        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return []

    async def get_similar_documents(self, doc_id: str, top_k: int = 5) -> List[Dict]:
        """获取相似文档"""
        if not self.is_initialized:
            raise RuntimeError("向量引擎未初始化")

        try:
            results = await self.semantic_search.get_similar_documents(doc_id, top_k)

            # 转换结果格式
            formatted_results = []
            for result in results:
                formatted_result = {
                    "document_id": result.document_id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score,
                    "rank": result.rank,
                    "explanation": result.explanation
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            self.logger.error(f"获取相似文档失败: {e}")
            return []

    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if not self.is_initialized:
            raise RuntimeError("向量引擎未初始化")

        return await self.semantic_search.delete_document(doc_id)

    def get_engine_status(self) -> Dict:
        """获取引擎状态"""
        status = {
            "initialized": self.is_initialized,
            "initialization_time": self.initialization_time,
            "performance_stats": self.performance_stats.copy(),
            "config": self.config
        }

        if self.is_initialized:
            # 添加组件状态
            status.update({
                "embedding_service": self.embedding_service.get_model_info(),
                "vector_store": self.vector_store.get_stats(),
                "search_service": self.semantic_search.get_search_stats()
            })

        return status

    def _update_search_stats(self, search_time: float):
        """更新搜索统计"""
        self.performance_stats["total_searches"] += 1
        self.performance_stats["last_activity"] = datetime.now().isoformat()

        # 更新平均搜索时间
        if self.performance_stats["total_searches"] > 1:
            total_time = (self.performance_stats["avg_search_time"] *
                         (self.performance_stats["total_searches"] - 1) + search_time)
            self.performance_stats["avg_search_time"] = total_time / self.performance_stats["total_searches"]
        else:
            self.performance_stats["avg_search_time"] = search_time

    async def rebuild_index(self) -> bool:
        """重建向量索引"""
        if not self.is_initialized:
            raise RuntimeError("向量引擎未初始化")

        try:
            self.logger.info("开始重建向量索引")
            start_time = time.time()

            # 重建存储索引
            await self.vector_store._rebuild_index()

            rebuild_time = time.time() - start_time
            self.logger.info(f"向量索引重建完成: time={rebuild_time:.2f}s")

            return True

        except Exception as e:
            self.logger.error(f"重建索引失败: {e}")
            return False

    async def export_data(self, export_path: str) -> bool:
        """导出向量数据"""
        if not self.is_initialized:
            raise RuntimeError("向量引擎未初始化")

        try:
            # 这里可以实现数据导出逻辑
            self.logger.info(f"开始导出数据到: {export_path}")

            # TODO: 实现具体的导出逻辑

            return True

        except Exception as e:
            self.logger.error(f"数据导出失败: {e}")
            return False

    async def cleanup(self):
        """清理资源"""
        try:
            if self.semantic_search:
                await self.semantic_search.cleanup()

            if self.vector_store:
                await self.vector_store.cleanup()

            if self.embedding_service:
                await self.embedding_service.cleanup()

            self.is_initialized = False
            self.logger.info("向量引擎资源已清理")

        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")

    async def health_check(self) -> Dict:
        """健康检查"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }

        try:
            if not self.is_initialized:
                health_status["status"] = "not_initialized"
                return health_status

            # 检查各组件状态
            if self.embedding_service and self.embedding_service.model:
                health_status["components"]["embedding_service"] = "healthy"
            else:
                health_status["components"]["embedding_service"] = "unhealthy"
                health_status["status"] = "degraded"

            if self.vector_store and self.vector_store.index:
                health_status["components"]["vector_store"] = "healthy"
            else:
                health_status["components"]["vector_store"] = "unhealthy"
                health_status["status"] = "degraded"

            if self.semantic_search:
                health_status["components"]["semantic_search"] = "healthy"
            else:
                health_status["components"]["semantic_search"] = "unhealthy"
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)

        return health_status