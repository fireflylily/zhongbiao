#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一LLM调用客户端
支持多种大模型的统一接口调用，包括OpenAI兼容格式和联通元景大模型
"""

import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import deque

# 导入第三方库
from openai import OpenAI

# 导入公共模块
from .config import get_config
from .logger import get_module_logger
from .exceptions import APIError


class LLMClient:
    """统一的LLM调用客户端"""

    # 联通元景访问频率限制：每分钟5次
    UNICOM_RATE_LIMIT = 5
    UNICOM_TIME_WINDOW = 60  # 秒

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        初始化LLM客户端

        Args:
            model_name: 模型名称 (gpt-4o-mini, unicom-yuanjing)
            api_key: API密钥，如果不提供则从配置中获取
        """
        self.config = get_config()
        self.logger = get_module_logger("llm_client")
        self.model_name = model_name

        # 联通元景访问频率控制
        self.unicom_call_times = deque(maxlen=self.UNICOM_RATE_LIMIT)

        # 获取模型配置
        self.model_config = self.config.get_model_config(model_name)

        # 根据模型类型设置不同的配置
        if model_name.startswith('unicom') or model_name.startswith('yuanjing'):
            # 联通元景配置
            self.api_key = api_key or self.model_config.get('access_token', '')
            self.base_url = self.model_config.get('base_url', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')
            self.api_endpoint = f"{self.base_url}/chat/completions"
        elif model_name.startswith('shihuang'):
            # 始皇API配置 - OpenAI兼容格式
            self.api_key = api_key or self.model_config.get('api_key', '')
            self.api_endpoint = self.model_config.get('api_endpoint', 'https://api.oaipro.com/v1/chat/completions')
            self.base_url = self.api_endpoint.rsplit('/chat/completions', 1)[0]
            # 始皇API特殊参数
            self.temperature = self.model_config.get('temperature', 0.3)
        else:
            # OpenAI兼容配置
            self.api_key = api_key or self.model_config.get('api_key', '')
            self.api_endpoint = self.model_config.get('api_endpoint', 'https://api.oaipro.com/v1/chat/completions')
            self.base_url = self.api_endpoint.rsplit('/chat/completions', 1)[0]

        self.max_tokens = self.model_config.get('max_tokens', 1000)
        self.timeout = self.model_config.get('timeout', 30)

        # 模型特定配置
        self.actual_model_name = self.model_config.get('model_name', model_name)

        self.logger.info(f"LLM客户端初始化完成，模型: {model_name}")

    def call(self,
             prompt: str,
             system_prompt: Optional[str] = None,
             temperature: float = 0.7,
             max_retries: int = 3,
             purpose: str = "LLM调用") -> str:
        """
        统一的LLM调用接口

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_retries: 最大重试次数
            purpose: 调用目的（用于日志）

        Returns:
            模型响应文本

        Raises:
            APIError: API调用失败
        """
        if self.model_name.startswith('unicom') or self.model_name.startswith('yuanjing'):
            try:
                return self._call_unicom_yuanjing(
                    prompt, system_prompt, temperature, max_retries, purpose
                )
            except APIError as e:
                # 如果联通元景API不可用，尝试使用默认的OpenAI兼容API作为fallback
                error_str = str(e)
                if "服务暂时不可用" in error_str or "code: 14" in error_str:
                    self.logger.warning(f"联通元景API不可用，尝试使用默认API作为fallback: {e}")
                    return self._call_openai_compatible_fallback(
                        prompt, system_prompt, temperature, max_retries, f"{purpose} (fallback)"
                    )
                else:
                    raise  # 对于其他错误，直接抛出
        elif self.model_name.startswith('shihuang'):
            # 始皇API使用OpenAI兼容格式，但使用配置的温度参数
            actual_temperature = self.temperature if hasattr(self, 'temperature') else temperature
            return self._call_openai_compatible(
                prompt, system_prompt, actual_temperature, max_retries, purpose
            )
        else:
            return self._call_openai_compatible(
                prompt, system_prompt, temperature, max_retries, purpose
            )

    def _call_openai_compatible(self,
                               prompt: str,
                               system_prompt: Optional[str] = None,
                               temperature: float = 0.7,
                               max_retries: int = 3,
                               purpose: str = "OpenAI兼容调用") -> str:
        """
        调用OpenAI兼容格式的API
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        data = {
            'model': self.actual_model_name,
            'messages': messages,
            'max_completion_tokens': self.max_tokens,
            'temperature': temperature
        }

        return self._make_request(
            headers, data, max_retries, purpose, 'openai'
        )

    def _call_openai_compatible_fallback(self,
                                        prompt: str,
                                        system_prompt: Optional[str] = None,
                                        temperature: float = 0.7,
                                        max_retries: int = 3,
                                        purpose: str = "OpenAI兼容fallback调用") -> str:
        """
        使用默认OpenAI兼容API作为fallback
        """
        config = get_config()
        default_config = config.get_all_model_configs().get('default', {})

        # 使用默认配置
        fallback_endpoint = default_config.get('api_endpoint', 'https://api.oaipro.com/v1/chat/completions')
        fallback_key = default_config.get('api_key', '')
        fallback_model = default_config.get('model_name', 'gpt-4o-mini')

        if not fallback_key:
            raise APIError("fallback API密钥未配置")

        headers = {
            'Authorization': f'Bearer {fallback_key}',
            'Content-Type': 'application/json'
        }

        # 构建消息
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        data = {
            'model': fallback_model,
            'messages': messages,
            'max_tokens': self.max_tokens,
            'temperature': temperature
        }

        # 临时替换endpoint进行fallback调用
        original_endpoint = self.api_endpoint
        self.api_endpoint = fallback_endpoint
        try:
            return self._make_request(
                headers, data, max_retries, purpose, 'openai'
            )
        finally:
            # 恢复原始endpoint
            self.api_endpoint = original_endpoint

    def _check_unicom_rate_limit(self) -> None:
        """
        检查联通元景API访问频率限制
        试用账号每分钟最多调用5次
        """
        now = datetime.now()

        # 清理超过时间窗口的记录
        while self.unicom_call_times and self.unicom_call_times[0] < now - timedelta(seconds=self.UNICOM_TIME_WINDOW):
            self.unicom_call_times.popleft()

        # 检查是否超过频率限制
        if len(self.unicom_call_times) >= self.UNICOM_RATE_LIMIT:
            # 计算需要等待的时间
            oldest_time = self.unicom_call_times[0]
            wait_time = (oldest_time + timedelta(seconds=self.UNICOM_TIME_WINDOW) - now).total_seconds()

            if wait_time > 0:
                self.logger.warning(f"联通元景API频率限制: 需要等待 {wait_time:.1f} 秒")
                self.logger.info(f"试用账号限制: 每分钟最多 {self.UNICOM_RATE_LIMIT} 次调用")
                time.sleep(wait_time + 1)  # 多等1秒确保安全

                # 等待后重新清理
                now = datetime.now()
                while self.unicom_call_times and self.unicom_call_times[0] < now - timedelta(seconds=self.UNICOM_TIME_WINDOW):
                    self.unicom_call_times.popleft()

    def _call_unicom_yuanjing(self,
                             prompt: str,
                             system_prompt: Optional[str] = None,
                             temperature: float = 0.7,
                             max_retries: int = 3,
                             purpose: str = "联通元景调用") -> str:
        """
        调用联通元景大模型API
        使用OpenAI库调用，基于官方API文档示例
        包含访问频率控制（试用账号每分钟5次）
        """
        try:
            # 检查并控制访问频率
            self._check_unicom_rate_limit()

            # 使用OpenAI客户端，按照官方示例
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            # 构建消息格式
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            self.logger.info(f"{purpose} - 使用模型: {self.actual_model_name}")

            for attempt in range(max_retries):
                try:
                    self.logger.info(f"{purpose} (尝试 {attempt + 1}/{max_retries})")

                    # 记录调用时间
                    self.unicom_call_times.append(datetime.now())
                    self.logger.debug(f"当前分钟内已调用 {len(self.unicom_call_times)}/{self.UNICOM_RATE_LIMIT} 次")

                    # 调用API
                    completion = client.chat.completions.create(
                        model=self.actual_model_name,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=temperature
                    )

                    # 提取响应内容
                    content = completion.choices[0].message.content
                    self.logger.info(f"{purpose} 成功")
                    return content

                except Exception as e:
                    error_msg = str(e)

                    # 检查是否是频率限制错误
                    if '5001' in error_msg or '限流' in error_msg or '429' in error_msg:
                        self.logger.warning(f"触发频率限制，等待60秒后重试...")
                        time.sleep(61)  # 等待超过1分钟
                        # 清空调用记录
                        self.unicom_call_times.clear()
                    else:
                        self.logger.error(f"{purpose} 尝试 {attempt + 1} 失败: {error_msg}")

                        if attempt == max_retries - 1:
                            raise APIError(f"{purpose}: {error_msg}")

                        # 其他错误的重试等待
                        time.sleep(2 ** attempt)

        except APIError:
            raise
        except Exception as e:
            error_msg = f"联通元景API调用失败: {str(e)}"
            self.logger.error(error_msg)
            raise APIError(error_msg)


    def _make_request(self,
                     headers: Dict[str, str],
                     data: Dict[str, Any],
                     max_retries: int,
                     purpose: str,
                     api_type: str) -> str:
        """
        执行HTTP请求
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(f"{purpose} (尝试 {attempt + 1}/{max_retries})")

                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    content = self._extract_content(result, api_type)
                    self.logger.info(f"{purpose} 成功")
                    return content
                else:
                    # 处理不同API的特定错误
                    error_details = self._parse_error_response(response, api_type)
                    error_msg = f"API调用失败: {response.status_code} - {error_details}"
                    self.logger.error(error_msg)

                    # 对于某些错误，不重试
                    if self._should_not_retry(response, api_type):
                        raise APIError(error_msg)

                    if attempt == max_retries - 1:
                        raise APIError(error_msg)

            except requests.exceptions.Timeout:
                error_msg = f"API调用超时 - {purpose}"
                self.logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise APIError(error_msg)

            except requests.exceptions.RequestException as e:
                error_msg = f"API请求异常 - {purpose}: {str(e)}"
                self.logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise APIError(error_msg)

            except Exception as e:
                error_msg = f"未预期的错误 - {purpose}: {str(e)}"
                self.logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise APIError(error_msg)

            # 重试前等待
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避

    def _extract_content(self, result: Dict[str, Any], api_type: str) -> str:
        """
        从API响应中提取内容
        """
        try:
            if api_type == 'openai':
                # OpenAI兼容格式
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    raise APIError(f"OpenAI格式API响应异常: {result}")

            elif api_type == 'unicom':
                # 联通元景格式（可能需要根据实际API调整）
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                elif 'data' in result and 'text' in result['data']:
                    # 可能的另一种响应格式
                    return result['data']['text']
                else:
                    raise APIError(f"联通元景API响应异常: {result}")

            else:
                raise APIError(f"未知的API类型: {api_type}")

        except KeyError as e:
            raise APIError(f"API响应格式错误，缺少字段: {e}")

    def _parse_error_response(self, response, api_type: str) -> str:
        """
        解析API错误响应
        """
        try:
            error_data = response.json()

            if api_type == 'unicom':
                # 联通元景特定错误格式
                error_code = error_data.get('code', 'unknown')
                error_msg = error_data.get('msg', '未知错误')
                lid = error_data.get('lid', '')

                # 特定错误代码的处理
                if error_code == 14:
                    return f"服务暂时不可用 (code: {error_code}, msg: {error_msg})"
                elif error_code == 5001:
                    return f"请求频率限制 (code: {error_code}, msg: {error_msg})"
                elif error_code == 1000:
                    return f"认证失败 (code: {error_code}, msg: {error_msg})"
                else:
                    return f"错误代码: {error_code}, 消息: {error_msg}, ID: {lid}"

            elif api_type == 'openai':
                # OpenAI格式错误
                error_info = error_data.get('error', {})
                return error_info.get('message', str(error_data))

            else:
                return str(error_data)

        except (ValueError, KeyError):
            return response.text[:200]

    def _should_not_retry(self, response, api_type: str) -> bool:
        """
        判断是否不应该重试
        """
        if api_type == 'unicom':
            try:
                error_data = response.json()
                error_code = error_data.get('code')

                # 以下错误不应该重试
                if error_code in [1000, 14]:  # 认证失败或服务不可用
                    return True

            except (ValueError, KeyError):
                pass

        # 401 和 403 通常不应该重试
        if response.status_code in [401, 403]:
            return True

        return False

    def validate_config(self) -> Dict[str, Any]:
        """
        验证当前模型配置是否有效

        Returns:
            验证结果字典
        """
        result = {
            'valid': False,
            'model_name': self.model_name,
            'endpoint': self.api_endpoint,
            'has_api_key': bool(self.api_key),
            'error': None
        }

        try:
            # 发送测试请求
            test_response = self.call(
                "请回复'测试成功'",
                purpose="配置验证",
                max_retries=1
            )

            if test_response and '测试成功' in test_response:
                result['valid'] = True
                result['test_response'] = test_response
            else:
                result['error'] = f"测试响应异常: {test_response}"

        except Exception as e:
            result['error'] = str(e)

        return result

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        """
        info = {
            'model_name': self.model_name,
            'actual_model_name': self.actual_model_name,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'has_api_key': bool(self.api_key),
            'display_name': self.model_config.get('display_name', self.model_name),
            'description': self.model_config.get('description', ''),
            'provider': self.model_config.get('provider', 'Unknown')
        }

        # 根据模型类型添加不同的端点信息
        if self.model_name.startswith('unicom') or self.model_name.startswith('yuanjing'):
            info['base_url'] = getattr(self, 'base_url', '')
            info['api_endpoint'] = f"{info['base_url']}/chat/completions"
        else:
            info['api_endpoint'] = self.api_endpoint

        return info


def create_llm_client(model_name: str = "gpt-4o-mini", api_key: Optional[str] = None) -> LLMClient:
    """
    工厂函数：创建LLM客户端

    Args:
        model_name: 模型名称
        api_key: API密钥

    Returns:
        LLMClient实例
    """
    return LLMClient(model_name, api_key)


def get_available_models() -> List[Dict[str, Any]]:
    """
    获取所有可用的模型配置

    Returns:
        模型配置列表
    """
    config = get_config()
    all_configs = config.get_all_model_configs()

    models = []
    for model_name, model_config in all_configs.items():
        # 检查API密钥 - 联通元景模型使用access_token，其他模型使用api_key
        if model_name.startswith('unicom') or model_name.startswith('yuanjing'):
            has_key = bool(model_config.get('access_token', ''))
        else:
            has_key = bool(model_config.get('api_key', ''))

        models.append({
            'name': model_name,
            'display_name': model_config.get('display_name', model_name),
            'description': model_config.get('description', ''),
            'provider': model_config.get('provider', 'Unknown'),
            'model_name': model_config.get('model_name', model_name),
            'endpoint': model_config.get('api_endpoint', ''),
            'has_api_key': has_key
        })

    return models


if __name__ == "__main__":
    # 测试代码
    print("=== LLM客户端测试 ===")

    # 测试GPT-4o-mini
    try:
        client = create_llm_client("gpt-4o-mini")
        print(f"创建客户端: {client.get_model_info()}")

        validation = client.validate_config()
        print(f"配置验证: {validation}")

    except Exception as e:
        print(f"测试失败: {e}")

    # 列出所有可用模型
    print(f"\n可用模型: {get_available_models()}")