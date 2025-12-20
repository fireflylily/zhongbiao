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
        <!-- 方法1: 语义锚点 -->
        <MethodCard
          title="方法1: 语义锚点解析"
          :result="results.semantic"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.semantic"
          color="#67C23A"
        />

        <!-- 方法2: 样式识别 -->
        <MethodCard
          title="方法2: 样式识别(增强)"
          :result="results.style"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.style"
          color="#409EFF"
        />

        <!-- 方法3: 混合启发式 -->
        <MethodCard
          title="方法3: 混合启发式识别"
          :result="results.hybrid"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.hybrid"
          color="#E6A23C"
        />

        <!-- 方法4: Azure Form Recognizer -->
        <MethodCard
          v-if="results.azure"
          title="方法4: Azure Form Recognizer"
          :result="results.azure"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.azure"
          color="#00B7C3"
        />

        <!-- 方法5: Word大纲级别识别 -->
        <MethodCard
          v-if="results.docx_native"
          title="方法5: Word大纲级别识别"
          :result="results.docx_native"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.docx_native"
          color="#9C27B0"
        />

        <!-- 方法6: Gemini AI解析器 -->
        <MethodCard
          v-if="results.gemini"
          title="方法6: Gemini AI解析器"
          :result="results.gemini"
          :ground-truth="groundTruth"
          :accuracy="accuracy?.gemini"
          color="#FF6D00"
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
          <el-table-column label="语义锚点" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.semantic_f1" :class="getScoreClass(row.semantic_f1)">
                {{ (row.semantic_f1 * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="样式识别" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.style_f1" :class="getScoreClass(row.style_f1)">
                {{ (row.style_f1 * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="混合启发式" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.hybrid_f1" :class="getScoreClass(row.hybrid_f1)">
                {{ (row.hybrid_f1 * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Azure" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.azure_f1" :class="getScoreClass(row.azure_f1)">
                {{ (row.azure_f1 * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Word大纲" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.docx_native_f1" :class="getScoreClass(row.docx_native_f1)">
                {{ (row.docx_native_f1 * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Gemini AI" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.gemini_f1" :class="getScoreClass(row.gemini_f1)">
                {{ (row.gemini_f1 * 100).toFixed(1) }}%
              </span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, UploadUserFile, ElIcon } from 'element-plus'
import { Upload, WarningFilled } from '@element-plus/icons-vue'
import { Card } from '@/components'
import { parserDebugApi, type ParseTestResult, type ChapterNode, type HistoryTest } from '@/api/parser-debug'
import MethodCard from './components/MethodCard.vue'
import GroundTruthCard from './components/GroundTruthCard.vue'

// 状态
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const parsing = ref(false)

const currentDocumentId = ref('')
const documentInfo = ref<ParseTestResult['document_info'] | null>(null)
const results = ref<ParseTestResult['results'] | null>(null)
const groundTruth = ref<ChapterNode[] | null>(null)
const accuracy = ref<ParseTestResult['accuracy'] | null>(null)

const historyDialogVisible = ref(false)
const historyList = ref<HistoryTest[]>([])

// 文件选择
const handleFileSelect = (uploadFile: any) => {
  selectedFile.value = uploadFile.raw
}

// 开始解析
const startParsing = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  parsing.value = true
  try {
    console.log('开始上传文件:', selectedFile.value.name)
    const response = await parserDebugApi.uploadDocument(selectedFile.value)

    console.log('API响应:', response)

    // 兼容不同的响应格式
    const data = response.data || response

    if (data && data.success) {
      currentDocumentId.value = data.document_id
      documentInfo.value = data.document_info
      results.value = data.results
      groundTruth.value = data.ground_truth || null
      accuracy.value = data.accuracy || null

      ElMessage.success('解析完成！')
    } else {
      console.error('解析失败，响应数据:', data)
      ElMessage.error(data?.error || '解析失败')
    }
  } catch (error: any) {
    console.error('解析异常:', error)
    console.error('错误详情:', error.response)
    ElMessage.error(error.response?.data?.error || error.message || '解析失败')
  } finally {
    parsing.value = false
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
    { key: 'semantic', name: '语义锚点解析' },
    { key: 'style', name: '样式识别(增强)' },
    { key: 'hybrid', name: '混合启发式识别' },
    { key: 'azure', name: 'Azure Form Recognizer' },
    { key: 'docx_native', name: 'Word大纲级别识别' },
    { key: 'gemini', name: 'Gemini AI解析器' }
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
    semantic: '语义锚点解析',
    style: '样式识别(增强)',
    hybrid: '混合启发式识别',
    azure: 'Azure Form Recognizer',
    docx_native: 'Word大纲级别识别',
    gemini: 'Gemini AI解析器'
  }
  return names[accuracy.value?.best_method] || '未知'
}

const getMethodDisplayName = (key: string) => {
  const names = {
    semantic: '语义锚点',
    style: '样式',
    hybrid: '混合启发式',
    azure: 'Azure',
    docx_native: 'Word大纲',
    gemini: 'Gemini AI'
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
</style>
