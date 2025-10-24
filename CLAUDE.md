# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

**AI智能标书生成平台** - 基于人工智能的投标文档自动化处理系统。系统可处理招标文档、管理企业知识库、生成商务应答和技术方案。

**技术栈**: Python 3.11+, Flask 2.3.3, SQLite, FAISS向量搜索, 多种大模型提供商（通义千问、GPT、DeepSeek）, Bootstrap 5前端。

## 核心命令

### 启动应用

```bash
# 启动Web应用（默认端口5000）
python -m ai_tender_system.web.app

# 使用自定义端口启动
FLASK_RUN_PORT=8080 python -m ai_tender_system.web.app

# 生产模式启动
FLASK_ENV=production python -m ai_tender_system.web.app
```

### 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=ai_tender_system --cov-report=html

# 运行特定类型的测试
pytest -m unit          # 仅单元测试
pytest -m integration   # 仅集成测试
pytest -m "not slow"    # 跳过慢速测试

# 运行特定测试文件
pytest tests/unit/test_example.py

# 并行执行测试
pytest -n auto
```

### 数据库操作

```bash
# 初始化数据库
python -m ai_tender_system.database.init_db

# 执行数据库迁移（需要手动执行SQL）
sqlite3 ai_tender_system/data/knowledge_base.db < ai_tender_system/database/schema_file.sql
```

### 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（测试、代码检查工具）
pip install -r requirements-dev.txt

# 调试模式运行
export DEBUG=True
python -m ai_tender_system.web.app
```

## 架构总览

### 高层架构

系统采用**三层模块化架构**：

1. **Web层** (`ai_tender_system/web/`):
   - 单体Flask应用 (`app.py` - 3,248行，需要重构)
   - 基于Blueprint的API路由
   - 静态资源管理，支持动态CSS加载
   - 已启用CSRF保护

2. **业务逻辑层** (`ai_tender_system/modules/`):
   - `business_response/` - 商务应答生成，含资质匹配
   - `tender_info/` - 招标文档解析和需求提取
   - `point_to_point/` - 点对点问答应答生成
   - `outline_generator/` - 技术方案大纲生成
   - `knowledge_base/` - 企业知识库管理
   - `case_library/` - 历史案例管理
   - `resume_library/` - 人员简历管理
   - `document_parser/` - 多格式文档处理（PDF、Word、Excel）
   - `vector_engine/` - 基于FAISS的语义搜索

3. **数据层**:
   - SQLite数据库（schema文件位于 `ai_tender_system/database/`）
   - 文件存储（`ai_tender_system/data/uploads/`、`/outputs/`）
   - FAISS向量索引

### 关键架构模式

**1. AI模型管理（全局状态模式）**

系统使用**集中式AI模型管理**方式：
- 模型配置在 `common/config.py` 中，支持10+种大模型选项
- 前端：`static/js/core/global-state-manager.js` 管理UI状态
- 后端：通过API请求传递模型选择
- 默认模型：`yuanjing-deepseek-v3`（中国联通提供商）

**2. 动态CSS加载**

前端使用懒加载CSS以提升性能：
- `static/js/utils/css-loader.js` 定义各标签页的CSS依赖
- `static/js/components/navigation-manager.js` 在标签页切换时触发加载
- CSS文件按标签页ID映射（如 `knowledge-company-library` → `qualifications.min.css`）

**3. 资质匹配系统**

企业资质管理使用**三阶段流水线**：
1. **提取** (`modules/tender_info/extractor.py`)：使用关键词匹配从招标文档中提取资质要求
2. **匹配** (`modules/business_response/qualification_matcher.py`)：将公司资质与项目要求进行匹配
3. **插入** (`modules/business_response/docx_processor.py`)：将匹配的资质文件插入到应答文档中

核心映射：`qualification_matcher.py` 中的 `QUALIFICATION_MAPPING` 字典定义了17+种标准资质类型及其关键词。

**4. HITL工作流（人机协作）**

项目遵循状态机工作流：
- 状态流转：`pending` → `processing` → `hitl_review` → `completed`
- HITL页面允许在最终生成前进行人工审核/编辑
- 同步按钮将完成的工作推送回项目管理系统

**5. 任务ID体系架构**

系统中存在**三种不同的任务ID**，用于支持并发处理和数据隔离：

1. **`task_id`** - 处理任务ID（如 `task_xxx`）
   - 存储在 `tender_processing_tasks` 表（主键）
   - 存储在 `tender_processing_logs` 表（用于查询进度）
   - 用于跟踪文档处理流程的异步任务

2. **`hitl_task_id`** - HITL任务ID（如 `hitl_xxx`）
   - 存储在 `tender_hitl_tasks` 表（主键）
   - 存储在 `tender_document_chunks` 表（用于隔离chunks）
   - 存储在 `tender_requirements` 表（用于隔离需求）
   - 用于HITL人机协作的三步审核流程

3. **`project_id`** - 项目ID
   - 所有表的外键，指向 `tender_projects` 表
   - 代表一个招标项目

**任务ID与项目ID的关系**：
```
项目 (project_id)
  ├── 多个处理任务 (task_id)
  │     └── 每个任务对应一个HITL任务 (hitl_task_id)
  └── 多个文档分块、要求等数据
```

**任务ID的核心作用**：
- **支持并发处理** - 同一个项目可能需要多次处理（如用户选择不同章节重新处理）
- **隔离数据版本** - 不同任务产生的chunks和requirements互不影响
- **跟踪处理进度** - 每个任务有独立的状态和进度
- **HITL工作流隔离** - 每个HITL任务有独立的三步审核流程

**注意事项**：
- 不建议完全用项目ID代替任务ID，因为需要支持重复处理、并发控制和版本管理
- 如果业务确定一个项目只处理一次，可以考虑简化为 `project_id` + 版本号的方式

## 关键配置

### 环境变量（`.env` 文件）

运行所需配置：
```ini
# AI模型（至少需要一个）
ACCESS_TOKEN=your_unicom_token           # 中国联通MaaS平台
OPENAI_API_KEY=your_openai_key          # 可选
SHIHUANG_API_KEY=your_shihuang_key      # 可选，用于GPT-4

# 应用配置
SECRET_KEY=your_secret_key_here          # CSRF保护密钥
DEBUG=False                              # 生产环境：False
FLASK_RUN_PORT=5000                      # 默认端口

# API端点
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1
```

### 模型配置

模型定义在 `common/config.py` 的 `multi_model_config` 中：
- 中国联通系列：`yuanjing-deepseek-v3`、`yuanjing-qwen3-235b`、`yuanjing-glm-rumination` 等
- OpenAI：通过自定义代理的 `gpt-4o-mini`
- 始皇API：`shihuang-gpt4o-mini`、`shihuang-gpt4`（用于内联应答）

添加新模型时需要更新：
1. `common/config.py` - 后端配置
2. 后端会通过 `/api/ai-models` 端点自动暴露模型

## 数据库架构

**主数据库**：`ai_tender_system/data/knowledge_base.db`

关键表（schema位于 `ai_tender_system/database/`）：
- `companies` - 企业信息
- `company_qualifications` - 资质文件（营业执照、ISO认证等）
- `qualification_types` - 预定义资质类型（17种标准类型）
- `tender_projects` - 招标项目元数据
- `knowledge_documents` - 企业知识库
- `cases` - 历史案例库
- `resumes` - 人员简历库

**Schema管理**：在 `database/` 目录创建 `.sql` 文件，并在 `common/database.py` 中导入即可添加新表。

## 前端架构

**框架**：原生JavaScript + Bootstrap 5（无React/Vue）

**关键JavaScript模块**：
- `core/global-state-manager.js` - 集中式状态管理（公司、项目、AI模型）
- `components/navigation-manager.js` - 标签页导航和CSS加载
- `utils/css-loader.js` - 动态CSS注入
- `hitl-config-manager.js` - HITL工作流UI逻辑（1,422行，较复杂）
- `pages/index/` - 页面特定处理器（商务应答、点对点应答等）

**事件驱动模式**：大多数交互使用Bootstrap事件（`shown.bs.tab`、`click`）+ 通过 `window.dispatchEvent` 派发的自定义事件。

**CSS组织**：
- `static/css/base/` - 变量、重置样式
- `static/css/components/` - 可复用组件（按钮、卡片、表单）
- 生产环境使用压缩版本（`.min.css`）

## 常见开发模式

### 添加新资质类型

1. **数据库**：在 `database/company_qualifications_schema.sql` 中添加：
   ```sql
   INSERT INTO qualification_types (type_key, type_name, category, sort_order)
   VALUES ('new_qual', '新资质名称', '行业资质', 20);
   ```

2. **匹配器**：更新 `modules/business_response/qualification_matcher.py`：
   ```python
   QUALIFICATION_MAPPING = {
       'new_qual': {
           'keywords': ['关键词1', '关键词2'],
           'priority': 'medium',
           'category': '资质类别'
       }
   }
   ```

3. **提取器**：更新 `modules/tender_info/extractor.py` 中的 `_get_qualification_keywords()` 方法。

### 添加新API端点

1. 在 `web/blueprints/` 创建blueprint或添加到现有blueprint
2. 在 `web/app.py` 中注册blueprint
3. 为POST/PUT/DELETE端点添加CSRF保护
4. 前端：使用 `csrf-protection.js` 工具发起请求

### 处理单体 `app.py`

**挑战**：`web/app.py` 有3,248行，包含多个职责。

**当前重构工作**：正在将blueprint提取到 `web/blueprints/` 目录。

**编辑 `app.py` 时**：
- 变更最终应迁移到blueprint中
- 在代码注释中记录新端点
- 保持相关路由组织在一起

## 测试策略

**当前覆盖率**：11.05%（目标：80%+）

**优先测试顺序**：
1. `common/` 工具类（最简单，纯函数）
2. `modules/` 业务逻辑（模拟外部依赖）
3. `web/` API端点（使用Flask测试客户端）

**模拟AI模型**：
```python
def test_with_mock_llm(mocker):
    mocker.patch(
        'ai_tender_system.common.llm_client.LLMClient.chat',
        return_value={'content': '测试响应'}
    )
```

**数据库测试**：通过fixtures使用临时SQLite数据库。

## 关键文件说明

**重大变更必读**：
1. `common/config.py` - 所有配置、模型定义
2. `common/database.py` - 数据库抽象层
3. `common/llm_client.py` - AI模型客户端封装
4. `web/app.py` - 主Flask应用（单体，正在重构）
5. `modules/business_response/qualification_matcher.py` - 核心资质逻辑
6. `modules/tender_info/extractor.py` - 招标需求提取（2,000+行）

**前端关键文件**：
1. `static/js/core/global-state-manager.js` - 状态管理
2. `static/js/hitl-config-manager.js` - HITL工作流（复杂）
3. `static/js/components/navigation-manager.js` - 标签页导航

## 已知问题与技术债务

1. **单体 `app.py`**：需要进一步重构为blueprints
2. **测试覆盖率**：仅11% - 优先改进领域
3. **硬编码值**：部分API端点存在魔术数字
4. **错误处理**：端点间错误响应不一致
5. **CSS加载**：最近已修复 - 确保在标签页切换时调用 `loadCSSForTab()`
6. **文档**：部分模块缺少文档字符串

## 性能考虑

- **FAISS索引**：大型知识库（10,000+文档）时可能较慢
- **AI模型调用**：尽可能实现缓存
- **数据库查询**：无ORM，使用原生SQL - 注意N+1查询问题
- **前端**：动态CSS加载改善首屏加载时间
- **文件上传**：在 `common/config.py` 中配置了100MB限制

## 安全说明

- **CSRF保护**：通过Flask-WTF全局启用
- **输入验证**：对所有用户输入进行清理，特别是文件上传
- **API密钥**：切勿提交到git - 使用 `.env` 文件
- **文件路径**：使用 `pathlib.Path` 防止路径遍历攻击
- **SQL注入**：使用参数化查询（已实现）

## 部署

**Docker**（推荐）：
```bash
docker build -t ai-tender-system .
docker run -p 5000:5000 -v $(pwd)/data:/app/data ai-tender-system
```

**生产服务器**（Gunicorn）：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 ai_tender_system.web.app:app
```

**环境设置**：设置 `FLASK_ENV=production` 和 `DEBUG=False`。

## 相关文档

- `README.md` - 项目概览和安装
- `TESTING_GUIDE.md` - 完整测试指南
- `CSRF_PROTECTION_GUIDE.md` - 安全实现
- `ai_tender_system/docs/` - 架构和实施文档
- `PERFORMANCE_OPTIMIZATION_GUIDE.md` - 性能调优
- `MIGRATION_SUMMARY.md` - 最近迁移说明

## Git工作流

**主分支**：`master`（生产环境）

**提交规范**：
- `feat:` 新功能
- `fix:` Bug修复
- `refactor:` 代码重构
- `docs:` 文档更新
- `test:` 测试添加/修改

**重要提示**：修改数据库schema时，还需更新：
1. `database/` 中的SQL schema文件
2. `modules/` 中的相关业务逻辑
3. 如果暴露API，需更新API端点
4. 如果UI有变化，需更新前端
