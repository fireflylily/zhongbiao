#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量转换已上传但未转换的PDF文件
用于修复路径问题后，转换之前上传的PDF文件
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.pdf_utils import get_pdf_converter, PDFDetector


def convert_pending_pdfs():
    """转换所有未转换的PDF文件"""

    # 连接数据库
    db_path = project_root / 'ai_tender_system' / 'data' / 'knowledge_base.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 查询所有未转换的PDF
    cursor.execute("""
        SELECT qualification_id, qualification_key, original_filename, file_path, file_type
        FROM company_qualifications
        WHERE (file_type = 'pdf' OR original_file_type = 'PDF')
          AND (converted_images IS NULL OR converted_images = '')
        ORDER BY upload_time DESC
    """)

    pending_pdfs = cursor.fetchall()

    if not pending_pdfs:
        print("✅ 没有需要转换的PDF文件")
        conn.close()
        return

    print(f"📋 找到 {len(pending_pdfs)} 个需要转换的PDF文件\n")

    success_count = 0
    fail_count = 0

    for pdf in pending_pdfs:
        qual_id = pdf['qualification_id']
        qual_key = pdf['qualification_key']
        filename = pdf['original_filename']
        relative_path = pdf['file_path']

        print(f"🔄 处理: {filename} (ID={qual_id}, key={qual_key})")

        # 转换为绝对路径
        file_path = Path(relative_path)
        if not file_path.is_absolute():
            # 数据库中的路径是 data/uploads/... 格式，需要加上 ai_tender_system/ 前缀
            if not relative_path.startswith('ai_tender_system/'):
                relative_path = 'ai_tender_system/' + relative_path
            file_path = project_root / relative_path

        # 检查文件是否存在
        if not file_path.exists():
            print(f"  ❌ 文件不存在: {file_path}")
            fail_count += 1
            continue

        # 检测是否为PDF
        if not PDFDetector.is_pdf(str(file_path)):
            print(f"  ⚠️  不是有效的PDF文件，跳过")
            fail_count += 1
            continue

        try:
            # 获取转换器
            converter = get_pdf_converter(qual_key)

            # 转换PDF
            result = converter.convert_to_images(
                str(file_path),
                custom_prefix=qual_key
            )

            if result['success']:
                # 更新数据库
                cursor.execute("""
                    UPDATE company_qualifications
                    SET original_file_type = 'PDF',
                        converted_images = ?,
                        conversion_info = ?,
                        conversion_date = ?
                    WHERE qualification_id = ?
                """, [
                    json.dumps(result['images']),
                    json.dumps({
                        'total_pages': result['total_pages'],
                        'output_dir': result['output_dir'],
                        'dpi': converter.config.dpi,
                        'format': converter.config.output_format
                    }),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    qual_id
                ])

                conn.commit()
                print(f"  ✅ 转换成功: {result['total_pages']}页")
                success_count += 1
            else:
                print(f"  ❌ 转换失败: {result.get('error')}")
                fail_count += 1

        except Exception as e:
            print(f"  ❌ 转换异常: {e}")
            fail_count += 1

    conn.close()

    # 输出统计
    print(f"\n{'='*50}")
    print(f"📊 转换完成:")
    print(f"  - 成功: {success_count} 个")
    print(f"  - 失败: {fail_count} 个")
    print(f"  - 总计: {len(pending_pdfs)} 个")
    print(f"{'='*50}")


if __name__ == '__main__':
    print("=" * 50)
    print("批量转换未转换的PDF文件")
    print("=" * 50)
    print()

    convert_pending_pdfs()
