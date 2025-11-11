<template>
  <div class="document-uploader">
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :http-request="httpRequest"
      :headers="uploadHeaders"
      :data="uploadData"
      :accept="accept"
      :limit="limit"
      :multiple="multiple"
      :drag="drag"
      :show-file-list="showFileList"
      :before-upload="handleBeforeUpload"
      :on-progress="handleProgress"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-exceed="handleExceed"
      :on-remove="handleRemove"
      :file-list="fileList"
      v-bind="$attrs"
    >
      <template #default>
        <slot name="trigger">
          <el-button v-if="!drag" type="primary" :icon="Upload">
            {{ triggerText }}
          </el-button>
          <div v-else class="upload-drag-area">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <div class="upload-hint" v-if="accept">
              支持的文件格式：{{ accept }}
            </div>
          </div>
        </slot>
      </template>

      <template #tip>
        <slot name="tip">
          <div class="upload-tip" v-if="tipText">
            <el-icon><InfoFilled /></el-icon>
            {{ tipText }}
          </div>
        </slot>
      </template>

      <template #file="{ file }">
        <slot name="file" :file="file">
          <div class="upload-file-item">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ file.name }}</span>
            <!-- 文件大小已隐藏 -->
            <el-progress
              v-if="file.status === 'uploading'"
              :percentage="file.percentage"
              :stroke-width="2"
            />
            <el-icon
              v-if="file.status === 'success'"
              class="status-icon success"
            >
              <CircleCheck />
            </el-icon>
            <el-icon
              v-if="file.status === 'fail'"
              class="status-icon error"
            >
              <CircleClose />
            </el-icon>
          </div>
        </slot>
      </template>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadUserFile, UploadFile, UploadRawFile } from 'element-plus'
import {
  Upload,
  UploadFilled,
  Document,
  CircleCheck,
  CircleClose,
  InfoFilled
} from '@element-plus/icons-vue'
import { smartCompressImage } from '@/utils/imageCompressor'

interface Props {
  /** 上传地址 */
  uploadUrl?: string
  /** 上传请求头 */
  uploadHeaders?: Record<string, string>
  /** 上传额外数据 */
  uploadData?: Record<string, any>
  /** 自定义上传函数 */
  httpRequest?: UploadProps['httpRequest']
  /** 接受的文件类型 */
  accept?: string
  /** 最大上传文件数 */
  limit?: number
  /** 最大文件大小（MB） */
  maxSize?: number
  /** 是否支持多选 */
  multiple?: boolean
  /** 是否启用拖拽上传 */
  drag?: boolean
  /** 是否显示文件列表 */
  showFileList?: boolean
  /** 触发按钮文本 */
  triggerText?: string
  /** 提示文本 */
  tipText?: string
  /** 已上传文件列表 */
  modelValue?: UploadUserFile[]
  /** 是否自动压缩图片（默认true） */
  autoCompressImage?: boolean
  /** 图片压缩类型（用于选择压缩参数） */
  imageType?: 'license' | 'qualification' | 'id_card' | 'seal' | 'photo' | 'default'
}

interface Emits {
  (e: 'update:modelValue', value: UploadUserFile[]): void
  (e: 'success', file: UploadFile, uploadFiles: UploadFile[]): void
  (e: 'error', error: Error, file: UploadFile, uploadFiles: UploadFile[]): void
  (e: 'exceed', files: File[], uploadFiles: UploadUserFile[]): void
  (e: 'remove', file: UploadFile, uploadFiles: UploadFile[]): void
}

const props = withDefaults(defineProps<Props>(), {
  uploadUrl: '/api/upload',
  accept: '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx',
  limit: 10,
  maxSize: 50,
  multiple: false,
  drag: false,
  showFileList: true,
  triggerText: '选择文件',
  tipText: '',
  autoCompressImage: true,
  imageType: 'default'
})

const emit = defineEmits<Emits>()

// 上传组件引用
const uploadRef = ref()

// 文件列表
const fileList = computed({
  get: () => props.modelValue || [],
  set: (value) => emit('update:modelValue', value)
})

// 上传前钩子
const handleBeforeUpload: UploadProps['beforeUpload'] = async (rawFile) => {
  // 文件大小验证
  if (props.maxSize && rawFile.size / 1024 / 1024 > props.maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }

  // 文件类型验证
  if (props.accept) {
    const acceptTypes = props.accept.split(',').map(t => t.trim())
    const fileExt = '.' + rawFile.name.split('.').pop()?.toLowerCase()

    if (!acceptTypes.some(type => fileExt === type.toLowerCase())) {
      ElMessage.error(`不支持的文件格式：${fileExt}`)
      return false
    }
  }

  // 图片自动压缩
  if (props.autoCompressImage && rawFile.type.startsWith('image/')) {
    try {
      console.log(`[DocumentUploader] 检测到图片文件，开始压缩: ${rawFile.name}, ${(rawFile.size / 1024).toFixed(0)}KB`)

      const compressedFile = await smartCompressImage(rawFile, props.imageType)

      // 显示压缩效果
      const originalSize = rawFile.size
      const compressedSize = compressedFile.size
      const savings = ((originalSize - compressedSize) / originalSize * 100).toFixed(1)

      if (compressedSize < originalSize) {
        console.log(
          `[DocumentUploader] ✅ 图片已压缩: ` +
          `${(originalSize / 1024).toFixed(0)}KB → ${(compressedSize / 1024).toFixed(0)}KB ` +
          `(节省${savings}%)`
        )

        // 返回压缩后的文件（Element Plus会用这个文件上传）
        return compressedFile as any
      } else {
        console.log(`[DocumentUploader] 图片无需压缩，使用原文件`)
      }
    } catch (error) {
      console.error('[DocumentUploader] 图片压缩失败:', error)
      // 压缩失败，继续使用原文件
      ElMessage.warning('图片压缩失败，将上传原文件')
    }
  }

  return true
}

// 上传进度
const handleProgress: UploadProps['onProgress'] = (event, file, fileList) => {
  // 可以在这里添加自定义进度处理逻辑
}

// 上传成功
const handleSuccess: UploadProps['onSuccess'] = (response, file, fileList) => {
  // 不在这里显示成功消息，由父组件负责显示更具体的提示
  emit('success', file, fileList)
  emit('update:modelValue', fileList)
}

// 上传失败
const handleError: UploadProps['onError'] = (error, file, fileList) => {
  ElMessage.error('文件上传失败：' + error.message)
  emit('error', error, file, fileList)
}

// 超出文件数量限制
const handleExceed: UploadProps['onExceed'] = (files, fileList) => {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
  emit('exceed', files, fileList)
}

// 删除文件
const handleRemove: UploadProps['onRemove'] = (file, fileList) => {
  emit('remove', file, fileList)
  emit('update:modelValue', fileList)
}

// 清空文件列表
const clearFiles = () => {
  uploadRef.value?.clearFiles()
  emit('update:modelValue', [])
}

// 提交上传
const submit = () => {
  uploadRef.value?.submit()
}

// 中止上传
const abort = (file?: UploadFile) => {
  uploadRef.value?.abort(file)
}

// 暴露方法给父组件
defineExpose({
  clearFiles,
  submit,
  abort
})
</script>

<style scoped lang="scss">
@import "@/assets/styles/variables.scss";

.document-uploader {
  :deep(.el-upload) {
    width: 100%;
  }

  :deep(.el-upload-dragger) {
    padding: 40px;
    border: 2px dashed var(--el-border-color);
    border-radius: 8px;
    background: var(--el-fill-color-blank);
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
      background: var(--el-fill-color-light);
    }
  }

  .upload-drag-area {
    text-align: center;

    .upload-icon {
      font-size: 48px;
      color: var(--el-color-primary);
      margin-bottom: 16px;
    }

    .upload-text {
      font-size: 14px;
      color: var(--el-text-color-regular);
      margin-bottom: 8px;

      em {
        color: var(--el-color-primary);
        font-style: normal;
      }
    }

    .upload-hint {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }

  .upload-tip {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);

    .el-icon {
      font-size: 14px;
    }
  }

  .upload-file-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border: 1px solid var(--el-border-color);
    border-radius: 6px;
    background: var(--el-fill-color-blank);
    transition: all 0.3s;

    &:hover {
      background: var(--el-fill-color-light);
    }

    .file-icon {
      font-size: 24px;
      color: var(--el-color-primary);
      flex-shrink: 0;
    }

    .file-name {
      flex: 1;
      font-size: 14px;
      color: var(--el-text-color-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .file-size {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      flex-shrink: 0;
    }

    .status-icon {
      font-size: 20px;
      flex-shrink: 0;

      &.success {
        color: var(--el-color-success);
      }

      &.error {
        color: var(--el-color-error);
      }
    }

    .el-progress {
      flex: 1;
      margin: 0 12px;
    }
  }

  :deep(.el-upload-list) {
    margin-top: 12px;
  }

  :deep(.el-upload-list__item) {
    transition: all 0.3s;

    &:hover {
      background: var(--el-fill-color-light);
    }
  }
}
</style>
