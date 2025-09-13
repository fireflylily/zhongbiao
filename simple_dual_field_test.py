#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的双字段处理测试
"""
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append('/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/ai_tender_system')

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_dual_field_direct():
    """直接测试双字段处理方法"""
    from modules.point_to_point.processor import PointToPointProcessor
    
    processor = PointToPointProcessor()
    
    # 设置公司信息
    processor.company_info = {
        'companyName': '智慧足迹数据科技有限公司',
        'fixedPhone': '010-63271000',
        'email': 'lvhe@smartsteps.com',
        'address': '北京市东城区王府井大街200号七层711室',
        'postalCode': '100006'
    }
    
    print("=== 直接测试双字段处理方法 ===")
    
    # 测试用例
    test_cases = [
        ("地址+邮编", "地址: 北京市东城区王府井大街200号七层711室邮编：____________", "地址"),
        ("电话+邮箱(空格)", "电话                    电子邮箱", "电话"), 
        ("电话+邮箱(紧邻)", "电话：010-63271000电子邮箱：", "电话"),
    ]
    
    for name, text, current_field in test_cases:
        print(f"\n--- {name} ---")
        print(f"输入: '{text}'")
        print(f"当前字段: {current_field}")
        
        try:
            result = processor._handle_dual_field_table_layout(text, current_field, "010-63271000")
            print(f"输出: '{result}'")
            
            if result != text:
                print("✅ 处理成功")
            else:
                print("❌ 无变化")
        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_dual_field_direct()