/**
 * Axios HTTP客户端配置
 *
 * 提供统一的HTTP请求客户端，包含：
 * - 基础配置（baseURL, timeout, headers）
 * - CSRF Token自动注入
 * - 请求/响应拦截器
 * - 自动重试机制
 */

import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@/types'
import { setupInterceptors } from './interceptors'

/**
 * API客户端配置选项
 */
interface ApiClientConfig {
  baseURL?: string
  timeout?: number
  withCredentials?: boolean
  retryCount?: number
  retryDelay?: number
}

/**
 * 默认配置
 */
const DEFAULT_CONFIG: ApiClientConfig = {
  baseURL: '/api',
  timeout: 30000, // 30秒超时
  withCredentials: true, // 携带cookie（CSRF token需要）
  retryCount: 3, // 失败重试3次
  retryDelay: 1000 // 重试延迟1秒
}

/**
 * 获取CSRF Token
 */
function getCsrfToken(): string | null {
  // 从cookie中读取CSRF token
  const match = document.cookie.match(/csrf_token=([^;]+)/)
  if (match) {
    return match[1]
  }

  // 从meta标签读取（备选方案）
  const metaTag = document.querySelector('meta[name="csrf-token"]')
  if (metaTag) {
    return metaTag.getAttribute('content')
  }

  return null
}

/**
 * 创建Axios实例
 */
function createAxiosInstance(config: ApiClientConfig = {}): AxiosInstance {
  const finalConfig = { ...DEFAULT_CONFIG, ...config }

  const instance = axios.create({
    baseURL: finalConfig.baseURL,
    timeout: finalConfig.timeout,
    withCredentials: finalConfig.withCredentials,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  return instance
}

/**
 * API客户端类
 */
class ApiClient {
  private instance: AxiosInstance
  private config: ApiClientConfig

  constructor(config: ApiClientConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.instance = createAxiosInstance(this.config)

    // Setup interceptors for CSRF token injection and error handling
    setupInterceptors(this.instance, {
      maxRetries: this.config.retryCount,
      retryDelay: this.config.retryDelay
    })
  }

  /**
   * 获取Axios实例（用于自定义请求）
   */
  getInstance(): AxiosInstance {
    return this.instance
  }

  /**
   * GET请求
   */
  async get<T = any>(
    url: string,
    params?: Record<string, any>,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.get(url, {
      params,
      ...config
    })
    return response.data
  }

  /**
   * POST请求
   */
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.post(url, data, config)
    return response.data
  }

  /**
   * PUT请求
   */
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.put(url, data, config)
    return response.data
  }

  /**
   * DELETE请求
   */
  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.delete(url, config)
    return response.data
  }

  /**
   * PATCH请求
   */
  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.patch(url, data, config)
    return response.data
  }

  /**
   * 文件上传（multipart/form-data）
   */
  async upload<T = any>(
    url: string,
    formData: FormData,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress
    })
    return response.data
  }

  /**
   * 文件下载
   */
  async download(
    url: string,
    filename?: string,
    onDownloadProgress?: (progressEvent: any) => void
  ): Promise<Blob> {
    const response = await this.instance.get(url, {
      responseType: 'blob',
      onDownloadProgress
    })

    // 自动触发下载
    if (filename) {
      const blob = response.data
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    }

    return response.data
  }

  /**
   * 设置默认请求头
   */
  setHeader(key: string, value: string): void {
    this.instance.defaults.headers.common[key] = value
  }

  /**
   * 移除默认请求头
   */
  removeHeader(key: string): void {
    delete this.instance.defaults.headers.common[key]
  }

  /**
   * 设置Authorization token
   */
  setAuthToken(token: string): void {
    this.setHeader('Authorization', `Bearer ${token}`)
  }

  /**
   * 清除Authorization token
   */
  clearAuthToken(): void {
    this.removeHeader('Authorization')
  }
}

/**
 * 默认API客户端实例
 */
export const apiClient = new ApiClient()

/**
 * 导出类和工具函数
 */
export { ApiClient, getCsrfToken }
export type { ApiClientConfig }
