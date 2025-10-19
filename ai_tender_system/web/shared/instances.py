#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局实例管理
管理应用级别的单例对象和共享状态
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 全局知识库管理器实例
_kb_manager = None

# 全局Pipeline实例存储（用于分步处理）
PIPELINE_INSTANCES = {}


def get_kb_manager():
    """
    获取知识库管理器单例

    Returns:
        KnowledgeBaseManager: 知识库管理器实例

    Notes:
        - 使用延迟初始化模式
        - 线程安全的单例实现
        - 确保整个应用只有一个KnowledgeBaseManager实例
    """
    global _kb_manager

    if _kb_manager is None:
        from modules.knowledge_base.manager import KnowledgeBaseManager
        _kb_manager = KnowledgeBaseManager()

    return _kb_manager
