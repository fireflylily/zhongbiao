# 简历库管理模块拆分说明

## 📁 模块结构

```
modules/resume/
├── README.md                      - 本文档
├── ResumeBatchExporter.js         - ✅ 已完成：批量导出器
├── ResumeAttachmentManager.js     - ⏳ 待创建：附件管理器
├── ResumeExperienceManager.js     - ⏳ 待创建：经历管理器
├── ResumeParser.js                - ⏳ 待创建：智能解析上传
└── ResumeDetailManager.js         - ⏳ 待创建：详情页管理器
```

## ✅ 已完成模块

### 1. ResumeBatchExporter（批量导出器）
**文件**: `ResumeBatchExporter.js` (~170行)

**功能**:
- 批量导出模态框
- 导出选项配置
- 执行导出

**使用示例**:
```javascript
// 在主管理器中注入
this.batchExporter = new ResumeBatchExporter(this);

// 调用导出功能
this.batchExporter.showBatchExportModal();
```

**API集成**:
- ✅ 使用 `window.apiClient.post()` 替代原生fetch
- ✅ 使用 `window.notifications` 替代alert

---

## ⏳ 待完成模块

### 2. ResumeAttachmentManager（附件管理器）
**预计行数**: ~200行

**主要功能**:
- 加载附件列表
- 渲染附件列表
- 上传附件（支持多文件）
- 删除附件
- 下载附件
- 文件图标识别
- 附件类型标签

**复用CSS**:
- `form-common.css` - `.case-attachment-*` 样式

**参考实现**:
- `case-library-manager.js` (1090-1333行)
- 原 `resume-library-manager.js` (1547-1750行)

---

### 3. ResumeExperienceManager（经历管理器）
**预计行数**: ~400行

**主要功能**:
- 工作经历管理（CRUD）
- 项目经历管理（CRUD）
- 经历模态框
- JSON数据解析和存储

**优化点**:
- 工作经历和项目经历逻辑高度相似
- 可抽象为通用的 `ExperienceHandler` + 配置驱动

**原代码位置**:
- 工作经历：`resume-library-manager.js` (1753-1943行)
- 项目经历：`resume-library-manager.js` (1946-2136行)

---

### 4. ResumeParser（智能解析上传器）
**预计行数**: ~300行

**主要功能**:
- 智能解析模态框
- 原生文件上传（拖拽+点击）
- 文件验证
- 上传进度显示
- 解析结果填充
- 保存解析的简历

**原代码位置**:
- `showParseResumeModal()` (306-446行)
- `initResumeUploader()` (451-511行)
- 上传解析逻辑 (539-659行)

---

### 5. ResumeDetailManager（详情页管理器）
**预计行数**: ~350行

**主要功能**:
- 详情/编辑视图渲染
- 加载简历数据
- 保存简历
- 基本信息表单处理
- 协调附件和经历管理器

**复用CSS**:
- `form-common.css` - `.case-edit-header`, `.case-form-section`
- `resume-library.css` - 简历特定样式

**原代码位置**:
- `renderResumeDetailView()` (1153-1415行)
- `loadResumeData()` (1427-1480行)
- `saveResume()` (1485-1544行)

---

## 🔄 主管理器重构

### 重构后的 ResumeLibraryManager
**预计行数**: ~700行

**保留功能**:
- 初始化和状态管理
- 列表视图渲染
- 加载简历列表
- 搜索和筛选
- 分页
- 批量选择
- 统计信息更新
- 工具方法（通知、HTML转义）

**注入子模块**:
```javascript
constructor() {
    // ... 原有初始化代码 ...

    // 注入子模块
    this.batchExporter = new ResumeBatchExporter(this);
    this.attachmentManager = new ResumeAttachmentManager(this);
    this.experienceManager = new ResumeExperienceManager(this);
    this.parser = new ResumeParser(this);
    this.detailManager = new ResumeDetailManager(this);
}
```

---

## 🎯 使用的工具和库

### 核心工具（已集成）
1. ✅ **window.notifications** - 统一通知系统
   - `success()`, `error()`, `warning()`, `info()`

2. ✅ **window.apiClient** - 统一API客户端
   - 自动重试3次
   - 统一错误处理

3. ✅ **window.globalState** - 状态管理
   - `getCompany()`, `getProject()`

### 辅助工具（按需使用）
4. ✅ **window.documentPreviewUtil** - 文档预览
5. ⚠️ **UniversalUploader** - 通用上传组件（暂不使用）

---

## 📦 文件加载顺序

在HTML中按以下顺序加载：

```html
<!-- 核心工具（已有） -->
<script src="/static/js/core/notification.js"></script>
<script src="/static/js/core/api-client.js"></script>
<script src="/static/js/core/global-state-manager.js"></script>
<script src="/static/js/utils/document-preview.js"></script>

<!-- 简历库子模块 -->
<script src="/static/js/pages/knowledge-base/modules/resume/ResumeBatchExporter.js"></script>
<script src="/static/js/pages/knowledge-base/modules/resume/ResumeAttachmentManager.js"></script>
<script src="/static/js/pages/knowledge-base/modules/resume/ResumeExperienceManager.js"></script>
<script src="/static/js/pages/knowledge-base/modules/resume/ResumeParser.js"></script>
<script src="/static/js/pages/knowledge-base/modules/resume/ResumeDetailManager.js"></script>

<!-- 主管理器（最后加载） -->
<script src="/static/js/pages/knowledge-base/resume-library-manager.js"></script>
```

---

## 🚀 后续步骤

1. ✅ ~~创建 `ResumeBatchExporter.js`~~
2. ⏳ 创建 `ResumeAttachmentManager.js`
3. ⏳ 创建 `ResumeExperienceManager.js`
4. ⏳ 创建 `ResumeParser.js`
5. ⏳ 创建 `ResumeDetailManager.js`
6. ⏳ 重构主管理器，注入子模块
7. ⏳ 全局替换 `alert()` → `window.notifications`
8. ⏳ 全局替换 `fetch()` → `window.apiClient`
9. ⏳ 更新HTML文件加载顺序
10. ⏳ 测试所有功能

---

## 📝 开发注意事项

1. **命名空间**: 所有类都挂载到 `window` 对象
2. **依赖注入**: 通过构造函数注入主管理器实例
3. **向后兼容**: 保持全局 `window.resumeLibraryManager` 实例
4. **CSS复用**: 详情页直接使用 `.case-*` 类名
5. **错误处理**: 统一使用 `window.notifications.error()`
6. **模块通信**: 通过主管理器实例进行模块间通信

---

## 📊 进度跟踪

- [x] 创建模块目录
- [x] 创建 ResumeBatchExporter (1/5)
- [ ] 创建 ResumeAttachmentManager (0/5)
- [ ] 创建 ResumeExperienceManager (0/5)
- [ ] 创建 ResumeParser (0/5)
- [ ] 创建 ResumeDetailManager (0/5)
- [ ] 重构主管理器 (0/1)
- [ ] 统一通知和API (0/1)
- [ ] 测试验证 (0/1)

**总进度**: 1/9 (11%)

---

最后更新：2025-10-25
