#!/bin/bash

# 获取脚本所在目录
cd "$(dirname "$0")"

echo "======================================"
echo "   AI投标系统 - 开发环境启动脚本"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 清理函数 - 退出时杀掉所有子进程
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止所有服务...${NC}"
    kill 0
    exit
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3${NC}"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 Node.js${NC}"
    exit 1
fi

# 检查并安装前端依赖
echo -e "${GREEN}[1/2] 检查前端依赖...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖..."
    npm install
fi
cd ..

# 启动后端服务
echo -e "${GREEN}[2/2] 启动服务...${NC}"
echo ""
echo -e "${GREEN}启动后端服务 (端口 8110)...${NC}"
WEB_PORT=8110 python3 -m ai_tender_system.web.app > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端服务
echo -e "${GREEN}启动前端开发服务器 (端口 5173)...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "前端 PID: $FRONTEND_PID"

echo ""
echo "======================================"
echo -e "${GREEN}✓ 所有服务已启动！${NC}"
echo "======================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8110"
echo ""
echo "日志文件:"
echo "  后端: logs/backend.log"
echo "  前端: logs/frontend.log"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 实时显示日志
tail -f logs/backend.log logs/frontend.log &

# 等待所有后台进程
wait
