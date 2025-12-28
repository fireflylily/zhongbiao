/**
 * 公司状态管理
 *
 * 管理当前选中的公司和公司列表
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { companyApi } from '@/api'
import type { Company, CompanyState } from '@/types'

/**
 * 公司Store
 */
export const useCompanyStore = defineStore('company', () => {
  // ==================== State ====================

  const currentCompany = ref<Company | null>(null)
  const companies = ref<Company[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==================== Getters ====================

  const companyId = computed(() => currentCompany.value?.id || null)

  const companyName = computed(() => currentCompany.value?.name || '')

  const companyCode = computed(() => currentCompany.value?.code || '')

  const hasCurrentCompany = computed(() => !!currentCompany.value)

  const companiesCount = computed(() => companies.value.length)

  const companiesOptions = computed(() => {
    return companies.value.map((company) => ({
      label: company.name,
      value: company.id
    }))
  })

  // ==================== Actions ====================

  /**
   * 设置当前公司
   */
  function setCurrentCompany(company: Company): void {
    currentCompany.value = company
    saveToStorage()
  }

  /**
   * 通过ID设置当前公司
   */
  async function setCurrentCompanyById(companyId: number): Promise<boolean> {
    // 先从已加载的公司列表中查找
    const company = companies.value.find((c) => c.id === companyId)

    if (company) {
      setCurrentCompany(company)
      return true
    }

    // 如果列表中没有，从API获取
    loading.value = true
    error.value = null

    try {
      const response = await companyApi.getCompany(companyId)

      if (response.success && response.data) {
        setCurrentCompany(response.data)
        return true
      }

      error.value = response.message || '获取公司信息失败'
      return false
    } catch (err: any) {
      error.value = err.message || '获取公司信息失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 清除当前公司
   */
  function clearCurrentCompany(): void {
    currentCompany.value = null
    localStorage.removeItem('current_company')
  }

  /**
   * 获取公司列表
   */
  async function fetchCompanies(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await companyApi.getCompanies()

      if (response.success && response.data) {
        // 后端返回 company_id，前端使用 id，需要做字段映射
        companies.value = response.data.map((item: any) => ({
          ...item,
          id: item.company_id ?? item.id,  // 优先使用 company_id，兼容两种格式
          name: item.name ?? item.company_name  // 优先使用 name，兼容 company_name
        }))
      }
    } catch (err: any) {
      error.value = err.message || '获取公司列表失败'
      console.error('获取公司列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个公司详情
   */
  async function fetchCompany(companyId: number): Promise<Company | null> {
    loading.value = true
    error.value = null

    try {
      const response = await companyApi.getCompany(companyId)

      if (response.success && response.data) {
        // 更新列表中的公司信息
        const index = companies.value.findIndex((c) => c.id === companyId)
        if (index !== -1) {
          companies.value[index] = response.data
        } else {
          companies.value.push(response.data)
        }

        return response.data
      }

      error.value = response.message || '获取公司详情失败'
      return null
    } catch (err: any) {
      error.value = err.message || '获取公司详情失败'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建新公司
   */
  async function createCompany(data: {
    name: string
    code?: string
    address?: string
    contact_person?: string
    contact_phone?: string
    email?: string
    website?: string
    description?: string
  }): Promise<Company | null> {
    loading.value = true
    error.value = null

    try {
      const response = await companyApi.createCompany(data)

      if (response.success && response.data) {
        // 添加到列表
        companies.value.push(response.data)
        return response.data
      }

      error.value = response.message || '创建公司失败'
      return null
    } catch (err: any) {
      error.value = err.message || '创建公司失败'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新公司信息
   */
  async function updateCompany(
    companyId: number,
    data: Partial<Company>
  ): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await companyApi.updateCompany(companyId, data)

      if (response.success && response.data) {
        // 更新列表中的公司
        const index = companies.value.findIndex((c) => c.id === companyId)
        if (index !== -1) {
          companies.value[index] = response.data
        }

        // 如果是当前公司，也更新
        if (currentCompany.value?.id === companyId) {
          currentCompany.value = response.data
          saveToStorage()
        }

        return true
      }

      error.value = response.message || '更新公司失败'
      return false
    } catch (err: any) {
      error.value = err.message || '更新公司失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除公司
   */
  async function deleteCompany(companyId: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await companyApi.deleteCompany(companyId)

      if (response.success) {
        // 从列表中移除
        companies.value = companies.value.filter((c) => c.id !== companyId)

        // 如果删除的是当前公司，清除当前公司
        if (currentCompany.value?.id === companyId) {
          clearCurrentCompany()
        }

        return true
      }

      error.value = response.message || '删除公司失败'
      return false
    } catch (err: any) {
      error.value = err.message || '删除公司失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 搜索公司
   */
  async function searchCompanies(keyword: string): Promise<Company[]> {
    if (!keyword.trim()) {
      return companies.value
    }

    loading.value = true
    error.value = null

    try {
      const response = await companyApi.searchCompanies(keyword)

      if (response.success && response.data) {
        return response.data
      }

      return []
    } catch (err: any) {
      error.value = err.message || '搜索失败'
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 从localStorage恢复状态
   */
  function restoreFromStorage(): void {
    try {
      const savedCompany = localStorage.getItem('current_company')

      if (savedCompany) {
        currentCompany.value = JSON.parse(savedCompany)
      }
    } catch (err) {
      console.error('恢复公司状态失败:', err)
    }
  }

  /**
   * 保存到localStorage
   */
  function saveToStorage(): void {
    try {
      if (currentCompany.value) {
        localStorage.setItem('current_company', JSON.stringify(currentCompany.value))
      }
    } catch (err) {
      console.error('保存公司状态失败:', err)
    }
  }

  /**
   * 重置状态
   */
  function $reset(): void {
    currentCompany.value = null
    companies.value = []
    loading.value = false
    error.value = null
    localStorage.removeItem('current_company')
  }

  // ==================== Return ====================

  return {
    // State
    currentCompany,
    companies,
    loading,
    error,

    // Getters
    companyId,
    companyName,
    companyCode,
    hasCurrentCompany,
    companiesCount,
    companiesOptions,

    // Actions
    setCurrentCompany,
    setCurrentCompanyById,
    clearCurrentCompany,
    fetchCompanies,
    fetchCompany,
    createCompany,
    updateCompany,
    deleteCompany,
    searchCompanies,
    restoreFromStorage,
    saveToStorage,
    $reset
  }
})
