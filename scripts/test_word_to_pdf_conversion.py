#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Word 到 PDF 转换功能
验证Azure解析器的自动转换是否工作
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tender_system.modules.tender_processing.azure_parser import AzureDocumentParser, is_azure_available

def test_conversion():
    """测试转换功能"""
    print("=" * 60)
    print("Word 到 PDF 自动转换测试")
    print("=" * 60)

    # 检查 Azure 是否可用
    if not is_azure_available():
        print("\n⚠️  Azure Form Recognizer 未配置")
        print("请在 .env 中设置:")
        print("  - AZURE_FORM_RECOGNIZER_ENDPOINT")
        print("  - AZURE_FORM_RECOGNIZER_KEY")
        return False

    # 查找测试文档
    test_docs_dir = Path(__file__).parent.parent / 'ai_tender_system' / 'data' / 'parser_debug'

    if not test_docs_dir.exists():
        print(f"\n⚠️  测试目录不存在: {test_docs_dir}")
        return False

    # 查找第一个 .docx 文件
    docx_files = list(test_docs_dir.glob('*.docx'))

    if not docx_files:
        print(f"\n⚠️  未找到 .docx 测试文件")
        print(f"请上传一个文档到: {test_docs_dir}")
        return False

    test_file = docx_files[0]
    print(f"\n测试文件: {test_file.name}")
    print(f"文件大小: {test_file.stat().st_size / 1024:.1f} KB")

    try:
        # 创建解析器
        parser = AzureDocumentParser()
        print(f"\n✅ Azure 解析器初始化成功")
        print(f"端点: {parser.endpoint}")

        # 测试转换
        print(f"\n开始测试转换...")
        pdf_path = parser._convert_docx_to_pdf(str(test_file))

        if pdf_path:
            print(f"✅ 转换成功！")
            print(f"PDF路径: {pdf_path}")
            print(f"PDF大小: {Path(pdf_path).stat().st_size / 1024:.1f} KB")

            # 清理
            Path(pdf_path).unlink()
            print(f"✅ 临时文件已清理")

            return True
        else:
            print(f"❌ 转换失败")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_conversion()
    sys.exit(0 if success else 1)
