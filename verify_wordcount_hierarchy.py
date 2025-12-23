#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证父章节字数和子章节字数之和是否对应
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'ai_tender_system'))

from modules.tender_processing.structure_parser import DocumentStructureParser

def verify_hierarchy(chapters, indent=0):
    """
    递归验证父子章节的字数关系

    Returns:
        (total_issues, total_chapters_checked)
    """
    issues = 0
    checked = 0

    for ch in chapters:
        prefix = "  " * indent

        # 如果有子章节，验证父章节字数 = 子章节字数之和
        if ch.get('children') and len(ch['children']) > 0:
            checked += 1

            # 计算子章节字数之和
            children_total = sum(child['word_count'] for child in ch['children'])
            parent_count = ch['word_count']

            print(f"{prefix}📊 [{ch['level']}级] {ch['title']}")
            print(f"{prefix}   父章节字数: {parent_count:,}")
            print(f"{prefix}   子章节字数之和: {children_total:,}")

            if parent_count == children_total:
                print(f"{prefix}   ✅ 相等")
            else:
                diff = parent_count - children_total
                diff_percent = (diff / parent_count * 100) if parent_count > 0 else 0
                print(f"{prefix}   ❌ 差异: {diff:,} ({diff_percent:+.1f}%)")

                # 显示父章节段落范围
                print(f"{prefix}   父章节范围: 段落 {ch['para_start_idx']} - {ch['para_end_idx']}")

                # 显示子章节段落范围
                print(f"{prefix}   子章节范围:")
                for i, child in enumerate(ch['children'], 1):
                    print(f"{prefix}     {i}. {child['title']}: 段落 {child['para_start_idx']} - {child['para_end_idx']} ({child['word_count']:,}字)")

                issues += 1

            print()

            # 递归检查子章节
            sub_issues, sub_checked = verify_hierarchy(ch['children'], indent + 1)
            issues += sub_issues
            checked += sub_checked
        else:
            # 叶子节点，只显示信息
            print(f"{prefix}📄 [{ch['level']}级] {ch['title']}: {ch['word_count']:,}字 (段落 {ch['para_start_idx']} - {ch['para_end_idx']})")

    return issues, checked

def main():
    # 测试文档（找一个有层级结构的文档）
    test_docs = [
        "ai_tender_system/data/uploads/tender_processing/2025/11/20251123_111226_招标文件-哈银消金_c9a419c9.docx",
        "ai_tender_system/data/uploads/tender_processing/2025/11/20251110_141642_【招标方案】成都数据集团第一批数据产品供应商库（发售版）(1)_75647a44.docx"
    ]

    parser = DocumentStructureParser()

    for doc_path in test_docs:
        if not Path(doc_path).exists():
            continue

        print("=" * 100)
        print(f"测试文档: {Path(doc_path).name}")
        print("=" * 100)
        print()

        # 使用方法2（大纲级别识别）- 更可能有层级结构
        result = parser.parse_by_outline_level(doc_path)

        if not result['success']:
            print(f"❌ 解析失败: {result.get('error', '未知错误')}")
            continue

        chapters = result['chapters']
        stats = result['statistics']

        print(f"解析方法: {result['method']}")
        print(f"总章节数: {stats['total_chapters']}")
        print(f"统计的总字数: {stats['total_words']:,}")
        print()

        # 检查是否有层级结构
        has_children = any(ch.get('children') for ch in chapters)

        if not has_children:
            print("⚠️  该文档没有子章节（扁平结构），跳过验证")
            print()
            continue

        print("-" * 100)
        print("开始验证父子章节字数关系:")
        print("-" * 100)
        print()

        issues, checked = verify_hierarchy(chapters)

        print("=" * 100)
        print("验证总结")
        print("=" * 100)
        print(f"检查的父章节数: {checked}")
        print(f"发现的问题数: {issues}")

        if issues == 0:
            print("✅ 所有父章节字数都等于子章节字数之和")
        else:
            print(f"❌ 发现 {issues} 个父章节字数与子章节字数之和不相等")

        print()
        print()

if __name__ == '__main__':
    main()
