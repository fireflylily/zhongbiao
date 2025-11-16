<template>
  <div class="history-files-panel">
    <!-- 当前项目文件卡片 -->
    <el-card v-if="currentFile" shadow="never" class="current-file-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <span>{{ title || '📄 该项目的生成文件' }}</span>
            <el-tag type="info">历史文件</el-tag>
          </div>
        </div>
      </template>

      <!-- 文件信息 -->
      <div class="current-file-content">
        <el-alert
          type="info"
          :title="currentFile.message || currentFileMessage"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <!-- 统计信息（如果有） -->
        <StatsCard
          v-if="currentFile.stats && showStats"
          :stats="currentFile.stats"
          :stat-items="statItems"
        />

        <!-- 文件详情 -->
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="文件名">
            {{ getFileName(currentFile.outputFile || currentFile.file_path) }}
          </el-descriptions-item>
          <el-descriptions-item label="下载地址">
            <el-link :href="currentFile.downloadUrl" type="primary">
              {{ getFileName(currentFile.downloadUrl) }}
            </el-link>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 操作按钮 -->
        <div class="history-actions">
          <el-button
            v-if="showEditorOpen"
            type="primary"
            size="large"
            @click="$emit('openInEditor', currentFile)"
          >
            <el-icon><Edit /></el-icon>
            在编辑器中打开
          </el-button>
          <el-button
            type="primary"
            size="large"
            :icon="View"
            @click="$emit('preview', currentFile)"
          >
            预览Word
          </el-button>
          <el-button
            type="success"
            size="large"
            :icon="Download"
            @click="$emit('download', currentFile)"
          >
            下载
          </el-button>
          <el-button
            v-if="showRegenerate"
            size="large"
            :icon="RefreshRight"
            @click="$emit('regenerate')"
          >
            重新生成
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 所有历史文件列表（折叠） - 仅当有历史文件时显示 -->
    <el-collapse v-if="historyFiles.length > 0" v-model="activeNames" class="history-collapse">
      <el-collapse-item name="history">
        <template #title>
          <div class="collapse-header">
            <span>📂 查看所有历史处理文件 ({{ historyFiles.length }})</span>
            <el-button
              v-if="activeNames.includes('history')"
              type="primary"
              size="small"
              :loading="loading"
              @click.stop="$emit('refresh')"
              style="margin-left: 16px"
            >
              刷新列表
            </el-button>
          </div>
        </template>

        <el-card shadow="never" style="border: none;">
          <el-table
            :data="historyFiles"
            border
            stripe
            v-loading="loading"
            max-height="400"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="filename" label="文件名" min-width="300">
              <template #default="{ row }">
                <div class="filename-cell">
                  <el-icon><Document /></el-icon>
                  <span>{{ row.filename }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="文件大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="process_time" label="处理时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.process_time || row.generated_at, 'YYYY-MM-DD HH:mm:ss') }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="$emit('preview', row)"
                >
                  预览
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  @click="$emit('download', row)"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 空状态 -->
          <el-empty
            v-if="!loading && historyFiles.length === 0"
            description="暂无历史文件"
            :image-size="100"
          />
        </el-card>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { View, Download, RefreshRight, Document, Edit } from '@element-plus/icons-vue'
import { StatsCard } from '@/components'
import { formatFileSize, formatDate } from '@/utils/format'
import type { StatItem } from './StatsCard.vue'

/**
 * 历史文件面板组件
 *
 * @description
 * 统一的历史文件管理面板，包括：
 * - 当前项目最新文件卡片
 * - 历史文件折叠列表
 * - 预览、下载、重新生成操作
 *
 * @example
 * ```vue
 * <HistoryFilesPanel
 *   title="该项目的商务应答文件"
 *   :current-file="generationResult"
 *   :history-files="historyFiles"
 *   :loading="loadingHistory"
 *   :show-stats="true"
 *   :stat-items="customStatItems"
 *   @preview="previewFile"
 *   @download="downloadFile"
 *   @regenerate="regenerateFile"
 *   @refresh="loadHistoryFiles"
 * />
 * ```
 */

export interface HistoryFilesPanelProps {
  /**
   * 卡片标题
   * @default '📄 该项目的生成文件'
   */
  title?: string

  /**
   * 当前项目的最新文件
   */
  currentFile?: any

  /**
   * 历史文件列表
   */
  historyFiles: any[]

  /**
   * 是否正在加载
   * @default false
   */
  loading?: boolean

  /**
   * 是否显示重新生成按钮
   * @default true
   */
  showRegenerate?: boolean

  /**
   * 是否显示统计信息
   * @default true
   */
  showStats?: boolean

  /**
   * 统计项配置（用于StatsCard）
   */
  statItems?: StatItem[]

  /**
   * 当前文件的提示消息
   */
  currentFileMessage?: string

  /**
   * 是否显示"在编辑器中打开"按钮
   * @default false
   */
  showEditorOpen?: boolean
}

const props = withDefaults(defineProps<HistoryFilesPanelProps>(), {
  title: '',
  loading: false,
  showRegenerate: true,
  showStats: true,
  currentFileMessage: '该项目已有生成文件',
  showEditorOpen: false
})

// Events
defineEmits<{
  /**
   * 在编辑器中打开文件
   */
  openInEditor: [file: any]
  /**
   * 预览文件
   */
  preview: [file: any]
  /**
   * 下载文件
   */
  download: [file: any]
  /**
   * 重新生成
   */
  regenerate: []
  /**
   * 刷新列表
   */
  refresh: []
}>()

// 折叠面板状态
const activeNames = ref<string[]>([])

/**
 * 从完整路径中提取文件名
 * @param path 完整文件路径或URL
 * @returns 文件名
 */
const getFileName = (path: string | undefined) => {
  if (!path) return '-'

  // 如果是URL，先解码
  let decodedPath = path
  try {
    decodedPath = decodeURIComponent(path)
  } catch {
    // 解码失败则使用原始路径
  }

  // 提取最后一个斜杠后的文件名
  const parts = decodedPath.split('/')
  return parts[parts.length - 1] || '-'
}
</script>

<style scoped lang="scss">
.history-files-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;

  // ==================== 当前文件卡片 ====================
  .current-file-card {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-light);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;

      .header-title {
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .header-actions {
        display: flex;
        gap: 8px;
        align-items: center;
      }
    }

    .current-file-content {
      .history-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--el-border-color-lighter);
      }
    }
  }

  // ==================== 历史文件折叠列表 ====================
  .history-collapse {
    :deep(.el-collapse-item__header) {
      padding: 16px 20px;
      background: var(--el-fill-color-lighter);
      border-radius: 8px;
      font-weight: 600;
    }

    :deep(.el-collapse-item__content) {
      padding: 0;
    }

    .collapse-header {
      display: flex;
      align-items: center;
      width: 100%;
    }

    // 文件名单元格
    .filename-cell {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-icon {
        color: var(--el-color-primary);
        font-size: 16px;
      }
    }
  }
}

// ==================== 响应式 ====================
@media (max-width: 768px) {
  .history-files-panel {
    .current-file-card .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .header-actions {
        width: 100%;
        justify-content: flex-start;
        flex-wrap: wrap;
      }
    }

    .history-collapse {
      .collapse-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;

        el-button {
          width: 100%;
        }
      }
    }
  }
}
</style>
