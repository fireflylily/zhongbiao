<template>
  <div class="business-response">
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
            clearable
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
          <!-- 现有项目模式：只读显示 -->
          <el-input
            v-if="form.projectId"
            :value="selectedProject?.company_name || '-'"
            disabled
            class="row-input"
          />
          <!-- 新建项目模式：可选择 -->
          <el-select
            v-else
            v-model="form.companyId"
            placeholder="请选择公司"
            filterable
            class="row-select"
          >
            <el-option
              v-for="company in companies"
              :key="company.company_id"
              :label="company.company_name"
              :value="company.company_id"
            />
          </el-select>
        </div>
      </div>

      <!-- 被授权人行 -->
      <div class="panel-row project-row">
        <div class="row-item">
          <label class="row-label">被授权人</label>
          <el-input
            v-model="form.authorizedPersonName"
            placeholder="请输入被授权人"
            class="row-input"
          />
        </div>
      </div>

      <!-- 新建项目信息：仅当未选择项目时显示 -->
      <div v-if="!form.projectId" class="panel-row project-row">
        <div class="row-item">
          <label class="row-label">项目名称</label>
          <el-input v-model="form.projectName" placeholder="新项目" class="row-input" />
        </div>
        <div class="row-item">
          <label class="row-label">项目编号</label>
          <el-input v-model="form.projectNumber" placeholder="PRJ-..." class="row-input" />
        </div>
      </div>

      <!-- 第二行：文档区域（商务应答模板 + 招标文档 并排） -->
      <div class="panel-row project-row document-row">
        <!-- 左侧：商务应答模板 -->
        <div class="row-item">
          <label class="row-label">应答模板</label>
          <!-- 已加载文件 -->
          <div v-if="useHitlTemplate" class="file-chip file-chip--success">
            <el-icon class="file-chip-icon"><Document /></el-icon>
            <span class="file-chip-name" :title="hitlTemplateInfo?.filename">
              {{ hitlTemplateInfo?.filename || '未知文件' }}
            </span>
            <span class="file-chip-tag">已加载</span>
            <el-button class="file-chip-close" type="danger" text size="small" @click="cancelHitlTemplate">×</el-button>
          </div>
          <!-- 手动上传的文件 -->
          <div v-else-if="form.templateFiles.length > 0" class="file-chip file-chip--info">
            <el-icon class="file-chip-icon"><Document /></el-icon>
            <span class="file-chip-name" :title="form.templateFiles[0].name">
              {{ form.templateFiles[0].name }}
            </span>
            <span class="file-chip-tag">已上传</span>
            <el-button class="file-chip-close" type="danger" text size="small" @click="form.templateFiles = []">×</el-button>
          </div>
          <!-- 未上传：显示为类似输入框的占位区域 -->
          <div v-else class="file-placeholder">
            <span class="placeholder-text">请上传应答模板</span>
            <DocumentUploader
              v-model="form.templateFiles"
              :http-request="handleTemplateUpload"
              accept=".doc,.docx"
              :limit="1"
              :max-size="100"
              :show-file-list="false"
              trigger-text="选择文件"
              @success="handleTemplateUploadSuccess"
            />
          </div>
        </div>

        <!-- 右侧：招标文档 -->
        <div class="row-item">
          <label class="row-label">招标文档</label>
          <!-- 已加载文件 -->
          <div v-if="useHitlTender" class="file-chip file-chip--success">
            <el-icon class="file-chip-icon"><Document /></el-icon>
            <span class="file-chip-name" :title="hitlTenderInfo?.filename">
              {{ hitlTenderInfo?.filename || '未知文件' }}
            </span>
            <span class="file-chip-tag">已加载</span>
            <el-button class="file-chip-close" type="danger" text size="small" @click="cancelHitlTender">×</el-button>
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
            <span class="placeholder-text">上传招标文档（可选）</span>
            <DocumentUploader
              v-model="form.tenderFiles"
              :http-request="handleTenderUpload"
              accept=".pdf,.doc,.docx"
              :limit="5"
              :max-size="50"
              :show-file-list="false"
              trigger-text="选择文件"
              @success="handleTenderUploadSuccess"
            />
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
          @click="startGeneration"
        >
          开始生成商务应答
        </el-button>
      </div>
    </el-card>

    <!-- 富文本编辑器（生成时立即显示） -->
    <el-card v-if="showEditor" class="editor-section" shadow="never">
      <RichTextEditor
        ref="editorRef"
        v-model="editorContent"
        title="商务应答文档"
        :streaming="generating"
        :height="1000"
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
          <span>{{ generationResult.isHistory ? '📄 历史应答文件' : '✅ 生成结果' }}</span>
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
              @click="downloadDocument"
            >
              下载Word文档
            </el-button>

            <!-- 同步状态显示 -->
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
              @click="startGeneration"
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
          :type="generationResult.isHistory ? 'info' : 'success'"
          :title="generationResult.message"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <!-- 处理统计 -->
        <StatsCard
          title="处理统计"
          :stats="generationResult.stats"
        />

        <!-- 资质处理详情 -->
        <div v-if="generationResult.stats?.qualifications_details?.length > 0" class="qualifications-details-section">
          <h4>📋 资质处理详情</h4>
          <el-table :data="generationResult.stats.qualifications_details" border stripe style="margin-top: 16px">
            <el-table-column type="index" label="#" width="60" align="center" />
            <el-table-column prop="display_title" label="资质名称" min-width="200">
              <template #default="{ row }">
                <div>
                  <strong>{{ row.display_title }}</strong>
                  <el-tag v-if="row.resource_type === 'id_card'" type="info" size="small" style="margin-left: 8px">
                    身份证
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="qual_name" label="类别" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="getQualCategoryType(row.qual_name)" size="small">
                  {{ row.qual_name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_pages" label="图片数" width="100" align="center">
              <template #default="{ row }">
                <el-text type="primary" size="large">
                  <strong>{{ row.total_pages }}</strong> {{ row.resource_type === 'id_card' ? '面' : '页' }}
                </el-text>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80" align="center">
              <template #default>
                <el-icon color="#67c23a" :size="20"><SuccessFilled /></el-icon>
              </template>
            </el-table-column>
          </el-table>

          <!-- 缺失资质提示 -->
          <el-alert
            v-if="generationResult.stats?.missing_qualifications?.length > 0"
            type="warning"
            :closable="false"
            style="margin-top: 16px"
          >
            <template #title>
              以下资质模板有占位符但未上传文件
            </template>
            <ul style="margin: 8px 0 0 20px; padding: 0;">
              <li v-for="(missing, idx) in generationResult.stats.missing_qualifications" :key="idx">
                {{ missing.qual_name || missing.qual_key }}
              </li>
            </ul>
          </el-alert>
        </div>

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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { Download, RefreshRight, Document, View, Upload, Edit, SuccessFilled, Close } from '@element-plus/icons-vue'
import { DocumentUploader, SSEStreamViewer, DocumentPreview, StatsCard, HitlFileAlert, RichTextEditor, HistoryFilesPanel } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import { businessLegacyApi } from '@/api/endpoints/business'
import { companyApi } from '@/api/endpoints/company'
import { useProjectStore } from '@/stores/project'
import { useProjectDocuments, useHitlIntegration } from '@/composables'
import { downloadFile } from '@/utils/helpers'
import type { Project, UploadUserFile, Company } from '@/types'

const projectStore = useProjectStore()

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

// HITL集成 - 商务应答模板
const {
  useHitlFile: useHitlTemplate,
  hitlFileInfo: hitlTemplateInfo,
  syncing,
  synced,
  loadFromHITL: loadTemplateFromHITL,
  cancelHitlFile: cancelHitlTemplate,
  syncToHitl
} = useHitlIntegration({
  onFileLoaded: () => {
    // 清空上传的文件
    form.value.templateFiles = []
  }
})

// HITL集成 - 招标文档（第二个实例）
const {
  useHitlFile: useHitlTender,
  hitlFileInfo: hitlTenderInfo,
  loadFromHITL: loadTenderFromHITL,
  cancelHitlFile: cancelHitlTender
} = useHitlIntegration({
  onFileLoaded: () => {
    // 清空上传的文件
    form.value.tenderFiles = []
  }
})

interface GenerationResult {
  success: boolean
  outputFile: string
  downloadUrl: string
  stats: {
    total_replacements?: number
    tables_processed?: number
    cells_filled?: number
    images_inserted?: number
  }
  message: string
  isHistory?: boolean  // 标识是否为历史记录
}

// 表单数据
const form = ref({
  projectId: null as number | null,
  companyId: null as number | null,  // 新建项目：公司ID
  projectName: '新项目',                // 新建项目：项目名称
  projectNumber: `PRJ-${Date.now()}`,  // 新建项目：项目编号
  tenderFiles: [] as UploadUserFile[],
  templateFiles: [] as UploadUserFile[],
  authorizedPersonName: ''  // 被授权人姓名
})

// 公司列表（项目列表由 Composable 提供）
const companies = ref<Company[]>([])
const selectedCompany = computed(() =>
  companies.value.find(c => c.company_id === form.value.companyId)
)

// 能否开始生成
const canGenerate = computed(() =>
  form.value.projectId && (form.value.templateFiles.length > 0 || useHitlTemplate.value)
)

// 生成状态
const generating = ref(false)
const generationProgress = ref(0)
const streamContent = ref('')
const generationResult = ref<GenerationResult | null>(null)

// 编辑器状态
const showEditor = ref(false)
const editorRef = ref<any>(null)
const editorContent = ref('')
const editorSaving = ref(false)

// 预览状态
const previewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

// 折叠面板状态
const activeCollapse = ref<string[]>([])

// 历史文件列表
const historyFiles = ref<any[]>([])
const loadingHistory = ref(false)
const showAllHistory = ref<string[]>([])

// 自定义上传函数：商务应答模板
const handleTemplateUpload = async (options: UploadRequestOptions) => {
  const { file, onSuccess, onError } = options

  try {
    // 【关键】如果未选择项目，先创建项目
    if (!form.value.projectId) {
      if (!form.value.companyId) {
        throw new Error('请先选择公司')
      }

      ElMessage.info('正在创建新项目...')

      // 创建新项目
      const createResponse = await tenderApi.createProject({
        company_id: form.value.companyId,
        project_name: form.value.projectName || '新项目',
        project_number: form.value.projectNumber || `PRJ-${Date.now()}`
      })

      // 获取新项目ID
      form.value.projectId = createResponse.project_id

      // 刷新项目列表
      await loadProjects()

      ElMessage.success('新项目已创建')

      // 触发项目切换逻辑（更新UI）
      await handleProjectChange()
    }

    // 使用正确的商务应答模板上传API
    const response = await tenderApi.uploadBusinessTemplate(
      form.value.projectId,
      file as File
    )

    if (response.success) {
      onSuccess(response.data)
      ElMessage.success('商务应答模板上传成功')
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (error: any) {
    onError(error)
    ElMessage.error(error.message || '模板上传失败')
  }
}

// 自定义上传函数：招标文档
const handleTenderUpload = async (options: UploadRequestOptions) => {
  const { file, onSuccess, onError } = options

  try {
    // 【关键】如果未选择项目，先创建项目
    if (!form.value.projectId) {
      if (!form.value.companyId) {
        throw new Error('请先选择公司')
      }

      ElMessage.info('正在创建新项目...')

      // 创建新项目
      const createResponse = await tenderApi.createProject({
        company_id: form.value.companyId,
        project_name: form.value.projectName || '新项目',
        project_number: form.value.projectNumber || `PRJ-${Date.now()}`
      })

      // 获取新项目ID
      form.value.projectId = createResponse.project_id

      // 刷新项目列表
      await loadProjects()

      ElMessage.success('新项目已创建')

      // 触发项目切换逻辑（更新UI）
      await handleProjectChange()
    }

    // 获取公司ID（现在一定有项目了）
    const companyId = selectedProject.value?.company_id
    if (!companyId) {
      throw new Error('项目没有关联公司')
    }

    // 上传文件
    const formData = new FormData()
    formData.append('file', file)
    formData.append('company_id', companyId.toString())
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

// 加载公司列表
const loadCompanies = async () => {
  try {
    const response = await companyApi.getCompanies()
    companies.value = response.data || []
  } catch (error) {
    console.error('加载公司列表失败:', error)
    ElMessage.error('加载公司列表失败')
  }
}

// 项目切换（使用 Composable + 页面特定逻辑）
const handleProjectChange = async () => {
  await handleProjectChangeComposable(form.value.projectId, {
    // 清空回调：清空页面特定状态
    onClear: () => {
      generationResult.value = null
      streamContent.value = ''
      form.value.tenderFiles = []
      form.value.templateFiles = []
      form.value.authorizedPersonName = ''  // 清空被授权人
      // 清空编辑器
      showEditor.value = false
      editorContent.value = ''
      activeCollapse.value = []
      // 清空历史文件列表
      historyFiles.value = []
      // 取消使用HITL文件
      if (useHitlTemplate.value) {
        cancelHitlTemplate()
      }
      if (useHitlTender.value) {
        cancelHitlTender()
      }
    },
    // 文档加载完成回调：同步到页面状态
    onDocumentsLoaded: (docs) => {
      // 从HITL加载招标文档
      if (docs.tenderFile) {
        loadTenderFromHITL(docs, 'tenderFile')
      }

      // 从HITL加载应答模板
      if (docs.templateFile) {
        loadTemplateFromHITL(docs, 'templateFile')
      }

      // 同步历史商务应答文件（不自动打开编辑器）
      if (docs.businessResponseFile) {
        generationResult.value = docs.businessResponseFile
        showEditor.value = false  // 明确不自动打开编辑器

        console.log('[Response] 检测到历史商务应答文件:', docs.businessResponseFile.outputFile)
      }
    }
  })

  // 项目选择后，自动加载历史文件列表和被授权人信息
  if (form.value.projectId) {
    await loadFilesList()
    // 从项目数据中加载被授权人信息
    if (selectedProject.value?.authorized_person_name) {
      form.value.authorizedPersonName = selectedProject.value.authorized_person_name
    }
  }

  // 【新建项目模式】重置项目编号
  if (!form.value.projectId) {
    form.value.projectNumber = `PRJ-${Date.now()}`
  }
}

// 招标文档上传成功
const handleTenderUploadSuccess = () => {
  ElMessage.success('招标文档上传成功')
}

// 模板上传成功
const handleTemplateUploadSuccess = () => {
  ElMessage.success('商务应答模板上传成功')
}

// 开始生成
const startGeneration = async () => {
  if (!form.value.projectId) {
    ElMessage.warning('请先选择项目')
    return
  }

  // 模板检查已通过canGenerate控制，此处不重复检查

  generating.value = true
  generationProgress.value = 0
  streamContent.value = ''
  generationResult.value = null

  // 立即显示编辑器
  showEditor.value = true
  editorContent.value = '<h1>📄 商务应答文档</h1><p style="color: #909399;">AI正在生成内容，请稍候...</p>'

  // 滚动到编辑器
  setTimeout(() => {
    document.querySelector('.editor-section')?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }, 100)

  try {
    // 获取项目详情
    streamContent.value = '正在加载项目信息...\n'
    const projectResponse = await tenderApi.getProject(form.value.projectId)
    const projectData = projectResponse.data

    // 提取商务应答模板路径
    const templateFilePath = projectData.step1_data?.response_file_path
    if (!templateFilePath) {
      throw new Error('未找到商务应答模板文件路径，请先在标书管理中上传模板')
    }

    streamContent.value += '正在处理商务应答文档...\n'
    generationProgress.value = 30

    // 调用后端API处理商务应答
    const response = await businessLegacyApi.processBusinessResponse({
      company_id: projectData.company_id,
      project_name: projectData.project_name,
      tender_no: projectData.project_number || '',
      date_text: projectData.bidding_time || '',
      hitl_file_path: templateFilePath,
      use_mcp: true
    })

    generationProgress.value = 80
    streamContent.value += '处理完成，正在生成结果...\n'

    // 调试：打印完整响应结构
    console.log('完整响应:', response)
    console.log('response.data:', response.data)
    console.log('response.success:', response.success)

    // 适配不同的响应格式
    // 格式1: { success: true, data: { ... } }
    // 格式2: { success: true, output_file: "...", ... }
    const result = response.data ? response.data : response

    console.log('处理后的result:', result)

    // 处理成功
    if (result.success) {
      generationProgress.value = 100
      streamContent.value += result.message + '\n'

      generationResult.value = {
        success: true,
        outputFile: result.output_file,
        downloadUrl: result.download_url,
        stats: result.stats || {},
        message: result.message
      }

      // 加载Word文档到编辑器
      await loadWordToEditor(result.output_file)

      ElMessage.success('商务应答生成完成！可以编辑了')

      // 自动同步到HITL项目
      if (result.output_file && form.value.projectId) {
        await syncToHitl(
          form.value.projectId,
          result.output_file,
          'business_response'
        )
      }
    } else {
      throw new Error(result.message || result.error || '处理失败')
    }
  } catch (error: any) {
    console.error('生成失败:', error)
    streamContent.value += `\n❌ 错误: ${error.message}\n`

    // 在编辑器中也显示错误
    if (editorRef.value) {
      editorRef.value.appendContent(`<p style="color: red;">❌ 错误: ${error.message}</p>`)
    }

    ElMessage.error(error.message || '生成失败，请重试')
  } finally {
    generating.value = false
    if (generationProgress.value < 100) {
      generationProgress.value = 0
    }
  }
}

// 停止生成
const stopGeneration = () => {
  generating.value = false
  ElMessage.info('已停止生成')
}

// 加载Word文档到编辑器
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

      console.log('[Response] Word文档已加载到编辑器')
    } else {
      throw new Error(result.error || '转换失败')
    }
  } catch (error: any) {
    console.error('[Response] 加载文档到编辑器失败:', error)

    // 如果转换失败，显示基础提示
    editorContent.value = `
      <h1>📄 商务应答文档</h1>
      <div style="padding: 20px; background: #FFF3E0; border-left: 4px solid #FF9800; margin: 16px 0;">
        <p><strong>⚠️ 提示：</strong>Word文档转换失败</p>
        <p>原因：${error.message}</p>
        <p>您可以：</p>
        <ul>
          <li>直接在此编辑器中输入内容</li>
          <li>或点击下方"查看原始生成结果"下载Word文档查看</li>
        </ul>
      </div>
      <p>开始编辑您的内容...</p>
    `

    ElMessage.warning('Word转换HTML失败，请使用下载功能或手动输入')
  }
}

// 保存编辑器内容
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
        document_type: 'business_response',
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

      console.log('[Response] 编辑内容已保存:', result.output_file)

      // 同步到HITL
      if (result.output_file) {
        await syncToHitl(
          form.value.projectId,
          result.output_file,
          'business_response'
        )
      }
    } else {
      throw new Error(result.error || '保存失败')
    }
  } catch (error: any) {
    console.error('[Response] 保存编辑内容失败:', error)
    throw error // 让RichTextEditor显示错误
  } finally {
    editorSaving.value = false
  }
}

// 预览文档
const previewDocument = () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可预览')
    return
  }

  if (!generationResult.value.downloadUrl) {
    ElMessage.warning('文档地址无效')
    return
  }

  previewVisible.value = true
}

// 下载文档（使用公用函数）
const downloadDocument = async () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可下载')
    return
  }

  try {
    const url = generationResult.value.downloadUrl
    const filename = `商务应答-${selectedProject.value?.project_name || '文档'}-${Date.now()}.docx`

    // 使用公用下载函数
    await downloadFile(url, filename)

    ElMessage.success('Word文档下载成功')
  } catch (error: any) {
    console.error('下载失败:', error)
    ElMessage.error(error.message || '文档下载失败，请重试')
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
    'business_response'
  )
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

/**
 * 根据资质类别返回标签颜色类型
 * @param category 资质类别名称
 * @returns Element Plus标签类型
 */
const getQualCategoryType = (category: string): string => {
  const typeMap: Record<string, string> = {
    '基本资质': 'danger',
    '信用证明': 'success',
    '身份证明': 'primary',
    '财务文件': 'warning',
    '信息安全': 'info',
    '电信资质': 'warning',
    'IT服务': 'info',
    '质量管理': 'success',
    '软件能力': 'info',
    '行业资质': 'warning',
    '知识产权': ''
  }

  return typeMap[category] || ''
}

// 加载历史文件列表（仅当前项目）
const loadFilesList = async () => {
  if (!form.value.projectId) {
    historyFiles.value = []
    return
  }

  loadingHistory.value = true
  try {
    const response = await fetch(`/api/business-files?project_id=${form.value.projectId}`)
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

// 预览历史文件
const previewFile = (file: any) => {
  if (!file.file_path) {
    ElMessage.warning('无法获取文件信息')
    return
  }

  previewFileUrl.value = file.file_path
  previewFileName.value = file.filename
  previewVisible.value = true
}

// 下载历史文件
const downloadHistoryFile = async (file: any) => {
  try {
    if (!file.download_url) {
      ElMessage.error('下载地址无效')
      return
    }

    const filename = file.filename || '商务应答.docx'
    downloadFile(file.download_url, filename)
    ElMessage.success('文件下载中...')
  } catch (error: any) {
    console.error('下载文件失败:', error)
    ElMessage.error(error.message || '下载文件失败')
  }
}

// 在编辑器中打开历史文件
const openHistoryInEditor = async () => {
  if (!generationResult.value?.outputFile) {
    ElMessage.error('历史文件信息无效')
    return
  }

  try {
    // 显示编辑器
    showEditor.value = true

    // 加载Word文档到编辑器
    await loadWordToEditor(generationResult.value.outputFile)

    ElMessage.success('历史文件已加载到编辑器')

    // 滚动到编辑器
    setTimeout(() => {
      document.querySelector('.editor-section')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }, 100)
  } catch (error: any) {
    console.error('[Response] 打开历史文件失败:', error)
    ElMessage.error('打开历史文件失败: ' + error.message)
  }
}

onMounted(async () => {
  // 并行加载项目列表和公司列表
  await Promise.all([
    loadProjects(),
    loadCompanies()
  ])

  // 从Store恢复项目（如果是从HITL页面跳转过来）
  const restoredProjectId = await restoreProjectFromStore({
    onClear: () => {
      generationResult.value = null
      streamContent.value = ''
      form.value.tenderFiles = []
      form.value.templateFiles = []
      form.value.authorizedPersonName = ''  // 清空被授权人
      // 清空编辑器
      showEditor.value = false
      editorContent.value = ''
      // 取消使用HITL文件
      if (useHitlTemplate.value) {
        cancelHitlTemplate()
      }
      if (useHitlTender.value) {
        cancelHitlTender()
      }
    },
    onDocumentsLoaded: (docs) => {
      // 从HITL加载招标文档
      if (docs.tenderFile) {
        loadTenderFromHITL(docs, 'tenderFile')
      }

      // 从HITL加载应答模板
      if (docs.templateFile) {
        loadTemplateFromHITL(docs, 'templateFile')
      }

      // 同步历史商务应答文件（不自动打开编辑器）
      if (docs.businessResponseFile) {
        generationResult.value = docs.businessResponseFile
        showEditor.value = false  // 明确不自动打开编辑器

        console.log('[Response] 从Store恢复历史商务应答文件:', docs.businessResponseFile.outputFile)
      }
    }
  })

  // 如果成功恢复项目，同步到表单
  if (restoredProjectId) {
    form.value.projectId = restoredProjectId
    // 从项目数据中加载被授权人信息
    if (selectedProject.value?.authorized_person_name) {
      form.value.authorizedPersonName = selectedProject.value.authorized_person_name
    }
    console.log('✅ 已从Store恢复项目:', restoredProjectId)
  }
})
</script>

<style scoped lang="scss">

.business-response {
  display: flex;
  flex-direction: column;
  gap: 20px;

  // ============================================
  // 统一操作面板样式
  // ============================================
  .main-panel {
    :deep(.el-card__body) {
      padding: 24px;
    }
  }

  .panel-row {
    display: flex;
    gap: 24px;
  }

  // 项目选择行
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

  // 操作按钮
  .panel-actions {
    display: flex;
    justify-content: center;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  // ============================================
  // 其他区域样式
  // ============================================
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .header-actions {
      display: flex;
      gap: 12px;
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

  .result-content {
    .file-info-section,
    .qualifications-details-section {
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

    .qualifications-details-section {
      :deep(.el-table) {
        th {
          background-color: var(--el-fill-color-light);
          font-weight: 600;
        }
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
