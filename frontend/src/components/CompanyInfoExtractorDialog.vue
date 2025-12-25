<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="900px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <!-- 步骤条 -->
    <el-steps :active="currentStep" finish-status="success" class="extractor-steps">
      <el-step title="上传文档" />
      <el-step title="AI提取" />
      <el-step title="预览确认" />
    </el-steps>

    <!-- 步骤1: 上传文档 -->
    <div v-show="currentStep === 0" class="step-content">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".docx,.doc"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="fileList"
        class="upload-area"
      >
        <i class="bi bi-file-earmark-word upload-icon"></i>
        <div class="el-upload__text">
          拖拽历史标书到此处，或 <em>点击选择文件</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .docx/.doc 格式的投标文件，系统将自动提取公司信息和资质图片
          </div>
        </template>
      </el-upload>

      <!-- AI模型选择 -->
      <div class="model-select">
        <span class="label">AI模型：</span>
        <el-select v-model="selectedModel" size="small" style="width: 200px">
          <el-option label="GPT-4o-mini (快速)" value="gpt-4o-mini" />
          <el-option label="DeepSeek-V3 (推荐)" value="yuanjing-deepseek-v3" />
          <el-option label="Qwen3-235B (最强)" value="yuanjing-qwen3-235b" />
        </el-select>
      </div>
    </div>

    <!-- 步骤2: 提取进度 -->
    <div v-show="currentStep === 1" class="step-content">
      <div class="extraction-progress">
        <el-progress
          :percentage="extractionProgress"
          :status="extractionStatus"
          :stroke-width="16"
          :text-inside="true"
        />
        <div class="progress-text">{{ progressText }}</div>

        <!-- 提取日志 -->
        <el-scrollbar height="180px" class="extraction-log">
          <div v-for="(log, index) in extractionLogs" :key="index" class="log-item">
            <el-icon v-if="log.status === 'success'" color="#67c23a"><Check /></el-icon>
            <el-icon v-else-if="log.status === 'loading'" class="is-loading" color="#409eff"><Loading /></el-icon>
            <el-icon v-else color="#f56c6c"><Close /></el-icon>
            <span>{{ log.message }}</span>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <!-- 步骤3: 预览确认 -->
    <div v-show="currentStep === 2" class="step-content preview-content">
      <el-tabs v-model="previewTab" class="preview-tabs">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-scrollbar height="400px">
            <el-form :model="extractedData.company_info" label-width="140px" class="preview-form">
              <el-row :gutter="20">
                <el-col :span="12" v-for="field in basicInfoFields" :key="field.key">
                  <el-form-item :label="field.label">
                    <el-input
                      v-model="extractedData.company_info[field.key]"
                      :placeholder="field.placeholder || `请输入${field.label}`"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-scrollbar>
        </el-tab-pane>

        <!-- 被授权人信息 -->
        <el-tab-pane label="被授权人" name="personnel">
          <el-form :model="extractedData.authorized_person" label-width="140px" class="preview-form">
            <el-row :gutter="20">
              <el-col :span="12" v-for="field in personnelFields" :key="field.key">
                <el-form-item :label="field.label">
                  <el-input
                    v-model="extractedData.authorized_person[field.key]"
                    :placeholder="field.placeholder || `请输入${field.label}`"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- 财务信息 -->
        <el-tab-pane label="财务信息" name="financial">
          <el-form :model="extractedData.financial_info" label-width="140px" class="preview-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="开户银行">
                  <el-input
                    v-model="extractedData.financial_info.bank_name"
                    placeholder="请输入开户银行"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="银行账号">
                  <el-input
                    v-model="extractedData.financial_info.bank_account"
                    placeholder="请输入银行账号"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- 资质图片 -->
        <el-tab-pane name="qualifications">
          <template #label>
            <span>
              资质文件
              <el-badge
                v-if="confirmedImagesCount > 0"
                :value="confirmedImagesCount"
                type="success"
                class="badge-margin"
              />
            </span>
          </template>
          <el-scrollbar height="400px">
            <div v-if="extractedData.qualification_images.length === 0" class="no-images">
              <el-empty description="未从文档中提取到图片" />
            </div>
            <el-row v-else :gutter="16" class="image-grid">
              <el-col :span="8" v-for="(img, index) in extractedData.qualification_images" :key="index">
                <el-card class="image-card" :class="{ 'is-confirmed': img.confirmed }" shadow="hover">
                  <div class="image-preview" @click="previewImage(img)">
                    <el-image
                      :src="getImageSrc(img)"
                      fit="contain"
                      :preview-src-list="[getImageSrc(img)]"
                      :preview-teleported="true"
                    >
                      <template #error>
                        <div class="image-error">
                          <el-icon><Picture /></el-icon>
                        </div>
                      </template>
                    </el-image>
                  </div>
                  <div class="image-info">
                    <el-select
                      v-model="img.guessed_type"
                      size="small"
                      placeholder="选择资质类型"
                      @change="handleTypeChange(img)"
                    >
                      <el-option
                        v-for="type in qualificationTypes"
                        :key="type.key"
                        :label="type.name"
                        :value="type.key"
                      />
                    </el-select>
                    <el-checkbox v-model="img.confirmed" size="small">
                      导入此图片
                    </el-checkbox>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-scrollbar>
        </el-tab-pane>
      </el-tabs>

      <!-- 提取统计 -->
      <div class="extraction-stats">
        <el-tag type="info">
          基本信息: {{ filledFieldsCount }}/{{ basicInfoFields.length }} 字段
        </el-tag>
        <el-tag type="info">
          资质图片: {{ confirmedImagesCount }}/{{ extractedData.qualification_images.length }} 张
        </el-tag>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="currentStep > 0 && currentStep < 2"
          @click="handlePrev"
          :disabled="extracting"
        >
          上一步
        </el-button>
        <el-button
          v-if="currentStep === 0"
          type="primary"
          @click="startExtraction"
          :disabled="!selectedFile"
        >
          开始提取
        </el-button>
        <el-button
          v-if="currentStep === 2"
          type="primary"
          @click="handleConfirm"
          :loading="saving"
        >
          {{ isNewMode ? '创建公司' : '保存信息' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { companyApi } from '@/api/endpoints/company'
import { useNotification } from '@/composables'
import { Check, Close, Loading, Picture } from '@element-plus/icons-vue'

// Props
const props = defineProps<{
  modelValue: boolean
  companyId?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success', companyId: number): void
}>()

// 响应式状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isNewMode = computed(() => !props.companyId)
const dialogTitle = computed(() => isNewMode.value ? '从标书创建公司' : '从标书提取信息')

const currentStep = ref(0)
const fileList = ref<any[]>([])
const selectedFile = ref<File | null>(null)
const selectedModel = ref('gpt-4o-mini')
const extracting = ref(false)
const saving = ref(false)
const extractionProgress = ref(0)
const extractionStatus = ref<'' | 'success' | 'exception'>('')
const progressText = ref('')
const extractionLogs = ref<Array<{ message: string; status: string }>>([])
const previewTab = ref('basic')

// 提取结果
const extractedData = ref<{
  company_info: Record<string, any>
  authorized_person: Record<string, any>
  financial_info: Record<string, any>
  qualification_images: Array<{
    index: number
    image_data: string
    content_type: string
    original_filename: string
    guessed_type: string
    guessed_type_name: string
    confidence: number
    confirmed: boolean
  }>
}>({
  company_info: {},
  authorized_person: {},
  financial_info: {},
  qualification_images: []
})

// 字段定义
const basicInfoFields = [
  { key: 'company_name', label: '公司名称' },
  { key: 'social_credit_code', label: '统一社会信用代码', placeholder: '18位代码' },
  { key: 'legal_representative', label: '法定代表人' },
  { key: 'legal_representative_position', label: '法定代表人职务' },
  { key: 'registered_capital', label: '注册资本', placeholder: '如：1000万元' },
  { key: 'establish_date', label: '成立日期', placeholder: 'YYYY-MM-DD' },
  { key: 'company_type', label: '公司类型' },
  { key: 'registered_address', label: '注册地址' },
  { key: 'office_address', label: '办公地址' },
  { key: 'fixed_phone', label: '联系电话' },
  { key: 'email', label: '电子邮箱' },
  { key: 'employee_count', label: '员工人数' }
]

const personnelFields = [
  { key: 'name', label: '被授权人姓名' },
  { key: 'id_number', label: '身份证号', placeholder: '18位身份证号' },
  { key: 'gender', label: '性别', placeholder: '男/女' },
  { key: 'position', label: '职位' },
  { key: 'title', label: '职称' },
  { key: 'phone', label: '联系电话' }
]

const qualificationTypes = [
  { key: 'business_license', name: '营业执照' },
  { key: 'legal_id_front', name: '法人身份证正面' },
  { key: 'legal_id_back', name: '法人身份证反面' },
  { key: 'auth_id_front', name: '被授权人身份证正面' },
  { key: 'auth_id_back', name: '被授权人身份证反面' },
  { key: 'iso9001', name: 'ISO9001认证' },
  { key: 'iso14001', name: 'ISO14001认证' },
  { key: 'iso20000', name: 'ISO20000认证' },
  { key: 'iso27001', name: 'ISO27001认证' },
  { key: 'cmmi', name: 'CMMI认证' },
  { key: 'itss', name: 'ITSS认证' },
  { key: 'value_added_telecom_permit', name: '增值电信许可证' },
  { key: 'level_protection', name: '等级保护认证' },
  { key: 'software_copyright', name: '软件著作权' },
  { key: 'patent_certificate', name: '专利证书' },
  { key: 'high_tech_enterprise', name: '高新技术企业证书' },
  { key: 'audit_report', name: '审计报告' },
  { key: 'bank_account_permit', name: '开户许可证' },
  { key: 'unknown', name: '其他/未识别' }
]

const { success, error } = useNotification()

// 计算属性
const filledFieldsCount = computed(() => {
  return Object.values(extractedData.value.company_info).filter(v => v).length
})

const confirmedImagesCount = computed(() => {
  return extractedData.value.qualification_images.filter(img => img.confirmed).length
})

// 文件处理
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

const handleFileRemove = () => {
  selectedFile.value = null
  fileList.value = []
}

// 获取图片src
const getImageSrc = (img: any) => {
  return `data:${img.content_type};base64,${img.image_data}`
}

// 预览图片
const previewImage = (img: any) => {
  // Element Plus的el-image组件会自动处理预览
}

// 资质类型变更
const handleTypeChange = (img: any) => {
  // 自动勾选确认
  if (img.guessed_type !== 'unknown') {
    img.confirmed = true
  }
}

// 上一步
const handlePrev = () => {
  if (currentStep.value > 0) {
    currentStep.value = 0
    extractionProgress.value = 0
    extractionLogs.value = []
    extractionStatus.value = ''
  }
}

// 开始提取
const startExtraction = async () => {
  if (!selectedFile.value) return

  extracting.value = true
  currentStep.value = 1
  extractionProgress.value = 0
  extractionLogs.value = []
  extractionStatus.value = ''
  progressText.value = '正在上传文档...'

  try {
    addLog('正在上传文档...', 'loading')
    extractionProgress.value = 10

    // 创建FormData
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('model', selectedModel.value)

    updateLastLog('success')
    addLog('文档上传成功', 'success')
    extractionProgress.value = 30

    addLog('正在解析文档结构...', 'loading')
    progressText.value = '正在AI提取...'
    extractionProgress.value = 40

    // 调用API
    const result = await companyApi.extractFromTender(formData)

    updateLastLog('success')
    extractionProgress.value = 80

    if (result.success) {
      addLog('公司信息提取完成', 'success')
      addLog(`识别到 ${result.qualification_images?.length || 0} 张资质图片`, 'success')

      extractionProgress.value = 100
      extractionStatus.value = 'success'
      progressText.value = '提取完成!'

      // 填充数据
      extractedData.value = {
        company_info: result.company_info || {},
        authorized_person: result.authorized_person || {},
        financial_info: result.financial_info || {},
        qualification_images: (result.qualification_images || []).map((img: any) => ({
          ...img,
          confirmed: img.confidence >= 0.6
        }))
      }

      // 自动跳转到预览
      setTimeout(() => {
        currentStep.value = 2
      }, 800)
    } else {
      throw new Error(result.error || '提取失败')
    }
  } catch (err: any) {
    extractionStatus.value = 'exception'
    progressText.value = '提取失败'
    addLog(`错误: ${err.message}`, 'error')
    error('提取失败', err.message)
  } finally {
    extracting.value = false
  }
}

// 日志管理
const addLog = (message: string, status: string) => {
  extractionLogs.value.push({ message, status })
}

const updateLastLog = (status: string) => {
  const lastLog = extractionLogs.value[extractionLogs.value.length - 1]
  if (lastLog && lastLog.status === 'loading') {
    lastLog.status = status
  }
}

// 确认保存
const handleConfirm = async () => {
  saving.value = true

  try {
    // 准备公司数据
    const companyData = {
      // 基本信息
      company_name: extractedData.value.company_info.company_name,
      social_credit_code: extractedData.value.company_info.social_credit_code,
      legal_representative: extractedData.value.company_info.legal_representative,
      legal_representative_position: extractedData.value.company_info.legal_representative_position,
      legal_representative_gender: extractedData.value.company_info.legal_representative_gender,
      registered_capital: extractedData.value.company_info.registered_capital,
      establish_date: extractedData.value.company_info.establish_date,
      company_type: extractedData.value.company_info.company_type,
      registered_address: extractedData.value.company_info.registered_address,
      office_address: extractedData.value.company_info.office_address,
      fixed_phone: extractedData.value.company_info.fixed_phone,
      email: extractedData.value.company_info.email,
      employee_count: extractedData.value.company_info.employee_count,
      // 被授权人信息
      authorized_person_name: extractedData.value.authorized_person.name,
      authorized_person_id: extractedData.value.authorized_person.id_number,
      authorized_person_gender: extractedData.value.authorized_person.gender,
      authorized_person_position: extractedData.value.authorized_person.position,
      authorized_person_title: extractedData.value.authorized_person.title,
      // 财务信息
      bank_name: extractedData.value.financial_info.bank_name,
      bank_account: extractedData.value.financial_info.bank_account
    }

    let targetCompanyId: number

    if (isNewMode.value) {
      // 创建新公司
      if (!companyData.company_name) {
        error('保存失败', '公司名称不能为空')
        saving.value = false
        return
      }

      const createResult = await companyApi.createCompany({
        name: companyData.company_name
      })

      if (!createResult.success || !createResult.data) {
        throw new Error(createResult.error || '创建公司失败')
      }

      targetCompanyId = createResult.data.company_id

      // 更新公司详细信息
      await companyApi.updateCompany(targetCompanyId, companyData)
    } else {
      // 更新现有公司
      targetCompanyId = props.companyId!
      await companyApi.updateCompany(targetCompanyId, companyData)
    }

    // 上传确认的资质图片
    const confirmedImages = extractedData.value.qualification_images.filter(img => img.confirmed)
    if (confirmedImages.length > 0) {
      for (const img of confirmedImages) {
        try {
          // 将base64转换为File对象
          const byteCharacters = atob(img.image_data)
          const byteNumbers = new Array(byteCharacters.length)
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i)
          }
          const byteArray = new Uint8Array(byteNumbers)
          const blob = new Blob([byteArray], { type: img.content_type })
          const file = new File([blob], img.original_filename, { type: img.content_type })

          // 上传资质文件
          await companyApi.uploadQualification(
            targetCompanyId,
            img.guessed_type,
            file,
            {}
          )
        } catch (uploadErr) {
          console.error('上传资质图片失败:', uploadErr)
          // 继续上传其他图片
        }
      }
    }

    success('保存成功', isNewMode.value ? '公司信息已创建' : '公司信息已更新')
    emit('success', targetCompanyId)
    visible.value = false
  } catch (err: any) {
    error('保存失败', err.message)
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  // 重置状态
  currentStep.value = 0
  fileList.value = []
  selectedFile.value = null
  extractionProgress.value = 0
  extractionLogs.value = []
  extractionStatus.value = ''
  extractedData.value = {
    company_info: {},
    authorized_person: {},
    financial_info: {},
    qualification_images: []
  }
  previewTab.value = 'basic'
  visible.value = false
}

// 监听对话框打开，重置状态
watch(visible, (newVal) => {
  if (newVal) {
    currentStep.value = 0
    fileList.value = []
    selectedFile.value = null
    extractionProgress.value = 0
    extractionLogs.value = []
  }
})
</script>

<style scoped lang="scss">
.extractor-steps {
  margin-bottom: 24px;
  padding: 0 40px;
}

.step-content {
  min-height: 350px;
  padding: 16px 0;
}

.upload-area {
  :deep(.el-upload-dragger) {
    padding: 40px 20px;
  }

  .upload-icon {
    font-size: 56px;
    color: var(--el-color-primary);
    margin-bottom: 12px;
  }
}

.model-select {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed #dcdfe6;

  .label {
    color: #606266;
    font-size: 14px;
  }
}

.extraction-progress {
  text-align: center;
  padding: 20px;

  .progress-text {
    margin-top: 16px;
    font-size: 15px;
    color: var(--el-text-color-regular);
  }
}

.extraction-log {
  margin-top: 24px;
  text-align: left;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 6px;

  .log-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    font-size: 13px;
    color: #606266;

    .is-loading {
      animation: rotating 1.5s linear infinite;
    }
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.preview-content {
  .preview-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 16px;
    }
  }
}

.preview-form {
  padding: 0 16px;

  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

.no-images {
  padding: 40px;
}

.image-grid {
  padding: 8px;
}

.image-card {
  margin-bottom: 16px;
  border: 2px solid transparent;
  transition: all 0.3s;

  &.is-confirmed {
    border-color: var(--el-color-success);
  }

  :deep(.el-card__body) {
    padding: 12px;
  }

  .image-preview {
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f7fa;
    border-radius: 4px;
    overflow: hidden;
    cursor: pointer;

    :deep(.el-image) {
      max-width: 100%;
      max-height: 100%;
    }

    .image-error {
      color: #c0c4cc;
      font-size: 32px;
    }
  }

  .image-info {
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;

    :deep(.el-select) {
      width: 100%;
    }
  }
}

.extraction-stats {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.badge-margin {
  margin-left: 6px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
