#!/bin/bash
# 快速回归测试脚本
# 用途：在修改代码后快速验证核心功能没有被破坏
# 使用：./check.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🔍 商务应答核心功能回归测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试结果数组
declare -a FAILED_TEST_NAMES

# 运行单个测试的函数
run_test() {
    local test_name=$1
    local test_path=$2

    echo -e "${YELLOW}▶ 运行: $test_name${NC}"

    if pytest "$test_path" -v --tb=short -q > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED_TESTS++))
        FAILED_TEST_NAMES+=("$test_name")
    fi
    ((TOTAL_TESTS++))
    echo ""
}

# ============================================
# 1. 核心字段识别测试
# ============================================
echo "📌 第1组：字段识别测试"
echo "----------------------------------------"

run_test "公司名称别名识别（7个）" \
    "tests/unit/modules/test_business_response_text_filling.py::test_company_name_aliases"

run_test "地址字段识别（7个）" \
    "tests/unit/modules/test_business_response_text_filling.py::test_address_field_recognition"

run_test "法人代表字段识别（10个）" \
    "tests/unit/modules/test_business_response_text_filling.py::test_legal_representative_recognition"

# ============================================
# 2. 核心业务逻辑测试（你关心的）
# ============================================
echo "📌 第2组：核心业务逻辑测试"
echo "----------------------------------------"

run_test "签字/盖章字段判断逻辑 ⭐" \
    "tests/unit/modules/test_business_response_text_filling.py::test_signature_field_skip_logic"

run_test "日期格式化（5种格式）⭐" \
    "tests/unit/modules/test_business_response_text_filling.py::test_date_formatting"

# ============================================
# 3. 字段填充测试
# ============================================
echo "📌 第3组：字段填充测试"
echo "----------------------------------------"

run_test "括号字段填充（5个）" \
    "tests/unit/modules/test_business_response_text_filling.py::test_bracket_field_filling"

run_test "组合字段识别（3个）" \
    "tests/unit/modules/test_business_response_text_filling.py::test_combo_field_recognition"

# ============================================
# 4. 边界情况测试
# ============================================
echo "📌 第4组：边界情况测试"
echo "----------------------------------------"

run_test "空值处理" \
    "tests/unit/modules/test_business_response_text_filling.py::test_skip_empty_values"

run_test "完整填充场景" \
    "tests/unit/modules/test_business_response_text_filling.py::test_complete_text_filling_scenario"

# ============================================
# 汇总报告
# ============================================
echo ""
echo "=========================================="
echo "📊 测试结果汇总"
echo "=========================================="
echo -e "总计: $TOTAL_TESTS 个测试"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有核心测试通过！${NC}"
    echo "✓ 字段识别功能正常"
    echo "✓ 盖章/签字逻辑正确"
    echo "✓ 日期格式化工作正常"
    echo "✓ 字段填充功能完整"
    echo ""
    echo "👍 可以安全地提交代码"
    exit 0
else
    echo -e "${RED}❌ 检测到 $FAILED_TESTS 个测试失败！${NC}"
    echo ""
    echo "失败的测试："
    for test in "${FAILED_TEST_NAMES[@]}"; do
        echo -e "${RED}  ✗ $test${NC}"
    done
    echo ""
    echo "⚠️  建议："
    echo "1. 查看详细错误信息："
    echo "   pytest tests/unit/modules/test_business_response_text_filling.py -v"
    echo ""
    echo "2. 运行失败的特定测试："
    for test in "${FAILED_TEST_NAMES[@]}"; do
        echo "   # $test"
    done
    echo ""
    echo "3. 修复问题后再次运行此脚本"
    echo ""
    echo "⛔ 请修复失败的测试后再提交代码"
    exit 1
fi
