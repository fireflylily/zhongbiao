#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一异常处理模块
"""

class AITenderSystemError(Exception):
    """AI标书系统基础异常类"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "SYSTEM_ERROR"
        self.details = details or {}

class ConfigurationError(AITenderSystemError):
    """配置错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CONFIG_ERROR", details)

class APIError(AITenderSystemError):
    """API调用错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "API_ERROR", details)

class FileProcessingError(AITenderSystemError):
    """文件处理错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "FILE_ERROR", details)

class DocumentProcessingError(AITenderSystemError):
    """文档处理错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DOCUMENT_ERROR", details)

class TenderInfoExtractionError(AITenderSystemError):
    """招标信息提取错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "TENDER_EXTRACTION_ERROR", details)

class BusinessResponseError(AITenderSystemError):
    """商务应答处理错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "BUSINESS_RESPONSE_ERROR", details)

class TechProposalError(AITenderSystemError):
    """技术方案生成错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "TECH_PROPOSAL_ERROR", details)

class ValidationError(AITenderSystemError):
    """数据验证错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)

def format_error_response(error: Exception) -> dict:
    """格式化错误响应"""
    if isinstance(error, AITenderSystemError):
        return {
            'success': False,
            'error': {
                'code': error.error_code,
                'message': error.message,
                'details': error.details
            }
        }
    else:
        return {
            'success': False,
            'error': {
                'code': 'UNKNOWN_ERROR',
                'message': str(error),
                'details': {}
            }
        }

def handle_api_error(func):
    """API错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AITenderSystemError as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(e)
    return wrapper