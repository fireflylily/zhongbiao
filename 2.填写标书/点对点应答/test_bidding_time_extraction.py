#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试投标时间提取功能
"""

import requests
import os
import json

def test_bidding_time_extraction():
    """测试投标时间提取功能"""
    
    test_file_path = 'test_bidding_time.txt'
    
    try:
        # 准备上传数据
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_bidding_time.txt', f, 'text/plain')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("🔍 测试投标时间提取功能...")
            print("📄 测试文档包含以下关键信息:")
            print("   • 应答文件递交截止时间：2025年9月4日上午9:00前")
            print("   • 磋商时间：2025年9月4日上午9:30")
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
                    print("\n📊 提取结果:")
                    tender_info = result.get('tender_info', {})
                    
                    # 重点检查投标时间提取
                    bidding_time = tender_info.get('bidding_time', '')
                    print(f"🕐 投标时间: '{bidding_time}'")
                    
                    if bidding_time:
                        if '2025年9月4日' in bidding_time and ('9:00' in bidding_time or '9：00' in bidding_time):
                            print("✅ 投标时间提取正确!")
                        else:
                            print("⚠️  投标时间提取可能不完整")
                    else:
                        print("❌ 投标时间未提取到")
                    
                    print("\n📋 完整提取信息:")
                    for key, value in tender_info.items():
                        print(f"   • {key}: {value}")
                        
                else:
                    print(f"❌ 提取失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 投标时间提取功能测试")
    print("=" * 60)
    test_bidding_time_extraction()
    print("=" * 60)