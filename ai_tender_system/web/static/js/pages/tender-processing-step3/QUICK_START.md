# 快速开始 - tender-processing-step3 模块化版本

**版本**: 1.0.0
**状态**: ✅ Phase 2 已完成

---

## 📦 安装

### 方式1: 完整加载（推荐）

在HTML页面中按顺序加载所有依赖:

```html
<!DOCTYPE html>
<html>
<head>
    <title>标书处理 Step 3</title>
</head>
<body>
    <!-- 1. 核心工具 (必须) -->
    <script src="/static/js/core/notification.js"></script>
    <script src="/static/js/core/validation.js"></script>
    <script src="/static/js/core/api-client.js"></script>
    <script src="/static/js/core/global-state-manager.js"></script>
    <script src="/static/js/components/modal-manager.js"></script>

    <!-- 2. Step3 API扩展 (必须) -->
    <script src="/static/js/pages/tender-processing-step3/api/tender-api-extension.js"></script>

    <!-- 3. Step3 工具和配置 (可选) -->
    <script src="/static/js/pages/tender-processing-step3/utils/formatter.js"></script>
    <script src="/static/js/pages/tender-processing-step3/config/eligibility-checklist.js"></script>

    <!-- 4. Step3 管理器 (必须) -->
    <script src="/static/js/pages/tender-processing-step3/managers/ChapterSelectorManager.js"></script>
    <script src="/static/js/pages/tender-processing-step3/managers/DataSyncManager.js"></script>
    <script src="/static/js/pages/tender-processing-step3/managers/RequirementsTableManager.js"></script>

    <!-- 5. Step3 主入口 (必须) -->
    <script src="/static/js/pages/tender-processing-step3/index.js"></script>

    <!-- 你的页面内容 -->
    <script>
        // 检测加载状态
        window.addEventListener('step3ModularLoaded', (e) => {
            console.log('✅ Step3模块化版本已加载');
            console.log('版本:', e.detail.version);
        });
    </script>
</body>
</html>
```

### 方式2: 与原版共存

如果你需要逐步迁移，可以同时加载模块化版本和原版:

```html
<!-- 模块化版本 -->
<script src="/static/js/pages/tender-processing-step3/index.js"></script>

<!-- 原版（用于未迁移的功能） -->
<script src="/static/js/pages/tender-processing-step3-enhanced.js"></script>

<script>
    // 检测哪个版本可用
    if (window.STEP3_MODULAR_LOADED) {
        console.log('使用模块化版本');
    } else {
        console.log('使用原版');
    }
</script>
```

---

## 🚀 基本用法

### 1. 保存基本信息

```javascript
// 方式1: 使用管理器（推荐）
const result = await window.dataSyncManager.saveBasicInfo();
if (result.success) {
    console.log('保存成功，项目ID:', result.projectId);
} else {
    console.error('保存失败:', result.message);
}

// 方式2: 使用向后兼容函数
await saveBasicInfo();
```

### 2. 章节选择

```javascript
// 显示章节选择器
await showChapterSelection('response'); // 应答文件
// 或
await showChapterSelection('technical'); // 技术需求

// 批量操作
selectAll('response');           // 全选
unselectAll('response');         // 全不选
selectByKeyword('response', '技术'); // 选择包含"技术"的章节
excludeByKeyword('response', '评分'); // 排除包含"评分"的章节

// 确认保存
await confirmSave('response');
```

### 3. 需求表格管理

```javascript
// 设置需求数据
window.requirementsTableManager.setRequirements(requirements);

// 应用过滤器
window.requirementsTableManager.applyFilters({
    constraint_type: 'mandatory',  // 强制性
    category: 'technical',         // 技术类
    priority: 'high',              // 高优先级
    search: '关键词'                // 搜索
});

// 导出数据
window.requirementsTableManager.exportRequirements('csv');  // CSV格式
window.requirementsTableManager.exportRequirements('json'); // JSON格式

// 清除过滤器
window.requirementsTableManager.clearFilters();
```

### 4. 保存并完成

```javascript
// 自动收集所有数据并保存
const result = await window.dataSyncManager.saveAndComplete();
if (result.success) {
    console.log('所有数据已保存');
} else {
    console.error('保存失败:', result.message);
}
```

---

## 🔧 高级用法

### 1. 自定义章节选择器

```javascript
// 创建自定义配置的章节选择器
const selector = new ChapterSelectorManager('response', {
    prefix: 'my-custom',
    contentId: 'myContentArea',
    selectionAreaId: 'mySelectionArea',
    confirmBtnId: 'myConfirmBtn',
    fileTypeName: '自定义文件',
    apiSave: '/api/my-custom-save',
    apiInfo: '/api/my-custom-info'
});

// 显示章节选择
await selector.showChapterSelection(taskId, chaptersData);

// 获取选中的章节ID
const selectedIds = selector.getSelectedIds();
console.log('选中章节:', selectedIds);

// 编程式设置选中
selector.setSelectedIds([1, 2, 3]);
```

### 2. 监听事件

```javascript
// 监听文件信息更新
window.addEventListener('fileInfoUpdated', (e) => {
    console.log('文件已更新:', e.detail.type, e.detail.taskId);
    // 刷新UI或执行其他操作
});

// 监听需求编辑请求
window.addEventListener('requirementEditRequested', (e) => {
    const requirement = e.detail.requirement;
    // 打开编辑模态框
    showEditModal(requirement);
});

// 监听需求删除请求
window.addEventListener('requirementDeleteRequested', async (e) => {
    const reqId = e.detail.requirementId;
    // 调用删除API
    await deleteRequirement(reqId);
});

// 监听章节预览请求
window.addEventListener('chapterPreviewRequested', (e) => {
    const chapterId = e.detail.chapterId;
    // 显示预览模态框
    showChapterPreview(chapterId);
});
```

### 3. 自定义数据收集

```javascript
// 单独收集某类数据
const qualifications = await window.dataSyncManager.collectQualificationsData();
const technical = await window.dataSyncManager.collectTechnicalData();
const scoring = await window.dataSyncManager.collectScoringData();

console.log('资格要求:', Object.keys(qualifications).length);
console.log('技术需求:', Object.keys(technical).length);
console.log('评分办法:', Object.keys(scoring).length);
```

### 4. 表格高级过滤

```javascript
const manager = window.requirementsTableManager;

// 链式过滤
manager
    .applyFilters({ constraint_type: 'mandatory' })
    .applyFilters({ category: 'technical' });

// 动态搜索
document.getElementById('searchInput').addEventListener('input', (e) => {
    manager.applyFilters({ search: e.target.value });
});

// 获取当前过滤条件
console.log('当前过滤器:', manager.currentFilters);

// 获取过滤后的数据
console.log('过滤后的需求:', manager.filteredRequirements);
```

---

## 🎯 常见场景

### 场景1: 创建新项目并保存章节

```javascript
// 1. 保存基本信息（创建项目）
const basicInfoResult = await window.dataSyncManager.saveBasicInfo({
    project_name: '新项目',
    project_number: 'P2025001',
    company_id: 'company_123'
});

if (!basicInfoResult.success) {
    alert('创建项目失败');
    return;
}

// 2. 显示章节选择
await showChapterSelection('response');

// 3. 选择章节（用户交互）
// ...

// 4. 保存选中章节
await confirmSave('response');

// 5. 完成并保存所有数据
await window.dataSyncManager.saveAndComplete();
```

### 场景2: 加载已有项目并编辑

```javascript
// 1. 加载项目数据
const projectId = 'project_123';
const projectData = await loadProjectData(projectId);

// 2. 填充表单
document.getElementById('projectName').value = projectData.project_name;
// ... 其他字段

// 3. 加载需求数据
const requirements = await loadRequirements(projectId);
window.requirementsTableManager.setRequirements(requirements);

// 4. 应用过滤器（显示特定类型）
window.requirementsTableManager.applyFilters({
    category: 'qualification'
});

// 5. 编辑后保存
await window.dataSyncManager.saveBasicInfo();
```

### 场景3: 批量导出需求

```javascript
// 导出所有需求为CSV
window.requirementsTableManager.clearFilters();
window.requirementsTableManager.exportRequirements('csv');

// 导出仅强制性需求为JSON
window.requirementsTableManager.applyFilters({
    constraint_type: 'mandatory'
});
window.requirementsTableManager.exportRequirements('json');
```

---

## 🐛 故障排查

### 问题1: 依赖未加载

**症状**: 控制台报错 `❌ 缺少必要依赖`

**解决**:
1. 检查HTML中是否按顺序加载了所有依赖
2. 确保核心工具（notification/validation/api-client）已加载
3. 检查浏览器Network面板，确认文件路径正确

### 问题2: 章节选择器无法显示

**症状**: 调用 `showChapterSelection()` 后无反应

**解决**:
1. 检查DOM元素是否存在（`contentId`, `selectionAreaId`）
2. 确认任务ID是否正确
3. 检查API `/api/tender-processing/chapters/{taskId}` 是否返回数据
4. 查看控制台日志排查错误

### 问题3: 数据保存失败

**症状**: `saveBasicInfo()` 返回 `success: false`

**解决**:
1. 确认公司ID是否已设置
2. 检查API `/api/tender-projects` 是否正常
3. 验证表单字段值是否有效
4. 查看Network面板检查请求/响应

### 问题4: 表格不显示数据

**症状**: `setRequirements()` 后表格仍为空

**解决**:
1. 确认 `requirements` 数组不为空
2. 检查 `tableBodyId` 是否正确（默认: `requirementsTableBody`）
3. 验证过滤器是否过于严格
4. 尝试调用 `clearFilters()` 后重新加载

---

## 📚 API参考

### DataSyncManager

```javascript
class DataSyncManager {
    // 保存基本信息
    async saveBasicInfo(basicInfo?, projectId?)
    // 返回: { success, projectId, message }

    // 保存并完成
    async saveAndComplete()
    // 返回: { success, message }

    // 收集资格要求
    async collectQualificationsData()
    // 返回: Object

    // 收集技术需求
    async collectTechnicalData()
    // 返回: Object

    // 收集评分办法
    async collectScoringData()
    // 返回: Object
}
```

### ChapterSelectorManager

```javascript
class ChapterSelectorManager {
    constructor(type, config)

    // 显示章节选择
    async showChapterSelection(taskId?, chaptersData?)

    // 隐藏章节选择
    hideChapterSelection()

    // 渲染章节树
    renderChapterTree()

    // 更新统计
    updateStatistics()

    // 批量操作
    selectAll()
    unselectAll()
    selectByKeyword(keyword)
    excludeByKeyword(keyword)

    // 保存
    async confirmSave()

    // 获取/设置选中ID
    getSelectedIds(): Array
    setSelectedIds(ids: Array)
}
```

### RequirementsTableManager

```javascript
class RequirementsTableManager {
    constructor(tableBodyId, options)

    // 设置数据
    setRequirements(requirements)

    // 应用过滤器
    applyFilters(filters)

    // 渲染表格
    render()

    // 更新统计
    updateStats()

    // 编辑/删除
    editRequirement(requirementId)
    deleteRequirement(requirementId)

    // 导出
    exportRequirements(format) // 'csv' | 'json'

    // 清除过滤器
    clearFilters()
}
```

---

## 🔗 相关文档

- [README.md](./README.md) - 完整文档
- [PHASE2_COMPLETION_SUMMARY.md](../../../../../PHASE2_COMPLETION_SUMMARY.md) - 完成总结
- [CLAUDE.md](../../../../../CLAUDE.md) - 项目架构

---

## 💡 提示

1. **优先使用模块化版本**: 新功能应优先使用模块化管理器
2. **向后兼容**: 旧代码中的全局函数调用仍然有效
3. **事件驱动**: 使用事件监听解耦组件
4. **错误处理**: 始终检查API返回的 `success` 字段
5. **日志调试**: 控制台会输出详细的调试日志

---

**最后更新**: 2025-10-25
**维护者**: Claude Code
