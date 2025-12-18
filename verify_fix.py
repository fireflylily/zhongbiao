#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证文档扫描器修复 - 使用实际问题文本
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_tender_system.modules.business_response.document_scanner import DocumentScanner

def main():
    """验证实际问题文本的分类"""
    scanner = DocumentScanner()

    # 实际出现问题的三个候选段落
    candidates = [
        {
            'index': 153,
            'text': '★法定代表人/负责人身份证明',
            'expected': 'neutral'
        },
        {
            'index': 155,
            'text': '法定代表人/负责人身份证明',
            'expected': 'neutral'
        },
        {
            'index': 165,
            'text': '附：法定代表人/负责人的合法有效身份证明扫描件(如提供中华人民共和国居民身份证的，需同时提供国徽面及人像面)',
            'expected': 'strong_attach'  # 修复后应该是这个分类
        }
    ]

    # 定义分类优先级（与document_scanner.py中一致）
    category_priority = {
        'strong_attach': 100,
        'weak_attach': 80,
        'neutral': 50,
        'chapter': 30,
        'toc': 10,
        'reference': 5,
        'requirement_clause': -10,
        'header_noise': -50,
        'exclude': -999,
    }

    print("=" * 100)
    print("验证文档扫描器修复 - 实际问题场景")
    print("=" * 100)
    print("\n问题描述：")
    print("  段落#165包含'附：'前缀且提到'身份证明扫描件'，应该是最佳插入点")
    print("  但之前因为文本长度>50被分类为neutral(50分)，导致选择了更短的段落#155(14字符)")
    print("\n修复方案：")
    print("  增加智能判断：长文本(>50字符)如果包含关键资质词，也识别为strong_attach")
    print("\n" + "=" * 100)

    print("\n📊 候选段落分类结果：\n")

    classified_candidates = []
    for candidate in candidates:
        text = candidate['text']
        para_idx = candidate['index']
        expected = candidate['expected']

        # 分类
        actual = scanner._classify_paragraph(text, para_idx=para_idx, total_paras=200, style_name='')
        priority = category_priority.get(actual, 0)

        classified_candidates.append({
            **candidate,
            'actual': actual,
            'priority': priority,
            'match': actual == expected
        })

        # 输出
        status = "✅" if actual == expected else "❌"
        print(f"{status} 段落#{para_idx}")
        print(f"   文本: {text[:70]}{'...' if len(text) > 70 else ''}")
        print(f"   文本长度: {len(text)} 字符")
        print(f"   预期分类: {expected}")
        print(f"   实际分类: {actual}")
        print(f"   优先级评分: {priority}")
        print(f"   匹配状态: {'✅ 正确' if actual == expected else '❌ 错误'}")
        print()

    # 模拟选择逻辑
    print("=" * 100)
    print("📌 选择最佳候选（模拟max()函数）：\n")

    # 按照实际选择逻辑排序
    best = max(classified_candidates, key=lambda x: (
        x['priority'],      # 第一优先级：类别评分
        -len(x['text']),    # 第二优先级：文本越短越好
        x['index']          # 第三优先级：位置越靠后越好
    ))

    print(f"最佳选择: 段落#{best['index']}")
    print(f"  文本: {best['text']}")
    print(f"  分类: {best['actual']}")
    print(f"  优先级: {best['priority']}")
    print(f"  文本长度: {len(best['text'])}")

    print("\n" + "=" * 100)

    # 验证是否修复成功
    if best['index'] == 165 and best['actual'] == 'strong_attach':
        print("✅ 修复成功！")
        print("   段落#165被正确识别为strong_attach(100分)")
        print("   将优先于其他neutral(50分)候选被选中")
    else:
        print("❌ 修复失败！")
        print(f"   当前选择: 段落#{best['index']} ({best['actual']})")
        print(f"   预期选择: 段落#165 (strong_attach)")

    print("=" * 100)

    return best['index'] == 165

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
