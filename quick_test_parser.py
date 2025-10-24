#!/usr/bin/env python3
"""快速测试文档解析修复"""

import sys
import os

# 设置环境
os.chdir('/Users/lvhe/Downloads/zhongbiao/zhongbiao')
sys.path.insert(0, '/Users/lvhe/Downloads/zhongbiao/zhongbiao')

# 直接导入并执行
from ai_tender_system.modules.tender_processing.structure_parser import StructureParser

# 测试文档
test_doc = "ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_招标文件_6cfefcaf.docx"

print("=" * 80)
print("测试文档解析 - 文件构成修复")
print("=" * 80)

parser = StructureParser()
chapters = parser.parse_document_structure(test_doc)

print(f"\n共找到 {len(chapters)} 个章节:\n")

zero_count = 0
for i, ch in enumerate(chapters, 1):
    status = '✅' if ch.auto_selected else '❌' if ch.skip_recommended else '⚪'
    print(f"{i}. [{status}] {ch.title}")
    print(f"   段落: {ch.para_start_idx}-{ch.para_end_idx}, 字数: {ch.word_count}")
    if ch.word_count == 0:
        zero_count += 1

print("\n" + "=" * 80)
if zero_count == 0:
    print("✅ 修复成功！所有章节都有内容")
else:
    print(f"❌ 仍有{zero_count}个0字章节")
print("=" * 80)
