#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例查询和统计工具

功能:
- 按来源类型查询测试用例
- 按项目ID查询测试用例
- 按模板文件查询测试用例
- 统计各维度的测试用例分布
- 查找最常出现的字段变体

使用方法:
    # 查看所有统计
    python tests/scripts/query_test_cases.py --stats

    # 查询特定项目的测试用例
    python tests/scripts/query_test_cases.py --project 50

    # 查询特定模板的测试用例
    python tests/scripts/query_test_cases.py --template "第四部分  响应文件格式"

    # 查询手工创建的测试用例
    python tests/scripts/query_test_cases.py --source manual

    # 查询自动提取的测试用例
    python tests/scripts/query_test_cases.py --source template

    # 查找最高频的字段变体(Top 10)
    python tests/scripts/query_test_cases.py --top-fields 10

作者: AI Tender System
日期: 2025-12-02
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import argparse


def load_test_cases(file_path):
    """加载测试用例JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_test_case(test_case, indent=2):
    """格式化打印单个测试用例"""
    prefix = " " * indent
    print(f"{prefix}ID: {test_case.get('id', 'N/A')}")
    print(f"{prefix}字段别名: {test_case.get('field_alias', 'N/A')}")
    print(f"{prefix}标准字段: {test_case.get('expected_standard_field', 'N/A')}")

    source = test_case.get('source', {})
    print(f"{prefix}来源类型: {source.get('type', 'N/A')}")

    if source.get('type') == 'template':
        print(f"{prefix}项目ID: {source.get('project_id', 'N/A')}")
        print(f"{prefix}项目名称: {source.get('project_name', 'N/A')}")
        print(f"{prefix}模板文件: {source.get('template_file', 'N/A')}")
        print(f"{prefix}提取日期: {source.get('extracted_date', 'N/A')}")
    elif source.get('type') == 'manual':
        print(f"{prefix}创建日期: {source.get('created_date', 'N/A')}")

    print()


def query_by_source_type(data, source_type):
    """按来源类型查询"""
    print(f"\n{'='*70}")
    print(f"📋 来源类型: {source_type}")
    print(f"{'='*70}\n")

    count = 0
    for suite_name, suite_data in data['test_suites'].items():
        suite_count = 0
        suite_cases = []

        for test_case in suite_data['test_cases']:
            source = test_case.get('source', {})
            if source.get('type') == source_type:
                suite_cases.append(test_case)
                suite_count += 1
                count += 1

        if suite_cases:
            print(f"📦 测试套件: {suite_name}")
            print(f"   用例数: {suite_count}")
            print()
            for test_case in suite_cases:
                print_test_case(test_case, indent=4)

    print(f"{'='*70}")
    print(f"✅ 总计: {count} 个测试用例")
    print(f"{'='*70}")


def query_by_project(data, project_id):
    """按项目ID查询"""
    print(f"\n{'='*70}")
    print(f"📋 项目ID: {project_id}")
    print(f"{'='*70}\n")

    count = 0
    for suite_name, suite_data in data['test_suites'].items():
        suite_cases = []

        for test_case in suite_data['test_cases']:
            source = test_case.get('source', {})
            if source.get('project_id') == project_id:
                suite_cases.append(test_case)
                count += 1

        if suite_cases:
            print(f"📦 测试套件: {suite_name}")
            print(f"   用例数: {len(suite_cases)}")
            print()
            for test_case in suite_cases:
                print_test_case(test_case, indent=4)

    print(f"{'='*70}")
    print(f"✅ 总计: {count} 个测试用例")
    print(f"{'='*70}")


def query_by_template(data, template_keyword):
    """按模板文件名关键字查询"""
    print(f"\n{'='*70}")
    print(f"📋 模板文件关键字: {template_keyword}")
    print(f"{'='*70}\n")

    count = 0
    for suite_name, suite_data in data['test_suites'].items():
        suite_cases = []

        for test_case in suite_data['test_cases']:
            source = test_case.get('source', {})
            template_file = source.get('template_file', '')
            if template_keyword.lower() in template_file.lower():
                suite_cases.append(test_case)
                count += 1

        if suite_cases:
            print(f"📦 测试套件: {suite_name}")
            print(f"   用例数: {len(suite_cases)}")
            print()
            for test_case in suite_cases:
                print_test_case(test_case, indent=4)

    print(f"{'='*70}")
    print(f"✅ 总计: {count} 个测试用例")
    print(f"{'='*70}")


def show_statistics(data):
    """显示统计信息"""
    print(f"\n{'='*70}")
    print("📊 测试用例统计分析")
    print(f"{'='*70}\n")

    # 总体统计
    total_cases = sum(len(suite['test_cases']) for suite in data['test_suites'].values())
    print(f"📈 总体统计:")
    print(f"   总测试用例数: {total_cases}")
    print(f"   测试套件数: {len(data['test_suites'])}")
    print()

    # 按测试套件统计
    print("📦 按测试套件统计:")
    for suite_name, suite_data in data['test_suites'].items():
        count = len(suite_data['test_cases'])
        print(f"   {suite_name}: {count} 个用例")
    print()

    # 按来源类型统计
    source_stats = Counter()
    for suite_data in data['test_suites'].values():
        for test_case in suite_data['test_cases']:
            source_type = test_case.get('source', {}).get('type', 'unknown')
            source_stats[source_type] += 1

    print("🔖 按来源类型统计:")
    for source_type, count in source_stats.most_common():
        percentage = (count / total_cases * 100) if total_cases > 0 else 0
        print(f"   {source_type}: {count} 个用例 ({percentage:.1f}%)")
    print()

    # 按项目统计(仅template类型)
    project_stats = Counter()
    project_names = {}
    for suite_data in data['test_suites'].values():
        for test_case in suite_data['test_cases']:
            source = test_case.get('source', {})
            if source.get('type') == 'template':
                project_id = source.get('project_id', 'unknown')
                project_stats[project_id] += 1
                if project_id not in project_names:
                    project_names[project_id] = source.get('project_name', '未知项目')

    if project_stats:
        print("🏢 按项目统计(自动提取):")
        for project_id, count in project_stats.most_common():
            project_name = project_names.get(project_id, '未知项目')
            print(f"   项目 {project_id} ({project_name}): {count} 个用例")
        print()

    # 按模板文件统计
    template_stats = Counter()
    for suite_data in data['test_suites'].values():
        for test_case in suite_data['test_cases']:
            source = test_case.get('source', {})
            if source.get('type') == 'template':
                template_file = source.get('template_file', 'unknown')
                template_stats[template_file] += 1

    if template_stats:
        print("📄 按模板文件统计(Top 10):")
        for template_file, count in template_stats.most_common(10):
            print(f"   {template_file}: {count} 个用例")
        print()

    # 按标准字段统计
    field_stats = Counter()
    for suite_data in data['test_suites'].values():
        for test_case in suite_data['test_cases']:
            standard_field = test_case.get('expected_standard_field', 'unknown')
            field_stats[standard_field] += 1

    print("🏷️  按标准字段统计:")
    for field_name, count in field_stats.most_common():
        percentage = (count / total_cases * 100) if total_cases > 0 else 0
        print(f"   {field_name}: {count} 个用例 ({percentage:.1f}%)")
    print()

    print(f"{'='*70}")


def show_top_fields(data, top_n=10):
    """显示最常出现的字段别名"""
    print(f"\n{'='*70}")
    print(f"🔝 Top {top_n} 字段别名")
    print(f"{'='*70}\n")

    field_counter = Counter()
    field_standard = {}

    for suite_data in data['test_suites'].values():
        for test_case in suite_data['test_cases']:
            field_alias = test_case.get('field_alias', '')
            standard_field = test_case.get('expected_standard_field', '')
            field_counter[field_alias] += 1
            if field_alias not in field_standard:
                field_standard[field_alias] = standard_field

    for i, (field_alias, count) in enumerate(field_counter.most_common(top_n), 1):
        standard_field = field_standard.get(field_alias, 'unknown')
        print(f"{i:2d}. {field_alias}")
        print(f"    → 映射到: {standard_field}")
        print(f"    出现次数: {count}")
        print()

    print(f"{'='*70}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='测试用例查询和统计工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --stats                          显示所有统计信息
  %(prog)s --project 50                     查询项目50的测试用例
  %(prog)s --template "响应文件格式"        查询包含关键字的模板
  %(prog)s --source manual                  查询手工创建的测试用例
  %(prog)s --top-fields 10                  显示Top 10字段别名
        """
    )

    parser.add_argument('--stats', action='store_true',
                        help='显示所有统计信息')
    parser.add_argument('--project', type=str,
                        help='按项目ID查询')
    parser.add_argument('--template', type=str,
                        help='按模板文件名关键字查询')
    parser.add_argument('--source', type=str, choices=['manual', 'template', 'user_feedback'],
                        help='按来源类型查询')
    parser.add_argument('--top-fields', type=int, metavar='N',
                        help='显示Top N字段别名')
    parser.add_argument('--file', type=str,
                        default='tests/data/business_response_test_cases.json',
                        help='测试用例JSON文件路径 (默认: tests/data/business_response_test_cases.json)')

    args = parser.parse_args()

    # 加载数据
    base_dir = Path(__file__).parent.parent.parent
    json_file = base_dir / args.file

    if not json_file.exists():
        print(f"❌ 文件不存在: {json_file}")
        sys.exit(1)

    print(f"📖 加载测试用例: {json_file.name}")
    data = load_test_cases(json_file)

    # 执行查询
    if args.stats:
        show_statistics(data)
    elif args.project:
        query_by_project(data, args.project)
    elif args.template:
        query_by_template(data, args.template)
    elif args.source:
        query_by_source_type(data, args.source)
    elif args.top_fields:
        show_top_fields(data, args.top_fields)
    else:
        # 默认显示统计
        show_statistics(data)


if __name__ == "__main__":
    main()
