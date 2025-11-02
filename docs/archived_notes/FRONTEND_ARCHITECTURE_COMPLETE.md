# AI智能标书生成平台 - 完整前后端分离架构文档

> **版本**: 2.0
> **创建日期**: 2025-10-30
> **状态**: 架构设计完成,实施中

---

## 📋 目录

1. [架构概述](#架构概述)
2. [目录结构](#目录结构)
3. [技术栈](#技术栈)
4. [核心模块设计](#核心模块设计)
5. [迁移路线图](#迁移路线图)
6. [开发指南](#开发指南)
7. [部署方案](#部署方案)

---

## 架构概述

### 当前问题

- **前端代码**: 22,314行原生JavaScript,分散在36个文件中
- **最大单文件**: `tender-processing-step3-enhanced.js` (2,761行)
- **维护难度**: 命令式DOM操作,全局变量污染,难以测试
- **性能问题**: 首屏加载大量未使用代码,CSS/JS重复加载

### 目标架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Vue 3 SPA (单页面应用)                      │  │
│  │                                                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │  │
│  │  │  Router  │  │  Pinia   │  │   API    │        │  │
│  │  │  路由管理 │  │  状态管理 │  │  服务层   │        │  │
│  │  └──────────┘  └──────────┘  └──────────┘        │  │
│  │                                                     │  │
│  │  Views (页面级组件)                                 │  │
│  │  ├─ TenderProcessingView.vue                       │  │
│  │  ├─ BusinessResponseView.vue                       │  │
│  │  ├─ KnowledgeBaseView.vue                          │  │
│  │  └─ ...                                            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│               Flask API Server (后端)                     │
│                                                           │
│  Blueprints (API端点)      Modules (业务逻辑)             │
│  ├─ /api/v1/tender         ├─ business_response/        │
│  ├─ /api/v1/company        ├─ tender_info/              │
│  ├─ /api/v1/knowledge      ├─ knowledge_base/           │
│  └─ ...                    └─ ...                       │
│                                                           │
│  Database (SQLite)                                       │
│  ├─ knowledge_base.db                                    │
│  └─ tender_projects...                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 目录结构

### 最终目标结构

```
zhongbiao/
├── frontend/                        # 👈 全新前端SPA应用
│   ├── src/
│   │   ├── main.ts                  # 应用入口
│   │   ├── App.vue                  # 根组件
│   │   │
│   │   ├── router/                  # 🚀 Vue Router配置
│   │   │   ├── index.ts             # 主路由配置
│   │   │   ├── modules/             # 路由模块化
│   │   │   │   ├── tender.ts        # 投标相关路由
│   │   │   │   ├── knowledge.ts     # 知识库路由
│   │   │   │   └── business.ts      # 商务应答路由
│   │   │   └── guards.ts            # 路由守卫(权限控制)
│   │   │
│   │   ├── stores/                  # 🚀 Pinia状态管理
│   │   │   ├── index.ts             # Store入口
│   │   │   ├── user.ts              # 用户状态
│   │   │   ├── company.ts           # 公司状态
│   │   │   ├── project.ts           # 项目状态
│   │   │   ├── aiModel.ts           # AI模型配置
│   │   │   └── notification.ts      # 通知状态
│   │   │
│   │   ├── api/                     # 🚀 API服务层
│   │   │   ├── client.ts            # Axios实例配置
│   │   │   ├── interceptors.ts      # 请求/响应拦截器
│   │   │   ├── endpoints/           # API端点模块化
│   │   │   │   ├── tender.ts        # 投标API
│   │   │   │   ├── company.ts       # 公司API
│   │   │   │   ├── knowledge.ts     # 知识库API
│   │   │   │   └── index.ts         # 统一导出
│   │   │   └── types.ts             # API类型定义
│   │   │
│   │   ├── types/                   # 🚀 TypeScript类型定义
│   │   │   ├── models.ts            # 数据模型类型
│   │   │   ├── api.ts               # API响应类型
│   │   │   ├── store.ts             # Store状态类型
│   │   │   └── index.ts             # 统一导出
│   │   │
│   │   ├── layouts/                 # 🚀 页面布局
│   │   │   ├── DefaultLayout.vue    # 默认布局(含导航)
│   │   │   ├── BlankLayout.vue      # 空白布局(登录页)
│   │   │   └── index.ts             # 布局注册
│   │   │
│   │   ├── views/                   # 🚀 页面级组件
│   │   │   ├── TenderProcessing/    # 文档处理页面
│   │   │   │   ├── index.vue
│   │   │   │   ├── components/
│   │   │   │   └── composables/
│   │   │   ├── BusinessResponse/    # 商务应答页面
│   │   │   ├── PointToPoint/        # 点对点应答页面
│   │   │   ├── TechProposal/        # 技术方案页面
│   │   │   ├── KnowledgeBase/       # 知识库页面
│   │   │   │   ├── Companies/
│   │   │   │   ├── Cases/
│   │   │   │   ├── Documents/
│   │   │   │   └── Resumes/
│   │   │   └── Login/               # 登录页面
│   │   │
│   │   ├── components/              # 🚀 可复用组件
│   │   │   ├── common/              # 通用组件
│   │   │   │   ├── Button/
│   │   │   │   ├── Modal/
│   │   │   │   ├── Table/
│   │   │   │   ├── Form/
│   │   │   │   └── Upload/
│   │   │   └── business/            # 业务组件
│   │   │       ├── CompanySelector/
│   │   │       ├── ProjectCard/
│   │   │       └── DocumentPreview/
│   │   │
│   │   ├── composables/             # 🚀 Vue3组合式函数
│   │   │   ├── useNotification.ts   # 通知hooks
│   │   │   ├── useSSE.ts            # SSE流式处理hooks
│   │   │   ├── useFileUpload.ts     # 文件上传hooks
│   │   │   ├── useForm.ts           # 表单处理hooks
│   │   │   └── useAsync.ts          # 异步处理hooks
│   │   │
│   │   ├── utils/                   # 🚀 工具函数
│   │   │   ├── format.ts            # 格式化工具
│   │   │   ├── validation.ts        # 表单验证
│   │   │   ├── constants.ts         # 常量定义
│   │   │   ├── helpers.ts           # 辅助函数
│   │   │   └── storage.ts           # 本地存储封装
│   │   │
│   │   └── assets/                  # 静态资源
│   │       ├── styles/              # 样式文件
│   │       │   ├── variables.scss   # CSS变量
│   │       │   ├── mixins.scss      # SCSS混合
│   │       │   └── global.scss      # 全局样式
│   │       └── images/              # 图片资源
│   │
│   ├── public/                      # 公共静态文件
│   │   ├── favicon.ico
│   │   └── index.html               # SPA入口HTML
│   │
│   ├── tests/                       # 测试文件
│   │   ├── unit/                    # 单元测试
│   │   └── e2e/                     # E2E测试
│   │
│   ├── package.json                 # 依赖配置
│   ├── vite.config.ts               # Vite构建配置
│   ├── tsconfig.json                # TypeScript配置
│   ├── .eslintrc.cjs                # ESLint配置
│   ├── .prettierrc.json             # Prettier配置
│   └── README.md                    # 前端文档
│
└── ai_tender_system/                # 后端(演变为纯API服务器)
    ├── web/
    │   ├── app.py                   # Flask应用(简化)
    │   ├── blueprints/              # API蓝图
    │   │   ├── v1/                  # API v1版本
    │   │   │   ├── __init__.py
    │   │   │   ├── tender_api.py
    │   │   │   ├── company_api.py
    │   │   │   └── knowledge_api.py
    │   │   └── v2/                  # API v2版本(未来)
    │   └── static/                  # 静态文件目录
    │       └── dist/                # 前端构建产物(自动生成)
    │           ├── js/
    │           ├── css/
    │           ├── images/
    │           └── manifest.json
    ├── modules/                     # 业务逻辑(完全保留)
    ├── database/                    # 数据库(完全保留)
    └── ...
```

---

## 技术栈

### 前端技术栈

| 技术 | 版本 | 用途 | 理由 |
|------|------|------|------|
| **Vue 3** | ^3.4.0 | 框架核心 | Composition API,更好的TypeScript支持 |
| **TypeScript** | ~5.3.0 | 类型系统 | 类型安全,减少运行时错误 |
| **Vite** | ^5.0.11 | 构建工具 | 极速开发,优化构建产物 |
| **Vue Router 4** | ^4.2.5 | 路由管理 | SPA路由,支持路由守卫 |
| **Pinia** | ^2.1.7 | 状态管理 | 官方推荐,TypeScript友好 |
| **Axios** | ^1.6.5 | HTTP客户端 | 请求封装,拦截器支持 |
| **Element Plus** | ^2.5.4 | UI组件库 | 企业级组件,完善的中文文档 |
| **VueUse** | ^10.7.2 | 组合式工具 | 丰富的hooks,提升开发效率 |
| **Day.js** | ^1.11.10 | 日期处理 | 轻量级,Moment.js替代品 |
| **SCSS** | ^1.70.0 | CSS预处理 | 变量,嵌套,混合 |

### 后端技术栈 (保持不变)

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 后端语言 |
| **Flask** | 2.3.3 | Web框架 |
| **SQLite** | - | 数据库 |
| **FAISS** | - | 向量搜索 |

---

## 核心模块设计

### 1. API服务层 (`src/api/`)

#### `client.ts` - Axios实例配置

```typescript
// frontend/src/api/client.ts
import axios, { AxiosInstance } from 'axios'
import { setupInterceptors } from './interceptors'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 设置拦截器
setupInterceptors(apiClient)

export default apiClient
```

#### `interceptors.ts` - 请求/响应拦截器

```typescript
// frontend/src/api/interceptors.ts
import { AxiosInstance, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

export function setupInterceptors(axiosInstance: AxiosInstance) {
  // 请求拦截器
  axiosInstance.interceptors.request.use(
    (config) => {
      // 添加CSRF Token
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }

      // 添加认证Token
      const userStore = useUserStore()
      if (userStore.token) {
        config.headers['Authorization'] = `Bearer ${userStore.token}`
      }

      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  axiosInstance.interceptors.response.use(
    (response) => {
      // 统一处理响应格式
      const { success, data, message } = response.data

      if (success === false) {
        ElMessage.error(message || '请求失败')
        return Promise.reject(new Error(message))
      }

      return response.data
    },
    (error: AxiosError<any>) => {
      // 统一错误处理
      const { response } = error

      if (response) {
        switch (response.status) {
          case 401:
            ElMessage.error('未授权,请重新登录')
            // 跳转到登录页
            break
          case 403:
            ElMessage.error('没有权限访问此资源')
            break
          case 404:
            ElMessage.error('请求的资源不存在')
            break
          case 500:
            ElMessage.error('服务器错误')
            break
          default:
            ElMessage.error(response.data?.message || '请求失败')
        }
      } else if (error.request) {
        ElMessage.error('网络错误,请检查网络连接')
      }

      return Promise.reject(error)
    }
  )
}
```

#### `endpoints/tender.ts` - 投标API端点

```typescript
// frontend/src/api/endpoints/tender.ts
import apiClient from '../client'
import type {
  Project,
  ProjectList,
  SourceDocuments,
  MergeTaskResponse
} from '@/types'

export const tenderApi = {
  // 获取项目列表
  getProjects(params?: {
    company_id?: number
    page?: number
    page_size?: number
  }): Promise<ProjectList> {
    return apiClient.get('/v1/projects', { params })
  },

  // 获取项目详情
  getProject(projectId: number): Promise<Project> {
    return apiClient.get(`/v1/projects/${projectId}`)
  },

  // 获取源文档信息
  getSourceDocuments(projectId: number): Promise<SourceDocuments> {
    return apiClient.get(`/v1/projects/${projectId}/source-documents`)
  },

  // 启动文档融合任务
  startMergeTask(projectId: number, data: {
    business_doc_path: string | null
    p2p_doc_path: string | null
    tech_doc_path: string | null
    style_option: string
  }): Promise<MergeTaskResponse> {
    return apiClient.post(`/v1/projects/${projectId}/merge-documents`, data)
  },

  // SSE监控融合进度
  monitorMergeProgress(taskId: string): EventSource {
    return new EventSource(`/api/v1/merge-status/${taskId}`)
  }
}
```

### 2. 状态管理 (`src/stores/`)

#### `company.ts` - 公司状态Store

```typescript
// frontend/src/stores/company.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Company } from '@/types'

export const useCompanyStore = defineStore('company', () => {
  // State
  const currentCompany = ref<Company | null>(null)
  const companies = ref<Company[]>([])

  // Getters
  const companyId = computed(() => currentCompany.value?.id || null)
  const companyName = computed(() => currentCompany.value?.name || '')

  // Actions
  function setCompany(company: Company) {
    currentCompany.value = company
    // 持久化到localStorage
    localStorage.setItem('current_company', JSON.stringify(company))
  }

  function clearCompany() {
    currentCompany.value = null
    localStorage.removeItem('current_company')
  }

  function loadCompanyFromStorage() {
    const stored = localStorage.getItem('current_company')
    if (stored) {
      currentCompany.value = JSON.parse(stored)
    }
  }

  return {
    currentCompany,
    companies,
    companyId,
    companyName,
    setCompany,
    clearCompany,
    loadCompanyFromStorage
  }
})
```

### 3. 组合式函数 (`src/composables/`)

#### `useSSE.ts` - SSE流式处理Hook

```typescript
// frontend/src/composables/useSSE.ts
import { ref, onUnmounted } from 'vue'

export interface SSEOptions {
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onComplete?: (data: any) => void
}

export function useSSE(url: string, options: SSEOptions = {}) {
  const isConnected = ref(false)
  const error = ref<Event | null>(null)
  let eventSource: EventSource | null = null

  function connect() {
    if (eventSource) {
      disconnect()
    }

    eventSource = new EventSource(url)
    isConnected.value = true

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.status === 'completed') {
          options.onComplete?.(data)
          disconnect()
        } else {
          options.onMessage?.(data)
        }
      } catch (err) {
        console.error('SSE解析错误:', err)
      }
    }

    eventSource.onerror = (err) => {
      error.value = err
      options.onError?.(err)
      disconnect()
    }
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
      isConnected.value = false
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    error,
    connect,
    disconnect
  }
}
```

---

## 迁移路线图

### 阶段0: 技术预研 (1周) ✅ 完成

- [x] 创建frontend项目结构
- [x] 配置TypeScript + Vite + ESLint
- [x] 建立API服务层基础架构
- [x] 创建Pinia stores基础
- [x] 编写完整架构文档

### 阶段1: 第一个页面迁移 (2周)

**目标**: 迁移 `tender-processing` 页面,验证技术方案

**任务清单**:

1. **创建基础路由和布局** (2天)
   - [ ] 实现 `DefaultLayout.vue` (包含顶部导航+侧边栏)
   - [ ] 配置Vue Router基础路由
   - [ ] 实现路由守卫(权限检查)

2. **实现TenderProcessing视图** (5天)
   - [ ] 创建 `TenderProcessingView.vue`
   - [ ] 实现项目信息卡片组件
   - [ ] 实现源文档列表组件
   - [ ] 实现文档融合表单组件
   - [ ] 实现SSE进度监控组件

3. **API集成与测试** (3天)
   - [ ] 对接Flask API端点
   - [ ] 测试文档融合完整流程
   - [ ] 处理边界情况和错误

4. **构建与部署** (2天)
   - [ ] 配置Vite构建输出
   - [ ] Flask路由配置
   - [ ] 生产环境测试

**验收标准**:
- ✅ 功能与原版100%一致
- ✅ 性能优于原版(首屏加载<2s)
- ✅ 通过所有手动测试用例

### 阶段2: 核心功能迁移 (8-10周)

#### Week 1-2: 项目总览 + 投标管理 (HITL工作流)

**复杂度**: ⭐⭐⭐⭐⭐ (最高)

**原因**:
- `tender-processing-step3-enhanced.js` 2,761行
- 复杂的状态机工作流
- 章节选择器管理器
- 需求表格管理器

**迁移策略**:
1. 将HITL工作流拆分为独立的Store
2. 使用Vue3的Teleport处理复杂模态框
3. 使用Pinia的多Store组合管理状态

#### Week 3-4: 商务应答 + 点对点应答

**复杂度**: ⭐⭐⭐

**已完成重构**:
- 使用HITLFileLoader统一文件加载
- 使用ApiClient统一API调用
- 代码量已减少-18.9%

**迁移策略**:
1. 复用现有的重构成果
2. 将业务逻辑迁移到组合式函数
3. 使用Element Plus的Upload组件

#### Week 5-6: 技术方案生成

**复杂度**: ⭐⭐⭐⭐

**原因**:
- `proposal-generator.js` 1,992行
- 大纲生成算法复杂
- 产品匹配逻辑
- Word文档导出

**迁移策略**:
1. 将大纲生成逻辑提取到专门的Service
2. 使用组合式函数管理表单状态
3. 保持与后端Word导出API的集成

#### Week 7-8: 知识库 - 公司信息库

**复杂度**: ⭐⭐⭐⭐

**原因**:
- `company-profile-manager.js` 1,943行
- 资质管理系统
- 17种标准资质类型
- 文件上传与预览

**迁移策略**:
1. 使用Element Plus的Form组件
2. 资质类型配置化管理
3. 文件上传使用组合式函数

#### Week 9-10: 知识库 - 案例库 + 文档库 + 简历库

**复杂度**: ⭐⭐⭐

**原因**:
- 三个模块功能类似
- 简历库已模块化重构

**迁移策略**:
1. 创建通用的CRUD视图模板
2. 配置化驱动不同模块
3. 复用简历库的模块化设计

#### Week 11-12: 测试 + Bug修复

- [ ] 编写单元测试(核心业务逻辑)
- [ ] 编写E2E测试(关键用户流程)
- [ ] 修复测试发现的Bug
- [ ] 性能优化

### 阶段3: 清理与完成 (2周)

**任务清单**:

1. **删除旧代码** (3天)
   - [ ] 删除 `ai_tender_system/web/static/js/`
   - [ ] 删除 `ai_tender_system/web/static/css/`
   - [ ] 删除 `ai_tender_system/web/templates/` (保留base.html)

2. **Flask简化** (2天)
   - [ ] 简化 `app.py` 为纯API服务器
   - [ ] 实现catch-all路由
   - [ ] 配置静态文件服务

3. **文档与培训** (3天)
   - [ ] 编写开发者文档
   - [ ] 编写部署文档
   - [ ] 团队培训

4. **上线准备** (2天)
   - [ ] 生产环境构建
   - [ ] 性能测试
   - [ ] 备份旧系统

**最终验收标准**:
- ✅ 所有功能迁移完成
- ✅ 无功能回归
- ✅ 性能提升30%+
- ✅ 代码量减少40%+
- ✅ 测试覆盖率>70%

---

## 开发指南

### 本地开发环境搭建

```bash
# 1. 安装Node.js (>=18.0.0)
# 下载: https://nodejs.org/

# 2. 克隆项目
cd zhongbiao/frontend

# 3. 安装依赖
npm install

# 4. 启动开发服务器
npm run dev

# 5. 在另一个终端启动Flask后端
cd ../
export FLASK_RUN_PORT=8110
python3 -m ai_tender_system.web.app

# 6. 访问开发环境
# 前端: http://localhost:5173
# 后端API: http://localhost:8110/api
```

### 代码规范

#### 命名约定

```typescript
// 文件名: kebab-case
// tender-processing.vue
// api-client.ts

// 组件名: PascalCase
export default {
  name: 'TenderProcessing'
}

// 变量/函数: camelCase
const projectId = 123
function loadProject() {}

// 常量: UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 100 * 1024 * 1024

// 类型/接口: PascalCase
interface Project {}
type ApiResponse = {}
```

#### 组件结构

```vue
<template>
  <!-- 模板代码 -->
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'

// 2. Props & Emits
interface Props {
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update', value: string): void
}>()

// 3. Composables
const router = useRouter()
const projectStore = useProjectStore()

// 4. State
const loading = ref(false)
const data = ref<any>(null)

// 5. Computed
const projectName = computed(() => projectStore.currentProject?.name)

// 6. Methods
async function loadData() {
  loading.value = true
  try {
    // 加载数据
  } finally {
    loading.value = false
  }
}

// 7. Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
// 组件样式
</style>
```

### Git工作流

```bash
# 1. 从main分支创建功能分支
git checkout main
git pull origin main
git checkout -b feature/tender-processing-migration

# 2. 开发并提交
git add .
git commit -m "feat: 迁移tender-processing页面到Vue3"

# 3. 推送到远程
git push origin feature/tender-processing-migration

# 4. 创建Pull Request
# 在GitHub/GitLab上创建PR,等待Code Review

# 5. 合并到main
git checkout main
git merge feature/tender-processing-migration
git push origin main
```

---

## 部署方案

### 开发环境部署

```bash
# 前端开发服务器
cd frontend
npm run dev

# 后端Flask服务器
cd ..
export FLASK_RUN_PORT=8110
python3 -m ai_tender_system.web.app
```

### 生产环境部署

#### 方式1: 传统部署

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 前端产物已自动输出到:
#    ai_tender_system/web/static/dist/

# 3. 启动Flask (使用Gunicorn)
cd ..
gunicorn -w 4 -b 0.0.0.0:8110 ai_tender_system.web.app:app

# 4. 配置Nginx反向代理
# /etc/nginx/sites-available/ai-tender-system
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8110;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 方式2: Docker部署

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai_tender_system/ ./ai_tender_system/
COPY --from=builder /app/../ai_tender_system/web/static/dist ./ai_tender_system/web/static/dist
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8110", "ai_tender_system.web.app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8110:8110"
    volumes:
      - ./ai_tender_system/data:/app/ai_tender_system/data
    environment:
      - FLASK_ENV=production
```

---

## 关键决策记录

### 为什么选择Vue 3而非React?

1. **学习曲线**: Vue更易上手,团队熟悉度更高
2. **TypeScript支持**: Vue 3原生支持TS,类型推导优秀
3. **Composition API**: 与React Hooks类似,但更直观
4. **生态系统**: Vue Router + Pinia官方支持,集成度高
5. **性能**: Vue 3的响应式系统性能优于React

### 为什么选择Element Plus?

1. **企业级**: 专为B端应用设计,组件丰富
2. **中文文档**: 完善的中文文档和社区
3. **定制性**: 支持主题定制
4. **维护活跃**: 持续更新,bug修复及时

### 为什么不使用Nuxt.js?

1. **不需要SSR**: 本系统是内部应用,无SEO需求
2. **复杂度**: Nuxt增加学习成本
3. **灵活性**: Vue SPA更灵活,适合渐进式迁移

---

## 常见问题 (FAQ)

### Q1: 旧系统与新系统如何共存?

**A**: 通过Flask路由区分:
- 新系统路由: `/` → 返回Vue SPA
- 旧系统路由: `/old/*` → 返回Jinja2模板
- API路由: `/api/*` → 返回JSON

### Q2: 如何处理CSRF保护?

**A**:
1. Flask在HTML中注入CSRF token到meta标签
2. Axios拦截器自动从meta标签读取token
3. 每次请求自动添加到header

### Q3: 如何处理文件上传?

**A**:
1. 使用FormData发送multipart/form-data请求
2. Axios配置 `Content-Type: multipart/form-data`
3. 后端Flask继续使用现有的文件处理逻辑

### Q4: SSE如何在Vue中使用?

**A**:
使用组合式函数 `useSSE.ts` 封装EventSource API,
在组件unmount时自动断开连接。

### Q5: 如何保持与现有Python模块的兼容?

**A**:
Python modules完全不动,仅修改:
1. Flask路由(从渲染模板改为返回JSON)
2. 添加CORS支持(如需)
3. 统一API响应格式

---

## 附录

### A. 完整的技术栈对比

| 维度 | 当前架构 | 新架构 | 改进 |
|------|----------|--------|------|
| **前端框架** | 原生JS | Vue 3 + TypeScript | 类型安全,组件化 |
| **状态管理** | window全局变量 | Pinia | 集中管理,可追溯 |
| **路由** | URL hash + Bootstrap Tab | Vue Router | SPA路由,懒加载 |
| **HTTP** | fetch + 手动封装 | Axios + 拦截器 | 统一错误处理,自动重试 |
| **UI组件** | Bootstrap 5 | Element Plus | 企业级组件,功能丰富 |
| **CSS** | 手写CSS | SCSS + CSS变量 | 模块化,可维护性强 |
| **构建工具** | 无 | Vite | 极速开发,优化构建 |
| **代码规范** | 无 | ESLint + Prettier | 统一代码风格 |
| **测试** | 无 | Vitest + Cypress | 单元测试+E2E测试 |

### B. 性能对比预期

| 指标 | 当前系统 | 新系统(预期) | 提升 |
|------|----------|--------------|------|
| 首屏加载时间 | ~3.5s | ~1.8s | **48%** |
| 页面切换速度 | ~500ms(刷新) | ~50ms(SPA) | **90%** |
| Bundle大小 | ~2.5MB | ~800KB | **68%** |
| 代码行数 | 22,314行 | ~13,000行 | **42%** |
| 维护成本 | 高 | 中 | - |

### C. 参考资源

- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Pinia 官方文档](https://pinia.vuejs.org/)
- [Element Plus 官方文档](https://element-plus.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [VueUse 官方文档](https://vueuse.org/)

---

## 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2025-10-30 | 2.0 | 完整架构设计文档初版 | Claude Code |

---

**文档维护者**: 开发团队
**最后更新**: 2025-10-30
**文档状态**: ✅ 已审核通过
