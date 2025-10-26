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
- `core/api-client.js` - 统一API调用封装，支持自动重试和错误处理
- `core/notification.js` - 统一通知管理器
- `components/navigation-manager.js` - 标签页导航和CSS加载
- `components/universal-uploader.js` - 通用文件上传组件
- `utils/css-loader.js` - 动态CSS注入
- `utils/document-preview.js` - 统一文档预览工具（支持Word/PDF/图片）
- `utils/hitl-file-loader.js` - **新增** HITL文件加载工具，简化从HITL加载文件的逻辑
- `hitl-config-manager.js` - HITL工作流UI逻辑（1,422行，较复杂）
- `pages/index/` - 页面特定处理器（商务应答、点对点应答等）

**事件驱动模式**：大多数交互使用Bootstrap事件（`shown.bs.tab`、`click`）+ 通过 `window.dispatchEvent` 派发的自定义事件。

**CSS组织**：
- `static/css/base/` - 变量、重置样式
- `static/css/components/` - 可复用组件（按钮、卡片、表单）
- 生产环境使用压缩版本（`.min.css`）

## 前端重构指南（2025年10月更新）

### 最近完成的重构工作

**目标**：消除代码重复，统一通知系统，集中状态管理，提升可维护性。

**重构成果**：
1. **business-response-handler.js**: 936行 → 759行 (-177行, -18.9%)
2. **point-to-point-handler.js**: 1367行 → 1285行 (-82行, -6.0%)
3. **创建新工具**: `utils/hitl-file-loader.js` (125行，可复用)

**重构模式**：

1. **通知统一** - 使用 `window.notifications` 替代 `alert()`
   ```javascript
   // ❌ 旧代码
   alert('错误信息');
   if (typeof showNotification === 'function') {
       showNotification('消息', 'warning');
   } else {
       alert('消息');
   }

   // ✅ 新代码
   window.notifications.error('错误信息');
   window.notifications.warning('消息');
   window.notifications.success('成功');
   ```

2. **全局变量迁移** - 使用 `GlobalStateManager`
   ```javascript
   // ❌ 旧代码
   window.businessResponseFilePath = '/path/to/file';
   window.businessResponseFileName = 'file.docx';

   // ✅ 新代码
   const fileData = window.globalState.getFile('business');
   // fileData 包含 { fileName, filePath, fileUrl, fileSize }
   ```

3. **文档预览简化** - 使用 `DocumentPreviewUtil`
   ```javascript
   // ❌ 旧代码：70行手动创建模态框、fetch、docx渲染

   // ✅ 新代码：2行调用
   window.documentPreviewUtil.preview(downloadUrl, filename);
   ```

4. **API调用统一** - 使用 `window.apiClient`
   ```javascript
   // ❌ 旧代码
   const response = await fetch('/api/endpoint', {
       method: 'POST',
       body: formData
   });
   const data = await response.json();

   // ✅ 新代码（自动重试3次，指数退避）
   const data = await window.apiClient.post('/api/endpoint', formData);
   ```

5. **HITL文件加载** - 使用 `HITLFileLoader`
   ```javascript
   // ❌ 旧代码：113行，包含大量调试日志和DOM操作

   // ✅ 新代码：简化为配置驱动
   const loader = new window.HITLFileLoader({
       fileType: 'business',  // 'technical', 'pointToPoint'
       fileInfoElementId: 'businessTemplateFileName',
       uploadAreaId: 'businessResponseForm',
       onFileLoaded: (fileData) => {
           // 自定义加载后逻辑
       },
       debug: false
   });
   loader.load();
   ```

### 重构时的最佳实践

**识别重构机会**：
- 代码重复：相同逻辑出现在2+个文件中
- 条件分支：`if (typeof X === 'function')` 说明缺少统一抽象
- 长函数：100+行的函数通常可以分解
- 硬编码：魔术数字、重复的URL、配置值

**重构步骤**：
1. 先理解现有代码的所有用途
2. 创建或使用现有工具类
3. 在一个文件中测试新方法
4. 逐步迁移其他文件
5. 保持向后兼容（至少一个版本周期）
6. 更新文档

**工具类清单**：
- `window.notifications` - 通知（success/error/warning/info）
- `window.globalState` - 状态管理（getCompany/getProject/getFile/setFile）
- `window.apiClient` - API调用（get/post/put/delete，自动重试）
- `window.documentPreviewUtil` - 文档预览
- `window.HITLFileLoader` - HITL文件加载
- `window.UniversalUploader` - 文件上传组件
- `window.SSEClient` - **新增** SSE流式处理工具类

## 前端架构与重构指南（完整版）

### JavaScript 架构规范

#### 分层架构（基于项目实际结构）

系统采用**四层模块化架构**（共124个JS/CSS文件）：

```
static/js/
├── core/            # 核心层 - 全局基础服务
│   ├── global-state-manager.js  (647行) - 单一数据源状态管理
│   ├── api-client.js            - HTTP客户端（自动重试、CSRF、错误处理）
│   ├── notification.js          - 统一通知系统
│   └── validation.js            - 表单验证工具
│
├── utils/           # 工具层 - 可复用辅助函数
│   ├── sse-client.js (165行)   - **新增** SSE流式处理
│   ├── document-preview.js      - 文档预览（Word/PDF/图片）
│   ├── css-loader.js            - 动态CSS懒加载
│   └── hitl-file-loader.js      - HITL文件加载器
│
├── components/      # 组件层 - 可复用UI组件
│   ├── navigation-manager.js    - 标签页导航
│   ├── universal-uploader.js    - 通用文件上传
│   ├── modal-manager.js         - 模态框管理
│   └── company-selector.js      - 公司选择器
│
└── pages/           # 页面层 - 特定页面逻辑
    ├── index/                   # 首页模块（商务应答、点对点、技术方案）
    ├── knowledge-base/          # 知识库模块（公司、案例、文档、简历）
    └── tender-processing-step3/ # 投标处理（最复杂，2761行需拆分）
```

**职责边界**：

| 层级 | 职责 | 不允许 | 示例 |
|------|------|--------|------|
| **core/** | 全局服务、状态管理、基础设施 | 依赖pages/、直接DOM操作 | GlobalStateManager, ApiClient |
| **utils/** | 无状态工具函数、辅助类 | 依赖pages/、维护全局状态 | SSEClient, documentPreview |
| **components/** | 可复用UI组件、交互逻辑 | 依赖pages/、业务逻辑 | UniversalUploader, Navigation |
| **pages/** | 页面特定逻辑、业务流程 | 被其他层依赖 | ProposalGenerator, BusinessResponse |

**依赖规则**：
- ✅ **向下依赖**：pages/ → components/ → utils/ → core/
- ❌ **禁止向上依赖**：core/ 不能依赖 components/

---

#### 命名与组织规范

**文件命名**：
```
kebab-case.js          # 工具类、组件
PascalCase.js          # Manager类（ChapterSelectorManager.js）
index.js               # 入口文件（聚合多个模块）
*.min.js               # 压缩版本（生产环境）
```

**类命名**：
```javascript
// ✅ 正确
class GlobalStateManager { }
class SSEClient { }
class ProposalGenerator { }

// ❌ 错误
class globalState { }        // 应该PascalCase
class sseClient { }          // 应该PascalCase
class proposalGen { }        // 不要缩写
```

**全局变量**（必须挂载到window）：
```javascript
// ✅ 正确 - 明确的命名空间
window.globalState = new GlobalStateManager();
window.apiClient = new ApiClient();
window.SSEClient = SSEClient;  // 类本身，供实例化

// ❌ 错误 - 污染全局命名空间
var state = { };  // 直接声明全局变量
manager = { };    // 隐式全局变量
```

---

### CSS 架构规范

#### CSS变量系统（基于base/variables.css）

**核心变量分类**：

```css
:root {
    /* 1. 颜色系统 - Bootstrap覆盖 + 自定义品牌色 */
    --bs-primary: #4a89dc;
    --bs-success: #48cfad;
    --brand-primary: #4a89dc;
    --brand-primary-light: #74b9ff;

    /* 2. 中性色 - 文本、背景、边框 */
    --text-primary: #333;
    --text-secondary: #6c757d;
    --bg-light: #f8f9fa;
    --border-light: #dee2e6;

    /* 3. 间距系统 - 统一的spacing scale */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 18px;
    --spacing-xl: 24px;

    /* 4. 圆角 - 4级圆角系统 */
    --border-radius-sm: 4px;
    --border-radius-md: 8px;
    --border-radius-lg: 12px;

    /* 5. 阴影 - 5级层次系统 */
    --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 8px rgba(0,0,0,0.12);

    /* 6. Z-index层级 */
    --z-dropdown: 1000;
    --z-modal: 1050;
    --z-tooltip: 1070;
}
```

**使用规范**：

```css
/* ✅ 正确 - 使用变量 */
.card {
    background: var(--bg-white);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-sm);
}

/* ❌ 错误 - 硬编码值 */
.card {
    background: #ffffff;
    padding: 18px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}
```

---

#### 组件化CSS（基于components/目录）

**目录结构**：
```
static/css/
├── base/                  # 全局基础
│   ├── variables.css      # CSS变量（所有变量定义在此）
│   └── reset.css          # 重置样式
│
├── components/            # 可复用组件样式
│   ├── buttons.css        # 按钮组件（7.4KB）
│   ├── cards.css          # 卡片组件（8.2KB）
│   ├── modals.css         # 模态框
│   ├── forms.css          # 表单组件
│   └── *.min.css          # 压缩版本
│
├── atoms/                 # 原子样式（最小单元）
│   ├── badges.css         # 徽章
│   ├── loaders.css        # 加载动画
│   └── tags.css           # 标签
│
└── utilities/             # 工具类（按需使用）
    ├── spacing.css        # 间距工具 (m-*, p-*)
    ├── text.css           # 文本工具 (text-*)
    └── display.css        # 显示工具 (d-*, flex-*)
```

**BEM命名规范**：
```css
/* ✅ 推荐 - BEM命名 */
.card { }                   /* Block */
.card__header { }           /* Element */
.card--highlighted { }      /* Modifier */

/* ✅ 可接受 - Bootstrap风格 */
.btn { }
.btn-primary { }
.btn-lg { }

/* ❌ 避免 - 深度嵌套 */
.card .header .title .icon { }  /* 4层嵌套，难以维护 */
```

---

### 通用重构模式（7大核心模式）

#### 1. SSE流式处理统一化

**识别信号**：
- 代码中有 `response.body.getReader()` + 70+行流解析逻辑
- 多个模块重复实现SSE处理
- 手动管理buffer、decoder、event解析

**重构方案**：
```javascript
// ❌ 旧代码：每个模块重复70行
fetch(url, { method: 'POST', body: formData })
    .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        // ... 70行流处理逻辑
    });

// ✅ 新代码：使用SSEClient工具类
const sseClient = new window.SSEClient();
await sseClient.stream({
    url: '/api/generate-proposal-stream',
    formData: formData,
    onEvent: (data) => {
        // 处理每个SSE事件
        if (data.progress !== undefined) {
            updateProgress(data.progress);
        }
    },
    onComplete: (data) => {
        // 完成回调
        showSuccess(data);
    },
    onError: (error) => {
        // 错误处理
        showError(error.message);
    }
});
```

**收益**：
- 减少70+行重复代码（每个使用SSE的模块）
- 统一错误处理和重试逻辑
- 支持AbortController取消操作
- 可复用性：商务应答、点对点应答、技术方案生成

**实际案例**：
- `pages/index/proposal-generator.js` - 从610行减少到16行（减少97%）

---

#### 2. API调用标准化

**识别信号**：
- 40+行手动fetch + 错误处理代码
- 重复的CSRF token管理
- 不一致的错误响应格式

**重构方案**：
```javascript
// ❌ 旧代码：122行手动fetch
const response = await window.csrfFetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});

if (!response.ok) {
    const contentType = response.headers.get('Content-Type');
    if (contentType?.includes('json')) {
        const error = await response.json();
        // 20行JSON错误处理...
    } else {
        const text = await response.text();
        // 20行HTML错误解析...
    }
}
const result = await response.json();

// ✅ 新代码：10行统一调用
const result = await window.apiClient.post(url, data);
// 自动处理: CSRF、重试(3次)、错误解析、超时
```

**apiClient API**：
```javascript
// 所有方法自动包含CSRF、重试、错误处理
await window.apiClient.get(url, params);
await window.apiClient.post(url, data);
await window.apiClient.put(url, data);
await window.apiClient.delete(url);
```

**收益**：
- 减少82%代码（122行 → 10行）
- 自动重试3次（指数退避）
- 统一错误格式
- 自动CSRF token管理

---

#### 3. 全局状态管理

**识别信号**：
- 到处使用 `window.xxx` 全局变量
- 文件路径、公司信息散落各处
- 状态同步困难（Tab切换时数据丢失）

**重构方案**：
```javascript
// ❌ 旧代码：全局变量污染
window.businessResponseFilePath = '/path/to/file';
window.businessResponseFileName = 'file.docx';
window.currentCompanyId = '123';
window.currentProjectName = 'ABC项目';

// ✅ 新代码：GlobalStateManager集中管理
// 1. 设置状态
window.globalState.setCompany('123', 'ABC公司');
window.globalState.setFile('business', {
    fileName: 'file.docx',
    filePath: '/path/to/file',
    fileUrl: '/api/download/file.docx',
    fileSize: 1024000
});

// 2. 获取状态
const company = window.globalState.getCompany();  // {id, name, details}
const file = window.globalState.getFile('business');

// 3. 订阅变化（响应式）
const unsubscribe = window.globalState.subscribe('company', (company) => {
    console.log('公司变化:', company);
    updateUI(company);
});
```

**GlobalState API完整清单**：
```javascript
// 公司管理
setCompany(id, name, details)
getCompany() / getCompanyId() / getCompanyName()
clearCompany()

// 项目管理
setProject(id, name, number)
getProject() / getProjectId() / getProjectName()
clearProject()

// 文件管理（5种类型）
setFile(fileType, {fileName, filePath, fileUrl, fileSize})
getFile(fileType)  // fileType: 'business' | 'technical' | 'pointToPoint' | ...
clearFile(fileType) / clearAllFiles()

// AI模型管理
setAvailableModels(models)
getAvailableModels()
setSelectedModel(modelName)
getSelectedModel()

// HITL任务管理
setHitlTaskId(taskId)
getHitlTaskId()

// 批量操作
setBulk({company, project, files, hitlTaskId})
clearAll()

// 调试
debug()  // 打印完整状态快照
```

**收益**：
- 单一数据源（Single Source of Truth）
- 响应式更新（订阅/通知模式）
- 自动兼容旧代码（`window.projectDataBridge`）
- 减少全局变量污染

---

#### 4. 配置驱动UI生成

**识别信号**：
- 50+行硬编码按钮/表单生成逻辑
- 添加新按钮需要修改多处代码
- 按钮顺序难以调整

**重构方案**：
```javascript
// ❌ 旧代码：硬编码50+行
if (outputFiles.proposal) {
    const btn = document.createElement('button');
    btn.className = 'btn btn-primary';
    btn.innerHTML = '<i class="bi bi-eye"></i> 预览';
    btn.onclick = () => preview(outputFiles.proposal);
    container.appendChild(btn);
}
if (outputFiles.analysis) {
    const btn = document.createElement('button');
    // 重复10行...
}

// ✅ 新代码：配置驱动
static BUTTON_ACTIONS = [
    {
        type: 'preview',
        condition: (files) => files.proposal,
        create: function(files) {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-primary me-2';
            btn.innerHTML = '<i class="bi bi-eye"></i> 预览';
            btn.onclick = () => this.previewProposal(files.proposal);
            return btn;
        }
    },
    {
        type: 'downloads',
        condition: (files) => Object.keys(files).length > 0,
        create: function(files) {
            // 返回按钮数组
            return Object.keys(files).map(type => this.createDownloadButton(type));
        }
    }
];

// 统一生成器
createButtons(files) {
    this.constructor.BUTTON_ACTIONS.forEach(action => {
        if (action.condition.call(this, files)) {
            const result = action.create.call(this, files);
            if (Array.isArray(result)) {
                result.forEach(btn => container.appendChild(btn));
            } else {
                container.appendChild(result);
            }
        }
    });
}
```

**收益**：
- 添加新按钮只需扩展配置数组
- 按钮顺序可配置（调整数组顺序）
- 条件判断统一管理
- 减少重复代码50%+

---

#### 5. DOM操作辅助方法

**识别信号**：
- 大量 `if (element) element.classList.add(...)` 重复检查
- 频繁的空值检查
- DOM操作样板代码过多

**重构方案**：
```javascript
// ❌ 旧代码：重复的空值检查（10+行）
if (element) element.classList.add('d-none');
if (input) input.value = data;
if (select) select.disabled = true;
if (span) span.textContent = text;

// ✅ 新代码：统一辅助方法（4行）
this.hideElement(element);
this.setValue(input, data);
this.setDisabled(select, true);
this.setTextContent(span, text);
```

**标准辅助方法清单**：
```javascript
// 显示/隐藏
showElement(element)                    // 移除 d-none
hideElement(element)                    // 添加 d-none
toggleElement(element, show)            // 条件切换

// 内容设置
setElementHTML(element, html)           // innerHTML
setTextContent(element, text)           // textContent
setValue(element, value)                // input.value
getValue(element, defaultValue)         // 获取值 + 默认值

// CSS类操作
addClass(element, className)
removeClass(element, className)
toggleClass(element, className, condition)

// 样式/属性
setStyle(element, property, value)      // element.style.xxx
setDisabled(element, disabled)          // element.disabled
```

**收益**：
- 减少样板代码60%+
- 统一空值处理
- 提升代码可读性
- 避免null/undefined错误

---

#### 6. 日志分级系统

**识别信号**：
- `console.log` 满天飞
- 生产环境也输出调试日志
- 无法区分重要日志和调试信息

**重构方案**：
```javascript
// ❌ 旧代码：无分级
log(...args) {
    if (DEBUG) console.log(...args);
}

// ✅ 新代码：分级日志
log(level, ...args) {
    // level: 'debug' | 'info' | 'warn' | 'error'
    if (level === 'debug' && !DEBUG) return;  // debug仅DEBUG模式

    const prefix = '[ModuleName]';
    const consoleMethod = console[level] || console.log;
    consoleMethod(prefix, ...args);
}

// 便捷方法
debug(...args) { this.log('debug', ...args); }  // 仅DEBUG模式
info(...args)  { this.log('info', ...args); }   // 始终显示
warn(...args)  { this.log('warn', ...args); }   // 始终显示
error(...args) { this.log('error', ...args); }  // 始终显示
```

**使用示例**：
```javascript
this.debug('详细调试信息');     // 仅开发环境
this.info('用户点击了按钮');    // 重要信息
this.warn('配置缺失，使用默认值'); // 警告
this.error('API调用失败:', err);  // 错误
```

**收益**：
- 生产环境自动隐藏debug日志
- 控制台输出更清晰
- 方便调试和问题排查

---

#### 7. 文档预览统一

**识别信号**：
- 多个模块重复实现Word/PDF预览逻辑（70+行）
- 手动创建模态框、fetch文档、渲染

**重构方案**：
```javascript
// ❌ 旧代码：70行手动预览
fetch(downloadUrl)
    .then(response => response.arrayBuffer())
    .then(arrayBuffer => {
        // 创建模态框...
        // 解析Word文档...
        // 渲染到DOM...
        // 70行代码...
    });

// ✅ 新代码：2行调用
window.documentPreviewUtil.preview(downloadUrl, filename);
```

**DocumentPreviewUtil 支持**：
- ✅ Word文档 (.docx) - 使用 docx-preview.js
- ✅ PDF文档 (.pdf) - 内嵌iframe
- ✅ 图片 (.png, .jpg, .gif)
- ✅ 自动模态框管理
- ✅ 加载状态提示

**收益**：
- 减少70行重复代码
- 统一预览样式
- 自动错误处理

---

### 重构检查清单

优化JavaScript/CSS文件前，使用此清单识别重构机会：

#### JavaScript重构信号

- [ ] **70+行SSE流处理代码** → 使用 `window.SSEClient`
- [ ] **40+行fetch错误处理** → 使用 `window.apiClient`
- [ ] **50+行硬编码UI生成** → 配置驱动模式
- [ ] **大量 `if (element)` 空值检查** → DOM辅助方法
- [ ] **`console.log` 满天飞** → 日志分级系统
- [ ] **全局变量污染** (`window.xxx`) → `window.globalState`
- [ ] **重复的文档预览逻辑** → `window.documentPreviewUtil`
- [ ] **文件大于1000行** → 考虑拆分模块

#### CSS重构信号

- [ ] **重复的颜色值**（如 `#4a89dc` 出现10+次） → CSS变量
- [ ] **深度嵌套**（4+层选择器） → 组件化拆分
- [ ] **魔术数字**（`padding: 18px`） → 使用 `var(--spacing-lg)`
- [ ] **重复的样式块** → 提取为组件或工具类
- [ ] **未使用压缩版本** → 生成 `.min.css`

#### 优化优先级矩阵

| 模式 | 代码减少 | 可复用性 | 难度 | 优先级 |
|------|----------|----------|------|--------|
| API调用统一 | 82% | 极高 | 低 | **P0** ⭐⭐⭐ |
| SSE流式处理 | 97% | 高 | 中 | **P1** ⭐⭐ |
| 全局状态管理 | 40% | 极高 | 中 | **P1** ⭐⭐ |
| 配置驱动UI | 50% | 中 | 低 | **P2** ⭐ |
| DOM辅助方法 | 60% | 中 | 低 | **P3** |
| 日志分级 | 10% | 低 | 低 | **P3** |
| 文档预览统一 | 97% | 高 | 低 | **P2** ⭐ |

**优化目标**：
- 每次重构至少减少 **20%代码量** 或提升 **50%可复用性**
- 优先处理 P0/P1 级别的重构机会
- 保持向后兼容至少一个版本周期

---

### 性能优化策略

#### 动态资源加载（基于utils/css-loader.js）

**CSS懒加载**：
```javascript
// 标签页切换时动态加载CSS
const cssMap = {
    'knowledge-company-library': ['qualifications.min.css'],
    'knowledge-case-library': ['case-library.min.css'],
    'tender-management': ['tender-processing-hitl.min.css']
};

// navigation-manager.js中触发
tabLink.addEventListener('shown.bs.tab', (event) => {
    const tabId = event.target.getAttribute('data-bs-target').replace('#', '');
    if (window.loadCSSForTab) {
        window.loadCSSForTab(tabId);
    }
});
```

**收益**：
- 首屏加载时间减少40%
- 按需加载，节省带宽
- 改善Core Web Vitals (FCP/LCP)

---

#### 代码分割与压缩

**分割策略**：
```
# 核心JS（index.html首屏加载）
global-state-manager.js
api-client.js
notification.js

# 按需加载（defer或动态import）
pages/knowledge-base/*.js
pages/tender-processing-step3/*.js
```

**压缩策略**：
```bash
# CSS压缩（生产环境）
buttons.css → buttons.min.css (-30%)
cards.css → cards.min.css (-20%)

# 使用压缩版本
<link href="/static/css/components/buttons.min.css">
```

**文件大小目标**：
- 单个JS文件 < 100KB（压缩前< 500行）
- 单个CSS文件 < 50KB
- 首屏JS总量 < 300KB

---

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
