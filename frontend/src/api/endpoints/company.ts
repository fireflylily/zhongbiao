/**
 * 公司管理API端点
 *
 * 包含公司信息、资质管理等功能
 */

import { apiClient } from '../client'
import type {
  Company,
  CompanyQualification,
  QualificationType,
  ApiResponse,
  ListApiResponse,
  PaginatedApiResponse,
  PaginationParams
} from '@/types'

/**
 * 公司管理API
 */
export const companyApi = {
  // ==================== 公司管理 ====================

  /**
   * 获取公司列表
   */
  async getCompanies(params?: PaginationParams): Promise<ListApiResponse<Company>> {
    return apiClient.get('/companies', params)
  },

  /**
   * 获取公司详情
   */
  async getCompany(companyId: number): Promise<ApiResponse<Company>> {
    return apiClient.get(`/companies/${companyId}`)
  },

  /**
   * 创建新公司
   */
  async createCompany(data: {
    name: string
    code?: string
    address?: string
    contact_person?: string
    contact_phone?: string
    email?: string
    website?: string
    description?: string
  }): Promise<ApiResponse<Company>> {
    return apiClient.post('/companies', data)
  },

  /**
   * 更新公司信息
   */
  async updateCompany(
    companyId: number,
    data: Partial<Company>
  ): Promise<ApiResponse<Company>> {
    return apiClient.put(`/companies/${companyId}`, data)
  },

  /**
   * 删除公司
   */
  async deleteCompany(companyId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/companies/${companyId}`)
  },

  // ==================== 资质管理 ====================

  /**
   * 获取公司资质列表
   */
  async getCompanyQualifications(
    companyId: number
  ): Promise<ListApiResponse<CompanyQualification>> {
    return apiClient.get(`/companies/${companyId}/qualifications`)
  },

  /**
   * 获取资质类型列表
   */
  async getQualificationTypes(): Promise<ListApiResponse<QualificationType>> {
    return apiClient.get('/qualification-types')
  },

  /**
   * 上传资质文件
   */
  async uploadQualification(
    companyId: number,
    typeKey: string,
    file: File,
    data: {
      issue_date?: string
      expiry_date?: string
      issuing_authority?: string
      certificate_number?: string
      notes?: string
    },
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<CompanyQualification>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('company_id', companyId.toString())
    formData.append('type_key', typeKey)

    // 添加可选字段
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value)
      }
    })

    return apiClient.upload('/qualifications/upload', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 更新资质信息
   */
  async updateQualification(
    qualificationId: number,
    data: {
      issue_date?: string
      expiry_date?: string
      issuing_authority?: string
      certificate_number?: string
      notes?: string
      status?: 'active' | 'expired' | 'pending'
    }
  ): Promise<ApiResponse<CompanyQualification>> {
    return apiClient.put(`/qualifications/${qualificationId}`, data)
  },

  /**
   * 删除资质
   */
  async deleteQualification(qualificationId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/qualifications/${qualificationId}`)
  },

  /**
   * 下载资质文件
   */
  async downloadQualification(
    qualificationId: number,
    filename: string,
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    return apiClient.download(
      `/qualifications/${qualificationId}/download`,
      filename,
      (event) => {
        if (onProgress && event.total) {
          const progress = Math.round((event.loaded * 100) / event.total)
          onProgress(progress)
        }
      }
    )
  },

  /**
   * 批量上传资质
   */
  async batchUploadQualifications(
    companyId: number,
    files: Array<{ file: File; typeKey: string }>,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<CompanyQualification[]>> {
    const formData = new FormData()
    formData.append('company_id', companyId.toString())

    files.forEach((item, index) => {
      formData.append(`files[${index}]`, item.file)
      formData.append(`type_keys[${index}]`, item.typeKey)
    })

    return apiClient.upload('/qualifications/batch-upload', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 获取即将过期的资质
   */
  async getExpiringQualifications(
    companyId: number,
    days: number = 30
  ): Promise<ListApiResponse<CompanyQualification>> {
    return apiClient.get(`/companies/${companyId}/qualifications/expiring`, { days })
  },

  /**
   * 搜索公司
   */
  async searchCompanies(keyword: string): Promise<ListApiResponse<Company>> {
    return apiClient.get('/companies/search', { keyword })
  }
}
