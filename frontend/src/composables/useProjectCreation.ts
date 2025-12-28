/**
 * 项目创建 Composable
 *
 * 提供统一的项目创建逻辑，支持快速创建新项目
 * 适用于商务应答、点对点应答、技术方案等业务页面
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { tenderApi } from '@/api/endpoints/tender'

export interface ProjectCreationForm {
  companyId: number | null
  projectName: string
  projectNumber: string
  productCategoryId: number | null
  productItems: string[]
}

export interface UseProjectCreationOptions {
  /**
   * 项目创建成功后的回调函数
   * @param projectId 新创建的项目ID
   */
  onProjectCreated?: (projectId: number) => void | Promise<void>

  /**
   * 是否自动生成项目编号
   * @default true
   */
  autoGenerateNumber?: boolean

  /**
   * 项目编号前缀
   * @default 'PRJ'
   */
  numberPrefix?: string
}

export function useProjectCreation(options: UseProjectCreationOptions = {}) {
  const {
    onProjectCreated,
    autoGenerateNumber = true,
    numberPrefix = 'PRJ'
  } = options

  const creating = ref(false)
  const createdProjectId = ref<number | null>(null)

  /**
   * 创建新项目
   * @param formData 项目创建表单数据
   * @returns 创建的项目ID
   */
  const createProject = async (formData: ProjectCreationForm): Promise<number> => {
    if (!formData.companyId) {
      throw new Error('请先选择公司')
    }

    creating.value = true

    try {
      ElMessage.info('正在创建新项目...')

      // 如果未提供项目编号且开启自动生成，则自动生成
      const projectNumber = formData.projectNumber ||
        (autoGenerateNumber ? generateProjectNumber() : '')

      const response = await tenderApi.createProject({
        company_id: formData.companyId,
        project_name: formData.projectName || '新项目',
        project_number: projectNumber,
        product_category_id: formData.productCategoryId || undefined,
        product_items: formData.productItems?.length > 0 ? formData.productItems : undefined
      })

      createdProjectId.value = response.project_id
      ElMessage.success(`新项目已创建: ${formData.projectName || '新项目'}`)

      // 执行回调
      if (onProjectCreated) {
        await onProjectCreated(response.project_id)
      }

      return response.project_id
    } catch (error: any) {
      console.error('创建项目失败:', error)
      ElMessage.error(error.message || '创建项目失败，请重试')
      throw error
    } finally {
      creating.value = false
    }
  }

  /**
   * 生成新的项目编号
   * @returns 项目编号，格式: {prefix}-{timestamp}
   */
  const generateProjectNumber = (): string => {
    const timestamp = Date.now()
    return `${numberPrefix}-${timestamp}`
  }

  /**
   * 重置创建状态
   */
  const resetCreation = () => {
    creating.value = false
    createdProjectId.value = null
  }

  /**
   * 检查是否可以创建项目
   * @param formData 项目创建表单数据
   * @returns 是否可以创建
   */
  const canCreate = (formData: ProjectCreationForm): boolean => {
    return !!formData.companyId && !!formData.projectName
  }

  return {
    creating,
    createdProjectId,
    createProject,
    generateProjectNumber,
    resetCreation,
    canCreate
  }
}
