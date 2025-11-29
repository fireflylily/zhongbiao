#!/usr/bin/env python3
"""
调试目录搜索逻辑
"""

import sys
import re
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.database import get_knowledge_base_db

def main():
    print("=== 调试目录搜索 ===\n")

    query = "300091 法院涉诉信息个人查询"
    doc_id = 11

    # 提取关键词（复制 rag_engine.py 的逻辑）
    keywords = []
    numbers = re.findall(r'\d{3,}', query)
    keywords.extend(numbers)
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,8}', query)
    keywords.extend(chinese_words[:3])

    print(f"查询: {query}")
    print(f"提取的关键词: {keywords}\n")

    db = get_knowledge_base_db()

    # 测试1: 关键词搜索
    print("=" * 60)
    print("测试1: 关键词精确匹配 (search_toc_by_keywords)")
    print("=" * 60)
    keyword_results = db.search_toc_by_keywords(keywords, doc_id)
    print(f"结果数: {len(keyword_results)}")
    for r in keyword_results[:3]:
        print(f"  - {r['heading_text']}")
        print(f"    keywords字段: {r.get('keywords')}")

    # 测试2: 文本模糊搜索
    print("\n" + "=" * 60)
    print("测试2: 文本模糊匹配 (search_toc_by_text)")
    print("=" * 60)
    text_results = db.search_toc_by_text(query, doc_id)
    print(f"结果数: {len(text_results)}")
    for r in text_results[:3]:
        print(f"  - {r['heading_text']}")

    # 测试3: 查看数据库中实际存储的关键词
    print("\n" + "=" * 60)
    print("测试3: 查看300091条目的实际存储")
    print("=" * 60)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT heading_text, section_number, keywords
            FROM document_toc
            WHERE doc_id = ? AND heading_text LIKE '%300091%'
        """, (doc_id,))
        rows = cursor.fetchall()

        print(f"找到 {len(rows)} 条包含'300091'的记录:")
        for row in rows:
            print(f"\n  标题: {row['heading_text']}")
            print(f"  章节号: {row['section_number']}")
            print(f"  关键词: {row['keywords']}")

    # 测试4: 手动测试 LIKE 查询
    print("\n" + "=" * 60)
    print("测试4: 手动 SQL LIKE 查询")
    print("=" * 60)

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # 测试关键词 LIKE 查询
        test_keyword = "300091"
        cursor.execute("""
            SELECT heading_text, keywords
            FROM document_toc
            WHERE doc_id = ? AND keywords LIKE ?
        """, (doc_id, f'%{test_keyword}%'))

        rows = cursor.fetchall()
        print(f"LIKE '%{test_keyword}%' 结果数: {len(rows)}")
        for row in rows[:3]:
            print(f"  - {row['heading_text']}")

if __name__ == '__main__':
    main()
