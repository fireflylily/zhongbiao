#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量重新转换Word案例附件脚本
修复图片提取顺序问题
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'ai_tender_system'))

from common.database import get_knowledge_base_db
from common.document_image_extractor import extract_images_from_document
from common.logger import get_module_logger

logger = get_module_logger("reconvert_word")


def reconvert_word_attachments():
    """批量重新转换Word附件"""

    db = get_knowledge_base_db()

    # 查询所有需要重新转换的Word附件
    query = """
        SELECT attachment_id, case_id, file_path, original_filename, converted_images
        FROM case_attachments
        WHERE (file_type = 'docx' OR file_type = 'doc')
        AND converted_images IS NOT NULL
        ORDER BY attachment_id
    """

    attachments = db.execute_query(query)

    if not attachments:
        logger.info("没有需要重新转换的Word附件")
        return

    logger.info(f"找到 {len(attachments)} 个Word附件需要重新转换")
    print(f"\n{'='*60}")
    print(f"批量重新转换Word案例附件")
    print(f"{'='*60}\n")

    success_count = 0
    failed_count = 0

    for att in attachments:
        attachment_id = att['attachment_id']
        case_id = att['case_id']
        file_path = att['file_path']
        original_filename = att['original_filename']
        old_converted_images = att['converted_images']

        print(f"\n处理附件 #{attachment_id}: {original_filename}")
        print(f"  案例ID: {case_id}")
        print(f"  文件路径: {file_path}")

        try:
            # 解析文件路径（支持相对路径）
            from common import resolve_file_path
            resolved_path = resolve_file_path(file_path)

            # 检查文件是否存在
            if not resolved_path or not Path(resolved_path).exists():
                logger.warning(f"  ⚠️  文件不存在，跳过: {file_path}")
                failed_count += 1
                continue

            file_path = str(resolved_path)

            # 删除旧的转换图片
            try:
                old_images = json.loads(old_converted_images)
                old_image_dir = None

                # 找到旧图片目录
                if old_images and len(old_images) > 0:
                    first_image_path = Path(old_images[0]['file_path'])
                    old_image_dir = first_image_path.parent

                    if old_image_dir.exists():
                        logger.info(f"  删除旧转换图片目录: {old_image_dir}")
                        shutil.rmtree(old_image_dir)
            except Exception as e:
                logger.warning(f"  删除旧图片失败: {e}")

            # 使用新的提取逻辑重新转换
            base_name = f"case_{case_id}_{Path(original_filename).stem}"

            logger.info(f"  开始重新转换...")
            result = extract_images_from_document(
                file_path=file_path,
                base_name=base_name,
                dpi=200
            )

            if result['success']:
                new_converted_images = result['images']
                conversion_info = result['conversion_info']

                logger.info(f"  ✅ 重新转换成功: {len(new_converted_images)} 张图片")

                # 更新数据库
                update_query = """
                    UPDATE case_attachments
                    SET converted_images = ?,
                        conversion_info = ?,
                        conversion_date = ?
                    WHERE attachment_id = ?
                """

                # 使用连接上下文管理器手动commit
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        update_query,
                        (
                            json.dumps(new_converted_images, ensure_ascii=False),
                            json.dumps(conversion_info, ensure_ascii=False),
                            datetime.now(),
                            attachment_id
                        )
                    )
                    conn.commit()

                logger.info(f"  ✅ 数据库已更新")
                print(f"  ✅ 成功：重新转换了 {len(new_converted_images)} 张图片")
                success_count += 1
            else:
                logger.error(f"  ❌ 转换失败: {result.get('error')}")
                print(f"  ❌ 失败：{result.get('error')}")
                failed_count += 1

        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            print(f"  ❌ 失败：{e}")
            failed_count += 1

    # 统计结果
    print(f"\n{'='*60}")
    print(f"批量转换完成")
    print(f"{'='*60}")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    print(f"总计: {len(attachments)} 个\n")

    logger.info(f"批量重新转换完成: 成功{success_count}个, 失败{failed_count}个")


if __name__ == "__main__":
    reconvert_word_attachments()
