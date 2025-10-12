#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：将completed_response_file迁移到三个独立字段

背景：
原架构使用单一字段 step1_data['completed_response_file'] 存储三种文件：
- 商务应答文件 (source: 'business_response')
- 点对点应答文件 (source: 'point_to_point')
- 技术方案文件 (source: 'tech_proposal')

新架构使用三个独立字段：
- step1_data['business_response_file']
- step1_data['technical_point_to_point_file']
- step1_data['technical_proposal_file']

迁移逻辑：
根据 completed_response_file['source'] 字段，将数据复制到对应的新字段
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.database import get_knowledge_base_db
from common import get_module_logger

logger = get_module_logger("migrate_completed_response")


def migrate_completed_response_files(dry_run=True):
    """
    迁移completed_response_file到三个独立字段

    Args:
        dry_run: 如果为True，只模拟不实际修改数据库
    """
    db = get_knowledge_base_db()

    # 查询所有包含completed_response_file的任务
    tasks = db.execute_query("""
        SELECT hitl_task_id, step1_data
        FROM tender_hitl_tasks
        WHERE step1_data LIKE '%completed_response_file%'
    """)

    if not tasks:
        logger.info("没有找到需要迁移的任务")
        return

    logger.info(f"找到 {len(tasks)} 个任务包含 completed_response_file")

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for task in tasks:
        task_id = task['hitl_task_id']
        step1_data = json.loads(task['step1_data'])

        # 检查是否有completed_response_file
        completed_response = step1_data.get('completed_response_file')
        if not completed_response:
            skipped_count += 1
            continue

        # 获取source字段
        source = completed_response.get('source', 'unknown')

        # 确定目标字段
        target_field = None
        if source == 'business_response':
            target_field = 'business_response_file'
        elif source == 'point_to_point':
            target_field = 'technical_point_to_point_file'
        elif source == 'tech_proposal':
            target_field = 'technical_proposal_file'
        else:
            logger.warning(f"任务 {task_id}: 未知的source '{source}'，跳过")
            skipped_count += 1
            continue

        # 检查目标字段是否已存在
        if target_field in step1_data:
            logger.info(f"任务 {task_id}: {target_field} 已存在，跳过")
            skipped_count += 1
            continue

        # 创建新的文件信息（移除source字段）
        new_file_info = {
            'file_path': completed_response.get('file_path'),
            'filename': completed_response.get('filename'),
            'file_size': completed_response.get('file_size'),
            'saved_at': completed_response.get('saved_at'),
            'source_file': completed_response.get('source_file')
        }

        # 如果是技术方案，保留output_files字段
        if source == 'tech_proposal' and 'output_files' in completed_response:
            new_file_info['output_files'] = completed_response['output_files']

        logger.info(f"任务 {task_id}: 将 {source} 迁移到 {target_field}")
        logger.info(f"  - 文件名: {new_file_info['filename']}")
        logger.info(f"  - 文件路径: {new_file_info['file_path']}")

        if not dry_run:
            try:
                # 更新数据库
                step1_data[target_field] = new_file_info
                # 保留原有的completed_response_file，以防需要回滚
                # 如果需要删除，可以取消注释下面这行
                # del step1_data['completed_response_file']

                db.execute_query("""
                    UPDATE tender_hitl_tasks
                    SET step1_data = ?
                    WHERE hitl_task_id = ?
                """, (json.dumps(step1_data, ensure_ascii=False), task_id))

                migrated_count += 1
                logger.info(f"  ✓ 成功迁移")
            except Exception as e:
                logger.error(f"  ✗ 迁移失败: {str(e)}")
                error_count += 1
        else:
            logger.info(f"  ✓ (模拟模式，未实际修改)")
            migrated_count += 1

    # 打印总结
    logger.info("\n" + "=" * 60)
    logger.info("迁移总结:")
    logger.info(f"  - 总任务数: {len(tasks)}")
    logger.info(f"  - 成功迁移: {migrated_count}")
    logger.info(f"  - 跳过: {skipped_count}")
    logger.info(f"  - 错误: {error_count}")
    logger.info(f"  - 模式: {'模拟模式（未修改数据库）' if dry_run else '实际修改模式'}")
    logger.info("=" * 60)

    return migrated_count, skipped_count, error_count


def cleanup_old_field(dry_run=True):
    """
    清理旧的completed_response_file字段（可选）

    只有在确认新字段工作正常后才执行此操作
    """
    db = get_knowledge_base_db()

    tasks = db.execute_query("""
        SELECT hitl_task_id, step1_data
        FROM tender_hitl_tasks
        WHERE step1_data LIKE '%completed_response_file%'
    """)

    if not tasks:
        logger.info("没有找到需要清理的旧字段")
        return

    logger.info(f"找到 {len(tasks)} 个任务包含旧字段 completed_response_file")

    cleaned_count = 0

    for task in tasks:
        task_id = task['hitl_task_id']
        step1_data = json.loads(task['step1_data'])

        if 'completed_response_file' in step1_data:
            logger.info(f"任务 {task_id}: 删除 completed_response_file")

            if not dry_run:
                try:
                    del step1_data['completed_response_file']
                    db.execute_query("""
                        UPDATE tender_hitl_tasks
                        SET step1_data = ?
                        WHERE hitl_task_id = ?
                    """, (json.dumps(step1_data, ensure_ascii=False), task_id))
                    cleaned_count += 1
                    logger.info(f"  ✓ 成功删除")
                except Exception as e:
                    logger.error(f"  ✗ 删除失败: {str(e)}")
            else:
                logger.info(f"  ✓ (模拟模式，未实际删除)")
                cleaned_count += 1

    logger.info(f"\n清理完成: {cleaned_count} 个任务")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='迁移completed_response_file到独立字段')
    parser.add_argument('--execute', action='store_true',
                        help='实际执行迁移（默认为模拟模式）')
    parser.add_argument('--cleanup', action='store_true',
                        help='清理旧的completed_response_file字段（需要与--execute一起使用）')

    args = parser.parse_args()

    dry_run = not args.execute

    if dry_run:
        logger.info("=" * 60)
        logger.info("模拟模式：将显示迁移操作但不会修改数据库")
        logger.info("使用 --execute 参数来实际执行迁移")
        logger.info("=" * 60 + "\n")
    else:
        logger.warning("=" * 60)
        logger.warning("实际修改模式：将修改数据库！")
        logger.warning("=" * 60 + "\n")

    # 执行迁移
    migrate_completed_response_files(dry_run=dry_run)

    # 如果指定了cleanup参数，清理旧字段
    if args.cleanup:
        logger.info("\n" + "=" * 60)
        logger.info("开始清理旧字段...")
        logger.info("=" * 60 + "\n")
        cleanup_old_field(dry_run=dry_run)
