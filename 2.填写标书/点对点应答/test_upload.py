#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试招标信息提取上传功能
"""

import requests
import os

def test_tender_info_upload():
    """测试招标信息提取上传功能"""
    
    # 创建一个简单的测试文档
    test_content = """
    招标公告
    
    项目名称：哈银消金2025年-2027年运营商数据采购项目
    招标编号：GXTC-C-251590031
    招标人：哈尔滨哈银消费金融有限责任公司
    招标代理：国信招标集团股份有限公司
    投标方式：公开招标
    投标地点：北京市朝阳区建国路88号现代城A座
    投标时间：2025年1月15日 09:30
    中标人数量：1家
    """
    
    # 创建测试文件
    test_file_path = 'test_tender.txt'
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # 准备上传数据
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_tender.txt', f, 'text/plain')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("正在测试招标信息提取上传...")
            response = requests.post('http://localhost:8082/extract-tender-info', 
                                   files=files, data=data, timeout=30)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 上传和提取成功!")
                    print("提取的信息:")
                    for key, value in result.get('tender_info', {}).items():
                        print(f"  {key}: {value}")
                else:
                    print(f"❌ 提取失败: {result.get('error')}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_tender_info_upload()