#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书片段管理器

管理从标书中提取的章节/片段，用于技术方案生成时的素材检索。
"""

import json
import logging
import sqlite3
import struct
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class ExcerptManager:
    """标书片段管理器"""

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
    # 片段 CRUD
    # =========================================================================

    def create_excerpt(
        self,
        tender_doc_id: int,
        company_id: int,
        content: str,
        chapter_number: str = None,
        chapter_title: str = None,
        chapter_level: int = 1,
        parent_excerpt_id: int = None,
        category: str = None,
        subcategory: str = None,
        keywords: List[str] = None,
        scoring_points: List[str] = None,
        quality_score: int = 0,
        is_highlighted: bool = False,
        quality_notes: str = None,
        source_page_start: int = None,
        source_page_end: int = None
    ) -> int:
        """
        创建片段记录

        Args:
            tender_doc_id: 标书文档ID
            company_id: 企业ID
            content: 片段内容
            chapter_number: 章节号
            chapter_title: 章节标题
            chapter_level: 章节级别
            parent_excerpt_id: 父章节ID
            category: 分类
            subcategory: 子分类
            keywords: 关键词列表
            scoring_points: 可响应的评分点
            quality_score: 质量评分
            is_highlighted: 是否为精选
            quality_notes: 质量评估说明
            source_page_start: 原文档起始页
            source_page_end: 原文档结束页

        Returns:
            新创建的片段ID
        """
        conn = self._get_connection()
        try:
            word_count = len(content) if content else 0

            cursor = conn.execute(
                """
                INSERT INTO tender_excerpts
                (tender_doc_id, company_id, chapter_number, chapter_title,
                 chapter_level, parent_excerpt_id, content, word_count,
                 quality_score, is_highlighted, quality_notes,
                 category, subcategory, keywords, scoring_points,
                 source_page_start, source_page_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tender_doc_id, company_id, chapter_number, chapter_title,
                    chapter_level, parent_excerpt_id, content, word_count,
                    quality_score, is_highlighted, quality_notes,
                    category, subcategory,
                    json.dumps(keywords, ensure_ascii=False) if keywords else None,
                    json.dumps(scoring_points, ensure_ascii=False) if scoring_points else None,
                    source_page_start, source_page_end
                )
            )
            conn.commit()
            excerpt_id = cursor.lastrowid
            self.logger.info(f"创建片段成功: {chapter_title or excerpt_id}")
            return excerpt_id
        finally:
            conn.close()

    def get_excerpt(self, excerpt_id: int) -> Optional[Dict[str, Any]]:
        """获取片段详情"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT e.*, d.doc_name, d.project_name, d.bid_result
                FROM tender_excerpts e
                JOIN tender_documents d ON e.tender_doc_id = d.tender_doc_id
                WHERE e.excerpt_id = ?
                """,
                (excerpt_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # 解析JSON字段
                if result.get('keywords'):
                    result['keywords'] = json.loads(result['keywords'])
                if result.get('scoring_points'):
                    result['scoring_points'] = json.loads(result['scoring_points'])
                # 移除向量字段
                if 'vector_embedding' in result:
                    del result['vector_embedding']
                return result
            return None
        finally:
            conn.close()

    def list_excerpts(
        self,
        company_id: int,
        tender_doc_id: int = None,
        category: str = None,
        is_highlighted: bool = None,
        min_quality: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取片段列表

        Args:
            company_id: 企业ID
            tender_doc_id: 筛选特定标书
            category: 筛选分类
            is_highlighted: 筛选精选
            min_quality: 最低质量分
            limit: 返回数量
            offset: 偏移量

        Returns:
            片段列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT e.excerpt_id, e.tender_doc_id, e.chapter_number,
                       e.chapter_title, e.chapter_level, e.category,
                       e.subcategory, e.word_count, e.quality_score,
                       e.is_highlighted, e.usage_count,
                       e.content,
                       substr(e.content, 1, 200) as content_preview,
                       d.doc_name, d.bid_result
                FROM tender_excerpts e
                JOIN tender_documents d ON e.tender_doc_id = d.tender_doc_id
                WHERE e.company_id = ?
            """
            params = [company_id]

            if tender_doc_id:
                sql += " AND e.tender_doc_id = ?"
                params.append(tender_doc_id)

            if category:
                sql += " AND e.category = ?"
                params.append(category)

            if is_highlighted is not None:
                sql += " AND e.is_highlighted = ?"
                params.append(1 if is_highlighted else 0)

            if min_quality is not None:
                sql += " AND e.quality_score >= ?"
                params.append(min_quality)

            sql += " ORDER BY e.quality_score DESC, e.usage_count DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_excerpt(
        self,
        excerpt_id: int,
        **kwargs
    ) -> bool:
        """更新片段"""
        if not kwargs:
            return False

        conn = self._get_connection()
        try:
            updates = []
            params = []
            allowed_fields = [
                'chapter_number', 'chapter_title', 'chapter_level',
                'content', 'content_html', 'quality_score', 'is_highlighted',
                'quality_notes', 'category', 'subcategory', 'keywords',
                'scoring_points', 'capability_tag_ids'
            ]

            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    # JSON字段特殊处理
                    if field in ['keywords', 'scoring_points', 'capability_tag_ids'] and isinstance(value, list):
                        params.append(json.dumps(value, ensure_ascii=False))
                    else:
                        params.append(value)

            if not updates:
                return False

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(excerpt_id)

            sql = f"UPDATE tender_excerpts SET {', '.join(updates)} WHERE excerpt_id = ?"
            conn.execute(sql, params)
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_excerpt(self, excerpt_id: int) -> bool:
        """删除片段"""
        conn = self._get_connection()
        try:
            conn.execute(
                "DELETE FROM tender_excerpts WHERE excerpt_id = ?",
                (excerpt_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"删除片段失败: {e}")
            return False
        finally:
            conn.close()

    # =========================================================================
    # 片段搜索
    # =========================================================================

    def search_by_category(
        self,
        company_id: int,
        category: str,
        subcategory: str = None,
        won_only: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        按分类搜索片段

        Args:
            company_id: 企业ID
            category: 分类
            subcategory: 子分类
            won_only: 只返回中标标书的片段
            limit: 返回数量

        Returns:
            片段列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT e.*, d.doc_name, d.bid_result, d.technical_score
                FROM tender_excerpts e
                JOIN tender_documents d ON e.tender_doc_id = d.tender_doc_id
                WHERE e.company_id = ? AND e.category = ?
            """
            params = [company_id, category]

            if subcategory:
                sql += " AND e.subcategory = ?"
                params.append(subcategory)

            if won_only:
                sql += " AND d.bid_result = 'won'"

            sql += " ORDER BY e.quality_score DESC, d.technical_score DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if 'vector_embedding' in result:
                    del result['vector_embedding']
                if result.get('keywords'):
                    result['keywords'] = json.loads(result['keywords'])
                if result.get('scoring_points'):
                    result['scoring_points'] = json.loads(result['scoring_points'])
                results.append(result)
            return results
        finally:
            conn.close()

    def search_by_scoring_point(
        self,
        company_id: int,
        scoring_point: str,
        won_only: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        按评分点搜索片段

        Args:
            company_id: 企业ID
            scoring_point: 评分点关键词
            won_only: 只返回中标标书的片段
            limit: 返回数量

        Returns:
            片段列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT e.*, d.doc_name, d.bid_result, d.technical_score
                FROM tender_excerpts e
                JOIN tender_documents d ON e.tender_doc_id = d.tender_doc_id
                WHERE e.company_id = ?
                  AND e.scoring_points LIKE ?
            """
            params = [company_id, f'%{scoring_point}%']

            if won_only:
                sql += " AND d.bid_result = 'won'"

            sql += " ORDER BY e.quality_score DESC, d.technical_score DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if 'vector_embedding' in result:
                    del result['vector_embedding']
                if result.get('keywords'):
                    result['keywords'] = json.loads(result['keywords'])
                if result.get('scoring_points'):
                    result['scoring_points'] = json.loads(result['scoring_points'])
                results.append(result)
            return results
        finally:
            conn.close()

    def search_by_keyword(
        self,
        company_id: int,
        keyword: str,
        won_only: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        按关键词搜索片段

        Args:
            company_id: 企业ID
            keyword: 搜索关键词
            won_only: 只返回中标标书的片段
            limit: 返回数量

        Returns:
            片段列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT e.*, d.doc_name, d.bid_result, d.technical_score
                FROM tender_excerpts e
                JOIN tender_documents d ON e.tender_doc_id = d.tender_doc_id
                WHERE e.company_id = ?
                  AND (e.chapter_title LIKE ? OR e.content LIKE ? OR e.keywords LIKE ?)
            """
            like_pattern = f'%{keyword}%'
            params = [company_id, like_pattern, like_pattern, like_pattern]

            if won_only:
                sql += " AND d.bid_result = 'won'"

            sql += " ORDER BY e.quality_score DESC, d.technical_score DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if 'vector_embedding' in result:
                    del result['vector_embedding']
                if result.get('keywords'):
                    result['keywords'] = json.loads(result['keywords'])
                if result.get('scoring_points'):
                    result['scoring_points'] = json.loads(result['scoring_points'])
                results.append(result)
            return results
        finally:
            conn.close()

    # =========================================================================
    # 使用统计
    # =========================================================================

    def increment_usage(self, excerpt_id: int) -> bool:
        """增加片段使用次数"""
        conn = self._get_connection()
        try:
            conn.execute(
                """
                UPDATE tender_excerpts
                SET usage_count = usage_count + 1, last_used_at = CURRENT_TIMESTAMP
                WHERE excerpt_id = ?
                """,
                (excerpt_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"更新使用次数失败: {e}")
            return False
        finally:
            conn.close()

    def get_most_used(
        self,
        company_id: int,
        category: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取使用最多的片段"""
        conn = self._get_connection()
        try:
            sql = """
                SELECT e.excerpt_id, e.chapter_title, e.category,
                       e.usage_count, e.quality_score, d.doc_name
                FROM tender_excerpts e
                JOIN tender_documents d ON e.tender_doc_id = d.tender_doc_id
                WHERE e.company_id = ? AND e.usage_count > 0
            """
            params = [company_id]

            if category:
                sql += " AND e.category = ?"
                params.append(category)

            sql += " ORDER BY e.usage_count DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # =========================================================================
    # 分类管理
    # =========================================================================

    def get_categories(self, company_id: int = None) -> List[Dict[str, Any]]:
        """获取所有分类"""
        conn = self._get_connection()
        try:
            sql = """
                SELECT category_id, category_code, category_name,
                       parent_category_id, description, category_order
                FROM excerpt_categories
                WHERE is_active = 1
            """
            params = []

            if company_id:
                sql += " AND (company_id IS NULL OR company_id = ?)"
                params.append(company_id)
            else:
                sql += " AND company_id IS NULL"

            sql += " ORDER BY category_order, category_id"

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_category_stats(self, company_id: int) -> List[Dict[str, Any]]:
        """获取分类统计"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT category, COUNT(*) as count,
                       AVG(quality_score) as avg_quality,
                       SUM(usage_count) as total_usage
                FROM tender_excerpts
                WHERE company_id = ? AND category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
                """,
                (company_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
