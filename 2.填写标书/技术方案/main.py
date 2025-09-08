#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
标书生成系统主入口
提供命令行接口调用TenderGenerator
"""

import sys
import os
from pathlib import Path

# 添加TenderGenerator模块路径
sys.path.insert(0, str(Path(__file__).parent / "TenderGenerator"))

# 导入主程序
from TenderGenerator.main import main

if __name__ == "__main__":
    main()