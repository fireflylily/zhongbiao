# -*- coding: utf-8 -*-
"""
自定义异常类
统一异常处理机制
"""


class AITenderSystemError(Exception):
    """AI标书系统基础异常类"""
    pass


class ConfigError(AITenderSystemError):
    """配置相关异常"""
    pass


class LLMError(AITenderSystemError):
    """LLM相关异常"""
    pass


class APIError(LLMError):
    """API调用异常"""
    pass


class TimeoutError(APIError):
    """请求超时异常"""
    pass


class DocumentError(AITenderSystemError):
    """文档处理异常"""
    pass


class DocumentFormatError(DocumentError):
    """文档格式异常"""
    pass


class DocumentParsingError(DocumentError):
    """文档解析异常"""
    pass


class ValidationError(AITenderSystemError):
    """数据验证异常"""
    pass


class BusinessLogicError(AITenderSystemError):
    """业务逻辑异常"""
    pass