#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资质文件数据迁移脚本
将现有的JSON存储的资质信息迁移到数据库中
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根路径到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.database import KnowledgeBaseDB
from common.logger import get_module_logger
from common.config import get_config

logger = get_module_logger("migrate_qualifications")


def migrate_company_qualifications():
    """迁移公司资质文件数据"""
    config = get_config()
    db = KnowledgeBaseDB()

    companies_dir = config.get_path('config') / 'companies'
    migrated_count = 0
    error_count = 0

    if not companies_dir.exists():
        logger.warning(f"公司配置目录不存在: {companies_dir}")
        return migrated_count, error_count

    # 遍历所有公司JSON文件
    for company_file in companies_dir.glob("*.json"):
        try:
            with open(company_file, 'r', encoding='utf-8') as f:
                company_data = json.load(f)

            # 提取公司ID（从文件名或JSON数据）
            company_id_str = company_data.get('id', company_file.stem)

            # 检查公司在数据库中是否存在
            companies = db.get_companies()
            company_id = None
            for company in companies:
                if (str(company['company_id']) == company_id_str or
                    company.get('company_name') == company_data.get('companyName')):
                    company_id = company['company_id']
                    break

            if not company_id:
                logger.warning(f"公司 {company_id_str} 在数据库中不存在，跳过迁移")
                continue

            # 迁移资质文件信息
            qualifications = company_data.get('qualifications', {})
            if not qualifications:
                logger.info(f"公司 {company_id} 没有资质文件")
                continue

            for qual_key, qual_info in qualifications.items():
                try:
                    # 构建文件路径
                    safe_filename = qual_info.get('safe_filename', '')
                    if safe_filename:
                        # 检查多个可能的文件位置
                        possible_paths = [
                            companies_dir / 'qualifications' / company_id_str / safe_filename,
                            project_root / 'qualifications' / company_id_str / safe_filename,
                            config.get_path('uploads') / 'qualifications' / str(company_id) / safe_filename
                        ]

                        file_path = None
                        for path in possible_paths:
                            if path.exists():
                                file_path = str(path)
                                break

                        if not file_path:
                            logger.warning(f"资质文件不存在: {safe_filename}")
                            file_path = str(possible_paths[0])  # 使用第一个路径作为默认值
                    else:
                        file_path = ''

                    # 转换时间格式
                    upload_time = qual_info.get('upload_time')
                    if isinstance(upload_time, (int, float)):
                        # Unix时间戳
                        upload_time = datetime.fromtimestamp(upload_time).isoformat()
                    elif isinstance(upload_time, str) and 'T' not in upload_time:
                        # 可能是其他格式，保持原样或转换
                        pass

                    # 保存到数据库
                    qualification_id = db.save_company_qualification(
                        company_id=company_id,
                        qualification_key=qual_key,
                        qualification_name=qual_info.get('filename', qual_key),
                        original_filename=qual_info.get('filename', ''),
                        safe_filename=safe_filename,
                        file_path=file_path,
                        file_size=qual_info.get('file_size', 0) or qual_info.get('size', 0),
                        file_type=Path(safe_filename).suffix[1:] if safe_filename else '',
                        custom_name=qual_info.get('custom_name'),
                        upload_by='migration_script'
                    )

                    if qualification_id:
                        migrated_count += 1
                        logger.info(f"成功迁移资质: 公司{company_id} - {qual_key}")
                    else:
                        error_count += 1
                        logger.error(f"迁移失败: 公司{company_id} - {qual_key}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"迁移资质文件失败 {qual_key}: {e}")

        except Exception as e:
            error_count += 1
            logger.error(f"处理公司文件失败 {company_file}: {e}")

    return migrated_count, error_count


def backup_json_files():
    """备份原有的JSON文件"""
    config = get_config()
    companies_dir = config.get_path('config') / 'companies'
    backup_dir = companies_dir.parent / 'backup_before_migration'

    if not companies_dir.exists():
        return

    backup_dir.mkdir(exist_ok=True)

    # 备份公司JSON文件
    for company_file in companies_dir.glob("*.json"):
        backup_file = backup_dir / company_file.name
        backup_file.write_text(company_file.read_text(encoding='utf-8'), encoding='utf-8')
        logger.info(f"备份文件: {company_file.name}")


def main():
    """主函数"""
    print("=== 资质文件数据迁移脚本 ===")

    # 备份原始数据
    print("1. 备份原始JSON文件...")
    backup_json_files()

    # 执行迁移
    print("2. 开始迁移资质文件数据...")
    migrated_count, error_count = migrate_company_qualifications()

    # 报告结果
    print(f"\n=== 迁移完成 ===")
    print(f"成功迁移: {migrated_count} 个资质文件")
    print(f"失败数量: {error_count} 个")

    if error_count > 0:
        print(f"请检查日志文件查看详细错误信息")
        return 1
    else:
        print("所有资质文件迁移成功！")
        return 0


if __name__ == "__main__":
    exit(main())