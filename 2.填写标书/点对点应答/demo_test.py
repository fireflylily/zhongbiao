#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标信息提取系统演示测试
不需要真实API密钥的演示版本
"""

import requests
import os
import json

def test_tender_info_demo():
    """演示招标信息提取功能（不需要真实API密钥）"""
    
    # 创建测试文档内容
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
    预算金额：500万元
    """
    
    # 创建测试文件
    test_file_path = 'demo_tender.txt'
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # 准备上传数据
        with open(test_file_path, 'rb') as f:
            files = {'file': ('demo_tender.txt', f, 'text/plain')}
            data = {'api_key': 'demo-key'}  # 演示密钥
            
            print("🔍 正在测试招标信息提取功能（演示模式）...")
            print(f"📄 测试文件内容预览:")
            print("-" * 50)
            print(test_content.strip())
            print("-" * 50)
            
            # 模拟提取结果（实际系统会调用AI API）
            demo_result = {
                "success": True,
                "tender_info": {
                    "项目名称": "哈银消金2025年-2027年运营商数据采购项目",
                    "招标编号": "GXTC-C-251590031", 
                    "招标人": "哈尔滨哈银消费金融有限责任公司",
                    "招标代理": "国信招标集团股份有限公司",
                    "投标方式": "公开招标",
                    "投标地点": "北京市朝阳区建国路88号现代城A座",
                    "投标时间": "2025年1月15日 09:30",
                    "中标人数量": "1家",
                    "预算金额": "500万元"
                }
            }
            
            print("\n✅ 演示：如果使用真实API密钥，系统会提取以下信息：")
            print(json.dumps(demo_result, ensure_ascii=False, indent=2))
            
            # 尝试连接到实际服务器（但会失败，因为使用的是演示密钥）
            print("\n🌐 尝试连接到Web服务器进行实际测试...")
            try:
                response = requests.post(
                    'http://localhost:8082/extract-tender-info',
                    files=files, 
                    data=data, 
                    timeout=10
                )
                
                print(f"📡 服务器响应状态码: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print("✅ 服务器响应成功!")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(f"⚠️  服务器返回错误: {response.text}")
                    print("\n💡 提示：这是预期的，因为使用的是演示API密钥")
                    print("   在实际使用中，请提供有效的API密钥")
                    
            except requests.exceptions.ConnectionError:
                print("❌ 无法连接到Web服务器")
                print("   请确保服务器正在运行: python3 web_app.py")
            except Exception as e:
                print(f"❌ 连接出错: {e}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def show_system_info():
    """显示系统信息"""
    print("=" * 60)
    print("🤖 AI标书点对点应答系统 - 招标信息提取演示")
    print("=" * 60)
    print("📋 系统功能:")
    print("  • 自动提取招标文档中的关键信息")
    print("  • 支持 .docx, .doc, .txt, .pdf 格式")
    print("  • Web界面操作，简单易用")
    print("  • AI智能解析，准确率高")
    print()
    print("🚀 启动方式:")
    print("  1. python3 web_app.py")
    print("  2. 打开浏览器访问 http://localhost:8082")
    print("  3. 上传招标文档并提供API密钥")
    print()
    print("💡 注意事项:")
    print("  • 需要有效的API密钥才能正常工作")
    print("  • 本演示使用模拟数据展示功能")
    print("=" * 60)
    print()

if __name__ == "__main__":
    show_system_info()
    test_tender_info_demo()