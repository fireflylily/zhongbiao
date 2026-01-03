<template>
  <div class="response-check">
    <!-- 上传区域 -->
    <el-card class="upload-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>上传应答文件</span>
        </div>
      </template>

      <el-upload
        ref="uploadRef"
        class="upload-dragger"
        drag
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        :before-upload="beforeUpload"
        accept=".pdf,.doc,.docx"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、DOC、DOCX 格式，文件大小不超过 50MB
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" class="selected-file">
        <el-tag type="info" size="large" closable @close="clearFile">
          <i class="bi bi-file-earmark-text"></i>
          {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
        </el-tag>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="!selectedFile"
          @click="startCheck"
        >
          开始检查
        </el-button>
      </div>
    </el-card>

    <!-- 检查进度 -->
    <el-card v-if="currentTask" class="progress-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>检查进度</span>
          <el-tag :type="getStatusType(currentTask.status)">
            {{ getStatusText(currentTask.status) }}
          </el-tag>
        </div>
      </template>

      <div class="progress-content">
        <div class="file-info">
          <i class="bi bi-file-earmark-pdf"></i>
          <span>{{ currentTask.file_name }}</span>
        </div>

        <el-progress
          :percentage="currentTask.progress"
          :status="currentTask.status === 'failed' ? 'exception' : currentTask.status === 'completed' ? 'success' : undefined"
          :stroke-width="20"
        />

        <div class="current-step">
          {{ currentTask.current_step || '准备中...' }}
        </div>

        <div v-if="currentTask.error_message" class="error-message">
          <el-alert :title="currentTask.error_message" type="error" :closable="false" />
        </div>
      </div>
    </el-card>

    <!-- 检查结果 -->
    <el-card v-if="checkResult" class="result-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>检查结果</span>
          <div class="header-actions">
            <el-button type="primary" :icon="Download" @click="handleExport">
              导出Excel报告
            </el-button>
          </div>
        </div>
      </template>

      <!-- 统计汇总 -->
      <div class="statistics">
        <div class="stat-item total">
          <div class="stat-value">{{ checkResult.statistics.total_items }}</div>
          <div class="stat-label">总检查项</div>
        </div>
        <div class="stat-item pass">
          <div class="stat-value">{{ checkResult.statistics.pass_count }}</div>
          <div class="stat-label">符合</div>
        </div>
        <div class="stat-item fail">
          <div class="stat-value">{{ checkResult.statistics.fail_count }}</div>
          <div class="stat-label">不符合</div>
        </div>
        <div class="stat-item unknown">
          <div class="stat-value">{{ checkResult.statistics.unknown_count }}</div>
          <div class="stat-label">无法判断</div>
        </div>
      </div>

      <!-- 检查明细 -->
      <div class="check-details">
        <el-collapse v-model="expandedCategories">
          <el-collapse-item
            v-for="category in checkResult.categories"
            :key="category.category_id"
            :name="category.category_id"
          >
            <template #title>
              <div class="category-header">
                <span class="category-icon">{{ category.status_icon }}</span>
                <span class="category-name">{{ category.category_name }}</span>
                <span class="category-stats">
                  <el-tag type="success" size="small">{{ category.pass_count }}</el-tag>
                  <el-tag v-if="category.fail_count > 0" type="danger" size="small">{{ category.fail_count }}</el-tag>
                  <el-tag v-if="category.unknown_count > 0" type="warning" size="small">{{ category.unknown_count }}</el-tag>
                </span>
              </div>
            </template>

            <div class="check-items">
              <div
                v-for="item in category.items"
                :key="item.item_id"
                class="check-item"
                :class="getItemClass(item.status)"
              >
                <div class="item-status">
                  <span v-if="item.status === '符合'" class="status-icon pass">&#10003;</span>
                  <span v-else-if="item.status === '不符合'" class="status-icon fail">&#10007;</span>
                  <span v-else class="status-icon unknown">?</span>
                </div>
                <div class="item-content">
                  <div class="item-name">{{ item.name }}</div>
                  <div v-if="item.detail" class="item-detail">{{ item.detail }}</div>
                  <div v-if="item.location" class="item-location">
                    <i class="bi bi-geo-alt"></i> {{ item.location }}
                  </div>
                  <div v-if="item.suggestion" class="item-suggestion">
                    <i class="bi bi-lightbulb"></i> {{ item.suggestion }}
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 历史记录 -->
    <el-card class="history-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>历史检查记录</span>
          <el-button text type="primary" @click="loadHistory">
            <i class="bi bi-arrow-clockwise"></i> 刷新
          </el-button>
        </div>
      </template>

      <el-table :data="historyList" v-loading="historyLoading" empty-text="暂无检查记录">
        <el-table-column prop="original_filename" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="检查时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="150">
          <template #default="{ row }">
            <span v-if="row.status === 'completed'">
              {{ row.pass_count }}/{{ row.total_items }} 符合
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed'"
              type="primary"
              size="small"
              text
              @click="viewResult(row.task_id)"
            >
              查看
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDelete(row.task_id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox, type UploadInstance, type UploadFile } from 'element-plus'
import { UploadFilled, Download } from '@element-plus/icons-vue'
import {
  uploadAndCheck,
  getCheckStatus,
  getCheckResult,
  exportExcel,
  getHistory,
  deleteTask
} from '@/api/responseCheck'
import type {
  CheckStatusResponse,
  CheckResult,
  HistoryTask,
  TaskStatus,
  CheckStatusType
} from '@/types/responseCheck'

// 上传相关
const uploadRef = ref<UploadInstance>()
const selectedFile = ref<File | null>(null)
const uploading = ref(false)

// 当前任务
const currentTask = ref<CheckStatusResponse | null>(null)
let pollTimer: number | null = null

// 检查结果
const checkResult = ref<CheckResult | null>(null)
const expandedCategories = ref<string[]>([])

// 历史记录
const historyList = ref<HistoryTask[]>([])
const historyLoading = ref(false)
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 文件选择处理
function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件')
}

function beforeUpload(file: File) {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

function clearFile() {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

// 开始检查
async function startCheck() {
  if (!selectedFile.value) return

  uploading.value = true
  checkResult.value = null
  currentTask.value = null

  try {
    const res = await uploadAndCheck(selectedFile.value)
    if (res.success && res.data) {
      ElMessage.success('检查任务已创建')
      currentTask.value = {
        task_id: res.data.task_id,
        file_name: selectedFile.value.name,
        status: 'pending',
        progress: 0,
        current_step: '准备中...',
        current_category: '',
        error_message: '',
        categories: [],
        statistics: { total_items: 0, pass_count: 0, fail_count: 0, unknown_count: 0 }
      }
      startPolling(res.data.task_id)
      clearFile()
    } else {
      ElMessage.error(res.message || '创建任务失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 轮询检查状态
function startPolling(taskId: string) {
  stopPolling()
  pollTimer = window.setInterval(async () => {
    try {
      const res = await getCheckStatus(taskId)
      if (res.success && res.data) {
        currentTask.value = res.data

        // 检查完成或失败时停止轮询
        if (res.data.status === 'completed' || res.data.status === 'failed') {
          stopPolling()
          if (res.data.status === 'completed') {
            await loadResult(taskId)
            loadHistory()
          }
        }
      }
    } catch (error) {
      console.error('轮询状态失败:', error)
    }
  }, 2000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 加载检查结果
async function loadResult(taskId: string) {
  try {
    const res = await getCheckResult(taskId)
    if (res.success && res.data) {
      checkResult.value = res.data
      // 默认展开有问题的类别
      expandedCategories.value = res.data.categories
        .filter(cat => cat.fail_count > 0 || cat.unknown_count > 0)
        .map(cat => cat.category_id)
    }
  } catch (error: any) {
    ElMessage.error('加载结果失败')
  }
}

// 查看历史结果
async function viewResult(taskId: string) {
  currentTask.value = null
  await loadResult(taskId)
}

// 导出Excel
async function handleExport() {
  if (!checkResult.value) return

  try {
    const filename = `${checkResult.value.file_name.replace(/\.[^.]+$/, '')}_自检报告.xlsx`
    await exportExcel(checkResult.value.task_id, filename)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error('导出失败')
  }
}

// 加载历史记录
async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await getHistory(pagination.page, pagination.pageSize)
    if (res.success && res.data) {
      historyList.value = res.data.tasks
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    historyLoading.value = false
  }
}

// 删除记录
async function handleDelete(taskId: string) {
  try {
    await ElMessageBox.confirm('确定要删除这条检查记录吗？', '提示', {
      type: 'warning'
    })
    const res = await deleteTask(taskId)
    if (res.success) {
      ElMessage.success('删除成功')
      loadHistory()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    // 用户取消
  }
}

// 工具函数
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function getStatusType(status: TaskStatus): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<TaskStatus, 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'info',
    parsing: 'warning',
    checking: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

function getStatusText(status: TaskStatus): string {
  const map: Record<TaskStatus, string> = {
    pending: '等待中',
    parsing: '解析中',
    checking: '检查中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

function getItemClass(status: CheckStatusType): string {
  if (status === '符合') return 'item-pass'
  if (status === '不符合') return 'item-fail'
  return 'item-unknown'
}

// 生命周期
onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.response-check {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;

  .el-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

// 上传区域
.upload-card {
  .upload-dragger {
    width: 100%;

    :deep(.el-upload-dragger) {
      width: 100%;
      padding: 40px 20px;
    }
  }

  .selected-file {
    margin-top: 20px;
    display: flex;
    align-items: center;
    gap: 20px;

    .el-tag {
      i {
        margin-right: 8px;
      }
    }
  }
}

// 进度区域
.progress-card {
  .progress-content {
    .file-info {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 20px;
      font-size: 16px;

      i {
        font-size: 24px;
        color: #409eff;
      }
    }

    .current-step {
      margin-top: 15px;
      color: #666;
      font-size: 14px;
    }

    .error-message {
      margin-top: 15px;
    }
  }
}

// 结果区域
.result-card {
  .header-actions {
    display: flex;
    gap: 10px;
  }

  .statistics {
    display: flex;
    gap: 30px;
    margin-bottom: 30px;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;

    .stat-item {
      text-align: center;
      flex: 1;

      .stat-value {
        font-size: 36px;
        font-weight: bold;
        line-height: 1.2;
      }

      .stat-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
      }

      &.total .stat-value {
        color: #409eff;
      }

      &.pass .stat-value {
        color: #67c23a;
      }

      &.fail .stat-value {
        color: #f56c6c;
      }

      &.unknown .stat-value {
        color: #e6a23c;
      }
    }
  }

  .check-details {
    .category-header {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;

      .category-icon {
        font-size: 18px;
      }

      .category-name {
        font-weight: 500;
        flex: 1;
      }

      .category-stats {
        display: flex;
        gap: 5px;
      }
    }

    .check-items {
      .check-item {
        display: flex;
        padding: 12px 15px;
        border-bottom: 1px solid #ebeef5;
        transition: background-color 0.2s;

        &:hover {
          background-color: #f5f7fa;
        }

        &:last-child {
          border-bottom: none;
        }

        &.item-pass {
          .item-status .status-icon {
            color: #67c23a;
          }
        }

        &.item-fail {
          background-color: #fef0f0;

          .item-status .status-icon {
            color: #f56c6c;
          }
        }

        &.item-unknown {
          background-color: #fdf6ec;

          .item-status .status-icon {
            color: #e6a23c;
          }
        }

        .item-status {
          width: 30px;
          text-align: center;

          .status-icon {
            font-size: 18px;
            font-weight: bold;

            &.pass {
              color: #67c23a;
            }

            &.fail {
              color: #f56c6c;
            }

            &.unknown {
              color: #e6a23c;
            }
          }
        }

        .item-content {
          flex: 1;

          .item-name {
            font-weight: 500;
            margin-bottom: 5px;
          }

          .item-detail {
            color: #666;
            font-size: 13px;
            margin-bottom: 5px;
          }

          .item-location,
          .item-suggestion {
            color: #909399;
            font-size: 12px;

            i {
              margin-right: 5px;
            }
          }

          .item-suggestion {
            color: #409eff;
            margin-top: 5px;
          }
        }
      }
    }
  }
}

// 历史记录
.history-card {
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
