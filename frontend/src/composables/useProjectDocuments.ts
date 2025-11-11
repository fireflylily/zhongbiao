/**
 * Project Documents Management Composable
 * Unified logic for loading and managing project documents across business pages
 *
 * 用于商务应答、点对点应答、技术方案三个页面的项目和文档管理
 */

import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { tenderApi } from '@/api/endpoints/tender'
import { useProjectStore } from '@/stores/project'
import type { Project, ProjectDetail, UploadUserFile } from '@/types'

/**
 * 项目文档集合
 */
export interface ProjectDocuments {
  tenderFile: UploadUserFile | null          // 招标文档
  templateFile: UploadUserFile | null        // 应答模板
  technicalFile: UploadUserFile | null       // 技术需求文档
  businessResponseFile: any | null           // 历史商务应答文件
  p2pResponseFile: any | null                // 历史点对点应答文件
  techProposalFile: any | null               // 历史技术方案文件
}

/**
 * 项目切换回调函数
 */
export interface ProjectChangeCallbacks {
  onClear?: () => void                       // 清空回调
  onDocumentsLoaded?: (docs: ProjectDocuments) => void  // 文档加载完成回调
}

/**
 * useProjectDocuments Composable
 */
export function useProjectDocuments() {
  const projectStore = useProjectStore()

  // ============================================
  // 状态管理
  // ============================================

  const projects = ref<Project[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentDocuments = ref<ProjectDocuments>({
    tenderFile: null,
    templateFile: null,
    technicalFile: null,
    businessResponseFile: null,
    p2pResponseFile: null,
    techProposalFile: null
  })

  // ============================================
  // 计算属性
  // ============================================

  const selectedProject = computed(() =>
    projects.value.find(p => p.id === projectStore.projectId)
  )

  const hasProjects = computed(() => projects.value.length > 0)

  const hasTenderFile = computed(() => currentDocuments.value.tenderFile !== null)

  const hasTemplateFile = computed(() => currentDocuments.value.templateFile !== null)

  const hasTechnicalFile = computed(() => currentDocuments.value.technicalFile !== null)

  // ============================================
  // 核心函数：加载项目列表
  // ============================================

  /**
   * 加载项目列表
   * @param filters 可选的过滤条件
   */
  const loadProjects = async (filters?: { status?: string }) => {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.getProjects({
        page: 1,
        page_size: 100,
        ...filters
      })

      projects.value = response.data?.items || []

      if (projects.value.length === 0) {
        ElMessage.warning('暂无项目数据')
      }
    } catch (err) {
      error.value = '加载项目列表失败'
      ElMessage.error(error.value)
      console.error('Load projects error:', err)
    } finally {
      loading.value = false
    }
  }

  // ============================================
  // 核心函数：项目切换处理
  // ============================================

  /**
   * 处理项目切换
   * @param projectId 项目ID
   * @param callbacks 回调函数
   */
  const handleProjectChange = async (
    projectId: number | null,
    callbacks?: ProjectChangeCallbacks
  ) => {
    // 清空当前文档状态
    clearDocuments()

    // 执行自定义清空回调
    if (callbacks?.onClear) {
      callbacks.onClear()
    }

    // 如果选择了项目，加载项目文档
    if (projectId) {
      // 🔧 修复：获取完整的ProjectDetail（而不是简化的Project）
      // 这样才能确保 tender_document_path 等字段存在，悬浮按钮才能正常显示
      try {
        const response = await tenderApi.getProject(projectId)
        if (response.data) {
          // 更新Store中的当前项目（使用完整数据）
          projectStore.setCurrentProject(response.data)
        }
      } catch (err) {
        console.error('获取项目详情失败:', err)
        ElMessage.error('获取项目详情失败')
      }

      // 加载项目文档
      await loadProjectDocuments(projectId, callbacks)
    } else {
      // 清空Store中的项目
      projectStore.clearCurrentProject()
    }
  }

  // ============================================
  // 核心函数：加载项目文档
  // ============================================

  /**
   * 加载项目相关文档
   * @param projectId 项目ID
   * @param callbacks 回调函数
   */
  const loadProjectDocuments = async (
    projectId: number,
    callbacks?: ProjectChangeCallbacks
  ) => {
    loading.value = true

    try {
      const response = await tenderApi.getProject(projectId)
      const projectData: ProjectDetail = response.data

      if (!projectData) {
        ElMessage.warning('未找到项目数据')
        return
      }

      const step1Data = projectData.step1_data
      const docs: ProjectDocuments = {
        tenderFile: null,
        templateFile: null,
        technicalFile: null,
        businessResponseFile: null,
        p2pResponseFile: null,
        techProposalFile: null
      }

      // ============================================
      // 1. 提取招标文档
      // ============================================
      if (step1Data?.file_path) {
        const fileName = step1Data.file_name || step1Data.file_path.split('/').pop() || '招标文档'
        const fileExt = fileName.split('.').pop()?.toLowerCase() || 'doc'
        const isWordDoc = ['doc', 'docx'].includes(fileExt)

        docs.tenderFile = {
          name: step1Data.file_name || '招标文档',
          url: step1Data.file_path,
          status: 'success',
          uid: Date.now() + Math.random(),
          size: step1Data.file_size || 0
        }

        console.log(`✅ 招标文档: ${fileName} (${isWordDoc ? 'Word' : fileExt})`)
      }

      // ============================================
      // 2. 提取应答模板
      // ============================================
      if (step1Data?.response_file_path) {
        const fileName = step1Data.response_file_path.split('/').pop() || '应答模板'
        const fileExt = fileName.split('.').pop()?.toLowerCase() || 'doc'
        const isWordDoc = ['doc', 'docx'].includes(fileExt)

        docs.templateFile = {
          name: fileName,
          url: step1Data.response_file_path,
          status: 'success',
          uid: Date.now() + Math.random() + 1,
          size: 0
        }

        console.log(`✅ 应答模板: ${fileName} (${isWordDoc ? 'Word' : fileExt})`)
      }

      // ============================================
      // 3. 提取技术需求文档
      // ============================================
      if (step1Data?.technical_file_path) {
        const fileName = step1Data.technical_file_path.split('/').pop() || '技术需求文档'
        const fileExt = fileName.split('.').pop()?.toLowerCase() || 'doc'
        const isWordDoc = ['doc', 'docx'].includes(fileExt)

        docs.technicalFile = {
          name: fileName,
          url: step1Data.technical_file_path,
          status: 'success',
          uid: Date.now() + Math.random() + 2,
          size: 0
        }

        console.log(`✅ 技术需求文档: ${fileName} (${isWordDoc ? 'Word' : fileExt})`)
      }

      // ============================================
      // 4. 提取历史商务应答文件
      // ============================================
      if (step1Data?.business_response_file) {
        const businessFile = step1Data.business_response_file
        const fileName = businessFile.file_path?.split('/').pop() || '商务应答文件'
        const fileExt = fileName.split('.').pop()?.toLowerCase() || 'docx'
        const isWordDoc = ['doc', 'docx'].includes(fileExt)

        docs.businessResponseFile = {
          success: true,
          outputFile: businessFile.file_path,
          downloadUrl: getDownloadUrl(businessFile.file_path),
          previewUrl: isWordDoc ? `/api/business-response/preview/${projectId}` : undefined,
          stats: businessFile.stats || {},
          message: '该项目已有商务应答文件',
          isHistory: true,
          generated_at: businessFile.generated_at || step1Data.updated_at
        }

        console.log(`✅ 历史商务应答: ${fileName}`)
      }

      // ============================================
      // 5. 提取历史点对点应答文件
      // ============================================
      if (step1Data?.technical_point_to_point_file) {
        const p2pFile = step1Data.technical_point_to_point_file
        const fileName = p2pFile.file_path?.split('/').pop() || '点对点应答文件'
        const fileExt = fileName.split('.').pop()?.toLowerCase() || 'docx'
        const isWordDoc = ['doc', 'docx'].includes(fileExt)

        docs.p2pResponseFile = {
          success: true,
          outputFile: p2pFile.file_path,
          downloadUrl: getDownloadUrl(p2pFile.file_path),
          previewUrl: isWordDoc ? `/api/point-to-point/preview/${projectId}` : undefined,
          stats: p2pFile.stats || {},
          message: '该项目已有点对点应答文件',
          isHistory: true,
          generated_at: p2pFile.generated_at || step1Data.updated_at
        }

        console.log(`✅ 历史点对点应答: ${fileName}`)
      }

      // ============================================
      // 6. 提取历史技术方案文件
      // ============================================
      if (step1Data?.technical_proposal_file) {
        const proposalFile = step1Data.technical_proposal_file
        const fileName = proposalFile.file_path?.split('/').pop() || '技术方案文件'
        const fileExt = fileName.split('.').pop()?.toLowerCase() || 'docx'
        const isWordDoc = ['doc', 'docx'].includes(fileExt)

        docs.techProposalFile = {
          success: true,
          outputFile: proposalFile.file_path,
          downloadUrl: getDownloadUrl(proposalFile.file_path),
          previewUrl: isWordDoc ? `/api/tech-proposal/preview/${projectId}` : undefined,
          stats: proposalFile.stats || {},
          message: '该项目已有技术方案文件',
          isHistory: true,
          generated_at: proposalFile.generated_at || step1Data.updated_at
        }

        console.log(`✅ 历史技术方案: ${fileName}`)
      }

      // 更新当前文档状态
      currentDocuments.value = docs

      // 执行文档加载完成回调
      // 注意：不在这里显示通用消息，让各页面根据实际需要显示具体的消息
      if (callbacks?.onDocumentsLoaded) {
        callbacks.onDocumentsLoaded(docs)
      }

    } catch (err) {
      error.value = '加载项目文档失败'
      ElMessage.error(error.value)
      console.error('Load project documents error:', err)
    } finally {
      loading.value = false
    }
  }

  // ============================================
  // 辅助函数：清空文档
  // ============================================

  /**
   * 清空当前文档状态
   */
  const clearDocuments = () => {
    currentDocuments.value = {
      tenderFile: null,
      templateFile: null,
      technicalFile: null,
      businessResponseFile: null,
      p2pResponseFile: null,
      techProposalFile: null
    }
  }

  // ============================================
  // 辅助函数：从Store恢复项目
  // ============================================

  /**
   * 从Store恢复当前项目（用于从HITL页面跳转过来的场景）
   */
  const restoreProjectFromStore = async (callbacks?: ProjectChangeCallbacks) => {
    if (projectStore.projectId) {
      console.log(`🔄 从Store恢复项目: ${projectStore.projectId}`)
      await handleProjectChange(projectStore.projectId, callbacks)
      return projectStore.projectId
    }
    return null
  }

  // ============================================
  // 辅助函数：文件转换为UploadUserFile格式
  // ============================================

  /**
   * 将文件路径转换为UploadUserFile格式
   * @param filePath 文件路径
   * @param fileName 文件名（可选）
   */
  const filePathToUploadFile = (
    filePath: string,
    fileName?: string
  ): UploadUserFile => {
    const name = fileName || filePath.split('/').pop() || '文件'
    return {
      name,
      url: filePath,
      status: 'success',
      uid: Date.now() + Math.random(),
      size: 0
    }
  }

  // ============================================
  // 辅助函数：获取文件下载URL
  // ============================================

  /**
   * 获取文件下载URL（支持outputs和uploads目录）
   * 复用DocumentPreview的路径转换逻辑，添加download参数
   * @param filePath 文件路径（可以是绝对路径或相对路径）
   */
  const getDownloadUrl = (filePath: string): string => {
    // 如果已经是API路径，直接返回并添加download参数
    if (filePath.startsWith('/api/')) {
      return filePath.includes('?') ? `${filePath}&download=true` : `${filePath}?download=true`
    }

    // 处理本地文件路径，转换为API路径
    let apiPath = filePath

    // 步骤1: 移除绝对路径前缀（如果存在）
    const absolutePrefix = '/Users/lvhe/Downloads/zhongbiao/zhongbiao/'
    if (apiPath.startsWith(absolutePrefix)) {
      apiPath = apiPath.substring(absolutePrefix.length)
    }

    // 步骤2: 移除 ai_tender_system/data/ 或 data/ 前缀
    if (apiPath.startsWith('ai_tender_system/data/')) {
      apiPath = apiPath.substring('ai_tender_system/data/'.length)
    } else if (apiPath.startsWith('data/')) {
      apiPath = apiPath.substring('data/'.length)
    }

    // 步骤3: 构建API URL（使用 /api/files/serve/ 万能API）
    // 现在 apiPath 应该是：outputs/xxx.docx 或 uploads/xxx/xxx.docx
    return `/api/files/serve/${apiPath}?download=true`
  }

  // ============================================
  // 返回API
  // ============================================

  return {
    // 状态
    projects,
    loading,
    error,
    currentDocuments,

    // 计算属性
    selectedProject,
    hasProjects,
    hasTenderFile,
    hasTemplateFile,
    hasTechnicalFile,

    // 核心函数
    loadProjects,
    handleProjectChange,
    loadProjectDocuments,

    // 辅助函数
    clearDocuments,
    restoreProjectFromStore,
    filePathToUploadFile,
    getDownloadUrl
  }
}
