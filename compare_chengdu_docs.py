#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比成都数据文档的两次解析结果（12月21日 vs 12月25日）
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'ai_tender_system'))

from modules.tender_processing.structure_parser import DocumentStructureParser

def print_chapters(chapters, prefix=""):
    """递归打印章节树"""
    for ch in chapters:
        word_info = f"{ch.get('word_count', 0)}字" if ch.get('word_count', 0) > 0 else "无字数"
        print(f"{prefix}[{ch['level']}级] {ch['title']} - {word_info}")
        if ch.get('children'):
            print_chapters(ch['children'], prefix + "  ")

def main():
    # 两个文档路径
    doc1_path = "ai_tender_system/data/uploads/tender_processing/2025/12/20251221_180236_【招标方案】成都数据集团第一批数据产品供应商库（发售版）(1)_9dcd0af2.docx"
    doc2_path = "ai_tender_system/data/uploads/tender_processing/2025/12/20251225_095358_【招标方案】成都数据集团第一批数据产品供应商库（发售版）(1)_ae5bb8ca.docx"

    parser = DocumentStructureParser()

    print("=" * 100)
    print("解析文档1（12月21日）")
    print("=" * 100)
    result1 = parser.parse_document_structure(doc1_path, methods=['outline_level'])

    if result1['success']:
        print(f"\n✅ 解析成功")
        print(f"方法: {result1.get('method', 'N/A')}")
        stats1 = result1.get('statistics', {})
        print(f"统计: 总章节={stats1.get('total_chapters', 0)}, 总字数={stats1.get('total_words', 0)}")
        print(f"\n章节列表:")
        print_chapters(result1['chapters'])
    else:
        print(f"\n❌ 解析失败: {result1.get('error', 'Unknown error')}")
        return

    print("\n" + "=" * 100)
    print("解析文档2（12月25日，今天）")
    print("=" * 100)
    result2 = parser.parse_document_structure(doc2_path, methods=['outline_level'])

    if result2['success']:
        print(f"\n✅ 解析成功")
        print(f"方法: {result2.get('method', 'N/A')}")
        stats2 = result2.get('statistics', {})
        print(f"统计: 总章节={stats2.get('total_chapters', 0)}, 总字数={stats2.get('total_words', 0)}")
        print(f"\n章节列表:")
        print_chapters(result2['chapters'])
    else:
        print(f"\n❌ 解析失败: {result2.get('error', 'Unknown error')}")
        return

    print("\n" + "=" * 100)
    print("对比结果")
    print("=" * 100)

    def flatten_chapters(chapters):
        """扁平化章节树"""
        result = []
        for ch in chapters:
            result.append(ch)
            if ch.get('children'):
                result.extend(flatten_chapters(ch['children']))
        return result

    chapters1 = flatten_chapters(result1['chapters'])
    chapters2 = flatten_chapters(result2['chapters'])

    print(f"\n章节数量对比:")
    print(f"  12月21日: {len(chapters1)} 个章节")
    print(f"  12月25日: {len(chapters2)} 个章节")

    stats1 = result1.get('statistics', {})
    stats2 = result2.get('statistics', {})
    print(f"\n总字数对比:")
    print(f"  12月21日: {stats1.get('total_words', 0)} 字")
    print(f"  12月25日: {stats2.get('total_words', 0)} 字")

    # 逐章节对比
    print(f"\n逐章节对比:")
    max_len = max(len(chapters1), len(chapters2))

    diff_count = 0
    for i in range(max_len):
        ch1 = chapters1[i] if i < len(chapters1) else None
        ch2 = chapters2[i] if i < len(chapters2) else None

        if ch1 and ch2:
            title_match = ch1['title'] == ch2['title']
            word_match = ch1.get('word_count', 0) == ch2.get('word_count', 0)
            level_match = ch1['level'] == ch2['level']

            if not (title_match and word_match and level_match):
                diff_count += 1
                print(f"\n  【章节 {i+1} 存在差异】")
                print(f"    标题: {'✓' if title_match else '✗'}")
                print(f"      21日: {ch1['title']}")
                print(f"      25日: {ch2['title']}")
                print(f"    层级: {'✓' if level_match else '✗'} | 21日: {ch1['level']} | 25日: {ch2['level']}")
                print(f"    字数: {'✓' if word_match else '✗'} | 21日: {ch1.get('word_count', 0)} | 25日: {ch2.get('word_count', 0)}")
        elif ch1:
            diff_count += 1
            print(f"\n  【章节 {i+1}: ❌ 12月25日缺失】")
            print(f"    21日: [{ch1['level']}级] {ch1['title']} ({ch1.get('word_count', 0)}字)")
        elif ch2:
            diff_count += 1
            print(f"\n  【章节 {i+1}: ➕ 12月25日新增】")
            print(f"    25日: [{ch2['level']}级] {ch2['title']} ({ch2.get('word_count', 0)}字)")

    # 判断是否一致
    if diff_count == 0:
        print(f"\n\n🎉 结论: 两次解析结果完全一致！章节数={len(chapters1)}, 总字数={stats1.get('total_words', 0)}")
    else:
        print(f"\n\n⚠️  结论: 发现 {diff_count} 处差异！")
        print(f"  可能原因:")
        print(f"    1. 文档内容本身有修改")
        print(f"    2. 解析算法有变化（删除白/黑名单功能后）")
        print(f"    3. 章节边界计算逻辑的差异")

if __name__ == '__main__':
    main()
