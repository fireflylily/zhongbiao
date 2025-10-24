#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的文档结构解析器（简化版）
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 直接导入必要的模块，避免通过 __init__.py
sys.path.insert(0, str(project_root / "ai_tender_system"))

# 先导入 common 模块
from common import get_module_logger

# 再直接导入 structure_parser
import importlib.util
spec = importlib.util.spec_from_file_location(
    "structure_parser",
    project_root / "ai_tender_system" / "modules" / "tender_processing" / "structure_parser.py"
)
structure_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structure_parser)

DocumentStructureParser = structure_parser.DocumentStructureParser


def test_document(doc_path: str, doc_name: str):
    """测试单个文档"""
    print(f"\n{'='*80}")
    print(f"测试文档: {doc_name}")
    print(f"{'='*80}")

    parser = DocumentStructureParser()
    result = parser.parse_document_structure(doc_path)

    if result["success"]:
        stats = result["statistics"]
        print(f"✅ 解析成功！")
        print(f"   - 总章节数: {stats['total_chapters']}")
        print(f"   - 自动选中: {stats['auto_selected']}")
        print(f"   - 推荐跳过: {stats['skip_recommended']}")
        print(f"   - 总字数: {stats['total_words']}")

        # 显示章节结构（仅显示顶层章节）
        print(f"\n章节结构（顶层）:")
        for i, ch in enumerate(result["chapters"]):
            if i >= 10:  # 只显示前10个顶层章节
                break
            status = "✅" if ch["auto_selected"] else "❌" if ch["skip_recommended"] else "⚪"
            print(f"   {status} [{ch['level']}级] {ch['title']} ({ch['word_count']}字)")

        if len(result["chapters"]) > 10:
            print(f"   ... 还有 {len(result['chapters']) - 10} 个章节")
    else:
        print(f"❌ 解析失败: {result.get('error')}")

    return result["success"]


def main():
    """主测试函数"""
    base_path = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/7-标书读取"

    test_docs = [
        ("采购文件-2025-IT-0032所属运营商数据.doc", "采购文件-2025-IT-0032"),
        ("招标文件-哈银消金.docx", "招标文件-哈银消金（有'文件构成'问题）"),
        ("正式版（2025-066期）2025年信息公司上市公司股东会网络投票一键通项目磋商文件.docx", "磋商文件-股东会网络投票"),
        ("单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx", "单一谈判-手机信息核验"),
        ("数字人民币运营管理中心有限公司2025年二次放号查询服务采购项目采购需求文件-无目录.docx", "采购需求-二次放号（无目录）"),
        ("中邮保险手机号实名认证服务采购项目竞争性磋商采购文件.docx", "竞争性磋商-手机号实名认证"),
        ("采购谈判邀请函（采购项目：中国联通运营商个人数据服务）.doc", "谈判邀请函-运营商数据服务"),
        ("中国建设银行股份有限公司运营商失联修复外呼服务采购项目谈判文件(1).docx", "谈判文件-失联修复外呼"),
    ]

    success_count = 0
    total_count = len(test_docs)

    print("\n" + "="*80)
    print("开始集成测试：验证改进后的文档结构解析器")
    print("="*80)

    for filename, display_name in test_docs:
        doc_path = f"{base_path}/{filename}"
        try:
            if test_document(doc_path, display_name):
                success_count += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}")
    print(f"测试完成: {success_count}/{total_count} 个文档解析成功")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
