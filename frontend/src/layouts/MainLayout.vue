<!--
  MainLayout - 主应用布局组件

  功能：
  - 整体页面布局（顶部导航 + 侧边栏 + 内容区 + 页脚）
  - 响应式布局（支持移动端）
  - 侧边栏折叠/展开
  - 面包屑导航集成
  - 多标签页视图（可选）
-->

<template>
  <div class="main-layout" :class="layoutClasses">
    <!-- 顶部导航栏 -->
    <Navbar
      :collapsed="sidebarCollapsed"
      @toggle-sidebar="toggleSidebar"
    />

    <div class="layout-container">
      <!-- 侧边栏 -->
      <Sidebar
        v-if="showSidebar"
        :collapsed="sidebarCollapsed"
        @update:collapsed="setSidebarCollapsed"
      />

      <!-- 主内容区 -->
      <div class="main-content" :class="contentClasses">
        <!-- 面包屑导航 -->
        <Breadcrumb v-if="showBreadcrumb" class="breadcrumb-container" />

        <!-- 多标签页视图 -->
        <TabsView v-if="showTabs" class="tabs-container" />

        <!-- 页面内容 -->
        <div class="page-content" :class="pageContentClasses">
          <router-view v-slot="{ Component, route }">
            <transition :name="transitionName" mode="out-in">
              <!-- 使用keep-alive缓存组件 -->
              <keep-alive :include="cachedViews">
                <component :is="Component" :key="route.path" />
              </keep-alive>
            </transition>
          </router-view>
        </div>

        <!-- 页脚 -->
        <Footer v-if="showFooter" class="footer-container" />
      </div>
    </div>

    <!-- 移动端遮罩层 -->
    <div
      v-if="isMobile && !sidebarCollapsed"
      class="sidebar-overlay"
      @click="toggleSidebar"
    />

    <!-- 标书预览悬浮按钮 -->
    <TenderDocumentFloatingButton />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useSettingsStore } from '@/stores'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import Breadcrumb from './components/Breadcrumb.vue'
import TabsView from './components/TabsView.vue'
import Footer from './components/Footer.vue'
import TenderDocumentFloatingButton from '@/components/TenderDocumentFloatingButton.vue'

// ==================== State ====================

const route = useRoute()
const settingsStore = useSettingsStore()

// 侧边栏折叠状态
const sidebarCollapsed = ref(false)

// 响应式状态
const isMobile = ref(false)
const isTablet = ref(false)

// 缓存的视图列表（根据路由meta.keepAlive）
const cachedViews = ref<string[]>([])

// ==================== Computed ====================

/**
 * 布局类名
 */
const layoutClasses = computed(() => ({
  'layout--mobile': isMobile.value,
  'layout--tablet': isTablet.value,
  'layout--sidebar-collapsed': sidebarCollapsed.value,
  'layout--fixed-header': settingsStore.fixedHeader,
  'layout--sidebar-hidden': !showSidebar.value
}))

/**
 * 内容区类名
 */
const contentClasses = computed(() => ({
  'content--with-sidebar': showSidebar.value,
  'content--sidebar-collapsed': sidebarCollapsed.value,
  'content--full-width': !showSidebar.value
}))

/**
 * 页面内容类名
 */
const pageContentClasses = computed(() => ({
  'page-content--with-tabs': showTabs.value,
  'page-content--with-breadcrumb': showBreadcrumb.value,
  'page-content--padding': !route.meta.noPadding
}))

/**
 * 是否显示侧边栏
 */
const showSidebar = computed(() => {
  // 登录页不显示侧边栏
  if (route.name === 'Login') return false
  // 根据路由meta配置
  if (route.meta.hideSidebar) return false
  return settingsStore.showSidebar
})

/**
 * 是否显示面包屑
 */
const showBreadcrumb = computed(() => {
  if (route.name === 'Login') return false
  if (route.meta.hideBreadcrumb) return false
  return settingsStore.showBreadcrumb
})

/**
 * 是否显示多标签页
 */
const showTabs = computed(() => {
  if (route.name === 'Login') return false
  if (route.meta.hideTabs) return false
  return settingsStore.showTabs
})

/**
 * 是否显示页脚
 */
const showFooter = computed(() => {
  if (route.name === 'Login') return false
  if (route.meta.hideFooter) return false
  return settingsStore.showFooter
})

/**
 * 页面切换动画
 */
const transitionName = computed(() => {
  return settingsStore.pageTransition || 'fade'
})

// ==================== Methods ====================

/**
 * 切换侧边栏折叠状态
 */
function toggleSidebar(): void {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

/**
 * 设置侧边栏折叠状态
 */
function setSidebarCollapsed(collapsed: boolean): void {
  sidebarCollapsed.value = collapsed
}

/**
 * 检查屏幕尺寸
 */
function checkScreenSize(): void {
  const width = window.innerWidth

  isMobile.value = width < 768
  isTablet.value = width >= 768 && width < 1024

  // 移动端默认折叠侧边栏
  if (isMobile.value && !sidebarCollapsed.value) {
    sidebarCollapsed.value = true
  }
}

/**
 * 更新缓存视图列表
 */
function updateCachedViews(): void {
  if (route.meta.keepAlive && route.name) {
    const viewName = route.name as string
    if (!cachedViews.value.includes(viewName)) {
      cachedViews.value.push(viewName)
    }
  }
}

// ==================== Lifecycle ====================

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)

  // 从localStorage恢复侧边栏状态
  const savedCollapsed = localStorage.getItem('sidebarCollapsed')
  if (savedCollapsed !== null) {
    sidebarCollapsed.value = savedCollapsed === 'true'
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// ==================== Watchers ====================

/**
 * 监听侧边栏折叠状态，保存到localStorage
 */
watch(sidebarCollapsed, (newValue) => {
  localStorage.setItem('sidebarCollapsed', String(newValue))
})

/**
 * 监听路由变化，更新缓存视图
 */
watch(
  () => route.path,
  () => {
    updateCachedViews()

    // 移动端切换路由时自动折叠侧边栏
    if (isMobile.value && !sidebarCollapsed.value) {
      sidebarCollapsed.value = true
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page, #f5f7fa);
}

.layout-container {
  display: flex;
  flex: 1;
  position: relative;
  overflow: hidden;
}

// ==================== 主内容区 ====================

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  &.content--with-sidebar {
    margin-left: 200px;
  }

  &.content--sidebar-collapsed {
    margin-left: 64px;
  }

  &.content--full-width {
    margin-left: 0;
  }
}

// ==================== 面包屑容器 ====================

.breadcrumb-container {
  padding: 12px 24px;
  background: var(--bg-white, #ffffff);
  border-bottom: 1px solid var(--border-light, #e5e7eb);
}

// ==================== 标签页容器 ====================

.tabs-container {
  background: var(--bg-white, #ffffff);
  border-bottom: 1px solid var(--border-light, #e5e7eb);
}

// ==================== 页面内容 ====================

.page-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;

  &.page-content--padding {
    padding: 20px;
  }

  &.page-content--with-tabs {
    // 有标签页时减少顶部padding
  }

  &.page-content--with-breadcrumb {
    // 有面包屑时减少顶部padding
  }
}

// ==================== 页脚容器 ====================

.footer-container {
  margin-top: auto;
}

// ==================== 移动端遮罩层 ====================

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  cursor: pointer;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

// ==================== 页面切换动画 ====================

// 淡入淡出
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 滑动
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

// 缩放
.zoom-enter-active,
.zoom-leave-active {
  transition: all 0.2s ease;
}

.zoom-enter-from,
.zoom-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

// ==================== 响应式布局 ====================

// 固定顶部导航栏
.layout--fixed-header {
  .main-content {
    padding-top: 60px;
  }
}

// 平板设备
.layout--tablet {
  .main-content {
    &.content--with-sidebar {
      margin-left: 180px;
    }
  }
}

// 移动设备
.layout--mobile {
  .main-content {
    margin-left: 0 !important;
  }

  .page-content {
    &.page-content--padding {
      padding: 16px;
    }
  }

  .breadcrumb-container {
    padding: 8px 16px;
  }
}

// 隐藏侧边栏
.layout--sidebar-hidden {
  .main-content {
    margin-left: 0 !important;
  }
}
</style>
