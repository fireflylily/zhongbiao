/**
 * 历史文件管理 Composable
 *
 * 提供统一的历史文件管理逻辑
 * 支持加载、预览、下载历史生成的文件
 *
 * 适用于点对点应答、商务应答、技术方案等业务页面
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { formatFileSize, formatDate } from '@/utils/format'

/**
 * 历史文件信息
 */
export interface HistoryFile {
  /** 文件ID */
  id?: number
  /** 文件名 */
  filename: string
  /** 文件路径 */
  file_path: string
  /** 文件大小（字节） */
  size: number
  /** 处理时间 */
  process_time: string
  /** 生成时间 */
  generated_at?: string
  /** 统计信息 */
  stats?: Record<string, any>
  /** 其他元数据 */
  [key: string]: any
}

/**
 * 历史文件管理配置选项
 */
export interface UseHistoryFilesOptions {
  /**
   * 文件加载成功后的回调
   */
  onFilesLoaded?: (files: HistoryFile[]) => void | Promise<void>

  /**
   * 文件下载成功后的回调
   */
  onFileDownloaded?: (file: HistoryFile) => void | Promise<void>

  /**
   * 是否自动格式化文件信息
   * @default true
   */
  autoFormat?: boolean
}

export function useHistoryFiles(
  apiEndpoint: string,
  options: UseHistoryFilesOptions = {}
) {
  const {
    onFilesLoaded,
    onFileDownloaded,
    autoFormat = true
  } = options

  // 历史文件列表
  const historyFiles = ref<HistoryFile[]>([])

  // 加载状态
  const loading = ref(false)

  // 错误信息
  const error = ref<string | null>(null)

  /**
   * 加载历史文件列表
   *
   * @returns 历史文件列表
   */
  const loadFiles = async (): Promise<HistoryFile[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(apiEndpoint)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()

      if (result.success) {
        historyFiles.value = result.data || []

        // 自动格式化文件信息
        if (autoFormat) {
          historyFiles.value = historyFiles.value.map(formatFileInfo)
        }

        ElMessage.success(`加载了 ${historyFiles.value.length} 个历史文件`)

        // 执行回调
        if (onFilesLoaded) {
          await onFilesLoaded(historyFiles.value)
        }

        return historyFiles.value
      } else {
        throw new Error(result.error || result.message || '加载失败')
      }
    } catch (err: any) {
      console.error('加载历史文件失败:', err)
      error.value = err.message || '加载历史文件失败'

      ElMessage.error({
        message: error.value,
        duration: 5000
      })

      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 下载文件
   *
   * @param file 历史文件对象
   */
  const downloadFile = async (file: HistoryFile): Promise<void> => {
    try {
      if (!file.file_path) {
        throw new Error('文件路径无效')
      }

      // 构建下载URL
      const downloadUrl = file.file_path.startsWith('/api/')
        ? file.file_path
        : `/api/download?file_path=${encodeURIComponent(file.file_path)}`

      // 创建下载链接
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = file.filename
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      ElMessage.success('文件下载中...')

      // 执行回调
      if (onFileDownloaded) {
        await onFileDownloaded(file)
      }
    } catch (err: any) {
      console.error('下载文件失败:', err)
      ElMessage.error(err.message || '下载文件失败')
    }
  }

  /**
   * 格式化文件信息（内部使用）
   *
   * @param file 原始文件对象
   * @returns 格式化后的文件对象
   */
  const formatFileInfo = (file: HistoryFile): HistoryFile => {
    return {
      ...file,
      _formatted: {
        size: formatFileSize(file.size),
        processTime: formatDate(file.process_time || file.generated_at, 'YYYY-MM-DD HH:mm:ss')
      }
    }
  }

  /**
   * 刷新文件列表
   */
  const refresh = async (): Promise<void> => {
    await loadFiles()
  }

  /**
   * 清空文件列表
   */
  const clear = (): void => {
    historyFiles.value = []
    error.value = null
  }

  /**
   * 获取文件数量
   */
  const count = (): number => {
    return historyFiles.value.length
  }

  /**
   * 根据条件筛选文件
   *
   * @param predicate 筛选条件函数
   * @returns 筛选后的文件列表
   */
  const filter = (predicate: (file: HistoryFile) => boolean): HistoryFile[] => {
    return historyFiles.value.filter(predicate)
  }

  /**
   * 查找文件
   *
   * @param predicate 查找条件函数
   * @returns 找到的文件或undefined
   */
  const find = (predicate: (file: HistoryFile) => boolean): HistoryFile | undefined => {
    return historyFiles.value.find(predicate)
  }

  return {
    // 状态
    historyFiles,
    loading,
    error,

    // 方法
    loadFiles,
    downloadFile,
    refresh,
    clear,
    count,
    filter,
    find,

    // 工具方法（直接暴露）
    formatFileSize,
    formatDate
  }
}
