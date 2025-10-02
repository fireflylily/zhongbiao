#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：标书智能处理系统
执行SQL文件创建新表和索引
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common import get_config, setup_logging, get_module_logger


def run_migration():
    """执行数据库迁移"""
    setup_logging()
    logger = get_module_logger("db_migration")
    config = get_config()

    # 获取数据库路径
    db_path = config.get_path('data') / 'knowledge_base.db'
    schema_path = Path(__file__).parent / "tender_processing_schema.sql"

    logger.info(f"开始数据库迁移...")
    logger.info(f"数据库路径: {db_path}")
    logger.info(f"Schema文件: {schema_path}")

    if not schema_path.exists():
        logger.error(f"Schema文件不存在: {schema_path}")
        return False

    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 读取SQL文件
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # 执行SQL脚本
        logger.info("执行SQL脚本...")
        cursor.executescript(sql_script)
        conn.commit()

        # 验证表是否创建成功
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'tender_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()

        logger.info("创建的表:")
        for table in tables:
            logger.info(f"  - {table[0]}")

        # 验证视图
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='view' AND name LIKE 'v_%'
            ORDER BY name
        """)
        views = cursor.fetchall()

        logger.info("创建的视图:")
        for view in views:
            logger.info(f"  - {view[0]}")

        # 验证索引
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
            ORDER BY name
        """)
        indexes = cursor.fetchall()

        logger.info(f"创建的索引数量: {len(indexes)}")

        conn.close()
        logger.info("✅ 数据库迁移完成!")
        return True

    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def rollback_migration():
    """回滚迁移（删除创建的表）"""
    setup_logging()
    logger = get_module_logger("db_rollback")
    config = get_config()

    db_path = config.get_path('data') / 'knowledge_base.db'

    logger.warning("⚠️  开始回滚数据库迁移...")
    logger.warning(f"数据库路径: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 删除表（按依赖顺序）
        tables_to_drop = [
            'tender_requirements',
            'tender_document_chunks',
            'tender_processing_logs',
            'tender_processing_tasks'
        ]

        for table in tables_to_drop:
            logger.info(f"删除表: {table}")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")

        # 删除视图
        views_to_drop = [
            'v_processing_statistics',
            'v_requirements_summary'
        ]

        for view in views_to_drop:
            logger.info(f"删除视图: {view}")
            cursor.execute(f"DROP VIEW IF EXISTS {view}")

        # 删除触发器
        triggers_to_drop = [
            'update_chunks_timestamp',
            'update_requirements_timestamp',
            'update_logs_timestamp'
        ]

        for trigger in triggers_to_drop:
            logger.info(f"删除触发器: {trigger}")
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")

        conn.commit()
        conn.close()

        logger.info("✅ 回滚完成!")
        return True

    except Exception as e:
        logger.error(f"❌ 回滚失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='标书智能处理系统数据库迁移工具')
    parser.add_argument('action', choices=['migrate', 'rollback'],
                        help='执行的操作: migrate（迁移）或 rollback（回滚）')

    args = parser.parse_args()

    if args.action == 'migrate':
        success = run_migration()
    else:
        success = rollback_migration()

    sys.exit(0 if success else 1)
