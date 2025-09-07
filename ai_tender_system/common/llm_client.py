# -*- coding: utf-8 -*-
"""
统一LLM客户端模块
整合所有LLM调用逻辑，消除代码重复
"""

import json
import requests
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .config import get_config, LLMConfig
from .exceptions import LLMError, APIError, TimeoutError


@dataclass
class LLMMessage:
    """LLM消息结构"""
    role: str  # system, user, assistant
    content: str


@dataclass 
class LLMRequest:
    """LLM请求结构"""
    messages: List[LLMMessage]
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False


@dataclass
class LLMResponse:
    """LLM响应结构"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    raw_response: Dict[str, Any]


class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """聊天补全接口"""
        pass
    
    def simple_chat(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """简化的聊天接口"""
        messages = []
        
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        
        messages.append(LLMMessage(role="user", content=prompt))
        
        request = LLMRequest(
            messages=messages,
            model=kwargs.get('model', self.config.model),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            temperature=kwargs.get('temperature', 0.3)
        )
        
        response = self.chat_completion(request)
        return response.content


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI兼容的LLM客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })
    
    def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """执行聊天补全请求"""
        # 构建请求payload
        payload = {
            "model": request.model or self.config.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "stream": request.stream
        }
        
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        
        # 执行请求，带重试机制
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"LLM请求开始 (尝试 {attempt + 1}/{self.config.max_retries})")
                self.logger.debug(f"请求payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                
                start_time = time.time()
                response = self.session.post(
                    self.config.base_url,
                    json=payload,
                    timeout=self.config.timeout
                )
                elapsed_time = time.time() - start_time
                
                self.logger.info(f"API响应状态: {response.status_code}, 耗时: {elapsed_time:.2f}s")
                
                # 处理HTTP错误
                if response.status_code != 200:
                    error_msg = f"API请求失败: HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"
                    
                    self.logger.error(error_msg)
                    
                    if attempt == self.config.max_retries - 1:
                        raise APIError(error_msg)
                    
                    # 根据错误码决定是否重试
                    if response.status_code in [429, 500, 502, 503, 504]:
                        wait_time = (attempt + 1) * 2
                        self.logger.info(f"服务器错误，{wait_time}秒后重试")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise APIError(error_msg)
                
                # 解析响应
                try:
                    result = response.json()
                    self.logger.debug(f"原始响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    # 提取响应内容
                    if "choices" not in result or not result["choices"]:
                        raise APIError("API响应格式错误: 缺少choices字段")
                    
                    choice = result["choices"][0]
                    content = choice.get("message", {}).get("content", "").strip()
                    
                    if not content:
                        if attempt < self.config.max_retries - 1:
                            self.logger.warning("API返回空内容，重试中...")
                            time.sleep(1)
                            continue
                        else:
                            raise APIError("API返回空内容")
                    
                    # 构建响应对象
                    llm_response = LLMResponse(
                        content=content,
                        model=result.get("model", payload["model"]),
                        usage=result.get("usage", {}),
                        finish_reason=choice.get("finish_reason", "unknown"),
                        raw_response=result
                    )
                    
                    self.logger.info(f"LLM请求成功，响应长度: {len(content)}")
                    return llm_response
                    
                except json.JSONDecodeError as e:
                    error_msg = f"API响应JSON解析失败: {e}"
                    self.logger.error(error_msg)
                    if attempt == self.config.max_retries - 1:
                        raise APIError(error_msg)
                
            except requests.exceptions.Timeout:
                error_msg = f"API请求超时 (>{self.config.timeout}s)"
                self.logger.error(error_msg)
                if attempt == self.config.max_retries - 1:
                    raise TimeoutError(error_msg)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"API请求异常: {e}"
                self.logger.error(error_msg)
                if attempt == self.config.max_retries - 1:
                    raise APIError(error_msg)
                
            except Exception as e:
                error_msg = f"未知错误: {e}"
                self.logger.error(error_msg)
                if attempt == self.config.max_retries - 1:
                    raise LLMError(error_msg)
            
            # 重试前等待
            if attempt < self.config.max_retries - 1:
                wait_time = (attempt + 1) * 2
                self.logger.info(f"{wait_time}秒后进行第{attempt + 2}次重试...")
                time.sleep(wait_time)
        
        raise LLMError("所有重试都失败了")


class LLMClientFactory:
    """LLM客户端工厂"""
    
    @staticmethod
    def create_client(client_type: str = "openai_compatible") -> BaseLLMClient:
        """创建LLM客户端实例"""
        config = get_config()
        
        if not config.validate():
            raise ValueError("配置验证失败")
        
        if client_type == "openai_compatible":
            return OpenAICompatibleClient(config.llm)
        else:
            raise ValueError(f"不支持的客户端类型: {client_type}")


# 全局客户端实例（单例模式）
_default_client = None


def get_llm_client() -> BaseLLMClient:
    """获取默认LLM客户端实例"""
    global _default_client
    if _default_client is None:
        _default_client = LLMClientFactory.create_client()
    return _default_client


def reload_llm_client() -> BaseLLMClient:
    """重新加载LLM客户端"""
    global _default_client
    _default_client = LLMClientFactory.create_client()
    return _default_client


# 便捷函数
def chat(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
    """便捷的聊天函数"""
    client = get_llm_client()
    return client.simple_chat(prompt, system_prompt, **kwargs)


def chat_with_context(messages: List[Dict[str, str]], **kwargs) -> str:
    """带上下文的聊天函数"""
    client = get_llm_client()
    
    llm_messages = [LLMMessage(role=msg["role"], content=msg["content"]) 
                    for msg in messages]
    
    request = LLMRequest(
        messages=llm_messages,
        **kwargs
    )
    
    response = client.chat_completion(request)
    return response.content


if __name__ == "__main__":
    # 测试LLM客户端
    import sys
    import os
    
    # 检查是否设置了API密钥
    if not os.getenv('SHIHUANG_API_KEY'):
        print("请设置环境变量 SHIHUANG_API_KEY")
        sys.exit(1)
    
    try:
        # 测试简单聊天
        print("测试LLM客户端...")
        result = chat("你好，请简单介绍一下你自己。")
        print(f"响应: {result}")
        print("✅ LLM客户端测试成功")
        
    except Exception as e:
        print(f"❌ LLM客户端测试失败: {e}")
        sys.exit(1)