<template>
  <div class="case-basic-info-tab">
    <el-card>
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
            <el-form-item label="所属行业" prop="industry">
              <el-select v-model="formData.industry" placeholder="请选择行业" style="width: 100%">
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
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同类型" prop="contract_type">
              <el-radio-group v-model="formData.contract_type">
                <el-radio label="合同">合同</el-radio>
                <el-radio label="订单">订单</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="案例状态" prop="case_status">
              <el-radio-group v-model="formData.case_status">
                <el-radio label="success">成功</el-radio>
                <el-radio label="in_progress">进行中</el-radio>
                <el-radio label="pending_acceptance">待验收</el-radio>
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
          <el-col :span="12">
            <el-form-item label="最终客户" prop="final_customer_name">
              <el-input
                v-model="formData.final_customer_name"
                placeholder="订单类型时填写最终客户"
                :disabled="formData.contract_type !== '订单'"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
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

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import type { FormInstance, FormRules } from 'element-plus'

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
const formRef = ref<FormInstance>()
const saving = ref(false)
const formData = ref({
  case_title: '',
  case_number: '',
  customer_name: '',
  industry: '',
  contract_type: '合同' as '订单' | '合同',
  final_customer_name: '',
  contract_amount: '',
  contract_start_date: '',
  contract_end_date: '',
  case_status: 'success' as 'success' | 'in_progress' | 'pending_acceptance'
})

const formRules: FormRules = {
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

// 监听 caseData 变化，同步到 formData
watch(
  () => props.caseData,
  (newData) => {
    if (newData) {
      formData.value = {
        case_title: newData.case_title || '',
        case_number: newData.case_number || '',
        customer_name: newData.customer_name || '',
        industry: newData.industry || '',
        contract_type: newData.contract_type || '合同',
        final_customer_name: newData.final_customer_name || '',
        contract_amount: newData.contract_amount || '',
        contract_start_date: newData.contract_start_date || '',
        contract_end_date: newData.contract_end_date || '',
        case_status: newData.case_status || 'success'
      }
    }
  },
  { immediate: true, deep: true }
)

// 保存
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const response = await knowledgeApi.updateCase(props.caseId, formData.value)
      if (response.success) {
        success('保存成功', '案例基本信息已更新')
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

// 重置
const handleReset = () => {
  formRef.value?.resetFields()
}

// 案例状态类型和标签
const getCaseStatusType = (status: string) => {
  switch (status) {
    case 'success': return 'success'
    case 'in_progress': return 'warning'
    case 'pending_acceptance': return 'info'
    default: return 'info'
  }
}

const getCaseStatusLabel = (status: string) => {
  switch (status) {
    case 'success': return '成功'
    case 'in_progress': return '进行中'
    case 'pending_acceptance': return '待验收'
    default: return status
  }
}
</script>

<style scoped lang="scss">
.case-basic-info-tab {
  // 样式继承自父组件
}
</style>
