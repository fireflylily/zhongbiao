#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断脚本：检查案例ID 23的附件获取问题
用于在阿里云服务器上运行
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_tender_system.common.database import get_knowledge_base_db
from ai_tender_system.common.logger import get_module_logger

logger = get_module_logger("diagnose")

def diagnose_case_23():
    """诊断案例ID 23的问题"""

    print("\n" + "="*80)
    print("案例ID 23附件获取问题诊断")
    print("="*80 + "\n")

    db = get_knowledge_base_db()

    # 1. 检查案例是否存在
    print("1. 检查案例ID 23是否存在...")
    try:
        case_query = "SELECT * FROM case_studies WHERE case_id = ?"
        case = db.execute_query(case_query, (23,), fetch_one=True)

        if case:
            print(f"   ✅ 案例存在")
            print(f"   - 案例标题: {case.get('case_title')}")
            print(f"   - 客户名称: {case.get('customer_name')}")
            print(f"   - 公司ID: {case.get('company_id')}")
        else:
            print(f"   ❌ 案例ID 23 不存在!")
            return
    except Exception as e:
        print(f"   ❌ 查询案例失败: {e}")
        logger.error(f"查询案例失败: {e}", exc_info=True)
        return

    # 2. 检查附件表结构
    print("\n2. 检查case_attachments表结构...")
    try:
        schema_query = "PRAGMA table_info(case_attachments)"
        columns = db.execute_query(schema_query)
        print(f"   ✅ 表结构:")
        for col in columns:
            print(f"      - {col['name']}: {col['type']}")
    except Exception as e:
        print(f"   ❌ 查询表结构失败: {e}")
        logger.error(f"查询表结构失败: {e}", exc_info=True)

    # 3. 检查附件数据
    print("\n3. 检查案例ID 23的附件...")
    try:
        attachment_query = """
            SELECT * FROM case_attachments
            WHERE case_id = ?
            ORDER BY uploaded_at DESC
        """
        attachments = db.execute_query(attachment_query, (23,))

        if attachments:
            print(f"   ✅ 找到 {len(attachments)} 个附件:")
            for i, att in enumerate(attachments, 1):
                print(f"\n   附件 {i}:")
                print(f"      - ID: {att.get('attachment_id')}")
                print(f"      - 原始文件名: {att.get('original_filename')}")
                print(f"      - 文件路径: {att.get('file_path')}")
                print(f"      - 文件类型: {att.get('file_type')}")
                print(f"      - 附件类型: {att.get('attachment_type')}")

                # 检查文件是否存在
                file_path = Path(att.get('file_path', ''))
                if file_path.exists():
                    print(f"      - 文件存在: ✅")
                    print(f"      - 文件大小: {file_path.stat().st_size} 字节")
                else:
                    print(f"      - 文件存在: ❌ (路径: {file_path})")
        else:
            print(f"   ℹ️  案例ID 23 没有附件")
    except Exception as e:
        print(f"   ❌ 查询附件失败: {e}")
        logger.error(f"查询附件失败: {e}", exc_info=True)

    # 4. 测试API调用
    print("\n4. 测试 get_attachments 方法...")
    try:
        from ai_tender_system.modules.case_library.manager import CaseLibraryManager

        manager = CaseLibraryManager()
        result = manager.get_attachments(23)

        print(f"   ✅ API调用成功")
        print(f"   - 返回数据类型: {type(result)}")
        print(f"   - 返回数据长度: {len(result)}")

        if result:
            print(f"\n   返回的附件数据:")
            for i, att in enumerate(result, 1):
                print(f"\n   附件 {i}:")
                for key, value in att.items():
                    if key not in ['converted_images', 'conversion_info']:  # 跳过长JSON字段
                        print(f"      - {key}: {value}")
    except Exception as e:
        print(f"   ❌ API调用失败: {e}")
        logger.error(f"API调用失败: {e}", exc_info=True)

    # 5. 检查日志中的错误
    print("\n5. 建议检查的日志位置:")
    print("   - 应用日志: /path/to/logs/app.log")
    print("   - Flask日志: 检查Flask应用的标准输出")
    print("   - Nginx日志: /var/log/nginx/error.log")

    print("\n" + "="*80)
    print("诊断完成")
    print("="*80 + "\n")


if __name__ == '__main__':
    diagnose_case_23()
