/**
 * 投标处理API端点
 *
 * 包含项目管理、文档处理、文档融合等核心功能
 */

import { apiClient } from '../client'
import type {
  Project,
  ProjectDetail,
  Document,
  SourceDocuments,
  MergeTaskResult,
  ApiResponse,
  ListApiResponse,
  PaginatedApiResponse,
  TaskCreateResponse,
  TaskStatusResponse,
  PaginationParams,
  TenderProcessingRequest,
  TenderProcessingResponse,
  DocumentMergeRequest,
  DocumentMergeResponse
} from '@/types'

/**
 * 投标处理API
 */
export const tenderApi = {
  // ==================== 项目管理 ====================

  /**
   * 获取项目列表
   */
  async getProjects(params?: PaginationParams): Promise<PaginatedApiResponse<Project>> {
    return apiClient.get('/tender-projects', params)
  },

  /**
   * 获取项目详情
   */
  async getProject(projectId: number): Promise<ApiResponse<ProjectDetail>> {
    return apiClient.get(`/tender-projects/${projectId}`)
  },

  /**
   * 创建新项目
   */
  async createProject(data: {
    project_name: string
    project_number: string
    company_id: number
    product_category_id?: number
    product_items?: string[]
    description?: string
  }): Promise<ApiResponse<Project>> {
    return apiClient.post('/tender-projects', data)
  },

  /**
   * 更新项目信息
   */
  async updateProject(
    projectId: number,
    data: Partial<Project>
  ): Promise<ApiResponse<Project>> {
    return apiClient.put(`/tender-projects/${projectId}`, data)
  },

  /**
   * 删除项目
   */
  async deleteProject(projectId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/tender-projects/${projectId}`)
  },

  // ==================== 文档管理 ====================

  /**
   * 上传招标文档
   */
  async uploadTenderDocument(
    projectId: number,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<Document>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId.toString())
    formData.append('type', 'tender_document')

    return apiClient.upload('/files/upload', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 上传商务应答模板
   */
  async uploadBusinessTemplate(
    projectId: number,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<Document>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId.toString())

    return apiClient.upload('/files/upload/business-template', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 上传技术方案模板
   */
  async uploadTechnicalTemplate(
    projectId: number,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<Document>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId.toString())
    formData.append('type', 'technical_template')

    return apiClient.upload('/files/upload', formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  /**
   * 获取项目文档列表
   */
  async getProjectDocuments(projectId: number): Promise<ListApiResponse<Document>> {
    return apiClient.get(`/tender-projects/${projectId}/documents`)
  },

  /**
   * 删除文档
   */
  async deleteDocument(documentId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/documents/${documentId}`)
  },

  /**
   * 下载文档
   */
  async downloadDocument(
    documentId: number,
    filename: string,
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    return apiClient.download(`/documents/${documentId}/download`, filename, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    })
  },

  // ==================== 文档处理 ====================

  /**
   * 启动文档处理任务（Step 1 - 解析招标文档）
   */
  async startTenderProcessing(
    data: TenderProcessingRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/tender-processing/start', data)
  },

  /**
   * 获取任务状态
   */
  async getTaskStatus(taskId: string): Promise<ApiResponse<TaskStatusResponse>> {
    return apiClient.get(`/tasks/${taskId}/status`)
  },

  /**
   * 取消任务
   */
  async cancelTask(taskId: string): Promise<ApiResponse<void>> {
    return apiClient.post(`/tasks/${taskId}/cancel`)
  },

  /**
   * 获取任务结果
   */
  async getTaskResult(taskId: string): Promise<ApiResponse<TenderProcessingResponse>> {
    return apiClient.get(`/tasks/${taskId}/result`)
  },

  /**
   * 解析文档结构（用于章节选择）
   *
   * FormData 参数:
   * - file: Word文档文件（与 file_path 二选一）
   * - file_path: 历史文件路径（与 file 二选一）
   * - company_id: 公司ID（必填）
   * - project_id: 项目ID（可选）
   * - methods: 解析方法列表（可选，JSON字符串数组）
   *   例如: JSON.stringify(['toc_exact', 'style'])
   *   可选值: 'toc_exact', 'semantic_anchors', 'style', 'hybrid', 'azure', 'outline_level', 'gemini'
   * - fallback: 是否启用回退机制（可选，'true'/'false'字符串，默认'true'）
   */
  async parseDocumentStructure(formData: FormData): Promise<ApiResponse<{
    task_id: string
    project_id: number
    chapters: any[]
    statistics: any
    method?: string  // 使用的解析方法
  }>> {
    return apiClient.post('/tender-processing/parse-structure', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 180000 // 180秒超时（文档解析可能需要较长时间，包含LLM重试）
    })
  },

  /**
   * 快速解析文档结构（阶段1）
   *
   * 只做LLM目录识别，不做定位和字数统计，快速返回目录树
   *
   * FormData 参数:
   * - file: Word文档文件（与 file_path 二选一）
   * - file_path: 历史文件路径（与 file 二选一）
   * - company_id: 公司ID（必填）
   * - project_id: 项目ID（可选）
   */
  async parseDocumentStructureQuick(formData: FormData): Promise<ApiResponse<{
    project_id: number
    chapters: any[]
    file_path: string
    toc_end_idx: number
    method?: string
  }>> {
    return apiClient.post('/tender-processing/parse-structure-quick', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 180000 // 180秒超时（与 parseDocumentStructure 保持一致）
    })
  },

  /**
   * 补充章节信息（阶段2）
   *
   * 执行定位和字数统计，补充完整的章节信息
   *
   * @param data - 包含 project_id, file_path, chapters, toc_end_idx
   */
  async enrichChapters(data: {
    project_id: number
    file_path: string
    chapters: any[]
    toc_end_idx: number
  }): Promise<ApiResponse<{
    chapters: any[]
    statistics: {
      total_chapters: number
      total_words: number
      estimated_processing_cost: number
    }
  }>> {
    return apiClient.post('/tender-processing/enrich-chapters', data, {
      timeout: 60000 // 60秒超时
    })
  },

  /**
   * 保存应答文件章节
   */
  async saveResponseFile(projectId: number, chapterIds: string[]): Promise<ApiResponse<{
    file_path: string
    file_url: string
    filename: string
    file_size: number
  }>> {
    return apiClient.post(`/tender-processing/save-response-file/${projectId}`, {
      chapter_ids: chapterIds
    })
  },

  /**
   * 保存技术需求章节
   */
  async saveTechnicalChapters(projectId: number, chapterIds: string[]): Promise<ApiResponse<{
    file_path: string
    file_url: string
    filename: string
    file_size: number
  }>> {
    return apiClient.post(`/tender-processing/save-technical-chapters/${projectId}`, {
      chapter_ids: chapterIds
    })
  },

  /**
   * AI提取基本信息
   */
  async extractBasicInfo(projectId: number): Promise<ApiResponse<{
    project_name?: string
    project_number?: string
    tender_party?: string
    tender_agent?: string
    tender_method?: string
    tender_location?: string
    tender_deadline?: string
    winner_count?: number
    tenderer_contact_person?: string
    tenderer_contact_method?: string
    agency_contact_person?: string
    agency_contact_method?: string
  }>> {
    return apiClient.post(`/tender-processing/extract-basic-info/${projectId}`, {})
  },

  /**
   * AI提取资格要求
   */
  async extractQualifications(projectId: number): Promise<ApiResponse<any>> {
    return apiClient.post(`/tender-processing/extract-qualifications/${projectId}`, {})
  },

  // ==================== 文档融合 ====================

  /**
   * 获取源文档列表（用于文档融合）
   */
  async getSourceDocuments(projectId: number): Promise<ApiResponse<SourceDocuments>> {
    return apiClient.get(`/document-merger/source-documents/${projectId}`)
  },

  /**
   * 启动文档融合任务
   */
  async startDocumentMerge(
    data: DocumentMergeRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/document-merger/merge', data)
  },

  /**
   * 获取文档融合结果
   */
  async getMergeTaskResult(taskId: string): Promise<ApiResponse<MergeTaskResult>> {
    return apiClient.get(`/document-merger/tasks/${taskId}/result`)
  },

  /**
   * 下载融合后的文档
   */
  async downloadMergedDocument(
    taskId: string,
    filename: string,
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    return apiClient.download(
      `/document-merger/tasks/${taskId}/download`,
      filename,
      (event) => {
        if (onProgress && event.total) {
          const progress = Math.round((event.loaded * 100) / event.total)
          onProgress(progress)
        }
      }
    )
  },

  // ==================== HITL工作流 ====================

  /**
   * 获取HITL任务详情
   */
  async getHITLTask(projectId: number): Promise<ApiResponse<any>> {
    return apiClient.get(`/tender-processing/hitl-tasks/${projectId}`)
  },

  /**
   * 更新HITL任务状态
   */
  async updateHITLTask(projectId: number, data: any): Promise<ApiResponse<void>> {
    return apiClient.put(`/tender-processing/hitl-tasks/${projectId}`, data)
  },

  /**
   * 提交HITL审核
   */
  async submitHITLReview(projectId: number, data: any): Promise<ApiResponse<void>> {
    return apiClient.post(`/tender-processing/hitl-tasks/${projectId}/submit`, data)
  },

  // ==================== 统计数据 ====================

  /**
   * 获取工作台全局统计数据
   */
  async getDashboardStatistics(): Promise<ApiResponse<{
    totalProjects: number
    inProgressProjects: number
    wonThisMonth: number
    pendingTasks: number
  }>> {
    return apiClient.get('/tender-management/dashboard-stats')
  },

  /**
   * 获取项目统计数据
   */
  async getProjectStatistics(projectId: number): Promise<ApiResponse<any>> {
    return apiClient.get(`/tender-projects/${projectId}/statistics`)
  },

  // ==================== 提示词配置 ====================

  /**
   * 获取大纲生成提示词配置
   */
  async getOutlineGenerationPrompts(): Promise<ApiResponse<{
    analyze_requirements: string
    generate_outline: string
    generate_response_suggestions: string
    recommend_product_docs: string
  }>> {
    return apiClient.get('/prompts/outline-generation')
  }
}

/**
 * SSE流式处理（用于实时进度更新）
 */
export const tenderSSE = {
  /**
   * 监听文档处理进度
   */
  createProcessingStream(taskId: string): EventSource {
    return new EventSource(`/api/tender-processing/stream/${taskId}`)
  },

  /**
   * 监听文档融合进度
   */
  createMergeStream(taskId: string): EventSource {
    return new EventSource(`/api/document-merger/stream/${taskId}`)
  }
}
