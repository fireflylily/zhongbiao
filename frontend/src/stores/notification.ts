/**
 * 通知状态管理
 *
 * 管理应用内的通知消息队列
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NotificationState, NotificationItem } from '@/types'

/**
 * 通知Store
 */
export const useNotificationStore = defineStore('notification', () => {
  // ==================== State ====================

  const notifications = ref<NotificationItem[]>([])
  const maxNotifications = ref(5) // 最多显示5个通知

  // ==================== Getters ====================

  const notificationsCount = computed(() => notifications.value.length)

  const hasNotifications = computed(() => notifications.value.length > 0)

  const unreadCount = computed(() => {
    // 如果未来添加已读/未读状态，可以在这里统计
    return notifications.value.length
  })

  const recentNotifications = computed(() => {
    return notifications.value.slice(0, maxNotifications.value)
  })

  // ==================== Actions ====================

  /**
   * 添加通知
   */
  function addNotification(
    type: 'success' | 'error' | 'warning' | 'info',
    title: string,
    message: string,
    duration?: number
  ): string {
    const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    const notification: NotificationItem = {
      id,
      type,
      title,
      message,
      duration: duration || 3000,
      timestamp: new Date()
    }

    // 添加到队列开头
    notifications.value.unshift(notification)

    // 限制通知数量
    if (notifications.value.length > maxNotifications.value) {
      notifications.value = notifications.value.slice(0, maxNotifications.value)
    }

    // 自动移除（如果设置了duration）
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, notification.duration)
    }

    return id
  }

  /**
   * 成功通知
   */
  function success(title: string, message: string = '', duration?: number): string {
    return addNotification('success', title, message, duration)
  }

  /**
   * 错误通知
   */
  function error(title: string, message: string = '', duration?: number): string {
    return addNotification('error', title, message, duration || 5000) // 错误默认5秒
  }

  /**
   * 警告通知
   */
  function warning(title: string, message: string = '', duration?: number): string {
    return addNotification('warning', title, message, duration)
  }

  /**
   * 信息通知
   */
  function info(title: string, message: string = '', duration?: number): string {
    return addNotification('info', title, message, duration)
  }

  /**
   * 移除通知
   */
  function removeNotification(id: string): void {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * 清除所有通知
   */
  function clearAll(): void {
    notifications.value = []
  }

  /**
   * 清除指定类型的通知
   */
  function clearByType(type: 'success' | 'error' | 'warning' | 'info'): void {
    notifications.value = notifications.value.filter((n) => n.type !== type)
  }

  /**
   * 设置最大通知数量
   */
  function setMaxNotifications(max: number): void {
    maxNotifications.value = max

    // 如果当前通知数量超过限制，移除旧的
    if (notifications.value.length > max) {
      notifications.value = notifications.value.slice(0, max)
    }
  }

  /**
   * 获取指定ID的通知
   */
  function getNotification(id: string): NotificationItem | null {
    return notifications.value.find((n) => n.id === id) || null
  }

  /**
   * 重置状态
   */
  function $reset(): void {
    notifications.value = []
    maxNotifications.value = 5
  }

  // ==================== Return ====================

  return {
    // State
    notifications,
    maxNotifications,

    // Getters
    notificationsCount,
    hasNotifications,
    unreadCount,
    recentNotifications,

    // Actions
    addNotification,
    success,
    error,
    warning,
    info,
    removeNotification,
    clearAll,
    clearByType,
    setMaxNotifications,
    getNotification,
    $reset
  }
})
