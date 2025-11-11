/**
 * 图片压缩工具
 *
 * 功能：
 * - 智能判断是否需要压缩
 * - 按图片类型使用不同的压缩参数
 * - Canvas API实现客户端压缩
 * - 防止压缩后文件反而变大
 */

/**
 * 压缩配置类型
 */
export interface CompressionConfig {
  maxWidth?: number    // 最大宽度（像素）
  maxHeight?: number   // 最大高度（像素）
  quality?: number     // 压缩质量（0-1）
  mimeType?: string    // 输出格式
}

/**
 * 图片类型压缩配置
 */
export const COMPRESSION_PRESETS: Record<string, CompressionConfig> = {
  // 营业执照：需要较高质量
  license: {
    maxWidth: 1500,
    quality: 0.80,
    mimeType: 'image/jpeg'
  },

  // 资质证书：标准质量
  qualification: {
    maxWidth: 1200,
    quality: 0.75,
    mimeType: 'image/jpeg'
  },

  // 身份证：可读即可
  id_card: {
    maxWidth: 1000,
    quality: 0.70,
    mimeType: 'image/jpeg'
  },

  // 公章：必须清晰
  seal: {
    maxWidth: 800,
    quality: 0.85,
    mimeType: 'image/jpeg'
  },

  // 照片：标准质量
  photo: {
    maxWidth: 800,
    quality: 0.75,
    mimeType: 'image/jpeg'
  },

  // 默认配置
  default: {
    maxWidth: 1200,
    quality: 0.75,
    mimeType: 'image/jpeg'
  }
}

/**
 * 压缩阈值配置
 */
const COMPRESSION_THRESHOLDS = {
  // 文件大小阈值（小于此值不压缩）
  minFileSize: 300 * 1024,  // 300KB

  // 尺寸阈值
  minWidth: 1200,
  minHeight: 1200,

  // PNG转JPEG阈值
  pngToJpegSize: 100 * 1024,  // 100KB

  // 压缩效果阈值（压缩后如果只减少<10%，使用原图）
  minSavingRatio: 0.1
}

/**
 * 加载图片
 */
function loadImage(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      const img = new Image()

      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('图片加载失败'))
      img.src = e.target?.result as string
    }

    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsDataURL(file)
  })
}

/**
 * 判断是否需要压缩
 */
function shouldCompress(file: File, img: HTMLImageElement): boolean {
  const { size, type } = file
  const { width, height } = img

  // 快速跳过：非常小的文件
  if (size < 100 * 1024) {
    console.log('[ImageCompressor] 文件<100KB，跳过压缩')
    return false
  }

  // 条件1：文件大于阈值
  if (size > COMPRESSION_THRESHOLDS.minFileSize) {
    console.log('[ImageCompressor] 文件大小超过阈值，需要压缩')
    return true
  }

  // 条件2：尺寸过大
  if (width > COMPRESSION_THRESHOLDS.minWidth || height > COMPRESSION_THRESHOLDS.minHeight) {
    console.log('[ImageCompressor] 图片尺寸过大，需要压缩')
    return true
  }

  // 条件3：PNG且大于100KB（可以转JPEG大幅减小）
  if (type === 'image/png' && size > COMPRESSION_THRESHOLDS.pngToJpegSize) {
    console.log('[ImageCompressor] PNG图片>100KB，转JPEG可节省空间')
    return true
  }

  console.log('[ImageCompressor] 图片符合要求，不需要压缩')
  return false
}

/**
 * 压缩图片
 */
async function compressImage(
  file: File,
  config: CompressionConfig = COMPRESSION_PRESETS.default
): Promise<File> {
  try {
    // 1. 加载图片
    const img = await loadImage(file)

    console.log(`[ImageCompressor] 原始图片: ${img.width}x${img.height}, ${formatFileSize(file.size)}`)

    // 2. 判断是否需要压缩
    if (!shouldCompress(file, img)) {
      return file
    }

    // 3. 计算新尺寸
    let { width, height } = img
    const maxWidth = config.maxWidth || 1200
    const maxHeight = config.maxHeight || maxWidth

    if (width > maxWidth || height > maxHeight) {
      const ratio = Math.min(maxWidth / width, maxHeight / height)
      width = Math.round(width * ratio)
      height = Math.round(height * ratio)
    }

    // 4. 创建Canvas并绘制
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height

    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#FFFFFF'  // 白色背景（处理透明PNG）
    ctx.fillRect(0, 0, width, height)
    ctx.drawImage(img, 0, 0, width, height)

    // 5. 转换为Blob
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob)
          } else {
            reject(new Error('Canvas转Blob失败'))
          }
        },
        config.mimeType || 'image/jpeg',
        config.quality || 0.75
      )
    })

    // 6. 转换为File
    const compressedFile = new File(
      [blob],
      file.name.replace(/\.(png|jpg|jpeg|gif|bmp)$/i, '.jpg'),  // 统一扩展名为.jpg
      {
        type: config.mimeType || 'image/jpeg',
        lastModified: Date.now()
      }
    )

    // 7. 比较大小，防止压缩后反而变大
    const savingRatio = (file.size - compressedFile.size) / file.size

    if (savingRatio < COMPRESSION_THRESHOLDS.minSavingRatio) {
      console.log(`[ImageCompressor] 压缩效果不明显（节省${(savingRatio * 100).toFixed(1)}%），使用原图`)
      return file
    }

    console.log(
      `[ImageCompressor] ✅ 压缩成功: ` +
      `${img.width}x${img.height} → ${width}x${height}, ` +
      `${formatFileSize(file.size)} → ${formatFileSize(compressedFile.size)} ` +
      `(节省${(savingRatio * 100).toFixed(1)}%)`
    )

    return compressedFile

  } catch (error) {
    console.error('[ImageCompressor] 压缩失败:', error)
    // 压缩失败，返回原文件
    return file
  }
}

/**
 * 智能压缩图片（根据图片类型自动选择配置）
 */
export async function smartCompressImage(
  file: File,
  imageType: keyof typeof COMPRESSION_PRESETS = 'default'
): Promise<File> {
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    console.warn('[ImageCompressor] 不是图片文件，跳过压缩')
    return file
  }

  // 获取对应的压缩配置
  const config = COMPRESSION_PRESETS[imageType] || COMPRESSION_PRESETS.default

  // 执行压缩
  return compressImage(file, config)
}

/**
 * 批量压缩图片
 */
export async function compressImages(
  files: File[],
  imageType: keyof typeof COMPRESSION_PRESETS = 'default'
): Promise<File[]> {
  console.log(`[ImageCompressor] 开始批量压缩 ${files.length} 张图片`)

  const compressedFiles = await Promise.all(
    files.map(file => smartCompressImage(file, imageType))
  )

  // 统计压缩效果
  const originalSize = files.reduce((sum, f) => sum + f.size, 0)
  const compressedSize = compressedFiles.reduce((sum, f) => sum + f.size, 0)
  const savings = ((originalSize - compressedSize) / originalSize * 100).toFixed(1)

  console.log(
    `[ImageCompressor] 批量压缩完成: ` +
    `${formatFileSize(originalSize)} → ${formatFileSize(compressedSize)} ` +
    `(节省${savings}%)`
  )

  return compressedFiles
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

/**
 * 获取图片信息（不加载完整图片）
 */
export function getImageInfo(file: File): Promise<{
  width: number
  height: number
  size: number
  type: string
}> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)

    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve({
        width: img.width,
        height: img.height,
        size: file.size,
        type: file.type
      })
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('无法读取图片信息'))
    }

    img.src = url
  })
}

// 导出
export default {
  smartCompressImage,
  compressImages,
  getImageInfo,
  COMPRESSION_PRESETS
}
