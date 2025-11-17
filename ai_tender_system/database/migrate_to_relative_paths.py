#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：将绝对路径转换为相对路径

背景：
- 旧版本存储的是绝对路径（/Users/lvhe/.../uploads/xxx.docx）
- 新版本存储相对路径（ai_tender_system/data/uploads/xxx.docx）

影响的表：
1. file_storage.file_path
2. tender_projects.tender_document_path
3. tender_projects.step1_data (JSON字段中的路径)
"""

import sys
import json
import re
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.database import get_db_connection
from common.logger import get_module_logger

logger = get_module_logger("db_migration")


def convert_absolute_to_relative(absolute_path: str) -> str:
    """
    将绝对路径转换为相对路径

    Args:
        absolute_path: 绝对路径字符串

    Returns:
        相对路径字符串
    """
    if not absolute_path:
        return absolute_path

    path_str = str(absolute_path)

    # 定义可能的绝对路径前缀
    absolute_prefixes = [
        '/Users/lvhe/Downloads/zhongbiao/zhongbiao/',
        '/var/www/ai-tender-system/',
        'C:\\zhongbiao\\',
    ]

    # 移除绝对路径前缀
    for prefix in absolute_prefixes:
        if path_str.startswith(prefix):
            relative = path_str[len(prefix):]
            logger.debug(f"转换路径: {path_str[:50]}... -> {relative[:50]}...")
            return relative

    # 如果已经是相对路径，直接返回
    return path_str


def migrate_file_storage_table():
    """迁移 file_storage 表的路径"""
    logger.info("开始迁移 file_storage 表...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 查询所有记录
        cursor.execute("SELECT file_id, file_path FROM file_storage")
        rows = cursor.fetchall()

        logger.info(f"找到 {len(rows)} 条记录")

        updated_count = 0
        for file_id, file_path in rows:
            relative_path = convert_absolute_to_relative(file_path)

            if relative_path != file_path:
                # 更新记录
                cursor.execute(
                    "UPDATE file_storage SET file_path = ? WHERE file_id = ?",
                    (relative_path, file_id)
                )
                updated_count += 1

        conn.commit()
        logger.info(f"file_storage 表迁移完成，更新了 {updated_count} 条记录")

    return updated_count


def migrate_tender_projects_table():
    """迁移 tender_projects 表的路径"""
    logger.info("开始迁移 tender_projects 表...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 查询所有记录
        cursor.execute("SELECT project_id, tender_document_path, step1_data FROM tender_projects")
        rows = cursor.fetchall()

        logger.info(f"找到 {len(rows)} 个项目")

        updated_count = 0
        for project_id, tender_doc_path, step1_data_str in rows:
            needs_update = False

            # 1. 转换 tender_document_path
            new_tender_doc_path = tender_doc_path
            if tender_doc_path:
                new_tender_doc_path = convert_absolute_to_relative(tender_doc_path)
                if new_tender_doc_path != tender_doc_path:
                    needs_update = True

            # 2. 转换 step1_data 中的路径
            new_step1_data = step1_data_str
            if step1_data_str:
                try:
                    step1_data = json.loads(step1_data_str)

                    # 需要转换的路径字段
                    path_fields = [
                        'file_path',
                        'response_file_path',
                        'technical_file_path',
                        'tender_document_path'
                    ]

                    for field in path_fields:
                        if field in step1_data and step1_data[field]:
                            old_path = step1_data[field]
                            new_path = convert_absolute_to_relative(old_path)
                            if new_path != old_path:
                                step1_data[field] = new_path
                                needs_update = True

                    # 处理嵌套的文件对象（如 business_response_file）
                    nested_file_fields = [
                        'business_response_file',
                        'technical_point_to_point_file',
                        'technical_proposal_file'
                    ]

                    for field in nested_file_fields:
                        if field in step1_data and isinstance(step1_data[field], dict):
                            file_obj = step1_data[field]

                            # 转换文件对象中的路径
                            for path_key in ['file_path', 'file_url', 'download_url']:
                                if path_key in file_obj and file_obj[path_key]:
                                    old_path = file_obj[path_key]
                                    new_path = convert_absolute_to_relative(old_path)
                                    if new_path != old_path:
                                        file_obj[path_key] = new_path
                                        needs_update = True

                    new_step1_data = json.dumps(step1_data, ensure_ascii=False)

                except json.JSONDecodeError:
                    logger.warning(f"项目 {project_id} 的 step1_data JSON解析失败，跳过")

            # 更新数据库
            if needs_update:
                cursor.execute(
                    "UPDATE tender_projects SET tender_document_path = ?, step1_data = ? WHERE project_id = ?",
                    (new_tender_doc_path, new_step1_data, project_id)
                )
                updated_count += 1

        conn.commit()
        logger.info(f"tender_projects 表迁移完成，更新了 {updated_count} 个项目")

    return updated_count


def main():
    """执行迁移"""
    logger.info("=" * 80)
    logger.info("开始数据库路径迁移：绝对路径 → 相对路径")
    logger.info("=" * 80)

    try:
        # 迁移 file_storage 表
        count1 = migrate_file_storage_table()

        # 迁移 tender_projects 表
        count2 = migrate_tender_projects_table()

        logger.info("=" * 80)
        logger.info(f"✅ 迁移完成！")
        logger.info(f"   file_storage: 更新 {count1} 条记录")
        logger.info(f"   tender_projects: 更新 {count2} 个项目")
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
