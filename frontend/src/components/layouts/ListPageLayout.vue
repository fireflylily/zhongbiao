<template>
  <div class="list-page-layout">
    <!-- 统计卡片区（可选） -->
    <div v-if="$slots.stats" class="stats-bar">
      <slot name="stats" />
    </div>

    <!-- 主内容卡片 -->
    <Card :title="title">
      <!-- 头部操作按钮（可选） -->
      <template v-if="$slots.actions" #actions>
        <slot name="actions" />
      </template>

      <!-- 筛选区（可选） -->
      <div v-if="$slots.filters" class="filter-section">
        <slot name="filters" />
      </div>

      <!-- 加载状态 -->
      <Loading v-if="loading" :text="loadingText" />

      <!-- 空状态 -->
      <Empty
        v-else-if="isEmpty"
        :type="emptyType"
        :description="emptyDescription"
      />

      <!-- 主内容区（必需） -->
      <div v-else class="content-area">
        <slot name="content" />
      </div>

      <!-- 分页区（可选） -->
      <div v-if="$slots.pagination && !isEmpty && !loading" class="pagination-wrapper">
        <slot name="pagination" />
      </div>
    </Card>

    <!-- 对话框/其他（可选） -->
    <slot name="dialogs" />
  </div>
</template>

<script setup lang="ts">
import { Card, Loading, Empty } from '@/components'

/**
 * 列表页统一布局组件
 *
 * @description
 * 提供统一的列表页布局，包括：
 * - 可选的统计卡片区
 * - 可选的筛选区
 * - 必需的内容区（表格/卡片等）
 * - 可选的分页区
 * - 可选的对话框区
 *
 * @example
 * ```vue
 * <ListPageLayout
 *   title="项目列表"
 *   :loading="loading"
 *   :is-empty="!projects.length"
 *   empty-description="暂无项目"
 * >
 *   <template #actions>
 *     <el-button @click="handleCreate">新建</el-button>
 *   </template>
 *
 *   <template #content>
 *     <el-table :data="projects">...</el-table>
 *   </template>
 *
 *   <template #pagination>
 *     <el-pagination />
 *   </template>
 * </ListPageLayout>
 * ```
 */

interface Props {
  /** Card 标题 */
  title: string
  /** 是否正在加载 */
  loading?: boolean
  /** 加载提示文本 */
  loadingText?: string
  /** 是否为空（无数据） */
  isEmpty?: boolean
  /** 空状态类型 */
  emptyType?: 'no-data' | 'no-result'
  /** 空状态描述文本 */
  emptyDescription?: string
}

withDefaults(defineProps<Props>(), {
  loading: false,
  loadingText: '加载中...',
  isEmpty: false,
  emptyType: 'no-data',
  emptyDescription: '暂无数据'
})
</script>

<style scoped lang="scss">
.list-page-layout {
  padding: var(--spacing-lg, 20px);

  // ==================== 统计卡片区 ====================
  .stats-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;

    // 统计卡片的通用样式（由父组件通过插槽提供的卡片继承）
    :deep(.stat-card) {
      flex: 1;
      cursor: default;

      .el-card__body {
        padding: 16px;
      }
    }
  }

  // ==================== 筛选区 ====================
  .filter-section {
    margin-bottom: 16px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 4px;

    :deep(.el-form-item) {
      margin-bottom: 0;
    }

    :deep(.el-form--inline .el-form-item) {
      margin-right: 16px;
    }
  }

  // ==================== 内容区 ====================
  .content-area {
    // 内容区域的样式由插槽内容决定
    // 这里只提供基本的容器
  }

  // ==================== 分页区 ====================
  .pagination-wrapper {
    margin-top: var(--spacing-lg, 24px);
    display: flex;
    justify-content: flex-end;

    :deep(.el-pagination) {
      // Element Plus 分页组件的默认样式
    }
  }
}

// ==================== 响应式 ====================
@media (max-width: 768px) {
  .list-page-layout {
    padding: var(--spacing-md, 16px);

    .stats-bar {
      flex-direction: column;
      gap: 12px;
    }

    .pagination-wrapper {
      justify-content: center;

      :deep(.el-pagination) {
        flex-wrap: wrap;
        justify-content: center;
      }
    }
  }
}
</style>
