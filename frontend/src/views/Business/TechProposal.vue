<template>
  <div class="tech-proposal">
    <!-- Step 1: 项目选择 -->
    <el-card class="project-section" shadow="never">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目">
              <el-select
                v-model="form.projectId"
                placeholder="请选择项目"
                filterable
                @change="handleProjectChange"
                style="width: 100%"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="`${project.project_name} (${project.project_number || '-'})`"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="公司">
              <el-input
                :value="selectedProject?.company_name || '-'"
                disabled
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- Step 2: 文件上传和配置 -->
    <el-card class="upload-section" shadow="never">
      <!-- 使用技术文件提示 -->
      <el-alert
        v-if="currentDocuments.technicalFile && !useHitlFile"
        type="success"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #default>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>💡 检测到该项目已有技术需求文件，可直接使用</span>
            <el-button
              type="primary"
              size="small"
              @click="loadFromHITL(currentDocuments, 'technicalFile')"
            >
              使用技术需求文件
            </el-button>
          </div>
        </template>
      </el-alert>

      <!-- HITL文件Alert -->
      <HitlFileAlert
        v-if="useHitlFile"
        :file-info="hitlFileInfo"
        label="技术需求文件:"
        @cancel="cancelHitlFile"
      />

      <!-- 文件上传器（不使用HITL文件时显示） -->
      <DocumentUploader
        v-if="!useHitlFile"
        v-model="form.tenderFiles"
        :http-request="handleTenderUpload"
        accept=".pdf,.doc,.docx"
        :limit="1"
        :max-size="50"
        drag
        tip-text="上传技术需求文档"
        @success="handleUploadSuccess"
      />

      <!-- 生成配置 -->
      <el-divider>生成选项</el-divider>

      <el-form :model="config" label-width="140px" class="config-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="输出文件前缀">
              <el-input
                v-model="config.outputPrefix"
                placeholder="技术方案"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="AI模型">
              <el-select v-model="config.aiModel" style="width: 100%">
                <el-option label="GPT5（最强推理）" value="shihuang-gpt5" />
                <el-option label="Claude Sonnet 4.5（标书专用）" value="shihuang-claude-sonnet-45" />
                <el-option label="GPT4o Mini（推荐-默认）" value="shihuang-gpt4o-mini" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="方案模式">
          <el-radio-group v-model="config.proposalMode">
            <el-radio value="basic">
              基础方案
              <el-tooltip placement="top">
                <template #content>
                  <div style="max-width: 300px;">
                    快速生成通用技术方案<br/>
                    • 适合时间紧急的项目<br/>
                    • 生成速度快<br/>
                    • 使用通用技术描述
                  </div>
                </template>
                <el-icon style="margin-left: 4px;"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-radio>
            <el-radio value="advanced">
              进阶方案（推荐）
              <el-tooltip placement="top">
                <template #content>
                  <div style="max-width: 300px;">
                    生成业务定制化方案<br/>
                    • 紧扣招标需求和业务场景<br/>
                    • 突出数据优势和实力证明<br/>
                    • 语言专业、具有说服力<br/>
                    • 适合竞争激烈的重要项目
                  </div>
                </template>
                <el-icon style="margin-left: 4px;"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="附加输出">
          <el-checkbox-group v-model="config.additionalOutputs">
            <el-checkbox label="includeAnalysis">需求分析报告</el-checkbox>
            <el-checkbox label="includeMapping">需求匹配表</el-checkbox>
            <el-checkbox label="includeSummary">生成总结报告</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="action-controls">
        <el-button
          type="primary"
          size="large"
          :disabled="!canGenerate"
          :loading="generating"
          @click="generateProposal"
        >
          <el-icon><Promotion /></el-icon>
          生成技术方案
        </el-button>
      </div>
    </el-card>

    <!-- AI生成流式输出 -->
    <el-card v-if="generating" class="generation-output" shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI正在生成技术方案...</span>
          <el-progress
            :percentage="generationProgress"
            :status="generationProgress === 100 ? 'success' : undefined"
            style="width: 300px"
          />
        </div>
      </template>

      <SSEStreamViewer
        :content="streamContent"
        :is-streaming="generating"
        @stop="stopGeneration"
      />
    </el-card>

    <!-- 需求分析结果 -->
    <el-card v-if="analysisResult" class="analysis-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>需求分析结果</span>
          <el-button
            size="small"
            @click="analysisExpanded = !analysisExpanded"
          >
            {{ analysisExpanded ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>

      <div v-show="analysisExpanded">
        <!-- 文档摘要统计 -->
        <StatsCard
          title="文档摘要"
          :stats="analysisResult.document_summary || {}"
          :stat-items="[
            { key: 'total_requirements', label: '总需求数', suffix: '项' },
            { key: 'mandatory_count', label: '强制需求', suffix: '项' },
            { key: 'optional_count', label: '可选需求', suffix: '项' }
          ]"
        />

        <!-- 需求分类 -->
        <div class="requirement-categories">
          <h4>需求分类</h4>
          <el-collapse accordion>
            <el-collapse-item
              v-for="(category, index) in analysisResult.requirement_categories"
              :key="index"
              :name="index"
            >
              <template #title>
                <div class="category-title">
                  <span>{{ category.category }}</span>
                  <el-tag :type="getPriorityType(category.priority)" size="small">
                    {{ category.priority }}
                  </el-tag>
                  <el-tag type="info" size="small">
                    {{ category.requirements_count || 0 }}项
                  </el-tag>
                </div>
              </template>

              <div class="category-content">
                <p v-if="category.summary" class="category-summary">
                  {{ category.summary }}
                </p>

                <div v-if="category.keywords && category.keywords.length > 0" class="category-keywords">
                  <strong>关键词：</strong>
                  <el-tag
                    v-for="keyword in category.keywords"
                    :key="keyword"
                    size="small"
                    style="margin-right: 8px"
                  >
                    {{ keyword }}
                  </el-tag>
                </div>

                <div v-if="category.key_points && category.key_points.length > 0" class="category-points">
                  <strong>要点：</strong>
                  <ul>
                    <li v-for="(point, idx) in category.key_points" :key="idx">
                      {{ point }}
                    </li>
                  </ul>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-card>

    <!-- 大纲展示 -->
    <el-card v-if="outlineData" class="outline-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>技术方案大纲</span>
          <el-button
            size="small"
            @click="outlineExpanded = !outlineExpanded"
          >
            {{ outlineExpanded ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>

      <div v-show="outlineExpanded">
        <!-- 大纲统计 -->
        <StatsCard
          title="大纲概览"
          :stats="outlineData"
          :stat-items="[
            { key: 'total_chapters', label: '总章节数', suffix: '章' },
            { key: 'estimated_pages', label: '预计页数', suffix: '页' }
          ]"
          :span="12"
        />

        <!-- 章节树 -->
        <div class="章节结构">
          <h4>章节结构</h4>
          <el-tree
            :data="chapterTreeData"
            :props="{ label: 'title', children: 'subsections' }"
            default-expand-all
            node-key="chapter_number"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon v-if="data.level === 1"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                <span class="node-title">{{ data.chapter_number }} {{ data.title }}</span>
                <span v-if="data.description" class="node-desc">{{ data.description }}</span>
              </span>
            </template>
          </el-tree>
        </div>
      </div>
    </el-card>

    <!-- 富文本编辑器（生成完成后显示） -->
    <el-card v-if="showEditor" class="editor-section" shadow="never">
      <RichTextEditor
        ref="editorRef"
        v-model="editorContent"
        title="技术方案文档"
        :height="1000"
        :loading="editorLoading"
        :saving="editorSaving"
        @save="handleEditorSave"
      />
    </el-card>

    <!-- 生成结果 -->
    <el-card v-if="generationResult" class="result-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>✅ 生成结果</span>
          <div class="header-actions">
            <el-button
              type="primary"
              :icon="View"
              @click="previewDocument"
            >
              预览文档
            </el-button>
            <el-button
              type="success"
              :icon="Download"
              @click="downloadDocument('proposal')"
            >
              下载技术方案
            </el-button>

            <!-- 同步状态 -->
            <el-button
              v-if="!synced"
              type="info"
              :icon="Upload"
              :loading="syncing"
              @click="handleSyncToHitl"
            >
              同步到投标项目
            </el-button>
            <el-tag v-else type="success" size="large">
              已同步到投标项目
            </el-tag>

            <el-button
              type="primary"
              :icon="RefreshRight"
              @click="generateProposal"
            >
              重新生成
            </el-button>
          </div>
        </div>
      </template>

      <div class="result-content">
        <!-- 生成统计 -->
        <StatsCard
          title="生成统计"
          :stats="generationResult"
          :stat-items="[
            { key: 'requirements_count', label: '需求数量', suffix: '项' },
            { key: 'sections_count', label: '章节数量', suffix: '章' },
            { key: 'matches_count', label: '匹配数量', suffix: '项' }
          ]"
        />

        <!-- 输出文件列表 -->
        <div class="output-files">
          <h4>输出文件</h4>
          <div class="file-buttons">
            <el-button
              v-if="generationResult.output_files?.proposal"
              type="success"
              @click="downloadDocument('proposal')"
            >
              <el-icon><Download /></el-icon>
              下载技术方案
            </el-button>
            <el-button
              v-if="generationResult.output_files?.analysis"
              type="primary"
              @click="downloadDocument('analysis')"
            >
              <el-icon><Download /></el-icon>
              下载需求分析
            </el-button>
            <el-button
              v-if="generationResult.output_files?.mapping"
              type="info"
              @click="downloadDocument('mapping')"
            >
              <el-icon><Download /></el-icon>
              下载匹配表
            </el-button>
            <el-button
              v-if="generationResult.output_files?.summary"
              type="warning"
              @click="downloadDocument('summary')"
            >
              <el-icon><Download /></el-icon>
              下载生成报告
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 历史文件管理 -->
    <HistoryFilesPanel
      v-if="form.projectId"
      title="该项目的技术方案文件"
      :current-file="currentTechFile"
      :history-files="historyFiles"
      :loading="loadingHistory"
      :show-stats="false"
      :show-editor-open="true"
      @preview="previewFile"
      @download="downloadHistoryFile"
      @regenerate="handleRegenerate"
      @refresh="loadHistoryFiles"
      @open-in-editor="openHistoryInEditor"
    />

    <!-- 文档预览对话框 -->
    <DocumentPreview
      v-model="previewVisible"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import {
  Download,
  RefreshRight,
  View,
  Upload,
  Promotion,
  Folder,
  Document,
  QuestionFilled
} from '@element-plus/icons-vue'
import {
  DocumentUploader,
  SSEStreamViewer,
  DocumentPreview,
  StatsCard,
  HitlFileAlert,
  HistoryFilesPanel,
  RichTextEditor
} from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import {
  useProjectDocuments,
  useHitlIntegration,
  useHistoryFiles
} from '@/composables'
import { downloadFile } from '@/utils/helpers'
import type { Project, UploadUserFile } from '@/types'

// ============================================
// Composables
// ============================================
const {
  projects,
  selectedProject,
  currentDocuments,
  loadProjects,
  handleProjectChange: handleProjectChangeComposable,
  restoreProjectFromStore
} = useProjectDocuments()

const {
  useHitlFile,
  hitlFileInfo,
  syncing,
  synced,
  loadFromHITL,
  cancelHitlFile,
  syncToHitl
} = useHitlIntegration({
  onFileLoaded: () => {
    form.value.tenderFiles = []
  }
})

// 暂时禁用历史文件API（接口未实现）
const historyFiles = ref<any[]>([])
const loadingHistory = ref(false)
const loadHistoryFiles = async () => {
  console.log('历史文件API暂未实现')
}
const downloadHistoryFile = async (file: any) => {
  try {
    if (!file.downloadUrl) {
      ElMessage.error('下载地址无效')
      return
    }

    // 从URL中提取文件名，去除查询参数
    let filename = file.filename || file.downloadUrl.split('/').pop() || '技术方案.docx'
    // 去除URL查询参数（例如 ?download=true）
    filename = filename.split('?')[0]

    // 使用公用下载函数
    downloadFile(file.downloadUrl, filename)

    ElMessage.success('文件下载中...')
  } catch (error: any) {
    console.error('下载文件失败:', error)
    ElMessage.error(error.message || '下载文件失败')
  }
}

// ============================================
// 响应式数据
// ============================================
const form = ref({
  projectId: null as number | null,
  tenderFiles: [] as UploadUserFile[]
})

const config = ref({
  outputPrefix: '技术方案',
  aiModel: 'shihuang-gpt4o-mini',
  proposalMode: 'basic' as 'basic' | 'advanced',  // 默认基础模式
  additionalOutputs: ['includeAnalysis', 'includeMapping', 'includeSummary'] as string[]
})

// 生成状态
const generating = ref(false)
const generationProgress = ref(0)
const streamContent = ref('')

// 分析结果
const analysisResult = ref<any>(null)
const analysisExpanded = ref(true)

// 大纲数据
const outlineData = ref<any>(null)
const outlineExpanded = ref(true)

// 生成结果
const generationResult = ref<any>(null)

// 当前项目技术方案文件
const currentTechFile = ref<any>(null)

// 预览状态
const previewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

// 编辑器状态
const showEditor = ref(false)
const editorRef = ref(null)
const editorContent = ref('')
const editorLoading = ref(false)
const editorSaving = ref(false)

// 章节树数据
const chapterTreeData = computed(() => {
  if (!outlineData.value?.chapters) return []
  return outlineData.value.chapters
})

// 能否生成
const canGenerate = computed(() =>
  form.value.projectId && (useHitlFile.value || form.value.tenderFiles.length > 0)
)

// 优先级类型映射
const getPriorityType = (priority: string) => {
  const types: Record<string, any> = {
    '高': 'danger',
    'high': 'danger',
    '中': 'warning',
    'medium': 'warning',
    '低': 'info',
    'low': 'info'
  }
  return types[priority] || 'info'
}

// ============================================
// 自定义上传处理
// ============================================
const handleTenderUpload = async (options: UploadRequestOptions) => {
  const { file, onSuccess, onError } = options

  if (!form.value.projectId) {
    const error = new Error('请先选择项目')
    onError(error)
    ElMessage.error('请先选择项目')
    return
  }

  if (!selectedProject.value?.company_id) {
    const error = new Error('项目没有关联公司')
    onError(error)
    ElMessage.error('项目没有关联公司')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('company_id', selectedProject.value.company_id.toString())
    formData.append('project_id', form.value.projectId.toString())

    const response = await tenderApi.parseDocumentStructure(formData)

    if (response.success) {
      onSuccess(response.data)
      ElMessage.success('技术需求文档上传成功')
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (error: any) {
    onError(error)
    ElMessage.error(error.message || '文档上传失败')
  }
}

const handleUploadSuccess = () => {
  ElMessage.success('文档上传成功')
}

// ============================================
// 项目切换
// ============================================
const handleProjectChange = async () => {
  await handleProjectChangeComposable(form.value.projectId, {
    onClear: () => {
      form.value.tenderFiles = []
      analysisResult.value = null
      outlineData.value = null
      generationResult.value = null
      currentTechFile.value = null
      streamContent.value = ''
      showEditor.value = false
      editorContent.value = ''
      if (useHitlFile.value) {
        cancelHitlFile()
      }
    },
    onDocumentsLoaded: (docs) => {
      // 自动加载HITL技术文件
      if (docs.technicalFile) {
        loadFromHITL(docs, 'technicalFile')
      }

      // 显示历史技术方案文件
      if (docs.techProposalFile) {
        currentTechFile.value = docs.techProposalFile
        ElMessage.success('已加载历史技术方案文件')
      }
    }
  })
}

// ============================================
// 生成技术方案
// ============================================
const generateProposal = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('请选择项目并上传技术需求文档')
    return
  }

  generating.value = true
  generationProgress.value = 0
  streamContent.value = ''
  analysisResult.value = null
  // outlineData.value = null  // ✅ 不清空大纲数据，保持显示
  generationResult.value = null
  showEditor.value = false  // 重置编辑器显示状态
  editorContent.value = ''   // 清空编辑器内容

  try {
    const formData = new FormData()

    // 判断使用HITL文件还是上传文件
    if (useHitlFile.value && hitlFileInfo.value) {
      formData.append('use_hitl_technical_file', 'true')
      formData.append('project_id', form.value.projectId!.toString())
    } else if (form.value.tenderFiles[0]?.raw) {
      formData.append('tender_file', form.value.tenderFiles[0].raw)
    } else {
      throw new Error('请上传技术需求文档或使用技术文件')
    }

    // 添加配置参数
    formData.append('outputPrefix', config.value.outputPrefix)
    formData.append('companyId', selectedProject.value!.company_id.toString())
    formData.append('projectName', selectedProject.value!.project_name || '')
    formData.append('projectId', form.value.projectId!.toString())
    formData.append('aiModel', config.value.aiModel)  // ✅ 添加AI模型参数
    formData.append('proposalMode', config.value.proposalMode)  // ✅ 添加方案模式参数

    // 附加输出选项
    formData.append('includeAnalysis', config.value.additionalOutputs.includes('includeAnalysis') ? 'true' : 'false')
    formData.append('includeMapping', config.value.additionalOutputs.includes('includeMapping') ? 'true' : 'false')
    formData.append('includeSummary', config.value.additionalOutputs.includes('includeSummary') ? 'true' : 'false')

    // 使用SSE流式处理
    await generateWithSSE(formData)

    ElMessage.success('技术方案生成完成')

    // 刷新历史文件列表（暂时禁用）
    // await loadHistoryFiles()
  } catch (error: any) {
    console.error('生成失败:', error)
    ElMessage.error(error.message || '生成失败，请重试')
  } finally {
    generating.value = false
  }
}

// SSE流式处理（支持实时内容推送）
const generateWithSSE = async (formData: FormData) => {
  // 选择使用V2接口（支持流式内容）
  const useStreamingContent = true
  const apiEndpoint = useStreamingContent ? '/api/generate-proposal-stream-v2' : '/api/generate-proposal-stream'

  const response = await fetch(apiEndpoint, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('无法读取响应流')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  // 章节内容累积器
  const chapterContents: Record<string, string> = {}
  let currentChapterNumber = ''

  // 防抖定时器（减少编辑器更新频率，避免闪烁）
  let editorUpdateTimer: ReturnType<typeof setTimeout> | null = null
  const debouncedUpdateEditor = () => {
    if (editorUpdateTimer) clearTimeout(editorUpdateTimer)
    editorUpdateTimer = setTimeout(() => {
      updateEditorContent(chapterContents)
    }, 500) // 500ms防抖
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))

          // 更新进度
          if (data.progress !== undefined) {
            generationProgress.value = data.progress
          }

          // 更新消息
          if (data.message) {
            streamContent.value += data.message + '\n'
          }

          // 处理需求分析完成
          if (data.stage === 'analysis_completed' && data.analysis_result) {
            analysisResult.value = data.analysis_result
          }

          // 处理大纲生成完成
          if (data.stage === 'outline_completed' && data.outline_data) {
            outlineData.value = data.outline_data
          }

          // 【新增】处理流式内容生成事件
          if (data.stage === 'content_generation') {
            if (data.event === 'chapter_start') {
              // 章节开始
              currentChapterNumber = data.chapter_number || ''
              chapterContents[currentChapterNumber] = ''
              streamContent.value += `\n\n## ${data.chapter_number} ${data.chapter_title}\n\n`

              // 【新增】第一个章节开始时就显示编辑器，实时展示AI生成内容
              if (!showEditor.value) {
                showEditor.value = true
              }
            } else if (data.event === 'content_chunk') {
              // 接收内容片段
              const chapterNum = data.chapter_number || currentChapterNumber
              if (chapterNum) {
                chapterContents[chapterNum] = (chapterContents[chapterNum] || '') + (data.content || '')
                // 使用防抖更新编辑器（避免频繁全量替换导致闪烁）
                debouncedUpdateEditor()
              }
            } else if (data.event === 'chapter_end') {
              // 章节完成 - 强制立即更新一次编辑器（确保完整性）
              if (editorUpdateTimer) clearTimeout(editorUpdateTimer)
              updateEditorContent(chapterContents)
              streamContent.value += `\n✓ ${data.chapter_title || '章节'} 生成完成\n`
            }
          }

          // 处理完成
          if (data.stage === 'completed' && data.success) {
            generationResult.value = data
            currentTechFile.value = {
              outputFile: data.output_file,
              downloadUrl: data.output_files?.proposal,
              stats: {
                requirements_count: data.requirements_count,
                sections_count: data.sections_count,
                matches_count: data.matches_count
              },
              message: '技术方案已生成'
            }

            // 显示编辑器
            if (useStreamingContent) {
              showEditor.value = true
            }

            // 自动同步到HITL
            if (data.output_file && form.value.projectId) {
              await syncToHitl(
                form.value.projectId,
                data.output_file,
                'tech_proposal'
              )
            }
          }

          // 处理错误
          if (data.stage === 'error') {
            // 显示详细错误信息
            streamContent.value += `\n❌ 错误: ${data.error || data.message}\n`
            throw new Error(data.error || data.message || '生成失败')
          }
        } catch (e: any) {
          // 如果是JSON解析错误，可能是正常的非data行，忽略
          if (e.message?.includes('JSON')) {
            // 忽略JSON解析错误
          } else {
            // 其他错误抛出
            console.error('SSE处理错误:', e, '原始数据:', line)
            throw e
          }
        }
      }
    }
  }
}

// 更新编辑器内容（增量更新）- 包含大纲指导信息
const updateEditorContent = (chapterContents: Record<string, string>) => {
  // ✅ 使用大纲数据按正确顺序生成HTML（如果大纲可用）
  if (outlineData.value?.chapters) {
    let htmlContent = ''

    // 递归生成章节HTML（包含大纲指导信息）
    const generateChapterHtml = (chapters: any[]) => {
      for (const chapter of chapters) {
        const chapterNum = chapter.chapter_number
        const content = chapterContents[chapterNum] || ''

        // 根据level使用不同的标题级别
        const headingLevel = chapter.level || 1
        const chapterId = `ch-${chapterNum.replace(/\./g, '-')}`
        // ✅ 添加id属性，完整显示章节号和标题
        htmlContent += `<h${headingLevel} id="${chapterId}">${chapterNum} ${chapter.title}</h${headingLevel}>\n`

        // ✅ 显示章节说明
        if (chapter.description) {
          htmlContent += `<div style="padding: 12px; background: #E8F4FD; border-left: 4px solid #409EFF; margin: 12px 0;">
            <strong>【本章说明】</strong> ${chapter.description}
          </div>\n`
        }

        // ✅ 显示应答策略
        if (chapter.response_strategy) {
          htmlContent += `<div style="padding: 12px; background: #F0F9FF; border-left: 4px solid #67C23A; margin: 12px 0;">
            <strong>【应答策略】</strong> ${chapter.response_strategy}
          </div>\n`
        }

        // ✅ 显示内容提示
        if (chapter.content_hints && chapter.content_hints.length > 0) {
          htmlContent += `<div style="padding: 12px; background: #FFF7E6; border-left: 4px solid #E6A23C; margin: 12px 0;">
            <strong>【内容提示】</strong>
            <ul style="margin: 8px 0; padding-left: 24px;">
              ${chapter.content_hints.map((hint: string) => `<li>${hint}</li>`).join('')}
            </ul>
          </div>\n`
        }

        // ✅ 显示应答建议
        if (chapter.response_tips && chapter.response_tips.length > 0) {
          htmlContent += `<div style="padding: 12px; background: #FEF0F0; border-left: 4px solid #F56C6C; margin: 12px 0;">
            <strong>【应答建议】</strong>
            <ul style="margin: 8px 0; padding-left: 24px;">
              ${chapter.response_tips.map((tip: string) => `<li>${tip}</li>`).join('')}
            </ul>
          </div>\n`
        }

        // ✅ 显示AI生成的内容
        if (content) {
          htmlContent += `<div style="padding: 12px; background: #F0FFF4; border-left: 4px solid #52C41A; margin: 12px 0;">
            <strong style="color: #52C41A;">【AI生成内容】</strong>
          </div>\n`
          htmlContent += `<div style="line-height: 1.8; margin: 12px 0;">${content.replace(/\n/g, '<br>')}</div>\n`
        } else if (chapterNum in chapterContents) {
          // 正在生成中但内容为空，显示占位符
          htmlContent += `<div style="padding: 12px; background: #F5F5F5; border: 1px dashed #D9D9D9; margin: 12px 0; color: #999;">
            <em>正在生成内容...</em>
          </div>\n`
        }

        // 递归处理子章节
        if (chapter.subsections && chapter.subsections.length > 0) {
          generateChapterHtml(chapter.subsections)
        }
      }
    }

    generateChapterHtml(outlineData.value.chapters)
    editorContent.value = htmlContent
  } else {
    // ✅ 回退方案：按章节编号排序（适用于大纲尚未加载时）
    let htmlContent = ''

    // 对章节编号进行排序
    const sortedEntries = Object.entries(chapterContents).sort((a, b) => {
      const [numA] = a
      const [numB] = b

      // 简单的字符串比较（适用于中文编号）
      return numA.localeCompare(numB, 'zh-CN')
    })

    for (const [chapterNum, content] of sortedEntries) {
      htmlContent += `<h2>${chapterNum}</h2>\n`
      if (content) {
        htmlContent += `<div style="line-height: 1.8;">${content.replace(/\n/g, '<br>')}</div>\n`
      }
    }

    editorContent.value = htmlContent
  }
}

// ============================================
// 操作函数
// ============================================
const stopGeneration = () => {
  generating.value = false
  ElMessage.info('已停止生成')
}

const downloadDocument = (fileType: string) => {
  if (!generationResult.value?.output_files?.[fileType]) {
    ElMessage.warning('文件不存在')
    return
  }

  const url = generationResult.value.output_files[fileType]
  // 从URL中提取文件名，去除查询参数
  let filename = url.split('/').pop() || `技术方案_${fileType}.docx`
  // 去除URL查询参数（例如 ?download=true）
  filename = filename.split('?')[0]

  // 使用公用下载函数
  downloadFile(url, filename)

  ElMessage.success('下载已开始')
}

const previewDocument = () => {
  if (!generationResult.value?.output_files?.proposal) {
    ElMessage.warning('暂无文档可预览')
    return
  }

  previewFileUrl.value = generationResult.value.output_files.proposal
  previewFileName.value = `技术方案-${selectedProject.value?.project_name || '文档'}.docx`
  previewVisible.value = true
}

const previewFile = (file: any) => {
  previewFileUrl.value = file.file_path || file.outputFile
  previewFileName.value = file.filename || '技术方案.docx'
  previewVisible.value = true
}

const handleSyncToHitl = async () => {
  if (!generationResult.value?.output_file) {
    ElMessage.warning('没有可同步的文件')
    return
  }

  if (!form.value.projectId) {
    ElMessage.error('项目ID无效')
    return
  }

  await syncToHitl(
    form.value.projectId,
    generationResult.value.output_file,
    'tech_proposal'
  )
}

const handleRegenerate = () => {
  currentTechFile.value = null
  generationResult.value = null
  analysisResult.value = null
  outlineData.value = null
  showEditor.value = false
  editorContent.value = ''
  ElMessage.info('请配置参数后重新生成')
}

// 编辑器保存处理
const handleEditorSave = async (content: string) => {
  if (!generationResult.value?.output_file) {
    ElMessage.warning('没有可保存的文件')
    return
  }

  try {
    editorSaving.value = true

    // 调用后端保存编辑内容
    const response = await fetch('/api/editor/save-html-to-word', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        html_content: content,
        project_id: form.value.projectId,
        document_type: 'tech_proposal',
        original_file: generationResult.value.output_file
      })
    })

    const result = await response.json()

    if (result.success) {
      ElMessage.success('技术方案内容已保存')

      // 更新文件路径（如果有新路径）
      if (result.output_file) {
        generationResult.value.output_file = result.output_file
        if (result.download_url && generationResult.value.output_files) {
          generationResult.value.output_files.proposal = result.download_url
        }
      }

      // 同步到HITL
      if (result.output_file && form.value.projectId) {
        await syncToHitl(
          form.value.projectId,
          result.output_file,
          'tech_proposal'
        )
      }
    } else {
      throw new Error(result.error || '保存失败')
    }
  } catch (error: any) {
    console.error('[TechProposal] 保存编辑内容失败:', error)
    throw error // 让RichTextEditor显示错误
  } finally {
    editorSaving.value = false
  }
}

// 加载Word文档到编辑器
const loadWordToEditor = async (filePath: string) => {
  try {
    editorLoading.value = true
    editorContent.value = '<p style="color: #409EFF;">正在转换Word文档为可编辑格式...</p>'

    // 调用后端API将Word转换为HTML
    const response = await fetch('/api/editor/convert-word-to-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath })
    })

    const result = await response.json()

    if (result.success && result.html_content) {
      editorContent.value = result.html_content

      if (editorRef.value) {
        editorRef.value.setContent(result.html_content)
      }

      console.log('[TechProposal] Word文档已加载到编辑器')
    } else {
      throw new Error(result.error || '转换失败')
    }
  } catch (error: any) {
    console.error('[TechProposal] 加载文档到编辑器失败:', error)

    // 如果转换失败，显示基础提示
    editorContent.value = `
      <h1>📄 技术方案文档</h1>
      <div style="padding: 20px; background: #FFF3E0; border-left: 4px solid #FF9800; margin: 16px 0;">
        <p><strong>⚠️ 提示：</strong>Word文档转换失败</p>
        <p>原因：${error.message}</p>
        <p>您可以：</p>
        <ul>
          <li>直接在此编辑器中输入内容</li>
          <li>或点击下方"预览Word"或"下载"按钮查看原始文档</li>
        </ul>
      </div>
      <p>开始编辑您的内容...</p>
    `

    ElMessage.warning('Word转换HTML失败，请使用预览或下载功能')
  } finally {
    editorLoading.value = false
  }
}

// 在编辑器中打开历史文件
const openHistoryInEditor = async () => {
  if (!currentTechFile.value?.outputFile) {
    ElMessage.error('历史文件信息无效')
    return
  }

  try {
    // 显示编辑器
    showEditor.value = true

    // 加载Word文档到编辑器
    await loadWordToEditor(currentTechFile.value.outputFile)

    ElMessage.success('历史文件已加载到编辑器')

    // 滚动到编辑器
    setTimeout(() => {
      document.querySelector('.editor-section')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }, 100)
  } catch (error: any) {
    console.error('[TechProposal] 打开历史文件失败:', error)
    ElMessage.error('打开历史文件失败: ' + error.message)
  }
}

// ============================================
// 生命周期
// ============================================
onMounted(async () => {
  await loadProjects()

  const restoredProjectId = await restoreProjectFromStore({
    onClear: () => {
      form.value.tenderFiles = []
      analysisResult.value = null
      outlineData.value = null
      generationResult.value = null
      currentTechFile.value = null
      if (useHitlFile.value) {
        cancelHitlFile()
      }
    },
    onDocumentsLoaded: (docs) => {
      if (docs.technicalFile) {
        loadFromHITL(docs, 'technicalFile')
      }
      if (docs.techProposalFile) {
        currentTechFile.value = docs.techProposalFile
      }
    }
  })

  if (restoredProjectId) {
    form.value.projectId = restoredProjectId
  }
})
</script>

<style scoped lang="scss">

.tech-proposal {
  // 移除padding，避免与page-content的padding叠加
  display: flex;
  flex-direction: column;
  gap: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .header-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .project-section,
  .upload-section,
  .generation-output,
  .analysis-section,
  .outline-section,
  .result-section,
  .editor-section {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
    }
  }

  .editor-section {
    height: 1050px;       // 固定卡片高度（包含header）
    overflow: hidden;     // 防止溢出

    :deep(.el-card__body) {
      padding: 0;
      height: 1000px;     // 内容区域1000px（编辑器高度）
      overflow: hidden;   // 防止溢出
    }
  }

  .config-form {
    margin-top: 20px;
    padding: 20px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
  }

  .action-controls {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 30px;
    padding-top: 30px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  .requirement-categories,
  .章节结构 {
    margin-top: 20px;

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .category-title {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
    }

    .category-content {
      padding: 16px;
      background: var(--el-fill-color-lighter);
      border-radius: 8px;

      .category-summary {
        margin-bottom: 12px;
        font-style: italic;
        color: var(--el-text-color-secondary);
      }

      .category-keywords,
      .category-points {
        margin-top: 12px;
      }

      ul {
        margin: 8px 0;
        padding-left: 20px;
      }
    }

    .tree-node {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;

      .el-icon {
        color: var(--el-color-primary);
      }

      .node-title {
        font-weight: 500;
      }

      .node-desc {
        margin-left: 12px;
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }
  }

  .result-content {
    .output-files {
      margin-top: 24px;

      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .file-buttons {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
    }
  }
}
</style>
