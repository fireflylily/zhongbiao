# 测试用例注册表

> **目的**：防止"修改A功能，B功能又出错"的回归问题
>
> **使用方法**：修改任何代码前，先查看此表，运行相关测试确保不破坏现有功能

---

## 📊 测试概览

| 指标 | 数值 | 状态 |
|-----|------|------|
| 总测试数 | 47+ | ✅ |
| 核心测试数 | 15 | 🔒 |
| 覆盖率 | 19.91% | 🟡 |
| 最后更新 | 2025-12-02 | - |

---

## 🔒 核心回归测试（不能失败）

这些测试保护最重要的功能，**任何修改都必须保证这些测试通过**。

### 1. 商务应答字段识别

| 测试用例 | 文件位置 | 保护的功能 | 测试数 |
|---------|---------|-----------|--------|
| `test_company_name_aliases` | `tests/unit/modules/test_business_response_text_filling.py:59-83` | 公司名称7种别名识别 | 7个参数化 |
| `test_address_field_recognition` | `tests/unit/modules/test_business_response_text_filling.py:91-109` | 地址字段7种别名识别 | 7个参数化 |
| `test_legal_representative_recognition` | `tests/unit/modules/test_business_response_text_filling.py:117-137` | 法人代表/被授权人10种别名 | 10个参数化 |

**快速运行**：
```bash
pytest tests/unit/modules/test_business_response_text_filling.py::test_company_name_aliases -v
pytest tests/unit/modules/test_business_response_text_filling.py::test_address_field_recognition -v
pytest tests/unit/modules/test_business_response_text_filling.py::test_legal_representative_recognition -v
```

### 2. 盖章/签字字段处理（你关心的用例）

| 测试用例 | 文件位置 | 保护的功能 | 重要性 |
|---------|---------|-----------|--------|
| `test_signature_field_skip_logic` | `tests/unit/modules/test_business_response_text_filling.py:270-304` | 区分签字/盖章字段 | 🔴 极高 |

**测试场景**：
- ✅ "供应商名称（盖章）" → 应该填充
- ✅ "单位名称（盖章）" → 应该填充
- ❌ "法定代表人（签字）" → 不应该填充
- ✅ "投标人（签字或盖章）" → 应该填充（投标人是单位）

**快速运行**：
```bash
pytest tests/unit/modules/test_business_response_text_filling.py::test_signature_field_skip_logic -v
```

### 3. 日期格式化（你关心的用例）

| 测试用例 | 文件位置 | 保护的功能 | 重要性 |
|---------|---------|-----------|--------|
| `test_date_formatting` | `tests/unit/modules/test_business_response_text_filling.py:241-264` | 5种日期格式转换为"XX年XX月XX日" | 🔴 极高 |

**测试场景**：
- "2025-11-28" → "2025年11月28日"
- "2025/11/28" → "2025年11月28日"
- "2025.11.28" → "2025年11月28日"
- "2025年11月28日" → "2025年11月28日"
- "2025年11月28日下午14:30" → "2025年11月28日"

**快速运行**：
```bash
pytest tests/unit/modules/test_business_response_text_filling.py::test_date_formatting -v
```

### 4. 括号字段填充

| 测试用例 | 文件位置 | 保护的功能 | 测试数 |
|---------|---------|-----------|--------|
| `test_bracket_field_filling` | `tests/unit/modules/test_business_response_text_filling.py:144-184` | 括号字段识别和填充 | 5个参数化 |

**测试场景**：
- "(供应商名称)" → 识别并填充公司名称
- "（公司名称）" → 中文括号也能识别
- "[单位名称]" → 方括号也能识别

**快速运行**：
```bash
pytest tests/unit/modules/test_business_response_text_filling.py::test_bracket_field_filling -v
```

### 5. 组合字段识别

| 测试用例 | 文件位置 | 保护的功能 | 测试数 |
|---------|---------|-----------|--------|
| `test_combo_field_recognition` | `tests/unit/modules/test_business_response_text_filling.py:192-237` | 组合字段拆分和填充 | 3个参数化 |

**测试场景**：
- "(公司名称、地址)" → 拆分为2个字段
- "（单位名称、法定代表人）" → 识别并分别填充
- "[供应商、联系电话]" → 方括号组合字段

**快速运行**：
```bash
pytest tests/unit/modules/test_business_response_text_filling.py::test_combo_field_recognition -v
```

---

## 🧪 集成测试

| 测试文件 | 保护的功能 | 重要性 |
|---------|-----------|--------|
| `test_text_filling_integration.py` | 完整的文字填充流程 | 🔴 高 |
| `test_processor_integration.py` | 商务应答处理器集成 | 🔴 高 |

**快速运行**：
```bash
pytest tests/integration/business_response/ -v
```

---

## 📝 代码修改检查清单

### 当你修改 `field_recognizer.py` 时

**影响范围**：字段识别、别名映射

**必须运行的测试**：
```bash
# 1. 公司名称别名测试（7个）
pytest tests/unit/modules/test_business_response_text_filling.py::test_company_name_aliases -v

# 2. 地址字段测试（7个）
pytest tests/unit/modules/test_business_response_text_filling.py::test_address_field_recognition -v

# 3. 法人代表测试（10个）
pytest tests/unit/modules/test_business_response_text_filling.py::test_legal_representative_recognition -v

# 4. 签字/盖章逻辑
pytest tests/unit/modules/test_business_response_text_filling.py::test_signature_field_skip_logic -v

# 5. 运行所有字段识别测试
pytest tests/unit/modules/test_business_response_text_filling.py -v
```

**检查覆盖率**：
```bash
pytest tests/unit/modules/test_business_response_text_filling.py --cov=ai_tender_system.modules.business_response.field_recognizer --cov-report=term-missing
```
- 当前覆盖率：86%
- 不应低于：86%

---

### 当你修改 `content_filler.py` 时

**影响范围**：内容填充、日期格式化

**必须运行的测试**：
```bash
# 1. 日期格式化（5种格式）
pytest tests/unit/modules/test_business_response_text_filling.py::test_date_formatting -v

# 2. 括号字段填充
pytest tests/unit/modules/test_business_response_text_filling.py::test_bracket_field_filling -v

# 3. 组合字段填充
pytest tests/unit/modules/test_business_response_text_filling.py::test_combo_field_recognition -v

# 4. 空值处理
pytest tests/unit/modules/test_business_response_text_filling.py::test_skip_empty_values -v

# 5. 集成测试
pytest tests/integration/business_response/test_text_filling_integration.py -v
```

**检查覆盖率**：
- 当前覆盖率：10.53%
- 不应低于：10%

---

### 当你修改 `processor.py` 时

**影响范围**：整个商务应答流程

**必须运行的测试**：
```bash
# 1. 运行所有单元测试
pytest tests/unit/modules/test_business_response_text_filling.py -v

# 2. 运行所有集成测试
pytest tests/integration/business_response/ -v

# 3. 运行文档扫描测试
pytest tests/unit/modules/test_document_scanner.py -v

# 4. 运行图片处理测试
pytest tests/unit/modules/test_image_handler.py -v
```

**检查覆盖率**：
- 当前覆盖率：25.40%
- 不应低于：25%

---

### 当你修改 `image_handler.py` 时

**影响范围**：图片插入（营业执照、身份证、资质证书）

**必须运行的测试**：
```bash
# 1. 图片处理单元测试
pytest tests/unit/modules/test_image_handler.py -v

# 2. 图片配置构建测试
pytest tests/unit/modules/test_image_config_builder.py -v

# 3. 身份证插入测试
pytest tests/unit/modules/test_id_card_inserter.py -v

# 4. 处理器集成测试
pytest tests/integration/business_response/test_processor_integration.py -v
```

**检查覆盖率**：
- 当前覆盖率：10.92%
- 不应低于：10%

---

### 当你修改 `document_scanner.py` 时

**影响范围**：文档字段扫描

**必须运行的测试**：
```bash
# 1. 文档扫描测试
pytest tests/unit/modules/test_document_scanner.py -v

# 2. 内容填充测试（依赖扫描结果）
pytest tests/unit/modules/test_content_filler_extended.py -v

# 3. 集成测试
pytest tests/integration/business_response/test_text_filling_integration.py -v
```

---

## 🚀 快速测试命令

### 运行所有核心测试（1-2分钟）
```bash
pytest tests/unit/modules/test_business_response_text_filling.py -v
```

### 运行所有商务应答测试（3-5分钟）
```bash
pytest tests/unit/modules/ tests/integration/business_response/ -v
```

### 运行特定功能测试
```bash
# 只测试盖章/签字逻辑
pytest tests/unit/modules/test_business_response_text_filling.py::test_signature_field_skip_logic -v

# 只测试日期格式化
pytest tests/unit/modules/test_business_response_text_filling.py::test_date_formatting -v

# 只测试公司名称别名
pytest tests/unit/modules/test_business_response_text_filling.py::test_company_name_aliases -v
```

### 使用标记运行测试
```bash
# 只运行商务应答相关测试
pytest -m business_response -v

# 只运行单元测试（快速）
pytest -m unit -v

# 只运行集成测试
pytest -m integration -v
```

---

## 📈 覆盖率监控

### 查看覆盖率报告
```bash
# 生成覆盖率报告
pytest tests/unit/modules/test_business_response_text_filling.py --cov=ai_tender_system.modules.business_response --cov-report=html --cov-report=term-missing

# 查看HTML报告
open htmlcov/index.html
```

### 关键模块覆盖率基线

| 模块 | 当前覆盖率 | 不应低于 | 目标 |
|-----|----------|---------|------|
| `field_recognizer.py` | 86.00% | 86% | 90% |
| `field_classifier.py` | 62.16% | 62% | 70% |
| `constants.py` | 100.00% | 100% | 100% |
| `processor.py` | 25.40% | 25% | 60% |
| `content_filler.py` | 10.53% | 10% | 50% |
| `image_handler.py` | 10.92% | 10% | 50% |
| `document_scanner.py` | 3.63% | 3% | 50% |

---

## 🎯 添加新测试用例

### 模板1：参数化测试
```python
@pytest.mark.unit
@pytest.mark.parametrize("input_value,expected_output", [
    ("输入1", "期望输出1"),
    ("输入2", "期望输出2"),
])
def test_new_feature(input_value, expected_output):
    """测试新功能"""
    # 1. 准备数据
    # 2. 执行操作
    result = some_function(input_value)
    # 3. 验证结果
    assert result == expected_output
```

### 模板2：集成测试
```python
@pytest.mark.integration
@pytest.mark.business_response
def test_complete_flow():
    """测试完整流程"""
    # 1. 准备测试数据
    # 2. 执行完整流程
    # 3. 验证最终结果
    # 4. 清理资源
    pass
```

### 添加测试后需要做的事
1. ✅ 在本文档中更新测试用例表格
2. ✅ 更新总测试数统计
3. ✅ 运行测试确保通过
4. ✅ 更新覆盖率数据
5. ✅ 提交到Git
6. ✅ 更新 `check.sh` 如果是核心测试

---

## 🔄 测试维护流程

### 每周检查（推荐）
```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 生成覆盖率报告
pytest tests/ --cov=ai_tender_system --cov-report=html

# 3. 查看报告
open htmlcov/index.html

# 4. 更新本文档的覆盖率数据
```

### 每月检查（必须）
1. 检查所有核心测试是否仍然有效
2. 更新测试用例注册表
3. 检查覆盖率是否下降
4. 补充缺失的测试用例

---

## 🐛 测试失败处理流程

### 步骤1：定位问题
```bash
# 运行失败的测试，查看详细错误
pytest tests/unit/modules/test_business_response_text_filling.py::test_xxx -vv --tb=long
```

### 步骤2：检查是否是代码变更导致
```bash
# 查看最近的修改
git log --oneline -10

# 查看具体修改内容
git diff HEAD~1 ai_tender_system/modules/business_response/
```

### 步骤3：修复或更新测试
- 如果是代码bug：修复代码
- 如果是测试过时：更新测试用例
- 如果是需求变更：更新测试和文档

### 步骤4：验证修复
```bash
# 重新运行测试
pytest tests/unit/modules/test_business_response_text_filling.py -v

# 运行相关测试
pytest tests/unit/modules/ -v

# 运行所有测试
pytest tests/ -v
```

---

## 📞 需要帮助？

### 测试相关文档
- 测试路线图：`docs/TESTING_ROADMAP.md`
- 测试监控指南：`docs/TESTING_DASHBOARD_GUIDE.md`
- 测试总结：`docs/TESTING_FINAL_SUMMARY.md`

### 快速链接
- 测试监控页面：http://localhost:8110/abtest/testing-dashboard
- 覆盖率报告：`htmlcov/index.html`
- GitHub Actions：https://github.com/your-repo/actions

### 常见命令
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/unit/modules/test_business_response_text_filling.py -v

# 生成覆盖率报告
pytest tests/ --cov=ai_tender_system --cov-report=html

# 查看测试列表
pytest tests/ --co -q

# 运行失败的测试
pytest --lf -v

# 调试模式
pytest tests/unit/modules/test_xxx.py -vv --pdb
```

---

**维护责任人**：开发团队
**最后更新**：2025-12-02
**版本**：v1.0
