#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境完整性检查工具
功能：检测新机器上缺失的配置、数据库、文件等，并提供修复建议
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

# 颜色输出支持
class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


class EnvironmentChecker:
    """环境检查器"""

    def __init__(self):
        """初始化检查器"""
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []
        self.successes = []

    def check_all(self) -> Tuple[List[str], List[str], List[str]]:
        """执行所有检查"""
        print_header("AI标书系统 - 环境完整性检查")

        self.check_env_file()
        self.check_databases()
        self.check_data_directories()
        self.check_python_dependencies()
        self.check_config_files()
        self.check_migrations()

        return self.issues, self.warnings, self.successes

    def check_env_file(self):
        """检查环境配置文件"""
        print_header("1. 环境配置检查 (.env)")

        env_example = self.project_root / 'ai_tender_system' / '.env.example'
        env_file = self.project_root / 'ai_tender_system' / '.env'

        if not env_file.exists():
            print_error(f".env 文件不存在: {env_file}")
            self.issues.append("缺少 .env 配置文件")

            if env_example.exists():
                print_info(f"发现示例文件: {env_example}")
                print_info("修复命令:")
                print(f"    cp {env_example} {env_file}")
                print(f"    # 然后编辑 {env_file} 填入你的API密钥")
            return

        print_success(f".env 文件存在: {env_file}")

        # 检查关键环境变量
        required_vars = [
            ('ACCESS_TOKEN', '联通MaaS平台访问令牌'),
            ('SECRET_KEY', 'Flask会话密钥'),
        ]

        optional_vars = [
            ('OPENAI_API_KEY', 'OpenAI API密钥'),
            ('SHIHUANG_API_KEY', '始皇API密钥'),
        ]

        # 读取.env文件
        env_vars = {}
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

        # 检查必需变量
        for var_name, description in required_vars:
            if var_name in env_vars and env_vars[var_name] and \
               env_vars[var_name] not in ['your-api-key-here', 'your_secret_key_here']:
                print_success(f"{var_name}: 已配置")
                self.successes.append(f"{var_name} 已正确配置")
            else:
                print_error(f"{var_name}: 未配置或使用示例值")
                self.issues.append(f"环境变量 {var_name} ({description}) 未正确配置")

        # 检查可选变量
        for var_name, description in optional_vars:
            if var_name in env_vars and env_vars[var_name] and \
               env_vars[var_name] not in ['your-api-key-here', 'sk-your-openai-api-key-here']:
                print_success(f"{var_name}: 已配置 (可选)")
                self.successes.append(f"{var_name} 已配置")
            else:
                print_warning(f"{var_name}: 未配置 (可选，{description})")
                self.warnings.append(f"{var_name} 未配置 (可选)")

    def check_databases(self):
        """检查数据库文件"""
        print_header("2. 数据库文件检查")

        data_dir = self.project_root / 'ai_tender_system' / 'data'

        databases = [
            ('knowledge_base.db', '主数据库（企业、知识库、文档等）'),
            ('tender.db', '招标项目数据库'),
            ('resume_library.db', '简历库数据库'),
        ]

        missing_dbs = []
        for db_name, description in databases:
            db_path = data_dir / db_name
            if db_path.exists():
                size_kb = db_path.stat().st_size / 1024
                if size_kb > 10:  # 大于10KB说明有数据
                    print_success(f"{db_name}: 存在 ({size_kb:.1f} KB) - {description}")
                    self.successes.append(f"{db_name} 存在且包含数据")
                else:
                    print_warning(f"{db_name}: 存在但为空 ({size_kb:.1f} KB) - {description}")
                    self.warnings.append(f"{db_name} 可能为空数据库")
            else:
                print_error(f"{db_name}: 不存在 - {description}")
                missing_dbs.append((db_name, description))
                self.issues.append(f"数据库 {db_name} 不存在")

        if missing_dbs:
            print_info("\n数据库修复选项:")
            print("  选项1: 从备份恢复（如果你有数据库导出文件）")
            print("  选项2: 让系统自动创建空数据库（首次运行时）")
            print("  选项3: 从另一台机器复制数据库文件")
            print("\n推荐: 使用 scripts/export_database.py 从旧机器导出数据")

    def check_data_directories(self):
        """检查数据目录"""
        print_header("3. 数据目录检查")

        data_dir = self.project_root / 'ai_tender_system' / 'data'

        directories = [
            ('uploads', '上传的文件（招标文档、资质等）'),
            ('outputs', '生成的文档（标书、方案等）'),
            ('logs', '系统日志'),
            ('temp', '临时文件'),
        ]

        for dir_name, description in directories:
            dir_path = data_dir / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.glob('*')))
                print_success(f"{dir_name}/: 存在 ({file_count} 个文件) - {description}")
                self.successes.append(f"{dir_name}/ 目录存在")

                if file_count == 0 and dir_name in ['uploads', 'outputs']:
                    print_warning(f"  ⚠️  {dir_name}/ 目录为空，可能缺少历史文件")
                    self.warnings.append(f"{dir_name}/ 目录为空")
            else:
                print_warning(f"{dir_name}/: 不存在 - {description}")
                print_info(f"  将在首次运行时自动创建")
                self.warnings.append(f"{dir_name}/ 目录不存在（将自动创建）")

    def check_python_dependencies(self):
        """检查Python依赖"""
        print_header("4. Python依赖检查")

        requirements_file = self.project_root / 'requirements.txt'
        requirements_lock = self.project_root / 'requirements.lock'

        if not requirements_file.exists():
            print_error("requirements.txt 不存在")
            self.issues.append("缺少 requirements.txt 文件")
            return

        print_success(f"requirements.txt 存在")

        if requirements_lock.exists():
            print_success(f"requirements.lock 存在（版本已锁定）")
            print_info("建议使用: pip install -r requirements.lock")
            self.successes.append("依赖版本已锁定")
        else:
            print_warning("requirements.lock 不存在")
            print_info("建议创建版本锁定文件: pip freeze > requirements.lock")
            self.warnings.append("缺少依赖版本锁定文件")

        # 检查关键依赖是否已安装
        critical_packages = [
            'Flask',
            'Flask-WTF',
            'faiss-cpu',
            'sentence-transformers',
            'python-docx',
            'PyMuPDF',
        ]

        try:
            import importlib
            for package in critical_packages:
                # 转换包名（faiss-cpu -> faiss）
                import_name = package.replace('-', '_').lower()
                if import_name == 'python_docx':
                    import_name = 'docx'
                elif import_name == 'pymupdf':
                    import_name = 'fitz'
                elif import_name == 'faiss_cpu':
                    import_name = 'faiss'

                try:
                    importlib.import_module(import_name)
                    print_success(f"  {package}: 已安装")
                except ImportError:
                    print_error(f"  {package}: 未安装")
                    self.issues.append(f"Python包 {package} 未安装")
        except Exception as e:
            print_warning(f"依赖检查失败: {e}")

    def check_config_files(self):
        """检查配置文件"""
        print_header("5. 配置文件检查")

        config_files = [
            ('ai_tender_system/common/config.py', '核心配置文件'),
            ('ai_tender_system/database/knowledge_base_schema.sql', '数据库Schema'),
        ]

        for file_path, description in config_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print_success(f"{file_path}: 存在 - {description}")
                self.successes.append(f"{file_path} 存在")
            else:
                print_error(f"{file_path}: 不存在 - {description}")
                self.issues.append(f"配置文件 {file_path} 不存在")

    def check_migrations(self):
        """检查数据库迁移文件"""
        print_header("6. 数据库迁移文件检查")

        migrations_dir = self.project_root / 'ai_tender_system' / 'database' / 'migrations'

        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob('*.sql'))
            print_success(f"migrations/ 目录存在 ({len(migration_files)} 个迁移文件)")
            self.successes.append(f"找到 {len(migration_files)} 个数据库迁移文件")

            if migration_files:
                print_info("  迁移文件列表:")
                for migration in sorted(migration_files):
                    print(f"    - {migration.name}")
        else:
            print_warning("migrations/ 目录不存在")
            self.warnings.append("缺少数据库迁移目录")

    def generate_report(self):
        """生成检查报告"""
        print_header("检查报告汇总")

        print(f"\n{Colors.BOLD}统计信息:{Colors.ENDC}")
        print(f"  ✅ 成功: {len(self.successes)} 项")
        print(f"  ⚠️  警告: {len(self.warnings)} 项")
        print(f"  ❌ 错误: {len(self.issues)} 项")

        if self.issues:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ 严重问题 ({len(self.issues)} 项):{Colors.ENDC}")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")

        if self.warnings:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  警告 ({len(self.warnings)} 项):{Colors.ENDC}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.issues and not self.warnings:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 恭喜！环境检查全部通过！{Colors.ENDC}")
            return True

        # 生成修复建议
        print_header("修复建议")

        if self.issues or self.warnings:
            print("\n📋 推荐修复步骤:\n")

            if any('.env' in issue for issue in self.issues):
                print("1️⃣  配置环境变量:")
                print("   cp ai_tender_system/.env.example ai_tender_system/.env")
                print("   vim ai_tender_system/.env  # 填入你的API密钥\n")

            if any('数据库' in issue for issue in self.issues):
                print("2️⃣  恢复数据库（选择一种方式）:")
                print("   方式A: 从导出文件恢复")
                print("     python scripts/restore_env.sh exports/backup_YYYYMMDD.tar.gz")
                print("   方式B: 从另一台机器复制")
                print("     scp user@old-machine:path/to/ai_tender_system/data/*.db ai_tender_system/data/")
                print("   方式C: 让系统自动创建空数据库")
                print("     python -m ai_tender_system.web.app  # 首次运行会自动创建\n")

            if any('依赖' in issue or 'Python包' in issue for issue in self.issues):
                print("3️⃣  安装Python依赖:")
                if (self.project_root / 'requirements.lock').exists():
                    print("   pip install -r requirements.lock  # 推荐（版本已锁定）")
                else:
                    print("   pip install -r requirements.txt\n")

            if any('uploads' in warning or 'outputs' in warning for warning in self.warnings):
                print("4️⃣  恢复历史文件（可选）:")
                print("   scp -r user@old-machine:path/to/ai_tender_system/data/uploads ai_tender_system/data/")
                print("   scp -r user@old-machine:path/to/ai_tender_system/data/outputs ai_tender_system/data/\n")

        print(f"\n{Colors.OKBLUE}💡 提示:{Colors.ENDC}")
        print("  - 完整的环境同步指南: 查看 DEPLOYMENT_CHECKLIST.md")
        print("  - 数据库导出工具: python scripts/export_database.py")
        print("  - 环境配置向导: python scripts/setup_wizard.py")

        return len(self.issues) == 0


def main():
    """主函数"""
    checker = EnvironmentChecker()

    try:
        issues, warnings, successes = checker.check_all()
        success = checker.generate_report()

        # 返回适当的退出码
        if issues:
            sys.exit(1)  # 有严重问题
        elif warnings:
            sys.exit(2)  # 只有警告
        else:
            sys.exit(0)  # 完美

    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}检查已取消{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}检查过程出错: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
