<template>
  <div class="point-to-point">
    <!-- 项目选择 -->
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

    <!-- 文档上传 -->
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

      <!-- 文档上传器（当不使用HITL文件时显示） -->
      <DocumentUploader
        v-if="!useHitlFile"
        v-model="form.tenderFiles"
        :http-request="handleTenderUpload"
        accept=".pdf,.doc,.docx"
        :limit="5"
        :max-size="50"
        drag
        tip-text="上传技术需求文档"
        @success="handleUploadSuccess"
      />

      <el-form :model="config" label-width="100px" style="margin-top: 20px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="应答频率">
              <el-select v-model="config.responseFrequency" style="width: 100%">
                <el-option label="每段应答" value="every_paragraph" />
                <el-option label="每页应答" value="every_page" />
                <el-option label="每章节应答" value="every_section" />
                <el-option label="文档末尾统一应答" value="end_of_document" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="应答方式">
              <el-radio-group v-model="config.responseMode">
                <el-radio label="simple">简单模板应答</el-radio>
                <el-radio label="ai">AI智能应答</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-if="config.responseMode === 'ai'">
            <el-form-item label="AI模型">
              <el-select v-model="config.aiModel" style="width: 100%">
                <el-option label="GPT5（最强推理）" value="shihuang-gpt5" />
                <el-option label="Claude Sonnet 4.5（标书专用）" value="shihuang-claude-sonnet-45" />
                <el-option label="GPT4o Mini（推荐-默认）" value="shihuang-gpt4o-mini" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="action-controls">
        <el-button
          type="success"
          size="large"
          :disabled="!canExtract"
          :loading="generating"
          @click="processPointToPointDirect"
        >
          直接生成Word文档
        </el-button>
      </div>
    </el-card>

    <!-- 要求提取中 -->
    <el-card v-if="extracting" class="extracting-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>正在提取招标要求...</span>
          <el-progress
            :percentage="extractProgress"
            :status="extractProgress === 100 ? 'success' : undefined"
            style="width: 300px"
          />
        </div>
      </template>

      <SSEStreamViewer
        :content="extractContent"
        :is-streaming="extracting"
      />
    </el-card>

    <!-- 富文本编辑器（生成时立即显示） -->
    <el-card v-if="showEditor" class="editor-section" shadow="never">
      <RichTextEditor
        ref="editorRef"
        v-model="editorContent"
        title="点对点应答文档"
        :streaming="generating"
        :height="700"
        @save="handleEditorSave"
        @preview="previewDocument"
        @export="downloadDocument"
      />
    </el-card>

    <!-- 原始生成结果（折叠查看） -->
    <el-collapse v-if="showEditor && generationResult" v-model="activeCollapse" class="result-collapse">
      <el-collapse-item name="result" title="📄 查看原始生成结果">
        <el-card class="result-section" shadow="never">
          <template #header>
            <div class="card-header">
              <span>✅ 生成结果</span>
              <div class="header-actions">
                <el-button
                  type="primary"
                  size="large"
                  :icon="View"
                  @click="previewDocument"
                >
                  预览文档
                </el-button>
                <el-button
                  type="success"
                  size="large"
                  :icon="Download"
                  @click="downloadDocument"
                >
                  下载Word文档
                </el-button>

                <!-- 同步状态显示 -->
                <el-button
                  v-if="!synced"
                  type="info"
                  size="large"
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
                  size="large"
                  :icon="RefreshRight"
                  @click="processPointToPointDirect"
                >
                  重新生成
                </el-button>
              </div>
            </div>
          </template>

          <!-- 处理结果展示 -->
          <div class="result-content">
            <!-- 成功消息 -->
            <el-alert
              type="success"
              :title="generationResult.message"
              :closable="false"
              show-icon
              style="margin-bottom: 20px"
            />

            <!-- 处理统计 -->
            <StatsCard
              v-if="generationResult.stats && Object.keys(generationResult.stats).length > 0"
              title="处理统计"
              :stats="generationResult.stats"
            />

            <!-- 文件信息 -->
            <div class="file-info-section">
              <h4>生成文件</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="文件名">
                  {{ getFileName(generationResult.outputFile) }}
                </el-descriptions-item>
                <el-descriptions-item label="下载地址">
                  <el-link :href="generationResult.downloadUrl" type="primary">
                    {{ getFileName(generationResult.downloadUrl) }}
                  </el-link>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
      </el-collapse-item>
    </el-collapse>

    <!-- 要求列表 -->
    <el-card v-if="requirements.length > 0" class="requirements-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>招标要求列表 (共 {{ requirements.length }} 条)</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索要求..."
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterCategory"
              placeholder="筛选分类"
              clearable
              style="width: 150px"
            >
              <el-option label="全部" value="" />
              <el-option label="技术要求" value="technical" />
              <el-option label="商务要求" value="business" />
              <el-option label="资质要求" value="qualification" />
              <el-option label="其他要求" value="other" />
            </el-select>
            <el-button
              type="primary"
              :disabled="selectedRequirements.length === 0"
              :loading="generating"
              @click="generateResponses"
            >
              生成应答 ({{ selectedRequirements.length }})
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredRequirements"
        border
        @selection-change="handleSelectionChange"
        max-height="500"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requirement" label="招标要求" min-width="300">
          <template #default="{ row }">
            <div class="requirement-text">{{ row.requirement }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="应答状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.response"
              type="primary"
              size="small"
              text
              @click="viewResponse(row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- AI生成流式输出 -->
    <el-card v-if="generating" class="generation-output" shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI正在生成点对点应答...</span>
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

    <!-- 应答结果列表 -->
    <el-card v-if="hasResponses" class="responses-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>点对点应答结果</span>
          <div class="header-actions">
            <el-button type="success" :icon="Download" @click="exportResponses">
              导出应答文档
            </el-button>
          </div>
        </div>
      </template>

      <el-collapse v-model="activeResponses" accordion>
        <el-collapse-item
          v-for="req in requirements.filter(r => r.response)"
          :key="req.id"
          :name="req.id"
        >
          <template #title>
            <div class="collapse-title">
              <el-tag :type="getCategoryType(req.category)" size="small">
                {{ getCategoryLabel(req.category) }}
              </el-tag>
              <span class="requirement-preview">{{ req.requirement }}</span>
              <el-tag :type="getStatusType(req.status)" size="small">
                {{ getStatusLabel(req.status) }}
              </el-tag>
            </div>
          </template>

          <div class="response-content">
            <div class="response-item">
              <h4>招标要求</h4>
              <div class="requirement-detail">{{ req.requirement }}</div>
            </div>

            <div class="response-item">
              <h4>我方应答</h4>
              <SSEStreamViewer
                :content="req.response || ''"
                :is-streaming="false"
                :enable-markdown="true"
              />
            </div>

            <div class="response-item" v-if="req.compliance">
              <h4>符合性说明</h4>
              <el-tag :type="req.compliance === '完全符合' ? 'success' : 'warning'" size="large">
                {{ req.compliance }}
              </el-tag>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 应答详情对话框 -->
    <el-dialog
      v-model="responseDialogVisible"
      title="应答详情"
      width="800px"
      destroy-on-close
    >
      <div v-if="currentRequirement" class="response-dialog">
        <div class="dialog-section">
          <h4>招标要求</h4>
          <div class="requirement-detail">{{ currentRequirement.requirement }}</div>
        </div>

        <div class="dialog-section">
          <h4>我方应答</h4>
          <SSEStreamViewer
            :content="currentRequirement.response || ''"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </div>

        <div class="dialog-section" v-if="currentRequirement.compliance">
          <h4>符合性</h4>
          <el-tag :type="currentRequirement.compliance === '完全符合' ? 'success' : 'warning'">
            {{ currentRequirement.compliance }}
          </el-tag>
        </div>
      </div>
    </el-dialog>

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
                <el-button type="success" size="small" @click="downloadFile(row)">
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
import { Download, Search, Document, View, RefreshRight, Edit, Upload } from '@element-plus/icons-vue'
import { DocumentUploader, SSEStreamViewer, DocumentPreview, HitlFileAlert, RichTextEditor, StatsCard, HistoryFilesPanel } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import { useProjectDocuments, useHitlIntegration } from '@/composables'
import { downloadFile } from '@/utils/helpers'
import type { Project, UploadUserFile } from '@/types'

// ============================================
// 使用 useProjectDocuments Composable
// ============================================
const {
  projects,
  selectedProject,
  currentDocuments,
  loadProjects,
  handleProjectChange: handleProjectChangeComposable,
  restoreProjectFromStore
} = useProjectDocuments()

// ============================================
// 使用 useHitlIntegration Composable
// ============================================
const {
  useHitlFile,
  hitlFileInfo,
  hasHitlFile,
  syncing,
  synced,
  loadFromHITL,
  cancelHitlFile,
  syncToHitl
} = useHitlIntegration({
  onFileLoaded: () => {
    // 清空上传的文件
    form.value.tenderFiles = []
  }
})

interface Requirement {
  id: number
  category: 'technical' | 'business' | 'qualification' | 'other'
  requirement: string
  priority: '高' | '中' | '低'
  status: 'pending' | 'generated' | 'reviewed'
  response?: string
  compliance?: '完全符合' | '部分符合' | '不符合'
}

// 表单数据（项目列表由 Composable 提供）
const form = ref({
  projectId: null as number | null,
  tenderFiles: [] as UploadUserFile[]
})

// 处理配置
const config = ref({
  responseFrequency: 'every_paragraph' as 'every_paragraph' | 'every_page' | 'every_section' | 'end_of_document',
  responseMode: 'simple' as 'ai' | 'simple',
  aiModel: 'shihuang-gpt4o-mini'
})

// 提取状态
const extracting = ref(false)
const extractProgress = ref(0)
const extractContent = ref('')

// 要求列表
const requirements = ref<Requirement[]>([])
const selectedRequirements = ref<Requirement[]>([])
const searchKeyword = ref('')
const filterCategory = ref('')

// 筛选后的要求
const filteredRequirements = computed(() => {
  let filtered = requirements.value

  if (searchKeyword.value) {
    filtered = filtered.filter(req =>
      req.requirement.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  if (filterCategory.value) {
    filtered = filtered.filter(req => req.category === filterCategory.value)
  }

  return filtered
})

// 生成状态
const generating = ref(false)
const generationProgress = ref(0)
const streamContent = ref('')

// 生成结果
const outputFile = ref('')
const downloadUrl = ref('')
const processingStats = ref<any>(null)

// 生成结果对象（参考商务应答）
interface GenerationResult {
  success: boolean
  outputFile: string
  downloadUrl: string
  stats: {
    inline_reply?: boolean
    gray_shading?: boolean
    format_preserved?: boolean
    requirements_count?: number
    responses_count?: number
    response_mode?: string
    model_name?: string | null
  }
  message: string
}
const generationResult = ref<GenerationResult | null>(null)

// 编辑器状态（参考商务应答）
const showEditor = ref(false)
const editorRef = ref<any>(null)
const editorContent = ref('')
const editorSaving = ref(false)

// 折叠面板状态
const activeCollapse = ref<string[]>([])

// 当前项目的点对点应答文件（类似 Response.vue 的 generationResult）
const currentP2pFile = ref<any>(null)

// 所有历史文件列表（可选功能）
const historyFiles = ref<any[]>([])
const loadingHistory = ref(false)
const showAllHistory = ref<string[]>([])

// 预览相关状态
const previewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

// 是否有应答结果
const hasResponses = computed(() =>
  requirements.value.some(req => req.response)
)

// 应答展开项
const activeResponses = ref<number[]>([])

// 应答详情对话框
const responseDialogVisible = ref(false)
const currentRequirement = ref<Requirement | null>(null)

// 能否提取 - 修复：使用HITL文件时也应该允许
const canExtract = computed(() =>
  form.value.projectId && (form.value.tenderFiles.length > 0 || useHitlFile.value)
)

// 自定义上传函数：招标文档
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
      ElMessage.success('招标文档上传成功')
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (error: any) {
    onError(error)
    ElMessage.error(error.message || '招标文档上传失败')
  }
}

// 项目切换（使用 Composable + 页面特定逻辑）
const handleProjectChange = async () => {
  await handleProjectChangeComposable(form.value.projectId, {
    // 清空回调：清空页面特定状态
    onClear: () => {
      form.value.tenderFiles = []
      requirements.value = []
      selectedRequirements.value = []
      currentP2pFile.value = null
      // 清空编辑器状态
      generationResult.value = null
      showEditor.value = false
      editorContent.value = ''
      activeCollapse.value = []
      // 清空历史文件列表
      historyFiles.value = []
      // 取消使用HITL文件
      if (useHitlFile.value) {
        cancelHitlFile()
      }
    },
    // 文档加载完成回调：使用共享函数
    onDocumentsLoaded: handleDocumentsLoaded
  })

  // 项目选择后，自动加载历史文件列表
  if (form.value.projectId) {
    await loadFilesList()
  }
}

// 上传成功
const handleUploadSuccess = () => {
  ElMessage.success('文档上传成功')
}

// ============================================
// 共享的文档加载回调（避免代码重复）
// ============================================
const handleDocumentsLoaded = (docs: ProjectDocuments) => {
  // 1. 优先使用技术需求文档（点对点应答的主要输入）
  if (docs.technicalFile) {
    loadFromHITL(docs, 'technicalFile')
  } else if (docs.tenderFile) {
    // 2. 备选：如果没有技术需求文档，使用招标文档
    form.value.tenderFiles = [docs.tenderFile]
  }

  // 3. 自动显示当前项目的历史点对点应答文件（不自动打开编辑器）
  if (docs.p2pResponseFile) {
    currentP2pFile.value = docs.p2pResponseFile
    showEditor.value = false  // 明确不自动打开编辑器

    console.log('[PointToPoint] 检测到历史点对点应答文件:', docs.p2pResponseFile.outputFile)
    ElMessage.info('检测到历史点对点应答文件，点击"在编辑器中打开"可编辑')
  }
}

// 提取招标要求
const extractRequirements = async () => {
  extracting.value = true
  extractProgress.value = 0
  extractContent.value = ''
  requirements.value = []

  try {
    await simulateExtraction()
    ElMessage.success('招标要求提取完成')
  } catch (error) {
    console.error('提取失败:', error)
    ElMessage.error('提取失败，请重试')
  } finally {
    extracting.value = false
  }
}

// 模拟提取过程
const simulateExtraction = async () => {
  return new Promise<void>((resolve) => {
    const stages = [
      { progress: 25, message: '正在解析招标文档...' },
      { progress: 50, message: '正在识别招标要求...' },
      { progress: 75, message: '正在分类整理...' },
      { progress: 100, message: '提取完成！' }
    ]

    let currentStage = 0

    const interval = setInterval(() => {
      if (currentStage < stages.length) {
        const stage = stages[currentStage]
        extractProgress.value = stage.progress
        extractContent.value += `\n[${stage.progress}%] ${stage.message}`
        currentStage++
      } else {
        clearInterval(interval)

        // 生成模拟要求
        requirements.value = [
          {
            id: 1,
            category: 'technical',
            requirement: '系统应支持不少于10000个并发用户同时在线访问',
            priority: '高',
            status: 'pending'
          },
          {
            id: 2,
            category: 'technical',
            requirement: '系统响应时间应不超过3秒',
            priority: '高',
            status: 'pending'
          },
          {
            id: 3,
            category: 'business',
            requirement: '项目实施周期不超过6个月',
            priority: '高',
            status: 'pending'
          },
          {
            id: 4,
            category: 'qualification',
            requirement: '投标人应具有ISO 9001质量管理体系认证',
            priority: '中',
            status: 'pending'
          },
          {
            id: 5,
            category: 'qualification',
            requirement: '投标人应具有信息安全等级保护三级资质',
            priority: '中',
            status: 'pending'
          },
          {
            id: 6,
            category: 'business',
            requirement: '质保期不少于2年',
            priority: '中',
            status: 'pending'
          },
          {
            id: 7,
            category: 'technical',
            requirement: '系统应支持移动端访问（iOS和Android）',
            priority: '中',
            status: 'pending'
          },
          {
            id: 8,
            category: 'other',
            requirement: '投标文件应包含详细的培训计划',
            priority: '低',
            status: 'pending'
          }
        ]

        resolve()
      }
    }, 600)
  })
}

// 选择变化
const handleSelectionChange = (selection: Requirement[]) => {
  selectedRequirements.value = selection
}

// 生成应答
const generateResponses = async () => {
  if (selectedRequirements.value.length === 0) {
    ElMessage.warning('请选择要生成应答的要求')
    return
  }

  generating.value = true
  generationProgress.value = 0
  streamContent.value = ''

  try {
    await simulateGeneration()
    ElMessage.success('点对点应答生成完成')
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    generating.value = false
  }
}

// 模拟生成过程
const simulateGeneration = async () => {
  return new Promise<void>((resolve) => {
    const total = selectedRequirements.value.length
    let current = 0

    const interval = setInterval(() => {
      if (current < total) {
        const req = selectedRequirements.value[current]
        generationProgress.value = Math.round(((current + 1) / total) * 100)
        streamContent.value += `\n[${current + 1}/${total}] 正在生成"${req.requirement.substring(0, 20)}..."的应答`

        // 更新状态和生成应答
        const index = requirements.value.findIndex(r => r.id === req.id)
        if (index !== -1) {
          requirements.value[index] = {
            ...requirements.value[index],
            status: 'generated',
            response: generateMockResponse(req),
            compliance: Math.random() > 0.3 ? '完全符合' : '部分符合'
          }
        }

        current++
      } else {
        clearInterval(interval)
        resolve()
      }
    }, 800)
  })
}

// 直接生成Word文档（调用真实API）
const processPointToPointDirect = async () => {
  if (!form.value.projectId || !selectedProject.value) {
    ElMessage.error('请先选择项目')
    return
  }

  // 检查是否使用HITL文件或上传文件
  if (!useHitlFile.value && form.value.tenderFiles.length === 0) {
    ElMessage.error('请先上传招标文档或使用技术文件')
    return
  }

  generating.value = true
  generationProgress.value = 0
  generationResult.value = null

  // 立即显示编辑器（参考商务应答）
  showEditor.value = true
  editorContent.value = '<h1>📄 点对点应答文档</h1><p style="color: #909399;">AI正在生成内联应答，请稍候...</p>'

  // 滚动到编辑器
  setTimeout(() => {
    document.querySelector('.editor-section')?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }, 100)

  try {
    const formData = new FormData()

    // 判断是使用HITL文件还是上传文件
    if (useHitlFile.value && hitlFileInfo.value) {
      // 使用HITL技术需求文件
      formData.append('use_hitl_technical_file', 'true')
      formData.append('project_id', form.value.projectId.toString())
    } else {
      // 使用上传的文件
      if (form.value.tenderFiles.length > 0 && form.value.tenderFiles[0].raw) {
        formData.append('file', form.value.tenderFiles[0].raw)
      }
    }

    // 添加基本参数
    formData.append('companyId', selectedProject.value.company_id.toString())
    formData.append('projectName', selectedProject.value.project_name || '')

    // 添加处理配置
    formData.append('responseFrequency', config.value.responseFrequency)
    formData.append('responseMode', config.value.responseMode)
    formData.append('aiModel', config.value.aiModel)

    // 调用后端API
    const response = await fetch('/api/process-point-to-point', {
      method: 'POST',
      body: formData
    })

    console.log('点对点应答API响应状态:', response.status, response.statusText)

    const result = await response.json()
    console.log('点对点应答API响应数据:', result)

    if (result.success) {
      outputFile.value = result.output_file
      downloadUrl.value = result.download_url
      processingStats.value = result.stats

      // 设置生成结果对象（参考商务应答）
      generationResult.value = {
        success: true,
        outputFile: result.output_file,
        downloadUrl: result.download_url,
        stats: result.stats || {},
        message: result.message || '点对点应答生成完成'
      }

      // 加载Word文档到编辑器
      await loadWordToEditor(result.output_file)

      ElMessage.success('点对点应答生成完成！可以编辑了')

      // 自动同步到项目（如果有输出文件）
      if (result.output_file) {
        await syncToHitl(
          form.value.projectId!,
          result.output_file,
          'point_to_point'
        )
      }
    } else {
      // 改进错误消息提取
      let errorMsg = '处理失败'
      if (result.error) {
        // 如果error是对象，提取message字段
        if (typeof result.error === 'object' && result.error.message) {
          errorMsg = result.error.message
        } else if (typeof result.error === 'string') {
          errorMsg = result.error
        } else {
          errorMsg = JSON.stringify(result.error)
        }
      } else if (result.message) {
        errorMsg = result.message
      }

      console.error('处理失败，错误信息:', errorMsg, '完整结果:', result)
      throw new Error(errorMsg)
    }
  } catch (error: any) {
    console.error('点对点应答处理失败:', error)

    // 改进错误消息提取
    let errorMessage = '处理失败，请重试'
    if (typeof error === 'string') {
      errorMessage = error
    } else if (error?.message) {
      errorMessage = error.message
    } else if (error?.error) {
      errorMessage = error.error
    } else if (typeof error === 'object') {
      // 尝试从对象中提取有用信息
      errorMessage = JSON.stringify(error)
    }

    // 在编辑器中也显示错误
    if (editorRef.value) {
      editorRef.value.appendContent(`<p style="color: red;">❌ 错误: ${errorMessage}</p>`)
    }

    ElMessage.error({
      message: errorMessage,
      duration: 5000
    })
  } finally {
    generating.value = false
  }
}

// 生成模拟应答
const generateMockResponse = (req: Requirement): string => {
  const responses: Record<string, string> = {
    technical: `## 技术响应\n\n我方系统完全满足该技术要求：\n\n### 方案说明\n1. 采用xxx架构设计，支持高并发访问\n2. 经过压力测试，可支持xxx并发用户\n3. 配置xxx服务器集群，确保系统稳定性\n\n### 技术指标\n- 并发处理能力：满足要求\n- 响应时间：平均2秒以内\n- 系统可用性：99.9%\n\n### 证明材料\n详见附件《技术方案书》第xx页`,
    business: `## 商务响应\n\n我方完全接受该商务条款：\n\n### 承诺内容\n1. 严格按照要求执行\n2. 提供相应的保障措施\n3. 确保按时完成\n\n### 具体安排\n- 项目周期：符合要求\n- 质保期：满足要求\n- 验收标准：按照招标文件执行\n\n### 服务保障\n详见附件《商务应答书》第xx页`,
    qualification: `## 资质响应\n\n我方具备该项资质要求：\n\n### 资质证明\n1. 持有xxx证书，证书编号：xxx\n2. 证书有效期：xxxx年xx月至xxxx年xx月\n3. 认证范围：覆盖本项目需求\n\n### 相关业绩\n- 近三年完成类似项目xx个\n- 项目验收合格率100%\n\n### 附件材料\n详见附件《资质证明文件》`,
    other: `## 其他要求响应\n\n我方承诺满足该要求：\n\n### 具体安排\n1. 制定详细计划\n2. 配备专业人员\n3. 提供完整文档\n\n### 执行标准\n- 严格按照招标文件要求\n- 确保质量和进度\n\n### 相关文件\n详见附件相关章节`
  }

  return responses[req.category] || '我方完全响应该要求。'
}

// 停止生成
const stopGeneration = () => {
  generating.value = false
  ElMessage.info('已停止生成')
}

// 加载Word文档到编辑器（参考商务应答）
const loadWordToEditor = async (filePath: string) => {
  try {
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

      console.log('[PointToPoint] Word文档已加载到编辑器')
    } else {
      throw new Error(result.error || '转换失败')
    }
  } catch (error: any) {
    console.error('[PointToPoint] 加载文档到编辑器失败:', error)

    // 如果转换失败，显示基础提示
    editorContent.value = `
      <h1>📄 点对点应答文档</h1>
      <div style="padding: 20px; background: #FFF3E0; border-left: 4px solid #FF9800; margin: 16px 0;">
        <p><strong>⚠️ 提示：</strong>Word文档转换失败</p>
        <p>原因：${error.message}</p>
        <p>您可以：</p>
        <ul>
          <li>点击下方"查看原始生成结果"下载Word文档查看</li>
          <li>Word文档中已包含内联回复（灰色底纹标记）</li>
        </ul>
      </div>
    `

    ElMessage.warning('Word转换HTML失败，请使用下载功能查看')
  }
}

// 保存编辑器内容（参考商务应答）
const handleEditorSave = async (htmlContent: string) => {
  if (!form.value.projectId) {
    ElMessage.error('项目ID无效')
    return
  }

  editorSaving.value = true

  try {
    // 调用后端API将HTML保存为Word
    const response = await fetch('/api/editor/save-html-to-word', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        html_content: htmlContent,
        project_id: form.value.projectId,
        document_type: 'point_to_point',
        original_file: generationResult.value?.outputFile
      })
    })

    const result = await response.json()

    if (result.success) {
      // 更新生成结果
      generationResult.value = {
        success: true,
        outputFile: result.output_file,
        downloadUrl: result.download_url,
        stats: generationResult.value?.stats || {},
        message: '文档已保存'
      }

      console.log('[PointToPoint] 编辑内容已保存:', result.output_file)

      // 同步到HITL
      if (result.output_file) {
        await syncToHitl(
          form.value.projectId,
          result.output_file,
          'point_to_point'
        )
      }
    } else {
      throw new Error(result.error || '保存失败')
    }
  } catch (error: any) {
    console.error('[PointToPoint] 保存编辑内容失败:', error)
    throw error // 让RichTextEditor显示错误
  } finally {
    editorSaving.value = false
  }
}

// 查看应答
const viewResponse = (req: Requirement) => {
  currentRequirement.value = req
  responseDialogVisible.value = true
}

// 预览文档（用于编辑器）
const previewDocument = () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可预览')
    return
  }

  if (!generationResult.value.downloadUrl) {
    ElMessage.warning('文档地址无效')
    return
  }

  previewFileUrl.value = generationResult.value.outputFile
  previewFileName.value = `点对点应答-${selectedProject.value?.project_name || '文档'}.docx`
  previewVisible.value = true
}

// 下载文档（用于编辑器）
const downloadDocument = () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可下载')
    return
  }

  try {
    const url = generationResult.value.downloadUrl
    const filename = `点对点应答-${selectedProject.value?.project_name || '文档'}-${Date.now()}.docx`

    // 使用公用下载函数
    downloadFile(url, filename)

    ElMessage.success('Word文档下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('文档下载失败，请重试')
  }
}

// 手动同步到HITL
const handleSyncToHitl = async () => {
  if (!generationResult.value?.outputFile) {
    ElMessage.warning('没有可同步的文件')
    return
  }

  if (!form.value.projectId) {
    ElMessage.error('项目ID无效')
    return
  }

  await syncToHitl(
    form.value.projectId,
    generationResult.value.outputFile,
    'point_to_point'
  )
}

// 导出应答
const exportResponses = () => {
  const responsesText = requirements.value
    .filter(req => req.response)
    .map((req, index) => {
      return `${index + 1}. 【${getCategoryLabel(req.category)}】${req.requirement}\n\n${req.response}\n\n符合性：${req.compliance}\n\n---\n`
    })
    .join('\n')

  const blob = new Blob([`# 点对点应答文档\n\n${responsesText}`], {
    type: 'text/plain;charset=utf-8'
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `点对点应答-${selectedProject.value?.project_name || 'export'}-${Date.now()}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('导出成功')
}

// 获取分类标签
const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    technical: '技术要求',
    business: '商务要求',
    qualification: '资质要求',
    other: '其他要求'
  }
  return labels[category] || category
}

// 获取分类类型
const getCategoryType = (category: string) => {
  const types: Record<string, any> = {
    technical: 'primary',
    business: 'success',
    qualification: 'warning',
    other: 'info'
  }
  return types[category] || ''
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const types: Record<string, any> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return types[priority] || ''
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待生成',
    generated: '已生成',
    reviewed: '已审核'
  }
  return labels[status] || status
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    pending: 'info',
    generated: 'success',
    reviewed: 'primary'
  }
  return types[status] || ''
}

/**
 * 从完整路径中提取文件名
 * @param path 完整文件路径或URL
 * @returns 文件名
 */
const getFileName = (path: string | undefined) => {
  if (!path) return '-'

  // 如果是URL，先解码
  let decodedPath = path
  try {
    decodedPath = decodeURIComponent(path)
  } catch {
    // 解码失败则使用原始路径
  }

  // 提取最后一个斜杠后的文件名
  const parts = decodedPath.split('/')
  return parts[parts.length - 1] || '-'
}

// ============================================
// P1功能：历史文件列表
// ============================================

// 加载历史文件列表（仅当前项目）
const loadFilesList = async () => {
  if (!form.value.projectId) {
    historyFiles.value = []
    return
  }

  loadingHistory.value = true
  try {
    const response = await fetch(`/api/point-to-point/files?project_id=${form.value.projectId}`)
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

// ============================================
// P1功能：文档预览
// ============================================

// 预览文件 - 使用 DocumentPreview 组件
const previewFile = (file: any) => {
  if (!file.file_path) {
    ElMessage.warning('无法获取文件信息')
    return
  }

  previewFileUrl.value = file.file_path
  previewFileName.value = file.filename
  previewVisible.value = true
}

// 下载历史文件（使用公用函数）
const downloadHistoryFileFunc = async (file: any) => {
  try {
    const downloadUrl = `/api/point-to-point/download?file_path=${encodeURIComponent(file.file_path)}`
    downloadFile(downloadUrl, file.filename)
    ElMessage.success('文件下载中...')
  } catch (error: any) {
    console.error('下载文件失败:', error)
    ElMessage.error(error.message || '下载文件失败')
  }
}

// ============================================
// 当前项目历史文件操作
// ============================================

// 预览当前项目的点对点应答文件
const previewCurrentFile = () => {
  if (!currentP2pFile.value) return

  previewFileUrl.value = currentP2pFile.value.outputFile
  previewFileName.value = `点对点应答-${selectedProject.value?.project_name || '文档'}.docx`
  previewVisible.value = true
}

// 下载当前项目的点对点应答文件（使用公用函数）
const downloadCurrentFile = () => {
  if (!currentP2pFile.value) return

  try {
    const filename = `点对点应答-${selectedProject.value?.project_name || '文档'}-${Date.now()}.docx`
    downloadFile(currentP2pFile.value.downloadUrl, filename)
    ElMessage.success('文档下载成功')
  } catch (error: any) {
    console.error('下载失败:', error)
    ElMessage.error('文档下载失败，请重试')
  }
}

// 重新生成当前项目的点对点应答文件
const regenerateCurrentFile = () => {
  // 清空当前文件，触发重新生成流程
  currentP2pFile.value = null
  ElMessage.info('请配置参数后点击"直接生成Word文档"按钮重新生成')
}

// 在编辑器中打开历史文件（参考商务应答）
const openHistoryInEditor = async () => {
  if (!currentP2pFile.value?.outputFile) {
    ElMessage.error('历史文件信息无效')
    return
  }

  try {
    // 显示编辑器
    showEditor.value = true

    // 设置generationResult以便编辑器可以使用
    generationResult.value = {
      success: true,
      outputFile: currentP2pFile.value.outputFile,
      downloadUrl: currentP2pFile.value.downloadUrl || '',
      stats: currentP2pFile.value.stats || {},
      message: currentP2pFile.value.message || '历史点对点应答文件'
    }

    // 加载Word文档到编辑器
    await loadWordToEditor(currentP2pFile.value.outputFile)

    ElMessage.success('历史文件已加载到编辑器')

    // 滚动到编辑器
    setTimeout(() => {
      document.querySelector('.editor-section')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }, 100)
  } catch (error: any) {
    console.error('[PointToPoint] 打开历史文件失败:', error)
    ElMessage.error('打开历史文件失败: ' + error.message)
  }
}

onMounted(async () => {
  // 加载项目列表
  await loadProjects()

  // 从Store恢复项目（如果是从HITL页面跳转过来）
  const restoredProjectId = await restoreProjectFromStore({
    onClear: () => {
      form.value.tenderFiles = []
      requirements.value = []
      selectedRequirements.value = []
      currentP2pFile.value = null
      // 清空编辑器状态
      generationResult.value = null
      showEditor.value = false
      editorContent.value = ''
      // 取消使用HITL文件
      if (useHitlFile.value) {
        cancelHitlFile()
      }
    },
    // 文档加载完成回调：使用共享函数
    onDocumentsLoaded: handleDocumentsLoaded
  })

  // 如果成功恢复项目，同步到表单
  if (restoredProjectId) {
    form.value.projectId = restoredProjectId
    console.log('✅ 已从Store恢复项目:', restoredProjectId)
  }
})
</script>

<style scoped lang="scss">

.point-to-point {
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
  .extracting-section,
  .requirements-section,
  .generation-output,
  .responses-section,
  .current-file-section,
  .editor-section,
  .result-section {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
    }
  }

  .editor-section {
    min-height: 600px;

    :deep(.el-card__body) {
      padding: 0;
    }
  }

  .result-collapse {
    margin-top: 20px;

    :deep(.el-collapse-item__header) {
      padding: 12px 20px;
      background: var(--el-fill-color-lighter);
      font-weight: 600;
    }

    :deep(.el-collapse-item__content) {
      padding: 0;
    }
  }

  .current-file-content {
    .current-file-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      margin-top: 20px;
    }
  }

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
  }

  .filename-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: var(--el-color-primary);
    }
  }

  .action-controls {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 20px;
  }

  .requirement-text {
    line-height: 1.6;
  }

  .collapse-title {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;

    .requirement-preview {
      flex: 1;
      font-size: 14px;
      color: var(--el-text-color-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .response-content {
    .response-item {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .requirement-detail {
        padding: 12px;
        background: var(--el-fill-color-light);
        border-radius: 6px;
        line-height: 1.6;
      }
    }
  }

  .result-content {
    .file-info-section {
      margin-bottom: 24px;

      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      :deep(.el-descriptions__label) {
        font-weight: 600;
      }
    }
  }

  .response-dialog {
    .dialog-section {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .requirement-detail {
        padding: 12px;
        background: var(--el-fill-color-light);
        border-radius: 6px;
        line-height: 1.6;
      }
    }
  }
}
</style>
