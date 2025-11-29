/**
 * 认证API端点
 *
 * 包含登录、登出、用户管理等功能
 */

import { apiClient } from '../client'
import type { User, ApiResponse } from '@/types'

/**
 * 认证API
 */
export const authApi = {
  /**
   * 用户登录
   */
  async login(data: { username: string; password: string }): Promise<
    ApiResponse<{
      user: User
      token?: string
    }>
  > {
    const response = await apiClient.post('/api/auth/login', data)

    // 如果返回token，保存到localStorage
    if (response.data?.token) {
      localStorage.setItem('auth_token', response.data.token)
      apiClient.setAuthToken(response.data.token)
    }

    return response
  },

  /**
   * 用户登出
   */
  async logout(): Promise<ApiResponse<void>> {
    const response = await apiClient.post('/auth/logout')

    // 清除本地token
    localStorage.removeItem('auth_token')
    apiClient.clearAuthToken()

    return response
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiClient.get('/auth/user')
  },

  /**
   * 更新当前用户信息
   */
  async updateCurrentUser(data: Partial<User>): Promise<ApiResponse<User>> {
    return apiClient.put('/auth/user', data)
  },

  /**
   * 修改密码
   */
  async changePassword(data: {
    old_password: string
    new_password: string
    confirm_password: string
  }): Promise<ApiResponse<void>> {
    return apiClient.post('/auth/change-password', data)
  },

  /**
   * 重置密码（需要管理员权限）
   */
  async resetPassword(userId: number, newPassword: string): Promise<ApiResponse<void>> {
    return apiClient.post('/auth/reset-password', {
      user_id: userId,
      new_password: newPassword
    })
  },

  /**
   * 验证token有效性
   */
  async verifyToken(): Promise<ApiResponse<{ valid: boolean; user?: User }>> {
    return apiClient.get('/auth/verify-token')
  },

  /**
   * 刷新token
   */
  async refreshToken(): Promise<
    ApiResponse<{
      token: string
      user: User
    }>
  > {
    const response = await apiClient.post('/auth/refresh-token')

    // 更新token
    if (response.data?.token) {
      localStorage.setItem('auth_token', response.data.token)
      apiClient.setAuthToken(response.data.token)
    }

    return response
  },

  /**
   * 从localStorage恢复认证状态
   */
  restoreAuth(): void {
    const token = localStorage.getItem('auth_token')
    if (token) {
      apiClient.setAuthToken(token)
    }
  }
}
