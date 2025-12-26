<template>
  <div class="financial-tab">
    <!-- 财务资质文件 -->
    <Card title="财务资质文件" class="mb-4">
      <el-row :gutter="20">
        <el-col
          v-for="qualification in financialQualifications"
          :key="qualification.key"
          :span="12"
        >
          <QualificationCard
            :qualification="qualification"
            :file-info="qualificationFiles[qualification.key]"
            @upload="handleUploadFile(qualification.key, $event)"
            @download="handleDownloadFile"
            @delete="handleDeleteFile"
          />
        </el-col>
      </el-row>
    </Card>

    <!-- 银行信息 -->
    <Card title="银行账户信息">
      <el-form
        ref="bankFormRef"
        :model="bankForm"
        label-width="140px"
        class="bank-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户行全称">
              <el-input v-model="bankForm.bank_name" placeholder="请输入开户行全称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号">
              <el-input v-model="bankForm.bank_account" placeholder="请输入银行账号" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </Card>

    <!-- 股权结构 -->
    <Card title="股权结构信息" class="mt-4">
      <el-form
        ref="equityFormRef"
        :model="equityForm"
        label-width="140px"
        class="equity-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实际控制人">
              <el-input v-model="equityForm.actual_controller" placeholder="请输入实际控制人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="控股股东">
              <el-input v-model="equityForm.controlling_shareholder" placeholder="请输入控股股东" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 股东列表 -->
      <div class="shareholders-section">
        <div class="section-header">
          <h6>股东/投资人列表</h6>
          <el-button type="primary" size="small" @click="showAddShareholderDialog">
            <el-icon><Plus /></el-icon>
            添加股东
          </el-button>
        </div>

        <el-table v-if="shareholders.length > 0" :data="shareholders" stripe>
          <el-table-column prop="name" label="股东名称" min-width="150" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="ratio" label="出资比例" width="120" />
          <el-table-column label="控股股东" width="100" align="center">
            <template #default="{ $index }">
              <el-radio
                v-model="controllingShareholderIndex"
                :label="$index"
                @change="handleControllingShareholderChange"
              >
                <span></span>
              </el-radio>
            </template>
          </el-table-column>
          <el-table-column label="实际控制人" width="110" align="center">
            <template #default="{ $index }">
              <el-radio
                v-model="actualControllerIndex"
                :label="$index"
                @change="handleActualControllerChange"
              >
                <span></span>
              </el-radio>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row, $index }">
              <el-button text type="primary" size="small" @click="handleEditShareholder($index)">
                编辑
              </el-button>
              <el-button text type="danger" size="small" @click="handleDeleteShareholder($index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无股东信息" :image-size="100" />
      </div>
    </Card>

    <!-- 管理关系 -->
    <Card title="管理关系信息" class="mt-4">
      <el-form
        ref="managementFormRef"
        :model="managementForm"
        label-width="140px"
        class="management-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="管理单位名称">
              <el-input v-model="managementForm.managing_unit_name" placeholder="如有管理单位请输入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="被管理单位名称">
              <el-input v-model="managementForm.managed_unit_name" placeholder="如有被管理单位请输入" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </Card>

    <!-- 保存按钮 -->
    <div class="save-section">
      <el-button type="primary" size="large" :loading="saving" @click="handleSaveAll">
        <el-icon><Select /></el-icon>
        保存财务信息
      </el-button>
    </div>

    <!-- 添加/编辑股东对话框 -->
    <el-dialog
      v-model="shareholderDialogVisible"
      :title="editingIndex === -1 ? '添加股东' : '编辑股东'"
      width="500px"
    >
      <el-form
        ref="shareholderFormRef"
        :model="shareholderForm"
        :rules="shareholderRules"
        label-width="100px"
      >
        <el-form-item label="股东名称" prop="name">
          <el-input v-model="shareholderForm.name" placeholder="请输入股东名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="shareholderForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="企业" value="企业" />
            <el-option label="自然人" value="自然人" />
          </el-select>
        </el-form-item>
        <el-form-item label="出资比例" prop="ratio">
          <el-input v-model="shareholderForm.ratio" placeholder="如：30%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shareholderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmShareholder">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Card } from '@/components'
import QualificationCard from './QualificationCard.vue'
import { useNotification } from '@/composables'
import { companyApi } from '@/api/endpoints/company'
import { Plus, Select, Document, Tickets } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessageBox } from 'element-plus'

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
const bankFormRef = ref<FormInstance>()
const equityFormRef = ref<FormInstance>()
const managementFormRef = ref<FormInstance>()
const shareholderFormRef = ref<FormInstance>()

// 状态
const saving = ref(false)
const loading = ref(false)

// 财务资质定义
const financialQualifications = ref([
  {
    key: 'audit_report',
    name: '财务审计报告',
    icon: Document,
    required: false,
    allowMultiple: true
  },
  {
    key: 'taxpayer_certificate',
    name: '纳税人资格证明',
    icon: Tickets,
    required: false,
    allowMultiple: false
  }
])

// 资质文件数据
const qualificationFiles = ref<Record<string, any>>({})

// 表单数据
const bankForm = ref({
  bank_name: '',
  bank_account: ''
})

const equityForm = ref({
  actual_controller: '',
  controlling_shareholder: ''
})

const managementForm = ref({
  managing_unit_name: '',
  managed_unit_name: ''
})

const shareholders = ref<any[]>([])

// 控股股东和实际控制人的索引（-1表示未选择）
const controllingShareholderIndex = ref<number>(-1)
const actualControllerIndex = ref<number>(-1)

// 股东对话框
const shareholderDialogVisible = ref(false)
const editingIndex = ref(-1)
const shareholderForm = ref({
  name: '',
  type: '',
  ratio: ''
})

const shareholderRules: FormRules = {
  name: [{ required: true, message: '请输入股东名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  ratio: [{ required: true, message: '请输入出资比例', trigger: 'blur' }]
}

// 监听数据变化
watch(
  () => props.companyData,
  (newData) => {
    if (newData) {
      bankForm.value = {
        bank_name: newData.bank_name || '',
        bank_account: newData.bank_account || ''
      }

      equityForm.value = {
        actual_controller: newData.actual_controller || '',
        controlling_shareholder: newData.controlling_shareholder || ''
      }

      managementForm.value = {
        managing_unit_name: newData.managing_unit_name || '',
        managed_unit_name: newData.managed_unit_name || ''
      }

      // 解析股东信息
      try {
        const shareholdersInfo = newData.shareholders_info
        if (shareholdersInfo) {
          shareholders.value = typeof shareholdersInfo === 'string'
            ? JSON.parse(shareholdersInfo)
            : shareholdersInfo

          // 🆕 读取控股股东和实际控制人的标记
          controllingShareholderIndex.value = shareholders.value.findIndex(
            (s: any) => s.is_controlling === true
          )
          actualControllerIndex.value = shareholders.value.findIndex(
            (s: any) => s.is_actual_controller === true
          )
        } else {
          shareholders.value = []
          controllingShareholderIndex.value = -1
          actualControllerIndex.value = -1
        }
      } catch (err) {
        console.error('解析股东信息失败:', err)
        shareholders.value = []
        controllingShareholderIndex.value = -1
        actualControllerIndex.value = -1
      }
    }
  },
  { immediate: true, deep: true }
)

// 显示添加股东对话框
const showAddShareholderDialog = () => {
  editingIndex.value = -1
  shareholderForm.value = {
    name: '',
    type: '',
    ratio: ''
  }
  shareholderDialogVisible.value = true
}

// 编辑股东
const handleEditShareholder = (index: number) => {
  editingIndex.value = index
  const shareholder = shareholders.value[index]
  shareholderForm.value = {
    name: shareholder.name,
    type: shareholder.type,
    ratio: shareholder.ratio
  }
  shareholderDialogVisible.value = true
}

// 删除股东
const handleDeleteShareholder = async (index: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此股东吗？',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 如果删除的是已标记的股东，清除标记
    if (index === controllingShareholderIndex.value) {
      controllingShareholderIndex.value = -1
    }
    if (index === actualControllerIndex.value) {
      actualControllerIndex.value = -1
    }

    shareholders.value.splice(index, 1)

    // 更新索引（如果删除的股东在已标记股东之前）
    if (index < controllingShareholderIndex.value) {
      controllingShareholderIndex.value--
    }
    if (index < actualControllerIndex.value) {
      actualControllerIndex.value--
    }

    success('删除成功', '股东已删除，请点击保存按钮保存更改')
  } catch {
    // 用户取消
  }
}

// 🆕 处理控股股东标记变更
const handleControllingShareholderChange = () => {
  // 清除所有股东的控股标记
  shareholders.value.forEach((s: any) => {
    s.is_controlling = false
  })
  // 设置新的控股股东标记
  if (controllingShareholderIndex.value !== -1) {
    shareholders.value[controllingShareholderIndex.value].is_controlling = true
  }
}

// 🆕 处理实际控制人标记变更
const handleActualControllerChange = () => {
  // 清除所有股东的实际控制人标记
  shareholders.value.forEach((s: any) => {
    s.is_actual_controller = false
  })
  // 设置新的实际控制人标记
  if (actualControllerIndex.value !== -1) {
    shareholders.value[actualControllerIndex.value].is_actual_controller = true
  }
}

// 确认添加/编辑股东
const handleConfirmShareholder = async () => {
  if (!shareholderFormRef.value) return

  await shareholderFormRef.value.validate((valid) => {
    if (!valid) return

    if (editingIndex.value === -1) {
      // 添加新股东（带标记字段）
      shareholders.value.push({
        ...shareholderForm.value,
        is_controlling: false,       // 🆕 默认不是控股股东
        is_actual_controller: false  // 🆕 默认不是实际控制人
      })
      success('添加成功', '股东已添加，请点击保存按钮保存更改')
    } else {
      // 更新股东（保留原有标记）
      const existingShareholder = shareholders.value[editingIndex.value]
      shareholders.value[editingIndex.value] = {
        ...shareholderForm.value,
        is_controlling: existingShareholder.is_controlling || false,
        is_actual_controller: existingShareholder.is_actual_controller || false
      }
      success('编辑成功', '股东信息已更新，请点击保存按钮保存更改')
    }

    shareholderDialogVisible.value = false
  })
}

// 加载财务资质文件
const loadQualifications = async () => {
  try {
    loading.value = true
    const response = await companyApi.getCompanyQualifications(props.companyId)
    if (response.success) {
      qualificationFiles.value = response.data || {}
    }
  } catch (err) {
    console.error('加载资质文件失败:', err)
  } finally {
    loading.value = false
  }
}

// 上传资质文件
const handleUploadFile = async (qualKey: string, file: File) => {
  try {
    // 如果是多文件资质，需要询问版本信息（年份）
    const qualification = financialQualifications.value.find(q => q.key === qualKey)
    let fileVersion = null

    if (qualification?.allowMultiple) {
      fileVersion = prompt(`请输入 "${file.name}" 的年份:\n例如：2023、2024`)
      if (fileVersion === null) {
        // 用户取消
        return
      }
      if (!fileVersion.trim()) {
        error('上传失败', '年份不能为空')
        return
      }
    }

    // 构建FormData - 匹配后端API格式
    const formData = new FormData()
    formData.append(`qualifications[${qualKey}]`, file)
    formData.append('qualification_names', JSON.stringify({ [qualKey]: qualification?.name || qualKey }))

    if (fileVersion) {
      formData.append('file_versions', JSON.stringify({ [qualKey]: fileVersion.trim() }))
    }

    // 使用fetch直接上传，因为companyApi.uploadQualification的参数不匹配
    const response = await fetch(`/api/companies/${props.companyId}/qualifications/upload`, {
      method: 'POST',
      body: formData,
      credentials: 'include', // 包含cookies进行认证
      headers: {
        // 注意：不要设置 Content-Type，让浏览器自动设置multipart/form-data边界
      }
    })

    // 检查响应状态
    if (!response.ok) {
      // 尝试解析错误信息
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json()
        throw new Error(errorData.error || `服务器错误: ${response.status}`)
      } else {
        // 如果不是JSON，可能是HTML错误页面
        throw new Error(`上传失败: 服务器返回错误 ${response.status}`)
      }
    }

    const result = await response.json()

    if (result.success) {
      success('上传成功', `${qualification?.name || '资质文件'}上传成功`)
      await loadQualifications()
      emit('update')
    } else {
      throw new Error(result.error || '上传失败')
    }
  } catch (err) {
    console.error('上传资质文件失败:', err)
    error('上传失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 下载资质文件
const handleDownloadFile = async (qualKey: string, qualId?: number) => {
  try {
    let url: string
    if (qualId) {
      // 通过ID下载（多文件资质）
      url = `/api/qualifications/${qualId}/download`
    } else {
      // 通过key下载（单文件资质）
      url = `/api/companies/${props.companyId}/qualifications/${qualKey}/download`
    }
    window.open(url, '_blank')
  } catch (err) {
    console.error('下载资质文件失败:', err)
    error('下载失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 删除资质文件
const handleDeleteFile = async (qualKey: string, qualId?: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此资质文件吗？',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (qualId) {
      // 通过ID删除（多文件资质）
      await companyApi.deleteQualification(qualId)
    } else {
      // 通过key删除（单文件资质）
      const response = await fetch(`/api/companies/${props.companyId}/qualifications/${qualKey}`, {
        method: 'DELETE',
        credentials: 'include' // 包含cookies进行认证
      })
      if (!response.ok) throw new Error('删除失败')
    }

    success('删除成功', '资质文件已删除')
    await loadQualifications()
    emit('update')
  } catch (err) {
    console.error('删除资质文件失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 保存所有财务信息
const handleSaveAll = async () => {
  saving.value = true
  try {
    const response = await companyApi.updateCompany(props.companyId, {
      // 银行信息
      bank_name: bankForm.value.bank_name,
      bank_account: bankForm.value.bank_account,

      // 股权结构
      actual_controller: equityForm.value.actual_controller,
      controlling_shareholder: equityForm.value.controlling_shareholder,
      shareholders_info: JSON.stringify(shareholders.value),

      // 管理关系
      managing_unit_name: managementForm.value.managing_unit_name,
      managed_unit_name: managementForm.value.managed_unit_name
    })

    if (response.success) {
      success('保存成功', '财务信息已更新')
      emit('update')
    }
  } catch (err) {
    console.error('保存财务信息失败:', err)
    error('保存失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    saving.value = false
  }
}

// 组件挂载时加载资质文件
onMounted(() => {
  loadQualifications()
})
</script>

<style scoped lang="scss">
.financial-tab {
  .bank-form,
  .equity-form,
  .management-form {
    // 移除 max-width 限制，让表单占满整个容器宽度
  }

  .mt-4 {
    margin-top: 20px;
  }

  .shareholders-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #e4e7ed;

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h6 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }
    }
  }

  .save-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 2px solid #e4e7ed;
    text-align: center;
  }
}
</style>
