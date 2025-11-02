#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境恢复工具
功能：从备份文件恢复完整环境
"""

import os
import sys
import json
import tarfile
import shutil
from pathlib import Path
from typing import Dict, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class EnvironmentRestore:
    """环境恢复工具"""

    def __init__(self, backup_file: str, force: bool = False):
        """
        初始化恢复工具

        Args:
            backup_file: 备份文件路径
            force: 是否强制覆盖现有文件
        """
        self.backup_file = Path(backup_file)
        self.force = force
        self.project_root = project_root
        self.temp_dir = project_root / '.restore_temp'
        self.manifest = None

    def restore_all(self):
        """执行完整恢复"""
        print("=" * 80)
        print(f"{'环境恢复工具':^80}")
        print("=" * 80)
        print()

        if not self.backup_file.exists():
            print(f"❌ 备份文件不存在: {self.backup_file}")
            sys.exit(1)

        print(f"备份文件: {self.backup_file}")
        print(f"文件大小: {self._format_size(self.backup_file.stat().st_size)}")
        print()

        try:
            # 1. 解压备份文件
            self._extract_backup()

            # 2. 读取manifest
            self._load_manifest()

            # 3. 显示备份信息
            self._show_backup_info()

            # 4. 确认恢复
            if not self.force and not self._confirm_restore():
                print("\n恢复已取消")
                return

            # 5. 恢复数据库
            self._restore_databases()

            # 6. 恢复文件目录
            self._restore_files()

            # 7. 恢复配置文件
            self._restore_config()

            # 8. 显示后续步骤
            self._show_next_steps()

            print("\n" + "=" * 80)
            print(f"{'✅ 恢复完成！':^80}")
            print("=" * 80)

        except KeyboardInterrupt:
            print("\n\n恢复已取消")
            sys.exit(130)
        except Exception as e:
            print(f"\n❌ 恢复失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            # 清理临时目录
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

    def _extract_backup(self):
        """解压备份文件"""
        print("📦 解压备份文件...")

        self.temp_dir.mkdir(exist_ok=True)

        with tarfile.open(self.backup_file, 'r:gz') as tar:
            tar.extractall(self.temp_dir)

        # 查找备份目录（应该只有一个）
        backup_dirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
        if len(backup_dirs) != 1:
            raise ValueError("备份文件格式错误：找到多个或没有备份目录")

        self.backup_root = backup_dirs[0]
        print(f"  ✅ 解压到: {self.backup_root}")

    def _load_manifest(self):
        """读取备份清单"""
        manifest_file = self.backup_root / 'MANIFEST.json'

        if not manifest_file.exists():
            raise FileNotFoundError("未找到备份清单文件 MANIFEST.json")

        with open(manifest_file, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)

    def _show_backup_info(self):
        """显示备份信息"""
        print("\n📋 备份信息:")
        print(f"  备份时间: {self.manifest['backup_date']}")
        print(f"  备份版本: {self.manifest['backup_version']}")
        print(f"  总大小: {self._format_size(self.manifest['total_size'])}")

        print(f"\n包含内容:")
        print(f"  - {len(self.manifest['databases'])} 个数据库")
        for db in self.manifest['databases']:
            print(f"    • {db['name']}: {db['description']} ({db['size_formatted']})")

        if self.manifest['file_directories']:
            print(f"  - {len(self.manifest['file_directories'])} 个文件目录")
            for dir_info in self.manifest['file_directories']:
                print(f"    • {dir_info['name']}/: {dir_info['file_count']} 个文件 ({dir_info['size_formatted']})")

        if self.manifest.get('warnings'):
            print(f"\n  ⚠️  备份时的警告:")
            for warning in self.manifest['warnings']:
                print(f"    - {warning}")

    def _confirm_restore(self) -> bool:
        """确认恢复操作"""
        print()
        print("⚠️  警告: 恢复操作将覆盖现有数据！")
        print()

        # 检查冲突
        conflicts = []
        data_dir = self.project_root / 'ai_tender_system' / 'data'

        for db in self.manifest['databases']:
            db_path = data_dir / db['name']
            if db_path.exists():
                conflicts.append(f"数据库: {db['name']}")

        for dir_info in self.manifest.get('file_directories', []):
            dir_path = data_dir / dir_info['name']
            if dir_path.exists() and any(dir_path.iterdir()):
                conflicts.append(f"目录: {dir_info['name']}/")

        if conflicts:
            print("将覆盖以下现有内容:")
            for conflict in conflicts:
                print(f"  - {conflict}")
            print()

        response = input("确认继续恢复？[y/N] ").strip().lower()
        return response in ['y', 'yes']

    def _restore_databases(self):
        """恢复数据库"""
        print("\n📦 恢复数据库...")

        data_dir = self.project_root / 'ai_tender_system' / 'data'
        data_dir.mkdir(exist_ok=True)

        db_dir = self.backup_root / 'databases'

        for db in self.manifest['databases']:
            # 优先使用.db文件（快速恢复）
            db_file = db_dir / db['db_file']
            target_path = data_dir / db['name']

            if db_file.exists():
                shutil.copy2(db_file, target_path)
                print(f"  ✅ {db['name']} ({db['size_formatted']})")
            else:
                # 如果.db文件不存在，尝试从SQL恢复
                sql_file = db_dir / db['sql_file']
                if sql_file.exists():
                    self._restore_from_sql(sql_file, target_path)
                    print(f"  ✅ {db['name']} (从SQL恢复)")
                else:
                    print(f"  ❌ {db['name']} - 备份文件缺失")

    def _restore_from_sql(self, sql_file: Path, db_path: Path):
        """从SQL文件恢复数据库"""
        import sqlite3

        # 删除旧数据库
        if db_path.exists():
            db_path.unlink()

        conn = sqlite3.connect(db_path)
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql = f.read()
                conn.executescript(sql)
            conn.commit()
        finally:
            conn.close()

    def _restore_files(self):
        """恢复文件目录"""
        if not self.manifest.get('file_directories'):
            return

        print("\n📁 恢复文件目录...")

        data_dir = self.project_root / 'ai_tender_system' / 'data'
        files_dir = self.backup_root / 'files'

        for dir_info in self.manifest['file_directories']:
            source_dir = files_dir / dir_info['name']
            target_dir = data_dir / dir_info['name']

            if source_dir.exists():
                # 删除旧目录
                if target_dir.exists():
                    shutil.rmtree(target_dir)

                # 复制新目录
                shutil.copytree(source_dir, target_dir)
                print(f"  ✅ {dir_info['name']}/ ({dir_info['file_count']} 个文件)")
            else:
                print(f"  ❌ {dir_info['name']}/ - 备份目录缺失")

    def _restore_config(self):
        """恢复配置文件"""
        print("\n⚙️  恢复配置文件...")

        config_dir = self.backup_root / 'config'
        env_template = config_dir / '.env.template'
        env_example = config_dir / '.env.example'
        env_target = self.project_root / 'ai_tender_system' / '.env'

        # 如果.env不存在，从模板创建
        if not env_target.exists():
            if env_template.exists():
                shutil.copy2(env_template, env_target)
                print(f"  ✅ 从模板创建 .env 文件")
                print(f"  ⚠️  请编辑 {env_target} 填入你的API密钥")
            elif env_example.exists():
                shutil.copy2(env_example, env_target)
                print(f"  ✅ 从示例创建 .env 文件")
                print(f"  ⚠️  请编辑 {env_target} 填入你的API密钥")
        else:
            print(f"  ℹ️  .env 文件已存在，跳过")

        # 复制requirements文件
        requirements_lock = config_dir / 'requirements.lock'
        if requirements_lock.exists():
            shutil.copy2(requirements_lock, self.project_root / 'requirements.lock')
            print(f"  ✅ requirements.lock")

    def _show_next_steps(self):
        """显示后续步骤"""
        print("\n📋 后续步骤:")

        env_file = self.project_root / 'ai_tender_system' / '.env'

        steps = []

        # 检查.env配置
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'YOUR_' in content or 'your-api-key-here' in content:
                    steps.append(("配置API密钥", f"vim {env_file}", "填入你的实际API密钥"))

        # 检查依赖
        requirements_lock = self.project_root / 'requirements.lock'
        if requirements_lock.exists():
            steps.append(("安装Python依赖", "pip install -r requirements.lock", ""))

        # 运行环境检查
        steps.append(("运行环境检查", "python3 scripts/check_env.py", "确认环境完整性"))

        # 启动应用
        steps.append(("启动应用", "python3 -m ai_tender_system.web.app", ""))

        if steps:
            for i, (title, command, note) in enumerate(steps, 1):
                print(f"\n{i}. {title}:")
                print(f"   {command}")
                if note:
                    print(f"   # {note}")

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

    parser = argparse.ArgumentParser(description='环境恢复工具')
    parser.add_argument('backup_file', help='备份文件路径 (*.tar.gz)')
    parser.add_argument('--force', '-f', action='store_true', help='强制覆盖，不提示确认')

    args = parser.parse_args()

    restore = EnvironmentRestore(args.backup_file, force=args.force)
    restore.restore_all()


if __name__ == "__main__":
    main()
