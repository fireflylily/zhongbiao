#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def debug_colon_version():
    """调试有冒号版本的匹配情况"""
    
    # 实际文档中的文本
    test_texts = [
        '供应商名称：                                        ',  # 段落#29
        '                                供应商名称：                           ',  # 段落#37  
        '供应商名称：                                （加盖公章）'  # 段落#132
    ]
    
    # 定义各种格式的正则模式
    patterns = [
        # 格式18: 无冒号
        {
            'name': '格式18 - 无冒号',
            'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<placeholder>\s{20,})\s*$'),
            'type': 'fill_space_no_separator'
        },
        # 格式3: 长空格有冒号
        {
            'name': '格式3 - 长空格',
            'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>\s{20,})\s*$'),
            'type': 'fill_space'
        },
        # 格式4: 中等空格有冒号  
        {
            'name': '格式4 - 中等空格',
            'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>\s{10,19})\s*$'),
            'type': 'fill_space'
        },
        # 格式9-2: 带公章后缀
        {
            'name': '格式9-2 - 公章后缀',
            'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>\s{10,})\s*(?P<suffix>（[^）]*公章[^）]*）|\([^)]*公章[^)]*\))\s*$'),
            'type': 'fill_space'
        },
        # 格式8: 通用（无占位符）
        {
            'name': '格式8 - 通用',
            'pattern': re.compile(r'^\s*(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>)\s*$'),
            'type': 'fill_space'
        }
    ]
    
    print("=== 测试各种文本的模式匹配 ===\n")
    
    for i, text in enumerate(test_texts):
        print(f"文本 #{i+1}: '{text}'")
        print(f"长度: {len(text)}")
        
        matches = []
        for pattern_info in patterns:
            match = pattern_info['pattern'].search(text)
            if match:
                matches.append({
                    'name': pattern_info['name'],
                    'type': pattern_info['type'],
                    'groups': match.groupdict()
                })
        
        if matches:
            print(f"✅ 匹配到 {len(matches)} 个模式:")
            for match_info in matches:
                print(f"  - {match_info['name']} ({match_info['type']})")
                for key, value in match_info['groups'].items():
                    if value is not None:
                        print(f"    {key}: '{value}' (长度: {len(value)})")
                    else:
                        print(f"    {key}: None")
        else:
            print(f"❌ 没有匹配任何模式")
            
            # 分析原因
            stripped = text.strip()
            print(f"  去除首尾空格后: '{stripped}'")
            if stripped.startswith('供应商名称'):
                if '：' in stripped or ':' in stripped:
                    colon_index = stripped.find('：') if '：' in stripped else stripped.find(':')
                    after_colon = stripped[colon_index+1:]
                    print(f"  冒号后内容: '{after_colon}' (长度: {len(after_colon)})")
                    if after_colon.isspace():
                        print(f"  冒号后都是空格，应该能匹配格式3或8")
                else:
                    print(f"  无冒号，应该能匹配格式18")
        
        print()

if __name__ == "__main__":
    debug_colon_version()