#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试真实案例 - 模拟实际的文档情况
"""

import re

def debug_real_matching():
    """调试真实的匹配情况"""
    
    # 从图片中看到的真实情况
    real_cases = [
        # 成立时间的情况
        {
            'original': '成立时间：                    年        月        日',
            'after_processing': '成立时间：                    2000年4月21日',
            'field': '成立日期'
        },
        # 法定代表人的情况  
        {
            'original': '法定代表人（负责人）姓名：                    陈忠岳',
            'field': '法定代表人'
        },
        # 地址的情况
        {
            'original': '地址：                                      北京市西城区金融大街21号传真',
            'field': '地址'
        }
    ]
    
    # 当前使用的正则模式
    patterns = {
        '成立日期': [r'成立日期.*?[:：]\s*([_\s]*)', r'成立时间.*?[:：]\s*([_\s]*)', r'设立日期.*?[:：]\s*([_\s]*)'],
        '法定代表人': [r'法定代表人.*?[:：]\s*([_\s]*)', r'负责人.*?[:：]\s*([_\s]*)', r'法人代表.*?[:：]\s*([_\s]*)'],
        '地址': [r'地址[_\s]*$', r'地址[:：]\s*([_\s]*)', r'^地址\s*([_\s]*)'],
    }
    
    print("=== 真实案例调试 ===")
    
    for case in real_cases:
        text = case['original'] if 'original' in case else case['after_processing']
        field = case['field']
        
        print(f"\n【{field}字段分析】")
        print(f"文本: '{text}'")
        
        # 测试当前模式
        for pattern_str in patterns.get(field, []):
            pattern = re.compile(pattern_str, re.IGNORECASE)
            match = pattern.search(text)
            
            if match:
                print(f"\n✅ 匹配模式: {pattern_str}")
                print(f"完整匹配: '{match.group(0)}'")
                print(f"匹配位置: {match.start()}-{match.end()}")
                
                if match.groups():
                    placeholder = match.group(1)
                    print(f"占位符(group1): '{placeholder}' (长度:{len(placeholder)})")
                    
                    # 分析当前替换逻辑的问题
                    if placeholder:
                        # 当前逻辑
                        current_replacement = match.group(0).replace(placeholder, "填写内容", 1)
                        print(f"当前替换逻辑结果: '{current_replacement}'")
                        
                        # 分析问题
                        prefix = match.group(0)[:match.group(0).find(placeholder)]
                        print(f"前缀部分: '{prefix}' (长度:{len(prefix)})")
                        
                        # 建议的改进逻辑
                        improved = f"{field.split('.')[-1]}：填写内容"
                        print(f"建议改进结果: '{improved}'")
                    else:
                        print("占位符为空，使用追加逻辑")
                        current_replacement = match.group(0) + "填写内容"
                        print(f"当前追加逻辑结果: '{current_replacement}'")
                        
                break
        
        print("-" * 60)


def analyze_problem_and_solution():
    """分析问题并提出解决方案"""
    
    print("\n=== 问题根本原因分析 ===")
    print("""
1. 正则表达式问题:
   当前: r'成立时间.*?[:：]\\s*([_\\s]*)'
   问题: 这个模式会匹配 '成立时间：                    '
   捕获组: 通常是空字符串，因为没有下划线或额外空格字符
   
2. 替换逻辑问题:  
   当前逻辑: match.group(0).replace(placeholder, value)
   实际执行: '成立时间：                    '.replace('', '2000年4月21日')
   结果: '成立时间：                    2000年4月21日'
   问题: 由于placeholder是空字符串，replace没有替换任何内容，而是追加
   
3. 真正的问题:
   - 文档中的空格不是用于替换的占位符，而是排版用的空白
   - 我们需要的是清理这些空格，紧凑地填写内容
    """)
    
    print("\n=== 解决方案 ===")
    print("""
方案A: 改进正则表达式 (推荐)
   模式: r'(成立时间[:：])\\s*(.*)$'  
   逻辑: 分离标签和内容部分，重新构建为 标签 + 内容
   
方案B: 智能空格处理
   识别标签后的大量空格，替换为 标签 + 合理空格 + 内容
   
方案C: 全新的字段识别逻辑  
   专门识别这类"标签 + 大量空格 + 可能的内容"的模式
    """)


if __name__ == '__main__':
    debug_real_matching() 
    analyze_problem_and_solution()