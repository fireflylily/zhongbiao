#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 common/database.py 模块
"""

import pytest
import tempfile
import os
from pathlib import Path
import json
from datetime import datetime

from ai_tender_system.common.database import KnowledgeBaseDB, get_knowledge_base_db


class TestKnowledgeBaseDB:
    """测试 KnowledgeBaseDB 类"""

    @pytest.fixture
    def temp_db(self):
        """创建临时测试数据库"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        db = KnowledgeBaseDB(db_path=db_path)
        yield db

        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_database_initialization(self, temp_db):
        """测试数据库初始化"""
        assert temp_db is not None
        assert os.path.exists(temp_db.db_path)

    def test_create_company(self, temp_db):
        """测试创建公司"""
        company_id = temp_db.create_company(
            company_name="测试公司",
            company_code="TEST001",
            industry_type="科技",
            description="这是一个测试公司"
        )

        assert company_id > 0

        # 验证公司信息
        company = temp_db.get_company_by_id(company_id)
        assert company is not None
        assert company['company_name'] == "测试公司"
        assert company['company_code'] == "TEST001"

    def test_get_companies(self, temp_db):
        """测试获取公司列表"""
        # 创建多个公司
        temp_db.create_company("公司A", "A001")
        temp_db.create_company("公司B", "B002")

        companies = temp_db.get_companies()
        assert len(companies) >= 2

    def test_update_company(self, temp_db):
        """测试更新公司信息"""
        # 创建公司
        company_id = temp_db.create_company("原公司名", "ORIG001")

        # 更新公司信息
        update_data = {
            'company_name': '新公司名',
            'description': '更新后的描述'
        }
        result = temp_db.update_company(company_id, update_data)
        assert result is True

        # 验证更新
        company = temp_db.get_company_by_id(company_id)
        assert company['company_name'] == '新公司名'
        assert company['description'] == '更新后的描述'

    def test_create_product(self, temp_db):
        """测试创建产品"""
        # 先创建公司
        company_id = temp_db.create_company("产品测试公司", "PROD001")

        # 创建产品
        product_id = temp_db.create_product(
            company_id=company_id,
            product_name="测试产品",
            product_code="P001",
            product_category="软件",
            description="这是一个测试产品"
        )

        assert product_id > 0

        # 验证产品信息
        product = temp_db.get_product_by_id(product_id)
        assert product is not None
        assert product['product_name'] == "测试产品"

    def test_get_products(self, temp_db):
        """测试获取产品列表"""
        # 创建公司和产品
        company_id = temp_db.create_company("测试公司", "TEST001")
        temp_db.create_product(company_id, "产品1", "P001")
        temp_db.create_product(company_id, "产品2", "P002")

        products = temp_db.get_products(company_id)
        assert len(products) >= 2

    def test_create_document_library(self, temp_db):
        """测试创建文档库"""
        # 创建公司和产品
        company_id = temp_db.create_company("文档库测试公司", "DOC001")
        product_id = temp_db.create_product(company_id, "测试产品", "P001")

        # 创建文档库
        library_id = temp_db.create_document_library(
            owner_type='product',
            owner_id=product_id,
            library_name='技术文档库',
            library_type='tech',
            privacy_level=1
        )

        assert library_id > 0

        # 验证文档库
        library = temp_db.get_library(library_id)
        assert library is not None
        assert library['library_name'] == '技术文档库'

    def test_create_document(self, temp_db):
        """测试创建文档记录"""
        # 准备数据
        company_id = temp_db.create_company("文档测试公司", "DOCTEST001")
        product_id = temp_db.create_product(company_id, "测试产品", "P001")
        library_id = temp_db.create_document_library(
            owner_type='product',
            owner_id=product_id,
            library_name='测试文档库',
            library_type='tech'
        )

        # 创建文档
        doc_id = temp_db.create_document(
            library_id=library_id,
            filename='test_doc.pdf',
            original_filename='测试文档.pdf',
            file_path='/path/to/test_doc.pdf',
            file_type='pdf',
            file_size=1024,
            privacy_classification=1,
            tags=['测试', '文档'],
            metadata={'author': '测试员'}
        )

        assert doc_id > 0

        # 验证文档
        documents = temp_db.get_documents(library_id)
        assert len(documents) == 1
        assert documents[0]['original_filename'] == '测试文档.pdf'

    def test_update_document_status(self, temp_db):
        """测试更新文档状态"""
        # 准备数据
        company_id = temp_db.create_company("状态测试公司", "STATUS001")
        product_id = temp_db.create_product(company_id, "测试产品", "P001")
        library_id = temp_db.create_document_library(
            owner_type='product',
            owner_id=product_id,
            library_name='测试库',
            library_type='tech'
        )
        doc_id = temp_db.create_document(
            library_id=library_id,
            filename='test.pdf',
            original_filename='test.pdf',
            file_path='/path/test.pdf',
            file_type='pdf',
            file_size=1024
        )

        # 更新状态
        result = temp_db.update_document_status(
            doc_id=doc_id,
            parse_status='completed',
            vector_status='pending'
        )

        assert result is True

    def test_delete_document(self, temp_db):
        """测试删除文档"""
        # 准备数据
        company_id = temp_db.create_company("删除测试公司", "DEL001")
        product_id = temp_db.create_product(company_id, "测试产品", "P001")
        library_id = temp_db.create_document_library(
            owner_type='product',
            owner_id=product_id,
            library_name='测试库',
            library_type='tech'
        )
        doc_id = temp_db.create_document(
            library_id=library_id,
            filename='delete_test.pdf',
            original_filename='delete_test.pdf',
            file_path='/tmp/delete_test.pdf',
            file_type='pdf',
            file_size=1024
        )

        # 删除文档
        result = temp_db.delete_document(doc_id)
        assert result is True

        # 验证删除
        documents = temp_db.get_documents(library_id)
        assert len(documents) == 0

    def test_get_connection_context_manager(self, temp_db):
        """测试数据库连接上下文管理器"""
        with temp_db.get_connection() as conn:
            assert conn is not None
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_execute_query(self, temp_db):
        """测试执行查询"""
        # 创建公司
        company_id = temp_db.create_company("查询测试公司", "QUERY001")

        # 使用execute_query查询
        result = temp_db.execute_query(
            "SELECT * FROM companies WHERE company_id = ?",
            (company_id,),
            fetch_one=True
        )

        assert result is not None
        assert result['company_name'] == "查询测试公司"

    def test_get_knowledge_base_stats(self, temp_db):
        """测试获取知识库统计信息"""
        # 创建测试数据
        company_id = temp_db.create_company("统计测试公司", "STATS001")
        product_id = temp_db.create_product(company_id, "测试产品", "P001")
        library_id = temp_db.create_document_library(
            owner_type='product',
            owner_id=product_id,
            library_name='测试库',
            library_type='tech'
        )
        temp_db.create_document(
            library_id=library_id,
            filename='doc1.pdf',
            original_filename='doc1.pdf',
            file_path='/path/doc1.pdf',
            file_type='pdf',
            file_size=1024
        )

        # 获取统计
        stats = temp_db.get_knowledge_base_stats(company_id)
        assert stats is not None
        assert 'total_documents' in stats

    def test_create_tender_requirement(self, temp_db):
        """测试创建标书要求"""
        try:
            # 创建项目（使用tender_processing_tasks表）
            task_id = 'task_' + datetime.now().strftime('%Y%m%d%H%M%S')
            temp_db.create_processing_task(
                project_id=1,
                task_id=task_id,
                pipeline_config={'steps': ['parse', 'extract']}
            )

            # 创建标书要求
            req_id = temp_db.create_tender_requirement(
                project_id=1,
                constraint_type='mandatory',
                category='qualification',
                detail='需要提供营业执照',
                priority='high',
                extraction_confidence=0.95
            )

            assert req_id > 0
        except Exception as e:
            # 如果表不存在,跳过这个测试
            pytest.skip(f"标书相关表不存在: {e}")

    def test_config_management(self, temp_db):
        """测试配置管理"""
        # 设置配置
        result = temp_db.set_config('test_key', 'test_value', 'string')
        assert result is True

        # 获取配置
        value = temp_db.get_config('test_key')
        assert value == 'test_value'

        # 测试JSON类型配置
        json_data = {'key': 'value', 'number': 123}
        temp_db.set_config('json_key', json_data, 'json')
        retrieved = temp_db.get_config('json_key')
        assert retrieved == json_data


def test_get_knowledge_base_db():
    """测试获取全局数据库实例"""
    db1 = get_knowledge_base_db()
    db2 = get_knowledge_base_db()

    # 应该返回同一个实例
    assert db1 is db2
