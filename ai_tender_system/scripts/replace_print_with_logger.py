#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量替换print语句为logger调用的脚本
"""

import re
import os
from pathlib import Path

def replace_print_in_file(file_path: Path) -> bool:
    """替换单个文件中的print语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 检查是否已经导入logger
        has_logger_import = 'from common.logger import get_module_logger' in content or 'from common import' in content

        # 如果文件中有print语句,需要处理
        if 'print(' in content:
            # 获取模块名(文件名去掉.py)
            module_name = file_path.stem

            # 添加logger导入(如果还没有)
            if not has_logger_import:
                # 找到最后一个import语句的位置
                import_pattern = r'((?:^from .+ import .+$|^import .+$)\n)'
                imports = list(re.finditer(import_pattern, content, re.MULTILINE))

                if imports:
                    last_import = imports[-1]
                    insert_pos = last_import.end()

                    # 插入logger导入
                    logger_import = f"\nfrom common.logger import get_module_logger\n\nlogger = get_module_logger(\"{module_name}\")\n"
                    content = content[:insert_pos] + logger_import + content[insert_pos:]

            # 替换print语句
            # 1. print(f"xxx") -> logger.info("xxx")
            content = re.sub(
                r'print\(f"(.+?)"\)',
                r'logger.info(f"\1")',
                content
            )

            # 2. print("xxx") -> logger.info("xxx")
            content = re.sub(
                r'print\("(.+?)"\)',
                r'logger.info("\1")',
                content
            )

            # 3. print(variable) -> logger.info(str(variable))
            content = re.sub(
                r'print\(([^"\']+)\)',
                r'logger.info(str(\1))',
                content
            )

        # 如果内容有变化,写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已处理: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"✗ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 获取ai_tender_system目录
    script_dir = Path(__file__).parent
    ai_tender_dir = script_dir.parent

    # 需要处理的目录列表
    target_dirs = [
        ai_tender_dir / 'web' / 'blueprints',
        ai_tender_dir / 'database'
    ]

    processed_count = 0

    for target_dir in target_dirs:
        if not target_dir.exists():
            continue

        print(f"\n处理目录: {target_dir}")
        for py_file in target_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue

            if replace_print_in_file(py_file):
                processed_count += 1

    print(f"\n总共处理了 {processed_count} 个文件")

if __name__ == '__main__':
    main()
