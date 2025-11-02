#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整环境备份工具
功能：
1. 导出所有数据库
2. 打包上传文件和输出文件
3. 创建环境配置模板
4. 生成备份清单
"""

import sqlite3
import os
import sys
import json
import tarfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class EnvironmentBackup:
    """环境备份工具"""

    def __init__(self, output_dir: Optional[str] = None, include_files: bool = True):
        """
        初始化备份工具

        Args:
            output_dir: 输出目录（默认为 exports/）
            include_files: 是否包含上传和输出文件（默认True）
        """
        self.project_root = project_root
        self.output_dir = Path(output_dir) if output_dir else project_root / "exports"
        self.output_dir.mkdir(exist_ok=True)
        self.include_files = include_files

        # 生成备份时间戳
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"backup_{self.timestamp}"
        self.backup_dir = self.output_dir / self.backup_name
        self.backup_dir.mkdir(exist_ok=True)

        self.manifest = {
            'backup_date': datetime.now().isoformat(),
            'backup_version': '1.0',
            'databases': [],
            'file_directories': [],
            'total_size': 0,
            'warnings': []
        }

    def backup_all(self) -> str:
        """
        执行完整备份

        Returns:
            备份压缩包路径
        """
        print("=" * 80)
        print(f"{'环境完整备份工具':^80}")
        print("=" * 80)
        print()

        try:
            # 1. 备份数据库
            self._backup_databases()

            # 2. 备份文件目录
            if self.include_files:
                self._backup_file_directories()

            # 3. 备份环境配置模板
            self._backup_env_template()

            # 4. 生成依赖清单
            self._backup_dependencies()

            # 5. 写入manifest
            self._write_manifest()

            # 6. 创建压缩包
            archive_path = self._create_archive()

            # 7. 清理临时目录
            shutil.rmtree(self.backup_dir)

            print("\n" + "=" * 80)
            print(f"{'✅ 备份完成！':^80}")
            print("=" * 80)
            print(f"\n备份文件: {archive_path}")
            print(f"备份大小: {self._format_size(Path(archive_path).stat().st_size)}")
            print(f"\n包含内容:")
            print(f"  - {len(self.manifest['databases'])} 个数据库")
            print(f"  - {len(self.manifest['file_directories'])} 个文件目录")
            print(f"  - 环境配置模板")
            print(f"  - Python依赖清单")

            if self.manifest['warnings']:
                print(f"\n⚠️  警告 ({len(self.manifest['warnings'])}):")
                for warning in self.manifest['warnings']:
                    print(f"  - {warning}")

            print(f"\n恢复命令:")
            print(f"  python3 scripts/restore_environment.py {archive_path}")

            return str(archive_path)

        except Exception as e:
            print(f"\n❌ 备份失败: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _backup_databases(self):
        """备份数据库"""
        print("📦 备份数据库...")

        data_dir = self.project_root / "ai_tender_system" / "data"
        databases = [
            ('knowledge_base.db', '主数据库'),
            ('tender.db', '招标项目数据库'),
            ('resume_library.db', '简历库数据库'),
        ]

        db_dir = self.backup_dir / 'databases'
        db_dir.mkdir(exist_ok=True)

        for db_name, description in databases:
            db_path = data_dir / db_name

            if not db_path.exists():
                warning = f"数据库不存在，跳过: {db_name}"
                print(f"  ⚠️  {warning}")
                self.manifest['warnings'].append(warning)
                continue

            db_size = db_path.stat().st_size
            if db_size == 0:
                warning = f"数据库为空，跳过: {db_name}"
                print(f"  ⚠️  {warning}")
                self.manifest['warnings'].append(warning)
                continue

            # 导出SQL
            sql_file = db_dir / f"{db_path.stem}.sql"
            self._export_database_to_sql(db_path, sql_file)

            # 同时复制原始.db文件（用于快速恢复）
            shutil.copy2(db_path, db_dir / db_name)

            db_info = {
                'name': db_name,
                'description': description,
                'size': db_size,
                'size_formatted': self._format_size(db_size),
                'sql_file': sql_file.name,
                'db_file': db_name
            }
            self.manifest['databases'].append(db_info)
            self.manifest['total_size'] += db_size

            print(f"  ✅ {db_name} ({self._format_size(db_size)}) - {description}")

    def _export_database_to_sql(self, db_path: Path, output_file: Path):
        """导出数据库为SQL"""
        conn = sqlite3.connect(db_path)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"-- Database: {db_path.name}\n")
                f.write(f"-- Export date: {datetime.now().isoformat()}\n\n")
                f.write("PRAGMA foreign_keys=OFF;\n")
                f.write("BEGIN TRANSACTION;\n\n")

                for line in conn.iterdump():
                    if line.startswith('PRAGMA') or line.startswith('BEGIN') or line.startswith('COMMIT'):
                        continue
                    f.write(f"{line}\n")

                f.write("\nCOMMIT;\n")
                f.write("PRAGMA foreign_keys=ON;\n")
        finally:
            conn.close()

    def _backup_file_directories(self):
        """备份文件目录"""
        print("\n📁 备份文件目录...")

        data_dir = self.project_root / "ai_tender_system" / "data"
        directories = [
            ('uploads', '上传的文件'),
            ('outputs', '生成的文档'),
        ]

        for dir_name, description in directories:
            source_dir = data_dir / dir_name

            if not source_dir.exists():
                warning = f"目录不存在，跳过: {dir_name}"
                print(f"  ⚠️  {warning}")
                self.manifest['warnings'].append(warning)
                continue

            # 统计文件
            files = list(source_dir.rglob('*'))
            file_count = len([f for f in files if f.is_file()])
            total_size = sum(f.stat().st_size for f in files if f.is_file())

            if file_count == 0:
                warning = f"目录为空，跳过: {dir_name}"
                print(f"  ⚠️  {warning}")
                self.manifest['warnings'].append(warning)
                continue

            # 复制整个目录
            dest_dir = self.backup_dir / 'files' / dir_name
            shutil.copytree(source_dir, dest_dir)

            dir_info = {
                'name': dir_name,
                'description': description,
                'file_count': file_count,
                'size': total_size,
                'size_formatted': self._format_size(total_size)
            }
            self.manifest['file_directories'].append(dir_info)
            self.manifest['total_size'] += total_size

            print(f"  ✅ {dir_name}/ ({file_count} 个文件, {self._format_size(total_size)}) - {description}")

    def _backup_env_template(self):
        """备份环境配置模板"""
        print("\n⚙️  备份环境配置模板...")

        env_example = self.project_root / 'ai_tender_system' / '.env.example'
        env_file = self.project_root / 'ai_tender_system' / '.env'

        config_dir = self.backup_dir / 'config'
        config_dir.mkdir(exist_ok=True)

        # 复制.env.example
        if env_example.exists():
            shutil.copy2(env_example, config_dir / '.env.example')
            print(f"  ✅ .env.example")

        # 创建带说明的.env模板（不包含实际密钥）
        if env_file.exists():
            env_template = config_dir / '.env.template'
            with open(env_file, 'r', encoding='utf-8') as f_in:
                with open(env_template, 'w', encoding='utf-8') as f_out:
                    f_out.write("# 环境配置模板（从原.env文件生成）\n")
                    f_out.write("# 请填入你的实际API密钥\n\n")
                    for line in f_in:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            # 隐藏敏感值
                            if any(keyword in key.upper() for keyword in ['KEY', 'TOKEN', 'SECRET', 'PASSWORD']):
                                f_out.write(f"{key}=<YOUR_{key}_HERE>\n")
                            else:
                                f_out.write(f"{line}\n")
                        else:
                            f_out.write(f"{line}\n")
            print(f"  ✅ .env.template (已脱敏)")

    def _backup_dependencies(self):
        """备份依赖清单"""
        print("\n📦 备份Python依赖...")

        config_dir = self.backup_dir / 'config'
        config_dir.mkdir(exist_ok=True)

        # 复制requirements.txt
        requirements_txt = self.project_root / 'requirements.txt'
        if requirements_txt.exists():
            shutil.copy2(requirements_txt, config_dir / 'requirements.txt')
            print(f"  ✅ requirements.txt")

        # 生成精确版本清单
        requirements_lock = config_dir / 'requirements.lock'
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'freeze'],
                capture_output=True,
                text=True,
                check=True
            )
            with open(requirements_lock, 'w', encoding='utf-8') as f:
                f.write(f"# Python {sys.version}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(result.stdout)
            print(f"  ✅ requirements.lock (精确版本)")
        except Exception as e:
            warning = f"无法生成requirements.lock: {e}"
            print(f"  ⚠️  {warning}")
            self.manifest['warnings'].append(warning)

    def _write_manifest(self):
        """写入备份清单"""
        manifest_file = self.backup_dir / 'MANIFEST.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=2)

        # 生成可读的README
        readme_file = self.backup_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f"# 环境备份 - {self.timestamp}\n\n")
            f.write(f"**备份时间**: {self.manifest['backup_date']}\n\n")
            f.write(f"**备份版本**: {self.manifest['backup_version']}\n\n")

            f.write("## 包含内容\n\n")
            f.write("### 数据库\n\n")
            for db in self.manifest['databases']:
                f.write(f"- **{db['name']}**: {db['description']} ({db['size_formatted']})\n")

            f.write("\n### 文件目录\n\n")
            for dir_info in self.manifest['file_directories']:
                f.write(f"- **{dir_info['name']}/**: {dir_info['description']} ")
                f.write(f"({dir_info['file_count']} 个文件, {dir_info['size_formatted']})\n")

            f.write("\n## 恢复方法\n\n")
            f.write("```bash\n")
            f.write(f"python3 scripts/restore_environment.py backup_{self.timestamp}.tar.gz\n")
            f.write("```\n\n")
            f.write("或手动恢复:\n\n")
            f.write("```bash\n")
            f.write("# 1. 解压备份\n")
            f.write(f"tar -xzf backup_{self.timestamp}.tar.gz\n\n")
            f.write("# 2. 恢复数据库\n")
            f.write("cp backup_*/databases/*.db ai_tender_system/data/\n\n")
            f.write("# 3. 恢复文件\n")
            f.write("cp -r backup_*/files/* ai_tender_system/data/\n\n")
            f.write("# 4. 配置环境变量\n")
            f.write("cp backup_*/config/.env.example ai_tender_system/.env\n")
            f.write("vim ai_tender_system/.env  # 填入API密钥\n\n")
            f.write("# 5. 安装依赖\n")
            f.write("pip install -r backup_*/config/requirements.lock\n")
            f.write("```\n")

    def _create_archive(self) -> str:
        """创建压缩包"""
        print("\n📦 创建压缩包...")

        archive_path = self.output_dir / f"{self.backup_name}.tar.gz"

        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(self.backup_dir, arcname=self.backup_name)

        print(f"  ✅ {archive_path.name}")
        return str(archive_path)

    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='环境完整备份工具')
    parser.add_argument('--output', '-o', help='输出目录', default=None)
    parser.add_argument('--no-files', action='store_true', help='不包含上传和输出文件')

    args = parser.parse_args()

    try:
        backup = EnvironmentBackup(
            output_dir=args.output,
            include_files=not args.no_files
        )
        archive_path = backup.backup_all()

        print(f"\n💡 提示:")
        print(f"  - 将备份文件复制到新机器: scp {archive_path} user@new-machine:/path/")
        print(f"  - 在新机器上恢复: python3 scripts/restore_environment.py backup_*.tar.gz")
        print(f"  - 查看备份清单: tar -tzf {archive_path}")

    except KeyboardInterrupt:
        print("\n\n备份已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n备份失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
