#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并测试用例JSON文件

用途:
- 将自动提取的测试用例合并到主JSON文件
- 自动去重(基于field_alias)
- 保留来源信息

使用方法:
    python tests/scripts/merge_test_cases.py

作者:AI Tender System
日期:2025-12-02
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_json(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, file_path):
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_test_cases(main_file, extracted_file, output_file):
    """合并测试用例"""

    print("=" * 70)
    print("📥 合并测试用例")
    print("=" * 70)
    print()

    # 加载两个JSON文件
    print(f"📖 加载主文件: {main_file.name}")
    main_data = load_json(main_file)

    print(f"📖 加载提取文件: {extracted_file.name}")
    extracted_data = load_json(extracted_file)

    # 统计信息
    main_count_before = sum(len(suite['test_cases']) for suite in main_data['test_suites'].values())
    extracted_count = sum(len(suite['test_cases']) for suite in extracted_data['test_suites'].values())

    print(f"📊 主文件现有测试用例: {main_count_before} 个")
    print(f"📊 提取文件测试用例: {extracted_count} 个")
    print()

    # 合并测试套件
    merged_count = 0
    duplicate_count = 0

    # 收集所有已存在的field_alias (用于去重)
    existing_fields = set()
    for suite_data in main_data['test_suites'].values():
        for test_case in suite_data['test_cases']:
            if 'field_alias' in test_case:
                existing_fields.add(test_case['field_alias'])

    # 合并提取的测试套件
    for suite_name, suite_data in extracted_data['test_suites'].items():
        # 映射提取的套件名到主文件的套件名
        # 例如: field_recognition_company_name_extracted -> field_recognition_company
        base_suite_name = suite_name.replace('_extracted', '').replace('_name', '')

        # 如果主文件中不存在这个套件,创建它
        if base_suite_name not in main_data['test_suites']:
            # 尝试找到最相似的套件
            similar_suites = []
            for s in main_data['test_suites'].keys():
                parts_s = s.split('_')
                parts_suite = suite_name.split('_')
                if len(parts_s) >= 3 and len(parts_suite) >= 3 and parts_s[2] == parts_suite[2]:
                    similar_suites.append(s)

            if similar_suites:
                base_suite_name = similar_suites[0]
            else:
                # 创建新套件
                main_data['test_suites'][base_suite_name] = {
                    "description": suite_data['description'],
                    "test_cases": []
                }

        # 合并测试用例
        for test_case in suite_data['test_cases']:
            field_alias = test_case.get('field_alias')

            # 检查是否重复
            if field_alias in existing_fields:
                duplicate_count += 1
                print(f"  ⚠️  跳过重复字段: {field_alias}")
                continue

            # 添加到主文件
            main_data['test_suites'][base_suite_name]['test_cases'].append(test_case)
            existing_fields.add(field_alias)
            merged_count += 1
            print(f"  ✓ 添加新字段: {field_alias} -> {base_suite_name}")

    # 更新统计信息
    main_count_after = sum(len(suite['test_cases']) for suite in main_data['test_suites'].values())

    main_data['version'] = '2.0'
    main_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    # 更新source_statistics
    if 'source_statistics' not in main_data:
        main_data['source_statistics'] = {}

    main_data['source_statistics']['total_cases'] = main_count_after
    main_data['source_statistics']['by_source_type'] = {
        'manual': main_count_before,
        'template': merged_count,
        'user_feedback': 0
    }

    # 保存合并后的文件
    print()
    print(f"💾 保存到: {output_file}")
    save_json(main_data, output_file)

    # 显示统计
    print()
    print("=" * 70)
    print("✅ 合并完成！")
    print("=" * 70)
    print(f"📊 合并前测试用例数: {main_count_before}")
    print(f"➕ 新增测试用例数: {merged_count}")
    print(f"⊗  跳过重复用例数: {duplicate_count}")
    print(f"📊 合并后测试用例数: {main_count_after}")
    print()
    print("📝 后续步骤:")
    print("  1. 查看合并结果: cat tests/data/business_response_test_cases.json")
    print("  2. 运行测试验证: pytest tests/unit/modules/test_business_response_text_filling.py -v")
    print("=" * 70)


def main():
    """主函数"""
    base_dir = Path(__file__).parent.parent.parent
    main_file = base_dir / "tests" / "data" / "business_response_test_cases.json"
    extracted_file = base_dir / "tests" / "data" / "business_response_test_cases_extracted.json"
    output_file = main_file  # 直接覆盖主文件

    # 检查文件是否存在
    if not main_file.exists():
        print(f"❌ 主文件不存在: {main_file}")
        sys.exit(1)

    if not extracted_file.exists():
        print(f"❌ 提取文件不存在: {extracted_file}")
        print("💡 请先运行: python tests/scripts/extract_test_cases_from_templates.py")
        sys.exit(1)

    # 备份主文件
    backup_file = main_file.with_suffix('.json.backup')
    print(f"💾 备份原文件到: {backup_file}")
    import shutil
    shutil.copy(main_file, backup_file)

    # 合并
    merge_test_cases(main_file, extracted_file, output_file)


if __name__ == "__main__":
    main()
