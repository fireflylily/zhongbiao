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
  Resume,
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
    params?: PaginationParams & { company_id?: number; category?: string }
  ): Promise<PaginatedApiResponse<Case>> {
    return apiClient.get('/knowledge/cases', params)
  },

  /**
   * 获取案例详情
   */
  async getCase(caseId: number): Promise<ApiResponse<Case>> {
    return apiClient.get(`/knowledge/cases/${caseId}`)
  },

  /**
   * 创建案例
   */
  async createCase(data: {
    company_id: number
    project_name: string
    customer_name: string
    contract_amount?: number
    start_date?: string
    end_date?: string
    category?: string
    description?: string
    outcomes?: string
    technologies?: string[]
  }): Promise<ApiResponse<Case>> {
    return apiClient.post('/knowledge/cases', data)
  },

  /**
   * 更新案例
   */
  async updateCase(caseId: number, data: Partial<Case>): Promise<ApiResponse<Case>> {
    return apiClient.put(`/knowledge/cases/${caseId}`, data)
  },

  /**
   * 删除案例
   */
  async deleteCase(caseId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/knowledge/cases/${caseId}`)
  },

  /**
   * 上传案例附件
   */
  async uploadCaseAttachment(
    caseId: number,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('case_id', caseId.toString())

    return apiClient.upload('/knowledge/cases/upload-attachment', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 搜索案例
   */
  async searchCases(keyword: string): Promise<ListApiResponse<Case>> {
    return apiClient.get('/knowledge/cases/search', { keyword })
  },

  // ==================== 简历库 ====================

  /**
   * 获取简历列表
   */
  async getResumes(
    params?: PaginationParams & { company_id?: number; position?: string }
  ): Promise<PaginatedApiResponse<Resume>> {
    return apiClient.get('/knowledge/resumes', params)
  },

  /**
   * 获取简历详情
   */
  async getResume(resumeId: number): Promise<ApiResponse<Resume>> {
    return apiClient.get(`/knowledge/resumes/${resumeId}`)
  },

  /**
   * 创建简历
   */
  async createResume(data: {
    company_id: number
    name: string
    position: string
    department?: string
    phone?: string
    email?: string
    education?: string
    years_of_experience?: number
    skills?: string[]
    certifications?: string[]
    summary?: string
  }): Promise<ApiResponse<Resume>> {
    return apiClient.post('/knowledge/resumes', data)
  },

  /**
   * 更新简历
   */
  async updateResume(
    resumeId: number,
    data: Partial<Resume>
  ): Promise<ApiResponse<Resume>> {
    return apiClient.put(`/knowledge/resumes/${resumeId}`, data)
  },

  /**
   * 删除简历
   */
  async deleteResume(resumeId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/knowledge/resumes/${resumeId}`)
  },

  /**
   * 上传简历文件
   */
  async uploadResumeFile(
    resumeId: number,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('resume_id', resumeId.toString())

    return apiClient.upload('/knowledge/resumes/upload-file', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 上传简历照片
   */
  async uploadResumePhoto(
    resumeId: number,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('photo', file)
    formData.append('resume_id', resumeId.toString())

    return apiClient.upload('/knowledge/resumes/upload-photo', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 添加项目经验
   */
  async addProjectExperience(
    resumeId: number,
    data: {
      project_name: string
      role: string
      start_date: string
      end_date?: string
      description?: string
      achievements?: string
      technologies?: string[]
    }
  ): Promise<ApiResponse<ProjectExperience>> {
    return apiClient.post(`/knowledge/resumes/${resumeId}/experiences`, data)
  },

  /**
   * 更新项目经验
   */
  async updateProjectExperience(
    experienceId: number,
    data: Partial<ProjectExperience>
  ): Promise<ApiResponse<ProjectExperience>> {
    return apiClient.put(`/knowledge/project-experiences/${experienceId}`, data)
  },

  /**
   * 删除项目经验
   */
  async deleteProjectExperience(experienceId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/knowledge/project-experiences/${experienceId}`)
  },

  /**
   * 搜索简历
   */
  async searchResumes(params: {
    keyword?: string
    position?: string
    skills?: string[]
    min_experience?: number
  }): Promise<ListApiResponse<Resume>> {
    return apiClient.get('/knowledge/resumes/search', params)
  },

  /**
   * 批量导出简历
   */
  async exportResumes(
    resumeIds: number[],
    format: 'pdf' | 'docx' = 'pdf'
  ): Promise<Blob> {
    const response = await apiClient.getInstance().post(
      '/knowledge/resumes/export',
      { resume_ids: resumeIds, format },
      { responseType: 'blob' }
    )
    return response.data
  }
}
