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
                       privacy_classification: int = 1, tags: List[str] = None,
                       metadata: Dict = None) -> int:
        """创建文档记录"""
        tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        query = """
        INSERT INTO documents
        (library_id, filename, original_filename, file_path, file_type, file_size,
         privacy_classification, tags, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            library_id, filename, original_filename, file_path, file_type, file_size,
            privacy_classification, tags_json, metadata_json
        ))

    def get_documents(self, library_id: int = None, privacy_level: int = None) -> List[Dict]:
        """获取文档列表"""
        conditions = []
        params = []

        if library_id:
            conditions.append("library_id = ?")
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