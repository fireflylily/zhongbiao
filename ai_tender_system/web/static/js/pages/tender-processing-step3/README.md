# tender-processing-step3 模块化架构

**状态**: 🚧 重构进行中 (Phase 1 完成 40%)
**分支**: refactor/step3-modularization
**原始文件**: `../tender-processing-step3-enhanced.js` (2,761行)

---

## 📁 目录结构

```
tender-processing-step3/
├── README.md                   # 本文件
├── index.js                    # 主入口（待创建）
├── api/
│   └── tender-processing-api.js   # API封装层 ✅
├── components/
│   └── (待创建)
├── config/
│   └── eligibility-checklist.js   # 资格清单配置 ✅
├── managers/
│   └── (待创建)
└── utils/
    ├── toast-manager.js           # Toast提示 ✅
    ├── formatter.js               # 格式化工具 ✅
    └── validator.js               # 验证工具 ✅
```

---

## ✅ 已完成模块

### 1. utils/toast-manager.js
**功能**: 统一的Toast提示管理

**使用方法**:
```javascript
import toastManager, { showSuccessToast, showErrorToast } from './utils/toast-manager.js';

// 方式1: 使用单例（推荐）
toastManager.success('操作成功');
toastManager.error('操作失败');
toastManager.warning('警告信息');
toastManager.info('提示信息');

// 方式2: 使用便捷函数（向后兼容）
showSuccessToast('操作成功');
showErrorToast('操作失败');

// 自定义持续时间
toastManager.show('自定义消息', 'info', 5000);
```

**特性**:
- ✅ 4种类型：success, error, warning, info
- ✅ 自动清理机制
- ✅ 优雅的滑入/滑出动画
- ✅ 单例模式，全局唯一实例
- ✅ 向后兼容旧代码

---

### 2. utils/formatter.js
**功能**: 文本格式化、HTML转义、类型标签

**使用方法**:
```javascript
import {
    formatDetailTextWithToggle,
    formatFileSize,
    formatDateTime,
    getConstraintTypeBadge,
    escapeHtml
} from './utils/formatter.js';

// 长文本展开/收起
const html = formatDetailTextWithToggle(longText, 150);
document.getElementById('content').innerHTML = html;

// 文件大小格式化
const size = formatFileSize(1048576); // "1.00 MB"

// 日期时间格式化
const date = formatDateTime(new Date(), 'datetime'); // "2025-10-25 17:00:00"

// 约束类型徽章
const badgeClass = getConstraintTypeBadge('mandatory'); // "danger"

// HTML转义
const safe = escapeHtml('<script>alert("xss")</script>');
```

**特性**:
- ✅ 智能文本截断（优先在标点符号处）
- ✅ 展开/收起功能（自动生成ID）
- ✅ 文件大小、日期时间格式化
- ✅ 约束类型徽章和标签
- ✅ HTML转义防XSS

---

### 3. utils/validator.js
**功能**: 数据验证工具集

**使用方法**:
```javascript
import {
    validateBasicInfo,
    validateChapterSelection,
    validateRequirement,
    isValidEmail,
    validateFileType
} from './utils/validator.js';

// 验证基本信息
const result = validateBasicInfo({
    project_name: '测试项目',
    project_number: 'P2025001'
});

if (!result.valid) {
    console.error(result.message);
    console.error(result.errors); // 字段级错误
}

// 验证章节选择
const chapterResult = validateChapterSelection(selectedChapters);

// 验证邮箱
if (isValidEmail('test@example.com')) {
    // 有效邮箱
}

// 验证文件类型
const fileResult = validateFileType('document.pdf', ['.pdf', '.doc', '.docx']);
```

**特性**:
- ✅ 统一的验证结果格式 `{valid, message, errors}`
- ✅ 必填字段验证
- ✅ 邮箱、电话、URL验证
- ✅ 文件类型和大小验证
- ✅ 批量验证支持

---

### 4. config/eligibility-checklist.js
**功能**: 18条供应商资格清单配置

**使用方法**:
```javascript
import {
    ELIGIBILITY_CHECKLIST,
    matchEligibilityItems,
    getEligibilityItemById,
    getEligibilityItemsByCategory
} from './config/eligibility-checklist.js';

// 获取所有清单
console.log(ELIGIBILITY_CHECKLIST); // 18条清单数组

// 智能匹配
const requirementText = "投标人需提供营业执照复印件和ISO9001认证";
const matches = matchEligibilityItems(requirementText);
console.log('匹配到', matches.length, '个清单项');
matches.forEach(match => {
    console.log(`${match.name} (匹配${match.matchCount}个关键词, 分数: ${match.score})`);
});

// 根据ID获取
const item = getEligibilityItemById(1); // 营业执照信息

// 根据类别获取
const basicItems = getEligibilityItemsByCategory('基本资质');
```

**数据结构**:
```javascript
{
    id: 1,
    name: "营业执照信息",
    keywords: ["营业执照", "注册", "法人", "注册资金"],
    category: "基本资质",
    priority: "high",
    description: "企业营业执照及基本工商信息"
}
```

**特性**:
- ✅ 18条标准资格清单
- ✅ 智能关键词匹配
- ✅ 权重和优先级配置
- ✅ 类别分组
- ✅ 辅助查询函数

---

### 5. api/tender-processing-api.js
**功能**: 统一API调用封装

**使用方法**:
```javascript
import tenderProcessingAPI from './api/tender-processing-api.js';

// 加载需求
try {
    const data = await tenderProcessingAPI.loadRequirements(taskId, projectId);
    console.log('加载了', data.requirements.length, '条需求');
} catch (error) {
    console.error('加载失败:', error.message);
}

// 保存章节选择
await tenderProcessingAPI.saveChapterSelection(taskId, 'technical', chapters);

// 提取基本信息
await tenderProcessingAPI.extractBasicInfo(taskId, 'yuanjing-deepseek-v3');

// 创建项目
const project = await tenderProcessingAPI.createProject({
    project_name: '测试项目',
    project_number: 'P2025001'
});
```

**特性**:
- ✅ 自动重试机制（指数退避：1s → 2s → 4s）
- ✅ 统一错误处理
- ✅ 超时控制（默认30秒）
- ✅ RESTful方法封装（GET/POST/PUT/DELETE）
- ✅ 详细日志记录

**配置**:
```javascript
import { TenderProcessingAPI } from './api/tender-processing-api.js';

// 自定义配置
const customAPI = new TenderProcessingAPI({
    baseURL: '/api/custom',
    retryAttempts: 5,
    timeout: 60000
});
```

---

## 🚧 待完成模块

### managers/ChapterSelectorManager.js (待创建)
**功能**: 统一章节选择逻辑
**预计行数**: ~350行
**消除重复**: 减少~300行重复代码

### managers/DataSyncManager.js (待创建)
**功能**: 统一数据保存和同步
**预计行数**: ~200行

### managers/RequirementsTableManager.js (待迁移)
**功能**: 需求表格管理
**预计行数**: ~250行

### components/EligibilityChecker.js (待创建)
**功能**: 18条资格清单匹配
**预计行数**: ~300行

### index.js (待创建)
**功能**: 主入口，组装所有模块
**预计行数**: ~150行

---

## 🔄 迁移指南

### 当前状态
- ✅ 原始文件 `tender-processing-step3-enhanced.js` 保持不变
- ✅ 新模块在 `tender-processing-step3/` 目录下开发
- ⏳ 待主入口完成后，可选择性切换

### 如何切换到新模块（未来）
1. 在HTML中引入新的主入口：
```html
<!-- 旧方式（当前使用） -->
<script src="/static/js/pages/tender-processing-step3-enhanced.js"></script>

<!-- 新方式（未来切换） -->
<script type="module" src="/static/js/pages/tender-processing-step3/index.js"></script>
```

2. 使用Feature Toggle控制切换：
```javascript
const USE_REFACTORED_STEP3 = localStorage.getItem('use_refactored_step3') === 'true';

if (USE_REFACTORED_STEP3) {
    import('./pages/tender-processing-step3/index.js');
} else {
    import('./pages/tender-processing-step3-enhanced.js');
}
```

---

## 📊 当前进度

| 模块 | 状态 | 行数 |
|-----|------|------|
| utils/toast-manager.js | ✅ | 261 |
| utils/formatter.js | ✅ | 274 |
| utils/validator.js | ✅ | 273 |
| config/eligibility-checklist.js | ✅ | 384 |
| api/tender-processing-api.js | ✅ | 409 |
| **已完成小计** | | **1,601** |
| **待完成预计** | | **~1,480** |
| **总计** | | **~3,081** |

**原始文件**: 2,761行
**预计变化**: +320行 (+11.6%)
**重复代码减少**: ~300行 (-10.8%)

---

## 🧪 测试

### 单元测试（待创建）
```bash
# 测试工具函数
npm test -- utils/toast-manager.test.js
npm test -- utils/formatter.test.js
npm test -- utils/validator.test.js

# 测试API层
npm test -- api/tender-processing-api.test.js

# 测试配置
npm test -- config/eligibility-checklist.test.js
```

### 浏览器测试
```javascript
// 在浏览器控制台测试Toast
import('./utils/toast-manager.js').then(({ showSuccessToast }) => {
    showSuccessToast('测试消息');
});

// 测试格式化
import('./utils/formatter.js').then(({ formatFileSize }) => {
    console.log(formatFileSize(1024 * 1024)); // "1.00 MB"
});
```

---

## 📚 文档

- [完整重构方案](../../../../../../TENDER_PROCESSING_STEP3_REFACTOR_PLAN.md)
- [重构进度报告](../../../../../../REFACTOR_PROGRESS.md)
- [项目架构指南](../../../../../../CLAUDE.md)

---

## 🤝 贡献指南

### 添加新工具函数
1. 在 `utils/` 目录创建新文件
2. 使用ES6模块导出
3. 添加JSDoc注释
4. 编写单元测试

### 添加新配置
1. 在 `config/` 目录创建新文件
2. 导出配置对象和辅助函数
3. 更新本README

### 修改现有模块
1. 保持向后兼容
2. 更新JSDoc注释
3. 运行测试确保无破坏

---

**最后更新**: 2025-10-25
**维护者**: Claude Code
**问题反馈**: [GitHub Issues](...)
