# -*- coding: utf-8 -*-
"""
系统集成测试
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.config import get_config, reload_config
from common.logger import setup_logging, get_logger
from common.document_processor import get_document_processor
from modules.tender_info import TenderInfoExtractor, TenderInfo


class TestSystemIntegration:
    """系统集成测试"""
    
    def setup_method(self):
        """测试前设置"""
        # 设置测试环境变量
        os.environ['SHIHUANG_API_KEY'] = 'test-key-for-testing'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        # 重新加载配置
        reload_config()
        
        # 初始化日志
        setup_logging()
        self.logger = get_logger("test_system")
    
    def test_config_loading(self):
        """测试配置加载"""
        config = get_config()
        
        # 验证配置加载
        assert config.llm.api_key == 'test-key-for-testing'
        assert config.app.log_level == 'DEBUG'
        assert config.llm.model == 'gpt-4o-mini'
        
        self.logger.info("✅ 配置加载测试通过")
    
    def test_document_processor(self):
        """测试文档处理器"""
        processor = get_document_processor()
        
        # 测试支持的格式
        formats = processor.get_supported_formats()
        assert '.txt' in formats
        assert '.docx' in formats
        
        # 创建测试文本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            test_content = """
            测试招标文档
            项目名称：测试项目
            项目编号：TEST-2024-001
            招标人：测试公司
            """
            f.write(test_content)
            test_file = f.name
        
        try:
            # 测试文档处理
            content = processor.process_document(test_file)
            assert "测试项目" in content
            assert "TEST-2024-001" in content
            
            self.logger.info("✅ 文档处理器测试通过")
            
        finally:
            # 清理测试文件
            os.unlink(test_file)
    
    def test_tender_info_extraction_without_api(self):
        """测试招标信息提取（不调用API）"""
        # 创建测试文档
        test_document = """
        **一、项目名称：** 测试招标项目
        **二、招标编号：** **TEST-2024-001**
        
        招标人：测试招标公司
        代理机构：测试代理公司（招标代理机构）
        投标方式：公开招标
        投标地点：北京市朝阳区
        投标截止时间：2024年12月31日14时30分
        预计成交供应商数量：1家
        
        投标人资格要求：
        1. 具有独立承担民事责任能力的法人，须提供营业执照副本；
        2. 具有增值税纳税人资格，须提供税务登记证；
        3. 须提供近3年类似项目业绩证明；
        4. 须提供法人授权委托书；
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_document)
            test_file = f.name
        
        try:
            # 创建临时输出目录
            with tempfile.TemporaryDirectory() as temp_dir:
                extractor = TenderInfoExtractor(output_dir=temp_dir)
                
                # 只测试正则表达式提取（避免API调用）
                content = extractor.document_processor.process_document(test_file)
                tender_info = extractor._regex_extraction(content)
                tender_info.source_file = test_file
                
                # 验证提取结果
                assert tender_info.project_name == "测试招标项目"
                assert tender_info.project_number == "TEST-2024-001"
                assert tender_info.tenderer == "测试招标公司"
                assert "测试代理公司" in tender_info.agency
                
                # 测试配置保存
                config_file = extractor.save_to_config(tender_info)
                assert os.path.exists(config_file)
                
                self.logger.info("✅ 招标信息提取测试通过")
        
        finally:
            os.unlink(test_file)
    
    def test_data_models(self):
        """测试数据模型"""
        # 测试TenderInfo模型
        tender_info = TenderInfo(
            project_name="测试项目",
            project_number="TEST-001",
            tenderer="测试公司"
        )
        
        # 测试转换为字典
        data_dict = tender_info.to_dict()
        assert data_dict['project_name'] == "测试项目"
        assert data_dict['project_number'] == "TEST-001"
        
        # 测试从字典创建
        restored_info = TenderInfo.from_dict(data_dict)
        assert restored_info.project_name == tender_info.project_name
        assert restored_info.project_number == tender_info.project_number
        
        # 测试有效性检查
        assert tender_info.is_valid()
        
        empty_info = TenderInfo()
        assert not empty_info.is_valid()
        
        self.logger.info("✅ 数据模型测试通过")
    
    def teardown_method(self):
        """测试后清理"""
        # 清理环境变量
        if 'SHIHUANG_API_KEY' in os.environ:
            del os.environ['SHIHUANG_API_KEY']
        if 'LOG_LEVEL' in os.environ:
            del os.environ['LOG_LEVEL']


def run_manual_tests():
    """手动运行测试"""
    print("🧪 开始系统集成测试...")
    
    test_instance = TestSystemIntegration()
    tests = [
        ('配置加载', test_instance.test_config_loading),
        ('文档处理器', test_instance.test_document_processor),
        ('数据模型', test_instance.test_data_models),
        ('招标信息提取', test_instance.test_tender_info_extraction_without_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 测试: {test_name}")
            test_instance.setup_method()
            test_func()
            print(f"✅ {test_name} - 通过")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} - 失败: {e}")
        finally:
            test_instance.teardown_method()
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_manual_tests()
    sys.exit(0 if success else 1)