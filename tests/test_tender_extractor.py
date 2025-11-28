#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 modules/tender_info/extractor.py
包含对TenderInfoExtractor类的全面单元测试
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.modules.tender_info.extractor import TenderInfoExtractor


class TestTenderInfoExtractor:
    """测试TenderInfoExtractor类"""

    @pytest.fixture
    def mock_config(self):
        """Mock配置"""
        with patch('ai_tender_system.modules.tender_info.extractor.get_config') as mock:
            config = Mock()
            config.get_api_config.return_value = {
                'api_key': 'test_key',
                'api_endpoint': 'https://api.test.com/v1/chat/completions',
                'max_tokens': 1000,
                'timeout': 30
            }
            config.get_path.return_value = Path('/tmp/test')
            mock.return_value = config
            yield config

    @pytest.fixture
    def mock_db(self):
        """Mock数据库"""
        with patch('ai_tender_system.modules.tender_info.extractor.get_knowledge_base_db') as mock:
            db = Mock()
            db.get_connection = Mock()
            db.execute_query = Mock()
            mock.return_value = db
            yield db

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM客户端"""
        with patch('ai_tender_system.modules.tender_info.extractor.create_llm_client') as mock:
            client = Mock()
            client.call = Mock(return_value='{"test": "response"}')
            mock.return_value = client
            yield client

    @pytest.fixture
    def extractor(self, mock_config, mock_db, mock_llm_client):
        """创建TenderInfoExtractor实例"""
        return TenderInfoExtractor(api_key="test_key", model_name="gpt-4o-mini")

    def test_init(self, extractor):
        """测试初始化"""
        assert extractor is not None
        assert extractor.model_name == "gpt-4o-mini"
        assert extractor.api_key is not None

    def test_safe_json_parse_valid(self, extractor):
        """测试安全JSON解析 - 有效JSON"""
        json_str = '{"key": "value", "number": 123}'
        result = extractor._safe_json_parse(json_str, "测试")

        assert result is not None
        assert result['key'] == 'value'
        assert result['number'] == 123

    def test_safe_json_parse_with_markdown(self, extractor):
        """测试安全JSON解析 - 带markdown标记"""
        json_str = '```json\n{"key": "value"}\n```'
        result = extractor._safe_json_parse(json_str, "测试")

        assert result is not None
        assert result['key'] == 'value'

    def test_safe_json_parse_empty(self, extractor):
        """测试安全JSON解析 - 空字符串"""
        result = extractor._safe_json_parse("", "测试")
        assert result is None

    def test_safe_json_parse_invalid(self, extractor):
        """测试安全JSON解析 - 无效JSON"""
        result = extractor._safe_json_parse("invalid json {", "测试")
        assert result is None

    def test_clean_json_string(self, extractor):
        """测试JSON字符串清理"""
        dirty_json = "'key': 'value', // comment\n 'number': 123"
        cleaned = extractor._clean_json_string(dirty_json)

        assert "//" not in cleaned
        assert '"key"' in cleaned or "'key'" in cleaned

    def test_get_qualification_keywords(self, extractor):
        """测试获取资质关键字"""
        keywords = extractor._get_qualification_keywords()

        assert isinstance(keywords, dict)
        assert 'business_license' in keywords
        assert 'iso9001' in keywords
        assert '营业执照' in keywords['business_license']

    def test_extract_context_around_keyword(self, extractor):
        """测试提取关键词周围上下文"""
        text = "这是一段测试文本，包含关键词营业执照的内容。需要提取周围的文字。"
        context = extractor._extract_context_around_keyword(text, "营业执照", 10)

        assert "营业执照" in context
        assert len(context) > 0

    def test_extract_sentence_with_keyword(self, extractor):
        """测试提取包含关键词的句子"""
        text = "第一句话。第二句话包含营业执照关键词。第三句话。"
        sentence = extractor._extract_sentence_with_keyword(text, "营业执照")

        assert "营业执照" in sentence
        assert "第二句话" in sentence

    def test_extract_qualification_requirements_by_keywords(self, extractor):
        """测试关键词匹配提取资质要求"""
        text = """
        供应商资格要求：
        1. 具有有效的营业执照
        2. 需要提供ISO9001质量管理体系认证
        3. 提供近三年的审计报告
        4. 不得被列入失信被执行人名单
        """

        result = extractor.extract_qualification_requirements_by_keywords(text)

        assert 'qualifications' in result
        qualifications = result['qualifications']

        # 验证找到的资质
        assert 'business_license' in qualifications
        assert 'iso9001' in qualifications
        assert 'audit_report' in qualifications
        assert 'credit_dishonest' in qualifications

        # 验证资质详情
        assert qualifications['business_license']['required'] is True
        assert len(qualifications['business_license']['keywords_found']) > 0

    def test_extract_qualification_with_negation(self, extractor):
        """测试资质提取时过滤否定词"""
        text = """
        资质要求：
        1. 本项目不适用ISO9001认证
        2. 需要提供营业执照
        """

        result = extractor.extract_qualification_requirements_by_keywords(text)
        qualifications = result['qualifications']

        # ISO9001不应被检测到（因为有"不适用"）
        assert 'iso9001' not in qualifications

        # 营业执照应被检测到
        assert 'business_license' in qualifications

    def test_extract_supplier_eligibility_checklist(self, extractor):
        """测试提取19条供应商资格清单"""
        text = """
        供应商资格要求：
        1. 营业执照
        2. 财务审计报告
        3. 依法缴纳税收
        4. 缴纳社会保险
        """

        result = extractor.extract_supplier_eligibility_checklist(text)

        assert isinstance(result, list)
        assert len(result) == 19  # 应该返回19条清单

        # 检查找到的项
        found_items = [item for item in result if item['found']]
        assert len(found_items) > 0

        # 验证清单项结构
        for item in result:
            assert 'checklist_id' in item
            assert 'checklist_name' in item
            assert 'found' in item
            assert 'requirements' in item

    def test_llm_callback_success(self, extractor, mock_llm_client):
        """测试LLM回调成功"""
        mock_llm_client.call.return_value = "测试响应"

        result = extractor.llm_callback("测试提示词", purpose="测试")

        assert result == "测试响应"
        mock_llm_client.call.assert_called_once()

    def test_llm_callback_error(self, extractor, mock_llm_client):
        """测试LLM回调错误"""
        from ai_tender_system.common.exceptions import APIError

        mock_llm_client.call.side_effect = Exception("API错误")

        with pytest.raises(APIError):
            extractor.llm_callback("测试提示词", purpose="测试")

    def test_read_text_file(self, extractor):
        """测试读取文本文件"""
        # 创建临时文本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("这是测试文本内容")
            temp_file = f.name

        try:
            text = extractor.read_document(temp_file)
            assert "这是测试文本内容" in text
        finally:
            os.remove(temp_file)

    def test_read_unsupported_format(self, extractor):
        """测试读取不支持的文件格式"""
        from ai_tender_system.common.exceptions import FileProcessingError

        with pytest.raises(FileProcessingError) as exc_info:
            extractor.read_document("/path/to/file.xyz")

        assert "不支持的文件格式" in str(exc_info.value)

    def test_read_nonexistent_file(self, extractor):
        """测试读取不存在的文件"""
        from ai_tender_system.common.exceptions import FileProcessingError

        with pytest.raises(FileProcessingError) as exc_info:
            extractor.read_document("/path/to/nonexistent/file.txt")

        assert "文件不存在" in str(exc_info.value)

    def test_extract_basic_info(self, extractor, mock_llm_client):
        """测试提取基本信息"""
        # Mock LLM响应
        mock_response = json.dumps({
            'project_name': '测试项目',
            'project_number': 'PROJ001',
            'tenderer': '测试招标单位'
        })
        mock_llm_client.call.return_value = mock_response

        result = extractor.extract_basic_info("测试文档内容")

        assert result is not None
        assert result['project_name'] == '测试项目'
        assert result['project_number'] == 'PROJ001'

    def test_extract_technical_scoring(self, extractor, mock_llm_client):
        """测试提取技术评分标准"""
        mock_response = json.dumps({
            'total_score': '100',
            'items_count': 2,
            'item_1_name': '技术方案',
            'item_1_weight': '50'
        })
        mock_llm_client.call.return_value = mock_response

        result = extractor.extract_technical_scoring("评分标准文档")

        assert result is not None
        assert 'total_score' in result
        assert 'items_count' in result

    def test_process_document(self, extractor, mock_llm_client, mock_db):
        """测试处理完整文档"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试招标文档内容")
            temp_file = f.name

        try:
            # Mock LLM responses
            mock_llm_client.call.side_effect = [
                json.dumps({'project_name': '测试项目'}),  # 基本信息
                json.dumps({'total_score': '100'})  # 评分标准
            ]

            # Mock数据库操作
            mock_db.get_connection.return_value.__enter__ = Mock()
            mock_db.get_connection.return_value.__exit__ = Mock()

            with patch.object(extractor, 'save_to_database', return_value=1), \
                 patch.object(extractor, 'save_to_config'):
                result = extractor.process_document(temp_file)

                assert result is not None
                assert 'project_id' in result
                assert 'extraction_time' in result

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_save_to_database(self, extractor, mock_db):
        """测试保存到数据库"""
        data = {
            'project_name': '测试项目',
            'project_number': 'PROJ001',
            'file_path': '/path/to/file.txt'
        }

        file_info = {
            'file_path': '/path/to/file.txt',
            'original_filename': 'test.txt',
            'file_size': 1000,
            'file_hash': 'abc123'
        }

        # Mock数据库连接
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_cursor.fetchone.return_value = None
        mock_conn.execute.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock()
        mock_db.get_connection.return_value = mock_conn

        project_id = extractor.save_to_database(data, file_info)

        assert project_id == 1
        assert mock_conn.execute.called

    def test_timeout_regex_search(self, extractor):
        """测试带超时的正则搜索"""
        text = "这是一段测试文本，包含关键词"
        pattern = r"关键词"

        result = extractor._timeout_regex_search(pattern, text, timeout=1)

        assert result is not None
        assert result.group(0) == "关键词"

    def test_timeout_regex_search_timeout(self, extractor):
        """测试正则搜索超时"""
        # 创建一个会导致灾难性回溯的模式
        text = "a" * 100
        pattern = r"(a+)+"

        result = extractor._timeout_regex_search(pattern, text, timeout=1)

        # 超时应返回None
        assert result is None


class TestQualificationKeywords:
    """测试资质关键词相关功能"""

    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        with patch('ai_tender_system.modules.tender_info.extractor.get_config'), \
             patch('ai_tender_system.modules.tender_info.extractor.get_knowledge_base_db'), \
             patch('ai_tender_system.modules.tender_info.extractor.create_llm_client'):
            return TenderInfoExtractor()

    def test_business_license_keywords(self, extractor):
        """测试营业执照关键词"""
        keywords = extractor._get_qualification_keywords()
        business_keywords = keywords['business_license']

        assert '营业执照' in business_keywords
        assert '三证合一' in business_keywords
        assert '注册资金' in business_keywords

    def test_iso_keywords(self, extractor):
        """测试ISO认证关键词"""
        keywords = extractor._get_qualification_keywords()

        assert 'ISO9001' in keywords['iso9001']
        assert 'ISO14001' in keywords['iso14001']
        assert 'ISO27001' in keywords['iso27001']

    def test_social_security_keywords(self, extractor):
        """测试社保关键词"""
        keywords = extractor._get_qualification_keywords()
        social_keywords = keywords['social_security']

        assert '社保' in social_keywords
        assert '社会保险' in social_keywords
        assert '养老保险' in social_keywords

    def test_credit_keywords(self, extractor):
        """测试信用关键词"""
        keywords = extractor._get_qualification_keywords()

        assert '失信被执行人' in keywords['credit_dishonest']
        assert '重大税收违法' in keywords['credit_corruption']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
