#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版向量存储
用于开发和测试阶段的向量索引和检索
"""

import os
import pickle
import numpy as np
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("vector_engine.simple_vector_store")


@dataclass
class SimpleVectorDocument:
    """简化向量文档"""
    id: str
    content: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class SimpleSearchResult:
    """简化搜索结果"""
    document: SimpleVectorDocument
    score: float
    rank: int


class SimpleVectorStore:
    """简化版向量存储"""

    def __init__(self, store_path: str = "data/simple_vector_store", dimension: int = 100):
        self.logger = logger
        self.store_path = Path(store_path)
        self.dimension = dimension

        # 确保存储目录存在
        self.store_path.mkdir(parents=True, exist_ok=True)

        # 文档存储
        self.documents: Dict[str, SimpleVectorDocument] = {}
        self.vectors: np.ndarray = np.array([]).reshape(0, dimension)
        self.document_ids: List[str] = []

        # 存储文件
        self.data_file = self.store_path / "data.pkl"
        self.metadata_file = self.store_path / "metadata.json"

        # 统计信息
        self.stats = {
            "total_vectors": 0,
            "last_updated": "",
            "search_count": 0,
            "avg_search_time": 0.0
        }

    async def initialize(self) -> bool:
        """初始化向量存储"""
        try:
            self.logger.info(f"初始化简化向量存储: path={self.store_path}")

            # 加载现有数据
            await self._load_data()

            self.logger.info(f"向量存储初始化完成: vectors={len(self.documents)}")
            return True

        except Exception as e:
            self.logger.error(f"向量存储初始化失败: {e}")
            return False

    async def _load_data(self):
        """加载数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', {})
                    self.document_ids = data.get('document_ids', [])

                # 重建向量矩阵
                if self.documents:
                    vectors = []
                    for doc_id in self.document_ids:
                        if doc_id in self.documents:
                            vectors.append(self.documents[doc_id].vector)

                    if vectors:
                        self.vectors = np.vstack(vectors)
                    else:
                        self.vectors = np.array([]).reshape(0, self.dimension)

                self.logger.info(f"加载数据: {len(self.documents)} 个文档")

            except Exception as e:
                self.logger.warning(f"加载数据失败: {e}")

        # 加载元数据
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except Exception as e:
                self.logger.warning(f"加载元数据失败: {e}")

    async def add_documents(self, documents: List[SimpleVectorDocument]) -> bool:
        """添加文档"""
        if not documents:
            return True

        try:
            self.logger.info(f"添加文档: {len(documents)} 个文档")

            new_vectors = []
            for doc in documents:
                if doc.id in self.documents:
                    self.logger.warning(f"文档ID已存在，跳过: {doc.id}")
                    continue

                # 添加文档
                self.documents[doc.id] = doc
                self.document_ids.append(doc.id)
                new_vectors.append(doc.vector)

            # 更新向量矩阵
            if new_vectors:
                new_vectors_array = np.vstack(new_vectors)
                if self.vectors.size == 0:
                    self.vectors = new_vectors_array
                else:
                    self.vectors = np.vstack([self.vectors, new_vectors_array])

            # 更新统计
            self.stats["total_vectors"] = len(self.documents)
            self.stats["last_updated"] = datetime.now().isoformat()

            # 保存数据
            await self._save_data()

            self.logger.info(f"文档添加完成: total_vectors={len(self.documents)}")
            return True

        except Exception as e:
            self.logger.error(f"添加文档失败: {e}")
            return False

    async def search(self,
                    query_vector: np.ndarray,
                    top_k: int = 10,
                    threshold: float = 0.0,
                    filter_metadata: Optional[Dict] = None) -> List[SimpleSearchResult]:
        """向量搜索"""
        if len(self.documents) == 0 or self.vectors.size == 0:
            return []

        try:
            import time
            start_time = time.time()

            # 计算相似度
            similarities = self._calculate_similarities(query_vector)

            # 获取排序索引
            sorted_indices = np.argsort(similarities)[::-1]

            # 构建结果
            results = []
            for rank, idx in enumerate(sorted_indices):
                if len(results) >= top_k:
                    break

                score = similarities[idx]
                if score < threshold:
                    continue

                doc_id = self.document_ids[idx]
                if doc_id not in self.documents:
                    continue

                document = self.documents[doc_id]

                # 应用元数据过滤
                if filter_metadata:
                    if not self._match_metadata_filter(document.metadata, filter_metadata):
                        continue

                results.append(SimpleSearchResult(
                    document=document,
                    score=float(score),
                    rank=rank + 1
                ))

            # 更新统计
            search_time = time.time() - start_time
            self._update_search_stats(search_time)

            return results

        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return []

    def _calculate_similarities(self, query_vector: np.ndarray) -> np.ndarray:
        """计算相似度"""
        # 标准化查询向量
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)

        # 计算余弦相似度
        similarities = []
        for i, doc_vector in enumerate(self.vectors):
            doc_norm = doc_vector / (np.linalg.norm(doc_vector) + 1e-8)
            similarity = np.dot(query_norm, doc_norm)
            similarities.append(similarity)

        return np.array(similarities)

    def _match_metadata_filter(self, metadata: Dict, filter_conditions: Dict) -> bool:
        """检查元数据过滤条件"""
        for key, expected_value in filter_conditions.items():
            if key not in metadata:
                return False

            actual_value = metadata[key]
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            else:
                if actual_value != expected_value:
                    return False

        return True

    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if doc_id not in self.documents:
            return False

        try:
            # 找到索引
            idx = self.document_ids.index(doc_id)

            # 删除文档
            del self.documents[doc_id]
            del self.document_ids[idx]

            # 删除向量
            if self.vectors.size > 0:
                self.vectors = np.delete(self.vectors, idx, axis=0)

            # 更新统计
            self.stats["total_vectors"] = len(self.documents)
            self.stats["last_updated"] = datetime.now().isoformat()

            # 保存数据
            await self._save_data()

            return True

        except Exception as e:
            self.logger.error(f"删除文档失败: {e}")
            return False

    async def _save_data(self):
        """保存数据"""
        try:
            # 保存文档数据
            data = {
                'documents': self.documents,
                'document_ids': self.document_ids
            }

            with open(self.data_file, 'wb') as f:
                pickle.dump(data, f)

            # 保存元数据
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")

    def _update_search_stats(self, search_time: float):
        """更新搜索统计"""
        self.stats["search_count"] += 1

        # 更新平均搜索时间
        if self.stats["search_count"] > 1:
            total_time = (self.stats["avg_search_time"] *
                         (self.stats["search_count"] - 1) + search_time)
            self.stats["avg_search_time"] = total_time / self.stats["search_count"]
        else:
            self.stats["avg_search_time"] = search_time

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "dimension": self.dimension,
            "store_path": str(self.store_path),
            "documents_count": len(self.documents)
        }

    async def cleanup(self):
        """清理资源"""
        try:
            await self._save_data()
            self.logger.info("简化向量存储资源已清理")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")