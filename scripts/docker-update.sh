#!/bin/bash
# AI标书系统 - Docker快速更新脚本（阿里云ECS）
# 用途：日常代码更新，30秒完成

set -e

echo "========================================="
echo "  AI标书系统 快速更新"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

START_TIME=$(date +%s)

# 1. 拉取最新代码
echo -e "${YELLOW}📥 拉取最新代码...${NC}"
git pull origin master

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ git pull失败${NC}"
    exit 1
fi

# 2. 检查是否有requirements.txt变化
REBUILD_FLAG=""
if git diff HEAD@{1} --name-only | grep -q "requirements.txt"; then
    echo -e "${YELLOW}⚠️  检测到依赖变化，将完全重建镜像（约2分钟）${NC}"
    REBUILD_FLAG="--no-cache"
else
    echo -e "${GREEN}✅ 依赖未变化，使用缓存快速构建（约30秒）${NC}"
fi

# 3. 重新构建镜像
echo ""
echo -e "${YELLOW}🔨 重新构建镜像...${NC}"
docker-compose build $REBUILD_FLAG

# 4. 优雅重启服务
echo ""
echo -e "${YELLOW}🔄 重启服务...${NC}"
docker-compose up -d --force-recreate

# 5. 等待服务就绪
echo ""
echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
sleep 3

# 6. 健康检查
echo -e "${YELLOW}🏥 健康检查...${NC}"
for i in {1..10}; do
    if docker-compose exec -T ai-tender-web python -c "import requests; requests.get('http://localhost:8110/api/health', timeout=5)" 2>/dev/null; then
        echo -e "${GREEN}✅ 服务健康${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 健康检查失败，请查看日志${NC}"
        docker-compose logs --tail=50
        exit 1
    fi
    echo "  等待中... ($i/10)"
    sleep 2
done

# 7. 清理旧镜像
echo ""
echo -e "${YELLOW}🧹 清理旧镜像...${NC}"
docker image prune -f 2>/dev/null || true

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ 更新完成！耗时: ${DURATION}秒${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f"
echo ""
