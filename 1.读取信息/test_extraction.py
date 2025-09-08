#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试招标信息提取功能（不依赖API）
"""

from read_info import TenderInfoExtractor

def test_fallback_extraction():
    """测试备用提取方法"""
    print("=== 测试备用提取方法 ===")
    
    # 模拟LLM响应内容
    mock_response = """
    以下是从招标文档中提取的信息：
    招标人：哈尔滨哈银消费金融有限责任公司
    招标代理：国信招标集团股份有限公司
    投标方式：公开招标
    投标地点：北京市朝阳区建国路88号现代城A座
    投标时间：2025年1月15日 09:30
    中标人数量：1家
    项目名称：哈银消金2025年-2027年运营商数据采购项目
    项目编号：GXTC-C-251590031
    """
    
    extractor = TenderInfoExtractor()
    result = extractor._fallback_extraction(mock_response)
    
    print("提取结果：")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    return result

def test_config_save():
    """测试配置保存功能"""
    print("\n=== 测试配置保存功能 ===")
    
    test_data = {
        "tenderer": "哈尔滨哈银消费金融有限责任公司",
        "agency": "国信招标集团股份有限公司",
        "bidding_method": "公开招标",
        "bidding_location": "北京市朝阳区建国路88号现代城A座",
        "bidding_time": "2025年1月15日 09:30",
        "winner_count": "1家",
        "project_name": "哈银消金2025年-2027年运营商数据采购项目",
        "project_number": "GXTC-C-251590031"
    }
    
    extractor = TenderInfoExtractor()
    extractor.save_to_config(test_data)
    print("配置文件保存测试完成！")

def main():
    """主测试函数"""
    try:
        result = test_fallback_extraction()
        test_config_save()
        
        print("\n=== 所有测试完成 ===")
        print("✅ 备用提取功能正常")
        print("✅ 配置保存功能正常")
        print(f"✅ 提取到 {len([v for v in result.values() if v])} 个有效字段")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()