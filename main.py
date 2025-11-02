#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境启动入口文件
适配多种部署环境（本地、Railway、阿里云等）
"""

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent

# 检测是否在 ai_tender_system 子目录中
# Railway部署: /app/ai_tender_system/
# 阿里云部署: /var/www/ai-tender-system/
if (project_root / "ai_tender_system").exists():
    # 如果存在 ai_tender_system 子目录,说明在项目根目录
    # 需要添加 ai_tender_system 到路径
    sys.path.insert(0, str(project_root / "ai_tender_system"))
else:
    # 否则当前目录就是 ai_tender_system,直接添加父目录
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
