#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理现有案例附件 - 重新提取Word/PDF中的图片

使用场景：
- 数据库schema更新后，为历史附件补充converted_images字段
- 修复案例附件图片插入功能

执行：
python scripts/batch_convert_case_attachments.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.database import get_knowledge_base_db
from common.logger import get_module_logger
from common.document_image_extractor import extract_images_from_document

logger = get_module_logger("batch_convert_case_attachments")


def batch_convert_attachments(dry_run=False):
    """
    批量转换案例附件

    Args:
        dry_run: 是否只模拟运行（不实际修改数据库）
    """
    db = get_knowledge_base_db()

    # 查询所有需要处理的附件（PDF和Word文档）
    query = """
        SELECT attachment_id, case_id, original_filename, file_path, file_type
        FROM case_attachments
        WHERE file_type IN ('pdf', 'docx', 'doc')
          AND (converted_images IS NULL OR converted_images = '')
        ORDER BY attachment_id
    """

    attachments = db.execute_query(query)

    if not attachments:
        logger.info("没有需要处理的附件")
        return

    logger.info(f"找到 {len(attachments)} 个需要转换的附件")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for idx, att in enumerate(attachments):
        attachment_id = att['attachment_id']
        file_path = att['file_path']
        original_filename = att['original_filename']
        file_type = att['file_type']

        logger.info(f"\n[{idx+1}/{len(attachments)}] 处理: {original_filename} (ID: {attachment_id})")

        # 检查文件是否存在
        if not Path(file_path).exists():
            logger.warning(f"  ⚠️ 文件不存在，跳过: {file_path}")
            skip_count += 1
            continue

        try:
            # 提取/转换图片
            logger.info(f"  开始提取图片...")
            result = extract_images_from_document(
                file_path=file_path,
                base_name=f"case_{att['case_id']}_{Path(file_path).stem}",
                dpi=200
            )

            if result['success'] and result['images']:
                converted_images = result['images']
                conversion_info = result['conversion_info']

                logger.info(f"  ✅ 提取成功: {len(converted_images)} 张图片")

                if not dry_run:
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
                        file_type.upper(),
                        attachment_id
                    )

                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(update_query, update_values)
                        conn.commit()

                    logger.info(f"  ✅ 数据库更新成功")
                    success_count += 1
                else:
                    logger.info(f"  ⏭️  [DRY RUN] 跳过数据库更新")
                    success_count += 1

            else:
                logger.warning(f"  ⚠️ 提取失败: {result.get('error', '未知错误')}")
                fail_count += 1

        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            fail_count += 1

    # 输出统计
    logger.info("\n" + "=" * 60)
    logger.info("批量处理完成")
    logger.info("=" * 60)
    logger.info(f"  - 总数: {len(attachments)}")
    logger.info(f"  - 成功: {success_count}")
    logger.info(f"  - 失败: {fail_count}")
    logger.info(f"  - 跳过: {skip_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='批量转换案例附件')
    parser.add_argument('--dry-run', action='store_true', help='只模拟运行，不实际修改数据库')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("批量转换案例附件脚本")
    logger.info("=" * 60)

    if args.dry_run:
        logger.info("⚠️ DRY RUN 模式：只模拟运行，不会修改数据库")

    batch_convert_attachments(dry_run=args.dry_run)
