#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局实例管理
管理应用级别的单例对象和共享状态
"""

import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 全局知识库管理器实例
_kb_manager = None

# 全局Pipeline实例存储（用于分步处理）
# 格式: {task_id: {'instance': pipeline, 'timestamp': time.time()}}
_PIPELINE_INSTANCES = {}
_PIPELINE_LOCK = threading.Lock()
_PIPELINE_TTL = 3600  # TTL: 1小时


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


# ===================
# Pipeline实例管理（线程安全）
# ===================

def set_pipeline_instance(task_id: str, pipeline: Any) -> None:
    """
    存储Pipeline实例（线程安全）

    Args:
        task_id: 任务ID
        pipeline: Pipeline实例

    Notes:
        - 使用锁保证线程安全
        - 自动记录时间戳用于TTL清理
    """
    with _PIPELINE_LOCK:
        _PIPELINE_INSTANCES[task_id] = {
            'instance': pipeline,
            'timestamp': time.time()
        }


def get_pipeline_instance(task_id: str) -> Optional[Any]:
    """
    获取Pipeline实例（线程安全）

    Args:
        task_id: 任务ID

    Returns:
        Pipeline实例，如果不存在或已过期返回None

    Notes:
        - 使用锁保证线程安全
        - 自动检查TTL，过期自动删除
    """
    with _PIPELINE_LOCK:
        if task_id not in _PIPELINE_INSTANCES:
            return None

        entry = _PIPELINE_INSTANCES[task_id]
        current_time = time.time()

        # 检查是否过期
        if current_time - entry['timestamp'] > _PIPELINE_TTL:
            # 过期，删除并返回None
            del _PIPELINE_INSTANCES[task_id]
            return None

        # 更新访问时间戳（延长TTL）
        entry['timestamp'] = current_time
        return entry['instance']


def remove_pipeline_instance(task_id: str) -> bool:
    """
    删除Pipeline实例（线程安全）

    Args:
        task_id: 任务ID

    Returns:
        bool: 是否成功删除

    Notes:
        - 使用锁保证线程安全
    """
    with _PIPELINE_LOCK:
        if task_id in _PIPELINE_INSTANCES:
            del _PIPELINE_INSTANCES[task_id]
            return True
        return False


def cleanup_expired_pipelines() -> int:
    """
    清理过期的Pipeline实例（线程安全）

    Returns:
        int: 清理的实例数量

    Notes:
        - 使用锁保证线程安全
        - 应定期调用此函数（如通过定时任务）
    """
    with _PIPELINE_LOCK:
        current_time = time.time()
        expired_tasks = [
            task_id for task_id, entry in _PIPELINE_INSTANCES.items()
            if current_time - entry['timestamp'] > _PIPELINE_TTL
        ]

        for task_id in expired_tasks:
            del _PIPELINE_INSTANCES[task_id]

        return len(expired_tasks)


def get_pipeline_stats() -> Dict[str, Any]:
    """
    获取Pipeline实例统计信息（线程安全）

    Returns:
        dict: 统计信息，包括总数、最老实例年龄等

    Notes:
        - 使用锁保证线程安全
        - 用于监控和调试
    """
    with _PIPELINE_LOCK:
        if not _PIPELINE_INSTANCES:
            return {
                'total': 0,
                'oldest_age': 0,
                'average_age': 0
            }

        current_time = time.time()
        ages = [current_time - entry['timestamp'] for entry in _PIPELINE_INSTANCES.values()]

        return {
            'total': len(_PIPELINE_INSTANCES),
            'oldest_age': max(ages),
            'average_age': sum(ages) / len(ages),
            'ttl': _PIPELINE_TTL
        }


# 向后兼容：保留PIPELINE_INSTANCES字典接口（已弃用，建议使用上述函数）
# 注意：直接访问此字典不是线程安全的，请使用上述函数
PIPELINE_INSTANCES = _PIPELINE_INSTANCES
