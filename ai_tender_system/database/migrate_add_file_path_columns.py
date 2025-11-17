#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加独立的文件路径字段

背景：
- 旧设计：文件路径杂糅在 step1_data JSON中
- 新设计：每个文件类型有独立的路径字段

新增字段：
1. response_template_path      - 应答模板文件路径
2. technical_requirement_path  - 技术需求文件路径
3. business_response_path      - 商务应答完成文件路径
4. technical_p2p_path          - 点对点应答文件路径
5. technical_proposal_path     - 技术方案文件路径
6. final_package_path          - 最终应答文件包路径
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.database import get_db_connection
from common.logger import get_module_logger

logger = get_module_logger("db_migration")


def add_file_path_columns():
    """添加文件路径字段"""
    logger.info("步骤1: 添加文件路径字段...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(tender_projects)")
        existing_columns = [row[1] for row in cursor.fetchall()]

        new_columns = [
            ('response_template_path', 'VARCHAR(500)', '应答模板文件路径'),
            ('technical_requirement_path', 'VARCHAR(500)', '技术需求文件路径'),
            ('business_response_path', 'VARCHAR(500)', '商务应答完成文件路径'),
            ('technical_p2p_path', 'VARCHAR(500)', '点对点应答文件路径'),
            ('technical_proposal_path', 'VARCHAR(500)', '技术方案文件路径'),
            ('final_package_path', 'VARCHAR(500)', '最终应答文件包路径'),
        ]

        added_count = 0
        for column_name, column_type, comment in new_columns:
            if column_name not in existing_columns:
                sql = f"ALTER TABLE tender_projects ADD COLUMN {column_name} {column_type}"
                cursor.execute(sql)
                logger.info(f"  ✓ 添加字段: {column_name} ({comment})")
                added_count += 1
            else:
                logger.info(f"  ⊙ 字段已存在: {column_name}")

        conn.commit()
        logger.info(f"字段添加完成，新增 {added_count} 个字段")

    return added_count


def migrate_data_from_json():
    """从step1_data迁移数据到独立字段"""
    logger.info("步骤2: 从step1_data迁移数据...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 查询所有项目
        cursor.execute("SELECT project_id, step1_data, tender_document_path FROM tender_projects")
        rows = cursor.fetchall()

        logger.info(f"找到 {len(rows)} 个项目")

        updated_count = 0
        for project_id, step1_data_str, tender_doc_path in rows:
            if not step1_data_str:
                continue

            try:
                step1_data = json.loads(step1_data_str)

                # 提取各个文件路径
                updates = {}

                # 1. 标书文件（如果tender_document_path为空，从step1_data获取）
                if not tender_doc_path and step1_data.get('file_path'):
                    updates['tender_document_path'] = step1_data['file_path']

                # 2. 应答模板文件
                if step1_data.get('response_file_path'):
                    updates['response_template_path'] = step1_data['response_file_path']

                # 3. 技术需求文件
                if step1_data.get('technical_file_path'):
                    updates['technical_requirement_path'] = step1_data['technical_file_path']

                # 4. 商务应答完成文件（可能是对象）
                business_file = step1_data.get('business_response_file')
                if business_file:
                    if isinstance(business_file, dict):
                        path = business_file.get('file_path') or business_file.get('file_url')
                        if path:
                            updates['business_response_path'] = path
                    elif isinstance(business_file, str):
                        updates['business_response_path'] = business_file

                # 5. 点对点应答文件（可能是对象）
                p2p_file = step1_data.get('technical_point_to_point_file')
                if p2p_file:
                    if isinstance(p2p_file, dict):
                        path = p2p_file.get('file_path') or p2p_file.get('file_url')
                        if path:
                            updates['technical_p2p_path'] = path
                    elif isinstance(p2p_file, str):
                        updates['technical_p2p_path'] = p2p_file

                # 6. 技术方案文件（可能是对象）
                proposal_file = step1_data.get('technical_proposal_file')
                if proposal_file:
                    if isinstance(proposal_file, dict):
                        path = proposal_file.get('file_path') or proposal_file.get('file_url')
                        if path:
                            updates['technical_proposal_path'] = path
                    elif isinstance(proposal_file, str):
                        updates['technical_proposal_path'] = proposal_file

                # 执行更新
                if updates:
                    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
                    values = list(updates.values()) + [project_id]

                    cursor.execute(
                        f"UPDATE tender_projects SET {set_clause} WHERE project_id = ?",
                        values
                    )
                    updated_count += 1

                    logger.debug(f"项目 {project_id}: 更新了 {len(updates)} 个路径字段")

            except json.JSONDecodeError:
                logger.warning(f"项目 {project_id} 的 step1_data JSON解析失败，跳过")

        conn.commit()
        logger.info(f"数据迁移完成，更新了 {updated_count} 个项目")

    return updated_count


def verify_migration():
    """验证迁移结果"""
    logger.info("步骤3: 验证迁移结果...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 统计各个字段的非空数量
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN tender_document_path IS NOT NULL THEN 1 ELSE 0 END) as has_tender,
                SUM(CASE WHEN response_template_path IS NOT NULL THEN 1 ELSE 0 END) as has_response,
                SUM(CASE WHEN technical_requirement_path IS NOT NULL THEN 1 ELSE 0 END) as has_tech,
                SUM(CASE WHEN business_response_path IS NOT NULL THEN 1 ELSE 0 END) as has_business,
                SUM(CASE WHEN technical_p2p_path IS NOT NULL THEN 1 ELSE 0 END) as has_p2p,
                SUM(CASE WHEN technical_proposal_path IS NOT NULL THEN 1 ELSE 0 END) as has_proposal
            FROM tender_projects
        """)

        row = cursor.fetchone()
        total, has_tender, has_response, has_tech, has_business, has_p2p, has_proposal = row

        logger.info(f"验证结果（共{total}个项目）：")
        logger.info(f"  - 标书文件: {has_tender} 个")
        logger.info(f"  - 应答模板: {has_response} 个")
        logger.info(f"  - 技术需求: {has_tech} 个")
        logger.info(f"  - 商务应答: {has_business} 个")
        logger.info(f"  - 点对点应答: {has_p2p} 个")
        logger.info(f"  - 技术方案: {has_proposal} 个")

    return True


def main():
    """执行迁移"""
    logger.info("=" * 80)
    logger.info("开始数据库迁移：添加独立文件路径字段")
    logger.info("=" * 80)

    try:
        # 步骤1: 添加字段
        added = add_file_path_columns()

        # 步骤2: 迁移数据
        updated = migrate_data_from_json()

        # 步骤3: 验证
        verify_migration()

        logger.info("=" * 80)
        logger.info(f"✅ 迁移完成！")
        logger.info(f"   新增字段: {added} 个")
        logger.info(f"   更新项目: {updated} 个")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
