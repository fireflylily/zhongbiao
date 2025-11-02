<!--
  Card - 增强版卡片组件

  功能：
  - 标题和描述
  - 头部操作区
  - 加载状态
  - 折叠/展开
  - 阴影效果
  - 自定义样式
-->

<template>
  <div
    class="card"
    :class="{
      'card--shadow': shadow,
      'card--hover': hover,
      'card--collapsed': collapsed,
      'card--loading': loading
    }"
  >
    <!-- 头部 -->
    <div v-if="$slots.header || title" class="card-header" :class="{ 'is-collapsible': collapsible }" @click="handleHeaderClick">
      <div class="header-content">
        <!-- 折叠图标 -->
        <i v-if="collapsible" class="bi collapse-icon" :class="collapsed ? 'bi-chevron-right' : 'bi-chevron-down'"></i>

        <!-- 标题区 -->
        <div class="header-title">
          <slot name="header">
            <h3 class="title-text">{{ title }}</h3>
            <p v-if="description" class="title-description">{{ description }}</p>
          </slot>
        </div>
      </div>

      <!-- 操作区 -->
      <div v-if="$slots.actions" class="header-actions" @click.stop>
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="card-loading">
      <el-icon class="is-loading" :size="24">
        <component :is="LoadingIcon" />
      </el-icon>
    </div>

    <!-- 内容区 -->
    <transition name="card-collapse">
      <div v-show="!collapsed" class="card-body" :style="bodyStyle">
        <slot></slot>
      </div>
    </transition>

    <!-- 底部 -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Loading as LoadingIcon } from '@element-plus/icons-vue'

// ==================== Props ====================

interface Props {
  title?: string
  description?: string
  shadow?: 'always' | 'hover' | 'never'
  hover?: boolean
  loading?: boolean
  collapsible?: boolean
  defaultCollapsed?: boolean
  bodyPadding?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  description: '',
  shadow: 'hover',
  hover: false,
  loading: false,
  collapsible: false,
  defaultCollapsed: false,
  bodyPadding: '20px'
})

const emit = defineEmits<{
  (e: 'collapse', collapsed: boolean): void
}>()

// ==================== State ====================

const collapsed = ref(props.defaultCollapsed)

// ==================== Computed ====================

const bodyStyle = {
  padding: props.bodyPadding
}

// ==================== Methods ====================

function handleHeaderClick(): void {
  if (props.collapsible) {
    collapsed.value = !collapsed.value
    emit('collapse', collapsed.value)
  }
}
</script>

<style scoped lang="scss">
.card {
  background: var(--bg-white, #ffffff);
  border: 1px solid var(--border-light, #e5e7eb);
  border-radius: var(--border-radius-md, 8px);
  overflow: hidden;
  position: relative;
  transition: all 0.3s;

  &.card--shadow {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }

  &.card--hover:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }

  &.card--loading {
    pointer-events: none;
  }
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light, #e5e7eb);
  background: var(--bg-light, #f8f9fa);

  &.is-collapsible {
    cursor: pointer;
    user-select: none;

    &:hover {
      background: var(--bg-hover, #f3f4f6);
    }
  }
}

.header-content {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
}

.collapse-icon {
  font-size: 16px;
  color: var(--text-secondary, #6c757d);
  margin-top: 2px;
  transition: transform 0.3s;
}

.header-title {
  flex: 1;
  min-width: 0;
}

.title-text {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #333);
}

.title-description {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;

  .is-loading {
    color: var(--brand-primary, #4a89dc);
  }
}

.card-body {
  overflow: hidden;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-light, #e5e7eb);
  background: var(--bg-light, #f8f9fa);
}

// 折叠动画
.card-collapse-enter-active,
.card-collapse-leave-active {
  transition: all 0.3s ease;
}

.card-collapse-enter-from,
.card-collapse-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>
