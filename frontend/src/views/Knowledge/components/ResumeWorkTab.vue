<template>
  <div class="resume-work-tab">
    <el-card>
      <template #header>
        <span>工作信息</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当前职位" prop="current_position">
              <el-input v-model="formData.current_position" placeholder="如：项目经理" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="professional_title">
              <el-input v-model="formData.professional_title" placeholder="如：高级工程师" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作年限" prop="work_years">
              <el-input-number
                v-model="formData.work_years"
                :min="0"
                :max="50"
                placeholder="年"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前单位" prop="current_company">
              <el-input v-model="formData.current_company" placeholder="当前工作单位" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所在部门" prop="department">
              <el-input v-model="formData.department" placeholder="部门名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作地点" prop="work_location">
              <el-input v-model="formData.work_location" placeholder="工作城市" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="技能特长" prop="skills">
          <el-input
            v-model="formData.skills"
            type="textarea"
            :rows="3"
            placeholder="请输入技能特长，多个技能用逗号分隔，如：项目管理,需求分析,Java开发"
          />
        </el-form-item>

        <el-form-item label="证书列表" prop="certificates">
          <el-input
            v-model="formData.certificates"
            type="textarea"
            :rows="2"
            placeholder="请输入证书名称，多个证书用逗号分隔，如：PMP,软考高级"
          />
        </el-form-item>

        <el-form-item label="获奖情况" prop="awards">
          <el-input
            v-model="formData.awards"
            type="textarea"
            :rows="2"
            placeholder="请输入获奖情况"
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
  current_position: '',
  professional_title: '',
  work_years: undefined as number | undefined,
  current_company: '',
  department: '',
  work_location: '',
  skills: '',
  certificates: '',
  awards: ''
})

// 监听 resumeData 变化
watch(
  () => props.resumeData,
  (newData) => {
    if (newData) {
      formData.value = {
        current_position: newData.current_position || '',
        professional_title: newData.professional_title || '',
        work_years: newData.work_years,
        current_company: newData.current_company || '',
        department: newData.department || '',
        work_location: newData.work_location || '',
        skills: newData.skills || '',
        certificates: newData.certificates || '',
        awards: newData.awards || ''
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
      success('保存成功', '工作信息已更新')
      emit('update')
    } else {
      error('保存失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('保存工作信息失败:', err)
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
.resume-work-tab {
  // 样式继承自父组件
}
</style>
