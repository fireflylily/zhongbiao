#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查成都数据文档的目录结构
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'ai_tender_system'))

from docx import Document
from modules.tender_processing.structure_parser import DocumentStructureParser

def main():
    doc_path = "ai_tender_system/data/uploads/tender_processing/2025/11/20251110_141642_【招标方案】成都数据集团第一批数据产品供应商库（发售版）(1)_75647a44.docx"
    doc = Document(doc_path)

    print("=" * 100)
    print("成都数据文档：检查目录结构")
    print("=" * 100)
    print(f"文档: {Path(doc_path).name}\n")

    # 查找目录
    parser = DocumentStructureParser()
    toc_idx = parser._find_toc_section(doc)

    if toc_idx is None:
        print("❌ 未找到目录")
        return

    print(f"✅ 找到目录，起始段落: {toc_idx}")

    # 解析目录
    toc_items, toc_end_idx = parser._parse_toc_items(doc, toc_idx)

    print(f"✅ 解析到 {len(toc_items)} 个目录项，结束段落: {toc_end_idx}\n")

    print("目录内容:")
    print("-" * 100)
    for i, item in enumerate(toc_items):
        print(f"{i+1:2d}. [Level {item['level']}] {item['title']}")

    print()

    # 查找"第二章"和"第三章"
    print("=" * 100)
    print("查找第二章和第三章在目录中的定义")
    print("=" * 100)

    for i, item in enumerate(toc_items):
        if '第二章' in item['title'] or '第三章' in item['title']:
            print(f"{i+1:2d}. [Level {item['level']}] {item['title']}")

    print()

    # 查找"投标文件"相关的目录项
    print("=" * 100)
    print("查找'投标文件'相关的目录项")
    print("=" * 100)

    for i, item in enumerate(toc_items):
        if '投标文件' in item['title']:
            print(f"{i+1:2d}. [Level {item['level']}] {item['title']}")

    print()

    # 显示方法3如何匹配"第三章"
    print("=" * 100)
    print("方法3的匹配逻辑分析")
    print("=" * 100)

    print("\n目录中的第三章定义: '第三章  投标文件格式'")
    print("\n在正文中搜索时，方法3会尝试匹配:")
    print("  1. 完全匹配: '第三章  投标文件格式'")
    print("  2. 模糊匹配: 包含'第三章'和'投标文件格式'的段落")

    print("\n可能的匹配结果:")
    print("  - 段落126: '四、投标文件' (Heading 2)")
    print("  - 段落240: '第三章  投标文件格式' (Heading 1)")

    print("\n如果段落126被误匹配为'第三章  投标文件格式'的开始位置，")
    print("那就解释了为什么方法3的第三章从126开始，而不是240。")

    print()

if __name__ == '__main__':
    main()
