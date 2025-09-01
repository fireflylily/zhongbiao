#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书点对点应答系统 - 后台服务启动脚本
"""

import os
import sys
import subprocess
import signal
import time

def start_server():
    """启动服务器（后台模式）"""
    try:
        # 启动web应用
        from web_app import app, find_available_port
        
        port = find_available_port()
        if not port:
            print("❌ 无法找到可用端口")
            return False
            
        print("🚀 启动AI标书点对点应答系统...")
        print(f"📱 Web界面: http://localhost:{port}")
        print("📱 局域网访问: http://192.168.x.x:{port}")
        print("\n✨ 功能特点:")
        print("   • 智能识别采购需求条目")
        print("   • AI生成专业技术应答")
        print("   • 自动格式化：黑色字体 + 灰色底纹 + 1.5倍行距")
        print("   • 支持拖拽上传 .docx/.doc 文件")
        print("\n🔄 服务器运行中，按 Ctrl+C 停止服务...")
        
        # 设置信号处理
        def signal_handler(sig, frame):
            print("\n\n👋 正在停止服务器...")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # 启动Flask应用（生产模式）
        app.run(
            debug=False,          # 关闭调试模式
            host='0.0.0.0',       # 允许外部访问
            port=port,
            threaded=True,        # 多线程支持
            use_reloader=False    # 不使用重载器
        )
        
    except KeyboardInterrupt:
        print("👋 服务器已停止")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI标书点对点应答系统 - 服务器启动")
    print("=" * 60)
    
    # 检查依赖
    try:
        import flask
        import docx
        import requests
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install flask python-docx requests")
        return False
    
    # 创建必要目录
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # 启动服务器
    return start_server()

if __name__ == "__main__":
    main()