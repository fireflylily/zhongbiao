<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="80%"
    :before-close="handleClose"
    destroy-on-close
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

      <!-- 预览内容区域 -->
      <div
        ref="previewContentRef"
        class="preview-content"
        :style="{ display: error ? 'none' : 'block' }"
      ></div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as docxPreview from 'docx-preview'

interface Props {
  modelValue: boolean
  fileUrl?: string
  fileName?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  fileUrl: '',
  fileName: '文档预览'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 状态
const loading = ref(false)
const error = ref('')
const previewContentRef = ref<HTMLElement | null>(null)

// 对话框显示状态（双向绑定）
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 对话框标题
const dialogTitle = computed(() => {
  return `文档预览 - ${props.fileName || '未命名文档'}`
})

// 将文件路径转换为API URL
const convertFilePathToUrl = (filePath: string): string => {
  // 如果已经是完整的URL，直接返回
  if (filePath.startsWith('http://') || filePath.startsWith('https://') || filePath.startsWith('/api/')) {
    return filePath
  }

  // 处理本地文件路径
  let apiPath = filePath

  // 移除可能的前缀路径
  const prefixes = [
    '/Users/lvhe/Downloads/zhongbiao/zhongbiao/',
    'ai_tender_system/data/',
    'data/'
  ]

  for (const prefix of prefixes) {
    if (apiPath.includes(prefix)) {
      apiPath = apiPath.substring(apiPath.indexOf(prefix) + prefix.length)
    }
  }

  // 处理以 /download/ 开头的路径（这些通常是output目录的文件）
  if (apiPath.startsWith('/download/')) {
    // 移除开头的斜杠，直接使用相对路径
    apiPath = apiPath.substring(1)
  }
  // 处理以 download/ 开头的路径
  else if (apiPath.startsWith('download/')) {
    // 保持原样
  }
  // 确保其他路径以 uploads/ 开头
  else if (!apiPath.startsWith('uploads/')) {
    apiPath = 'uploads/' + apiPath
  }

  // 构建API URL
  return `/api/files/serve/${apiPath}`
}

// 加载文档
const loadDocument = async () => {
  if (!props.fileUrl) {
    error.value = '文档地址不能为空'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const fileUrl = convertFilePathToUrl(props.fileUrl)
    console.log('[DocumentPreview] 开始加载文档:', props.fileUrl)
    console.log('[DocumentPreview] 转换后的URL:', fileUrl)

    // 获取文档数据
    const response = await fetch(fileUrl)
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`)
    }

    const arrayBuffer = await response.arrayBuffer()
    console.log('[DocumentPreview] 文档已下载，大小:', arrayBuffer.byteLength, '字节')

    // 等待DOM更新
    await nextTick()

    if (!previewContentRef.value) {
      throw new Error('预览容器未找到')
    }

    // 清空容器
    previewContentRef.value.innerHTML = ''

    // 使用docx-preview渲染文档
    await docxPreview.renderAsync(arrayBuffer, previewContentRef.value, undefined, {
      className: 'docx-preview',
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      ignoreFonts: false,
      breakPages: true,
      ignoreLastRenderedPageBreak: true,
      experimental: true,
      trimXmlDeclaration: true
    })

    console.log('[DocumentPreview] 文档渲染成功')
  } catch (err: any) {
    console.error('[DocumentPreview] 文档预览失败:', err)
    error.value = `文档预览失败: ${err.message || '未知错误'}`
    ElMessage.error('文档预览失败，请检查文件是否正确或尝试下载后查看')
  } finally {
    loading.value = false
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
    if (newValue && props.fileUrl) {
      // 延迟加载，确保对话框已完全打开
      await nextTick()
      loadDocument()
    } else {
      // 关闭时清空内容
      error.value = ''
      if (previewContentRef.value) {
        previewContentRef.value.innerHTML = ''
      }
    }
  }
)
</script>

<style scoped lang="scss">
.preview-container {
  min-height: 400px;
  max-height: 70vh;
  overflow-y: auto;

  .preview-content {
    padding: 20px;
    background: #f5f5f5;
    border-radius: 4px;

    :deep(.docx-preview) {
      background: white;
      padding: 40px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      min-height: 500px;
    }

    // 统一页面宽度，防止不同尺寸的页面显示不一致
    :deep(.docx-wrapper) {
      max-width: 900px;
      margin: 0 auto;

      section {
        margin: 20px auto !important;
        max-width: 100%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
    }

    // 保留Word文档的样式
    :deep(.docx) {
      font-family: 'Times New Roman', serif;
      line-height: 1.6;

      table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;

        td,
        th {
          border: 1px solid #ddd;
          padding: 8px;
        }
      }

      p {
        margin: 0.5em 0;
      }

      h1,
      h2,
      h3,
      h4,
      h5,
      h6 {
        margin: 1em 0 0.5em 0;
        font-weight: bold;
      }
    }
  }
}
</style>
