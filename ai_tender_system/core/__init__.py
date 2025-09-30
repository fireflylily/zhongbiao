#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统核心模块
Core functionality package for AI Tender System
"""

from .storage_service import storage_service, FileStorageService, FileMetadata

__all__ = [
    'storage_service',
    'FileStorageService',
    'FileMetadata'
]