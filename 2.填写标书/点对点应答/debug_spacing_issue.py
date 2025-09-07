#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试空格问题 - 分析为什么填写位置不正确
"""

import re

def analyze_regex_patterns():
    """分析正则表达式匹配结果"""
    
    # 测试文本（模拟图片中的情况）
    test_texts = [
        "成立时间：                    2000年4月21日",  # 有大量空格
        "法定代表人（负责人）姓名：                    陈忠岳",  # 有大量空格 
        "地址：                                      北京市西城区金融大街21号传真",  # 有大量空格
    ]
    
    # 当前使用的模式
    patterns = {
        '成立日期': [r'成立日期.*?[:：]\s*([_\s]*)', r'成立时间.*?[:：]\s*([_\s]*)', r'设立日期.*?[:：]\s*([_\s]*)'],
        '法定代表人': [r'法定代表人.*?[:：]\s*([_\s]*)', r'负责人.*?[:：]\s*([_\s]*)', r'法人代表.*?[:：]\s*([_\s]*)'],
        '地址': [r'地址[_\s]*$', r'地址[:：]\s*([_\s]*)', r'^地址\s*([_\s]*)'],
    }
    
    print("=== 正则表达式匹配分析 ===")
    
    for text in test_texts:
        print(f"\n原始文本: '{text}'")
        print(f"文本长度: {len(text)}")
        
        # 分析每个模式的匹配结果
        for field_type, field_patterns in patterns.items():
            for pattern_str in field_patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                match = pattern.search(text)
                
                if match:
                    print(f"\n✅ {field_type} 模式匹配: '{pattern_str}'")
                    print(f"   完整匹配: '{match.group(0)}'")
                    print(f"   匹配长度: {len(match.group(0))}")
                    if match.groups():
                        print(f"   捕获组: '{match.group(1)}'")
                        print(f"   捕获组长度: {len(match.group(1))}")
                        
                        # 模拟当前的替换逻辑
                        placeholder = match.group(1)
                        if placeholder:
                            # 当前逻辑：替换占位符
                            new_text = text.replace(match.group(0), match.group(0).replace(placeholder, "填写值", 1))
                            print(f"   替换后: '{new_text}'")
                            print(f"   问题: 填写值前面还有{len(match.group(0)) - len(placeholder) - len('填写值')}个字符的空格")
                    break
        
        print("-" * 50)


def propose_solutions():
    """提出解决方案"""
    print("\n=== 问题分析 ===")
    print("1. 当前正则表达式 r'成立时间.*?[:：]\\s*([_\\s]*)' 匹配了:")
    print("   - '成立时间：                    ' (包含大量空格)")
    print("   - 捕获组是空格部分，但替换时保留了标签和冒号后的空格")
    
    print("\n2. 问题根源:")
    print("   - 替换逻辑是: match.group(0).replace(placeholder, value)")
    print("   - match.group(0) = '成立时间：                    '")
    print("   - placeholder = '                    ' (空格)")
    print("   - 结果是: '成立时间：填写值' (空格被替换为填写值，但位置不对)")
    
    print("\n=== 解决方案建议 ===")
    print("方案1: 修改正则表达式，分离标签和占位符")
    print("   改为: r'(成立时间[:：])\\s*([_\\s]*)'")
    print("   这样可以只替换占位符部分，保留标签:冒号格式")
    
    print("\n方案2: 修改替换逻辑")
    print("   不使用 match.group(0).replace(placeholder, value)")
    print("   而是重新构建: 标签 + 冒号 + 空格 + 填写值")
    
    print("\n方案3: 智能空格处理")
    print("   检测标签后的空格数量，保留合理的空格(如1-2个)，去掉多余的")


if __name__ == '__main__':
    analyze_regex_patterns()
    propose_solutions()