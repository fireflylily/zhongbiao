#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书点对点应答系统 - 启动脚本
"""

import subprocess
import sys
import os

def check_and_install_dependencies():
    """检查并安装依赖包"""
    required_packages = [
        'flask',
        'python-docx',
        'requests'
    ]
    
    print("🔧 检查依赖包...")
    
    for package in required_packages:
        try:
            # 特殊处理python-docx包名
            import_name = 'docx' if package == 'python-docx' else package.replace('-', '_')
            __import__(import_name)
            print(f"✅ {package} - 已安装")
        except ImportError:
            print(f"❌ {package} - 未安装，正在安装...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} - 安装完成")
            except subprocess.CalledProcessError:
                print(f"❌ {package} - 安装失败")
                return False
    
    return True

def create_directories():
    """创建必要的目录"""
    directories = ['uploads', 'outputs', 'templates', 'config']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 创建目录: {directory}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI标书点对点应答系统 - Web版")
    print("=" * 60)
    
    # 检查依赖
    if not check_and_install_dependencies():
        print("❌ 依赖安装失败，请手动安装：")
        print("pip install flask python-docx requests")
        return False
    
    # 创建目录
    create_directories()
    
    print("\n" + "=" * 60)
    print("🎉 系统准备就绪！")
    print("📋 功能说明:")
    print("   • 智能识别采购需求条目")
    print("   • AI生成专业技术应答") 
    print("   • 自动格式化：黑色字体 + 灰色底纹 + 1.5倍行距")
    print("   • 支持拖拽上传 .docx/.doc 文件")
    print("=" * 60)
    print("\n正在启动Web服务器...")
    
    # 启动Flask应用
    try:
        from web_app import app, find_available_port
        port = find_available_port()
        if port:
            print(f"📱 Web界面: http://localhost:{port}")
            app.run(debug=True, host='0.0.0.0', port=port)
        else:
            print("❌ 无法找到可用端口")
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()