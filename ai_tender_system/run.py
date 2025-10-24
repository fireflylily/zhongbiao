#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统启动脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入Web应用
from web.app import main
from common.logger import get_module_logger

logger = get_module_logger("run")

if __name__ == '__main__':
    logger.info("正在启动AI标书系统...")
    main()