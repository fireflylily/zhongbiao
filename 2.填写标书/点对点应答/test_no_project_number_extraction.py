#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试没有项目编号情况下的信息提取功能
"""

import requests
import os
import json

def test_no_project_number_extraction():
    """测试没有项目编号时的信息提取功能"""
    
    test_file_path = 'test_no_project_number.txt'
    
    try:
        # 准备上传数据
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_no_project_number.txt', f, 'text/plain')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("🔍 测试没有项目编号时的信息提取功能...")
            print("📄 测试文档特点:")
            print("   • 包含项目名称：办公设备采购项目")
            print("   • 包含投标时间：2025年10月15日下午2:30前")
            print("   • ❌ 不包含项目编号信息")
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
                    print("\n📊 提取结果分析:")
                    tender_info = result.get('tender_info', {})
                    
                    # 检查项目编号处理
                    project_number = tender_info.get('project_number', '')
                    print(f"📋 项目编号: '{project_number}'")
                    
                    if project_number == '' or project_number is None:
                        print("✅ 项目编号正确处理：返回空值")
                    else:
                        print(f"⚠️  项目编号处理异常：'{project_number}' (应该为空)")
                    
                    # 检查其他必要信息是否正确提取
                    project_name = tender_info.get('project_name', '')
                    bidding_time = tender_info.get('bidding_time', '')
                    
                    print(f"📝 项目名称: '{project_name}'")
                    print(f"🕐 投标时间: '{bidding_time}'")
                    
                    if project_name and '办公设备采购项目' in project_name:
                        print("✅ 项目名称提取正确")
                    else:
                        print("❌ 项目名称提取错误")
                        
                    if bidding_time and '2025年10月15日' in bidding_time:
                        print("✅ 投标时间提取正确")
                    else:
                        print("❌ 投标时间提取错误")
                    
                    print("\n📋 完整提取信息:")
                    for key, value in tender_info.items():
                        status = "✅" if value else "➖"
                        print(f"   {status} {key}: {value}")
                        
                else:
                    print(f"❌ 提取失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 项目编号缺失情况测试")
    print("=" * 60)
    test_no_project_number_extraction()
    print("=" * 60)