/**
 * SSE流式处理Composable
 *
 * 封装SSE（Server-Sent Events）流式数据处理逻辑
 */

import { ref, onUnmounted, type Ref } from 'vue'
import type { SSEEvent, SSEProgressEvent } from '@/types'

/**
 * SSE事件处理器类型
 */
export interface SSEHandlers {
  onMessage?: (data: any) => void
  onProgress?: (event: SSEProgressEvent) => void
  onComplete?: (result: any) => void
  onError?: (error: Error) => void
  onOpen?: () => void
}

/**
 * SSE连接配置
 */
export interface SSEOptions {
  reconnect?: boolean // 是否自动重连
  reconnectDelay?: number // 重连延迟(毫秒)
  maxReconnectAttempts?: number // 最大重连次数
}

/**
 * useSSE返回值类型
 */
export interface UseSSEReturn {
  isConnected: Ref<boolean>
  progress: Ref<number>
  status: Ref<'idle' | 'connecting' | 'connected' | 'error' | 'completed'>
  error: Ref<Error | null>
  result: Ref<any>
  connect: (url: string) => void
  disconnect: () => void
}

/**
 * SSE流式处理Hook
 *
 * @param handlers - 事件处理器
 * @param options - 配置选项
 * @returns SSE连接控制对象
 */
export function useSSE(
  handlers: SSEHandlers = {},
  options: SSEOptions = {}
): UseSSEReturn {
  // 配置默认值
  const {
    reconnect = false,
    reconnectDelay = 3000,
    maxReconnectAttempts = 3
  } = options

  // ==================== State ====================

  const eventSource = ref<EventSource | null>(null)
  const isConnected = ref(false)
  const progress = ref(0)
  const status = ref<'idle' | 'connecting' | 'connected' | 'error' | 'completed'>(
    'idle'
  )
  const error = ref<Error | null>(null)
  const result = ref<any>(null)
  const reconnectAttempts = ref(0)

  // ==================== Methods ====================

  /**
   * 连接到SSE端点
   */
  function connect(url: string): void {
    if (eventSource.value) {
      disconnect()
    }

    status.value = 'connecting'
    error.value = null

    try {
      eventSource.value = new EventSource(url)

      // 连接打开事件
      eventSource.value.addEventListener('open', handleOpen)

      // 消息事件
      eventSource.value.addEventListener('message', handleMessage)

      // 错误事件
      eventSource.value.addEventListener('error', handleError)
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('连接失败')
      status.value = 'error'
      handlers.onError?.(error.value)
    }
  }

  /**
   * 断开SSE连接
   */
  function disconnect(): void {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

    isConnected.value = false
    status.value = 'idle'
    reconnectAttempts.value = 0
  }

  /**
   * 处理连接打开
   */
  function handleOpen(): void {
    isConnected.value = true
    status.value = 'connected'
    reconnectAttempts.value = 0
    handlers.onOpen?.()
  }

  /**
   * 处理消息
   */
  function handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data)

      // 调用通用消息处理器
      handlers.onMessage?.(data)

      // 处理进度事件
      if (data.progress !== undefined) {
        progress.value = data.progress
        handlers.onProgress?.(data as SSEProgressEvent)
      }

      // 处理完成事件
      if (data.status === 'completed') {
        status.value = 'completed'
        result.value = data.result || data
        handlers.onComplete?.(result.value)
        disconnect()
      }

      // 处理失败事件
      if (data.status === 'failed' || data.error) {
        const errorMsg = data.error || data.message || '任务失败'
        error.value = new Error(errorMsg)
        status.value = 'error'
        handlers.onError?.(error.value)
        disconnect()
      }
    } catch (err) {
      console.error('解析SSE消息失败:', err)
      error.value = err instanceof Error ? err : new Error('消息解析失败')
      handlers.onError?.(error.value)
    }
  }

  /**
   * 处理错误
   */
  function handleError(event: Event): void {
    isConnected.value = false
    status.value = 'error'

    const errorInstance = new Error('SSE连接错误')
    error.value = errorInstance

    // 尝试重连
    if (reconnect && reconnectAttempts.value < maxReconnectAttempts) {
      reconnectAttempts.value += 1
      console.log(
        `SSE连接断开，${reconnectDelay}ms后尝试第${reconnectAttempts.value}次重连...`
      )

      setTimeout(() => {
        if (eventSource.value) {
          const url = eventSource.value.url
          connect(url)
        }
      }, reconnectDelay)
    } else {
      handlers.onError?.(errorInstance)
      disconnect()
    }
  }

  /**
   * 重置状态
   */
  function reset(): void {
    disconnect()
    progress.value = 0
    status.value = 'idle'
    error.value = null
    result.value = null
  }

  // ==================== Lifecycle ====================

  // 组件卸载时自动断开连接
  onUnmounted(() => {
    disconnect()
  })

  // ==================== Return ====================

  return {
    isConnected,
    progress,
    status,
    error,
    result,
    connect,
    disconnect
  }
}

/**
 * 简化版SSE Hook - 用于常见的进度监听场景
 *
 * @param url - SSE端点URL
 * @param onProgress - 进度回调
 * @param onComplete - 完成回调
 * @param onError - 错误回调
 * @returns SSE连接控制对象
 */
export function useSSEProgress(
  url: string,
  onProgress: (progress: number, message?: string) => void,
  onComplete: (result: any) => void,
  onError?: (error: Error) => void
): UseSSEReturn {
  return useSSE({
    onProgress: (event) => {
      onProgress(event.progress, event.message)
    },
    onComplete,
    onError
  })
}
