#!/bin/bash
# AI标书系统 - Docker一键部署脚本（阿里云ECS）
# 用途：首次部署或完全重建

set -e  # 遇到错误立即退出

echo "========================================="
echo "  AI标书系统 Docker部署"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
    echo "安装方法: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose未安装，请先安装docker-compose${NC}"
    echo "安装方法: sudo apt install docker-compose"
    exit 1
fi

echo -e "${GREEN}✅ Docker环境检查通过${NC}"
echo ""

# 检查环境变量文件
if [ ! -f "ai_tender_system/.env" ]; then
    echo -e "${YELLOW}⚠️  警告: 未找到ai_tender_system/.env文件${NC}"
    echo "请确保已配置环境变量，包括："
    echo "  - AZURE_FORM_RECOGNIZER_KEY"
    echo "  - AZURE_FORM_RECOGNIZER_ENDPOINT"
    echo "  - 其他API密钥"
    echo ""
    read -p "是否继续部署? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 停止并删除旧容器
echo -e "${YELLOW}🛑 停止旧容器...${NC}"
docker-compose down 2>/dev/null || true

# 构建镜像
echo ""
echo -e "${YELLOW}🔨 构建Docker镜像（首次构建约5-10分钟）...${NC}"
docker-compose build --no-cache

# 启动服务
echo ""
echo -e "${YELLOW}🚀 启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo ""
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✅ 部署成功！${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "服务访问地址:"
    echo "  - http://localhost:8110"
    echo "  - http://$(hostname -I | awk '{print $1}'):8110"
    echo ""
    echo "查看日志:"
    echo "  docker-compose logs -f"
    echo ""
    echo "停止服务:"
    echo "  docker-compose down"
    echo ""
    echo "重启服务:"
    echo "  docker-compose restart"
    echo ""
else
    echo -e "${RED}❌ 部署失败，请检查日志${NC}"
    echo "查看日志: docker-compose logs"
    exit 1
fi
