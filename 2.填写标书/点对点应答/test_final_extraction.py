#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终的信息提取功能测试
"""

import requests
import os
import json

def test_real_document():
    """测试真实的Word文档"""
    
    # 假设用户有一个真实的Word文档
    docx_files = [f for f in os.listdir('.') if f.endswith('.docx')]
    
    if not docx_files:
        print("❌ 没有找到Word文档进行测试")
        return
    
    test_file = docx_files[0]
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print(f"🔍 测试真实Word文档: {test_file}")
            
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
                    tender_info = result.get('tender_info', {})
                    
                    print("\n📊 提取结果分析:")
                    
                    # 分析每个字段
                    field_analysis = {
                        'bidding_time': '投标时间',
                        'project_number': '项目编号', 
                        'project_name': '项目名称',
                        'tenderer': '采购人',
                        'agency': '代理机构',
                        'bidding_location': '投标地点',
                        'bidding_method': '投标方式',
                        'winner_count': '中标人数量'
                    }
                    
                    for field, name in field_analysis.items():
                        value = tender_info.get(field, '')
                        if field == 'bidding_time':
                            if value and any(year in value for year in ['2024', '2025', '2026']):
                                status = "✅"
                            elif value:
                                status = "⚠️ "
                            else:
                                status = "❌"
                        elif field == 'project_number':
                            if not value:
                                status = "✅" # 空值也是正确的
                            elif "法定代表人" in value or "签字" in value:
                                status = "❌"
                            else:
                                status = "✅"
                        else:
                            status = "✅" if value else "➖"
                        
                        print(f"   {status} {name}: '{value}'")
                    
                    # 检查问题
                    issues = []
                    if not tender_info.get('bidding_time'):
                        issues.append("投标时间未提取到")
                    
                    project_number = tender_info.get('project_number', '')
                    if project_number and ("法定代表人" in project_number or "签字" in project_number):
                        issues.append("项目编号提取了错误内容")
                    
                    if issues:
                        print(f"\n⚠️  发现问题:")
                        for issue in issues:
                            print(f"   • {issue}")
                    else:
                        print(f"\n🎉 所有字段提取正常!")
                        
                else:
                    print(f"❌ 提取失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_text_document():
    """测试文本文档"""
    
    test_content = """
中邮保险手机号实名认证服务采购项目竞争性磋商采购文件

项目名称：中邮保险手机号实名认证服务采购项目
采购人：中邮人寿保险股份有限公司
采购代理机构：北京国信招标有限公司

一、项目概况
本项目为中邮保险手机号实名认证服务采购，采用竞争性磋商方式进行采购。

三、磋商文件提交要求
（1）应答文件递交截止时间(即应答截止时间)：2025年9月4日上午9:00前；
（2）应答文件递交地点：北京市朝阳区建国路88号现代城A座2106室；
（3）成交供应商数量：1家。

四、磋商时间和地点
磋商时间：2025年9月4日上午9:30
磋商地点：北京市朝阳区建国路88号现代城A座2106室
    """
    
    test_file_path = 'final_test.txt'
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('final_test.txt', f, 'text/plain')}
            data = {'api_key': 'sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob'}
            
            print("🔍 测试标准文本文档...")
            
            response = requests.post(
                'http://localhost:8082/extract-tender-info',
                files=files, 
                data=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    tender_info = result.get('tender_info', {})
                    bidding_time = tender_info.get('bidding_time', '')
                    project_number = tender_info.get('project_number', '')
                    
                    print(f"✅ 投标时间: '{bidding_time}' " + 
                          ("✅" if '2025年9月4日' in bidding_time else "❌"))
                    print(f"✅ 项目编号: '{project_number}' " + 
                          ("✅" if not project_number else "❌"))
                else:
                    print(f"❌ 提取失败: {result.get('error')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
    
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 最终信息提取功能测试")
    print("=" * 60)
    
    print("\n📝 测试1: 标准文本文档")
    print("-" * 30)
    test_text_document()
    
    print("\n📄 测试2: 真实Word文档")
    print("-" * 30) 
    test_real_document()
    
    print("=" * 60)