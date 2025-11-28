#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 common/database.py
包含对KnowledgeBaseDB类的全面单元测试
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.database import KnowledgeBaseDB, get_knowledge_base_db, get_db_connection


class TestKnowledgeBaseDB:
    """测试KnowledgeBaseDB类"""

    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'test_knowledge_base.db')
        yield db_path
        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)

    @pytest.fixture
    def db(self, temp_db_path):
        """创建测试数据库实例"""
        with patch('ai_tender_system.common.database.get_config') as mock_config:
            # Mock配置
            mock_config_obj = Mock()
            mock_config_obj.get_path.return_value = Path(os.path.dirname(temp_db_path))
            mock_config.return_value = mock_config_obj

            db = KnowledgeBaseDB(db_path=temp_db_path)
            yield db

    def test_init_database(self, db, temp_db_path):
        """测试数据库初始化"""
        assert os.path.exists(temp_db_path)

        # 检查数据库文件可以打开
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # 检查主要表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # 验证关键表存在
        assert 'companies' in tables
        assert 'products' in tables
        assert 'documents' in tables
        assert 'document_libraries' in tables

        conn.close()

    def test_get_connection(self, db):
        """测试数据库连接上下文管理器"""
        with db.get_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_execute_query_select(self, db):
        """测试SELECT查询"""
        # 创建测试公司
        company_id = db.create_company(
            company_name="测试公司",
            company_code="TEST001"
        )

        # 查询公司
        result = db.execute_query(
            "SELECT * FROM companies WHERE company_id = ?",
            (company_id,),
            fetch_one=True
        )

        assert result is not None
        assert result['company_name'] == "测试公司"
        assert result['company_code'] == "TEST001"

    def test_execute_query_insert(self, db):
        """测试INSERT查询"""
        result = db.execute_query(
            "INSERT INTO companies (company_name, company_code) VALUES (?, ?)",
            ("新公司", "NEW001")
        )

        # execute_query对INSERT返回lastrowid
        assert isinstance(result, int)
        assert result > 0

    def test_create_company(self, db):
        """测试创建公司"""
        company_id = db.create_company(
            company_name="测试公司A",
            company_code="COMP_A",
            industry_type="IT",
            description="这是一个测试公司"
        )

        assert company_id > 0

        # 验证公司已创建
        company = db.get_company_by_id(company_id)
        assert company['company_name'] == "测试公司A"
        assert company['company_code'] == "COMP_A"
        assert company['industry_type'] == "IT"

    def test_get_companies(self, db):
        """测试获取公司列表"""
        # 创建多个公司
        db.create_company("公司1", "C001")
        db.create_company("公司2", "C002")
        db.create_company("公司3", "C003")

        companies = db.get_companies()

        assert len(companies) >= 3
        company_names = [c['company_name'] for c in companies]
        assert "公司1" in company_names
        assert "公司2" in company_names

    def test_update_company(self, db):
        """测试更新公司信息"""
        # 创建公司
        company_id = db.create_company("原始公司", "ORIG001")

        # 更新公司
        update_data = {
            'company_name': '更新后公司',
            'description': '更新后的描述'
        }

        result = db.update_company(company_id, update_data)
        assert result is True

        # 验证更新
        company = db.get_company_by_id(company_id)
        assert company['company_name'] == '更新后公司'
        assert company['description'] == '更新后的描述'

    def test_create_product(self, db):
        """测试创建产品"""
        # 先创建公司
        company_id = db.create_company("测试公司", "TEST001")

        # 创建产品
        product_id = db.create_product(
            company_id=company_id,
            product_name="测试产品",
            product_code="PROD001",
            product_category="软件",
            description="测试产品描述"
        )

        assert product_id > 0

        # 验证产品
        product = db.get_product_by_id(product_id)
        assert product['product_name'] == "测试产品"
        assert product['company_id'] == company_id

    def test_get_products(self, db):
        """测试获取产品列表"""
        # 创建公司和产品
        company_id = db.create_company("测试公司", "TEST001")
        db.create_product(company_id, "产品A", "PA001")
        db.create_product(company_id, "产品B", "PB001")

        products = db.get_products(company_id)

        assert len(products) == 2
        product_names = [p['product_name'] for p in products]
        assert "产品A" in product_names
        assert "产品B" in product_names

    def test_create_document_library(self, db):
        """测试创建文档库"""
        # 创建公司和产品
        company_id = db.create_company("测试公司", "TEST001")
        product_id = db.create_product(company_id, "测试产品", "PROD001")

        # 创建文档库
        library_id = db.create_document_library(
            owner_type='product',
            owner_id=product_id,
            library_name='技术文档库',
            library_type='tech',
            privacy_level=1
        )

        assert library_id > 0

        # 验证文档库
        library = db.get_library(library_id)
        assert library['library_name'] == '技术文档库'
        assert library['owner_type'] == 'product'

    def test_create_document(self, db):
        """测试创建文档记录"""
        # 准备数据
        company_id = db.create_company("测试公司", "TEST001")
        product_id = db.create_product(company_id, "测试产品", "PROD001")
        library_id = db.create_document_library(
            'product', product_id, '文档库', 'tech'
        )

        # 创建文档
        doc_id = db.create_document(
            library_id=library_id,
            filename='test_doc.pdf',
            original_filename='测试文档.pdf',
            file_path='/path/to/test_doc.pdf',
            file_type='pdf',
            file_size=1024000,
            privacy_classification=1,
            tags=['测试', '文档'],
            metadata={'author': '测试者'}
        )

        assert doc_id > 0

        # 验证文档
        docs = db.get_documents(library_id)
        assert len(docs) == 1
        assert docs[0]['original_filename'] == '测试文档.pdf'

    def test_update_document_status(self, db):
        """测试更新文档状态"""
        # 创建文档
        company_id = db.create_company("测试公司", "TEST001")
        product_id = db.create_product(company_id, "测试产品", "PROD001")
        library_id = db.create_document_library('product', product_id, '文档库', 'tech')
        doc_id = db.create_document(
            library_id, 'test.pdf', 'test.pdf', '/path/test.pdf', 'pdf', 1000
        )

        # 更新状态
        result = db.update_document_status(
            doc_id,
            parse_status='completed',
            vector_status='completed'
        )

        assert result is True

    def test_delete_document(self, db):
        """测试删除文档"""
        # 创建文档
        company_id = db.create_company("测试公司", "TEST001")
        product_id = db.create_product(company_id, "测试产品", "PROD001")
        library_id = db.create_document_library('product', product_id, '文档库', 'tech')
        doc_id = db.create_document(
            library_id, 'test.pdf', 'test.pdf', '/path/test.pdf', 'pdf', 1000
        )

        # 删除文档
        result = db.delete_document(doc_id)
        assert result is True

        # 验证已删除
        docs = db.get_documents(library_id)
        assert len(docs) == 0

    def test_get_config(self, db):
        """测试获取配置"""
        # 设置配置
        db.set_config('test_key', 'test_value', 'string')

        # 获取配置
        value = db.get_config('test_key')
        assert value == 'test_value'

    def test_set_config_integer(self, db):
        """测试设置整数配置"""
        db.set_config('max_items', 100, 'integer')
        value = db.get_config('max_items')
        assert value == 100
        assert isinstance(value, int)

    def test_set_config_boolean(self, db):
        """测试设置布尔配置"""
        db.set_config('enabled', True, 'boolean')
        value = db.get_config('enabled')
        assert value is True
        assert isinstance(value, bool)

    def test_set_config_json(self, db):
        """测试设置JSON配置"""
        data = {'key1': 'value1', 'key2': ['a', 'b', 'c']}
        db.set_config('json_data', data, 'json')
        value = db.get_config('json_data')
        assert value == data

    def test_create_company_qualification(self, db):
        """测试保存公司资质"""
        company_id = db.create_company("测试公司", "TEST001")

        qual_id = db.save_company_qualification(
            company_id=company_id,
            qualification_key='business_license',
            qualification_name='营业执照',
            original_filename='营业执照.pdf',
            safe_filename='business_license_20250101.pdf',
            file_path='/path/to/license.pdf',
            file_size=500000,
            file_type='pdf'
        )

        assert qual_id > 0

        # 验证资质
        quals = db.get_company_qualifications(company_id)
        assert len(quals) == 1
        assert quals[0]['qualification_name'] == '营业执照'

    def test_rollback_on_error(self, db):
        """测试错误时回滚"""
        with pytest.raises(Exception):
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO companies (company_name) VALUES (?)",
                    ("测试公司",)
                )
                # 触发错误 - 插入无效数据
                conn.execute("INSERT INTO invalid_table VALUES (1)")

        # 验证事务已回滚
        companies = db.get_companies()
        company_names = [c['company_name'] for c in companies]
        assert "测试公司" not in company_names


class TestDatabaseHelpers:
    """测试数据库辅助函数"""

    def test_get_knowledge_base_db_singleton(self):
        """测试单例模式"""
        db1 = get_knowledge_base_db()
        db2 = get_knowledge_base_db()

        # 应该返回同一个实例
        assert db1 is db2

    def test_get_db_connection_context(self):
        """测试数据库连接上下文管理器"""
        with patch('ai_tender_system.common.database.get_config') as mock_config:
            mock_config_obj = Mock()
            temp_dir = tempfile.mkdtemp()
            mock_config_obj.get_path.return_value = Path(temp_dir)
            mock_config.return_value = mock_config_obj

            with get_db_connection() as conn:
                assert conn is not None
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
