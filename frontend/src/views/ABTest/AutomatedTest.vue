<template>
  <div class="automated-test">
    <Card title="🧪 自动化测试运行器">
      <template #extra>
        <el-button @click="loadQuickInfo" :icon="RefreshIcon" circle size="small" title="刷新"></el-button>
      </template>

      <!-- 快速信息卡片 -->
      <div class="quick-info-grid">
        <el-card class="info-card" shadow="hover">
          <div class="info-content">
            <i class="bi-list-check info-icon"></i>
            <div class="info-text">
              <div class="info-label">总测试数</div>
              <div class="info-value">{{ quickInfo?.total_tests || 0 }}</div>
            </div>
          </div>
        </el-card>

        <el-card class="info-card" shadow="hover">
          <div class="info-content">
            <i class="bi-file-earmark-code info-icon"></i>
            <div class="info-text">
              <div class="info-label">测试文件</div>
              <div class="info-value">{{ quickInfo?.test_files || 0 }}</div>
            </div>
          </div>
        </el-card>

        <el-card class="info-card" shadow="hover">
          <div class="info-content">
            <i class="bi-pie-chart info-icon"></i>
            <div class="info-text">
              <div class="info-label">测试覆盖率</div>
              <div class="info-value" :class="getCoverageClass(quickInfo?.coverage_percent || 0)">
                {{ (quickInfo?.coverage_percent || 0).toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="info-card" shadow="hover">
          <div class="info-content">
            <i class="bi-clock-history info-icon"></i>
            <div class="info-text">
              <div class="info-label">最后运行</div>
              <div class="info-value small">{{ quickInfo?.last_run || '未运行' }}</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 测试运行控制面板 -->
      <div class="control-panel">
        <el-card shadow="never">
          <template #header>
            <span>运行测试</span>
          </template>

          <div class="run-options">
            <el-radio-group v-model="testType" :disabled="isRunning">
              <el-radio-button value="unit">单元测试</el-radio-button>
              <el-radio-button value="integration">集成测试</el-radio-button>
              <el-radio-button value="all">全部测试</el-radio-button>
            </el-radio-group>

            <el-checkbox v-model="enableCoverage" :disabled="isRunning">
              生成覆盖率报告
            </el-checkbox>

            <el-button
              type="primary"
              :icon="isRunning ? LoadingIcon : PlayIcon"
              :loading="isRunning"
              @click="startTest"
              size="large"
            >
              {{ isRunning ? '测试运行中...' : '开始测试' }}
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 测试结果统计 -->
      <div v-if="currentTask?.result" class="results-panel">
        <el-card shadow="never" class="stats-card">
          <template #header>
            <div class="stats-header">
              <span>测试结果</span>
              <el-tag :type="currentTask.result.passed ? 'success' : 'danger'" effect="dark">
                {{ currentTask.result.passed ? '✅ 通过' : '❌ 失败' }}
              </el-tag>
            </div>
          </template>

          <div class="test-stats">
            <div class="stat-item success">
              <i class="bi-check-circle"></i>
              <div class="stat-content">
                <div class="stat-label">通过</div>
                <div class="stat-value">{{ currentTask.result.passed }}</div>
              </div>
            </div>

            <div class="stat-item danger">
              <i class="bi-x-circle"></i>
              <div class="stat-content">
                <div class="stat-label">失败</div>
                <div class="stat-value">{{ currentTask.result.failed }}</div>
              </div>
            </div>

            <div class="stat-item warning">
              <i class="bi-skip-forward-circle"></i>
              <div class="stat-content">
                <div class="stat-label">跳过</div>
                <div class="stat-value">{{ currentTask.result.skipped }}</div>
              </div>
            </div>

            <div class="stat-item info">
              <i class="bi-exclamation-circle"></i>
              <div class="stat-content">
                <div class="stat-label">错误</div>
                <div class="stat-value">{{ currentTask.result.errors }}</div>
              </div>
            </div>

            <div class="stat-item">
              <i class="bi-stopwatch"></i>
              <div class="stat-content">
                <div class="stat-label">耗时</div>
                <div class="stat-value">{{ currentTask.result.duration?.toFixed(2) }}s</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 覆盖率报告 -->
      <div v-if="coverageData" class="coverage-section">
        <el-card shadow="never">
          <template #header>
            <div class="coverage-header">
              <span>测试覆盖率</span>
              <el-progress
                :percentage="coverageData.coverage_percent"
                :color="getCoverageColor(coverageData.coverage_percent)"
                :stroke-width="20"
                text-inside
              />
            </div>
          </template>

          <div class="coverage-summary">
            <div class="summary-item">
              <span class="summary-label">总代码行数:</span>
              <span class="summary-value">{{ coverageData.total_statements }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">已覆盖:</span>
              <span class="summary-value success">{{ coverageData.covered_statements }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">未覆盖:</span>
              <span class="summary-value danger">{{ coverageData.missing_statements }}</span>
            </div>
          </div>

          <!-- 文件覆盖率表格 -->
          <el-table :data="paginatedCoverageFiles" border stripe max-height="400">
            <el-table-column prop="file" label="文件" min-width="300" show-overflow-tooltip />
            <el-table-column prop="statements" label="总行数" width="100" align="center" />
            <el-table-column prop="covered" label="已覆盖" width="100" align="center" />
            <el-table-column prop="missing" label="未覆盖" width="100" align="center" />
            <el-table-column label="覆盖率" width="150" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.coverage"
                  :color="getCoverageColor(row.coverage)"
                  :stroke-width="6"
                  :show-text="false"
                />
                <span :class="getCoverageClass(row.coverage)" style="margin-left: 8px;">
                  {{ row.coverage.toFixed(1) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="coverageData.files.length"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>

      <!-- 测试历史 -->
      <div class="history-section">
        <el-card shadow="never">
          <template #header>
            <div class="history-header">
              <span>测试历史</span>
              <div class="header-actions">
                <el-button size="small" @click="loadHistory">刷新</el-button>
                <el-button size="small" type="danger" @click="clearHistory">清除</el-button>
              </div>
            </div>
          </template>

          <el-table :data="historyList" border stripe>
            <el-table-column label="任务ID" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <el-text size="small" type="info">{{ row.task_id }}</el-text>
              </template>
            </el-table-column>

            <el-table-column prop="test_type" label="测试类型" width="120" align="center">
              <template #default="{ row }">
                <el-tag size="small" effect="plain">
                  {{ getTestTypeLabel(row.test_type) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="结果" width="200" align="center">
              <template #default="{ row }">
                <div v-if="row.result" class="result-summary">
                  <span class="result-item success">✓ {{ row.result.passed }}</span>
                  <span class="result-item danger">✗ {{ row.result.failed }}</span>
                  <span class="result-item warning">⊙ {{ row.result.skipped }}</span>
                </div>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>

            <el-table-column prop="created_time" label="创建时间" width="180" />

            <el-table-column label="耗时" width="100" align="center">
              <template #default="{ row }">
                <span v-if="row.result">{{ row.result.duration?.toFixed(2) }}s</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="120" fixed="right" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="viewTaskDetail(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="historyList.length === 0" class="empty-state">
            <el-empty description="暂无测试历史" />
          </div>
        </el-card>
      </div>

      <!-- 测试日志（页面底部） -->
      <div v-if="currentTask" class="logs-section">
        <el-card shadow="never" class="logs-card">
          <template #header>
            <div class="logs-header">
              <span>📝 测试日志</span>
              <div class="header-actions">
                <el-tag v-if="isRunning" type="info" effect="plain">
                  <i class="bi-arrow-clockwise rotating"></i>
                  运行中...
                </el-tag>
                <el-button size="small" @click="copyLogs">复制日志</el-button>
              </div>
            </div>
          </template>

          <div class="logs-container" ref="logsContainer">
            <pre v-if="currentTask.logs && currentTask.logs.length > 0" class="logs-content">{{ currentTask.logs.join('\n') }}</pre>
            <div v-else class="empty-logs">
              <i class="bi-terminal"></i>
              <p>等待测试开始...</p>
            </div>
          </div>
        </el-card>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh as RefreshIcon, VideoPlay as PlayIcon, Loading as LoadingIcon } from '@element-plus/icons-vue'
import { Card } from '@/components'
import { testRunnerApi, type TestTask, type CoverageData, type QuickInfo } from '@/api/test-runner'

// ==================== State ====================

const quickInfo = ref<QuickInfo | null>(null)
const testType = ref<'unit' | 'integration' | 'all'>('unit')
const enableCoverage = ref(true)

const isRunning = ref(false)
const currentTask = ref<TestTask | null>(null)
const currentTaskId = ref<string | null>(null)
const pollingTimer = ref<number | null>(null)

const coverageData = ref<CoverageData | null>(null)
const historyList = ref<TestTask[]>([])

const logsContainer = ref<HTMLElement | null>(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// ==================== Computed ====================

const paginatedCoverageFiles = computed(() => {
  if (!coverageData.value) return []
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return coverageData.value.files.slice(start, end)
})

// ==================== Methods ====================

/**
 * 加载快速信息
 */
const loadQuickInfo = async () => {
  try {
    const response = await testRunnerApi.getQuickInfo()
    if (response.success) {
      quickInfo.value = response.info
    }
  } catch (error) {
    console.error('加载快速信息失败:', error)
  }
}

/**
 * 开始测试
 */
const startTest = async () => {
  if (isRunning.value) return

  try {
    // 运行测试
    const response = await testRunnerApi.runTests(testType.value, enableCoverage.value, true)

    if (response.success) {
      currentTaskId.value = response.task_id
      isRunning.value = true

      ElMessage.success('测试已开始运行')

      // 开始轮询获取状态
      startPolling()
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '启动测试失败')
  }
}

/**
 * 开始轮询任务状态
 */
const startPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
  }

  pollingTimer.value = window.setInterval(async () => {
    if (!currentTaskId.value) return

    try {
      const response = await testRunnerApi.getTestStatus(currentTaskId.value)

      if (response.success) {
        currentTask.value = response.task

        // 自动滚动日志到底部
        await nextTick()
        if (logsContainer.value) {
          logsContainer.value.scrollTop = logsContainer.value.scrollHeight
        }

        // 如果任务完成，停止轮询
        if (currentTask.value.status === 'completed' || currentTask.value.status === 'failed') {
          stopPolling()
          isRunning.value = false

          // 加载覆盖率数据
          if (enableCoverage.value && currentTask.value.status === 'completed') {
            await loadCoverageData()
          }

          // 刷新快速信息和历史
          await loadQuickInfo()
          await loadHistory()

          // 显示完成消息
          if (currentTask.value.status === 'completed') {
            ElMessage.success('测试运行完成')
          } else {
            ElMessage.error('测试运行失败')
          }
        }
      }
    } catch (error) {
      console.error('获取任务状态失败:', error)
    }
  }, 1000) // 每秒轮询一次
}

/**
 * 停止轮询
 */
const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

/**
 * 加载覆盖率数据
 */
const loadCoverageData = async () => {
  try {
    const response = await testRunnerApi.getCoverageData()
    if (response.success) {
      coverageData.value = response.coverage
    }
  } catch (error: any) {
    // 覆盖率数据可能不存在，不显示错误
    console.log('覆盖率数据不可用:', error.response?.data?.error)
  }
}

/**
 * 加载测试历史
 */
const loadHistory = async () => {
  try {
    const response = await testRunnerApi.getTestHistory(20)
    if (response.success) {
      historyList.value = response.history
    }
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

/**
 * 清除历史
 */
const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清除所有测试历史记录吗？', '确认清除', {
      type: 'warning'
    })

    await testRunnerApi.clearHistory()
    historyList.value = []
    ElMessage.success('历史记录已清除')
  } catch (error) {
    // 用户取消或清除失败
  }
}

/**
 * 查看任务详情
 */
const viewTaskDetail = (task: TestTask) => {
  currentTask.value = task
  ElMessage.info('已加载测试详情')
}

/**
 * 复制日志
 */
const copyLogs = () => {
  if (!currentTask.value?.logs) return

  const text = currentTask.value.logs.join('\n')
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('日志已复制到剪贴板')
  })
}

/**
 * 获取覆盖率颜色类
 */
const getCoverageClass = (percent: number) => {
  if (percent >= 80) return 'coverage-excellent'
  if (percent >= 50) return 'coverage-good'
  if (percent >= 30) return 'coverage-fair'
  return 'coverage-poor'
}

/**
 * 获取覆盖率进度条颜色
 */
const getCoverageColor = (percent: number) => {
  if (percent >= 80) return '#67C23A'
  if (percent >= 50) return '#409EFF'
  if (percent >= 30) return '#E6A23C'
  return '#F56C6C'
}

/**
 * 获取测试类型标签
 */
const getTestTypeLabel = (type: string) => {
  const labels = {
    unit: '单元测试',
    integration: '集成测试',
    all: '全部测试'
  }
  return labels[type] || type
}

/**
 * 获取状态类型
 */
const getStatusType = (status: string) => {
  const types = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

/**
 * 获取状态标签
 */
const getStatusLabel = (status: string) => {
  const labels = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

/**
 * 分页处理
 */
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// ==================== Lifecycle ====================

onMounted(async () => {
  await loadQuickInfo()
  await loadHistory()
  await loadCoverageData()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.automated-test {
  padding: 20px;
}

// ==================== 快速信息卡片 ====================

.quick-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.info-card {
  .info-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .info-icon {
    font-size: 36px;
    color: var(--el-color-primary);
    opacity: 0.8;
  }

  .info-text {
    flex: 1;
  }

  .info-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    margin-bottom: 4px;
  }

  .info-value {
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);

    &.small {
      font-size: 14px;
    }

    &.coverage-excellent {
      color: #67C23A;
    }

    &.coverage-good {
      color: #409EFF;
    }

    &.coverage-fair {
      color: #E6A23C;
    }

    &.coverage-poor {
      color: #F56C6C;
    }
  }
}

// ==================== 控制面板 ====================

.control-panel {
  margin-bottom: 24px;

  .run-options {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }
}

// ==================== 结果统计面板 ====================

.results-panel {
  margin-bottom: 24px;
}

.stats-card {
  .stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .test-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }

  .stat-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    background: var(--el-fill-color-lighter);

    i {
      font-size: 28px;
    }

    &.success i {
      color: #67C23A;
    }

    &.danger i {
      color: #F56C6C;
    }

    &.warning i {
      color: #E6A23C;
    }

    &.info i {
      color: #909399;
    }

    .stat-content {
      flex: 1;
    }

    .stat-label {
      font-size: 13px;
      color: var(--el-text-color-secondary);
    }

    .stat-value {
      font-size: 20px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }
}

// ==================== 覆盖率部分 ====================

.coverage-section {
  margin-bottom: 24px;

  .coverage-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
  }

  .coverage-summary {
    display: flex;
    gap: 32px;
    margin-bottom: 20px;
    padding: 16px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;

    .summary-item {
      display: flex;
      gap: 8px;
      align-items: center;

      .summary-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }

      .summary-value {
        font-size: 18px;
        font-weight: 600;

        &.success {
          color: #67C23A;
        }

        &.danger {
          color: #F56C6C;
        }
      }
    }
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}

// ==================== 历史部分 ====================

.history-section {
  margin-bottom: 24px;

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .result-summary {
    display: flex;
    gap: 12px;
    font-size: 13px;

    .result-item {
      &.success {
        color: #67C23A;
      }

      &.danger {
        color: #F56C6C;
      }

      &.warning {
        color: #E6A23C;
      }
    }
  }

  .empty-state {
    padding: 40px;
    text-align: center;
  }
}

// ==================== 日志部分（页面底部） ====================

.logs-section {
  margin-top: 24px;
}

.logs-card {
  .logs-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .logs-container {
    height: 500px;
    overflow-y: auto;
    background: #1e1e1e;
    border-radius: 4px;
    padding: 16px;

    .logs-content {
      margin: 0;
      font-family: 'Courier New', Consolas, monospace;
      font-size: 12px;
      line-height: 1.5;
      color: #d4d4d4;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .empty-logs {
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #606266;

      i {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
      }

      p {
        margin: 0;
        font-size: 14px;
      }
    }
  }
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.text-muted {
  color: #909399;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .quick-info-grid {
    grid-template-columns: 1fr;
  }

  .test-stats {
    grid-template-columns: 1fr;
  }

  .coverage-summary {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
