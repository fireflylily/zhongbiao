#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本嵌入服务
支持多种向量化模型和批量处理
"""

import asyncio
import numpy as np
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import time

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("vector_engine.embedding")

# 延迟导入以避免启动时加载
_sentence_transformers = None
_torch = None

def get_sentence_transformers():
    global _sentence_transformers
    if _sentence_transformers is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformers = SentenceTransformer
        except ImportError:
            raise ImportError("需要安装sentence-transformers: pip install sentence-transformers")
    return _sentence_transformers

def get_torch():
    global _torch
    if _torch is None:
        try:
            import torch
            _torch = torch
        except ImportError:
            logger.warning("未安装PyTorch，将使用CPU模式")
            _torch = None
    return _torch


@dataclass
class EmbeddingResult:
    """嵌入结果数据类"""
    vectors: np.ndarray
    processing_time: float
    model_used: str
    text_count: int
    dimensions: int


class EmbeddingService:
    """文本嵌入服务"""

    # 支持的模型配置
    SUPPORTED_MODELS = {
        "chinese": {
            "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "dimensions": 384,
            "description": "多语言模型，支持中文"
        },
        "chinese-large": {
            "model_name": "sentence-transformers/distiluse-base-multilingual-cased",
            "dimensions": 512,
            "description": "大型多语言模型，更高精度"
        },
        "english": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "dimensions": 384,
            "description": "英文专用轻量模型"
        }
    }

    def __init__(self, model_type: str = "chinese", cache_dir: Optional[str] = None):
        self.logger = logger
        self.model_type = model_type
        self.model_config = self.SUPPORTED_MODELS.get(model_type)

        if not self.model_config:
            raise ValueError(f"不支持的模型类型: {model_type}, 支持的类型: {list(self.SUPPORTED_MODELS.keys())}")

        self.cache_dir = cache_dir
        self.model = None
        self.device = "cpu"  # 默认使用CPU

        # 性能统计
        self.stats = {
            "total_embeddings": 0,
            "total_tokens": 0,
            "avg_processing_time": 0.0,
            "model_load_time": 0.0
        }

    async def initialize(self) -> bool:
        """初始化嵌入服务"""
        try:
            self.logger.info(f"初始化嵌入服务: model_type={self.model_type}")
            start_time = time.time()

            # 在线程池中加载模型，避免阻塞
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(None, self._load_model)

            load_time = time.time() - start_time
            self.stats["model_load_time"] = load_time

            # 检测设备
            torch = get_torch()
            if torch and torch.cuda.is_available():
                self.device = "cuda"
                self.logger.info("使用GPU加速")
            else:
                self.device = "cpu"
                self.logger.info("使用CPU模式")

            self.logger.info(f"嵌入服务初始化完成: model={self.model_config['model_name']}, "
                           f"device={self.device}, load_time={load_time:.2f}s")

            return True

        except Exception as e:
            self.logger.error(f"嵌入服务初始化失败: {e}")
            return False

    def _load_model(self):
        """加载嵌入模型"""
        SentenceTransformer = get_sentence_transformers()

        model = SentenceTransformer(
            self.model_config["model_name"],
            cache_folder=self.cache_dir
        )

        return model

    async def embed_texts(self, texts: List[str], batch_size: int = 32) -> EmbeddingResult:
        """
        批量文本嵌入

        Args:
            texts: 待嵌入的文本列表
            batch_size: 批处理大小

        Returns:
            EmbeddingResult: 嵌入结果
        """
        if not self.model:
            raise RuntimeError("嵌入服务未初始化，请先调用initialize()")

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
            loop = asyncio.get_event_loop()
            if len(processed_texts) <= batch_size:
                # 单批处理
                vectors = await loop.run_in_executor(
                    None, self._embed_batch, processed_texts
                )
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

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """单批嵌入"""
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    async def _embed_large_batch(self, texts: List[str], batch_size: int) -> np.ndarray:
        """大批量分批嵌入"""
        all_vectors = []
        loop = asyncio.get_event_loop()

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_vectors = await loop.run_in_executor(
                None, self._embed_batch, batch
            )
            all_vectors.append(batch_vectors)

            # 记录进度
            progress = (i + len(batch)) / len(texts) * 100
            self.logger.info(f"嵌入进度: {progress:.1f}% ({i + len(batch)}/{len(texts)})")

        return np.vstack(all_vectors) if all_vectors else np.array([])

    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """预处理文本"""
        processed = []

        for text in texts:
            if not text or not text.strip():
                processed.append("")
                continue

            # 清理和规范化
            cleaned = text.strip()

            # 长度限制（避免超长文本影响性能）
            max_length = 8192  # 模型通常支持的最大长度
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
            "device": self.device,
            "stats": self.stats.copy(),
            "is_initialized": self.model is not None
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
        # 确保向量是规范化的
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)

        return np.dot(vec1_norm, vec2_norm)

    async def cleanup(self):
        """清理资源"""
        if self.model:
            # 清理GPU内存
            torch = get_torch()
            if torch and torch.cuda.is_available():
                torch.cuda.empty_cache()

            self.model = None
            self.logger.info("嵌入服务资源已清理")