<template>
  <div class="rich-text-editor" :class="{ fullscreen: isFullscreen, streaming: isStreaming }">
    <!-- 编辑器头部 -->
    <div class="editor-header">
      <div class="header-left">
        <h3>✏️ {{ title }}</h3>
        <el-tag v-if="isStreaming" type="primary" effect="plain">
          <el-icon class="is-loading"><Loading /></el-icon>
          AI生成中...
        </el-tag>
        <el-tag v-else-if="isDirty" type="warning">有未保存的修改</el-tag>
        <el-tag v-else type="success">已保存</el-tag>
      </div>

      <div class="header-actions">
        <el-button
          @click="toggleFullscreen"
          size="small"
        >
          <el-icon><FullScreen /></el-icon>
          {{ isFullscreen ? '退出全屏' : '全屏编辑' }}
        </el-button>

        <el-button
          type="primary"
          @click="emit('preview')"
          size="small"
          :disabled="!hasContent || isStreaming"
        >
          <el-icon><View /></el-icon>
          预览Word
        </el-button>

        <el-button
          type="success"
          @click="emit('export')"
          size="small"
          :disabled="!hasContent || isStreaming"
        >
          <el-icon><Download /></el-icon>
          导出Word
        </el-button>

        <el-button
          type="primary"
          :loading="saving"
          :disabled="!hasContent || isStreaming"
          @click="handleSave"
          size="small"
        >
          保存
        </el-button>
      </div>
    </div>

    <!-- 编辑器主体 -->
    <div class="editor-body">
      <!-- 左侧目录 -->
      <div v-if="showOutline && !outlineCollapsed" class="outline-sidebar">
        <div class="outline-header">
          <h4>📑 目录</h4>
          <el-button
            text
            size="small"
            @click="refreshOutline"
            :loading="refreshingOutline"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>

        <div class="outline-list">
          <div
            v-for="(item, index) in outline"
            :key="item.id || index"
            :class="['outline-item', `level-${item.level}`, { active: activeHeadingId === item.id }]"
            @click="scrollToHeading(item)"
          >
            <span class="outline-text">{{ item.textContent }}</span>
          </div>

          <el-empty
            v-if="outline.length === 0 && !isStreaming"
            description="暂无标题"
            :image-size="60"
          />
        </div>

        <div class="outline-footer">
          <el-button
            text
            size="small"
            @click="outlineCollapsed = true"
          >
            <el-icon><DArrowLeft /></el-icon>
            折叠目录
          </el-button>
        </div>
      </div>

      <!-- 展开按钮（折叠后显示） -->
      <div v-if="showOutline && outlineCollapsed" class="outline-toggle" @click="outlineCollapsed = false">
        <el-icon><DArrowRight /></el-icon>
        <span class="toggle-text">展开目录</span>
      </div>

      <!-- 右侧编辑器 -->
      <div class="editor-main">
        <!-- 流式指示器 -->
        <div v-if="isStreaming" class="streaming-indicator">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>AI 正在生成内容，请稍候...</span>
        </div>

        <!-- Umo Editor组件 -->
        <UmoEditor
          ref="umoEditorRef"
          v-bind="editorOptions"
          @changed="handleContentChange"
          @created="handleEditorCreated"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  View,
  Download,
  Refresh,
  DArrowLeft,
  DArrowRight,
  FullScreen
} from '@element-plus/icons-vue'
import { UmoEditor } from '@umoteam/editor'

interface Props {
  modelValue: string
  title?: string
  height?: number | string
  readonly?: boolean
  streaming?: boolean
  showOutline?: boolean
  companyId?: number        // 公司ID（用于AI助手）
  projectName?: string      // 项目名称（用于AI助手）
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'save', value: string): void
  (e: 'preview'): void
  (e: 'export'): void
  (e: 'ready'): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '文档编辑',
  height: 600,
  readonly: false,
  streaming: false,
  showOutline: true
})

const emit = defineEmits<Emits>()

// 状态
const umoEditorRef = ref<any>(null)
const content = ref(props.modelValue)
const isDirty = ref(false)
const saving = ref(false)
const isFullscreen = ref(false)
const isStreaming = computed(() => props.streaming)
const hasContent = computed(() => !!content.value && content.value !== '<p></p>')
const needsSwitchToPageLayout = ref(false)  // 标记是否需要切换到分页模式

// Umo Editor 配置选项 (v8.x)
// 完整类型定义：UmoEditorOptions (types/index.d.ts)
const editorOptions = computed(() => ({
  // 工具栏配置
  toolbar: {
    defaultMode: 'ribbon'
  },
  // 页面配置（使用官方文档的完整配置）
  page: {
    layouts: ['page', 'web'],           // 🔥 两种布局都支持（官方默认）
    defaultMargin: {
      left: 3.18,
      right: 3.18,
      top: 2.54,
      bottom: 2.54
    },
    defaultOrientation: 'portrait',
    defaultBackground: '#ffffff',
    showBreakMarks: true,
    showLineNumber: false,
    showToc: false,
    watermark: {
      type: 'compact',
      alpha: 0.2,
      fontColor: '#000',
      fontSize: 16,
      fontFamily: 'SimSun',
      fontWeight: 'normal',
      text: ''
    }
  },
  // 文档配置
  document: {
    enableSpellcheck: false,
    readOnly: props.readonly
  },
  // 文件配置 (FileOptions)
  file: {
    maxSize: 10 * 1024 * 1024,            // 最大 10MB
    allowedMimeTypes: [                   // 允许的文件类型
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp'
    ]
  },
  // 文件上传回调（顶级配置）- 必须是 async 函数
  onFileUpload: async (file: File) => {
    console.log('[RichTextEditor] 文件上传:', file.name, file.type)
    // 转换为 base64（避免服务器上传）
    return new Promise<{ id: string; url: string }>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const url = e.target?.result as string
        resolve({
          id: `img-${Date.now()}`,
          url: url
        })
      }
      reader.onerror = () => reject(new Error('读取失败'))
      reader.readAsDataURL(file)
    })
  },
  // 文件删除回调（顶级配置）- 必须是普通函数（非 async）
  onFileDelete: (file: any) => {
    // 只在file存在时打印日志（避免转换时的噪音日志）
    if (file) {
      console.log('[RichTextEditor] 文件删除:', file)
    }
    // 使用 base64，无需从服务器删除
    return true
  },

  // 【新增】AI 助手配置
  ai: {
    assistant: {
      enabled: true,  // 启用 AI 助手

      // 自定义指令列表（标书专用）
      commands: [
        // 标书专用指令
        {
          label: { en_US: 'Auto Fill', zh_CN: '智能填写' },
          value: { en_US: 'auto_fill', zh_CN: 'auto_fill' }
        },
        {
          label: { en_US: 'Generate Table', zh_CN: '生成表格' },
          value: { en_US: 'generate_table', zh_CN: 'generate_table' }
        },
        // 保留通用指令
        {
          label: { en_US: 'Rewrite', zh_CN: '重写' },
          value: { en_US: 'rewrite', zh_CN: 'rewrite' }
        },
        {
          label: { en_US: 'Expansion', zh_CN: '扩写' },
          value: { en_US: 'expand', zh_CN: 'expand' }
        },
        {
          label: { en_US: 'Summarize', zh_CN: '总结' },
          value: { en_US: 'summarize', zh_CN: 'summarize' }
        },
        {
          label: { en_US: 'Polish', zh_CN: '润色' },
          value: { en_US: 'polish', zh_CN: 'polish' }
        },
        {
          label: { en_US: 'Translate', zh_CN: '翻译' },
          value: { en_US: 'translate', zh_CN: 'translate' }
        }
      ],

      // AI 消息处理回调（核心方法）
      onMessage: async (payload: any, content: string) => {
        console.log('[AI Assistant] 收到请求:', payload)

        try {
          const { command, lang, input, output } = payload

          // 调用后端 AI API
          const response = await fetch('/api/editor/ai-assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              command,           // AI 操作类型（如：rewrite, expand, summarize）
              input,             // 用户选中的文本
              output,            // 输出格式（HTML）
              lang,              // 语言设置
              company_id: props.companyId || 1,      // 当前公司ID
              project_name: props.projectName || ''  // 当前项目名称
            })
          })

          if (!response.ok) {
            throw new Error('AI 请求失败')
          }

          const result = await response.json()

          if (result.success) {
            console.log('[AI Assistant] 生成成功:', result.content.substring(0, 100))
            return result.content  // 返回 AI 生成的内容（HTML格式）
          } else {
            ElMessage.error(result.error || 'AI 生成失败')
            return input  // 失败时返回原始内容
          }

        } catch (error: any) {
          console.error('[AI Assistant] 错误:', error)
          ElMessage.error('AI 助手调用失败: ' + error.message)
          return payload.input  // 出错时返回原始内容
        }
      }
    }
  }
}))

// 目录相关
const outline = ref<any[]>([])
const outlineCollapsed = ref(false)
const activeHeadingId = ref('')
const refreshingOutline = ref(false)

// 编辑器高度
const editorHeight = computed(() => {
  if (isFullscreen.value) {
    return 'calc(100vh - 120px)'
  }
  return typeof props.height === 'number' ? `${props.height}px` : props.height
})

// 文件上传处理
const handleFileUpload = async (file: File): Promise<string> => {
  console.log('[RichTextEditor] 处理文件上传:', file.name, file.type)

  try {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.warning('仅支持上传图片文件')
      throw new Error('不支持的文件类型')
    }

    // 检查文件大小（限制5MB）
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.warning('图片大小不能超过5MB')
      throw new Error('文件太大')
    }

    // 转换为DataURL（base64）
    return new Promise((resolve, reject) => {
      const reader = new FileReader()

      reader.onload = (e) => {
        const result = e.target?.result as string
        console.log('[RichTextEditor] 图片转换成功，大小:', result.length)
        resolve(result)
      }

      reader.onerror = () => {
        console.error('[RichTextEditor] 图片读取失败')
        ElMessage.error('图片读取失败')
        reject(new Error('读取失败'))
      }

      reader.readAsDataURL(file)
    })

    // TODO: 如果需要上传到服务器，使用以下代码：
    /*
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/upload-image', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()
    if (result.success) {
      return result.url  // 返回服务器上的图片URL
    } else {
      throw new Error(result.error || '上传失败')
    }
    */
  } catch (error: any) {
    console.error('[RichTextEditor] 文件上传失败:', error)
    throw error
  }
}

// 监听外部内容变化
watch(() => props.modelValue, (newValue) => {
  if (newValue && newValue !== content.value) {
    content.value = newValue
    isDirty.value = false

    // 通过编辑器实例更新内容
    if (umoEditorRef.value) {
      setEditorContent(newValue)
    }
  }
})

// 监听流式状态变化
watch(isStreaming, (streaming) => {
  console.log('[RichTextEditor] 流式状态变化:', streaming)
  // 使用setReadOnly设置只读状态
  if (umoEditorRef.value && typeof umoEditorRef.value.setReadOnly === 'function') {
    umoEditorRef.value.setReadOnly(streaming || props.readonly)
  }
})

// ===== Umo Editor v8 事件处理 =====

// 编辑器创建完成事件（替代watch监听器）
const handleEditorCreated = () => {
  console.log('[RichTextEditor] ✅ 编辑器创建完成 (@created事件)')

  // 统一在创建后切换到分页模式，保留延迟以确保编辑器就绪
  setTimeout(() => {
    switchToPageLayout()
  }, 300)

  // 设置初始内容
  if (props.modelValue) {
    // 延迟设置内容，确保布局切换先生效
    setTimeout(() => {
      setEditorContent(props.modelValue)
    }, 100)
  }

  // 设置只读状态
  if (props.readonly || props.streaming) {
    if (umoEditorRef.value && typeof umoEditorRef.value.setReadOnly === 'function') {
      umoEditorRef.value.setReadOnly(true)
    }
  }

  // 触发就绪事件
  emit('ready')
  console.log('[RichTextEditor] 编辑器就绪')

  // 初始化时刷新目录
  setTimeout(() => {
    refreshOutline()
  }, 800)
}

// 切换到分页模式的辅助函数
const switchToPageLayout = () => {
  if (!umoEditorRef.value) return

  try {
    if (typeof umoEditorRef.value.setLayout === 'function') {
      umoEditorRef.value.setLayout('page')
      console.log('[RichTextEditor] ✅ 已切换到分页模式')
      needsSwitchToPageLayout.value = false // 更新状态

      // 切换后手动添加CSS类（确保分页视图生效）
      setTimeout(() => {
        const container = document.querySelector('.umo-editor-container')
        if (container) {
          container.classList.add('umo-page-mode')
          container.classList.remove('umo-continuous-mode')
          console.log('[RichTextEditor] 已添加 umo-page-mode 类')
        }
        console.log('[RichTextEditor] 分页模式DOM应该已更新')
      }, 500)
    } else {
      console.warn('[RichTextEditor] setLayout方法不可用')
    }
  } catch (error) {
    console.error('[RichTextEditor] 切换分页模式失败:', error)
  }
}

// 内容变化事件（替代editor.on('update')）
const handleContentChange = () => {
  console.log('[RichTextEditor] ✨ 内容变化 (@changed事件)')

  if (!umoEditorRef.value) return

  try {
    const html = umoEditorRef.value.getHTML()
    console.log('[RichTextEditor] 当前内容长度:', html.length)
    console.log('[RichTextEditor] 之前内容长度:', content.value.length)

    if (html !== content.value) {
      content.value = html
      isDirty.value = true
      console.log('[RichTextEditor] ✅ isDirty设置为true')
      emit('update:modelValue', html)

      // 防抖更新目录
      debouncedRefreshOutline()
    } else {
      console.log('[RichTextEditor] ⚠️ 内容未变化，不更新isDirty')
    }
  } catch (error) {
    console.error('[RichTextEditor] 处理内容变化失败:', error)
  }
}

// 设置编辑器内容
const setEditorContent = (html: string) => {
  if (!umoEditorRef.value) {
    console.warn('[RichTextEditor] 编辑器未就绪')
    return
  }

  try {
    // 先清理localStorage（关键！）
    cleanupLocalStorage()

    // 使用官方API setContent
    if (typeof umoEditorRef.value.setContent === 'function') {
      umoEditorRef.value.setContent(html)
      console.log('[RichTextEditor] 内容已更新，长度:', html.length)

      // 设置后立即再次清理，防止自动保存
      setTimeout(() => {
        cleanupLocalStorage()
      }, 100)
    } else {
      console.error('[RichTextEditor] setContent方法不存在')
    }
  } catch (error) {
    console.error('[RichTextEditor] 设置内容失败:', error)
    // 如果还是localStorage错误，强制清理并重试
    if (error.name === 'QuotaExceededError') {
      console.warn('[RichTextEditor] localStorage超限，清理后重试')
      cleanupLocalStorage()
      try {
        umoEditorRef.value.setContent(html)
      } catch (retryError) {
        console.error('[RichTextEditor] 重试仍然失败:', retryError)
      }
    }
  }
}

// 追加内容（流式）
const appendContent = (html: string) => {
  if (!umoEditorRef.value) {
    console.warn('[RichTextEditor] 编辑器未就绪，内容已缓存')
    content.value += html
    return
  }

  try {
    // 获取当前内容
    const currentHtml = umoEditorRef.value.getHTML()
    const newHtml = currentHtml + html

    // 设置新内容
    umoEditorRef.value.setContent(newHtml)
    content.value = newHtml

    console.log('[RichTextEditor] 内容已追加，当前长度:', newHtml.length)

    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })

    // 更新目录
    debouncedRefreshOutline()
  } catch (error) {
    console.error('[RichTextEditor] 追加内容失败:', error)
  }
}

// 滚动到底部
const scrollToBottom = () => {
  try {
    const editor = umoEditorRef.value?.getEditor()
    if (editor && editor.view) {
      const { dom } = editor.view
      dom.scrollTop = dom.scrollHeight
    }
  } catch (error) {
    console.error('[RichTextEditor] 滚动失败:', error)
  }
}

// 刷新目录
let refreshTimer: number | null = null
const debouncedRefreshOutline = () => {
  if (refreshTimer) clearTimeout(refreshTimer)
  refreshTimer = window.setTimeout(() => {
    refreshOutline()
  }, 500)
}

const refreshOutline = async () => {
  if (!umoEditorRef.value) return

  // 如果不显示大纲，跳过刷新
  if (!props.showOutline) return

  refreshingOutline.value = true

  try {
    // 使用Umo Editor的官方API getTableOfContents
    if (typeof umoEditorRef.value.getTableOfContents === 'function') {
      const toc = umoEditorRef.value.getTableOfContents()
      outline.value = toc || []
      console.log('[RichTextEditor] 目录更新:', outline.value.length, '项', toc)
    } else {
      console.warn('[RichTextEditor] getTableOfContents方法不可用')
      outline.value = []
    }
  } catch (error) {
    console.error('[RichTextEditor] 获取目录失败:', error)
    outline.value = []
  } finally {
    refreshingOutline.value = false
  }
}

// 滚动到指定标题
const scrollToHeading = (item: any) => {
  if (!item) return

  try {
    // 方法1：使用DOM引用
    if (item.dom && typeof item.dom.scrollIntoView === 'function') {
      item.dom.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
      activeHeadingId.value = item.id
      return
    }

    // 方法2：通过ID查找
    if (item.id) {
      const element = document.getElementById(item.id)
      if (element) {
        element.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        })
        activeHeadingId.value = item.id
        return
      }
    }

    console.warn('[RichTextEditor] 无法滚动到标题:', item)
  } catch (error) {
    console.error('[RichTextEditor] 滚动失败:', error)
  }
}

// 保存
const handleSave = async () => {
  if (!isDirty.value || isStreaming.value) return

  saving.value = true
  try {
    emit('save', content.value)
    await nextTick()
    isDirty.value = false
  } catch (error) {
    console.error('[RichTextEditor] 保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 自动保存（编辑器内置的保存事件）
const handleAutoSave = () => {
  console.log('[RichTextEditor] 触发自动保存')
  // 可以在这里实现自动保存逻辑
}

// 全屏切换
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value

  if (isFullscreen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

// 清空内容
const clear = () => {
  content.value = ''
  setEditorContent('')
  outline.value = []
  isDirty.value = false
}

// 获取内容
const getContent = (): string => {
  try {
    if (umoEditorRef.value && typeof umoEditorRef.value.getHTML === 'function') {
      return umoEditorRef.value.getHTML()
    }
  } catch (error) {
    console.error('[RichTextEditor] 获取内容失败:', error)
  }

  return content.value
}

// 设置内容
const setContent = (html: string) => {
  content.value = html
  setEditorContent(html)
  isDirty.value = false

  // 更新目录
  setTimeout(() => {
    refreshOutline()
  }, 300)
}

// 设置流式状态
const setStreaming = (streaming: boolean) => {
  // editorOptions会自动响应isStreaming的变化
  console.log('[RichTextEditor] 设置流式状态:', streaming)
}

// 获取底层编辑器实例
const getEditor = () => {
  return umoEditorRef.value?.getEditor?.()
}

// 插入原生分页符
const insertPageBreak = () => {
  try {
    let editor = getEditor()

    // 解包 RefImpl
    if (editor && editor.__v_isRef) {
      editor = editor.value
    }

    if (editor && editor.commands && editor.commands.setPageBreak) {
      editor.commands.setPageBreak()
      console.log('[RichTextEditor] 已插入原生分页符')
      return true
    } else {
      console.warn('[RichTextEditor] setPageBreak 命令不可用')
      return false
    }
  } catch (error) {
    console.error('[RichTextEditor] 插入分页符失败:', error)
    return false
  }
}

// 暴露方法给父组件
defineExpose({
  getContent,
  setContent,
  appendContent,
  clear,
  refreshOutline,
  setStreaming,
  getEditor,  // 暴露底层编辑器实例
  insertPageBreak  // 新增：插入原生分页符
})

// 清理localStorage中的Umo Editor数据
const cleanupLocalStorage = () => {
  try {
    const keys = Object.keys(localStorage)
    for (const key of keys) {
      if (key.startsWith('umo-editor:')) {
        localStorage.removeItem(key)
      }
    }
  } catch (error) {
    console.error('[RichTextEditor] 清理localStorage失败:', error)
  }
}

// 拦截localStorage.setItem，阻止Umo Editor写入大数据
const originalSetItem = localStorage.setItem
let hasWarnedAboutStorage = false

const blockUmoEditorStorage = () => {
  localStorage.setItem = function(key: string, value: string) {
    // 阻止Umo Editor的自动保存
    if (key.startsWith('umo-editor:')) {
      // 只在第一次警告，避免日志刷屏
      if (!hasWarnedAboutStorage) {
        console.warn('[RichTextEditor] 已阻止 Umo Editor 写入 localStorage（大小:', value.length, '字节），后续将静默阻止')
        hasWarnedAboutStorage = true
      }
      return // 直接返回，不保存
    }
    // 其他数据正常保存
    return originalSetItem.call(localStorage, key, value)
  }
  console.log('[RichTextEditor] localStorage 保护已启用')
}

// 恢复localStorage.setItem
const restoreLocalStorage = () => {
  localStorage.setItem = originalSetItem
  console.log('[RichTextEditor] localStorage拦截器已移除')
}

// 生命周期
onMounted(() => {
  // 启动localStorage拦截器（阻止Umo Editor写入）
  blockUmoEditorStorage()

  // 清理旧的localStorage数据
  cleanupLocalStorage()
})

onBeforeUnmount(() => {
  if (isFullscreen.value) {
    document.body.style.overflow = ''
  }

  if (refreshTimer) {
    clearTimeout(refreshTimer)
  }

  // 恢复localStorage
  restoreLocalStorage()

  // 清理localStorage
  cleanupLocalStorage()
})
</script>

<style scoped lang="scss">
.rich-text-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 9999;
    border-radius: 0;
  }

  &.streaming {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
  }

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: var(--el-fill-color-light);
    border-bottom: 1px solid var(--el-border-color);

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .editor-body {
    display: flex;
    flex: 1;
    overflow: hidden;

    .outline-sidebar {
      width: 250px;
      display: flex;
      flex-direction: column;
      background: var(--el-bg-color);
      border-right: 1px solid var(--el-border-color);

      .outline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid var(--el-border-color-lighter);

        h4 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
        }
      }

      .outline-list {
        flex: 1;
        overflow-y: auto;
        padding: 8px;

        .outline-item {
          padding: 8px 12px;
          margin: 4px 0;
          cursor: pointer;
          border-radius: 4px;
          font-size: 13px;
          line-height: 1.5;
          color: var(--el-text-color-regular);
          transition: all 0.2s;
          word-break: break-word;

          &:hover {
            background: var(--el-fill-color-light);
            color: var(--el-text-color-primary);
          }

          &.active {
            background: var(--el-color-primary-light-9);
            color: var(--el-color-primary);
            font-weight: 600;
          }

          &.level-1 {
            font-weight: 600;
            font-size: 14px;
          }

          &.level-2 {
            padding-left: 24px;
            font-size: 13px;
          }

          &.level-3 {
            padding-left: 36px;
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }

          .outline-text {
            display: block;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }

      .outline-footer {
        padding: 12px 16px;
        border-top: 1px solid var(--el-border-color-lighter);
      }
    }

    .outline-toggle {
      width: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--el-fill-color-light);
      border-right: 1px solid var(--el-border-color);
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background: var(--el-fill-color);
      }

      .toggle-text {
        writing-mode: vertical-rl;
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }

    .editor-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;

      .streaming-indicator {
        position: absolute;
        top: 12px;
        right: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--el-color-primary);
        color: white;
        border-radius: 20px;
        font-size: 12px;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
        z-index: 1000;

        .el-icon {
          font-size: 16px;
        }
      }

      // 【修复】强制隐藏Umo Editor内置的目录/大纲面板（避免与我们自己的目录重复）
      :deep(.umo-toc-panel),
      :deep(.umo-outline-panel),
      :deep(.umo-toc-sidebar),
      :deep([class*="toc-panel"]),
      :deep([class*="outline-panel"]) {
        display: none !important;
      }
    }
  }
}
</style>
