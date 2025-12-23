#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟搜索"第三章  投标文件格式"的匹配过程
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

def test_match(title, para_text):
    """测试标题和段落的匹配"""
    clean_title = re.sub(r'\s+', '', title)
    clean_para = re.sub(r'\s+', '', para_text)

    # 提取核心关键词
    core_keywords = extract_core_keywords(clean_title)
    para_keywords = extract_core_keywords(clean_para)

    print(f"\n标题: '{title}'")
    print(f"  clean_title: '{clean_title}'")
    print(f"  core_keywords: '{core_keywords}'")

    print(f"\n段落: '{para_text}'")
    print(f"  clean_para: '{clean_para}'")
    print(f"  para_keywords: '{para_keywords}'")

    # 检查各个级别的匹配
    print(f"\n匹配结果:")

    # Level 1
    if clean_title == clean_para or clean_title in clean_para:
        print(f"  ✓ Level 1: 完全匹配或包含匹配")
        return True

    # Level 3
    title_without_number = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', clean_title)
    para_without_number = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', clean_para)

    if title_without_number and para_without_number and title_without_number == para_without_number:
        print(f"  ✓ Level 3: 去除编号后匹配")
        print(f"     title_without_number: '{title_without_number}'")
        print(f"     para_without_number: '{para_without_number}'")
        return True

    # Level 4
    if len(core_keywords) >= 4 and len(para_keywords) >= 4:
        if core_keywords in para_keywords or para_keywords in core_keywords:
            print(f"  ✓ Level 4: 核心关键词匹配")
            print(f"     core_keywords: '{core_keywords}'")
            print(f"     para_keywords: '{para_keywords}'")
            print(f"     匹配方式: ", end="")
            if core_keywords in para_keywords:
                print(f"core_keywords in para_keywords")
            else:
                print(f"para_keywords in core_keywords")
            return True

    print(f"  ✗ 无匹配")
    return False

def main():
    print("=" * 100)
    print("模拟搜索'第三章  投标文件格式'的匹配过程")
    print("=" * 100)

    title = "第三章  投标文件格式"

    # 测试段落126
    print("\n" + "=" * 100)
    print("测试1: 段落126 '四、投标文件'")
    print("=" * 100)
    test_match(title, "四、投标文件")

    # 测试段落240
    print("\n" + "=" * 100)
    print("测试2: 段落240 '第三章  投标文件格式'")
    print("=" * 100)
    test_match(title, "第三章  投标文件格式")

    print("\n" + "=" * 100)
    print("分析")
    print("=" * 100)

    print("\n如果'四、投标文件'被Level 4匹配到，那说明:")
    print("  1. extract_core_keywords('第三章投标文件格式') = '投标文件格式'")
    print("  2. extract_core_keywords('四、投标文件') = '投标文件'")
    print("  3. '投标文件' in '投标文件格式' = True （包含关系）")
    print("\n这就是为什么段落126被误匹配的原因！")

    print()

if __name__ == '__main__':
    main()
