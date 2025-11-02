<!--
  IconButton - 图标按钮组件

  功能：
  - 纯图标按钮
  - 多种样式和尺寸
  - Tooltip提示
  - 加载状态
  - 徽标提示
-->

<template>
  <el-tooltip
    :content="tooltip"
    :placement="tooltipPlacement"
    :disabled="!tooltip"
  >
    <el-badge
      :value="badge"
      :hidden="!badge"
      :max="badgeMax"
      :type="badgeType"
    >
      <button
        class="icon-button"
        :class="buttonClasses"
        :disabled="disabled || loading"
        @click="handleClick"
      >
        <el-icon v-if="loading" class="is-loading" :size="iconSize">
          <component :is="LoadingIcon" />
        </el-icon>
        <i v-else :class="icon" class="icon-button-icon" :style="iconStyle"></i>
      </button>
    </el-badge>
  </el-tooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading as LoadingIcon } from '@element-plus/icons-vue'

// ==================== Props ====================

interface Props {
  icon: string
  tooltip?: string
  tooltipPlacement?: 'top' | 'bottom' | 'left' | 'right'
  type?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'large' | 'default' | 'small'
  circle?: boolean
  disabled?: boolean
  loading?: boolean
  badge?: string | number
  badgeMax?: number
  badgeType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'bi-question-circle',
  tooltip: '',
  tooltipPlacement: 'top',
  type: 'default',
  size: 'default',
  circle: false,
  disabled: false,
  loading: false,
  badge: '',
  badgeMax: 99,
  badgeType: 'danger'
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

// ==================== Computed ====================

/**
 * 按钮类名
 */
const buttonClasses = computed(() => ({
  [`icon-button--${props.type}`]: true,
  [`icon-button--${props.size}`]: true,
  'icon-button--circle': props.circle,
  'is-disabled': props.disabled,
  'is-loading': props.loading
}))

/**
 * 图标大小
 */
const iconSize = computed(() => {
  const sizeMap = {
    large: 20,
    default: 18,
    small: 16
  }
  return sizeMap[props.size]
})

/**
 * 图标样式
 */
const iconStyle = computed(() => ({
  fontSize: `${iconSize.value}px`
}))

// ==================== Methods ====================

/**
 * 处理点击事件
 */
function handleClick(event: MouseEvent): void {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
  outline: none;

  // 默认尺寸
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-md, 8px);

  &:hover:not(.is-disabled):not(.is-loading) {
    background: var(--bg-hover, #f3f4f6);
  }

  &:active:not(.is-disabled):not(.is-loading) {
    transform: scale(0.95);
  }

  &.is-disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.is-loading {
    cursor: not-allowed;
  }
}

// ==================== 类型 ====================

.icon-button--default {
  color: var(--text-primary, #333);

  &:hover:not(.is-disabled) {
    color: var(--brand-primary, #4a89dc);
  }
}

.icon-button--primary {
  color: var(--brand-primary, #4a89dc);

  &:hover:not(.is-disabled) {
    background: rgba(74, 137, 220, 0.1);
  }
}

.icon-button--success {
  color: var(--color-success, #67c23a);

  &:hover:not(.is-disabled) {
    background: rgba(103, 194, 58, 0.1);
  }
}

.icon-button--warning {
  color: var(--color-warning, #e6a23c);

  &:hover:not(.is-disabled) {
    background: rgba(230, 162, 60, 0.1);
  }
}

.icon-button--danger {
  color: var(--color-danger, #f56c6c);

  &:hover:not(.is-disabled) {
    background: rgba(245, 108, 108, 0.1);
  }
}

.icon-button--info {
  color: var(--color-info, #909399);

  &:hover:not(.is-disabled) {
    background: rgba(144, 147, 153, 0.1);
  }
}

// ==================== 尺寸 ====================

.icon-button--large {
  width: 44px;
  height: 44px;
  font-size: 20px;
}

.icon-button--default {
  width: 36px;
  height: 36px;
  font-size: 18px;
}

.icon-button--small {
  width: 28px;
  height: 28px;
  font-size: 16px;
}

// ==================== 圆形 ====================

.icon-button--circle {
  border-radius: 50%;
}

// ==================== 图标 ====================

.icon-button-icon {
  transition: all 0.3s;
}

// ==================== 加载状态 ====================

.is-loading {
  .icon-button-icon {
    opacity: 0;
  }
}
</style>
