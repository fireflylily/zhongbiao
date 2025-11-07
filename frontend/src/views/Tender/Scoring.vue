<template>
  <div class="tender-scoring">
    <!-- 项目选择 -->
    <el-card class="project-selector" shadow="never">
      <template #header>
        <div class="card-header">
          <span>选择项目</span>
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
                  :label="`${project.project_name} (${project.project_number})`"
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

    <!-- 评分配置 -->
    <el-card v-if="form.projectId" class="scoring-config" shadow="never">
      <template #header>
        <div class="card-header">
          <span>评分维度配置</span>
          <el-button type="primary" size="small" @click="addDimension">
            添加维度
          </el-button>
        </div>
      </template>

      <el-table :data="scoringDimensions" border>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="评分维度" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.name" placeholder="请输入评分维度" />
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重 (%)" width="120">
          <template #default="{ row }">
            <el-input-number
              v-model="row.weight"
              :min="0"
              :max="100"
              :step="5"
              controls-position="right"
              style="width: 100%"
            />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="评分说明" min-width="200">
          <template #default="{ row }">
            <el-input
              v-model="row.description"
              type="textarea"
              :rows="2"
              placeholder="请输入评分说明"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ $index }">
            <el-button
              type="danger"
              size="small"
              text
              @click="removeDimension($index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="scoring-actions">
        <div class="weight-summary">
          总权重: <strong :class="{ 'error': totalWeight !== 100 }">{{ totalWeight }}%</strong>
          <span v-if="totalWeight !== 100" class="weight-tip">
            (权重总和应为 100%)
          </span>
        </div>
        <el-button
          type="primary"
          :disabled="!canStartScoring"
          :loading="scoringLoading"
          @click="startScoring"
        >
          开始AI评分
        </el-button>
      </div>
    </el-card>

    <!-- 评分结果 -->
    <el-card v-if="scoringResult" class="scoring-result" shadow="never">
      <template #header>
        <div class="card-header">
          <span>评分结果</span>
          <div class="header-actions">
            <el-tag :type="getScoreType(scoringResult.totalScore)" size="large">
              总分: {{ scoringResult.totalScore }} / 100
            </el-tag>
            <el-button
              type="success"
              size="small"
              :icon="Download"
              @click="exportReport"
            >
              导出报告
            </el-button>
          </div>
        </div>
      </template>

      <!-- 各维度评分 -->
      <div class="dimension-scores">
        <h4>各维度评分详情</h4>
        <el-table :data="scoringResult.dimensions" border>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="name" label="评分维度" min-width="150" />
          <el-table-column prop="weight" label="权重" width="100">
            <template #default="{ row }">
              {{ row.weight }}%
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得分" width="100">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.score)">
                {{ row.score }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="weightedScore" label="加权得分" width="120">
            <template #default="{ row }">
              {{ row.weightedScore.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="analysis" label="AI分析" min-width="300">
            <template #default="{ row }">
              <div class="analysis-content" v-html="formatMarkdown(row.analysis)"></div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 风险分析 -->
      <div class="risk-analysis">
        <h4>风险分析</h4>
        <SSEStreamViewer
          :content="scoringResult.riskAnalysis"
          :is-streaming="false"
          :enable-markdown="true"
        />
      </div>

      <!-- 改进建议 -->
      <div class="improvement-suggestions">
        <h4>改进建议</h4>
        <SSEStreamViewer
          :content="scoringResult.suggestions"
          :is-streaming="false"
          :enable-markdown="true"
        />
      </div>
    </el-card>

    <!-- AI评分流式输出 -->
    <el-card v-if="scoringLoading" class="streaming-output" shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI正在评分...</span>
        </div>
      </template>

      <SSEStreamViewer
        :content="streamContent"
        :is-streaming="scoringLoading"
        @stop="stopScoring"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { SSEStreamViewer } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import { marked } from 'marked'
import type { Project } from '@/types'

interface ScoringDimension {
  name: string
  weight: number
  description: string
}

interface DimensionScore extends ScoringDimension {
  score: number
  weightedScore: number
  analysis: string
}

interface ScoringResult {
  totalScore: number
  dimensions: DimensionScore[]
  riskAnalysis: string
  suggestions: string
}

// 表单数据
const form = ref({
  projectId: null as number | null
})

// 项目列表
const projects = ref<Project[]>([])
const selectedProject = computed(() =>
  projects.value.find(p => p.id === form.value.projectId)
)

// 评分维度
const scoringDimensions = ref<ScoringDimension[]>([
  { name: '技术方案完整性', weight: 30, description: '技术方案的完整性和可行性' },
  { name: '商务响应度', weight: 25, description: '商务条款的响应程度' },
  { name: '资质匹配度', weight: 20, description: '公司资质与项目要求的匹配程度' },
  { name: '成本合理性', weight: 15, description: '报价的合理性和竞争力' },
  { name: '风险控制', weight: 10, description: '项目风险的识别和控制措施' }
])

// 总权重
const totalWeight = computed(() =>
  scoringDimensions.value.reduce((sum, dim) => sum + dim.weight, 0)
)

// 能否开始评分
const canStartScoring = computed(() =>
  form.value.projectId && totalWeight.value === 100 && scoringDimensions.value.length > 0
)

// 评分状态
const scoringLoading = ref(false)
const streamContent = ref('')
const scoringResult = ref<ScoringResult | null>(null)

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
  // 清空之前的评分结果
  scoringResult.value = null
  streamContent.value = ''
}

// 添加评分维度
const addDimension = () => {
  scoringDimensions.value.push({
    name: '',
    weight: 0,
    description: ''
  })
}

// 删除评分维度
const removeDimension = (index: number) => {
  scoringDimensions.value.splice(index, 1)
}

// 开始AI评分
const startScoring = async () => {
  if (!form.value.projectId) {
    ElMessage.warning('请先选择项目')
    return
  }

  if (totalWeight.value !== 100) {
    ElMessage.warning('评分维度权重总和必须为100%')
    return
  }

  scoringLoading.value = true
  streamContent.value = ''
  scoringResult.value = null

  try {
    // 模拟AI评分流程（实际应该调用后端API）
    await simulateAIScoring()

    ElMessage.success('评分完成')
  } catch (error) {
    console.error('评分失败:', error)
    ElMessage.error('评分失败，请重试')
  } finally {
    scoringLoading.value = false
  }
}

// 模拟AI评分（实际应该调用后端SSE接口）
const simulateAIScoring = async () => {
  return new Promise<void>((resolve) => {
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      streamContent.value += `\n正在分析第 ${progress/10} 个维度...`

      if (progress >= 100) {
        clearInterval(interval)

        // 生成评分结果
        const dimensions: DimensionScore[] = scoringDimensions.value.map(dim => {
          const score = Math.random() * 30 + 70 // 70-100分
          return {
            ...dim,
            score: Math.round(score),
            weightedScore: score * dim.weight / 100,
            analysis: `该维度表现${score >= 85 ? '优秀' : score >= 70 ? '良好' : '一般'}，${
              score >= 85
                ? '完全满足招标要求，具有明显竞争优势。'
                : score >= 70
                ? '基本满足招标要求，但仍有改进空间。'
                : '存在一定差距，需要重点改进。'
            }\n\n**优势：**\n- 方案设计合理\n- 团队经验丰富\n\n**不足：**\n- 部分细节需要完善`
          }
        })

        const totalScore = dimensions.reduce((sum, dim) => sum + dim.weightedScore, 0)

        scoringResult.value = {
          totalScore: Math.round(totalScore),
          dimensions,
          riskAnalysis: `# 风险评估\n\n## 技术风险\n- **中等风险**: 部分技术方案需要进一步细化\n- 建议加强技术团队的配置\n\n## 商务风险\n- **低风险**: 商务条款基本符合要求\n- 价格竞争力较强\n\n## 执行风险\n- **中等风险**: 项目周期较紧\n- 需要合理安排资源和进度`,
          suggestions: `# 改进建议\n\n## 技术方案优化\n1. 完善系统架构设计文档\n2. 补充性能测试方案\n3. 加强数据安全保障措施\n\n## 商务条款完善\n1. 明确验收标准\n2. 补充售后服务承诺\n\n## 团队能力提升\n1. 增加项目相关经验人员\n2. 提供更详细的团队简历`
        }

        resolve()
      }
    }, 300)
  })
}

// 停止评分
const stopScoring = () => {
  scoringLoading.value = false
  ElMessage.info('已停止评分')
}

// 获取分数类型
const getScoreType = (score: number) => {
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 70) return 'warning'
  return 'danger'
}

// 格式化Markdown
const formatMarkdown = (text: string) => {
  try {
    return marked.parse(text)
  } catch (error) {
    return text
  }
}

// 导出报告
const exportReport = () => {
  if (!scoringResult.value) return

  const report = generateReport()
  const blob = new Blob([report], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `标书评分报告-${selectedProject.value?.project_name || 'report'}-${Date.now()}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('报告导出成功')
}

// 生成报告内容
const generateReport = () => {
  if (!scoringResult.value) return ''

  let report = `# 标书评分报告\n\n`
  report += `## 项目信息\n`
  report += `- 项目名称: ${selectedProject.value?.project_name}\n`
  report += `- 项目编号: ${selectedProject.value?.project_number}\n`
  report += `- 公司名称: ${selectedProject.value?.company_name}\n`
  report += `- 评分时间: ${new Date().toLocaleString()}\n\n`

  report += `## 总体评分\n`
  report += `**总分: ${scoringResult.value.totalScore} / 100**\n\n`

  report += `## 各维度评分\n\n`
  scoringResult.value.dimensions.forEach((dim, index) => {
    report += `### ${index + 1}. ${dim.name} (权重: ${dim.weight}%)\n`
    report += `- 得分: ${dim.score}\n`
    report += `- 加权得分: ${dim.weightedScore.toFixed(2)}\n`
    report += `- 分析:\n${dim.analysis}\n\n`
  })

  report += `## ${scoringResult.value.riskAnalysis}\n\n`
  report += `## ${scoringResult.value.suggestions}\n`

  return report
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
@import "@/assets/styles/variables.scss";

.tender-scoring {
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

  .project-selector,
  .scoring-config,
  .scoring-result,
  .streaming-output {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
    }
  }

  .scoring-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid var(--el-border-color-lighter);

    .weight-summary {
      font-size: 14px;
      color: var(--el-text-color-regular);

      strong {
        font-size: 18px;
        color: var(--el-color-success);

        &.error {
          color: var(--el-color-danger);
        }
      }

      .weight-tip {
        margin-left: 8px;
        color: var(--el-color-warning);
        font-size: 12px;
      }
    }
  }

  .dimension-scores,
  .risk-analysis,
  .improvement-suggestions {
    margin-bottom: 30px;

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .analysis-content {
      font-size: 13px;
      line-height: 1.6;

      :deep(strong) {
        color: var(--el-color-primary);
      }

      :deep(ul) {
        margin: 8px 0;
        padding-left: 20px;
      }
    }
  }
}
</style>
