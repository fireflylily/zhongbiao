#!/usr/bin/env python3
"""
数据库导出脚本
将SQLite数据库导出为SQL格式，用于同步到Railway或其他环境
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DatabaseExporter:
    """数据库导出器"""

    def __init__(self, db_path: str, output_dir: str = None):
        """
        初始化导出器

        Args:
            db_path: 数据库文件路径
            output_dir: 输出目录（默认为exports/目录）
        """
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir) if output_dir else project_root / "exports"
        self.output_dir.mkdir(exist_ok=True)

    def export_to_sql(self) -> str:
        """
        导出数据库为SQL文件

        Returns:
            导出的SQL文件路径
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = self.db_path.stem
        output_file = self.output_dir / f"{db_name}_export_{timestamp}.sql"

        print(f"正在导出数据库: {self.db_path}")
        print(f"输出文件: {output_file}")

        # 连接数据库
        conn = sqlite3.connect(self.db_path)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write(f"-- Database export: {db_name}\n")
                f.write(f"-- Export date: {datetime.now().isoformat()}\n")
                f.write(f"-- Source: {self.db_path}\n")
                f.write("\n")
                f.write("-- Disable foreign key checks during import\n")
                f.write("PRAGMA foreign_keys=OFF;\n")
                f.write("BEGIN TRANSACTION;\n\n")

                # 导出schema和数据
                for line in conn.iterdump():
                    # 跳过PRAGMA和COMMIT/BEGIN语句
                    if line.startswith('PRAGMA') or line.startswith('BEGIN') or line.startswith('COMMIT'):
                        continue
                    f.write(f"{line}\n")

                # 写入文件尾
                f.write("\nCOMMIT;\n")
                f.write("PRAGMA foreign_keys=ON;\n")

            # 获取文件大小
            file_size = output_file.stat().st_size
            file_size_mb = file_size / 1024 / 1024

            print(f"✓ 导出成功!")
            print(f"  文件大小: {file_size_mb:.2f} MB")
            print(f"  保存位置: {output_file}")

            # 统计信息
            self._print_statistics(conn)

            return str(output_file)

        finally:
            conn.close()

    def _print_statistics(self, conn: sqlite3.Connection):
        """打印数据库统计信息"""
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()

        print("\n数据库统计:")
        print(f"  表数量: {len(tables)}")

        total_rows = 0
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            total_rows += row_count
            if row_count > 0:
                print(f"  - {table_name}: {row_count} 行")

        print(f"  总记录数: {total_rows}")


def main():
    """主函数"""
    # 数据库文件列表
    databases = [
        project_root / "ai_tender_system" / "data" / "knowledge_base.db",
        project_root / "ai_tender_system" / "data" / "tender.db",
        project_root / "ai_tender_system" / "data" / "resume_library.db",
    ]

    print("=" * 60)
    print("数据库导出工具")
    print("=" * 60)
    print()

    exported_files = []

    for db_path in databases:
        if not db_path.exists():
            print(f"⚠ 跳过不存在的数据库: {db_path}")
            print()
            continue

        # 检查数据库大小
        db_size = db_path.stat().st_size
        if db_size == 0:
            print(f"⚠ 跳过空数据库: {db_path}")
            print()
            continue

        try:
            exporter = DatabaseExporter(db_path)
            output_file = exporter.export_to_sql()
            exported_files.append(output_file)
            print()
        except Exception as e:
            print(f"✗ 导出失败: {e}")
            print()

    # 总结
    print("=" * 60)
    print("导出完成!")
    print("=" * 60)
    print(f"\n成功导出 {len(exported_files)} 个数据库文件:")
    for file in exported_files:
        print(f"  - {file}")

    print("\n下一步:")
    print("1. 安装 Railway CLI: brew install railway 或访问 https://railway.app/cli")
    print("2. 登录 Railway: railway login")
    print("3. 链接项目: railway link")
    print("4. 上传数据库文件或通过Railway Shell执行SQL文件")
    print("\n详细说明请查看: DATABASE_SYNC_GUIDE.md")


if __name__ == "__main__":
    main()
