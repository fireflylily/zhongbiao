/**
 * AI模型状态管理
 *
 * 管理可用的AI模型列表和当前选中的模型
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { businessApi } from '@/api'
import type { AIModel, AIModelState } from '@/types'

/**
 * AI模型Store
 */
export const useAIModelStore = defineStore('aiModel', () => {
  // ==================== State ====================

  const availableModels = ref<AIModel[]>([])
  const selectedModel = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==================== Getters ====================

  const hasModels = computed(() => availableModels.value.length > 0)

  const activeModels = computed(() => {
    return availableModels.value.filter((model) => model.status === 'available')
  })

  const activeModelsCount = computed(() => activeModels.value.length)

  const modelsOptions = computed(() => {
    return activeModels.value.map((model) => ({
      label: model.display_name,
      value: model.name
    }))
  })

  const currentModel = computed(() => {
    if (!selectedModel.value) {
      return null
    }
    return availableModels.value.find((m) => m.name === selectedModel.value) || null
  })

  const currentModelDisplayName = computed(() => {
    return currentModel.value?.display_name || ''
  })

  const hasSelectedModel = computed(() => !!selectedModel.value)

  const modelsByProvider = computed(() => {
    const grouped: Record<string, AIModel[]> = {}

    availableModels.value.forEach((model) => {
      const provider = model.provider || 'unknown'
      if (!grouped[provider]) {
        grouped[provider] = []
      }
      grouped[provider].push(model)
    })

    return grouped
  })

  // ==================== Actions ====================

  /**
   * 获取可用模型列表
   */
  async function fetchAvailableModels(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await businessApi.getAvailableModels()

      if (response.success && response.data) {
        availableModels.value = response.data

        // 如果没有选中模型且有可用模型，自动选中第一个
        if (!selectedModel.value && activeModels.value.length > 0) {
          setSelectedModel(activeModels.value[0].name)
        }

        // 如果当前选中的模型已不可用，自动切换到第一个可用模型
        if (
          selectedModel.value &&
          !activeModels.value.find((m) => m.name === selectedModel.value)
        ) {
          if (activeModels.value.length > 0) {
            setSelectedModel(activeModels.value[0].name)
          } else {
            selectedModel.value = null
          }
        }
      }
    } catch (err: any) {
      error.value = err.message || '获取模型列表失败'
      console.error('获取模型列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 设置选中的模型
   */
  function setSelectedModel(modelName: string): void {
    const model = availableModels.value.find((m) => m.name === modelName)

    if (model && model.status === 'available') {
      selectedModel.value = modelName
      saveToStorage()
    } else {
      console.warn(`模型不可用: ${modelName}`)
    }
  }

  /**
   * 测试模型连接
   */
  async function testModelConnection(modelName: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await businessApi.testModelConnection(modelName)

      if (response.success) {
        return true
      }

      error.value = response.message || '模型连接测试失败'
      return false
    } catch (err: any) {
      error.value = err.message || '模型连接测试失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取模型详情
   */
  function getModel(modelName: string): AIModel | null {
    return availableModels.value.find((m) => m.name === modelName) || null
  }

  /**
   * 检查模型是否可用
   */
  function isModelAvailable(modelName: string): boolean {
    const model = getModel(modelName)
    return model?.status === 'available'
  }

  /**
   * 获取特定提供商的模型
   */
  function getModelsByProvider(provider: string): AIModel[] {
    return availableModels.value.filter((m) => m.provider === provider)
  }

  /**
   * 从localStorage恢复状态
   */
  function restoreFromStorage(): void {
    try {
      const savedModel = localStorage.getItem('selected_ai_model')

      if (savedModel) {
        selectedModel.value = savedModel
      }
    } catch (err) {
      console.error('恢复AI模型状态失败:', err)
    }
  }

  /**
   * 保存到localStorage
   */
  function saveToStorage(): void {
    try {
      if (selectedModel.value) {
        localStorage.setItem('selected_ai_model', selectedModel.value)
      }
    } catch (err) {
      console.error('保存AI模型状态失败:', err)
    }
  }

  /**
   * 重置状态
   */
  function $reset(): void {
    availableModels.value = []
    selectedModel.value = null
    loading.value = false
    error.value = null
    localStorage.removeItem('selected_ai_model')
  }

  // ==================== Return ====================

  return {
    // State
    availableModels,
    selectedModel,
    loading,
    error,

    // Getters
    hasModels,
    activeModels,
    activeModelsCount,
    modelsOptions,
    currentModel,
    currentModelDisplayName,
    hasSelectedModel,
    modelsByProvider,

    // Actions
    fetchAvailableModels,
    setSelectedModel,
    testModelConnection,
    getModel,
    isModelAvailable,
    getModelsByProvider,
    restoreFromStorage,
    saveToStorage,
    $reset
  }
})
