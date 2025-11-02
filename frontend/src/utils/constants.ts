/**
 * 常量定义
 *
 * 项目中使用的各种常量：
 * - API常量
 * - 业务常量
 * - 文件常量
 * - 状态常量
 * - 权限常量
 */

// ============ API常量 ============

/**
 * HTTP状态码
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504
} as const

/**
 * 请求超时时间（毫秒）
 */
export const REQUEST_TIMEOUT = {
  DEFAULT: 30000, // 30秒
  UPLOAD: 300000, // 5分钟
  DOWNLOAD: 300000, // 5分钟
  LONG: 60000 // 1分钟
} as const

/**
 * API响应消息
 */
export const API_MESSAGE = {
  SUCCESS: '操作成功',
  FAILURE: '操作失败',
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT: '请求超时，请稍后重试',
  UNAUTHORIZED: '未授权，请重新登录',
  FORBIDDEN: '无权限访问',
  NOT_FOUND: '请求的资源不存在',
  SERVER_ERROR: '服务器内部错误',
  UNKNOWN_ERROR: '未知错误'
} as const

// ============ 文件常量 ============

/**
 * 文件类型
 */
export const FILE_TYPES = {
  // 文档
  DOCUMENT: {
    WORD: ['.doc', '.docx'],
    EXCEL: ['.xls', '.xlsx'],
    PDF: ['.pdf'],
    TEXT: ['.txt'],
    ALL: ['.doc', '.docx', '.xls', '.xlsx', '.pdf', '.txt']
  },
  // 图片
  IMAGE: {
    JPEG: ['.jpg', '.jpeg'],
    PNG: ['.png'],
    GIF: ['.gif'],
    BMP: ['.bmp'],
    SVG: ['.svg'],
    ALL: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
  },
  // 压缩包
  ARCHIVE: {
    ZIP: ['.zip'],
    RAR: ['.rar'],
    TAR: ['.tar', '.tar.gz', '.tgz'],
    SEVEN_ZIP: ['.7z'],
    ALL: ['.zip', '.rar', '.tar', '.tar.gz', '.tgz', '.7z']
  }
} as const

/**
 * 文件大小限制（字节）
 */
export const FILE_SIZE_LIMIT = {
  IMAGE: 10 * 1024 * 1024, // 10MB
  DOCUMENT: 50 * 1024 * 1024, // 50MB
  ATTACHMENT: 100 * 1024 * 1024, // 100MB
  DEFAULT: 20 * 1024 * 1024 // 20MB
} as const

/**
 * MIME类型
 */
export const MIME_TYPES = {
  // 文档
  DOC: 'application/msword',
  DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  XLS: 'application/vnd.ms-excel',
  XLSX: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  PDF: 'application/pdf',
  TXT: 'text/plain',
  // 图片
  JPEG: 'image/jpeg',
  PNG: 'image/png',
  GIF: 'image/gif',
  BMP: 'image/bmp',
  SVG: 'image/svg+xml',
  // 压缩包
  ZIP: 'application/zip',
  RAR: 'application/x-rar-compressed',
  // JSON
  JSON: 'application/json'
} as const

// ============ 业务常量 ============

/**
 * 项目状态
 */
export const PROJECT_STATUS = {
  DRAFT: 'draft', // 草稿
  PROCESSING: 'processing', // 处理中
  PENDING: 'pending', // 待审核
  APPROVED: 'approved', // 已通过
  REJECTED: 'rejected', // 已拒绝
  COMPLETED: 'completed', // 已完成
  ARCHIVED: 'archived' // 已归档
} as const

/**
 * 项目状态标签
 */
export const PROJECT_STATUS_LABEL = {
  [PROJECT_STATUS.DRAFT]: '草稿',
  [PROJECT_STATUS.PROCESSING]: '处理中',
  [PROJECT_STATUS.PENDING]: '待审核',
  [PROJECT_STATUS.APPROVED]: '已通过',
  [PROJECT_STATUS.REJECTED]: '已拒绝',
  [PROJECT_STATUS.COMPLETED]: '已完成',
  [PROJECT_STATUS.ARCHIVED]: '已归档'
} as const

/**
 * 项目状态颜色
 */
export const PROJECT_STATUS_COLOR = {
  [PROJECT_STATUS.DRAFT]: '#909399',
  [PROJECT_STATUS.PROCESSING]: '#409EFF',
  [PROJECT_STATUS.PENDING]: '#E6A23C',
  [PROJECT_STATUS.APPROVED]: '#67C23A',
  [PROJECT_STATUS.REJECTED]: '#F56C6C',
  [PROJECT_STATUS.COMPLETED]: '#67C23A',
  [PROJECT_STATUS.ARCHIVED]: '#909399'
} as const

/**
 * 任务状态
 */
export const TASK_STATUS = {
  PENDING: 'pending', // 等待中
  RUNNING: 'running', // 运行中
  SUCCESS: 'success', // 成功
  FAILED: 'failed', // 失败
  CANCELLED: 'cancelled' // 已取消
} as const

/**
 * 任务状态标签
 */
export const TASK_STATUS_LABEL = {
  [TASK_STATUS.PENDING]: '等待中',
  [TASK_STATUS.RUNNING]: '运行中',
  [TASK_STATUS.SUCCESS]: '成功',
  [TASK_STATUS.FAILED]: '失败',
  [TASK_STATUS.CANCELLED]: '已取消'
} as const

/**
 * 文档类型
 */
export const DOCUMENT_TYPE = {
  TENDER: 'tender', // 招标文档
  BUSINESS_TEMPLATE: 'business_template', // 商务应答模板
  TECHNICAL_TEMPLATE: 'technical_template', // 技术方案模板
  BUSINESS_RESPONSE: 'business_response', // 商务应答结果
  TECHNICAL_RESPONSE: 'technical_response', // 技术方案结果
  POINT_TO_POINT: 'point_to_point', // 点对点应答
  MERGED: 'merged' // 融合文档
} as const

/**
 * AI模型类型
 */
export const AI_MODEL = {
  GPT_4O_MINI: 'shihuang-gpt4o-mini',
  GPT_4: 'shihuang-gpt4',
  DEEPSEEK_V3: 'yuanjing-deepseek-v3',
  QWEN_235B: 'yuanjing-qwen-235b'
} as const

/**
 * AI模型标签
 */
export const AI_MODEL_LABEL = {
  [AI_MODEL.GPT_4O_MINI]: 'GPT-4o Mini（快速）',
  [AI_MODEL.GPT_4]: 'GPT-4（标准）',
  [AI_MODEL.DEEPSEEK_V3]: 'DeepSeek V3（经济）',
  [AI_MODEL.QWEN_235B]: 'Qwen 235B（大模型）'
} as const

/**
 * 用户角色
 */
export const USER_ROLE = {
  ADMIN: 'admin', // 管理员
  USER: 'user', // 普通用户
  GUEST: 'guest' // 访客
} as const

/**
 * 用户角色标签
 */
export const USER_ROLE_LABEL = {
  [USER_ROLE.ADMIN]: '管理员',
  [USER_ROLE.USER]: '普通用户',
  [USER_ROLE.GUEST]: '访客'
} as const

/**
 * 权限列表
 */
export const PERMISSIONS = {
  // 项目权限
  PROJECT_VIEW: 'project:view',
  PROJECT_CREATE: 'project:create',
  PROJECT_EDIT: 'project:edit',
  PROJECT_DELETE: 'project:delete',
  // 文档权限
  DOCUMENT_UPLOAD: 'document:upload',
  DOCUMENT_DOWNLOAD: 'document:download',
  DOCUMENT_DELETE: 'document:delete',
  // 知识库权限
  KNOWLEDGE_VIEW: 'knowledge:view',
  KNOWLEDGE_EDIT: 'knowledge:edit',
  // 系统权限
  SYSTEM_SETTINGS: 'system:settings',
  USER_MANAGE: 'user:manage'
} as const

// ============ UI常量 ============

/**
 * 分页配置
 */
export const PAGINATION = {
  PAGE_SIZE: 20, // 默认每页条数
  PAGE_SIZES: [10, 20, 50, 100], // 可选每页条数
  LAYOUT: 'total, sizes, prev, pager, next, jumper' // 分页布局
} as const

/**
 * 表格配置
 */
export const TABLE = {
  STRIPE: true, // 斑马纹
  BORDER: true, // 边框
  SIZE: 'default', // 尺寸
  HEIGHT: null // 高度
} as const

/**
 * 消息提示持续时间（毫秒）
 */
export const MESSAGE_DURATION = {
  SUCCESS: 3000,
  WARNING: 3000,
  ERROR: 5000,
  INFO: 3000
} as const

/**
 * 主题颜色
 */
export const THEME_COLORS = {
  PRIMARY: '#409EFF',
  SUCCESS: '#67C23A',
  WARNING: '#E6A23C',
  DANGER: '#F56C6C',
  INFO: '#909399'
} as const

// ============ 存储键名 ============

/**
 * LocalStorage键名
 */
export const STORAGE_KEY = {
  TOKEN: 'auth_token',
  USER_INFO: 'user_info',
  REMEMBER_ME: 'remember_me',
  COMPANY_ID: 'current_company_id',
  LANGUAGE: 'language',
  THEME: 'theme'
} as const

// ============ 正则表达式 ============

/**
 * 常用正则表达式
 */
export const REGEX = {
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-Z]{2,}$/,
  PHONE: /^1[3-9]\d{9}$/,
  ID_CARD: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
  URL: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,20}$/
} as const

// ============ 日期格式 ============

/**
 * 日期格式模板
 */
export const DATE_FORMAT = {
  DATE: 'YYYY-MM-DD',
  DATETIME: 'YYYY-MM-DD HH:mm:ss',
  TIME: 'HH:mm:ss',
  MONTH: 'YYYY-MM',
  YEAR: 'YYYY',
  CHINESE_DATE: 'YYYY年MM月DD日',
  CHINESE_DATETIME: 'YYYY年MM月DD日 HH时mm分ss秒'
} as const

// ============ 其他常量 ============

/**
 * 默认头像
 */
export const DEFAULT_AVATAR = '/static/images/default-avatar.png'

/**
 * 空值占位符
 */
export const EMPTY_PLACEHOLDER = '-'

/**
 * 加载文本
 */
export const LOADING_TEXT = {
  DEFAULT: '加载中...',
  UPLOADING: '上传中...',
  PROCESSING: '处理中...',
  DOWNLOADING: '下载中...',
  SAVING: '保存中...',
  DELETING: '删除中...'
} as const

/**
 * 确认对话框文本
 */
export const CONFIRM_TEXT = {
  DELETE: '确定要删除吗？',
  CANCEL: '确定要取消吗？',
  SUBMIT: '确定要提交吗？',
  RESET: '确定要重置吗？',
  LOGOUT: '确定要退出登录吗？'
} as const
