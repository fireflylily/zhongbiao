#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统公共模块
"""

from .config import get_config, Config
from .logger import setup_logging, get_module_logger
from .llm_client import LLMClient
from .prompt_manager import get_prompt_manager, PromptManager, get_prompt, reload_prompts
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
from .constants import (
    # 导入常用常量
    BYTES_PER_KB, BYTES_PER_MB, BYTES_PER_GB,
    MAX_FILE_SIZE_BYTES, DEFAULT_CHUNK_READ_SIZE,
    DEFAULT_PAGE_SIZE, PROGRESS_COMPLETE, PROGRESS_HALF_COMPLETE,
    HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_SERVER_ERROR,
    STATUS_PENDING, STATUS_COMPLETED, STATUS_FAILED,
    PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW
)

__all__ = [
    # 配置
    'get_config', 'Config',
    # 日志
    'setup_logging', 'get_module_logger',
    # LLM客户端
    'LLMClient',
    # 提示词管理
    'get_prompt_manager', 'PromptManager', 'get_prompt', 'reload_prompts',
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
    'merge_configs', 'sanitize_json_value', 'batch_process_files',
    # 常量
    'BYTES_PER_KB', 'BYTES_PER_MB', 'BYTES_PER_GB',
    'MAX_FILE_SIZE_BYTES', 'DEFAULT_CHUNK_READ_SIZE',
    'DEFAULT_PAGE_SIZE', 'PROGRESS_COMPLETE', 'PROGRESS_HALF_COMPLETE',
    'HTTP_OK', 'HTTP_BAD_REQUEST', 'HTTP_NOT_FOUND', 'HTTP_INTERNAL_SERVER_ERROR',
    'STATUS_PENDING', 'STATUS_COMPLETED', 'STATUS_FAILED',
    'PRIORITY_HIGH', 'PRIORITY_MEDIUM', 'PRIORITY_LOW'
]