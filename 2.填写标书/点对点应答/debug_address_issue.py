#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试地址字段删除传真标签的问题
"""

import re

def debug_address_pattern():
    """调试地址字段的正则匹配问题"""
    
    # 模拟问题文本（一行中包含地址和传真）
    problem_text = "地址：                                      北京市西城区金融大街21号传真"
    
    print("=== 地址字段正则匹配调试 ===")
    print(f"问题文本: '{problem_text}'")
    
    # 当前有问题的模式
    current_patterns = [
        r'(地址[:：])\s*(.*?)$', 
        r'^(地址)\s*(.*?)$'
    ]
    
    for pattern_str in current_patterns:
        pattern = re.compile(pattern_str)
        match = pattern.search(problem_text)
        
        if match:
            print(f"\n❌ 问题模式: {pattern_str}")
            print(f"完整匹配: '{match.group(0)}'")
            print(f"标签部分: '{match.group(1)}'")
            if len(match.groups()) >= 2:
                print(f"内容部分: '{match.group(2)}'")
                print(f"问题: 内容部分包含了'传真'标签")
    
    print("\n=== 改进的正则模式建议 ===")
    
    # 改进的模式建议
    improved_patterns = [
        r'(地址[:：])\s*([^传真]*?)(?=传真|$)',  # 匹配到"传真"之前停止
        r'(地址[:：])\s*([^传]*?)(?=传|$)',      # 匹配到"传"字之前停止
        r'(地址[:：])\s*(\S+(?:\s+\S+)*?)(?:\s+传真|$)',  # 匹配非空格内容，遇到"传真"停止
    ]
    
    for pattern_str in improved_patterns:
        pattern = re.compile(pattern_str)
        match = pattern.search(problem_text)
        
        if match:
            print(f"\n✅ 改进模式: {pattern_str}")
            print(f"完整匹配: '{match.group(0)}'")
            print(f"标签部分: '{match.group(1)}'")
            if len(match.groups()) >= 2:
                content = match.group(2).strip()
                print(f"内容部分: '{content}'")
                remaining = problem_text.replace(match.group(0), '', 1)
                print(f"剩余部分: '{remaining}'")
                print(f"改进效果: 保留了传真标签")


def test_improved_pattern():
    """测试改进后的模式"""
    print("\n=== 测试改进后的模式 ===")
    
    test_cases = [
        "地址：                                      北京市西城区金融大街21号传真",
        "地址：北京市东城区王府井大街200号七层711室传真：010-12345678",
        "地址：上海市浦东新区陆家嘴环路1000号传真号码：021-12345678",
        "地址：广州市天河区珠江新城传真",
        "地址：深圳市南山区科技园",  # 没有传真的情况
    ]
    
    # 使用改进的模式
    improved_pattern = r'(地址[:：])\s*([^传]*?)(?=传|$)'
    pattern = re.compile(improved_pattern)
    
    for text in test_cases:
        print(f"\n测试文本: '{text}'")
        match = pattern.search(text)
        
        if match:
            label = match.group(1)
            content = match.group(2).strip()
            remaining = text[match.end():]
            
            print(f"  标签: '{label}'")
            print(f"  地址内容: '{content}'")
            print(f"  剩余内容: '{remaining}'")
            
            # 模拟填写结果
            new_address = "北京市西城区金融大街21号"
            result = f"{label}{new_address}"
            if remaining:
                result += remaining
            print(f"  填写结果: '{result}'")
        else:
            print("  无匹配")


if __name__ == '__main__':
    debug_address_pattern()
    test_improved_pattern()