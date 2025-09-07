#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试正则表达式模式匹配问题
"""

import re

def test_patterns():
    """测试各种模式匹配"""
    
    test_cases = [
        # 地址相关
        {
            'text': '地址                                  传真                                ',
            'patterns': [r'(地址[:：])\s*([^传]*?)(?=传|$)', r'^(地址)\s*([^传]*?)(?=传|$)'],
            'field': '地址'
        },
        # 电话相关
        {
            'text': '电话                                  电子邮件                            ',
            'patterns': [r'^电话[_\s]*$', r'^电话[:：]\s*([_\s]*)', r'^电话\s*([_\s]*)'],
            'field': '电话'
        },
        # 邮件相关
        {
            'text': '电话                                  电子邮件                            ',
            'patterns': [r'电子邮件[_\s]*$', r'电子邮件[:：]\s*([_\s]*)', r'^电子邮件\s*([_\s]*)', r'邮箱[_\s]*$', r'邮箱[:：]\s*([_\s]*)', r'^邮箱\s*([_\s]*)'],
            'field': '电子邮件'
        },
        # 单独的电话测试
        {
            'text': '电话',
            'patterns': [r'^电话[_\s]*$', r'^电话[:：]\s*([_\s]*)', r'^电话\s*([_\s]*)'],
            'field': '电话（单独）'
        },
        # 单独的邮件测试
        {
            'text': '电子邮件',
            'patterns': [r'电子邮件[_\s]*$', r'电子邮件[:：]\s*([_\s]*)', r'^电子邮件\s*([_\s]*)', r'邮箱[_\s]*$', r'邮箱[:：]\s*([_\s]*)', r'^邮箱\s*([_\s]*)'],
            'field': '电子邮件（单独）'
        }
    ]
    
    print("=== 正则表达式模式匹配测试 ===")
    
    for test_case in test_cases:
        text = test_case['text']
        patterns = test_case['patterns']
        field = test_case['field']
        
        print(f"\n【{field}】测试文本: '{text}'")
        
        matched = False
        for i, pattern_str in enumerate(patterns):
            try:
                pattern = re.compile(pattern_str)
                match = pattern.search(text)
                
                if match:
                    print(f"  ✅ 模式{i+1}匹配: {pattern_str}")
                    print(f"     完整匹配: '{match.group(0)}'")
                    for j, group in enumerate(match.groups()):
                        print(f"     组{j+1}: '{group}'")
                    matched = True
                    break
                else:
                    print(f"  ❌ 模式{i+1}不匹配: {pattern_str}")
                    
            except Exception as e:
                print(f"  ❌ 模式{i+1}错误: {pattern_str} - {e}")
        
        if not matched:
            print(f"  🚫 所有模式都不匹配")
    
    print("\n=== 改进建议 ===")
    
    # 测试改进的模式
    improved_tests = [
        {
            'text': '电话                                  电子邮件                            ',
            'phone_pattern': r'(电话)([^\u4e00-\u9fff]*?)(?=电子邮件|$)',  # 匹配到"电子邮件"之前
            'email_pattern': r'(电子邮件)([^\u4e00-\u9fff]*?)$',  # 从电子邮件开始到结尾
        }
    ]
    
    for test in improved_tests:
        text = test['text']
        print(f"\n测试改进模式: '{text}'")
        
        # 测试电话模式
        phone_pattern = re.compile(test['phone_pattern'])
        phone_match = phone_pattern.search(text)
        if phone_match:
            print(f"  ✅ 电话模式匹配: '{phone_match.group(0)}'")
            print(f"     标签: '{phone_match.group(1)}'")
            print(f"     内容: '{phone_match.group(2)}'")
        
        # 测试邮件模式
        email_pattern = re.compile(test['email_pattern'])
        email_match = email_pattern.search(text)
        if email_match:
            print(f"  ✅ 邮件模式匹配: '{email_match.group(0)}'")
            print(f"     标签: '{email_match.group(1)}'")
            print(f"     内容: '{email_match.group(2)}'")

if __name__ == '__main__':
    test_patterns()