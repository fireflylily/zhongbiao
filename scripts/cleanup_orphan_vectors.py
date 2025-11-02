#!/usr/bin/env python3
"""
清理孤儿向量脚本
删除向量数据库中对应的文档已被删除的向量
"""

import sqlite3
from pathlib import Path

# 数据库路径
knowledge_db_path = Path(__file__).parent / 'ai_tender_system' / 'data' / 'knowledge_base.db'
chroma_db_path = Path(__file__).parent / 'ai_tender_system' / 'modules' / 'data' / 'chroma_db' / 'chroma.sqlite3'

def get_valid_document_ids():
    """获取所有有效的文档ID"""
    conn = sqlite3.connect(str(knowledge_db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT doc_id FROM documents")
    valid_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return valid_ids

def get_valid_file_paths():
    """获取所有有效的文件路径"""
    conn = sqlite3.connect(str(knowledge_db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM documents")
    valid_paths = {row[0] for row in cursor.fetchall()}
    conn.close()
    return valid_paths

def cleanup_orphan_vectors():
    """清理孤儿向量"""
    print("=== 开始清理孤儿向量 ===\n")

    # 获取有效数据
    valid_doc_ids = get_valid_document_ids()
    valid_paths = get_valid_file_paths()

    print(f"有效文档数量: {len(valid_doc_ids)}")
    print(f"有效文件路径数量: {len(valid_paths)}\n")

    # 连接Chroma数据库
    conn = sqlite3.connect(str(chroma_db_path))
    cursor = conn.cursor()

    # 统计当前向量数量
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total_vectors = cursor.fetchone()[0]
    print(f"当前向量总数: {total_vectors}\n")

    orphan_vector_ids = set()

    # 方法1: 查找document_id不在有效列表中的向量
    cursor.execute("""
        SELECT DISTINCT e.id
        FROM embeddings e
        JOIN embedding_metadata m ON e.id = m.id
        WHERE m.key = 'document_id' AND m.int_value NOT IN ({})
    """.format(','.join(str(id) for id in valid_doc_ids) if valid_doc_ids else '0'))

    for row in cursor.fetchall():
        orphan_vector_ids.add(row[0])

    print(f"找到 {len(orphan_vector_ids)} 个孤儿向量 (document_id格式)")

    # 方法2: 查找source不在有效路径列表中的向量
    cursor.execute("""
        SELECT DISTINCT e.id, m.string_value
        FROM embeddings e
        JOIN embedding_metadata m ON e.id = m.id
        WHERE m.key = 'source'
    """)

    source_orphans = 0
    for row in cursor.fetchall():
        vector_id, source_path = row
        # 检查source路径是否对应有效文档
        if source_path not in valid_paths:
            orphan_vector_ids.add(vector_id)
            source_orphans += 1

    print(f"找到 {source_orphans} 个孤儿向量 (source格式)")
    print(f"合计孤儿向量: {len(orphan_vector_ids)}\n")

    if not orphan_vector_ids:
        print("✅ 没有发现孤儿向量，数据库干净！")
        conn.close()
        return

    # 删除孤儿向量
    print(f"开始删除 {len(orphan_vector_ids)} 个孤儿向量...")

    # 分批删除（避免SQL语句过长）
    batch_size = 500
    orphan_list = list(orphan_vector_ids)
    deleted_count = 0

    for i in range(0, len(orphan_list), batch_size):
        batch = orphan_list[i:i+batch_size]
        placeholders = ','.join(['?' for _ in batch])

        # 删除向量元数据
        cursor.execute(f"DELETE FROM embedding_metadata WHERE id IN ({placeholders})", batch)
        # 删除向量数据
        cursor.execute(f"DELETE FROM embeddings WHERE id IN ({placeholders})", batch)

        deleted_count += len(batch)
        print(f"  已删除: {deleted_count}/{len(orphan_vector_ids)}")

    conn.commit()

    # 统计删除后的向量数量
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    remaining_vectors = cursor.fetchone()[0]

    print(f"\n✅ 清理完成！")
    print(f"删除向量数: {total_vectors - remaining_vectors}")
    print(f"剩余向量数: {remaining_vectors}")

    conn.close()

if __name__ == '__main__':
    cleanup_orphan_vectors()
