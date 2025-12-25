<!--
  Sidebar - 侧边栏导航组件

  功能：
  - 基于路由自动生成菜单
  - 支持多级菜单（最多3级）
  - 折叠/展开动画
  - 激活状态高亮
  - 图标 + 文字显示
  - 响应式适配
-->

<template>
  <aside class="sidebar" :class="sidebarClasses">
    <!-- 菜单容器 -->
    <el-scrollbar class="sidebar-scrollbar">
      <el-menu
        :default-active="activeMenu"
        :default-openeds="defaultOpeneds"
        :collapse="collapsed"
        :unique-opened="false"
        :collapse-transition="false"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <!-- 按分类分组显示菜单 -->
        <template v-for="category in menuCategories" :key="category.key">
          <!-- 只显示有菜单项的分组 -->
          <template v-if="groupedMenuItems[category.key] && groupedMenuItems[category.key].length > 0">
            <!-- 分组标题（非折叠时显示，且分组有多个菜单项） -->
            <div v-if="!collapsed && groupedMenuItems[category.key].length > 1" class="menu-group-title">
              <i class="bi group-icon" :class="category.icon"></i>
              <span class="group-label">{{ category.label }}</span>
            </div>

            <!-- 分组菜单项 -->
            <template v-for="item in groupedMenuItems[category.key]" :key="item.path">
              <!-- 单级菜单项 -->
              <el-menu-item
                v-if="!item.children || item.children.length === 0"
                :index="item.path"
              >
                <template #title>
                  <i v-if="item.icon" class="bi menu-icon" :class="item.icon"></i>
                  <span class="menu-title">{{ item.title }}</span>
                </template>
              </el-menu-item>

              <!-- 多级菜单（子菜单） -->
              <el-sub-menu v-else :index="item.path">
                <template #title>
                  <i v-if="item.icon" class="bi menu-icon" :class="item.icon"></i>
                  <span class="menu-title">{{ item.title }}</span>
                </template>

                <!-- 二级菜单项 -->
                <template v-for="subItem in item.children" :key="subItem.path">
                  <!-- 二级普通菜单 -->
                  <el-menu-item
                    v-if="!subItem.children || subItem.children.length === 0"
                    :index="subItem.path"
                  >
                    <template #title>
                      <i v-if="subItem.icon" class="bi submenu-icon" :class="subItem.icon"></i>
                      <span>{{ subItem.title }}</span>
                    </template>
                  </el-menu-item>

                  <!-- 三级菜单 -->
                  <el-sub-menu v-else :index="subItem.path">
                    <template #title>
                      <i v-if="subItem.icon" class="bi submenu-icon" :class="subItem.icon"></i>
                      <span>{{ subItem.title }}</span>
                    </template>

                    <el-menu-item
                      v-for="thirdItem in subItem.children"
                      :key="thirdItem.path"
                      :index="thirdItem.path"
                    >
                      <template #title>
                        <i v-if="thirdItem.icon" class="bi submenu-icon" :class="thirdItem.icon"></i>
                        <span>{{ thirdItem.title }}</span>
                      </template>
                    </el-menu-item>
                  </el-sub-menu>
                </template>
              </el-sub-menu>
            </template>

            <!-- 分组分隔线（只在多项分组时显示） -->
            <el-divider v-if="!collapsed && groupedMenuItems[category.key].length > 1" class="menu-group-divider" />
          </template>
        </template>

        <!-- 显示未分组的菜单项(other分组) -->
        <template v-if="groupedMenuItems['other'] && groupedMenuItems['other'].length > 0">
          <template v-for="item in groupedMenuItems['other']" :key="item.path">
            <!-- 单级菜单项 -->
            <el-menu-item
              v-if="!item.children || item.children.length === 0"
              :index="item.path"
            >
              <template #title>
                <i v-if="item.icon" class="bi menu-icon" :class="item.icon"></i>
                <span class="menu-title">{{ item.title }}</span>
              </template>
            </el-menu-item>

            <!-- 多级菜单（子菜单） -->
            <el-sub-menu v-else :index="item.path">
              <template #title>
                <i v-if="item.icon" class="bi menu-icon" :class="item.icon"></i>
                <span class="menu-title">{{ item.title }}</span>
              </template>

              <!-- 二级菜单项 -->
              <template v-for="subItem in item.children" :key="subItem.path">
                <!-- 二级普通菜单 -->
                <el-menu-item
                  v-if="!subItem.children || subItem.children.length === 0"
                  :index="subItem.path"
                >
                  <template #title>
                    <i v-if="subItem.icon" class="bi submenu-icon" :class="subItem.icon"></i>
                    <span>{{ subItem.title }}</span>
                  </template>
                </el-menu-item>

                <!-- 三级菜单 -->
                <el-sub-menu v-else :index="subItem.path">
                  <template #title>
                    <i v-if="subItem.icon" class="bi submenu-icon" :class="subItem.icon"></i>
                    <span>{{ subItem.title }}</span>
                  </template>

                  <el-menu-item
                    v-for="thirdItem in subItem.children"
                    :key="thirdItem.path"
                    :index="thirdItem.path"
                  >
                    <template #title>
                      <i v-if="thirdItem.icon" class="bi submenu-icon" :class="thirdItem.icon"></i>
                      <span>{{ thirdItem.title }}</span>
                    </template>
                  </el-menu-item>
                </el-sub-menu>
              </template>
            </el-sub-menu>
          </template>
        </template>
      </el-menu>
    </el-scrollbar>

    <!-- 折叠按钮 -->
    <div class="sidebar-footer" v-if="showCollapseButton">
      <button class="collapse-button" @click="toggleCollapse">
        <i :class="collapsed ? 'bi-chevron-right' : 'bi-chevron-left'" class="bi"></i>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { generateMenuFromRoutes } from '@/router/utils'
import type { MenuItem } from '@/types'

// ==================== Props & Emits ====================

interface Props {
  collapsed?: boolean
  uniqueOpened?: boolean
  showCollapseButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
  uniqueOpened: true,
  showCollapseButton: true
})

const emit = defineEmits<{
  (e: 'update:collapsed', value: boolean): void
}>()

// ==================== State ====================

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// ==================== Computed ====================

/**
 * Sidebar类名
 */
const sidebarClasses = computed(() => ({
  'sidebar--collapsed': props.collapsed
}))

/**
 * 菜单分组配置
 */
const menuCategories = computed(() => {
  const categories = [
    { key: 'bidding-center', label: '投标中心', icon: 'bi-folder-fill' },
    { key: 'knowledge', label: '知识中心', icon: 'bi-book-fill' }
  ]

  // 只有admin用户才显示ABTest分类
  if (userStore.username === 'admin') {
    categories.push({ key: 'abtest', label: 'AB测试', icon: 'bi-bug' })
  }

  return categories
})

/**
 * 菜单项列表
 */
const menuItems = computed((): MenuItem[] => {
  // 从router实例获取标准化的路由(而不是静态配置)
  const allRoutes = router.getRoutes()

  // 生成菜单项
  const allMenus = generateMenuFromRoutes(allRoutes)

  // 过滤掉不在菜单中显示的项
  return allMenus.filter((item) => {
    if (item.meta?.showInMenu === false) return false

    // ABTest分类只对admin用户可见
    if (item.meta?.category === 'abtest' && userStore.username !== 'admin') {
      return false
    }

    return true
  })
})

/**
 * 按分类分组的菜单
 */
const groupedMenuItems = computed(() => {
  const groups: Record<string, MenuItem[]> = {}

  // 按category分组，过滤掉有parent属性的子菜单（它们应该只显示在父菜单下）
  menuItems.value.forEach((item) => {
    // 跳过有parent属性的菜单项（它们应该只作为子菜单显示）
    if (item.meta?.parent) {
      return
    }

    const category = item.meta?.category || 'other'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(item)
  })

  // 特殊处理：为投标中心手动创建一个虚拟父菜单项
  if (groups['bidding-center'] && groups['bidding-center'].length > 0) {
    // 收集所有投标中心的菜单项（包括有parent属性的）
    const biddingItems: MenuItem[] = []
    menuItems.value.forEach((item) => {
      if (item.meta?.category === 'bidding-center' || item.meta?.parent === 'BiddingCenter') {
        biddingItems.push(item)
      }
    })

    // 按order排序
    biddingItems.sort((a, b) => (a.order || 99) - (b.order || 99))

    // 创建虚拟父菜单项
    const biddingCenterMenu: MenuItem = {
      name: 'BiddingCenter',
      path: '/bidding-center',
      title: '投标中心',
      icon: 'bi-folder-fill',
      order: 1,
      category: 'bidding-center',
      children: biddingItems,
      meta: {
        title: '投标中心',
        icon: 'bi-folder-fill',
        category: 'bidding-center',
        order: 1
      }
    }

    // 替换原来的分组
    groups['bidding-center'] = [biddingCenterMenu]
  }

  // 按order排序其他分组
  Object.keys(groups).forEach((key) => {
    if (key !== 'bidding-center') {
      groups[key].sort((a, b) => (a.order || 99) - (b.order || 99))
    }
  })

  return groups
})

/**
 * 当前激活的菜单
 */
const activeMenu = computed(() => {
  const { path } = route
  return path
})

/**
 * 默认展开的菜单
 */
const defaultOpeneds = computed(() => {
  // 投标中心默认展开
  return ['/bidding-center']
})

// ==================== Methods ====================

/**
 * 菜单选择事件
 */
function handleMenuSelect(index: string): void {
  // 导航到选中的路由
  if (index !== route.path) {
    router.push(index)
  }
}

/**
 * 切换折叠状态
 */
function toggleCollapse(): void {
  emit('update:collapsed', !props.collapsed)
}

// ==================== Watchers ====================

/**
 * 监听路由变化，确保菜单激活状态正确
 */
watch(
  () => route.path,
  () => {
    // Element Plus的菜单组件会自动处理激活状态
  }
)
</script>

<style scoped lang="scss">
.sidebar {
  width: 200px;
  height: calc(100vh - 60px);
  background: var(--bg-white, #ffffff);
  border-right: 1px solid var(--border-light, #e5e7eb);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 60px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 999;

  &.sidebar--collapsed {
    width: 64px;
  }
}

// ==================== 滚动容器 ====================

.sidebar-scrollbar {
  flex: 1;
  overflow: hidden;

  :deep(.el-scrollbar__wrap) {
    overflow-x: hidden;
  }
}

// ==================== 菜单样式 ====================

.sidebar-menu {
  border-right: none;
  background: transparent;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;
    padding: 0 20px !important;
    transition: all 0.3s;

    &:hover {
      background: var(--bg-hover, #f3f4f6);
      color: var(--brand-primary, #4a89dc);

      .menu-icon,
      .submenu-icon {
        color: var(--brand-primary, #4a89dc);
      }
    }

    &.is-active {
      background: var(--brand-primary-light, rgba(74, 137, 220, 0.1));
      color: var(--brand-primary, #4a89dc);
      font-weight: 600;
      border-right: 3px solid var(--brand-primary, #4a89dc);

      .menu-icon {
        color: var(--brand-primary, #4a89dc);
      }
    }
  }

  // 子菜单样式
  :deep(.el-sub-menu) {
    .el-menu-item {
      padding-left: 40px !important;
      min-width: 0;

      &:hover {
        background: var(--bg-hover, #f3f4f6);
      }

      &.is-active {
        background: var(--brand-primary-light, rgba(74, 137, 220, 0.1));
        color: var(--brand-primary, #4a89dc);
        font-weight: 600;
      }
    }
  }

  // 三级菜单
  :deep(.el-sub-menu .el-sub-menu .el-menu-item) {
    padding-left: 60px !important;
  }
}

// ==================== 分组标题 ====================

.menu-group-title {
  padding: 16px 20px 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #6c757d);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  user-select: none;

  .group-icon {
    font-size: 14px;
    color: var(--brand-primary, #4a89dc);
  }

  .group-label {
    flex: 1;
  }
}

.menu-group-divider {
  margin: 12px 0;
  opacity: 0.3;
}

// ==================== 图标样式 ====================

.menu-icon,
.submenu-icon {
  font-size: 18px;
  margin-right: 12px;
  color: var(--text-secondary, #6c757d);
  transition: color 0.3s;
  display: inline-block;
  width: 18px;
  text-align: center;
}

.submenu-icon {
  font-size: 16px;
}

.menu-title {
  font-size: 14px;
  transition: opacity 0.3s;
}

// ==================== 折叠状态 ====================

.sidebar--collapsed {
  .sidebar-menu {
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding: 0 20px !important;
      justify-content: center;

      .menu-icon {
        margin-right: 0;
      }
    }

    :deep(.el-sub-menu__icon-arrow) {
      display: none;
    }
  }
}

// ==================== 页脚（折叠按钮） ====================

.sidebar-footer {
  height: 48px;
  border-top: 1px solid var(--border-light, #e5e7eb);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}

.collapse-button {
  width: 100%;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: var(--border-radius-md, 8px);
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-secondary, #6c757d);

  &:hover {
    background: var(--bg-hover, #f3f4f6);
    color: var(--brand-primary, #4a89dc);
  }

  i {
    font-size: 16px;
    transition: transform 0.3s;
  }
}

// ==================== Element Plus菜单自定义 ====================

:deep(.el-menu) {
  // 移除默认边框
  border: none;

  // 子菜单展开动画
  .el-menu--inline {
    background: var(--bg-light, #f8f9fa);
  }

  // 子菜单标题箭头
  .el-sub-menu__icon-arrow {
    font-size: 12px;
    color: var(--text-secondary, #6c757d);
    transition: transform 0.3s;
  }

  // 展开状态
  .el-sub-menu.is-opened {
    > .el-sub-menu__title {
      .el-sub-menu__icon-arrow {
        transform: rotateZ(180deg);
      }
    }
  }
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .sidebar {
    &:not(.sidebar--collapsed) {
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
    }
  }
}
</style>
