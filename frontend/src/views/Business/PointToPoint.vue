<template>
  <div class="point-to-point">
    <!-- 项目选择 -->
    <el-card class="project-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Step 1: 选择项目</span>
        </div>
      </template>

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
    <el-card v-if="form.projectId" class="upload-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Step 2: 选择技术需求文档</span>
          <el-button
            v-if="currentDocuments.technicalFile && !useHitlFile"
            type="primary"
            size="small"
            @click="loadFromHITL(currentDocuments, 'technicalFile')"
          >
            使用HITL技术需求文件
          </el-button>
        </div>
      </template>

      <!-- HITL文件Alert -->
      <HitlFileAlert
        v-if="useHitlFile"
        :file-info="hitlFileInfo"
        label="使用HITL技术需求文件:"
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
        tip-text="上传技术需求文档，或使用HITL流程中提取的技术需求文件"
        @success="handleUploadSuccess"
      />

      <!-- 处理配置 -->
      <el-divider>处理配置</el-divider>

      <el-form :model="config" label-width="100px" class="config-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="投标角色">
              <el-radio-group v-model="config.bidRole">
                <el-radio label="primary">应标</el-radio>
                <el-radio label="secondary">陪标</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>

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
        </el-row>

        <el-row :gutter="20">
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
                <el-option label="始皇-GPT4o迷你版（快速高效）" value="shihuang-gpt4o-mini" />
                <el-option label="始皇-GPT4专业版（深度分析）" value="shihuang-gpt4" />
                <el-option label="GPT-4O Mini（推荐）" value="gpt-4o-mini" />
                <el-option label="GPT-4O（高质量）" value="gpt-4o" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="action-controls">
        <el-button
          type="primary"
          size="large"
          :disabled="!canExtract"
          :loading="extracting"
          @click="extractRequirements"
        >
          提取招标要求
        </el-button>
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

    <!-- 当前项目的历史文件（类似 Response.vue 的生成结果展示） -->
    <el-card v-if="currentP2pFile" class="current-file-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>📄 该项目的点对点应答文件</span>
          <div class="header-actions">
            <el-button
              type="primary"
              :icon="View"
              @click="previewCurrentFile"
            >
              预览文档
            </el-button>
            <el-button
              type="success"
              :icon="Download"
              @click="downloadCurrentFile"
            >
              下载文档
            </el-button>
            <el-button
              type="info"
              :icon="RefreshRight"
              @click="regenerateCurrentFile"
            >
              重新生成
            </el-button>
          </div>
        </div>
      </template>

      <div class="current-file-content">
        <el-alert
          type="info"
          :title="currentP2pFile.message || '该项目已有点对点应答文件'"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <!-- 文件信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件路径">
            {{ currentP2pFile.outputFile }}
          </el-descriptions-item>
          <el-descriptions-item label="生成时间" v-if="currentP2pFile.generated_at">
            {{ formatDate(currentP2pFile.generated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="统计信息" :span="2" v-if="currentP2pFile.stats">
            <el-tag v-for="(value, key) in currentP2pFile.stats" :key="key" style="margin-right: 8px">
              {{ key }}: {{ value }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 所有历史文件列表（可折叠，可选功能） -->
    <el-collapse v-model="showAllHistory" class="history-collapse">
      <el-collapse-item name="history">
        <template #title>
          <div class="collapse-header">
            <span>📂 查看所有历史处理文件 ({{ historyFiles.length }})</span>
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
import { Download, Search, Document, View, RefreshRight } from '@element-plus/icons-vue'
import { DocumentUploader, SSEStreamViewer, DocumentPreview, HitlFileAlert } from '@/components'
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
  bidRole: 'primary' as 'primary' | 'secondary',
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
      // 取消使用HITL文件
      if (useHitlFile.value) {
        cancelHitlFile()
      }
    },
    // 文档加载完成回调：使用共享函数
    onDocumentsLoaded: handleDocumentsLoaded
  })
}

// 上传成功
const handleUploadSuccess = () => {
  ElMessage.success('文档上传成功')
}

// ============================================
// 共享的文档加载回调（避免代码重复）
// ============================================
const handleDocumentsLoaded = (docs: ProjectDocuments) => {
  // 收集加载的文档信息
  const loadedItems: string[] = []

  // 1. 优先使用技术需求文档（点对点应答的主要输入）
  if (docs.technicalFile) {
    loadFromHITL(docs, 'technicalFile')
    loadedItems.push('技术需求文档')
  } else if (docs.tenderFile) {
    // 2. 备选：如果没有技术需求文档，使用招标文档
    form.value.tenderFiles = [docs.tenderFile]
    loadedItems.push('招标文档')
  }

  // 3. 自动显示当前项目的历史点对点应答文件
  if (docs.p2pResponseFile) {
    currentP2pFile.value = docs.p2pResponseFile
    loadedItems.push('历史应答文件')
  }

  // 合并显示一条消息（避免多条重复消息）
  if (loadedItems.length > 0 && !docs.technicalFile) {
    // 如果使用了technicalFile，loadFromHITL已经显示了消息
    ElMessage.success(`已加载：${loadedItems.join('、')}`)
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
    ElMessage.error('请先上传招标文档或选择使用HITL技术文件')
    return
  }

  generating.value = true
  generationProgress.value = 0

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

      ElMessage.success({
        message: '点对点应答Word文档生成完成！',
        duration: 3000
      })

      // 自动下载（使用公用函数）
      const filename = result.filename || 'point-to-point-response.docx'
      downloadFile(result.download_url, filename)

      // 自动同步到项目（如果有输出文件）
      if (result.output_file) {
        await syncToHitl(
          form.value.projectId!,
          result.output_file,
          'point_to_point'
        )
      }

      // 刷新历史文件列表
      await loadFilesList()
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

// 查看应答
const viewResponse = (req: Requirement) => {
  currentRequirement.value = req
  responseDialogVisible.value = true
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

// ============================================
// P1功能：历史文件列表
// ============================================

// 加载历史文件列表
const loadFilesList = async () => {
  loadingHistory.value = true
  try {
    const response = await fetch('/api/point-to-point/files')
    const result = await response.json()

    if (result.success) {
      historyFiles.value = result.data || []
      ElMessage.success(`加载了 ${historyFiles.value.length} 个历史文件`)
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


// ============================================
// 监听折叠面板展开，自动加载历史文件
// ============================================
watch(showAllHistory, (newVal) => {
  // 当用户展开折叠面板且历史文件列表为空时，自动加载
  if (newVal.includes('history') && historyFiles.value.length === 0 && !loadingHistory.value) {
    loadFilesList()
  }
})

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
@import "@/assets/styles/variables.scss";

.point-to-point {
  padding: 20px;
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
  .current-file-section {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
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

  .config-form {
    margin-top: 20px;
    padding: 20px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
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
    margin-top: 30px;
    padding-top: 30px;
    border-top: 1px solid var(--el-border-color-lighter);
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
