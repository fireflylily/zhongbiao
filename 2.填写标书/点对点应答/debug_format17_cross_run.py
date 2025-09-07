#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
from docx import Document

def debug_format17_cross_run_issue():
    """Debug the format 17 cross-run issue"""
    
    # Use a file that contains the pattern
    input_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/uploads/20250903_095446_tender_document.docx"
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    try:
        doc = Document(input_file)
        print("Document opened successfully")
        
        # Pattern for format 17
        pattern = re.compile(r'(?P<prefix>[\(（])\s*(?P<content>供应商名称、地址)\s*(?P<suffix>[\)）])')
        
        # Search for the target paragraph
        target_paragraph = None
        target_para_idx = -1
        
        for para_idx, paragraph in enumerate(doc.paragraphs):
            para_text = paragraph.text
            if pattern.search(para_text):
                target_paragraph = paragraph
                target_para_idx = para_idx
                print(f"\nFound target paragraph #{para_idx}: '{para_text}'")
                break
        
        if not target_paragraph:
            print("Target pattern not found in document")
            return
            
        # Analyze the runs in this paragraph
        print(f"\nAnalyzing runs in paragraph #{target_para_idx}:")
        print(f"Total runs: {len(target_paragraph.runs)}")
        
        for run_idx, run in enumerate(target_paragraph.runs):
            print(f"Run #{run_idx}: '{run.text}' (contains target: {'供应商名称、地址' in run.text})")
        
        # Check if it's a cross-run issue
        full_text = ''.join([run.text for run in target_paragraph.runs])
        match = pattern.search(full_text)
        if match:
            print(f"\nPattern matches in concatenated text: '{match.group(0)}'")
            print(f"Content: '{match.group('content')}'")
            
            # Check which runs contain parts of the pattern
            target_content = match.group('content')
            print(f"\nAnalyzing cross-run distribution for '{target_content}':")
            
            content_runs = []
            for run_idx, run in enumerate(target_paragraph.runs):
                if any(part in run.text for part in ['供应商名称', '地址', '、']):
                    content_runs.append((run_idx, run.text))
                    print(f"Run #{run_idx} contains part of target: '{run.text}'")
            
            if len(content_runs) > 1:
                print(f"\n🚨 CROSS-RUN ISSUE DETECTED!")
                print(f"Target content '{target_content}' is split across {len(content_runs)} runs")
                
                # Try to fix it by reconstructing runs
                print("\nAttempting fix using run reconstruction...")
                
                # Find the position where the pattern should be replaced
                start_pos = 0
                pattern_start_run = -1
                pattern_start_pos = -1
                
                for run_idx, run in enumerate(target_paragraph.runs):
                    if match.start() >= start_pos and match.start() < start_pos + len(run.text):
                        pattern_start_run = run_idx
                        pattern_start_pos = match.start() - start_pos
                        print(f"Pattern starts in run #{run_idx} at position {pattern_start_pos}")
                        break
                    start_pos += len(run.text)
                
                # Test replacement
                replacement_text = "中国联合网络通信有限公司、北京市东城区王府井大街200号七层711室"
                new_full_text = full_text.replace(match.group(0), replacement_text)
                print(f"\nReplacement result: '{new_full_text}'")
                
            else:
                print(f"\nTarget content is in a single run - should work fine")
        else:
            print("\n❌ Pattern doesn't match in concatenated text - regex issue")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_format17_cross_run_issue()