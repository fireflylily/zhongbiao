<template>
  <div class="tech-proposal">
    <!-- 统一的操作面板：项目选择 + 文档准备 -->
    <el-card class="main-panel" shadow="never">
      <!-- 第一行：项目和公司选择 -->
      <div class="panel-row project-row">
        <div class="row-item">
          <label class="row-label">选择项目</label>
          <el-select
            v-model="form.projectId"
            placeholder="请选择项目"
            filterable
            @change="handleProjectChange"
            class="row-select"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="`${project.project_name} (${project.project_number || '-'})`"
              :value="project.id"
            />
          </el-select>
        </div>

        <div class="row-item">
          <label class="row-label">应答公司</label>
          <el-input
            :value="selectedProject?.company_name || '-'"
            disabled
            class="row-input"
          />
        </div>
      </div>

      <!-- 第二行：文档区域（行内样式） -->
      <div class="panel-row project-row document-row">
        <div class="row-item">
          <label class="row-label">技术文档</label>
          <!-- 已加载文件 -->
          <div v-if="useHitlFile" class="file-chip file-chip--success">
            <el-icon class="file-chip-icon"><Document /></el-icon>
            <span class="file-chip-name" :title="hitlFileInfo?.filename">
              {{ hitlFileInfo?.filename || '未知文件' }}
            </span>
            <span class="file-chip-tag">已加载</span>
            <el-button class="file-chip-close" type="danger" text size="small" @click="cancelHitlFile">×</el-button>
          </div>
          <!-- 手动上传的文件 -->
          <div v-else-if="form.tenderFiles.length > 0" class="file-chip file-chip--info">
            <el-icon class="file-chip-icon"><Document /></el-icon>
            <span class="file-chip-name" :title="form.tenderFiles[0].name">
              {{ form.tenderFiles[0].name }}
            </span>
            <span class="file-chip-tag">已上传</span>
            <el-button class="file-chip-close" type="danger" text size="small" @click="form.tenderFiles = []">×</el-button>
          </div>
          <!-- 未上传：显示为类似输入框的占位区域 -->
          <div v-else class="file-placeholder">
            <span class="placeholder-text">请上传技术需求文档</span>
            <DocumentUploader
              v-model="form.tenderFiles"
              :http-request="handleTenderUpload"
              accept=".pdf,.doc,.docx"
              :limit="1"
              :max-size="50"
              :show-file-list="false"
              trigger-text="选择文件"
              @success="handleUploadSuccess"
            />
          </div>
        </div>
      </div>

      <!-- 第三行：配置选项 -->
      <div class="config-section">
        <!-- 第一行：输出前缀 + AI模型 -->
        <div class="panel-row project-row">
          <div class="row-item">
            <label class="row-label">输出前缀</label>
            <el-input v-model="config.outputPrefix" placeholder="技术方案" class="row-input" />
          </div>
          <div class="row-item">
            <label class="row-label">AI模型</label>
            <el-select v-model="config.aiModel" class="row-select">
              <el-option label="GPT5（最强推理）" value="shihuang-gpt5" />
              <el-option label="Claude Sonnet 4.5（标书专用）" value="shihuang-claude-sonnet-45" />
              <el-option label="GPT4o Mini（推荐-默认）" value="shihuang-gpt4o-mini" />
              <el-option label="通义千问-Max" value="qwen-max" />
            </el-select>
          </div>
        </div>

        <!-- 第二行：生成模式 -->
        <div class="panel-row project-row">
          <div class="row-item">
            <label class="row-label">生成模式</label>
            <el-radio-group v-model="config.generationMode" class="row-radio-group">
              <el-radio value="Quality-First">
                Quality-First模式
                <el-tag type="success" size="small" style="margin-left: 4px">推荐</el-tag>
              </el-radio>
              <el-radio value="按评分点写">按评分点写</el-radio>
              <el-radio value="按招标书目录写">按招标书目录写</el-radio>
              <el-radio value="编写专项章节">使用固定模板</el-radio>
            </el-radio-group>
          </div>
          <!-- 模板选择（仅当选择"使用固定模板"时显示） -->
          <div v-if="config.generationMode === '编写专项章节'" class="row-item">
            <label class="row-label">选择模板</label>
            <el-select v-model="config.templateName" placeholder="请选择模板" class="row-select">
              <el-option label="政府采购标准（5章）" value="政府采购标准" />
              <el-option label="软件开发项目（8章）" value="软件开发项目" />
              <el-option label="ISO质量体系（6章）" value="ISO质量体系" />
            </el-select>
          </div>
          <div v-else class="row-item"></div>
        </div>

        <!-- Quality-First 模式配置（仅当选择 Quality-First 时显示） -->
        <div v-if="config.generationMode === 'Quality-First'" class="quality-first-config">
          <div class="config-header">
            <el-icon><Setting /></el-icon>
            <span>Quality-First 高级配置</span>
            <el-tooltip content="8个智能体协作生成高质量技术方案：评分点提取 → 产品匹配 → 策略规划 → 素材检索 → 大纲生成 → 内容撰写 → 专家评审 → 迭代优化" placement="top">
              <el-icon class="help-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>

          <div class="panel-row project-row">
            <!-- 流程控制 -->
            <div class="row-item">
              <label class="row-label">流程控制</label>
              <el-checkbox-group v-model="crewConfig.enabledPhases" class="row-checkbox-group">
                <el-checkbox label="product_matching">产品匹配</el-checkbox>
                <el-checkbox label="material_retrieval">素材检索</el-checkbox>
                <el-checkbox label="expert_review">专家评审</el-checkbox>
              </el-checkbox-group>
            </div>
          </div>

          <div class="panel-row project-row">
            <!-- 质量目标 -->
            <div class="row-item slider-row">
              <label class="row-label">质量目标</label>
              <div class="slider-wrapper">
                <el-slider
                  v-model="crewConfig.minReviewScore"
                  :min="60"
                  :max="100"
                  :step="5"
                  :marks="{ 60: '60分', 70: '70分', 80: '80分', 90: '90分', 100: '100分' }"
                  show-input
                  :show-input-controls="false"
                />
              </div>
              <span class="page-hint" style="color: var(--el-color-success); background: var(--el-color-success-light-9);">评审目标分数</span>
            </div>
          </div>

          <div class="panel-row project-row">
            <!-- 最大迭代次数 -->
            <div class="row-item">
              <label class="row-label">迭代优化</label>
              <el-input-number
                v-model="crewConfig.maxIterations"
                :min="0"
                :max="5"
                :step="1"
                controls-position="right"
              />
              <span class="page-hint">0表示不迭代，最多5轮</span>
            </div>
            <div class="row-item"></div>
          </div>
        </div>

        <!-- 第三行：页数控制 -->
        <div class="panel-row project-row">
          <div class="row-item slider-row">
            <label class="row-label">页数控制</label>
            <div class="slider-wrapper">
              <el-slider
                v-model="config.pageCount"
                :min="50"
                :max="400"
                :step="10"
                :marks="{ 50: '50页', 100: '100页', 200: '200页', 300: '300页', 400: '400页' }"
                show-input
                :show-input-controls="false"
              />
            </div>
            <span class="page-hint">约 {{ Math.round(config.pageCount * 700 * 0.8).toLocaleString() }} - {{ Math.round(config.pageCount * 700).toLocaleString() }} 字</span>
          </div>
        </div>

        <!-- 第四行：内容风格 -->
        <div class="panel-row project-row">
          <div class="row-item">
            <label class="row-label">表格数量</label>
            <el-select v-model="config.contentStyle.tables" class="row-select">
              <el-option label="无" value="无" />
              <el-option label="少量" value="少量" />
              <el-option label="适量（推荐）" value="适量" />
              <el-option label="大量" value="大量" />
            </el-select>
          </div>
          <div class="row-item">
            <label class="row-label">流程图</label>
            <el-select v-model="config.contentStyle.flowcharts" class="row-select">
              <el-option label="无" value="无" />
              <el-option label="流程图（推荐）" value="流程图" />
              <el-option label="SmartArt" value="SmartArt" />
            </el-select>
          </div>
        </div>

        <!-- 第五行：图片数量 + 附加输出 -->
        <div class="panel-row project-row">
          <div class="row-item">
            <label class="row-label">图片数量</label>
            <el-select v-model="config.contentStyle.images" class="row-select">
              <el-option label="无" value="无" />
              <el-option label="少量（推荐）" value="少量" />
              <el-option label="大量" value="大量" />
            </el-select>
          </div>
          <div class="row-item">
            <label class="row-label">附加输出</label>
            <el-checkbox-group v-model="config.additionalOutputs" class="row-checkbox-group">
              <el-checkbox label="includeAnalysis">需求分析</el-checkbox>
              <el-checkbox label="includeMapping">匹配表</el-checkbox>
              <el-checkbox label="includeSummary">总结报告</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="panel-actions">
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

      <!-- Quality-First 模式进度追踪 -->
      <CrewProgressTracker
        v-if="config.generationMode === 'Quality-First'"
        :current-phase="crewResults.currentPhase"
        :phase-progress="crewResults.phaseProgress"
        :scoring-points="crewResults.scoringPoints"
        :product-match="crewResults.productMatch"
        :scoring-strategy="crewResults.scoringStrategy"
        :materials="crewResults.materials"
        :review-result="crewResults.reviewResult"
        :show-details="true"
        class="crew-tracker"
      />

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

    <!-- 本项目历史文件列表 -->
    <el-collapse v-if="form.projectId" v-model="showAllHistory" class="history-collapse">
      <el-collapse-item name="history">
        <template #title>
          <div class="collapse-header">
            <span>📂 本项目历史文件 ({{ historyFiles.length }})</span>
            <el-button
              v-if="showAllHistory"
              type="primary"
              size="small"
              :loading="loadingHistory"
              @click.stop="loadFilesList"
              style="margin-left: 16px"
            >
              刷新列表
            </el-button>
          </div>
        </template>

        <el-card shadow="never" style="border: none;">
          <el-table
            :data="historyFiles"
            border
            stripe
            v-loading="loadingHistory"
            max-height="400"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="filename" label="文件名" min-width="300">
              <template #default="{ row }">
                <div class="filename-cell">
                  <el-icon><Document /></el-icon>
                  <span>{{ row.filename }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="文件大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="process_time" label="处理时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.process_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="previewFile(row)">
                  预览
                </el-button>
                <el-button type="success" size="small" @click="downloadHistoryFile(row)">
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 空状态 -->
          <el-empty
            v-if="!loadingHistory && historyFiles.length === 0"
            description="暂无历史文件"
            :image-size="100"
          />
        </el-card>
      </el-collapse-item>
    </el-collapse>

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
import { marked } from 'marked'
import {
  Download,
  RefreshRight,
  View,
  Upload,
  Promotion,
  Folder,
  Document,
  QuestionFilled,
  Setting
} from '@element-plus/icons-vue'
import {
  DocumentUploader,
  SSEStreamViewer,
  DocumentPreview,
  StatsCard,
  HitlFileAlert,
  HistoryFilesPanel,
  RichTextEditor,
  CrewProgressTracker
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

// 历史文件列表
const historyFiles = ref<any[]>([])
const loadingHistory = ref(false)
const showAllHistory = ref<string[]>([])

// 加载历史文件列表（仅当前项目）
const loadFilesList = async () => {
  if (!form.value.projectId) {
    historyFiles.value = []
    return
  }

  loadingHistory.value = true
  try {
    const response = await fetch(`/api/tech-proposal/files?project_id=${form.value.projectId}`)
    const result = await response.json()

    if (result.success) {
      historyFiles.value = result.data || []
    } else {
      throw new Error(result.error || '加载失败')
    }
  } catch (error: any) {
    console.error('加载历史文件失败:', error)
    ElMessage.error(error.message || '加载历史文件失败')
  } finally {
    loadingHistory.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// 下载历史文件
const downloadHistoryFile = async (file: any) => {
  try {
    if (!file.download_url) {
      ElMessage.error('下载地址无效')
      return
    }

    const filename = file.filename || '技术方案.docx'
    downloadFile(file.download_url, filename)
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
  generationMode: 'Quality-First' as 'Quality-First' | '按评分点写' | '按招标书目录写' | '编写专项章节',  // 智能体生成模式
  templateName: '政府采购标准' as string,  // 模板名称
  pageCount: 200,  // 目标页数
  contentStyle: {  // 内容风格
    tables: '适量',
    flowcharts: '流程图',
    images: '少量'
  },
  additionalOutputs: ['includeAnalysis', 'includeMapping', 'includeSummary'] as string[]
})

// Quality-First 模式配置
const crewConfig = ref({
  enabledPhases: ['product_matching', 'material_retrieval', 'expert_review'] as string[],
  minReviewScore: 85,
  maxIterations: 2
})

// Quality-First 模式结果
const crewResults = ref({
  scoringPoints: null as any,
  productMatch: null as any,
  scoringStrategy: null as any,
  materials: null as any,
  reviewResult: null as any,
  currentPhase: '' as string,
  phaseProgress: {} as Record<string, any>
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

    // 阶段1：快速解析，获取目录树结构
    const quickResponse = await tenderApi.parseDocumentStructureQuick(formData)

    if (quickResponse.success) {
      ElMessage.success('目录识别完成，正在分析字数...')

      // 阶段2：补充字数和定位信息
      const enrichResponse = await tenderApi.enrichChapters({
        project_id: form.value.projectId,
        file_path: (quickResponse as any).file_path,
        chapters: (quickResponse as any).chapters,
        toc_end_idx: (quickResponse as any).toc_end_idx
      })

      if (enrichResponse.success) {
        onSuccess(enrichResponse.data)
        ElMessage.success('技术需求文档上传成功')
      } else {
        // 补充信息失败，但目录已识别，仍然算成功
        onSuccess((quickResponse as any))
        ElMessage.warning('字数统计失败，但目录结构已识别')
      }
    } else {
      throw new Error((quickResponse as any).message || (quickResponse as any).error || '解析失败')
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
      // 清空历史文件列表
      historyFiles.value = []
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
        console.log('[TechProposal] 已加载历史技术方案文件')
      }
    }
  })

  // 项目选择后，自动加载历史文件列表
  if (form.value.projectId) {
    await loadFilesList()
  }
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

    // 智能体模式参数
    if (config.value.generationMode) {
      formData.append('generation_mode', config.value.generationMode)
      formData.append('page_count', config.value.pageCount.toString())
      formData.append('content_style', JSON.stringify(config.value.contentStyle))

      // 如果使用模板模式，添加模板名称
      if (config.value.generationMode === '编写专项章节' && config.value.templateName) {
        formData.append('template_name', config.value.templateName)
      }
    }

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
  // 根据生成模式选择API端点
  let apiEndpoint: string
  if (config.value.generationMode === 'Quality-First') {
    apiEndpoint = '/api/agent/generate-crew'  // Quality-First 模式（8智能体协作）

    // 添加 crew 配置参数
    formData.append('crew_config', JSON.stringify({
      skip_product_matching: !crewConfig.value.enabledPhases.includes('product_matching'),
      skip_material_retrieval: !crewConfig.value.enabledPhases.includes('material_retrieval'),
      enable_expert_review: crewConfig.value.enabledPhases.includes('expert_review'),
      min_review_score: crewConfig.value.minReviewScore,
      max_iterations: crewConfig.value.maxIterations
    }))

    // 重置 crew 结果
    crewResults.value = {
      scoringPoints: null,
      productMatch: null,
      scoringStrategy: null,
      materials: null,
      reviewResult: null,
      currentPhase: '',
      phaseProgress: {}
    }
  } else if (config.value.generationMode) {
    apiEndpoint = '/api/agent/generate'  // 其他智能体模式
  } else {
    apiEndpoint = '/api/generate-proposal-stream-v2'  // 传统API（向后兼容）
  }

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

  // ✅ 立即打开编辑器，显示"正在生成中..."占位内容
  showEditor.value = true
  editorContent.value = '<div style="text-align:center; padding:40px; color:#909399;">🔄 技术方案生成中，请稍候...</div>'

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

          // ========================================
          // Quality-First 模式阶段事件处理
          // ========================================
          if (config.value.generationMode === 'Quality-First') {
            // 更新当前阶段
            if (data.phase) {
              crewResults.value.currentPhase = data.phase
              crewResults.value.phaseProgress[data.phase] = {
                status: data.status,
                message: data.message,
                result: data.result
              }
            }

            // 评分点提取完成
            if (data.phase === 'scoring_extraction' && data.status === 'complete') {
              crewResults.value.scoringPoints = data.result
              streamContent.value += `✅ 评分点提取完成: ${data.result?.count || 0}个评分维度\n`
            }

            // 产品匹配完成
            if (data.phase === 'product_matching' && data.status === 'complete') {
              crewResults.value.productMatch = data.result
              const coverage = data.result?.coverage_rate || 0
              streamContent.value += `✅ 产品能力匹配完成: 覆盖率 ${(coverage * 100).toFixed(1)}%\n`
            }

            // 策略规划完成
            if (data.phase === 'strategy_planning' && data.status === 'complete') {
              crewResults.value.scoringStrategy = data.result
              streamContent.value += `✅ 评分策略制定完成: 预估得分 ${data.result?.estimated_score || 0}\n`
            }

            // 素材检索完成
            if (data.phase === 'material_retrieval' && data.status === 'complete') {
              crewResults.value.materials = data.result
              streamContent.value += `✅ 素材检索完成: ${data.result?.package_count || 0}个素材包\n`
            }

            // 大纲生成完成
            if (data.phase === 'outline_generation' && data.status === 'complete') {
              // 更新大纲数据
              if (data.result?.outline) {
                outlineData.value = {
                  chapters: data.result.outline,
                  total_chapters: data.result.chapter_count,
                  total_words: data.result.total_words
                }

                // ✅ 立即在编辑器中显示大纲结构（章节标题+指导信息，内容待填充）
                updateEditorContent(chapterContents)
              }
              streamContent.value += `✅ 大纲生成完成: ${data.result?.chapter_count || 0}章\n`
            }

            // 内容撰写进度
            if (data.phase === 'content_writing') {
              if (data.event === 'chapter_progress') {
                currentChapterNumber = data.chapter_index?.toString() || ''
                streamContent.value += `📝 正在撰写: ${data.chapter_title}\n`
                if (!showEditor.value) {
                  showEditor.value = true
                }
              } else if (data.event === 'chapter_complete' && data.chapter) {
                // 接收完成的章节内容
                const chapterNum = data.chapter?.chapter_number || currentChapterNumber
                if (chapterNum) {
                  chapterContents[chapterNum] = data.chapter?.content || ''
                  updateEditorContent(chapterContents)
                }
                streamContent.value += `✓ ${data.chapter?.title || '章节'} 撰写完成\n`
              }
            }

            // 专家评审完成
            if (data.phase === 'expert_review' && data.status === 'complete') {
              crewResults.value.reviewResult = data.result
              const score = data.result?.overall_score || 0
              const passed = data.result?.pass_recommendation ? '✅通过' : '⚠️需改进'
              streamContent.value += `✅ 专家评审完成: ${score}分 ${passed}\n`
            }

            // 迭代优化
            if (data.phase === 'iteration') {
              if (data.status === 'running') {
                streamContent.value += `🔄 第${data.iteration}轮优化中... (当前${data.current_score}分 → 目标${data.target_score}分)\n`
              } else if (data.status === 'complete') {
                streamContent.value += `✅ 第${data.iteration}轮优化完成: ${data.result?.new_score || 0}分\n`
              }
            }

            // 跳过的阶段
            if (data.status === 'skipped') {
              streamContent.value += `⏭️ 跳过: ${data.message}\n`
            }
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

            // 显示编辑器并加载Word内容
            showEditor.value = true

            // 加载生成的Word文档到编辑器
            if (data.output_file) {
              await loadWordToEditor(data.output_file)
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
            const errorMsg = data.error || data.message || '未知错误'
            streamContent.value += `\n❌ 错误: ${errorMsg}\n`
            if (data.traceback) {
              console.error('[Quality-First] 后端错误堆栈:', data.traceback)
              streamContent.value += `\n📋 详细信息:\n${data.traceback}\n`
            }
            throw new Error(errorMsg)
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
          // 使用 marked 将 Markdown 转换为 HTML
          const renderedContent = marked(content, { breaks: true }) as string
          htmlContent += `<div style="line-height: 1.8; margin: 12px 0;">${renderedContent}</div>\n`
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
        // 使用 marked 将 Markdown 转换为 HTML
        const renderedContent = marked(content, { breaks: true }) as string
        htmlContent += `<div style="line-height: 1.8;">${renderedContent}</div>\n`
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

  // ========================================
  // 统一的主面板样式
  // ========================================
  .main-panel {
    :deep(.el-card__body) {
      padding: 24px;
    }
  }

  .panel-row {
    display: flex;
    gap: 24px;
  }

  .project-row {
    margin-bottom: 24px;  // 1.5倍行距

    .row-item {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 12px;

      .row-label {
        flex-shrink: 0;
        width: 70px;
        font-size: 14px;
        font-weight: 500;
        color: var(--el-text-color-regular);
      }

      .row-select,
      .row-input {
        flex: 1;
      }
    }
  }

  // 文档行样式（复用 project-row 的 row-item 结构）
  .document-row {
    margin-top: 0;
    margin-bottom: 0;

    .row-item {
      // 确保和项目行的对齐一致
      align-items: flex-start;  // 顶部对齐，因为文件条可能更高

      .row-label {
        // 保持和项目行一致的label高度对齐
        line-height: 40px;  // 与 file-chip 高度一致
      }
    }

    .file-chip,
    .file-placeholder {
      flex: 1;
      min-width: 0;  // 防止flex子项溢出
      box-sizing: border-box;  // 确保与 el-input/el-select 一致的盒模型
    }
  }

  // 响应式布局：小屏幕时改为垂直排列
  @media (max-width: 1200px) {
    .panel-row.document-row {
      flex-direction: column;
      gap: 16px;

      .row-item {
        width: 100%;
      }
    }
  }

  @media (max-width: 768px) {
    .panel-row.project-row {
      flex-direction: column;
      gap: 16px;

      .row-item {
        width: 100%;
      }
    }
  }

  // 文件占位区域（未上传时显示）
  .file-placeholder {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 40px;
    padding: 0 16px;
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    background: var(--el-fill-color-lighter);
    transition: all 0.2s;

    &:hover {
      border-color: var(--el-color-primary);
      background: var(--el-color-primary-light-9);
    }

    .placeholder-text {
      font-size: 14px;
      color: var(--el-text-color-placeholder);
    }

    :deep(.document-uploader) {
      .el-upload {
        display: flex;
      }

      .el-button {
        padding: 8px 16px;
        font-size: 13px;
      }
    }
  }

  // 文件条样式
  .file-chip {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 16px;
    height: 40px;
    border-radius: 6px;
    border: 1px solid;
    background: var(--el-fill-color-lighter);

    &--success {
      background: #f0f9eb;
      border-color: #b3e19d;
    }

    &--info {
      background: #ecf5ff;
      border-color: #a0cfff;
    }

    .file-chip-icon {
      flex-shrink: 0;
      font-size: 20px;
      color: #67C23A;
    }

    .file-chip-name {
      flex: 1;
      min-width: 0;
      font-size: 13px;
      color: var(--el-text-color-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .file-chip-tag {
      flex-shrink: 0;
      font-size: 12px;
      color: #67C23A;
      padding: 2px 8px;
      background: rgba(103, 194, 58, 0.1);
      border-radius: 4px;
    }

    .file-chip-close {
      flex-shrink: 0;
      font-size: 12px;
      padding: 4px 8px;
    }
  }

  // 配置区域样式
  .config-section {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid var(--el-border-color-lighter);

    .project-row:last-child {
      margin-bottom: 0;
    }

    .row-radio-group {
      flex: 1;
      display: flex;
      align-items: center;
    }

    .row-checkbox-group {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    // 滑块行特殊样式
    .slider-row {
      flex: 1;

      .slider-wrapper {
        flex: 1;
        min-width: 0;

        :deep(.el-slider) {
          margin-bottom: 24px;  // 为刻度标记留出空间
        }
      }

      .page-hint {
        flex-shrink: 0;
        font-size: 13px;
        color: var(--el-text-color-secondary);
        white-space: nowrap;
        padding: 6px 12px;
        background: var(--el-fill-color-light);
        border-radius: 4px;
        margin-left: 16px;
      }
    }
  }

  // Quality-First 配置面板样式（复用 Element Plus 变量）
  .quality-first-config {
    margin: 16px 0 24px;
    padding: 20px;
    background: var(--el-color-success-light-9);
    border: 1px solid var(--el-color-success-light-5);
    border-radius: 8px;

    .config-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 20px;
      font-size: 15px;
      font-weight: 600;
      color: var(--el-color-success);

      .help-icon {
        margin-left: auto;
        color: var(--el-text-color-secondary);
        cursor: help;
      }
    }

    .panel-row.project-row {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }

  // 操作按钮区域
  .panel-actions {
    display: flex;
    justify-content: center;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  // ========================================
  // 其他卡片样式
  // ========================================
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

  .generation-output {
    .crew-tracker {
      margin-bottom: 20px;
    }
  }

  .editor-section {
    height: 1050px;
    overflow: hidden;

    :deep(.el-card__body) {
      padding: 0;
      height: 1000px;
      overflow: hidden;
    }
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

  // 历史文件折叠面板
  .history-collapse {
    :deep(.el-collapse-item__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-lighter);
      border-radius: 8px;
      font-weight: 600;
    }

    :deep(.el-collapse-item__content) {
      padding: 0;
    }

    .collapse-header {
      display: flex;
      align-items: center;
      width: 100%;
    }

    .filename-cell {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-icon {
        color: var(--el-color-primary);
      }
    }
  }
}
</style>

