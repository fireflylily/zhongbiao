#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试盖章格式匹配问题
"""

import re
from mcp_bidder_name_processor_enhanced import MCPBidderNameProcessor

def test_regex_matching():
    """测试正则表达式匹配"""
    processor = MCPBidderNameProcessor()
    
    # 获取规则2 - 盖章相关规则
    seal_rule = processor.bidder_patterns[2]
    pattern = seal_rule['pattern']
    
    print(f"🔍 测试规则: {seal_rule['description']}")
    print(f"📝 正则表达式: {pattern.pattern}")
    print("=" * 60)
    
    # 测试各种格式
    test_texts = [
        "1. 公司名称（全称、盖章）：_____________________",
        "公司名称（全称、盖章）：_____________________",
        "公司名称（盖章）：_____________________", 
        "供应商名称(盖章)：_____________________",
        "供应商全称及公章：_____________________",
        "供应商名称：_____________________ （公章）",
        "投标人名称（盖章）：_____________________",
        "单位名称及公章：_____________________",
        "公司名称：_____________________",
        "供应商名称：_____________________"
    ]
    
    for text in test_texts:
        # 尝试匹配整行
        match = pattern.match(text)
        if match:
            print(f"✅ 匹配: '{text}'")
            print(f"   groups: {match.groupdict()}")
        else:
            print(f"❌ 不匹配: '{text}'")
            
            # 尝试部分匹配来调试
            # 检查是否是行首空白字符问题
            stripped_text = text.strip()
            match_stripped = pattern.match(stripped_text)
            if match_stripped:
                print(f"   🔧 去掉前缀空白后匹配: '{stripped_text}'")
            else:
                # 检查是否因为行首有数字编号
                no_number_text = re.sub(r'^\d+\.\s*', '', text)
                match_no_number = pattern.match(no_number_text)
                if match_no_number:
                    print(f"   🔧 去掉数字编号后匹配: '{no_number_text}'")
                
        print()

def test_actual_doc_paragraphs():
    """测试实际文档段落"""
    from docx import Document
    
    doc = Document("test_seal_format_input.docx")
    processor = MCPBidderNameProcessor()
    seal_rule = processor.bidder_patterns[2]
    pattern = seal_rule['pattern']
    
    print("🔍 测试实际文档段落匹配:")
    print("=" * 60)
    
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            text = para.text
            match = pattern.match(text)
            
            if match:
                print(f"✅ 段落 {i} 匹配: '{text}'")
                print(f"   groups: {match.groupdict()}")
            else:
                if any(keyword in text for keyword in ['公司名称', '供应商名称', '盖章', '公章']):
                    print(f"❌ 段落 {i} 不匹配但包含关键词: '{text}'")
                    
                    # 详细调试
                    print(f"   原文: '{repr(text)}'")
                    print(f"   长度: {len(text)}")
                    print(f"   首字符: '{text[0] if text else 'N/A'}' (ord={ord(text[0]) if text else 'N/A'})")
                    print(f"   末字符: '{text[-1] if text else 'N/A'}' (ord={ord(text[-1]) if text else 'N/A'})")
            print()

if __name__ == "__main__":
    print("🧪 调试盖章格式匹配问题")
    print("=" * 60)
    
    # 测试正则表达式
    test_regex_matching()
    
    print("\n" + "=" * 60)
    
    # 测试实际文档
    test_actual_doc_paragraphs()