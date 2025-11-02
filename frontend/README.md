# AI智能标书生成平台 - 前端应用

> Vue 3 + TypeScript + Vite 构建的现代化单页面应用

## 🚀 快速开始

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
# 启动开发服务器 (http://localhost:5173)
npm run dev

# 确保后端Flask服务器运行在 http://localhost:8110
```

### 构建生产版本

```bash
# 构建到 ../ai_tender_system/web/static/dist/
npm run build

# 预览构建结果
npm run preview
```

### 类型检查

```bash
npm run type-check
```

### 代码检查与格式化

```bash
# ESLint检查
npm run lint

# Prettier格式化
npm run format
```

## 📁 项目结构

```
src/
├── api/                    # API服务层
│   ├── client.ts           # Axios实例配置
│   ├── interceptors.ts     # 请求/响应拦截器
│   └── endpoints/          # API端点模块
│       ├── tender.ts       # 投标API
│       ├── company.ts      # 公司API
│       ├── knowledge.ts    # 知识库API
│       └── index.ts        # 统一导出
│
├── stores/                 # Pinia状态管理
│   ├── user.ts             # 用户状态
│   ├── company.ts          # 公司状态
│   ├── project.ts          # 项目状态
│   ├── aiModel.ts          # AI模型配置
│   └── index.ts            # Store入口
│
├── router/                 # Vue Router配置
│   ├── index.ts            # 主路由配置
│   ├── modules/            # 路由模块
│   └── guards.ts           # 路由守卫
│
├── views/                  # 页面组件
│   ├── TenderProcessing/   # 文档处理页面
│   ├── BusinessResponse/   # 商务应答页面
│   └── ...
│
├── components/             # 通用组件
│   ├── common/             # 基础组件
│   └── business/           # 业务组件
│
├── composables/            # 组合式函数
│   ├── useSSE.ts           # SSE流处理
│   ├── useNotification.ts  # 通知hooks
│   └── useFileUpload.ts    # 文件上传hooks
│
├── layouts/                # 页面布局
│   ├── DefaultLayout.vue   # 默认布局
│   └── BlankLayout.vue     # 空白布局
│
├── types/                  # TypeScript类型定义
│   ├── models.ts           # 数据模型类型
│   ├── api.ts              # API响应类型
│   ├── store.ts            # Store状态类型
│   └── index.ts            # 统一导出
│
├── utils/                  # 工具函数
│   ├── format.ts           # 格式化工具
│   ├── validation.ts       # 验证工具
│   └── constants.ts        # 常量定义
│
├── assets/                 # 静态资源
│   ├── styles/             # 全局样式
│   └── images/             # 图片资源
│
├── App.vue                 # 根组件
└── main.ts                 # 应用入口
```

## 🔧 技术栈

### 核心框架

- **Vue 3.4** - 渐进式JavaScript框架
- **TypeScript 5.3** - JavaScript的超集
- **Vite 5.0** - 下一代前端构建工具

### 路由与状态管理

- **Vue Router 4.2** - 官方路由管理器
- **Pinia 2.1** - 官方状态管理库

### UI组件与工具

- **Element Plus 2.5** - 企业级UI组件库
- **Axios 1.6** - HTTP客户端
- **VueUse 10.7** - 组合式工具库
- **Day.js 1.11** - 轻量级日期库

### 开发工具

- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **TypeScript ESLint** - TypeScript代码检查

## 📝 开发规范

### 命名约定

```typescript
// 文件命名: kebab-case
api-client.ts
use-notification.ts

// 组件命名: PascalCase
TenderProcessing.vue
CompanySelector.vue

// 变量/函数: camelCase
const projectId = 123
function loadProject() {}

// 常量: UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 100 * 1024 * 1024

// 类型/接口: PascalCase
interface Project {}
type ApiResponse = {}
```

### 组件编写规范

```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 2. Props & Emits
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

const emit = defineEmits<{
  (e: 'update', value: number): void
  (e: 'close'): void
}>()

// 3. Composables
const router = useRouter()

// 4. State
const loading = ref(false)
const data = ref<any>(null)

// 5. Computed
const displayText = computed(() => `${props.title}: ${props.count}`)

// 6. Methods
async function loadData() {
  loading.value = true
  try {
    // 加载数据
  } finally {
    loading.value = false
  }
}

function handleClick() {
  emit('update', props.count + 1)
}

// 7. Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.component-name {
  // 组件样式
}
</style>
```

### API调用规范

```typescript
// 使用统一的API服务层
import { tenderApi } from '@/api/endpoints'

// 在组件中调用
async function fetchProject(id: number) {
  try {
    const project = await tenderApi.getProject(id)
    // 处理数据
  } catch (error) {
    // 错误已由拦截器统一处理
    console.error('获取项目失败:', error)
  }
}
```

### Store使用规范

```typescript
// 在组件中使用Store
import { useProjectStore } from '@/stores/project'

const projectStore = useProjectStore()

// 读取状态
const currentProject = projectStore.currentProject

// 调用action
await projectStore.loadProject(123)

// 使用computed
const projectName = computed(() => projectStore.currentProject?.name)
```

## 🔌 API代理配置

开发环境下,所有API请求自动代理到Flask后端:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8110',
      changeOrigin: true
    }
  }
}
```

## 🎨 样式组织

### SCSS变量

```scss
// assets/styles/variables.scss
$primary-color: #4a89dc;
$success-color: #48cfad;
$warning-color: #eb7d3c;
$danger-color: #da4453;

$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;

$border-radius: 8px;
```

### 全局样式

```scss
// assets/styles/global.scss
// 全局样式在main.ts中导入
import '@/assets/styles/global.scss'
```

### 组件样式

```vue
<style scoped lang="scss">
// 使用scoped避免样式污染
.component {
  color: $primary-color; // 使用SCSS变量
  padding: $spacing-md;
}
</style>
```

## 🧪 测试

### 单元测试

```bash
# 运行单元测试 (计划中)
npm run test:unit
```

### E2E测试

```bash
# 运行E2E测试 (计划中)
npm run test:e2e
```

## 📦 构建与部署

### 构建配置

```typescript
// vite.config.ts
build: {
  // 输出到Flask static目录
  outDir: '../ai_tender_system/web/static/dist',

  // 代码分割
  rollupOptions: {
    output: {
      manualChunks: {
        'vue-vendor': ['vue', 'vue-router', 'pinia'],
        'ui-vendor': ['element-plus'],
        'utils-vendor': ['axios', '@vueuse/core']
      }
    }
  }
}
```

### 生产部署流程

1. **构建前端**
   ```bash
   npm run build
   ```

2. **验证构建产物**
   ```bash
   ls -la ../ai_tender_system/web/static/dist/
   ```

3. **启动Flask服务器**
   ```bash
   cd ..
   gunicorn -w 4 -b 0.0.0.0:8110 ai_tender_system.web.app:app
   ```

4. **访问应用**
   ```
   http://your-domain.com/
   ```

## 🐛 调试技巧

### Vue DevTools

安装Chrome扩展: [Vue.js devtools](https://chrome.google.com/webstore/detail/vuejs-devtools)

### 日志输出

```typescript
// 开发环境日志
if (import.meta.env.DEV) {
  console.log('[Debug]', data)
}

// 生产环境不输出
```

### 网络请求调试

所有API请求都会在控制台输出:

```typescript
// api/interceptors.ts
console.log('[API Request]', config.url)
console.log('[API Response]', response.data)
```

## 📊 开发进度

| 模块 | 完成度 | 状态 |
|------|--------|------|
| TypeScript类型系统 | 100% | ✅ 完成 |
| API服务层 | 100% | ✅ 完成 |
| Pinia状态管理 | 100% | ✅ 完成 |
| 组合式函数库 | 100% | ✅ 完成 |
| 路由系统 | 100% | ✅ 完成 |
| 布局组件 | 100% | ✅ 完成 |
| 根组件 | 100% | ✅ 完成 |
| 工具函数库 | 100% | ✅ 完成 |
| 通用组件 | 85% | 🚧 进行中 |
| 业务页面 | 70% | 🚧 进行中 |

**总体进度**: 94% (15,000+ 行代码, 68+ 文件)

查看详细进度：[INFRASTRUCTURE_PROGRESS.md](./INFRASTRUCTURE_PROGRESS.md)

---

## 📖 相关文档

- 📘 [架构总览](./ARCHITECTURE_OVERVIEW.md) - 详细的架构设计文档
- 📗 [进度追踪](./INFRASTRUCTURE_PROGRESS.md) - 开发进度和统计
- 📙 [Vue 3 文档](https://vuejs.org/)
- 📕 [TypeScript 文档](https://www.typescriptlang.org/)
- 📔 [Pinia 文档](https://pinia.vuejs.org/)
- 📓 [Element Plus 文档](https://element-plus.org/)
- 📒 [Vite 文档](https://vitejs.dev/)

## 🤝 贡献指南

### 开发流程

1. 从main分支创建feature分支
2. 开发功能并提交
3. 运行lint和type-check
4. 创建Pull Request
5. Code Review
6. 合并到main

### 提交规范

```bash
feat: 添加新功能
fix: 修复bug
refactor: 代码重构
docs: 文档更新
style: 代码格式调整
test: 测试相关
chore: 构建/工具相关
```

## ❓ 常见问题

### Q1: 如何添加新的API端点?

在 `src/api/endpoints/` 下创建新文件或添加到现有文件,然后在 `index.ts` 中导出。

### Q2: 如何创建新的Store?

在 `src/stores/` 下创建新文件,使用 `defineStore` 定义,然后在需要的组件中导入使用。

### Q3: 如何添加新路由?

在 `src/router/modules/` 下创建路由模块,然后在 `src/router/index.ts` 中导入。

### Q4: 样式不生效?

检查是否使用了 `scoped` 属性,以及SCSS变量是否正确导入。

### Q5: TypeScript报错?

运行 `npm run type-check` 查看详细错误信息,确保所有类型定义正确。

## 📞 联系方式

- **项目负责人**: Claude Code
- **文档更新**: 2025-10-31
- **版本**: 2.0.0
- **项目状态**: 🟢 核心基础设施已完成，进展顺利

---

**Happy Coding! 🚀**
