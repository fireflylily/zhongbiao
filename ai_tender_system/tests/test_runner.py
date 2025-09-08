# -*- coding: utf-8 -*-
"""
测试运行器
"""

import os
import sys
import tempfile
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from common.config import get_config
        from common.logger import setup_logging, get_logger
        from common.document_processor import get_document_processor
        print("✅ 公共组件导入成功")
    except Exception as e:
        print(f"❌ 公共组件导入失败: {e}")
        return False
    
    try:
        from modules.tender_info.extractor import TenderInfoExtractor
        from modules.tender_info.models import TenderInfo
        print("✅ 业务模块导入成功")
    except Exception as e:
        print(f"❌ 业务模块导入失败: {e}")
        return False
    
    return True


def test_config():
    """测试配置系统"""
    print("\n🔍 测试配置系统...")
    
    # 设置测试环境变量
    os.environ['SHIHUANG_API_KEY'] = 'test-key-12345'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    try:
        from common.config import get_config, reload_config
        
        config = reload_config()
        
        assert config.llm.api_key == 'test-key-12345'
        assert config.app.log_level == 'INFO'
        
        print("✅ 配置系统测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")
        return False


def test_document_processor():
    """测试文档处理"""
    print("\n🔍 测试文档处理...")
    
    try:
        from common.document_processor import get_document_processor
        
        processor = get_document_processor()
        formats = processor.get_supported_formats()
        print(f"支持格式: {formats}")
        
        # 创建测试文件
        test_content = """
        项目名称：系统测试项目
        项目编号：SYS-TEST-001
        招标人：系统测试公司
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        content = processor.process_document(test_file)
        assert "系统测试项目" in content
        
        os.unlink(test_file)
        
        print("✅ 文档处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 文档处理测试失败: {e}")
        return False


def test_tender_extraction():
    """测试招标信息提取"""
    print("\n🔍 测试招标信息提取...")
    
    try:
        from modules.tender_info.extractor import TenderInfoExtractor
        
        test_document = """
        一、项目名称：重构测试项目
        二、招标编号：**REFACTOR-2024**
        
        招标人：重构测试公司
        投标截止时间：2024年12月31日16时00分
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_document)
            test_file = f.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = TenderInfoExtractor(output_dir=temp_dir)
            content = extractor.document_processor.process_document(test_file)
            tender_info = extractor._regex_extraction(content)
            
            assert "重构测试项目" in tender_info.project_name
            print(f"提取项目名称: {tender_info.project_name}")
            
        os.unlink(test_file)
        
        print("✅ 招标信息提取测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 招标信息提取测试失败: {e}")
        return False


def run_tests():
    """运行所有测试"""
    print("🧪 AI标书系统 v2.0 - 重构测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("配置系统", test_config),
        ("文档处理", test_document_processor),
        ("招标提取", test_tender_extraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 系统重构测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False


if __name__ == "__main__":
    run_tests()