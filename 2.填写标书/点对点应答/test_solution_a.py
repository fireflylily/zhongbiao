#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试方案A的效果 - 看看是否还会有大量空格
"""

import re

def test_solution_a():
    """测试方案A的实际效果"""
    
    # 真实的测试案例
    test_cases = [
        {
            'original': '成立时间：                    年        月        日',
            'expected_clean': '成立时间：2000年4月21日',
            'field_value': '2000年4月21日'
        },
        {
            'original': '法定代表人（负责人）姓名：                    陈忠岳',
            'expected_clean': '法定代表人（负责人）姓名：陈忠岳',
            'field_value': '陈忠岳'
        },
        {
            'original': '地址：                                      北京市西城区金融大街21号传真',
            'expected_clean': '地址：北京市西城区金融大街21号',
            'field_value': '北京市西城区金融大街21号'
        }
    ]
    
    print("=== 方案A效果测试 ===")
    
    for i, case in enumerate(test_cases, 1):
        original = case['original']
        field_value = case['field_value']
        expected = case['expected_clean']
        
        print(f"\n测试案例 {i}:")
        print(f"原始文本: '{original}'")
        print(f"原始长度: {len(original)}")
        
        # 方案A的新正则表达式
        patterns_to_test = [
            r'(成立时间[:：])\s*(.*?)$',
            r'(法定代表人.*?[:：])\s*(.*?)$', 
            r'(地址[:：])\s*(.*?)$'
        ]
        
        for pattern_str in patterns_to_test:
            pattern = re.compile(pattern_str)
            match = pattern.search(original)
            
            if match:
                label = match.group(1)  # 标签部分
                existing_content = match.group(2).strip()  # 现有内容部分
                
                print(f"\n✅ 匹配模式: {pattern_str}")
                print(f"标签部分: '{label}'")
                print(f"现有内容: '{existing_content}' (长度:{len(existing_content)})")
                
                # 方案A的处理逻辑
                if existing_content and field_value not in existing_content:
                    # 如果有现有内容且不包含我们要填的值
                    result_a = f"{label} {field_value}"
                    print(f"方案A结果: '{result_a}' (现有内容被替换)")
                else:
                    # 没有现有内容或已经包含填写值
                    result_a = f"{label} {field_value}" 
                    print(f"方案A结果: '{result_a}' (直接填写)")
                
                print(f"结果长度: {len(result_a)}")
                print(f"期望结果: '{expected}'")
                print(f"是否符合期望: {'✅' if result_a == expected else '❌'}")
                
                # 检查是否还有大量空格
                trailing_spaces = len(result_a) - len(result_a.rstrip())
                if trailing_spaces > 2:
                    print(f"⚠️  结果末尾仍有 {trailing_spaces} 个空格")
                else:
                    print("✅ 结果格式紧凑，无多余空格")
                
                break
        
        print("-" * 50)

def test_edge_cases():
    """测试边缘情况"""
    print("\n=== 边缘情况测试 ===")
    
    edge_cases = [
        # 情况1：填写值后面原本就有其他内容
        '成立时间：                    2000年4月21日   其他内容',
        # 情况2：只有空格，没有其他内容  
        '成立时间：                              ',
        # 情况3：空格中混有其他字符
        '成立时间：_____________________',
    ]
    
    for case in edge_cases:
        print(f"\n边缘案例: '{case}'")
        
        pattern = re.compile(r'(成立时间[:：])\s*(.*?)$')
        match = pattern.search(case)
        
        if match:
            label = match.group(1)
            content = match.group(2).strip()
            
            result = f"{label} 2000年4月21日"
            print(f"处理结果: '{result}'")
            print(f"潜在问题: {'原有内容被完全替换' if content else '无问题'}")


if __name__ == '__main__':
    test_solution_a()
    test_edge_cases()