/**
 * Composables统一导出
 *
 * 提供所有可复用组合式函数的统一访问入口
 */

// SSE流式处理
export { useSSE, useSSEProgress } from './useSSE'
export type { SSEHandlers, SSEOptions, UseSSEReturn } from './useSSE'

// 通知系统
export { useNotification, notification } from './useNotification'
export type {
  NotificationType,
  NotificationOptions,
  ConfirmOptions,
  UseNotificationReturn
} from './useNotification'

// 文件上传
export { useFileUpload, useBatchFileUpload } from './useFileUpload'
export type {
  FileValidationRules,
  UploadOptions,
  FileUploadState,
  UseFileUploadReturn
} from './useFileUpload'

// 表单处理
export { useForm, useSearchForm } from './useForm'
export type { UseFormOptions, UseFormReturn } from './useForm'

// 异步数据加载
export { useAsync, useAsyncList, usePolling } from './useAsync'
export type { UseAsyncOptions, UseAsyncReturn } from './useAsync'

// 项目文档管理
export { useProjectDocuments } from './useProjectDocuments'
export type { ProjectDocuments, ProjectChangeCallbacks } from './useProjectDocuments'

// 项目创建
export { useProjectCreation } from './useProjectCreation'
export type { ProjectCreationForm, UseProjectCreationOptions } from './useProjectCreation'

// HITL集成
export { useHitlIntegration } from './useHitlIntegration'
export type { HitlFileInfo, HitlFileType, UseHitlIntegrationOptions } from './useHitlIntegration'

// 历史文件管理
export { useHistoryFiles } from './useHistoryFiles'
export type { HistoryFile, UseHistoryFilesOptions } from './useHistoryFiles'
