/**
 * 数据模型类型定义
 *
 * 对应后端数据库模型和业务实体
 */

// ============================================
// 用户相关
// ============================================

export interface User {
  id: number
  username: string
  email?: string
  role: 'admin' | 'user' | 'viewer'
  created_at: string
  last_login?: string
}

// ============================================
// 公司相关
// ============================================

export interface Company {
  id: number
  name: string
  code?: string
  description?: string
  address?: string
  phone?: string
  fax?: string
  postal_code?: string
  contact_person?: string
  website?: string
  created_at: string
  updated_at?: string
}

export interface CompanyQualification {
  id: number
  company_id: number
  type_key: string
  type_name: string
  category: string
  file_path: string
  file_name: string
  file_size: number
  upload_date: string
  expiry_date?: string
  notes?: string
}

export interface QualificationType {
  id: number
  type_key: string
  type_name: string
  category: string
  sort_order: number
  is_required: boolean
  description?: string
}

// ============================================
// 项目相关
// ============================================

export interface Project {
  id: number
  project_name: string
  project_number?: string
  company_id: number
  company_name?: string
  status: 'pending' | 'processing' | 'hitl_review' | 'completed' | 'failed' | 'draft' | 'active'
  created_at: string
  updated_at?: string
  deadline?: string
  budget?: number
  description?: string
  authorized_person?: string
  winner?: string
}

export interface ProjectDetail extends Project {
  // 别名字段 (用于兼容前端组件)
  name?: string  // 别名 project_name
  number?: string  // 别名 project_number

  // 文档路径
  tender_file_path?: string
  tender_document_path?: string
  business_doc_path?: string
  p2p_doc_path?: string
  tech_doc_path?: string

  // 招标信息
  tender_unit?: string
  tender_agency?: string
  budget_amount?: number
  project_type?: string
  registration_deadline?: string
  bid_deadline?: string
  bid_opening_time?: string
  bid_opening_location?: string

  // 联系人信息
  project_manager_name?: string
  project_manager_phone?: string
  tech_lead_name?: string
  tech_lead_phone?: string
  business_contact_name?: string
  business_contact_phone?: string
  authorized_person_name?: string
  authorized_person_id?: string

  // AI处理数据
  step1_data?: any  // 包含章节、文件路径等AI提取的数据

  // 章节和需求
  chapters?: Chapter[]
  requirements?: Requirement[]
}

// ============================================
// 章节相关
// ============================================

export interface Chapter {
  id: number
  project_id: number
  parent_id?: number
  level: number
  number: string
  title: string
  content: string
  word_count: number
  sort_order: number
  is_selected: boolean
  children?: Chapter[]
}

export interface ChapterNode extends Chapter {
  children: ChapterNode[]
  selected: boolean
  expanded: boolean
}

// ============================================
// 需求相关
// ============================================

export interface Requirement {
  id: number
  project_id: number
  hitl_task_id?: string
  chapter_id?: number
  requirement_type: string
  requirement_text: string
  response_text?: string
  status: 'pending' | 'matched' | 'manual' | 'completed'
  confidence_score?: number
  created_at: string
  updated_at?: string
}

// ============================================
// 文档相关
// ============================================

export interface Document {
  id: number
  name: string
  file_path: string
  file_type: string
  file_size: number
  category: 'tender' | 'business' | 'technical' | 'p2p' | 'other'
  project_id?: number
  company_id?: number
  uploaded_by?: number
  upload_date: string
  tags?: string[]
  description?: string
}

export interface DocumentChunk {
  id: number
  hitl_task_id: string
  chunk_index: number
  chunk_text: string
  embedding_vector?: number[]
  metadata?: Record<string, any>
}

// ============================================
// 知识库相关
// ============================================

export interface KnowledgeDocument {
  id: number
  title: string
  content: string
  file_path?: string
  file_type?: string
  category_id?: number
  category_name?: string
  tags?: string[]
  created_at: string
  updated_at?: string
  view_count?: number
  download_count?: number
}

export interface KnowledgeCategory {
  id: number
  name: string
  parent_id?: number
  description?: string
  sort_order: number
  doc_count: number
  children?: KnowledgeCategory[]
}

// ============================================
// 案例库相关
// ============================================

export interface Case {
  id: number
  title: string
  company_id: number
  company_name?: string
  project_name: string
  project_date: string
  project_amount?: number
  description: string
  success_factors?: string
  technologies?: string[]
  file_path?: string
  created_at: string
  updated_at?: string
  tags?: string[]
}

// ============================================
// 简历库相关
// ============================================

export interface Resume {
  id: number
  name: string
  gender?: 'male' | 'female'
  birth_date?: string
  phone?: string
  email?: string
  education: string
  major?: string
  title?: string
  company?: string
  years_experience?: number
  skills?: string[]
  certifications?: string[]
  project_experience?: ProjectExperience[]
  file_path?: string
  created_at: string
  updated_at?: string
}

export interface ProjectExperience {
  id: number
  resume_id: number
  project_name: string
  role: string
  start_date: string
  end_date?: string
  description: string
  responsibilities?: string
  achievements?: string
}

// ============================================
// AI模型相关
// ============================================

export interface AIModel {
  name: string
  display_name: string
  provider: string
  status: 'available' | 'no_api_key' | 'error'
  status_message: string
  description?: string
  max_tokens?: number
  supports_streaming?: boolean
}

// Navbar组件使用的AI模型选项（扩展版本）
export interface AIModelOption {
  value: string
  label: string
  icon?: string
  recommended?: boolean
  provider: 'unicom' | 'openai' | 'other'
}

// ============================================
// 任务相关
// ============================================

export interface Task {
  id: string
  task_type: 'tender_processing' | 'business_response' | 'p2p_response' | 'tech_proposal' | 'document_merge'
  project_id?: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
  result?: any
  error?: string
  created_at: string
  updated_at?: string
  completed_at?: string
}

export interface HITLTask {
  id: string
  project_id: number
  company_id: number
  status: 'step1' | 'step2' | 'step3' | 'completed'
  current_step: number
  tender_file_path?: string
  technical_file_path?: string
  business_file_path?: string
  created_at: string
  updated_at?: string
}

// ============================================
// 文档融合相关
// ============================================

export interface SourceDocuments {
  project_id: number
  project_name: string
  company_id: number
  company_name: string
  business_doc_path: string | null
  p2p_doc_path: string | null
  tech_doc_path: string | null
  business_doc_exists: boolean
  p2p_doc_exists: boolean
  tech_doc_exists: boolean
}

export interface MergeTaskResult {
  task_id: string
  status: 'processing' | 'completed' | 'failed'
  progress: number
  merged_file_path?: string
  index_file_path?: string
  error?: string
}

// ============================================
// 通用类型
// ============================================

export interface FileInfo {
  fileName: string
  filePath: string
  fileUrl?: string
  fileSize?: number
  uploadDate?: string
}

export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
  children?: SelectOption[]
}

export interface TreeNode {
  id: string | number
  label: string
  children?: TreeNode[]
  disabled?: boolean
  [key: string]: any
}

// ============================================
// 分页相关
// ============================================

export interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface PaginatedData<T> {
  items: T[]
  pagination: Pagination
}

// ============================================
// 统计数据
// ============================================

export interface Statistics {
  total_projects: number
  pending_projects: number
  completed_projects: number
  total_companies: number
  total_documents: number
  total_cases: number
  total_resumes: number
}

// ============================================
// 资格要求相关
// ============================================

// 资质证书要求
export interface CertificationRequirement {
  name: string
  level?: string
  note: string
  required: boolean
  detail?: string
}

// 业绩要求
export interface PerformanceRequirement {
  description: string
  detail: string
  amount?: number
  time_range?: string
  count?: number
  required: boolean
}

// 人员配置要求
export interface PersonnelRequirement {
  position: string
  detail: string
  count?: number
  qualification?: string
  experience?: string
  required: boolean
}

// 财务要求
export interface FinancialRequirement {
  description: string
  registered_capital?: number
  annual_revenue?: number
  total_assets?: number
  net_assets?: number
  bank_credit?: boolean
}

// 资格要求汇总
export interface QualificationsData {
  certifications: CertificationRequirement[]
  performance: PerformanceRequirement[]
  personnel: PersonnelRequirement[]
  financial: FinancialRequirement | null
}

// 后端存储的原始格式（tender_requirements表）
export interface RawQualificationItem {
  requirement_id: number
  constraint_type: 'mandatory' | 'optional' | 'scoring'
  detail: string
  summary: string
  source_location?: string
  priority?: 'high' | 'medium' | 'low'
  extraction_confidence?: number
  is_verified?: boolean
  created_at?: string
}
