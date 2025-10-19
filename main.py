#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway 启动入口文件
自动切换到 ai_tender_system 目录并导入应用
"""

import sys
from pathlib import Path

# 添加 ai_tender_system 到 Python 路径
project_root = Path(__file__).parent / "ai_tender_system"
sys.path.insert(0, str(project_root))

# 导入 Flask 应用
from web.app import create_app

# 创建应用实例供 gunicorn 使用
app = create_app()

if __name__ == '__main__':
    # 本地开发运行
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
