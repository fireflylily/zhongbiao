#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析管理器
统一管理不同格式文档的解析过程
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.config import get_config
from common.database import get_knowledge_base_db

logger = get_module_logger("document_parser.manager")


class DocumentType(Enum):
    """文档类型枚举"""
    PDF = "pdf"
    WORD = "docx"
    DOC = "doc"
    TXT = "txt"
    UNKNOWN = "unknown"


class ParseStatus(Enum):
    """解析状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ParseResult:
    """解析结果数据类"""
    doc_id: int
    status: ParseStatus
    content: str = ""
    chunks: List[Dict] = None
    metadata: Dict = None
    error_message: str = ""
    parse_time: float = 0.0

    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []
        if self.metadata is None:
            self.metadata = {}


class ParserManager:
    """文档解析管理器"""

    def __init__(self):
        self.config = get_config()
        self.db = get_knowledge_base_db()
        self.logger = logger

        # 延迟导入解析器，避免循环导入
        self._parsers = {}
        self._text_splitter = None
        self._content_cleaner = None

        self.logger.info("文档解析管理器初始化完成")

    def _get_parser(self, doc_type: DocumentType):
        """获取对应类型的解析器"""
        if doc_type not in self._parsers:
            if doc_type == DocumentType.PDF:
                from .pdf_parser import PDFParser
                self._parsers[doc_type] = PDFParser()
            elif doc_type in [DocumentType.WORD, DocumentType.DOC]:
                from .word_parser import WordParser
                self._parsers[doc_type] = WordParser()
            elif doc_type == DocumentType.TXT:
                from .txt_parser import TXTParser
                self._parsers[doc_type] = TXTParser()
            else:
                raise ValueError(f"不支持的文档类型: {doc_type}")

        return self._parsers[doc_type]

    def _get_text_splitter(self):
        """获取文本分块器"""
        if self._text_splitter is None:
            from .text_splitter import IntelligentTextSplitter
            self._text_splitter = IntelligentTextSplitter()
        return self._text_splitter

    def _get_content_cleaner(self):
        """获取内容清洗器"""
        if self._content_cleaner is None:
            from .content_cleaner import ContentCleaner
            self._content_cleaner = ContentCleaner()
        return self._content_cleaner

    def _detect_document_type(self, file_path: str) -> DocumentType:
        """检测文档类型"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        type_mapping = {
            '.pdf': DocumentType.PDF,
            '.docx': DocumentType.WORD,
            '.doc': DocumentType.DOC,
            '.txt': DocumentType.TXT,
        }

        return type_mapping.get(suffix, DocumentType.UNKNOWN)

    async def parse_document(self, doc_id: int, file_path: str) -> ParseResult:
        """解析文档的主要方法"""
        start_time = datetime.now()

        try:
            # 更新解析状态为处理中
            self._update_parse_status(doc_id, ParseStatus.PROCESSING)

            # 检测文档类型
            doc_type = self._detect_document_type(file_path)
            if doc_type == DocumentType.UNKNOWN:
                raise ValueError(f"不支持的文档格式: {file_path}")

            self.logger.info(f"开始解析文档: doc_id={doc_id}, type={doc_type.value}, path={file_path}")

            # 获取对应的解析器
            parser = self._get_parser(doc_type)

            # 解析文档内容
            raw_content, metadata = await parser.parse(file_path)

            # 内容清洗
            cleaner = self._get_content_cleaner()
            cleaned_content = cleaner.clean_content(raw_content)

            # 文本分块
            text_splitter = self._get_text_splitter()
            chunks = text_splitter.split_text(
                content=cleaned_content,
                metadata=metadata,
                strategy='hierarchical'  # 默认使用层级分块策略
            )

            # 计算处理时间
            end_time = datetime.now()
            parse_time = (end_time - start_time).total_seconds()

            # 创建解析结果
            result = ParseResult(
                doc_id=doc_id,
                status=ParseStatus.COMPLETED,
                content=cleaned_content,
                chunks=chunks,
                metadata=metadata,
                parse_time=parse_time
            )

            # 保存解析结果到数据库
            await self._save_parse_result(result)

            # 更新文档解析状态
            self._update_parse_status(doc_id, ParseStatus.COMPLETED)

            self.logger.info(f"文档解析完成: doc_id={doc_id}, chunks={len(chunks)}, time={parse_time:.2f}s")

            return result

        except Exception as e:
            # 处理解析失败
            error_msg = f"文档解析失败: {str(e)}"
            self.logger.error(f"doc_id={doc_id}, error={error_msg}")

            # 更新失败状态
            self._update_parse_status(doc_id, ParseStatus.FAILED, error_msg)

            # 计算处理时间
            end_time = datetime.now()
            parse_time = (end_time - start_time).total_seconds()

            return ParseResult(
                doc_id=doc_id,
                status=ParseStatus.FAILED,
                error_message=error_msg,
                parse_time=parse_time
            )

    def parse_document_simple(self, file_path: str) -> str:
        """
        同步简化版本的文档解析（仅返回文本内容）
        适用于不需要完整ParseResult对象的场景，如需求分析

        Args:
            file_path: 文档路径

        Returns:
            提取的文本内容

        Raises:
            ValueError: 不支持的文档格式
            FileNotFoundError: 文件不存在
            Exception: 解析失败
        """
        import asyncio
        import concurrent.futures

        self.logger.info(f"开始简化解析文档: {file_path}")

        try:
            # 检测文档类型
            doc_type = self._detect_document_type(file_path)
            if doc_type == DocumentType.UNKNOWN:
                raise ValueError(f"不支持的文档格式: {file_path}")

            # 获取对应的解析器
            parser = self._get_parser(doc_type)

            # 在同步上下文中执行异步解析
            try:
                # 尝试获取当前事件循环
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果已有事件循环在运行，在新线程中创建新循环
                    self.logger.debug("检测到运行中的事件循环，在新线程中执行解析")
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(asyncio.run, parser.parse(file_path))
                        text, metadata = future.result(timeout=300)  # 5分钟超时
                else:
                    # 没有运行的事件循环，直接使用asyncio.run
                    self.logger.debug("使用asyncio.run执行解析")
                    text, metadata = asyncio.run(parser.parse(file_path))
            except RuntimeError:
                # 没有事件循环，创建新的
                self.logger.debug("创建新事件循环执行解析")
                text, metadata = asyncio.run(parser.parse(file_path))

            if not text or not text.strip():
                raise ValueError("文档内容为空")

            self.logger.info(f"简化解析完成，内容长度: {len(text)} 字符")
            return text

        except Exception as e:
            error_msg = f"文档解析失败: {str(e)}"
            self.logger.error(error_msg)
            raise

    def _update_parse_status(self, doc_id: int, status: ParseStatus, error_message: str = ""):
        """更新文档解析状态"""
        try:
            # 这里需要扩展数据库结构，暂时先更新现有的documents表
            query = """
            UPDATE documents
            SET parse_status = ?,
                parse_error = ?,
                parse_time = datetime('now')
            WHERE doc_id = ?
            """
            self.db.execute_query(query, (status.value, error_message, doc_id))

        except Exception as e:
            self.logger.error(f"更新解析状态失败: doc_id={doc_id}, error={e}")

    async def _save_parse_result(self, result: ParseResult):
        """保存解析结果到数据库"""
        try:
            # 保存到parse_results表（需要扩展数据库）
            chunks_json = json.dumps(result.chunks, ensure_ascii=False)
            metadata_json = json.dumps(result.metadata, ensure_ascii=False)

            query = """
            INSERT INTO document_parse_results (
                doc_id, parse_status, content_chunks,
                metadata, parse_time, error_message
            ) VALUES (?, ?, ?, ?, ?, ?)
            """

            # 注意：这个表需要在数据库扩展阶段创建
            # 暂时记录日志
            self.logger.info(f"解析结果准备保存: doc_id={result.doc_id}, chunks={len(result.chunks)}")

        except Exception as e:
            self.logger.error(f"保存解析结果失败: {e}")

    async def get_parse_status(self, doc_id: int) -> Dict:
        """获取文档解析状态"""
        try:
            # 从documents表获取解析状态
            query = """
            SELECT doc_id, parse_status, parse_error, parse_time
            FROM documents
            WHERE doc_id = ?
            """
            result = self.db.execute_query(query, (doc_id,))

            if result:
                doc_info = result[0]
                return {
                    'doc_id': doc_info['doc_id'],
                    'status': doc_info.get('parse_status', 'pending'),
                    'error_message': doc_info.get('parse_error', ''),
                    'parse_time': doc_info.get('parse_time', None),
                    'progress': self._calculate_progress(doc_info.get('parse_status', 'pending'))
                }
            else:
                return {
                    'doc_id': doc_id,
                    'status': 'not_found',
                    'error_message': '文档不存在',
                    'progress': 0
                }

        except Exception as e:
            self.logger.error(f"获取解析状态失败: doc_id={doc_id}, error={e}")
            return {
                'doc_id': doc_id,
                'status': 'error',
                'error_message': str(e),
                'progress': 0
            }

    def _calculate_progress(self, status: str) -> int:
        """计算解析进度百分比"""
        progress_mapping = {
            'pending': 0,
            'processing': 50,
            'completed': 100,
            'failed': 0
        }
        return progress_mapping.get(status, 0)

    async def batch_parse_documents(self, doc_ids: List[int]) -> List[ParseResult]:
        """批量解析文档"""
        self.logger.info(f"开始批量解析文档: {len(doc_ids)} 个文档")

        # 获取文档信息
        results = []

        # 限制并发数量，避免资源过载
        semaphore = asyncio.Semaphore(3)  # 最多同时解析3个文档

        async def parse_single_doc(doc_id):
            async with semaphore:
                # 获取文档文件路径
                doc_info = self._get_document_info(doc_id)
                if doc_info:
                    return await self.parse_document(doc_id, doc_info['file_path'])
                else:
                    return ParseResult(
                        doc_id=doc_id,
                        status=ParseStatus.FAILED,
                        error_message="文档信息不存在"
                    )

        # 并发执行解析任务
        tasks = [parse_single_doc(doc_id) for doc_id in doc_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ParseResult(
                    doc_id=doc_ids[i],
                    status=ParseStatus.FAILED,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)

        self.logger.info(f"批量解析完成: 成功={sum(1 for r in processed_results if r.status == ParseStatus.COMPLETED)}, "
                        f"失败={sum(1 for r in processed_results if r.status == ParseStatus.FAILED)}")

        return processed_results

    def _get_document_info(self, doc_id: int) -> Optional[Dict]:
        """获取文档信息"""
        try:
            query = "SELECT * FROM documents WHERE doc_id = ?"
            results = self.db.execute_query(query, (doc_id,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"获取文档信息失败: doc_id={doc_id}, error={e}")
            return None