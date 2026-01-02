#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版数据库初始化脚本
不依赖 dataclasses，兼容 Python 3.6+
"""

import sqlite3
import os
from pathlib import Path

def main():
    """初始化数据库"""
    print("开始初始化生产环境数据库...")

    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    db_path = data_dir / "knowledge_base.db"

    # 确保数据目录存在
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"数据库路径: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 创建表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS risk_analysis_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            current_step TEXT DEFAULT '',
            file_path TEXT DEFAULT '',
            file_name TEXT DEFAULT '',
            file_size INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT DEFAULT '',
            risk_items TEXT DEFAULT '[]',
            risk_count INTEGER DEFAULT 0,
            high_risk_count INTEGER DEFAULT 0,
            medium_risk_count INTEGER DEFAULT 0,
            low_risk_count INTEGER DEFAULT 0,
            analysis_result TEXT DEFAULT '{}',
            ai_model TEXT DEFAULT '',
            processing_time REAL DEFAULT 0.0,

            -- V5 新增：应答文件相关
            response_file_path TEXT DEFAULT '',
            response_file_name TEXT DEFAULT '',

            -- V5 新增：对账相关
            reconcile_results TEXT DEFAULT '',
            reconcile_progress INTEGER DEFAULT 0,
            reconcile_step TEXT DEFAULT '',

            -- V5 新增：业务模式
            task_mode TEXT DEFAULT 'bid_check'
        )
        """

        cursor.execute(create_table_sql)
        print("✅ risk_analysis_tasks 表已创建")

        # 检查表结构
        cursor.execute("PRAGMA table_info(risk_analysis_tasks)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        print(f"✅ 表字段总数: {len(columns)}")

        # 检查关键 V5 字段
        v5_fields = {
            'response_file_path': 'TEXT',
            'response_file_name': 'TEXT',
            'reconcile_results': 'TEXT',
            'reconcile_progress': 'INTEGER',
            'reconcile_step': 'TEXT',
            'task_mode': 'TEXT'
        }

        missing_fields = []
        for field_name, field_type in v5_fields.items():
            if field_name not in columns:
                missing_fields.append(field_name)

        # 添加缺失字段
        if missing_fields:
            print(f"⚠️  发现缺失字段: {', '.join(missing_fields)}")
            for field_name in missing_fields:
                field_type = v5_fields[field_name]
                default_value = "''" if field_type == 'TEXT' else '0'
                alter_sql = f"ALTER TABLE risk_analysis_tasks ADD COLUMN {field_name} {field_type} DEFAULT {default_value}"
                try:
                    cursor.execute(alter_sql)
                    print(f"✅ 已添加字段: {field_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"❌ 添加字段 {field_name} 失败: {e}")
        else:
            print("✅ 所有 V5 字段已存在")

        # 创建索引（提高查询性能）
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_task_id ON risk_analysis_tasks(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_id ON risk_analysis_tasks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_status ON risk_analysis_tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON risk_analysis_tasks(created_at)"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        print("✅ 索引已创建")

        # 查询当前任务数量
        cursor.execute("SELECT COUNT(*) FROM risk_analysis_tasks")
        task_count = cursor.fetchone()[0]
        print(f"📊 当前任务数量: {task_count}")

        conn.commit()
        conn.close()

        print("\n🎉 数据库初始化完成！")
        print("\n下一步:")
        print("1. 重启后端服务")
        print("2. 测试小程序对账功能")

        return True

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
