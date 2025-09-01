#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的信息提取功能
"""

import requests
import os
import json

def test_enhanced_extraction():
    """测试增强后的信息提取功能"""
    
    test_file_path = 'test_enhanced_extraction.txt'
    
    try:
        # 准备上传数据
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_enhanced_extraction.txt', f, 'text/plain')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("🔍 测试增强的信息提取功能...")
            print("📄 测试文档包含:")
            print("   ✅ 应答文件递交截止时间：2025年9月4日上午9:00前")
            print("   ❌ 无项目编号")
            print("   ✅ 其他完整信息")
            print()
            
            response = requests.post(
                'http://localhost:8082/extract-tender-info',
                files=files, 
                data=data, 
                timeout=30
            )
            
            print(f"📡 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 信息提取成功!")
                    print("\n📊 关键字段检查:")
                    tender_info = result.get('tender_info', {})
                    
                    # 重点检查投标时间
                    bidding_time = tender_info.get('bidding_time', '')
                    print(f"🕐 投标时间: '{bidding_time}'")
                    if bidding_time and ('2025年9月4日' in bidding_time or '9:00' in bidding_time or '9：00' in bidding_time):
                        print("   ✅ 投标时间提取正确")
                    elif bidding_time:
                        print("   ⚠️  投标时间提取不完整")
                    else:
                        print("   ❌ 投标时间未提取到")
                    
                    # 检查项目编号
                    project_number = tender_info.get('project_number', '')
                    print(f"📋 项目编号: '{project_number}'")
                    if not project_number or project_number == "":
                        print("   ✅ 项目编号正确处理（空值）")
                    elif "法定代表人" in project_number or "签字" in project_number:
                        print("   ❌ 项目编号错误提取了无关内容")
                    else:
                        print(f"   ⚠️  项目编号内容: {project_number}")
                    
                    # 检查其他字段
                    project_name = tender_info.get('project_name', '')
                    tenderer = tender_info.get('tenderer', '')
                    agency = tender_info.get('agency', '')
                    
                    print(f"📝 项目名称: '{project_name}'")
                    print(f"🏢 采购人: '{tenderer}'")
                    print(f"🏛️  代理机构: '{agency}'")
                    
                    print("\n📋 完整提取结果:")
                    for key, value in tender_info.items():
                        status = "✅" if value else "➖"
                        if key == 'bidding_time' and value and '2025年9月4日' in value:
                            status = "🎯"
                        elif key == 'project_number' and not value:
                            status = "✅"
                        elif key == 'project_number' and ("法定代表人" in value or "签字" in value):
                            status = "❌"
                        print(f"   {status} {key}: {value}")
                        
                else:
                    print(f"❌ 提取失败: {result.get('error', '未知错误')}")
                    print(f"详细信息: {result}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 增强版信息提取功能测试")
    print("=" * 60)
    test_enhanced_extraction()
    print("=" * 60)