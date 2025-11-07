/**
 * 通知系统Composable
 *
 * 封装Element Plus通知和Notification Store的使用
 */

import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { useNotificationStore } from '@/stores'
import type { ElMessageBoxOptions } from 'element-plus'

/**
 * 通知类型
 */
export type NotificationType = 'success' | 'warning' | 'info' | 'error'

/**
 * 通知选项
 */
export interface NotificationOptions {
  title?: string
  message: string
  type?: NotificationType
  duration?: number
  showClose?: boolean
  dangerouslyUseHTMLString?: boolean
}

/**
 * 确认框选项
 */
export interface ConfirmOptions {
  title?: string
  message: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: NotificationType
}

/**
 * useNotification返回值类型
 */
export interface UseNotificationReturn {
  // Message（轻量级提示）
  // 支持三种调用方式: fn('消息'), fn('消息', 3000), fn('标题', '消息')
  success: (titleOrMessage: string, messageOrDuration?: string | number) => void
  error: (titleOrMessage: string, messageOrDuration?: string | number) => void
  warning: (titleOrMessage: string, messageOrDuration?: string | number) => void
  info: (titleOrMessage: string, messageOrDuration?: string | number) => void

  // Notification（通知框）
  notify: (options: NotificationOptions) => void
  notifySuccess: (title: string, message: string) => void
  notifyError: (title: string, message: string) => void
  notifyWarning: (title: string, message: string) => void
  notifyInfo: (title: string, message: string) => void

  // MessageBox（确认框）
  confirm: (options: ConfirmOptions) => Promise<boolean>
  alert: (message: string, title?: string) => Promise<void>
  prompt: (message: string, title?: string) => Promise<string>
}

/**
 * 通知系统Hook
 *
 * 提供统一的通知、消息、确认框接口
 */
export function useNotification(): UseNotificationReturn {
  const notificationStore = useNotificationStore()

  // ==================== Message（轻量级提示）====================

  /**
   * 成功消息
   * 支持两种调用方式:
   * 1. success('消息') - 只显示消息
   * 2. success('消息', 3000) - 消息 + 自定义持续时间
   * 3. success('标题', '消息') - 标题和消息组合显示
   */
  function success(titleOrMessage: string, messageOrDuration?: string | number): void {
    let message: string
    let duration: number

    if (typeof messageOrDuration === 'string') {
      // 第二个参数是字符串，说明第一个是标题，第二个是消息
      message = `${titleOrMessage}: ${messageOrDuration}`
      duration = 3000
    } else {
      // 第二个参数是数字或未定义，第一个参数就是消息
      message = titleOrMessage
      duration = messageOrDuration || 3000
    }

    ElMessage.success({
      message,
      duration,
      showClose: true
    })

    // 同时添加到Store
    notificationStore.success('操作成功', message, duration)
  }

  /**
   * 错误消息
   * 支持两种调用方式:
   * 1. error('消息') - 只显示消息
   * 2. error('消息', 5000) - 消息 + 自定义持续时间
   * 3. error('标题', '消息') - 标题和消息组合显示
   */
  function error(titleOrMessage: string, messageOrDuration?: string | number): void {
    let message: string
    let duration: number

    if (typeof messageOrDuration === 'string') {
      // 第二个参数是字符串，说明第一个是标题，第二个是消息
      message = `${titleOrMessage}: ${messageOrDuration}`
      duration = 5000
    } else {
      // 第二个参数是数字或未定义，第一个参数就是消息
      message = titleOrMessage
      duration = messageOrDuration || 5000
    }

    ElMessage.error({
      message,
      duration,
      showClose: true
    })

    // 同时添加到Store
    notificationStore.error('操作失败', message, duration)
  }

  /**
   * 警告消息
   * 支持两种调用方式:
   * 1. warning('消息') - 只显示消息
   * 2. warning('消息', 3000) - 消息 + 自定义持续时间
   * 3. warning('标题', '消息') - 标题和消息组合显示
   */
  function warning(titleOrMessage: string, messageOrDuration?: string | number): void {
    let message: string
    let duration: number

    if (typeof messageOrDuration === 'string') {
      // 第二个参数是字符串，说明第一个是标题，第二个是消息
      message = `${titleOrMessage}: ${messageOrDuration}`
      duration = 3000
    } else {
      // 第二个参数是数字或未定义，第一个参数就是消息
      message = titleOrMessage
      duration = messageOrDuration || 3000
    }

    ElMessage.warning({
      message,
      duration,
      showClose: true
    })

    // 同时添加到Store
    notificationStore.warning('警告', message, duration)
  }

  /**
   * 信息消息
   * 支持两种调用方式:
   * 1. info('消息') - 只显示消息
   * 2. info('消息', 3000) - 消息 + 自定义持续时间
   * 3. info('标题', '消息') - 标题和消息组合显示
   */
  function info(titleOrMessage: string, messageOrDuration?: string | number): void {
    let message: string
    let duration: number

    if (typeof messageOrDuration === 'string') {
      // 第二个参数是字符串，说明第一个是标题，第二个是消息
      message = `${titleOrMessage}: ${messageOrDuration}`
      duration = 3000
    } else {
      // 第二个参数是数字或未定义，第一个参数就是消息
      message = titleOrMessage
      duration = messageOrDuration || 3000
    }

    ElMessage.info({
      message,
      duration,
      showClose: true
    })

    // 同时添加到Store
    notificationStore.info('提示', message, duration)
  }

  // ==================== Notification（通知框）====================

  /**
   * 通用通知
   */
  function notify(options: NotificationOptions): void {
    ElNotification({
      title: options.title || '通知',
      message: options.message,
      type: options.type || 'info',
      duration: options.duration || 4500,
      showClose: options.showClose !== false,
      dangerouslyUseHTMLString: options.dangerouslyUseHTMLString || false
    })

    // 同时添加到Store
    const type = options.type || 'info'
    notificationStore.addNotification(
      type,
      options.title || '通知',
      options.message,
      options.duration
    )
  }

  /**
   * 成功通知
   */
  function notifySuccess(title: string, message: string): void {
    notify({
      title,
      message,
      type: 'success',
      duration: 4500
    })
  }

  /**
   * 错误通知
   */
  function notifyError(title: string, message: string): void {
    notify({
      title,
      message,
      type: 'error',
      duration: 6000 // 错误通知显示更久
    })
  }

  /**
   * 警告通知
   */
  function notifyWarning(title: string, message: string): void {
    notify({
      title,
      message,
      type: 'warning',
      duration: 4500
    })
  }

  /**
   * 信息通知
   */
  function notifyInfo(title: string, message: string): void {
    notify({
      title,
      message,
      type: 'info',
      duration: 4500
    })
  }

  // ==================== MessageBox（确认框）====================

  /**
   * 确认框
   */
  async function confirm(options: ConfirmOptions): Promise<boolean> {
    try {
      await ElMessageBox.confirm(options.message, options.title || '确认', {
        confirmButtonText: options.confirmButtonText || '确定',
        cancelButtonText: options.cancelButtonText || '取消',
        type: options.type || 'warning',
        distinguishCancelAndClose: true
      })
      return true
    } catch (action) {
      // 用户点击取消或关闭
      return false
    }
  }

  /**
   * 警告框
   */
  async function alert(message: string, title: string = '提示'): Promise<void> {
    await ElMessageBox.alert(message, title, {
      confirmButtonText: '确定',
      type: 'info'
    })
  }

  /**
   * 输入框
   */
  async function prompt(message: string, title: string = '输入'): Promise<string> {
    try {
      const { value } = await ElMessageBox.prompt(message, title, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '输入不能为空'
      })
      return value || ''
    } catch {
      return ''
    }
  }

  // ==================== Return ====================

  return {
    // Message
    success,
    error,
    warning,
    info,

    // Notification
    notify,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,

    // MessageBox
    confirm,
    alert,
    prompt
  }
}

/**
 * 快捷通知函数（可在非组件中使用）
 */
export const notification = {
  success: (message: string, duration?: number) => {
    ElMessage.success({ message, duration: duration || 3000, showClose: true })
  },

  error: (message: string, duration?: number) => {
    ElMessage.error({ message, duration: duration || 5000, showClose: true })
  },

  warning: (message: string, duration?: number) => {
    ElMessage.warning({ message, duration: duration || 3000, showClose: true })
  },

  info: (message: string, duration?: number) => {
    ElMessage.info({ message, duration: duration || 3000, showClose: true })
  },

  notify: (title: string, message: string, type: NotificationType = 'info') => {
    ElNotification({ title, message, type, duration: 4500 })
  }
}
