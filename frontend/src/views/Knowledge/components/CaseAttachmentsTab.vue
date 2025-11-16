<template>
  <div class="case-attachments-tab">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>案例附件</span>
          <el-button type="primary" size="small" @click="handleUpload">
            <el-icon><Upload /></el-icon>
            上传附件
          </el-button>
        </div>
      </template>

      <Loading v-if="loading" text="加载附件中..." />
      <Empty v-else-if="!attachments.length" type="no-data" description="暂无附件" />
      <div v-else class="attachments-grid">
        <div
          v-for="attachment in attachments"
          :key="attachment.attachment_id"
          class="attachment-card"
        >
          <div class="attachment-header">
            <el-icon :size="32" :color="getAttachmentColor(attachment.attachment_type)">
              <component :is="getAttachmentIcon(attachment.attachment_type)" />
            </el-icon>
            <el-tag :type="getAttachmentTagType(attachment.attachment_type)" size="small">
              {{ getAttachmentLabel(attachment.attachment_type) }}
            </el-tag>
          </div>

          <div class="attachment-body">
            <div class="file-name" :title="attachment.original_filename">
              {{ attachment.original_filename }}
            </div>
            <div class="file-info">
              <span class="file-size">{{ formatFileSize(attachment.file_size) }}</span>
              <span class="file-date">{{ formatDate(attachment.uploaded_at, 'date') }}</span>
            </div>
            <div v-if="attachment.attachment_description" class="file-desc">
              {{ attachment.attachment_description }}
            </div>
          </div>

          <div class="attachment-actions">
            <el-button size="small" @click="handleDownload(attachment)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(attachment)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 上传附件对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传案例附件"
      width="500px"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadFormRules"
        label-width="120px"
      >
        <el-form-item label="附件类型" prop="attachment_type">
          <el-select v-model="uploadForm.attachment_type" placeholder="请选择附件类型" style="width: 100%">
            <el-option label="合同文件" value="contract" />
            <el-option label="验收证明" value="acceptance" />
            <el-option label="客户证明" value="testimony" />
            <el-option label="项目照片" value="photo" />
            <el-option label="其他材料" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="附件说明" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="2"
            placeholder="请简要说明附件内容（可选）"
          />
        </el-form-item>

        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到这里 或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持PDF、DOC、DOCX、JPG、PNG格式，文件大小不超过20MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleConfirmUpload">
          确定上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import { formatFileSize, formatDate } from '@/utils/formatters'
import { smartCompressImage } from '@/utils/imageCompressor'
import {
  Upload,
  UploadFilled,
  Download,
  Delete,
  Document,
  Select,
  Picture,
  Files,
  Tickets
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadInstance, UploadFile } from 'element-plus'
import type { CaseAttachment } from '@/types'

// Props
const props = defineProps<{
  caseId: number
  caseData: any
}>()

// Emits
const emit = defineEmits<{
  update: []
}>()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const attachments = ref<CaseAttachment[]>([])
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const uploadForm = ref({
  attachment_type: 'contract' as 'contract' | 'acceptance' | 'testimony' | 'photo' | 'other',
  description: '',
  file: null as File | null
})

const uploadFormRules: FormRules = {
  attachment_type: [
    { required: true, message: '请选择附件类型', trigger: 'change' }
  ]
}

// 获取附件图标
const getAttachmentIcon = (type: string) => {
  switch (type) {
    case 'contract': return Document
    case 'acceptance': return Select
    case 'testimony': return Tickets
    case 'photo': return Picture
    default: return Files
  }
}

// 获取附件颜色
const getAttachmentColor = (type: string) => {
  switch (type) {
    case 'contract': return '#409eff'
    case 'acceptance': return '#67c23a'
    case 'testimony': return '#e6a23c'
    case 'photo': return '#f56c6c'
    default: return '#909399'
  }
}

// 获取附件标签类型
const getAttachmentTagType = (type: string) => {
  switch (type) {
    case 'contract': return 'primary'
    case 'acceptance': return 'success'
    case 'testimony': return 'warning'
    case 'photo': return 'danger'
    default: return 'info'
  }
}

// 获取附件标签文本
const getAttachmentLabel = (type: string) => {
  switch (type) {
    case 'contract': return '合同文件'
    case 'acceptance': return '验收证明'
    case 'testimony': return '客户证明'
    case 'photo': return '项目照片'
    default: return '其他材料'
  }
}

// 加载附件列表
const loadAttachments = async () => {
  loading.value = true
  try {
    const response = await knowledgeApi.getCaseAttachments(props.caseId)
    if (response.success && response.data) {
      attachments.value = response.data
    }
  } catch (err) {
    console.error('加载附件列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 文件选择
const handleFileChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    uploadForm.value.file = uploadFile.raw
  }
}

// 打开上传对话框
const handleUpload = () => {
  uploadDialogVisible.value = true
}

// 确认上传
const handleConfirmUpload = async () => {
  if (!uploadFormRef.value) return

  await uploadFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (!uploadForm.value.file) {
      error('请选择文件', '请先选择要上传的文件')
      return
    }

    uploading.value = true
    try {
      // 压缩图片（如果是图片类型）
      let fileToUpload = uploadForm.value.file
      if (fileToUpload.type.startsWith('image/')) {
        // 项目照片使用 photo 配置，其他使用默认配置
        const imageType = uploadForm.value.attachment_type === 'photo' ? 'photo' : 'default'
        fileToUpload = await smartCompressImage(fileToUpload, imageType)
        console.log('[CaseAttachments] 图片已压缩')
      }

      const response = await knowledgeApi.uploadCaseAttachment(
        props.caseId,
        fileToUpload,
        uploadForm.value.attachment_type,
        uploadForm.value.description || undefined
      )

      if (response.success) {
        success('上传成功', '附件已上传')
        uploadDialogVisible.value = false
        uploadRef.value?.clearFiles()
        uploadForm.value = {
          attachment_type: 'contract',
          description: '',
          file: null
        }
        await loadAttachments()
        emit('update')
      } else {
        error('上传失败', response.error || '未知错误')
      }
    } catch (err) {
      console.error('上传附件失败:', err)
      error('上传失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      uploading.value = false
    }
  })
}

// 下载附件
const handleDownload = (attachment: CaseAttachment) => {
  const url = knowledgeApi.downloadCaseAttachment(attachment.attachment_id)
  window.open(url, '_blank')
}

// 删除附件
const handleDelete = async (attachment: CaseAttachment) => {
  try {
    if (!confirm(`确定要删除附件 "${attachment.original_filename}" 吗？`)) {
      return
    }

    const response = await knowledgeApi.deleteCaseAttachment(attachment.attachment_id)
    if (response.success) {
      success('删除成功', '附件已删除')
      await loadAttachments()
      emit('update')
    } else {
      error('删除失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('删除附件失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 重置
const handleReset = () => {
  // 重新加载附件列表
  loadAttachments()
}

// 生命周期
onMounted(() => {
  loadAttachments()
})
</script>

<style scoped lang="scss">
.case-attachments-tab {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.attachments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.attachment-card {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    border-color: #409eff;
  }

  .attachment-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .attachment-body {
    margin-bottom: 12px;

    .file-name {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      margin-bottom: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .file-info {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #909399;
      margin-bottom: 4px;
    }

    .file-desc {
      font-size: 12px;
      color: #606266;
      margin-top: 8px;
      padding: 8px;
      background: #f5f7fa;
      border-radius: 4px;
    }
  }

  .attachment-actions {
    display: flex;
    gap: 8px;

    .el-button {
      flex: 1;
    }
  }
}
</style>
