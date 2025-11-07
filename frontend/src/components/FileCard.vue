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

// 下载
const handleDownload = () => {
  const link = document.createElement('a')
  link.href = props.fileUrl
  link.download = fileName.value
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('文件下载已开始')
}

// 预览
const handlePreview = () => {
  // 判断是否为Word文档
  const ext = fileName.value.split('.').pop()?.toLowerCase()
  const isWordDoc = ext === 'doc' || ext === 'docx'

  if (isWordDoc) {
    // Word文档使用DocumentPreview组件预览
    emit('preview', props.fileUrl, fileName.value)
  } else {
    // 其他文件使用新窗口打开
    window.open(props.fileUrl, '_blank')
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
