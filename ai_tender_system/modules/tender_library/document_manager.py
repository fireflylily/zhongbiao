#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书文档管理器

管理历史标书文档的上传、解析和存储。
"""

import json
import logging
import sqlite3
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class TenderDocumentManager:
    """标书文档管理器"""

    def __init__(self, db_path: str = None):
        """
        初始化管理器

        Args:
            db_path: 数据库路径
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "knowledge_base.db")
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================================
    # 标书文档 CRUD
    # =========================================================================

    def create_document(
        self,
        company_id: int,
        doc_name: str,
        file_path: str,
        file_name: str,
        file_type: str,
        file_size: int,
        project_name: str = None,
        customer_name: str = None,
        industry: str = None,
        project_type: str = None,
        bid_date: str = None,
        bid_amount: float = None,
        bid_result: str = 'unknown',
        final_score: float = None,
        technical_score: float = None,
        notes: str = None,
        uploaded_by: str = None
    ) -> int:
        """
        创建标书文档记录

        Args:
            company_id: 企业ID
            doc_name: 标书名称
            file_path: 文件存储路径
            file_name: 原始文件名
            file_type: 文件类型
            file_size: 文件大小
            project_name: 投标项目名称
            customer_name: 招标方名称
            industry: 所属行业
            project_type: 项目类型
            bid_date: 投标日期
            bid_amount: 投标金额
            bid_result: 投标结果 won/lost/unknown
            final_score: 最终得分
            technical_score: 技术分
            notes: 备注
            uploaded_by: 上传者

        Returns:
            新创建的文档ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO tender_documents
                (company_id, doc_name, project_name, customer_name, industry,
                 project_type, bid_date, bid_amount, bid_result, final_score,
                 technical_score, file_path, file_name, file_type, file_size,
                 notes, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id, doc_name, project_name, customer_name, industry,
                    project_type, bid_date, bid_amount, bid_result, final_score,
                    technical_score, file_path, file_name, file_type, file_size,
                    notes, uploaded_by
                )
            )
            conn.commit()
            doc_id = cursor.lastrowid
            self.logger.info(f"创建标书文档成功: {doc_name} (ID: {doc_id})")
            return doc_id
        finally:
            conn.close()

    def get_document(self, tender_doc_id: int) -> Optional[Dict[str, Any]]:
        """获取标书文档详情"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM tender_documents WHERE tender_doc_id = ?",
                (tender_doc_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_documents(
        self,
        company_id: int,
        bid_result: str = None,
        industry: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取企业的标书文档列表

        Args:
            company_id: 企业ID
            bid_result: 筛选投标结果
            industry: 筛选行业
            limit: 返回数量
            offset: 偏移量

        Returns:
            文档列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT tender_doc_id, doc_name, project_name, customer_name,
                       industry, project_type, bid_date, bid_result,
                       final_score, technical_score, parse_status,
                       total_chapters, created_at
                FROM tender_documents
                WHERE company_id = ?
            """
            params = [company_id]

            if bid_result:
                sql += " AND bid_result = ?"
                params.append(bid_result)

            if industry:
                sql += " AND industry = ?"
                params.append(industry)

            sql += " ORDER BY bid_date DESC, created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_document(
        self,
        tender_doc_id: int,
        **kwargs
    ) -> bool:
        """更新标书文档"""
        if not kwargs:
            return False

        conn = self._get_connection()
        try:
            # 构建更新语句
            updates = []
            params = []
            allowed_fields = [
                'doc_name', 'project_name', 'customer_name', 'industry',
                'project_type', 'bid_date', 'bid_amount', 'bid_result',
                'final_score', 'technical_score', 'commercial_score',
                'score_rank', 'parse_status', 'chunk_status', 'parse_error',
                'total_pages', 'total_chapters', 'total_words',
                'tags', 'metadata', 'notes'
            ]

            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    params.append(value)

            if not updates:
                return False

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(tender_doc_id)

            sql = f"UPDATE tender_documents SET {', '.join(updates)} WHERE tender_doc_id = ?"
            conn.execute(sql, params)
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_document(self, tender_doc_id: int) -> bool:
        """删除标书文档（同时删除关联的片段）"""
        conn = self._get_connection()
        try:
            # 外键约束会自动删除关联的 tender_excerpts
            conn.execute(
                "DELETE FROM tender_documents WHERE tender_doc_id = ?",
                (tender_doc_id,)
            )
            conn.commit()
            self.logger.info(f"删除标书文档成功: ID={tender_doc_id}")
            return True
        except Exception as e:
            self.logger.error(f"删除标书文档失败: {e}")
            return False
        finally:
            conn.close()

    # =========================================================================
    # 统计信息
    # =========================================================================

    def get_stats(self, company_id: int) -> Dict[str, Any]:
        """获取企业标书库统计"""
        conn = self._get_connection()
        try:
            # 总数统计
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN bid_result = 'won' THEN 1 ELSE 0 END) as won,
                    SUM(CASE WHEN bid_result = 'lost' THEN 1 ELSE 0 END) as lost,
                    SUM(CASE WHEN parse_status = 'completed' THEN 1 ELSE 0 END) as parsed,
                    AVG(technical_score) as avg_tech_score
                FROM tender_documents
                WHERE company_id = ?
                """,
                (company_id,)
            )
            row = cursor.fetchone()

            # 按行业统计
            cursor = conn.execute(
                """
                SELECT industry, COUNT(*) as count,
                       SUM(CASE WHEN bid_result = 'won' THEN 1 ELSE 0 END) as won
                FROM tender_documents
                WHERE company_id = ? AND industry IS NOT NULL
                GROUP BY industry
                ORDER BY count DESC
                LIMIT 10
                """,
                (company_id,)
            )
            by_industry = [dict(r) for r in cursor.fetchall()]

            # 片段统计
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_excerpts,
                    SUM(CASE WHEN is_highlighted = 1 THEN 1 ELSE 0 END) as highlighted,
                    AVG(quality_score) as avg_quality
                FROM tender_excerpts
                WHERE company_id = ?
                """,
                (company_id,)
            )
            excerpt_row = cursor.fetchone()

            return {
                "documents": {
                    "total": row['total'] or 0,
                    "won": row['won'] or 0,
                    "lost": row['lost'] or 0,
                    "parsed": row['parsed'] or 0,
                    "avg_tech_score": round(row['avg_tech_score'] or 0, 1)
                },
                "by_industry": by_industry,
                "excerpts": {
                    "total": excerpt_row['total_excerpts'] or 0,
                    "highlighted": excerpt_row['highlighted'] or 0,
                    "avg_quality": round(excerpt_row['avg_quality'] or 0, 1)
                }
            }
        finally:
            conn.close()

    def get_industries(self, company_id: int) -> List[str]:
        """获取企业标书涉及的所有行业"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT DISTINCT industry
                FROM tender_documents
                WHERE company_id = ? AND industry IS NOT NULL AND industry != ''
                ORDER BY industry
                """,
                (company_id,)
            )
            return [row['industry'] for row in cursor.fetchall()]
        finally:
            conn.close()
