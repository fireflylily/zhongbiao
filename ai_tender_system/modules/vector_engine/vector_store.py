#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量存储服务
基于FAISS实现高效的向量索引和检索
"""

import os
import pickle
import numpy as np
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import time

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("vector_engine.vector_store")

# 延迟导入FAISS
_faiss = None

def get_faiss():
    global _faiss
    if _faiss is None:
        try:
            import faiss
            _faiss = faiss
        except ImportError:
            raise ImportError("需要安装FAISS: pip install faiss-cpu")
    return _faiss


@dataclass
class VectorDocument:
    """向量文档数据类"""
    id: str
    content: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典格式（不包含vector）"""
        return {
            'id': self.id,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at
        }


@dataclass
class SearchResult:
    """搜索结果数据类"""
    document: VectorDocument
    score: float
    rank: int


class VectorStore:
    """向量存储服务"""

    def __init__(self,
                 store_path: str = "data/vector_store",
                 dimension: int = 384,
                 index_type: str = "flat"):
        """
        初始化向量存储

        Args:
            store_path: 存储路径
            dimension: 向量维度
            index_type: 索引类型 (flat, ivf, hnsw)
        """
        self.logger = logger
        self.store_path = Path(store_path)
        self.dimension = dimension
        self.index_type = index_type

        # 确保存储目录存在
        self.store_path.mkdir(parents=True, exist_ok=True)

        # FAISS索引
        self.index = None
        self.index_file = self.store_path / "vector.index"

        # 文档存储
        self.documents: Dict[str, VectorDocument] = {}
        self.document_file = self.store_path / "documents.pkl"
        self.metadata_file = self.store_path / "metadata.json"

        # ID映射（FAISS索引位置到文档ID）
        self.id_mapping: Dict[int, str] = {}
        self.next_index = 0

        # 索引配置
        self.index_config = {
            "flat": {"factory": "Flat", "description": "精确搜索，内存占用大"},
            "ivf": {"factory": "IVF100,Flat", "description": "倒排索引，平衡速度和精度"},
            "hnsw": {"factory": "HNSW32", "description": "分层图索引，快速近似搜索"}
        }

        # 统计信息
        self.stats = {
            "total_vectors": 0,
            "last_updated": "",
            "index_build_time": 0.0,
            "search_count": 0,
            "avg_search_time": 0.0
        }

    async def initialize(self) -> bool:
        """初始化向量存储"""
        try:
            self.logger.info(f"初始化向量存储: path={self.store_path}, dim={self.dimension}")

            # 加载现有数据
            await self._load_existing_data()

            # 初始化FAISS索引
            await self._initialize_index()

            self.logger.info(f"向量存储初始化完成: vectors={len(self.documents)}")
            return True

        except Exception as e:
            self.logger.error(f"向量存储初始化失败: {e}")
            return False

    async def _load_existing_data(self):
        """加载现有数据"""
        # 加载文档数据
        if self.document_file.exists():
            try:
                loop = asyncio.get_event_loop()
                with open(self.document_file, 'rb') as f:
                    data = await loop.run_in_executor(None, pickle.load, f)
                    self.documents = data.get('documents', {})
                    self.id_mapping = data.get('id_mapping', {})
                    self.next_index = data.get('next_index', 0)

                self.logger.info(f"加载文档数据: {len(self.documents)} 个文档")
            except Exception as e:
                self.logger.warning(f"加载文档数据失败: {e}")

        # 加载元数据
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except Exception as e:
                self.logger.warning(f"加载元数据失败: {e}")

    async def _initialize_index(self):
        """初始化FAISS索引"""
        faiss = get_faiss()

        if self.index_file.exists() and self.documents:
            try:
                # 加载现有索引
                loop = asyncio.get_event_loop()
                self.index = await loop.run_in_executor(None, faiss.read_index, str(self.index_file))
                self.logger.info("加载现有FAISS索引")
            except Exception as e:
                self.logger.warning(f"加载FAISS索引失败，创建新索引: {e}")
                self.index = None

        if self.index is None:
            # 创建新索引
            config = self.index_config.get(self.index_type, self.index_config["flat"])
            factory_string = config["factory"]

            if self.index_type == "flat":
                self.index = faiss.IndexFlatIP(self.dimension)  # 内积索引
            elif self.index_type == "ivf":
                quantizer = faiss.IndexFlatIP(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            elif self.index_type == "hnsw":
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                self.index.hnsw.efConstruction = 200
            else:
                self.index = faiss.IndexFlatIP(self.dimension)

            self.logger.info(f"创建新FAISS索引: type={self.index_type}")

            # 如果有现有数据，重建索引
            if self.documents:
                await self._rebuild_index()

    async def add_documents(self, documents: List[VectorDocument]) -> bool:
        """
        添加文档到向量存储

        Args:
            documents: 文档列表

        Returns:
            bool: 是否成功
        """
        if not documents:
            return True

        try:
            self.logger.info(f"添加文档到向量存储: {len(documents)} 个文档")
            start_time = time.time()

            # 准备向量和映射
            vectors = []
            for doc in documents:
                if doc.id in self.documents:
                    self.logger.warning(f"文档ID已存在，跳过: {doc.id}")
                    continue

                # 添加到文档存储
                self.documents[doc.id] = doc

                # 准备向量数据
                vector = doc.vector
                if vector.ndim == 1:
                    vector = vector.reshape(1, -1)
                vectors.append(vector)

                # 更新ID映射
                self.id_mapping[self.next_index] = doc.id
                self.next_index += 1

            if not vectors:
                self.logger.warning("没有新文档需要添加")
                return True

            # 添加向量到索引
            vectors_array = np.vstack(vectors).astype('float32')

            if self.index_type == "ivf" and not getattr(self.index, 'is_trained', False):
                # IVF索引需要训练
                if len(vectors_array) >= 100:  # 需要足够的训练数据
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.index.train, vectors_array)

            # 添加向量
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.index.add, vectors_array)

            # 更新统计
            self.stats["total_vectors"] = len(self.documents)
            self.stats["last_updated"] = datetime.now().isoformat()

            # 保存数据
            await self._save_data()

            processing_time = time.time() - start_time
            self.logger.info(f"文档添加完成: vectors={len(vectors_array)}, "
                           f"time={processing_time:.2f}s")

            return True

        except Exception as e:
            self.logger.error(f"添加文档失败: {e}")
            return False

    async def search(self,
                    query_vector: np.ndarray,
                    top_k: int = 10,
                    threshold: float = 0.0,
                    filter_metadata: Optional[Dict] = None) -> List[SearchResult]:
        """
        向量搜索

        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            threshold: 相似度阈值
            filter_metadata: 元数据过滤条件

        Returns:
            List[SearchResult]: 搜索结果
        """
        if not self.index or len(self.documents) == 0:
            return []

        try:
            start_time = time.time()

            # 准备查询向量
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            query_vector = query_vector.astype('float32')

            # 执行搜索
            loop = asyncio.get_event_loop()
            scores, indices = await loop.run_in_executor(
                None, self.index.search, query_vector, min(top_k * 2, len(self.documents))
            )

            # 处理搜索结果
            results = []
            for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS返回-1表示无效结果
                    continue

                if score < threshold:
                    continue

                # 获取文档ID
                doc_id = self.id_mapping.get(idx)
                if not doc_id or doc_id not in self.documents:
                    continue

                document = self.documents[doc_id]

                # 应用元数据过滤
                if filter_metadata:
                    if not self._match_metadata_filter(document.metadata, filter_metadata):
                        continue

                results.append(SearchResult(
                    document=document,
                    score=float(score),
                    rank=rank
                ))

                if len(results) >= top_k:
                    break

            # 更新搜索统计
            search_time = time.time() - start_time
            self._update_search_stats(search_time)

            self.logger.info(f"向量搜索完成: query_dim={query_vector.shape[1]}, "
                           f"results={len(results)}, time={search_time:.3f}s")

            return results

        except Exception as e:
            self.logger.error(f"向量搜索失败: {e}")
            return []

    def _match_metadata_filter(self, metadata: Dict, filter_conditions: Dict) -> bool:
        """检查元数据是否匹配过滤条件"""
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
        """
        删除文档（软删除）

        Args:
            doc_id: 文档ID

        Returns:
            bool: 是否成功
        """
        if doc_id not in self.documents:
            self.logger.warning(f"文档不存在: {doc_id}")
            return False

        try:
            # 从文档存储中删除
            del self.documents[doc_id]

            # 从ID映射中删除
            index_to_remove = None
            for idx, mapped_id in self.id_mapping.items():
                if mapped_id == doc_id:
                    index_to_remove = idx
                    break

            if index_to_remove is not None:
                del self.id_mapping[index_to_remove]

            # 更新统计
            self.stats["total_vectors"] = len(self.documents)
            self.stats["last_updated"] = datetime.now().isoformat()

            # 保存数据
            await self._save_data()

            self.logger.info(f"文档删除成功: {doc_id}")
            return True

        except Exception as e:
            self.logger.error(f"删除文档失败: {doc_id}, error={e}")
            return False

    async def _rebuild_index(self):
        """重建索引"""
        if not self.documents:
            return

        try:
            self.logger.info("开始重建向量索引")
            start_time = time.time()

            # 收集所有向量
            vectors = []
            new_id_mapping = {}
            index = 0

            for doc_id, doc in self.documents.items():
                vector = doc.vector
                if vector.ndim == 1:
                    vector = vector.reshape(1, -1)
                vectors.append(vector)
                new_id_mapping[index] = doc_id
                index += 1

            if vectors:
                vectors_array = np.vstack(vectors).astype('float32')

                # 清空现有索引
                self.index.reset()

                # 训练索引（如果需要）
                if self.index_type == "ivf":
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.index.train, vectors_array)

                # 添加向量
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.index.add, vectors_array)

                # 更新映射
                self.id_mapping = new_id_mapping
                self.next_index = len(vectors)

            build_time = time.time() - start_time
            self.stats["index_build_time"] = build_time

            self.logger.info(f"索引重建完成: vectors={len(vectors)}, time={build_time:.2f}s")

        except Exception as e:
            self.logger.error(f"重建索引失败: {e}")
            raise

    async def _save_data(self):
        """保存数据到磁盘"""
        try:
            # 保存文档数据
            data = {
                'documents': self.documents,
                'id_mapping': self.id_mapping,
                'next_index': self.next_index
            }

            loop = asyncio.get_event_loop()
            with open(self.document_file, 'wb') as f:
                await loop.run_in_executor(None, pickle.dump, data, f)

            # 保存FAISS索引
            if self.index:
                await loop.run_in_executor(None, get_faiss().write_index, self.index, str(self.index_file))

            # 保存元数据
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            raise

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
        """获取存储统计信息"""
        return {
            **self.stats,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "store_path": str(self.store_path),
            "documents_count": len(self.documents)
        }

    async def cleanup(self):
        """清理资源"""
        try:
            await self._save_data()
            self.logger.info("向量存储资源已清理")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")