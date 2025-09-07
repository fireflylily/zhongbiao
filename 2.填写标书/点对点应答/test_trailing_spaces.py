#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试方案A是否会在填写值后面产生大量空格
"""

import re

def test_trailing_spaces():
    """专门测试填写值后面的空格情况"""
    
    # 模拟真实的文档情况
    test_cases = [
        # 情况1: 标签后有大量空格，空格后还有内容（年月日）
        {
            'text': '成立时间：                    年        月        日',
            'description': '空格后有年月日字符'
        },
        # 情况2: 标签后有大量空格，空格后没有内容
        {
            'text': '成立时间：                                        ',
            'description': '空格后无内容'
        },
        # 情况3: 标签后有大量空格，空格后有下划线
        {
            'text': '成立时间：                    __________________',
            'description': '空格后有下划线'
        },
        # 情况4: 模拟跨run的情况（一个段落，多个run）
        {
            'text': '成立时间：                    ',  # 这个run后面可能还有其他run
            'description': '可能的跨run情况'
        }
    ]
    
    print("=== 测试填写值后面的空格情况 ===")
    
    for i, case in enumerate(test_cases, 1):
        text = case['text']
        desc = case['description']
        
        print(f"\n案例 {i}: {desc}")
        print(f"原文本: '{text}' (长度:{len(text)})")
        
        # 方案A的处理
        pattern = re.compile(r'(成立时间[:：])\s*(.*?)$')
        match = pattern.search(text)
        
        if match:
            label = match.group(1)  # '成立时间：'
            content = match.group(2)  # 空格后的内容
            
            print(f"标签: '{label}'")
            print(f"现有内容: '{content}' (长度:{len(content)})")
            
            # 方案A的结果
            result_a = f"{label} 2000年4月21日"
            print(f"方案A结果: '{result_a}' (长度:{len(result_a)})")
            
            # 检查末尾空格
            trailing_spaces = len(result_a) - len(result_a.rstrip())
            print(f"结果末尾空格数: {trailing_spaces}")
            
            # 可视化显示
            visual = result_a.replace(' ', '·')  # 用·显示空格
            print(f"可视化显示: '{visual}'")
            
            if trailing_spaces == 0:
                print("✅ 无末尾空格问题")
            else:
                print(f"⚠️  有 {trailing_spaces} 个末尾空格")
        
        print("-" * 50)

def simulate_current_behavior():
    """模拟当前行为，看看会不会产生末尾空格"""
    
    print("\n=== 模拟当前系统的行为 ===")
    
    # 当前系统可能的处理方式
    original = '成立时间：                    年        月        日'
    
    print(f"原始: '{original}'")
    
    # 当前逻辑：追加内容
    current_result = original.replace('年        月        日', '2000年4月21日')
    print(f"当前替换逻辑: '{current_result}'")
    
    # 检查当前结果的问题
    trailing_spaces = len(current_result) - len(current_result.rstrip())
    print(f"当前结果末尾空格数: {trailing_spaces}")
    
    if trailing_spaces > 0:
        print("❌ 当前方法确实会产生末尾空格")
    else:
        print("✅ 当前方法无末尾空格")

def test_paragraph_replacement():
    """测试段落级别的替换是否会产生末尾空格"""
    
    print("\n=== 段落级别替换测试 ===")
    
    # 模拟段落替换（整个段落文本替换）
    old_paragraph = '成立时间：                    年        月        日'
    new_paragraph_a = '成立时间：2000年4月21日'
    
    print(f"原段落: '{old_paragraph}' (长度:{len(old_paragraph)})")
    print(f"新段落: '{new_paragraph_a}' (长度:{len(new_paragraph_a)})")
    
    # 检查新段落
    trailing = len(new_paragraph_a) - len(new_paragraph_a.rstrip())
    print(f"新段落末尾空格: {trailing}")
    
    if trailing == 0:
        print("✅ 方案A不会在填写值后面产生大量空格")
    else:
        print(f"❌ 方案A会产生 {trailing} 个末尾空格")

if __name__ == '__main__':
    test_trailing_spaces()
    simulate_current_behavior() 
    test_paragraph_replacement()