#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能力搜索匹配器

提供产品能力的搜索和匹配功能：
1. 语义搜索 - 基于向量相似度
2. 关键词搜索 - 基于关键词匹配
3. 混合搜索 - 结合语义和关键词

用于招标需求匹配：判断公司产品能否满足招标需求。
"""

import json
import logging
import sqlite3
import struct
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import uuid


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
        import asyncio
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的嵌入向量（返回float列表）"""
        import asyncio
        try:
            loop = self._get_loop()
            result = loop.run_until_complete(self.service.embed_texts([text]))
            if result.vectors is not None and len(result.vectors) > 0:
                return result.vectors[0].tolist()
            return None
        except Exception as e:
            logging.getLogger(__name__).warning(f"获取嵌入向量失败: {e}")
            return None


class CapabilitySearcher:
    """能力搜索匹配器"""

    def __init__(self, db_path: str = None):
        """
        初始化搜索器

        Args:
            db_path: 数据库路径
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "knowledge_base.db")
        self.db_path = db_path
        self.embedding_service = get_embedding_service()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def search(
        self,
        query: str,
        company_id: int,
        tag_id: int = None,
        method: str = "hybrid",
        top_k: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        搜索匹配的能力

        Args:
            query: 搜索查询（招标需求描述）
            company_id: 企业ID
            tag_id: 限定能力标签（可选）
            method: 搜索方法 - semantic/keyword/hybrid
            top_k: 返回结果数量
            min_score: 最小匹配分数

        Returns:
            匹配的能力列表，按相关度排序
        """
        if method == "semantic":
            return self._semantic_search(query, company_id, tag_id, top_k, min_score)
        elif method == "keyword":
            return self._keyword_search(query, company_id, tag_id, top_k)
        else:  # hybrid
            return self._hybrid_search(query, company_id, tag_id, top_k, min_score)

    def _semantic_search(
        self,
        query: str,
        company_id: int,
        tag_id: int = None,
        top_k: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """语义搜索"""
        if not self.embedding_service:
            self.logger.warning("嵌入服务不可用，降级为关键词搜索")
            return self._keyword_search(query, company_id, tag_id, top_k)

        # 生成查询向量
        query_embedding = self.embedding_service.get_embedding(query)
        if query_embedding is None:
            return self._keyword_search(query, company_id, tag_id, top_k)

        conn = self._get_connection()
        try:
            # 获取所有能力（带向量）
            sql = """
                SELECT c.*, t.tag_name, d.original_filename as doc_name
                FROM product_capabilities_index c
                LEFT JOIN product_capability_tags t ON c.tag_id = t.tag_id
                LEFT JOIN documents d ON c.doc_id = d.doc_id
                WHERE c.company_id = ? AND c.is_active = 1
                  AND c.capability_embedding IS NOT NULL
            """
            params = [company_id]

            if tag_id:
                sql += " AND c.tag_id = ?"
                params.append(tag_id)

            cursor = conn.execute(sql, params)
            capabilities = cursor.fetchall()

            # 计算相似度
            results = []
            for cap in capabilities:
                if cap['capability_embedding']:
                    try:
                        cap_embedding = self._deserialize_embedding(cap['capability_embedding'])
                        score = self._cosine_similarity(query_embedding, cap_embedding)
                        if score >= min_score:
                            result = dict(cap)
                            result['match_score'] = score
                            result['match_method'] = 'semantic'
                            results.append(result)
                    except Exception as e:
                        continue

            # 排序
            results.sort(key=lambda x: x['match_score'], reverse=True)
            return results[:top_k]

        finally:
            conn.close()

    def _keyword_search(
        self,
        query: str,
        company_id: int,
        tag_id: int = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """关键词搜索"""
        conn = self._get_connection()
        try:
            # 分词（简单空格分词，实际可用jieba）
            keywords = query.replace('，', ' ').replace(',', ' ').split()

            # 构建搜索条件
            sql = """
                SELECT c.*, t.tag_name, d.original_filename as doc_name,
                       0 as match_score
                FROM product_capabilities_index c
                LEFT JOIN product_capability_tags t ON c.tag_id = t.tag_id
                LEFT JOIN documents d ON c.doc_id = d.doc_id
                WHERE c.company_id = ? AND c.is_active = 1
                  AND (
            """
            params = [company_id]

            conditions = []
            for kw in keywords:
                conditions.append("c.capability_name LIKE ? OR c.capability_description LIKE ?")
                params.extend([f"%{kw}%", f"%{kw}%"])

            sql += " OR ".join(conditions) + ")"

            if tag_id:
                sql += " AND c.tag_id = ?"
                params.append(tag_id)

            sql += f" LIMIT {top_k}"

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                # 计算关键词匹配得分
                text = f"{result['capability_name']} {result['capability_description']}"
                matched = sum(1 for kw in keywords if kw in text)
                result['match_score'] = matched / len(keywords) if keywords else 0
                result['match_method'] = 'keyword'
                results.append(result)

            results.sort(key=lambda x: x['match_score'], reverse=True)
            return results

        finally:
            conn.close()

    def _hybrid_search(
        self,
        query: str,
        company_id: int,
        tag_id: int = None,
        top_k: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """混合搜索（语义 + 关键词）"""
        # 分别执行两种搜索
        semantic_results = self._semantic_search(query, company_id, tag_id, top_k * 2, min_score * 0.8)
        keyword_results = self._keyword_search(query, company_id, tag_id, top_k * 2)

        # 合并结果
        seen = set()
        merged = []

        for result in semantic_results:
            cap_id = result['capability_id']
            if cap_id not in seen:
                seen.add(cap_id)
                result['match_method'] = 'hybrid'
                merged.append(result)

        for result in keyword_results:
            cap_id = result['capability_id']
            if cap_id not in seen:
                seen.add(cap_id)
                # 关键词结果分数加权
                result['match_score'] = result['match_score'] * 0.8
                result['match_method'] = 'hybrid'
                merged.append(result)
            else:
                # 已存在，提升分数
                for m in merged:
                    if m['capability_id'] == cap_id:
                        m['match_score'] = min(1.0, m['match_score'] + result['match_score'] * 0.2)
                        break

        merged.sort(key=lambda x: x['match_score'], reverse=True)
        return merged[:top_k]

    def match_requirement(
        self,
        requirement: str,
        company_id: int,
        tag_id: int = None,
        threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        匹配单个招标需求

        Args:
            requirement: 招标需求描述
            company_id: 企业ID
            tag_id: 限定能力标签
            threshold: 匹配阈值

        Returns:
            匹配结果
        """
        results = self.search(
            query=requirement,
            company_id=company_id,
            tag_id=tag_id,
            method="hybrid",
            top_k=5,
            min_score=threshold
        )

        if not results:
            return {
                "requirement": requirement,
                "status": "not_supported",
                "note": "未找到匹配的产品能力",
                "matched_capabilities": []
            }

        best_match = results[0]

        if best_match['match_score'] >= 0.8:
            status = "supported"
        elif best_match['match_score'] >= 0.6:
            status = "partial"
        else:
            status = "uncertain"

        return {
            "requirement": requirement,
            "status": status,
            "match_score": best_match['match_score'],
            "capability": best_match['capability_name'],
            "capability_description": best_match['capability_description'],
            "evidence": best_match.get('original_text', ''),
            "doc_name": best_match.get('doc_name', ''),
            "doc_id": best_match.get('doc_id'),
            "matched_capabilities": results[:3]  # 返回前3个匹配
        }

    def match_requirements_batch(
        self,
        requirements: List[str],
        company_id: int,
        tender_project_id: int = None
    ) -> Dict[str, Any]:
        """
        批量匹配招标需求

        Args:
            requirements: 需求列表
            company_id: 企业ID
            tender_project_id: 招标项目ID（用于记录历史）

        Returns:
            批量匹配结果
        """
        session_id = str(uuid.uuid4())
        results = {
            "session_id": session_id,
            "total": len(requirements),
            "supported": 0,
            "partial": 0,
            "not_supported": 0,
            "uncertain": 0,
            "details": [],
            "risk_points": []
        }

        for req in requirements:
            match = self.match_requirement(req, company_id)
            results['details'].append(match)

            status = match['status']
            results[status] = results.get(status, 0) + 1

            if status == "not_supported":
                results['risk_points'].append(f"需求「{req[:30]}...」无法满足")

            # 记录匹配历史
            if match.get('matched_capabilities'):
                self._save_match_history(
                    company_id=company_id,
                    tender_project_id=tender_project_id,
                    session_id=session_id,
                    requirement=req,
                    match=match
                )

        # 计算覆盖率
        results['coverage_rate'] = (
            (results['supported'] + results['partial'] * 0.5) / results['total']
            if results['total'] > 0 else 0
        )

        return results

    def _save_match_history(
        self,
        company_id: int,
        tender_project_id: int,
        session_id: str,
        requirement: str,
        match: Dict[str, Any]
    ):
        """保存匹配历史"""
        conn = self._get_connection()
        try:
            for i, cap in enumerate(match.get('matched_capabilities', [])[:3]):
                conn.execute(
                    """
                    INSERT INTO capability_match_history
                    (company_id, tender_project_id, session_id, requirement_text,
                     matched_capability_id, match_score, match_method, match_rank)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company_id,
                        tender_project_id,
                        session_id,
                        requirement,
                        cap['capability_id'],
                        cap['match_score'],
                        cap.get('match_method', 'hybrid'),
                        i + 1
                    )
                )
            conn.commit()
        except Exception as e:
            self.logger.error(f"保存匹配历史失败: {e}")
        finally:
            conn.close()

    def get_company_capabilities(
        self,
        company_id: int,
        tag_id: int = None,
        verified_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取企业的所有能力

        Args:
            company_id: 企业ID
            tag_id: 能力标签筛选
            verified_only: 只返回已审核的

        Returns:
            能力列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT c.*, t.tag_name, d.original_filename as doc_name
                FROM product_capabilities_index c
                LEFT JOIN product_capability_tags t ON c.tag_id = t.tag_id
                LEFT JOIN documents d ON c.doc_id = d.doc_id
                WHERE c.company_id = ? AND c.is_active = 1
            """
            params = [company_id]

            if tag_id:
                sql += " AND c.tag_id = ?"
                params.append(tag_id)

            if verified_only:
                sql += " AND c.verified = 1"

            sql += " ORDER BY c.confidence_score DESC"

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def get_capability_stats(self, company_id: int) -> Dict[str, Any]:
        """获取能力统计信息"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified,
                    AVG(confidence_score) as avg_confidence
                FROM product_capabilities_index
                WHERE company_id = ? AND is_active = 1
                """,
                (company_id,)
            )
            row = cursor.fetchone()

            # 按标签统计
            cursor = conn.execute(
                """
                SELECT t.tag_name, COUNT(*) as count
                FROM product_capabilities_index c
                JOIN product_capability_tags t ON c.tag_id = t.tag_id
                WHERE c.company_id = ? AND c.is_active = 1
                GROUP BY t.tag_id
                ORDER BY count DESC
                """,
                (company_id,)
            )
            by_tag = [dict(r) for r in cursor.fetchall()]

            return {
                "total": row['total'] or 0,
                "verified": row['verified'] or 0,
                "avg_confidence": round(row['avg_confidence'] or 0, 2),
                "by_tag": by_tag
            }

        finally:
            conn.close()

    # =========================================================================
    # 辅助方法
    # =========================================================================

    def _deserialize_embedding(self, blob: bytes) -> List[float]:
        """反序列化向量"""
        import struct
        n = len(blob) // 4
        return list(struct.unpack(f'{n}f', blob))

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        import math
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
