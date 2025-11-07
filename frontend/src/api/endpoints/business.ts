/**
 * 商务应答API端点
 *
 * 包含商务应答生成、点对点应答、技术方案生成等功能
 */

import { apiClient } from '../client'
import type {
  Chapter,
  Requirement,
  ApiResponse,
  ListApiResponse,
  TaskCreateResponse,
  BusinessResponseRequest,
  BusinessResponseResponse,
  PointToPointRequest,
  PointToPointResponse,
  TechProposalRequest,
  TechProposalResponse
} from '@/types'

/**
 * 商务应答API
 */
export const businessApi = {
  // ==================== 商务应答生成 ====================

  /**
   * 启动商务应答生成任务
   */
  async startBusinessResponse(
    data: BusinessResponseRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/business-response/generate', data)
  },

  /**
   * 启动商务应答生成（SSE流式）
   */
  async startBusinessResponseStream(
    data: BusinessResponseRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/business-response/generate-stream', data)
  },

  /**
   * 获取商务应答结果
   */
  async getBusinessResponseResult(
    taskId: string
  ): Promise<ApiResponse<BusinessResponseResponse>> {
    return apiClient.get(`/business-response/tasks/${taskId}/result`)
  },

  /**
   * 下载商务应答文档
   */
  async downloadBusinessResponse(
    taskId: string,
    filename: string,
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    return apiClient.download(
      `/business-response/tasks/${taskId}/download`,
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
   * 获取商务应答任务状态
   */
  async getBusinessResponseStatus(taskId: string): Promise<ApiResponse<any>> {
    return apiClient.get(`/business-response/tasks/${taskId}/status`)
  },

  // ==================== 点对点应答 ====================

  /**
   * 启动点对点应答生成
   */
  async startPointToPoint(
    data: PointToPointRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/point-to-point/generate', data)
  },

  /**
   * 启动点对点应答生成（SSE流式）
   */
  async startPointToPointStream(
    data: PointToPointRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/point-to-point/generate-stream', data)
  },

  /**
   * 获取点对点应答结果
   */
  async getPointToPointResult(
    taskId: string
  ): Promise<ApiResponse<PointToPointResponse>> {
    return apiClient.get(`/point-to-point/tasks/${taskId}/result`)
  },

  /**
   * 下载点对点应答文档
   */
  async downloadPointToPoint(
    taskId: string,
    filename: string,
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    return apiClient.download(
      `/point-to-point/tasks/${taskId}/download`,
      filename,
      (event) => {
        if (onProgress && event.total) {
          const progress = Math.round((event.loaded * 100) / event.total)
          onProgress(progress)
        }
      }
    )
  },

  // ==================== 技术方案生成 ====================

  /**
   * 启动技术方案生成
   */
  async startTechProposal(
    data: TechProposalRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/tech-proposal/generate', data)
  },

  /**
   * 启动技术方案生成（SSE流式）
   */
  async startTechProposalStream(
    data: TechProposalRequest
  ): Promise<ApiResponse<TaskCreateResponse>> {
    return apiClient.post('/tech-proposal/generate-stream', data)
  },

  /**
   * 获取技术方案结果
   */
  async getTechProposalResult(
    taskId: string
  ): Promise<ApiResponse<TechProposalResponse>> {
    return apiClient.get(`/tech-proposal/tasks/${taskId}/result`)
  },

  /**
   * 下载技术方案文档
   */
  async downloadTechProposal(
    taskId: string,
    filename: string,
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    return apiClient.download(
      `/tech-proposal/tasks/${taskId}/download`,
      filename,
      (event) => {
        if (onProgress && event.total) {
          const progress = Math.round((event.loaded * 100) / event.total)
          onProgress(progress)
        }
      }
    )
  },

  // ==================== 章节管理 ====================

  /**
   * 获取项目章节树
   */
  async getChapterTree(projectId: number): Promise<ApiResponse<Chapter[]>> {
    return apiClient.get(`/projects/${projectId}/chapters`)
  },

  /**
   * 创建章节
   */
  async createChapter(data: {
    project_id: number
    title: string
    level: number
    parent_id?: number
    sort_order: number
  }): Promise<ApiResponse<Chapter>> {
    return apiClient.post('/chapters', data)
  },

  /**
   * 更新章节
   */
  async updateChapter(
    chapterId: number,
    data: Partial<Chapter>
  ): Promise<ApiResponse<Chapter>> {
    return apiClient.put(`/chapters/${chapterId}`, data)
  },

  /**
   * 删除章节
   */
  async deleteChapter(chapterId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/chapters/${chapterId}`)
  },

  /**
   * 批量创建章节
   */
  async batchCreateChapters(
    projectId: number,
    chapters: Array<{
      title: string
      level: number
      parent_id?: number
    }>
  ): Promise<ApiResponse<Chapter[]>> {
    return apiClient.post('/chapters/batch', { project_id: projectId, chapters })
  },

  // ==================== 需求管理 ====================

  /**
   * 获取项目需求列表
   */
  async getRequirements(projectId: number): Promise<ListApiResponse<Requirement>> {
    return apiClient.get(`/projects/${projectId}/requirements`)
  },

  /**
   * 创建需求
   */
  async createRequirement(data: {
    project_id: number
    chapter_id?: number
    content: string
    priority?: 'high' | 'medium' | 'low'
    status?: 'pending' | 'in_progress' | 'completed'
  }): Promise<ApiResponse<Requirement>> {
    return apiClient.post('/requirements', data)
  },

  /**
   * 更新需求
   */
  async updateRequirement(
    requirementId: number,
    data: Partial<Requirement>
  ): Promise<ApiResponse<Requirement>> {
    return apiClient.put(`/requirements/${requirementId}`, data)
  },

  /**
   * 删除需求
   */
  async deleteRequirement(requirementId: number): Promise<ApiResponse<void>> {
    return apiClient.delete(`/requirements/${requirementId}`)
  },

  /**
   * 批量更新需求
   */
  async batchUpdateRequirements(
    requirements: Array<{ id: number; updates: Partial<Requirement> }>
  ): Promise<ApiResponse<void>> {
    return apiClient.post('/requirements/batch-update', { requirements })
  },

  // ==================== AI模型管理 ====================

  /**
   * 获取可用AI模型列表
   */
  async getAvailableModels(): Promise<ListApiResponse<any>> {
    return apiClient.get('/ai-models')
  },

  /**
   * 测试AI模型连接
   */
  async testModelConnection(modelName: string): Promise<ApiResponse<any>> {
    return apiClient.post('/ai-models/test', { model_name: modelName })
  }
}

/**
 * SSE流式处理（用于实时内容生成）
 */
export const businessSSE = {
  /**
   * 监听商务应答生成进度
   */
  createBusinessResponseStream(taskId: string): EventSource {
    return new EventSource(`/api/business-response/stream/${taskId}`)
  },

  /**
   * 监听点对点应答生成进度
   */
  createPointToPointStream(taskId: string): EventSource {
    return new EventSource(`/api/point-to-point/stream/${taskId}`)
  },

  /**
   * 监听技术方案生成进度
   */
  createTechProposalStream(taskId: string): EventSource {
    return new EventSource(`/api/tech-proposal/stream/${taskId}`)
  }
}

/**
 * 旧版商务应答API（直接调用后端处理Word模板）
 */
export const businessLegacyApi = {
  /**
   * 处理商务应答（调用旧版API）
   *
   * 功能：
   * - 在Word模板上填充公司信息
   * - 处理表格
   * - 插入图片（营业执照、资质证书等）
   * - 生成真实的.docx文档
   */
  async processBusinessResponse(data: {
    company_id: number
    project_name: string
    tender_no?: string
    date_text?: string
    hitl_file_path: string
    use_mcp?: boolean
  }): Promise<ApiResponse<{
    success: boolean
    output_file: string
    download_url: string
    stats?: {
      total_replacements?: number
      tables_processed?: number
      cells_filled?: number
      images_inserted?: number
    }
    message: string
  }>> {
    const formData = new FormData()
    formData.append('company_id', data.company_id.toString())
    formData.append('project_name', data.project_name)
    if (data.tender_no) formData.append('tender_no', data.tender_no)
    if (data.date_text) formData.append('date_text', data.date_text)
    formData.append('hitl_file_path', data.hitl_file_path)
    formData.append('use_mcp', data.use_mcp !== false ? 'true' : 'false')

    return apiClient.post('/process-business-response', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}
