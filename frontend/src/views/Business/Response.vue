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
              label="使用HITL商务应答模板:"
              @cancel="cancelHitlTemplate"
            />

            <!-- 文件上传器（不使用HITL模板时显示） -->
            <DocumentUploader
              v-if="!useHitlTemplate"
              v-model="form.templateFiles"
              :http-request="handleTemplateUpload"
              accept=".doc,.docx"
              :limit="1"
              :max-size="20"
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
              label="使用HITL招标文档:"
              type="info"
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

    <!-- AI生成流式输出 -->
    <el-card v-if="generating" class="generation-output" shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI正在生成商务应答...</span>
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
        @regenerate="startGeneration"
      />
    </el-card>

    <!-- 生成结果 -->
    <el-card v-if="generationResult" class="result-section" shadow="never">
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
            <el-descriptions-item label="文件路径">
              {{ generationResult.outputFile }}
            </el-descriptions-item>
            <el-descriptions-item label="下载地址">
              <el-link :href="generationResult.downloadUrl" type="primary">
                点击下载
              </el-link>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>

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
import { Download, RefreshRight, Document, View, Upload } from '@element-plus/icons-vue'
import { DocumentUploader, SSEStreamViewer, DocumentPreview, StatsCard, HitlFileAlert } from '@/components'
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

// 预览状态
const previewVisible = ref(false)

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

      // 同步历史商务应答文件
      if (docs.businessResponseFile) {
        generationResult.value = docs.businessResponseFile
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

      ElMessage.success('商务应答生成完成！')

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
const downloadDocument = () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可下载')
    return
  }

  try {
    const url = generationResult.value.downloadUrl
    const filename = `商务应答-${selectedProject.value?.project_name || '文档'}-${Date.now()}.docx`

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
    'business_response'
  )
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

      // 同步历史商务应答文件
      if (docs.businessResponseFile) {
        generationResult.value = docs.businessResponseFile
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
@import "@/assets/styles/variables.scss";

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
  .result-section {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
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
