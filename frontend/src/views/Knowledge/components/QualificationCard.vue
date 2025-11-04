<template>
  <el-card class="qualification-card" :class="{ 'required': qualification.required, 'has-file': hasFile }">
    <div class="card-header">
      <div class="qual-info">
        <el-icon class="qual-icon" :size="20">
          <component :is="qualification.icon" />
        </el-icon>
        <span class="qual-name">{{ qualification.name }}</span>
      </div>
      <div class="badges">
        <el-tag v-if="qualification.required" type="warning" size="small">必需</el-tag>
        <el-tag v-if="qualification.allowMultiple" type="info" size="small">
          <el-icon><Files /></el-icon>
          多文件
        </el-tag>
      </div>
    </div>

    <!-- 文件状态显示 -->
    <div v-if="hasFile" class="file-status">
      <!-- 单文件显示 -->
      <div v-if="!isMultipleFiles" class="single-file">
        <div class="file-item">
          <el-icon class="file-icon"><Document /></el-icon>
          <div class="file-details">
            <div class="file-name">{{ fileInfo.original_filename }}</div>
            <div class="file-meta">
              <span>{{ formatFileSize(fileInfo.file_size) }}</span>
              <span class="divider">•</span>
              <span>{{ formatDate(fileInfo.upload_time) }}</span>
            </div>
          </div>
          <div class="file-actions">
            <el-button
              text
              type="primary"
              size="small"
              @click="handleDownload"
            >
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              @click="handleDelete"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 多文件显示 -->
      <div v-else class="multiple-files">
        <div v-for="file in fileInfo.files" :key="file.qualification_id" class="file-item">
          <el-icon class="file-icon"><Document /></el-icon>
          <div class="file-details">
            <div class="file-name">{{ file.original_filename }}</div>
            <div class="file-meta">
              <span>{{ formatFileSize(file.file_size) }}</span>
              <span class="divider">•</span>
              <span>{{ formatDate(file.upload_time) }}</span>
            </div>
          </div>
          <div class="file-actions">
            <el-button
              text
              type="primary"
              size="small"
              @click="handleDownloadById(file.qualification_id)"
            >
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              @click="handleDeleteById(file.qualification_id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 无文件状态 -->
    <div v-else class="no-file">
      <el-text type="info" size="small">未上传文件</el-text>
    </div>

    <!-- 操作按钮 -->
    <div class="card-footer">
      <input
        ref="fileInputRef"
        type="file"
        :accept="acceptTypes"
        :multiple="qualification.allowMultiple"
        style="display: none"
        @change="handleFileChange"
      >
      <el-button
        type="primary"
        size="small"
        @click="triggerFileInput"
      >
        <el-icon><Upload /></el-icon>
        {{ qualification.allowMultiple ? '批量上传' : '上传文件' }}
      </el-button>
      <el-button
        v-if="isCustom"
        type="danger"
        size="small"
        @click="$emit('remove-custom')"
      >
        <el-icon><Delete /></el-icon>
        移除
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Document, Upload, Download, Delete, Files } from '@element-plus/icons-vue'

// Props
const props = defineProps<{
  qualification: any
  fileInfo?: any
  isCustom?: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'upload', file: File): void
  (e: 'download', qualKey: string, qualId?: number): void
  (e: 'delete', qualKey: string, qualId?: number): void
  (e: 'remove-custom'): void
}>()

// Refs
const fileInputRef = ref<HTMLInputElement>()

// 计算属性
const hasFile = computed(() => {
  if (!props.fileInfo) return false
  if (props.fileInfo.allow_multiple_files) {
    return props.fileInfo.files && props.fileInfo.files.length > 0
  }
  return !!props.fileInfo.original_filename
})

const isMultipleFiles = computed(() => {
  return props.fileInfo?.allow_multiple_files && props.fileInfo?.files
})

const acceptTypes = computed(() => {
  // 根据资质类型决定接受的文件类型
  if (props.qualification.key === 'financial_audit_report') {
    return '.pdf,.xls,.xlsx'
  }
  return '.pdf,.jpg,.jpeg,.png'
})

// 方法
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  // 如果是多文件上传，处理所有文件
  if (props.qualification.allowMultiple) {
    Array.from(files).forEach(file => {
      emit('upload', file)
    })
  } else {
    // 单文件上传
    emit('upload', files[0])
  }

  // 清空input以便下次可以选择相同文件
  target.value = ''
}

const handleDownload = () => {
  emit('download', props.qualification.key)
}

const handleDownloadById = (qualId: number) => {
  emit('download', props.qualification.key, qualId)
}

const handleDelete = () => {
  emit('delete', props.qualification.key)
}

const handleDeleteById = (qualId: number) => {
  emit('delete', props.qualification.key, qualId)
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
.qualification-card {
  height: 100%;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;

  &.required {
    border-left: 3px solid #e6a23c;
  }

  &.has-file {
    border-color: #67c23a;
  }

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }

  :deep(.el-card__body) {
    padding: 16px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;

    .qual-info {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;

      .qual-icon {
        color: #409eff;
        flex-shrink: 0;
      }

      .qual-name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        line-height: 1.4;
      }
    }

    .badges {
      display: flex;
      gap: 4px;
      flex-shrink: 0;
    }
  }

  .file-status {
    margin: 12px 0;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;

    .file-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px;
      background: white;
      border-radius: 4px;
      margin-bottom: 8px;

      &:last-child {
        margin-bottom: 0;
      }

      .file-icon {
        font-size: 20px;
        color: #606266;
        flex-shrink: 0;
      }

      .file-details {
        flex: 1;
        min-width: 0;

        .file-name {
          font-size: 13px;
          color: #303133;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .file-meta {
          font-size: 12px;
          color: #909399;
          margin-top: 2px;

          .divider {
            margin: 0 4px;
          }
        }
      }

      .file-actions {
        display: flex;
        gap: 4px;
        flex-shrink: 0;
      }
    }
  }

  .no-file {
    padding: 12px;
    text-align: center;
    background: #f5f7fa;
    border-radius: 4px;
    margin: 12px 0;
  }

  .card-footer {
    display: flex;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid #e4e7ed;
  }
}
</style>
