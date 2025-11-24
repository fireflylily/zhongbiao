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
      <div class="upload-section">
        <DocumentUploader
          ref="uploaderRef"
          :accept="acceptTypes"
          :multiple="qualification.allowMultiple"
          :show-file-list="false"
          :http-request="handleCustomUpload"
          :max-size="100"
          :auto-compress-image="true"
          :image-type="imageType"
        >
          <template #trigger>
            <el-button type="primary" size="small">
              <el-icon><Upload /></el-icon>
              {{ qualification.allowMultiple ? '批量上传' : '上传文件' }}
            </el-button>
          </template>
        </DocumentUploader>
        <el-button
          v-if="hasCreditQueryUrl"
          type="success"
          size="small"
          @click="openQueryWebsite"
        >
          <el-icon><Link /></el-icon>
          打开查询网站
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
      <!-- PDF转换提示 -->
      <div class="upload-tips">
        <el-text type="info" size="small">
          支持JPG、PNG、PDF格式 <span class="pdf-tip">（PDF将自动转换为图片）</span>
        </el-text>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Document, Upload, Download, Delete, Files, Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { DocumentUploader } from '@/components'

// Props
const props = defineProps<{
  qualification: any
  fileInfo?: any
  isCustom?: boolean
  onUpload?: (file: File) => Promise<void>
  companyName?: string  // 新增: 公司名称,用于打开查询网站
}>()

// Emits
const emit = defineEmits<{
  (e: 'upload', file: File): void
  (e: 'download', qualKey: string, qualId?: number): void
  (e: 'delete', qualKey: string, qualId?: number): void
  (e: 'remove-custom'): void
}>()

// Refs
const uploaderRef = ref()

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
  // 所有资质类型都支持PDF（会自动转换为图片）
  // 根据资质类型决定接受的文件类型
  if (props.qualification.key === 'financial_audit_report') {
    return '.pdf,.xls,.xlsx,.jpg,.jpeg,.png'
  }
  // 默认支持图片和PDF格式
  return '.pdf,.jpg,.jpeg,.png'
})

// 根据资质类型智能选择压缩配置
const imageType = computed(() => {
  const key = props.qualification.key

  // 营业执照
  if (key === 'business_license') {
    return 'license'
  }

  // 身份证类型
  if (key.includes('id') || key === 'legal_id_front' || key === 'legal_id_back') {
    return 'id_card'
  }

  // 公章
  if (key.includes('seal')) {
    return 'seal'
  }

  // ISO、CMMI等资质证书
  if (key.includes('iso') || key.includes('cmmi') || key.includes('certificate') ||
      key.includes('qualification') || key.includes('认证')) {
    return 'qualification'
  }

  // 默认
  return 'default'
})

// 方法
// 自定义上传处理器（使用DocumentUploader的接口）
const handleCustomUpload = async (options: UploadRequestOptions) => {
  const { file, onSuccess, onError } = options

  try {
    // 如果提供了 onUpload 属性，调用它
    if (props.onUpload) {
      await props.onUpload(file as File)
    } else {
      // 否则使用旧的 emit 方式（向后兼容）
      emit('upload', file as File)
    }

    // 调用成功回调
    onSuccess({ success: true })
  } catch (error: any) {
    // 调用错误回调
    onError(error)
  }
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

// 信用资质查询网站配置
const creditQueryUrls: Record<string, string> = {
  'dishonest_executor': 'https://zxgk.court.gov.cn/shixin/',  // 失信被执行人
  'tax_violation_check': 'https://www.creditchina.gov.cn/zhuanxiangchaxun/zhongdashuishouweifaanjian/',  // 重大税收违法失信主体
  'gov_procurement_creditchina': 'https://www.creditchina.gov.cn/zhuanxiangchaxun/zhengfucaigouyanzhongweifashixinmingdan/',  // 政府采购严重违法失信行为
  'creditchina_blacklist': 'https://www.creditchina.gov.cn/xinxigongshi/shixinheimingdan/',  // 严重失信主体
  'creditchina_credit_report': 'https://www.creditchina.gov.cn/xybgxzzn/',  // 信用报告
  'enterprise_credit_report': 'https://www.gsxt.gov.cn/',  // 国家企业信用信息公示系统
  'gov_procurement_ccgp': 'http://www.ccgp.gov.cn/search/cr/'  // 政府采购严重违法失信行为信息记录(政府采购网)
}

// 判断是否为信用资质(有查询网站)
const hasCreditQueryUrl = computed(() => {
  return props.qualification.key in creditQueryUrls
})

// 打开查询网站
const openQueryWebsite = () => {
  const url = creditQueryUrls[props.qualification.key]
  if (url) {
    window.open(url, '_blank')
    ElMessage.success('已在新窗口打开查询网站,请手动查询后截图上传')
  }
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
    padding-top: 12px;
    border-top: 1px solid #e4e7ed;

    .upload-section {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }

    .upload-tips {
      font-size: 12px;
      color: #909399;

      .pdf-tip {
        color: #67c23a;
        font-weight: 500;
      }
    }
  }
}
</style>
