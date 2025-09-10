#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统公共模块
"""

from .config import get_config, Config
from .logger import setup_logging, get_module_logger
from .exceptions import (
    AITenderSystemError, ConfigurationError, APIError, 
    FileProcessingError, DocumentProcessingError,
    TenderInfoExtractionError, BusinessResponseError, 
    TechProposalError, ValidationError,
    format_error_response, handle_api_error
)
from .utils import (
    generate_timestamp, generate_file_hash, safe_filename,
    allowed_file, ensure_dir, cleanup_temp_files, create_temp_copy,
    format_file_size, validate_file_type, extract_text_preview,
    merge_configs, sanitize_json_value, batch_process_files
)

__all__ = [
    # 配置
    'get_config', 'Config',
    # 日志
    'setup_logging', 'get_module_logger',
    # 异常
    'AITenderSystemError', 'ConfigurationError', 'APIError',
    'FileProcessingError', 'DocumentProcessingError',
    'TenderInfoExtractionError', 'BusinessResponseError',
    'TechProposalError', 'ValidationError',
    'format_error_response', 'handle_api_error',
    # 工具
    'generate_timestamp', 'generate_file_hash', 'safe_filename',
    'allowed_file', 'ensure_dir', 'cleanup_temp_files', 'create_temp_copy',
    'format_file_size', 'validate_file_type', 'extract_text_preview',
    'merge_configs', 'sanitize_json_value', 'batch_process_files'
]