#!/usr/bin/env python3
"""
直接重新索引文档（提取目录）
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_tender_system.modules.knowledge_base.rag_engine import RAGEngine
from ai_tender_system.modules.knowledge_base.toc_extractor import TOCExtractor
from ai_tender_system.common.database import get_knowledge_base_db

def main():
    print("=== 直接重新索引文档11（智慧足迹API文档）===\n")

    file_path = "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/product_docs/2025/10/20251006_211921_智慧足迹金融风控平台v2.0api文档--20250102更新_795409ab.docx"
    doc_id = 11

    # 1. 提取目录
    print("步骤1: 提取文档目录...")
    extractor = TOCExtractor()
    toc_entries = extractor.extract_toc(file_path, doc_id)
    print(f"✓ 提取了 {len(toc_entries)} 个目录条目")

    if len(toc_entries) > 0:
        print(f"\n前5个目录条目示例:")
        for i, entry in enumerate(toc_entries[:5]):
            print(f"  {i+1}. [{entry['heading_level']}级] {entry['heading_text'][:50]}...")

    # 2. 存入数据库
    print(f"\n步骤2: 将目录存入数据库...")
    db = get_knowledge_base_db()

    # 先删除旧的
    db.delete_toc_by_doc(doc_id)

    # 插入新的
    for entry in toc_entries:
        db.insert_toc_entry(
            doc_id=entry['doc_id'],
            heading_level=entry['heading_level'],
            heading_text=entry['heading_text'],
            section_number=entry.get('section_number'),
            keywords=entry.get('keywords'),
            page_number=entry.get('page_number'),
            parent_toc_id=None,
            sequence_order=entry['sequence_order']
        )

    print(f"✓ 已将 {len(toc_entries)} 个目录条目存入数据库")

    # 3. 测试搜索
    print("\n步骤3: 测试目录搜索...")
    results = db.search_toc_by_keywords(["300091"], doc_id)
    print(f"✓ 关键词搜索'300091': 找到 {len(results)} 条结果")

    if results:
        for r in results[:3]:
            print(f"  - {r['heading_text']}")

    results2 = db.search_toc_by_text("法院涉诉", doc_id)
    print(f"✓ 文本搜索'法院涉诉': 找到 {len(results2)} 条结果")

    if results2:
        for r in results2[:3]:
            print(f"  - {r['heading_text']}")

    print("\n✅ 重新索引完成！现在可以测试搜索功能了。")
    print("提示: 访问 http://localhost:8110/knowledge_base 搜索 '300091' 或 '法院涉诉信息'")

if __name__ == '__main__':
    main()
