<!--
  Navbar - 顶部导航栏组件

  功能：
  - 侧边栏切换按钮
  - Logo和系统标题
  - AI模型选择器
  - 用户信息和下拉菜单
  - 全屏切换
  - 通知中心
  - 响应式适配
-->

<template>
  <header class="navbar" :class="navbarClasses">
    <div class="navbar-left">
      <!-- 侧边栏切换按钮 -->
      <button
        class="sidebar-toggle"
        :class="{ 'is-active': !collapsed }"
        @click="handleToggleSidebar"
        :title="collapsed ? '展开侧边栏' : '折叠侧边栏'"
      >
        <i class="bi bi-list"></i>
      </button>

      <!-- Logo和标题 -->
      <div class="navbar-brand" @click="goHome">
        <!-- 使用Bootstrap图标代替logo图片，避免Vite编译问题 -->
        <i class="bi bi-lightbulb-fill brand-icon" v-if="!isMobile"></i>
        <span class="brand-title">元景AI标书生成平台</span>
      </div>
    </div>

    <div class="navbar-right">
      <!-- AI模型选择器 -->
      <el-select
        v-model="selectedModel"
        class="model-selector"
        placeholder="选择AI模型"
        size="default"
        @change="handleModelChange"
        v-if="!isMobile"
      >
        <template #prefix>
          <i class="bi bi-robot"></i>
        </template>
        <el-option
          v-for="model in availableModels"
          :key="model.value"
          :label="model.label"
          :value="model.value"
        >
          <span class="model-option">
            <i :class="model.icon" class="model-icon"></i>
            <span>{{ model.label }}</span>
            <el-tag
              v-if="model.recommended"
              type="success"
              size="small"
              class="model-tag"
            >
              推荐
            </el-tag>
          </span>
        </el-option>
      </el-select>

      <!-- 全屏切换 -->
      <el-tooltip content="全屏" placement="bottom" v-if="!isMobile">
        <button class="navbar-action" @click="toggleFullscreen">
          <i
            :class="isFullscreen ? 'bi-fullscreen-exit' : 'bi-fullscreen'"
            class="bi"
          ></i>
        </button>
      </el-tooltip>

      <!-- 通知中心 -->
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="navbar-badge">
        <el-tooltip content="通知" placement="bottom">
          <button class="navbar-action" @click="showNotifications">
            <i class="bi bi-bell"></i>
          </button>
        </el-tooltip>
      </el-badge>

      <!-- 用户信息下拉菜单 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" :src="userAvatar">
            <i class="bi bi-person-circle"></i>
          </el-avatar>
          <span class="user-name" v-if="!isMobile">{{ username }}</span>
          <i class="bi bi-chevron-down dropdown-icon" v-if="!isMobile"></i>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <i class="bi bi-person"></i>
              <span>个人信息</span>
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <i class="bi bi-gear"></i>
              <span>系统设置</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <i class="bi bi-box-arrow-right"></i>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore, useNotificationStore } from '@/stores'
import type { AIModelOption } from '@/types'

// ==================== Props & Emits ====================

interface Props {
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false
})

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

// ==================== State ====================

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const isMobile = ref(false)
const isFullscreen = ref(false)

// ==================== Computed ====================

/**
 * Navbar类名
 */
const navbarClasses = computed(() => ({
  'navbar--mobile': isMobile.value,
  'navbar--fixed': true
}))

/**
 * 用户名
 */
const username = computed(() => userStore.username || '未登录')

/**
 * 用户头像
 */
const userAvatar = computed(() => userStore.avatar || '')

/**
 * 可用的AI模型列表
 */
const availableModels = computed((): AIModelOption[] => {
  return [
    // 始皇API模型（新增）
    {
      value: 'shihuang-gpt5',
      label: 'GPT5（最强推理）',
      icon: 'bi-stars',
      recommended: false,
      provider: 'shihuang'
    },
    {
      value: 'shihuang-claude-sonnet-45',
      label: 'Claude Sonnet 4.5（标书专用）',
      icon: 'bi-chat-square-text',
      recommended: true,
      provider: 'shihuang'
    },
    {
      value: 'shihuang-gpt4o-mini',
      label: 'GPT4o Mini',
      icon: 'bi-robot',
      recommended: false,
      provider: 'shihuang'
    },
    // 阿里云通义千问
    {
      value: 'qwen-max',
      label: '通义千问-Max（推荐-默认）',
      icon: 'bi-translate',
      recommended: true,
      provider: 'alibaba'
    },
    // 联通元景模型（保留）
    {
      value: 'yuanjing-deepseek-v3',
      label: 'DeepSeek V3',
      icon: 'bi-stars',
      recommended: false,
      provider: 'unicom'
    },
    {
      value: 'yuanjing-qwen3-235b',
      label: 'Qwen 2.5 235B',
      icon: 'bi-lightning',
      recommended: false,
      provider: 'unicom'
    },
    {
      value: 'yuanjing-glm-rumination',
      label: 'GLM Rumination',
      icon: 'bi-chat-dots',
      recommended: false,
      provider: 'unicom'
    }
  ]
})

/**
 * 当前选中的模型
 */
const selectedModel = computed({
  get: () => {
    // 从localStorage或Store获取
    return localStorage.getItem('selectedModel') || 'qwen-max'
  },
  set: (value: string) => {
    localStorage.setItem('selectedModel', value)
  }
})

/**
 * 未读通知数量
 */
const unreadCount = computed(() => notificationStore.unreadCount)

// ==================== Methods ====================

/**
 * 切换侧边栏
 */
function handleToggleSidebar(): void {
  emit('toggle-sidebar')
}

/**
 * 回到首页
 */
function goHome(): void {
  router.push({ name: 'Home' })
}

/**
 * AI模型变更
 */
function handleModelChange(modelValue: string): void {
  const model = availableModels.value.find((m) => m.value === modelValue)
  if (model) {
    ElMessage.success(`已切换到 ${model.label} 模型`)
    // 触发全局事件通知其他组件
    window.dispatchEvent(
      new CustomEvent('ai-model-changed', {
        detail: { model: modelValue }
      })
    )
  }
}

/**
 * 切换全屏
 */
function toggleFullscreen(): void {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
      isFullscreen.value = false
    }
  }
}

/**
 * 显示通知中心
 */
function showNotifications(): void {
  // TODO: 实现通知中心弹窗
  ElMessage.info('通知中心功能开发中...')
}

/**
 * 处理用户菜单命令
 */
async function handleCommand(command: string): Promise<void> {
  switch (command) {
    case 'profile':
      router.push({ name: 'UserProfile' })
      break

    case 'settings':
      router.push({ name: 'UserSettings' })
      break

    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await userStore.logout()
        ElMessage.success('已退出登录')
        router.push({ name: 'Login' })
      } catch (error) {
        // 用户取消
      }
      break
  }
}

/**
 * 检查屏幕尺寸
 */
function checkScreenSize(): void {
  isMobile.value = window.innerWidth < 768
}

/**
 * 监听全屏状态变化
 */
function handleFullscreenChange(): void {
  isFullscreen.value = !!document.fullscreenElement
}

// ==================== Lifecycle ====================

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkScreenSize)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style scoped lang="scss">
.navbar {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-white, #ffffff);
  border-bottom: 1px solid var(--border-light, #e5e7eb);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 1000;

  &.navbar--fixed {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
  }

  &.navbar--mobile {
    padding: 0 12px;
  }
}

// ==================== 左侧区域 ====================

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sidebar-toggle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: var(--border-radius-md, 8px);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 24px;
  color: var(--text-primary, #333);

  &:hover {
    background: var(--bg-hover, #f3f4f6);
  }

  &:active {
    transform: scale(0.95);
  }

  &.is-active {
    color: var(--brand-primary, #4a89dc);
  }
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;

  .brand-icon {
    font-size: 28px;
    color: var(--brand-primary, #4a89dc);
    transition: transform 0.3s;
  }

  &:hover .brand-icon {
    transform: scale(1.1);
  }

  .brand-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary, #333);
    white-space: nowrap;
  }
}

// ==================== 右侧区域 ====================

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-selector {
  width: 220px;

  :deep(.el-input__prefix) {
    font-size: 18px;
    color: var(--brand-primary, #4a89dc);
  }
}

.model-option {
  display: flex;
  align-items: center;
  gap: 8px;

  .model-icon {
    font-size: 16px;
    color: var(--brand-primary, #4a89dc);
  }

  .model-tag {
    margin-left: auto;
  }
}

.navbar-action {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: var(--border-radius-md, 8px);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 20px;
  color: var(--text-primary, #333);

  &:hover {
    background: var(--bg-hover, #f3f4f6);
    color: var(--brand-primary, #4a89dc);
  }
}

.navbar-badge {
  :deep(.el-badge__content) {
    border: 2px solid var(--bg-white, #ffffff);
  }
}

// ==================== 用户信息 ====================

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 4px 4px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: var(--bg-hover, #f3f4f6);
  }

  .user-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary, #333);
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .dropdown-icon {
    font-size: 12px;
    color: var(--text-secondary, #6c757d);
    transition: transform 0.3s;
  }
}

// ==================== 下拉菜单 ====================

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;

  i {
    font-size: 16px;
  }

  &:hover {
    background: var(--bg-hover, #f3f4f6);
  }
}

// ==================== 响应式 ====================

.navbar--mobile {
  .brand-title {
    font-size: 16px;
  }

  .navbar-left {
    gap: 8px;
  }

  .navbar-right {
    gap: 8px;
  }
}

@media (max-width: 576px) {
  .brand-title {
    display: none;
  }
}
</style>
