#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查系统实际分配给章节的段落范围
对比手工统计的范围，找出差异
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'ai_tender_system'))

from modules.tender_processing.structure_parser import DocumentStructureParser

def check_actual_ranges():
    """检查系统分配的实际段落范围"""

    doc_path = "ai_tender_system/data/uploads/tender_processing/2025/11/20251117_160736_【招标方案】成都数据集团第一批数据产品供应商库（发售版）(1)_b6e72bac.docx"

    if not Path(doc_path).exists():
        doc_path = "ai_tender_system/data/uploads/tender_processing/2025/11/20251110_141642_【招标方案】成都数据集团第一批数据产品供应商库（发售版）(1)_75647a44.docx"

    print("=" * 100)
    print("检查系统实际分配的段落范围")
    print("=" * 100)

    parser = DocumentStructureParser()
    result = parser.parse_document_structure(doc_path)

    if not result['success']:
        print(f"解析失败: {result.get('error')}")
        return

    print(f"\n解析方法: {result.get('method')}")
    print(f"总章节数: {result['statistics']['total_chapters']}")
    print(f"总字数: {result['statistics']['total_words']:,}")

    # 手工统计的范围（作为参考）
    manual_ranges = {
        "第四章": (532, 540, 218),
        "第五章": (541, 556, 588),
        "第六章": (560, 629, 1823),
        "第七章": (630, 737, 4711),
        "第八章": (738, 818, 1646),
    }

    print("\n" + "=" * 100)
    print("对比分析")
    print("=" * 100)
    print(f"{'章节':<20} {'手工范围':<15} {'系统范围':<15} {'手工字数':<10} {'系统字数':<10} {'差异':<10} {'子章节':<6}")
    print("-" * 100)

    # 递归查找章节
    def find_chapters(chapters_list, prefix=""):
        results = []
        for ch in chapters_list:
            chapter_key = None
            for manual_key in manual_ranges.keys():
                if manual_key in ch['title']:
                    chapter_key = manual_key
                    break

            if chapter_key:
                manual_start, manual_end, manual_words = manual_ranges[chapter_key]
                system_start = ch.get('para_start_idx', '?')
                system_end = ch.get('para_end_idx', '?')
                system_words = ch.get('word_count', 0)

                manual_range = f"{manual_start}-{manual_end}"
                system_range = f"{system_start}-{system_end}"

                diff = system_words - manual_words
                diff_str = f"{diff:+,}" if isinstance(diff, int) else "N/A"

                child_count = len(ch.get('children', []))

                results.append({
                    'title': ch['title'][:18],
                    'manual_range': manual_range,
                    'system_range': system_range,
                    'manual_words': manual_words,
                    'system_words': system_words,
                    'diff': diff_str,
                    'children': child_count
                })

            # 递归查找子章节
            if ch.get('children'):
                results.extend(find_chapters(ch['children'], prefix + "  "))

        return results

    comparison_results = find_chapters(result['chapters'])

    for r in comparison_results:
        print(f"{r['title']:<20} {r['manual_range']:<15} {r['system_range']:<15} "
              f"{r['manual_words']:<10,} {r['system_words']:<10,} {r['diff']:<10} {r['children']:<6}")

    print("\n" + "=" * 100)
    print("详细章节树（显示前30个章节）")
    print("=" * 100)

    # 递归打印章节树
    def print_tree(chapters_list, level=0, count=[0]):
        for ch in chapters_list:
            if count[0] >= 30:
                return

            indent = "  " * level
            title = ch['title'][:50]
            start = ch.get('para_start_idx', '?')
            end = ch.get('para_end_idx', '?')
            words = ch.get('word_count', 0)
            children = len(ch.get('children', []))

            print(f"{indent}{title:<52} {start:>4}-{end:<4} {words:>8,}字 ({children}个子章节)")
            count[0] += 1

            if ch.get('children'):
                print_tree(ch['children'], level + 1, count)

    print_tree(result['chapters'])

    print("\n" + "=" * 100)

if __name__ == '__main__':
    check_actual_ranges()
