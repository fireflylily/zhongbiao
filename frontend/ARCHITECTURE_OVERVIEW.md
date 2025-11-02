# 前端架构总览

> **项目名称**: 元景AI智能标书生成平台 - 前端应用
> **技术栈**: Vue 3 + TypeScript + Vite + Pinia
> **文档版本**: v1.0
> **更新日期**: 2025-10-31

---

## 📐 架构设计

### 整体架构图

```
frontend/
├── src/
│   ├── api/                    # API服务层
│   │   ├── client.ts          # Axios客户端
│   │   ├── interceptors.ts    # 拦截器
│   │   └── endpoints/         # API端点
│   │       ├── auth.ts        # 认证
│   │       ├── tender.ts      # 投标
│   │       ├── company.ts     # 公司
│   │       ├── knowledge.ts   # 知识库
│   │       ├── business.ts    # 商务应答
│   │       └── index.ts       # 统一导出
│   │
│   ├── types/                 # TypeScript类型定义
│   │   ├── models.ts          # 数据模型
│   │   ├── api.ts            # API类型
│   │   ├── store.ts          # Store类型
│   │   └── router.d.ts       # 路由类型
│   │
│   ├── stores/                # Pinia状态管理
│   │   ├── user.ts           # 用户状态
│   │   ├── company.ts        # 公司状态
│   │   ├── project.ts        # 项目状态
│   │   ├── aiModel.ts        # AI模型
│   │   ├── notification.ts   # 通知
│   │   ├── settings.ts       # 设置
│   │   └── index.ts          # Store入口
│   │
│   ├── composables/           # 组合式函数
│   │   ├── useSSE.ts         # SSE流处理
│   │   ├── useNotification.ts # 通知
│   │   ├── useFileUpload.ts  # 文件上传
│   │   ├── useForm.ts        # 表单处理
│   │   ├── useAsync.ts       # 异步处理
│   │   └── index.ts          # 统一导出
│   │
│   ├── router/                # Vue Router
│   │   ├── index.ts          # 路由配置
│   │   ├── routes.ts         # 路由定义
│   │   ├── guards.ts         # 路由守卫
│   │   └── utils.ts          # 路由工具
│   │
│   ├── layouts/               # 布局组件
│   │   ├── MainLayout.vue    # 主布局
│   │   └── components/       # 布局子组件
│   │
│   ├── views/                 # 页面组件
│   │   ├── Login.vue         # 登录页
│   │   ├── Home/             # 首页
│   │   ├── Tender/           # 投标管理
│   │   ├── Knowledge/        # 知识库
│   │   ├── Business/         # 商务应答
│   │   ├── System/           # 系统设置
│   │   └── Error/            # 错误页面
│   │
│   ├── components/            # 通用组件
│   │   ├── Card.vue
│   │   ├── Loading.vue
│   │   ├── Empty.vue
│   │   └── ...
│   │
│   ├── utils/                 # 工具函数（规划中）
│   │
│   ├── assets/                # 静态资源
│   │
│   ├── App.vue                # 根组件
│   └── main.ts                # 应用入口
│
├── public/                    # 公共资源
├── .env.development          # 开发环境配置
├── .env.production           # 生产环境配置
├── package.json              # 项目配置
├── vite.config.ts            # Vite配置
├── tsconfig.json             # TypeScript配置
└── README.md                 # 项目说明
```

---

## 🎯 核心模块详解

### 1. API服务层 (`/src/api`)

**设计原则**：
- 统一的请求/响应格式
- 自动错误处理和重试
- TypeScript类型安全
- SSE流式处理支持

**核心文件**：

#### `client.ts` - HTTP客户端
```typescript
// 功能特性：
- Axios实例封装
- CSRF Token自动注入
- 统一请求方法（GET/POST/PUT/DELETE/PATCH）
- 文件上传/下载支持
- 请求头管理
```

#### `interceptors.ts` - 拦截器
```typescript
// 请求拦截器：
- CSRF Token注入
- 请求日志记录
- 缓存控制

// 响应拦截器：
- 统一错误处理
- 自动重试（指数退避）
- 响应格式化
- 特殊状态码处理（401/403/404/500等）
```

#### `endpoints/` - API端点模块
- **tender.ts**: 项目管理、文档处理、文档融合、HITL工作流
- **company.ts**: 公司信息、资质文档管理
- **knowledge.ts**: 案例库、产品库、简历库、向量检索
- **business.ts**: 商务应答、点对点应答、技术方案、章节管理
- **auth.ts**: 登录、登出、用户信息

**使用示例**：
```typescript
import { tenderApi, businessApi } from '@/api'

// 获取项目列表
const projects = await tenderApi.getProjects({ page: 1, page_size: 20 })

// 启动商务应答生成
const task = await businessApi.startBusinessResponse({
  project_id: 1,
  company_id: 2,
  template_file: file
})
```

---

### 2. TypeScript类型系统 (`/src/types`)

**设计原则**：
- 完整的类型覆盖
- 严格的类型检查
- 接口复用
- 类型推断友好

**核心类型**：

#### `models.ts` - 数据模型（2000+行）
```typescript
// 核心业务模型
- User, Company, Project
- Document, Chapter, Requirement
- Case, Product, Resume
- AIModel, Task, HITLTask
- Qualification, FinancialInfo
```

#### `api.ts` - API类型（1500+行）
```typescript
// 统一响应格式
interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: string
  code?: number
}

// 分页响应
interface PaginatedApiResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

// SSE事件类型
interface SSEEvent {
  event: string
  data: any
  id?: string
}
```

---

### 3. Pinia状态管理 (`/src/stores`)

**设计原则**：
- 模块化设计
- TypeScript支持
- 持久化存储
- DevTools集成

**Store模块**：

#### `user.ts` - 用户状态
```typescript
interface UserState {
  userInfo: User | null
  isLoggedIn: boolean
  token: string | null
  permissions: string[]
}

// Actions
- login(credentials)
- logout()
- fetchUserInfo()
- updateUserInfo(data)
```

#### `company.ts` - 公司状态
```typescript
interface CompanyState {
  currentCompany: Company | null
  companies: Company[]
  qualifications: Qualification[]
}

// Actions
- setCurrentCompany(company)
- fetchCompanies()
- fetchQualifications(companyId)
```

#### `project.ts` - 项目状态
```typescript
interface ProjectState {
  currentProject: Project | null
  projects: Project[]
  documents: Document[]
  chapters: Chapter[]
}

// Actions
- setCurrentProject(project)
- fetchProjects()
- createProject(data)
- uploadDocument(file)
```

---

### 4. 组合式函数库 (`/src/composables`)

**设计原则**：
- 逻辑复用
- 响应式设计
- TypeScript类型安全
- 易于测试

**核心Composables**：

#### `useSSE.ts` - SSE流处理
```typescript
interface UseSSEOptions {
  autoConnect?: boolean
  onMessage?: (event: SSEEvent) => void
  onError?: (error: Error) => void
  reconnect?: boolean
  reconnectDelay?: number
}

function useSSE(url: string, options?: UseSSEOptions) {
  return {
    connect,
    disconnect,
    isConnected,
    error,
    lastEvent
  }
}
```

#### `useFileUpload.ts` - 文件上传
```typescript
interface UseFileUploadOptions {
  accept?: string
  maxSize?: number
  multiple?: boolean
  onProgress?: (progress: number) => void
  onSuccess?: (response: any) => void
  onError?: (error: Error) => void
}

function useFileUpload(options?: UseFileUploadOptions) {
  return {
    upload,
    selectFile,
    isDragging,
    isUploading,
    progress,
    error
  }
}
```

#### `useAsync.ts` - 异步处理
```typescript
interface UseAsyncOptions<T> {
  immediate?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
}

function useAsync<T>(
  asyncFn: () => Promise<T>,
  options?: UseAsyncOptions<T>
) {
  return {
    execute,
    cancel,
    isLoading,
    data,
    error,
    isSuccess,
    isError
  }
}
```

---

### 5. 路由系统 (`/src/router`)

**设计原则**：
- 懒加载优化
- 权限控制
- 路由守卫
- 动态路由

**路由结构**：

```typescript
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home/index.vue')
      },
      {
        path: 'tender',
        name: 'Tender',
        children: [
          { path: 'projects', name: 'TenderProjects', ... },
          { path: 'processing', name: 'TenderProcessing', ... }
        ]
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        children: [...]
      },
      {
        path: 'business',
        name: 'Business',
        children: [...]
      }
    ]
  }
]
```

**路由守卫**：
```typescript
// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 1. 检查登录状态
  // 2. 验证权限
  // 3. 设置页面标题
  // 4. 加载进度条
})

// 全局后置守卫
router.afterEach((to, from) => {
  // 1. 关闭加载进度条
  // 2. 页面埋点
})
```

---

## 🔧 技术特性

### 1. TypeScript严格模式
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### 2. Axios拦截器链
```typescript
// 请求链
Request → CSRF注入 → 日志记录 → 缓存控制 → 发送

// 响应链
Response → 格式检查 → 错误处理 → 重试逻辑 → 返回
```

### 3. SSE流式处理
```typescript
// EventSource封装
- 自动重连机制
- 心跳检测
- 错误处理
- 类型安全的事件监听
```

### 4. 文件上传
```typescript
// 多种上传方式
- 点击选择
- 拖拽上传
- 进度跟踪
- 大文件分片（规划中）
```

---

## 📝 编码规范

### 命名约定

#### 文件命名
```typescript
// Vue组件：PascalCase
UserProfile.vue
CompanyList.vue

// TypeScript文件：kebab-case
user-service.ts
api-client.ts

// Composables：camelCase (use前缀)
useAuth.ts
useTable.ts

// Stores：kebab-case
user-store.ts
```

#### 变量命名
```typescript
// 常量：UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 10 * 1024 * 1024

// 接口：PascalCase (I前缀)
interface IUser { ... }

// 类型：PascalCase
type UserRole = 'admin' | 'user'

// 变量：camelCase
const userName = 'John'
```

### 代码风格

#### Vue组件结构
```vue
<template>
  <!-- 模板 -->
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'

// 2. Props & Emits
interface Props {
  title: string
}
const props = defineProps<Props>()
const emit = defineEmits<{
  update: [value: string]
}>()

// 3. 响应式数据
const state = ref('')

// 4. 计算属性
const computedValue = computed(() => ...)

// 5. 方法
function handleClick() { ... }

// 6. 生命周期
onMounted(() => { ... })
</script>

<style scoped lang="scss">
/* 组件样式 */
</style>
```

#### API调用
```typescript
// 使用async/await
async function fetchData() {
  try {
    const response = await api.getData()
    // 处理数据
  } catch (error) {
    // 错误处理
  }
}

// 使用useAsync
const { execute, isLoading, data, error } = useAsync(
  () => api.getData()
)
```

---

## 🚀 性能优化

### 1. 路由懒加载
```typescript
// 使用动态导入
const UserProfile = () => import('@/views/UserProfile.vue')
```

### 2. 组件懒加载
```vue
<script setup>
import { defineAsyncComponent } from 'vue'

const HeavyComponent = defineAsyncComponent(
  () => import('./HeavyComponent.vue')
)
</script>
```

### 3. 请求优化
```typescript
// 请求取消
const controller = new AbortController()
apiClient.get('/data', { signal: controller.signal })

// 请求缓存（开发中）
```

### 4. 资源优化
```typescript
// Vite自动优化
- Tree Shaking
- Code Splitting
- Asset Inlining
- CSS Code Splitting
```

---

## 🔐 安全措施

### 1. CSRF保护
```typescript
// 自动注入CSRF Token
function getCsrfToken(): string | null {
  return document.cookie.match(/csrf_token=([^;]+)/)?.[1] || null
}
```

### 2. XSS防护
```vue
<!-- 自动转义 -->
<div>{{ userInput }}</div>

<!-- 危险HTML需显式标记 -->
<div v-html="sanitizedHtml"></div>
```

### 3. 权限控制
```typescript
// 路由级别
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  }
})

// 组件级别
<template>
  <button v-if="hasPermission('delete')">删除</button>
</template>
```

---

## 📦 构建与部署

### 开发环境
```bash
npm run dev
# 启动Vite开发服务器
# Hot Module Replacement (HMR)
# TypeScript类型检查
```

### 生产构建
```bash
npm run build
# TypeScript编译检查
# Vite优化打包
# 资源压缩
# Source Map生成
```

### 环境变量
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8110
VITE_APP_TITLE=元景AI标书系统（开发）

# .env.production
VITE_API_BASE_URL=https://api.production.com
VITE_APP_TITLE=元景AI标书系统
```

---

## 🧪 测试策略（规划中）

### 单元测试
```typescript
// Vitest
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('UserProfile', () => {
  it('renders correctly', () => {
    const wrapper = mount(UserProfile)
    expect(wrapper.text()).toContain('用户')
  })
})
```

### E2E测试
```typescript
// Playwright
test('login flow', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[name="username"]', 'admin')
  await page.fill('input[name="password"]', 'password')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/')
})
```

---

## 📚 相关文档

- [开发指南](./docs/DEVELOPMENT_GUIDE.md)（待创建）
- [API文档](./docs/API_REFERENCE.md)（待创建）
- [组件库文档](./docs/COMPONENTS.md)（待创建）
- [进度追踪](./INFRASTRUCTURE_PROGRESS.md)

---

## 🤝 贡献指南

### 开发流程
1. Clone仓库
2. 安装依赖：`npm install`
3. 启动开发服务器：`npm run dev`
4. 开发功能
5. 提交代码（遵循规范）

### Commit规范
```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具

# 示例
git commit -m "feat: 添加用户权限管理功能"
git commit -m "fix: 修复文件上传进度显示问题"
```

---

## 📞 联系方式

**项目负责人**: Claude Code
**技术支持**: [GitHub Issues](https://github.com/...)
**文档更新**: 2025-10-31

---

**版权所有 © 2025 元景AI**
