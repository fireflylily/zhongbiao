<!--
  Empty - 空状态组件

  功能：
  - 显示无数据状态
  - 多种预设场景（无数据、无搜索结果、错误等）
  - 自定义图标和文本
  - 可配置操作按钮
  - 响应式适配
-->

<template>
  <div class="empty-container" :class="{ 'empty--small': small }">
    <!-- 图标或插槽 -->
    <div class="empty-icon">
      <slot name="icon">
        <!-- 预设图标 -->
        <i v-if="type === 'no-data'" class="bi bi-inbox empty-icon-svg"></i>
        <i v-else-if="type === 'no-search'" class="bi bi-search empty-icon-svg"></i>
        <i v-else-if="type === 'error'" class="bi bi-exclamation-triangle empty-icon-svg error"></i>
        <i v-else-if="type === 'no-permission'" class="bi bi-lock empty-icon-svg"></i>
        <i v-else-if="type === 'network-error'" class="bi bi-wifi-off empty-icon-svg error"></i>
        <i v-else :class="icon" class="empty-icon-svg"></i>
      </slot>
    </div>

    <!-- 描述文本 -->
    <div class="empty-description">
      <slot name="description">
        <p class="empty-title">{{ title || defaultTitle }}</p>
        <p v-if="description" class="empty-text">{{ description }}</p>
      </slot>
    </div>

    <!-- 操作按钮 -->
    <div v-if="$slots.action || action" class="empty-action">
      <slot name="action">
        <el-button
          v-if="action"
          :type="actionType"
          :icon="actionIcon"
          @click="handleAction"
        >
          {{ actionText }}
        </el-button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// ==================== Props ====================

interface Props {
  type?: 'no-data' | 'no-search' | 'error' | 'no-permission' | 'network-error' | 'custom'
  icon?: string
  title?: string
  description?: string
  small?: boolean
  action?: boolean
  actionText?: string
  actionType?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  actionIcon?: any
}

const props = withDefaults(defineProps<Props>(), {
  type: 'no-data',
  icon: 'bi-inbox',
  title: '',
  description: '',
  small: false,
  action: false,
  actionText: '刷新',
  actionType: 'primary'
})

const emit = defineEmits<{
  (e: 'action'): void
}>()

// ==================== Computed ====================

/**
 * 默认标题（根据type）
 */
const defaultTitle = computed(() => {
  const titles = {
    'no-data': '暂无数据',
    'no-search': '无搜索结果',
    'error': '加载失败',
    'no-permission': '暂无权限',
    'network-error': '网络连接失败',
    'custom': '暂无数据'
  }
  return titles[props.type]
})

// ==================== Methods ====================

/**
 * 处理操作按钮点击
 */
function handleAction(): void {
  emit('action')
}
</script>

<style scoped lang="scss">
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;

  &.empty--small {
    padding: 40px 20px;

    .empty-icon-svg {
      font-size: 64px;
    }

    .empty-title {
      font-size: 15px;
    }

    .empty-text {
      font-size: 13px;
    }
  }
}

// ==================== 图标 ====================

.empty-icon {
  margin-bottom: 20px;
}

.empty-icon-svg {
  font-size: 96px;
  color: var(--text-disabled, #d1d5db);
  transition: color 0.3s;

  &.error {
    color: var(--color-danger, #f56c6c);
  }
}

// ==================== 描述 ====================

.empty-description {
  margin-bottom: 24px;
}

.empty-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.empty-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
  line-height: 1.6;
  max-width: 400px;
}

// ==================== 操作按钮 ====================

.empty-action {
  margin-top: 16px;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .empty-container {
    padding: 40px 16px;

    .empty-icon-svg {
      font-size: 72px;
    }

    .empty-title {
      font-size: 15px;
    }

    .empty-text {
      font-size: 13px;
      max-width: 300px;
    }
  }
}
</style>
