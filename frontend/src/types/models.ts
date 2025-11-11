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
  company_id?: number  // 改为可选，更新时允许不传
  company_name?: string
  status: 'pending' | 'processing' | 'hitl_review' | 'completed' | 'failed' | 'draft' | 'active'
  created_at: string
  updated_at?: string
  deadline?: string
  budget?: number
  description?: string
  authorized_person?: string
  winner?: string
  // 招标信息（用于更新）
  tenderer?: string
  agency?: string
  bidding_method?: string
  bidding_location?: string
  bidding_time?: string
  budget_amount?: number
  // 联系人信息（用于更新）
  business_contact_name?: string
  business_contact_phone?: string
  tenderer_contact_person?: string
  tenderer_contact_method?: string
  agency_contact_person?: string
  agency_contact_method?: string
  authorized_person_name?: string
  authorized_person_id?: string
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
  tenderer?: string  // 别名 tender_unit
  agency?: string  // 别名 tender_agency
  bidding_method?: string  // 招标方式
  bidding_location?: string  // 开标地点
  bidding_time?: string  // 开标时间
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
  tenderer_contact_person?: string  // 招标方联系人
  tenderer_contact_method?: string  // 招标方联系方式
  agency_contact_person?: string  // 代理机构联系人
  agency_contact_method?: string  // 代理机构联系方式
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
  project_id: number
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

/**
 * 案例库主表 (case_studies)
 * 对应数据库: ai_tender_system/database/case_library_schema.sql
 */
export interface Case {
  // 主键和外键
  case_id: number
  company_id: number
  company_name?: string  // 前端显示用（Join查询）
  product_id?: number

  // 基本信息
  case_title: string  // 案例标题/合同名称（统一字段）
  case_number?: string  // 案例编号/合同编号
  customer_name: string  // 甲方客户名称（统一字段）
  industry?: string  // 所属行业

  // 合同信息
  contract_name?: string  // 合同名称（等同于case_title）
  contract_type: '订单' | '合同'  // 合同类型
  final_customer_name?: string  // 最终客户名称（订单类型时填写）
  contract_amount?: string  // 合同金额（支持数字或文字描述，如"100万元"、"百万级"）
  contract_start_date?: string  // 合同开始日期
  contract_end_date?: string  // 合同结束日期
  party_a_customer_name?: string  // 甲方客户名称（等同于customer_name）
  party_b_company_name?: string  // 乙方公司名称

  // 甲方客户详细信息
  party_a_name?: string  // 甲方名称（等同于customer_name）
  party_a_address?: string  // 甲方地址
  party_a_contact_name?: string  // 甲方联系人姓名
  party_a_contact_phone?: string  // 甲方联系电话
  party_a_contact_email?: string  // 甲方联系邮箱

  // 乙方公司详细信息
  party_b_name?: string  // 乙方名称
  party_b_address?: string  // 乙方地址
  party_b_contact_name?: string  // 乙方联系人姓名
  party_b_contact_phone?: string  // 乙方联系电话
  party_b_contact_email?: string  // 乙方联系邮箱

  // 案例状态
  case_status: 'success' | 'in_progress' | 'pending_acceptance'  // 成功/进行中/待验收

  // 时间戳
  created_by?: string
  created_at: string
  updated_at?: string

  // 前端扩展字段（非数据库字段）
  attachments?: CaseAttachment[]  // 关联的附件列表
}

/**
 * 案例附件表 (case_attachments)
 */
export interface CaseAttachment {
  // 主键和外键
  attachment_id: number
  case_id: number

  // 文件信息
  file_name: string  // 存储的文件名
  original_filename: string  // 原始文件名
  file_path: string  // 文件路径
  file_type?: string  // pdf/doc/docx/jpg/png
  file_size?: number  // 文件大小（字节）

  // 附件类型和说明
  attachment_type: 'contract' | 'acceptance' | 'testimony' | 'photo' | 'other'  // 合同/验收证明/客户证明/项目照片/其他
  attachment_description?: string  // 附件说明

  // 时间戳
  uploaded_by?: string
  uploaded_at: string
}

/**
 * 案例表单数据（用于创建/编辑）
 */
export interface CaseFormData {
  company_id: number
  case_title: string
  customer_name: string
  industry?: string
  contract_type: '订单' | '合同'
  final_customer_name?: string
  contract_amount?: string
  contract_start_date?: string
  contract_end_date?: string
  party_a_address?: string
  party_a_contact_name?: string
  party_a_contact_phone?: string
  party_a_contact_email?: string
  party_b_company_name?: string
  party_b_address?: string
  party_b_contact_name?: string
  party_b_contact_phone?: string
  party_b_contact_email?: string
  case_status?: 'success' | 'in_progress' | 'pending_acceptance'
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

export interface UploadUserFile {
  name: string
  url: string
  status: 'success' | 'uploading' | 'failed'
  uid: number
  size?: number
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
