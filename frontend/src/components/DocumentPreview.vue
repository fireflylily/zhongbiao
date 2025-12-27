<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    fullscreen
    :before-close="handleClose"
    destroy-on-close
    class="document-preview-dialog fullscreen-preview"
  >
    <div
      v-loading="loading"
      element-loading-text="正在加载文档..."
      class="preview-container"
    >
      <!-- 错误提示 -->
      <el-alert
        v-if="error"
        type="error"
        :title="error"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <!-- 预览主体：左侧目录 + 右侧编辑器 -->
      <div v-if="!error && previewContent" class="preview-body">
        <!-- 左侧目录 -->
        <div v-if="!outlineCollapsed" class="outline-sidebar">
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
              v-if="outline.length === 0"
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
        <div v-if="outlineCollapsed" class="outline-toggle" @click="outlineCollapsed = false">
          <el-icon><DArrowRight /></el-icon>
          <span class="toggle-text">展开目录</span>
        </div>

        <!-- 右侧编辑器预览 -->
        <div class="editor-preview-wrapper">
          <UmoEditor
            ref="editorRef"
            :document="{ readOnly: true }"
            @created="handleEditorCreated"
          />
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, DArrowLeft, DArrowRight } from '@element-plus/icons-vue'
import { UmoEditor } from '@umoteam/editor'

interface Props {
  modelValue: boolean
  fileUrl?: string
  fileName?: string
  htmlContent?: string  // 支持直接传入HTML内容
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  fileUrl: '',
  fileName: '文档预览',
  htmlContent: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 状态
const loading = ref(false)
const error = ref('')
const previewContent = ref('')
const editorRef = ref<any>(null)

// 目录相关
const outline = ref<any[]>([])
const outlineCollapsed = ref(false)  // 默认展开目录
const activeHeadingId = ref('')
const refreshingOutline = ref(false)

// 对话框显示状态（双向绑定）
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 对话框标题
const dialogTitle = computed(() => {
  return `文档预览 - ${props.fileName || '未命名文档'}`
})

// 将文件路径转换为API URL（简化版）
const convertFilePathToUrl = (filePath: string): string => {
  // 如果已经是完整的URL或API路径，直接返回
  if (filePath.startsWith('http://') ||
      filePath.startsWith('https://') ||
      filePath.startsWith('/api/')) {
    return filePath
  }

  // 特殊处理：将 /download/ 路径转换为API路径
  if (filePath.startsWith('/download/')) {
    const filename = filePath.substring(10)
    return `/api/files/serve/download/${filename}`
  }

  // 现在后端存储的是相对路径（ai_tender_system/data/...）
  // 直接构建API URL即可
  let apiPath = filePath

  // 如果是旧数据的绝对路径，移除绝对路径前缀（向下兼容）
  const absolutePrefixes = [
    '/Users/lvhe/Downloads/zhongbiao/zhongbiao/',
    '/var/www/ai-tender-system/'
  ]

  for (const prefix of absolutePrefixes) {
    if (apiPath.startsWith(prefix)) {
      apiPath = apiPath.substring(prefix.length)
      break
    }
  }

  // 移除 ai_tender_system/data/ 前缀（如果有）
  if (apiPath.startsWith('ai_tender_system/data/')) {
    apiPath = apiPath.substring('ai_tender_system/data/'.length)
  }

  // 处理 outputs 目录：转换为 download/ 前缀
  if (apiPath.startsWith('outputs/')) {
    apiPath = 'download/' + apiPath.substring('outputs/'.length)
  }

  // 构建API URL
  return `/api/files/serve/${apiPath}`
}

// 加载文档
const loadDocument = async () => {
  // 优先使用 HTML 内容
  if (props.htmlContent) {
    console.log('[DocumentPreview] 使用HTML内容预览')
    previewContent.value = props.htmlContent
    return
  }

  if (!props.fileUrl) {
    error.value = '文档地址不能为空'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('[DocumentPreview] 开始加载文档:', props.fileUrl)

    // 调用后端API将Word转换为HTML
    const response = await fetch('/api/editor/convert-word-to-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: props.fileUrl })
    })

    const result = await response.json()

    if (result.success && result.html_content) {
      previewContent.value = result.html_content
      console.log('[DocumentPreview] Word转HTML成功，长度:', result.html_content.length)
    } else {
      throw new Error(result.error || 'Word转HTML失败')
    }

    console.log('[DocumentPreview] 文档渲染成功')
  } catch (err: any) {
    console.error('[DocumentPreview] 文档预览失败:', err)
    error.value = `文档预览失败: ${err.message || '未知错误'}`
    ElMessage.error('文档预览失败，请检查文件是否正确或尝试下载后查看')
  } finally {
    loading.value = false
  }
}

// 编辑器创建完成事件
const handleEditorCreated = () => {
  console.log('[DocumentPreview] 编辑器已创建，设置内容...')

  if (editorRef.value && previewContent.value) {
    // 延迟设置内容，确保编辑器完全就绪
    setTimeout(() => {
      if (typeof editorRef.value.setContent === 'function') {
        editorRef.value.setContent(previewContent.value)
        console.log('[DocumentPreview] 内容已设置，长度:', previewContent.value.length)

        // 设置内容后刷新目录
        setTimeout(() => {
          refreshOutline()
        }, 500)
      } else {
        console.error('[DocumentPreview] setContent方法不可用')
      }
    }, 300)
  }
}

// 刷新目录
const refreshOutline = async () => {
  if (!editorRef.value) return

  refreshingOutline.value = true

  try {
    // 使用自定义HTML解析提取标题
    const html = editorRef.value.getHTML?.() || previewContent.value

    if (!html || html === '<p></p>') {
      outline.value = []
      return
    }

    // 创建临时DOM解析HTML
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')

    // 查找所有标题（h1-h6）
    const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6')

    outline.value = Array.from(headings).map((heading, index) => ({
      id: heading.id || `heading-${index}`,
      level: parseInt(heading.tagName[1]),  // h1 → 1, h2 → 2
      textContent: (heading.textContent || '').trim(),
      dom: null
    }))

    console.log('[DocumentPreview] 目录提取完成:', outline.value.length, '项')
  } catch (error) {
    console.error('[DocumentPreview] 获取目录失败:', error)
    outline.value = []
  } finally {
    refreshingOutline.value = false
  }
}

// 滚动到指定标题
const scrollToHeading = (item: any) => {
  if (!item) return

  try {
    // 通过ID查找
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

    // 通过内容查找（备选）
    const editorContainer = document.querySelector('.editor-preview-wrapper .umo-editor-container')
    if (editorContainer && item.textContent) {
      const headings = editorContainer.querySelectorAll('h1, h2, h3, h4, h5, h6')
      for (const heading of headings) {
        if (heading.textContent?.trim() === item.textContent) {
          heading.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
          activeHeadingId.value = item.id
          return
        }
      }
    }

    console.warn('[DocumentPreview] 无法滚动到标题:', item)
  } catch (error) {
    console.error('[DocumentPreview] 滚动失败:', error)
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}

// 监听对话框打开事件
watch(
  () => props.modelValue,
  async (newValue) => {
    if (newValue && (props.fileUrl || props.htmlContent)) {
      // 延迟加载，确保对话框已完全打开
      await nextTick()
      loadDocument()
    } else {
      // 关闭时清空内容
      error.value = ''
      previewContent.value = ''
      outline.value = []
      activeHeadingId.value = ''
    }
  }
)

// 监听内容加载完成，设置到编辑器
watch(
  () => previewContent.value,
  async (newContent) => {
    if (newContent && editorRef.value) {
      await nextTick()
      setTimeout(() => {
        if (editorRef.value && typeof editorRef.value.setContent === 'function') {
          editorRef.value.setContent(newContent)
          console.log('[DocumentPreview] 内容已通过watch设置，长度:', newContent.length)
          // 设置内容后刷新目录
          setTimeout(() => refreshOutline(), 500)
        }
      }, 300)
    }
  }
)
</script>

<style lang="scss">
// 全局样式（dialog teleport到body，需要全局样式）
.document-preview-dialog.fullscreen-preview {
  .el-dialog__body {
    padding: 0 !important;
    height: calc(100vh - 54px) !important;
    overflow: hidden !important;
  }

  .el-dialog__header {
    padding: 12px 20px;
    margin: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .preview-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }

  .preview-body {
    display: flex;
    height: 100%;
    overflow: hidden;
  }

  .outline-sidebar {
    width: 250px;
    min-width: 250px;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--el-bg-color);
    border-right: 1px solid var(--el-border-color);
    flex-shrink: 0;
    overflow: hidden;
  }

  .outline-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    flex-shrink: 0;

    h4 {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
    }
  }

  .outline-list {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 8px;
    min-height: 0;
  }

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

    &.level-4,
    &.level-5,
    &.level-6 {
      padding-left: 48px;
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

  .outline-footer {
    padding: 12px 16px;
    border-top: 1px solid var(--el-border-color-lighter);
    flex-shrink: 0;
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
    flex-shrink: 0;

    &:hover {
      background: var(--el-fill-color);
    }

    .toggle-text {
      writing-mode: vertical-rl;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }

  .editor-preview-wrapper {
    flex: 1;
    height: 100%;
    min-width: 0;
    background: #f5f5f5;
    overflow: hidden;  // 容器不滚动
    position: relative;

    .umo-editor-container {
      height: 100% !important;
      border: none;
      display: flex;
      flex-direction: column;
    }

    // 隐藏工具栏
    .umo-toolbar,
    .umo-menubar,
    .umo-editor-toolbar,
    .umo-tabs-container,
    .umo-ribbon {
      display: none !important;
    }

    // 隐藏底部状态栏
    .umo-statusbar,
    .umo-editor-footer,
    .umo-page-footer {
      display: none !important;
    }

    // 编辑器主体区域 - 让内部滚动
    .umo-editor-main {
      flex: 1;
      height: 100% !important;
      overflow: hidden;
    }

    // 编辑器内容区域 - 独立滚动
    .umo-editor-content,
    .umo-editor {
      height: 100% !important;
    }

    // ProseMirror 编辑器滚动容器
    .ProseMirror {
      overflow-y: auto !important;
      height: 100% !important;
    }

    // 页面容器滚动
    .umo-page-container,
    .umo-page-content {
      overflow-y: auto !important;
    }

    // 隐藏侧边栏和其他面板
    .umo-sidebar,
    .umo-toc-panel,
    .umo-outline-panel {
      display: none !important;
    }
  }
}
</style>
