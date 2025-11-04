<template>
  <div class="tech-proposal">
    <PageHeader
      title="技术方案"
      description="AI生成技术方案大纲"
    />

    <!-- 项目选择与配置 -->
    <el-card shadow="never">
      <template #header>
        <span>方案配置</span>
      </template>

      <el-form :model="form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目">
              <el-select
                v-model="form.projectId"
                placeholder="请选择项目"
                filterable
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
            <el-form-item label="方案类型">
              <el-select v-model="form.proposalType" style="width: 100%">
                <el-option label="系统集成方案" value="integration" />
                <el-option label="软件开发方案" value="development" />
                <el-option label="运维服务方案" value="operation" />
                <el-option label="云服务方案" value="cloud" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="技术要求">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="4"
            placeholder="请输入主要技术要求，AI将基于此生成技术方案大纲"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :disabled="!canGenerate"
            :loading="generating"
            @click="generateProposal"
          >
            生成技术方案大纲
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI生成流式输出 -->
    <el-card v-if="generating" shadow="never" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>AI正在生成技术方案...</span>
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

    <!-- 方案结果 -->
    <el-card v-if="proposalResult" shadow="never" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>技术方案大纲</span>
          <div style="display: flex; gap: 12px">
            <el-button type="success" :icon="Download" @click="exportProposal">
              导出方案
            </el-button>
            <el-button type="primary" :icon="RefreshRight" @click="generateProposal">
              重新生成
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="方案大纲" name="outline">
          <SSEStreamViewer
            :content="proposalResult.outline"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </el-tab-pane>

        <el-tab-pane label="技术架构" name="architecture">
          <SSEStreamViewer
            :content="proposalResult.architecture"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </el-tab-pane>

        <el-tab-pane label="实施计划" name="plan">
          <SSEStreamViewer
            :content="proposalResult.plan"
            :is-streaming="false"
            :enable-markdown="true"
          />
        </el-tab-pane>

        <el-tab-pane label="风险评估" name="risks">
          <SSEStreamViewer
            :content="proposalResult.risks"
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
import { PageHeader, SSEStreamViewer } from '@/components'
import { tenderApi } from '@/api/endpoints/tender'
import type { Project } from '@/types'

interface ProposalResult {
  outline: string
  architecture: string
  plan: string
  risks: string
}

const form = ref({
  projectId: null as number | null,
  proposalType: 'integration',
  requirements: ''
})

const projects = ref<Project[]>([])
const generating = ref(false)
const generationProgress = ref(0)
const streamContent = ref('')
const proposalResult = ref<ProposalResult | null>(null)
const activeTab = ref('outline')

const canGenerate = computed(() =>
  form.value.projectId && form.value.requirements.trim().length > 0
)

const loadProjects = async () => {
  try {
    const response = await tenderApi.getProjects({ page: 1, page_size: 100 })
    projects.value = response.data?.items || []
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  }
}

const generateProposal = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('请填写必要信息')
    return
  }

  generating.value = true
  generationProgress.value = 0
  streamContent.value = ''
  proposalResult.value = null

  try {
    await simulateGeneration()
    ElMessage.success('技术方案生成完成')
  } catch (error) {
    ElMessage.error('生成失败，请重试')
  } finally {
    generating.value = false
  }
}

const simulateGeneration = async () => {
  return new Promise<void>((resolve) => {
    const stages = [
      { progress: 25, message: '正在分析技术要求...' },
      { progress: 50, message: '正在生成方案大纲...' },
      { progress: 75, message: '正在完善技术细节...' },
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
        proposalResult.value = {
          outline: `# 技术方案大纲\n\n## 1. 项目概述\n\n### 1.1 项目背景\n本项目旨在构建xxx系统，满足xxx业务需求。\n\n### 1.2 建设目标\n- 提升xxx效率\n- 优化xxx流程\n- 保障xxx安全\n\n## 2. 需求分析\n\n### 2.1 功能需求\n- 核心功能1\n- 核心功能2\n- 扩展功能\n\n### 2.2 性能需求\n- 并发用户数：xxx\n- 响应时间：< 3s\n- 系统可用性：99.9%\n\n## 3. 技术选型\n\n### 3.1 技术栈\n- 前端：Vue 3 + TypeScript\n- 后端：Python Flask\n- 数据库：PostgreSQL\n\n### 3.2 选型理由\n详细说明技术选型的合理性...`,
          architecture: `# 技术架构设计\n\n## 1. 总体架构\n\n采用分层架构设计：\n- 展现层\n- 业务层\n- 数据层\n\n## 2. 系统架构图\n\n\`\`\`\n┌─────────────┐\n│   用户层    │\n└──────┬──────┘\n       │\n┌──────▼──────┐\n│  前端应用   │\n└──────┬──────┘\n       │\n┌──────▼──────┐\n│   API网关   │\n└──────┬──────┘\n       │\n┌──────▼──────┐\n│  业务服务   │\n└──────┬──────┘\n       │\n┌──────▼──────┐\n│   数据库    │\n└─────────────┘\n\`\`\`\n\n## 3. 关键技术\n\n### 3.1 高可用设计\n- 负载均衡\n- 服务冗余\n- 故障切换\n\n### 3.2 安全设计\n- 身份认证\n- 权限控制\n- 数据加密`,
          plan: `# 实施计划\n\n## 1. 项目阶段\n\n### 阶段一：需求调研（2周）\n- 用户访谈\n- 需求文档\n- 原型设计\n\n### 阶段二：系统设计（3周）\n- 架构设计\n- 数据库设计\n- 接口设计\n\n### 阶段三：开发实施（12周）\n- 前端开发\n- 后端开发\n- 接口联调\n\n### 阶段四：测试验收（4周）\n- 单元测试\n- 集成测试\n- 用户验收\n\n## 2. 资源配置\n\n### 2.1 人员配置\n- 项目经理：1名\n- 架构师：1名\n- 开发人员：5名\n- 测试人员：2名\n\n## 3. 质量保障\n\n- 代码审查\n- 自动化测试\n- 持续集成`,
          risks: `# 风险评估与应对\n\n## 1. 技术风险\n\n### 1.1 性能风险\n**风险描述**: 系统并发量不足\n**风险等级**: 中\n**应对措施**:\n- 进行压力测试\n- 优化数据库查询\n- 增加缓存机制\n\n### 1.2 安全风险\n**风险描述**: 数据泄露风险\n**风险等级**: 高\n**应对措施**:\n- 实施数据加密\n- 完善权限控制\n- 定期安全审计\n\n## 2. 项目风险\n\n### 2.1 进度风险\n**风险描述**: 项目延期\n**风险等级**: 中\n**应对措施**:\n- 合理安排进度\n- 增加人力投入\n- 及时沟通调整\n\n## 3. 运维风险\n\n- 系统故障应急预案\n- 数据备份恢复策略\n- 7x24技术支持`
        }
        resolve()
      }
    }, 700)
  })
}

const stopGeneration = () => {
  generating.value = false
  ElMessage.info('已停止生成')
}

const exportProposal = () => {
  if (!proposalResult.value) return

  const content = `# 技术方案文档\n\n${proposalResult.value.outline}\n\n${proposalResult.value.architecture}\n\n${proposalResult.value.plan}\n\n${proposalResult.value.risks}`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `技术方案-${Date.now()}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('导出成功')
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
@import "@/assets/styles/variables.scss";

.tech-proposal {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    background: var(--el-fill-color-light);
    font-weight: 600;
  }
}
</style>
