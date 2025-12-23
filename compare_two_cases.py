#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比哈银消金和成都数据两个case的匹配逻辑差异
"""

import re

def extract_core_keywords(text: str) -> str:
    """提取核心关键词：去除编号和常见前缀"""
    # 移除编号
    text = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', text)
    # 移除"附件"前缀
    text = re.sub(r'^附件[-:：]?', '', text)
    # 移除分隔符
    text = re.sub(r'[-_\t]+', '', text)
    # 移除空格
    text = re.sub(r'\s+', '', text)
    return text

def test_match_logic(toc_title, para_text, case_name):
    """测试匹配逻辑"""
    print(f"\n{'='*100}")
    print(f"{case_name}")
    print(f"{'='*100}")

    clean_title = re.sub(r'\s+', '', toc_title)
    clean_para = re.sub(r'\s+', '', para_text)

    core_keywords = extract_core_keywords(clean_title)
    para_keywords = extract_core_keywords(para_text)

    print(f"\nTOC标题: '{toc_title}'")
    print(f"  core_keywords: '{core_keywords}'")

    print(f"\n正文段落: '{para_text}'")
    print(f"  para_keywords: '{para_keywords}'")

    # 检查各级别匹配
    print(f"\n匹配测试:")

    # Level 1: 完全匹配
    if clean_title == clean_para or clean_title in clean_para:
        print(f"  ✓ Level 1: 完全匹配 → 会立即返回")
        return True
    else:
        print(f"  ✗ Level 1: 不匹配")

    # Level 3: 去除编号后匹配
    title_without_number = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', clean_title)
    para_without_number = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', clean_para)

    if title_without_number and para_without_number and title_without_number == para_without_number:
        print(f"  ✓ Level 3: 去编号后完全匹配 → 会立即返回")
        print(f"     title_without_number: '{title_without_number}'")
        print(f"     para_without_number: '{para_without_number}'")
        return True
    else:
        print(f"  ✗ Level 3: 去编号后不匹配")
        print(f"     title_without_number: '{title_without_number}'")
        print(f"     para_without_number: '{para_without_number}'")

    # Level 4: 核心关键词匹配
    if len(core_keywords) >= 4 and len(para_keywords) >= 4:
        if core_keywords in para_keywords:
            print(f"  ✓ Level 4: 核心关键词匹配 (core_keywords in para_keywords) → 会立即返回")
            print(f"     '{core_keywords}' in '{para_keywords}'")
            return True
        elif para_keywords in core_keywords:
            print(f"  ✓ Level 4: 核心关键词匹配 (para_keywords in core_keywords) → 会立即返回")
            print(f"     '{para_keywords}' in '{core_keywords}'")
            return True
        else:
            print(f"  ✗ Level 4: 核心关键词不匹配")
            print(f"     '{core_keywords}' vs '{para_keywords}'")
    else:
        print(f"  ✗ Level 4: 关键词长度不足")
        print(f"     core_keywords长度: {len(core_keywords)}, para_keywords长度: {len(para_keywords)}")

    return False

def main():
    print("="*100)
    print("对比哈银消金和成都数据两个case的匹配逻辑")
    print("="*100)

    # Case 1: 哈银消金 - 评标办法
    print("\n\n" + "="*100)
    print("Case 1: 哈银消金文档")
    print("="*100)

    # 哈银消金的目录项
    test_match_logic(
        "第三部分 评标办法",
        "评标办法",
        "【哈银消金】TOC='第三部分 评标办法' vs 正文='评标办法'"
    )

    # Case 2: 成都数据 - 投标文件格式
    print("\n\n" + "="*100)
    print("Case 2: 成都数据文档")
    print("="*100)

    test_match_logic(
        "第三章  投标文件格式",
        "四、投标文件",
        "【成都数据】TOC='第三章  投标文件格式' vs 正文='四、投标文件'"
    )

    # 对比分析
    print("\n\n" + "="*100)
    print("对比分析")
    print("="*100)

    print("\n【哈银消金】:")
    print("  - TOC核心关键词: '评标办法' (4字)")
    print("  - 正文核心关键词: '评标办法' (4字)")
    print("  - Level 4判断: '评标办法' in '评标办法' = True ✅")
    print("  - 结果: 应该匹配上！")

    print("\n【成都数据】:")
    print("  - TOC核心关键词: '投标文件格式' (6字)")
    print("  - 正文核心关键词: '投标文件' (4字)")
    print("  - Level 4判断: '投标文件' in '投标文件格式' = True ✅")
    print("  - 结果: 匹配上了（但这是误匹配）")

    print("\n【差异】:")
    print("  哈银消金: 核心关键词完全相等 → 正确匹配")
    print("  成都数据: 核心关键词是包含关系 → 误匹配")

    print("\n【问题】:")
    print("  为什么哈银消金的'评标办法'没有被方法3找到？")
    print("  → 需要检查日志，看实际搜索过程中发生了什么")

if __name__ == '__main__':
    main()
