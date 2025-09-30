"""
RAG知识库引擎
基于LangChain + Chroma实现智能文档检索和问答
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # 定义占位类型以避免NameError
    Document = Any
    logging.warning("LangChain dependencies not installed. RAG features will be disabled.")

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG知识库引擎"""

    def __init__(self, persist_directory: str = None):
        """
        初始化RAG引擎

        Args:
            persist_directory: 向量数据库持久化目录
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain dependencies not installed. Please run: pip install -r requirements_rag.txt")

        self.persist_directory = persist_directory or os.path.join(
            os.path.dirname(__file__), '../data/chroma_db'
        )

        # 确保目录存在
        os.makedirs(self.persist_directory, exist_ok=True)

        # 初始化Embedding模型（中文优化）
        logger.info("正在加载Embedding模型...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 初始化文本切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 每个文本块500字符
            chunk_overlap=50,  # 重叠50字符保持语义连贯
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )

        # 初始化或加载向量存储
        logger.info(f"初始化向量数据库: {self.persist_directory}")
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

        logger.info("RAG引擎初始化完成")

    def load_document(self, file_path: str) -> List[Document]:
        """
        加载文档

        Args:
            file_path: 文档路径

        Returns:
            文档对象列表
        """
        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_ext in ['.docx', '.doc']:
                loader = Docx2txtLoader(file_path)
            elif file_ext == '.txt':
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")

            documents = loader.load()
            logger.info(f"成功加载文档: {file_path}, 共{len(documents)}页")
            return documents

        except Exception as e:
            logger.error(f"加载文档失败: {file_path}, 错误: {e}")
            raise

    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        添加文档到知识库

        Args:
            file_path: 文档路径
            metadata: 文档元数据（公司ID、产品ID、文档类型等）

        Returns:
            处理结果
        """
        try:
            # 加载文档
            documents = self.load_document(file_path)

            # 添加元数据
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)

            # 文本切分
            splits = self.text_splitter.split_documents(documents)
            logger.info(f"文档切分为{len(splits)}个文本块")

            # 添加到向量存储
            ids = self.vectorstore.add_documents(splits)

            # 持久化
            self.vectorstore.persist()

            return {
                'success': True,
                'file_path': file_path,
                'chunks_count': len(splits),
                'vector_ids': ids
            }

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        智能检索

        Args:
            query: 查询问题
            k: 返回结果数量
            filter_dict: 过滤条件（如指定公司ID）

        Returns:
            检索结果列表
        """
        try:
            # 执行相似度搜索
            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)

            # 格式化结果
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'score': float(1 - score),  # 转换为相似度分数
                    'metadata': doc.metadata,
                    'source': doc.metadata.get('source', '未知来源')
                })

            logger.info(f"检索完成，查询: {query}, 返回{len(formatted_results)}条结果")
            return formatted_results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def delete_by_metadata(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据元数据删除文档

        Args:
            filter_dict: 过滤条件（如{'company_id': 8, 'document_id': 123}）

        Returns:
            删除结果
        """
        try:
            # Chroma不直接支持按metadata删除，需要先查询再删除
            results = self.vectorstore.similarity_search("", k=10000, filter=filter_dict)

            if not results:
                return {'success': True, 'deleted_count': 0}

            # 获取ID并删除
            ids = [doc.metadata.get('id') for doc in results if doc.metadata.get('id')]

            if ids:
                self.vectorstore.delete(ids)
                self.vectorstore.persist()

            return {
                'success': True,
                'deleted_count': len(ids)
            }

        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            统计信息
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()

            return {
                'total_chunks': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'total_chunks': 0,
                'error': str(e)
            }


# 全局单例
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    """获取RAG引擎单例"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine