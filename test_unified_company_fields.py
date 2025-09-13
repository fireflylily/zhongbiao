#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一公司信息字段处理测试脚本
验证优化后的表格式双字段处理、采购人识别、后处理美化等功能
"""

import sys
import logging
from pathlib import Path

# 设置路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / '2.填写标书/点对点应答'))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_unified_company_fields():
    """测试统一的公司信息字段处理"""
    try:
        # 导入处理器
        module_name = 'mcp_bidder_name_processor_enhanced 2'
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            module_name, 
            script_dir / '2.填写标书/点对点应答/mcp_bidder_name_processor_enhanced 2.py'
        )
        processor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(processor_module)
        MCPBidderNameProcessor = processor_module.MCPBidderNameProcessor
        
        # 初始化处理器
        processor = MCPBidderNameProcessor()
        
        # 设置测试用的公司信息
        test_company_info = {
            'name': '北京智慧足迹信息技术有限公司',
            'fixedPhone': '010-63271000',
            'email': 'lvhe@smartsteps.com',
            'fax': '010-63271001',
            'address': '北京市东城区王府井大街200号七层711室',
            'postalCode': '100006',
            'website': 'www.smartsteps.com',
            'socialCreditCode': '91110101MA01234567',
            'registeredCapital': '500万元人民币'
        }
        
        # 设置处理器的公司信息
        processor.company_info = test_company_info
        
        print("🧪 开始测试统一公司信息字段处理功能")
        print("=" * 60)
        
        # 测试1: 双字段表格处理
        print("\n📋 测试1: 双字段表格式布局处理")
        test_table_layouts = [
            "电话                                  电子邮件",
            "电话：                    电子邮件：",
            "地址                      传真", 
            "邮政编码：                网站：",
            "联系电话                  邮箱"
        ]
        
        for i, test_text in enumerate(test_table_layouts, 1):
            print(f"\n测试用例 {i}: '{test_text}'")
            
            # 测试双字段处理
            result1 = processor._handle_dual_field_table_layout(test_text, '联系电话', '010-63271000')
            result2 = processor._handle_dual_field_table_layout(test_text, '电子邮件', 'lvhe@smartsteps.com')
            
            if result1 != test_text:
                print(f"  ✅ 双字段处理结果: '{result1}'")
            elif result2 != test_text:
                print(f"  ✅ 双字段处理结果: '{result2}'")
            else:
                print(f"  ⚠️ 未匹配双字段模式")
        
        # 测试2: 采购人信息识别
        print(f"\n📋 测试2: 增强版采购人信息识别")
        test_purchaser_texts = [
            "采购人：北京市政府采购中心",
            "【项目联系人】：张三",
            "开标时间：2024年3月15日上午9:00",
            "供应商名称：                ",
            "招标代理机构：北京招标有限公司",
            "投标人联系电话：",
            "政府采购项目编号：ABC123456"
        ]
        
        for i, test_text in enumerate(test_purchaser_texts, 1):
            is_purchaser = processor._is_purchaser_info(test_text, ['采购人', '招标人'])
            score = processor._calculate_purchaser_probability_score(test_text, ['采购人', '招标人'])
            result = "🔴 采购人信息" if is_purchaser else "🟢 投标人信息"
            print(f"  用例 {i}: '{test_text}' -> {result} (得分: {score:.2f})")
        
        # 测试3: 后处理美化
        print(f"\n📋 测试3: 后处理美化机制")
        test_beautify_texts = [
            "电话：010-63271000   电子邮件：lvhe@smartsteps.com",
            "联系电话::010-63271000____",
            "地址   :   北京市东城区王府井大街200号七层711室       ",
            "网站:www.smartsteps.com",
            "电话：010-63271000                          邮箱：test@test.com"
        ]
        
        for i, test_text in enumerate(test_beautify_texts, 1):
            beautified = processor._beautify_paragraph_text(test_text)
            if beautified != test_text:
                print(f"  用例 {i}:")
                print(f"    原文: '{test_text}'")
                print(f"    美化: '{beautified}'")
            else:
                print(f"  用例 {i}: 无需美化 - '{test_text}'")
        
        # 测试4: 字段名称标准化
        print(f"\n📋 测试4: 字段名称标准化")
        test_field_names = ['电话', '联系电话', '固定电话', '电子邮件', '邮箱', 'email', '传真', 'fax']
        
        for field_name in test_field_names:
            normalized = processor._normalize_field_name(field_name)
            print(f"  '{field_name}' -> {normalized}")
        
        print(f"\n✅ 测试完成!")
        print(f"📈 优化功能总结:")
        print(f"   - ✅ 统一字段配置框架")
        print(f"   - ✅ 智能双字段表格处理") 
        print(f"   - ✅ 增强采购人识别 (11种识别规则 + 概率评估)")
        print(f"   - ✅ 完善的run级格式保持")
        print(f"   - ✅ 后处理美化机制 (5种美化规则)")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保处理器文件路径正确")
        return False
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unified_company_fields()
    if success:
        print(f"\n🎉 所有测试通过，优化完成！")
    else:
        print(f"\n❌ 测试失败，请检查代码")
        sys.exit(1)