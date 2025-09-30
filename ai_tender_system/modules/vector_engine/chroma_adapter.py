"""
Chroma适配器
将Chroma向量数据库适配到现有的SimpleVectorStore接口
保持API兼容性，无缝替换SimpleVectorStore
"""
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("vector_engine.chroma_adapter")

# 延迟导入Chroma
_chromadb = None

def get_chromadb():
    global _chromadb
    if _chromadb is None:
        try:
            import chromadb
            _chromadb = chromadb
            logger.info("Chroma数据库模块加载成功")
        except ImportError:
            logger.warning("Chroma未安装，请运行: pip install chromadb")
            raise ImportError("需要安装Chroma: pip install chromadb")
    return _chromadb


@dataclass
class ChromaVectorDocument:
    """向量文档数据类（兼容SimpleVectorDocument接口）"""
    id: str
    content: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ChromaSearchResult:
    """搜索结果数据类（兼容SimpleSearchResult接口）"""
    document: ChromaVectorDocument
    score: float
    rank: int


class ChromaVectorStore:
    """
    Chroma向量存储适配器
    兼容SimpleVectorStore的接口，但使用Chroma作为底层实现
    """

    def __init__(self, dimension: int = 100, persist_directory: str = None):
        """
        初始化Chroma向量存储

        Args:
            dimension: 向量维度（Chroma会自动检测，这里保留参数是为了接口兼容）
            persist_directory: 持久化目录
        """
        self.logger = logger
        self.dimension = dimension

        # 设置持久化目录
        if persist_directory is None:
            self.persist_directory = str(Path(__file__).parent.parent.parent / "data" / "chroma_vector_db")
        else:
            self.persist_directory = persist_directory

        # Chroma客户端和集合
        self.client = None
        self.collection = None

        # 文档缓存（为了兼容某些直接访问documents的代码）
        self.documents = {}

        self.is_initialized = False

        logger.info(f"Chroma向量存储初始化 - 维度: {dimension}, 存储路径: {self.persist_directory}")

    async def initialize(self):
        """异步初始化Chroma客户端"""
        try:
            chromadb = get_chromadb()

            # 创建持久化客户端
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="vector_search_collection",
                metadata={"description": "向量搜索主集合"}
            )

            # 加载现有文档到缓存
            await self._load_documents_cache()

            self.is_initialized = True
            logger.info(f"Chroma向量存储初始化完成 - 已有文档数: {self.collection.count()}")

        except Exception as e:
            logger.error(f"Chroma初始化失败: {e}")
            raise

    async def _load_documents_cache(self):
        """加载文档到内存缓存"""
        try:
            # 获取所有文档ID
            results = self.collection.get()

            if results and results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    self.documents[doc_id] = ChromaVectorDocument(
                        id=doc_id,
                        content=results['documents'][i] if results['documents'] else "",
                        vector=np.array(results['embeddings'][i]) if results['embeddings'] else np.zeros(self.dimension),
                        metadata=results['metadatas'][i] if results['metadatas'] else {},
                        created_at=results['metadatas'][i].get('created_at', '') if results['metadatas'] else ''
                    )

            logger.info(f"文档缓存加载完成: {len(self.documents)} 个文档")

        except Exception as e:
            logger.warning(f"加载文档缓存失败: {e}")

    async def add_document(self, doc_id: str, content: str, vector: np.ndarray, metadata: Dict = None):
        """
        添加文档到向量存储

        Args:
            doc_id: 文档ID
            content: 文档内容
            vector: 文档向量
            metadata: 元数据
        """
        try:
            if metadata is None:
                metadata = {}

            # 清理元数据：移除None值（Chroma不支持None）
            cleaned_metadata = {k: v for k, v in metadata.items() if v is not None}

            # 添加时间戳
            if 'created_at' not in cleaned_metadata:
                cleaned_metadata['created_at'] = datetime.now().isoformat()

            # 添加到Chroma
            self.collection.add(
                ids=[doc_id],
                documents=[content],
                embeddings=[vector.tolist()],
                metadatas=[cleaned_metadata]
            )

            # 更新缓存
            self.documents[doc_id] = ChromaVectorDocument(
                id=doc_id,
                content=content,
                vector=vector,
                metadata=metadata,
                created_at=metadata.get('created_at', '')
            )

            logger.info(f"文档已添加: {doc_id}")

        except Exception as e:
            logger.error(f"添加文档失败 {doc_id}: {e}")
            raise

    async def add_documents(self, documents: List[ChromaVectorDocument]) -> bool:
        """
        批量添加文档到向量存储（兼容SimpleVectorStore接口）

        Args:
            documents: ChromaVectorDocument对象列表

        Returns:
            是否成功
        """
        try:
            if not documents:
                return True

            ids = []
            contents = []
            embeddings = []
            metadatas = []

            for doc in documents:
                # 清理元数据：移除None值
                cleaned_metadata = {k: v for k, v in doc.metadata.items() if v is not None}

                # 确保元数据包含时间戳
                if 'created_at' not in cleaned_metadata:
                    cleaned_metadata['created_at'] = datetime.now().isoformat()

                ids.append(doc.id)
                contents.append(doc.content)
                embeddings.append(doc.vector.tolist())
                metadatas.append(cleaned_metadata)

                # 更新缓存（使用清理后的元数据）
                doc.metadata = cleaned_metadata
                self.documents[doc.id] = doc

            # 批量添加到Chroma
            self.collection.add(
                ids=ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"批量添加文档完成: {len(documents)} 个文档")
            return True

        except Exception as e:
            logger.error(f"批量添加文档失败: {e}")
            return False

    async def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
        filter_metadata: Dict = None
    ) -> List[ChromaSearchResult]:
        """
        执行向量搜索

        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            threshold: 相似度阈值
            filter_metadata: 元数据过滤条件

        Returns:
            搜索结果列表
        """
        try:
            # Chroma搜索
            results = self.collection.query(
                query_embeddings=[query_vector.tolist()],
                n_results=top_k,
                where=filter_metadata if filter_metadata else None
            )

            # 转换为ChromaSearchResult格式
            search_results = []

            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    # Chroma返回的是距离，需要转换为相似度分数
                    distance = results['distances'][0][i] if results['distances'] else 0
                    score = 1.0 / (1.0 + distance)  # 距离转相似度

                    # 应用阈值过滤
                    if score < threshold:
                        continue

                    doc = ChromaVectorDocument(
                        id=doc_id,
                        content=results['documents'][0][i] if results['documents'] else "",
                        vector=np.array(results['embeddings'][0][i]) if results['embeddings'] else np.zeros(self.dimension),
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                        created_at=results['metadatas'][0][i].get('created_at', '') if results['metadatas'] else ''
                    )

                    search_result = ChromaSearchResult(
                        document=doc,
                        score=score,
                        rank=i + 1
                    )

                    search_results.append(search_result)

            logger.info(f"搜索完成: 返回 {len(search_results)} 个结果")
            return search_results

        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []

    async def delete_document(self, doc_id: str):
        """删除文档"""
        try:
            self.collection.delete(ids=[doc_id])

            # 从缓存中删除
            if doc_id in self.documents:
                del self.documents[doc_id]

            logger.info(f"文档已删除: {doc_id}")

        except Exception as e:
            logger.error(f"删除文档失败 {doc_id}: {e}")
            raise

    async def update_document(self, doc_id: str, content: str = None, vector: np.ndarray = None, metadata: Dict = None):
        """更新文档"""
        try:
            update_data = {'ids': [doc_id]}

            if content is not None:
                update_data['documents'] = [content]
            if vector is not None:
                update_data['embeddings'] = [vector.tolist()]
            if metadata is not None:
                if 'updated_at' not in metadata:
                    metadata['updated_at'] = datetime.now().isoformat()
                update_data['metadatas'] = [metadata]

            self.collection.update(**update_data)

            # 更新缓存
            if doc_id in self.documents:
                doc = self.documents[doc_id]
                if content is not None:
                    doc.content = content
                if vector is not None:
                    doc.vector = vector
                if metadata is not None:
                    doc.metadata.update(metadata)

            logger.info(f"文档已更新: {doc_id}")

        except Exception as e:
            logger.error(f"更新文档失败 {doc_id}: {e}")
            raise

    def get_stats(self) -> Dict:
        """获取统计信息（兼容SimpleVectorStore接口）"""
        try:
            return {
                'total_documents': self.collection.count() if self.collection else 0,
                'dimension': self.dimension,
                'backend': 'Chroma',
                'persist_directory': self.persist_directory,
                'initialized': self.is_initialized
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'total_documents': 0,
                'dimension': self.dimension,
                'backend': 'Chroma',
                'error': str(e)
            }

    async def clear(self):
        """清空所有文档"""
        try:
            # Chroma没有直接的clear方法，需要删除集合重建
            if self.collection:
                self.client.delete_collection(name="vector_search_collection")
                self.collection = self.client.create_collection(
                    name="vector_search_collection",
                    metadata={"description": "向量搜索主集合"}
                )
                self.documents.clear()
                logger.info("向量存储已清空")

        except Exception as e:
            logger.error(f"清空向量存储失败: {e}")
            raise


# 创建全局实例（可选）
_chroma_store_instance = None

def get_chroma_store(dimension: int = 100, persist_directory: str = None) -> ChromaVectorStore:
    """获取ChromaVectorStore单例"""
    global _chroma_store_instance
    if _chroma_store_instance is None:
        _chroma_store_instance = ChromaVectorStore(dimension, persist_directory)
    return _chroma_store_instance