#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 能力提取器

从产品文档中自动提取产品能力描述，包括：
- 功能能力（如"支持实时风控决策"）
- 技术指标（如"响应时间<50ms"）
- 服务能力（如"7x24小时运维支持"）

提取结果存入 product_capabilities_index 表，支持向量检索。
"""

import json
import logging
import sqlite3
import struct
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from ai_tender_system.common import create_llm_client


def get_embedding_service():
    """获取嵌入服务（延迟初始化）"""
    try:
        from ai_tender_system.modules.vector_engine import EmbeddingService
        return SimpleEmbeddingWrapper()
    except ImportError:
        return None


class SimpleEmbeddingWrapper:
    """简单的嵌入服务同步包装器"""

    def __init__(self):
        import asyncio
        from ai_tender_system.modules.vector_engine import EmbeddingService
        self.service = EmbeddingService()
        self.model_name = self.service.model_type
        self._loop = None

    def _get_loop(self):
        """获取或创建事件循环"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def get_embedding(self, text: str) -> Optional[bytes]:
        """获取文本的嵌入向量（返回序列化的bytes）"""
        import asyncio
        try:
            loop = self._get_loop()
            result = loop.run_until_complete(self.service.embed_texts([text]))
            if result.vectors is not None and len(result.vectors) > 0:
                # 序列化为bytes
                vector = result.vectors[0]
                return struct.pack(f'{len(vector)}f', *vector)
            return None
        except Exception as e:
            logging.getLogger(__name__).warning(f"获取嵌入向量失败: {e}")
            return None


class CapabilityExtractor:
    """AI 能力提取器"""

    # 能力提取提示词
    EXTRACTION_PROMPT = """你是一个专业的技术文档分析专家。请从以下产品文档片段中提取产品能力描述。

## 文档内容
{content}

## 提取要求
1. 提取具体的产品功能、技术能力、服务能力
2. 每个能力应该是可以用于回答招标需求的具体描述
3. 如果有量化指标（如性能参数），一定要提取
4. 忽略营销性描述，只保留技术事实

## 输出格式（JSON数组）
[
    {{
        "capability_name": "能力名称（简短，10字以内）",
        "capability_type": "功能类型：function/interface/service/performance",
        "capability_description": "详细描述（50-100字）",
        "metrics": {{"指标名": "指标值"}},  // 如果有量化指标
        "original_text": "原文摘录（作为证据）",
        "confidence": 0.9  // 提取置信度 0-1
    }}
]

## 示例
文档：系统采用分布式架构设计，支持水平扩展，单节点可处理10万TPS，响应时间P99<50ms。

提取结果：
[
    {{
        "capability_name": "高性能处理",
        "capability_type": "performance",
        "capability_description": "系统采用分布式架构，支持水平扩展，具备高性能处理能力",
        "metrics": {{"TPS": "10万/节点", "响应时间P99": "<50ms"}},
        "original_text": "系统采用分布式架构设计，支持水平扩展，单节点可处理10万TPS，响应时间P99<50ms",
        "confidence": 0.95
    }}
]

请分析以上文档，提取所有产品能力。如果没有可提取的能力，返回空数组 []。
只返回JSON数组，不要有其他文字。
"""

    def __init__(
        self,
        db_path: str = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        初始化能力提取器

        Args:
            db_path: 数据库路径
            model_name: LLM模型名称
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "knowledge_base.db")
        self.db_path = db_path
        self.model_name = model_name
        self.llm_client = create_llm_client(model_name)
        self.embedding_service = get_embedding_service()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def extract_from_text(
        self,
        content: str,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        从文本中提取能力

        Args:
            content: 文档内容
            min_confidence: 最小置信度阈值

        Returns:
            提取的能力列表
        """
        if not content or len(content.strip()) < 50:
            return []

        prompt = self.EXTRACTION_PROMPT.format(content=content[:4000])

        try:
            response = self.llm_client.call(
                prompt=prompt,
                purpose="能力提取"
            )

            # 解析JSON
            capabilities = self._parse_response(response)

            # 过滤低置信度
            capabilities = [
                c for c in capabilities
                if c.get('confidence', 0) >= min_confidence
            ]

            return capabilities

        except Exception as e:
            self.logger.error(f"能力提取失败: {e}")
            return []

    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """解析LLM响应"""
        try:
            # 清理响应
            text = response.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()

            return json.loads(text)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return []

    def extract_from_document(
        self,
        doc_id: int,
        company_id: int,
        tag_id: int = None,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        从文档的所有chunk中提取能力

        Args:
            doc_id: 文档ID
            company_id: 企业ID
            tag_id: 关联的能力标签ID（可选）
            min_confidence: 最小置信度

        Returns:
            提取结果统计
        """
        conn = self._get_connection()
        result = {
            "doc_id": doc_id,
            "total_chunks": 0,
            "capabilities_extracted": 0,
            "capabilities_saved": 0,
            "errors": []
        }

        try:
            # 获取文档的所有chunk
            cursor = conn.execute(
                """
                SELECT chunk_id, content, chunk_index
                FROM document_chunks
                WHERE doc_id = ?
                ORDER BY chunk_index
                """,
                (doc_id,)
            )
            chunks = cursor.fetchall()
            result['total_chunks'] = len(chunks)

            for chunk in chunks:
                chunk_id = chunk['chunk_id']
                content = chunk['content']

                try:
                    # 提取能力
                    capabilities = self.extract_from_text(content, min_confidence)
                    result['capabilities_extracted'] += len(capabilities)

                    # 保存到数据库
                    for cap in capabilities:
                        saved = self._save_capability(
                            conn=conn,
                            company_id=company_id,
                            doc_id=doc_id,
                            chunk_id=chunk_id,
                            capability=cap,
                            tag_id=tag_id
                        )
                        if saved:
                            result['capabilities_saved'] += 1

                except Exception as e:
                    result['errors'].append({
                        "chunk_id": chunk_id,
                        "error": str(e)
                    })

            conn.commit()
            self.logger.info(
                f"文档 {doc_id} 能力提取完成: "
                f"提取 {result['capabilities_extracted']} 个, "
                f"保存 {result['capabilities_saved']} 个"
            )

        except Exception as e:
            self.logger.error(f"文档能力提取失败: {e}")
            result['errors'].append({"error": str(e)})
        finally:
            conn.close()

        return result

    def _save_capability(
        self,
        conn: sqlite3.Connection,
        company_id: int,
        doc_id: int,
        chunk_id: int,
        capability: Dict[str, Any],
        tag_id: int = None
    ) -> bool:
        """保存单个能力到数据库"""
        try:
            # 生成向量嵌入
            embedding_text = f"{capability['capability_name']}: {capability.get('capability_description', '')}"
            embedding = None
            if self.embedding_service:
                try:
                    embedding = self.embedding_service.get_embedding(embedding_text)
                except Exception as e:
                    self.logger.warning(f"生成嵌入向量失败: {e}")

            # 插入数据库
            cursor = conn.execute(
                """
                INSERT INTO product_capabilities_index
                (company_id, doc_id, chunk_id, capability_name, capability_type,
                 capability_description, original_text, metrics, tag_id,
                 extraction_model, confidence_score, extracted_at,
                 capability_embedding, embedding_model)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    doc_id,
                    chunk_id,
                    capability['capability_name'],
                    capability.get('capability_type', 'function'),
                    capability.get('capability_description', ''),
                    capability.get('original_text', ''),
                    json.dumps(capability.get('metrics', {}), ensure_ascii=False),
                    tag_id,
                    self.model_name,
                    capability.get('confidence', 0.8),
                    datetime.now().isoformat(),
                    embedding,
                    self.embedding_service.model_name if self.embedding_service else None
                )
            )

            capability_id = cursor.lastrowid

            # 提取并保存关键词
            keywords = self._extract_keywords(capability)
            for kw in keywords:
                conn.execute(
                    """
                    INSERT INTO capability_keywords (capability_id, keyword, keyword_type, source)
                    VALUES (?, ?, ?, 'ai_extracted')
                    """,
                    (capability_id, kw['keyword'], kw['type'])
                )

            return True

        except Exception as e:
            self.logger.error(f"保存能力失败: {e}")
            return False

    def _extract_keywords(self, capability: Dict[str, Any]) -> List[Dict[str, str]]:
        """从能力描述中提取关键词"""
        keywords = []

        # 从能力名称提取
        name = capability.get('capability_name', '')
        if name:
            keywords.append({"keyword": name, "type": "name"})

        # 从指标中提取
        metrics = capability.get('metrics', {})
        for key in metrics.keys():
            keywords.append({"keyword": key, "type": "metric"})

        return keywords

    def extract_from_document_batch(
        self,
        doc_ids: List[int],
        company_id: int,
        tag_id: int = None
    ) -> Dict[str, Any]:
        """
        批量从多个文档提取能力

        Args:
            doc_ids: 文档ID列表
            company_id: 企业ID
            tag_id: 关联的能力标签ID

        Returns:
            批量提取结果
        """
        results = {
            "total_docs": len(doc_ids),
            "success": 0,
            "failed": 0,
            "total_capabilities": 0,
            "details": []
        }

        for doc_id in doc_ids:
            try:
                detail = self.extract_from_document(
                    doc_id=doc_id,
                    company_id=company_id,
                    tag_id=tag_id
                )
                results['success'] += 1
                results['total_capabilities'] += detail['capabilities_saved']
                results['details'].append(detail)
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    "doc_id": doc_id,
                    "error": str(e)
                })

        return results

    def get_document_capabilities(
        self,
        doc_id: int
    ) -> List[Dict[str, Any]]:
        """获取文档的所有已提取能力"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT c.*, t.tag_name
                FROM product_capabilities_index c
                LEFT JOIN product_capability_tags t ON c.tag_id = t.tag_id
                WHERE c.doc_id = ? AND c.is_active = 1
                ORDER BY c.confidence_score DESC
                """,
                (doc_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_document_capabilities(self, doc_id: int) -> int:
        """删除文档的所有能力（重新提取前调用）"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM product_capabilities_index WHERE doc_id = ?",
                (doc_id,)
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
