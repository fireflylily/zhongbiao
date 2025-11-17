# 文档融合功能实施总结

## 📋 概述

本文档记录了**产品融合(文档融合)**功能的完整实施过程,包括后端API、前端UI集成和测试验证。

## ✅ 已完成的工作

### 1. 后端实现

#### 1.1 创建文档融合服务模块

**文件**: `ai_tender_system/modules/document_merger/merger_service.py`

**功能**:
- 合并商务应答、点对点应答和技术方案三个Word文档
- 支持两种样式选项:
  - `business_style`: 保留商务应答文件的原有格式
  - `standard_style`: 使用标准样式(全文仿宋、1.5倍行距等)
- 自动生成目录和索引
- 跟踪合并进度并更新数据库

**核心方法**:
```python
def merge_documents(
    business_doc_path: str,
    p2p_doc_path: str,
    tech_doc_path: str,
    output_path: str,
    style_option: str = 'business_style',
    task_id: str = None
) -> Dict[str, Any]
```

#### 1.2 创建API蓝图

**文件**: `ai_tender_system/web/blueprints/document_merger_api.py`

**端点**:

1. **启动文档融合任务** - `POST /api/projects/<int:project_id>/merge-documents`
   ```json
   {
     "business_doc_path": "/path/to/business.docx",
     "p2p_doc_path": "/path/to/p2p.docx",
     "tech_doc_path": "/path/to/tech.docx",
     "style_option": "business_style"
   }
   ```

   响应:
   ```json
   {
     "message": "Merge task started",
     "task_id": "uuid-string"
   }
   ```

2. **获取项目源文档信息** - `GET /api/projects/<int:project_id>/source-documents`

   响应:
   ```json
   {
     "success": true,
     "data": {
       "project_name": "项目名称",
       "company_name": "公司名称",
       "business_doc_path": "/path/to/business.docx",
       "p2p_doc_path": "/path/to/p2p.docx",
       "tech_doc_path": "/path/to/tech.docx"
     }
   }
   ```

3. **SSE流式获取融合进度** - `GET /api/merge-status/<task_id>`

   SSE事件格式:
   ```json
   {
     "task_id": "uuid-string",
     "overall_status": "running",
     "current_step": "正在合并文档...",
     "progress_percentage": 50,
     "merged_document_path": null,
     "index_file_path": null
   }
   ```

#### 1.3 蓝图注册

**文件**: `ai_tender_system/web/blueprints/__init__.py`

在 `register_all_blueprints()` 函数中添加:
```python
try:
    from .document_merger_api import document_merger_api_bp
    app.register_blueprint(document_merger_api_bp)
    logger.info("文档融合API蓝图注册成功")
except ImportError as e:
    logger.warning(f"文档融合API蓝图加载失败: {e}")
```

### 2. 前端实现

#### 2.1 创建文档融合处理器

**文件**: `ai_tender_system/web/static/js/pages/index/document-merger-handler.js`

**类**: `DocumentMergerHandler`

**功能**:
- 显示项目和公司信息
- 加载并显示源文档(商务/点对点/技术)
- 提供文档预览功能
- 启动文档融合任务
- 使用SSE实时监控融合进度
- 显示融合结果和下载链接

**核心方法**:
```javascript
class DocumentMergerHandler {
    constructor(projectId, projectName, companyName)
    init()
    displayProjectInfo()
    fetchSourceFiles()
    renderSourceFiles()
    handleConfirmMerge()
    startMergeProgressStream(taskId)
    updateMergeProgressUI(data)
}
```

#### 2.2 集成到页面

**文件**: `ai_tender_system/web/templates/tender_processing.html`

**修改内容**:

1. **导入依赖脚本** (第639-647行):
```html
<!-- 核心工具类 -->
<script src="/static/js/core/global-state-manager.js"></script>
<script src="/static/js/core/api-client.js"></script>
<script src="/static/js/core/notification.js"></script>
<script src="/static/js/utils/sse-client.js"></script>
<script src="/static/js/utils/document-preview.js"></script>

<!-- 文档融合处理器 -->
<script src="/static/js/pages/index/document-merger-handler.js"></script>
```

2. **页面加载时初始化** (第1253-1301行):
```javascript
document.addEventListener('DOMContentLoaded', async function() {
    const urlParams = new URLSearchParams(window.location.search);
    const projectIdFromUrl = urlParams.get('project_id');

    if (projectIdFromUrl) {
        currentProjectId = parseInt(projectIdFromUrl);

        // 获取项目信息并初始化文档融合处理器
        const response = await window.apiClient.get(
            `/api/projects/${projectIdFromUrl}/source-documents`
        );

        if (response.success && response.data) {
            documentMergerHandler = new DocumentMergerHandler(
                parseInt(projectIdFromUrl),
                response.data.project_name,
                response.data.company_name
            );
        }
    }
});
```

3. **UI组件** (已存在于模板中):
   - 项目信息展示区 (第337-346行)
   - 源文档展示和预览 (第349-380行)
   - 融合按钮和样式选择模态框 (第376-631行)
   - 融合进度步骤指示器 (第461-468行)

### 3. 测试验证

#### 3.1 后端API测试

**测试脚本**: `tmp_scripts/test_document_merger.py`

**测试结果**:
- ✅ `/api/projects/8/source-documents` - 200 OK
  ```json
  {
    "data": {
      "project_name": "中国联通手机信息核验类外部数据服务采购项目",
      "company_name": "中国联合网络通信有限公司",
      "business_doc_path": null,
      "p2p_doc_path": null,
      "tech_doc_path": null
    },
    "success": true
  }
  ```

- ✅ 蓝图注册成功 - 应用启动日志显示:
  ```
  2025-10-30 09:40:09,801 - ai_tender_system.web_app - INFO - 文档融合API蓝图注册成功
  ```

#### 3.2 前端集成测试

**测试方式**:
1. 启动应用: `http://localhost:8110`
2. 访问页面: `http://localhost:8110/tender-processing?project_id=8`
3. 验证功能:
   - ✅ 项目信息正确显示
   - ✅ DocumentMergerHandler 正确初始化
   - ✅ 源文档信息加载
   - ✅ 融合按钮和模态框显示
   - ✅ 进度监控UI准备就绪

## 🔧 技术栈

- **后端**:
  - Flask Blueprint
  - threading (异步任务处理)
  - SQLite (任务状态存储)
  - SSE (Server-Sent Events 实时进度推送)

- **前端**:
  - 原生JavaScript (ES6+)
  - Bootstrap 5 (UI组件)
  - SSEClient (流式数据处理)
  - DocumentPreviewUtil (文档预览)
  - ApiClient (统一API调用)
  - GlobalStateManager (状态管理)

## 📂 文件结构

```
ai_tender_system/
├── modules/
│   └── document_merger/
│       ├── __init__.py
│       └── merger_service.py          # 文档融合核心服务
│
├── web/
│   ├── blueprints/
│   │   ├── __init__.py               # 蓝图注册 (新增注册代码)
│   │   └── document_merger_api.py    # 文档融合API蓝图
│   │
│   ├── static/js/pages/index/
│   │   └── document-merger-handler.js # 文档融合前端处理器
│   │
│   └── templates/
│       └── tender_processing.html     # 集成文档融合UI
│
└── tmp_scripts/
    └── test_document_merger.py        # API测试脚本
```

## 🎯 核心功能流程

### 用户操作流程

1. **访问页面**
   ```
   用户访问: /tender-processing?project_id=8
   ```

2. **页面加载**
   ```
   DOMContentLoaded → 初始化 DocumentMergerHandler
                   → 调用 /api/projects/8/source-documents
                   → 显示项目信息和源文档
   ```

3. **启动融合**
   ```
   用户点击"融合文件" → 显示样式选择模态框
                      → 用户选择样式
                      → 点击"确认融合"
   ```

4. **执行融合**
   ```
   前端: POST /api/projects/8/merge-documents
         { business_doc_path, p2p_doc_path, tech_doc_path, style_option }

   后端: 创建任务 → 启动后台线程
                 → 返回 task_id
   ```

5. **监控进度**
   ```
   前端: SSE连接 /api/merge-status/task_id
         → 实时接收进度更新
         → 更新UI进度条

   后端: 持续推送任务状态
         → 完成后推送最终结果
   ```

6. **完成下载**
   ```
   融合完成 → 显示下载链接
           → 用户下载融合文档和索引文件
   ```

### 数据流转

```
用户界面
   ↓ (选择项目)
DocumentMergerHandler
   ↓ (GET /api/projects/8/source-documents)
document_merger_api.py
   ↓ (查询数据库)
tender_projects + tender_processing_tasks
   ↓ (返回项目信息和文档路径)
DocumentMergerHandler
   ↓ (显示源文档)
用户界面
   ↓ (点击融合)
DocumentMergerHandler
   ↓ (POST /api/projects/8/merge-documents)
document_merger_api.py
   ↓ (创建后台任务)
threading.Thread → merger_service.merge_documents()
   ↓ (更新任务状态)
tender_processing_tasks (数据库)
   ↓ (SSE推送进度)
DocumentMergerHandler
   ↓ (更新UI)
用户界面
```

## 🚀 下一步工作

### 1. 实现真实的文档融合逻辑

目前 `merger_service.py` 使用占位逻辑(仅等待5秒),需要实现:

- [ ] 使用 `python-docx` 库读取三个Word文档
- [ ] 按顺序合并内容到新文档
- [ ] 应用选定的样式(business_style 或 standard_style)
- [ ] 生成目录
- [ ] 创建索引文件
- [ ] 保存到 `ai_tender_system/data/outputs/` 目录

**参考代码框架**:
```python
from docx import Document

def merge_documents(business_doc_path, p2p_doc_path, tech_doc_path,
                   output_path, style_option='business_style', task_id=None):
    db = get_knowledge_base_db()

    try:
        # 更新状态: 开始合并
        db.update_task_status(task_id, 'running', '正在读取文档...')

        # 读取文档
        business_doc = Document(business_doc_path)
        p2p_doc = Document(p2p_doc_path)
        tech_doc = Document(tech_doc_path)

        # 创建新文档
        merged_doc = Document()

        # 合并内容
        db.update_task_status(task_id, 'running', '正在合并内容...',
                             progress=30)

        # 1. 添加商务应答内容
        for element in business_doc.element.body:
            merged_doc.element.body.append(element)

        # 2. 添加点对点应答内容
        for element in p2p_doc.element.body:
            merged_doc.element.body.append(element)

        # 3. 添加技术方案内容
        for element in tech_doc.element.body:
            merged_doc.element.body.append(element)

        # 应用样式
        db.update_task_status(task_id, 'running', '正在应用样式...',
                             progress=60)
        if style_option == 'standard_style':
            apply_standard_style(merged_doc)

        # 生成目录
        db.update_task_status(task_id, 'running', '正在生成目录...',
                             progress=80)
        generate_table_of_contents(merged_doc)

        # 保存文档
        merged_doc.save(output_path)

        # 生成索引
        index_path = output_path.replace('.docx', '_index.json')
        generate_index(merged_doc, index_path)

        # 完成
        db.update_task_status(task_id, 'completed', '合并完成',
                             options={
                                 'merged_document_path': output_path,
                                 'index_file_path': index_path
                             })

        return {'success': True, 'output_path': output_path}

    except Exception as e:
        logger.error(f"文档融合失败: {e}", exc_info=True)
        db.update_task_status(task_id, 'failed', str(e))
        return {'success': False, 'error': str(e)}
```

### 2. 优化前端体验

- [ ] 添加文档预览缩略图
- [ ] 实现拖拽排序(调整文档合并顺序)
- [ ] 添加更多样式选项
- [ ] 显示文档大小、页数等元信息
- [ ] 支持部分文档融合(只选择部分文档)

### 3. 错误处理增强

- [ ] 处理文件不存在的情况
- [ ] 处理文档格式不兼容
- [ ] 添加重试机制
- [ ] 提供详细的错误信息

### 4. 性能优化

- [ ] 大文档处理时的进度细粒度更新
- [ ] 使用Celery替代threading进行任务调度
- [ ] 添加任务队列和并发控制
- [ ] 实现任务取消功能

## 📝 使用示例

### 前端调用示例

```javascript
// 初始化处理器
const handler = new DocumentMergerHandler(
    8,  // projectId
    "中国联通手机信息核验类外部数据服务采购项目",  // projectName
    "中国联合网络通信有限公司"  // companyName
);

// 处理器会自动:
// 1. 显示项目信息
// 2. 加载源文档列表
// 3. 绑定融合按钮事件
// 4. 监控融合进度
```

### 后端API调用示例

```python
import requests

# 启动融合任务
response = requests.post(
    'http://localhost:8110/api/projects/8/merge-documents',
    json={
        'business_doc_path': '/path/to/business.docx',
        'p2p_doc_path': '/path/to/p2p.docx',
        'tech_doc_path': '/path/to/tech.docx',
        'style_option': 'business_style'
    }
)

task_id = response.json()['task_id']

# 监控进度 (SSE)
import sseclient

sse = sseclient.SSEClient(f'http://localhost:8110/api/merge-status/{task_id}')
for event in sse:
    data = json.loads(event.data)
    print(f"状态: {data['overall_status']}, 步骤: {data['current_step']}")
    if data['overall_status'] in ['completed', 'failed']:
        break
```

## 🐛 已知问题

1. **占位逻辑**: 当前 `merger_service.py` 仅使用 `time.sleep(5)` 模拟合并,需要实现真实逻辑
2. **文档路径**: 项目8的源文档路径为null,需要先生成商务应答、点对点应答和技术方案
3. **Celery未配置**: 当前使用 `threading.Thread`,生产环境建议使用Celery

## 📚 参考资料

- [Flask Blueprint文档](https://flask.palletsprojects.com/en/2.3.x/blueprints/)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [python-docx文档](https://python-docx.readthedocs.io/)
- [项目CLAUDE.md架构指南](./CLAUDE.md)

## 📅 时间线

- **2025-10-29**: 创建后端API和前端handler
- **2025-10-30**: 完成前端集成和测试验证
- **待定**: 实现真实文档融合逻辑

---

**状态**: ✅ 前端集成完成,后端API就绪,等待实现真实文档融合逻辑

**负责人**: Claude Code

**最后更新**: 2025-10-30
