#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试电话字段处理问题
"""
import sys
import re
from pathlib import Path

# 添加项目路径
script_dir = Path(__file__).parent
project_root = script_dir / 'ai_tender_system'
sys.path.insert(0, str(project_root))

print("🔍 调试电话字段处理问题")
print("=" * 50)

# 测试不同的电话字段模式
test_cases = [
    "电话：_______",
    "电话：       ",
    "电话：_______________",
    "联系电话：_______",
    "固定电话：_______",
    "电话                                  电子邮件",
    "电话：010-63271000",  # 已经有内容的情况
]

# 公司电话数据
phone_value = "010-63271000"

print(f"📋 测试电话号码: {phone_value}")
print(f"🧪 测试 {len(test_cases)} 个不同格式:")

# 测试修复后的正则表达式
phone_patterns = [
    r'(电话[:：])(\s*[_\s]+)',                     # 表单式：电话：_____  (修复版)
    r'(联系电话[:：])(\s*[_\s]+)',                 # 表单式：联系电话：_____  (修复版)
    r'(固定电话[:：])(\s*[_\s]+)',                 # 表单式：固定电话：_____  (修复版)
    r'(电话)(\s{10,})(?=电子邮件|电子邮箱|邮箱)',    # 表格式：电话[大量空格]电子邮件
    r'(电话)(\s+)(?=\s*电子邮件|\s*电子邮箱|\s*邮箱)'  # 表格式：电话[空格]电子邮件
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n🔧 测试用例 #{i}: '{test_case}'")
    
    matched = False
    for j, pattern in enumerate(phone_patterns):
        match = re.search(pattern, test_case)
        if match:
            print(f"  ✅ 匹配模式 #{j+1}: {pattern}")
            print(f"     捕获组: {match.groups()}")
            
            # 模拟紧凑格式替换
            if len(match.groups()) >= 2:
                label = match.group(1)
                placeholder = match.group(2)
                
                # 构建替换结果
                if label.endswith('：') or label.endswith(':'):
                    new_text = f"{label}{phone_value}"
                else:
                    new_text = f"{label}：{phone_value}"
                
                # 如果有后续内容，保留
                remaining = test_case[match.end():]
                if remaining:
                    new_text += remaining
                
                print(f"     替换结果: '{new_text}'")
                matched = True
                break
    
    if not matched:
        print(f"  ❌ 无匹配模式")

print(f"\n🎯 特殊情况测试:")

# 测试具体的情况，模拟图片中看到的格式
specific_case = "电话：                    "
print(f"\n📍 具体案例: '{specific_case}'")

for j, pattern in enumerate(phone_patterns):
    match = re.search(pattern, specific_case)
    if match:
        print(f"  ✅ 匹配模式 #{j+1}: {pattern}")
        print(f"     捕获组: {match.groups()}")
        print(f"     捕获组1长度: {len(match.group(1)) if match.groups() else 0}")
        print(f"     捕获组2长度: {len(match.group(2)) if len(match.groups()) >= 2 else 0}")
        print(f"     捕获组2内容: '{match.group(2)}'" if len(match.groups()) >= 2 else "")
        
        # 检查捕获的占位符是否为空格或下划线
        if len(match.groups()) >= 2:
            placeholder = match.group(2)
            is_valid_placeholder = bool(re.match(r'^[_\s]+$', placeholder))
            print(f"     占位符有效性: {'✅' if is_valid_placeholder else '❌'}")

print(f"\n✅ 调试完成")