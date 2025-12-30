#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本嵌入服务 - API版本
使用OpenAI Embeddings API代替本地模型
"""

import asyncio
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import os

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.config import clean_env_value
import requests

logger = get_module_logger("vector_engine.embedding")


@dataclass
class EmbeddingResult:
    """嵌入结果数据类"""
    vectors: np.ndarray
    processing_time: float
    model_used: str
    text_count: int
    dimensions: int


class EmbeddingService:
    """文本嵌入服务 - 支持OpenAI和通义千问API"""

    # 支持的模型配置
    SUPPORTED_MODELS = {
        "text-embedding-3-small": {
            "model_name": "text-embedding-3-small",
            "dimensions": 1536,
            "description": "OpenAI最新小型嵌入模型,性价比高",
            "provider": "openai"
        },
        "text-embedding-3-large": {
            "model_name": "text-embedding-3-large",
            "dimensions": 3072,
            "description": "OpenAI大型嵌入模型,精度更高",
            "provider": "openai"
        },
        "text-embedding-ada-002": {
            "model_name": "text-embedding-ada-002",
            "dimensions": 1536,
            "description": "OpenAI经典嵌入模型",
            "provider": "openai"
        },
        # 通义千问 Embedding 模型
        "text-embedding-v3": {
            "model_name": "text-embedding-v3",
            "dimensions": 1024,
            "description": "通义千问最新嵌入模型,中文效果优秀",
            "provider": "dashscope"
        },
        "text-embedding-v2": {
            "model_name": "text-embedding-v2",
            "dimensions": 1536,
            "description": "通义千问嵌入模型v2",
            "provider": "dashscope"
        }
    }

    def __init__(self, model_type: str = None, api_key: Optional[str] = None,
                 api_endpoint: Optional[str] = None, **kwargs):
        self.logger = logger

        # 从环境变量读取默认模型类型
        default_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
        self.model_type = model_type or default_model
        self.model_config = self.SUPPORTED_MODELS.get(self.model_type)

        if not self.model_config:
            # 兼容旧配置,默认使用text-embedding-v3(通义千问)
            self.logger.warning(f"模型类型 {self.model_type} 不支持,使用默认模型 text-embedding-v3")
            self.model_type = "text-embedding-v3"
            self.model_config = self.SUPPORTED_MODELS[self.model_type]

        # 根据模型提供商选择API配置
        provider = self.model_config.get("provider", "openai")

        if provider == "dashscope":
            # 通义千问 DashScope API
            self.api_key = clean_env_value(api_key or os.getenv("DASHSCOPE_API_KEY") or "")
            base_url = clean_env_value(api_endpoint or os.getenv("DASHSCOPE_EMBEDDING_ENDPOINT") or "https://dashscope.aliyuncs.com/compatible-mode/v1")
        else:
            # OpenAI 兼容 API
            self.api_key = clean_env_value(api_key or os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY") or "")
            base_url = clean_env_value(api_endpoint or os.getenv("EMBEDDING_API_ENDPOINT") or os.getenv("OPENAI_API_ENDPOINT") or "https://api.openai.com/v1")

        # 确保endpoint正确格式 - 移除 /chat/completions 后缀（如果有）
        base_url = base_url.rstrip("/")
        if base_url.endswith("/chat/completions"):
            base_url = base_url[:-len("/chat/completions")]

        # 添加 /embeddings 后缀
        if not base_url.endswith("/embeddings"):
            self.api_endpoint = base_url + "/embeddings"
        else:
            self.api_endpoint = base_url

        self.timeout = int(os.getenv("EMBEDDING_API_TIMEOUT", "30"))
        self.provider = provider
        self.initialized = False

        # 性能统计
        self.stats = {
            "total_embeddings": 0,
            "total_tokens": 0,
            "avg_processing_time": 0.0,
            "api_calls": 0
        }

    async def initialize(self) -> bool:
        """初始化嵌入服务"""
        try:
            if not self.api_key:
                raise ValueError("未配置EMBEDDING_API_KEY或OPENAI_API_KEY环境变量")

            self.logger.info(f"初始化嵌入服务: model={self.model_type}, endpoint={self.api_endpoint}")

            # 测试API连接
            test_result = await self.embed_texts(["测试"], batch_size=1)
            if test_result.vectors.shape[0] > 0:
                self.initialized = True
                self.logger.info(f"嵌入服务初始化成功: dimensions={test_result.dimensions}")
                return True
            else:
                raise RuntimeError("API测试失败")

        except Exception as e:
            self.logger.error(f"嵌入服务初始化失败: {e}")
            return False

    async def embed_texts(self, texts: List[str], batch_size: int = 100) -> EmbeddingResult:
        """
        批量文本嵌入

        Args:
            texts: 待嵌入的文本列表
            batch_size: 批处理大小(OpenAI API最大支持2048个文本)

        Returns:
            EmbeddingResult: 嵌入结果
        """
        if not texts:
            return EmbeddingResult(
                vectors=np.array([]),
                processing_time=0.0,
                model_used=self.model_type,
                text_count=0,
                dimensions=0
            )

        self.logger.info(f"开始文本嵌入: texts={len(texts)}, batch_size={batch_size}")
        start_time = time.time()

        try:
            # 预处理文本
            processed_texts = self._preprocess_texts(texts)

            # 批量处理
            if len(processed_texts) <= batch_size:
                # 单批处理
                vectors = await self._embed_batch(processed_texts)
            else:
                # 多批处理
                vectors = await self._embed_large_batch(processed_texts, batch_size)

            processing_time = time.time() - start_time

            # 更新统计信息
            self._update_stats(len(texts), processing_time)

            result = EmbeddingResult(
                vectors=vectors,
                processing_time=processing_time,
                model_used=self.model_type,
                text_count=len(texts),
                dimensions=vectors.shape[1] if len(vectors) > 0 else 0
            )

            self.logger.info(f"文本嵌入完成: vectors_shape={vectors.shape}, "
                           f"time={processing_time:.2f}s")

            return result

        except Exception as e:
            self.logger.error(f"文本嵌入失败: {e}")
            raise

    async def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """单批嵌入 - 调用API"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._call_embedding_api, texts)

    def _call_embedding_api(self, texts: List[str]) -> np.ndarray:
        """调用OpenAI Embeddings API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_config["model_name"],
            "input": texts
        }

        try:
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # 提取向量
            embeddings = []
            for item in sorted(data["data"], key=lambda x: x["index"]):
                embeddings.append(item["embedding"])

            self.stats["api_calls"] += 1

            return np.array(embeddings, dtype=np.float32)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API调用失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"响应内容: {e.response.text}")
            raise

    async def _embed_large_batch(self, texts: List[str], batch_size: int) -> np.ndarray:
        """大批量分批嵌入"""
        all_vectors = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_vectors = await self._embed_batch(batch)
            all_vectors.append(batch_vectors)

            # 记录进度
            progress = (i + len(batch)) / len(texts) * 100
            self.logger.info(f"嵌入进度: {progress:.1f}% ({i + len(batch)}/{len(texts)})")

            # 短暂延迟避免API速率限制
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)

        return np.vstack(all_vectors) if all_vectors else np.array([])

    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """预处理文本"""
        processed = []

        for text in texts:
            if not text or not text.strip():
                processed.append(" ")  # API不接受空字符串
                continue

            # 清理和规范化
            cleaned = text.strip()

            # 长度限制 - OpenAI模型通常支持8191 tokens
            max_length = 8000  # 保守估计,1个字符≈1个token
            if len(cleaned) > max_length:
                cleaned = cleaned[:max_length]
                self.logger.warning(f"文本被截断: 原长度={len(text)}, 新长度={max_length}")

            processed.append(cleaned)

        return processed

    def _update_stats(self, text_count: int, processing_time: float):
        """更新性能统计"""
        self.stats["total_embeddings"] += text_count
        self.stats["total_tokens"] += text_count  # 简化计算

        # 更新平均处理时间
        if self.stats["total_embeddings"] > 0:
            total_time = (self.stats["avg_processing_time"] *
                         (self.stats["total_embeddings"] - text_count) + processing_time)
            self.stats["avg_processing_time"] = total_time / self.stats["total_embeddings"]

    async def embed_query(self, query: str) -> np.ndarray:
        """
        单个查询嵌入

        Args:
            query: 查询文本

        Returns:
            np.ndarray: 查询向量
        """
        result = await self.embed_texts([query])
        return result.vectors[0] if len(result.vectors) > 0 else np.array([])

    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "model_type": self.model_type,
            "model_name": self.model_config["model_name"],
            "dimensions": self.model_config["dimensions"],
            "description": self.model_config["description"],
            "provider": self.provider,
            "api_endpoint": self.api_endpoint,
            "stats": self.stats.copy(),
            "is_initialized": self.initialized
        }

    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            float: 余弦相似度 (-1到1)
        """
        # OpenAI的embedding已经是规范化的,可以直接点积
        return float(np.dot(vec1, vec2))

    async def cleanup(self):
        """清理资源"""
        self.logger.info("嵌入服务资源已清理")
        self.initialized = False
