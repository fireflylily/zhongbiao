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
    name: string
    project_number: string
    company_id: number
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

    return apiClient.upload('/upload/tender-document', formData, (event) => {
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

    return apiClient.upload('/upload/business-template', formData, (event) => {
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

    return apiClient.upload('/upload/technical-template', formData, (event) => {
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
  async getHITLTask(hitlTaskId: string): Promise<ApiResponse<any>> {
    return apiClient.get(`/hitl/${hitlTaskId}`)
  },

  /**
   * 更新HITL任务状态
   */
  async updateHITLTask(hitlTaskId: string, data: any): Promise<ApiResponse<void>> {
    return apiClient.put(`/hitl/${hitlTaskId}`, data)
  },

  /**
   * 提交HITL审核
   */
  async submitHITLReview(hitlTaskId: string, data: any): Promise<ApiResponse<void>> {
    return apiClient.post(`/hitl/${hitlTaskId}/submit`, data)
  },

  // ==================== 统计数据 ====================

  /**
   * 获取项目统计数据
   */
  async getProjectStatistics(projectId: number): Promise<ApiResponse<any>> {
    return apiClient.get(`/tender-projects/${projectId}/statistics`)
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
