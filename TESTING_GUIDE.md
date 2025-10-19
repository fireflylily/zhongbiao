# 🧪 测试框架使用指南

> AI 标书系统 - 完整的测试框架文档

---

## 📋 目录

- [测试框架概述](#测试框架概述)
- [快速开始](#快速开始)
- [测试结构](#测试结构)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [测试覆盖率](#测试覆盖率)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 🎯 测试框架概述

### 当前状态

✅ **测试框架已搭建完成**

| 组件 | 状态 | 说明 |
|------|------|------|
| pytest | ✅ 已安装 | v7.4.3 |
| pytest-cov | ✅ 已安装 | v4.1.0 |
| pytest-mock | ✅ 已安装 | v3.12.0 |
| 测试目录 | ✅ 已创建 | `tests/` |
| 配置文件 | ✅ 已配置 | `pytest.ini`, `.coveragerc` |
| Fixtures | ✅ 已创建 | `tests/conftest.py` |
| 示例测试 | ✅ 已编写 | 32 个示例测试 |

### 测试运行结果

```
✅ 29 passed
⏭️ 2 skipped
⚠️ 1 error (mock fixture 需要修复)
📊 当前覆盖率: 11.05%
🎯 目标覆盖率: 80%+
```

---

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 安装核心测试工具
pip install pytest pytest-cov pytest-mock

# 或安装所有开发依赖
pip install -r requirements-dev.txt
```

### 2. 运行第一个测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/unit/test_example.py

# 运行特定测试
pytest tests/unit/test_example.py::test_basic_assertion
```

### 3. 查看测试覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=ai_tender_system --cov-report=html

# 打开 HTML 报告
open htmlcov/index.html
```

---

## 📂 测试结构

```
tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                 # 全局 fixtures 和配置
│
├── unit/                       # 单元测试（测试单个函数/类）
│   ├── __init__.py
│   ├── test_example.py         # 示例测试（32个测试用例）
│   ├── common/                 # 公共模块测试
│   │   ├── __init__.py
│   │   └── test_config.py      # 配置模块测试
│   ├── modules/                # 业务模块测试
│   │   └── (待添加)
│   └── web/                    # Web 模块测试
│       └── (待添加)
│
├── integration/                # 集成测试（测试模块间交互）
│   └── (待添加)
│
├── e2e/                        # 端到端测试（测试完整流程）
│   └── (待添加)
│
└── fixtures/                   # 测试数据和夹具
    └── (待添加)
```

---

## 🏃 运行测试

### 基础命令

```bash
# 运行所有测试
pytest

# 详细输出（-v）
pytest -v

# 非常详细输出（-vv）
pytest -vv

# 显示打印输出（-s）
pytest -s

# 失败时立即停止
pytest -x

# 失败后进入调试器
pytest --pdb
```

### 按标记运行

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 排除慢速测试
pytest -m "not slow"

# 组合标记
pytest -m "unit and not slow"
```

### 按路径运行

```bash
# 运行特定目录
pytest tests/unit/

# 运行特定文件
pytest tests/unit/test_example.py

# 运行特定类
pytest tests/unit/test_example.py::TestCalculations

# 运行特定测试
pytest tests/unit/test_example.py::test_basic_assertion
```

### 并行运行（需要 pytest-xdist）

```bash
# 使用 4 个进程并行运行
pytest -n 4

# 自动检测 CPU 数量
pytest -n auto
```

### 覆盖率报告

```bash
# 生成终端报告
pytest --cov=ai_tender_system

# 生成 HTML 报告
pytest --cov=ai_tender_system --cov-report=html

# 生成 XML 报告（CI/CD 用）
pytest --cov=ai_tender_system --cov-report=xml

# 只显示缺失覆盖的行
pytest --cov=ai_tender_system --cov-report=term-missing
```

---

## ✍️ 编写测试

### 基础测试结构

```python
# tests/unit/test_my_module.py

import pytest

def test_simple_function():
    """测试简单函数"""
    result = 1 + 1
    assert result == 2

def test_with_fixture(sample_data):
    """使用 fixture"""
    assert len(sample_data) > 0
```

### 测试类

```python
class TestMyClass:
    """组织相关测试"""

    def test_method_one(self):
        """测试方法1"""
        assert True

    def test_method_two(self):
        """测试方法2"""
        assert 2 + 2 == 4
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    """参数化测试 - 一次定义，多组数据"""
    assert input * 2 == expected
```

### 异常测试

```python
def test_exception():
    """测试异常"""
    with pytest.raises(ValueError):
        int("not a number")

    with pytest.raises(ZeroDivisionError, match="division by zero"):
        1 / 0
```

### 使用 Fixtures

```python
@pytest.fixture
def sample_data():
    """定义测试数据"""
    return [1, 2, 3, 4, 5]

def test_with_fixture(sample_data):
    """使用 fixture"""
    assert sum(sample_data) == 15
```

### Mock 测试

```python
def test_with_mock(mocker):
    """使用 pytest-mock"""
    # Mock 函数
    mock_func = mocker.Mock(return_value=42)

    result = mock_func()
    assert result == 42

    # 验证调用
    mock_func.assert_called_once()
```

### Flask 应用测试

```python
def test_api_endpoint(client):
    """测试 API 端点"""
    response = client.get('/api/health')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'ok'
```

---

## 📊 测试覆盖率

### 当前覆盖率统计

| 模块 | 覆盖率 | 说明 |
|------|--------|------|
| **总体** | **11.05%** | 🔴 需要大幅提升 |
| common/ | ~20% | 🟡 基础覆盖 |
| modules/ | ~10% | 🔴 急需测试 |
| web/ | ~10% | 🔴 急需测试 |

### 提升覆盖率计划

#### 第一阶段：核心模块（目标 40%）

```bash
# 优先测试这些模块
tests/unit/common/
  ├── test_config.py        ✅ 已完成
  ├── test_database.py      ⏭️ 待编写
  └── test_llm_client.py    ⏭️ 待编写

tests/unit/modules/
  ├── test_document_parser.py    ⏭️ 待编写
  └── test_vector_engine.py      ⏭️ 待编写
```

#### 第二阶段：业务模块（目标 60%）

```bash
tests/unit/modules/
  ├── test_tender_info_extractor.py       ⏭️ 待编写
  ├── test_business_response_processor.py ⏭️ 待编写
  └── test_knowledge_base_manager.py      ⏭️ 待编写
```

#### 第三阶段：Web 和集成测试（目标 80%+）

```bash
tests/unit/web/
  └── test_routes.py               ⏭️ 待编写

tests/integration/
  └── test_end_to_end_workflow.py  ⏭️ 待编写
```

### 查看详细覆盖率报告

```bash
# 生成 HTML 报告
pytest --cov=ai_tender_system --cov-report=html

# 在浏览器中打开
open htmlcov/index.html
```

报告内容：
- ✅ 每个文件的覆盖率百分比
- 📊 未覆盖的代码行高亮显示
- 📈 覆盖率趋势图

---

## 🎯 最佳实践

### 1. 测试命名规范

```python
# ✅ 好的命名
def test_extract_deadline_from_standard_format():
    """测试从标准格式提取截止日期"""
    pass

def test_extract_deadline_with_missing_data():
    """测试缺失数据时的截止日期提取"""
    pass

# ❌ 不好的命名
def test1():
    pass

def test_func():
    pass
```

### 2. 一个测试只测一件事

```python
# ✅ 好的做法
def test_addition():
    assert 2 + 2 == 4

def test_subtraction():
    assert 5 - 3 == 2

# ❌ 不好的做法
def test_math():
    assert 2 + 2 == 4
    assert 5 - 3 == 2
    assert 3 * 4 == 12
```

### 3. 使用描述性的断言消息

```python
# ✅ 好的做法
assert result > 0, f"Expected positive result, got {result}"

# ❌ 不好的做法
assert result > 0
```

### 4. 隔离测试（不依赖其他测试）

```python
# ✅ 好的做法 - 每个测试独立
@pytest.fixture
def clean_database():
    db = create_test_db()
    yield db
    db.cleanup()

def test_insert(clean_database):
    # 使用干净的数据库
    pass

# ❌ 不好的做法 - 测试间有依赖
test_order = []

def test_first():
    test_order.append(1)

def test_second():
    assert len(test_order) == 1  # 依赖 test_first
```

### 5. 使用 Fixtures 共享设置

```python
# ✅ 好的做法
@pytest.fixture
def sample_user():
    return {"name": "Test User", "email": "test@example.com"}

def test_user_name(sample_user):
    assert sample_user["name"] == "Test User"

def test_user_email(sample_user):
    assert "test@example.com" in sample_user["email"]
```

### 6. 测试边界条件

```python
def test_age_validation():
    """测试年龄验证的边界"""
    assert validate_age(0) == False   # 最小边界
    assert validate_age(1) == True    # 有效值
    assert validate_age(150) == True  # 有效值
    assert validate_age(151) == False # 最大边界
    assert validate_age(-1) == False  # 异常值
```

---

## ❓ 常见问题

### Q1: 测试运行很慢怎么办？

**解决方案**：

```bash
# 1. 并行运行测试
pytest -n auto

# 2. 只运行失败的测试
pytest --lf  # last-failed

# 3. 跳过慢速测试
pytest -m "not slow"

# 4. 使用更快的断言模式
pytest --assert=plain
```

### Q2: 如何 Mock AI 模型调用？

**解决方案**：

```python
def test_with_mock_llm(mocker):
    """Mock LLM 调用"""
    mock_response = {"content": "测试响应"}

    mocker.patch(
        'ai_tender_system.common.llm_client.LLMClient.chat',
        return_value=mock_response
    )

    # 执行测试
    result = my_function_that_calls_llm()
    assert "测试响应" in result
```

### Q3: 如何测试数据库操作？

**解决方案**：

```python
def test_database_insert(temp_db):
    """使用临时数据库测试"""
    from ai_tender_system.common.database import Database

    db = Database(str(temp_db))
    db.execute("INSERT INTO users (name) VALUES ('Test')")

    result = db.execute_query("SELECT * FROM users")
    assert len(result) == 1
```

### Q4: 测试覆盖率如何快速提升？

**建议顺序**：

1. **工具函数**（最容易测试）
   - `common/` 目录下的工具类
   - 纯函数，无副作用

2. **业务逻辑**（中等难度）
   - `modules/` 下的处理器
   - Mock 外部依赖

3. **API 端点**（较难）
   - 使用 Flask test client
   - 集成测试

### Q5: 如何处理测试中的文件操作？

**解决方案**：

```python
def test_file_upload(temp_dir):
    """使用临时目录测试文件上传"""
    test_file = temp_dir / "test.pdf"
    test_file.write_bytes(b"fake pdf content")

    # 执行测试
    result = process_file(test_file)
    assert result is not None
```

---

## 📚 相关资源

### 文档

- [Pytest 官方文档](https://docs.pytest.org/)
- [Coverage.py 文档](https://coverage.readthedocs.io/)
- [pytest-mock 文档](https://pytest-mock.readthedocs.io/)

### 项目文档

- [README.md](README.md) - 项目总览
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [测试策略](ai_tender_system/docs/implementation/testing-strategy.md) 🚧

---

## 🎯 下一步行动

### 立即执行

- [ ] 修复 `mock_llm_response` fixture 错误
- [ ] 为 `common/database.py` 编写测试（目标覆盖率 80%）
- [ ] 为 `modules/document_parser/` 编写测试

### 本周目标

- [ ] 核心模块测试覆盖率达到 40%
- [ ] 编写 10+ 个新测试文件
- [ ] 设置 CI/CD 自动测试

### 长期目标

- [ ] 整体测试覆盖率达到 80%+
- [ ] 集成测试覆盖主要流程
- [ ] 性能测试基准建立

---

**最后更新**: 2025-10-19
**维护者**: AI标书系统开发团队
