# 如何使用测试防护系统

> **目标**：防止"修改A功能，B功能又出错"的回归问题

---

## 🎯 快速开始（5分钟设置）

### 1. 赋予脚本执行权限

```bash
chmod +x check.sh
chmod +x scripts/smart_test.py
chmod +x .git/hooks/pre-commit
```

### 2. 测试一下是否工作

```bash
# 运行快速回归测试
./check.sh
```

如果看到 `✅ 所有核心测试通过！`，说明设置成功！

---

## 📚 日常使用流程

### 场景1：修改代码前

```bash
# 第1步：运行当前测试，确认当前状态
./check.sh

# 第2步：查看测试注册表，了解影响范围
cat tests/TEST_REGISTRY.md

# 第3步：开始修改代码
vim ai_tender_system/modules/business_response/field_recognizer.py
```

### 场景2：修改代码后

```bash
# 第1步：运行快速回归测试
./check.sh

# 如果失败，查看详细错误
pytest tests/unit/modules/test_business_response_text_filling.py -v

# 第2步：智能测试（自动检测修改的文件）
python scripts/smart_test.py

# 第3步：提交代码（会自动触发pre-commit hook）
git add .
git commit -m "fix: 修复字段识别问题"
# ↑ 这里会自动运行核心测试
```

### 场景3：大规模重构

```bash
# 第1步：运行所有商务应答测试
python scripts/smart_test.py --suite business_response

# 第2步：检查覆盖率
pytest tests/unit/modules/test_business_response_text_filling.py \
  --cov=ai_tender_system.modules.business_response \
  --cov-report=html

# 第3步：查看报告
open htmlcov/index.html
```

---

## 🛠️ 工具详解

### 1. check.sh - 快速回归测试脚本

**用途**：快速验证核心功能（1-2分钟）

**使用**：
```bash
./check.sh
```

**测试内容**：
- ✓ 字段识别（24个测试）
- ✓ 签字/盖章逻辑（5个测试）
- ✓ 日期格式化（5个测试）
- ✓ 字段填充（8个测试）
- ✓ 边界情况（2个测试）

**特点**：
- 彩色输出，易读
- 失败时给出详细建议
- 返回值：0=成功，1=失败

---

### 2. smart_test.py - 智能测试运行器

**用途**：根据修改的文件自动选择测试

**基本用法**：
```bash
# 自动检测修改并运行相关测试
python scripts/smart_test.py

# 列出会运行哪些测试（不实际运行）
python scripts/smart_test.py --list

# 查看某个文件的相关测试
python scripts/smart_test.py --file ai_tender_system/modules/business_response/field_recognizer.py
```

**运行测试套件**：
```bash
# 快速测试（1-2分钟）
python scripts/smart_test.py --suite quick

# 商务应答完整测试（3-5分钟）
python scripts/smart_test.py --suite business_response

# 所有测试（10-15分钟）
python scripts/smart_test.py --suite full
```

**只运行核心测试**：
```bash
python scripts/smart_test.py --core
```

**安静模式**：
```bash
python scripts/smart_test.py -q
```

---

### 3. pre-commit hook - 提交前自动检查

**工作原理**：
- 在 `git commit` 时自动触发
- 检测修改的文件
- 如果修改了关键模块，运行核心测试
- 测试失败时阻止提交

**触发条件**：
- 修改了 `field_recognizer.py`
- 修改了 `content_filler.py`
- 修改了 `processor.py`
- 修改了 `image_handler.py`
- 修改了 `document_scanner.py`

**跳过检查**（不推荐）：
```bash
git commit --no-verify
```

---

### 4. GitHub Actions - CI/CD 严格模式

**触发时机**：
- 创建 PR 到 `master` 或 `main` 分支
- 修改了 `ai_tender_system/modules/business_response/**` 目录

**检查内容**：
- 运行核心回归测试
- 运行所有商务应答测试
- 检查覆盖率不下降

**测试失败时**：
- PR 会被标记为失败
- 自动评论到 PR
- 阻止合并

**查看结果**：
- GitHub PR 页面的 "Checks" 标签
- Actions 运行日志

---

## 📖 TEST_REGISTRY.md - 测试注册表

**用途**：文档化所有测试用例和修改检查清单

**查看方法**：
```bash
cat tests/TEST_REGISTRY.md
# 或
less tests/TEST_REGISTRY.md
```

**包含内容**：
1. 核心回归测试清单
2. 代码修改检查清单
3. 快速测试命令
4. 覆盖率基线
5. 测试维护流程

---

## 🎓 实际案例演示

### 案例1：修改字段识别逻辑

```bash
# 场景：需要添加一个新的字段别名
# 文件：field_recognizer.py

# 第1步：查看当前测试
cat tests/TEST_REGISTRY.md | grep "field_recognizer"

# 第2步：运行当前测试（应该通过）
./check.sh

# 第3步：修改代码，添加新别名
vim ai_tender_system/modules/business_response/field_recognizer.py

# 第4步：添加测试用例
vim tests/unit/modules/test_business_response_text_filling.py

# 第5步：运行测试
pytest tests/unit/modules/test_business_response_text_filling.py::test_company_name_aliases -v

# 第6步：运行所有相关测试
python scripts/smart_test.py

# 第7步：提交
git add .
git commit -m "feat: 添加新的字段别名支持"
# ← pre-commit hook 会自动运行测试
```

### 案例2：修复日期格式化Bug

```bash
# 场景：日期格式化有bug
# 文件：content_filler.py

# 第1步：运行失败的测试，重现问题
pytest tests/unit/modules/test_business_response_text_filling.py::test_date_formatting -v

# 第2步：修复代码
vim ai_tender_system/modules/business_response/content_filler.py

# 第3步：验证修复
pytest tests/unit/modules/test_business_response_text_filling.py::test_date_formatting -v

# 第4步：运行回归测试，确保没破坏其他功能
./check.sh

# 第5步：提交
git add .
git commit -m "fix: 修复日期格式化bug"
```

### 案例3：大型重构

```bash
# 场景：重构 processor.py

# 第1步：记录当前测试状态
./check.sh > before_refactor.txt

# 第2步：重构代码
vim ai_tender_system/modules/business_response/processor.py

# 第3步：运行所有相关测试
python scripts/smart_test.py --suite business_response

# 第4步：对比测试结果
./check.sh > after_refactor.txt
diff before_refactor.txt after_refactor.txt

# 第5步：检查覆盖率
pytest tests/ --cov=ai_tender_system.modules.business_response --cov-report=html

# 第6步：如果都通过，提交
git add .
git commit -m "refactor: 重构processor以提高可维护性"
```

---

## 🔧 配置文件说明

### test_config.json

定义了文件到测试的映射关系：

```json
{
  "file_to_tests": {
    "ai_tender_system/modules/business_response/field_recognizer.py": [
      "tests/unit/modules/test_business_response_text_filling.py::test_company_name_aliases",
      ...
    ]
  },
  "core_tests": {...},
  "test_suites": {...},
  "coverage_thresholds": {...}
}
```

**修改建议**：
- 添加新文件时，更新 `file_to_tests`
- 添加核心测试时，更新 `core_tests`
- 调整覆盖率基线时，更新 `coverage_thresholds`

---

## 🚨 常见问题

### Q1: pre-commit hook没有运行？

**原因**：可能没有执行权限

**解决**：
```bash
chmod +x .git/hooks/pre-commit
```

### Q2: 测试失败但我确定代码是对的？

**可能原因**：
1. 测试用例过时，需要更新
2. 需求变更，测试需要调整

**解决**：
1. 查看测试代码：`vim tests/unit/modules/test_business_response_text_filling.py`
2. 更新测试用例以匹配新需求
3. 更新 `TEST_REGISTRY.md` 文档
4. 提交测试和代码的修改

### Q3: 如何临时跳过pre-commit检查？

**不推荐，但如果必须**：
```bash
git commit --no-verify -m "WIP: 临时提交"
```

**建议**：
- 尽快修复问题
- 下次提交时不要使用 `--no-verify`

### Q4: CI 上测试通过，但本地失败？

**可能原因**：
1. 环境差异
2. 依赖版本不同

**解决**：
```bash
# 更新依赖
pip install -r requirements-dev.txt

# 清理缓存
find . -type d -name __pycache__ -exec rm -r {} +
pytest --cache-clear

# 重新运行测试
./check.sh
```

---

## 📊 监控和维护

### 每周检查（推荐）

```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 生成覆盖率报告
pytest tests/ --cov=ai_tender_system --cov-report=html

# 3. 查看Web监控页面
open http://localhost:8110/abtest/testing-dashboard

# 4. 更新 TEST_REGISTRY.md 中的覆盖率数据
```

### 添加新测试时

1. ✅ 编写测试代码
2. ✅ 运行测试确保通过
3. ✅ 更新 `TEST_REGISTRY.md`
4. ✅ 如果是核心测试，更新 `test_config.json`
5. ✅ 更新 `check.sh`（如果是快速测试）
6. ✅ 提交所有修改

---

## 🎯 最佳实践

### DO ✅

- ✅ 修改代码前运行 `./check.sh`
- ✅ 修改代码后运行 `./check.sh`
- ✅ 使用 `python scripts/smart_test.py` 智能选择测试
- ✅ 提交前查看 TEST_REGISTRY.md
- ✅ 添加新功能时先写测试
- ✅ 定期查看测试监控页面
- ✅ 保持测试文档更新

### DON'T ❌

- ❌ 不要使用 `git commit --no-verify` 跳过检查
- ❌ 不要忽略失败的测试
- ❌ 不要提交未测试的代码
- ❌ 不要修改测试使其"通过"而不修复问题
- ❌ 不要删除"麻烦的"测试
- ❌ 不要在没有运行测试的情况下合并PR

---

## 📞 需要帮助？

### 文档
- 测试注册表：`tests/TEST_REGISTRY.md`
- 测试路线图：`docs/TESTING_ROADMAP.md`
- 测试监控指南：`docs/TESTING_DASHBOARD_GUIDE.md`

### 工具
- 快速检查：`./check.sh`
- 智能测试：`python scripts/smart_test.py --help`
- Web监控：http://localhost:8110/abtest/testing-dashboard

### 常用命令
```bash
# 查看所有测试
pytest tests/ --co -q

# 运行失败的测试
pytest --lf -v

# 调试测试
pytest tests/unit/modules/test_xxx.py -vv --pdb

# 查看覆盖率
pytest tests/ --cov=ai_tender_system --cov-report=term-missing
```

---

**维护责任人**：开发团队
**最后更新**：2025-12-02
**版本**：v1.0
