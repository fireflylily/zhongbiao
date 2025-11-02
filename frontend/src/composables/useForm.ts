/**
 * 表单处理Composable
 *
 * 封装表单验证、提交、重置等通用逻辑
 */

import { ref, reactive, computed, type Ref, type UnwrapRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useNotification } from './useNotification'

/**
 * 表单选项
 */
export interface UseFormOptions<T> {
  initialValues: T
  rules?: FormRules
  onSubmit: (values: T) => Promise<any>
  onSuccess?: (response: any) => void
  onError?: (error: Error) => void
  resetAfterSubmit?: boolean
}

/**
 * useForm返回值类型
 */
export interface UseFormReturn<T> {
  // Form实例
  formRef: Ref<FormInstance | null>

  // State
  formData: UnwrapRef<T>
  submitting: Ref<boolean>
  errors: Ref<Record<string, string>>

  // Computed
  isDirty: Ref<boolean>
  isValid: Ref<boolean>

  // Methods
  validate: () => Promise<boolean>
  validateField: (field: keyof T) => Promise<boolean>
  submit: () => Promise<any>
  reset: () => void
  setFieldValue: (field: keyof T, value: any) => void
  setFieldError: (field: keyof T, error: string) => void
  clearErrors: () => void
}

/**
 * 表单处理Hook
 *
 * @param options - 表单选项
 * @returns 表单控制对象
 */
export function useForm<T extends Record<string, any>>(
  options: UseFormOptions<T>
): UseFormReturn<T> {
  const {
    initialValues,
    rules,
    onSubmit,
    onSuccess,
    onError,
    resetAfterSubmit = false
  } = options

  const { success, error: showError } = useNotification()

  // ==================== State ====================

  const formRef = ref<FormInstance | null>(null)
  const formData = reactive({ ...initialValues }) as UnwrapRef<T>
  const submitting = ref(false)
  const errors = ref<Record<string, string>>({})
  const initialValuesSnapshot = JSON.stringify(initialValues)

  // ==================== Computed ====================

  const isDirty = computed(() => {
    return JSON.stringify(formData) !== initialValuesSnapshot
  })

  const isValid = computed(() => {
    return Object.keys(errors.value).length === 0
  })

  // ==================== Methods ====================

  /**
   * 验证整个表单
   */
  async function validate(): Promise<boolean> {
    if (!formRef.value) return false

    try {
      await formRef.value.validate()
      return true
    } catch (err) {
      return false
    }
  }

  /**
   * 验证单个字段
   */
  async function validateField(field: keyof T): Promise<boolean> {
    if (!formRef.value) return false

    try {
      await formRef.value.validateField(field as string)
      return true
    } catch (err) {
      return false
    }
  }

  /**
   * 提交表单
   */
  async function submit(): Promise<any> {
    // 验证表单
    const valid = await validate()
    if (!valid) {
      showError('请检查表单输入')
      return null
    }

    submitting.value = true
    errors.value = {}

    try {
      const response = await onSubmit(formData as T)

      // 调用成功回调
      onSuccess?.(response)

      // 显示成功消息
      success('提交成功')

      // 重置表单（如果配置了）
      if (resetAfterSubmit) {
        reset()
      }

      return response
    } catch (err: any) {
      // 处理服务器返回的字段错误
      if (err.details && typeof err.details === 'object') {
        errors.value = err.details
      }

      // 显示错误消息
      showError(err.message || '提交失败')

      // 调用错误回调
      onError?.(err)

      throw err
    } finally {
      submitting.value = false
    }
  }

  /**
   * 重置表单
   */
  function reset(): void {
    if (formRef.value) {
      formRef.value.resetFields()
    }

    // 重置为初始值
    Object.assign(formData, initialValues)
    errors.value = {}
  }

  /**
   * 设置字段值
   */
  function setFieldValue(field: keyof T, value: any): void {
    ;(formData as any)[field] = value

    // 清除该字段的错误
    if (errors.value[field as string]) {
      delete errors.value[field as string]
    }
  }

  /**
   * 设置字段错误
   */
  function setFieldError(field: keyof T, error: string): void {
    errors.value[field as string] = error
  }

  /**
   * 清除所有错误
   */
  function clearErrors(): void {
    errors.value = {}
  }

  // ==================== Return ====================

  return {
    formRef,
    formData,
    submitting,
    errors,
    isDirty,
    isValid,
    validate,
    validateField,
    submit,
    reset,
    setFieldValue,
    setFieldError,
    clearErrors
  }
}

/**
 * 搜索表单Hook
 *
 * 简化版的表单Hook，专门用于搜索场景
 */
export function useSearchForm<T extends Record<string, any>>(
  initialValues: T,
  onSearch: (values: T) => Promise<void>
) {
  const formData = reactive({ ...initialValues }) as UnwrapRef<T>
  const searching = ref(false)

  /**
   * 执行搜索
   */
  async function search(): Promise<void> {
    searching.value = true

    try {
      await onSearch(formData as T)
    } finally {
      searching.value = false
    }
  }

  /**
   * 重置搜索
   */
  function reset(): void {
    Object.assign(formData, initialValues)
    search() // 重置后自动搜索
  }

  /**
   * 设置字段值并搜索
   */
  function setAndSearch(field: keyof T, value: any): void {
    ;(formData as any)[field] = value
    search()
  }

  return {
    formData,
    searching,
    search,
    reset,
    setAndSearch
  }
}
