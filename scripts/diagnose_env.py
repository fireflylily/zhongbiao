#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量诊断工具
检查环境变量中是否包含不可见字符（换行符、空格等）
"""

import os
import sys

def diagnose_env_variable(var_name):
    """诊断单个环境变量"""
    value = os.getenv(var_name, '')

    print(f"\n{'='*60}")
    print(f"检查环境变量: {var_name}")
    print(f"{'='*60}")

    if not value:
        print(f"❌ 环境变量 {var_name} 未设置或为空")
        return False

    print(f"原始值长度: {len(value)}")
    print(f"原始值 (repr): {repr(value)}")

    # 检查不可见字符
    issues = []

    if '\n' in value:
        issues.append("包含换行符 (\\n)")
    if '\r' in value:
        issues.append("包含回车符 (\\r)")
    if '\t' in value:
        issues.append("包含制表符 (\\t)")
    if value.strip() != value:
        issues.append(f"前后有空格 (前{len(value) - len(value.lstrip())}个，后{len(value) - len(value.rstrip())}个)")

    if issues:
        print(f"\n⚠️ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")

        cleaned_value = value.strip()
        print(f"\n✅ 清理后的值: {cleaned_value}")
        print(f"✅ 清理后长度: {len(cleaned_value)}")
        return cleaned_value
    else:
        print(f"✅ 无问题")
        return value

def main():
    """主函数"""
    print("="*60)
    print("环境变量诊断工具")
    print("="*60)

    # 需要检查的环境变量
    env_vars = [
        'OPENAI_API_ENDPOINT',
        'UNICOM_BASE_URL',
        'ACCESS_TOKEN',
        'OPENAI_API_KEY',
        'SHIHUANG_API_KEY',
    ]

    results = {}
    for var in env_vars:
        cleaned = diagnose_env_variable(var)
        if cleaned:
            results[var] = cleaned

    # 生成修复建议
    print("\n" + "="*60)
    print("修复建议")
    print("="*60)

    if results:
        print("\n在Railway中更新以下环境变量值:")
        for var, value in results.items():
            if value != os.getenv(var, ''):
                print(f"\n{var}=")
                print(f"  旧值: {repr(os.getenv(var, ''))}")
                print(f"  新值: {value}")
    else:
        print("所有环境变量正常!")

if __name__ == "__main__":
    main()
