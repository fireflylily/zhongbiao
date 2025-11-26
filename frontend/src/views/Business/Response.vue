<template>
  <div class="business-response">
    <!-- 项目选择 -->
    <el-card class="project-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Step 1: 选择项目</span>
        </div>
      </template>

      <!-- 提示信息 -->
      <el-alert type="info" :closable="false" style="margin-bottom: 16px">
        <template #default>
          💡 提示：可选择现有项目，或选择公司后新建项目并上传文档
        </template>
      </el-alert>

      <el-form :model="form" label-width="100px">
        <!-- 项目选择 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目">
              <el-select
                v-model="form.projectId"
                placeholder="请选择项目或直接新建"
                filterable
                clearable
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

          <!-- 公司：根据是否选择项目显示不同内容 -->
          <el-col :span="12">
            <el-form-item label="公司">
              <!-- 现有项目模式：只读显示 -->
              <el-input
                v-if="form.projectId"
                :value="selectedProject?.company_name || '-'"
                disabled
              />
              <!-- 新建项目模式：可选择 -->
              <el-select
                v-else
                v-model="form.companyId"
                placeholder="请选择公司（必填）"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="company in companies"
                  :key="company.company_id"
                  :label="company.company_name"
                  :value="company.company_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 新建项目信息：仅当未选择项目时显示 -->
        <el-row v-if="!form.projectId" :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目名称">
              <el-input
                v-model="form.projectName"
                placeholder="新项目"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="项目编号">
              <el-input
                v-model="form.projectNumber"
                placeholder="PRJ-..."
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 文档上传 -->
    <el-card class="upload-section" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Step 2: 上传相关文档</span>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 商务应答模板 -->
        <el-col :span="12">
          <div class="upload-item">
            <h4>商务应答模板 <span class="required">*</span></h4>

            <!-- HITL模板文件Alert -->
            <HitlFileAlert
              v-if="useHitlTemplate"
              :file-info="hitlTemplateInfo"
              label="商务应答模板:"
              @cancel="cancelHitlTemplate"
            />

            <!-- 文件上传器（不使用HITL模板时显示） -->
            <DocumentUploader
              v-if="!useHitlTemplate"
              v-model="form.templateFiles"
              :http-request="handleTemplateUpload"
              accept=".doc,.docx"
              :limit="1"
              :max-size="100"
              drag
              tip-text="必须上传商务应答模板，用于生成应答文档"
              @success="handleTemplateUploadSuccess"
            />
          </div>
        </el-col>

        <!-- 招标文档 -->
        <el-col :span="12">
          <div class="upload-item">
            <h4>招标文档（可选）</h4>

            <!-- HITL招标文档Alert -->
            <HitlFileAlert
              v-if="useHitlTender"
              :file-info="hitlTenderInfo"
              label="招标文档:"
              @cancel="cancelHitlTender"
            />

            <!-- 文件上传器（不使用HITL时显示） -->
            <DocumentUploader
              v-if="!useHitlTender"
              v-model="form.tenderFiles"
              :http-request="handleTenderUpload"
              accept=".pdf,.doc,.docx"
              :limit="5"
              :max-size="50"
              drag
              tip-text="可选上传招标文档作为参考，支持PDF、Word格式，最大50MB"
              @success="handleTenderUploadSuccess"
            />
          </div>
        </el-col>
      </el-row>

      <div class="generation-controls">
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

    <!-- 历史商务应答文件卡片（使用统一组件） -->
    <HistoryFilesPanel
      v-if="generationResult && !showEditor"
      title="📄 该项目已有商务应答文件"
      :current-file="generationResult"
      :history-files="[]"
      :show-editor-open="true"
      :show-stats="true"
      current-file-message="检测到该项目的历史商务应答文件"
      @open-in-editor="openHistoryInEditor"
      @preview="previewDocument"
      @download="downloadDocument"
      @regenerate="startGeneration"
    />

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

    <!-- 文档预览对话框 -->
    <DocumentPreview
      v-model="previewVisible"
      :file-url="generationResult?.downloadUrl"
      :file-name="`商务应答-${selectedProject?.project_name || '文档'}.docx`"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { Download, RefreshRight, Document, View, Upload, Edit } from '@element-plus/icons-vue'
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
  templateFiles: [] as UploadUserFile[]
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

// 折叠面板状态
const activeCollapse = ref<string[]>([])

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
      // 清空编辑器
      showEditor.value = false
      editorContent.value = ''
      activeCollapse.value = []
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
        ElMessage.info('检测到历史商务应答文件，点击"在编辑器中打开"可编辑')
      }
    }
  })

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
        ElMessage.info('检测到历史商务应答文件，点击"在编辑器中打开"可编辑')
      }
    }
  })

  // 如果成功恢复项目，同步到表单
  if (restoredProjectId) {
    form.value.projectId = restoredProjectId
    console.log('✅ 已从Store恢复项目:', restoredProjectId)
  }
})
</script>

<style scoped lang="scss">

.business-response {
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
    }
  }

  .project-section,
  .upload-section,
  .generation-output,
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

  .upload-item {
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);

      .required {
        color: var(--el-color-danger);
        margin-left: 4px;
      }
    }
  }

  .generation-controls {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    padding-top: 30px;
    border-top: 1px solid var(--el-border-color-lighter);
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
}
</style>
