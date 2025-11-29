/**
 * Axios请求/响应拦截器
 *
 * 提供统一的：
 * - 请求前处理（CSRF token注入、日志记录）
 * - 响应后处理（错误处理、数据格式化）
 * - 自动重试机制（指数退避策略）
 */

import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { getCsrfToken } from './client'
import type { ApiResponse, ApiError } from '@/types'

/**
 * 重试配置
 */
interface RetryConfig {
  count: number // 当前重试次数
  maxRetries: number // 最大重试次数
  retryDelay: number // 重试延迟（毫秒）
}

/**
 * 延迟函数
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * 计算指数退避延迟
 */
function calculateBackoffDelay(retryCount: number, baseDelay: number = 1000): number {
  return Math.min(baseDelay * Math.pow(2, retryCount), 10000) // 最多10秒
}

/**
 * 判断是否应该重试
 */
function shouldRetry(error: AxiosError): boolean {
  // 仅对网络错误或5xx服务器错误重试
  if (!error.response) {
    return true // 网络错误
  }

  const status = error.response.status
  return status >= 500 && status < 600 // 5xx服务器错误
}

/**
 * 请求拦截器
 */
function setupRequestInterceptor(instance: AxiosInstance): void {
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // 1. 注入CSRF Token（仅POST/PUT/DELETE/PATCH请求）
      const method = config.method?.toUpperCase()
      if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method || '')) {
        const csrfToken = getCsrfToken()
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken
        }
      }

      // 2. 请求日志（开发环境）
      if (import.meta.env.DEV) {
        console.log('[API Request]', {
          method: config.method?.toUpperCase(),
          url: config.url,
          params: config.params,
          data: config.data
        })
      }

      // 3. 添加时间戳（防止缓存）
      if (config.method?.toUpperCase() === 'GET') {
        config.params = {
          ...config.params,
          _t: Date.now()
        }
      }

      return config
    },
    (error: AxiosError) => {
      console.error('[API Request Error]', error)
      return Promise.reject(error)
    }
  )
}

/**
 * 响应拦截器
 */
function setupResponseInterceptor(instance: AxiosInstance, maxRetries: number = 3, retryDelay: number = 1000): void {
  instance.interceptors.response.use(
    (response: AxiosResponse<ApiResponse>) => {
      // 1. 响应日志（开发环境）
      if (import.meta.env.DEV) {
        console.log('[API Response]', {
          url: response.config.url,
          status: response.status,
          data: response.data
        })
      }

      // 2. 统一响应格式检查
      const data = response.data
      if (data && typeof data === 'object') {
        // 如果后端返回了success字段且为false，抛出错误
        if ('success' in data && data.success === false) {
          const error: ApiError = {
            message: data.message || data.error || '请求失败',
            code: data.code || response.status,
            details: data
          }
          return Promise.reject(error)
        }
      }

      return response
    },
    async (error: AxiosError<ApiResponse>) => {
      // 1. 获取重试配置
      const config = error.config as InternalAxiosRequestConfig & { retryConfig?: RetryConfig }
      if (!config) {
        return Promise.reject(error)
      }

      // 初始化重试配置
      if (!config.retryConfig) {
        config.retryConfig = {
          count: 0,
          maxRetries,
          retryDelay
        }
      }

      // 2. 判断是否应该重试
      if (config.retryConfig.count < config.retryConfig.maxRetries && shouldRetry(error)) {
        config.retryConfig.count += 1

        // 计算退避延迟
        const backoffDelay = calculateBackoffDelay(config.retryConfig.count, config.retryConfig.retryDelay)

        console.warn(`[API Retry] 第${config.retryConfig.count}次重试，延迟${backoffDelay}ms`, {
          url: config.url,
          method: config.method
        })

        // 延迟后重试
        await delay(backoffDelay)
        return instance.request(config)
      }

      // 3. 错误处理
      console.error('[API Response Error]', {
        url: config.url,
        method: config.method,
        status: error.response?.status,
        message: error.message,
        data: error.response?.data
      })

      // 4. 格式化错误对象
      const apiError: ApiError = {
        message: '请求失败',
        code: error.response?.status || 0
      }

      if (error.response) {
        // 服务器返回错误
        const data = error.response.data
        if (data && typeof data === 'object') {
          apiError.message = data.message || data.error || `服务器错误 (${error.response.status})`
          apiError.code = data.code || error.response.status
          apiError.details = data
        } else if (typeof data === 'string') {
          apiError.message = data
        } else {
          apiError.message = `HTTP ${error.response.status}: ${error.response.statusText}`
        }

        // 特殊状态码处理
        switch (error.response.status) {
          case 401:
            // 优先使用后端返回的具体错误信息
            apiError.message = data?.message || '未授权，请重新登录'
            // 可以在这里触发登出逻辑
            // window.location.href = '/login'
            break
          case 403:
            apiError.message = data?.message || '无权限访问'
            break
          case 404:
            apiError.message = data?.message || '请求的资源不存在'
            break
          case 422:
            apiError.message = data?.message || '请求参数验证失败'
            break
          case 500:
            apiError.message = data?.message || '服务器内部错误'
            break
          case 502:
            apiError.message = '网关错误'
            break
          case 503:
            apiError.message = '服务暂时不可用'
            break
          case 504:
            apiError.message = '网关超时'
            break
        }
      } else if (error.request) {
        // 请求已发送但没有收到响应
        apiError.message = '网络连接失败，请检查网络设置'
        apiError.code = 0
      } else {
        // 请求配置错误
        apiError.message = error.message || '请求配置错误'
        apiError.code = -1
      }

      return Promise.reject(apiError)
    }
  )
}

/**
 * 安装所有拦截器
 */
export function setupInterceptors(
  instance: AxiosInstance,
  options: { maxRetries?: number; retryDelay?: number } = {}
): void {
  const { maxRetries = 3, retryDelay = 1000 } = options

  setupRequestInterceptor(instance)
  setupResponseInterceptor(instance, maxRetries, retryDelay)
}

/**
 * 导出工具函数
 */
export { shouldRetry, calculateBackoffDelay }
