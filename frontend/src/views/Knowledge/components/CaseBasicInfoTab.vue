<template>
  <div class="case-basic-info-tab">
    <!-- 基本信息卡片 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <span>案例基本信息</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="140px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属企业" prop="company_id">
              <el-select
                v-model="formData.company_id"
                placeholder="请选择企业"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="company in companies"
                  :key="company.company_id"
                  :label="company.company_name"
                  :value="company.company_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="案例标题" prop="case_title">
              <el-input v-model="formData.case_title" placeholder="请输入案例标题/合同名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="案例编号" prop="case_number">
              <el-input v-model="formData.case_number" placeholder="请输入案例编号（可选）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="formData.customer_name" placeholder="请输入甲方客户名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品分类" prop="product_category">
              <el-select v-model="formData.product_category" placeholder="请选择产品分类" clearable style="width: 100%">
                <el-option label="风控产品" value="风控产品" />
                <el-option label="实修" value="实修" />
                <el-option label="免密" value="免密" />
                <el-option label="风控位置" value="风控位置" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属行业" prop="industry">
              <el-select v-model="formData.industry" placeholder="请选择行业" clearable style="width: 100%">
                <el-option label="科技" value="科技" />
                <el-option label="制造业" value="制造业" />
                <el-option label="金融" value="金融" />
                <el-option label="教育" value="教育" />
                <el-option label="医疗" value="医疗" />
                <el-option label="建筑" value="建筑" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同类型" prop="contract_type">
              <el-radio-group v-model="formData.contract_type">
                <el-radio label="合同">合同</el-radio>
                <el-radio label="订单">订单</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同金额" prop="contract_amount">
              <el-input v-model="formData.contract_amount" placeholder="如：100万元、百万级">
                <template #append>元</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最终客户" prop="final_customer_name">
              <el-input
                v-model="formData.final_customer_name"
                placeholder="订单类型时填写最终客户"
                :disabled="formData.contract_type !== '订单'"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同开始日期" prop="contract_start_date">
              <el-date-picker
                v-model="formData.contract_start_date"
                type="date"
                placeholder="选择开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同结束日期" prop="contract_end_date">
              <el-date-picker
                v-model="formData.contract_end_date"
                type="date"
                placeholder="选择结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">客户联系方式</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="联系人姓名" prop="party_a_contact_name">
              <el-input v-model="formData.party_a_contact_name" placeholder="联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系电话" prop="party_a_contact_phone">
              <el-input v-model="formData.party_a_contact_phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系邮箱" prop="party_a_contact_email">
              <el-input v-model="formData.party_a_contact_email" placeholder="邮箱地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 附件管理卡片 -->
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
      @close="handleUploadDialogClose"
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
            v-model:file-list="uploadFileList"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
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
import { ref, watch, onMounted } from 'vue'
import { Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import { companyApi } from '@/api/endpoints/company'
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

// 基本信息表单
const formRef = ref<FormInstance>()
const saving = ref(false)
const companies = ref<any[]>([])
const formData = ref({
  company_id: null as number | null,
  case_title: '',
  case_number: '',
  customer_name: '',
  product_category: '',
  industry: '金融',
  contract_type: '合同' as '订单' | '合同',
  final_customer_name: '',
  contract_amount: '',
  contract_start_date: '',
  contract_end_date: '',
  party_a_contact_name: '',
  party_a_contact_phone: '',
  party_a_contact_email: ''
})

const formRules: FormRules = {
  company_id: [
    { required: true, message: '请选择所属企业', trigger: 'change' }
  ],
  case_title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' }
  ],
  customer_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  contract_type: [
    { required: true, message: '请选择合同类型', trigger: 'change' }
  ]
}

// 附件管理
const loading = ref(false)
const attachments = ref<CaseAttachment[]>([])
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const uploadFileList = ref<UploadFile[]>([])
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

// 监听 caseData 变化，同步到 formData
watch(
  () => props.caseData,
  (newData) => {
    if (newData) {
      formData.value = {
        company_id: newData.company_id || null,
        case_title: newData.case_title || '',
        case_number: newData.case_number || '',
        customer_name: newData.customer_name || '',
        product_category: newData.product_category || '',
        industry: newData.industry || '金融',
        contract_type: newData.contract_type || '合同',
        final_customer_name: newData.final_customer_name || '',
        contract_amount: newData.contract_amount || '',
        contract_start_date: newData.contract_start_date || '',
        contract_end_date: newData.contract_end_date || '',
        party_a_contact_name: newData.party_a_contact_name || '',
        party_a_contact_phone: newData.party_a_contact_phone || '',
        party_a_contact_email: newData.party_a_contact_email || ''
      }
    }
  },
  { immediate: true, deep: true }
)

// 加载企业列表
const loadCompanies = async () => {
  try {
    const response = await companyApi.getCompanies()
    if (response.success && response.data) {
      companies.value = response.data
    }
  } catch (err) {
    console.error('加载企业列表失败:', err)
  }
}

// 保存基本信息
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const response = await knowledgeApi.updateCase(props.caseId, formData.value)
      if (response.success) {
        success('保存成功', '案例信息已更新')
        emit('update')
      } else {
        error('保存失败', response.error || '未知错误')
      }
    } catch (err) {
      console.error('保存案例信息失败:', err)
      error('保存失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      saving.value = false
    }
  })
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
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
    // 验证文件大小（20MB限制）
    const maxSize = 20 * 1024 * 1024
    if (uploadFile.raw.size > maxSize) {
      error('文件过大', '文件大小不能超过20MB')
      uploadFileList.value = []
      uploadForm.value.file = null
      return
    }
    uploadForm.value.file = uploadFile.raw
  }
}

// 文件移除
const handleFileRemove = () => {
  uploadForm.value.file = null
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
        console.log('[CaseBasicInfo] 图片已压缩')
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

// 关闭上传对话框
const handleUploadDialogClose = () => {
  uploadFileList.value = []
  uploadForm.value = {
    attachment_type: 'contract',
    description: '',
    file: null
  }
  uploadFormRef.value?.resetFields()
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

// 生命周期
onMounted(() => {
  loadCompanies()
  loadAttachments()
})
</script>

<style scoped lang="scss">
.case-basic-info-tab {
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
