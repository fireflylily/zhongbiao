<template>
  <div class="document-merge-panel">
    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <!-- 主要内容 -->
    <template v-else>
      <!-- ========== 步骤1：文件状态检查 ========== -->
      <section class="merge-section">
        <div class="section-header">
          <h3><i class="bi bi-file-check"></i> 步骤 1/3：文件状态检查</h3>
        </div>

        <div class="files-status">
          <!-- 商务应答文件 -->
          <div class="file-status-item" :class="{ 'file-ready': files.business }">
            <div class="status-icon">
              <i v-if="files.business" class="bi bi-check-circle-fill text-success"></i>
              <i v-else class="bi bi-x-circle-fill text-danger"></i>
            </div>
            <div class="file-info">
              <h4>商务应答文件</h4>
              <template v-if="files.business">
                <p class="file-name">{{ files.business.file_name }}</p>
                <p class="file-meta">{{ formatFileSize(files.business.file_size) }}</p>
              </template>
              <p v-else class="text-muted">未生成</p>
            </div>
            <div v-if="files.business" class="file-actions">
              <el-button size="small" @click="handlePreviewFile('business')">
                <i class="bi bi-eye"></i> 预览
              </el-button>
            </div>
          </div>

          <!-- 技术点对点应答 -->
          <div class="file-status-item" :class="{ 'file-ready': files.p2p }">
            <div class="status-icon">
              <i v-if="files.p2p" class="bi bi-check-circle-fill text-success"></i>
              <i v-else class="bi bi-dash-circle text-warning"></i>
            </div>
            <div class="file-info">
              <h4>技术点对点应答</h4>
              <template v-if="files.p2p">
                <p class="file-name">{{ files.p2p.file_name }}</p>
                <p class="file-meta">{{ formatFileSize(files.p2p.file_size) }}</p>
              </template>
              <p v-else class="text-muted">未生成（可选）</p>
            </div>
            <div v-if="files.p2p" class="file-actions">
              <el-button size="small" @click="handlePreviewFile('p2p')">
                <i class="bi bi-eye"></i> 预览
              </el-button>
            </div>
          </div>

          <!-- 技术方案文件 -->
          <div class="file-status-item" :class="{ 'file-ready': files.tech }">
            <div class="status-icon">
              <i v-if="files.tech" class="bi bi-check-circle-fill text-success"></i>
              <i v-else class="bi bi-x-circle-fill text-danger"></i>
            </div>
            <div class="file-info">
              <h4>技术方案文件</h4>
              <template v-if="files.tech">
                <p class="file-name">{{ files.tech.file_name }}</p>
                <p class="file-meta">{{ formatFileSize(files.tech.file_size) }}</p>
              </template>
              <p v-else class="text-muted">未生成</p>
            </div>
            <div v-if="files.tech" class="file-actions">
              <el-button size="small" @click="handlePreviewFile('tech')">
                <i class="bi bi-eye"></i> 预览
              </el-button>
            </div>
          </div>
        </div>

        <!-- 必需文件缺失提示 -->
        <el-alert
          v-if="!canMerge"
          type="warning"
          :closable="false"
          show-icon
          class="mt-3"
        >
          <template #title>
            无法整合：缺少必需的文件
          </template>
          <template #default>
            <p v-if="!files.business">• 商务应答文件未生成，请先完成商务应答</p>
            <p v-if="!files.tech">• 技术方案文件未生成，请先完成技术方案</p>
          </template>
        </el-alert>
      </section>

      <!-- ========== 步骤2：整合配置 ========== -->
      <section v-if="canMerge" class="merge-section">
        <div class="section-header">
          <h3><i class="bi bi-sliders"></i> 步骤 2/3：整合配置</h3>
        </div>

        <!-- 文档组成 -->
        <div class="config-group">
          <h4><i class="bi bi-files"></i> 文档组成与顺序</h4>
          <div class="doc-order-list">
            <div class="doc-order-item fixed">
              <span class="order-number">1</span>
              <span class="doc-name">商务应答</span>
              <el-tag size="small" type="info">固定第一部分</el-tag>
            </div>

            <div v-if="files.p2p" class="doc-order-item">
              <span class="order-number">2</span>
              <span class="doc-name">点对点应答</span>
              <el-checkbox v-model="mergeConfig.include_p2p">包含此部分</el-checkbox>
            </div>

            <div class="doc-order-item">
              <span class="order-number">{{ files.p2p ? '3' : '2' }}</span>
              <span class="doc-name">技术方案</span>
              <el-tag size="small" type="success">✓ 包含</el-tag>
            </div>
          </div>
        </div>

        <!-- 格式选项 -->
        <div class="config-group">
          <h4><i class="bi bi-palette"></i> 格式与目录选项</h4>
          <div class="options-list">
            <el-checkbox v-model="mergeConfig.generate_toc">
              自动生成目录（基于1-3级标题，带页码）
            </el-checkbox>
            <el-checkbox v-model="mergeConfig.remove_blanks">
              删除空白页和空白段落
            </el-checkbox>
            <el-checkbox v-model="mergeConfig.unify_styles">
              统一页眉页脚格式
            </el-checkbox>
            <el-checkbox v-model="mergeConfig.add_section_breaks">
              每部分间添加分节符
            </el-checkbox>
          </div>
        </div>

        <!-- 索引设置 -->
        <div class="config-group">
          <h4><i class="bi bi-list-ol"></i> 索引设置</h4>

          <!-- 无索引要求 -->
          <el-alert
            v-if="!indexRequirement.required"
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              招标文件未要求提供索引，无需生成
            </template>
          </el-alert>

          <!-- 固定格式索引 -->
          <el-alert
            v-else-if="indexRequirement.type === 'fixed_format'"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #title>
              招标文件要求提供固定格式索引
            </template>
            <template #default>
              <div class="index-template-preview">
                <pre>{{ indexRequirement.template }}</pre>
              </div>
              <el-checkbox v-model="indexEnabled" disabled checked>
                自动生成索引（必需）
              </el-checkbox>
            </template>
          </el-alert>

          <!-- 评分标准索引 -->
          <el-alert
            v-else-if="indexRequirement.type === 'score_based'"
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              招标文件要求以评分标准建立索引
            </template>
            <template #default>
              <div class="score-items-preview">
                <p>将基于以下评分项生成索引：</p>
                <ul>
                  <li v-for="item in indexRequirement.score_items" :key="item">
                    {{ item }}
                  </li>
                </ul>
              </div>
              <el-checkbox v-model="indexEnabled" disabled checked>
                自动生成评分标准索引（必需）
              </el-checkbox>
            </template>
          </el-alert>
        </div>

        <!-- 文档名称 -->
        <div class="config-group">
          <h4><i class="bi bi-file-earmark-text"></i> 文档名称</h4>
          <el-input
            v-model="mergeConfig.output_filename"
            placeholder="请输入最终标书文件名"
            maxlength="100"
            show-word-limit
          >
            <template #suffix>.docx</template>
          </el-input>
        </div>
      </section>

      <!-- ========== 步骤3：开始整合 ========== -->
      <section v-if="canMerge" class="merge-section">
        <div class="section-header">
          <h3><i class="bi bi-rocket-takeoff"></i> 步骤 3/3：开始整合</h3>
        </div>

        <!-- 未开始状态 -->
        <div v-if="!merging && !mergeResult" class="action-area">
          <el-button
            type="primary"
            size="large"
            :loading="starting"
            @click="startMerge"
          >
            <i class="bi bi-play-fill"></i> 开始整合
          </el-button>
        </div>

        <!-- 整合中 -->
        <div v-if="merging" class="merge-progress">
          <el-progress :percentage="mergeProgress" :status="mergeStatus" />
          <p class="progress-message">{{ mergeMessage }}</p>

          <div class="progress-details">
            <h5>处理详情：</h5>
            <ul>
              <li v-for="(step, index) in completedSteps" :key="index" class="completed">
                <i class="bi bi-check-circle-fill"></i> {{ step }}
              </li>
              <li v-if="currentStep" class="current">
                <i class="bi bi-arrow-right-circle-fill"></i> {{ currentStep }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 整合完成 -->
        <div v-if="mergeResult" class="merge-result">
          <el-result
            icon="success"
            title="整合完成！"
            sub-title="您的最终标书已生成"
          >
            <template #extra>
              <div class="result-info">
                <h4><i class="bi bi-file-earmark-check"></i> 文件信息</h4>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="文件名">
                    {{ mergeResult.filename }}
                  </el-descriptions-item>
                  <el-descriptions-item label="文件大小">
                    {{ formatFileSize(mergeResult.file_size) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="总页数">
                    {{ mergeResult.stats?.total_pages || '--' }} 页
                  </el-descriptions-item>
                  <el-descriptions-item label="生成时间">
                    {{ mergeResult.created_at }}
                  </el-descriptions-item>
                </el-descriptions>

                <h4 class="mt-3"><i class="bi bi-bar-chart"></i> 文件组成统计</h4>
                <ul class="stats-list">
                  <li v-if="mergeResult.stats?.toc_pages">
                    目录：{{ mergeResult.stats.toc_pages }} 页
                  </li>
                  <li>商务应答：{{ mergeResult.stats?.business_pages || '--' }} 页</li>
                  <li v-if="mergeConfig.include_p2p">
                    点对点应答：{{ mergeResult.stats?.p2p_pages || '--' }} 页
                  </li>
                  <li>技术方案：{{ mergeResult.stats?.tech_pages || '--' }} 页</li>
                  <li v-if="mergeResult.stats?.index_pages">
                    索引：{{ mergeResult.stats.index_pages }} 页
                  </li>
                </ul>

                <h4 class="mt-3"><i class="bi bi-tools"></i> 处理详情</h4>
                <ul class="processing-details">
                  <li v-if="mergeResult.stats?.removed_blanks">
                    <i class="bi bi-check-circle text-success"></i>
                    已删除 {{ mergeResult.stats.removed_blanks }} 个空白段落
                  </li>
                  <li v-if="mergeConfig.generate_toc">
                    <i class="bi bi-check-circle text-success"></i>
                    已生成多级目录
                  </li>
                  <li v-if="indexRequirement.required">
                    <i class="bi bi-check-circle text-success"></i>
                    已生成{{ indexRequirement.type === 'score_based' ? '评分标准' : '固定格式' }}索引
                  </li>
                  <li v-if="mergeConfig.unify_styles">
                    <i class="bi bi-check-circle text-success"></i>
                    已统一页眉页脚
                  </li>
                </ul>

                <div class="action-buttons">
                  <el-button type="primary" size="large" @click="downloadMergedFile">
                    <i class="bi bi-download"></i> 下载Word版
                  </el-button>
                  <el-button type="success" size="large" @click="previewMergedFile">
                    <i class="bi bi-eye"></i> 在线预览
                  </el-button>
                  <el-button type="warning" size="large" @click="editMergedFile">
                    <i class="bi bi-pencil-square"></i> 在线编辑
                  </el-button>
                  <el-button size="large" @click="resetMerge">
                    <i class="bi bi-arrow-clockwise"></i> 重新整合
                  </el-button>
                </div>
              </div>
            </template>
          </el-result>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// Props
const props = defineProps<{
  projectId: number
  currentDocuments?: any  // 从父组件传递的文档信息
}>()

// State
const loading = ref(true)
const files = ref<any>({})
const indexRequirement = ref<any>({ required: false, type: 'none' })
const mergeConfig = ref<any>({
  include_p2p: true,
  doc_order: ['business', 'p2p', 'tech'],
  generate_toc: true,
  remove_blanks: true,
  unify_styles: true,
  add_section_breaks: true,
  output_filename: ''
})

const merging = ref(false)
const starting = ref(false)
const mergeProgress = ref(0)
const mergeStatus = ref<'' | 'success' | 'exception'>('')
const mergeMessage = ref('')
const currentStep = ref('')
const completedSteps = ref<string[]>([])
const mergeResult = ref<any>(null)
const indexEnabled = ref(true)

// Computed
const canMerge = computed(() => {
  return files.value.business && files.value.tech
})

// Methods
const loadMergeConfig = async () => {
  try {
    loading.value = true

    // 如果父组件传递了 currentDocuments，使用它来构建文件信息
    if (props.currentDocuments) {
      console.log('[DocumentMergePanel] 使用父组件传递的文档:', props.currentDocuments)

      // 构建文件信息
      const docs = props.currentDocuments
      files.value = {}

      // 商务应答文件
      if (docs.businessResponseFile) {
        files.value.business = {
          status: 'ready',
          file_path: docs.businessResponseFile.outputFile,
          file_name: docs.businessResponseFile.outputFile?.split('/').pop() || '商务应答文件.docx',
          file_size: docs.businessResponseFile.stats?.file_size || 0
        }
      }

      // 点对点应答文件
      if (docs.p2pResponseFile) {
        files.value.p2p = {
          status: 'ready',
          file_path: docs.p2pResponseFile.outputFile,
          file_name: docs.p2pResponseFile.outputFile?.split('/').pop() || '点对点应答文件.docx',
          file_size: docs.p2pResponseFile.stats?.file_size || 0
        }
      }

      // 技术方案文件
      if (docs.techProposalFile) {
        files.value.tech = {
          status: 'ready',
          file_path: docs.techProposalFile.outputFile,
          file_name: docs.techProposalFile.outputFile?.split('/').pop() || '技术方案文件.docx',
          file_size: docs.techProposalFile.stats?.file_size || 0
        }
      }

      console.log('[DocumentMergePanel] 构建的文件信息:', files.value)

      // 设置默认配置
      mergeConfig.value = {
        include_p2p: !!files.value.p2p,
        doc_order: files.value.p2p ? ['business', 'p2p', 'tech'] : ['business', 'tech'],
        generate_toc: true,
        remove_blanks: true,
        unify_styles: true,
        add_section_breaks: true,
        output_filename: `项目${props.projectId}_最终标书`
      }

      loading.value = false
      return
    }

    // 否则，调用API获取配置
    const response = await axios.get(`/api/projects/${props.projectId}/merge-config`)

    console.log('[DocumentMergePanel] API配置响应:', response.data)

    if (response.data.success) {
      const data = response.data.data
      files.value = data.files || {}
      indexRequirement.value = data.index_requirement || { required: false, type: 'none' }

      // 应用默认配置
      if (data.default_config) {
        mergeConfig.value = { ...data.default_config }
      }
    }
  } catch (error) {
    console.error('[DocumentMergePanel] 加载整合配置失败:', error)
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const startMerge = async () => {
  try {
    starting.value = true

    // 构建文件路径
    const file_paths: any = {
      business: files.value.business.file_path,
      tech: files.value.tech.file_path
    }

    if (mergeConfig.value.include_p2p && files.value.p2p) {
      file_paths.p2p = files.value.p2p.file_path
    }

    // 发起整合请求
    const response = await axios.post(
      `/api/projects/${props.projectId}/merge-documents`,
      {
        file_paths,
        config: {
          ...mergeConfig.value,
          index_config: indexRequirement.value
        }
      }
    )

    if (response.data.success) {
      const taskId = response.data.task_id || props.projectId  // task_id实际上就是project_id

      console.log('[DocumentMergePanel] 整合任务已启动，task_id:', taskId)

      // 开始监听进度
      merging.value = true
      starting.value = false
      watchMergeProgress(taskId)
    }
  } catch (error: any) {
    console.error('启动整合失败:', error)
    ElMessage.error(error.response?.data?.error || '启动整合失败')
    starting.value = false
  }
}

const watchMergeProgress = (taskId: number) => {
  const eventSource = new EventSource(`/api/merge-status/${taskId}`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      mergeProgress.value = data.progress_percentage || 0
      mergeMessage.value = data.current_step || ''

      // 记录已完成的步骤
      if (data.current_step && !completedSteps.value.includes(data.current_step)) {
        if (currentStep.value) {
          completedSteps.value.push(currentStep.value)
        }
        currentStep.value = data.current_step
      }

      // 检查是否完成
      if (data.overall_status === 'completed') {
        mergeStatus.value = 'success'
        mergeProgress.value = 100

        // 解析结果
        if (data.options) {
          const options = typeof data.options === 'string'
            ? JSON.parse(data.options)
            : data.options

          mergeResult.value = {
            filename: mergeConfig.value.output_filename + '.docx',
            file_path: options.merged_document_path,
            file_size: options.file_size || 0,
            stats: options.stats,
            created_at: new Date().toLocaleString('zh-CN')
          }
        }

        merging.value = false
        eventSource.close()
        ElMessage.success('文档整合完成！')
      } else if (data.overall_status === 'failed') {
        mergeStatus.value = 'exception'
        merging.value = false
        eventSource.close()
        ElMessage.error('文档整合失败：' + data.current_step)
      }
    } catch (e) {
      console.error('解析进度数据失败:', e)
    }
  }

  eventSource.onerror = () => {
    eventSource.close()
    if (merging.value) {
      ElMessage.error('进度监听中断')
      merging.value = false
    }
  }
}

const resetMerge = () => {
  ElMessageBox.confirm('确定要重新整合吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    mergeResult.value = null
    mergeProgress.value = 0
    mergeStatus.value = ''
    mergeMessage.value = ''
    currentStep.value = ''
    completedSteps.value = []
  }).catch(() => {})
}

/**
 * 转换文件路径为API URL
 */
const convertToApiUrl = (filePath: string): string => {
  if (!filePath) return ''

  // 如果已经是API路径，直接返回
  if (filePath.startsWith('/api/')) {
    return filePath
  }

  // 移除绝对路径前缀
  let apiPath = filePath
  const absolutePrefix = '/Users/lvhe/Downloads/zhongbiao/zhongbiao/'
  if (apiPath.startsWith(absolutePrefix)) {
    apiPath = apiPath.substring(absolutePrefix.length)
  }

  // 移除 ai_tender_system/data/ 前缀
  if (apiPath.startsWith('ai_tender_system/data/')) {
    apiPath = apiPath.substring('ai_tender_system/data/'.length)
  } else if (apiPath.startsWith('data/')) {
    apiPath = apiPath.substring('data/'.length)
  }

  // 构建API URL
  return `/api/files/serve/${apiPath}`
}

const downloadMergedFile = () => {
  if (mergeResult.value?.file_path) {
    const downloadUrl = convertToApiUrl(mergeResult.value.file_path) + '?download=true'
    console.log('[DocumentMergePanel] 下载URL:', downloadUrl)
    window.open(downloadUrl, '_blank')
  }
}

const previewMergedFile = () => {
  if (mergeResult.value?.file_path) {
    const previewUrl = convertToApiUrl(mergeResult.value.file_path)
    console.log('[DocumentMergePanel] 预览URL:', previewUrl)
    window.open(previewUrl, '_blank')
  }
}

const editMergedFile = () => {
  if (mergeResult.value?.file_path) {
    ElMessage.success('正在打开编辑器...')
    // TODO: 打开富文本编辑器
    ElMessage.info('编辑功能开发中...')
  }
}

const handlePreviewFile = (type: string) => {
  const file = files.value[type]
  if (file?.file_path) {
    const previewUrl = convertToApiUrl(file.file_path)
    console.log('[DocumentMergePanel] 预览文件:', previewUrl)
    window.open(previewUrl, '_blank')
  }
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '--'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

onMounted(() => {
  loadMergeConfig()
})
</script>

<style scoped lang="scss">
.document-merge-panel {
  padding: 20px;

  .merge-section {
    margin-bottom: 30px;
    padding: 24px;
    background: var(--el-bg-color);
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);

    .section-header {
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--el-color-primary);

      h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);

        i {
          margin-right: 8px;
          color: var(--el-color-primary);
        }
      }
    }
  }

  .files-status {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .file-status-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px;
      background: var(--el-fill-color-lighter);
      border-radius: 8px;
      border: 2px solid transparent;
      transition: all 0.3s;

      &.file-ready {
        border-color: var(--el-color-success-light-5);
        background: var(--el-color-success-light-9);
      }

      .status-icon {
        font-size: 32px;

        .text-success {
          color: var(--el-color-success);
        }

        .text-danger {
          color: var(--el-color-danger);
        }

        .text-warning {
          color: var(--el-color-warning);
        }
      }

      .file-info {
        flex: 1;

        h4 {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
        }

        .file-name {
          margin: 0;
          font-size: 14px;
          color: var(--el-text-color-regular);
        }

        .file-meta {
          margin: 2px 0 0 0;
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }

        .text-muted {
          margin: 0;
          color: var(--el-text-color-placeholder);
        }
      }

      .file-actions {
        flex-shrink: 0;
      }
    }
  }

  .config-group {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    h4 {
      margin: 0 0 12px 0;
      font-size: 15px;
      font-weight: 600;
      color: var(--el-text-color-primary);

      i {
        margin-right: 6px;
        color: var(--el-color-primary);
      }
    }
  }

  .doc-order-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .doc-order-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--el-fill-color-light);
      border-radius: 6px;

      .order-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: var(--el-color-primary);
        color: white;
        border-radius: 50%;
        font-weight: 600;
        font-size: 14px;
      }

      .doc-name {
        flex: 1;
        font-weight: 500;
      }
    }
  }

  .options-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .index-template-preview,
  .score-items-preview {
    margin: 12px 0;
    padding: 12px;
    background: var(--el-fill-color-lighter);
    border-radius: 4px;

    pre {
      margin: 0;
      white-space: pre-wrap;
      font-size: 13px;
    }

    ul {
      margin: 8px 0 0 0;
      padding-left: 20px;

      li {
        margin: 4px 0;
      }
    }
  }

  .action-area {
    display: flex;
    justify-content: center;
    padding: 30px 0;
  }

  .merge-progress {
    padding: 20px;

    .progress-message {
      margin: 12px 0 0 0;
      text-align: center;
      font-size: 14px;
      color: var(--el-text-color-secondary);
    }

    .progress-details {
      margin-top: 24px;

      h5 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
      }

      ul {
        margin: 0;
        padding: 0;
        list-style: none;

        li {
          padding: 8px 12px;
          margin: 4px 0;
          border-radius: 4px;

          i {
            margin-right: 8px;
          }

          &.completed {
            background: var(--el-color-success-light-9);
            color: var(--el-color-success);
          }

          &.current {
            background: var(--el-color-primary-light-9);
            color: var(--el-color-primary);
            font-weight: 500;
          }
        }
      }
    }
  }

  .merge-result {
    .result-info {
      text-align: left;
      max-width: 800px;
      margin: 0 auto;

      h4 {
        margin: 20px 0 12px 0;
        font-size: 16px;
        font-weight: 600;

        i {
          margin-right: 6px;
          color: var(--el-color-primary);
        }

        &.mt-3 {
          margin-top: 24px;
        }
      }

      .stats-list,
      .processing-details {
        margin: 0;
        padding: 0 0 0 20px;

        li {
          margin: 8px 0;
        }
      }

      .processing-details {
        list-style: none;
        padding: 0;

        li {
          padding: 8px 12px;
          background: var(--el-fill-color-light);
          border-radius: 4px;

          i {
            margin-right: 8px;
          }
        }
      }

      .action-buttons {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 30px;
      }
    }
  }
}
</style>
