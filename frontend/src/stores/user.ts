/**
 * 用户状态管理
 *
 * 管理当前登录用户的信息、认证状态和权限
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import type { User, UserState } from '@/types'

/**
 * 用户Store
 */
export const useUserStore = defineStore('user', () => {
  // ==================== State ====================

  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(null)
  const permissions = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==================== Getters ====================

  const isLoggedIn = computed(() => !!currentUser.value && !!token.value)

  const hasToken = computed(() => !!token.value)

  const userId = computed(() => currentUser.value?.id || null)

  const username = computed(() => currentUser.value?.username || '')

  const userEmail = computed(() => currentUser.value?.email || '')

  const hasPermission = computed(() => {
    return (permission: string) => permissions.value.includes(permission)
  })

  const isAdmin = computed(() => {
    return currentUser.value?.role === 'admin' || permissions.value.includes('admin')
  })

  // ==================== Actions ====================

  /**
   * 用户登录
   */
  async function login(credentials: { username: string; password: string }): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)

      if (response.success && response.data) {
        currentUser.value = response.data.user
        token.value = response.data.token || null

        // 保存到localStorage
        saveToStorage()

        return true
      }

      // 登录失败，抛出异常而不是返回 false
      error.value = response.message || '登录失败'
      throw new Error(error.value)
    } catch (err: any) {
      error.value = err.message || '登录失败'
      throw err  // 重新抛出异常
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  async function logout(): Promise<void> {
    loading.value = true

    try {
      await authApi.logout()
    } catch (err) {
      console.error('登出请求失败:', err)
    } finally {
      // 清除状态（无论API调用是否成功）
      currentUser.value = null
      token.value = null
      permissions.value = []
      error.value = null

      // 清除localStorage
      clearStorage()

      loading.value = false
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.getCurrentUser()

      if (response.success && response.data) {
        currentUser.value = response.data
        saveToStorage()
      }
    } catch (err: any) {
      error.value = err.message || '获取用户信息失败'
      console.error('获取用户信息失败:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新当前用户信息
   */
  async function updateUser(data: Partial<User>): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.updateCurrentUser(data)

      if (response.success && response.data) {
        currentUser.value = response.data
        saveToStorage()
        return true
      }

      error.value = response.message || '更新失败'
      return false
    } catch (err: any) {
      error.value = err.message || '更新失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 修改密码
   */
  async function changePassword(
    oldPassword: string,
    newPassword: string
  ): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      })

      if (response.success) {
        return true
      }

      error.value = response.message || '密码修改失败'
      return false
    } catch (err: any) {
      error.value = err.message || '密码修改失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 验证Token有效性
   */
  async function verifyToken(): Promise<boolean> {
    if (!token.value) {
      return false
    }

    try {
      const response = await authApi.verifyToken()

      if (response.success && response.data?.valid) {
        if (response.data.user) {
          currentUser.value = response.data.user
          saveToStorage()
        }
        return true
      }

      // Token无效，清除状态
      await logout()
      return false
    } catch (err) {
      console.error('Token验证失败:', err)
      await logout()
      return false
    }
  }

  /**
   * 刷新Token
   */
  async function refreshToken(): Promise<boolean> {
    try {
      const response = await authApi.refreshToken()

      if (response.success && response.data) {
        token.value = response.data.token
        if (response.data.user) {
          currentUser.value = response.data.user
        }
        saveToStorage()
        return true
      }

      return false
    } catch (err) {
      console.error('Token刷新失败:', err)
      return false
    }
  }

  /**
   * 设置权限
   */
  function setPermissions(newPermissions: string[]): void {
    permissions.value = newPermissions
    saveToStorage()
  }

  /**
   * 从localStorage恢复状态
   */
  function restoreFromStorage(): void {
    try {
      const savedUser = localStorage.getItem('user')
      const savedToken = localStorage.getItem('auth_token')
      const savedPermissions = localStorage.getItem('user_permissions')

      if (savedUser) {
        currentUser.value = JSON.parse(savedUser)
      }

      if (savedToken) {
        token.value = savedToken
        // 恢复API客户端的token
        authApi.restoreAuth()
      }

      if (savedPermissions) {
        permissions.value = JSON.parse(savedPermissions)
      }
    } catch (err) {
      console.error('恢复用户状态失败:', err)
    }
  }

  /**
   * 保存到localStorage
   */
  function saveToStorage(): void {
    try {
      if (currentUser.value) {
        localStorage.setItem('user', JSON.stringify(currentUser.value))
      }

      if (token.value) {
        localStorage.setItem('auth_token', token.value)
      }

      if (permissions.value.length > 0) {
        localStorage.setItem('user_permissions', JSON.stringify(permissions.value))
      }
    } catch (err) {
      console.error('保存用户状态失败:', err)
    }
  }

  /**
   * 清除localStorage
   */
  function clearStorage(): void {
    localStorage.removeItem('user')
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_permissions')
  }

  /**
   * 重置状态
   */
  function $reset(): void {
    currentUser.value = null
    token.value = null
    permissions.value = []
    loading.value = false
    error.value = null
    clearStorage()
  }

  // ==================== Return ====================

  return {
    // State
    currentUser,
    token,
    permissions,
    loading,
    error,

    // Getters
    isLoggedIn,
    hasToken,
    userId,
    username,
    userEmail,
    hasPermission,
    isAdmin,

    // Actions
    login,
    logout,
    fetchCurrentUser,
    updateUser,
    changePassword,
    verifyToken,
    refreshToken,
    setPermissions,
    restoreFromStorage,
    saveToStorage,
    clearStorage,
    $reset
  }
})
