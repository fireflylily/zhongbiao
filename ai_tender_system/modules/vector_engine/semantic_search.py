#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义搜索服务
整合嵌入服务和向量存储，提供高级搜索功能
"""

import asyncio
import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
import time

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from .embedding_service import EmbeddingService, EmbeddingResult
from .vector_store import VectorStore, VectorDocument, SearchResult

logger = get_module_logger("vector_engine.semantic_search")


@dataclass
class SearchQuery:
    """搜索查询数据类"""
    text: str
    top_k: int = 10
    threshold: float = 0.3
    filters: Optional[Dict[str, Any]] = None
    boost_fields: Optional[List[str]] = None  # 字段权重提升
    rerank: bool = True  # 是否重排序


@dataclass
class EnhancedSearchResult:
    """增强搜索结果"""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    rank: int
    matched_segments: List[str]  # 匹配的文本片段
    explanation: str  # 匹配说明


class SemanticSearch:
    """语义搜索服务"""

    def __init__(self,
                 embedding_service: EmbeddingService,
                 vector_store: VectorStore):
        """
        初始化语义搜索

        Args:
            embedding_service: 嵌入服务
            vector_store: 向量存储
        """
        self.logger = logger
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        # 搜索配置
        self.config = {
            "default_top_k": 10,
            "default_threshold": 0.3,
            "max_top_k": 100,
            "rerank_top_k": 50,  # 重排序前的候选数量
            "highlight_context": 100,  # 高亮上下文长度
        }

        # 搜索统计
        self.search_stats = {
            "total_searches": 0,
            "avg_search_time": 0.0,
            "avg_results_count": 0.0,
            "popular_queries": {},  # 查询频率统计
        }

    async def search(self, query: Union[str, SearchQuery]) -> List[EnhancedSearchResult]:
        """
        执行语义搜索

        Args:
            query: 搜索查询（字符串或SearchQuery对象）

        Returns:
            List[EnhancedSearchResult]: 增强搜索结果
        """
        # 标准化查询
        if isinstance(query, str):
            search_query = SearchQuery(text=query)
        else:
            search_query = query

        if not search_query.text.strip():
            return []

        try:
            self.logger.info(f"开始语义搜索: query='{search_query.text[:100]}...', "
                           f"top_k={search_query.top_k}")
            start_time = time.time()

            # 1. 查询向量化
            query_vector = await self.embedding_service.embed_query(search_query.text)
            if query_vector.size == 0:
                self.logger.warning("查询向量化失败")
                return []

            # 2. 向量搜索
            raw_results = await self.vector_store.search(
                query_vector=query_vector,
                top_k=min(search_query.top_k * 3, self.config["max_top_k"]),  # 获取更多候选
                threshold=search_query.threshold * 0.8,  # 降低初筛阈值
                filter_metadata=search_query.filters
            )

            if not raw_results:
                self.logger.info("向量搜索无结果")
                return []

            # 3. 结果增强和重排序
            enhanced_results = await self._enhance_results(
                search_query, raw_results, query_vector
            )

            # 4. 应用最终过滤和排序
            final_results = self._finalize_results(
                enhanced_results, search_query
            )

            # 5. 更新统计信息
            search_time = time.time() - start_time
            self._update_search_stats(search_query.text, len(final_results), search_time)

            self.logger.info(f"语义搜索完成: results={len(final_results)}, "
                           f"time={search_time:.3f}s")

            return final_results

        except Exception as e:
            self.logger.error(f"语义搜索失败: {e}")
            return []

    async def _enhance_results(self,
                              query: SearchQuery,
                              raw_results: List[SearchResult],
                              query_vector: np.ndarray) -> List[EnhancedSearchResult]:
        """增强搜索结果"""
        enhanced_results = []

        for result in raw_results:
            try:
                # 提取匹配片段
                matched_segments = self._extract_matched_segments(
                    query.text, result.document.content
                )

                # 生成匹配说明
                explanation = self._generate_explanation(
                    query.text, result.document, result.score
                )

                # 字段权重调整
                adjusted_score = self._adjust_score_by_fields(
                    result.score, result.document.metadata, query.boost_fields
                )

                enhanced_result = EnhancedSearchResult(
                    document_id=result.document.id,
                    content=result.document.content,
                    metadata=result.document.metadata,
                    score=adjusted_score,
                    rank=result.rank,
                    matched_segments=matched_segments,
                    explanation=explanation
                )

                enhanced_results.append(enhanced_result)

            except Exception as e:
                self.logger.warning(f"增强结果失败: doc_id={result.document.id}, error={e}")
                continue

        # 重排序
        if query.rerank and len(enhanced_results) > 1:
            enhanced_results = await self._rerank_results(query, enhanced_results)

        return enhanced_results

    def _extract_matched_segments(self, query_text: str, document_content: str) -> List[str]:
        """提取匹配的文本片段"""
        segments = []

        try:
            # 简单的关键词匹配（后续可以用更复杂的方法）
            query_words = set(query_text.lower().split())
            sentences = document_content.split('。')

            for sentence in sentences[:10]:  # 限制处理的句子数量
                sentence = sentence.strip()
                if not sentence:
                    continue

                sentence_words = set(sentence.lower().split())

                # 计算词汇重叠度
                overlap = len(query_words & sentence_words)
                if overlap > 0:
                    # 添加上下文
                    context_start = max(0, len(sentence) - self.config["highlight_context"] // 2)
                    context_end = min(len(sentence), context_start + self.config["highlight_context"])

                    segment = sentence[context_start:context_end]
                    if segment not in segments:
                        segments.append(segment)

                    if len(segments) >= 3:  # 限制片段数量
                        break

        except Exception as e:
            self.logger.debug(f"提取匹配片段失败: {e}")

        return segments

    def _generate_explanation(self, query: str, document: VectorDocument, score: float) -> str:
        """生成匹配说明"""
        try:
            # 基于分数等级生成说明
            if score >= 0.8:
                level = "高度相关"
            elif score >= 0.6:
                level = "相关"
            elif score >= 0.4:
                level = "部分相关"
            else:
                level = "低相关"

            # 添加元数据信息
            doc_type = document.metadata.get('document_type', '未知类型')
            source = document.metadata.get('source', '未知来源')

            explanation = f"{level} (相似度: {score:.2f}) - {doc_type}文档，来源: {source}"

            return explanation

        except Exception as e:
            self.logger.debug(f"生成说明失败: {e}")
            return f"相似度: {score:.2f}"

    def _adjust_score_by_fields(self,
                               base_score: float,
                               metadata: Dict[str, Any],
                               boost_fields: Optional[List[str]]) -> float:
        """根据字段权重调整分数"""
        if not boost_fields:
            return base_score

        adjusted_score = base_score

        try:
            # 字段权重映射
            field_weights = {
                'title': 1.5,        # 标题权重
                'important': 1.3,    # 重要标记
                'recent': 1.2,       # 最新文档
                'verified': 1.1      # 已验证文档
            }

            for field in boost_fields:
                if field in metadata and field in field_weights:
                    if metadata[field]:  # 字段值为真
                        adjusted_score *= field_weights[field]

        except Exception as e:
            self.logger.debug(f"调整分数失败: {e}")

        return min(adjusted_score, 1.0)  # 限制最大分数

    async def _rerank_results(self,
                             query: SearchQuery,
                             results: List[EnhancedSearchResult]) -> List[EnhancedSearchResult]:
        """重排序结果"""
        try:
            # 简单的重排序策略（可以后续改进）

            # 1. 按分数降序
            results.sort(key=lambda x: x.score, reverse=True)

            # 2. 相同分数情况下，按匹配片段数量排序
            results.sort(key=lambda x: (x.score, len(x.matched_segments)), reverse=True)

            # 3. 更新排名
            for i, result in enumerate(results):
                result.rank = i + 1

            self.logger.debug(f"重排序完成: {len(results)} 个结果")

        except Exception as e:
            self.logger.warning(f"重排序失败: {e}")

        return results

    def _finalize_results(self,
                         enhanced_results: List[EnhancedSearchResult],
                         query: SearchQuery) -> List[EnhancedSearchResult]:
        """最终处理结果"""
        # 应用最终阈值过滤
        filtered_results = [
            result for result in enhanced_results
            if result.score >= query.threshold
        ]

        # 限制返回数量
        final_results = filtered_results[:query.top_k]

        # 重新编号
        for i, result in enumerate(final_results):
            result.rank = i + 1

        return final_results

    async def add_documents(self, documents: List[Dict]) -> bool:
        """
        添加文档到搜索索引

        Args:
            documents: 文档列表，每个文档包含 id, content, metadata

        Returns:
            bool: 是否成功
        """
        if not documents:
            return True

        try:
            self.logger.info(f"添加文档到搜索索引: {len(documents)} 个文档")

            # 1. 提取文本内容
            texts = [doc.get('content', '') for doc in documents]

            # 2. 批量向量化
            embedding_result = await self.embedding_service.embed_texts(texts)

            if embedding_result.vectors.size == 0:
                self.logger.error("文档向量化失败")
                return False

            # 3. 创建向量文档
            vector_documents = []
            for i, doc in enumerate(documents):
                vector_doc = VectorDocument(
                    id=str(doc.get('id', f'doc_{i}')),
                    content=doc.get('content', ''),
                    vector=embedding_result.vectors[i],
                    metadata=doc.get('metadata', {})
                )
                vector_documents.append(vector_doc)

            # 4. 添加到向量存储
            success = await self.vector_store.add_documents(vector_documents)

            if success:
                self.logger.info(f"文档添加成功: {len(vector_documents)} 个文档")
            else:
                self.logger.error("文档添加到向量存储失败")

            return success

        except Exception as e:
            self.logger.error(f"添加文档失败: {e}")
            return False

    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        return await self.vector_store.delete_document(doc_id)

    def _update_search_stats(self, query_text: str, result_count: int, search_time: float):
        """更新搜索统计"""
        self.search_stats["total_searches"] += 1

        # 更新平均搜索时间
        if self.search_stats["total_searches"] > 1:
            total_time = (self.search_stats["avg_search_time"] *
                         (self.search_stats["total_searches"] - 1) + search_time)
            self.search_stats["avg_search_time"] = total_time / self.search_stats["total_searches"]
        else:
            self.search_stats["avg_search_time"] = search_time

        # 更新平均结果数量
        if self.search_stats["total_searches"] > 1:
            total_results = (self.search_stats["avg_results_count"] *
                           (self.search_stats["total_searches"] - 1) + result_count)
            self.search_stats["avg_results_count"] = total_results / self.search_stats["total_searches"]
        else:
            self.search_stats["avg_results_count"] = result_count

        # 记录热门查询
        query_key = query_text.lower().strip()[:50]  # 限制长度
        if query_key in self.search_stats["popular_queries"]:
            self.search_stats["popular_queries"][query_key] += 1
        else:
            self.search_stats["popular_queries"][query_key] = 1

    async def get_similar_documents(self,
                                   doc_id: str,
                                   top_k: int = 5) -> List[EnhancedSearchResult]:
        """获取相似文档"""
        try:
            # 获取目标文档
            if doc_id not in self.vector_store.documents:
                self.logger.warning(f"文档不存在: {doc_id}")
                return []

            target_doc = self.vector_store.documents[doc_id]

            # 使用文档向量进行搜索
            raw_results = await self.vector_store.search(
                query_vector=target_doc.vector,
                top_k=top_k + 1,  # 多获取一个（排除自己）
                threshold=0.1
            )

            # 排除自己
            filtered_results = [r for r in raw_results if r.document.id != doc_id][:top_k]

            # 转换为增强结果
            enhanced_results = []
            for i, result in enumerate(filtered_results):
                enhanced_result = EnhancedSearchResult(
                    document_id=result.document.id,
                    content=result.document.content,
                    metadata=result.document.metadata,
                    score=result.score,
                    rank=i + 1,
                    matched_segments=[],
                    explanation=f"文档相似度: {result.score:.2f}"
                )
                enhanced_results.append(enhanced_result)

            return enhanced_results

        except Exception as e:
            self.logger.error(f"获取相似文档失败: {e}")
            return []

    def get_search_stats(self) -> Dict:
        """获取搜索统计信息"""
        return {
            **self.search_stats,
            "embedding_stats": self.embedding_service.get_model_info(),
            "vector_store_stats": self.vector_store.get_stats()
        }

    async def cleanup(self):
        """清理资源"""
        await self.embedding_service.cleanup()
        await self.vector_store.cleanup()
        self.logger.info("语义搜索服务资源已清理")