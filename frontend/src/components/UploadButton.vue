<!--
  UploadButton - 上传按钮组件

  功能：
  - 单文件/多文件上传
  - 拖拽上传
  - 文件类型限制
  - 文件大小限制
  - 上传进度显示
  - 预览功能
-->

<template>
  <div class="upload-button">
    <el-upload
      ref="uploadRef"
      :action="action"
      :headers="headers"
      :data="data"
      :multiple="multiple"
      :accept="accept"
      :limit="limit"
      :file-list="fileList"
      :before-upload="handleBeforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :on-exceed="handleExceed"
      :on-remove="handleRemove"
      :show-file-list="showFileList"
      :drag="drag"
      :auto-upload="autoUpload"
    >
      <!-- 按钮模式 -->
      <template v-if="!drag">
        <el-button :type="buttonType" :icon="buttonIcon" :loading="uploading">
          {{ buttonText }}
        </el-button>
      </template>

      <!-- 拖拽模式 -->
      <template v-else>
        <div class="upload-drag-area">
          <i class="bi bi-cloud-upload drag-icon"></i>
          <div class="drag-text">
            <p class="drag-title">拖拽文件到此处或<em>点击上传</em></p>
            <p class="drag-hint">{{ uploadHint }}</p>
          </div>
        </div>
      </template>

      <!-- 提示文本 -->
      <template v-if="tip && !drag" #tip>
        <div class="upload-tip">{{ tip }}</div>
      </template>
    </el-upload>

    <!-- 上传进度 -->
    <div v-if="showProgress && uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <el-progress :percentage="uploadProgress" :stroke-width="6" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadInstance, UploadProps, UploadUserFile, UploadRawFile } from 'element-plus'

// ==================== Props ====================

interface Props {
  action?: string
  headers?: Record<string, string>
  data?: Record<string, any>
  multiple?: boolean
  accept?: string
  limit?: number
  maxSize?: number // MB
  buttonText?: string
  buttonType?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  buttonIcon?: any
  tip?: string
  showFileList?: boolean
  showProgress?: boolean
  drag?: boolean
  autoUpload?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  action: '/api/upload',
  headers: () => ({}),
  data: () => ({}),
  multiple: false,
  accept: '*',
  limit: 1,
  maxSize: 100, // 100MB
  buttonText: '上传文件',
  buttonType: 'primary',
  buttonIcon: UploadFilled,
  tip: '',
  showFileList: true,
  showProgress: true,
  drag: false,
  autoUpload: true
})

const emit = defineEmits<{
  (e: 'success', response: any, file: UploadUserFile): void
  (e: 'error', error: Error, file: UploadUserFile): void
  (e: 'progress', event: any, file: UploadUserFile): void
  (e: 'remove', file: UploadUserFile): void
  (e: 'exceed', files: File[]): void
}>()

// ==================== State ====================

const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadUserFile[]>([])
const uploading = ref(false)
const uploadProgress = ref(0)

// ==================== Computed ====================

/**
 * 上传提示
 */
const uploadHint = computed(() => {
  if (props.tip) return props.tip

  const parts: string[] = []

  if (props.accept && props.accept !== '*') {
    parts.push(`支持${props.accept}格式`)
  }

  if (props.maxSize) {
    parts.push(`大小不超过${props.maxSize}MB`)
  }

  return parts.join('，')
})

// ==================== Methods ====================

/**
 * 上传前检查
 */
function handleBeforeUpload(file: UploadRawFile): boolean {
  // 检查文件大小
  if (props.maxSize) {
    const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize
    if (!isLtMaxSize) {
      ElMessage.error(`文件大小不能超过 ${props.maxSize}MB!`)
      return false
    }
  }

  // 检查文件类型
  if (props.accept && props.accept !== '*') {
    const acceptTypes = props.accept.split(',').map((t) => t.trim())
    const fileType = file.name.substring(file.name.lastIndexOf('.'))
    const isAccept = acceptTypes.some((type) => {
      return type === fileType || type === file.type
    })

    if (!isAccept) {
      ElMessage.error(`只支持 ${props.accept} 格式的文件！`)
      return false
    }
  }

  uploading.value = true
  uploadProgress.value = 0
  return true
}

/**
 * 上传成功
 */
function handleSuccess(response: any, file: UploadUserFile): void {
  uploading.value = false
  uploadProgress.value = 100

  setTimeout(() => {
    uploadProgress.value = 0
  }, 1000)

  ElMessage.success('上传成功')
  emit('success', response, file)
}

/**
 * 上传失败
 */
function handleError(error: Error, file: UploadUserFile): void {
  uploading.value = false
  uploadProgress.value = 0

  ElMessage.error('上传失败: ' + error.message)
  emit('error', error, file)
}

/**
 * 上传进度
 */
function handleProgress(event: any, file: UploadUserFile): void {
  uploadProgress.value = Math.round(event.percent)
  emit('progress', event, file)
}

/**
 * 超出限制
 */
function handleExceed(files: File[]): void {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件！`)
  emit('exceed', files)
}

/**
 * 移除文件
 */
function handleRemove(file: UploadUserFile): void {
  emit('remove', file)
}

/**
 * 清空文件列表
 */
function clearFiles(): void {
  uploadRef.value?.clearFiles()
}

/**
 * 手动提交上传
 */
function submit(): void {
  uploadRef.value?.submit()
}

// ==================== Expose ====================

defineExpose({
  clearFiles,
  submit
})
</script>

<style scoped lang="scss">
.upload-button {
  width: 100%;
}

.upload-tip {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
  line-height: 1.5;
}

.upload-progress {
  margin-top: 12px;
}

// ==================== 拖拽区域 ====================

.upload-drag-area {
  padding: 60px 20px;
  text-align: center;
  border: 2px dashed var(--border-light, #e5e7eb);
  border-radius: var(--border-radius-md, 8px);
  background: var(--bg-light, #f8f9fa);
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    border-color: var(--brand-primary, #4a89dc);
    background: rgba(74, 137, 220, 0.05);

    .drag-icon {
      color: var(--brand-primary, #4a89dc);
      transform: scale(1.1);
    }
  }
}

.drag-icon {
  font-size: 64px;
  color: var(--text-disabled, #d1d5db);
  transition: all 0.3s;
  display: block;
  margin-bottom: 16px;
}

.drag-text {
  .drag-title {
    margin: 0 0 8px;
    font-size: 14px;
    color: var(--text-primary, #333);

    em {
      color: var(--brand-primary, #4a89dc);
      font-style: normal;
    }
  }

  .drag-hint {
    margin: 0;
    font-size: 13px;
    color: var(--text-secondary, #6c757d);
  }
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .upload-drag-area {
    padding: 40px 16px;
  }

  .drag-icon {
    font-size: 48px;
  }

  .drag-title {
    font-size: 13px;
  }

  .drag-hint {
    font-size: 12px;
  }
}
</style>
