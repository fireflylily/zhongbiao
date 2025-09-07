#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from docx import Document

def debug_para25():
    """调试段落25为什么没有被处理"""
    
    # 读取原始文件
    input_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/uploads/20250906_075450_business_template_docx"
    
    try:
        doc = Document(input_file)
        
        # 获取段落25
        para25 = doc.paragraphs[25]
        text = para25.text
        
        print(f"段落 #25 内容: '{text}'")
        print(f"长度: {len(text)}")
        print(f"空格数: {text.count(' ')}")
        
        # 检查是否符合格式18
        pattern18 = re.compile(r'^(?P<label>供应商名称)\s*(?P<placeholder>\s{20,})\s*$')
        match = pattern18.search(text)
        
        if match:
            print(f"✅ 符合格式18模式")
            print(f"  标签: '{match.group('label')}'")
            print(f"  占位符: '{match.group('placeholder')}' (长度: {len(match.group('placeholder'))})")
        else:
            print(f"❌ 不符合格式18模式")
            
            # 分析原因
            print("\n分析原因：")
            
            # 检查是否以供应商名称开头
            if text.startswith("供应商名称"):
                print("✅ 以'供应商名称'开头")
            else:
                print(f"❌ 不以'供应商名称'开头，开头是: '{text[:10]}'")
            
            # 检查是否有冒号
            if "：" in text or ":" in text:
                print("❌ 包含冒号，不符合无冒号格式")
            else:
                print("✅ 没有冒号")
            
            # 检查空格数量
            space_after = text.replace("供应商名称", "")
            space_count = len(space_after)
            print(f"标签后内容: '{space_after}' (长度: {space_count})")
            
            if space_count >= 20:
                print(f"✅ 有{space_count}个字符（>=20）")
            else:
                print(f"❌ 只有{space_count}个字符（<20）")
                
            # 检查是否全是空格
            if space_after.isspace():
                print("✅ 标签后全是空格")
            else:
                print(f"❌ 标签后不全是空格，包含: {repr(space_after)}")
        
        # 测试其他可能的格式
        print("\n测试其他格式：")
        
        # 格式18-2: 公司名称
        pattern18_2 = re.compile(r'^(?P<label>公司名称)\s*(?P<placeholder>\s{20,})\s*$')
        if pattern18_2.search(text):
            print("✅ 符合格式18-2（公司名称）")
        
        # 格式19: 双字段
        pattern19 = re.compile(r'^(?P<label1>供应商名称)\s*(?P<sep1>[:：])\s*(?P<placeholder1>\s{10,})\s*(?P<label2>采购编号)\s*(?P<sep2>[:：])\s*(?P<placeholder2>\s*)\s*$')
        if pattern19.search(text):
            print("✅ 符合格式19（双字段）")
            
        # 检查runs结构
        print(f"\n段落的runs结构：")
        print(f"总run数: {len(para25.runs)}")
        for i, run in enumerate(para25.runs):
            print(f"  Run #{i}: '{run.text}' (长度: {len(run.text)})")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_para25()