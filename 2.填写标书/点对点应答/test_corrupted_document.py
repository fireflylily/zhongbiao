#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试损坏或异常文档的处理
"""

import requests
import os

def test_corrupted_document():
    """测试损坏文档的处理"""
    
    # 创建一个模拟损坏的文档（实际上是一个文本文件但扩展名为docx）
    corrupted_file = 'corrupted_test.docx'
    with open(corrupted_file, 'w', encoding='utf-8') as f:
        f.write("This is not a real Word document, just plain text content.")
    
    try:
        with open(corrupted_file, 'rb') as f:
            files = {'file': (corrupted_file, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("🔍 测试损坏文档的处理...")
            
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
                    print("✅ 系统成功处理了损坏的文档!")
                    tender_info = result.get('tender_info', {})
                    project_name = tender_info.get('project_name', '')
                    
                    if project_name and ('文档格式异常' in project_name or '未明确标注' in project_name):
                        print(f"✅ 正确识别为异常文档: '{project_name}'")
                    else:
                        print(f"⚠️  项目名称: '{project_name}'")
                    
                    print("\n📋 提取结果:")
                    for key, value in tender_info.items():
                        print(f"   • {key}: {value}")
                        
                else:
                    print(f"❌ 提取失败: {result.get('error')}")
                    # 这个结果也是可以接受的，说明系统正确识别了问题
                    if "缺少必要字段" in str(result.get('error')):
                        print("✅ 系统正确识别了文档问题")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                if response.status_code == 500 and "project_name" in response.text:
                    print("⚠️  这是预期的错误，修复后应该能够处理")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        if os.path.exists(corrupted_file):
            os.remove(corrupted_file)

def test_empty_document():
    """测试空文档"""
    
    empty_file = 'empty_test.txt'
    with open(empty_file, 'w', encoding='utf-8') as f:
        f.write("")
    
    try:
        with open(empty_file, 'rb') as f:
            files = {'file': (empty_file, f, 'text/plain')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("\n🔍 测试空文档的处理...")
            
            response = requests.post(
                'http://localhost:8082/extract-tender-info',
                files=files, 
                data=data, 
                timeout=30
            )
            
            print(f"📡 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 系统成功处理了空文档!")
                if result.get('success'):
                    tender_info = result.get('tender_info', {})
                    project_name = tender_info.get('project_name', '')
                    print(f"📝 项目名称: '{project_name}'")
                else:
                    print(f"提取结果: {result.get('error')}")
                    
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        if os.path.exists(empty_file):
            os.remove(empty_file)

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 异常文档处理测试")
    print("=" * 60)
    
    test_corrupted_document()
    test_empty_document()
    
    print("=" * 60)
    print("✅ 测试完成")