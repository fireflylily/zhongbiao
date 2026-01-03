/**
 * 应答文件自检相关类型定义
 */

/** 检查状态 */
export type CheckStatusType = '符合' | '不符合' | '无法判断'

/** 任务状态 */
export type TaskStatus = 'pending' | 'parsing' | 'checking' | 'completed' | 'failed'

/** 单条检查项 */
export interface CheckItem {
  item_id: string
  name: string
  status: CheckStatusType
  detail: string
  location: string
  suggestion: string
}

/** 检查类别 */
export interface CheckCategory {
  category_id: string
  category_name: string
  items: CheckItem[]
  pass_count: number
  fail_count: number
  unknown_count: number
  status_icon: string
}

/** 检查统计 */
export interface CheckStatistics {
  total_items: number
  pass_count: number
  fail_count: number
  unknown_count: number
}

/** 检查状态响应 */
export interface CheckStatusResponse {
  task_id: string
  file_name: string
  status: TaskStatus
  progress: number
  current_step: string
  current_category: string
  error_message: string
  categories: CheckCategory[]
  statistics: CheckStatistics
}

/** 检查结果 */
export interface CheckResult {
  task_id: string
  file_name: string
  check_time: string
  categories: CheckCategory[]
  statistics: CheckStatistics
  extracted_info: Record<string, unknown>
  total_pages: number
  analysis_time: number
  model_name: string
}

/** 历史任务项 */
export interface HistoryTask {
  task_id: string
  original_filename: string
  status: TaskStatus
  progress: number
  current_step: string
  total_items: number
  pass_count: number
  fail_count: number
  unknown_count: number
  created_at: string
  completed_at: string
  error_message: string
}

/** 历史列表响应 */
export interface HistoryListResponse {
  tasks: HistoryTask[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/** API通用响应 */
export interface ApiResponse<T = unknown> {
  success: boolean
  message?: string
  data?: T
}
