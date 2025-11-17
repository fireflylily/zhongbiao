# AI模型全局管理优化

## 问题描述
AI模型配置在不同Tab之间没有正常同步显示。各个Tab有独立的模型选择器：
- 点对点应答：`aiModel`
- 投标管理：`hitlAiModel`
- 技术方案生成：`tenderAiModel`

这些选择器之前相互独立，没有共享状态。

## 解决方案

### 1. 在 `window.projectDataBridge` 中添加AI模型管理

**位置**: [index.html:78-82](ai_tender_system/web/templates/index.html#L78-L82)

```javascript
// 【新增】AI模型管理
aiModels: {
    currentModels: [],           // 所有可用模型列表
    selectedModel: 'unicom-yuanjing'  // 当前选中的模型
}
```

### 2. 添加模型管理方法

**位置**: [index.html:159-186](ai_tender_system/web/templates/index.html#L159-L186)

新增以下方法：
- `setModels(models)` - 设置模型列表
- `getModels()` - 获取模型列表
- `setSelectedModel(modelName)` - 设置选中的模型
- `getSelectedModel()` - 获取选中的模型

### 3. ModelManager 与全局状态集成

#### 3.1 保存模型列表到全局状态
**位置**: [index.html:424-427](ai_tender_system/web/templates/index.html#L424-L427)

```javascript
// 【新增】保存到全局 projectDataBridge
if (window.projectDataBridge) {
    window.projectDataBridge.setModels(data.models);
}
```

#### 3.2 更新所有Tab的模型选择器
**位置**: [index.html:461-464](ai_tender_system/web/templates/index.html#L461-L464)

新增对 `hitlAiModel` (投标管理) 的支持：
```javascript
// 【新增】更新投标管理页面的模型选择器
if (hitlAiModelSelect) {
    this.updateSingleModelSelect(hitlAiModelSelect, 'hitlAiModel');
}
```

#### 3.3 绑定事件并同步到全局状态
**位置**: [index.html:594-605](ai_tender_system/web/templates/index.html#L594-L605)

```javascript
// 【新增】绑定投标管理模型选择器事件
const hitlAiModelSelect = document.getElementById('hitlAiModel');
if (hitlAiModelSelect) {
    hitlAiModelSelect.addEventListener('change', () => {
        this.currentModel = hitlAiModelSelect.value;
        // 保存到全局状态
        if (window.projectDataBridge) {
            window.projectDataBridge.setSelectedModel(hitlAiModelSelect.value);
        }
        this.updateModelStatus();
    });
}
```

### 4. Tab切换时自动同步模型

#### 4.1 监听所有Tab切换事件
**位置**: [index.html:675-705](ai_tender_system/web/templates/index.html#L675-L705)

```javascript
// 【新增】监听所有Tab切换，实时同步AI模型选择
document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tabLink => {
    tabLink.addEventListener('shown.bs.tab', function(event) {
        const targetTab = event.target.getAttribute('data-bs-target');

        // 根据不同tab获取对应的模型选择器
        if (targetTab === '#point-to-point') {
            currentModelSelect = document.getElementById('aiModel');
        } else if (targetTab === '#tender-management') {
            currentModelSelect = document.getElementById('hitlAiModel');
        }

        // 同步模型选择
        if (currentModelSelect && selectedModel && currentModelSelect.value !== selectedModel) {
            currentModelSelect.value = selectedModel;
            ModelManager.updateModelStatus();
        }
    });
});
```

#### 4.2 投标管理Tab特殊处理
**位置**: [index.html:722-738](ai_tender_system/web/templates/index.html#L722-L738)

在投标管理Tab激活时，额外同步AI模型选择：
```javascript
// 【新增】同步AI模型选择
if (bridge && ModelManager) {
    setTimeout(() => {
        const selectedModel = bridge.getSelectedModel();
        const hitlModelSelect = document.getElementById('hitlAiModel');

        if (hitlModelSelect && selectedModel) {
            hitlModelSelect.value = selectedModel;
            ModelManager.updateModelStatus();
        }
    }, 150);
}
```

### 5. HITLConfigManager 集成

**位置**: [hitl-config-manager.js:58-84](ai_tender_system/web/static/js/hitl-config-manager.js#L58-L84)

```javascript
// 加载模型列表
async loadModels() {
    // 【修改】优先从全局状态获取模型列表
    if (window.projectDataBridge && window.projectDataBridge.getModels().length > 0) {
        const models = window.projectDataBridge.getModels();
        this.updateModelSelect(models);
        return;
    }

    // 如果全局状态没有数据，从API加载
    const response = await fetch('/api/models');
    const data = await response.json();

    if (data.success && data.models) {
        // 【新增】保存到全局状态
        if (window.projectDataBridge) {
            window.projectDataBridge.setModels(data.models);
        }
        this.updateModelSelect(data.models);
    }
}
```

**位置**: [hitl-config-manager.js:487-490](ai_tender_system/web/static/js/hitl-config-manager.js#L487-L490)

```javascript
// 【新增】保存到全局状态
if (window.projectDataBridge) {
    window.projectDataBridge.setSelectedModel(e.target.value);
}
```

## 优点

1. **统一数据源**: 所有AI模型数据保存在 `window.projectDataBridge.aiModels` 中
2. **自动同步**: Tab之间切换时自动同步模型选择，无需手动干预
3. **避免重复加载**: 优先从全局状态读取，减少API请求
4. **双向绑定**: 任何Tab修改模型选择都会自动同步到全局状态和其他Tab
5. **向后兼容**: 不影响现有功能，只是添加了额外的同步机制

## 测试要点

1. 在点对点应答选择模型A
2. 切换到投标管理，应该自动选中模型A
3. 在投标管理改为模型B
4. 切换回点对点应答，应该自动变为模型B
5. 刷新页面后，模型列表应该正常加载

## 访问地址
服务器已启动: http://127.0.0.1:8110
