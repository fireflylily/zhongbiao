<template>
  <el-card class="demo-card">
    <template #header>
      <div class="card-header">
        <span>组合式函数演示</span>
        <el-tag type="success">composables/</el-tag>
      </div>
    </template>

    <!-- useNotification -->
    <el-divider content-position="left">
      <el-icon><Bell /></el-icon>
      useNotification (通知系统)
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="24">
        <demo-item label="消息通知">
          <el-space wrap>
            <el-button @click="showSuccessMsg" type="success">成功消息</el-button>
            <el-button @click="showWarningMsg" type="warning">警告消息</el-button>
            <el-button @click="showErrorMsg" type="danger">错误消息</el-button>
            <el-button @click="showInfoMsg" type="info">信息消息</el-button>
            <el-button @click="showConfirm" type="primary">确认对话框</el-button>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- useAsync -->
    <el-divider content-position="left">
      <el-icon><Loading /></el-icon>
      useAsync (异步处理)
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="异步加载状态">
          <el-space direction="vertical" style="width: 100%">
            <div>状态: {{ asyncState.loading ? '加载中...' : '已完成' }}</div>
            <div v-if="asyncState.error">错误: {{ asyncState.error }}</div>
            <div v-if="asyncState.data">数据: {{ asyncState.data }}</div>
            <el-space>
              <el-button @click="loadData" type="primary" :loading="asyncState.loading">
                加载数据
              </el-button>
              <el-button @click="loadDataWithError" type="danger" :loading="asyncState.loading">
                模拟错误
              </el-button>
            </el-space>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="并发请求">
          <el-space direction="vertical" style="width: 100%">
            <div>请求1: {{ concurrentState1.loading ? '加载中' : concurrentState1.data || '未加载' }}</div>
            <div>请求2: {{ concurrentState2.loading ? '加载中' : concurrentState2.data || '未加载' }}</div>
            <div>请求3: {{ concurrentState3.loading ? '加载中' : concurrentState3.data || '未加载' }}</div>
            <el-button @click="loadConcurrent" type="primary">并发加载</el-button>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- useFileUpload -->
    <el-divider content-position="left">
      <el-icon><UploadFilled /></el-icon>
      useFileUpload (文件上传)
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="文件选择">
          <el-space direction="vertical" style="width: 100%">
            <input
              ref="fileInputRef"
              type="file"
              @change="handleFileChange"
              accept=".pdf,.doc,.docx"
              style="display: none"
            />
            <el-button @click="selectFile" type="primary">选择文件</el-button>
            <div v-if="selectedFile">
              <div>文件名: {{ selectedFile.name }}</div>
              <div>文件大小: {{ formatFileSize(selectedFile.size) }}</div>
              <div>文件类型: {{ selectedFile.type }}</div>
            </div>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="上传进度">
          <el-space direction="vertical" style="width: 100%">
            <el-progress
              v-if="uploadProgress > 0"
              :percentage="uploadProgress"
              :status="uploadProgress === 100 ? 'success' : undefined"
            />
            <el-button
              @click="simulateUpload"
              type="success"
              :disabled="!selectedFile || uploadProgress > 0"
            >
              模拟上传
            </el-button>
            <div v-if="uploadProgress === 100">上传完成！</div>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- useForm -->
    <el-divider content-position="left">
      <el-icon><Edit /></el-icon>
      useForm (表单处理)
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="24">
        <demo-item label="表单验证与提交">
          <el-form :model="demoForm" :rules="formRules" ref="formRef" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="demoForm.username" placeholder="请输入用户名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="demoForm.email" placeholder="请输入邮箱" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="简介" prop="bio">
              <el-input
                v-model="demoForm.bio"
                type="textarea"
                :rows="3"
                placeholder="请输入简介"
              />
            </el-form-item>

            <el-form-item>
              <el-space>
                <el-button type="primary" @click="submitDemoForm" :loading="formSubmitting">
                  提交表单
                </el-button>
                <el-button @click="resetDemoForm">重置</el-button>
              </el-space>
            </el-form-item>
          </el-form>
        </demo-item>
      </el-col>
    </el-row>

    <!-- useSSE (说明) -->
    <el-divider content-position="left">
      <el-icon><Connection /></el-icon>
      useSSE (服务器推送事件)
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="24">
        <demo-item label="SSE流式处理">
          <el-alert
            title="SSE演示说明"
            type="info"
            description="SSE (Server-Sent Events) 用于实时接收服务器推送的数据流，常用于AI生成、进度更新等场景。在实际业务页面中会连接到真实的后端API。"
            :closable="false"
          />
          <el-space direction="vertical" style="width: 100%; margin-top: 16px">
            <div>
              <strong>使用示例:</strong>
            </div>
            <el-code>
              <pre>const { start, stop, isConnected, messages } = useSSE('/api/stream')</pre>
            </el-code>
            <div style="font-size: 12px; color: #909399">
              在商务应答、技术方案等模块中已集成使用，可查看实际业务页面了解详情。
            </div>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  Bell,
  Loading,
  UploadFilled,
  Edit,
  Connection
} from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { useNotification, useAsync } from '@/composables'
import { required, emailRule, formatFileSize } from '@/utils'

// ============ useNotification ============
const { success, warning, error, info, confirm } = useNotification()

function showSuccessMsg() {
  success('操作成功！', '这是一条成功消息')
}

function showWarningMsg() {
  warning('注意！', '这是一条警告消息')
}

function showErrorMsg() {
  error('错误！', '这是一条错误消息')
}

function showInfoMsg() {
  info('提示', '这是一条普通消息')
}

async function showConfirm() {
  try {
    await confirm('确认操作', '您确定要执行此操作吗？', 'warning')
    success('已确认', '您点击了确认按钮')
  } catch {
    info('已取消', '您点击了取消按钮')
  }
}

// ============ useAsync ============
// 单个异步请求
const mockApiCall = (delay: number = 1000, shouldFail: boolean = false): Promise<string> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (shouldFail) {
        reject(new Error('模拟请求失败'))
      } else {
        resolve('加载成功的数据')
      }
    }, delay)
  })
}

const { execute, loading, data, error: asyncError } = useAsync(mockApiCall)

const asyncState = reactive({
  loading,
  data,
  error: asyncError
})

async function loadData() {
  await execute(1500, false)
}

async function loadDataWithError() {
  await execute(1000, true)
}

// 并发请求
const { execute: execute1, loading: loading1, data: data1 } = useAsync(mockApiCall)
const { execute: execute2, loading: loading2, data: data2 } = useAsync(mockApiCall)
const { execute: execute3, loading: loading3, data: data3 } = useAsync(mockApiCall)

const concurrentState1 = reactive({ loading: loading1, data: data1 })
const concurrentState2 = reactive({ loading: loading2, data: data2 })
const concurrentState3 = reactive({ loading: loading3, data: data3 })

async function loadConcurrent() {
  await Promise.all([execute1(800, false), execute2(1200, false), execute3(1000, false)])
}

// ============ useFileUpload ============
const fileInputRef = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const uploadProgress = ref(0)

function selectFile() {
  fileInputRef.value?.click()
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    uploadProgress.value = 0
  }
}

function simulateUpload() {
  if (!selectedFile.value) return

  uploadProgress.value = 0
  const interval = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      success('上传成功', `文件 ${selectedFile.value?.name} 已上传完成`)
    }
  }, 300)
}

// ============ useForm ============
const formRef = ref<FormInstance>()
const formSubmitting = ref(false)

const demoForm = reactive({
  username: '',
  email: '',
  bio: ''
})

const formRules = {
  username: [required('请输入用户名'), { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }],
  email: [required('请输入邮箱'), emailRule()],
  bio: [{ max: 200, message: '最多200个字符', trigger: 'blur' }]
}

async function submitDemoForm() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    formSubmitting.value = true

    // 模拟API调用
    await new Promise((resolve) => setTimeout(resolve, 1500))

    formSubmitting.value = false
    success('提交成功', '表单数据已提交')
  } catch (error) {
    formSubmitting.value = false
  }
}

function resetDemoForm() {
  formRef.value?.resetFields()
}
</script>

<script lang="ts">
// DemoItem 组件
import { defineComponent, h } from 'vue'

const DemoItem = defineComponent({
  name: 'DemoItem',
  props: {
    label: String,
    code: String
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'demo-item' }, [
        h('div', { class: 'demo-label' }, props.label),
        h('div', { class: 'demo-result' }, slots.default?.()),
        props.code ? h('div', { class: 'demo-code' }, h('code', props.code)) : null
      ])
  }
})

// 代码显示组件
const ElCode = defineComponent({
  name: 'ElCode',
  setup(_, { slots }) {
    return () =>
      h(
        'div',
        {
          style: {
            background: '#f5f7fa',
            padding: '12px',
            borderRadius: '4px',
            fontSize: '12px',
            fontFamily: 'monospace'
          }
        },
        slots.default?.()
      )
  }
})

export default {
  components: { DemoItem, ElCode }
}
</script>

<style scoped lang="scss">
.demo-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.demo-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;

  .demo-label {
    font-size: 14px;
    color: #606266;
    margin-bottom: 12px;
    font-weight: 500;
  }

  .demo-result {
    font-size: 14px;
    color: #303133;
    padding: 12px;
    background: white;
    border-radius: 4px;
  }

  .demo-code {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;

    code {
      background: #e9ecef;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
  }
}

:deep(.el-divider) {
  margin: 24px 0;

  .el-divider__text {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #409eff;
  }
}

:deep(.el-form) {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

:deep(.el-alert) {
  margin: 8px 0;
}
</style>
