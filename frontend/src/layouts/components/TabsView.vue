<!--
  TabsView - 多标签页视图组件

  功能：
  - 访问过的页面自动添加标签
  - 支持关闭标签（除了固定标签）
  - 右键菜单（关闭其他、关闭所有、刷新）
  - 标签拖拽排序（可选）
  - 滚动查看更多标签
-->

<template>
  <div class="tabs-view" v-if="visitedViews.length > 0">
    <el-scrollbar class="tabs-scrollbar">
      <div class="tabs-container" ref="tabsContainerRef">
        <div
          v-for="tag in visitedViews"
          :key="tag.path"
          class="tabs-item"
          :class="{
            'is-active': isActive(tag),
            'is-affix': tag.meta?.affix
          }"
          @click="handleTabClick(tag)"
          @contextmenu.prevent="handleContextMenu(tag, $event)"
        >
          <i v-if="tag.meta?.icon" :class="tag.meta.icon" class="tab-icon"></i>
          <span class="tab-title">{{ tag.meta?.title || tag.name }}</span>
          <i
            v-if="!tag.meta?.affix"
            class="bi bi-x tab-close"
            @click.stop="closeTab(tag)"
          ></i>
        </div>
      </div>
    </el-scrollbar>

    <!-- 右键菜单 -->
    <div
      v-show="contextMenuVisible"
      class="context-menu"
      :style="{ left: contextMenuLeft + 'px', top: contextMenuTop + 'px' }"
      ref="contextMenuRef"
    >
      <div class="context-menu-item" @click="refreshTab">
        <i class="bi bi-arrow-clockwise"></i>
        <span>刷新</span>
      </div>
      <div class="context-menu-divider"></div>
      <div
        class="context-menu-item"
        @click="closeOtherTabs"
        :class="{ 'is-disabled': selectedTag?.meta?.affix }"
      >
        <i class="bi bi-x-circle"></i>
        <span>关闭其他</span>
      </div>
      <div class="context-menu-item" @click="closeAllTabs">
        <i class="bi bi-x-octagon"></i>
        <span>关闭所有</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter, type RouteLocationNormalized } from 'vue-router'

// ==================== Types ====================

interface TagView extends Partial<RouteLocationNormalized> {
  title?: string
}

// ==================== State ====================

const route = useRoute()
const router = useRouter()

const visitedViews = ref<TagView[]>([])
const selectedTag = ref<TagView | null>(null)

const contextMenuVisible = ref(false)
const contextMenuLeft = ref(0)
const contextMenuTop = ref(0)

const tabsContainerRef = ref<HTMLElement>()
const contextMenuRef = ref<HTMLElement>()

// ==================== Computed ====================

/**
 * 判断标签是否激活
 */
function isActive(tag: TagView): boolean {
  return tag.path === route.path
}

// ==================== Methods ====================

/**
 * 添加访问记录
 */
function addVisitedView(view: RouteLocationNormalized): void {
  // 跳过不需要标签的页面
  if (view.name === 'Login' || view.meta?.hideTabs) {
    return
  }

  // 检查是否已存在
  const exists = visitedViews.value.some((v) => v.path === view.path)
  if (!exists) {
    visitedViews.value.push({
      name: view.name,
      path: view.path,
      fullPath: view.fullPath,
      query: view.query,
      params: view.params,
      meta: view.meta
    })
  }

  // 保存到localStorage
  saveVisitedViews()
}

/**
 * 关闭标签
 */
function closeTab(tag: TagView): void {
  // 固定标签不能关闭
  if (tag.meta?.affix) {
    return
  }

  const index = visitedViews.value.findIndex((v) => v.path === tag.path)
  if (index > -1) {
    visitedViews.value.splice(index, 1)
    saveVisitedViews()

    // 如果关闭的是当前标签，跳转到最后一个标签
    if (isActive(tag)) {
      const lastTag = visitedViews.value[visitedViews.value.length - 1]
      if (lastTag) {
        router.push(lastTag.path as string)
      } else {
        router.push('/')
      }
    }
  }
}

/**
 * 标签点击
 */
function handleTabClick(tag: TagView): void {
  if (!isActive(tag)) {
    router.push(tag.path as string)
  }
}

/**
 * 右键菜单
 */
function handleContextMenu(tag: TagView, event: MouseEvent): void {
  selectedTag.value = tag
  contextMenuVisible.value = true
  contextMenuLeft.value = event.clientX
  contextMenuTop.value = event.clientY
}

/**
 * 刷新标签
 */
function refreshTab(): void {
  contextMenuVisible.value = false
  if (selectedTag.value) {
    router.replace({
      path: selectedTag.value.path as string,
      query: { _t: Date.now() }
    })
  }
}

/**
 * 关闭其他标签
 */
function closeOtherTabs(): void {
  contextMenuVisible.value = false
  if (!selectedTag.value) return

  visitedViews.value = visitedViews.value.filter(
    (v) => v.meta?.affix || v.path === selectedTag.value!.path
  )
  saveVisitedViews()

  // 如果当前不是选中的标签，跳转过去
  if (route.path !== selectedTag.value.path) {
    router.push(selectedTag.value.path as string)
  }
}

/**
 * 关闭所有标签
 */
function closeAllTabs(): void {
  contextMenuVisible.value = false

  // 只保留固定标签
  visitedViews.value = visitedViews.value.filter((v) => v.meta?.affix)
  saveVisitedViews()

  // 跳转到首页
  const affixTag = visitedViews.value.find((v) => v.meta?.affix)
  if (affixTag) {
    router.push(affixTag.path as string)
  } else {
    router.push('/')
  }
}

/**
 * 保存访问记录到localStorage
 */
function saveVisitedViews(): void {
  const views = visitedViews.value.map((v) => ({
    name: v.name,
    path: v.path,
    fullPath: v.fullPath,
    query: v.query,
    params: v.params,
    meta: v.meta
  }))
  localStorage.setItem('visitedViews', JSON.stringify(views))
}

/**
 * 从localStorage恢复访问记录
 */
function restoreVisitedViews(): void {
  try {
    const saved = localStorage.getItem('visitedViews')
    if (saved) {
      const views = JSON.parse(saved)
      visitedViews.value = views
    }
  } catch (error) {
    console.error('恢复访问记录失败:', error)
  }
}

/**
 * 关闭右键菜单
 */
function closeContextMenu(): void {
  contextMenuVisible.value = false
}

/**
 * 初始化固定标签
 */
function initAffixTags(): void {
  const affixTags = router.getRoutes().filter((route) => route.meta?.affix)
  for (const tag of affixTags) {
    if (tag.name) {
      addVisitedView(tag as RouteLocationNormalized)
    }
  }
}

// ==================== Lifecycle ====================

onMounted(() => {
  restoreVisitedViews()
  initAffixTags()
  addVisitedView(route)

  // 点击其他地方关闭右键菜单
  document.addEventListener('click', closeContextMenu)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeContextMenu)
})

// ==================== Watchers ====================

watch(
  () => route.path,
  () => {
    addVisitedView(route)
  }
)
</script>

<style scoped lang="scss">
.tabs-view {
  height: 40px;
  background: var(--bg-white, #ffffff);
  position: relative;
}

.tabs-scrollbar {
  height: 100%;

  :deep(.el-scrollbar__wrap) {
    overflow-y: hidden;
  }
}

.tabs-container {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 12px;
  height: 100%;
}

// ==================== 标签项 ====================

.tabs-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 12px;
  background: var(--bg-light, #f8f9fa);
  border: 1px solid var(--border-light, #e5e7eb);
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-primary, #333);
  cursor: pointer;
  user-select: none;
  transition: all 0.3s;
  white-space: nowrap;

  &:hover {
    background: var(--bg-hover, #e9ecef);
    color: var(--brand-primary, #4a89dc);

    .tab-close {
      opacity: 1;
    }
  }

  &.is-active {
    background: var(--brand-primary, #4a89dc);
    color: #ffffff;
    border-color: var(--brand-primary, #4a89dc);

    .tab-close {
      opacity: 1;
      color: #ffffff;

      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }

  &.is-affix {
    .tab-close {
      display: none;
    }
  }
}

.tab-icon {
  font-size: 14px;
}

.tab-title {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab-close {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 14px;
  opacity: 0;
  transition: all 0.3s;

  &:hover {
    background: var(--bg-hover, #dee2e6);
  }
}

// ==================== 右键菜单 ====================

.context-menu {
  position: fixed;
  min-width: 140px;
  background: var(--bg-white, #ffffff);
  border: 1px solid var(--border-light, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  z-index: 3000;
  animation: contextMenuFadeIn 0.15s ease;
}

@keyframes contextMenuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  color: var(--text-primary, #333);
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: var(--bg-hover, #f3f4f6);
    color: var(--brand-primary, #4a89dc);
  }

  &.is-disabled {
    color: var(--text-disabled, #adb5bd);
    cursor: not-allowed;
    pointer-events: none;
  }

  i {
    font-size: 14px;
  }
}

.context-menu-divider {
  height: 1px;
  background: var(--border-light, #e5e7eb);
  margin: 4px 0;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .tabs-item {
    .tab-title {
      max-width: 80px;
    }
  }
}
</style>
