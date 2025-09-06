#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
from docx import Document

def debug_underline_issue():
    """调试下划线格式问题"""
    
    # 使用最新的输出文件
    result_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/test_format17_fix_v2_result.docx"
    
    if not os.path.exists(result_file):
        print(f"结果文件不存在: {result_file}")
        return
        
    try:
        doc = Document(result_file)
        print("文档打开成功")
        
        # 查找包含替换文本的段落
        for para_idx, paragraph in enumerate(doc.paragraphs):
            if "智慧足迹数据科技有限公司" in paragraph.text and "北京市东城区王府井大街200号" in paragraph.text:
                print(f"\n找到处理后段落 #{para_idx}")
                print(f"段落文本: {paragraph.text}")
                print(f"总run数: {len(paragraph.runs)}")
                
                print(f"\n=== 详细run格式分析 ===")
                for run_idx, run in enumerate(paragraph.runs):
                    if run.text:  # 只分析有文本的run
                        font = run.font
                        print(f"Run #{run_idx}: '{run.text}'")
                        print(f"  斜体: {font.italic}")
                        print(f"  粗体: {font.bold}")
                        print(f"  下划线: {font.underline}")
                        print(f"  字体大小: {font.size}")
                        print("")
                
                # 特别检查包含"室）"的run
                for run_idx, run in enumerate(paragraph.runs):
                    if "室）" in run.text:
                        print(f"🚨 发现包含'室）'的Run #{run_idx}:")
                        print(f"  文本: '{run.text}'")
                        print(f"  下划线: {run.font.underline}")
                        print(f"  斜体: {run.font.italic}")
                        break
                
                break
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_underline_issue()