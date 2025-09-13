#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试电话+邮箱紧邻格式正则表达式
"""
import re

def test_email_pattern():
    """测试电话+邮箱正则表达式"""
    
    test_cases = [
        "电话：010-63271000电子邮箱：",
        "电话: 010-63271000电子邮箱：",
        "联系电话：010-63271000电子邮件：",
        "电话：010-63271000电子邮件：",
    ]
    
    # 当前的正则模式
    email_pattern = r'(电话|联系电话)[:：]\s*([0-9\-]+)(电子邮箱|电子邮件)[:：]\s*([_\s]*)'
    
    print("=== 电话+邮箱正则表达式调试 ===")
    print(f"正则模式: {email_pattern}")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- 测试 {i+1}: '{test_case}' ---")
        
        match = re.search(email_pattern, test_case)
        if match:
            print("✅ 匹配成功:")
            print(f"  - group(0): '{match.group(0)}'")
            print(f"  - group(1): '{match.group(1)}' (电话字段)")
            print(f"  - group(2): '{match.group(2)}' (电话号码)")
            print(f"  - group(3): '{match.group(3)}' (邮件字段)")
            print(f"  - group(4): '{match.group(4)}' (邮件占位符)")
            
            # 模拟处理
            phone_field = match.group(1)
            phone_number = match.group(2)
            email_field = match.group(3)
            email_value = "lvhe@smartsteps.com"
            
            result = f"{phone_field}：{phone_number}{email_field}：{email_value}"
            print(f"  - 处理结果: '{result}'")
        else:
            print("❌ 无匹配")
    
    # 测试改进的正则模式
    print(f"\n=== 改进的正则模式测试 ===")
    improved_pattern = r'(电话|联系电话)[:：]\s*([0-9\-]+)\s*(电子邮箱|电子邮件)[:：]\s*([_\s]*)'
    print(f"改进模式: {improved_pattern}")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- 改进测试 {i+1}: '{test_case}' ---")
        
        match = re.search(improved_pattern, test_case)
        if match:
            print("✅ 匹配成功:")
            print(f"  - group(0): '{match.group(0)}'")
            print(f"  - group(1): '{match.group(1)}' (电话字段)")
            print(f"  - group(2): '{match.group(2)}' (电话号码)")
            print(f"  - group(3): '{match.group(3)}' (邮件字段)")
            print(f"  - group(4): '{match.group(4)}' (邮件占位符)")
            
            # 模拟处理
            phone_field = match.group(1)
            phone_number = match.group(2)
            email_field = match.group(3)
            email_value = "lvhe@smartsteps.com"
            
            result = f"{phone_field}：{phone_number}{email_field}：{email_value}"
            print(f"  - 处理结果: '{result}'")
        else:
            print("❌ 无匹配")

if __name__ == "__main__":
    test_email_pattern()