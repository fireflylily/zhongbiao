/**
 * Pinia Store状态类型定义
 */

import type { User, Company, Project, AIModel, FileInfo } from './models'

// ============================================
// 用户Store状态
// ============================================

export interface UserState {
  currentUser: User | null
  token: string | null
  isLoggedIn: boolean
  permissions: string[]
}

// ============================================
// 公司Store状态
// ============================================

export interface CompanyState {
  currentCompany: Company | null
  companies: Company[]
  loading: boolean
  error: string | null
}

// ============================================
// 项目Store状态
// ============================================

export interface ProjectState {
  currentProject: Project | null
  projects: Project[]
  loading: boolean
  error: string | null
  pagination: {
    page: number
    pageSize: number
    total: number
  }
}

// ============================================
// AI模型Store状态
// ============================================

export interface AIModelState {
  availableModels: AIModel[]
  selectedModel: string | null
  loading: boolean
  error: string | null
}

// ============================================
// 文件Store状态
// ============================================

export interface FileState {
  files: {
    business: FileInfo | null
    technical: FileInfo | null
    pointToPoint: FileInfo | null
    tender: FileInfo | null
    [key: string]: FileInfo | null
  }
}

// ============================================
// 通知Store状态
// ============================================

export interface NotificationItem {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  timestamp: Date
}

export interface NotificationState {
  notifications: NotificationItem[]
  maxNotifications: number
}

// ============================================
// HITL任务Store状态
// ============================================

export interface HITLTaskState {
  currentTaskId: string | null
  taskStatus: 'step1' | 'step2' | 'step3' | 'completed' | null
  currentStep: number
  loading: boolean
  error: string | null
}

// ============================================
// 全局设置Store状态
// ============================================

export interface SettingsState {
  theme: 'light' | 'dark'
  language: 'zh-CN' | 'en-US'
  autoSave: boolean
  showHelpTooltips: boolean
  compactMode: boolean
  // 布局配置
  showSidebar?: boolean
  showBreadcrumb?: boolean
  showTabs?: boolean
  showFooter?: boolean
  fixedHeader?: boolean
  pageTransition?: 'fade' | 'slide' | 'zoom'
}
