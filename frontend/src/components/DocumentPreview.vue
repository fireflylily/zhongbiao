<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="90%"
    :before-close="handleClose"
    destroy-on-close
    class="document-preview-dialog"
  >
    <div
      v-loading="loading"
      element-loading-text="正在加载文档..."
      class="preview-container"
    >
      <!-- 错误提示 -->
      <el-alert
        v-if="error"
        type="error"
        :title="error"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <!-- 只读Umo Editor预览 -->
      <div v-if="!error && previewContent" class="editor-preview-wrapper">
        <UmoEditor
          ref="editorRef"
          :document="{ readOnly: true }"
          @created="handleEditorCreated"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { UmoEditor } from '@umoteam/editor'

interface Props {
  modelValue: boolean
  fileUrl?: string
  fileName?: string
  htmlContent?: string  // 支持直接传入HTML内容
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  fileUrl: '',
  fileName: '文档预览',
  htmlContent: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 状态
const loading = ref(false)
const error = ref('')
const previewContent = ref('')
const editorRef = ref<any>(null)

// 对话框显示状态（双向绑定）
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 对话框标题
const dialogTitle = computed(() => {
  return `文档预览 - ${props.fileName || '未命名文档'}`
})

// 将文件路径转换为API URL（简化版）
const convertFilePathToUrl = (filePath: string): string => {
  // 如果已经是完整的URL或API路径，直接返回
  if (filePath.startsWith('http://') ||
      filePath.startsWith('https://') ||
      filePath.startsWith('/api/')) {
    return filePath
  }

  // 特殊处理：将 /download/ 路径转换为API路径
  if (filePath.startsWith('/download/')) {
    const filename = filePath.substring(10)
    return `/api/files/serve/download/${filename}`
  }

  // 现在后端存储的是相对路径（ai_tender_system/data/...）
  // 直接构建API URL即可
  let apiPath = filePath

  // 如果是旧数据的绝对路径，移除绝对路径前缀（向下兼容）
  const absolutePrefixes = [
    '/Users/lvhe/Downloads/zhongbiao/zhongbiao/',
    '/var/www/ai-tender-system/'
  ]

  for (const prefix of absolutePrefixes) {
    if (apiPath.startsWith(prefix)) {
      apiPath = apiPath.substring(prefix.length)
      break
    }
  }

  // 移除 ai_tender_system/data/ 前缀（如果有）
  if (apiPath.startsWith('ai_tender_system/data/')) {
    apiPath = apiPath.substring('ai_tender_system/data/'.length)
  }

  // 处理 outputs 目录：转换为 download/ 前缀
  if (apiPath.startsWith('outputs/')) {
    apiPath = 'download/' + apiPath.substring('outputs/'.length)
  }

  // 构建API URL
  return `/api/files/serve/${apiPath}`
}

// 加载文档
const loadDocument = async () => {
  // 优先使用 HTML 内容
  if (props.htmlContent) {
    console.log('[DocumentPreview] 使用HTML内容预览')
    previewContent.value = props.htmlContent
    return
  }

  if (!props.fileUrl) {
    error.value = '文档地址不能为空'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('[DocumentPreview] 开始加载文档:', props.fileUrl)

    // 调用后端API将Word转换为HTML
    const response = await fetch('/api/editor/convert-word-to-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: props.fileUrl })
    })

    const result = await response.json()

    if (result.success && result.html_content) {
      previewContent.value = result.html_content
      console.log('[DocumentPreview] Word转HTML成功，长度:', result.html_content.length)
    } else {
      throw new Error(result.error || 'Word转HTML失败')
    }

    console.log('[DocumentPreview] 文档渲染成功')
  } catch (err: any) {
    console.error('[DocumentPreview] 文档预览失败:', err)
    error.value = `文档预览失败: ${err.message || '未知错误'}`
    ElMessage.error('文档预览失败，请检查文件是否正确或尝试下载后查看')
  } finally {
    loading.value = false
  }
}

// 编辑器创建完成事件
const handleEditorCreated = () => {
  console.log('[DocumentPreview] 编辑器已创建，设置内容...')

  if (editorRef.value && previewContent.value) {
    // 延迟设置内容，确保编辑器完全就绪
    setTimeout(() => {
      if (typeof editorRef.value.setContent === 'function') {
        editorRef.value.setContent(previewContent.value)
        console.log('[DocumentPreview] 内容已设置，长度:', previewContent.value.length)
      } else {
        console.error('[DocumentPreview] setContent方法不可用')
      }
    }, 300)
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}

// 监听对话框打开事件
watch(
  () => props.modelValue,
  async (newValue) => {
    if (newValue && (props.fileUrl || props.htmlContent)) {
      // 延迟加载，确保对话框已完全打开
      await nextTick()
      loadDocument()
    } else {
      // 关闭时清空内容
      error.value = ''
      previewContent.value = ''
    }
  }
)
</script>

<style scoped lang="scss">
.document-preview-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
  }
}

.preview-container {
  display: flex;
  flex-direction: column;

  .editor-preview-wrapper {
    width: 100%;
    height: 80vh;  // 固定高度
    background: #f5f5f5;

    :deep(.umo-editor-container) {
      height: 100% !important;
      border: none;
    }
  }
}
</style>
