#!/usr/bin/env python3
"""
基础测试脚本 - 测试系统的基本功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试模块导入"""
    try:
        print("测试基础导入...")
        import config
        print("✅ config模块导入成功")
        
        from utils.file_utils import get_file_utils
        print("✅ file_utils模块导入成功")
        
        from utils.llm_client import get_llm_client
        print("✅ llm_client模块导入成功")
        
        from parsers.tender_parser import get_tender_parser
        print("✅ tender_parser模块导入成功")
        
        from parsers.product_parser import get_product_parser
        print("✅ product_parser模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_file_reading(file_path):
    """测试文件读取功能"""
    try:
        print(f"测试文件读取: {os.path.basename(file_path)}")
        
        from utils.file_utils import get_file_utils
        file_utils = get_file_utils()
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        # 尝试读取文件
        file_data = file_utils.read_file(file_path)
        
        if 'error' in file_data:
            print(f"❌ 文件读取失败: {file_data['error']}")
            return False
        
        print(f"✅ 文件读取成功")
        print(f"   文件类型: {file_data.get('type', 'unknown')}")
        
        # 尝试提取文本
        text_content = file_utils.extract_text_content(file_data)
        if text_content:
            print(f"   文本长度: {len(text_content)} 字符")
            print(f"   预览: {text_content[:100]}...")
        else:
            print("   ⚠️ 未能提取文本内容")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件读取测试失败: {e}")
        return False

def test_api_connection():
    """测试API连接"""
    try:
        print("测试API连接...")
        
        from utils.llm_client import get_llm_client
        llm_client = get_llm_client()
        
        # 简单的连接测试
        result = llm_client.chat_completion("测试", max_tokens=10)
        
        if result:
            print("✅ API连接成功")
            return True
        else:
            print("❌ API连接失败")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== 自动标书生成系统 - 基础测试 ===\\n")
    
    # 测试模块导入
    if not test_imports():
        print("\\n❌ 模块导入测试失败，请检查依赖包安装")
        return
    
    print("\\n" + "="*50)
    
    # 获取命令行参数
    if len(sys.argv) > 1:
        tender_file = sys.argv[1]
        print(f"\\n测试招标文件: {tender_file}")
        test_file_reading(tender_file)
    
    if len(sys.argv) > 2:
        product_file = sys.argv[2]
        print(f"\\n测试产品文件: {product_file}")
        test_file_reading(product_file)
    
    print("\\n" + "="*50)
    
    # 测试API连接（可选）
    print("\\n")
    try:
        test_api_connection()
    except KeyboardInterrupt:
        print("\\n⏹️ 用户跳过API测试")
    
    print("\\n=== 基础测试完成 ===")

if __name__ == "__main__":
    main()