#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
from docx import Document

def debug_format17_formatting_issue():
    """调试格式17处理时的格式问题"""
    
    # 使用包含模式的文件
    input_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/uploads/20250903_095446_tender_document.docx"
    
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}")
        return
        
    try:
        doc = Document(input_file)
        print("文档打开成功")
        
        # 格式17的模式
        pattern = re.compile(r'(?P<prefix>[\(（])\s*(?P<content>供应商名称、地址)\s*(?P<suffix>[\)）])')
        
        # 查找目标段落
        target_paragraph = None
        target_para_idx = -1
        
        for para_idx, paragraph in enumerate(doc.paragraphs):
            para_text = paragraph.text
            if pattern.search(para_text):
                target_paragraph = paragraph
                target_para_idx = para_idx
                print(f"\n找到目标段落 #{para_idx}: '{para_text}'")
                break
        
        if not target_paragraph:
            print("文档中未找到目标模式")
            return
            
        print(f"\n=== 处理前的段落分析 ===")
        print(f"段落文本: {target_paragraph.text}")
        print(f"总run数: {len(target_paragraph.runs)}")
        
        # 分析每个run的格式
        for run_idx, run in enumerate(target_paragraph.runs):
            font = run.font
            print(f"Run #{run_idx}: '{run.text}'")
            print(f"  字体名称: {font.name}")
            print(f"  字体大小: {font.size}")
            print(f"  粗体: {font.bold}")
            print(f"  斜体: {font.italic}")
            print(f"  颜色: {font.color.rgb if font.color and font.color.rgb else 'None'}")
        
        # 模拟当前的_redistribute_text_to_runs方法
        print(f"\n=== 模拟当前方法处理 ===")
        full_text = ''.join(run.text for run in target_paragraph.runs)
        match = pattern.search(full_text)
        
        if match:
            replacement_text = "智慧足迹数据科技有限公司、北京市东城区王府井大街200号七层711室"
            new_full_text = full_text.replace(match.group(0), f"{match.group('prefix')}{replacement_text}{match.group('suffix')}")
            
            print(f"原始文本: {full_text}")
            print(f"替换后文本: {new_full_text}")
            
            # 检查当前方法会如何处理
            print(f"\n当前方法会:")
            print(f"1. 清空所有{len(target_paragraph.runs)}个run的文本")
            print(f"2. 将全部新文本放入第一个run")
            print(f"3. 其他{len(target_paragraph.runs)-1}个run变为空")
            
            # 分析问题
            print(f"\n=== 问题分析 ===")
            print("❌ 当前方法的问题:")
            print("1. 将所有文本集中到第一个run，丢失了原始的字体格式分布")
            print("2. 其他run变空，但可能保留了不同的格式，影响文档显示")
            print("3. 没有保持原始的字体格式组合")
            
        else:
            print("在完整文本中未找到匹配")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_format17_formatting_issue()