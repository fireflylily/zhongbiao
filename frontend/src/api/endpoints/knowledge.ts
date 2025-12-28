/**
 * 知识库API端点
 *
 * 包含企业知识库、案例库、简历库管理功能
 */

import { apiClient } from '../client'
import type {
  KnowledgeDocument,
  KnowledgeCategory,
  Case,
  CaseAttachment,
  Resume,
  ResumeAttachment,
  ProjectExperience,
  ApiResponse,
  ListApiResponse,
  PaginatedApiResponse,
  PaginationParams,
  KnowledgeSearchRequest,
  RAGRetrievalRequest
} from '@/types'

/**
 * 知识库API
 */
export const knowledgeApi = {
  // ==================== 企业知识库 ====================

  /**
   * 获取知识文档列表
   */
  async getKnowledgeDocuments(
    params?: PaginationParams & { category?: string; company_id?: number }
  ): Promise<PaginatedApiResponse<KnowledgeDocument>> {
    return apiClient.get('/knowledge/documents', params)
  },

  /**
   * 获取知识文档详情
   */
  async getKnowledgeDocument(documentId: number): Promise<ApiResponse<KnowledgeDocument>> {
    return apiClient.get(`/knowledge/documents/${documentId}`)
  },

  /**
   * 上传知识文档
   */
  async uploadKnowledgeDocument(
    data: {
      company_id: number
      category: string
      title: string
      description?: string
      file: File
    },
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<KnowledgeDocument>> {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('company_id', data.company_id.toString())
    formData.append('category', data.category)
    formData.append('title', data.title)
    if (data.description) {
      formData.append('description', data.description)
    }

    return apiClient.upload('/knowledge/documents/upload', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 更新知识文档
   */
  async updateKnowledgeDocument(
    documentId: number,
    data: Partial<KnowledgeDocument>
  ): Promise<ApiResponse<KnowledgeDocument>> {
    return apiClient.put(`/knowledge/documents/${documentId}`, data)
  },

  /**
   * 删除知识文档
   */
  async deleteKnowledgeDocument(documentId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/knowledge/documents/${documentId}`)
  },

  /**
   * 获取知识分类列表
   */
  async getKnowledgeCategories(): Promise<ListApiResponse<KnowledgeCategory>> {
    return apiClient.get('/knowledge/categories')
  },

  /**
   * 搜索知识库
   */
  async searchKnowledge(
    params: KnowledgeSearchRequest
  ): Promise<ListApiResponse<KnowledgeDocument>> {
    return apiClient.post('/knowledge/search', params)
  },

  /**
   * RAG检索（向量搜索）
   */
  async ragRetrieval(params: RAGRetrievalRequest): Promise<ApiResponse<any>> {
    return apiClient.post('/knowledge/rag-retrieval', params)
  },

  // ==================== 案例库 ====================

  /**
   * 获取案例列表
   */
  async getCases(
    params?: PaginationParams & { company_id?: number; industry?: string; contract_type?: string; case_status?: string }
  ): Promise<ListApiResponse<Case>> {
    return apiClient.get('/case_library/cases', params)
  },

  /**
   * 获取案例详情
   */
  async getCase(caseId: number): Promise<ApiResponse<Case>> {
    return apiClient.get(`/case_library/cases/${caseId}`)
  },

  /**
   * 创建案例
   */
  async createCase(data: {
    company_id: number
    case_title: string
    customer_name: string
    industry?: string
    contract_type: '订单' | '合同'
    contract_amount?: string
    contract_start_date?: string
    contract_end_date?: string
    party_a_contact_name?: string
    party_a_contact_phone?: string
    party_a_contact_email?: string
    case_status?: 'success' | 'in_progress' | 'pending_acceptance'
  }): Promise<ApiResponse<Case>> {
    return apiClient.post('/case_library/cases', data)
  },

  /**
   * 更新案例
   */
  async updateCase(caseId: number, data: Partial<Case>): Promise<ApiResponse<Case>> {
    return apiClient.put(`/case_library/cases/${caseId}`, data)
  },

  /**
   * 删除案例
   */
  async deleteCase(caseId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/case_library/cases/${caseId}`)
  },

  /**
   * 获取案例附件列表
   */
  async getCaseAttachments(caseId: number): Promise<ListApiResponse<CaseAttachment>> {
    return apiClient.get(`/case_library/cases/${caseId}/attachments`)
  },

  /**
   * 上传案例附件
   */
  async uploadCaseAttachment(
    caseId: number,
    file: File,
    attachmentType: 'contract' | 'acceptance' | 'testimony' | 'photo' | 'other',
    description?: string,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('attachment_type', attachmentType)
    if (description) {
      formData.append('description', description)
    }

    return apiClient.upload(`/case_library/cases/${caseId}/attachments`, formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 删除案例附件
   */
  async deleteCaseAttachment(attachmentId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/case_library/attachments/${attachmentId}`)
  },

  /**
   * 下载案例附件
   */
  downloadCaseAttachment(attachmentId: number): string {
    return `${apiClient.getInstance().defaults.baseURL}/case_library/attachments/${attachmentId}/download`
  },

  /**
   * 搜索案例
   */
  async searchCases(query: string, companyId?: number): Promise<ListApiResponse<Case>> {
    return apiClient.get('/case_library/search', { q: query, company_id: companyId })
  },

  /**
   * 获取案例统计信息
   */
  async getCaseStatistics(companyId?: number): Promise<ApiResponse<any>> {
    return apiClient.get('/case_library/statistics', companyId ? { company_id: companyId } : undefined)
  },

  // ==================== 简历库 ====================

  /**
   * 获取简历列表
   */
  async getResumes(params?: {
    company_id?: number
    status?: string
    search?: string
    education_level?: string
    position?: string
    tags?: string[]
    page?: number
    page_size?: number
  }): Promise<ApiResponse<any>> {
    return apiClient.get('/resume_library/list', params)
  },

  /**
   * 获取简历详情
   */
  async getResume(resumeId: number): Promise<ApiResponse<Resume>> {
    return apiClient.get(`/resume_library/detail/${resumeId}`)
  },

  /**
   * 创建简历
   */
  async createResume(data: {
    company_id?: number
    name: string
    gender?: string
    birth_date?: string
    phone?: string
    email?: string
    education_level?: string
    degree?: string
    university?: string
    major?: string
    current_position?: string
    professional_title?: string
    work_years?: number
    current_company?: string
    skills?: string
    certificates?: string
    introduction?: string
    status?: 'active' | 'inactive' | 'archived'
  }): Promise<ApiResponse<Resume>> {
    return apiClient.post('/resume_library/create', data)
  },

  /**
   * 更新简历
   */
  async updateResume(
    resumeId: number,
    data: Partial<Resume>
  ): Promise<ApiResponse<Resume>> {
    return apiClient.put(`/resume_library/update/${resumeId}`, data)
  },

  /**
   * 删除简历
   */
  async deleteResume(resumeId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/resume_library/delete/${resumeId}`)
  },

  /**
   * 解析简历文件
   */
  async parseResumeFile(
    file: File,
    autoCreate: boolean = false,
    companyId?: number,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('auto_create', autoCreate.toString())
    if (companyId) {
      formData.append('company_id', companyId.toString())
    }

    return apiClient.upload('/resume_library/parse-resume', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 上传简历附件
   */
  async uploadResumeAttachment(
    resumeId: number,
    file: File,
    category: 'resume' | 'id_card' | 'education' | 'degree' | 'qualification' | 'award' | 'other',
    description?: string,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('resume_id', resumeId.toString())
    formData.append('attachment_category', category)
    if (description) {
      formData.append('description', description)
    }

    return apiClient.upload('/resume_library/upload-attachment', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 获取简历附件列表
   */
  async getResumeAttachments(resumeId: number, category?: string): Promise<ApiResponse<ResumeAttachment[]>> {
    return apiClient.get(`/resume_library/attachments/${resumeId}`, category ? { category } : undefined)
  },

  /**
   * 删除简历附件
   */
  async deleteResumeAttachment(attachmentId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/resume_library/attachment/${attachmentId}`)
  },

  /**
   * 下载简历附件
   */
  downloadResumeAttachment(attachmentId: number): string {
    return `${apiClient.getInstance().defaults.baseURL}/resume_library/attachment/${attachmentId}/download`
  },

  /**
   * 搜索简历
   */
  async searchResumes(keyword: string, limit: number = 10): Promise<ApiResponse<Resume[]>> {
    return apiClient.get('/resume_library/search', { keyword, limit })
  },

  /**
   * 获取简历统计信息
   */
  async getResumeStatistics(companyId?: number): Promise<ApiResponse<any>> {
    return apiClient.get('/resume_library/statistics', companyId ? { company_id: companyId } : undefined)
  },

  /**
   * 批量导出简历
   */
  async exportResumes(
    resumeIds: number[],
    options?: any
  ): Promise<ApiResponse<any>> {
    return apiClient.post('/resume_library/export', { resume_ids: resumeIds, options })
  },

  /**
   * 获取附件类别列表
   */
  async getAttachmentCategories(): Promise<ApiResponse<any[]>> {
    return apiClient.get('/resume_library/categories')
  },

  /**
   * 获取学历级别列表
   */
  async getEducationLevels(): Promise<ApiResponse<any[]>> {
    return apiClient.get('/resume_library/education-levels')
  },

  // ==================== 产品分类 ====================

  /**
   * 获取产品分类列表（含子项）
   */
  async getProductCategories(): Promise<ApiResponse<{
    category_id: number
    category_name: string
    category_code: string
    category_description?: string
    category_order?: number
    items: {
      item_id: number
      item_name: string
      item_code?: string
      item_description?: string
      item_order?: number
    }[]
  }[]>> {
    return apiClient.get('/product-categories')
  },

  /**
   * 获取产品分类详情
   */
  async getProductCategory(categoryId: number): Promise<ApiResponse<any>> {
    return apiClient.get(`/product-categories/${categoryId}`)
  }
}
