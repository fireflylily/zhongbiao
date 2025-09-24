#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版嵌入服务
用于开发和测试阶段的文本向量化
"""

import asyncio
import numpy as np
from typing import List, Dict
from dataclasses import dataclass
import hashlib
import re

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("vector_engine.simple_embedding")


@dataclass
class SimpleEmbeddingResult:
    """简化嵌入结果"""
    vectors: np.ndarray
    processing_time: float
    model_used: str
    text_count: int
    dimensions: int


class SimpleEmbeddingService:
    """简化版嵌入服务（用于开发测试）"""

    def __init__(self, dimension: int = 100):
        self.logger = logger
        self.dimension = dimension
        self.is_initialized = False

        # 词汇表（简单的中文和英文关键词）
        self.vocabulary = {
            # 招标相关
            '招标': 0, '投标': 1, '采购': 2, '供应商': 3, '合同': 4,
            '方案': 5, '技术': 6, '价格': 7, '服务': 8, '质量': 9,

            # 技术相关
            '人工智能': 10, 'AI': 11, '算法': 12, '系统': 13, '平台': 14,
            '数据': 15, '分析': 16, '管理': 17, '评估': 18, '预测': 19,

            # 文档类型
            '文档': 20, '规范': 21, '要求': 22, '标准': 23, '流程': 24,
            '安全': 25, '加密': 26, '认证': 27, '控制': 28, '保护': 29,

            # 英文关键词
            'tender': 30, 'bid': 31, 'procurement': 32, 'supplier': 33,
            'contract': 34, 'solution': 35, 'technology': 36, 'price': 37,
            'service': 38, 'quality': 39, 'system': 40, 'platform': 41,
            'data': 42, 'analysis': 43, 'management': 44, 'security': 45
        }

    async def initialize(self) -> bool:
        """初始化服务"""
        try:
            self.logger.info("初始化简化版嵌入服务")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False

    async def embed_texts(self, texts: List[str]) -> SimpleEmbeddingResult:
        """文本嵌入"""
        if not self.is_initialized:
            raise RuntimeError("服务未初始化")

        vectors = []
        for text in texts:
            vector = self._text_to_vector(text)
            vectors.append(vector)

        return SimpleEmbeddingResult(
            vectors=np.array(vectors),
            processing_time=0.1,
            model_used="simple",
            text_count=len(texts),
            dimensions=self.dimension
        )

    async def embed_query(self, query: str) -> np.ndarray:
        """查询嵌入"""
        result = await self.embed_texts([query])
        return result.vectors[0]

    def _text_to_vector(self, text: str) -> np.ndarray:
        """将文本转换为向量"""
        vector = np.zeros(self.dimension)

        # 基于词汇匹配的简单向量化
        words = self._extract_words(text)

        for word in words:
            if word in self.vocabulary:
                idx = self.vocabulary[word]
                if idx < self.dimension:
                    vector[idx] = 1.0

        # 添加基于字符的哈希特征
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        for i in range(min(10, self.dimension - 46)):
            if (text_hash >> i) & 1:
                vector[46 + i] = 0.5

        # 文本长度特征
        if len(vector) > 56:
            vector[56] = min(len(text) / 1000.0, 1.0)

        # 标准化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def _extract_words(self, text: str) -> List[str]:
        """提取文本中的关键词"""
        words = []

        # 中文分词（简单的基于字典匹配）
        for word in self.vocabulary.keys():
            if word in text:
                words.append(word)

        # 英文单词
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        words.extend(english_words)

        return words

    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "model_type": "simple",
            "model_name": "simple-embedding",
            "dimensions": self.dimension,
            "description": "简化版嵌入服务，用于开发测试",
            "device": "cpu",
            "is_initialized": self.is_initialized
        }

    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8))

    async def cleanup(self):
        """清理资源"""
        self.is_initialized = False
        self.logger.info("简化版嵌入服务已清理")