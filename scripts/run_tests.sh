#!/bin/bash

# AI投标系统 - 本地测试脚本
# 用途: 在提交代码前本地运行测试,确保代码质量

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否在项目根目录
if [ ! -f "pytest.ini" ]; then
    print_error "请在项目根目录运行此脚本!"
    exit 1
fi

print_header "🧪 AI投标系统自动化测试"

# 1. 检查依赖
print_header "1. 检查测试依赖"
if ! python3 -c "import pytest" 2>/dev/null; then
    print_warning "pytest未安装,正在安装测试依赖..."
    pip install -r requirements-dev.txt
else
    print_success "测试依赖已安装"
fi

# 2. 运行单元测试
print_header "2. 运行单元测试"
if pytest tests/unit/ -v --tb=short -m "not slow" --maxfail=5; then
    print_success "单元测试通过"
    UNIT_TEST_PASSED=true
else
    print_warning "单元测试有失败用例"
    UNIT_TEST_PASSED=false
fi

# 3. 运行关键集成测试
print_header "3. 运行关键集成测试"
if pytest tests/test_common_database.py::TestKnowledgeBaseDB -v --tb=short; then
    print_success "关键测试通过"
    INTEGRATION_TEST_PASSED=true
else
    print_error "关键测试失败!"
    INTEGRATION_TEST_PASSED=false
fi

# 4. 代码覆盖率检查
print_header "4. 生成测试覆盖率报告"
pytest tests/ -v --cov=ai_tender_system --cov-report=html --cov-report=term-missing -m "not slow" || true
print_success "覆盖率报告已生成: htmlcov/index.html"

# 5. 代码质量检查 (可选)
print_header "5. 代码质量检查 (可选)"
if command -v black &> /dev/null; then
    if black --check ai_tender_system/ tests/ 2>/dev/null; then
        print_success "代码格式符合Black标准"
    else
        print_warning "代码格式不符合Black标准,可运行: black ai_tender_system/ tests/"
    fi
else
    print_warning "Black未安装,跳过格式检查"
fi

if command -v flake8 &> /dev/null; then
    if flake8 ai_tender_system/ --max-line-length=120 --extend-ignore=E203,E501,W503 --count 2>/dev/null; then
        print_success "代码风格检查通过"
    else
        print_warning "代码风格存在问题"
    fi
else
    print_warning "Flake8未安装,跳过风格检查"
fi

# 6. 生成测试总结
print_header "📊 测试总结"
echo ""

if [ "$INTEGRATION_TEST_PASSED" = true ]; then
    print_success "关键测试: ✅ 通过"
    CAN_DEPLOY=true
else
    print_error "关键测试: ❌ 失败"
    CAN_DEPLOY=false
fi

if [ "$UNIT_TEST_PASSED" = true ]; then
    print_success "单元测试: ✅ 通过"
else
    print_warning "单元测试: ⚠️  部分失败"
fi

echo ""
print_header "🎯 测试完成"

if [ "$CAN_DEPLOY" = true ]; then
    print_success "代码可以安全部署!"
    echo ""
    echo -e "${BLUE}💡 提示:${NC}"
    echo "  1. 查看覆盖率报告: open htmlcov/index.html"
    echo "  2. 提交代码: git add . && git commit -m 'your message'"
    echo "  3. 推送代码: git push origin master"
    echo "  4. GitHub Actions 会自动运行测试并部署到阿里云"
    exit 0
else
    print_error "关键测试未通过,请修复后再部署!"
    echo ""
    echo -e "${YELLOW}建议:${NC}"
    echo "  1. 查看失败的测试用例"
    echo "  2. 修复相关代码"
    echo "  3. 重新运行测试: ./scripts/run_tests.sh"
    exit 1
fi
