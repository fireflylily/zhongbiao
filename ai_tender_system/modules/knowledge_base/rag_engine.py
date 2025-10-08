"""
RAG知识库引擎
基于LangChain + Chroma实现智能文档检索和问答
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    # LangChain 0.3.x 新的导入方式
    from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    # 定义占位类型以避免NameError
    Document = Any
    logging.warning(f"LangChain dependencies not installed: {e}. RAG features will be disabled.")

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

        # 初始化文本切分器（优化参数以提升搜索质量）
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # 每个文本块800字符（增加以保留更完整上下文）
            chunk_overlap=150,  # 重叠150字符保持语义连贯（增加以提升语义连续性）
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]  # 优先按段落和句子分割
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

            # 提取文档目录（如果提供了document_id）
            toc_count = 0
            if metadata and 'document_id' in metadata:
                try:
                    from .toc_extractor import TOCExtractor
                    from ...common.database import get_knowledge_base_db

                    doc_id = metadata['document_id']
                    extractor = TOCExtractor()
                    toc_entries = extractor.extract_toc(file_path, doc_id)

                    if toc_entries:
                        db = get_knowledge_base_db()
                        # 删除旧的目录条目
                        db.delete_toc_by_doc(doc_id)

                        # 插入新的目录条目（需要先插入以获取toc_id，然后更新parent关系）
                        toc_id_map = {}  # sequence_order -> toc_id
                        for entry in toc_entries:
                            toc_id = db.insert_toc_entry(
                                doc_id=entry['doc_id'],
                                heading_level=entry['heading_level'],
                                heading_text=entry['heading_text'],
                                section_number=entry.get('section_number'),
                                keywords=entry.get('keywords'),
                                page_number=entry.get('page_number'),
                                parent_toc_id=None,  # 第一次插入先不设置parent
                                sequence_order=entry['sequence_order']
                            )
                            toc_id_map[entry['sequence_order']] = toc_id

                        # TODO: 更新parent_toc_id关系（需要UPDATE语句）
                        # 暂时先不实现parent关系，后续可以通过heading_level重建

                        toc_count = len(toc_entries)
                        logger.info(f"提取了 {toc_count} 个目录条目")

                except Exception as e:
                    logger.warning(f"提取目录失败，但不影响向量化: {e}")

            return {
                'success': True,
                'file_path': file_path,
                'chunks_count': len(splits),
                'vector_ids': ids,
                'toc_count': toc_count
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
        filter_dict: Optional[Dict[str, Any]] = None,
        hybrid: bool = True,
        include_toc: bool = True
    ) -> Dict[str, Any]:
        """
        三层混合搜索（目录 + 向量）

        Args:
            query: 查询问题
            k: 返回结果数量
            filter_dict: 过滤条件（如指定公司ID）
            hybrid: 是否使用混合搜索（关键词+语义）
            include_toc: 是否包含目录搜索

        Returns:
            {
                'toc_results': [...],  # 目录搜索结果
                'content_results': [...],  # 内容搜索结果
                'total_count': int
            }
        """
        try:
            all_results = {
                'toc_results': [],
                'content_results': [],
                'total_count': 0
            }

            # 第一层 & 第二层：目录搜索（如果启用）
            if include_toc:
                try:
                    toc_results = self._search_toc(query, filter_dict, k)
                    all_results['toc_results'] = toc_results
                    logger.info(f"目录搜索到 {len(toc_results)} 条结果")
                except Exception as e:
                    logger.warning(f"目录搜索失败: {e}")

            # 第三层：向量语义搜索（获取更多候选用于重排序）
            search_k = min(k * 10, 50) if hybrid else k

            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query,
                    k=search_k,
                    filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=search_k)

            # 格式化向量搜索结果并去重
            formatted_results = []
            seen_content = set()  # 用于内容去重

            for doc, score in results:
                # 使用内容的前200个字符进行去重判断
                content_hash = hash(doc.page_content[:200])

                # 跳过重复内容
                if content_hash in seen_content:
                    continue
                seen_content.add(content_hash)

                formatted_results.append({
                    'content': doc.page_content,
                    'score': float(1 / (1 + score)),
                    'metadata': doc.metadata,
                    'source': doc.metadata.get('source', '未知来源')
                })

            # 如果启用混合搜索，进行关键词加权重排
            if hybrid and formatted_results:
                formatted_results = self._rerank_with_keywords(formatted_results, query, k)

            all_results['content_results'] = formatted_results
            all_results['total_count'] = len(all_results['toc_results']) + len(formatted_results)

            logger.info(f"检索完成，查询: {query}, 目录结果:{len(all_results['toc_results'])}, "
                       f"内容结果:{len(formatted_results)}")
            return all_results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return {
                'toc_results': [],
                'content_results': [],
                'total_count': 0
            }

    def _search_toc(self, query: str, filter_dict: Optional[Dict], k: int = 5) -> List[Dict]:
        """
        搜索文档目录

        Returns:
            目录搜索结果列表
        """
        import re
        from ai_tender_system.common.database import get_knowledge_base_db

        db = get_knowledge_base_db()
        toc_results = []

        # 定义停用词列表(通用词、无实际语义的词)
        stopwords = {'查询', '接口', '验证', '检测', '监测', '信息', '数据', '服务', '平台', '系统'}

        # 提取查询关键词
        keywords = []
        # 提取数字（接口编号）- 数字是最重要的特征,不过滤
        numbers = re.findall(r'\d{3,}', query)
        keywords.extend(numbers)

        # 提取中文关键词并过滤停用词
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,8}', query)
        for word in chinese_words[:5]:  # 最多取5个候选
            if word not in stopwords:
                keywords.append(word)
                if len(keywords) >= 5:  # 最多保留5个关键词
                    break

        # 第一层：关键词精确匹配（权重90%）
        if keywords:
            try:
                doc_id = filter_dict.get('document_id') if filter_dict else None
                keyword_matches = db.search_toc_by_keywords(keywords, doc_id)
                for match in keyword_matches:
                    # 计算匹配度：统计匹配了多少个关键词
                    import json
                    stored_keywords = json.loads(match.get('keywords', '[]'))
                    matched_count = 0

                    # 统计有多少个查询关键词在存储的关键词中
                    # 支持双向匹配: kw包含sk 或 sk包含kw
                    for kw in keywords:
                        for sk in stored_keywords:
                            if kw in sk or sk in kw:
                                matched_count += 1
                                break  # 每个查询关键词最多匹配一次

                    # 根据匹配数量计算分数
                    # 匹配所有关键词=0.95, 匹配大部分=0.9, 匹配少数=0.7
                    if matched_count == len(keywords):
                        score = 0.95
                    elif matched_count >= len(keywords) * 0.6:
                        score = 0.9
                    else:
                        score = 0.7

                    toc_results.append({
                        'toc_id': match['toc_id'],
                        'heading_text': match['heading_text'],
                        'section_number': match.get('section_number'),
                        'page_number': match.get('page_number'),
                        'heading_level': match['heading_level'],
                        'score': score,
                        'match_type': 'keyword',
                        'matched_keywords': matched_count  # 调试信息
                    })
            except Exception as e:
                logger.warning(f"关键词目录搜索失败: {e}")

        # 第二层：文本模糊匹配（权重70%）
        try:
            doc_id = filter_dict.get('document_id') if filter_dict else None
            text_matches = db.search_toc_by_text(query, doc_id)
            for match in text_matches:
                # 去重：如果已经通过关键词匹配到了，跳过
                if any(r['toc_id'] == match['toc_id'] for r in toc_results):
                    continue

                toc_results.append({
                    'toc_id': match['toc_id'],
                    'heading_text': match['heading_text'],
                    'section_number': match.get('section_number'),
                    'page_number': match.get('page_number'),
                    'heading_level': match['heading_level'],
                    'score': 0.7,  # 文本模糊匹配中等分数
                    'match_type': 'fuzzy'
                })
        except Exception as e:
            logger.warning(f"文本目录搜索失败: {e}")

        # 排序并返回topK
        toc_results.sort(key=lambda x: x['score'], reverse=True)
        return toc_results[:k]

    def _rerank_with_keywords(
        self,
        results: List[Dict[str, Any]],
        query: str,
        k: int
    ) -> List[Dict[str, Any]]:
        """
        使用关键词匹配重新排序结果

        Args:
            results: 初始搜索结果
            query: 查询文本
            k: 返回结果数量

        Returns:
            重排序后的结果
        """
        import re

        # 提取查询中的关键词（数字、中文词组）
        keywords = []

        # 提取数字（如接口编号300091）
        numbers = re.findall(r'\d{3,}', query)
        keywords.extend(numbers)

        # 提取中文关键词（2-8个字的词组）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,8}', query)
        keywords.extend(chinese_words)

        logger.info(f"提取关键词: {keywords}")

        # 为每个结果计算关键词匹配分数
        for result in results:
            content = result['content']
            keyword_score = 0

            for keyword in keywords:
                if keyword in content:
                    # 精确匹配加分
                    keyword_score += 0.3

                    # 如果是数字且在前100个字符中出现，额外加分（可能是接口编号）
                    if keyword.isdigit() and keyword in content[:100]:
                        keyword_score += 0.4

                    # 统计出现次数
                    count = content.count(keyword)
                    keyword_score += min(count * 0.1, 0.3)  # 最多加0.3分

            # 限制keyword_score最大值为1.0，防止分数无限累加
            keyword_score = min(keyword_score, 1.0)

            # 综合分数：语义相似度(70%) + 关键词匹配(30%)，确保最终分数不超过1.0
            result['original_score'] = result['score']
            result['keyword_score'] = keyword_score
            result['score'] = min(result['score'] * 0.7 + keyword_score * 0.3, 1.0)

        # 按综合分数重新排序
        results.sort(key=lambda x: x['score'], reverse=True)

        # 返回前k个结果
        return results[:k]

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