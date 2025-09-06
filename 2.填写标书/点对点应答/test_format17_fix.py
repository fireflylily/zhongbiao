#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from mcp_bidder_name_processor_enhanced import MCPBidderNameProcessor

def test_format17_fix():
    """Test the format 17 fix"""
    
    # Use a file that contains the pattern
    input_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/uploads/20250903_095446_tender_document.docx"
    output_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/test_format17_fix_result.docx"
    company_name = "智慧足迹数据科技有限公司"
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return False
        
    try:
        print("Initializing MCP processor...")
        processor = MCPBidderNameProcessor()
        
        print(f"Processing file: {input_file}")
        print(f"Company name: {company_name}")
        print(f"Output file: {output_file}")
        
        result = processor.process_bidder_name(
            input_file=input_file,
            output_file=output_file,
            company_name=company_name
        )
        
        print(f"\nProcessing result: {result}")
        
        if result.get('success'):
            print("✅ Processing completed successfully!")
            
            # Get stats from the result
            stats = result.get('stats', {})
            print(f"Total replacements: {stats.get('total_replacements', 0)}")
            print(f"Replace content count: {stats.get('replace_content_count', 0)}")
            print(f"Fill space count: {stats.get('fill_space_count', 0)}")
            
            # Check if format 17 was processed
            patterns_found = stats.get('patterns_found', [])
            format17_found = False
            
            print(f"\nPatterns found: {len(patterns_found)}")
            for pattern in patterns_found:
                print(f"- Rule #{pattern.get('rule_index', 'unknown')}: {pattern.get('description', 'unknown')}")
                if '供应商名称、地址' in pattern.get('description', ''):
                    format17_found = True
                    print(f"  ✅ This is Format 17! Original: '{pattern.get('original_text', 'unknown')}'")
            
            if format17_found:
                print("\n✅ Format 17 was successfully processed!")
            else:
                print("\n⚠️  Format 17 pattern was not found in results")
            
            return True
        else:
            print("❌ Processing failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_format17_fix()