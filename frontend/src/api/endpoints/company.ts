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
   * 返回格式：{ data: { id_card_front: {...}, business_license: {...}, ... } }
   */
  async getCompanyQualifications(
    companyId: number
  ): Promise<ApiResponse<Record<string, CompanyQualification>>> {
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

    // 后端期望的格式是 qualifications[typeKey] 而不是单独的 file 字段
    formData.append(`qualifications[${typeKey}]`, file)

    // 如果有额外的资质名称，添加到 qualification_names（JSON格式）
    const qualificationNames: Record<string, string> = {}
    formData.append('qualification_names', JSON.stringify(qualificationNames))

    // 如果有文件版本信息，添加到 file_versions（JSON格式）
    const fileVersions: Record<string, string> = {}
    if (data.notes) {
      // 可以将 notes 作为文件版本使用
      fileVersions[typeKey] = data.notes
    }
    formData.append('file_versions', JSON.stringify(fileVersions))

    return apiClient.upload(`/companies/${companyId}/qualifications/upload`, formData, (event) => {
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
  },

  // ==================== 智能提取 ====================

  /**
   * 从标书中提取公司信息
   * @param formData 包含file字段的FormData
   * @returns 提取的公司信息预览
   */
  async extractFromTender(formData: FormData): Promise<ApiResponse<{
    company_info: Record<string, any>
    authorized_person: Record<string, any>
    financial_info: Record<string, any>
    qualification_images: Array<{
      index: number
      image_data: string
      content_type: string
      original_filename: string
      guessed_type: string
      guessed_type_name: string
      confidence: number
      confirmed: boolean
    }>
    extraction_time: string
    model_used: string
  }>> {
    return apiClient.upload('/companies/extract-from-tender', formData)
  }
}
