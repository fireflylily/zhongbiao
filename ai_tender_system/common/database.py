#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库数据库管理模块
功能：数据库连接、表创建、数据操作
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager

from .logger import get_module_logger
from .config import get_config

logger = get_module_logger("database")


class KnowledgeBaseDB:
    """知识库数据库管理类"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        config = get_config()
        self.db_path = db_path or str(config.get_path('data') / 'knowledge_base.db')

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 初始化数据库
        self._init_database()

        logger.info(f"知识库数据库初始化完成: {self.db_path}")

    def _init_database(self):
        """初始化数据库表结构"""
        schema_file = Path(__file__).parent.parent / 'database' / 'knowledge_base_schema.sql'

        if not schema_file.exists():
            logger.error(f"数据库架构文件不存在: {schema_file}")
            return

        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # Remove explicit COMMIT statements to avoid transaction conflicts
            schema_sql = schema_sql.replace('COMMIT;', '')

            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()

            logger.info("数据库表结构初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 支持字典式访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False) -> Any:
        """
        执行查询语句

        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_one: 是否只返回一条记录

        Returns:
            查询结果
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)

            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
                return cursor.lastrowid
            else:
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                else:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]

    # =========================
    # 公司管理相关方法
    # =========================

    def create_company(self, company_name: str, company_code: str = None,
                      industry_type: str = None, description: str = None) -> int:
        """创建公司记录"""
        query = """
        INSERT INTO companies (company_name, company_code, industry_type, description)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (company_name, company_code, industry_type, description))

    def get_companies(self) -> List[Dict]:
        """获取所有公司列表"""
        query = "SELECT * FROM companies WHERE 1=1 ORDER BY company_name"
        return self.execute_query(query)

    def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """根据ID获取公司信息"""
        query = "SELECT * FROM companies WHERE company_id = ?"
        return self.execute_query(query, (company_id,), fetch_one=True)

    def update_company(self, company_id: int, update_data: Dict) -> bool:
        """更新公司信息"""
        if not update_data:
            return False

        # DEBUG: 记录数据库层接收到的数据
        logger.info(f"[DEBUG DATABASE] 更新公司 {company_id} - 接收到的数据: {update_data}")
        if 'registered_capital' in update_data:
            logger.info(f"[DEBUG DATABASE] registered_capital 字段值: {update_data['registered_capital']!r}")

        # 构建更新语句
        set_clauses = []
        values = []

        for field, value in update_data.items():
            set_clauses.append(f"{field} = ?")
            values.append(value)

        values.append(company_id)  # WHERE条件的参数

        query = f"""
        UPDATE companies
        SET {', '.join(set_clauses)}
        WHERE company_id = ?
        """

        # DEBUG: 记录SQL语句和参数
        logger.info(f"[DEBUG DATABASE] 执行SQL: {query}")
        logger.info(f"[DEBUG DATABASE] SQL参数: {values}")

        try:
            self.execute_query(query, tuple(values))
            logger.info(f"[DEBUG DATABASE] SQL执行成功")
            return True
        except Exception as e:
            logger.error(f"[DEBUG DATABASE] SQL执行失败: {e}")
            logger.error(f"更新公司信息失败: {e}")
            return False

    # =========================
    # 企业信息库相关方法
    # =========================

    def create_company_profile(self, company_id: int, profile_type: str,
                              profile_name: str, description: str = None,
                              privacy_level: int = 1) -> int:
        """创建企业信息库记录"""
        query = """
        INSERT INTO company_profiles (company_id, profile_type, profile_name, description, privacy_level)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (company_id, profile_type, profile_name, description, privacy_level))

    def get_company_profiles(self, company_id: int) -> List[Dict]:
        """获取公司的企业信息库列表"""
        query = """
        SELECT * FROM company_profiles
        WHERE company_id = ? AND is_active = TRUE
        ORDER BY privacy_level, profile_type
        """
        return self.execute_query(query, (company_id,))

    # =========================
    # 产品管理相关方法
    # =========================

    def create_product(self, company_id: int, product_name: str,
                      product_code: str = None, product_category: str = None,
                      description: str = None) -> int:
        """创建产品记录"""
        query = """
        INSERT INTO products (company_id, product_name, product_code, product_category, description)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (company_id, product_name, product_code, product_category, description))

    def get_products(self, company_id: int) -> List[Dict]:
        """获取公司的产品列表"""
        query = """
        SELECT * FROM products
        WHERE company_id = ? AND is_active = TRUE
        ORDER BY product_category, product_name
        """
        return self.execute_query(query, (company_id,))

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """根据ID获取产品信息"""
        query = "SELECT * FROM products WHERE product_id = ?"
        return self.execute_query(query, (product_id,), fetch_one=True)

    # =========================
    # 文档库管理相关方法
    # =========================

    def create_document_library(self, owner_type: str, owner_id: int,
                               library_name: str, library_type: str,
                               privacy_level: int = 1, is_shared: bool = False,
                               share_scope: str = None, share_products: List[int] = None) -> int:
        """创建文档库记录"""
        share_products_json = json.dumps(share_products) if share_products else None

        query = """
        INSERT INTO document_libraries
        (owner_type, owner_id, library_name, library_type, privacy_level,
         is_shared, share_scope, share_products)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            owner_type, owner_id, library_name, library_type,
            privacy_level, is_shared, share_scope, share_products_json
        ))

    def get_document_libraries(self, owner_type: str, owner_id: int) -> List[Dict]:
        """获取指定所有者的文档库列表"""
        query = """
        SELECT * FROM document_libraries
        WHERE owner_type = ? AND owner_id = ?
        ORDER BY library_type, library_name
        """
        return self.execute_query(query, (owner_type, owner_id))

    # =========================
    # 文档管理相关方法
    # =========================

    def create_document(self, library_id: int, filename: str, original_filename: str,
                       file_path: str, file_type: str, file_size: int,
                       privacy_classification: int = 1, document_category: str = 'tech',
                       tags: List[str] = None, metadata: Dict = None) -> int:
        """创建文档记录"""
        tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        query = """
        INSERT INTO documents
        (library_id, filename, original_filename, file_path, file_type, file_size,
         privacy_classification, document_category, tags, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            library_id, filename, original_filename, file_path, file_type, file_size,
            privacy_classification, document_category, tags_json, metadata_json
        ))

    def get_documents(self, library_id: int = None, privacy_level: int = None) -> List[Dict]:
        """获取文档列表"""
        conditions = []
        params = []

        if library_id:
            conditions.append("d.library_id = ?")
            params.append(library_id)

        if privacy_level:
            conditions.append("privacy_classification <= ?")
            params.append(privacy_level)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT d.*, dl.library_name, dl.library_type
        FROM documents d
        JOIN document_libraries dl ON d.library_id = dl.library_id
        WHERE {where_clause}
        ORDER BY d.upload_time DESC
        """
        return self.execute_query(query, tuple(params))

    def update_document_status(self, doc_id: int, parse_status: str = None,
                              vector_status: str = None) -> bool:
        """更新文档处理状态"""
        updates = []
        params = []

        if parse_status:
            updates.append("parse_status = ?")
            params.append(parse_status)
            if parse_status == 'completed':
                updates.append("parsed_at = ?")
                params.append(datetime.now().isoformat())

        if vector_status:
            updates.append("vector_status = ?")
            params.append(vector_status)
            if vector_status == 'completed':
                updates.append("vectorized_at = ?")
                params.append(datetime.now().isoformat())

        if not updates:
            return False

        params.append(doc_id)

        query = f"""
        UPDATE documents
        SET {', '.join(updates)}
        WHERE doc_id = ?
        """
        result = self.execute_query(query, tuple(params))
        return result is not None

    def delete_document(self, doc_id: int) -> bool:
        """删除文档记录"""
        try:
            # 先删除相关的文档分块
            delete_chunks_query = "DELETE FROM document_chunks WHERE doc_id = ?"
            self.execute_query(delete_chunks_query, (doc_id,))

            # 删除文档记录
            delete_doc_query = "DELETE FROM documents WHERE doc_id = ?"
            result = self.execute_query(delete_doc_query, (doc_id,))
            return result is not None

        except Exception as e:
            print(f"删除文档失败: {e}")
            return False

    # =========================
    # 文档分块相关方法
    # =========================

    def create_document_chunk(self, doc_id: int, chunk_index: int, content: str,
                             content_type: str = 'text', page_number: int = None,
                             position_info: Dict = None, metadata: Dict = None) -> int:
        """创建文档分块记录"""
        position_json = json.dumps(position_info, ensure_ascii=False) if position_info else None
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        query = """
        INSERT INTO document_chunks
        (doc_id, chunk_index, content, content_type, page_number, position_info, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            doc_id, chunk_index, content, content_type, page_number, position_json, metadata_json
        ))

    def get_document_chunks(self, doc_id: int) -> List[Dict]:
        """获取文档的分块列表"""
        query = """
        SELECT * FROM document_chunks
        WHERE doc_id = ?
        ORDER BY chunk_index
        """
        return self.execute_query(query, (doc_id,))

    # =========================
    # 审计日志相关方法
    # =========================

    def create_audit_log(self, user_id: str, user_role: str, action_type: str,
                        resource_type: str, resource_id: int, privacy_level: int = None,
                        access_granted: bool = True, access_reason: str = None,
                        ip_address: str = None, user_agent: str = None,
                        session_id: str = None) -> int:
        """创建访问审计日志"""
        query = """
        INSERT INTO access_audit_logs
        (user_id, user_role, action_type, resource_type, resource_id, privacy_level,
         access_granted, access_reason, ip_address, user_agent, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            user_id, user_role, action_type, resource_type, resource_id, privacy_level,
            access_granted, access_reason, ip_address, user_agent, session_id
        ))

    # =========================
    # 统计和分析方法
    # =========================

    def get_knowledge_base_stats(self, company_id: int) -> Dict:
        """获取知识库统计信息"""
        stats = {}

        # 总文档数
        query = """
        SELECT COUNT(*) as total_docs
        FROM documents d
        JOIN document_libraries dl ON d.library_id = dl.library_id
        JOIN products p ON dl.owner_id = p.product_id AND dl.owner_type = 'product'
        WHERE p.company_id = ?
        """
        result = self.execute_query(query, (company_id,), fetch_one=True)
        stats['total_documents'] = result['total_docs'] if result else 0

        # 按类型统计
        query = """
        SELECT dl.library_type, COUNT(*) as count
        FROM documents d
        JOIN document_libraries dl ON d.library_id = dl.library_id
        JOIN products p ON dl.owner_id = p.product_id AND dl.owner_type = 'product'
        WHERE p.company_id = ?
        GROUP BY dl.library_type
        """
        type_stats = self.execute_query(query, (company_id,))
        stats['by_type'] = {item['library_type']: item['count'] for item in type_stats}

        # 按产品统计
        query = """
        SELECT p.product_name, COUNT(*) as count
        FROM documents d
        JOIN document_libraries dl ON d.library_id = dl.library_id
        JOIN products p ON dl.owner_id = p.product_id AND dl.owner_type = 'product'
        WHERE p.company_id = ?
        GROUP BY p.product_id, p.product_name
        """
        product_stats = self.execute_query(query, (company_id,))
        stats['by_product'] = {item['product_name']: item['count'] for item in product_stats}

        return stats

    # =========================
    # 向量搜索相关方法
    # =========================

    def create_vector_model(self, model_name: str, model_type: str, dimension: int,
                           model_path: str = None, description: str = None,
                           is_active: bool = False) -> int:
        """创建向量模型记录"""
        query = """
        INSERT INTO vector_models (model_name, model_type, dimension, model_path, description, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (model_name, model_type, dimension, model_path, description, is_active))

    def get_vector_models(self, active_only: bool = False) -> List[Dict]:
        """获取向量模型列表"""
        query = "SELECT * FROM vector_models"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY is_active DESC, model_name"
        return self.execute_query(query)

    def get_active_vector_model(self) -> Optional[Dict]:
        """获取当前激活的向量模型"""
        query = "SELECT * FROM vector_models WHERE is_active = TRUE LIMIT 1"
        return self.execute_query(query, fetch_one=True)

    def set_active_vector_model(self, model_id: int) -> bool:
        """设置激活的向量模型"""
        try:
            # 先将所有模型设为非激活
            self.execute_query("UPDATE vector_models SET is_active = FALSE")
            # 激活指定模型
            result = self.execute_query("UPDATE vector_models SET is_active = TRUE WHERE model_id = ?", (model_id,))
            return result is not None
        except Exception as e:
            logger.error(f"设置激活模型失败: {e}")
            return False

    def create_document_vector(self, chunk_id: int, model_id: int, vector_data: bytes, vector_norm: float = None) -> int:
        """创建文档向量记录"""
        query = """
        INSERT OR REPLACE INTO document_vectors (chunk_id, model_id, vector_data, vector_norm)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (chunk_id, model_id, vector_data, vector_norm))

    def get_document_vector(self, chunk_id: int, model_id: int = None) -> Optional[Dict]:
        """获取文档分块的向量"""
        if model_id:
            query = "SELECT * FROM document_vectors WHERE chunk_id = ? AND model_id = ?"
            params = (chunk_id, model_id)
        else:
            query = "SELECT * FROM document_vectors WHERE chunk_id = ?"
            params = (chunk_id,)
        return self.execute_query(query, params, fetch_one=True)

    def create_search_history(self, user_id: int, query_text: str, query_vector: bytes = None,
                             model_id: int = None, search_type: str = 'semantic',
                             filter_conditions: Dict = None, result_count: int = 0,
                             top_k: int = 10, threshold: float = 0.0, search_time: float = None) -> int:
        """创建搜索历史记录"""
        filter_json = json.dumps(filter_conditions, ensure_ascii=False) if filter_conditions else None

        query = """
        INSERT INTO search_history
        (user_id, query_text, query_vector, model_id, search_type, filter_conditions,
         result_count, top_k, threshold, search_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            user_id, query_text, query_vector, model_id, search_type, filter_json,
            result_count, top_k, threshold, search_time
        ))

    def create_search_results(self, search_id: int, chunk_id: int, doc_id: int,
                             similarity_score: float, rank_position: int,
                             result_snippet: str = None, highlight_info: Dict = None) -> int:
        """创建搜索结果记录"""
        highlight_json = json.dumps(highlight_info, ensure_ascii=False) if highlight_info else None

        query = """
        INSERT INTO search_results
        (search_id, chunk_id, doc_id, similarity_score, rank_position, result_snippet, highlight_info)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            search_id, chunk_id, doc_id, similarity_score, rank_position, result_snippet, highlight_json
        ))

    def create_vectorization_task(self, doc_id: int, model_id: int, task_type: str = 'new',
                                 priority: int = 5) -> int:
        """创建向量化任务"""
        query = """
        INSERT INTO vectorization_tasks (doc_id, model_id, task_type, priority, status)
        VALUES (?, ?, ?, ?, 'pending')
        """
        return self.execute_query(query, (doc_id, model_id, task_type, priority))

    def update_vectorization_task(self, task_id: int, status: str = None, progress: float = None,
                                 chunks_total: int = None, chunks_processed: int = None,
                                 error_message: str = None) -> bool:
        """更新向量化任务状态"""
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)
            if status == 'processing' and not hasattr(self, '_task_started'):
                updates.append("started_at = ?")
                params.append(datetime.now().isoformat())
            elif status in ['completed', 'failed', 'cancelled']:
                updates.append("completed_at = ?")
                params.append(datetime.now().isoformat())

        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)

        if chunks_total is not None:
            updates.append("chunks_total = ?")
            params.append(chunks_total)

        if chunks_processed is not None:
            updates.append("chunks_processed = ?")
            params.append(chunks_processed)

        if error_message:
            updates.append("error_message = ?")
            params.append(error_message)

        if not updates:
            return False

        params.append(task_id)
        query = f"UPDATE vectorization_tasks SET {', '.join(updates)} WHERE task_id = ?"
        result = self.execute_query(query, tuple(params))
        return result is not None

    def get_pending_vectorization_tasks(self, limit: int = 10) -> List[Dict]:
        """获取待处理的向量化任务"""
        query = """
        SELECT vt.*, d.filename, d.file_path, vm.model_name, vm.dimension
        FROM vectorization_tasks vt
        JOIN documents d ON vt.doc_id = d.doc_id
        JOIN vector_models vm ON vt.model_id = vm.model_id
        WHERE vt.status = 'pending'
        ORDER BY vt.priority ASC, vt.created_at ASC
        LIMIT ?
        """
        return self.execute_query(query, (limit,))

    def create_document_tag(self, tag_name: str, tag_category: str = None,
                           tag_color: str = '#007bff', description: str = None) -> int:
        """创建文档标签"""
        query = """
        INSERT OR IGNORE INTO document_tags (tag_name, tag_category, tag_color, description)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (tag_name, tag_category, tag_color, description))

    def get_document_tags(self, category: str = None) -> List[Dict]:
        """获取文档标签列表"""
        if category:
            query = "SELECT * FROM document_tags WHERE tag_category = ? ORDER BY tag_name"
            params = (category,)
        else:
            query = "SELECT * FROM document_tags ORDER BY tag_category, tag_name"
            params = ()
        return self.execute_query(query, params)

    def add_document_tag(self, doc_id: int, tag_id: int, confidence: float = 1.0,
                        is_auto_tagged: bool = False, tagged_by: int = None) -> int:
        """为文档添加标签"""
        query = """
        INSERT OR IGNORE INTO document_tag_relations
        (doc_id, tag_id, confidence, is_auto_tagged, tagged_by)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (doc_id, tag_id, confidence, is_auto_tagged, tagged_by))

    def remove_document_tag(self, doc_id: int, tag_id: int) -> bool:
        """移除文档标签"""
        query = "DELETE FROM document_tag_relations WHERE doc_id = ? AND tag_id = ?"
        result = self.execute_query(query, (doc_id, tag_id))
        return result is not None

    def get_document_tags_by_doc(self, doc_id: int) -> List[Dict]:
        """获取文档的所有标签"""
        query = """
        SELECT dt.*, dtr.confidence, dtr.is_auto_tagged, dtr.created_at as tagged_at
        FROM document_tags dt
        JOIN document_tag_relations dtr ON dt.tag_id = dtr.tag_id
        WHERE dtr.doc_id = ?
        ORDER BY dt.tag_category, dt.tag_name
        """
        return self.execute_query(query, (doc_id,))

    def record_system_metric(self, metric_name: str, metric_value: float,
                            metric_unit: str = None, component: str = None) -> int:
        """记录系统性能指标"""
        query = """
        INSERT INTO system_metrics (metric_name, metric_value, metric_unit, component)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (metric_name, metric_value, metric_unit, component))

    def get_system_metrics(self, component: str = None, limit: int = 100) -> List[Dict]:
        """获取系统性能指标"""
        if component:
            query = """
            SELECT * FROM system_metrics
            WHERE component = ?
            ORDER BY recorded_at DESC
            LIMIT ?
            """
            params = (component, limit)
        else:
            query = "SELECT * FROM system_metrics ORDER BY recorded_at DESC LIMIT ?"
            params = (limit,)
        return self.execute_query(query, params)

    def get_search_analytics(self, days: int = 30) -> Dict:
        """获取搜索分析数据"""
        stats = {}

        # 搜索次数统计
        query = """
        SELECT COUNT(*) as total_searches,
               AVG(search_time) as avg_search_time,
               AVG(result_count) as avg_result_count
        FROM search_history
        WHERE created_at >= datetime('now', '-{} days')
        """.format(days)
        result = self.execute_query(query, fetch_one=True)
        if result:
            stats.update(result)

        # 热门查询
        query = """
        SELECT query_text, COUNT(*) as count
        FROM search_history
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY query_text
        ORDER BY count DESC
        LIMIT 10
        """.format(days)
        stats['popular_queries'] = self.execute_query(query)

        # 搜索类型分布
        query = """
        SELECT search_type, COUNT(*) as count
        FROM search_history
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY search_type
        """.format(days)
        stats['search_types'] = self.execute_query(query)

        return stats

    def get_vectorization_stats(self) -> Dict:
        """获取向量化统计信息"""
        stats = {}

        # 任务状态统计
        query = """
        SELECT status, COUNT(*) as count
        FROM vectorization_tasks
        GROUP BY status
        """
        status_stats = self.execute_query(query)
        stats['task_status'] = {item['status']: item['count'] for item in status_stats}

        # 总体统计
        query = """
        SELECT
            COUNT(*) as total_tasks,
            AVG(CASE WHEN status = 'completed' AND started_at IS NOT NULL AND completed_at IS NOT NULL
                THEN (julianday(completed_at) - julianday(started_at)) * 86400 END) as avg_processing_time,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks
        FROM vectorization_tasks
        """
        result = self.execute_query(query, fetch_one=True)
        if result:
            stats.update(result)

        return stats

    # =========================
    # 配置管理方法
    # =========================

    def get_config(self, config_key: str) -> Any:
        """获取系统配置"""
        query = "SELECT config_value, config_type FROM knowledge_base_configs WHERE config_key = ?"
        result = self.execute_query(query, (config_key,), fetch_one=True)

        if not result:
            return None

        value = result['config_value']
        config_type = result['config_type']

        # 根据类型转换值
        if config_type == 'json':
            return json.loads(value)
        elif config_type == 'integer':
            return int(value)
        elif config_type == 'boolean':
            return value.lower() in ('true', '1', 'yes')
        else:
            return value

    def set_config(self, config_key: str, config_value: Any, config_type: str = 'string') -> bool:
        """设置系统配置"""
        # 转换值为字符串
        if config_type == 'json':
            value_str = json.dumps(config_value, ensure_ascii=False)
        else:
            value_str = str(config_value)

        query = """
        INSERT OR REPLACE INTO knowledge_base_configs
        (config_key, config_value, config_type, updated_at)
        VALUES (?, ?, ?, ?)
        """
        result = self.execute_query(query, (config_key, value_str, config_type, datetime.now().isoformat()))
        return result is not None

    # =========================
    # 公司资质文件管理方法
    # =========================

    def save_company_qualification(self, company_id: int, qualification_key: str,
                                  qualification_name: str, original_filename: str,
                                  safe_filename: str, file_path: str,
                                  file_size: int, file_type: str = None,
                                  custom_name: str = None, issue_date: str = None,
                                  expire_date: str = None, upload_by: str = None) -> int:
        """保存或更新公司资质文件信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 检查是否已存在
                cursor.execute("""
                    SELECT qualification_id FROM company_qualifications
                    WHERE company_id = ? AND qualification_key = ?
                """, (company_id, qualification_key))

                existing = cursor.fetchone()

                if existing:
                    # 更新现有记录
                    qualification_id = existing['qualification_id']
                    cursor.execute("""
                        UPDATE company_qualifications
                        SET qualification_name = ?, custom_name = ?,
                            original_filename = ?, safe_filename = ?,
                            file_path = ?, file_size = ?, file_type = ?,
                            issue_date = ?, expire_date = ?,
                            upload_by = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE qualification_id = ?
                    """, (qualification_name, custom_name,
                          original_filename, safe_filename,
                          file_path, file_size, file_type,
                          issue_date, expire_date, upload_by,
                          qualification_id))
                else:
                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO company_qualifications (
                            company_id, qualification_key, qualification_name,
                            custom_name, original_filename, safe_filename,
                            file_path, file_size, file_type,
                            issue_date, expire_date, upload_by
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (company_id, qualification_key, qualification_name,
                          custom_name, original_filename, safe_filename,
                          file_path, file_size, file_type,
                          issue_date, expire_date, upload_by))
                    qualification_id = cursor.lastrowid

                conn.commit()
                return qualification_id

        except Exception as e:
            logger.error(f"保存资质文件失败: {e}")
            return 0

    def get_company_qualifications(self, company_id: int) -> List[Dict]:
        """获取公司的所有资质文件"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT q.*, qt.type_name, qt.category
                    FROM company_qualifications q
                    LEFT JOIN qualification_types qt ON q.qualification_key = qt.type_key
                    WHERE q.company_id = ?
                    ORDER BY qt.sort_order, q.upload_time DESC
                """, (company_id,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"获取公司资质文件失败: {e}")
            return []

    def get_qualification_by_id(self, qualification_id: int) -> Optional[Dict]:
        """根据ID获取资质文件信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM company_qualifications
                    WHERE qualification_id = ?
                """, (qualification_id,))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"获取资质文件失败: {e}")
            return None

    def get_qualification_by_key(self, company_id: int, qualification_key: str) -> Optional[Dict]:
        """根据公司ID和资质key获取资质文件信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM company_qualifications
                    WHERE company_id = ? AND qualification_key = ?
                """, (company_id, qualification_key))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"获取资质文件失败: {e}")
            return None

    def delete_qualification(self, qualification_id: int) -> bool:
        """删除资质文件记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM company_qualifications
                    WHERE qualification_id = ?
                """, (qualification_id,))

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"删除资质文件失败: {e}")
            return False


# 全局数据库实例
_db_instance = None

def get_knowledge_base_db() -> KnowledgeBaseDB:
    """获取知识库数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = KnowledgeBaseDB()
    return _db_instance


if __name__ == "__main__":
    # 测试数据库功能
    db = get_knowledge_base_db()

    # 测试获取公司列表
    companies = db.get_companies()
    print(f"公司数量: {len(companies)}")

    if companies:
        company_id = companies[0]['company_id']
        print(f"测试公司: {companies[0]['company_name']}")

        # 测试获取产品列表
        products = db.get_products(company_id)
        print(f"产品数量: {len(products)}")

        # 测试获取统计信息
        stats = db.get_knowledge_base_stats(company_id)
        print(f"知识库统计: {stats}")