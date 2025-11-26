#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理数据库中文件不存在的资质记录

功能:
- 检查所有资质记录的文件是否存在
- 删除文件不存在的记录
- 生成清理报告

使用方法:
    # 预览模式(不实际删除)
    python3 scripts/clean_invalid_qualifications.py --dry-run

    # 实际清理
    python3 scripts/clean_invalid_qualifications.py

    # 只清理指定公司
    python3 scripts/clean_invalid_qualifications.py --company-id 1

    # 指定数据库路径(阿里云使用)
    python3 scripts/clean_invalid_qualifications.py --db /path/to/knowledge_base.db
"""

import sqlite3
import argparse
from pathlib import Path
import os
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def resolve_file_path(file_path: str, base_dir: Path) -> Path:
    """
    解析文件路径(支持相对路径和绝对路径)

    Args:
        file_path: 数据库中的文件路径
        base_dir: 项目根目录

    Returns:
        解析后的绝对路径
    """
    if not file_path:
        return None

    path = Path(file_path)

    # 如果是绝对路径,直接返回
    if path.is_absolute():
        return path

    # 如果是相对路径,基于项目根目录解析
    return base_dir / file_path


def clean_invalid_qualifications(db_path: str, company_id: int = None, dry_run: bool = True):
    """
    清理文件不存在的资质记录

    Args:
        db_path: 数据库路径
        company_id: 公司ID(可选,不指定则清理所有公司)
        dry_run: 是否为预览模式(不实际删除)
    """
    # 确定项目根目录(数据库所在目录的上级的上级)
    db_path_obj = Path(db_path).resolve()
    project_root = db_path_obj.parent.parent  # data/knowledge_base.db -> data -> project_root

    print(f"{'='*60}")
    print(f"数据库清理工具")
    print(f"{'='*60}")
    print(f"数据库路径: {db_path}")
    print(f"项目根目录: {project_root}")
    print(f"公司筛选: {f'company_id={company_id}' if company_id else '所有公司'}")
    print(f"运行模式: {'预览模式(不删除)' if dry_run else '实际清理模式'}")
    print(f"{'='*60}\n")

    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 使用字典模式
    cursor = conn.cursor()

    # 构建查询SQL
    if company_id:
        query = """
        SELECT qualification_id, company_id, qualification_key,
               original_filename, file_path, upload_time
        FROM company_qualifications
        WHERE company_id = ?
        ORDER BY company_id, qualification_key
        """
        params = (company_id,)
    else:
        query = """
        SELECT qualification_id, company_id, qualification_key,
               original_filename, file_path, upload_time
        FROM company_qualifications
        ORDER BY company_id, qualification_key
        """
        params = ()

    # 查询所有记录
    cursor.execute(query, params)
    records = cursor.fetchall()

    print(f"📊 共查询到 {len(records)} 条资质记录\n")

    # 统计信息
    total_checked = 0
    invalid_records = []
    valid_records = 0

    # 检查每条记录
    for record in records:
        total_checked += 1
        qual_id = record['qualification_id']
        comp_id = record['company_id']
        qual_key = record['qualification_key']
        filename = record['original_filename']
        file_path = record['file_path']
        upload_time = record['upload_time']

        # 解析文件路径
        resolved_path = resolve_file_path(file_path, project_root)

        # 检查文件是否存在
        if resolved_path and resolved_path.exists():
            valid_records += 1
            if total_checked <= 5:  # 只显示前5个有效记录
                print(f"  ✅ [ID:{qual_id}] {qual_key} - {filename}")
        else:
            invalid_records.append({
                'qualification_id': qual_id,
                'company_id': comp_id,
                'qualification_key': qual_key,
                'filename': filename,
                'file_path': file_path,
                'resolved_path': str(resolved_path) if resolved_path else 'N/A',
                'upload_time': upload_time
            })
            print(f"  ❌ [ID:{qual_id}] 公司{comp_id} - {qual_key} - {filename}")
            print(f"     路径: {file_path}")
            print(f"     解析: {resolved_path}")
            print(f"     时间: {upload_time}")
            print()

    # 输出统计
    print(f"\n{'='*60}")
    print(f"检查完成!")
    print(f"{'='*60}")
    print(f"总记录数: {total_checked}")
    print(f"有效记录: {valid_records}")
    print(f"无效记录: {len(invalid_records)}")
    print(f"{'='*60}\n")

    # 如果没有无效记录,结束
    if not invalid_records:
        print("✅ 所有记录都有效,无需清理!")
        conn.close()
        return

    # 显示将要删除的记录
    print(f"将要删除的 {len(invalid_records)} 条记录:")
    for idx, rec in enumerate(invalid_records, 1):
        print(f"  {idx}. [ID:{rec['qualification_id']}] 公司{rec['company_id']} - {rec['qualification_key']} - {rec['filename']}")

    # 如果是预览模式,不执行删除
    if dry_run:
        print(f"\n⚠️  当前为预览模式,未实际删除。")
        print(f"如需实际清理,请去掉 --dry-run 参数重新运行。")
        conn.close()
        return

    # 实际删除模式:请求用户确认
    print(f"\n⚠️  即将删除 {len(invalid_records)} 条无效记录!")
    confirm = input("确认删除? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("❌ 取消删除操作")
        conn.close()
        return

    # 执行删除
    deleted_count = 0
    for rec in invalid_records:
        try:
            cursor.execute(
                "DELETE FROM company_qualifications WHERE qualification_id = ?",
                (rec['qualification_id'],)
            )
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败 [ID:{rec['qualification_id']}]: {e}")

    # 提交事务
    conn.commit()
    conn.close()

    print(f"\n✅ 清理完成!")
    print(f"成功删除: {deleted_count} 条记录")


def main():
    parser = argparse.ArgumentParser(
        description='清理数据库中文件不存在的资质记录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览模式(默认)
  python3 scripts/clean_invalid_qualifications.py --dry-run

  # 实际清理
  python3 scripts/clean_invalid_qualifications.py

  # 只清理公司1的记录
  python3 scripts/clean_invalid_qualifications.py --company-id 1

  # 阿里云上使用
  python3 scripts/clean_invalid_qualifications.py --db /var/www/ai_tender_system/data/knowledge_base.db
        """
    )

    parser.add_argument(
        '--db',
        type=str,
        default='ai_tender_system/data/knowledge_base.db',
        help='数据库路径(默认: ai_tender_system/data/knowledge_base.db)'
    )

    parser.add_argument(
        '--company-id',
        type=int,
        default=None,
        help='只清理指定公司的记录(可选)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='预览模式,只显示将要删除的记录,不实际删除'
    )

    args = parser.parse_args()

    # 检查数据库文件是否存在
    if not os.path.exists(args.db):
        print(f"❌ 数据库文件不存在: {args.db}")
        sys.exit(1)

    # 执行清理
    clean_invalid_qualifications(args.db, args.company_id, args.dry_run)


if __name__ == '__main__':
    main()
