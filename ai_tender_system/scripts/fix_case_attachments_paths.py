#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复案例附件路径并重新转换图片
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
# __file__ = /path/to/ai_tender_system/scripts/fix_case_attachments_paths.py
# parent = /path/to/ai_tender_system/scripts
# parent.parent = /path/to/ai_tender_system
project_root = Path(__file__).parent.parent  # ai_tender_system 目录
sys.path.insert(0, str(project_root))

from common.database import get_knowledge_base_db
from common.logger import get_module_logger
from common.document_image_extractor import extract_images_from_document

logger = get_module_logger("fix_paths")

def fix_and_convert():
    """修复路径并转换"""
    db = get_knowledge_base_db()

    # 查询所有附件
    query = """
        SELECT attachment_id, case_id, original_filename, file_path, file_type, file_name
        FROM case_attachments
        WHERE file_type IN ('pdf', 'docx', 'doc')
        ORDER BY attachment_id
    """

    attachments = db.execute_query(query)

    logger.info(f"找到 {len(attachments)} 个附件记录")

    success_count = 0
    fixed_count = 0
    skip_count = 0

    for idx, att in enumerate(attachments, 1):
        attachment_id = att['attachment_id']
        original_filename = att['original_filename']
        file_path = att['file_path']
        file_name = att['file_name']

        logger.info(f"\n[{idx}/{len(attachments)}] 检查: {original_filename} (ID: {attachment_id})")
        logger.info(f"  当前路径: {file_path}")

        # 尝试多种路径
        possible_paths = []

        # 1. 原路径
        possible_paths.append(Path(file_path))

        # 2. 如果是绝对路径但错误，尝试提取文件名
        if file_path.startswith('/Users/') or file_path.startswith('/var/www/'):
            filename = Path(file_path).name
            # 在标准位置查找
            standard_path = project_root / 'data' / 'uploads' / 'case_attachments'
            for year_dir in standard_path.glob('*/'):
                for month_dir in year_dir.glob('*/'):
                    test_path = month_dir / filename
                    if test_path not in possible_paths:
                        possible_paths.append(test_path)

        # 3. 使用file_name字段
        if file_name:
            standard_path = project_root / 'data' / 'uploads' / 'case_attachments'
            for year_dir in standard_path.glob('*/'):
                for month_dir in year_dir.glob('*/'):
                    test_path = month_dir / file_name
                    if test_path not in possible_paths:
                        possible_paths.append(test_path)

        # 4. 相对路径
        if not Path(file_path).is_absolute():
            possible_paths.append(project_root / file_path)

        # 查找存在的文件
        actual_file = None
        for test_path in possible_paths:
            if test_path.exists():
                actual_file = test_path
                break

        if not actual_file:
            logger.warning(f"  ❌ 文件不存在，跳过")
            skip_count += 1
            continue

        logger.info(f"  ✅ 找到文件: {actual_file}")

        # 更新数据库中的路径（使用相对路径）
        try:
            relative_path = actual_file.relative_to(project_root)
            new_path = str(relative_path)
        except ValueError:
            # 如果无法转为相对路径，使用绝对路径
            new_path = str(actual_file)

        if new_path != file_path:
            logger.info(f"  🔧 更新路径: {new_path}")
            update_path_query = "UPDATE case_attachments SET file_path = ? WHERE attachment_id = ?"
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(update_path_query, (new_path, attachment_id))
                conn.commit()
            fixed_count += 1

        # 提取/转换图片
        try:
            logger.info(f"  📸 开始提取图片...")
            result = extract_images_from_document(
                file_path=str(actual_file),
                base_name=f"case_{att['case_id']}_{actual_file.stem}",
                dpi=200
            )

            if result['success'] and result['images']:
                converted_images = result['images']
                conversion_info = result['conversion_info']

                logger.info(f"  ✅ 提取成功: {len(converted_images)} 张图片")

                # 更新数据库
                update_query = """
                    UPDATE case_attachments
                    SET converted_images = ?,
                        conversion_info = ?,
                        conversion_date = ?,
                        original_file_type = ?
                    WHERE attachment_id = ?
                """

                update_values = (
                    json.dumps(converted_images, ensure_ascii=False),
                    json.dumps(conversion_info, ensure_ascii=False),
                    datetime.now(),
                    att['file_type'].upper(),
                    attachment_id
                )

                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(update_query, update_values)
                    conn.commit()

                success_count += 1
            else:
                logger.warning(f"  ⚠️ 提取失败: {result.get('error', '未知错误')}")

        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")

    # 输出统计
    logger.info("\n" + "=" * 60)
    logger.info("修复和转换完成")
    logger.info("=" * 60)
    logger.info(f"  - 总记录数: {len(attachments)}")
    logger.info(f"  - 路径修复: {fixed_count}")
    logger.info(f"  - 转换成功: {success_count}")
    logger.info(f"  - 文件不存在: {skip_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("修复案例附件路径并转换图片")
    logger.info("=" * 60)
    fix_and_convert()
