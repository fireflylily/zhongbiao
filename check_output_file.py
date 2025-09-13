#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查输出文件内容
"""

from docx import Document

def check_docx_content(file_path):
    """检查docx文件内容"""
    try:
        doc = Document(file_path)
        print(f"检查文件: {file_path}")
        print("=" * 60)
        
        # 检查关键字段
        key_fields = ["供应商全称", "采购人", "供应商代表姓名"]
        
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if text:
                # 检查是否包含关键字段
                for field in key_fields:
                    if field in text or "(" + field + ")" in text or "（" + field + "）" in text:
                        print(f"段落 {i+1}: {text}")
                        break
                
                # 检查特定模式
                if "致：" in text or "授权" in text or "供应商名称：" in text:
                    print(f"段落 {i+1}: {text}")
        
        print("=" * 60)
        print("检查完成")
        
    except Exception as e:
        print(f"读取文件失败: {e}")

if __name__ == "__main__":
    file_path = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/ai_tender_system/data/outputs/business_response_945150ca-68e1-4141-921b-fd4c48e07ebd_20250913_090008_-.docx"
    check_docx_content(file_path)