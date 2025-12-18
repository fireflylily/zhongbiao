/**
 * 自动化测试运行器 API
 */

import { apiClient } from './client'

export interface TestTask {
  task_id: string
  test_type: 'unit' | 'integration' | 'all'
  coverage: boolean
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_time: string
  start_time?: string
  end_time?: string
  result?: TestResult
  logs?: string[]
  error?: string
}

export interface TestResult {
  return_code: number
  passed: boolean
  output: string
  total: number
  passed: number
  failed: number
  skipped: number
  errors: number
  duration: number
}

export interface CoverageData {
  total_statements: number
  covered_statements: number
  missing_statements: number
  coverage_percent: number
  files: CoverageFile[]
  generated_at: string
}

export interface CoverageFile {
  file: string
  statements: number
  missing: number
  covered: number
  coverage: number
}

export interface QuickInfo {
  total_tests: number
  test_files: number
  coverage_percent: number
  last_run?: string
  test_dir: string
}

export interface TestItem {
  id: string
  name: string
  file: string
  full_path: string
  importance?: string
  is_directory?: boolean
}

export interface TestSuite {
  name: string
  description: string
  tests: TestItem[]
}

export interface Checklist {
  core_tests: {
    name: string
    description: string
    tests: TestItem[]
  }
  test_suites: {
    [key: string]: TestSuite
  }
}

export interface TestStatus {
  available: boolean
  status: 'unknown' | 'passed' | 'failed'
  last_run: string | null
}

/**
 * 测试运行器 API
 */
export const testRunnerApi = {
  /**
   * 运行测试
   */
  runTests(testType: 'unit' | 'integration' | 'all' = 'unit', coverage: boolean = true, verbose: boolean = true) {
    return apiClient.post<{ success: boolean; task_id: string; message: string }>('/test/run', {
      test_type: testType,
      coverage,
      verbose
    })
  },

  /**
   * 获取测试任务状态
   */
  getTestStatus(taskId: string) {
    return apiClient.get<{ success: boolean; task: TestTask }>(`/test/status/${taskId}`)
  },

  /**
   * 获取覆盖率数据
   */
  getCoverageData() {
    return apiClient.get<{ success: boolean; coverage: CoverageData }>('/test/coverage')
  },

  /**
   * 获取测试历史
   */
  getTestHistory(limit: number = 20) {
    return apiClient.get<{ success: boolean; history: TestTask[]; total: number }>('/test/history', {
      params: { limit }
    })
  },

  /**
   * 清除测试历史
   */
  clearHistory() {
    return apiClient.post<{ success: boolean; message: string }>('/test/clear-history')
  },

  /**
   * 获取快速信息
   */
  getQuickInfo() {
    return apiClient.get<{ success: boolean; info: QuickInfo }>('/test/quick-info')
  },

  /**
   * 获取测试清单
   */
  getChecklist() {
    return apiClient.get<{
      success: boolean
      checklist: Checklist
      total_core_tests: number
      total_suites: number
    }>('/testing/checklist')
  },

  /**
   * 获取测试清单状态
   */
  getChecklistStatus() {
    return apiClient.get<{
      success: boolean
      test_status: Record<string, TestStatus>
      total_tests: number
      available_tests: number
      last_run_time: string | null
    }>('/testing/checklist/status')
  },

  /**
   * 运行单个测试
   */
  runSingleTest(testPath: string) {
    return apiClient.post<{
      success: boolean
      test_path: string
      passed: boolean
      failed: boolean
      output: string
      return_code: number
    }>('/testing/run-single', {
      test_path: testPath
    })
  }
}
