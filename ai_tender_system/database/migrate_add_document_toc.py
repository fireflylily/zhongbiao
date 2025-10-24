#!/usr/bin/env python3
"""
数据库迁移脚本：添加 document_toc 表
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.database import get_knowledge_base_db

from common.logger import get_module_logger

logger = get_module_logger("migrate_add_document_toc")

def migrate():
    """执行迁移"""
    db = get_knowledge_base_db()

    logger.info("开始迁移：添加 document_toc 表...")

    with db.get_connection() as conn:
        cursor = conn.cursor()

        try:
            # 检查表是否已存在
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='document_toc'
            """)

            if cursor.fetchone():
                logger.info("✓ document_toc 表已存在，跳过创建")
                return

            # 创建 document_toc 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_toc (
                    toc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER NOT NULL,
                    heading_level INTEGER NOT NULL,
                    heading_text TEXT NOT NULL,
                    section_number VARCHAR(50),
                    keywords TEXT,
                    page_number INTEGER,
                    parent_toc_id INTEGER,
                    sequence_order INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_toc_id) REFERENCES document_toc(toc_id) ON DELETE SET NULL
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_toc_doc ON document_toc(doc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_toc_heading_text ON document_toc(heading_text)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_toc_section_number ON document_toc(section_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_toc_parent ON document_toc(parent_toc_id)")

            conn.commit()
            logger.info("✓ document_toc 表创建成功")
            logger.info("✓ 索引创建成功")

        except Exception as e:
            logger.info(f"✗ 迁移失败: {e}")
            conn.rollback()
            raise

if __name__ == '__main__':
    migrate()
    logger.info("\n迁移完成！")
