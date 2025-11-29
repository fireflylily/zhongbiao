# 测试监控仪表板使用指南

## 📊 功能概述

测试监控仪表板是一个集成的测试管理平台，让你可以在Web界面中：
- ✅ 查看测试状态和覆盖率
- ✅ 运行自动化测试
- ✅ 查看详细的HTML测试报告（原生覆盖率报告）
- ✅ 下载测试报告
- ✅ 查看测试历史记录

**关键特性：直接集成原生HTML报告，无需重新开发可视化！**

---

## 🚀 快速开始

### 1. 访问测试监控页面

登录系统后，在导航菜单中找到：

```
AB测试 → 测试监控
```

或直接访问：
```
http://localhost:8110/abtest/testing-dashboard
```

---

## 📱 界面功能说明

### 顶部操作区

- **运行测试按钮**：点击后在后台运行单元测试，并自动生成报告
- **刷新按钮**：刷新测试状态和覆盖率数据

### 概览卡片（3个卡片）

#### 1️⃣ **最新测试运行**
显示最近一次测试的结果：
- 总计测试数
- 通过数（绿色）
- 失败数（红色）
- 运行时间

#### 2️⃣ **代码覆盖率**
圆形进度图显示：
- 覆盖率百分比
- 总语句数
- 已覆盖语句数

颜色含义：
- 🟢 绿色 (≥80%): 优秀
- 🟠 橙色 (60-80%): 良好
- 🔴 红色 (<60%): 需改进

#### 3️⃣ **可用报告**
快速链接：
- 📊 测试报告（查看测试用例详情）
- 📈 覆盖率报告（查看代码覆盖情况）
- ⬇️ 下载报告

### 标签页（3个）

#### 📊 **测试报告**标签
- 直接嵌入 `test-report.html`（原生pytest-html生成）
- 显示所有测试用例的详细结果
- 可以查看失败测试的堆栈跟踪
- 支持搜索和过滤

#### 📈 **覆盖率报告**标签
- 直接嵌入 `htmlcov/index.html`（原生coverage.py生成）
- 显示每个文件的覆盖率
- 点击文件可查看具体哪些行被测试
- 绿色/红色高亮显示测试覆盖情况

#### 📜 **历史记录**标签
显示最近的测试运行记录表格：
- 运行时间
- 测试统计（总计/通过/失败/跳过）
- 覆盖率变化
- 状态（成功/失败）

---

## 🔌 后端API接口

### 1. 获取测试状态概览
```bash
GET /api/testing/status
```

**返回示例：**
```json
{
  "success": true,
  "latest_run": {
    "id": 1,
    "run_time": "2025-11-28 14:00:00",
    "total_tests": 47,
    "passed_tests": 47,
    "failed_tests": 0,
    "coverage_percent": 8.0
  },
  "coverage": {
    "coverage_percent": 8.0,
    "total_statements": 6676,
    "covered_statements": 729
  },
  "reports_available": {
    "html_report": true,
    "coverage_report": true
  }
}
```

### 2. 运行测试
```bash
POST /api/testing/run
Content-Type: application/json

{
  "test_path": "tests/unit/"
}
```

### 3. 获取覆盖率详情
```bash
GET /api/testing/coverage
```

### 4. 查看测试历史
```bash
GET /api/testing/history?limit=20
```

### 5. 下载报告
```bash
# 下载测试报告
GET /api/testing/download/report

# 下载覆盖率报告（ZIP）
GET /api/testing/download/coverage
```

### 6. 在iframe中查看报告
```bash
# 查看测试报告
GET /api/testing/view/report

# 查看覆盖率报告
GET /api/testing/view/coverage
```

---

## 💻 本地使用（命令行）

### 运行测试并生成所有报告
```bash
# 完整命令（生成HTML测试报告 + 覆盖率报告）
pytest tests/unit/ -v --tb=short \
  --html=test-report.html --self-contained-html \
  --cov=ai_tender_system --cov-report=html --cov-report=term

# 查看报告
open test-report.html      # 测试报告
open htmlcov/index.html    # 覆盖率报告
```

### 只运行特定模块的测试
```bash
# 只测试商务应答模块
pytest tests/unit/modules/test_business_response_text_filling.py -v

# 只测试公共工具
pytest tests/unit/common/ -v
```

### 查看实时覆盖率
```bash
pytest tests/unit/ --cov=ai_tender_system --cov-report=term-missing
```

---

## 🔧 GitHub Actions集成

### 自动生成报告

每次推送到GitHub后，Actions会自动：
1. 运行所有测试
2. 生成HTML测试报告
3. 生成覆盖率报告
4. 上传为Artifacts（保留30天）

### 查看GitHub上的报告

1. 打开GitHub仓库
2. 点击 **Actions** 标签
3. 选择最近的工作流运行
4. 在 **Summary** 页面查看测试结果
5. 下载 **test-report** Artifact（包含完整报告）

---

## 📂 文件结构

```
项目根目录/
├── test-report.html           # 测试报告（73KB）
├── htmlcov/                   # 覆盖率报告目录
│   ├── index.html            # 覆盖率首页
│   └── *.html                # 各个文件的详细覆盖率
├── ai_tender_system/
│   ├── data/
│   │   └── test_history.db   # 测试历史记录数据库
│   └── web/
│       └── blueprints/
│           └── api_testing_bp.py  # 测试管理API
└── frontend/
    └── src/
        └── views/
            └── TestingDashboard.vue  # 测试监控页面
```

---

## 🎯 核心设计理念

### ✅ 复用原生报告，不重复造轮子

```
pytest-html          → test-report.html      (原生测试报告)
coverage.py          → htmlcov/index.html    (原生覆盖率报告)
                              ↓
                      直接用iframe嵌入Web界面
                              ↓
                      无需重新开发可视化！
```

**优势：**
- ✅ 功能完整：原生报告已经非常专业
- ✅ 维护简单：报告工具更新自动生效
- ✅ 开发快速：只需嵌入，无需重写
- ✅ 体验一致：本地和Web看到的报告完全相同

---

## 📊 测试用例示例

项目中已经有完整的测试用例，展示了如何测试商务应答功能：

### tests/unit/modules/test_business_response_text_filling.py

这个文件包含 **47个自动化测试用例**，覆盖：

1. **供应商名称的7种别名识别**
   ```python
   @pytest.mark.parametrize("field_alias", [
       "供应商", "供应商名称", "供应商全称",
       "公司名称", "单位名称", "应答人名称", "企业名称"
   ])
   def test_company_name_aliases(field_alias):
       # 验证所有别名都映射到 companyName
   ```

2. **地址字段的7种别名**
3. **法人代表和被授权人的10种别名**
4. **组合字段填充测试**
5. **日期格式化测试（5种格式）**
6. **签字字段跳过逻辑**
7. **空值处理**

运行结果：**47 passed in 2.07s** ✅

---

## 🎓 如何编写新的测试用例

### 场景1：测试新的字段别名

```python
@pytest.mark.parametrize("field_name,expected", [
    ("新字段名1", "standardField"),
    ("新字段名2", "standardField"),
])
def test_new_field(field_name, expected):
    recognizer = FieldRecognizer()
    assert recognizer.recognize_field(field_name) == expected
```

### 场景2：测试完整业务流程

```python
def test_business_response_flow():
    # 1. 上传招标文件
    # 2. 创建项目
    # 3. 生成商务应答
    # 4. 验证输出文档
    pass
```

---

## 🐛 故障排查

### 问题1：报告不存在
**症状：** 访问报告页面显示"报告不存在"

**解决：** 运行测试生成报告
```bash
pytest tests/unit/ --html=test-report.html --self-contained-html --cov=ai_tender_system --cov-report=html
```

### 问题2：API返回404
**症状：** 访问 `/api/testing/*` 返回404

**解决：** 检查Blueprint是否正确注册
```bash
# 查看日志确认Blueprint已注册
# 应该看到：测试状态管理API蓝图注册成功
```

### 问题3：覆盖率为0%
**症状：** 显示覆盖率0%

**解决：** 运行测试时添加 `--cov` 参数
```bash
pytest tests/unit/ --cov=ai_tender_system --cov-report=html
```

---

## 📈 提升覆盖率建议

### 当前状态（2025-11-28）

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| `field_recognizer.py` | 86% | ✅ 优秀 |
| `field_classifier.py` | 62% | ✅ 良好 |
| `constants.py` | 100% | ✅ 完美 |
| `processor.py` | 8% | 🔴 需提升 |
| `content_filler.py` | 10% | 🔴 需提升 |

### 下一步建议

1. 为 `processor.py` 添加集成测试
2. 为 `content_filler.py` 添加实际文档填充测试
3. 补充异常场景测试
4. 目标：整体覆盖率达到 **60%+**

---

## 🎯 总结

现在你的系统已经集成了完整的测试监控功能！

### ✅ 完成的功能

1. **后端API** (`api_testing_bp.py`)
   - 9个API端点
   - 测试状态查询
   - 测试运行管理
   - 报告下载和查看
   - 历史记录存储

2. **前端页面** (`TestingDashboard.vue`)
   - 测试状态概览卡片
   - 代码覆盖率圆形进度图
   - 3个标签页（测试报告/覆盖率报告/历史记录）
   - **iframe直接嵌入原生HTML报告**

3. **集成到系统**
   - 添加到路由表
   - 显示在"AB测试"菜单下
   - Blueprint已注册

4. **GitHub Actions**
   - 自动运行测试
   - 自动生成报告
   - 自动上传Artifacts

### 🌟 设计亮点

**复用原生报告，不重复开发！**
- pytest-html 生成的 `test-report.html` 已经非常专业
- coverage.py 生成的 `htmlcov/` 功能完整
- 我们只是通过iframe优雅地集成它们

这比重新开发一套可视化节省了**数周的开发时间**！

---

## 📞 需要帮助？

- 查看测试用例示例：`tests/unit/modules/test_business_response_text_filling.py`
- 查看API文档：`ai_tender_system/web/blueprints/api_testing_bp.py`
- 查看前端组件：`frontend/src/views/TestingDashboard.vue`
