# -*- coding: utf-8 -*-
"""
AI标书系统主入口
"""

import os
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 现在可以安全地导入模块
from common.config import get_config
from common.logger import setup_logging, get_logger
from modules.tender_info.extractor import TenderInfoExtractor


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("AI标书系统 v2.0")
        print("使用方法:")
        print("  python main.py extract <文档路径>  # 提取招标信息")
        print("  python main.py web              # 启动Web服务")
        print("  python main.py test             # 运行测试")
        return
    
    command = sys.argv[1].lower()
    
    if command == "extract":
        if len(sys.argv) != 3:
            print("使用方法: python main.py extract <文档路径>")
            return
        
        # 初始化
        setup_logging()
        
        file_path = sys.argv[2]
        
        try:
            # 提取招标信息
            extractor = TenderInfoExtractor()
            tender_info = extractor.extract_from_file(file_path)
            
            # 保存配置
            config_file = extractor.save_to_config(tender_info)
            
            # 显示结果
            extractor.print_results(tender_info)
            print(f"\n配置文件已保存: {config_file}")
            
        except Exception as e:
            print(f"提取失败: {e}")
            sys.exit(1)
    
    elif command == "web":
        # 启动Web服务
        setup_logging()
        
        from web.app import create_app
        
        app = create_app()
        config = get_config()
        
        host = config.get('web.host', '0.0.0.0')
        port = config.get('web.port', 5000)
        debug = config.get('web.debug', False)
        
        print(f"启动Web服务: http://{host}:{port}")
        app.run(host=host, port=port, debug=debug)
    
    elif command == "test":
        # 运行测试
        from tests.test_runner import run_tests
        success = run_tests()
        sys.exit(0 if success else 1)
    
    else:
        print(f"未知命令: {command}")
        print("可用命令: extract, web, test")


if __name__ == "__main__":
    main()