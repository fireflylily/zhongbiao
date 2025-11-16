<template>
  <div class="file-card" :class="[`file-card--${type}`]">
    <div class="file-card__icon">
      <i :class="fileIcon"></i>
    </div>
    <div class="file-card__info">
      <div class="file-card__name">{{ fileName }}</div>
      <div class="file-card__meta">
        <!-- 文件大小已隐藏 -->
        <span v-if="uploadDate" class="meta-item">
          <i class="bi bi-calendar"></i> {{ uploadDate }}
        </span>
      </div>
    </div>
    <div v-if="showActions" class="file-card__actions">
      <el-button size="small" @click="handleDownload">
        <i class="bi bi-download"></i> 下载
      </el-button>
      <el-button size="small" @click="handlePreview">
        <i class="bi bi-eye"></i> 预览
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = withDefaults(
  defineProps<{
    fileUrl: string
    fileName?: string
    fileSize?: number
    uploadTime?: string
    type?: 'default' | 'success' | 'warning'
    showActions?: boolean
  }>(),
  {
    type: 'default',
    showActions: true
  }
)

const emit = defineEmits<{
  preview: [fileUrl: string, fileName: string]
}>()

// 文件名
const fileName = computed(() => {
  if (props.fileName) return props.fileName
  const parts = props.fileUrl.split('/')
  return parts[parts.length - 1] || ''
})

// 文件图标
const fileIcon = computed(() => {
  const ext = fileName.value.split('.').pop()?.toLowerCase()
  const iconMap: Record<string, string> = {
    pdf: 'bi-file-pdf',
    doc: 'bi-file-word',
    docx: 'bi-file-word',
    xls: 'bi-file-excel',
    xlsx: 'bi-file-excel',
    zip: 'bi-file-zip',
    rar: 'bi-file-zip'
  }
  return iconMap[ext || ''] || 'bi-file-earmark-text'
})

// 上传日期
const uploadDate = computed(() => {
  if (!props.uploadTime) return ''
  // 如果是完整时间，截取日期部分
  return props.uploadTime.split(' ')[0] || props.uploadTime
})

// 将文件路径转换为API URL
const convertToApiUrl = (filePath: string): string => {
  // 如果已经是完整的URL或API路径，直接返回
  if (filePath.startsWith('http://') ||
      filePath.startsWith('https://') ||
      filePath.startsWith('/api/')) {
    return filePath
  }

  // 现在后端存储的是相对路径（ai_tender_system/data/...）
  let apiPath = filePath

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

// 下载
const handleDownload = () => {
  const apiUrl = convertToApiUrl(props.fileUrl)
  const link = document.createElement('a')
  link.href = apiUrl + '?download=true'  // 添加download参数
  link.download = fileName.value
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('文件下载已开始')
}

// 预览
const handlePreview = () => {
  // 判断是否为Word文档
  // 从fileName和fileUrl两处尝试提取扩展名
  let ext = ''

  // 优先从fileName提取
  if (fileName.value) {
    const parts = fileName.value.split('.')
    if (parts.length > 1) {
      ext = parts[parts.length - 1].toLowerCase()
    }
  }

  // 如果fileName没有扩展名，从fileUrl提取
  if (!ext && props.fileUrl) {
    const urlWithoutQuery = props.fileUrl.split('?')[0] // 移除查询参数
    const parts = urlWithoutQuery.split('.')
    if (parts.length > 1) {
      ext = parts[parts.length - 1].toLowerCase()
    }
  }

  const isWordDoc = ext === 'doc' || ext === 'docx'

  if (isWordDoc) {
    // Word文档使用DocumentPreview组件预览
    emit('preview', props.fileUrl, fileName.value)
  } else {
    // 其他文件（PDF等）使用API URL打开
    const apiUrl = convertToApiUrl(props.fileUrl)
    window.open(apiUrl, '_blank')
  }
}
</script>

<style scoped lang="scss">
.file-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  border: 2px solid var(--el-border-color-lighter);
  transition: all 0.3s;

  &:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  &--success {
    background: var(--el-color-success-light-9);
    border-color: var(--el-color-success-light-5);
  }

  &--warning {
    background: var(--el-color-warning-light-9);
    border-color: var(--el-color-warning-light-5);
  }

  &__icon {
    font-size: 48px;
    color: var(--el-color-primary);
  }

  &__info {
    flex: 1;

    .file-card__name {
      font-size: 15px;
      font-weight: 500;
      color: var(--el-text-color-primary);
      margin-bottom: 6px;
      word-break: break-all;
    }

    .file-card__meta {
      display: flex;
      gap: 16px;
      font-size: 13px;
      color: var(--el-text-color-secondary);

      .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  &__actions {
    display: flex;
    gap: 8px;
  }
}
</style>
