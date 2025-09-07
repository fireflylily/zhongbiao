# -*- coding: utf-8 -*-
"""
简化系统测试（不依赖pytest）
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
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
        from modules.tender_info import TenderInfoExtractor, TenderInfo
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
        
        # 重新加载配置
        config = reload_config()
        
        # 验证配置
        assert config.llm.api_key == 'test-key-12345'
        assert config.app.log_level == 'INFO'
        assert config.llm.model == 'gpt-4o-mini'
        
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
        
        # 测试支持格式
        formats = processor.get_supported_formats()
        assert '.txt' in formats
        print(f"支持的格式: {formats}")
        
        # 创建测试文件
        test_content = """
        项目名称：AI标书系统测试项目
        项目编号：TEST-AI-2024-001
        招标人：测试科技有限公司
        投标截止时间：2024年12月31日17时00分
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        # 测试文档处理
        content = processor.process_document(test_file)
        assert "AI标书系统测试项目" in content
        assert "TEST-AI-2024-001" in content
        
        # 清理
        os.unlink(test_file)
        
        print("✅ 文档处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 文档处理测试失败: {e}")
        return False


def test_data_models():
    """测试数据模型"""
    print("\n🔍 测试数据模型...")
    
    try:
        from modules.tender_info.models import TenderInfo, QualificationRequirements
        
        # 创建测试对象
        tender_info = TenderInfo(
            project_name="测试项目",
            project_number="TEST-001",
            tenderer="测试公司"
        )
        
        # 验证基本功能
        assert tender_info.is_valid()
        assert tender_info.project_name == "测试项目"
        
        # 测试字典转换
        data_dict = tender_info.to_dict()
        assert data_dict['project_name'] == "测试项目"
        
        # 测试从字典恢复
        restored = TenderInfo.from_dict(data_dict)
        assert restored.project_name == tender_info.project_name
        
        # 测试摘要
        summary = tender_info.get_summary()
        assert "测试项目" in summary
        
        print("✅ 数据模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False


def test_tender_extractor():
    """测试招标信息提取器"""
    print("\n🔍 测试招标信息提取...")
    
    try:
        from modules.tender_info import TenderInfoExtractor
        
        # 创建测试文档
        test_document = """
        一、项目名称：AI标书系统重构测试项目
        二、招标编号：**REFACTOR-TEST-2024**
        
        招标人：重构测试科技有限公司
        招标代理机构：测试代理公司（招标代理机构）
        投标方式：公开招标
        投标地点：北京市海淀区中关村
        投标截止时间：2024年12月31日15时30分
        预计成交供应商数量：1家
        
        投标人资格要求：
        1. 具有独立承担民事责任能力的法人，须提供营业执照副本；
        2. 具有增值税纳税人资格，须提供相关证明；
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_document)
            test_file = f.name
        
        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = TenderInfoExtractor(output_dir=temp_dir)
            
            # 读取文档
            content = extractor.document_processor.process_document(test_file)
            
            # 测试正则提取（避免API调用）
            tender_info = extractor._regex_extraction(content)
            tender_info.source_file = test_file
            
            # 验证结果
            assert "AI标书系统重构测试项目" in tender_info.project_name
            assert "REFACTOR-TEST-2024" in tender_info.project_number
            assert "重构测试科技有限公司" in tender_info.tenderer
            
            print(f"项目名称: {tender_info.project_name}")
            print(f"项目编号: {tender_info.project_number}")
            print(f"招标人: {tender_info.tenderer}")
            
            # 测试配置保存
            config_file = extractor.save_to_config(tender_info)
            assert os.path.exists(config_file)
            
        # 清理
        os.unlink(test_file)
        
        print("✅ 招标信息提取测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 招标信息提取测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("🧪 AI标书系统 v2.0 - 集成测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置系统", test_config),
        ("文档处理", test_document_processor),
        ("数据模型", test_data_models),
        ("招标提取", test_tender_extractor)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统重构成功！")
        print("\n📋 下一步:")
        print("1. 设置 export SHIHUANG_API_KEY='your-real-api-key'")
        print("2. 运行 python web/app.py 启动Web服务")
        print("3. 访问 http://localhost:5000 使用系统")
        return True
    else:
        print("⚠️ 部分测试失败，需要检查和修复")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)