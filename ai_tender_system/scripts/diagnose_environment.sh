#!/bin/bash
# 环境诊断脚本 - 用于对比本地和阿里云环境差异

echo "=========================================="
echo "AI标书系统 - 环境诊断报告"
echo "=========================================="
echo ""

echo "1. 基本信息"
echo "  主机名: $(hostname)"
echo "  系统: $(uname -a)"
echo "  Python版本: $(python3 --version)"
echo ""

echo "2. 当前工作目录"
echo "  PWD: $PWD"
echo "  实际路径: $(pwd -P)"
echo ""

echo "3. 项目路径"
if [ -f "run.py" ]; then
    echo "  ✅ 当前目录是项目根目录"
    PROJECT_ROOT="$PWD"
else
    echo "  ❌ 当前目录不是项目根目录"
    # 尝试查找项目根目录
    if [ -f "../run.py" ]; then
        PROJECT_ROOT="$(cd .. && pwd)"
        echo "  项目根目录: $PROJECT_ROOT"
    else
        echo "  无法找到项目根目录"
    fi
fi
echo ""

echo "4. Python进程信息"
ps aux | grep "python.*run.py\|gunicorn.*8110" | grep -v grep || echo "  未找到运行中的Python进程"
echo ""

echo "5. Supervisor配置"
if command -v supervisorctl &> /dev/null; then
    echo "  Supervisor已安装"
    sudo supervisorctl status 2>/dev/null | grep "ai-tender\|tender" || echo "  未找到相关服务"

    # 查找配置文件
    echo ""
    echo "  配置文件位置:"
    sudo find /etc -name "*ai-tender*" -o -name "*tender*.conf" 2>/dev/null | head -5
else
    echo "  Supervisor未安装（可能使用其他方式运行）"
fi
echo ""

echo "6. 文件路径测试"
echo "  测试相对路径解析:"
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$PROJECT_ROOT')
from common.utils import get_project_root, resolve_file_path

print(f'    get_project_root(): {get_project_root()}')
print(f'    resolve_file_path(\"ai_tender_system/data/test.txt\"): {resolve_file_path(\"ai_tender_system/data/test.txt\")}')
print(f'    resolve_file_path(\"data/test.txt\"): {resolve_file_path(\"data/test.txt\")}')
"
echo ""

echo "7. 目录结构"
echo "  项目目录层级:"
if [ -d "$PROJECT_ROOT" ]; then
    ls -la "$PROJECT_ROOT" | grep "ai_tender\|data\|frontend" || echo "  无相关目录"
fi
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
