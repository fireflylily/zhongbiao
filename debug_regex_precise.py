#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确的正则表达式调试
"""
import re

def test_regex_backreference():
    """测试反向引用问题"""
    print("=== 精确正则反向引用测试 ===")
    
    text = "电话：_____________"
    field_name = "电话"
    field_value = "010-63271000"
    
    # 原始模式
    pattern = rf'({field_name}[:：]\s*)([_\s]*)'
    print(f"文本: '{text}'")
    print(f"模式: '{pattern}'")
    
    match = re.search(pattern, text)
    if match:
        print(f"匹配成功:")
        print(f"  - group(0): '{match.group(0)}'")
        print(f"  - group(1): '{match.group(1)}'")
        print(f"  - group(2): '{match.group(2)}'")
        
        # 测试不同的替换方式
        print(f"\n=== 测试不同的替换方式 ===")
        
        # 方式1: \\1 （原来的有问题的方式）
        try:
            result1 = re.sub(pattern, f'\\1{field_value}', text)
            print(f"方式1 (\\1): '{result1}'")
        except Exception as e:
            print(f"方式1错误: {e}")
        
        # 方式2: r'\1' （原始字符串）
        try:
            result2 = re.sub(pattern, rf'\1{field_value}', text)
            print(f"方式2 (r'\\1'): '{result2}'")
        except Exception as e:
            print(f"方式2错误: {e}")
            
        # 方式3: match.group(1) + field_value （直接使用匹配组）
        try:
            result3 = re.sub(pattern, f'{match.group(1)}{field_value}', text)
            print(f"方式3 (direct): '{result3}'")
        except Exception as e:
            print(f"方式3错误: {e}")
            
        # 方式4: 使用lambda函数
        try:
            result4 = re.sub(pattern, lambda m: f'{m.group(1)}{field_value}', text)
            print(f"方式4 (lambda): '{result4}'")
        except Exception as e:
            print(f"方式4错误: {e}")
    
    # 测试字符串字面意思分析
    print(f"\n=== 字符串字面意思分析 ===")
    print(f"\\1 as str: '{chr(1)}'")  # 这可能是问题所在！
    print(f"\\1 repr: {repr(chr(1))}")
    print(f"\\1 ord: {ord(chr(1))}")
    
    # 验证输出中的异常字符
    bad_output = "A0-63271000"
    print(f"\n异常输出分析: '{bad_output}'")
    for i, char in enumerate(bad_output):
        print(f"  位置{i}: '{char}' (ord: {ord(char)})")

def test_correct_replacement():
    """测试正确的替换方法"""
    print(f"\n=== 正确的替换方法测试 ===")
    
    test_cases = [
        "电话：_____________",
        "电话：010-63271000",
        "联系电话：_____________",
    ]
    
    field_value = "010-63271000"
    field_name = "电话"
    
    # 正确的模式和替换
    pattern = rf'({field_name}[:：]\s*)([_\s]*)'
    
    for text in test_cases:
        print(f"\n处理: '{text}'")
        match = re.search(pattern, text)
        if match:
            # 使用lambda函数确保正确替换
            result = re.sub(pattern, lambda m: f'{m.group(1)}{field_value}', text)
            print(f"  结果: '{result}'")
        else:
            print(f"  无匹配")

if __name__ == "__main__":
    test_regex_backreference()
    test_correct_replacement()