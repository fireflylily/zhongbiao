#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Excel文件导入测试用例到JSON

用途：
- 将 business_response_test_cases.xlsx 转换为 JSON 格式
- 支持在Excel中批量编辑后导入
- 自动验证数据完整性

使用方法：
    python tests/scripts/import_from_excel.py

输入：
    tests/data/business_response_test_cases.xlsx

输出：
    tests/data/business_response_test_cases.json (会覆盖原文件)

作者：AI Tender System
日期：2025-12-02
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    print("❌ 缺少依赖包，请先安装：")
    print("   pip install pandas openpyxl")
    sys.exit(1)


def import_from_excel():
    """从Excel导入测试用例到JSON"""

    # 文件路径
    script_dir = Path(__file__).parent
    excel_file = script_dir.parent / "data" / "business_response_test_cases.xlsx"
    json_file = script_dir.parent / "data" / "business_response_test_cases.json"

    # 检查Excel文件是否存在
    if not excel_file.exists():
        print(f"❌ Excel文件不存在: {excel_file}")
        print("💡 提示: 请先运行 export_to_excel.py 生成Excel文件")
        return False

    # 备份原JSON文件
    if json_file.exists():
        backup_file = json_file.with_suffix('.json.backup')
        print(f"💾 备份原文件: {backup_file}")
        import shutil
        shutil.copy(json_file, backup_file)

    print(f"📖 正在读取: {excel_file}")

    # 读取所有sheet
    try:
        excel_data = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
    except Exception as e:
        print(f"❌ 读取Excel失败: {e}")
        return False

    # 构建JSON结构
    output = {
        "version": "1.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "description": "商务应答文字填充功能测试用例数据",
        "test_suites": {}
    }

    # 处理每个sheet
    for sheet_name, df in excel_data.items():
        # 跳过概览和示例数据sheet
        if sheet_name in ['概览', '示例数据']:
            continue

        # 处理NaN值
        df = df.where(pd.notnull(df), None)

        # 转换为字典列表
        test_cases = df.to_dict('records')

        # 清理数据（移除空值）
        cleaned_cases = []
        for case in test_cases:
            cleaned_case = {k: v for k, v in case.items() if v is not None}
            if cleaned_case:  # 只添加非空用例
                cleaned_cases.append(cleaned_case)

        if cleaned_cases:
            output['test_suites'][sheet_name] = {
                "description": f"{sheet_name}测试",
                "test_cases": cleaned_cases
            }
            print(f"  ✓ 已导入测试套件: {sheet_name} ({len(cleaned_cases)} 个用例)")

    # 处理示例数据
    if '示例数据' in excel_data:
        sample_df = excel_data['示例数据']
        sample_data = {}
        for _, row in sample_df.iterrows():
            if pd.notnull(row.get('字段')) and pd.notnull(row.get('值')):
                sample_data[row['字段']] = row['值']

        if sample_data:
            output['sample_data'] = {
                "description": "测试用的示例公司数据",
                "data": sample_data
            }
            print(f"  ✓ 已导入示例数据 ({len(sample_data)} 个字段)")

    # 写入JSON
    print(f"💾 正在写入: {json_file}")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 验证JSON
    print("🔍 验证JSON格式...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json.load(f)
        print("  ✓ JSON格式验证通过")
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON格式错误: {e}")
        return False

    print(f"✅ 导入成功: {json_file}")
    print(f"📊 文件大小: {json_file.stat().st_size / 1024:.1f} KB")

    # 统计信息
    total_cases = sum(len(suite['test_cases']) for suite in output['test_suites'].values())
    print(f"📈 总计: {len(output['test_suites'])} 个测试套件, {total_cases} 个测试用例")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("📥 Excel测试用例导入工具")
    print("=" * 60)
    print()

    success = import_from_excel()

    print()
    print("=" * 60)
    if success:
        print("✅ 导入完成！")
        print()
        print("📝 后续步骤:")
        print("  1. 运行测试验证: pytest tests/unit/modules/test_business_response_text_filling.py -v")
        print("  2. 如果测试失败，检查导入的数据是否正确")
        print("  3. 提交更新: git add tests/data/business_response_test_cases.json")
    else:
        print("❌ 导入失败！")
        print()
        print("🔧 排查步骤:")
        print("  1. 检查Excel文件是否存在")
        print("  2. 检查Excel格式是否正确")
        print("  3. 查看上面的错误信息")
        sys.exit(1)
    print("=" * 60)
