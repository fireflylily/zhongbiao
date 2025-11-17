#!/bin/bash
#
# 环境依赖检查脚本
# 用于检查本地和阿里云服务器的依赖差异
#
# 使用方法:
#   本地: bash scripts/check_environment.sh local
#   远程: bash scripts/check_environment.sh remote
#

set -e

ENV_TYPE=${1:-local}  # local 或 remote

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}环境依赖检查 - ${ENV_TYPE}${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Python版本
echo -e "\n${YELLOW}1. 检查Python版本...${NC}"
python_version=$(python3 --version 2>&1)
echo "   $python_version"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo -e "   ${GREEN}✓ Python版本符合要求 (>= 3.11)${NC}"
else
    echo -e "   ${RED}✗ Python版本过低，需要 >= 3.11${NC}"
    exit 1
fi

# 检查虚拟环境
echo -e "\n${YELLOW}2. 检查虚拟环境...${NC}"
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "   ${GREEN}✓ 已激活虚拟环境: $VIRTUAL_ENV${NC}"
else
    echo -e "   ${RED}✗ 未激活虚拟环境${NC}"
    echo -e "   请运行: source venv/bin/activate"
    exit 1
fi

# 确定依赖文件
if [ "$ENV_TYPE" = "remote" ] || [ "$ENV_TYPE" = "production" ]; then
    REQUIREMENTS_FILE="requirements-prod.txt"
    echo -e "\n${BLUE}使用生产环境依赖: ${REQUIREMENTS_FILE}${NC}"
else
    REQUIREMENTS_FILE="requirements.txt"
    echo -e "\n${BLUE}使用开发环境依赖: ${REQUIREMENTS_FILE}${NC}"
fi

# 检查依赖文件是否存在
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}✗ 依赖文件不存在: $REQUIREMENTS_FILE${NC}"
    exit 1
fi

# 检查关键依赖
echo -e "\n${YELLOW}3. 检查关键依赖包...${NC}"

# 必需的核心依赖
CORE_PACKAGES=(
    "Flask"
    "requests"
    "PyMuPDF"
    "python-docx"
    "langchain"
    "faiss-cpu"
    "numpy"
    "openai"
)

missing_packages=()
installed_packages=()

for package in "${CORE_PACKAGES[@]}"; do
    if python3 -c "import importlib; importlib.import_module('${package,,}')" 2>/dev/null; then
        version=$(python3 -c "import importlib.metadata; print(importlib.metadata.version('${package}'))" 2>/dev/null || echo "未知版本")
        echo -e "   ${GREEN}✓${NC} $package ($version)"
        installed_packages+=("$package")
    else
        echo -e "   ${RED}✗${NC} $package (未安装)"
        missing_packages+=("$package")
    fi
done

# 检查环境特定的依赖
echo -e "\n${YELLOW}4. 检查环境特定依赖...${NC}"

if [ "$ENV_TYPE" = "local" ]; then
    # 本地开发环境应该有这些大型依赖
    OPTIONAL_PACKAGES=(
        "torch"
        "transformers"
        "sentence-transformers"
    )

    echo -e "   ${BLUE}本地开发环境 - 检查机器学习库:${NC}"
    for package in "${OPTIONAL_PACKAGES[@]}"; do
        if python3 -c "import ${package,,}" 2>/dev/null; then
            version=$(python3 -c "import importlib.metadata; print(importlib.metadata.version('${package}'))" 2>/dev/null || echo "未知版本")
            echo -e "   ${GREEN}✓${NC} $package ($version)"
        else
            echo -e "   ${YELLOW}⚠${NC} $package (未安装，可选)"
        fi
    done
else
    # 生产环境不应该有这些大型依赖
    echo -e "   ${BLUE}生产环境 - 验证已移除大型依赖:${NC}"
    REMOVED_PACKAGES=(
        "torch"
        "transformers"
        "sentence-transformers"
    )

    for package in "${REMOVED_PACKAGES[@]}"; do
        if python3 -c "import ${package,,}" 2>/dev/null; then
            echo -e "   ${YELLOW}⚠${NC} $package (应该在生产环境移除)"
        else
            echo -e "   ${GREEN}✓${NC} $package (已正确移除)"
        fi
    done
fi

# 检查.env文件
echo -e "\n${YELLOW}5. 检查环境变量配置...${NC}"
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✓ .env 文件存在${NC}"

    # 检查关键配置
    required_vars=("ACCESS_TOKEN" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "^${var}=$" .env; then
            echo -e "   ${GREEN}✓${NC} $var 已配置"
        else
            echo -e "   ${RED}✗${NC} $var 未配置或为空"
        fi
    done
else
    echo -e "   ${RED}✗ .env 文件不存在${NC}"
    echo -e "   请从 .env.example 复制: cp .env.example .env"
fi

# 统计信息
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}检查摘要${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "已安装核心包: ${GREEN}${#installed_packages[@]}${NC}/${#CORE_PACKAGES[@]}"
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo -e "缺失包: ${RED}${#missing_packages[@]}${NC}"
    echo -e "\n${YELLOW}缺失的包列表:${NC}"
    for package in "${missing_packages[@]}"; do
        echo -e "  - $package"
    done

    echo -e "\n${YELLOW}建议修复命令:${NC}"
    echo -e "  pip install -r $REQUIREMENTS_FILE"
    exit 1
else
    echo -e "${GREEN}✓ 所有核心依赖已安装${NC}"
fi

# 环境特定建议
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}环境建议${NC}"
echo -e "${BLUE}========================================${NC}"

if [ "$ENV_TYPE" = "local" ]; then
    echo -e "📌 ${YELLOW}本地开发环境${NC}"
    echo -e "   - 使用 requirements.txt (完整依赖)"
    echo -e "   - 可以离线运行模型"
    echo -e "   - 磁盘占用较大 (~2-3GB)"
    echo -e ""
    echo -e "💡 如需切换到生产依赖:"
    echo -e "   pip install -r requirements-prod.txt"
else
    echo -e "📌 ${YELLOW}生产环境 (阿里云)${NC}"
    echo -e "   - 使用 requirements-prod.txt (轻量级)"
    echo -e "   - 依赖API调用 (需要网络)"
    echo -e "   - 磁盘占用小 (~500MB)"
    echo -e ""
    echo -e "⚠️  注意事项:"
    echo -e "   - 确保 ACCESS_TOKEN 已配置"
    echo -e "   - 确保网络连接正常"
    echo -e "   - 不支持离线运行"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 环境检查完成${NC}"
echo -e "${GREEN}========================================${NC}"
