# 全局状态管理重构方案

## 一、架构设计

### 1. 统一状态管理器（GlobalStateManager）

```javascript
/**
 * 全局状态管理器 - 单一数据源
 * 管理所有跨页面共享的状态
 */
class GlobalStateManager {
    constructor() {
        this.state = {
            // 公司信息
            company: {
                id: null,
                name: null
            },

            // 项目信息
            project: {
                id: null,
                name: null
            },

            // HITL任务信息
            hitl: {
                taskId: null
            },

            // 文件管理（按类型分类）
            files: {
                originalTender: null,      // 原始招标文件
                technical: null,           // 技术需求文件
                business: null,            // 商务应答文件
                pointToPoint: null,        // 点对点应答文件
                techProposal: null         // 技术方案文件
            },

            // AI配置
            ai: {
                availableModels: [],       // 所有可用模型
                selectedModel: 'unicom-yuanjing'  // 当前选中模型
            }
        };

        // 监听器列表（观察者模式）
        this.listeners = {
            company: [],
            project: [],
            files: [],
            ai: []
        };
    }

    // ========================================
    // 公司管理
    // ========================================

    setCompany(companyId, companyName) {
        this.state.company.id = companyId;
        this.state.company.name = companyName;
        this.notify('company', this.state.company);
        console.log('[GlobalState] 公司信息已更新:', this.state.company);
    }

    getCompany() {
        return { ...this.state.company };
    }

    clearCompany() {
        this.state.company.id = null;
        this.state.company.name = null;
        this.notify('company', this.state.company);
    }

    // ========================================
    // 项目管理
    // ========================================

    setProject(projectId, projectName) {
        this.state.project.id = projectId;
        this.state.project.name = projectName;
        this.notify('project', this.state.project);
        console.log('[GlobalState] 项目信息已更新:', this.state.project);
    }

    getProject() {
        return { ...this.state.project };
    }

    clearProject() {
        this.state.project.id = null;
        this.state.project.name = null;
        this.notify('project', this.state.project);
    }

    // ========================================
    // 文件管理（统一接口）
    // ========================================

    /**
     * 设置文件信息
     * @param {string} fileType - 文件类型：originalTender, technical, business, pointToPoint, techProposal
     * @param {Object} fileInfo - 文件信息对象
     */
    setFile(fileType, fileInfo) {
        if (!this.state.files.hasOwnProperty(fileType)) {
            console.error(`[GlobalState] 无效的文件类型: ${fileType}`);
            return;
        }

        this.state.files[fileType] = {
            fileName: fileInfo.fileName || null,
            filePath: fileInfo.filePath || null,
            fileUrl: fileInfo.fileUrl || null,
            fileSize: fileInfo.fileSize || null,
            uploadedAt: new Date().toISOString()
        };

        this.notify('files', { type: fileType, data: this.state.files[fileType] });
        console.log(`[GlobalState] ${fileType} 文件信息已更新:`, this.state.files[fileType]);
    }

    getFile(fileType) {
        return this.state.files[fileType] ? { ...this.state.files[fileType] } : null;
    }

    clearFile(fileType) {
        this.state.files[fileType] = null;
        this.notify('files', { type: fileType, data: null });
    }

    clearAllFiles() {
        Object.keys(this.state.files).forEach(key => {
            this.state.files[key] = null;
        });
        this.notify('files', { type: 'all', data: null });
    }

    // ========================================
    // AI模型管理
    // ========================================

    setAvailableModels(models) {
        this.state.ai.availableModels = models;
        this.notify('ai', { type: 'models', data: models });
        console.log(`[GlobalState] AI模型列表已更新，共 ${models.length} 个模型`);
    }

    getAvailableModels() {
        return [...this.state.ai.availableModels];
    }

    setSelectedModel(modelName) {
        this.state.ai.selectedModel = modelName;
        this.notify('ai', { type: 'selectedModel', data: modelName });
        console.log(`[GlobalState] 已选择AI模型: ${modelName}`);
    }

    getSelectedModel() {
        return this.state.ai.selectedModel;
    }

    // ========================================
    // HITL任务管理
    // ========================================

    setHitlTaskId(taskId) {
        this.state.hitl.taskId = taskId;
        console.log(`[GlobalState] HITL任务ID已设置: ${taskId}`);
    }

    getHitlTaskId() {
        return this.state.hitl.taskId;
    }

    clearHitlTaskId() {
        this.state.hitl.taskId = null;
    }

    // ========================================
    // 观察者模式（订阅/通知）
    // ========================================

    /**
     * 订阅状态变化
     * @param {string} category - 类别：company, project, files, ai
     * @param {Function} callback - 回调函数
     * @returns {Function} - 取消订阅函数
     */
    subscribe(category, callback) {
        if (!this.listeners[category]) {
            console.error(`[GlobalState] 无效的订阅类别: ${category}`);
            return () => {};
        }

        this.listeners[category].push(callback);
        console.log(`[GlobalState] 新订阅: ${category}, 当前订阅数: ${this.listeners[category].length}`);

        // 返回取消订阅函数
        return () => {
            const index = this.listeners[category].indexOf(callback);
            if (index > -1) {
                this.listeners[category].splice(index, 1);
            }
        };
    }

    /**
     * 通知所有订阅者
     */
    notify(category, data) {
        if (this.listeners[category]) {
            this.listeners[category].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[GlobalState] 监听器执行错误 (${category}):`, error);
                }
            });
        }
    }

    // ========================================
    // 批量操作
    // ========================================

    /**
     * 批量设置状态（用于从HITL页面跳转）
     */
    setBulk(data) {
        let updated = [];

        if (data.company) {
            this.setCompany(data.company.id, data.company.name);
            updated.push('company');
        }

        if (data.project) {
            this.setProject(data.project.id, data.project.name);
            updated.push('project');
        }

        if (data.files) {
            Object.keys(data.files).forEach(fileType => {
                if (data.files[fileType]) {
                    this.setFile(fileType, data.files[fileType]);
                }
            });
            updated.push('files');
        }

        if (data.hitlTaskId) {
            this.setHitlTaskId(data.hitlTaskId);
            updated.push('hitl');
        }

        console.log('[GlobalState] 批量更新完成:', updated.join(', '));
    }

    /**
     * 清空所有状态（退出项目时使用）
     */
    clearAll() {
        this.clearCompany();
        this.clearProject();
        this.clearAllFiles();
        this.clearHitlTaskId();
        console.log('[GlobalState] 所有状态已清空');
    }

    // ========================================
    // 调试工具
    // ========================================

    /**
     * 获取完整状态快照（用于调试）
     */
    getSnapshot() {
        return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * 打印当前状态（用于调试）
     */
    debug() {
        console.group('[GlobalState] 当前状态快照');
        console.log('公司:', this.state.company);
        console.log('项目:', this.state.project);
        console.log('HITL任务:', this.state.hitl);
        console.log('文件:', this.state.files);
        console.log('AI配置:', this.state.ai);
        console.log('订阅统计:', {
            company: this.listeners.company.length,
            project: this.listeners.project.length,
            files: this.listeners.files.length,
            ai: this.listeners.ai.length
        });
        console.groupEnd();
    }
}

// 创建全局唯一实例
window.globalState = new GlobalStateManager();
console.log('[GlobalState] 全局状态管理器已初始化');
```

---

## 二、各页面使用方式

### 1. 投标管理页面（Tender Management）

```javascript
// ========================================
// 初始化时订阅状态变化
// ========================================
window.globalState.subscribe('company', (companyData) => {
    console.log('[TenderManagement] 收到公司变更:', companyData);
    const companySelect = document.getElementById('hitlCompanySelect');
    if (companySelect) {
        companySelect.value = companyData.id;
    }

    const companyNameSpan = document.getElementById('hitlSelectedCompanyName');
    if (companyNameSpan) {
        companyNameSpan.textContent = companyData.name || '未选择';
    }
});

window.globalState.subscribe('ai', (aiData) => {
    if (aiData.type === 'selectedModel') {
        console.log('[TenderManagement] 收到AI模型变更:', aiData.data);
        const modelSelect = document.getElementById('hitlAiModel');
        if (modelSelect) {
            modelSelect.value = aiData.data;
        }
    }
});

// ========================================
// 当用户选择公司时
// ========================================
document.getElementById('hitlCompanySelect').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    window.globalState.setCompany(this.value, selectedOption.text);
});

// ========================================
// 保存技术需求文件时
// ========================================
function saveTechnicalRequirements(fileName, filePath) {
    window.globalState.setFile('technical', {
        fileName: fileName,
        filePath: filePath,
        fileUrl: `/download/${fileName}`,
        fileSize: null  // 如果有大小信息可以传入
    });
}

// ========================================
// 保存商务应答文件时
// ========================================
function saveBusinessResponse(fileName, filePath) {
    window.globalState.setFile('business', {
        fileName: fileName,
        filePath: filePath,
        fileUrl: `/download/${fileName}`
    });
}
```

---

### 2. 商务应答页面（Business Response）

```javascript
// ========================================
// 初始化时订阅状态
// ========================================
window.globalState.subscribe('company', (companyData) => {
    const companyIdInput = document.getElementById('businessCompanyId');
    if (companyIdInput) {
        companyIdInput.value = companyData.id || '';
    }
});

window.globalState.subscribe('files', (fileData) => {
    if (fileData.type === 'business') {
        loadBusinessFile(fileData.data);
    }
});

// ========================================
// 从HITL加载文件
// ========================================
function loadBusinessFile(fileInfo) {
    if (!fileInfo) return;

    const fileNameDiv = document.getElementById('businessTemplateFileName');
    if (fileNameDiv) {
        fileNameDiv.innerHTML = `
            <div class="alert alert-success">
                <i class="bi bi-file-earmark-word"></i>
                <span>${fileInfo.fileName}</span>
                <span class="badge bg-success">已从投标项目加载</span>
            </div>
        `;
    }

    // 隐藏上传区域
    const uploadArea = document.querySelector('.upload-area');
    if (uploadArea) {
        uploadArea.style.display = 'none';
    }
}

// ========================================
// 表单提交时获取数据
// ========================================
async function submitBusinessResponse() {
    const formData = new FormData();

    // 从全局状态获取数据
    const company = window.globalState.getCompany();
    const project = window.globalState.getProject();
    const businessFile = window.globalState.getFile('business');

    if (!company.id) {
        alert('请选择公司');
        return;
    }

    if (!businessFile && !fileInput.files.length) {
        alert('请上传或选择商务应答文件');
        return;
    }

    // 构建表单
    formData.append('company_id', company.id);
    formData.append('project_name', project.name || '');

    if (businessFile && businessFile.filePath) {
        formData.append('hitl_file_path', businessFile.filePath);
    } else {
        formData.append('template_file', fileInput.files[0]);
    }

    // 发送请求...
}
```

---

### 3. 点对点应答页面（Point-to-Point）

```javascript
// ========================================
// 订阅技术文件变化
// ========================================
window.globalState.subscribe('files', (fileData) => {
    if (fileData.type === 'technical') {
        loadTechnicalFile(fileData.data);
    }
});

// ========================================
// 加载技术文件
// ========================================
function loadTechnicalFile(fileInfo) {
    if (!fileInfo) return;

    const fileNameElement = document.getElementById('fileName');
    const fileSizeElement = document.getElementById('fileSize');

    if (fileNameElement) {
        fileNameElement.textContent = fileInfo.fileName;
    }

    if (fileSizeElement && fileInfo.fileSize) {
        const sizeInMB = (fileInfo.fileSize / 1024 / 1024).toFixed(2);
        fileSizeElement.textContent = `(${sizeInMB} MB)`;
    }

    // 显示文件信息，隐藏上传区域
    document.getElementById('fileInfo').classList.remove('d-none');
    document.getElementById('uploadArea').style.display = 'none';
}

// ========================================
// 表单提交
// ========================================
async function submitPointToPoint() {
    const formData = new FormData();

    // 从全局状态获取数据
    const company = window.globalState.getCompany();
    const project = window.globalState.getProject();
    const technicalFile = window.globalState.getFile('technical');
    const selectedModel = window.globalState.getSelectedModel();

    formData.append('company_id', company.id);
    formData.append('project_name', project.name || '');
    formData.append('ai_model', selectedModel);

    // 如果有HITL传递的技术文件，使用文件路径
    if (technicalFile && technicalFile.filePath) {
        formData.append('hitl_technical_file_path', technicalFile.filePath);
    } else {
        // 否则使用用户上传的文件
        formData.append('technical_file', fileInput.files[0]);
    }

    // 发送请求...
}
```

---

### 4. 技术方案页面（Technical Proposal）

```javascript
// ========================================
// 订阅状态变化
// ========================================
window.globalState.subscribe('files', (fileData) => {
    if (fileData.type === 'technical') {
        displayTechnicalFile(fileData.data);
    }
});

// ========================================
// 显示技术文件
// ========================================
function displayTechnicalFile(fileInfo) {
    if (!fileInfo) return;

    const displayElement = document.getElementById('techTechnicalFileDisplay');
    const nameElement = document.getElementById('techTechnicalFileDisplayName');
    const sizeElement = document.getElementById('techTechnicalFileDisplaySize');

    if (nameElement) {
        nameElement.textContent = fileInfo.fileName;
    }

    if (sizeElement && fileInfo.fileSize) {
        const sizeInMB = (fileInfo.fileSize / 1024 / 1024).toFixed(2);
        sizeElement.textContent = `(${sizeInMB} MB)`;
    }

    if (displayElement) {
        displayElement.classList.remove('d-none');
    }

    // 隐藏上传区域
    document.getElementById('techTenderUpload').style.display = 'none';
}
```

---

## 三、Tab切换逻辑优化

```javascript
// ========================================
// 在 index.html 中统一处理Tab切换
// ========================================
document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tabLink => {
    tabLink.addEventListener('shown.bs.tab', function(event) {
        const targetTab = event.target.getAttribute('data-bs-target');
        console.log(`[TabSwitch] 切换到: ${targetTab}`);

        // ✅ 不再需要手动同步数据
        // 各页面已通过 subscribe 自动监听状态变化

        // 只需要按需加载CSS
        if (window.loadCSSForTab) {
            window.loadCSSForTab(targetTab.replace('#', ''));
        }
    });
});
```

---

## 四、从HITL跳转的处理

```javascript
// ========================================
// 在投标管理页面"跳转到商务应答"按钮
// ========================================
function jumpToBusinessResponse(hitlTaskId) {
    // ✅ 一次性设置所有状态
    window.globalState.setBulk({
        company: {
            id: currentCompanyId,
            name: currentCompanyName
        },
        project: {
            id: currentProjectId,
            name: currentProjectName
        },
        files: {
            business: {
                fileName: responseFileName,
                filePath: responseFilePath,
                fileUrl: responseFileUrl
            }
        },
        hitlTaskId: hitlTaskId
    });

    // ✅ 切换Tab（状态已自动同步到目标页面）
    const businessTab = document.querySelector('[data-bs-target="#business-response"]');
    if (businessTab) {
        businessTab.click();
    }
}

// ========================================
// 跳转到点对点应答
// ========================================
function jumpToPointToPoint(hitlTaskId) {
    window.globalState.setBulk({
        company: { id: currentCompanyId, name: currentCompanyName },
        project: { id: currentProjectId, name: currentProjectName },
        files: {
            technical: {
                fileName: technicalFileName,
                filePath: technicalFilePath,
                fileUrl: technicalFileUrl,
                fileSize: technicalFileSize
            }
        },
        hitlTaskId: hitlTaskId
    });

    const pointToPointTab = document.querySelector('[data-bs-target="#point-to-point"]');
    if (pointToPointTab) {
        pointToPointTab.click();
    }
}
```

---

## 五、优势总结

### ✅ 1. 单一数据源
- 所有状态都存储在 `window.globalState` 中
- 避免数据不一致问题

### ✅ 2. 自动同步
- 使用观察者模式，状态变化自动通知订阅者
- 不需要手动同步或定时器

### ✅ 3. 职责清晰
- `GlobalStateManager` 专注状态管理
- 各页面只负责UI展示和用户交互

### ✅ 4. 易于维护
- 新增功能只需 `subscribe` 和 `set`
- 统一的API，降低学习成本

### ✅ 5. 可调试
- `globalState.debug()` 查看完整状态
- `globalState.getSnapshot()` 获取状态快照

### ✅ 6. 解耦合
- 页面间不直接依赖
- 通过状态管理器间接通信

---

## 六、迁移步骤

### 第1步：创建 GlobalStateManager
```bash
# 创建新文件
ai_tender_system/web/static/js/core/global-state-manager.js
```

### 第2步：在 index.html 中引入
```html
<!-- 在其他脚本之前加载 -->
<script src="/static/js/core/global-state-manager.js"></script>
```

### 第3步：逐个迁移页面
1. 投标管理页面
2. 商务应答页面
3. 点对点应答页面
4. 技术方案页面

### 第4步：移除旧代码
- 删除 `window.projectDataBridge`
- 删除 `window.companyStateManager`
- 删除 `window.businessResponseFileUrl` 等临时全局变量

---

## 七、兼容性方案（可选）

如果需要渐进式迁移，可以先保留旧API，内部调用新API：

```javascript
// 兼容层 - 逐步迁移时使用
window.projectDataBridge = {
    setTechnicalFile(taskId, fileName, fileSize, fileUrl) {
        window.globalState.setFile('technical', {
            fileName, fileSize, fileUrl
        });
        window.globalState.setHitlTaskId(taskId);
    },

    getTechnicalFile() {
        return window.globalState.getFile('technical');
    },

    // 其他兼容方法...
};
```

---

## 八、测试检查清单

- [ ] 投标管理 → 商务应答跳转
- [ ] 投标管理 → 点对点应答跳转
- [ ] 投标管理 → 技术方案跳转
- [ ] 公司选择自动同步到所有页面
- [ ] AI模型选择自动同步
- [ ] 文件信息正确传递
- [ ] 页面刷新后状态是否需要持久化（localStorage）
- [ ] 多标签页打开时的状态同步（BroadcastChannel）

---

## 九、后续优化方向

### 1. 状态持久化
```javascript
// 可选：保存到 localStorage
saveToStorage() {
    localStorage.setItem('app_state', JSON.stringify(this.state));
}

loadFromStorage() {
    const saved = localStorage.getItem('app_state');
    if (saved) {
        this.state = JSON.parse(saved);
    }
}
```

### 2. 多标签页同步
```javascript
// 可选：使用 BroadcastChannel 同步多个标签页
const channel = new BroadcastChannel('app_state_sync');
channel.postMessage({ type: 'stateChange', data: this.state });
```

### 3. 状态历史记录
```javascript
// 可选：实现撤销/重做功能
class GlobalStateManager {
    constructor() {
        this.history = [];
        this.historyIndex = -1;
    }

    undo() { /* ... */ }
    redo() { /* ... */ }
}
```
