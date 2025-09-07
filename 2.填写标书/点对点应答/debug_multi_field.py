#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试多字段处理问题
"""

import re

def test_multi_field_processing():
    """测试多字段处理逻辑"""
    
    # 模拟段落文本
    test_paragraphs = [
        "地址________________________________  传真________________________________",
        "电话________________________________  电子邮件____________________________"
    ]
    
    # 模拟字段配置
    field_patterns = [
        {
            'name': '地址',
            'patterns': [r'(地址[:：])\s*([^传]*?)(?=传|$)', r'^(地址)\s*([^传]*?)(?=传|$)', r'^(地址)(\s+)(?=.*传真)'],
            'value': '北京市东城区王府井大街200号七层711室'
        },
        {
            'name': '传真',
            'patterns': [r'(传真)([_\s]*)', r'(传真)[:：]\s*([_\s]*)', r'(传真号码)[:：]\s*([_\s]*)', r'(传真号码)\s*([_\s]*)'],
            'value': '未填写'
        },
        {
            'name': '电话',
            'patterns': [r'^电话[_\s]*$', r'^电话[:：]\s*([_\s]*)', r'^(电话)(\s+)(?=.*电子邮件)', r'^(电话)\s*([_\s]*)'],
            'value': '010-63271000'
        },
        {
            'name': '电子邮件',
            'patterns': [r'(电子邮件)([_\s]*)$', r'(电子邮件)[:：]\s*([_\s]*)', r'^(电子邮件)\s*([_\s]*)', r'(邮箱)([_\s]*)$', r'(邮箱)[:：]\s*([_\s]*)', r'^(邮箱)\s*([_\s]*)'],
            'value': '未填写'
        }
    ]
    
    print("=== 多字段处理调试 ===\n")
    
    for para_idx, para_text in enumerate(test_paragraphs):
        print(f"处理段落{para_idx}: '{para_text}'")
        
        # 检测是否有多个字段
        has_multiple_fields = ('地址' in para_text and '传真' in para_text) or \
                            ('电话' in para_text and '电子邮件' in para_text)
        
        print(f"  多字段检测: {has_multiple_fields}")
        
        current_text = para_text
        paragraph_modified = False
        
        for field in field_patterns:
            print(f"\n  尝试匹配字段: {field['name']}")
            
            # 选择搜索文本
            search_text = current_text if has_multiple_fields and paragraph_modified else para_text
            print(f"    搜索文本: '{search_text}'")
            
            # 测试每个模式
            matched = False
            for pattern_str in field['patterns']:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                match = pattern.search(search_text)
                
                if match:
                    print(f"    ✅ 匹配成功: {pattern_str}")
                    print(f"       完整匹配: '{match.group(0)}'")
                    if match.groups():
                        for i, g in enumerate(match.groups()):
                            print(f"       组{i+1}: '{g}'")
                    
                    # 模拟替换
                    if len(match.groups()) >= 1:
                        label = match.group(1)
                        existing_content = match.group(2) if len(match.groups()) >= 2 else ""
                        
                        # 构建新文本
                        if label.endswith('：') or label.endswith(':'):
                            new_text_part = f"{label}{field['value']}"
                        else:
                            new_text_part = f"{label} {field['value']}"
                        
                        # 处理后续内容
                        trailing_content = search_text[match.end():]
                        if trailing_content:
                            # 特殊处理间距
                            if field['name'] == '地址' and '传真' in trailing_content:
                                new_text_part += "    " + trailing_content.lstrip()
                            elif field['name'] == '电话' and '电子邮件' in trailing_content:
                                new_text_part += "    " + trailing_content.lstrip()
                            else:
                                new_text_part += trailing_content
                        
                        # 构建完整的新文本
                        new_text = search_text[:match.start()] + new_text_part
                        
                        print(f"    新文本: '{new_text}'")
                        
                        # 更新当前文本
                        if has_multiple_fields:
                            current_text = new_text
                            paragraph_modified = True
                        
                        matched = True
                        break
                    else:
                        # 简单替换
                        new_text = pattern.sub(field['value'], search_text, count=1)
                        print(f"    简单替换: '{new_text}'")
                        
                        if has_multiple_fields:
                            current_text = new_text
                            paragraph_modified = True
                        
                        matched = True
                        break
            
            if not matched:
                print(f"    ❌ 未匹配任何模式")
        
        print(f"\n  最终结果: '{current_text}'")
        print("-" * 60)


if __name__ == '__main__':
    test_multi_field_processing()