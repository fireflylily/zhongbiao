#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档结构解析器接口和工厂类

提供多种解析器实现的统一接口,支持策略切换和A/B测试
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ParserMetrics:
    """解析器性能指标"""
    parser_name: str              # 解析器名称
    parse_time: float             # 解析耗时(秒)
    chapters_found: int           # 识别的章节数
    success: bool                 # 是否成功
    error_message: str = ""       # 错误信息
    confidence_score: float = 0.0 # 置信度分数(0-100)
    api_cost: float = 0.0         # API调用成本(元)


class BaseStructureParser(ABC):
    """文档结构解析器基类

    所有解析器必须继承此类并实现parse_structure方法
    """

    def __init__(self):
        self.parser_name = self.__class__.__name__

    @abstractmethod
    def parse_structure(self, doc_path: str) -> Dict:
        """解析文档结构

        Args:
            doc_path: Word文档路径

        Returns:
            {
                "success": True/False,
                "chapters": [ChapterNode.to_dict(), ...],
                "statistics": {...},
                "metrics": ParserMetrics,
                "error": "错误信息(如果失败)"
            }
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查解析器是否可用

        Returns:
            True: 解析器已配置且可用
            False: 缺少依赖或配置
        """
        pass

    def get_parser_info(self) -> Dict:
        """获取解析器信息

        Returns:
            {
                "name": "解析器名称",
                "display_name": "显示名称",
                "description": "功能描述",
                "requires_api": True/False,
                "cost_per_page": 0.01,
                "available": True/False
            }
        """
        return {
            "name": self.parser_name,
            "display_name": self.parser_name,
            "description": "基础解析器",
            "requires_api": False,
            "cost_per_page": 0.0,
            "available": self.is_available()
        }


class ParserFactory:
    """解析器工厂类

    负责创建和管理所有解析器实例
    """

    _parsers = {}  # 已注册的解析器类

    @classmethod
    def register_parser(cls, parser_name: str, parser_class):
        """注册解析器

        Args:
            parser_name: 解析器标识名称
            parser_class: 解析器类
        """
        cls._parsers[parser_name] = parser_class

    @classmethod
    def create_parser(cls, parser_name: str) -> BaseStructureParser:
        """创建解析器实例

        Args:
            parser_name: 解析器名称

        Returns:
            解析器实例

        Raises:
            ValueError: 解析器不存在
        """
        if parser_name not in cls._parsers:
            raise ValueError(f"解析器 '{parser_name}' 未注册")

        return cls._parsers[parser_name]()

    @classmethod
    def get_available_parsers(cls) -> List[Dict]:
        """获取所有可用的解析器列表

        Returns:
            [
                {
                    "name": "builtin",
                    "display_name": "内置解析器",
                    "description": "...",
                    "available": True
                },
                ...
            ]
        """
        parsers = []
        for parser_name, parser_class in cls._parsers.items():
            parser = parser_class()
            info = parser.get_parser_info()
            info['name'] = parser_name
            parsers.append(info)

        return parsers


# 导出
__all__ = [
    'BaseStructureParser',
    'ParserFactory',
    'ParserMetrics'
]
