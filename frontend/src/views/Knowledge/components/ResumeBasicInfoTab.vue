<template>
  <div class="resume-basic-info-tab">
    <el-card>
      <template #header>
        <span>基本信息</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formData.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="formData.birth_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="民族" prop="nationality">
              <el-input v-model="formData.nationality" placeholder="如：汉族" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="籍贯" prop="native_place">
              <el-input v-model="formData.native_place" placeholder="如：北京市" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="政治面貌" prop="political_status">
              <el-select v-model="formData.political_status" placeholder="请选择" style="width: 100%">
                <el-option label="中共党员" value="中共党员" />
                <el-option label="共青团员" value="共青团员" />
                <el-option label="民主党派" value="民主党派" />
                <el-option label="群众" value="群众" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_number">
              <el-input v-model="formData.id_number" placeholder="18位身份证号" maxlength="18" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="formData.phone" placeholder="手机号码" maxlength="11" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="邮箱地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系地址" prop="address">
              <el-input v-model="formData.address" placeholder="详细地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="个人简介" prop="introduction">
          <el-input
            v-model="formData.introduction"
            type="textarea"
            :rows="4"
            placeholder="请简要介绍个人经历、专长、优势等"
          />
        </el-form-item>

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
import { validatePhone, validateEmail, validateIdCard } from '@/utils/validators'
import type { FormInstance, FormRules } from 'element-plus'

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
const formRef = ref<FormInstance>()
const saving = ref(false)
const formData = ref({
  name: '',
  gender: '',
  birth_date: '',
  nationality: '',
  native_place: '',
  political_status: '',
  id_number: '',
  phone: '',
  email: '',
  address: '',
  introduction: ''
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ],
  id_number: [
    { validator: validateIdCard, trigger: 'blur' }
  ]
}

// 监听 resumeData 变化
watch(
  () => props.resumeData,
  (newData) => {
    if (newData) {
      formData.value = {
        name: newData.name || '',
        gender: newData.gender || '',
        birth_date: newData.birth_date || '',
        nationality: newData.nationality || '',
        native_place: newData.native_place || '',
        political_status: newData.political_status || '',
        id_number: newData.id_number || '',
        phone: newData.phone || '',
        email: newData.email || '',
        address: newData.address || '',
        introduction: newData.introduction || ''
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
      const response = await knowledgeApi.updateResume(props.resumeId, formData.value)
      if (response.success) {
        success('保存成功', '基本信息已更新')
        emit('update')
      } else {
        error('保存失败', response.error || '未知错误')
      }
    } catch (err) {
      console.error('保存基本信息失败:', err)
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
</script>

<style scoped lang="scss">
.resume-basic-info-tab {
  // 样式继承自父组件
}
</style>
