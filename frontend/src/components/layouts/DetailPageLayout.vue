<template>
  <div class="detail-page-layout" :class="[`mode-${mode}`]">
    <!-- Simple 模式：简单顶部导航 -->
    <div v-if="mode === 'simple'" class="detail-header simple">
      <el-button @click="handleBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <div class="header-title">
        <slot name="header-title">
          <h2>{{ title }}</h2>
        </slot>
      </div>
    </div>

    <!-- Advanced 模式：使用 PageHeader 组件 -->
    <PageHeader v-else-if="mode === 'advanced'" :title="title" :show-back="true">
      <template v-if="$slots['header-actions']" #actions>
        <slot name="header-actions" />
      </template>
    </PageHeader>

    <!-- 顶部额外内容（可选，仅 Advanced 模式） -->
    <div v-if="mode === 'advanced' && $slots['before-tabs']" class="before-tabs">
      <slot name="before-tabs" />
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading" :text="loadingText" />

    <!-- Tab 内容 -->
    <template v-else-if="$slots.tabs">
      <!-- Simple 模式：简单容器 -->
      <div v-if="mode === 'simple'" class="detail-content">
        <el-tabs v-model="activeTabValue" class="detail-tabs" @tab-change="handleTabChange">
          <slot name="tabs" />
        </el-tabs>
      </div>

      <!-- Advanced 模式：使用卡片 -->
      <el-card v-else class="tabs-card" shadow="never">
        <el-tabs v-model="activeTabValue" class="detail-tabs" @tab-change="handleTabChange">
          <slot name="tabs" />
        </el-tabs>
      </el-card>
    </template>

    <!-- 错误状态 -->
    <Empty v-else :description="errorDescription" type="no-data" />

    <!-- 对话框/其他（可选） -->
    <slot name="dialogs" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, Empty } from '@/components'
import { ArrowLeft } from '@element-plus/icons-vue'

// 动态导入 PageHeader（仅在 advanced 模式需要）
const PageHeader = defineAsyncComponent(() => import('@/components/PageHeader.vue'))

/**
 * 详情页统一布局组件
 *
 * @description
 * 提供两种模式的详情页布局：
 * - simple: 简单模式（企业、文档、案例、简历详情）
 * - advanced: 高级模式（项目详情，支持编辑模式）
 *
 * @example Simple 模式
 * ```vue
 * <DetailPageLayout
 *   mode="simple"
 *   title="企业详情"
 *   :loading="loading"
 *   v-model:active-tab="activeTab"
 * >
 *   <template #header-title>
 *     <h2>{{ companyName }}</h2>
 *     <el-tag>{{ industry }}</el-tag>
 *   </template>
 *
 *   <template #tabs>
 *     <el-tab-pane label="基础信息" name="basic">
 *       <BasicInfoTab />
 *     </el-tab-pane>
 *   </template>
 * </DetailPageLayout>
 * ```
 *
 * @example Advanced 模式
 * ```vue
 * <DetailPageLayout
 *   mode="advanced"
 *   title="项目详情"
 *   :loading="loading"
 *   v-model:active-tab="activeTab"
 * >
 *   <template #header-actions>
 *     <el-button @click="handleEdit">编辑</el-button>
 *   </template>
 *
 *   <template #before-tabs>
 *     <TenderDocumentProcessor />
 *   </template>
 *
 *   <template #tabs>
 *     <el-tab-pane label="基本信息" name="basic">...</el-tab-pane>
 *   </template>
 * </DetailPageLayout>
 * ```
 */

interface Props {
  /** 布局模式：simple（简单） 或 advanced（高级） */
  mode?: 'simple' | 'advanced'
  /** 页面标题 */
  title: string
  /** 是否正在加载 */
  loading?: boolean
  /** 加载提示文本 */
  loadingText?: string
  /** 当前激活的 Tab */
  activeTab?: string
  /** 错误状态描述 */
  errorDescription?: string
  /** 返回路径（可选，默认返回上一页） */
  backPath?: string
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'simple',
  loading: false,
  loadingText: '加载详情中...',
  activeTab: '',
  errorDescription: '数据不存在或加载失败'
})

// Emits
const emit = defineEmits<{
  (e: 'update:activeTab', value: string): void
  (e: 'tab-change', tabName: string): void
}>()

// Router
const router = useRouter()

// 内部状态
const activeTabValue = ref(props.activeTab)

// 监听 prop 变化
watch(() => props.activeTab, (newVal) => {
  activeTabValue.value = newVal
})

// 监听内部状态变化
watch(activeTabValue, (newVal) => {
  emit('update:activeTab', newVal)
})

// 处理返回
const handleBack = () => {
  if (props.backPath) {
    router.push(props.backPath)
  } else {
    router.back()
  }
}

// 处理 Tab 切换
const handleTabChange = (tabName: string | number) => {
  emit('tab-change', String(tabName))
}

// 异步组件
import { defineAsyncComponent } from 'vue'
</script>

<style scoped lang="scss">
.detail-page-layout {
  padding: 20px;
  min-height: calc(100vh - 60px);

  // ==================== Simple 模式样式 ====================
  &.mode-simple {
    background: #f5f7fa;

    .detail-header.simple {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      padding: 16px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

      .header-title {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;

        h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
          color: #303133;
        }
      }
    }

    .detail-content {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      padding: 20px;
    }
  }

  // ==================== Advanced 模式样式 ====================
  &.mode-advanced {
    .before-tabs {
      margin-bottom: 20px;
    }

    .tabs-card {
      :deep(.el-card__body) {
        padding: 0;
      }
    }
  }

  // ==================== Tab 通用样式 ====================
  .detail-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;
    }

    :deep(.el-tabs__nav-wrap::after) {
      height: 1px;
    }

    :deep(.el-tabs__content) {
      // Tab 内容由各个 Tab 组件自行决定
    }

    // Tab 标签样式
    .tab-label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;

      .el-icon {
        font-size: 16px;
      }
    }
  }

  // Advanced 模式的 Tab 样式
  &.mode-advanced .tabs-card .detail-tabs {
    :deep(.el-tabs__header) {
      padding: 0 20px;
      margin-bottom: 0;
    }

    :deep(.el-tabs__content) {
      padding: 30px 20px;
    }
  }
}

// ==================== 响应式 ====================
@media (max-width: 768px) {
  .detail-page-layout {
    padding: 16px;

    &.mode-simple .detail-header.simple {
      flex-direction: column;
      align-items: flex-start;

      .header-title {
        width: 100%;
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }
    }

    .detail-tabs {
      :deep(.el-tabs__nav) {
        flex-wrap: wrap;
      }
    }
  }
}
</style>
