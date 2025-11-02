# API使用指南

> 完整的API服务层使用文档

## 📚 目录

- [快速开始](#快速开始)
- [API模块概览](#api模块概览)
- [使用示例](#使用示例)
- [错误处理](#错误处理)
- [文件上传下载](#文件上传下载)
- [SSE流式处理](#sse流式处理)
- [高级用法](#高级用法)

---

## 快速开始

### 1. 导入API模块

```typescript
// 导入特定API模块
import { tenderApi, companyApi, knowledgeApi, businessApi } from '@/api'

// 或导入API客户端（用于自定义请求）
import { apiClient } from '@/api'
```

### 2. 基本使用

```typescript
// 在Vue组件中使用
<script setup lang="ts">
import { ref } from 'vue'
import { tenderApi } from '@/api'

const projects = ref([])
const loading = ref(false)

async function loadProjects() {
  loading.value = true
  try {
    const response = await tenderApi.getProjects({ page: 1, page_size: 10 })
    if (response.success) {
      projects.value = response.data
    }
  } catch (error) {
    console.error('加载项目失败:', error)
  } finally {
    loading.value = false
  }
}
</script>
```

---

## API模块概览

### 1. Tender API (`tenderApi`)

**用途**: 投标处理、项目管理、文档融合

**核心方法**:
```typescript
// 项目管理
await tenderApi.getProjects({ page: 1, page_size: 10 })
await tenderApi.getProject(123)
await tenderApi.createProject({ name: '新项目', ... })
await tenderApi.updateProject(123, { name: '更新名称' })
await tenderApi.deleteProject(123)

// 文档上传
await tenderApi.uploadTenderDocument(projectId, file, (progress) => {
  console.log(`上传进度: ${progress}%`)
})

// 文档处理
await tenderApi.startTenderProcessing({ project_id: 123, ... })
await tenderApi.getTaskStatus('task_xxx')

// 文档融合
await tenderApi.getSourceDocuments(123)
await tenderApi.startDocumentMerge({ project_id: 123, ... })
```

### 2. Company API (`companyApi`)

**用途**: 公司管理、资质管理

**核心方法**:
```typescript
// 公司管理
await companyApi.getCompanies()
await companyApi.getCompany(123)
await companyApi.createCompany({ name: '新公司', ... })

// 资质管理
await companyApi.getCompanyQualifications(123)
await companyApi.getQualificationTypes()
await companyApi.uploadQualification(companyId, typeKey, file, data)
await companyApi.deleteQualification(456)

// 搜索
await companyApi.searchCompanies('关键词')
await companyApi.getExpiringQualifications(123, 30) // 30天内过期
```

### 3. Knowledge API (`knowledgeApi`)

**用途**: 知识库、案例库、简历库管理

**核心方法**:
```typescript
// 知识库
await knowledgeApi.getKnowledgeDocuments({ category: '技术方案' })
await knowledgeApi.uploadKnowledgeDocument({ file, title, ... })
await knowledgeApi.searchKnowledge({ query: '搜索关键词' })

// 案例库
await knowledgeApi.getCases({ company_id: 123 })
await knowledgeApi.createCase({ project_name: '案例名称', ... })

// 简历库
await knowledgeApi.getResumes({ position: '项目经理' })
await knowledgeApi.createResume({ name: '张三', ... })
await knowledgeApi.addProjectExperience(resumeId, { ... })
```

### 4. Business API (`businessApi`)

**用途**: 商务应答、点对点应答、技术方案生成

**核心方法**:
```typescript
// 商务应答
await businessApi.startBusinessResponse({ project_id: 123, ... })
await businessApi.getBusinessResponseResult('task_xxx')
await businessApi.downloadBusinessResponse('task_xxx', 'output.docx')

// 点对点应答
await businessApi.startPointToPoint({ project_id: 123, ... })

// 技术方案
await businessApi.startTechProposal({ project_id: 123, ... })

// 章节管理
await businessApi.getChapterTree(123)
await businessApi.createChapter({ title: '第一章', ... })

// AI模型
await businessApi.getAvailableModels()
```

### 5. Auth API (`authApi`)

**用途**: 用户认证、权限管理

**核心方法**:
```typescript
// 登录登出
await authApi.login({ username: 'admin', password: '123456' })
await authApi.logout()

// 用户信息
await authApi.getCurrentUser()
await authApi.updateCurrentUser({ email: 'new@email.com' })

// 密码管理
await authApi.changePassword({ old_password: '...', new_password: '...' })
```

---

## 使用示例

### 示例1: 加载项目列表（带分页）

```typescript
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tenderApi } from '@/api'
import type { Project } from '@/types'

const projects = ref<Project[]>([])
const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})
const loading = ref(false)

async function loadProjects() {
  loading.value = true
  try {
    const response = await tenderApi.getProjects({
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })

    if (response.success && response.data) {
      projects.value = response.data.items
      pagination.value.total = response.data.total
    }
  } catch (error) {
    console.error('加载项目失败:', error)
    // 错误已由拦截器统一处理，这里只需记录
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProjects()
})
</script>
```

### 示例2: 文件上传（带进度）

```typescript
<script setup lang="ts">
import { ref } from 'vue'
import { tenderApi } from '@/api'

const uploadProgress = ref(0)
const uploading = ref(false)

async function handleFileUpload(file: File, projectId: number) {
  uploading.value = true
  uploadProgress.value = 0

  try {
    const response = await tenderApi.uploadTenderDocument(
      projectId,
      file,
      (progress) => {
        uploadProgress.value = progress
        console.log(`上传进度: ${progress}%`)
      }
    )

    if (response.success) {
      console.log('上传成功:', response.data)
      // 处理上传成功后的逻辑
    }
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div>
    <input type="file" @change="handleFileChange" :disabled="uploading" />
    <div v-if="uploading">
      上传进度: {{ uploadProgress }}%
      <el-progress :percentage="uploadProgress" />
    </div>
  </div>
</template>
```

### 示例3: 创建新公司

```typescript
<script setup lang="ts">
import { ref } from 'vue'
import { companyApi } from '@/api'
import { ElMessage } from 'element-plus'

const formData = ref({
  name: '',
  code: '',
  address: '',
  contact_person: '',
  contact_phone: '',
  email: ''
})

async function submitForm() {
  try {
    const response = await companyApi.createCompany(formData.value)

    if (response.success) {
      ElMessage.success('公司创建成功')
      // 重置表单或跳转
    }
  } catch (error) {
    ElMessage.error('创建失败，请重试')
  }
}
</script>
```

### 示例4: 搜索知识库

```typescript
<script setup lang="ts">
import { ref, watch } from 'vue'
import { knowledgeApi } from '@/api'
import { useDebounceFn } from '@vueuse/core'

const searchQuery = ref('')
const searchResults = ref([])

// 防抖搜索
const debouncedSearch = useDebounceFn(async (query: string) => {
  if (!query.trim()) {
    searchResults.value = []
    return
  }

  try {
    const response = await knowledgeApi.searchKnowledge({
      query,
      top_k: 10
    })

    if (response.success) {
      searchResults.value = response.data || []
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}, 500)

watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery)
})
</script>
```

---

## 错误处理

### 统一错误处理

所有API调用的错误已由拦截器统一处理：

```typescript
// 拦截器已处理的错误类型
interface ApiError {
  message: string  // 错误消息
  code: number     // 状态码
  details?: any    // 详细信息
}

// 特殊状态码自动处理
401 → '未授权，请重新登录'
403 → '无权限访问'
404 → '请求的资源不存在'
422 → '请求参数验证失败'
500 → '服务器内部错误'
```

### 组件中的错误处理

```typescript
async function loadData() {
  try {
    const response = await tenderApi.getProjects()
    if (response.success) {
      // 处理成功
    }
  } catch (error) {
    // 错误已由拦截器处理（日志记录、重试等）
    // 这里只需处理UI反馈
    ElMessage.error('加载失败，请稍后重试')
  }
}
```

### 自定义错误处理

```typescript
import { apiClient } from '@/api'

try {
  const response = await apiClient.get('/custom-endpoint')
} catch (error: any) {
  if (error.code === 403) {
    // 处理权限错误
    router.push('/no-permission')
  } else if (error.code === 404) {
    // 处理资源不存在
    ElMessage.warning('资源不存在')
  } else {
    // 其他错误
    console.error('请求失败:', error.message)
  }
}
```

---

## 文件上传下载

### 上传文件（带进度）

```typescript
// 1. 单文件上传
const response = await tenderApi.uploadTenderDocument(
  projectId,
  file,
  (progress) => {
    console.log(`上传进度: ${progress}%`)
    // 更新UI进度条
  }
)

// 2. 批量上传资质
const files = [
  { file: file1, typeKey: 'business_license' },
  { file: file2, typeKey: 'iso_9001' }
]
await companyApi.batchUploadQualifications(companyId, files, (progress) => {
  console.log(`批量上传进度: ${progress}%`)
})
```

### 下载文件

```typescript
// 1. 下载文档（自动触发浏览器下载）
await tenderApi.downloadDocument(
  documentId,
  'output.docx', // 下载文件名
  (progress) => {
    console.log(`下载进度: ${progress}%`)
  }
)

// 2. 下载后获取Blob（用于预览等）
const blob = await apiClient.getInstance().get('/documents/123/download', {
  responseType: 'blob'
})
const url = window.URL.createObjectURL(blob.data)
// 在新窗口打开预览
window.open(url, '_blank')
```

---

## SSE流式处理

### 监听实时进度

```typescript
import { tenderSSE } from '@/api'

// 1. 启动任务
const response = await tenderApi.startDocumentMerge({ ... })
const taskId = response.data.task_id

// 2. 监听进度
const eventSource = tenderSSE.createMergeStream(taskId)

eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data)

  if (data.status === 'processing') {
    console.log(`进度: ${data.progress}%`)
    console.log(`消息: ${data.message}`)
  } else if (data.status === 'completed') {
    console.log('任务完成:', data.result)
    eventSource.close()
  } else if (data.status === 'failed') {
    console.error('任务失败:', data.error)
    eventSource.close()
  }
})

eventSource.addEventListener('error', (error) => {
  console.error('SSE连接错误:', error)
  eventSource.close()
})
```

### 商务应答流式生成

```typescript
import { businessSSE } from '@/api'

// 启动生成
const response = await businessApi.startBusinessResponseStream({ ... })
const taskId = response.data.task_id

// 监听流式输出
const eventSource = businessSSE.createBusinessResponseStream(taskId)

eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data)

  // 实时显示生成的内容
  if (data.content) {
    appendContent(data.content)
  }

  // 进度更新
  if (data.progress !== undefined) {
    updateProgress(data.progress)
  }
})
```

---

## 高级用法

### 1. 自定义请求配置

```typescript
import { apiClient } from '@/api'

// 使用Axios实例进行自定义请求
const response = await apiClient.getInstance().get('/custom-endpoint', {
  params: { key: 'value' },
  headers: { 'Custom-Header': 'value' },
  timeout: 60000 // 60秒超时
})
```

### 2. 请求取消

```typescript
import axios from 'axios'
import { apiClient } from '@/api'

const cancelTokenSource = axios.CancelToken.source()

try {
  const response = await apiClient.getInstance().get('/long-running-task', {
    cancelToken: cancelTokenSource.token
  })
} catch (error) {
  if (axios.isCancel(error)) {
    console.log('请求已取消')
  }
}

// 取消请求
function cancelRequest() {
  cancelTokenSource.cancel('用户取消了操作')
}
```

### 3. 并发请求

```typescript
import { tenderApi, companyApi } from '@/api'

// Promise.all 并发执行
async function loadAllData() {
  try {
    const [projects, companies, models] = await Promise.all([
      tenderApi.getProjects(),
      companyApi.getCompanies(),
      businessApi.getAvailableModels()
    ])

    // 处理所有数据
  } catch (error) {
    console.error('加载失败:', error)
  }
}
```

### 4. 设置全局请求头

```typescript
import { apiClient } from '@/api'

// 设置自定义请求头
apiClient.setHeader('X-Custom-Header', 'custom-value')

// 设置Authorization（登录后）
apiClient.setAuthToken('your-jwt-token')

// 移除请求头
apiClient.removeHeader('X-Custom-Header')
```

### 5. 手动配置重试

```typescript
import { apiClient, setupInterceptors } from '@/api'

// 重新配置拦截器
setupInterceptors(apiClient.getInstance(), {
  maxRetries: 5,    // 重试5次
  retryDelay: 2000  // 延迟2秒
})
```

---

## 最佳实践

### 1. 在Composables中封装API调用

```typescript
// composables/useProjects.ts
import { ref, computed } from 'vue'
import { tenderApi } from '@/api'
import type { Project } from '@/types'

export function useProjects() {
  const projects = ref<Project[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadProjects() {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.getProjects()
      if (response.success) {
        projects.value = response.data || []
      }
    } catch (err: any) {
      error.value = err.message || '加载失败'
    } finally {
      loading.value = false
    }
  }

  return {
    projects: computed(() => projects.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    loadProjects
  }
}
```

### 2. 使用TypeScript类型推导

```typescript
import type { Project, ApiResponse } from '@/types'

// 类型安全的API调用
const response: ApiResponse<Project> = await tenderApi.getProject(123)

// IDE会自动提示response.data的所有字段
if (response.success && response.data) {
  console.log(response.data.name) // 自动补全
}
```

### 3. 错误边界处理

```typescript
async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  fallback: T
): Promise<T> {
  try {
    return await apiCall()
  } catch (error) {
    console.error('API调用失败:', error)
    return fallback
  }
}

// 使用
const projects = await safeApiCall(
  () => tenderApi.getProjects().then(r => r.data || []),
  [] // 失败时返回空数组
)
```

---

## 常见问题

### Q1: 如何处理401未授权错误？

**A**: 拦截器已自动处理401错误，您可以监听全局事件：

```typescript
// main.ts
import { apiClient } from '@/api'

apiClient.getInstance().interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 跳转到登录页
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### Q2: 如何添加新的API端点？

**A**: 在 `src/api/endpoints/` 下的相应模块添加方法：

```typescript
// src/api/endpoints/tender.ts
export const tenderApi = {
  // 添加新方法
  async getProjectSummary(projectId: number) {
    return apiClient.get(`/projects/${projectId}/summary`)
  }
}
```

### Q3: CSRF Token从哪里来？

**A**: 拦截器自动从cookie或meta标签读取，无需手动处理。

### Q4: 如何调试API请求？

**A**: 开发环境下，所有请求/响应自动输出到控制台：

```
[API Request] { method: 'GET', url: '/projects', ... }
[API Response] { url: '/projects', status: 200, data: ... }
```

---

## 总结

本API服务层提供了：

✅ **类型安全** - 完整的TypeScript类型定义
✅ **自动重试** - 失败自动重试3次（指数退避）
✅ **错误处理** - 统一错误处理和格式化
✅ **CSRF保护** - 自动注入CSRF Token
✅ **进度跟踪** - 文件上传/下载进度回调
✅ **SSE支持** - 实时流式数据处理
✅ **模块化** - 按业务模块清晰划分

**开始使用**: 直接导入API模块，享受类型安全的开发体验！

```typescript
import { tenderApi, companyApi, knowledgeApi, businessApi } from '@/api'
```
