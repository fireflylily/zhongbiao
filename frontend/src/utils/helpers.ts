/**
 * 辅助工具函数
 *
 * 提供各种通用辅助功能：
 * - 防抖/节流
 * - 深拷贝/浅拷贝
 * - 数组/对象处理
 * - 本地存储封装
 * - 树形数据处理
 * - 其他实用工具
 */

/**
 * 防抖函数
 * 在事件被触发n秒后再执行回调，如果在这n秒内又被触发，则重新计时
 *
 * @param func 要防抖的函数
 * @param wait 等待时间（毫秒）
 * @param immediate 是否立即执行
 * @returns 防抖后的函数
 *
 * @example
 * const debouncedSearch = debounce((keyword) => {
 *   console.log('搜索:', keyword)
 * }, 500)
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate: boolean = false
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function (this: any, ...args: Parameters<T>) {
    const context = this
    const later = () => {
      timeout = null
      if (!immediate) func.apply(context, args)
    }

    const callNow = immediate && !timeout
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)

    if (callNow) func.apply(context, args)
  }
}

/**
 * 节流函数
 * 规定在一个单位时间内，只能触发一次函数。如果这个单位时间内触发多次函数，只有一次生效
 *
 * @param func 要节流的函数
 * @param wait 等待时间（毫秒）
 * @returns 节流后的函数
 *
 * @example
 * const throttledScroll = throttle(() => {
 *   console.log('滚动事件')
 * }, 200)
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  let previous = 0

  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()
    const remaining = wait - (now - previous)
    const context = this

    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout)
        timeout = null
      }
      previous = now
      func.apply(context, args)
    } else if (!timeout) {
      timeout = setTimeout(() => {
        previous = Date.now()
        timeout = null
        func.apply(context, args)
      }, remaining)
    }
  }
}

/**
 * 深拷贝
 *
 * @param obj 要拷贝的对象
 * @returns 拷贝后的新对象
 *
 * @example
 * const obj = { a: 1, b: { c: 2 } }
 * const copy = deepClone(obj)
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as any
  }

  if (obj instanceof Array) {
    const copy: any[] = []
    obj.forEach((item, index) => {
      copy[index] = deepClone(item)
    })
    return copy as any
  }

  if (obj instanceof Object) {
    const copy: any = {}
    Object.keys(obj).forEach((key) => {
      copy[key] = deepClone((obj as any)[key])
    })
    return copy
  }

  return obj
}

/**
 * 对象合并（深度合并）
 *
 * @param target 目标对象
 * @param sources 源对象
 * @returns 合并后的对象
 */
export function deepMerge<T extends Record<string, any>>(
  target: T,
  ...sources: Partial<T>[]
): T {
  if (!sources.length) return target

  const source = sources.shift()
  if (!source) return target

  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach((key) => {
      const sourceValue = source[key]
      const targetValue = target[key]

      if (isObject(sourceValue) && isObject(targetValue)) {
        target[key] = deepMerge({ ...targetValue }, sourceValue)
      } else {
        target[key] = sourceValue as any
      }
    })
  }

  return deepMerge(target, ...sources)
}

/**
 * 判断是否为对象
 */
function isObject(item: any): boolean {
  return item && typeof item === 'object' && !Array.isArray(item)
}

/**
 * 数组去重
 *
 * @param arr 数组
 * @param key 对象数组的去重字段
 * @returns 去重后的数组
 *
 * @example
 * unique([1, 2, 2, 3]) // [1, 2, 3]
 * unique([{id: 1}, {id: 2}, {id: 1}], 'id') // [{id: 1}, {id: 2}]
 */
export function unique<T>(arr: T[], key?: keyof T): T[] {
  if (!key) {
    return Array.from(new Set(arr))
  }

  const seen = new Set()
  return arr.filter((item) => {
    const value = item[key]
    if (seen.has(value)) {
      return false
    }
    seen.add(value)
    return true
  })
}

/**
 * 数组分组
 *
 * @param arr 数组
 * @param key 分组字段
 * @returns 分组后的对象
 *
 * @example
 * const data = [
 *   { type: 'A', value: 1 },
 *   { type: 'B', value: 2 },
 *   { type: 'A', value: 3 }
 * ]
 * groupBy(data, 'type')
 * // { A: [{type: 'A', value: 1}, {type: 'A', value: 3}], B: [{type: 'B', value: 2}] }
 */
export function groupBy<T>(arr: T[], key: keyof T): Record<string, T[]> {
  return arr.reduce((result, item) => {
    const groupKey = String(item[key])
    if (!result[groupKey]) {
      result[groupKey] = []
    }
    result[groupKey].push(item)
    return result
  }, {} as Record<string, T[]>)
}

/**
 * 树形数据转列表
 *
 * @param tree 树形数据
 * @param childrenKey 子节点字段名
 * @returns 列表数据
 */
export function treeToList<T extends Record<string, any>>(
  tree: T[],
  childrenKey: string = 'children'
): T[] {
  const result: T[] = []

  function traverse(nodes: T[]) {
    nodes.forEach((node) => {
      const { [childrenKey]: children, ...rest } = node
      result.push(rest as T)
      if (children && Array.isArray(children) && children.length > 0) {
        traverse(children)
      }
    })
  }

  traverse(tree)
  return result
}

/**
 * 列表转树形数据
 *
 * @param list 列表数据
 * @param options 配置项
 * @returns 树形数据
 */
export function listToTree<T extends Record<string, any>>(
  list: T[],
  options: {
    idKey?: string
    parentKey?: string
    childrenKey?: string
    rootId?: any
  } = {}
): T[] {
  const {
    idKey = 'id',
    parentKey = 'parent_id',
    childrenKey = 'children',
    rootId = null
  } = options

  const map = new Map<any, T>()
  const roots: T[] = []

  // 创建映射
  list.forEach((item) => {
    map.set(item[idKey], { ...item, [childrenKey]: [] })
  })

  // 建立父子关系
  list.forEach((item) => {
    const node = map.get(item[idKey])!
    const parentId = item[parentKey]

    if (parentId === rootId || parentId === null || parentId === undefined) {
      roots.push(node)
    } else {
      const parent = map.get(parentId)
      if (parent) {
        parent[childrenKey].push(node)
      } else {
        roots.push(node) // 找不到父节点，作为根节点
      }
    }
  })

  return roots
}

/**
 * 查找树节点
 *
 * @param tree 树形数据
 * @param predicate 查找条件函数
 * @param childrenKey 子节点字段名
 * @returns 找到的节点或undefined
 */
export function findTreeNode<T extends Record<string, any>>(
  tree: T[],
  predicate: (node: T) => boolean,
  childrenKey: string = 'children'
): T | undefined {
  for (const node of tree) {
    if (predicate(node)) {
      return node
    }
    if (node[childrenKey] && Array.isArray(node[childrenKey])) {
      const found = findTreeNode(node[childrenKey], predicate, childrenKey)
      if (found) return found
    }
  }
  return undefined
}

// ============ 本地存储封装 ============

/**
 * LocalStorage封装
 */
export const storage = {
  /**
   * 设置存储
   */
  set(key: string, value: any): void {
    try {
      const data = JSON.stringify(value)
      localStorage.setItem(key, data)
    } catch (error) {
      console.error('Storage set error:', error)
    }
  },

  /**
   * 获取存储
   */
  get<T = any>(key: string, defaultValue?: T): T | null {
    try {
      const data = localStorage.getItem(key)
      if (data === null) return defaultValue ?? null
      return JSON.parse(data)
    } catch (error) {
      console.error('Storage get error:', error)
      return defaultValue ?? null
    }
  },

  /**
   * 移除存储
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('Storage remove error:', error)
    }
  },

  /**
   * 清空存储
   */
  clear(): void {
    try {
      localStorage.clear()
    } catch (error) {
      console.error('Storage clear error:', error)
    }
  },

  /**
   * 检查key是否存在
   */
  has(key: string): boolean {
    return localStorage.getItem(key) !== null
  }
}

/**
 * SessionStorage封装
 */
export const sessionStorage = {
  set(key: string, value: any): void {
    try {
      const data = JSON.stringify(value)
      window.sessionStorage.setItem(key, data)
    } catch (error) {
      console.error('SessionStorage set error:', error)
    }
  },

  get<T = any>(key: string, defaultValue?: T): T | null {
    try {
      const data = window.sessionStorage.getItem(key)
      if (data === null) return defaultValue ?? null
      return JSON.parse(data)
    } catch (error) {
      console.error('SessionStorage get error:', error)
      return defaultValue ?? null
    }
  },

  remove(key: string): void {
    try {
      window.sessionStorage.removeItem(key)
    } catch (error) {
      console.error('SessionStorage remove error:', error)
    }
  },

  clear(): void {
    try {
      window.sessionStorage.clear()
    } catch (error) {
      console.error('SessionStorage clear error:', error)
    }
  },

  has(key: string): boolean {
    return window.sessionStorage.getItem(key) !== null
  }
}

// ============ 其他工具函数 ============

/**
 * 生成UUID
 */
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

/**
 * 生成随机字符串
 *
 * @param length 长度
 * @returns 随机字符串
 */
export function randomString(length: number = 16): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 下载文件
 *
 * @param blob Blob对象或URL
 * @param filename 文件名
 */
export async function downloadFile(blob: Blob | string, filename: string): Promise<void> {
  // 如果是 Blob 对象，直接下载
  if (typeof blob !== 'string') {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    return
  }

  // 如果是 URL，先检查响应类型
  try {
    const response = await fetch(blob)

    if (!response.ok) {
      // HTTP 错误（404, 500等）
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        // 后端返回了JSON错误
        const errorData = await response.json()
        throw new Error(errorData.error || errorData.message || '文件下载失败')
      }
      throw new Error(`文件下载失败: HTTP ${response.status}`)
    }

    // 检查响应类型，确保不是HTML或JSON
    const contentType = response.headers.get('content-type')
    if (contentType && (contentType.includes('text/html') || contentType.includes('application/json'))) {
      throw new Error('服务器返回了错误页面，而不是文件')
    }

    // 获取文件 Blob
    const fileBlob = await response.blob()

    // 创建下载链接
    const url = URL.createObjectURL(fileBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('下载文件失败:', error)
    throw error
  }
}

/**
 * 复制文本到剪贴板
 *
 * @param text 要复制的文本
 * @returns Promise
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // 降级方案
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      const success = document.execCommand('copy')
      document.body.removeChild(textarea)
      return success
    }
  } catch (error) {
    console.error('Copy to clipboard failed:', error)
    return false
  }
}

/**
 * 获取文件扩展名
 *
 * @param filename 文件名
 * @returns 扩展名（含点）
 */
export function getFileExtension(filename: string): string {
  const lastDot = filename.lastIndexOf('.')
  return lastDot === -1 ? '' : filename.substring(lastDot)
}

/**
 * 获取文件名（不含扩展名）
 *
 * @param filename 文件名
 * @returns 文件名（不含扩展名）
 */
export function getFileName(filename: string): string {
  const lastDot = filename.lastIndexOf('.')
  return lastDot === -1 ? filename : filename.substring(0, lastDot)
}

/**
 * 延迟执行
 *
 * @param ms 延迟时间（毫秒）
 * @returns Promise
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * 重试函数
 *
 * @param fn 要重试的函数
 * @param retries 重试次数
 * @param delay 重试延迟（毫秒）
 * @returns Promise
 */
export async function retry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> {
  try {
    return await fn()
  } catch (error) {
    if (retries === 0) throw error
    await sleep(delay)
    return retry(fn, retries - 1, delay * 2) // 指数退避
  }
}

/**
 * 判断是否为移动端
 */
export function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
}

/**
 * 获取浏览器信息
 */
export function getBrowserInfo(): {
  name: string
  version: string
} {
  const ua = navigator.userAgent
  let name = 'Unknown'
  let version = 'Unknown'

  if (ua.indexOf('Firefox') > -1) {
    name = 'Firefox'
    version = ua.match(/Firefox\/(\d+\.\d+)/)?.[1] || ''
  } else if (ua.indexOf('Chrome') > -1) {
    name = 'Chrome'
    version = ua.match(/Chrome\/(\d+\.\d+)/)?.[1] || ''
  } else if (ua.indexOf('Safari') > -1) {
    name = 'Safari'
    version = ua.match(/Version\/(\d+\.\d+)/)?.[1] || ''
  } else if (ua.indexOf('MSIE') > -1 || ua.indexOf('Trident') > -1) {
    name = 'IE'
    version = ua.match(/(?:MSIE |rv:)(\d+\.\d+)/)?.[1] || ''
  }

  return { name, version }
}
