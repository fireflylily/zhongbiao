#!/usr/bin/env python3
"""
系统安装检查脚本
检查依赖包和配置是否正确
"""

import sys
import importlib

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.8+")
        return False

def check_required_packages():
    """检查必需的包"""
    required_packages = [
        'requests',
        'docx', 
        'openpyxl',
        'PyPDF2'
    ]
    
    print("\\n检查依赖包...")
    all_good = True
    
    for package in required_packages:
        try:
            # 特殊处理一些包名
            if package == 'docx':
                importlib.import_module('docx')
            elif package == 'PyPDF2':
                importlib.import_module('PyPDF2')
            else:
                importlib.import_module(package)
            
            print(f"✅ {package}")
            
        except ImportError:
            print(f"❌ {package} - 未安装")
            all_good = False
    
    return all_good

def check_config():
    """检查配置文件"""
    print("\\n检查配置文件...")
    
    try:
        import config
        print("✅ config.py 找到")
        
        # 检查关键配置
        if hasattr(config, 'SHIHUANG_API_KEY'):
            api_key = config.SHIHUANG_API_KEY
            if api_key and api_key != "your-api-key-here":
                print("✅ API密钥已配置")
            else:
                print("⚠️ API密钥需要配置")
        
        if hasattr(config, 'SHIHUANG_BASE_URL'):
            print(f"✅ API地址: {config.SHIHUANG_BASE_URL}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 配置文件导入失败: {e}")
        return False

def check_directories():
    """检查目录结构"""
    print("\\n检查目录结构...")
    
    import os
    required_dirs = [
        'parsers',
        'matchers', 
        'generators',
        'utils'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - 目录缺失")
            all_good = False
    
    return all_good

def main():
    """主检查函数"""
    print("=== 自动标书生成系统 - 安装检查 ===\\n")
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_required_packages), 
        ("配置文件", check_config),
        ("目录结构", check_directories)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name}检查失败: {e}")
            all_passed = False
    
    print("\\n" + "="*50)
    
    if all_passed:
        print("\\n🎉 所有检查通过！系统可以正常使用。")
        print("\\n使用方法:")
        print("  python main.py --tender 招标文件.pdf --product 产品文档.docx")
    else:
        print("\\n⚠️ 发现问题，请根据上述提示进行修复。")
        print("\\n安装依赖包:")
        print("  pip install requests python-docx openpyxl PyPDF2")

if __name__ == "__main__":
    main()