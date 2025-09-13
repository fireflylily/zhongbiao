#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查供应商名称处理问题"""

from docx import Document
import re

def check_document(file_path):
    """检查文档中的供应商名称字段"""
    print(f"\n检查文档: {file_path}")
    print("="*60)
    
    doc = Document(file_path)
    supplier_patterns = [
        '供应商名称', '供应商全称', '投标人名称', '公司名称', 
        '单位名称', '应答人名称'
    ]
    
    para_count = 0
    found_fields = []
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
            
        para_count += 1
        
        # 检查是否包含供应商相关字段
        for pattern in supplier_patterns:
            if pattern in text:
                found_fields.append({
                    'para_num': i,
                    'pattern': pattern,
                    'text': text[:200],
                    'full_text': text
                })
                
                # 分析文本格式
                print(f"\n段落 {i}: 找到 '{pattern}'")
                print(f"文本: {text[:100]}...")
                
                # 检查是否有空格填充
                if re.search(r'供应商名称\s*[:：]\s+(?!\S)', text):
                    print("  格式: 冒号后有空格（可能是空格填充格式）")
                    # 打印字符详情
                    match_part = re.search(r'供应商名称\s*[:：]\s*(.{0,50})', text)
                    if match_part:
                        after_colon = match_part.group(1)
                        print(f"  冒号后内容: '{after_colon}'")
                        print(f"  字符详情: {[ord(c) for c in after_colon[:20]]}")
                
                # 检查是否有下划线
                if '_' in text:
                    print("  格式: 包含下划线")
                    
                # 检查是否有括号
                if f'（{pattern}' in text or f'({pattern}' in text:
                    print("  格式: 括号格式")
                    
                # 检查是否已填充
                if '智慧足迹' in text:
                    print("  ✅ 已填充公司名称")
                else:
                    print("  ❌ 未填充公司名称")
    
    print(f"\n总共检查了 {para_count} 个非空段落")
    print(f"找到 {len(found_fields)} 个供应商名称相关字段")
    
    return found_fields

def main():
    # 检查最新的输出文档
    output_files = [
        './ai_tender_system/data/outputs/business_response_945150ca-68e1-4141-921b-fd4c48e07ebd_20250913_142227_-.docx',
        './test_template_fixed_processed.docx'
    ]
    
    all_fields = []
    for file_path in output_files:
        try:
            fields = check_document(file_path)
            all_fields.extend(fields)
        except Exception as e:
            print(f"错误处理文件 {file_path}: {e}")
    
    # 分析问题
    print("\n" + "="*60)
    print("问题分析:")
    print("="*60)
    
    unfilled = [f for f in all_fields if '智慧足迹' not in f['full_text']]
    if unfilled:
        print(f"\n发现 {len(unfilled)} 个未填充的供应商名称字段:")
        for f in unfilled[:3]:  # 只显示前3个
            print(f"  段落 {f['para_num']}: {f['text'][:80]}...")
            
            # 分析具体原因
            text = f['full_text']
            if re.search(r'供应商名称\s*[:：]\s+(?!\S)', text):
                print("    可能原因: 空格填充格式未被正确识别")
                # 显示具体的空格数量
                match = re.search(r'供应商名称\s*[:：](\s+)', text)
                if match:
                    spaces = match.group(1)
                    print(f"    空格数量: {len(spaces)}")
                    print(f"    空格字符码: {[ord(c) for c in spaces]}")

if __name__ == "__main__":
    main()