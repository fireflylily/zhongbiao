#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加资质文件多文件支持
Migration: Add multi-file support for company qualifications

变更内容：
1. 在 company_qualifications 表添加 file_version, file_sequence, is_primary 字段
2. 在 qualification_types 表添加 allow_multiple_files, version_label 字段
3. 删除 company_qualifications 表的 UNIQUE (company_id, qualification_key) 约束
4. 创建新的复合索引支持多文件查询
5. 为现有数据设置默认值

执行方式：
    python3 ai_tender_system/database/migrate_add_multi_file_support.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.logger import get_module_logger
from ai_tender_system.common.config import get_config

logger = get_module_logger('database_migration')


def migrate_database():
    """执行数据库迁移"""

    config = get_config()
    db_path = config.get_path('knowledge_base_db')

    logger.info(f"开始数据库迁移：添加资质文件多文件支持")
    logger.info(f"数据库路径：{db_path}")

    # 备份数据库
    backup_path = db_path.parent / f"knowledge_base_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    logger.info(f"创建数据库备份：{backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        logger.info("=" * 60)
        logger.info("步骤 1: 检查并添加 company_qualifications 表的新字段")
        logger.info("=" * 60)

        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(company_qualifications)")
        columns = [row['name'] for row in cursor.fetchall()]

        if 'file_version' not in columns:
            logger.info("添加字段：file_version")
            cursor.execute("ALTER TABLE company_qualifications ADD COLUMN file_version VARCHAR(50)")
        else:
            logger.info("字段 file_version 已存在，跳过")

        if 'file_sequence' not in columns:
            logger.info("添加字段：file_sequence")
            cursor.execute("ALTER TABLE company_qualifications ADD COLUMN file_sequence INTEGER DEFAULT 1")
            # 为现有记录设置默认值
            cursor.execute("UPDATE company_qualifications SET file_sequence = 1 WHERE file_sequence IS NULL")
        else:
            logger.info("字段 file_sequence 已存在，跳过")

        if 'is_primary' not in columns:
            logger.info("添加字段：is_primary")
            cursor.execute("ALTER TABLE company_qualifications ADD COLUMN is_primary BOOLEAN DEFAULT TRUE")
            # 为现有记录设置默认值
            cursor.execute("UPDATE company_qualifications SET is_primary = TRUE WHERE is_primary IS NULL")
        else:
            logger.info("字段 is_primary 已存在，跳过")

        conn.commit()

        logger.info("\n" + "=" * 60)
        logger.info("步骤 2: 检查并添加 qualification_types 表的新字段")
        logger.info("=" * 60)

        cursor.execute("PRAGMA table_info(qualification_types)")
        qual_type_columns = [row['name'] for row in cursor.fetchall()]

        if 'allow_multiple_files' not in qual_type_columns:
            logger.info("添加字段：allow_multiple_files")
            cursor.execute("ALTER TABLE qualification_types ADD COLUMN allow_multiple_files BOOLEAN DEFAULT FALSE")
            # 为现有记录设置默认值
            cursor.execute("UPDATE qualification_types SET allow_multiple_files = FALSE WHERE allow_multiple_files IS NULL")
        else:
            logger.info("字段 allow_multiple_files 已存在，跳过")

        if 'version_label' not in qual_type_columns:
            logger.info("添加字段：version_label")
            cursor.execute("ALTER TABLE qualification_types ADD COLUMN version_label VARCHAR(50)")
        else:
            logger.info("字段 version_label 已存在，跳过")

        conn.commit()

        logger.info("\n" + "=" * 60)
        logger.info("步骤 3: 更新预定义资质类型的多文件配置")
        logger.info("=" * 60)

        # 标记支持多文件的资质类型
        multi_file_qualifications = [
            ('audit_report', '年份'),
            ('patent_certificate', '专利号'),
            ('software_copyright', '软著名称')
        ]

        for type_key, version_label in multi_file_qualifications:
            logger.info(f"设置 {type_key} 支持多文件，版本标签：{version_label}")
            cursor.execute("""
                UPDATE qualification_types
                SET allow_multiple_files = TRUE, version_label = ?
                WHERE type_key = ?
            """, (version_label, type_key))

        conn.commit()

        logger.info("\n" + "=" * 60)
        logger.info("步骤 4: 创建新的复合索引")
        logger.info("=" * 60)

        # 检查索引是否存在
        cursor.execute("PRAGMA index_list(company_qualifications)")
        existing_indexes = [row['name'] for row in cursor.fetchall()]

        if 'idx_company_qual_key_seq' not in existing_indexes:
            logger.info("创建索引：idx_company_qual_key_seq")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_company_qual_key_seq
                ON company_qualifications(company_id, qualification_key, file_sequence)
            """)
        else:
            logger.info("索引 idx_company_qual_key_seq 已存在，跳过")

        conn.commit()

        logger.info("\n" + "=" * 60)
        logger.info("步骤 5: 处理 UNIQUE 约束（需要重建表）")
        logger.info("=" * 60)

        # SQLite 不支持直接删除约束，需要重建表
        # 检查是否需要重建表
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='company_qualifications'")
        table_sql = cursor.fetchone()

        if table_sql and 'UNIQUE' in table_sql['sql'] and 'company_id, qualification_key' in table_sql['sql']:
            logger.info("检测到 UNIQUE 约束，需要重建表以移除约束")
            logger.warning("注意：这个操作可能需要一些时间...")

            # 创建临时表（没有 UNIQUE 约束）
            cursor.execute("""
                CREATE TABLE company_qualifications_new (
                    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    qualification_key VARCHAR(50) NOT NULL,
                    qualification_name VARCHAR(255) NOT NULL,
                    custom_name VARCHAR(255),
                    original_filename VARCHAR(500) NOT NULL,
                    safe_filename VARCHAR(500) NOT NULL,
                    file_path VARCHAR(1000) NOT NULL,
                    file_size INTEGER,
                    file_type VARCHAR(50),
                    file_version VARCHAR(50),
                    file_sequence INTEGER DEFAULT 1,
                    is_primary BOOLEAN DEFAULT TRUE,
                    issue_date DATE,
                    expire_date DATE,
                    is_valid BOOLEAN DEFAULT TRUE,
                    verify_status VARCHAR(20) DEFAULT 'pending',
                    verify_time TIMESTAMP,
                    verify_by VARCHAR(100),
                    verify_note TEXT,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    upload_by VARCHAR(100),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                )
            """)

            # 复制数据
            cursor.execute("""
                INSERT INTO company_qualifications_new
                SELECT * FROM company_qualifications
            """)

            # 删除旧表
            cursor.execute("DROP TABLE company_qualifications")

            # 重命名新表
            cursor.execute("ALTER TABLE company_qualifications_new RENAME TO company_qualifications")

            # 重建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_qualifications_company ON company_qualifications(company_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_qualifications_expire ON company_qualifications(expire_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_qualifications_status ON company_qualifications(verify_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_qual_key_seq ON company_qualifications(company_id, qualification_key, file_sequence)")

            logger.info("表重建完成，UNIQUE 约束已移除")
        else:
            logger.info("未检测到需要移除的 UNIQUE 约束，跳过表重建")

        conn.commit()

        logger.info("\n" + "=" * 60)
        logger.info("步骤 6: 验证迁移结果")
        logger.info("=" * 60)

        # 验证字段
        cursor.execute("PRAGMA table_info(company_qualifications)")
        final_columns = {row['name']: row['type'] for row in cursor.fetchall()}

        required_fields = ['file_version', 'file_sequence', 'is_primary']
        for field in required_fields:
            if field in final_columns:
                logger.info(f"✓ 字段 {field} 存在，类型：{final_columns[field]}")
            else:
                logger.error(f"✗ 字段 {field} 不存在！")

        # 验证索引
        cursor.execute("PRAGMA index_list(company_qualifications)")
        final_indexes = [row['name'] for row in cursor.fetchall()]
        logger.info(f"当前索引：{', '.join(final_indexes)}")

        # 统计数据
        cursor.execute("SELECT COUNT(*) as count FROM company_qualifications")
        qual_count = cursor.fetchone()['count']
        logger.info(f"资质记录总数：{qual_count}")

        cursor.execute("SELECT COUNT(*) as count FROM qualification_types WHERE allow_multiple_files = TRUE")
        multi_file_types = cursor.fetchone()['count']
        logger.info(f"支持多文件的资质类型数：{multi_file_types}")

        logger.info("\n" + "=" * 60)
        logger.info("✅ 数据库迁移成功完成！")
        logger.info("=" * 60)
        logger.info(f"备份文件保存在：{backup_path}")
        logger.info("如果迁移出现问题，可以使用备份文件恢复数据库")

    except Exception as e:
        logger.error(f"❌ 数据库迁移失败：{e}")
        logger.error("正在回滚...")
        conn.rollback()
        logger.info(f"请使用备份文件恢复数据库：{backup_path}")
        raise

    finally:
        conn.close()


if __name__ == '__main__':
    try:
        migrate_database()
        sys.exit(0)
    except Exception as e:
        logger.error(f"迁移脚本执行失败：{e}")
        sys.exit(1)
