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
              type="success"
              :icon="Download"
              @click="downloadDocument"
            >
              下载文档
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

      <!-- 文档内容预览 -->
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商务应答内容" name="content">
          <SSEStreamViewer
            :content="generationResult.content"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </el-tab-pane>

        <el-tab-pane label="响应度分析" name="analysis">
          <div class="analysis-section">
            <h4>商务条款响应度</h4>
            <el-progress
              :percentage="generationResult.responseRate"
              :color="getProgressColor(generationResult.responseRate)"
              :stroke-width="20"
            >
              <span class="progress-text">{{ generationResult.responseRate }}%</span>
            </el-progress>

            <h4 style="margin-top: 30px">详细分析</h4>
            <SSEStreamViewer
              :content="generationResult.analysis"
              :is-streaming="false"
              :enable-markdown="true"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="风险提示" name="risks">
          <SSEStreamViewer
            :content="generationResult.risks"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </el-tab-pane>

        <el-tab-pane label="改进建议" name="suggestions">
          <SSEStreamViewer
            :content="generationResult.suggestions"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, RefreshRight } from '@element-plus/icons-vue'
import { DocumentUploader, SSEStreamViewer } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import type { Project, UploadUserFile } from '@/types'

interface GenerationResult {
  content: string
  responseRate: number
  analysis: string
  risks: string
  suggestions: string
  documentUrl?: string
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
const activeTab = ref('content')

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

  // 加载项目已上传的文档
  if (form.value.projectId) {
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
    // 模拟AI生成流程（实际应该调用后端SSE接口）
    await simulateGeneration()

    ElMessage.success('商务应答生成完成')
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    generating.value = false
  }
}

// 模拟AI生成（实际应该调用后端SSE接口）
const simulateGeneration = async () => {
  return new Promise<void>((resolve) => {
    const stages = [
      { progress: 20, message: '正在解析招标文档...' },
      { progress: 40, message: '正在提取商务条款要求...' },
      { progress: 60, message: '正在检索公司资质信息...' },
      { progress: 80, message: '正在生成商务应答内容...' },
      { progress: 100, message: '生成完成！' }
    ]

    let currentStage = 0

    const interval = setInterval(() => {
      if (currentStage < stages.length) {
        const stage = stages[currentStage]
        generationProgress.value = stage.progress
        streamContent.value += `\n[${stage.progress}%] ${stage.message}`
        currentStage++
      } else {
        clearInterval(interval)

        // 生成结果
        generationResult.value = {
          content: `# 商务应答文档\n\n## 一、公司资质响应\n\n### 1.1 营业执照\n我公司持有有效的营业执照，注册资本xxxx万元，经营范围涵盖本项目所需的全部业务内容。\n\n### 1.2 相关资质证书\n- ISO 9001质量管理体系认证\n- ISO 27001信息安全管理体系认证\n- CMMI 3级认证\n\n## 二、商务条款响应\n\n### 2.1 付款方式\n我司完全接受贵方提出的付款方式，具体如下：\n- 合同签订后支付30%\n- 项目验收后支付60%\n- 质保期满后支付10%\n\n### 2.2 质保期\n我司承诺提供**2年免费质保期**，质保期内免费提供7x24小时技术支持。\n\n### 2.3 违约责任\n我司完全接受招标文件中关于违约责任的约定，并承诺严格履行合同义务。\n\n## 三、服务承诺\n\n1. **响应时间承诺**\n   - 一般问题：2小时内响应\n   - 紧急问题：30分钟内响应\n\n2. **人员配置承诺**\n   - 配备专职项目经理1名\n   - 技术团队不少于5人\n\n3. **培训承诺**\n   - 提供不少于3次系统培训\n   - 提供完整的操作手册`,
          responseRate: 92,
          analysis: `# 商务条款响应度分析\n\n## 完全响应的条款（85%）\n\n1. **付款方式** ✅\n   - 完全接受甲方提出的三期付款方式\n\n2. **质保期** ✅\n   - 质保期2年，超出招标文件要求的1年\n\n3. **违约责任** ✅\n   - 完全接受违约责任条款\n\n## 部分响应的条款（7%）\n\n1. **人员配置**\n   - 招标文件要求技术人员不少于8人\n   - 我方承诺不少于5人\n   - **建议**: 增加至8人以完全满足要求\n\n## 未响应的条款（8%）\n\n1. **保险要求**\n   - 招标文件要求购买项目保险\n   - 应答文件中未提及\n   - **建议**: 补充保险购买承诺`,
          risks: `# 商务风险提示\n\n## ⚠️ 高风险项\n\n### 1. 人员配置不足\n- **风险**: 技术人员配置低于招标要求\n- **影响**: 可能被认定为非实质性响应\n- **建议**: 立即调整人员配置方案\n\n### 2. 缺少保险承诺\n- **风险**: 未响应保险要求\n- **影响**: 可能被扣分\n- **建议**: 补充项目保险购买计划\n\n## ⚡ 中风险项\n\n### 1. 质保期成本\n- **风险**: 质保期超出招标要求\n- **影响**: 增加成本负担\n- **建议**: 评估质保成本，调整报价\n\n## ✅ 低风险项\n\n1. 付款方式完全符合要求\n2. 违约责任条款明确\n3. 服务响应时间合理`,
          suggestions: `# 改进建议\n\n## 1. 人员配置优化\n\n**当前**: 技术团队不少于5人\n**建议**: 调整为不少于8人\n**原因**: 满足招标文件要求\n\n## 2. 补充保险条款\n\n**建议内容**:\n> 我司承诺为本项目购买项目责任保险，保额不低于xxxx万元，保险期限覆盖整个项目周期。\n\n## 3. 完善服务承诺\n\n**建议增加**:\n- 定期巡检计划（每月1次）\n- 应急预案（含备用方案）\n- 培训计划详细安排\n\n## 4. 优化表述\n\n- 将"完全接受"改为具体承诺\n- 增加量化指标\n- 补充证明材料清单`,
          documentUrl: '/api/documents/download/business-response-123.docx'
        }

        resolve()
      }
    }, 800)
  })
}

// 停止生成
const stopGeneration = () => {
  generating.value = false
  ElMessage.info('已停止生成')
}

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

// 下载文档
const downloadDocument = () => {
  if (!generationResult.value) {
    ElMessage.warning('暂无文档可下载')
    return
  }

  try {
    // 生成文档内容
    const content = generateDocumentContent()

    // 创建Blob对象
    const blob = new Blob([content], {
      type: 'text/plain;charset=utf-8'
    })

    // 生成文件名
    const fileName = `商务应答-${selectedProject.value?.project_name || '文档'}-${Date.now()}.txt`

    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('文档下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('文档下载失败，请重试')
  }
}

// 生成文档内容
const generateDocumentContent = (): string => {
  if (!generationResult.value) return ''

  let content = `# 商务应答文档\n\n`
  content += `## 项目信息\n`
  content += `- 项目名称: ${selectedProject.value?.project_name || '-'}\n`
  content += `- 项目编号: ${selectedProject.value?.project_number || '-'}\n`
  content += `- 公司名称: ${selectedProject.value?.company_name || '-'}\n`
  content += `- 生成时间: ${new Date().toLocaleString()}\n\n`

  content += `## 商务应答内容\n\n`
  content += `${generationResult.value.content}\n\n`

  content += `---\n\n`
  content += `## 响应度分析\n\n`
  content += `**总体响应度: ${generationResult.value.responseRate}%**\n\n`
  content += `${generationResult.value.analysis}\n\n`

  content += `---\n\n`
  content += `## 风险提示\n\n`
  content += `${generationResult.value.risks}\n\n`

  content += `---\n\n`
  content += `## 改进建议\n\n`
  content += `${generationResult.value.suggestions}\n`

  return content
}

onMounted(() => {
  loadProjects()
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

  .analysis-section {
    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .progress-text {
      font-size: 16px;
      font-weight: 600;
    }
  }

  :deep(.el-tabs) {
    .el-tabs__header {
      margin-bottom: 20px;
    }

    .el-tabs__item {
      font-size: 14px;
      font-weight: 500;
    }
  }
}
</style>
