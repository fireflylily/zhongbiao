<template>
  <div class="case-contract-info-tab">
    <el-card>
      <template #header>
        <span>合同信息</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        label-width="140px"
      >
        <el-divider content-position="left">甲方（客户）信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="甲方名称" prop="party_a_name">
              <el-input v-model="formData.party_a_name" placeholder="甲方客户名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="甲方地址" prop="party_a_address">
              <el-input v-model="formData.party_a_address" placeholder="甲方详细地址" />
            </el-form-item>
          </el-col>
        </el-row>

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

        <el-divider content-position="left">乙方（我方）信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="乙方名称" prop="party_b_name">
              <el-input v-model="formData.party_b_name" placeholder="乙方公司名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="乙方地址" prop="party_b_address">
              <el-input v-model="formData.party_b_address" placeholder="乙方详细地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="联系人姓名" prop="party_b_contact_name">
              <el-input v-model="formData.party_b_contact_name" placeholder="联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系电话" prop="party_b_contact_phone">
              <el-input v-model="formData.party_b_contact_phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系邮箱" prop="party_b_contact_email">
              <el-input v-model="formData.party_b_contact_email" placeholder="邮箱地址" />
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
import { validatePhone, validateEmail } from '@/utils/validators'
import type { FormInstance } from 'element-plus'

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
  party_a_name: '',
  party_a_address: '',
  party_a_contact_name: '',
  party_a_contact_phone: '',
  party_a_contact_email: '',
  party_b_name: '',
  party_b_address: '',
  party_b_contact_name: '',
  party_b_contact_phone: '',
  party_b_contact_email: ''
})

// 监听 caseData 变化
watch(
  () => props.caseData,
  (newData) => {
    if (newData) {
      formData.value = {
        party_a_name: newData.party_a_name || '',
        party_a_address: newData.party_a_address || '',
        party_a_contact_name: newData.party_a_contact_name || '',
        party_a_contact_phone: newData.party_a_contact_phone || '',
        party_a_contact_email: newData.party_a_contact_email || '',
        party_b_name: newData.party_b_name || '',
        party_b_address: newData.party_b_address || '',
        party_b_contact_name: newData.party_b_contact_name || '',
        party_b_contact_phone: newData.party_b_contact_phone || '',
        party_b_contact_email: newData.party_b_contact_email || ''
      }
    }
  },
  { immediate: true, deep: true }
)

// 保存
const handleSave = async () => {
  if (!formRef.value) return

  saving.value = true
  try {
    const response = await knowledgeApi.updateCase(props.caseId, formData.value)
    if (response.success) {
      success('保存成功', '合同信息已更新')
      emit('update')
    } else {
      error('保存失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('保存合同信息失败:', err)
    error('保存失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    saving.value = false
  }
}

// 重置
const handleReset = () => {
  formRef.value?.resetFields()
}
</script>

<style scoped lang="scss">
.case-contract-info-tab {
  // 样式继承自父组件
}
</style>
