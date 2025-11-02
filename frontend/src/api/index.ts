/**
 * API模块主入口
 *
 * 统一配置和导出所有API相关功能
 */

import { apiClient } from './client'
import { setupInterceptors } from './interceptors'

// 安装拦截器（自动处理CSRF、错误、重试）
setupInterceptors(apiClient.getInstance(), {
  maxRetries: 3, // 最大重试3次
  retryDelay: 1000 // 重试延迟1秒
})

// 导出所有API模块
export * from './endpoints'

// 导出API客户端（用于自定义请求）
export { apiClient }

/**
 * 初始化API模块
 *
 * 在应用启动时调用，恢复认证状态等
 */
export function initializeApi(): void {
  // 恢复认证token
  const token = localStorage.getItem('auth_token')
  if (token) {
    apiClient.setAuthToken(token)
  }

  // 可以在这里添加其他初始化逻辑
  // 例如：设置全局请求头、配置拦截器等
}
