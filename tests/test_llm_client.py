#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 common/llm_client.py
包含对LLMClient类的全面单元测试
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.llm_client import LLMClient, create_llm_client, get_available_models
from ai_tender_system.common.exceptions import APIError


class TestLLMClient:
    """测试LLMClient类"""

    @pytest.fixture
    def mock_config(self):
        """Mock配置对象"""
        with patch('ai_tender_system.common.llm_client.get_config') as mock:
            config_obj = Mock()
            config_obj.get_model_config.return_value = {
                'api_key': 'test_api_key',
                'api_endpoint': 'https://api.test.com/v1/chat/completions',
                'model_name': 'gpt-4o-mini',
                'max_tokens': 1000,
                'timeout': 30,
                'display_name': 'GPT-4o Mini',
                'description': 'Test model',
                'provider': 'OpenAI'
            }
            mock.return_value = config_obj
            yield mock

    @pytest.fixture
    def client(self, mock_config):
        """创建测试LLM客户端"""
        return LLMClient(model_name="gpt-4o-mini", api_key="test_key")

    def test_init(self, client):
        """测试初始化"""
        assert client.model_name == "gpt-4o-mini"
        assert client.api_key == "test_key"
        assert client.max_tokens == 1000
        assert client.timeout == 30

    def test_call_openai_compatible_success(self, client):
        """测试OpenAI兼容API调用成功"""
        with patch('ai_tender_system.common.llm_client.requests.post') as mock_post:
            # Mock成功响应
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

            result = client.call("测试提示词", purpose="测试")

            assert result == '这是测试响应'
            assert mock_post.called

    def test_call_with_system_prompt(self, client):
        """测试带系统提示词的调用"""
        with patch('ai_tender_system.common.llm_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {'content': '响应内容'}
                }]
            }
            mock_post.return_value = mock_response

            result = client.call(
                prompt="用户提示词",
                system_prompt="你是一个助手",
                purpose="测试"
            )

            assert result == '响应内容'

            # 验证请求包含system消息
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            messages = request_data['messages']

            assert len(messages) == 2
            assert messages[0]['role'] == 'system'
            assert messages[1]['role'] == 'user'

    def test_call_with_custom_temperature(self, client):
        """测试自定义temperature参数"""
        with patch('ai_tender_system.common.llm_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {'content': '响应'}
                }]
            }
            mock_post.return_value = mock_response

            client.call("提示词", temperature=0.5, purpose="测试")

            call_args = mock_post.call_args
            request_data = call_args[1]['json']

            assert request_data['temperature'] == 0.5

    def test_call_api_error_400(self, client):
        """测试API错误400"""
        with patch('ai_tender_system.common.llm_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                'error': {'message': 'Bad request'}
            }
            mock_post.return_value = mock_response

            with pytest.raises(APIError) as exc_info:
                client.call("测试", max_retries=1, purpose="测试")

            assert '400' in str(exc_info.value)

    def test_call_timeout(self, client):
        """测试请求超时"""
        with patch('ai_tender_system.common.llm_client.requests.post') as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.Timeout()

            with pytest.raises(APIError) as exc_info:
                client.call("测试", max_retries=1, purpose="测试")

            assert '超时' in str(exc_info.value)

    def test_call_retry_success(self, client):
        """测试重试成功"""
        with patch('ai_tender_system.common.llm_client.requests.post') as mock_post:
            # 第一次失败，第二次成功
            mock_response_fail = Mock()
            mock_response_fail.status_code = 500
            mock_response_fail.json.return_value = {'error': {'message': 'Server error'}}

            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = {
                'choices': [{'message': {'content': '成功响应'}}]
            }

            mock_post.side_effect = [mock_response_fail, mock_response_success]

            result = client.call("测试", max_retries=2, purpose="测试")

            assert result == '成功响应'
            assert mock_post.call_count == 2

    def test_validate_config_success(self, client):
        """测试配置验证成功"""
        with patch.object(client, 'call') as mock_call:
            mock_call.return_value = "测试成功"

            result = client.validate_config()

            assert result['valid'] is True
            assert result['model_name'] == 'gpt-4o-mini'
            assert result['has_api_key'] is True

    def test_validate_config_failure(self, client):
        """测试配置验证失败"""
        with patch.object(client, 'call') as mock_call:
            mock_call.side_effect = APIError("API调用失败")

            result = client.validate_config()

            assert result['valid'] is False
            assert 'error' in result

    def test_get_model_info(self, client):
        """测试获取模型信息"""
        info = client.get_model_info()

        assert info['model_name'] == 'gpt-4o-mini'
        assert info['max_tokens'] == 1000
        assert info['timeout'] == 30
        assert info['has_api_key'] is True

    def test_unicom_rate_limit(self):
        """测试联通元景频率限制"""
        with patch('ai_tender_system.common.llm_client.get_config') as mock_config:
            config_obj = Mock()
            config_obj.get_model_config.return_value = {
                'access_token': 'test_token',
                'base_url': 'https://test.com/v1',
                'model_name': 'yuanjing-test',
                'max_tokens': 1000,
                'timeout': 30,
                'display_name': 'Yuanjing Test',
                'provider': 'Unicom'
            }
            mock_config.return_value = config_obj

            client = LLMClient(model_name="unicom-yuanjing")

            # 模拟快速连续调用，验证频率限制逻辑
            for i in range(LLMClient.UNICOM_RATE_LIMIT):
                client.unicom_call_times.append(datetime.now())

            # 检查频率限制
            client._check_unicom_rate_limit()

            # 验证调用时间队列
            assert len(client.unicom_call_times) <= LLMClient.UNICOM_RATE_LIMIT

    def test_extract_content_openai_format(self, client):
        """测试提取OpenAI格式内容"""
        result = {
            'choices': [{
                'message': {
                    'content': '测试内容'
                }
            }]
        }

        content = client._extract_content(result, 'openai')
        assert content == '测试内容'

    def test_extract_content_invalid_format(self, client):
        """测试提取无效格式内容"""
        result = {'invalid': 'data'}

        with pytest.raises(APIError):
            client._extract_content(result, 'openai')

    def test_parse_error_response_openai(self, client):
        """测试解析OpenAI错误响应"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'Invalid request'
            }
        }

        error_msg = client._parse_error_response(mock_response, 'openai')
        assert 'Invalid request' in error_msg

    def test_should_not_retry_401(self, client):
        """测试401不应重试"""
        mock_response = Mock()
        mock_response.status_code = 401

        should_not_retry = client._should_not_retry(mock_response, 'openai')
        assert should_not_retry is True

    def test_should_retry_500(self, client):
        """测试500应该重试"""
        mock_response = Mock()
        mock_response.status_code = 500

        should_not_retry = client._should_not_retry(mock_response, 'openai')
        assert should_not_retry is False


class TestLLMClientHelpers:
    """测试LLM客户端辅助函数"""

    def test_create_llm_client(self):
        """测试创建LLM客户端工厂函数"""
        with patch('ai_tender_system.common.llm_client.get_config') as mock_config:
            config_obj = Mock()
            config_obj.get_model_config.return_value = {
                'api_key': 'test_key',
                'api_endpoint': 'https://api.test.com/v1/chat/completions',
                'model_name': 'gpt-4o-mini',
                'max_tokens': 1000,
                'timeout': 30
            }
            mock_config.return_value = config_obj

            client = create_llm_client("gpt-4o-mini", "custom_key")

            assert isinstance(client, LLMClient)
            assert client.model_name == "gpt-4o-mini"
            assert client.api_key == "custom_key"

    def test_get_available_models(self):
        """测试获取可用模型列表"""
        with patch('ai_tender_system.common.llm_client.get_config') as mock_config:
            config_obj = Mock()
            config_obj.get_all_model_configs.return_value = {
                'gpt-4o-mini': {
                    'display_name': 'GPT-4o Mini',
                    'description': 'Fast and efficient model',
                    'provider': 'OpenAI',
                    'model_name': 'gpt-4o-mini',
                    'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                    'api_key': 'sk-test'
                },
                'unicom-yuanjing': {
                    'display_name': '联通元景',
                    'description': '国产大模型',
                    'provider': 'Unicom',
                    'model_name': 'yuanjing-v1',
                    'api_endpoint': 'https://maas-api.ai-yuanjing.com/v1',
                    'access_token': 'token-test'
                }
            }
            mock_config.return_value = config_obj

            models = get_available_models()

            assert len(models) >= 2
            model_names = [m['name'] for m in models]
            assert 'gpt-4o-mini' in model_names
            assert 'unicom-yuanjing' in model_names

            # 验证模型信息
            gpt_model = next(m for m in models if m['name'] == 'gpt-4o-mini')
            assert gpt_model['has_api_key'] is True
            assert gpt_model['provider'] == 'OpenAI'


class TestUnicomYuanjingClient:
    """测试联通元景客户端特定功能"""

    @pytest.fixture
    def unicom_client(self):
        """创建联通元景测试客户端"""
        with patch('ai_tender_system.common.llm_client.get_config') as mock_config:
            config_obj = Mock()
            config_obj.get_model_config.return_value = {
                'access_token': 'test_token',
                'base_url': 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1',
                'model_name': 'yuanjing-lite',
                'max_tokens': 2000,
                'timeout': 60,
                'display_name': 'Yuanjing Lite',
                'provider': 'Unicom'
            }
            mock_config.return_value = config_obj

            return LLMClient(model_name="unicom-yuanjing")

    def test_unicom_client_init(self, unicom_client):
        """测试联通元景客户端初始化"""
        assert unicom_client.model_name == "unicom-yuanjing"
        assert unicom_client.base_url == 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1'
        assert unicom_client.api_key == 'test_token'

    def test_unicom_call_with_rate_limit(self, unicom_client):
        """测试联通元景频率限制调用"""
        with patch('ai_tender_system.common.llm_client.OpenAI') as mock_openai_class:
            # Mock OpenAI客户端
            mock_client = Mock()
            mock_completion = Mock()
            mock_completion.choices = [Mock(message=Mock(content='测试响应'))]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai_class.return_value = mock_client

            result = unicom_client.call("测试提示词", purpose="测试")

            assert result == '测试响应'
            assert mock_client.chat.completions.create.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
