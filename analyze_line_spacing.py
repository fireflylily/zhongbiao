#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Word文档行距设置的调试脚本
"""

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
import sys

def analyze_document_line_spacing(file_path):
    """分析文档中的行距设置"""
    print(f"分析文档: {file_path}")

    try:
        doc = Document(file_path)

        # 统计信息
        total_paragraphs = 0
        reply_paragraphs = 0
        line_spacing_stats = {
            'SINGLE': 0,
            'ONE_POINT_FIVE': 0,
            'DOUBLE': 0,
            'MULTIPLE': 0,
            'EXACTLY': 0,
            'AT_LEAST': 0,
            'NONE': 0
        }

        print("\n=== 段落行距分析 ===")

        for i, paragraph in enumerate(doc.paragraphs):
            total_paragraphs += 1

            # 检查是否是应答段落
            text = paragraph.text.strip()
            is_reply = text.startswith("应答：")

            if is_reply:
                reply_paragraphs += 1

            # 获取行距信息
            line_spacing_rule = paragraph.paragraph_format.line_spacing_rule
            line_spacing = paragraph.paragraph_format.line_spacing

            # 统计行距规则
            if line_spacing_rule is None:
                rule_name = 'NONE'
            else:
                rule_name = line_spacing_rule.name if hasattr(line_spacing_rule, 'name') else str(line_spacing_rule)

            line_spacing_stats[rule_name] = line_spacing_stats.get(rule_name, 0) + 1

            # 如果是应答段落，详细输出
            if is_reply:
                print(f"应答段落 {i+1}:")
                print(f"  文本: {text[:50]}...")
                print(f"  行距规则: {rule_name}")
                print(f"  行距值: {line_spacing}")

                # 检查段落的其他格式属性
                pf = paragraph.paragraph_format
                print(f"  空前: {pf.space_before}")
                print(f"  空后: {pf.space_after}")
                print(f"  首行缩进: {pf.first_line_indent}")
                print(f"  左缩进: {pf.left_indent}")
                print(f"  右缩进: {pf.right_indent}")

                # 检查run级别的格式
                for j, run in enumerate(paragraph.runs):
                    if j < 3:  # 只检查前3个run
                        print(f"  Run {j}: 字体={run.font.name}, 大小={run.font.size}")

                print()

        print(f"\n=== 统计摘要 ===")
        print(f"总段落数: {total_paragraphs}")
        print(f"应答段落数: {reply_paragraphs}")
        print("\n行距规则分布:")
        for rule, count in line_spacing_stats.items():
            if count > 0:
                print(f"  {rule}: {count}")

        # 检查文档样式
        print(f"\n=== 文档样式分析 ===")
        print(f"可用样式数量: {len(doc.styles)}")

        # 检查默认段落样式
        try:
            default_style = doc.styles['Normal']
            default_pf = default_style.paragraph_format
            print(f"默认样式 'Normal' 行距:")
            print(f"  规则: {default_pf.line_spacing_rule}")
            print(f"  值: {default_pf.line_spacing}")
        except:
            print("无法获取默认样式信息")

    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    file_path = "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/outputs/20250922_110506_docx-内联应答.docx"
    analyze_document_line_spacing(file_path)