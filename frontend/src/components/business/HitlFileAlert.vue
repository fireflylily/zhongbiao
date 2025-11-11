<template>
  <el-alert
    v-if="fileInfo"
    :type="type"
    :closable="false"
    class="hitl-file-alert"
  >
    <template #title>
      <div class="alert-content">
        <div class="file-info">
          <el-icon class="file-icon"><Document /></el-icon>
          <div class="file-details">
            <span class="file-label">{{ label }}</span>
            <span class="file-name">{{ fileInfo.filename }}</span>
            <span v-if="fileInfo.file_size" class="file-size">
              ({{ formatFileSize(fileInfo.file_size) }})
            </span>
            <el-tag v-if="showTag" type="success" size="small" class="hitl-tag">
              已从投标项目加载
            </el-tag>
          </div>
        </div>

        <div class="alert-actions">
          <slot name="actions">
            <el-button
              v-if="showCancel"
              type="text"
              size="small"
              @click="handleCancel"
            >
              <el-icon><Close /></el-icon>
              {{ cancelText }}
            </el-button>
          </slot>
        </div>
      </div>
    </template>
  </el-alert>
</template>

<script setup lang="ts">
import { Document, Close } from '@element-plus/icons-vue'
import { formatFileSize } from '@/utils/format'
import type { HitlFileInfo } from '@/composables/useHitlIntegration'

export interface HitlFileAlertProps {
  /**
   * HITL文件信息
   */
  fileInfo: HitlFileInfo | null

  /**
   * 提示类型
   * @default 'success'
   */
  type?: 'success' | 'info' | 'warning' | 'error'

  /**
   * 文件标签文本
   * @default '使用HITL文件:'
   */
  label?: string

  /**
   * 是否显示取消按钮
   * @default true
   */
  showCancel?: boolean

  /**
   * 取消按钮文本
   * @default '取消使用'
   */
  cancelText?: string

  /**
   * 是否显示"已从投标项目加载"标签
   * @default true
   */
  showTag?: boolean
}

const props = withDefaults(defineProps<HitlFileAlertProps>(), {
  type: 'success',
  label: '使用HITL文件:',
  showCancel: true,
  cancelText: '取消使用',
  showTag: true
})

const emit = defineEmits<{
  /**
   * 取消使用HITL文件
   */
  cancel: []
}>()

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped lang="scss">
.hitl-file-alert {
  margin-bottom: 20px;

  :deep(.el-alert__content) {
    width: 100%;
  }

  :deep(.el-alert__title) {
    width: 100%;
  }

  .alert-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    gap: 16px;

    .file-info {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      min-width: 0;

      .file-icon {
        font-size: 20px;
        color: var(--el-color-primary);
        flex-shrink: 0;
      }

      .file-details {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        min-width: 0;

        .file-label {
          font-weight: 600;
          color: var(--el-text-color-primary);
          white-space: nowrap;
        }

        .file-name {
          color: var(--el-text-color-regular);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          max-width: 300px;
        }

        .file-size {
          color: var(--el-text-color-secondary);
          font-size: 12px;
          white-space: nowrap;
        }

        .hitl-tag {
          flex-shrink: 0;
        }
      }
    }

    .alert-actions {
      flex-shrink: 0;

      :deep(.el-button) {
        display: flex;
        align-items: center;
        gap: 4px;

        &:hover {
          color: var(--el-color-danger);
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .hitl-file-alert {
    .alert-content {
      flex-direction: column;
      align-items: flex-start;

      .alert-actions {
        width: 100%;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}
</style>
