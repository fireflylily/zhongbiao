/**
 * HITL集成 Composable
 *
 * 提供统一的HITL（Human-In-The-Loop）流程集成逻辑
 * 支持从HITL页面加载文件、同步文件回HITL项目等功能
 *
 * 适用于商务应答、点对点应答、技术方案等业务页面
 */

import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { ProjectDocuments } from './useProjectDocuments'

/**
 * HITL文件信息
 */
export interface HitlFileInfo {
  /** 文件名 */
  filename: string
  /** 文件路径 */
  file_path: string
  /** 文件大小（字节） */
  file_size?: number
  /** 文件URL */
  file_url?: string
}

/**
 * 文件类型
 */
export type HitlFileType = 'point_to_point' | 'tech_proposal' | 'business_response' | 'template' | 'tender'

/**
 * HITL集成配置选项
 */
export interface UseHitlIntegrationOptions {
  /**
   * 文件加载成功后的回调
   */
  onFileLoaded?: (fileInfo: HitlFileInfo) => void | Promise<void>

  /**
   * 文件取消后的回调
   */
  onFileCancelled?: () => void | Promise<void>

  /**
   * 同步成功后的回调
   */
  onSyncSuccess?: () => void | Promise<void>
}

export function useHitlIntegration(options: UseHitlIntegrationOptions = {}) {
  const { onFileLoaded, onFileCancelled, onSyncSuccess } = options

  // 是否正在使用HITL文件
  const useHitlFile = ref(false)

  // HITL文件信息
  const hitlFileInfo = ref<HitlFileInfo | null>(null)

  // 是否正在同步
  const syncing = ref(false)

  // 是否已同步
  const synced = ref(false)

  // 是否有HITL文件信息
  const hasHitlFile = computed(() => !!hitlFileInfo.value)

  /**
   * 从HITL加载技术需求文件
   *
   * @param docs 项目文档对象
   * @param fileKey 要加载的文件键（默认：'technicalFile'）
   * @returns 是否成功加载
   */
  const loadFromHITL = (
    docs: ProjectDocuments,
    fileKey: keyof ProjectDocuments = 'technicalFile'
  ): boolean => {
    const file = docs[fileKey]

    if (!file) {
      ElMessage.warning(`当前项目没有${getFileTypeLabel(fileKey)}`)
      return false
    }

    // 兼容不同的文件对象结构
    hitlFileInfo.value = {
      filename: file.filename || file.name || '未知文件',
      file_path: file.file_path || file.url || '',
      file_size: file.file_size || file.size,
      file_url: file.file_url || file.url
    }

    useHitlFile.value = true
    synced.value = false

    ElMessage.success({
      message: `已加载HITL${getFileTypeLabel(fileKey)}: ${hitlFileInfo.value.filename}`,
      duration: 3000
    })

    // 执行回调
    if (onFileLoaded) {
      onFileLoaded(hitlFileInfo.value)
    }

    return true
  }

  /**
   * 取消使用HITL文件
   */
  const cancelHitlFile = () => {
    useHitlFile.value = false
    hitlFileInfo.value = null
    synced.value = false

    ElMessage.info('已取消使用HITL文件')

    // 执行回调
    if (onFileCancelled) {
      onFileCancelled()
    }
  }

  /**
   * 同步文件到HITL项目
   *
   * @param projectId 项目ID
   * @param outputFilePath 输出文件路径
   * @param fileType 文件类型
   * @returns 是否成功
   */
  const syncToHitl = async (
    projectId: number,
    outputFilePath: string,
    fileType: HitlFileType
  ): Promise<boolean> => {
    if (!projectId) {
      ElMessage.error('项目ID无效')
      return false
    }

    if (!outputFilePath) {
      ElMessage.error('文件路径无效')
      return false
    }

    syncing.value = true

    try {
      const response = await fetch(
        `/api/tender-processing/sync-file/${projectId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            file_path: outputFilePath,
            file_type: fileType
          })
        }
      )

      // 检查响应是否为JSON
      const contentType = response.headers.get('content-type')
      if (!contentType?.includes('application/json')) {
        const text = await response.text()
        console.error('同步API返回非JSON响应:', {
          status: response.status,
          statusText: response.statusText,
          contentType,
          responsePreview: text.substring(0, 200)
        })

        throw new Error(
          `服务器返回异常响应 (${response.status}): ${response.statusText}。` +
          '可能是后端配置问题，请联系管理员。'
        )
      }

      const result = await response.json()

      if (result.success || response.ok) {
        synced.value = true
        ElMessage.success({
          message: result.message || '已成功同步到投标项目',
          duration: 3000
        })

        // 执行回调
        if (onSyncSuccess) {
          await onSyncSuccess()
        }

        return true
      } else {
        throw new Error(result.error || result.message || '同步失败')
      }
    } catch (error: any) {
      console.error('同步到项目失败:', error)

      // 改进错误消息
      let errorMessage = '同步到项目失败'
      if (error.message) {
        errorMessage = error.message
      } else if (error.name === 'TypeError') {
        errorMessage = '网络请求失败，请检查网络连接'
      }

      ElMessage.error({
        message: errorMessage,
        duration: 5000
      })

      return false
    } finally {
      syncing.value = false
    }
  }

  /**
   * 重置同步状态
   */
  const resetSyncStatus = () => {
    synced.value = false
  }

  /**
   * 获取文件类型标签
   */
  const getFileTypeLabel = (fileKey: keyof ProjectDocuments): string => {
    const labels: Record<string, string> = {
      technicalFile: '技术需求文件',
      tenderFile: '招标文档',
      templateFile: '应答模板',
      businessResponseFile: '商务应答文件',
      p2pResponseFile: '点对点应答文件',
      techProposalFile: '技术方案文件'
    }
    return labels[fileKey] || '文件'
  }

  return {
    // 状态
    useHitlFile,
    hitlFileInfo,
    hasHitlFile,
    syncing,
    synced,

    // 方法
    loadFromHITL,
    cancelHitlFile,
    syncToHitl,
    resetSyncStatus
  }
}
