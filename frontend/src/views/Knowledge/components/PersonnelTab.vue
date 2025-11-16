<template>
  <div class="personnel-tab">
    <!-- 基本信息 -->
    <Card title="被授权人基本信息">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="140px"
        class="personnel-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="authorized_person_name">
              <el-input v-model="formData.authorized_person_name" placeholder="请输入被授权人姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="authorized_person_id">
              <el-input v-model="formData.authorized_person_id" placeholder="请输入身份证号" maxlength="18" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="authorized_person_gender">
              <el-select v-model="formData.authorized_person_gender" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄" prop="authorized_person_age">
              <el-input-number
                v-model="formData.authorized_person_age"
                :min="18"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位" prop="authorized_person_position">
              <el-input v-model="formData.authorized_person_position" placeholder="请输入职位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="authorized_person_title">
              <el-input v-model="formData.authorized_person_title" placeholder="请输入职称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSave">
                <el-icon><Select /></el-icon>
                保存被授权人信息
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </Card>

    <!-- 附件上传 -->
    <Card title="相关附件" class="mt-4">
      <div class="attachments-grid">
        <!-- 身份证正面 -->
        <div class="attachment-item">
          <div class="attachment-header">
            <el-icon class="icon"><CreditCard /></el-icon>
            <span class="title">被授权人身份证（正面）</span>
          </div>
          <div v-if="attachments.id_card_front" class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ attachments.id_card_front.name }}</span>
            <div class="file-actions">
              <el-button text type="primary" size="small" @click="downloadAttachment('id_card_front')">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button text type="danger" size="small" @click="deleteAttachment('id_card_front')">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <div v-else class="no-file">未上传</div>
          <DocumentUploader
            accept=".jpg,.jpeg,.png,.pdf"
            :show-file-list="false"
            :http-request="createUploadHandler('id_card_front')"
            :auto-compress-image="true"
            :image-type="'id_card'"
            :max-size="10"
          >
            <template #trigger>
              <el-button size="small">
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </template>
          </DocumentUploader>
        </div>

        <!-- 身份证反面 -->
        <div class="attachment-item">
          <div class="attachment-header">
            <el-icon class="icon"><CreditCard /></el-icon>
            <span class="title">被授权人身份证（反面）</span>
          </div>
          <div v-if="attachments.id_card_back" class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ attachments.id_card_back.name }}</span>
            <div class="file-actions">
              <el-button text type="primary" size="small" @click="downloadAttachment('id_card_back')">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button text type="danger" size="small" @click="deleteAttachment('id_card_back')">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <div v-else class="no-file">未上传</div>
          <DocumentUploader
            accept=".jpg,.jpeg,.png,.pdf"
            :show-file-list="false"
            :http-request="createUploadHandler('id_card_back')"
            :auto-compress-image="true"
            :image-type="'id_card'"
            :max-size="10"
          >
            <template #trigger>
              <el-button size="small">
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </template>
          </DocumentUploader>
        </div>

        <!-- 项目经理简历 -->
        <div class="attachment-item">
          <div class="attachment-header">
            <el-icon class="icon"><User /></el-icon>
            <span class="title">项目经理简历</span>
          </div>
          <div v-if="attachments.manager_resume" class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ attachments.manager_resume.name }}</span>
            <div class="file-actions">
              <el-button text type="primary" size="small" @click="downloadAttachment('manager_resume')">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button text type="danger" size="small" @click="deleteAttachment('manager_resume')">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <div v-else class="no-file">未上传</div>
          <DocumentUploader
            accept=".pdf,.doc,.docx"
            :show-file-list="false"
            :http-request="createUploadHandler('manager_resume')"
            :auto-compress-image="false"
            :max-size="20"
          >
            <template #trigger>
              <el-button size="small">
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </template>
          </DocumentUploader>
        </div>

        <!-- 社保证明 -->
        <div class="attachment-item">
          <div class="attachment-header">
            <el-icon class="icon"><DocumentChecked /></el-icon>
            <span class="title">社保证明</span>
          </div>
          <div v-if="attachments.social_security" class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ attachments.social_security.name }}</span>
            <div class="file-actions">
              <el-button text type="primary" size="small" @click="downloadAttachment('social_security')">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button text type="danger" size="small" @click="deleteAttachment('social_security')">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <div v-else class="no-file">未上传</div>
          <DocumentUploader
            accept=".pdf,.jpg,.jpeg,.png"
            :show-file-list="false"
            :http-request="createUploadHandler('social_security')"
            :auto-compress-image="true"
            :image-type="'default'"
            :max-size="20"
          >
            <template #trigger>
              <el-button size="small">
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </template>
          </DocumentUploader>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Card, DocumentUploader } from '@/components'
import { useNotification } from '@/composables'
import { companyApi } from '@/api/endpoints/company'
import { Select, CreditCard, User, DocumentChecked, Document, Upload, Download, Delete } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadRequestOptions } from 'element-plus'

// Props
const props = defineProps<{
  companyId: number
  companyData: any
}>()

// Emits
const emit = defineEmits<{
  (e: 'update'): void
}>()

// Hooks
const { success, error } = useNotification()

// Refs
const formRef = ref<FormInstance>()

// 状态
const saving = ref(false)
const formData = ref({
  authorized_person_name: '',
  authorized_person_id: '',
  authorized_person_gender: '',
  authorized_person_age: undefined as number | undefined,
  authorized_person_position: '',
  authorized_person_title: ''
})

const attachments = ref<Record<string, any>>({
  id_card_front: null,
  id_card_back: null,
  manager_resume: null,
  social_security: null
})

// 表单验证规则
const formRules: FormRules = {
  authorized_person_id: [
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/, message: '请输入正确的身份证号', trigger: 'blur' }
  ]
}

// 监听数据变化
watch(
  () => props.companyData,
  (newData) => {
    if (newData) {
      formData.value = {
        authorized_person_name: newData.authorized_person_name || '',
        authorized_person_id: newData.authorized_person_id || '',
        authorized_person_gender: newData.authorized_person_gender || '',
        authorized_person_age: newData.authorized_person_age || undefined,
        authorized_person_position: newData.authorized_person_position || '',
        authorized_person_title: newData.authorized_person_title || ''
      }
    }
  },
  { immediate: true, deep: true }
)

// 保存基本信息
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const response = await companyApi.updateCompany(props.companyId, {
        authorizedPersonName: formData.value.authorized_person_name,
        authorizedPersonId: formData.value.authorized_person_id,
        authorizedPersonGender: formData.value.authorized_person_gender,
        authorizedPersonAge: formData.value.authorized_person_age,
        authorizedPersonPosition: formData.value.authorized_person_position,
        authorizedPersonTitle: formData.value.authorized_person_title
      })

      if (response.success) {
        success('保存成功', '被授权人信息已更新')
        emit('update')
      }
    } catch (err) {
      console.error('保存被授权人信息失败:', err)
      error('保存失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      saving.value = false
    }
  })
}

// 创建上传处理器工厂函数（用于DocumentUploader）
const createUploadHandler = (qualKey: string) => {
  return async (options: UploadRequestOptions) => {
    const { file, onSuccess, onError } = options

    try {
      const response = await companyApi.uploadQualification(
        props.companyId,
        qualKey,
        file as File,
        {}
      )

      if (response.success) {
        success('上传成功', '附件上传成功')
        loadAttachments()
        emit('update')
        onSuccess(response)
      } else {
        throw new Error(response.error || '上传失败')
      }
    } catch (err) {
      console.error('上传附件失败:', err)
      const errorMsg = err instanceof Error ? err.message : '未知错误'
      error('上传失败', errorMsg)
      onError(err as Error)
    }
  }
}

// 下载附件
const downloadAttachment = (type: string) => {
  window.open(`/api/companies/${props.companyId}/qualifications/${type}/download`)
}

// 删除附件
const deleteAttachment = async (type: string) => {
  if (!confirm('确定要删除此附件吗？')) return

  try {
    const response = await fetch(`/api/companies/${props.companyId}/qualifications/${type}`, {
      method: 'DELETE'
    })
    if (!response.ok) throw new Error('删除失败')

    success('删除成功', '附件已删除')
    loadAttachments()
    emit('update')
  } catch (err) {
    console.error('删除附件失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 加载附件
const loadAttachments = async () => {
  try {
    const response = await companyApi.getCompanyQualifications(props.companyId)
    if (response.success && response.data) {
      const data = response.data
      attachments.value = {
        id_card_front: data.id_card_front ? { name: data.id_card_front.original_filename } : null,
        id_card_back: data.id_card_back ? { name: data.id_card_back.original_filename } : null,
        manager_resume: data.manager_resume ? { name: data.manager_resume.original_filename } : null,
        social_security: data.social_security ? { name: data.social_security.original_filename } : null
      }
    }
  } catch (err) {
    console.error('加载附件失败:', err)
  }
}

// 生命周期
onMounted(() => {
  loadAttachments()
})
</script>

<style scoped lang="scss">
.personnel-tab {
  .personnel-form {
    // 移除 max-width 限制，让表单占满整个容器宽度
  }

  .mt-4 {
    margin-top: 20px;
  }

  .attachments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;

    .attachment-item {
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      padding: 16px;
      background: #fafafa;

      .attachment-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: 500;
        color: #303133;

        .icon {
          font-size: 20px;
          color: #409eff;
        }
      }

      .file-info {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px;
        background: white;
        border-radius: 4px;
        margin-bottom: 12px;

        .file-icon {
          font-size: 18px;
          color: #606266;
          flex-shrink: 0;
        }

        .file-name {
          flex: 1;
          font-size: 13px;
          color: #303133;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .file-actions {
          display: flex;
          gap: 4px;
        }
      }

      .no-file {
        padding: 12px;
        text-align: center;
        color: #909399;
        font-size: 13px;
        background: white;
        border-radius: 4px;
        margin-bottom: 12px;
      }
    }
  }
}
</style>
