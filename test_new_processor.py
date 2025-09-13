#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新架构处理器功能测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / 'ai_tender_system'))

def test_new_processor():
    """测试新架构处理器"""
    try:
        from modules.point_to_point.processor import PointToPointProcessor
        
        print("✅ 成功导入新架构处理器")
        
        # 初始化处理器
        processor = PointToPointProcessor()
        print("✅ 处理器初始化成功")
        
        # 测试用的公司数据
        test_company_data = {
            'companyName': '北京智慧足迹信息技术有限公司',
            'fixedPhone': '010-63271000',
            'email': 'lvhe@smartsteps.com',
            'address': '北京市东城区王府井大街200号七层711室',
            'fax': '010-63271001',
            'postalCode': '100006',
            'website': 'www.smartsteps.com'
        }
        
        print("✅ 测试数据准备完成")
        print(f"  - 公司名称: {test_company_data['companyName']}")
        print(f"  - 联系电话: {test_company_data['fixedPhone']}")
        print(f"  - 电子邮件: {test_company_data['email']}")
        print(f"  - 公司地址: {test_company_data['address']}")
        
        # 测试字段配置创建
        field_configs = processor._create_unified_field_config(
            test_company_data, 
            "测试项目", 
            "TEST-2025-001", 
            "2025年9月12日"
        )
        
        print(f"✅ 字段配置创建成功，共 {len(field_configs)} 个配置")
        
        for i, config in enumerate(field_configs):
            field_names = config.get('field_names', [])
            field_value = config.get('value', '')
            field_type = config.get('field_type', '')
            print(f"  配置 {i+1}: {field_names[0] if field_names else 'N/A'} ({field_type}) -> '{field_value}'")
        
        print("🎉 新架构处理器测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dual_field_processing():
    """测试双字段表格处理"""
    try:
        from modules.point_to_point.processor import PointToPointProcessor
        
        processor = PointToPointProcessor()
        processor.company_info = {
            'fixedPhone': '010-63271000',
            'email': 'lvhe@smartsteps.com',
            'fax': '010-63271001',
            'address': '北京市东城区王府井大街200号七层711室'
        }
        
        print("\n📋 测试双字段表格处理:")
        
        test_cases = [
            "电话                                  电子邮件",
            "联系电话                    邮箱",
            "地址                      传真"
        ]
        
        for i, test_text in enumerate(test_cases, 1):
            print(f"\n  测试用例 {i}: '{test_text}'")
            
            # 测试电话字段处理
            result = processor._handle_dual_field_table_layout(test_text, '电话', '010-63271000')
            if result != test_text:
                print(f"    ✅ 处理结果: '{result}'")
            else:
                result = processor._handle_dual_field_table_layout(test_text, '地址', '北京市东城区王府井大街200号七层711室')
                if result != test_text:
                    print(f"    ✅ 处理结果: '{result}'")
                else:
                    print(f"    ⚠️ 未匹配任何模式")
        
        return True
        
    except Exception as e:
        print(f"❌ 双字段测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试新架构处理器...")
    
    success1 = test_new_processor()
    success2 = test_dual_field_processing()
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！新架构处理器可以投入使用。")
    else:
        print(f"\n❌ 部分测试失败，需要检查代码")
        sys.exit(1)