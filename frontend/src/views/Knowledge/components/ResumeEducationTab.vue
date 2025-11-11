<template>
  <div class="resume-education-tab">
    <el-card>
      <template #header>
        <span>教育信息</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历" prop="education_level">
              <el-select v-model="formData.education_level" placeholder="请选择学历" style="width: 100%">
                <el-option label="博士" value="博士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="本科" value="本科" />
                <el-option label="大专" value="大专" />
                <el-option label="高中" value="高中" />
                <el-option label="中专" value="中专" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学位" prop="degree">
              <el-select v-model="formData.degree" placeholder="请选择学位" style="width: 100%">
                <el-option label="博士学位" value="博士" />
                <el-option label="硕士学位" value="硕士" />
                <el-option label="学士学位" value="学士" />
                <el-option label="无学位" value="无" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="毕业院校" prop="university">
              <el-input v-model="formData.university" placeholder="请输入毕业院校" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="formData.major" placeholder="请输入专业" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="毕业时间" prop="graduation_date">
              <el-date-picker
                v-model="formData.graduation_date"
                type="date"
                placeholder="选择毕业日期"
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
import type { FormInstance } from 'element-plus'

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
  education_level: '',
  degree: '',
  university: '',
  major: '',
  graduation_date: ''
})

// 监听 resumeData 变化
watch(
  () => props.resumeData,
  (newData) => {
    if (newData) {
      formData.value = {
        education_level: newData.education_level || '',
        degree: newData.degree || '',
        university: newData.university || '',
        major: newData.major || '',
        graduation_date: newData.graduation_date || ''
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
    const response = await knowledgeApi.updateResume(props.resumeId, formData.value)
    if (response.success) {
      success('保存成功', '教育信息已更新')
      emit('update')
    } else {
      error('保存失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('保存教育信息失败:', err)
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
.resume-education-tab {
  // 样式继承自父组件
}
</style>
