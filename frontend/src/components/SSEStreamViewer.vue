<template>
  <div class="sse-stream-viewer" :class="{ 'is-loading': isStreaming }">
    <!-- 流式内容显示区域 -->
    <el-card class="stream-content" shadow="never">
      <div ref="contentRef" class="content-wrapper" v-html="formattedContent"></div>

      <!-- 流式加载指示器 -->
      <div v-if="isStreaming" class="streaming-indicator">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在生成中...</span>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div class="stream-actions" v-if="content">
      <el-button
        v-if="isStreaming"
        type="warning"
        :icon="VideoPause"
        @click="emit('stop')"
      >
        停止生成
      </el-button>

      <el-button
        v-else
        type="primary"
        :icon="CopyDocument"
        @click="handleCopy"
      >
        复制内容
      </el-button>

      <el-button
        v-if="!isStreaming && content"
        type="success"
        :icon="Download"
        @click="handleDownload"
      >
        下载文档
      </el-button>

      <el-button
        v-if="!isStreaming && content"
        :icon="RefreshRight"
        @click="emit('regenerate')"
      >
        重新生成
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  CopyDocument,
  Download,
  VideoPause,
  RefreshRight
} from '@element-plus/icons-vue'
import { marked } from 'marked'

interface Props {
  /** 流式内容 */
  content: string
  /** 是否正在流式传输 */
  isStreaming?: boolean
  /** 是否启用 Markdown 格式化 */
  enableMarkdown?: boolean
  /** 自动滚动到底部 */
  autoScroll?: boolean
}

interface Emits {
  (e: 'stop'): void
  (e: 'regenerate'): void
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  enableMarkdown: true,
  autoScroll: true
})

const emit = defineEmits<Emits>()

// 内容容器引用
const contentRef = ref<HTMLElement | null>(null)

// 格式化后的内容
const formattedContent = computed(() => {
  if (!props.content) return ''

  if (props.enableMarkdown) {
    try {
      // 使用 marked 解析 Markdown
      return marked.parse(props.content)
    } catch (error) {
      console.error('Markdown 解析失败:', error)
      return props.content
    }
  }

  // 如果不启用 Markdown，保留换行符
  return props.content.replace(/\n/g, '<br>')
})

// 监听内容变化，自动滚动
watch(() => props.content, async () => {
  if (props.autoScroll && props.isStreaming) {
    await nextTick()
    scrollToBottom()
  }
})

// 滚动到底部
const scrollToBottom = () => {
  if (contentRef.value) {
    contentRef.value.scrollTop = contentRef.value.scrollHeight
  }
}

// 复制内容
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

// 下载文档
const handleDownload = () => {
  try {
    const blob = new Blob([props.content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ai-content-${Date.now()}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('文档下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}
</script>

<style scoped lang="scss">

.sse-stream-viewer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;

  .stream-content {
    flex: 1;
    overflow: hidden;

    :deep(.el-card__body) {
      height: 100%;
      padding: 0;
    }

    .content-wrapper {
      height: 100%;
      padding: 20px;
      overflow-y: auto;
      font-size: 14px;
      line-height: 1.8;
      color: var(--el-text-color-primary);
      background: var(--el-bg-color);

      // Markdown 样式
      :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
        margin: 20px 0 10px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      :deep(h1) { font-size: 24px; }
      :deep(h2) { font-size: 20px; }
      :deep(h3) { font-size: 18px; }

      :deep(p) {
        margin: 10px 0;
      }

      :deep(ul), :deep(ol) {
        margin: 10px 0;
        padding-left: 20px;
      }

      :deep(li) {
        margin: 5px 0;
      }

      :deep(code) {
        padding: 2px 6px;
        background: var(--el-fill-color-light);
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
      }

      :deep(pre) {
        margin: 15px 0;
        padding: 15px;
        background: var(--el-fill-color-light);
        border-radius: 6px;
        overflow-x: auto;

        code {
          padding: 0;
          background: none;
        }
      }

      :deep(blockquote) {
        margin: 15px 0;
        padding: 10px 20px;
        border-left: 4px solid var(--el-color-primary);
        background: var(--el-fill-color-lighter);
        color: var(--el-text-color-secondary);
      }

      :deep(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;

        th, td {
          padding: 8px 12px;
          border: 1px solid var(--el-border-color);
        }

        th {
          background: var(--el-fill-color-light);
          font-weight: 600;
        }
      }

      :deep(a) {
        color: var(--el-color-primary);
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }

      :deep(hr) {
        margin: 20px 0;
        border: none;
        border-top: 1px solid var(--el-border-color);
      }
    }

    .streaming-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 20px;
      color: var(--el-color-primary);
      font-size: 14px;
      border-top: 1px solid var(--el-border-color-lighter);

      .el-icon {
        font-size: 16px;
      }
    }
  }

  .stream-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  &.is-loading {
    .content-wrapper {
      animation: pulse 1.5s ease-in-out infinite;
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.95;
  }
}
</style>
