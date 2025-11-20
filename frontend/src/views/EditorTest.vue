<template>
  <div class="editor-test-page">
    <el-card shadow="never">
      <template #header>
        <h2>📝 编辑器 & 分页符测试</h2>
      </template>

      <!-- 测试选项 -->
      <el-tabs v-model="activeTab" type="card">
        <!-- Tab 1: Word文档上传测试 -->
        <el-tab-pane label="Word文档测试" name="word">
          <el-alert type="info" :closable="false" style="margin-bottom: 16px">
            💡 上传一个包含分页符的Word文档，测试分页符是否正确显示
          </el-alert>

          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".doc,.docx"
            :on-change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽Word文档到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                仅支持 .doc / .docx 格式文件
              </div>
            </template>
          </el-upload>

          <el-button
            v-if="selectedFile"
            type="primary"
            :loading="converting"
            @click="convertWordToHtml"
            style="margin-top: 16px"
          >
            转换并加载到编辑器
          </el-button>
        </el-tab-pane>

        <!-- Tab 2: 手动分页符测试 -->
        <el-tab-pane label="手动分页符测试" name="manual">
          <el-alert type="info" :closable="false" style="margin-bottom: 16px">
            💡 点击下方按钮加载包含分页符的测试内容
          </el-alert>

          <el-button type="primary" @click="loadTestContentWithBreaks">
            加载测试内容（带分页符）
          </el-button>
          <el-button @click="insertPageBreak" :disabled="!editorRef">
            插入HR分页符
          </el-button>
          <el-button @click="insertNativePageBreak" :disabled="!editorRef" type="success">
            插入原生分页符（实验）
          </el-button>
          <el-button @click="debugEditor" :disabled="!editorRef" type="warning">
            调试编辑器API
          </el-button>
          <el-button @click="forcePageMode" :disabled="!editorRef" type="danger">
            强制启用分页模式
          </el-button>
          <el-button @click="clearEditor" :disabled="!editorRef">
            清空编辑器
          </el-button>
        </el-tab-pane>

        <!-- Tab 3: 长文档分页测试 -->
        <el-tab-pane label="长文档测试" name="long">
          <el-alert type="info" :closable="false" style="margin-bottom: 16px">
            💡 加载超长文档，测试编辑器性能和分页布局
          </el-alert>

          <el-button type="primary" @click="loadLongContent">
            加载长文档（4章节）
          </el-button>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 转换日志 -->
    <el-card v-if="conversionLog" shadow="never" style="margin-top: 16px">
      <template #header>
        <h3>转换日志</h3>
      </template>
      <pre style="white-space: pre-wrap; font-size: 12px;">{{ conversionLog }}</pre>
    </el-card>

    <!-- 编辑器 -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <h3>富文本编辑器</h3>
      </template>
      <div class="editor-container">
        <RichTextEditor
          ref="editorRef"
          v-model="editorContent"
          title="测试文档"
          :height="800"
          @ready="handleEditorReady"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { RichTextEditor } from '@/components'
import type { UploadFile } from 'element-plus'

const editorRef = ref<any>(null)
const editorContent = ref('')
const activeTab = ref('word')
const selectedFile = ref<File | null>(null)
const converting = ref(false)
const conversionLog = ref('')

// 处理文件选择
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    selectedFile.value = file.raw
    ElMessage.success(`已选择文件: ${file.name}`)
  }
}

// 转换Word为HTML
const convertWordToHtml = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择Word文档')
    return
  }

  converting.value = true
  conversionLog.value = '正在转换Word文档...\n'

  try {
    // 先上传文件（获取服务器路径）
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const uploadResponse = await fetch('/api/editor/upload-temp', {
      method: 'POST',
      body: formData
    })

    if (!uploadResponse.ok) {
      throw new Error('文件上传失败')
    }

    const uploadResult = await uploadResponse.json()
    const filePath = uploadResult.file_path

    conversionLog.value += `✓ 文件已上传: ${filePath}\n`
    conversionLog.value += '正在转换为HTML...\n'

    // 调用Word转HTML API
    const convertResponse = await fetch('/api/editor/convert-word-to-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath })
    })

    const result = await convertResponse.json()

    if (result.success && result.html_content) {
      conversionLog.value += `✓ 转换成功！HTML长度: ${result.html_content.length}\n`

      // 检查分页符数量
      const pageBreakCount = (result.html_content.match(/page-break/g) || []).length
      conversionLog.value += `✓ 检测到 ${pageBreakCount} 个分页符\n`

      // 加载到编辑器
      editorContent.value = result.html_content

      if (editorRef.value) {
        editorRef.value.setContent(result.html_content)
      }

      ElMessage.success('Word文档已加载到编辑器')
    } else {
      throw new Error(result.error || '转换失败')
    }
  } catch (error: any) {
    conversionLog.value += `❌ 错误: ${error.message}\n`
    ElMessage.error('转换失败: ' + error.message)
  } finally {
    converting.value = false
  }
}

// 加载测试内容（带分页符）
const loadTestContentWithBreaks = () => {
  const testContent = `
<h1>第一章 项目概述</h1>
<p>这是第一章的内容。我们将在这里介绍项目的基本情况和背景。</p>
<p>项目名称：智能标书管理系统</p>
<p>项目目标：提高标书编写效率，降低人工成本。</p>

<hr data-type="page-break" />

<h1>第二章 技术方案</h1>
<p>本章介绍我们采用的技术方案和架构设计。</p>
<h2>2.1 系统架构</h2>
<p>系统采用前后端分离架构，前端使用Vue3 + TypeScript，后端使用Python Flask。</p>
<h2>2.2 技术栈</h2>
<ul>
  <li>前端：Vue3 + Element Plus + UmoEditor</li>
  <li>后端：Python Flask + SQLAlchemy</li>
  <li>数据库：SQLite / MySQL</li>
</ul>

<hr data-type="page-break" />

<h1>第三章 实施计划</h1>
<p>本章描述项目的实施计划和时间安排。</p>
<table>
  <tr>
    <th>阶段</th>
    <th>任务</th>
    <th>时间</th>
  </tr>
  <tr>
    <td>第一阶段</td>
    <td>需求分析</td>
    <td>2周</td>
  </tr>
  <tr>
    <td>第二阶段</td>
    <td>系统开发</td>
    <td>8周</td>
  </tr>
  <tr>
    <td>第三阶段</td>
    <td>测试上线</td>
    <td>2周</td>
  </tr>
</table>

<hr data-type="page-break" />

<h1>第四章 总结</h1>
<p>通过本项目的实施，将大幅提升标书编写效率。</p>
<p><strong>预期成果：</strong></p>
<ul>
  <li>标书编写时间缩短50%</li>
  <li>错误率降低80%</li>
  <li>用户满意度提升</li>
</ul>
  `

  editorContent.value = testContent
  if (editorRef.value) {
    editorRef.value.setContent(testContent)
  }

  ElMessage.success('测试内容已加载（包含3个分页符）')
}

// 插入分页符
const insertPageBreak = () => {
  if (!editorRef.value) {
    ElMessage.warning('编辑器未就绪')
    return
  }

  const pageBreakHtml = '<hr data-type="page-break" />'

  // 获取当前内容并在末尾追加分页符
  const currentContent = editorRef.value.getContent()
  const newContent = currentContent + pageBreakHtml

  editorRef.value.setContent(newContent)
  ElMessage.success('已插入分页符')
}

// 清空编辑器
const clearEditor = () => {
  editorContent.value = ''
  if (editorRef.value) {
    editorRef.value.clear()
  }
  ElMessage.success('编辑器已清空')
}

// 加载长文档（超长内容测试多页效果）
const loadLongContent = () => {
  const longParagraph = '<p>' + '这是一个很长的段落内容。'.repeat(50) + '</p>\n'

  const longContent = `
<h1>第一章 项目背景</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第二章 需求分析</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第三章 技术方案</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第四章 实施计划</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第五章 总结</h1>
${longParagraph.repeat(30)}
  `

  editorContent.value = longContent
  if (editorRef.value) {
    editorRef.value.setContent(longContent)
  }

  ElMessage.success('超长文档已加载（包含原生分页符）')
}

// 插入原生分页符（使用Umo Editor的API）
const insertNativePageBreak = () => {
  if (!editorRef.value) {
    ElMessage.warning('编辑器未就绪')
    return
  }

  try {
    console.log('[EditorTest] 准备插入原生分页符...')

    // 直接使用RichTextEditor组件暴露的insertPageBreak方法
    const success = editorRef.value.insertPageBreak()

    console.log('[EditorTest] insertPageBreak 返回:', success)

    if (success) {
      ElMessage.success('✅ 已插入原生分页符')

      // 获取内容并分析
      setTimeout(() => {
        const html = editorRef.value.getContent()
        console.log('[EditorTest] 当前HTML长度:', html.length)

        // 查找所有分页符
        const pageBreaks = html.match(/<div class="umo-page-break"[^>]*>/g)
        console.log('[EditorTest] 找到分页符数量:', pageBreaks?.length || 0)

        if (pageBreaks && pageBreaks.length > 0) {
          console.log('[EditorTest] 分页符HTML:', pageBreaks)
        }

        // 查看DOM中的分页符
        const container = document.querySelector('[contenteditable="true"]')
        if (container) {
          const domBreaks = container.querySelectorAll('.umo-page-break')
          console.log('[EditorTest] DOM中的分页符数量:', domBreaks.length)
        }
      }, 200)
    } else {
      ElMessage.error('插入失败，返回false')
    }
  } catch (error: any) {
    console.error('插入原生分页符失败:', error)
    ElMessage.error('插入失败: ' + error.message)
  }
}

// 调试编辑器（输出可用的方法和命令）
const debugEditor = () => {
  if (!editorRef.value) {
    ElMessage.warning('编辑器未就绪')
    return
  }

  console.log('========== 编辑器调试信息 ==========')
  console.log('1. editorRef 方法:', Object.keys(editorRef.value).filter(k => typeof editorRef.value[k] === 'function'))

  let editor = editorRef.value.getEditor()

  // 解包 RefImpl
  if (editor && editor.__v_isRef) {
    console.log('2a. 检测到RefImpl，正在解包...')
    editor = editor.value
  }

  if (editor) {
    console.log('2. 底层编辑器类型:', editor.constructor?.name)
    console.log('3. 编辑器对象:', editor)
    console.log('4. 可用命令:', editor.commands ? Object.keys(editor.commands) : '无')

    // 筛选分页相关的命令
    if (editor.commands) {
      const pageCommands = Object.keys(editor.commands).filter(k =>
        k.toLowerCase().includes('page') ||
        k.toLowerCase().includes('break')
      )
      console.log('5. 分页相关命令:', pageCommands)
    }

    console.log('6. 编辑器属性:', Object.keys(editor))
    console.log('7. 当前布局:', editor.view?.dom?.closest('.umo-editor-container')?.classList)
  } else {
    console.log('2. 底层编辑器未找到')
  }

  console.log('================================')
  ElMessage.success('调试信息已输出到Console，请查看')
}

// 强制启用分页模式
const forcePageMode = () => {
  if (!editorRef.value) {
    ElMessage.warning('编辑器未就绪')
    return
  }

  try {
    let editor = editorRef.value.getEditor()
    if (editor && editor.__v_isRef) {
      editor = editor.value
    }

    console.log('[EditorTest] 当前布局:', editor.extensionStorage?.page?.layout)

    // 方法1：通过setLayout API
    if (editorRef.value.setLayout) {
      editorRef.value.setLayout('page')
      console.log('[EditorTest] ✓ 调用了 setLayout("page")')
    }

    // 方法2：直接修改extensionStorage
    if (editor.extensionStorage?.page) {
      editor.extensionStorage.page.layout = 'page'
      console.log('[EditorTest] ✓ 直接设置 extensionStorage.page.layout = "page"')
    }

    // 方法3：添加CSS类
    const container = document.querySelector('.umo-editor-container')
    if (container) {
      container.classList.add('page-layout')
      container.classList.remove('continuous-layout')
      console.log('[EditorTest] ✓ 添加了 page-layout 类')
    }

    // 方法4：查找工具栏中所有可能的布局按钮
    const allButtons = document.querySelectorAll('.umo-editor-container button, .umo-toolbar button, [role="button"]')
    console.log('[EditorTest] 工具栏按钮总数:', allButtons.length)

    // 查找包含"页面"、"布局"、"layout"等关键词的按钮
    const layoutButtons = Array.from(allButtons).filter(btn => {
      const text = btn.textContent || ''
      const title = btn.getAttribute('title') || ''
      const ariaLabel = btn.getAttribute('aria-label') || ''
      return text.includes('页面') || text.includes('布局') ||
             title.includes('页面') || title.includes('布局') ||
             title.toLowerCase().includes('layout') ||
             ariaLabel.includes('页面') || ariaLabel.includes('布局')
    })

    console.log('[EditorTest] 找到可能的布局按钮:', layoutButtons.length)
    layoutButtons.forEach((btn, i) => {
      console.log(`  ${i + 1}. ${btn.textContent || btn.getAttribute('title')}`, btn)
    })

    // 如果找到了，尝试点击第一个
    if (layoutButtons.length > 0) {
      console.log('[EditorTest] 尝试点击第一个布局按钮...')
      layoutButtons[0].click()
    }

    setTimeout(() => {
      console.log('[EditorTest] 300ms后布局:', editor.extensionStorage?.page?.layout)

      // 检查页面元素
      const pages = document.querySelectorAll('.umo-page, [data-page-number]')
      console.log('[EditorTest] 页面元素数量:', pages.length)
    }, 300)

    ElMessage.success('已尝试强制启用分页模式，请查看Console')
  } catch (error: any) {
    console.error('[EditorTest] 强制启用失败:', error)
    ElMessage.error('操作失败: ' + error.message)
  }
}

// 编辑器就绪
const handleEditorReady = () => {
  console.log('[EditorTest] 编辑器已就绪')

  // 自动调试一次，查看可用API
  setTimeout(() => {
    debugEditor()
  }, 500)
}
</script>

<style scoped>
.editor-test-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.editor-container {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.upload-demo {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>