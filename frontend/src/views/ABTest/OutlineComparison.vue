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

      <!-- 项目文档展示 -->
      <el-card v-if="selectedProjectId && (showTenderFile || showTechnicalFile)" class="documents-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <i class="bi-folder2-open"></i>
              项目文档
            </span>
          </div>
        </template>

        <el-row :gutter="16">
          <!-- 标书文件 -->
          <el-col v-if="showTenderFile && currentDocuments.tenderFile" :xs="24" :sm="12">
            <div class="document-item">
              <div class="document-header">
                <el-icon class="document-icon" color="#409EFF"><DocumentIcon /></el-icon>
                <span class="document-label">招标文档：</span>
              </div>
              <div class="document-info">
                <el-tag type="info" size="large">{{ currentDocuments.tenderFile.name }}</el-tag>
                <el-text size="small" type="info" style="margin-left: 8px">
                  {{ formatFileSize(currentDocuments.tenderFile.size) }}
                </el-text>
              </div>
            </div>
          </el-col>

          <!-- 技术文件 -->
          <el-col v-if="showTechnicalFile && currentDocuments.technicalFile" :xs="24" :sm="12">
            <div class="document-item">
              <div class="document-header">
                <el-icon class="document-icon" color="#67C23A"><DocumentIcon /></el-icon>
                <span class="document-label">技术需求文档：</span>
              </div>
              <div class="document-info">
                <el-tag type="success" size="large">{{ currentDocuments.technicalFile.name }}</el-tag>
                <el-text size="small" type="info" style="margin-left: 8px">
                  {{ formatFileSize(currentDocuments.technicalFile.size) }}
                </el-text>
                <el-button
                  type="primary"
                  size="small"
                  plain
                  style="margin-left: 12px"
                  @click="previewTechnicalFile"
                >
                  <el-icon style="margin-right: 4px"><View /></el-icon>
                  预览
                </el-button>
              </div>
            </div>
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
                  v-loading="promptLoading"
                  type="textarea"
                  :rows="12"
                  placeholder="当前使用的大纲生成提示词"
                  disabled
                />
                <template #extra>
                  <el-text v-if="promptLoading" size="small" type="warning">
                    正在从后端加载真实提示词配置...
                  </el-text>
                  <el-text v-else size="small" type="success">
                    ✓ 已加载系统提示词模板。实际使用时，{analysis} 占位符会被替换为标书的具体需求分析结果，确保每个标书的大纲都是个性化的。
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
                  <el-option label="GPT5（最强推理）" value="shihuang-gpt5" />
                  <el-option label="Claude Sonnet 4.5（标书专用）" value="shihuang-claude-sonnet-45" />
                  <el-option label="GPT4o Mini（推荐）" value="shihuang-gpt4o-mini" />
                  <el-option label="通义千问-Max（中文优化）" value="qwen-max" />
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
import {
  VideoPlay as PlayIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Document as DocumentIcon,
  View
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { tenderApi, companyApi } from '@/api'
import { useProjectDocuments } from '@/composables'
import { HitlFileAlert, DocumentPreview } from '@/components'

// ==================== Composables ====================

const {
  projects: projectsFromComposable,
  selectedProject,
  currentDocuments,
  loadProjects: loadProjectsFromComposable,
  handleProjectChange: handleProjectChangeComposable
} = useProjectDocuments()

// ==================== State ====================

// 项目和公司
const projects = projectsFromComposable
const companies = ref<any[]>([])
const selectedProjectId = ref<number | null>(null)
const selectedCompanyId = ref<number | null>(null)

// 文档展示状态
const showTenderFile = ref(false)
const showTechnicalFile = ref(false)

// 文档预览状态
const previewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

// 配置组1（固定 - 从后端加载）
const group1Prompt = ref('正在加载提示词配置...')
const promptLoading = ref(true)

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
 * 格式化文件大小
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '未知大小'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 加载项目列表（使用 composable）
 */
async function loadProjects() {
  await loadProjectsFromComposable()
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
 * 加载提示词配置
 */
async function loadPrompts() {
  promptLoading.value = true
  try {
    const response = await tenderApi.getOutlineGenerationPrompts()
    console.log('提示词API响应:', response)
    if (response.success && response.data) {
      // 使用 generate_outline 提示词作为基准组显示
      const promptData = response.data.prompts || response.data
      group1Prompt.value = promptData.generate_outline || '未找到提示词配置'
      console.log('✓ 提示词已加载，长度:', group1Prompt.value.length)
    } else {
      group1Prompt.value = '未找到提示词配置'
    }
  } catch (error) {
    console.error('加载提示词配置失败:', error)
    ElMessage.error('加载提示词配置失败')
    group1Prompt.value = '加载失败，请刷新页面重试'
  } finally {
    promptLoading.value = false
  }
}

/**
 * 项目切换事件
 */
async function handleProjectChange(projectId: number | null) {
  // 重置文档展示状态
  showTenderFile.value = false
  showTechnicalFile.value = false

  if (!projectId) {
    selectedCompanyId.value = null
    await handleProjectChangeComposable(null)
    return
  }

  // 使用 composable 加载项目文档
  await handleProjectChangeComposable(projectId, {
    onClear: () => {
      // 清空状态
      showTenderFile.value = false
      showTechnicalFile.value = false
    },
    onDocumentsLoaded: (docs) => {
      // 如果有标书文件，显示它
      if (docs.tenderFile) {
        showTenderFile.value = true
        console.log('✅ 标书文件已加载:', docs.tenderFile.name)
      }

      // 如果有技术文件，显示它
      if (docs.technicalFile) {
        showTechnicalFile.value = true
        console.log('✅ 技术文件已加载:', docs.technicalFile.name)
      }
    }
  })

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

/**
 * 预览技术文件
 */
function previewTechnicalFile() {
  if (!currentDocuments.value.technicalFile) {
    ElMessage.warning('技术文件不存在')
    return
  }

  previewFileUrl.value = currentDocuments.value.technicalFile.url
  previewFileName.value = currentDocuments.value.technicalFile.name
  previewVisible.value = true
}

// ==================== Lifecycle ====================

onMounted(() => {
  loadProjects()
  loadCompanies()
  loadPrompts()  // 加载提示词配置
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
.result-card,
.documents-card {
  margin-bottom: 16px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-light, #e5e7eb);
  }

  :deep(.el-card__body) {
    padding: 20px;
  }
}

// ==================== 文档展示样式 ====================

.documents-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #f8f9fb 100%);
  border: 1px solid var(--border-light, #e5e7eb);

  .document-item {
    padding: 16px;
    background: var(--bg-white, #ffffff);
    border-radius: var(--border-radius-md, 8px);
    box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.05));
    transition: all 0.3s ease;

    &:hover {
      box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.1));
      transform: translateY(-2px);
    }

    .document-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;

      .document-icon {
        font-size: 20px;
      }

      .document-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary, #1f2937);
      }
    }

    .document-info {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;

      .el-tag {
        font-size: 13px;
      }
    }
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
