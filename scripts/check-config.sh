#!/bin/bash
# 配置一致性检查脚本
# 用途：确保Nginx、Docker、Flask应用使用相同的端口配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 标准端口号
STANDARD_PORT=8110

echo "========================================="
echo "  配置一致性检查"
echo "========================================="
echo ""

# 检查计数器
ERRORS=0
WARNINGS=0

# 1. 检查代码默认端口
echo "1️⃣  检查代码默认端口配置..."
DEFAULT_PORT=$(grep "os.getenv('WEB_PORT'" ai_tender_system/common/config.py | grep -o "'[0-9]\+'" | tr -d "'")
if [ "$DEFAULT_PORT" == "$STANDARD_PORT" ]; then
    echo -e "${GREEN}✅ 代码默认端口：$DEFAULT_PORT (正确)${NC}"
else
    echo -e "${RED}❌ 代码默认端口：$DEFAULT_PORT (应该是$STANDARD_PORT)${NC}"
    ((ERRORS++))
fi
echo ""

# 2. 检查Docker配置
echo "2️⃣  检查Docker配置..."
if [ -f "docker-compose.yml" ]; then
    DOCKER_PORT=$(grep -A 1 "ports:" docker-compose.yml | grep -o "[0-9]\+:8110" | cut -d: -f1)
    if [ "$DOCKER_PORT" == "$STANDARD_PORT" ]; then
        echo -e "${GREEN}✅ Docker映射端口：$DOCKER_PORT (正确)${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker映射端口：$DOCKER_PORT (建议改为$STANDARD_PORT)${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️  未找到docker-compose.yml${NC}"
    ((WARNINGS++))
fi
echo ""

# 3. 检查Nginx配置
echo "3️⃣  检查Nginx配置..."
if [ -f "nginx/ai-tender-system.conf" ]; then
    NGINX_PORT=$(grep "proxy_pass http://localhost:" nginx/ai-tender-system.conf | grep -o ":[0-9]\+" | tr -d ":")
    if [ "$NGINX_PORT" == "$STANDARD_PORT" ]; then
        echo -e "${GREEN}✅ Nginx代理端口：$NGINX_PORT (正确)${NC}"
    else
        echo -e "${RED}❌ Nginx代理端口：$NGINX_PORT (应该是$STANDARD_PORT)${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠️  未找到nginx/ai-tender-system.conf${NC}"
    ((WARNINGS++))
fi
echo ""

# 4. 检查.env文件
echo "4️⃣  检查.env文件配置..."
if [ -f "ai_tender_system/.env" ]; then
    if grep -q "WEB_PORT=" ai_tender_system/.env; then
        ENV_PORT=$(grep "WEB_PORT=" ai_tender_system/.env | cut -d= -f2 | tr -d ' ')
        if [ "$ENV_PORT" == "$STANDARD_PORT" ]; then
            echo -e "${GREEN}✅ .env端口配置：$ENV_PORT (正确)${NC}"
        else
            echo -e "${RED}❌ .env端口配置：$ENV_PORT (应该是$STANDARD_PORT)${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "${YELLOW}⚠️  .env未配置WEB_PORT，将使用代码默认值${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ 未找到.env文件${NC}"
    ((ERRORS++))
fi
echo ""

# 5. 检查是否有端口冲突的进程
echo "5️⃣  检查端口占用情况..."
if command -v lsof &> /dev/null; then
    PORT_8082=$(lsof -ti:8082 2>/dev/null | wc -l)
    PORT_8110=$(lsof -ti:8110 2>/dev/null | wc -l)

    if [ "$PORT_8082" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  端口8082已被占用 (旧端口，建议停止)${NC}"
        ((WARNINGS++))
    fi

    if [ "$PORT_8110" -gt 0 ]; then
        echo -e "${GREEN}✅ 端口8110已被使用 (正确)${NC}"
    else
        echo -e "${YELLOW}⚠️  端口8110未被使用 (应用可能未运行)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  lsof命令不可用，跳过端口检查${NC}"
fi
echo ""

# 总结
echo "========================================="
echo "  检查结果汇总"
echo "========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有配置检查通过！${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $WARNINGS 个警告${NC}"
    exit 0
else
    echo -e "${RED}❌ 发现 $ERRORS 个错误和 $WARNINGS 个警告${NC}"
    echo ""
    echo "建议修复措施："
    echo "1. 运行: sed -i \"s/'8082'/'8110'/g\" ai_tender_system/common/config.py"
    echo "2. 在.env文件添加: WEB_PORT=8110"
    echo "3. 停止8082端口进程: sudo lsof -ti:8082 | xargs sudo kill"
    echo "4. 重新启动应用"
    exit 1
fi
