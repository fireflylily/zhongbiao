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
    <!-- 主要内容 -->
    <div class="page-header-main">
      <!-- 返回按钮（整合到主要内容中） -->
      <div v-if="showBack" class="page-header-back" @click="handleBack">
        <i class="bi bi-arrow-left back-icon"></i>
        <span class="back-text">{{ backText }}</span>
      </div>

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
  padding: 12px 20px;
  margin-bottom: 12px;
  border-radius: var(--border-radius-md, 8px);

  &.page-header--ghost {
    background: transparent;
    padding-left: 0;
    padding-right: 0;
  }
}

// ==================== 主要内容 ====================

.page-header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

// ==================== 返回按钮 ====================

.page-header-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--border-radius-md, 8px);
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
  flex-shrink: 0;

  &:hover {
    background: var(--bg-hover, #f3f4f6);
    color: var(--brand-primary, #4a89dc);

    .back-icon {
      transform: translateX(-2px);
    }
  }

  .back-icon {
    font-size: 16px;
    transition: transform 0.3s;
  }

  .back-text {
    font-size: 14px;
    font-weight: 500;
  }
}

// ==================== 标题区域 ====================

.page-header-heading {
  flex: 1;
  min-width: 0;
}

.heading-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.title-text {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #333);
  line-height: 1.3;
}

.heading-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.heading-description {
  margin-top: 6px;
}

.description-text {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
  line-height: 1.5;
}

.heading-extra {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
}

// ==================== 操作区域 ====================

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex-shrink: 0;

  :deep(.el-button) {
    margin: 0;
  }
}

// ==================== 底部内容 ====================

.page-header-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light, #e5e7eb);
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
    margin-bottom: 10px;
  }

  .page-header-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header-back {
    margin-bottom: 0;
  }

  .title-text {
    font-size: 18px;
  }

  .description-text {
    font-size: 12px;
  }

  .page-header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .page-header-footer {
    margin-top: 12px;
    padding-top: 12px;
  }
}
</style>
