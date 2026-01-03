/**
 * 应答文件自检 API 服务
 */

import { apiClient } from './client'
import type {
  ApiResponse,
  CheckStatusResponse,
  CheckResult,
  HistoryListResponse
} from '@/types/responseCheck'

const BASE_URL = '/response-check'

/**
 * 上传文件并开始检查
 * @param file 文件对象
 * @param model AI模型名称（可选）
 * @param onProgress 上传进度回调
 */
export async function uploadAndCheck(
  file: File,
  model?: string,
  onProgress?: (percent: number) => void
): Promise<ApiResponse<{ task_id: string; status: string; message: string }>> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('filename', file.name)
  if (model) {
    formData.append('model', model)
  }

  return apiClient.upload(`${BASE_URL}/upload`, formData, (progressEvent) => {
    if (onProgress && progressEvent.total) {
      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      onProgress(percent)
    }
  })
}

/**
 * 查询检查状态
 * @param taskId 任务ID
 */
export async function getCheckStatus(
  taskId: string
): Promise<ApiResponse<CheckStatusResponse>> {
  return apiClient.get(`${BASE_URL}/status/${taskId}`)
}

/**
 * 获取检查结果
 * @param taskId 任务ID
 */
export async function getCheckResult(
  taskId: string
): Promise<ApiResponse<CheckResult>> {
  return apiClient.get(`${BASE_URL}/result/${taskId}`)
}

/**
 * 导出Excel报告
 * @param taskId 任务ID
 * @param filename 下载文件名
 */
export async function exportExcel(
  taskId: string,
  filename?: string
): Promise<Blob> {
  return apiClient.download(`${BASE_URL}/export/${taskId}`, filename)
}

/**
 * 获取历史检查记录
 * @param page 页码
 * @param pageSize 每页数量
 */
export async function getHistory(
  page: number = 1,
  pageSize: number = 10
): Promise<ApiResponse<HistoryListResponse>> {
  return apiClient.get(`${BASE_URL}/history`, { page, page_size: pageSize })
}

/**
 * 删除检查记录
 * @param taskId 任务ID
 */
export async function deleteTask(
  taskId: string
): Promise<ApiResponse<{ message: string }>> {
  return apiClient.delete(`${BASE_URL}/${taskId}`)
}
