/**
 * 用户反馈API接口
 */

import { apiClient } from '../client'

export interface FeedbackSubmitData {
  content: string
  username?: string
  userId?: number
  projectId?: number
  projectName?: string
  companyId?: number
  companyName?: string
  pageRoute?: string
  pageTitle?: string
  feedbackType?: 'bug' | 'suggestion' | 'general'
  priority?: 'low' | 'medium' | 'high'
}

export interface Feedback {
  id: number
  content: string
  username?: string
  user_id?: number
  project_id?: number
  project_name?: string
  company_id?: number
  company_name?: string
  page_route?: string
  page_title?: string
  feedback_type: string
  priority: string
  status: string
  assigned_to?: string
  resolution?: string
  created_at: string
  updated_at: string
  resolved_at?: string
}

export interface FeedbackListParams {
  page?: number
  pageSize?: number
  status?: string
  feedbackType?: string
  priority?: string
  username?: string
  projectId?: number
}

export interface FeedbackListResponse {
  success: boolean
  data: Feedback[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

export interface FeedbackStatsResponse {
  success: boolean
  stats: {
    total: number
    byStatus: Record<string, number>
    byType: Record<string, number>
    byPriority: Record<string, number>
  }
}

/**
 * 提交用户反馈
 */
export function submitFeedback(data: FeedbackSubmitData) {
  return apiClient.post<{
    success: boolean
    feedbackId: number
    message: string
  }>('/api/feedback/submit', data)
}

/**
 * 获取反馈列表
 */
export function getFeedbackList(params?: FeedbackListParams) {
  return apiClient.get<FeedbackListResponse>('/api/feedback/list', { params })
}

/**
 * 获取单个反馈详情
 */
export function getFeedbackDetail(id: number) {
  return apiClient.get<{
    success: boolean
    data: Feedback
  }>(`/api/feedback/${id}`)
}

/**
 * 更新反馈（管理员功能）
 */
export function updateFeedback(
  id: number,
  data: {
    status?: string
    priority?: string
    assignedTo?: string
    resolution?: string
  }
) {
  return apiClient.put<{
    success: boolean
    message: string
  }>(`/api/feedback/${id}`, data)
}

/**
 * 获取反馈统计
 */
export function getFeedbackStats() {
  return apiClient.get<FeedbackStatsResponse>('/api/feedback/stats')
}
