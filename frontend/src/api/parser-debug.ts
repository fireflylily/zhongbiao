/**
 * 目录解析方法对比调试 API
 */

import { apiClient } from './client'

export interface ChapterNode {
  id: string
  level: number
  title: string
  para_start_idx: number
  para_end_idx: number
  word_count: number
  preview_text: string
  auto_selected: boolean
  skip_recommended: boolean
  content_tags?: string[]
  children?: ChapterNode[]
}

export interface ParseMethodResult {
  success: boolean
  method_name: string
  chapters: ChapterNode[]
  statistics?: {
    total_chapters: number
    total_words: number
    toc_items_count?: number
    match_rate?: number
  }
  performance: {
    elapsed: number
    elapsed_formatted: string
  }
  error?: string
}

export interface DocumentInfo {
  filename: string
  total_paragraphs: number
  has_toc: boolean
  toc_items_count: number
  toc_start_idx?: number
  toc_end_idx?: number
  upload_time?: string
}

export interface AccuracyMetrics {
  precision: number
  recall: number
  f1_score: number
  matched_count: number
  detected_count: number
  ground_truth_count: number
  details?: Array<{
    title: string
    status: 'matched' | 'missed' | 'false_positive'
    detected: boolean
  }>
}

export interface MethodAccuracy {
  precision: number
  recall: number
  f1_score: number
}

export interface ParseTestResult {
  success: boolean
  document_id: string
  document_info: DocumentInfo
  results: {
    semantic: ParseMethodResult
    style: ParseMethodResult
    hybrid: ParseMethodResult
    azure?: ParseMethodResult
    docx_native?: ParseMethodResult
    gemini?: ParseMethodResult
  }
  ground_truth?: ChapterNode[]
  accuracy?: {
    semantic: MethodAccuracy
    style: MethodAccuracy
    hybrid?: MethodAccuracy
    azure?: MethodAccuracy
    docx_native?: MethodAccuracy
    gemini?: MethodAccuracy
    best_method: string
    best_f1_score: number
  }
}

export interface HistoryTest {
  document_id: string
  filename: string
  upload_time: string
  has_toc: boolean
  toc_items_count: number
  semantic_chapters_count: number
  style_chapters_count: number
  hybrid_chapters_count: number
  azure_chapters_count: number
  docx_native_chapters_count: number
  gemini_chapters_count: number
  semantic_f1?: number
  style_f1?: number
  hybrid_f1?: number
  azure_f1?: number
  docx_native_f1?: number
  gemini_f1?: number
  best_method?: string
  best_f1_score?: number
  has_ground_truth: boolean
  annotator?: string
}

/**
 * 上传文档并运行所有解析方法
 */
export function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient.post<ParseTestResult>('/parser-debug/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 300000 // 5分钟超时（解析大文档可能需要几分钟）
  })
}

/**
 * 获取测试结果
 */
export function getTestResult(documentId: string) {
  return apiClient.get<ParseTestResult>(`/parser-debug/${documentId}`)
}

/**
 * 保存人工标注的正确答案
 */
export function saveGroundTruth(documentId: string, chapters: ChapterNode[], annotator: string = 'user') {
  return apiClient.post(`/parser-debug/${documentId}/ground-truth`, {
    chapters,
    annotator
  })
}

/**
 * 获取历史测试列表
 */
export function getHistory(params?: { limit?: number; has_ground_truth?: boolean }) {
  return apiClient.get<{ success: boolean; tests: HistoryTest[]; total: number }>('/parser-debug/history', {
    params
  })
}

/**
 * 删除测试记录
 */
export function deleteTest(documentId: string) {
  return apiClient.delete(`/parser-debug/${documentId}/delete`)
}

/**
 * 导出对比报告
 */
export function exportReport(documentId: string) {
  return apiClient.get(`/parser-debug/export/${documentId}`, {
    responseType: 'blob'
  })
}

/**
 * 解析单个方法
 */
export function parseSingleMethod(documentId: string, method: 'toc_exact' | 'azure' | 'docx_native' | 'gemini') {
  return apiClient.post<{ success: boolean; result: ParseMethodResult }>(
    `/parser-debug/parse-single/${documentId}/${method}`,
    {},
    {
      timeout: 300000 // 5分钟超时
    }
  )
}

export const parserDebugApi = {
  uploadDocument,
  getTestResult,
  saveGroundTruth,
  getHistory,
  deleteTest,
  exportReport,
  parseSingleMethod
}
