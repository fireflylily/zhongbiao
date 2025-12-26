<template>
  <div class="resume-attachments-tab">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>简历附件</span>
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
            <el-icon :size="32" :color="getAttachmentColor(attachment.attachment_category)">
              <component :is="getAttachmentIcon(attachment.attachment_category)" />
            </el-icon>
            <el-tag :type="getAttachmentTagType(attachment.attachment_category)" size="small">
              {{ getAttachmentLabel(attachment.attachment_category) }}
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
      title="上传简历附件"
      width="500px"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadFormRules"
        label-width="120px"
      >
        <el-form-item label="附件类型" prop="attachment_category">
          <el-select v-model="uploadForm.attachment_category" placeholder="请选择附件类型" style="width: 100%">
            <el-option label="简历文件" value="resume" />
            <el-option label="身份证" value="id_card" />
            <el-option label="学历证书" value="education" />
            <el-option label="学位证书" value="degree" />
            <el-option label="资质证书" value="qualification" />
            <el-option label="获奖证书" value="award" />
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
  Postcard,
  Tickets,
  Medal,
  TrophyBase,
  Files
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadInstance, UploadFile } from 'element-plus'
import { ElMessageBox } from 'element-plus'
import type { ResumeAttachment } from '@/types'

// Props
const props = defineProps<{
  resumeId: number
  resumeData: any
}>()

// Emits
const emit = defineEmits<{
  update: []
}>()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const attachments = ref<ResumeAttachment[]>([])
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const uploadForm = ref({
  attachment_category: 'resume' as 'resume' | 'id_card' | 'education' | 'degree' | 'qualification' | 'award' | 'other',
  description: '',
  file: null as File | null
})

const uploadFormRules: FormRules = {
  attachment_category: [
    { required: true, message: '请选择附件类型', trigger: 'change' }
  ]
}

// 获取附件图标
const getAttachmentIcon = (category: string) => {
  switch (category) {
    case 'resume': return Document
    case 'id_card': return Postcard
    case 'education': return Tickets
    case 'degree': return Tickets
    case 'qualification': return Medal
    case 'award': return TrophyBase
    default: return Files
  }
}

// 获取附件颜色
const getAttachmentColor = (category: string) => {
  switch (category) {
    case 'resume': return '#409eff'
    case 'id_card': return '#f56c6c'
    case 'education': return '#67c23a'
    case 'degree': return '#e6a23c'
    case 'qualification': return '#909399'
    case 'award': return '#ff9800'
    default: return '#909399'
  }
}

// 获取附件标签类型
const getAttachmentTagType = (category: string) => {
  switch (category) {
    case 'resume': return 'primary'
    case 'id_card': return 'danger'
    case 'education': return 'success'
    case 'degree': return 'warning'
    case 'qualification': return 'info'
    case 'award': return 'warning'
    default: return 'info'
  }
}

// 获取附件标签文本
const getAttachmentLabel = (category: string) => {
  switch (category) {
    case 'resume': return '简历文件'
    case 'id_card': return '身份证'
    case 'education': return '学历证书'
    case 'degree': return '学位证书'
    case 'qualification': return '资质证书'
    case 'award': return '获奖证书'
    default: return '其他材料'
  }
}

// 加载附件列表
const loadAttachments = async () => {
  loading.value = true
  try {
    const response = await knowledgeApi.getResumeAttachments(props.resumeId)
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
        // 根据附件类型选择压缩配置
        const imageType = uploadForm.value.attachment_category === 'id_card' ? 'id_card' : 'photo'
        fileToUpload = await smartCompressImage(fileToUpload, imageType)
        console.log('[ResumeAttachments] 图片已压缩')
      }

      const response = await knowledgeApi.uploadResumeAttachment(
        props.resumeId,
        fileToUpload,
        uploadForm.value.attachment_category,
        uploadForm.value.description || undefined
      )

      if (response.success) {
        success('上传成功', '附件已上传')
        uploadDialogVisible.value = false
        uploadRef.value?.clearFiles()
        uploadForm.value = {
          attachment_category: 'resume',
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
const handleDownload = (attachment: ResumeAttachment) => {
  const url = knowledgeApi.downloadResumeAttachment(attachment.attachment_id)
  window.open(url, '_blank')
}

// 删除附件
const handleDelete = async (attachment: ResumeAttachment) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除附件 "${attachment.original_filename}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await knowledgeApi.deleteResumeAttachment(attachment.attachment_id)
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

// 生命周期
onMounted(() => {
  loadAttachments()
})
</script>

<style scoped lang="scss">
.resume-attachments-tab {
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
