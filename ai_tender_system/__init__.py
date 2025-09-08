# -*- coding: utf-8 -*-
"""
AI标书系统
统一的招标文档处理平台
"""

__version__ = "2.0.0"
__author__ = "AI标书系统"

# 导入主要组件
from .common.config import get_config
from .common.llm_client import get_llm_client, chat
from .common.document_processor import process_document
from .common.logger import setup_logging, get_logger

# 导入业务模块
from .modules.tender_info import TenderInfoExtractor, TenderInfo

# 导入Web应用
from .web.app import create_app

__all__ = [
    'get_config',
    'get_llm_client', 
    'chat',
    'process_document',
    'setup_logging',
    'get_logger',
    'TenderInfoExtractor',
    'TenderInfo',
    'create_app'
]