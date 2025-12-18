#!/usr/bin/env python3
"""
智能测试运行器
根据修改的文件，自动选择相关测试运行

使用方法:
  python scripts/smart_test.py              # 检测修改的文件并运行相关测试
  python scripts/smart_test.py --suite quick    # 运行快速测试套件
  python scripts/smart_test.py --core           # 只运行核心测试
  python scripts/smart_test.py --file path/to/file.py  # 查看特定文件的测试
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from typing import List, Set

# 颜色定义
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def load_test_config() -> dict:
    """加载测试配置"""
    config_path = Path(__file__).parent.parent / 'tests' / 'test_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_modified_files() -> List[str]:
    """获取修改的文件（未提交的修改）"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f and f.endswith('.py')]
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}错误：无法获取git修改文件{Colors.NC}")
        return []

def get_tests_for_file(file_path: str, config: dict) -> List[str]:
    """根据文件路径获取相关测试"""
    file_to_tests = config.get('file_to_tests', {})

    # 精确匹配
    if file_path in file_to_tests:
        return file_to_tests[file_path]

    # 模糊匹配（检查是否是关键文件的子模块）
    for key in file_to_tests:
        if file_path.startswith(key.rsplit('/', 1)[0]):
            return file_to_tests[key]

    return []

def is_critical_file(file_path: str, config: dict) -> bool:
    """检查是否是关键文件"""
    critical_files = config.get('critical_files', [])
    return any(file_path.startswith(cf.rsplit('/', 1)[0]) for cf in critical_files)

def run_tests(tests: List[str], verbose: bool = True) -> bool:
    """运行测试并返回是否成功"""
    if not tests:
        print(f"{Colors.YELLOW}没有需要运行的测试{Colors.NC}")
        return True

    print(f"{Colors.BLUE}运行以下测试：{Colors.NC}")
    for test in tests:
        print(f"  - {test}")
    print()

    cmd = ['pytest'] + tests
    if verbose:
        cmd.extend(['-v', '--tb=short'])
    else:
        cmd.append('-q')

    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='智能测试运行器')
    parser.add_argument('--suite', choices=['quick', 'business_response', 'full'],
                       help='运行预定义的测试套件')
    parser.add_argument('--core', action='store_true',
                       help='只运行核心测试')
    parser.add_argument('--file', type=str,
                       help='查看特定文件的相关测试（不运行）')
    parser.add_argument('--list', action='store_true',
                       help='列出所有修改文件的相关测试（不运行）')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='安静模式（减少输出）')

    args = parser.parse_args()

    # 加载配置
    try:
        config = load_test_config()
    except FileNotFoundError:
        print(f"{Colors.RED}错误：找不到测试配置文件 tests/test_config.json{Colors.NC}")
        sys.exit(1)

    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}智能测试运行器{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print()

    # 处理 --file 参数
    if args.file:
        tests = get_tests_for_file(args.file, config)
        if tests:
            print(f"{Colors.GREEN}文件 {args.file} 的相关测试：{Colors.NC}")
            for test in tests:
                print(f"  - {test}")
        else:
            print(f"{Colors.YELLOW}文件 {args.file} 没有配置相关测试{Colors.NC}")
        sys.exit(0)

    # 处理 --core 参数
    if args.core:
        core_tests = config['core_tests']['tests']
        print(f"{Colors.YELLOW}运行核心测试（{len(core_tests)}个）{Colors.NC}")
        print()
        success = run_tests(core_tests, not args.quiet)
        sys.exit(0 if success else 1)

    # 处理 --suite 参数
    if args.suite:
        suite = config['test_suites'][args.suite]
        print(f"{Colors.YELLOW}运行测试套件: {args.suite}{Colors.NC}")
        print(f"{Colors.YELLOW}描述: {suite['description']}{Colors.NC}")
        print()
        success = run_tests(suite['tests'], not args.quiet)
        sys.exit(0 if success else 1)

    # 默认行为：检测修改的文件并运行相关测试
    modified_files = get_modified_files()

    if not modified_files:
        print(f"{Colors.GREEN}没有检测到修改的Python文件{Colors.NC}")
        print(f"{Colors.BLUE}提示：使用 --suite quick 运行快速测试{Colors.NC}")
        sys.exit(0)

    print(f"{Colors.YELLOW}检测到 {len(modified_files)} 个修改的文件：{Colors.NC}")
    for f in modified_files:
        is_critical = is_critical_file(f, config)
        marker = f"{Colors.RED}🔴 [关键]{Colors.NC}" if is_critical else ""
        print(f"  - {f} {marker}")
    print()

    # 收集所有相关测试
    all_tests: Set[str] = set()
    has_critical_changes = False

    for file in modified_files:
        tests = get_tests_for_file(file, config)
        if tests:
            all_tests.update(tests)
            print(f"{Colors.BLUE}▶ {file}{Colors.NC}")
            for test in tests:
                print(f"    → {test}")

        if is_critical_file(file, config):
            has_critical_changes = True
            # 关键文件修改，添加核心测试
            all_tests.update(config['core_tests']['tests'])

    print()

    if not all_tests:
        print(f"{Colors.YELLOW}修改的文件没有配置相关测试{Colors.NC}")
        print(f"{Colors.BLUE}运行快速测试套件...{Colors.NC}")
        all_tests.update(config['test_suites']['quick']['tests'])

    if has_critical_changes:
        print(f"{Colors.RED}⚠️  检测到关键文件被修改！{Colors.NC}")
        print(f"{Colors.RED}⚠️  将运行核心测试确保功能正常{Colors.NC}")
        print()

    # 处理 --list 参数
    if args.list:
        print(f"{Colors.GREEN}需要运行的测试列表：{Colors.NC}")
        for test in sorted(all_tests):
            print(f"  - {test}")
        sys.exit(0)

    # 运行测试
    print(f"{Colors.YELLOW}准备运行 {len(all_tests)} 个测试...{Colors.NC}")
    print()

    success = run_tests(list(all_tests), not args.quiet)

    print()
    if success:
        print(f"{Colors.GREEN}{'='*60}{Colors.NC}")
        print(f"{Colors.GREEN}✅ 所有测试通过！{Colors.NC}")
        print(f"{Colors.GREEN}{'='*60}{Colors.NC}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{'='*60}{Colors.NC}")
        print(f"{Colors.RED}❌ 测试失败！{Colors.NC}")
        print(f"{Colors.RED}{'='*60}{Colors.NC}")
        print()
        print(f"{Colors.YELLOW}建议：{Colors.NC}")
        print("1. 查看失败的测试详情")
        print("2. 修复问题")
        print("3. 重新运行: python scripts/smart_test.py")
        sys.exit(1)

if __name__ == '__main__':
    main()
