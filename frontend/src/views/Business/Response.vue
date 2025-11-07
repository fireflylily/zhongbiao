<template>
  <div class="business-response">
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
          <span>Step 2: 上传相关文档</span>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 商务应答模板 -->
        <el-col :span="12">
          <div class="upload-item">
            <h4>商务应答模板 <span class="required">*</span></h4>
            <DocumentUploader
              v-model="form.templateFiles"
              :upload-url="`/api/tender-projects/${form.projectId}/upload-template`"
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
            <DocumentUploader
              v-model="form.tenderFiles"
              :upload-url="`/api/tender-projects/${form.projectId}/upload-tender`"
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
          <span>生成结果</span>
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
          type="success"
          :title="generationResult.message"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <!-- 处理统计 -->
        <div class="stats-section">
          <h4>处理统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="文本替换" :value="generationResult.stats.total_replacements || 0">
                <template #suffix>处</template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="表格处理" :value="generationResult.stats.tables_processed || 0">
                <template #suffix>个</template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="单元格填充" :value="generationResult.stats.cells_filled || 0">
                <template #suffix>个</template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="图片插入" :value="generationResult.stats.images_inserted || 0">
                <template #suffix>张</template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

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
import { Download, RefreshRight, Document, View } from '@element-plus/icons-vue'
import { DocumentUploader, SSEStreamViewer, DocumentPreview } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import { businessLegacyApi } from '@/api/endpoints/business'
import { useProjectStore } from '@/stores/project'
import type { Project, UploadUserFile } from '@/types'

const projectStore = useProjectStore()

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
}

// 表单数据
const form = ref({
  projectId: null as number | null,
  tenderFiles: [] as UploadUserFile[],
  templateFiles: [] as UploadUserFile[]
})

// 项目列表
const projects = ref<Project[]>([])
const selectedProject = computed(() =>
  projects.value.find(p => p.id === form.value.projectId)
)

// 能否开始生成
const canGenerate = computed(() =>
  form.value.projectId && form.value.templateFiles.length > 0
)

// 生成状态
const generating = ref(false)
const generationProgress = ref(0)
const streamContent = ref('')
const generationResult = ref<GenerationResult | null>(null)

// 预览状态
const previewVisible = ref(false)

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await tenderApi.getProjects({ page: 1, page_size: 100 })
    projects.value = response.data?.items || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

// 项目切换
const handleProjectChange = async () => {
  // 清空结果但保留文件列表，准备加载已上传的文件
  generationResult.value = null
  streamContent.value = ''

  // 获取选中的项目并保存到 Pinia Store
  if (form.value.projectId) {
    const project = projects.value.find(p => p.id === form.value.projectId)
    if (project) {
      // 将选中的项目保存到 Store，实现跨页面状态共享
      projectStore.setCurrentProject(project as any)
    }

    // 加载项目已上传的文档
    await loadProjectDocuments(form.value.projectId)
  }
}

// 加载项目文档（从项目详情的 step1_data 中提取）
const loadProjectDocuments = async (projectId: number) => {
  try {
    // 获取项目详情，其中包含 step1_data
    const response = await tenderApi.getProject(projectId)
    const projectData = response.data

    // 清空文件列表
    form.value.tenderFiles = []
    form.value.templateFiles = []

    if (!projectData) {
      return
    }

    let loadedCount = 0

    // 提取招标文档：优先从 step1_data.file_path 读取（HITL任务中的标书）
    let tenderFileLoaded = false
    if (projectData.step1_data && projectData.step1_data.file_path) {
      const step1Data = projectData.step1_data
      form.value.tenderFiles.push({
        name: step1Data.file_name || step1Data.original_filename || '招标文档',
        url: step1Data.file_path,
        status: 'success',
        uid: Date.now() + Math.random(),
        size: step1Data.file_size
      })
      loadedCount++
      tenderFileLoaded = true
    }

    // 如果 step1_data 中没有，再从 tender_document_path 读取（项目级别的标书）
    if (!tenderFileLoaded && projectData.tender_document_path) {
      form.value.tenderFiles.push({
        name: projectData.original_filename || '招标文档',
        url: projectData.tender_document_path,
        status: 'success',
        uid: Date.now() + Math.random()
      })
      loadedCount++
    }

    // 从 step1_data 提取应答模板
    if (projectData.step1_data) {
      const step1Data = projectData.step1_data

      // 应答文件模板（商务应答模板）
      if (step1Data.response_file_path) {
        form.value.templateFiles.push({
          name: step1Data.response_filename || '商务应答模板',
          url: step1Data.response_file_path,
          status: 'success',
          uid: Date.now() + Math.random(),
          size: step1Data.response_file_size
        })
        loadedCount++
      }
    }

    if (loadedCount > 0) {
      ElMessage.success(`已加载 ${loadedCount} 个文件`)
    }
  } catch (error) {
    console.error('加载项目文档失败:', error)
    // 加载失败时清空文件列表
    form.value.tenderFiles = []
    form.value.templateFiles = []
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

  if (form.value.templateFiles.length === 0) {
    ElMessage.warning('请先上传商务应答模板')
    return
  }

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

    // 处理成功
    if (response.data.success) {
      generationProgress.value = 100
      streamContent.value += response.data.message + '\n'

      generationResult.value = {
        success: true,
        outputFile: response.data.output_file,
        downloadUrl: response.data.download_url,
        stats: response.data.stats || {},
        message: response.data.message
      }

      ElMessage.success('商务应答生成完成！')
    } else {
      throw new Error(response.data.message || '处理失败')
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

// 下载文档（下载后端生成的真实Word文档）
const downloadDocument = () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可下载')
    return
  }

  try {
    // 使用后端返回的下载地址
    const downloadUrl = generationResult.value.downloadUrl

    // 生成文件名
    const fileName = `商务应答-${selectedProject.value?.project_name || '文档'}-${Date.now()}.docx`

    // 创建下载链接
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = fileName
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('Word文档下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('文档下载失败，请重试')
  }
}

onMounted(async () => {
  // 加载项目列表
  await loadProjects()

  // 检查 Pinia Store 中是否有当前项目
  if (projectStore.currentProject && projectStore.currentProject.id) {
    // 自动选中从其他页面跳转过来时设置的项目
    form.value.projectId = projectStore.currentProject.id

    // 触发项目切换逻辑，加载项目文档
    await handleProjectChange()

    console.log('已自动选中项目:', projectStore.currentProject.name)
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
    .stats-section,
    .file-info-section {
      margin-bottom: 24px;

      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }
    }

    .stats-section {
      padding: 20px;
      background: var(--el-fill-color-light);
      border-radius: 4px;
    }

    .file-info-section {
      :deep(.el-descriptions__label) {
        font-weight: 600;
      }
    }
  }
}
</style>
