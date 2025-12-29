<template>
  <div class="parser-comparison">
    <Card title="📊 目录解析方法对比工具">
      <template #extra>
        <el-button @click="showHistory" type="text">历史记录</el-button>
      </template>

      <!-- 上传区域 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :on-change="handleFileSelect"
          :show-file-list="false"
          accept=".docx"
        >
          <el-button type="primary" :icon="Upload">选择标书文档 (.docx)</el-button>
        </el-upload>

        <span v-if="selectedFile" class="selected-file">
          已选择: {{ selectedFile.name }}
        </span>

        <el-button
          @click="startParsing"
          :loading="parsing"
          :disabled="!selectedFile"
          type="success"
        >
          开始解析对比
        </el-button>

        <el-divider direction="vertical" />

        <el-button
          @click="startSmartParsing"
          :loading="smartParsing"
          :disabled="!currentDocumentId"
          type="warning"
        >
          🧠 智能识别
        </el-button>

        <el-divider direction="vertical" />

        <el-button
          @click="previewDocument"
          :disabled="!currentDocumentId"
          type="info"
          :icon="View"
        >
          预览文档
        </el-button>
      </div>

      <!-- 智能识别结果展示 -->
      <div v-if="smartResult" class="smart-result-section">
        <el-card shadow="hover">
          <template #header>
            <div class="smart-result-header">
              <span class="title">🧠 智能识别结果</span>
              <div class="method-info">
                <el-tag type="primary">{{ smartResult.method_used }}</el-tag>
                <el-tag v-if="smartResult.fallback_from" type="warning">
                  回退自: {{ smartResult.fallback_from }}
                </el-tag>
                <el-tag v-if="smartResult.fallback_reason" type="info">
                  {{ smartResult.fallback_reason }}
                </el-tag>
                <span class="elapsed">耗时: {{ smartResult.performance?.elapsed_formatted || '-' }}</span>
              </div>
            </div>
          </template>

          <!-- 关键区域标记 -->
          <div v-if="smartResult.key_sections" class="key-sections">
            <h4>📌 关键区域</h4>
            <div class="section-tags">
              <div v-if="smartResult.key_sections.business_response?.length" class="section-item">
                <el-tag type="primary" effect="dark">商务应答模板</el-tag>
                <span v-for="title in smartResult.key_sections.business_response" :key="title" class="section-title">
                  {{ title }}
                </span>
              </div>
              <div v-if="smartResult.key_sections.technical_spec?.length" class="section-item">
                <el-tag type="success" effect="dark">技术规范</el-tag>
                <span v-for="title in smartResult.key_sections.technical_spec" :key="title" class="section-title">
                  {{ title }}
                </span>
              </div>
              <div v-if="smartResult.key_sections.contract_content?.length" class="section-item">
                <el-tag type="warning" effect="dark">合同内容</el-tag>
                <span v-for="title in smartResult.key_sections.contract_content" :key="title" class="section-title">
                  {{ title }}
                </span>
              </div>
            </div>
          </div>

          <!-- 章节树展示 -->
          <div class="chapters-tree">
            <h4>📚 章节结构 (共 {{ smartResult.chapters?.length || 0 }} 个一级章节)</h4>
            <el-tree
              :data="smartChapterTree"
              :props="{ label: 'label', children: 'children' }"
              default-expand-all
              :expand-on-click-node="false"
            >
              <template #default="{ node, data }">
                <span class="chapter-node">
                  <span class="chapter-title">{{ data.title }}</span>
                  <el-tag v-if="data.chapter_type" :type="getChapterTypeTag(data.chapter_type)" size="small">
                    {{ getChapterTypeName(data.chapter_type) }}
                  </el-tag>
                </span>
              </template>
            </el-tree>
          </div>
        </el-card>
      </div>

      <!-- 文档信息 -->
      <div v-if="documentInfo" class="doc-info">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="文件名">
            {{ documentInfo.filename }}
          </el-descriptions-item>
          <el-descriptions-item label="总段落数">
            {{ documentInfo.total_paragraphs }}
          </el-descriptions-item>
          <el-descriptions-item label="目录检测">
            <el-tag :type="documentInfo.has_toc ? 'success' : 'warning'">
              {{ documentInfo.has_toc ? `✓ 检测到 (${documentInfo.toc_items_count}项)` : '✗ 未检测到' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ documentInfo.upload_time || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 对比结果网格 -->
      <div v-if="results" class="comparison-grid">
        <!-- 方法1: Gemini AI解析器 -->
        <MethodCard
          v-if="results.gemini"
          title="方法1: Gemini AI解析器"
          :result="results.gemini"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.gemini"
          :status="methodStatus.gemini"
          color="#FF6D00"
          @start="startSingleMethod('gemini')"
        />

        <!-- 方法2: Word大纲级别识别 -->
        <MethodCard
          v-if="results.docx_native"
          title="方法2: Word大纲级别识别"
          :result="results.docx_native"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.docx_native"
          :status="methodStatus.docx_native"
          color="#9C27B0"
          @start="startSingleMethod('docx_native')"
        />

        <!-- 方法3: 精确匹配(基于目录) -->
        <MethodCard
          v-if="results.toc_exact"
          title="方法3: 精确匹配(基于目录)"
          :result="results.toc_exact"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.toc_exact"
          :status="methodStatus.toc_exact"
          color="#F56C6C"
          @start="startSingleMethod('toc_exact')"
        />

        <!-- 方法4: Azure Form Recognizer -->
        <MethodCard
          v-if="results.azure"
          title="方法4: Azure Form Recognizer"
          :result="results.azure"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.azure"
          :status="methodStatus.azure"
          color="#00B7C3"
          @start="startSingleMethod('azure')"
        />

        <!-- 方法5: LLM智能层级分析 -->
        <MethodCard
          v-if="results.llm_level"
          title="方法5: LLM智能层级分析"
          :result="results.llm_level"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.llm_level"
          :status="methodStatus.llm_level"
          color="#10B981"
          @start="startSingleMethod('llm_level')"
        />

        <!-- 人工标注卡片 -->
        <GroundTruthCard
          v-model="groundTruth"
          :document-id="currentDocumentId"
          :available-results="results"
          @save="handleSaveGroundTruth"
        />
      </div>

      <!-- 准确率对比表格 -->
      <div v-if="accuracy" class="accuracy-section">
        <h3>准确率对比</h3>
        <el-table :data="accuracyTableData" border stripe>
          <el-table-column prop="method" label="解析方法" width="180" />
          <el-table-column prop="precision" label="精确率 (P)" width="120">
            <template #default="{ row }">
              <span :class="getScoreClass(row.precision)">
                {{ (row.precision * 100).toFixed(1) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="recall" label="召回率 (R)" width="120">
            <template #default="{ row }">
              <span :class="getScoreClass(row.recall)">
                {{ (row.recall * 100).toFixed(1) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="f1" label="F1分数" width="120">
            <template #default="{ row }">
              <el-tag :type="getF1TagType(row.f1)" effect="dark">
                {{ (row.f1 * 100).toFixed(1) }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="detected" label="识别数量" width="100" />
          <el-table-column prop="elapsed" label="耗时" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_best" type="success">最佳</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="best-method-summary">
          <el-alert
            :title="`最佳方法: ${getBestMethodName()} (F1分数: ${(accuracy.best_f1_score * 100).toFixed(1)}%)`"
            type="success"
            :closable="false"
          />
        </div>
      </div>

      <!-- 历史解析记录（页面底部） -->
      <div class="history-section">
        <div class="section-header">
          <h3>📋 历史解析记录</h3>
          <el-button @click="loadHistoryList" :icon="Upload" size="small">
            刷新列表
          </el-button>
        </div>

        <el-table :data="historyList" border stripe>
          <el-table-column label="文件名" min-width="200">
            <template #default="{ row }">
              <span v-if="isValidFilename(row.filename)">{{ row.filename }}</span>
              <span v-else class="text-muted">
                <el-icon><WarningFilled /></el-icon>
                (文件名已损坏)
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="解析时间" width="180" />
          <el-table-column label="目录检测" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.has_toc ? 'success' : 'info'" size="small">
                {{ row.has_toc ? `✓ (${row.toc_items_count})` : '✗' }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 各方法准确率 -->
          <el-table-column label="精确匹配" width="110" align="center">
            <template #default="{ row }">
              <div v-if="row.toc_exact_f1" :class="getScoreClass(row.toc_exact_f1)">
                {{ (row.toc_exact_f1 * 100).toFixed(1) }}%
              </div>
              <div v-else-if="row.toc_exact_chapters_count > 0" class="chapter-count">
                {{ row.toc_exact_chapters_count }}章
              </div>
              <el-tag v-else-if="row.toc_exact_elapsed !== undefined && row.toc_exact_elapsed !== null" type="danger" size="small">失败</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Azure" width="110" align="center">
            <template #default="{ row }">
              <div v-if="row.azure_f1" :class="getScoreClass(row.azure_f1)">
                {{ (row.azure_f1 * 100).toFixed(1) }}%
              </div>
              <div v-else-if="row.azure_chapters_count > 0" class="chapter-count">
                {{ row.azure_chapters_count }}章
              </div>
              <el-tag v-else-if="row.azure_elapsed !== undefined && row.azure_elapsed !== null" type="danger" size="small">失败</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Word大纲" width="110" align="center">
            <template #default="{ row }">
              <div v-if="row.docx_native_f1" :class="getScoreClass(row.docx_native_f1)">
                {{ (row.docx_native_f1 * 100).toFixed(1) }}%
              </div>
              <div v-else-if="row.docx_native_chapters_count > 0" class="chapter-count">
                {{ row.docx_native_chapters_count }}章
              </div>
              <el-tag v-else-if="row.docx_native_elapsed !== undefined && row.docx_native_elapsed !== null" type="danger" size="small">失败</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Gemini AI" width="110" align="center">
            <template #default="{ row }">
              <div v-if="row.gemini_f1" :class="getScoreClass(row.gemini_f1)">
                {{ (row.gemini_f1 * 100).toFixed(1) }}%
              </div>
              <div v-else-if="row.gemini_chapters_count > 0" class="chapter-count">
                {{ row.gemini_chapters_count }}章
              </div>
              <el-tag v-else-if="row.gemini_elapsed !== undefined && row.gemini_elapsed !== null" type="danger" size="small">失败</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="LLM层级" width="110" align="center">
            <template #default="{ row }">
              <div v-if="row.llm_level_f1" :class="getScoreClass(row.llm_level_f1)">
                {{ (row.llm_level_f1 * 100).toFixed(1) }}%
              </div>
              <div v-else-if="row.llm_level_chapters_count > 0" class="chapter-count">
                {{ row.llm_level_chapters_count }}章
              </div>
              <el-tag v-else-if="row.llm_level_elapsed !== undefined && row.llm_level_elapsed !== null" type="danger" size="small">失败</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="最佳方法" width="150" align="center">
            <template #default="{ row }">
              <div v-if="row.best_method">
                <el-tag :type="row.best_f1_score >= 0.9 ? 'success' : 'primary'" effect="dark">
                  {{ getMethodDisplayName(row.best_method) }}
                </el-tag>
                <div style="font-size: 12px; margin-top: 4px; color: #606266;">
                  F1: {{ (row.best_f1_score * 100).toFixed(1) }}%
                </div>
              </div>
              <span v-else class="text-muted">未标注</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="loadTest(row.document_id)">
                查看
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteTest(row.document_id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="historyList.length === 0" class="empty-state">
          <el-empty description="暂无历史解析记录" />
        </div>
      </div>
    </Card>

    <!-- 文档预览对话框 -->
    <DocumentPreview
      v-model="previewDialogVisible"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, UploadUserFile, ElIcon } from 'element-plus'
import { Upload, WarningFilled, View } from '@element-plus/icons-vue'
import { Card, DocumentPreview } from '@/components'
import { parserDebugApi, type ParseTestResult, type ChapterNode, type HistoryTest } from '@/api/parser-debug'
import MethodCard from './components/MethodCard.vue'
import GroundTruthCard from './components/GroundTruthCard.vue'

// 状态
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const parsing = ref(false)
const smartParsing = ref(false)
const previewDialogVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

const currentDocumentId = ref('')
const documentInfo = ref<ParseTestResult['document_info'] | null>(null)
const results = ref<ParseTestResult['results'] | null>(null)
const groundTruth = ref<ChapterNode[] | null>(null)
const accuracy = ref<ParseTestResult['accuracy'] | null>(null)
const smartResult = ref<any>(null)

const historyDialogVisible = ref(false)
const historyList = ref<HistoryTest[]>([])

// 各方法的状态
const methodStatus = ref<Record<string, 'idle' | 'parsing' | 'success' | 'error'>>({
  gemini: 'idle',
  docx_native: 'idle',
  toc_exact: 'idle',
  azure: 'idle',
  llm_level: 'idle'
})

// 文件选择
const handleFileSelect = (uploadFile: any) => {
  selectedFile.value = uploadFile.raw
}

// 开始解析(仅上传文件，不自动开始解析)
const startParsing = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  parsing.value = true

  try {
    console.log('开始上传文件:', selectedFile.value.name)

    // 上传文件获取document_id
    const uploadResp = await parserDebugApi.uploadDocument(selectedFile.value)
    const data = uploadResp.data || uploadResp

    if (!data || !data.success) {
      ElMessage.error(data?.error || '文件上传失败')
      parsing.value = false
      return
    }

    currentDocumentId.value = data.document_id
    documentInfo.value = data.document_info

    // 初始化results对象为空结果(包含5种有效方法)
    results.value = {
      toc_exact: { success: false, chapters: [], method_name: '精确匹配(基于目录)', performance: { elapsed: 0, elapsed_formatted: '-' } },
      azure: { success: false, chapters: [], method_name: 'Azure Form Recognizer', performance: { elapsed: 0, elapsed_formatted: '-' } },
      docx_native: { success: false, chapters: [], method_name: 'Word大纲级别识别', performance: { elapsed: 0, elapsed_formatted: '-' } },
      gemini: { success: false, chapters: [], method_name: 'Gemini AI解析器', performance: { elapsed: 0, elapsed_formatted: '-' } },
      llm_level: { success: false, chapters: [], method_name: 'LLM智能层级分析', performance: { elapsed: 0, elapsed_formatted: '-' } }
    }

    // 重置所有方法状态为idle
    methodStatus.value = {
      gemini: 'idle',
      docx_native: 'idle',
      toc_exact: 'idle',
      azure: 'idle',
      llm_level: 'idle'
    }

    // 清空人工标注
    groundTruth.value = null
    accuracy.value = null

    ElMessage.success(`文件上传成功！请点击各方法的"开始解析"按钮`)
    parsing.value = false

  } catch (error: any) {
    console.error('上传异常:', error)
    ElMessage.error(error.response?.data?.error || error.message || '上传失败')
    parsing.value = false
  }
}

// 智能解析
const startSmartParsing = async () => {
  if (!currentDocumentId.value) {
    ElMessage.error('请先上传文件')
    return
  }

  smartParsing.value = true
  smartResult.value = null

  try {
    console.log('开始智能解析:', currentDocumentId.value)

    const response = await parserDebugApi.parseSmart(currentDocumentId.value, { classify: true })
    const data = response.data || response

    if (data.success && data.result) {
      smartResult.value = data.result
      ElMessage.success(`智能解析完成！使用方法: ${data.result.method_used}`)
    } else {
      ElMessage.error(`智能解析失败: ${data.error || '未知错误'}`)
    }
  } catch (error: any) {
    console.error('智能解析失败:', error)
    ElMessage.error(error.response?.data?.error || error.message || '智能解析失败')
  } finally {
    smartParsing.value = false
  }
}

// 预览文档
const previewDocument = async () => {
  if (!currentDocumentId.value) {
    ElMessage.error('请先上传文件')
    return
  }

  try {
    // 获取文档的文件路径
    const response = await parserDebugApi.getPreviewInfo(currentDocumentId.value)
    const data = response.data || response

    if (data.success) {
      // 使用 DocumentPreview 组件预览
      previewFileUrl.value = data.file_path
      previewFileName.value = data.filename || documentInfo.value?.filename || '文档预览'
      previewDialogVisible.value = true
    } else {
      ElMessage.error(data.error || '获取文档信息失败')
    }
  } catch (error: any) {
    console.error('获取文档预览信息失败:', error)
    ElMessage.error(error.response?.data?.error || error.message || '获取文档预览信息失败')
  }
}

// 智能解析结果转换为树形结构
const smartChapterTree = computed(() => {
  if (!smartResult.value?.chapters) return []

  const buildTree = (chapters: any[]): any[] => {
    return chapters.map(ch => ({
      ...ch,
      label: ch.title,
      children: ch.children ? buildTree(ch.children) : []
    }))
  }

  return buildTree(smartResult.value.chapters)
})

// 获取章节类型标签样式
const getChapterTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    invitation: 'info',
    bidder_notice: 'info',
    evaluation: '',
    contract_terms: '',
    contract_content: 'warning',
    business_response: 'primary',
    technical_spec: 'success',
    appendix: 'info',
    other: 'info'
  }
  return typeMap[type] || 'info'
}

// 获取章节类型中文名
const getChapterTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    invitation: '投标邀请',
    bidder_notice: '投标人须知',
    evaluation: '评标办法',
    contract_terms: '合同条款',
    contract_content: '合同内容',
    business_response: '商务应答',
    technical_spec: '技术规范',
    appendix: '附件',
    other: '其他'
  }
  return nameMap[type] || type
}

// 解析单个方法
const startSingleMethod = async (method: 'toc_exact' | 'azure' | 'docx_native' | 'gemini' | 'llm_level') => {
  if (!currentDocumentId.value) {
    ElMessage.error('请先上传文件')
    return
  }

  // 设置状态为解析中
  methodStatus.value[method] = 'parsing'

  try {
    console.log(`开始解析方法: ${method}`)

    const response = await parserDebugApi.parseSingleMethod(currentDocumentId.value, method)
    const data = response.data || response

    if (data.success && data.result) {
      // 更新结果
      if (results.value) {
        results.value[method] = data.result
      }

      // 设置状态
      methodStatus.value[method] = data.result.success ? 'success' : 'error'

      if (data.result.success) {
        ElMessage.success(`${data.result.method_name} 解析完成！`)
      } else {
        ElMessage.error(`${data.result.method_name} 解析失败: ${data.result.error || '未知错误'}`)
      }

      // 刷新历史记录列表
      loadHistoryList()
    } else {
      methodStatus.value[method] = 'error'
      ElMessage.error(`解析失败: ${data.error || '未知错误'}`)
    }

  } catch (error: any) {
    console.error(`解析方法 ${method} 失败:`, error)
    methodStatus.value[method] = 'error'
    ElMessage.error(error.response?.data?.error || error.message || '解析失败')
  }
}

// 保存人工标注
const handleSaveGroundTruth = async (chapters: ChapterNode[]) => {
  if (!currentDocumentId.value) {
    ElMessage.error('没有当前文档')
    return
  }

  try {
    const response = await parserDebugApi.saveGroundTruth(
      currentDocumentId.value,
      chapters,
      'user'
    )

    if (response.success) {
      accuracy.value = response.accuracy
      ElMessage.success('标注已保存，准确率已计算')
    }
  } catch (error: any) {
    console.error('保存标注失败:', error)
    ElMessage.error('保存失败')
  }
}

// 加载历史记录列表
const loadHistoryList = async () => {
  try {
    const response = await parserDebugApi.getHistory({ limit: 50 })
    historyList.value = response.tests
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
  }
}

// 显示历史记录（保留旧函数以兼容）
const showHistory = async () => {
  await loadHistoryList()
  historyDialogVisible.value = true
}

// 加载历史测试
const loadTest = async (documentId: string) => {
  try {
    const response = await parserDebugApi.getTestResult(documentId)

    if (response.success) {
      currentDocumentId.value = response.document_id
      documentInfo.value = response.document_info
      results.value = response.results
      groundTruth.value = response.ground_truth || null
      accuracy.value = response.accuracy || null

      // 根据结果设置各方法的状态
      methodStatus.value = {
        gemini: results.value?.gemini?.success ? 'success' : (results.value?.gemini ? 'error' : 'idle'),
        docx_native: results.value?.docx_native?.success ? 'success' : (results.value?.docx_native ? 'error' : 'idle'),
        toc_exact: results.value?.toc_exact?.success ? 'success' : (results.value?.toc_exact ? 'error' : 'idle'),
        azure: results.value?.azure?.success ? 'success' : (results.value?.azure ? 'error' : 'idle'),
        llm_level: results.value?.llm_level?.success ? 'success' : (results.value?.llm_level ? 'error' : 'idle')
      }

      historyDialogVisible.value = false
      ElMessage.success('测试结果已加载')
    }
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

// 删除测试
const handleDeleteTest = async (documentId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这条测试记录吗？', '确认删除', {
      type: 'warning'
    })

    await parserDebugApi.deleteTest(documentId)
    ElMessage.success('已删除')

    // 刷新列表
    showHistory()
  } catch (error) {
    // 用户取消或删除失败
  }
}

// 准确率表格数据
const accuracyTableData = computed(() => {
  if (!accuracy.value || !results.value) return []

  const methods = [
    { key: 'gemini', name: 'Gemini AI解析器' },
    { key: 'docx_native', name: 'Word大纲级别识别' },
    { key: 'toc_exact', name: '精确匹配(基于目录)' },
    { key: 'azure', name: 'Azure Form Recognizer' },
    { key: 'llm_level', name: 'LLM智能层级分析' }
  ]

  return methods
    .filter(({ key }) => results.value![key]) // 过滤不存在的方法
    .map(({ key, name }) => ({
      method: name,
      precision: accuracy.value![key]?.precision || 0,
      recall: accuracy.value![key]?.recall || 0,
      f1: accuracy.value![key]?.f1_score || 0,
      detected: results.value![key]?.chapters?.length || 0,
      elapsed: results.value![key]?.performance?.elapsed_formatted || '-',
      is_best: accuracy.value!.best_method === key
    }))
})

// 辅助函数
const getScoreClass = (score: number) => {
  if (score >= 0.9) return 'score-excellent'
  if (score >= 0.7) return 'score-good'
  if (score >= 0.5) return 'score-fair'
  return 'score-poor'
}

const getF1TagType = (f1: number) => {
  if (f1 >= 0.9) return 'success'
  if (f1 >= 0.7) return ''
  if (f1 >= 0.5) return 'warning'
  return 'danger'
}

const getBestMethodName = () => {
  const names = {
    toc_exact: '精确匹配(基于目录)',
    azure: 'Azure Form Recognizer',
    docx_native: 'Word大纲级别识别',
    gemini: 'Gemini AI解析器',
    llm_level: 'LLM智能层级分析'
  }
  return names[accuracy.value?.best_method] || '未知'
}

const getMethodDisplayName = (key: string) => {
  const names = {
    toc_exact: '精确匹配',
    azure: 'Azure',
    docx_native: 'Word大纲',
    gemini: 'Gemini AI',
    llm_level: 'LLM层级'
  }
  return names[key] || key
}

// 检查文件名是否有效（不是损坏的文件名）
const isValidFilename = (filename: string) => {
  // 如果文件名只是扩展名或者过短，认为是损坏的
  if (!filename || filename.length < 3) return false
  if (filename === 'docx' || filename === '.docx') return false
  if (filename.startsWith('-.') || filename.startsWith('--')) return false
  return true
}

// 页面加载时自动加载历史记录
onMounted(async () => {
  await loadHistoryList()
})
</script>

<style scoped lang="scss">
.parser-comparison {
  padding: 20px;
}

.upload-section {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;

  .selected-file {
    color: #606266;
    font-size: 14px;
  }
}

.doc-info {
  margin-bottom: 20px;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.accuracy-section {
  margin-top: 30px;

  h3 {
    margin-bottom: 16px;
    font-size: 18px;
    font-weight: 600;
  }

  .best-method-summary {
    margin-top: 16px;
  }
}

.score-excellent {
  color: #67C23A;
  font-weight: bold;
}

.score-good {
  color: #409EFF;
}

.score-fair {
  color: #E6A23C;
}

.score-poor {
  color: #F56C6C;
}

.method-counts {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;

  span {
    color: #606266;
  }
}

.text-muted {
  color: #909399;
}

.chapter-count {
  color: #606266;
  font-size: 13px;
}

.history-section {
  margin-top: 40px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .empty-state {
    padding: 40px;
    text-align: center;
  }
}

/* 智能识别结果区域 */
.smart-result-section {
  margin-bottom: 20px;

  .smart-result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 16px;
      font-weight: 600;
    }

    .method-info {
      display: flex;
      gap: 8px;
      align-items: center;

      .elapsed {
        color: #909399;
        font-size: 13px;
        margin-left: 8px;
      }
    }
  }

  .key-sections {
    margin-bottom: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;

    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      color: #606266;
    }

    .section-tags {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .section-item {
        display: flex;
        align-items: center;
        gap: 12px;

        .section-title {
          color: #303133;
          font-size: 14px;
        }
      }
    }
  }

  .chapters-tree {
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      color: #606266;
    }

    .chapter-node {
      display: flex;
      align-items: center;
      gap: 8px;

      .chapter-title {
        font-size: 14px;
      }
    }
  }
}
</style>
