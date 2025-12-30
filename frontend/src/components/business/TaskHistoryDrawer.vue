<template>
  <el-drawer
    v-model="visible"
    title="任务历史"
    direction="rtl"
    size="450px"
    :before-close="handleClose"
  >
    <template #header>
      <div class="drawer-header">
        <span class="title">任务历史</span>
        <el-button text @click="loadTasks">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>

    <div class="task-list" v-loading="loading">
      <!-- 空状态 -->
      <el-empty v-if="!loading && tasks.length === 0" description="暂无任务记录" />

      <!-- 任务列表 -->
      <div v-else class="task-items">
        <div
          v-for="task in tasks"
          :key="task.task_id"
          class="task-item"
          :class="{ 'is-failed': task.overall_status === 'failed' }"
        >
          <!-- 任务头部 -->
          <div class="task-header">
            <div class="task-id">
              <el-icon><Document /></el-icon>
              <span>{{ task.task_id }}</span>
            </div>
            <el-tag :type="getStatusType(task.overall_status)" size="small">
              {{ getStatusLabel(task.overall_status) }}
            </el-tag>
          </div>

          <!-- 进度条 -->
          <el-progress
            :percentage="task.progress_percentage"
            :status="getProgressStatus(task.overall_status)"
            :stroke-width="6"
            class="task-progress"
          />

          <!-- 任务信息 -->
          <div class="task-info">
            <div class="info-row">
              <span class="label">当前阶段:</span>
              <span class="value">{{ getPhaseLabel(task.current_phase) || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">创建时间:</span>
              <span class="value">{{ formatTime(task.created_at) }}</span>
            </div>
            <div v-if="task.last_error" class="info-row error">
              <span class="label">错误信息:</span>
              <span class="value">{{ task.last_error }}</span>
            </div>
            <div v-if="task.overall_status === 'failed' && task.seconds_until_expire > 0" class="info-row">
              <span class="label">剩余恢复时间:</span>
              <span class="value time-warning">{{ formatRemainingTime(task.seconds_until_expire) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="task-actions">
            <el-button
              v-if="task.can_resume && task.overall_status === 'failed'"
              type="primary"
              size="small"
              @click="handleResume(task)"
              :loading="resumingTaskId === task.task_id"
            >
              <el-icon><VideoPlay /></el-icon>
              恢复执行
            </el-button>
            <el-button
              v-if="task.overall_status === 'running'"
              type="danger"
              size="small"
              plain
              @click="handleCancel(task)"
            >
              取消
            </el-button>
            <el-button
              size="small"
              text
              @click="handleViewDetail(task)"
            >
              详情
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="任务详情"
      width="600px"
      append-to-body
    >
      <div v-if="currentTaskDetail" class="task-detail">
        <!-- 基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentTaskDetail.task.task_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTaskDetail.task.overall_status)">
              {{ getStatusLabel(currentTaskDetail.task.overall_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">{{ currentTaskDetail.task.progress_percentage }}%</el-descriptions-item>
          <el-descriptions-item label="重试次数">{{ currentTaskDetail.task.retry_count }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentTaskDetail.task.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(currentTaskDetail.task.started_at) || '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 执行统计 -->
        <div v-if="currentTaskDetail.stats" class="stats-section">
          <h4>执行统计</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="stat-item success">
                <div class="stat-value">{{ currentTaskDetail.stats.successful_phases }}</div>
                <div class="stat-label">成功阶段</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item danger">
                <div class="stat-value">{{ currentTaskDetail.stats.failed_phases }}</div>
                <div class="stat-label">失败阶段</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item warning">
                <div class="stat-value">{{ currentTaskDetail.stats.total_retries }}</div>
                <div class="stat-label">总重试</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item info">
                <div class="stat-value">{{ formatDuration(currentTaskDetail.stats.total_duration_ms) }}</div>
                <div class="stat-label">总耗时</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 执行日志 -->
        <div v-if="currentTaskDetail.logs?.length" class="logs-section">
          <h4>执行日志</h4>
          <el-timeline>
            <el-timeline-item
              v-for="log in currentTaskDetail.logs"
              :key="log.log_id"
              :type="getLogType(log.status)"
              :timestamp="formatTime(log.created_at)"
              placement="top"
            >
              <div class="log-content">
                <div class="log-header">
                  <span class="agent-name">{{ log.agent_name }}</span>
                  <el-tag :type="getLogType(log.status)" size="small">{{ log.status }}</el-tag>
                </div>
                <div v-if="log.error_message" class="log-error">
                  {{ log.error_message }}
                </div>
                <div v-if="log.duration_ms" class="log-duration">
                  耗时: {{ formatDuration(log.duration_ms) }}
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Refresh, VideoPlay } from '@element-plus/icons-vue'
import { tenderApi, type TechProposalTask, type TaskExecutionLog, type TaskStats } from '@/api/endpoints/tender'

// Props
const props = defineProps<{
  modelValue: boolean
  projectId?: number
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'resume', task: TechProposalTask): void
}>()

// State
const visible = ref(props.modelValue)
const loading = ref(false)
const tasks = ref<TechProposalTask[]>([])
const resumingTaskId = ref<string | null>(null)
const detailVisible = ref(false)
const currentTaskDetail = ref<{
  task: TechProposalTask
  logs: TaskExecutionLog[]
  stats: TaskStats
} | null>(null)

// Watch modelValue
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadTasks()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载任务列表
async function loadTasks() {
  loading.value = true
  try {
    const response = await tenderApi.getTechProposalTasks(props.projectId)
    if (response.success) {
      tasks.value = response.tasks
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 恢复任务
async function handleResume(task: TechProposalTask) {
  try {
    await ElMessageBox.confirm(
      `确定要恢复任务 ${task.task_id} 吗？将从上次失败的阶段继续执行。`,
      '恢复任务',
      { type: 'info' }
    )

    resumingTaskId.value = task.task_id
    const response = await tenderApi.resumeTechProposalTask(task.task_id)

    if (response.success) {
      ElMessage.success('任务已准备恢复')
      emit('resume', task)
      visible.value = false
    } else {
      ElMessage.error(response.error || '恢复失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('恢复任务失败')
    }
  } finally {
    resumingTaskId.value = null
  }
}

// 取消任务
async function handleCancel(task: TechProposalTask) {
  try {
    await ElMessageBox.confirm(
      `确定要取消任务 ${task.task_id} 吗？`,
      '取消任务',
      { type: 'warning' }
    )

    const response = await tenderApi.cancelTechProposalTask(task.task_id)
    if (response.success) {
      ElMessage.success('任务已取消')
      loadTasks()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('取消任务失败')
    }
  }
}

// 查看详情
async function handleViewDetail(task: TechProposalTask) {
  try {
    const response = await tenderApi.getTechProposalTaskDetail(task.task_id)
    if (response.success) {
      currentTaskDetail.value = {
        task: response.task,
        logs: response.logs,
        stats: response.stats
      }
      detailVisible.value = true
    }
  } catch (error) {
    ElMessage.error('获取任务详情失败')
  }
}

// 关闭抽屉
function handleClose() {
  visible.value = false
}

// 工具函数
function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    running: 'warning',
    failed: 'danger',
    pending: 'info',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    completed: '已完成',
    running: '运行中',
    failed: '失败',
    pending: '待执行',
    cancelled: '已取消'
  }
  return map[status] || status
}

function getProgressStatus(status: string): 'success' | 'warning' | 'exception' | '' {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return ''
}

function getPhaseLabel(phase: string | null): string {
  if (!phase) return ''
  const map: Record<string, string> = {
    scoring_extraction: '评分点提取',
    product_matching: '产品匹配',
    strategy_planning: '评分策略',
    material_retrieval: '素材检索',
    outline_generation: '大纲生成',
    content_writing: '内容撰写',
    expert_review: '专家评审',
    iteration: '迭代优化'
  }
  return map[phase] || phase
}

function getLogType(status: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
    success: 'success',
    failed: 'danger',
    running: 'primary',
    retrying: 'warning',
    skipped: 'info'
  }
  return map[status] || 'info'
}

function formatTime(time: string | null): string {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

function formatRemainingTime(seconds: number): string {
  if (seconds <= 0) return '已过期'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

function formatDuration(ms: number | null): string {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}分${remainingSeconds}秒`
}
</script>

<style scoped lang="scss">
.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;

  .title {
    font-size: 16px;
    font-weight: 600;
  }
}

.task-list {
  padding: 0 4px;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }

  &.is-failed {
    border-color: var(--el-color-danger-light-5);
    background: var(--el-color-danger-light-9);
  }
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;

  .task-id {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: monospace;
    font-size: 14px;
    color: var(--el-text-color-primary);
  }
}

.task-progress {
  margin-bottom: 12px;
}

.task-info {
  margin-bottom: 12px;

  .info-row {
    display: flex;
    font-size: 13px;
    margin-bottom: 4px;

    .label {
      color: var(--el-text-color-secondary);
      width: 80px;
      flex-shrink: 0;
    }

    .value {
      color: var(--el-text-color-primary);
      word-break: break-all;
    }

    &.error .value {
      color: var(--el-color-danger);
    }

    .time-warning {
      color: var(--el-color-warning);
    }
  }
}

.task-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

// 详情对话框
.task-detail {
  .stats-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }

    .stat-item {
      text-align: center;
      padding: 12px;
      border-radius: 8px;
      background: var(--el-fill-color-light);

      .stat-value {
        font-size: 24px;
        font-weight: 600;
      }

      .stat-label {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-top: 4px;
      }

      &.success .stat-value { color: var(--el-color-success); }
      &.danger .stat-value { color: var(--el-color-danger); }
      &.warning .stat-value { color: var(--el-color-warning); }
      &.info .stat-value { color: var(--el-color-info); }
    }
  }

  .logs-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }

    .log-content {
      .log-header {
        display: flex;
        align-items: center;
        gap: 8px;

        .agent-name {
          font-weight: 500;
        }
      }

      .log-error {
        margin-top: 4px;
        color: var(--el-color-danger);
        font-size: 12px;
      }

      .log-duration {
        margin-top: 4px;
        color: var(--el-text-color-secondary);
        font-size: 12px;
      }
    }
  }
}
</style>
