<template>
  <div class="point-to-point">
    <PageHeader
      title="点对点应答"
      description="针对招标要求逐点响应"
    />

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
                  :label="`${project.name} (${project.number || '-'})`"
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
          <span>Step 2: 上传招标文档</span>
        </div>
      </template>

      <DocumentUploader
        v-model="form.tenderFiles"
        :upload-url="`/api/tender-projects/${form.projectId}/upload-tender`"
        accept=".pdf,.doc,.docx"
        :limit="5"
        :max-size="50"
        drag
        tip-text="上传招标文档，AI将自动提取所有要求并生成点对点应答"
        @success="handleUploadSuccess"
      />

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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { PageHeader, DocumentUploader, SSEStreamViewer } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import type { Project, UploadUserFile } from '@/types'

interface Requirement {
  id: number
  category: 'technical' | 'business' | 'qualification' | 'other'
  requirement: string
  priority: '高' | '中' | '低'
  status: 'pending' | 'generated' | 'reviewed'
  response?: string
  compliance?: '完全符合' | '部分符合' | '不符合'
}

// 表单数据
const form = ref({
  projectId: null as number | null,
  tenderFiles: [] as UploadUserFile[]
})

// 项目列表
const projects = ref<Project[]>([])
const selectedProject = computed(() =>
  projects.value.find(p => p.id === form.value.projectId)
)

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

// 是否有应答结果
const hasResponses = computed(() =>
  requirements.value.some(req => req.response)
)

// 应答展开项
const activeResponses = ref<number[]>([])

// 应答详情对话框
const responseDialogVisible = ref(false)
const currentRequirement = ref<Requirement | null>(null)

// 能否提取
const canExtract = computed(() =>
  form.value.projectId && form.value.tenderFiles.length > 0
)

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
const handleProjectChange = () => {
  form.value.tenderFiles = []
  requirements.value = []
  selectedRequirements.value = []
}

// 上传成功
const handleUploadSuccess = () => {
  ElMessage.success('文档上传成功')
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
  link.download = `点对点应答-${selectedProject.value?.name || 'export'}-${Date.now()}.txt`
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

onMounted(() => {
  loadProjects()
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
  .responses-section {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
    }
  }

  .action-controls {
    display: flex;
    justify-content: center;
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
