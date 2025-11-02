/**
 * 全局设置状态管理
 *
 * 管理应用的全局配置和用户偏好设置
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { SettingsState } from '@/types'

/**
 * 设置Store
 */
export const useSettingsStore = defineStore('settings', () => {
  // ==================== State ====================

  const theme = ref<'light' | 'dark'>('light')
  const language = ref<'zh-CN' | 'en-US'>('zh-CN')
  const autoSave = ref(true)
  const showHelpTooltips = ref(true)
  const compactMode = ref(false)

  // 布局配置
  const showSidebar = ref(true)
  const showBreadcrumb = ref(true)
  const showTabs = ref(false)
  const showFooter = ref(true)
  const fixedHeader = ref(true)
  const pageTransition = ref<'fade' | 'slide' | 'zoom'>('fade')

  // ==================== Getters ====================

  const isDarkMode = computed(() => theme.value === 'dark')

  const isLightMode = computed(() => theme.value === 'light')

  const isChineseLanguage = computed(() => language.value === 'zh-CN')

  const isEnglishLanguage = computed(() => language.value === 'en-US')

  // ==================== Actions ====================

  /**
   * 设置主题
   */
  function setTheme(newTheme: 'light' | 'dark'): void {
    theme.value = newTheme
    applyTheme()
    saveToStorage()
  }

  /**
   * 切换主题
   */
  function toggleTheme(): void {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  /**
   * 应用主题到DOM
   */
  function applyTheme(): void {
    const htmlElement = document.documentElement

    if (theme.value === 'dark') {
      htmlElement.classList.add('dark')
    } else {
      htmlElement.classList.remove('dark')
    }

    // 设置data属性（用于CSS变量）
    htmlElement.setAttribute('data-theme', theme.value)
  }

  /**
   * 设置语言
   */
  function setLanguage(newLanguage: 'zh-CN' | 'en-US'): void {
    language.value = newLanguage
    applyLanguage()
    saveToStorage()
  }

  /**
   * 应用语言设置
   */
  function applyLanguage(): void {
    const htmlElement = document.documentElement
    htmlElement.setAttribute('lang', language.value)
  }

  /**
   * 设置自动保存
   */
  function setAutoSave(enabled: boolean): void {
    autoSave.value = enabled
    saveToStorage()
  }

  /**
   * 切换自动保存
   */
  function toggleAutoSave(): void {
    setAutoSave(!autoSave.value)
  }

  /**
   * 设置帮助提示
   */
  function setShowHelpTooltips(enabled: boolean): void {
    showHelpTooltips.value = enabled
    saveToStorage()
  }

  /**
   * 切换帮助提示
   */
  function toggleHelpTooltips(): void {
    setShowHelpTooltips(!showHelpTooltips.value)
  }

  /**
   * 设置紧凑模式
   */
  function setCompactMode(enabled: boolean): void {
    compactMode.value = enabled
    applyCompactMode()
    saveToStorage()
  }

  /**
   * 切换紧凑模式
   */
  function toggleCompactMode(): void {
    setCompactMode(!compactMode.value)
  }

  /**
   * 应用紧凑模式
   */
  function applyCompactMode(): void {
    const htmlElement = document.documentElement

    if (compactMode.value) {
      htmlElement.classList.add('compact-mode')
    } else {
      htmlElement.classList.remove('compact-mode')
    }
  }

  /**
   * 设置侧边栏显示
   */
  function setShowSidebar(show: boolean): void {
    showSidebar.value = show
    saveToStorage()
  }

  /**
   * 切换侧边栏
   */
  function toggleSidebar(): void {
    setShowSidebar(!showSidebar.value)
  }

  /**
   * 设置面包屑显示
   */
  function setShowBreadcrumb(show: boolean): void {
    showBreadcrumb.value = show
    saveToStorage()
  }

  /**
   * 设置标签页显示
   */
  function setShowTabs(show: boolean): void {
    showTabs.value = show
    saveToStorage()
  }

  /**
   * 设置页脚显示
   */
  function setShowFooter(show: boolean): void {
    showFooter.value = show
    saveToStorage()
  }

  /**
   * 设置固定头部
   */
  function setFixedHeader(fixed: boolean): void {
    fixedHeader.value = fixed
    saveToStorage()
  }

  /**
   * 设置页面切换动画
   */
  function setPageTransition(transition: 'fade' | 'slide' | 'zoom'): void {
    pageTransition.value = transition
    saveToStorage()
  }

  /**
   * 批量更新设置
   */
  function updateSettings(settings: Partial<SettingsState>): void {
    if (settings.theme !== undefined) {
      setTheme(settings.theme)
    }

    if (settings.language !== undefined) {
      setLanguage(settings.language)
    }

    if (settings.autoSave !== undefined) {
      setAutoSave(settings.autoSave)
    }

    if (settings.showHelpTooltips !== undefined) {
      setShowHelpTooltips(settings.showHelpTooltips)
    }

    if (settings.compactMode !== undefined) {
      setCompactMode(settings.compactMode)
    }
  }

  /**
   * 从localStorage恢复状态
   */
  function restoreFromStorage(): void {
    try {
      const savedSettings = localStorage.getItem('app_settings')

      if (savedSettings) {
        const settings = JSON.parse(savedSettings) as SettingsState

        theme.value = settings.theme || 'light'
        language.value = settings.language || 'zh-CN'
        autoSave.value = settings.autoSave !== undefined ? settings.autoSave : true
        showHelpTooltips.value =
          settings.showHelpTooltips !== undefined ? settings.showHelpTooltips : true
        compactMode.value = settings.compactMode || false

        // 布局配置
        showSidebar.value = settings.showSidebar !== undefined ? settings.showSidebar : true
        showBreadcrumb.value =
          settings.showBreadcrumb !== undefined ? settings.showBreadcrumb : true
        showTabs.value = settings.showTabs || false
        showFooter.value = settings.showFooter !== undefined ? settings.showFooter : true
        fixedHeader.value = settings.fixedHeader !== undefined ? settings.fixedHeader : true
        pageTransition.value = settings.pageTransition || 'fade'

        // 应用设置到DOM
        applyTheme()
        applyLanguage()
        applyCompactMode()
      }
    } catch (err) {
      console.error('恢复设置失败:', err)
    }
  }

  /**
   * 保存到localStorage
   */
  function saveToStorage(): void {
    try {
      const settings: SettingsState = {
        theme: theme.value,
        language: language.value,
        autoSave: autoSave.value,
        showHelpTooltips: showHelpTooltips.value,
        compactMode: compactMode.value,
        // 布局配置
        showSidebar: showSidebar.value,
        showBreadcrumb: showBreadcrumb.value,
        showTabs: showTabs.value,
        showFooter: showFooter.value,
        fixedHeader: fixedHeader.value,
        pageTransition: pageTransition.value
      }

      localStorage.setItem('app_settings', JSON.stringify(settings))
    } catch (err) {
      console.error('保存设置失败:', err)
    }
  }

  /**
   * 重置为默认设置
   */
  function resetToDefaults(): void {
    theme.value = 'light'
    language.value = 'zh-CN'
    autoSave.value = true
    showHelpTooltips.value = true
    compactMode.value = false

    // 布局配置重置
    showSidebar.value = true
    showBreadcrumb.value = true
    showTabs.value = false
    showFooter.value = true
    fixedHeader.value = true
    pageTransition.value = 'fade'

    applyTheme()
    applyLanguage()
    applyCompactMode()
    saveToStorage()
  }

  /**
   * 重置状态
   */
  function $reset(): void {
    resetToDefaults()
  }

  // ==================== Watchers ====================

  // 监听主题变化，自动应用
  watch(theme, () => {
    applyTheme()
  })

  // 监听语言变化，自动应用
  watch(language, () => {
    applyLanguage()
  })

  // 监听紧凑模式变化，自动应用
  watch(compactMode, () => {
    applyCompactMode()
  })

  // ==================== Return ====================

  return {
    // State
    theme,
    language,
    autoSave,
    showHelpTooltips,
    compactMode,
    showSidebar,
    showBreadcrumb,
    showTabs,
    showFooter,
    fixedHeader,
    pageTransition,

    // Getters
    isDarkMode,
    isLightMode,
    isChineseLanguage,
    isEnglishLanguage,

    // Actions
    setTheme,
    toggleTheme,
    setLanguage,
    setAutoSave,
    toggleAutoSave,
    setShowHelpTooltips,
    toggleHelpTooltips,
    setCompactMode,
    toggleCompactMode,
    setShowSidebar,
    toggleSidebar,
    setShowBreadcrumb,
    setShowTabs,
    setShowFooter,
    setFixedHeader,
    setPageTransition,
    updateSettings,
    restoreFromStorage,
    saveToStorage,
    resetToDefaults,
    $reset
  }
})
