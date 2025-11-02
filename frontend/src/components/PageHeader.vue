<!--
  PageHeader - 页面头部组件

  功能：
  - 页面标题和描述
  - 返回按钮
  - 操作按钮区域
  - 标签/状态显示
  - 响应式布局
-->

<template>
  <div class="page-header" :class="{ 'page-header--ghost': ghost }">
    <!-- 返回区域 -->
    <div v-if="showBack" class="page-header-back" @click="handleBack">
      <i class="bi bi-arrow-left back-icon"></i>
      <span class="back-text">{{ backText }}</span>
    </div>

    <!-- 主要内容 -->
    <div class="page-header-main">
      <!-- 左侧：标题区域 -->
      <div class="page-header-heading">
        <!-- 标题 -->
        <div class="heading-title">
          <slot name="title">
            <h1 class="title-text">{{ title }}</h1>
          </slot>
          <!-- 标签（可选） -->
          <div v-if="$slots.tags || tags" class="heading-tags">
            <slot name="tags">
              <el-tag
                v-for="(tag, index) in tags"
                :key="index"
                :type="tag.type"
                :size="tag.size || 'default'"
              >
                {{ tag.text }}
              </el-tag>
            </slot>
          </div>
        </div>

        <!-- 描述 -->
        <div v-if="$slots.description || description" class="heading-description">
          <slot name="description">
            <p class="description-text">{{ description }}</p>
          </slot>
        </div>

        <!-- 额外信息 -->
        <div v-if="$slots.extra" class="heading-extra">
          <slot name="extra"></slot>
        </div>
      </div>

      <!-- 右侧：操作区域 -->
      <div v-if="$slots.actions" class="page-header-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- 底部内容（可选） -->
    <div v-if="$slots.footer" class="page-header-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

// ==================== Types ====================

interface Tag {
  text: string
  type?: 'success' | 'info' | 'warning' | 'danger'
  size?: 'large' | 'default' | 'small'
}

// ==================== Props ====================

interface Props {
  title?: string
  description?: string
  showBack?: boolean
  backText?: string
  ghost?: boolean
  tags?: Tag[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  description: '',
  showBack: false,
  backText: '返回',
  ghost: false,
  tags: () => []
})

const emit = defineEmits<{
  (e: 'back'): void
}>()

// ==================== State ====================

const router = useRouter()

// ==================== Methods ====================

/**
 * 处理返回按钮点击
 */
function handleBack(): void {
  emit('back')
  // 如果没有监听back事件，默认使用router.back()
  if (!emit('back')) {
    router.back()
  }
}
</script>

<style scoped lang="scss">
.page-header {
  background: var(--bg-white, #ffffff);
  padding: 20px 24px;
  margin-bottom: 16px;
  border-radius: var(--border-radius-md, 8px);

  &.page-header--ghost {
    background: transparent;
    padding-left: 0;
    padding-right: 0;
  }
}

// ==================== 返回按钮 ====================

.page-header-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 6px 12px;
  border-radius: var(--border-radius-md, 8px);
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;

  &:hover {
    background: var(--bg-hover, #f3f4f6);
    color: var(--brand-primary, #4a89dc);

    .back-icon {
      transform: translateX(-2px);
    }
  }

  .back-icon {
    font-size: 18px;
    transition: transform 0.3s;
  }

  .back-text {
    font-size: 14px;
    font-weight: 500;
  }
}

// ==================== 主要内容 ====================

.page-header-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

// ==================== 标题区域 ====================

.page-header-heading {
  flex: 1;
  min-width: 0;
}

.heading-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.title-text {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #333);
  line-height: 1.4;
}

.heading-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.heading-description {
  margin-top: 8px;
}

.description-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
  line-height: 1.6;
}

.heading-extra {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
}

// ==================== 操作区域 ====================

.page-header-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;

  :deep(.el-button) {
    margin: 0;
  }
}

// ==================== 底部内容 ====================

.page-header-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light, #e5e7eb);
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .page-header {
    padding: 16px;
    margin-bottom: 12px;
  }

  .page-header-main {
    flex-direction: column;
    gap: 16px;
  }

  .page-header-back {
    margin-bottom: 12px;
  }

  .title-text {
    font-size: 20px;
  }

  .description-text {
    font-size: 13px;
  }

  .page-header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .page-header-footer {
    margin-top: 16px;
    padding-top: 16px;
  }
}
</style>
