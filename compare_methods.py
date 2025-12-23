#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比方法2和方法3对同一文档的解析结果
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'ai_tender_system'))

from modules.tender_processing.structure_parser import DocumentStructureParser

def print_chapters(chapters, method_name, indent=0):
    """递归打印章节"""
    for ch in chapters:
        prefix = "  " * indent
        level_mark = f"[{ch['level']}级]"

        print(f"{prefix}{level_mark} {ch['title']}")
        print(f"{prefix}       段落 {ch['para_start_idx']:4d} - {ch['para_end_idx']:4d}  |  {ch['word_count']:,}字")

        if ch.get('children'):
            print_chapters(ch['children'], method_name, indent + 1)

def main():
    doc_path = "ai_tender_system/data/uploads/tender_processing/2025/11/20251123_111226_招标文件-哈银消金_c9a419c9.docx"

    print("=" * 100)
    print("对比方法2（大纲级别识别）和方法3（精确匹配）")
    print("=" * 100)
    print(f"文档: {Path(doc_path).name}\n")

    parser = DocumentStructureParser()

    # 方法2：大纲级别识别
    print("=" * 100)
    print("方法2：大纲级别识别 (parse_by_outline_level)")
    print("=" * 100)

    result2 = parser.parse_by_outline_level(doc_path)

    if result2['success']:
        stats2 = result2['statistics']
        print(f"✅ 解析成功")
        print(f"   识别章节数: {stats2['total_chapters']}")
        print(f"   总字数: {stats2['total_words']:,}\n")

        print("章节列表（只显示1级章节）:")
        print("-" * 100)
        for ch in result2['chapters']:
            if ch['level'] == 1:
                child_count = len(ch.get('children', []))
                print(f"[{ch['level']}级] {ch['title']}")
                print(f"       段落 {ch['para_start_idx']:4d} - {ch['para_end_idx']:4d}  |  {ch['word_count']:,}字  |  子章节: {child_count}")
    else:
        print(f"❌ 解析失败: {result2.get('error')}")

    print()

    # 方法3：精确匹配
    print("=" * 100)
    print("方法3：精确匹配（基于目录） (parse_by_toc_exact)")
    print("=" * 100)

    result3 = parser.parse_by_toc_exact(doc_path)

    if result3['success']:
        stats3 = result3['statistics']
        print(f"✅ 解析成功")
        print(f"   识别章节数: {stats3['total_chapters']}")
        print(f"   总字数: {stats3['total_words']:,}\n")

        print("章节列表:")
        print("-" * 100)
        for ch in result3['chapters']:
            print(f"[{ch['level']}级] {ch['title']}")
            print(f"       段落 {ch['para_start_idx']:4d} - {ch['para_end_idx']:4d}  |  {ch['word_count']:,}字")
    else:
        print(f"❌ 解析失败: {result3.get('error')}")

    print()

    # 对比分析
    if result2['success'] and result3['success']:
        print("=" * 100)
        print("对比分析")
        print("=" * 100)

        diff_chapters = stats2['total_chapters'] - stats3['total_chapters']
        diff_words = stats2['total_words'] - stats3['total_words']

        print(f"\n📊 统计对比:")
        print(f"   识别章节数: 方法2 = {stats2['total_chapters']}, 方法3 = {stats3['total_chapters']}, 差异 = {diff_chapters:+d}")
        print(f"   总字数:     方法2 = {stats2['total_words']:,}, 方法3 = {stats3['total_words']:,}, 差异 = {diff_words:+,}")

        if diff_words != 0:
            percent = (diff_words / stats3['total_words']) * 100
            print(f"   字数差异百分比: {percent:+.1f}%")

        print("\n🔍 详细对比:")

        # 将方法3的章节建立索引（按标题）
        method3_chapters = {ch['title']: ch for ch in result3['chapters']}

        # 对比方法2的1级章节
        print("\n逐章节对比（方法2的1级章节 vs 方法3）:")
        print("-" * 100)

        for ch2 in result2['chapters']:
            if ch2['level'] != 1:
                continue

            title = ch2['title']

            # 在方法3中查找相同标题
            ch3 = method3_chapters.get(title)

            if ch3:
                word_diff = ch2['word_count'] - ch3['word_count']
                para_diff_start = ch2['para_start_idx'] - ch3['para_start_idx']
                para_diff_end = ch2['para_end_idx'] - ch3['para_end_idx']

                status = "✅" if word_diff == 0 else "⚠️"

                print(f"\n{status} {title}")
                print(f"   方法2: 段落 {ch2['para_start_idx']:4d} - {ch2['para_end_idx']:4d}  |  {ch2['word_count']:,}字")
                print(f"   方法3: 段落 {ch3['para_start_idx']:4d} - {ch3['para_end_idx']:4d}  |  {ch3['word_count']:,}字")

                if word_diff != 0 or para_diff_start != 0 or para_diff_end != 0:
                    print(f"   差异:")
                    if para_diff_start != 0:
                        print(f"     起始段落: {para_diff_start:+d}")
                    if para_diff_end != 0:
                        print(f"     结束段落: {para_diff_end:+d}")
                    if word_diff != 0:
                        print(f"     字数: {word_diff:+,} ({(word_diff/ch3['word_count']*100):+.1f}%)")
            else:
                print(f"\n❌ {title}")
                print(f"   方法2: 段落 {ch2['para_start_idx']:4d} - {ch2['para_end_idx']:4d}  |  {ch2['word_count']:,}字")
                print(f"   方法3: 未找到")

        # 检查方法3中有但方法2中没有的
        method2_titles = {ch['title'] for ch in result2['chapters'] if ch['level'] == 1}
        missing_in_method2 = [title for title in method3_chapters.keys() if title not in method2_titles]

        if missing_in_method2:
            print("\n\n方法3中有但方法2中缺失的章节:")
            print("-" * 100)
            for title in missing_in_method2:
                ch = method3_chapters[title]
                print(f"❌ {title}")
                print(f"   方法3: 段落 {ch['para_start_idx']:4d} - {ch['para_end_idx']:4d}  |  {ch['word_count']:,}字")

    print()

if __name__ == '__main__':
    main()
