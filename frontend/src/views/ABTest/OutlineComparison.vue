<!--
  大纲生成对比页面
  用于对比不同模型和提示词生成的大纲效果
-->

<template>
  <div class="outline-comparison-wrapper">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <i class="bi-diagram-3 header-icon"></i>
          <div class="title-group">
            <h1 class="page-title">大纲生成对比</h1>
            <p class="page-description">对比不同模型和提示词生成的技术方案大纲效果</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 项目和公司选择 -->
      <el-card class="selection-card">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="选择项目">
              <el-select
                v-model="selectedProjectId"
                placeholder="请选择项目"
                filterable
                clearable
                @change="handleProjectChange"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.project_name"
                  :value="project.id"
                >
                  <span>{{ project.project_name }}</span>
                  <span style="color: var(--text-secondary); font-size: 12px; margin-left: 8px">
                    {{ project.company_name }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12">
            <el-form-item label="应答公司">
              <el-select
                v-model="selectedCompanyId"
                placeholder="请选择应答公司"
                filterable
                clearable
              >
                <el-option
                  v-for="company in companies"
                  :key="company.company_id"
                  :label="company.company_name || company.name"
                  :value="company.company_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 两组对比配置 -->
      <el-row :gutter="16" style="margin-top: 16px">
        <!-- 第一组：固定配置 -->
        <el-col :xs="24" :lg="12">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-tag type="success" size="small">基准组</el-tag>
                  <span style="margin-left: 8px">当前配置</span>
                </span>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item label="模型">
                <el-input value="gpt-4o-mini" disabled>
                  <template #prepend>
                    <i class="bi-robot"></i>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="提示词">
                <el-input
                  v-model="group1Prompt"
                  type="textarea"
                  :rows="12"
                  placeholder="当前使用的大纲生成提示词"
                  disabled
                />
                <template #extra>
                  <el-text size="small" type="info">
                    这是当前系统使用的提示词（只读）
                  </el-text>
                </template>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 第二组：可编辑配置 -->
        <el-col :xs="24" :lg="12">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-tag type="warning" size="small">对比组</el-tag>
                  <span style="margin-left: 8px">自定义配置</span>
                </span>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item label="模型">
                <el-select v-model="group2Model" placeholder="选择模型">
                  <el-option label="GPT-4" value="gpt-4" />
                  <el-option label="GPT-4o" value="gpt-4o" />
                  <el-option label="GPT-4o-mini" value="gpt-4o-mini" />
                  <el-option label="GPT-3.5-turbo" value="gpt-3.5-turbo" />
                  <el-option label="Claude-3-Opus" value="claude-3-opus" />
                  <el-option label="Claude-3-Sonnet" value="claude-3-sonnet" />
                </el-select>
              </el-form-item>

              <el-form-item label="提示词">
                <el-input
                  v-model="group2Prompt"
                  type="textarea"
                  :rows="12"
                  placeholder="输入自定义提示词..."
                />
                <template #extra>
                  <el-text size="small" type="info">
                    自定义提示词，用于对比测试
                  </el-text>
                </template>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 操作按钮 -->
      <div class="action-section">
        <el-button
          type="primary"
          size="large"
          :icon="PlayIcon"
          :loading="generating"
          :disabled="!canGenerate"
          @click="handleGenerate"
        >
          开始生成对比
        </el-button>
        <el-button size="large" :icon="RefreshIcon" @click="handleReset">
          重置
        </el-button>
      </div>

      <!-- 对比结果 -->
      <el-card v-if="hasResults" class="result-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <i class="bi-bar-chart"></i>
              生成结果对比
            </span>
            <el-button text :icon="DownloadIcon">导出报告</el-button>
          </div>
        </template>

        <el-row :gutter="16">
          <!-- 基准组结果 -->
          <el-col :xs="24" :lg="12">
            <div class="result-section">
              <h3 class="result-title">
                <el-tag type="success" size="small">基准组</el-tag>
                GPT-4o-mini
              </h3>

              <div class="outline-content">
                <el-scrollbar max-height="600px">
                  <div v-if="group1Result" class="outline-text">
                    {{ group1Result }}
                  </div>
                  <el-empty v-else description="暂无结果" />
                </el-scrollbar>
              </div>

              <div class="result-meta">
                <el-text size="small" type="info">
                  生成时间: {{ group1Time || '-' }}
                </el-text>
              </div>
            </div>
          </el-col>

          <!-- 对比组结果 -->
          <el-col :xs="24" :lg="12">
            <div class="result-section">
              <h3 class="result-title">
                <el-tag type="warning" size="small">对比组</el-tag>
                {{ group2Model || '未选择' }}
              </h3>

              <div class="outline-content">
                <el-scrollbar max-height="600px">
                  <div v-if="group2Result" class="outline-text">
                    {{ group2Result }}
                  </div>
                  <el-empty v-else description="暂无结果" />
                </el-scrollbar>
              </div>

              <div class="result-meta">
                <el-text size="small" type="info">
                  生成时间: {{ group2Time || '-' }}
                </el-text>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Play as PlayIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { tenderApi, companyApi } from '@/api'

// ==================== State ====================

// 项目和公司
const projects = ref<any[]>([])
const companies = ref<any[]>([])
const selectedProjectId = ref<number | null>(null)
const selectedCompanyId = ref<number | null>(null)

// 配置组1（固定）
const group1Prompt = ref(`你是一个专业的技术方案大纲生成助手。请根据招标文档的需求分析结果，生成一份结构化的技术方案应答大纲。

要求：
1. 大纲应该包含3-4级标题
2. 每个章节应该有明确的主题和子主题
3. 章节之间应该有逻辑关系
4. 大纲应该全面覆盖招标文档中的技术需求

请以JSON格式返回大纲结构。`)

// 配置组2（可编辑）
const group2Model = ref('')
const group2Prompt = ref('')

// 生成状态
const generating = ref(false)
const hasResults = ref(false)
const group1Result = ref('')
const group2Result = ref('')
const group1Time = ref('')
const group2Time = ref('')

// ==================== Computed ====================

const canGenerate = computed(() => {
  return selectedProjectId.value && selectedCompanyId.value && group2Model.value && group2Prompt.value
})

// ==================== Methods ====================

/**
 * 加载项目列表
 */
async function loadProjects() {
  try {
    const response = await tenderApi.getProjects()
    if (response.success && response.data?.items) {
      projects.value = response.data.items
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

/**
 * 加载公司列表
 */
async function loadCompanies() {
  try {
    const response = await companyApi.getCompanies()
    if (response.success && response.data) {
      companies.value = response.data
    }
  } catch (error) {
    console.error('加载公司列表失败:', error)
    ElMessage.error('加载公司列表失败')
  }
}

/**
 * 项目切换事件
 */
function handleProjectChange(projectId: number | null) {
  if (!projectId) {
    selectedCompanyId.value = null
    return
  }

  // 自动选择项目关联的公司
  const project = projects.value.find(p => p.id === projectId)
  if (project && project.company_id) {
    selectedCompanyId.value = project.company_id
  }
}

/**
 * 开始生成对比
 */
async function handleGenerate() {
  if (!canGenerate.value) {
    ElMessage.warning('请完整填写所有配置项')
    return
  }

  generating.value = true
  hasResults.value = false

  try {
    // TODO: 调用后端API生成大纲
    // 这里需要后端提供对应的API接口
    ElMessage.info('大纲生成功能开发中...')

    // 模拟生成结果
    setTimeout(() => {
      group1Result.value = '第一章 项目概述\n1.1 项目背景\n1.2 项目目标\n第二章 技术方案\n2.1 系统架构\n2.2 技术选型'
      group2Result.value = '第一章 项目介绍\n1.1 背景分析\n1.2 目标设定\n第二章 解决方案\n2.1 架构设计\n2.2 技术栈'
      group1Time.value = '2.3秒'
      group2Time.value = '3.1秒'
      hasResults.value = true
      generating.value = false
    }, 2000)
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败')
    generating.value = false
  }
}

/**
 * 重置
 */
function handleReset() {
  selectedProjectId.value = null
  selectedCompanyId.value = null
  group2Model.value = ''
  group2Prompt.value = ''
  hasResults.value = false
  group1Result.value = ''
  group2Result.value = ''
  group1Time.value = ''
  group2Time.value = ''
}

// ==================== Lifecycle ====================

onMounted(() => {
  loadProjects()
  loadCompanies()
})
</script>

<style scoped lang="scss">
.outline-comparison-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-light, #f8f9fa);
}

// ==================== 页面头部 ====================

.page-header {
  background: var(--bg-white, #ffffff);
  border-bottom: 1px solid var(--border-light, #e5e7eb);
  padding: 20px 24px;
  flex-shrink: 0;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 32px;
  color: var(--brand-primary, #4a89dc);
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
}

// ==================== 主要内容 ====================

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

// ==================== 卡片样式 ====================

.selection-card,
.config-card,
.result-card {
  margin-bottom: 16px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-light, #e5e7eb);
  }

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  display: flex;
  align-items: center;
  gap: 8px;

  i {
    font-size: 18px;
    color: var(--brand-primary, #4a89dc);
  }
}

// ==================== 选择区域 ====================

.selection-card {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }

  :deep(.el-select) {
    width: 100%;
  }
}

// ==================== 配置卡片 ====================

.config-card {
  height: 100%;

  :deep(.el-textarea__inner) {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
  }

  :deep(.el-input.is-disabled .el-input__inner),
  :deep(.el-textarea.is-disabled .el-textarea__inner) {
    background-color: var(--bg-light, #f8f9fa);
    color: var(--text-secondary, #6c757d);
  }
}

// ==================== 操作按钮 ====================

.action-section {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 24px 0;
  padding: 20px;
  background: var(--bg-white, #ffffff);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.1));
}

// ==================== 结果展示 ====================

.result-section {
  .result-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary, #1f2937);
  }

  .outline-content {
    background: var(--bg-light, #f8f9fa);
    border-radius: var(--border-radius-md, 8px);
    padding: 16px;
    margin-bottom: 12px;
  }

  .outline-text {
    white-space: pre-wrap;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-primary, #1f2937);
  }

  .result-meta {
    text-align: right;
    padding: 8px 0;
  }
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .page-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 20px;
  }

  .main-content {
    padding: 16px;
  }

  .action-section {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }
}
</style>
