"""
自动标书生成系统
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "自动化标书生成系统，支持招标文件解析、产品功能匹配和技术方案生成"

from .main import TenderGenerator

__all__ = ['TenderGenerator']