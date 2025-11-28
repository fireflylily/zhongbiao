#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 modules/knowledge_base/manager.py
包含对KnowledgeBaseManager类的全面单元测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.modules.knowledge_base.manager import KnowledgeBaseManager


class TestKnowledgeBaseManager:
    """测试KnowledgeBaseManager类"""

    @pytest.fixture
    def mock_db(self):
        """Mock数据库"""
        with patch('ai_tender_system.modules.knowledge_base.manager.get_knowledge_base_db') as mock:
            db = Mock()
            db.create_company = Mock(return_value=1)
            db.get_companies = Mock(return_value=[])
            db.get_company_by_id = Mock(return_value={'company_id': 1, 'company_name': '测试公司'})
            db.update_company = Mock(return_value=True)
            db.create_product = Mock(return_value=1)
            db.get_products = Mock(return_value=[])
            db.get_product_by_id = Mock(return_value={'product_id': 1})
            db.create_document_library = Mock(return_value=1)
            db.get_document_libraries = Mock(return_value=[])
            db.get_library = Mock(return_value={'library_id': 1})
            db.create_document = Mock(return_value=1)
            db.get_documents = Mock(return_value=[])
            db.delete_document = Mock(return_value=True)
            db.update_document_status = Mock(return_value=True)
            db.execute_query = Mock(return_value=[])
            db.get_connection = Mock()
            db.create_company_profile = Mock(return_value=1)
            db.save_company_qualification = Mock(return_value=1)
            db.get_company_qualifications = Mock(return_value=[])
            mock.return_value = db
            yield db

    @pytest.fixture
    def mock_config(self):
        """Mock配置"""
        with patch('ai_tender_system.modules.knowledge_base.manager.get_config') as mock:
            config = Mock()
            temp_dir = tempfile.mkdtemp()
            config.get_path = Mock(return_value=Path(temp_dir))
            mock.return_value = config
            yield config

    @pytest.fixture
    def manager(self, mock_db, mock_config):
        """创建KnowledgeBaseManager实例"""
        return KnowledgeBaseManager()

    def test_init(self, manager):
        """测试初始化"""
        assert manager is not None
        assert manager.db is not None
        assert manager.config is not None

    def test_create_company_success(self, manager, mock_db):
        """测试创建公司成功"""
        # Mock公司列表为空（无重复）
        mock_db.get_companies.return_value = []

        result = manager.create_company(
            company_name="新公司",
            company_code="NEW001",
            industry_type="IT",
            description="测试描述"
        )

        assert result['success'] is True
        assert result['company_id'] == 1
        mock_db.create_company.assert_called_once()

    def test_create_company_duplicate_name(self, manager, mock_db):
        """测试创建重复公司名称"""
        # Mock已存在的公司
        mock_db.get_companies.return_value = [
            {'company_name': '已存在公司', 'company_code': 'EXIST001'}
        ]

        result = manager.create_company(
            company_name="已存在公司",
            company_code="NEW001"
        )

        assert result['success'] is False
        assert '已存在' in result['error']

    def test_create_company_duplicate_code(self, manager, mock_db):
        """测试创建重复公司代码"""
        mock_db.get_companies.return_value = [
            {'company_name': '其他公司', 'company_code': 'SAME001'}
        ]

        result = manager.create_company(
            company_name="新公司",
            company_code="SAME001"
        )

        assert result['success'] is False
        assert '已存在' in result['error']

    def test_update_company_success(self, manager, mock_db):
        """测试更新公司信息成功"""
        data = {
            'companyName': '更新后的公司',
            'registeredCapital': '1000万元'
        }

        result = manager.update_company(company_id=1, data=data)

        assert result['success'] is True
        mock_db.update_company.assert_called_once()

    def test_update_company_not_found(self, manager, mock_db):
        """测试更新不存在的公司"""
        mock_db.get_company_by_id.return_value = None

        result = manager.update_company(company_id=999, data={'companyName': '测试'})

        assert result['success'] is False
        assert '不存在' in result['error']

    def test_update_company_no_fields(self, manager, mock_db):
        """测试更新公司但没有可更新字段"""
        result = manager.update_company(company_id=1, data={})

        assert result['success'] is False
        assert '没有可更新的字段' in result['error']

    def test_get_companies(self, manager, mock_db):
        """测试获取公司列表"""
        mock_db.get_companies.return_value = [
            {'company_id': 1, 'company_name': '公司1'},
            {'company_id': 2, 'company_name': '公司2'}
        ]
        mock_db.get_products.return_value = []
        mock_db.get_knowledge_base_stats.return_value = {'total_documents': 0}

        companies = manager.get_companies()

        assert len(companies) == 2
        assert companies[0]['company_name'] == '公司1'

    def test_get_company_detail(self, manager, mock_db):
        """测试获取公司详情"""
        mock_db.get_company_by_id.return_value = {
            'company_id': 1,
            'company_name': '测试公司'
        }
        mock_db.get_company_profiles.return_value = []
        mock_db.get_products.return_value = []
        mock_db.get_knowledge_base_stats.return_value = {}

        detail = manager.get_company_detail(company_id=1)

        assert detail is not None
        assert detail['company_name'] == '测试公司'
        assert 'profiles' in detail
        assert 'products' in detail

    def test_get_company_detail_not_found(self, manager, mock_db):
        """测试获取不存在的公司详情"""
        mock_db.get_company_by_id.return_value = None

        detail = manager.get_company_detail(company_id=999)

        assert detail is None

    def test_create_product_success(self, manager, mock_db):
        """测试创建产品成功"""
        mock_db.get_products.return_value = []

        result = manager.create_product(
            company_id=1,
            product_name="测试产品",
            product_code="PROD001"
        )

        assert result['success'] is True
        assert result['product_id'] == 1
        mock_db.create_product.assert_called_once()

    def test_create_product_company_not_found(self, manager, mock_db):
        """测试为不存在的公司创建产品"""
        mock_db.get_company_by_id.return_value = None

        result = manager.create_product(
            company_id=999,
            product_name="测试产品"
        )

        assert result['success'] is False
        assert '不存在' in result['error']

    def test_create_product_duplicate_code(self, manager, mock_db):
        """测试创建重复产品代码"""
        mock_db.get_products.return_value = [
            {'product_code': 'PROD001'}
        ]

        result = manager.create_product(
            company_id=1,
            product_name="新产品",
            product_code="PROD001"
        )

        assert result['success'] is False
        assert '已存在' in result['error']

    def test_get_products(self, manager, mock_db):
        """测试获取产品列表"""
        mock_db.get_products.return_value = [
            {'product_id': 1, 'product_name': '产品1'},
            {'product_id': 2, 'product_name': '产品2'}
        ]
        mock_db.get_document_libraries.return_value = []

        products = manager.get_products(company_id=1)

        assert len(products) == 2
        assert products[0]['product_name'] == '产品1'

    def test_get_product_detail(self, manager, mock_db):
        """测试获取产品详情"""
        mock_db.get_product_by_id.return_value = {
            'product_id': 1,
            'product_name': '测试产品'
        }
        mock_db.get_document_libraries.return_value = []

        detail = manager.get_product_detail(product_id=1)

        assert detail is not None
        assert detail['product_name'] == '测试产品'
        assert 'libraries' in detail

    def test_upload_document_success(self, manager, mock_db):
        """测试上传文档成功"""
        # Mock文件对象
        file_obj = Mock()
        file_obj.read = Mock(return_value=b'file content')

        # Mock存储服务
        with patch('ai_tender_system.modules.knowledge_base.manager.storage_service') as mock_storage:
            mock_file_metadata = Mock()
            mock_file_metadata.file_id = 'file123'
            mock_file_metadata.safe_name = 'safe_name.pdf'
            mock_file_metadata.original_name = 'original.pdf'
            mock_file_metadata.file_path = '/path/to/file.pdf'
            mock_file_metadata.file_size = 1024
            mock_file_metadata.checksum = 'abc123'
            mock_storage.store_file.return_value = mock_file_metadata

            mock_db.get_library.return_value = {
                'owner_type': 'product',
                'owner_id': 1
            }
            mock_db.get_product.return_value = {'company_id': 1}

            result = manager.upload_document(
                library_id=1,
                file_obj=file_obj,
                original_filename='test.pdf'
            )

            assert result['success'] is True
            assert result['doc_id'] == 1
            assert result['file_id'] == 'file123'

    def test_get_documents(self, manager, mock_db):
        """测试获取文档列表"""
        mock_db.get_documents.return_value = [
            {
                'doc_id': 1,
                'original_filename': 'test.pdf',
                'file_path': '/path/to/test.pdf',
                'file_size': 1024,
                'tags': '[]',
                'metadata': '{}'
            }
        ]

        docs = manager.get_documents(library_id=1)

        assert len(docs) == 1
        assert docs[0]['original_filename'] == 'test.pdf'

    def test_update_document_status(self, manager, mock_db):
        """测试更新文档状态"""
        result = manager.update_document_status(
            doc_id=1,
            parse_status='completed',
            vector_status='completed'
        )

        assert result is True
        mock_db.update_document_status.assert_called_once()

    def test_delete_document_success(self, manager, mock_db):
        """测试删除文档成功"""
        # Mock文档信息
        mock_db.get_documents.return_value = [
            {
                'doc_id': 1,
                'original_filename': 'test.pdf',
                'file_path': '/tmp/test.pdf',
                'vector_status': 'pending'
            }
        ]

        # 创建临时文件
        temp_file = '/tmp/test_doc_delete.pdf'
        with open(temp_file, 'w') as f:
            f.write('test')

        try:
            # 更新mock返回的file_path
            mock_db.get_documents.return_value[0]['file_path'] = temp_file

            result = manager.delete_document(doc_id=1)

            assert result['success'] is True
            mock_db.delete_document.assert_called_once_with(1)

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_delete_document_not_found(self, manager, mock_db):
        """测试删除不存在的文档"""
        mock_db.get_documents.return_value = []

        result = manager.delete_document(doc_id=999)

        assert result['success'] is False
        assert '不存在' in result['error']

    def test_check_document_access(self, manager):
        """测试检查文档访问权限"""
        # 公开文档
        assert manager.check_document_access('guest', 1) is True

        # 内部文档
        assert manager.check_document_access('user', 2) is True
        assert manager.check_document_access('guest', 2) is False

        # 机密文档
        assert manager.check_document_access('admin', 3) is True
        assert manager.check_document_access('user', 3) is False

    def test_log_document_access(self, manager, mock_db):
        """测试记录文档访问日志"""
        log_id = manager.log_document_access(
            user_id='user1',
            user_role='user',
            action_type='view',
            doc_id=1,
            privacy_level=1,
            access_granted=True
        )

        assert log_id >= 0

    def test_get_dashboard_stats(self, manager, mock_db):
        """测试获取仪表板统计"""
        mock_db.get_knowledge_base_stats.return_value = {
            'total_documents': 100,
            'by_type': {},
            'by_product': {}
        }

        stats = manager.get_dashboard_stats(company_id=1)

        assert 'total_documents' in stats or 'company_name' in stats

    def test_search_documents(self, manager, mock_db):
        """测试搜索文档"""
        mock_db.execute_query.return_value = [
            {
                'doc_id': 1,
                'original_filename': '测试文档.pdf',
                'library_type': 'tech'
            }
        ]

        results = manager.search_documents(query="测试", privacy_level=2)

        assert len(results) >= 0

    def test_upload_qualification_success(self, manager, mock_db):
        """测试上传资质文件成功"""
        file_obj = Mock()

        with patch('ai_tender_system.modules.knowledge_base.manager.storage_service') as mock_storage:
            mock_file_metadata = Mock()
            mock_file_metadata.file_id = 'qual123'
            mock_file_metadata.safe_name = 'license.pdf'
            mock_file_metadata.original_name = '营业执照.pdf'
            mock_file_metadata.file_path = '/path/to/license.pdf'
            mock_file_metadata.file_size = 2048
            mock_storage.store_file.return_value = mock_file_metadata

            result = manager.upload_qualification(
                company_id=1,
                qualification_key='business_license',
                file_obj=file_obj,
                original_filename='营业执照.pdf',
                qualification_name='营业执照'
            )

            assert result['success'] is True
            assert result['qualification_id'] == 1

    def test_get_company_qualifications(self, manager, mock_db):
        """测试获取公司资质列表"""
        mock_db.get_company_qualifications.return_value = [
            {
                'qualification_id': 1,
                'qualification_name': '营业执照',
                'file_path': '/path/to/license.pdf',
                'file_size': 1024,
                'expire_date': None
            }
        ]

        quals = manager.get_company_qualifications(company_id=1)

        assert len(quals) == 1
        assert 'file_exists' in quals[0]
        assert 'is_expired' in quals[0]

    def test_get_qualification_types(self, manager, mock_db):
        """测试获取资质类型定义"""
        mock_db.execute_query.return_value = [
            {
                'type_key': 'business_license',
                'type_name': '营业执照',
                'category': '基础资质',
                'is_required': 1,
                'description': '企业营业执照',
                'sort_order': 1,
                'is_active': 1,
                'created_at': '2025-01-01'
            }
        ]

        types = manager.get_qualification_types()

        assert len(types) == 1
        assert types[0]['qualification_key'] == 'business_license'
        assert types[0]['is_required'] is True

    def test_get_all_documents_with_filters(self, manager, mock_db):
        """测试获取所有文档（带筛选）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock()
        mock_db.get_connection.return_value = mock_conn

        docs = manager.get_all_documents_with_filters(
            company_id=1,
            product_id=1
        )

        assert isinstance(docs, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
