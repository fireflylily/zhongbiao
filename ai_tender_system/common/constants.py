#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局常量定义
包含系统中使用的所有魔术数字和固定配置值
"""

# ===================
# 文件大小相关常量
# ===================

# 字节单位
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

# 文件大小限制
MAX_FILE_SIZE_BYTES = 100 * BYTES_PER_MB  # 100MB
MAX_CHUNK_SIZE_BYTES = 10 * BYTES_PER_MB   # 10MB (用于文件分块处理)
DEFAULT_CHUNK_READ_SIZE = 4096             # 4KB (文件读取缓冲区)

# ===================
# 缓存相关常量
# ===================

# HTTP缓存时间 (秒)
CACHE_MAX_AGE_STATIC = 31536000  # 1年 (静态资源)
CACHE_MAX_AGE_ZERO = 0            # 不缓存

# ===================
# 分页相关常量
# ===================

DEFAULT_PAGE_SIZE = 20           # 默认每页条目数
MAX_PAGE_SIZE = 100              # 最大每页条目数
MIN_PAGE_SIZE = 1                # 最小每页条目数

# ===================
# 进度相关常量
# ===================

PROGRESS_NOT_STARTED = 0         # 未开始
PROGRESS_HALF_COMPLETE = 50      # 进行中 (50%)
PROGRESS_COMPLETE = 100          # 已完成

# ===================
# 超时和重试相关常量
# ===================

# 任务启动超时
TASK_START_TIMEOUT_SECONDS = 2.0      # 等待任务ID生成的超时时间
TASK_START_MAX_RETRIES = 20           # 最大重试次数 (每次0.1秒)
TASK_START_RETRY_INTERVAL = 0.1       # 重试间隔 (秒)

# 步骤执行超时
STEP_EXECUTION_TIMEOUT_SECONDS = 5.0  # 等待步骤完成的超时时间
STEP_EXECUTION_MAX_RETRIES = 50       # 最大重试次数 (每次0.1秒)
STEP_EXECUTION_RETRY_INTERVAL = 0.1   # 重试间隔 (秒)

# ===================
# AI模型相关常量
# ===================

# Token限制
DEFAULT_MAX_TOKENS = 4096             # 默认最大输出token数
MAX_COMPLETION_TOKENS = 4096          # 最大补全token数

# ===================
# 文本处理相关常量
# ===================

# 文本长度限制
DEFAULT_TEXT_PREVIEW_LENGTH = 200     # 默认预览文本长度
MAX_TEXT_LENGTH = 10000               # 最大文本长度

# ===================
# 数据库相关常量
# ===================

# 批量操作
DEFAULT_BATCH_SIZE = 100              # 默认批量操作大小
MAX_BATCH_SIZE = 1000                 # 最大批量操作大小

# ===================
# 状态码相关常量
# ===================

# HTTP状态码
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_REQUEST_TIMEOUT = 408
HTTP_PAYLOAD_TOO_LARGE = 413
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# ===================
# 文件类型相关常量
# ===================

# 允许的文档类型
ALLOWED_DOCUMENT_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt',
    'xls', 'xlsx', 'ppt', 'pptx'
}

# 允许的图片类型
ALLOWED_IMAGE_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'
}

# 允许的归档类型
ALLOWED_ARCHIVE_EXTENSIONS = {
    'zip', 'rar', '7z', 'tar', 'gz'
}

# ===================
# 日期时间格式
# ===================

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# ===================
# 优先级常量
# ===================

PRIORITY_HIGH = 'high'
PRIORITY_MEDIUM = 'medium'
PRIORITY_LOW = 'low'

# ===================
# 任务状态常量
# ===================

STATUS_PENDING = 'pending'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_COMPLETED = 'completed'
STATUS_FAILED = 'failed'
STATUS_CANCELLED = 'cancelled'

# ===================
# 步骤编号常量
# ===================

STEP_1 = 1  # 文档分块
STEP_2 = 2  # 需求提取
STEP_3 = 3  # 最终处理

# ===================
# 约束类型常量
# ===================

CONSTRAINT_MANDATORY = 'mandatory'    # 强制性要求
CONSTRAINT_OPTIONAL = 'optional'      # 可选要求
CONSTRAINT_PREFERRED = 'preferred'    # 优先要求

# ===================
# 类别常量
# ===================

CATEGORY_QUALIFICATION = 'qualification'  # 资质类别
CATEGORY_TECHNICAL = 'technical'          # 技术类别
CATEGORY_COMMERCIAL = 'commercial'        # 商务类别
CATEGORY_LEGAL = 'legal'                  # 法律类别


# ===================
# 导出所有常量
# ===================

__all__ = [
    # 文件大小
    'BYTES_PER_KB', 'BYTES_PER_MB', 'BYTES_PER_GB',
    'MAX_FILE_SIZE_BYTES', 'MAX_CHUNK_SIZE_BYTES', 'DEFAULT_CHUNK_READ_SIZE',

    # 缓存
    'CACHE_MAX_AGE_STATIC', 'CACHE_MAX_AGE_ZERO',

    # 分页
    'DEFAULT_PAGE_SIZE', 'MAX_PAGE_SIZE', 'MIN_PAGE_SIZE',

    # 进度
    'PROGRESS_NOT_STARTED', 'PROGRESS_HALF_COMPLETE', 'PROGRESS_COMPLETE',

    # 超时和重试
    'TASK_START_TIMEOUT_SECONDS', 'TASK_START_MAX_RETRIES', 'TASK_START_RETRY_INTERVAL',
    'STEP_EXECUTION_TIMEOUT_SECONDS', 'STEP_EXECUTION_MAX_RETRIES', 'STEP_EXECUTION_RETRY_INTERVAL',

    # AI模型
    'DEFAULT_MAX_TOKENS', 'MAX_COMPLETION_TOKENS',

    # 文本处理
    'DEFAULT_TEXT_PREVIEW_LENGTH', 'MAX_TEXT_LENGTH',

    # 数据库
    'DEFAULT_BATCH_SIZE', 'MAX_BATCH_SIZE',

    # HTTP状态码
    'HTTP_OK', 'HTTP_CREATED', 'HTTP_BAD_REQUEST', 'HTTP_UNAUTHORIZED',
    'HTTP_FORBIDDEN', 'HTTP_NOT_FOUND', 'HTTP_REQUEST_TIMEOUT',
    'HTTP_PAYLOAD_TOO_LARGE', 'HTTP_INTERNAL_SERVER_ERROR', 'HTTP_SERVICE_UNAVAILABLE',

    # 文件类型
    'ALLOWED_DOCUMENT_EXTENSIONS', 'ALLOWED_IMAGE_EXTENSIONS', 'ALLOWED_ARCHIVE_EXTENSIONS',

    # 日期时间
    'DATETIME_FORMAT', 'DATE_FORMAT', 'TIME_FORMAT', 'TIMESTAMP_FORMAT',

    # 优先级
    'PRIORITY_HIGH', 'PRIORITY_MEDIUM', 'PRIORITY_LOW',

    # 任务状态
    'STATUS_PENDING', 'STATUS_IN_PROGRESS', 'STATUS_COMPLETED', 'STATUS_FAILED', 'STATUS_CANCELLED',

    # 步骤
    'STEP_1', 'STEP_2', 'STEP_3',

    # 约束类型
    'CONSTRAINT_MANDATORY', 'CONSTRAINT_OPTIONAL', 'CONSTRAINT_PREFERRED',

    # 类别
    'CATEGORY_QUALIFICATION', 'CATEGORY_TECHNICAL', 'CATEGORY_COMMERCIAL', 'CATEGORY_LEGAL',
]
