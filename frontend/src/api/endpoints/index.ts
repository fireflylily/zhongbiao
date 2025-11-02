/**
 * API端点统一导出
 *
 * 提供所有API模块的统一访问入口
 */

// 导出所有API模块
export { tenderApi, tenderSSE } from './tender'
export { companyApi } from './company'
export { knowledgeApi } from './knowledge'
export { businessApi, businessSSE } from './business'
export { authApi } from './auth'

// 导出API客户端
export { apiClient, ApiClient, getCsrfToken } from '../client'
export type { ApiClientConfig } from '../client'

// 导出拦截器工具
export { setupInterceptors } from '../interceptors'
