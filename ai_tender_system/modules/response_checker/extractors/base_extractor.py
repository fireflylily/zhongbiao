#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    信息提取器基类
    """

    def __init__(self, llm_client=None):
        """
        初始化提取器

        Args:
            llm_client: LLM客户端实例（可选）
        """
        self.llm = llm_client

    @abstractmethod
    def extract(self, content: Any) -> Dict[str, Any]:
        """
        提取信息

        Args:
            content: 输入内容（文本或图片）

        Returns:
            提取结果字典
        """
        pass

    def _safe_extract(self, func, *args, **kwargs) -> Optional[Any]:
        """
        安全执行提取，捕获异常

        Args:
            func: 提取函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            提取结果或None
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"提取失败: {e}")
            return None
