#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境数据库初始化脚本
用于创建 risk_analysis_tasks 表及所有 V5 字段
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.risk_analyzer.task_manager import RiskTaskManager
from common.logger import get_module_logger

logger = get_module_logger("init_db")

def main():
    """初始化数据库"""
    logger.info("开始初始化生产环境数据库...")

    try:
        # 创建 RiskTaskManager 实例会自动创建表
        task_manager = RiskTaskManager()
        logger.info("✅ risk_analysis_tasks 表已创建")

        # 验证表结构
        import sqlite3
        from common.config import DB_PATH

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='risk_analysis_tasks'")
        if cursor.fetchone():
            logger.info("✅ 表 risk_analysis_tasks 已存在")

            # 检查关键字段
            cursor.execute("PRAGMA table_info(risk_analysis_tasks)")
            columns = [row[1] for row in cursor.fetchall()]

            required_fields = [
                'task_id', 'status', 'progress', 'file_path', 'file_name',
                'response_file_path', 'response_file_name',
                'reconcile_results', 'reconcile_progress', 'reconcile_step'
            ]

            missing_fields = [f for f in required_fields if f not in columns]
            if missing_fields:
                logger.warning(f"⚠️  缺少字段: {', '.join(missing_fields)}")

                # 尝试添加缺失字段
                for field in missing_fields:
                    if field == 'task_mode':
                        cursor.execute("ALTER TABLE risk_analysis_tasks ADD COLUMN task_mode TEXT DEFAULT 'bid_check'")
                        logger.info(f"✅ 已添加字段: {field}")
            else:
                logger.info(f"✅ 所有必需字段已存在: {len(required_fields)} 个")

            # 检查 task_mode 字段（可能需要单独添加）
            if 'task_mode' not in columns:
                cursor.execute("ALTER TABLE risk_analysis_tasks ADD COLUMN task_mode TEXT DEFAULT 'bid_check'")
                logger.info("✅ 已添加 task_mode 字段")

            conn.commit()
        else:
            logger.error("❌ 表创建失败")
            return False

        conn.close()

        logger.info("🎉 数据库初始化完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
