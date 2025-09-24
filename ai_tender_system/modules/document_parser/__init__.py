#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析引擎模块
提供多格式文档的智能解析和内容提取功能
"""

from .parser_manager import ParserManager
from .pdf_parser import PDFParser
from .word_parser import WordParser
from .text_splitter import IntelligentTextSplitter
from .content_cleaner import ContentCleaner

__all__ = [
    'ParserManager',
    'PDFParser',
    'WordParser',
    'IntelligentTextSplitter',
    'ContentCleaner'
]

__version__ = "1.0.0"
__author__ = "AI标书系统开发团队"