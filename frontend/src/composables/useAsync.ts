/**
 * 异步数据加载Composable
 *
 * 封装异步数据加载的通用逻辑，包括loading状态、错误处理、重试
 */

import { ref, computed, onMounted, type Ref } from 'vue'
import { useNotification } from './useNotification'

/**
 * 异步加载选项
 */
export interface UseAsyncOptions<T> {
  immediate?: boolean // 是否立即执行
  initialData?: T // 初始数据
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
  resetOnExecute?: boolean // 执行时是否重置数据
}

/**
 * useAsync返回值类型
 */
export interface UseAsyncReturn<T> {
  // State
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<Error | null>

  // Computed
  isReady: Ref<boolean>
  isSuccess: Ref<boolean>
  isError: Ref<boolean>

  // Methods
  execute: (...args: any[]) => Promise<T | null>
  refresh: () => Promise<T | null>
  reset: () => void
  mutate: (newData: T | ((oldData: T | null) => T)) => void
}

/**
 * 异步数据加载Hook
 *
 * @param asyncFn - 异步函数
 * @param options - 加载选项
 * @returns 异步加载控制对象
 */
export function useAsync<T>(
  asyncFn: (...args: any[]) => Promise<T>,
  options: UseAsyncOptions<T> = {}
): UseAsyncReturn<T> {
  const {
    immediate = true,
    initialData = null,
    onSuccess,
    onError,
    resetOnExecute = false
  } = options

  const { error: showError } = useNotification()

  // ==================== State ====================

  const data = ref<T | null>(initialData) as Ref<T | null>
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const lastArgs = ref<any[]>([])

  // ==================== Computed ====================

  const isReady = computed(() => !loading.value && data.value !== null)

  const isSuccess = computed(() => !loading.value && !error.value && data.value !== null)

  const isError = computed(() => !loading.value && error.value !== null)

  // ==================== Methods ====================

  /**
   * 执行异步函数
   */
  async function execute(...args: any[]): Promise<T | null> {
    if (resetOnExecute) {
      data.value = null
    }

    loading.value = true
    error.value = null
    lastArgs.value = args

    try {
      const result = await asyncFn(...args)
      data.value = result

      // 调用成功回调
      onSuccess?.(result)

      return result
    } catch (err: any) {
      error.value = err instanceof Error ? err : new Error(err.message || '请求失败')

      // 显示错误消息
      showError(error.value.message)

      // 调用错误回调
      onError?.(error.value)

      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新数据（使用上次的参数重新执行）
   */
  async function refresh(): Promise<T | null> {
    return execute(...lastArgs.value)
  }

  /**
   * 重置状态
   */
  function reset(): void {
    data.value = initialData
    loading.value = false
    error.value = null
    lastArgs.value = []
  }

  /**
   * 手动更新数据（不触发网络请求）
   */
  function mutate(newData: T | ((oldData: T | null) => T)): void {
    if (typeof newData === 'function') {
      data.value = (newData as (oldData: T | null) => T)(data.value)
    } else {
      data.value = newData
    }
  }

  // ==================== Lifecycle ====================

  // 自动执行
  if (immediate) {
    onMounted(() => {
      execute()
    })
  }

  // ==================== Return ====================

  return {
    data,
    loading,
    error,
    isReady,
    isSuccess,
    isError,
    execute,
    refresh,
    reset,
    mutate
  }
}

/**
 * 列表数据加载Hook（带分页）
 *
 * @param asyncFn - 异步列表加载函数
 * @param options - 加载选项
 * @returns 列表加载控制对象
 */
export function useAsyncList<T>(
  asyncFn: (params: { page: number; pageSize: number }) => Promise<{
    items: T[]
    total: number
  }>,
  options: UseAsyncOptions<T[]> = {}
) {
  const list = ref<T[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  })

  const { error: showError } = useNotification()

  /**
   * 加载列表
   */
  async function loadList(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await asyncFn({
        page: pagination.value.page,
        pageSize: pagination.value.pageSize
      })

      list.value = response.items
      pagination.value.total = response.total

      options.onSuccess?.(response.items)
    } catch (err: any) {
      error.value = err instanceof Error ? err : new Error(err.message || '加载失败')
      showError(error.value.message)
      options.onError?.(error.value)
    } finally {
      loading.value = false
    }
  }

  /**
   * 切换页码
   */
  async function changePage(page: number): Promise<void> {
    pagination.value.page = page
    await loadList()
  }

  /**
   * 切换每页数量
   */
  async function changePageSize(pageSize: number): Promise<void> {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1 // 重置到第一页
    await loadList()
  }

  /**
   * 刷新当前页
   */
  async function refresh(): Promise<void> {
    await loadList()
  }

  /**
   * 重置到第一页
   */
  async function reset(): Promise<void> {
    pagination.value.page = 1
    await loadList()
  }

  // 自动加载
  if (options.immediate !== false) {
    onMounted(() => {
      loadList()
    })
  }

  return {
    list,
    loading,
    error,
    pagination,
    loadList,
    changePage,
    changePageSize,
    refresh,
    reset
  }
}

/**
 * 轮询数据Hook
 *
 * @param asyncFn - 异步函数
 * @param interval - 轮询间隔(毫秒)
 * @param options - 加载选项
 * @returns 轮询控制对象
 */
export function usePolling<T>(
  asyncFn: () => Promise<T>,
  interval: number = 3000,
  options: UseAsyncOptions<T> = {}
) {
  const asyncResult = useAsync(asyncFn, { ...options, immediate: false })
  const isPolling = ref(false)
  let pollingTimer: number | null = null

  /**
   * 开始轮询
   */
  function startPolling(): void {
    if (isPolling.value) return

    isPolling.value = true

    // 立即执行一次
    asyncResult.execute()

    // 设置定时器
    pollingTimer = window.setInterval(() => {
      asyncResult.execute()
    }, interval)
  }

  /**
   * 停止轮询
   */
  function stopPolling(): void {
    if (!isPolling.value) return

    isPolling.value = false

    if (pollingTimer !== null) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  /**
   * 重置并停止轮询
   */
  function reset(): void {
    stopPolling()
    asyncResult.reset()
  }

  // 组件卸载时自动停止轮询
  onMounted(() => {
    if (options.immediate !== false) {
      startPolling()
    }

    return () => {
      stopPolling()
    }
  })

  return {
    ...asyncResult,
    isPolling,
    startPolling,
    stopPolling,
    reset
  }
}
