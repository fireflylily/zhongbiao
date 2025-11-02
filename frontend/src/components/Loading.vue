<!--
  Loading - 加载状态组件

  功能：
  - 全屏加载遮罩
  - 局部加载状态
  - 多种加载动画样式
  - 自定义加载文本
  - 可配置背景色和透明度
-->

<template>
  <div
    v-if="visible"
    class="loading-container"
    :class="{
      'loading--fullscreen': fullscreen,
      'loading--inline': !fullscreen,
      [`loading--${type}`]: true
    }"
    :style="containerStyle"
  >
    <!-- 加载动画 -->
    <div class="loading-content">
      <!-- Spinner样式 -->
      <div v-if="type === 'spinner'" class="loading-spinner">
        <div class="spinner-circle"></div>
      </div>

      <!-- Dots样式 -->
      <div v-else-if="type === 'dots'" class="loading-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>

      <!-- Pulse样式 -->
      <div v-else-if="type === 'pulse'" class="loading-pulse">
        <div class="pulse-ring"></div>
      </div>

      <!-- Bars样式 -->
      <div v-else-if="type === 'bars'" class="loading-bars">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>

      <!-- Element Plus样式（默认） -->
      <el-icon v-else class="loading-icon is-loading" :size="iconSize">
        <component :is="LoadingIcon" />
      </el-icon>

      <!-- 加载文本 -->
      <p v-if="text" class="loading-text">{{ text }}</p>

      <!-- 进度条（可选） -->
      <div v-if="showProgress && progress !== undefined" class="loading-progress">
        <el-progress
          :percentage="progress"
          :show-text="false"
          :stroke-width="3"
          :color="progressColor"
        />
        <span class="progress-text">{{ progress }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading as LoadingIcon } from '@element-plus/icons-vue'

// ==================== Props ====================

interface Props {
  visible?: boolean
  fullscreen?: boolean
  type?: 'spinner' | 'dots' | 'pulse' | 'bars' | 'default'
  text?: string
  iconSize?: number
  background?: string
  opacity?: number
  showProgress?: boolean
  progress?: number
  progressColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  fullscreen: true,
  type: 'spinner',
  text: '加载中...',
  iconSize: 48,
  background: '#ffffff',
  opacity: 0.9,
  showProgress: false,
  progressColor: '#4a89dc'
})

// ==================== Computed ====================

/**
 * 容器样式
 */
const containerStyle = computed(() => {
  if (props.fullscreen) {
    return {
      backgroundColor: `rgba(255, 255, 255, ${props.opacity})`
    }
  }
  return {
    backgroundColor: props.background
  }
})
</script>

<style scoped lang="scss">
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

// ==================== 全屏加载 ====================

.loading--fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

// ==================== 局部加载 ====================

.loading--inline {
  width: 100%;
  min-height: 200px;
  border-radius: var(--border-radius-md, 8px);
}

// ==================== 加载内容 ====================

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.loading-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
  font-weight: 500;
}

// ==================== 进度条 ====================

.loading-progress {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;

  .progress-text {
    font-size: 13px;
    color: var(--text-secondary, #6c757d);
    font-weight: 600;
  }
}

// ==================== Spinner样式 ====================

.loading-spinner {
  width: 48px;
  height: 48px;
  position: relative;
}

.spinner-circle {
  width: 100%;
  height: 100%;
  border: 4px solid var(--border-light, #e5e7eb);
  border-top-color: var(--brand-primary, #4a89dc);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// ==================== Dots样式 ====================

.loading-dots {
  display: flex;
  gap: 8px;
  align-items: center;
}

.dot {
  width: 12px;
  height: 12px;
  background: var(--brand-primary, #4a89dc);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;

  &:nth-child(1) {
    animation-delay: -0.32s;
  }

  &:nth-child(2) {
    animation-delay: -0.16s;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

// ==================== Pulse样式 ====================

.loading-pulse {
  width: 48px;
  height: 48px;
  position: relative;
}

.pulse-ring {
  width: 100%;
  height: 100%;
  border: 4px solid var(--brand-primary, #4a89dc);
  border-radius: 50%;
  animation: pulse 1.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
}

// ==================== Bars样式 ====================

.loading-bars {
  display: flex;
  gap: 4px;
  align-items: center;
  height: 40px;
}

.bar {
  width: 6px;
  height: 100%;
  background: var(--brand-primary, #4a89dc);
  border-radius: 3px;
  animation: bar-stretch 1.2s infinite ease-in-out;

  &:nth-child(1) {
    animation-delay: -0.45s;
  }

  &:nth-child(2) {
    animation-delay: -0.3s;
  }

  &:nth-child(3) {
    animation-delay: -0.15s;
  }
}

@keyframes bar-stretch {
  0%,
  40%,
  100% {
    transform: scaleY(0.4);
  }
  20% {
    transform: scaleY(1);
  }
}

// ==================== Element Plus图标 ====================

.loading-icon {
  color: var(--brand-primary, #4a89dc);

  &.is-loading {
    animation: spin 1s linear infinite;
  }
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .loading-content {
    gap: 12px;
    padding: 16px;
  }

  .loading-text {
    font-size: 13px;
  }

  .loading-progress {
    width: 160px;
  }
}
</style>
