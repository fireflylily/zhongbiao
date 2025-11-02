/**
 * 文件上传Composable
 *
 * 封装文件上传的通用逻辑，包括进度跟踪、验证、错误处理
 */

import { ref, computed, type Ref } from 'vue'
import { useNotification } from './useNotification'

/**
 * 文件验证规则
 */
export interface FileValidationRules {
  maxSize?: number // 最大文件大小(字节)
  allowedTypes?: string[] // 允许的文件类型
  allowedExtensions?: string[] // 允许的文件扩展名
}

/**
 * 上传选项
 */
export interface UploadOptions {
  validation?: FileValidationRules
  autoUpload?: boolean // 是否自动上传
  onSuccess?: (response: any, file: File) => void
  onError?: (error: Error, file: File) => void
  onProgress?: (progress: number, file: File) => void
}

/**
 * 文件上传状态
 */
export interface FileUploadState {
  file: File | null
  fileUrl: string | null
  uploading: boolean
  progress: number
  error: string | null
}

/**
 * useFileUpload返回值类型
 */
export interface UseFileUploadReturn {
  // State
  file: Ref<File | null>
  fileUrl: Ref<string | null>
  fileName: Ref<string>
  fileSize: Ref<string>
  uploading: Ref<boolean>
  progress: Ref<number>
  error: Ref<string | null>

  // Computed
  hasFile: Ref<boolean>
  isValid: Ref<boolean>

  // Methods
  selectFile: (file: File) => boolean
  uploadFile: (
    uploadFn: (file: File, onProgress: (p: number) => void) => Promise<any>
  ) => Promise<any>
  clearFile: () => void
  reset: () => void
}

/**
 * 文件上传Hook
 *
 * @param options - 上传选项
 * @returns 文件上传控制对象
 */
export function useFileUpload(options: UploadOptions = {}): UseFileUploadReturn {
  const { validation, autoUpload = false, onSuccess, onError, onProgress } = options
  const { error: showError } = useNotification()

  // ==================== State ====================

  const file = ref<File | null>(null)
  const fileUrl = ref<string | null>(null)
  const uploading = ref(false)
  const progress = ref(0)
  const error = ref<string | null>(null)

  // ==================== Computed ====================

  const hasFile = computed(() => !!file.value)

  const fileName = computed(() => file.value?.name || '')

  const fileSize = computed(() => {
    if (!file.value) return ''
    return formatFileSize(file.value.size)
  })

  const isValid = computed(() => {
    if (!file.value) return false
    return validateFile(file.value, validation)
  })

  // ==================== Methods ====================

  /**
   * 格式化文件大小
   */
  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'

    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  /**
   * 验证文件
   */
  function validateFile(
    file: File,
    rules: FileValidationRules | undefined
  ): boolean {
    if (!rules) return true

    // 验证文件大小
    if (rules.maxSize && file.size > rules.maxSize) {
      error.value = `文件大小不能超过 ${formatFileSize(rules.maxSize)}`
      showError(error.value)
      return false
    }

    // 验证文件类型
    if (rules.allowedTypes && rules.allowedTypes.length > 0) {
      if (!rules.allowedTypes.includes(file.type)) {
        error.value = `不支持的文件类型: ${file.type}`
        showError(error.value)
        return false
      }
    }

    // 验证文件扩展名
    if (rules.allowedExtensions && rules.allowedExtensions.length > 0) {
      const ext = file.name.split('.').pop()?.toLowerCase()
      if (!ext || !rules.allowedExtensions.includes(ext)) {
        error.value = `不支持的文件扩展名: .${ext}`
        showError(error.value)
        return false
      }
    }

    return true
  }

  /**
   * 选择文件
   */
  function selectFile(selectedFile: File): boolean {
    error.value = null

    if (!validateFile(selectedFile, validation)) {
      return false
    }

    file.value = selectedFile

    // 创建预览URL（如果是图片）
    if (selectedFile.type.startsWith('image/')) {
      fileUrl.value = URL.createObjectURL(selectedFile)
    }

    return true
  }

  /**
   * 上传文件
   */
  async function uploadFile(
    uploadFn: (file: File, onProgress: (progress: number) => void) => Promise<any>
  ): Promise<any> {
    if (!file.value) {
      error.value = '请先选择文件'
      showError(error.value)
      return null
    }

    if (!isValid.value) {
      error.value = '文件验证失败'
      return null
    }

    uploading.value = true
    progress.value = 0
    error.value = null

    try {
      const response = await uploadFn(file.value, (p) => {
        progress.value = p
        onProgress?.(p, file.value!)
      })

      // 调用成功回调
      onSuccess?.(response, file.value)

      return response
    } catch (err: any) {
      error.value = err.message || '上传失败'
      showError(error.value)

      // 调用错误回调
      onError?.(err, file.value)

      throw err
    } finally {
      uploading.value = false
    }
  }

  /**
   * 清除文件
   */
  function clearFile(): void {
    // 释放URL对象
    if (fileUrl.value) {
      URL.revokeObjectURL(fileUrl.value)
    }

    file.value = null
    fileUrl.value = null
    progress.value = 0
    error.value = null
  }

  /**
   * 重置状态
   */
  function reset(): void {
    clearFile()
    uploading.value = false
  }

  // ==================== Return ====================

  return {
    // State
    file,
    fileUrl,
    fileName,
    fileSize,
    uploading,
    progress,
    error,

    // Computed
    hasFile,
    isValid,

    // Methods
    selectFile,
    uploadFile,
    clearFile,
    reset
  }
}

/**
 * 批量文件上传Hook
 *
 * @param options - 上传选项
 * @returns 批量上传控制对象
 */
export function useBatchFileUpload(options: UploadOptions = {}) {
  const { validation, onSuccess, onError } = options
  const { error: showError } = useNotification()

  // ==================== State ====================

  const files = ref<File[]>([])
  const uploadingFiles = ref<Set<string>>(new Set())
  const uploadProgress = ref<Map<string, number>>(new Map())
  const uploadErrors = ref<Map<string, string>>(new Map())

  // ==================== Computed ====================

  const hasFiles = computed(() => files.value.length > 0)

  const filesCount = computed(() => files.value.length)

  const allUploading = computed(() => uploadingFiles.value.size > 0)

  const totalProgress = computed(() => {
    if (files.value.length === 0) return 0

    let total = 0
    files.value.forEach((file) => {
      total += uploadProgress.value.get(file.name) || 0
    })

    return Math.round(total / files.value.length)
  })

  // ==================== Methods ====================

  /**
   * 添加文件
   */
  function addFiles(newFiles: File[]): void {
    newFiles.forEach((file) => {
      if (validateFile(file, validation)) {
        if (!files.value.find((f) => f.name === file.name)) {
          files.value.push(file)
        }
      }
    })
  }

  /**
   * 验证文件
   */
  function validateFile(
    file: File,
    rules: FileValidationRules | undefined
  ): boolean {
    if (!rules) return true

    if (rules.maxSize && file.size > rules.maxSize) {
      const error = `文件 ${file.name} 大小超过限制`
      showError(error)
      uploadErrors.value.set(file.name, error)
      return false
    }

    if (rules.allowedTypes && !rules.allowedTypes.includes(file.type)) {
      const error = `文件 ${file.name} 类型不支持`
      showError(error)
      uploadErrors.value.set(file.name, error)
      return false
    }

    return true
  }

  /**
   * 移除文件
   */
  function removeFile(fileName: string): void {
    files.value = files.value.filter((f) => f.name !== fileName)
    uploadProgress.value.delete(fileName)
    uploadErrors.value.delete(fileName)
  }

  /**
   * 上传单个文件
   */
  async function uploadSingleFile(
    file: File,
    uploadFn: (file: File, onProgress: (p: number) => void) => Promise<any>
  ): Promise<void> {
    uploadingFiles.value.add(file.name)
    uploadProgress.value.set(file.name, 0)
    uploadErrors.value.delete(file.name)

    try {
      const response = await uploadFn(file, (progress) => {
        uploadProgress.value.set(file.name, progress)
      })

      onSuccess?.(response, file)
    } catch (err: any) {
      const error = err.message || '上传失败'
      uploadErrors.value.set(file.name, error)
      onError?.(err, file)
    } finally {
      uploadingFiles.value.delete(file.name)
    }
  }

  /**
   * 上传所有文件
   */
  async function uploadAll(
    uploadFn: (file: File, onProgress: (p: number) => void) => Promise<any>
  ): Promise<void> {
    const promises = files.value.map((file) => uploadSingleFile(file, uploadFn))
    await Promise.all(promises)
  }

  /**
   * 清除所有文件
   */
  function clearAll(): void {
    files.value = []
    uploadingFiles.value.clear()
    uploadProgress.value.clear()
    uploadErrors.value.clear()
  }

  // ==================== Return ====================

  return {
    files,
    uploadingFiles,
    uploadProgress,
    uploadErrors,
    hasFiles,
    filesCount,
    allUploading,
    totalProgress,
    addFiles,
    removeFile,
    uploadAll,
    clearAll
  }
}
