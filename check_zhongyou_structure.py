#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查中邮保险文档的实际结构，看看章节是否按TOC顺序出现
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
    doc_path = "ai_tender_system/data/uploads/tender_processing/2025/12/20251221_180214_中邮保险手机号实名认证服务采购项目竞争性磋商采购文件_fcfdcec9.docx"
    doc = Document(doc_path)

    print("=" * 100)
    print("中邮保险文档：检查实际文档结构")
    print("=" * 100)
    print(f"文档: {Path(doc_path).name}\n")

    # 解析TOC
    parser = DocumentStructureParser()
    toc_idx = parser._find_toc_section(doc)

    if toc_idx is None:
        print("❌ 未找到目录")
        return

    print(f"✅ 找到目录，起始段落: {toc_idx}")

    toc_items, toc_end_idx = parser._parse_toc_items(doc, toc_idx)
    print(f"✅ 解析到 {len(toc_items)} 个目录项，结束段落: {toc_end_idx}\n")

    print("TOC内容（按出现顺序）:")
    print("-" * 100)
    for i, item in enumerate(toc_items):
        print(f"{i+1:2d}. [Level {item['level']}] {item['title']}")

    print("\n" + "=" * 100)
    print("在文档中搜索这些标题的实际位置")
    print("=" * 100)

    # 在整个文档中搜索这些标题
    title_positions = []

    for item in toc_items:
        title = item['title']
        # 去掉冒号，因为文档中可能没有冒号
        search_variants = [
            title,
            title.replace('：', ' '),
            title.replace('：', ''),
        ]

        found = False
        for i, para in enumerate(doc.paragraphs):
            para_text = para.text.strip()
            if not para_text:
                continue

            # 检查是否匹配任何变体
            for variant in search_variants:
                if variant in para_text or para_text in variant:
                    # 检查样式
                    style_name = para.style.name if para.style else "None"

                    title_positions.append({
                        'title': title,
                        'level': item['level'],
                        'para_idx': i,
                        'para_text': para_text,
                        'style': style_name
                    })
                    found = True
                    break

            if found:
                break

        if not found:
            title_positions.append({
                'title': title,
                'level': item['level'],
                'para_idx': None,
                'para_text': '未找到',
                'style': ''
            })

    print("\n实际位置（按段落索引排序）:")
    print("-" * 100)

    # 按段落索引排序
    sorted_positions = sorted(title_positions, key=lambda x: x['para_idx'] if x['para_idx'] is not None else 999999)

    for pos in sorted_positions:
        if pos['para_idx'] is not None:
            print(f"段落 {pos['para_idx']:4d}: [Level {pos['level']}] [{pos['style']:20s}] {pos['title']}")
            if pos['para_text'] != pos['title']:
                print(f"             实际文本: {pos['para_text']}")
        else:
            print(f"未找到      : [Level {pos['level']}] {pos['title']}")

    print("\n" + "=" * 100)
    print("分析")
    print("=" * 100)

    print("\nTOC顺序 vs 文档顺序:")
    print("  TOC中的顺序:")
    for i, item in enumerate(toc_items[:6]):  # 只显示前6个
        print(f"    {i+1}. {item['title']}")

    print("\n  文档中的实际顺序（按段落位置）:")
    for i, pos in enumerate(sorted_positions[:6]):
        if pos['para_idx'] is not None:
            print(f"    段落{pos['para_idx']}: {pos['title']}")

    print("\n如果TOC顺序和文档顺序不一致，那么sequential search就会失败！")
    print()

if __name__ == '__main__':
    main()
