/**
 * API响应类型定义
 *
 * 统一的API响应格式和相关类型
 */

import type { Pagination, PaginatedData } from './models'

// ============================================
// 通用API响应
// ============================================

/**
 * 标准API响应格式
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  code?: number
}

/**
 * 分页API响应格式
 */
export interface PaginatedApiResponse<T = any> extends ApiResponse {
  data: PaginatedData<T>
}

/**
 * 列表API响应格式（不分页）
 */
export interface ListApiResponse<T = any> extends ApiResponse {
  data: T[]
  count?: number
}

// ============================================
// 请求参数类型
// ============================================

/**
 * 分页请求参数
 */
export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

/**
 * 搜索请求参数
 */
export interface SearchParams extends PaginationParams {
  keyword?: string
  category?: string
  tags?: string[]
  date_from?: string
  date_to?: string
}

/**
 * 过滤请求参数
 */
export interface FilterParams {
  [key: string]: string | number | boolean | undefined | null
}

// ============================================
// 文件上传相关
// ============================================

/**
 * 文件上传响应
 */
export interface UploadResponse {
  file_name: string
  file_path: string
  file_url: string
  file_size: number
  file_type: string
  upload_date: string
}

/**
 * 批量上传响应
 */
export interface BatchUploadResponse {
  success_count: number
  failed_count: number
  files: UploadResponse[]
  errors?: Array<{
    file_name: string
    error: string
  }>
}

// ============================================
// 任务相关
// ============================================

/**
 * 任务创建响应
 */
export interface TaskCreateResponse {
  task_id: string
  message: string
  status: 'started' | 'queued'
}

/**
 * 任务状态响应
 */
export interface TaskStatusResponse {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
  result?: any
  error?: string
  created_at: string
  updated_at?: string
  completed_at?: string
}

/**
 * SSE事件数据
 */
export interface SSEEvent<T = any> {
  event?: string
  data: T
}

/**
 * SSE进度事件
 */
export interface SSEProgressEvent {
  status: 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
  current_step?: string
  total_steps?: number
  result?: any
  error?: string
}

// ============================================
// 投标处理相关
// ============================================

/**
 * 投标处理请求
 */
export interface TenderProcessingRequest {
  project_id: number
  company_id: number
  tender_file_path?: string
  ai_model?: string
  processing_options?: {
    extract_requirements?: boolean
    generate_outline?: boolean
    match_qualifications?: boolean
  }
}

/**
 * 投标处理响应
 */
export interface TenderProcessingResponse extends TaskCreateResponse {
  project_id: number
}

// ============================================
// 商务应答相关
// ============================================

/**
 * 商务应答生成请求
 */
export interface BusinessResponseRequest {
  project_id: number
  company_id: number
  template_style?: 'business_style' | 'standard_style'
  ai_model?: string
  selected_chapters?: number[]
}

/**
 * 商务应答生成响应
 */
export interface BusinessResponseResponse extends TaskCreateResponse {
  file_path?: string
  file_url?: string
}

// ============================================
// 点对点应答相关
// ============================================

/**
 * 点对点应答请求
 */
export interface PointToPointRequest {
  project_id: number
  company_id: number
  technical_file_path?: string
  ai_model?: string
  requirements?: Array<{
    id: number
    question: string
    response?: string
  }>
}

/**
 * 点对点应答响应
 */
export interface PointToPointResponse extends TaskCreateResponse {
  file_path?: string
  file_url?: string
  matched_count?: number
  total_count?: number
}

// ============================================
// 技术方案相关
// ============================================

/**
 * 技术方案生成请求
 */
export interface TechProposalRequest {
  project_id: number
  company_id: number
  technical_file_path?: string
  ai_model?: string
  outline?: any
  product_selection?: any
}

/**
 * 技术方案生成响应
 */
export interface TechProposalResponse extends TaskCreateResponse {
  file_path?: string
  file_url?: string
  outline?: any
}

// ============================================
// 文档融合相关
// ============================================

/**
 * 文档融合请求
 */
export interface DocumentMergeRequest {
  project_id: number
  business_doc_path: string | null
  p2p_doc_path: string | null
  tech_doc_path: string | null
  style_option: 'business_style' | 'standard_style'
}

/**
 * 文档融合响应
 */
export interface DocumentMergeResponse extends TaskCreateResponse {
  merged_file_path?: string
  index_file_path?: string
}

// ============================================
// 知识库相关
// ============================================

/**
 * 知识库搜索请求
 */
export interface KnowledgeSearchRequest extends SearchParams {
  query: string
  category_id?: number
  use_vector_search?: boolean
  top_k?: number
}

/**
 * 知识库搜索响应
 */
export interface KnowledgeSearchResponse {
  results: Array<{
    id: number
    title: string
    content: string
    relevance_score: number
    category_name?: string
    file_path?: string
  }>
  total: number
  search_time: number
}

/**
 * RAG检索请求
 */
export interface RAGRetrievalRequest {
  query: string
  top_k?: number
  filters?: FilterParams
}

/**
 * RAG检索响应
 */
export interface RAGRetrievalResponse {
  chunks: Array<{
    chunk_id: number
    chunk_text: string
    relevance_score: number
    metadata?: Record<string, any>
  }>
  total: number
}

// ============================================
// 统计数据相关
// ============================================

/**
 * 统计数据请求
 */
export interface StatisticsRequest {
  start_date?: string
  end_date?: string
  company_id?: number
  project_id?: number
}

/**
 * 统计数据响应
 */
export interface StatisticsResponse {
  total_projects: number
  pending_projects: number
  completed_projects: number
  success_rate: number
  avg_processing_time: number
  recent_activities: Array<{
    type: string
    description: string
    timestamp: string
  }>
}

// ============================================
// 错误响应
// ============================================

/**
 * API错误响应
 */
export interface ApiError {
  code: string
  message: string
  details?: any
  timestamp?: string
}

/**
 * 验证错误
 */
export interface ValidationError {
  field: string
  message: string
  value?: any
}

/**
 * 验证错误响应
 */
export interface ValidationErrorResponse extends ApiError {
  errors: ValidationError[]
}

// ============================================
// 批量操作
// ============================================

/**
 * 批量操作请求
 */
export interface BatchOperationRequest<T = any> {
  operation: 'create' | 'update' | 'delete'
  items: T[]
}

/**
 * 批量操作响应
 */
export interface BatchOperationResponse {
  success_count: number
  failed_count: number
  results: Array<{
    index: number
    success: boolean
    data?: any
    error?: string
  }>
}

// ============================================
// 导出相关
// ============================================

/**
 * 导出请求
 */
export interface ExportRequest {
  format: 'excel' | 'pdf' | 'word' | 'csv'
  filters?: FilterParams
  fields?: string[]
}

/**
 * 导出响应
 */
export interface ExportResponse {
  file_url: string
  file_name: string
  file_size: number
  expires_at: string
}

// ============================================
// WebSocket消息
// ============================================

/**
 * WebSocket消息
 */
export interface WSMessage<T = any> {
  type: string
  data: T
  timestamp: string
}

/**
 * WebSocket通知
 */
export interface WSNotification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  read: boolean
}
