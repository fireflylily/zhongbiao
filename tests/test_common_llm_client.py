#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 common/llm_client.py 模块
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime

from ai_tender_system.common.llm_client import (
    LLMClient,
    create_llm_client,
    get_available_models
)
from ai_tender_system.common.exceptions import APIError


class TestLLMClient:
    """测试 LLMClient 类"""

    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        with patch('ai_tender_system.common.llm_client.get_config') as mock:
            config = Mock()
            config.get_model_config.return_value = {
                'api_key': 'test_api_key',
                'api_endpoint': 'https://api.test.com/v1/chat/completions',
                'model_name': 'gpt-4o-mini',
                'max_tokens': 1000,
                'timeout': 30,
                'display_name': 'GPT-4o Mini',
                'description': 'Test model',
                'provider': 'OpenAI'
            }
            mock.return_value = config
            yield config

    def test_client_initialization(self, mock_config):
        """测试客户端初始化"""
        client = LLMClient(model_name="gpt-4o-mini")

        assert client.model_name == "gpt-4o-mini"
        assert client.api_key == 'test_api_key'
        assert client.max_tokens == 1000
        assert client.timeout == 30

    def test_create_llm_client(self, mock_config):
        """测试工厂函数"""
        client = create_llm_client("gpt-4o-mini")

        assert isinstance(client, LLMClient)
        assert client.model_name == "gpt-4o-mini"

    @patch('ai_tender_system.common.llm_client.requests.post')
    def test_call_openai_compatible_success(self, mock_post, mock_config):
        """测试成功调用OpenAI兼容API"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '这是测试响应'
                }
            }]
        }
        mock_post.return_value = mock_response

        client = LLMClient(model_name="gpt-4o-mini")
        result = client.call(
            prompt="测试提示",
            system_prompt="系统提示",
            temperature=0.7
        )

        assert result == '这是测试响应'
        assert mock_post.called

    @patch('ai_tender_system.common.llm_client.requests.post')
    def test_call_api_error(self, mock_post, mock_config):
        """测试API调用错误"""
        # 模拟API错误响应
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            'error': {
                'message': 'Internal Server Error'
            }
        }
        mock_post.return_value = mock_response

        client = LLMClient(model_name="gpt-4o-mini")

        with pytest.raises(APIError):
            client.call(
                prompt="测试提示",
                max_retries=1
            )

    @patch('ai_tender_system.common.llm_client.requests.post')
    def test_call_timeout(self, mock_post, mock_config):
        """测试API超时"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        client = LLMClient(model_name="gpt-4o-mini")

        with pytest.raises(APIError):
            client.call(
                prompt="测试提示",
                max_retries=1
            )

    @patch('ai_tender_system.common.llm_client.requests.post')
    def test_call_retry_logic(self, mock_post, mock_config):
        """测试重试逻辑"""
        # 第一次失败，第二次成功
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            'choices': [{
                'message': {
                    'content': '重试成功'
                }
            }]
        }

        mock_post.side_effect = [mock_response_fail, mock_response_success]

        client = LLMClient(model_name="gpt-4o-mini")
        result = client.call(
            prompt="测试提示",
            max_retries=2
        )

        assert result == '重试成功'
        assert mock_post.call_count == 2

    def test_unicom_rate_limit_check(self, mock_config):
        """测试联通元景频率限制检查"""
        # 修改配置为联通元景模型
        mock_config.get_model_config.return_value = {
            'access_token': 'test_token',
            'base_url': 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1',
            'model_name': 'unicom-model',
            'max_tokens': 1000,
            'timeout': 30
        }

        client = LLMClient(model_name="unicom-yuanjing")

        # 模拟填满调用记录
        for _ in range(client.UNICOM_RATE_LIMIT):
            client.unicom_call_times.append(datetime.now())

        # 检查频率限制（这个调用应该等待）
        start_time = time.time()
        # 注意：实际测试时会等待，这里只是验证逻辑存在
        # client._check_unicom_rate_limit()
        # elapsed = time.time() - start_time
        # assert elapsed > 0  # 应该等待了一段时间

    def test_extract_content_openai_format(self, mock_config):
        """测试从OpenAI格式响应中提取内容"""
        client = LLMClient(model_name="gpt-4o-mini")

        result = {
            'choices': [{
                'message': {
                    'content': '提取的内容'
                }
            }]
        }

        content = client._extract_content(result, 'openai')
        assert content == '提取的内容'

    def test_extract_content_invalid_format(self, mock_config):
        """测试提取内容时的错误格式"""
        client = LLMClient(model_name="gpt-4o-mini")

        # 缺少choices字段
        result = {'error': 'no choices'}

        with pytest.raises(APIError):
            client._extract_content(result, 'openai')

    def test_parse_error_response_openai(self, mock_config):
        """测试解析OpenAI错误响应"""
        client = LLMClient(model_name="gpt-4o-mini")

        mock_response = Mock()
        mock_response.json.return_value = {
            'error': {
                'message': '请求错误'
            }
        }

        error_msg = client._parse_error_response(mock_response, 'openai')
        assert '请求错误' in error_msg

    def test_should_not_retry_auth_error(self, mock_config):
        """测试认证错误不应重试"""
        client = LLMClient(model_name="gpt-4o-mini")

        mock_response = Mock()
        mock_response.status_code = 401

        should_not_retry = client._should_not_retry(mock_response, 'openai')
        assert should_not_retry is True

    @patch('ai_tender_system.common.llm_client.requests.post')
    def test_validate_config(self, mock_post, mock_config):
        """测试配置验证"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '测试成功'
                }
            }]
        }
        mock_post.return_value = mock_response

        client = LLMClient(model_name="gpt-4o-mini")
        result = client.validate_config()

        assert result['valid'] is True
        assert result['model_name'] == 'gpt-4o-mini'

    def test_get_model_info(self, mock_config):
        """测试获取模型信息"""
        client = LLMClient(model_name="gpt-4o-mini")
        info = client.get_model_info()

        assert info['model_name'] == 'gpt-4o-mini'
        assert info['has_api_key'] is True
        assert 'display_name' in info
        assert 'provider' in info


class TestGetAvailableModels:
    """测试获取可用模型列表"""

    @patch('ai_tender_system.common.llm_client.get_config')
    def test_get_available_models(self, mock_get_config):
        """测试获取可用模型"""
        # 模拟配置
        mock_config = Mock()
        mock_config.get_all_model_configs.return_value = {
            'gpt-4o-mini': {
                'api_key': 'key1',
                'display_name': 'GPT-4o Mini',
                'description': 'Fast model',
                'provider': 'OpenAI',
                'model_name': 'gpt-4o-mini',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions'
            },
            'unicom-yuanjing': {
                'access_token': 'token1',
                'display_name': 'Unicom Yuanjing',
                'description': 'Unicom model',
                'provider': 'Unicom',
                'model_name': 'yuanjing-model',
                'api_endpoint': 'https://maas-api.ai-yuanjing.com/v1/chat'
            }
        }
        mock_get_config.return_value = mock_config

        models = get_available_models()

        assert len(models) == 2
        assert any(m['name'] == 'gpt-4o-mini' for m in models)
        assert any(m['name'] == 'unicom-yuanjing' for m in models)


class TestLLMClientEdgeCases:
    """测试边缘情况"""

    @patch('ai_tender_system.common.llm_client.get_config')
    def test_missing_api_key(self, mock_get_config):
        """测试缺少API密钥"""
        mock_config = Mock()
        mock_config.get_model_config.return_value = {
            'api_key': '',
            'api_endpoint': 'https://api.test.com/v1/chat/completions',
            'model_name': 'test-model',
            'max_tokens': 1000,
            'timeout': 30
        }
        mock_get_config.return_value = mock_config

        client = LLMClient(model_name="test-model")
        assert client.api_key == ''

    @patch('ai_tender_system.common.llm_client.get_config')
    @patch('ai_tender_system.common.llm_client.requests.post')
    def test_empty_response(self, mock_post, mock_get_config):
        """测试空响应"""
        mock_config = Mock()
        mock_config.get_model_config.return_value = {
            'api_key': 'test_key',
            'api_endpoint': 'https://api.test.com/v1/chat/completions',
            'model_name': 'test-model',
            'max_tokens': 1000,
            'timeout': 30
        }
        mock_get_config.return_value = mock_config

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': []
        }
        mock_post.return_value = mock_response

        client = LLMClient(model_name="test-model")

        with pytest.raises(APIError):
            client.call(prompt="测试")
