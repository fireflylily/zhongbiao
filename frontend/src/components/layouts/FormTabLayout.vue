<template>
  <div class="form-tab-layout">
    <Card :title="title">
      <el-form
        ref="formRef"
        :model="modelValue"
        :rules="rules"
        :label-width="labelWidth"
        :class="formClass"
      >
        <!-- 表单内容（必需） -->
        <slot name="form-content" />

        <!-- 保存按钮行 -->
        <el-row v-if="showSaveButton">
          <el-col :span="24">
            <el-form-item>
              <el-button
                type="primary"
                :loading="saving"
                :disabled="disabled"
                @click="handleSave"
              >
                <el-icon v-if="!saving"><Select /></el-icon>
                {{ saveButtonText }}
              </el-button>
              <el-button v-if="showCancelButton" @click="handleCancel">
                取消
              </el-button>
              <!-- 额外按钮（可选） -->
              <slot name="extra-buttons" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Card } from '@/components'
import { Select } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

/**
 * 表单 Tab 统一布局组件
 *
 * @description
 * 提供统一的表单 Tab 布局，包括：
 * - Card 容器
 * - 表单验证
 * - 保存/取消按钮
 * - 统一的表单样式
 *
 * @example
 * ```vue
 * <FormTabLayout
 *   title="基础信息"
 *   v-model="formData"
 *   :rules="formRules"
 *   :saving="saving"
 *   save-button-text="保存基础信息"
 *   @save="handleSave"
 * >
 *   <template #form-content>
 *     <el-row :gutter="20">
 *       <el-col :span="12">
 *         <el-form-item label="企业名称" prop="company_name">
 *           <el-input v-model="formData.company_name" />
 *         </el-form-item>
 *       </el-col>
 *     </el-row>
 *   </template>
 * </FormTabLayout>
 * ```
 */

interface Props {
  /** Card 标题 */
  title?: string
  /** 表单数据（支持 v-model） */
  modelValue?: Record<string, any>
  /** 表单验证规则 */
  rules?: FormRules
  /** 标签宽度 */
  labelWidth?: string | number
  /** 表单自定义类名 */
  formClass?: string
  /** 是否正在保存 */
  saving?: boolean
  /** 是否禁用保存按钮 */
  disabled?: boolean
  /** 是否显示保存按钮 */
  showSaveButton?: boolean
  /** 是否显示取消按钮 */
  showCancelButton?: boolean
  /** 保存按钮文本 */
  saveButtonText?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  modelValue: () => ({}),
  rules: () => ({}),
  labelWidth: '140px',
  formClass: '',
  saving: false,
  disabled: false,
  showSaveButton: true,
  showCancelButton: false,
  saveButtonText: '保存'
})

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'save'): void
  (e: 'cancel'): void
  (e: 'validate', valid: boolean): void
}>()

// 表单引用
const formRef = ref<FormInstance>()

// 处理保存
const handleSave = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    emit('validate', valid)
    if (valid) {
      emit('save')
    }
  } catch (error) {
    emit('validate', false)
    console.error('表单验证失败:', error)
  }
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}

// 暴露方法给父组件
defineExpose({
  /** 表单实例 */
  formRef,
  /** 验证表单 */
  validate: () => formRef.value?.validate(),
  /** 重置表单 */
  resetFields: () => formRef.value?.resetFields(),
  /** 清除验证 */
  clearValidate: () => formRef.value?.clearValidate()
})
</script>

<style scoped lang="scss">
.form-tab-layout {
  // Card 的外层容器样式由父组件决定

  :deep(.el-form) {
    // 表单项间距
    .el-form-item {
      margin-bottom: 18px;
    }

    // 最后一行（保存按钮行）
    .el-row:last-child .el-form-item {
      margin-bottom: 0;
      margin-top: 8px;
    }
  }

  // 如果父组件需要特殊的表单样式（如编辑模式），可以通过 formClass 传入
}
</style>
