/**
 * Pinia Store统一导出
 *
 * 集中管理所有Store模块的导出和初始化
 */

import { createPinia } from 'pinia'

// 导出所有Store
export { useUserStore } from './user'
export { useCompanyStore } from './company'
export { useProjectStore } from './project'
export { useAIModelStore } from './aiModel'
export { useNotificationStore } from './notification'
export { useSettingsStore } from './settings'

/**
 * 创建Pinia实例
 */
export const pinia = createPinia()

/**
 * 初始化所有Store
 *
 * 在应用启动时调用，恢复所有Store的持久化状态
 */
export function initializeStores(): void {
  // 动态导入所有Store并恢复状态
  import('./user').then(({ useUserStore }) => {
    const userStore = useUserStore()
    userStore.restoreFromStorage()
  })

  import('./company').then(({ useCompanyStore }) => {
    const companyStore = useCompanyStore()
    companyStore.restoreFromStorage()
  })

  import('./project').then(({ useProjectStore }) => {
    const projectStore = useProjectStore()
    projectStore.restoreFromStorage()
  })

  import('./aiModel').then(({ useAIModelStore }) => {
    const aiModelStore = useAIModelStore()
    aiModelStore.restoreFromStorage()
  })

  import('./settings').then(({ useSettingsStore }) => {
    const settingsStore = useSettingsStore()
    settingsStore.restoreFromStorage()
  })
}

/**
 * 重置所有Store
 *
 * 清除所有Store的状态和localStorage
 */
export function resetAllStores(): void {
  import('./user').then(({ useUserStore }) => {
    useUserStore().$reset()
  })

  import('./company').then(({ useCompanyStore }) => {
    useCompanyStore().$reset()
  })

  import('./project').then(({ useProjectStore }) => {
    useProjectStore().$reset()
  })

  import('./aiModel').then(({ useAIModelStore }) => {
    useAIModelStore().$reset()
  })

  import('./notification').then(({ useNotificationStore }) => {
    useNotificationStore().$reset()
  })

  import('./settings').then(({ useSettingsStore }) => {
    useSettingsStore().$reset()
  })
}
