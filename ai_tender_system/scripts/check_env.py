#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查生产环境 Python 版本和依赖
"""

import sys

print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"Python 版本信息: {sys.version_info}")

# 检查关键模块
modules_to_check = [
    'dataclasses',
    'sqlite3',
    'pathlib',
    'typing',
]

print("\n模块检查:")
for module in modules_to_check:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module} - {e}")

# 检查是否有 python3.7+
print("\n可用的 Python 版本:")
import subprocess
for cmd in ['python3.7', 'python3.8', 'python3.9', 'python3.10', 'python3.11', 'python3']:
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {cmd}: {result.stdout.strip()}")
    except FileNotFoundError:
        pass
