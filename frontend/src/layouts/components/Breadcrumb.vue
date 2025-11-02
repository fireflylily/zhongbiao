<!--
  Breadcrumb - 面包屑导航组件

  功能：
  - 自动基于路由生成面包屑
  - 支持点击跳转
  - 显示图标
  - 响应式适配
-->

<template>
  <div class="breadcrumb-wrapper" v-if="breadcrumbs.length > 0">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item
        v-for="(crumb, index) in breadcrumbs"
        :key="index"
        :to="crumb.path ? { path: crumb.path } : undefined"
      >
        <span class="breadcrumb-item">
          <i
            v-if="crumb.icon && showIcon"
            :class="crumb.icon"
            class="breadcrumb-icon"
          ></i>
          <span>{{ crumb.title }}</span>
        </span>
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getBreadcrumbs } from '@/router/utils'
import type { Breadcrumb as BreadcrumbType } from '@/types'

// ==================== Props ====================

interface Props {
  showIcon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showIcon: true
})

// ==================== State ====================

const route = useRoute()

// ==================== Computed ====================

/**
 * 面包屑列表
 */
const breadcrumbs = computed((): BreadcrumbType[] => {
  return getBreadcrumbs(route)
})
</script>

<style scoped lang="scss">
.breadcrumb-wrapper {
  display: flex;
  align-items: center;
  min-height: 40px;
}

.breadcrumb-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-primary, #333);
  transition: color 0.3s;

  &:hover {
    color: var(--brand-primary, #4a89dc);
  }
}

.breadcrumb-icon {
  font-size: 14px;
}

// ==================== Element Plus自定义 ====================

:deep(.el-breadcrumb) {
  font-size: 14px;

  .el-breadcrumb__item {
    .el-breadcrumb__inner {
      font-weight: 400;
      color: var(--text-secondary, #6c757d);
      transition: color 0.3s;

      &:hover {
        color: var(--brand-primary, #4a89dc);
      }

      &.is-link {
        font-weight: 400;
      }
    }

    &:last-child {
      .el-breadcrumb__inner {
        color: var(--text-primary, #333);
        font-weight: 500;
      }
    }
  }

  .el-breadcrumb__separator {
    color: var(--text-secondary, #6c757d);
    margin: 0 8px;
  }
}

// ==================== 响应式 ====================

@media (max-width: 576px) {
  .breadcrumb-wrapper {
    :deep(.el-breadcrumb) {
      font-size: 13px;
    }

    .breadcrumb-icon {
      font-size: 13px;
    }
  }
}
</style>
