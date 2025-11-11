<!--
  TenderDocumentFloatingButton - 标书预览悬浮按钮

  功能：
  - 全局悬浮按钮，固定在右下角
  - 点击快速预览当前项目的标书文档
  - 只在有当前项目且有标书文件时显示
  - 集成DocumentPreview组件
-->

<template>
  <transition name="fade-slide">
    <div
      v-if="shouldShow"
      class="tender-document-floating-button"
    >
      <el-tooltip
        content="点击预览当前项目的招标文档"
        placement="left"
        :show-after="500"
      >
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handlePreview"
          class="floating-btn"
        >
          <el-icon class="btn-icon"><DocumentIcon /></el-icon>
          <span class="btn-text">预览标书</span>
        </el-button>
      </el-tooltip>

      <!-- 文档预览组件 -->
      <DocumentPreview
        v-model="previewVisible"
        :file-url="tenderDocumentPath"
        :file-name="tenderDocumentName"
      />
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { Document as DocumentIcon } from '@element-plus/icons-vue'
import DocumentPreview from './DocumentPreview.vue'

// ==================== State ====================

const projectStore = useProjectStore()
const previewVisible = ref(false)
const loading = ref(false)

// ==================== Computed ====================

/**
 * 是否应该显示悬浮按钮
 * 条件：有当前项目 && 有标书文档路径
 */
const shouldShow = computed(() => {
  const hasProject = projectStore.hasCurrentProject
  const currentProj = projectStore.currentProject
  const hasTenderDoc = !!currentProj?.tender_document_path

  // 保留轻量级日志（可选）
  if (hasProject && !hasTenderDoc) {
    console.log('[悬浮按钮] 项目已选择但没有标书文档:', currentProj?.id, currentProj?.project_name)
  }

  return hasProject && hasTenderDoc
})

/**
 * 标书文档路径
 */
const tenderDocumentPath = computed(() => {
  return projectStore.currentProject?.tender_document_path || ''
})

/**
 * 标书文档名称（用于预览标题）
 */
const tenderDocumentName = computed(() => {
  const projectName = projectStore.currentProject?.project_name ||
                     projectStore.currentProject?.name ||
                     '未命名项目'
  return `${projectName} - 招标文档`
})

// ==================== Methods ====================

/**
 * 处理预览按钮点击
 */
function handlePreview(): void {
  if (!tenderDocumentPath.value) {
    ElMessage.warning('当前项目没有招标文档')
    return
  }

  // 打开预览对话框
  previewVisible.value = true
}
</script>

<style scoped lang="scss">
.tender-document-floating-button {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 1000;

  .floating-btn {
    // 胶囊按钮样式（图标 + 文字）
    height: 48px;
    padding: 0 24px 0 20px;
    font-size: 15px;
    font-weight: 600;
    border-radius: 24px;
    box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    // 呼吸动画 - 吸引注意力
    animation: breath 2s ease-in-out infinite;

    // 按钮内部布局
    display: inline-flex;
    align-items: center;
    gap: 8px;

    .btn-icon {
      font-size: 20px;
    }

    .btn-text {
      line-height: 1;
      white-space: nowrap;
    }

    &:hover {
      transform: translateY(-4px) scale(1.05);
      box-shadow: 0 10px 28px rgba(64, 158, 255, 0.6);
      animation: none; // 悬停时停止呼吸动画
    }

    &:active {
      transform: translateY(-2px) scale(1.02);
    }

    // 加载状态下的样式
    &.is-loading {
      pointer-events: none;
      opacity: 0.8;
    }
  }
}

// 呼吸动画
@keyframes breath {
  0%, 100% {
    box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
  }
  50% {
    box-shadow: 0 6px 20px rgba(64, 158, 255, 0.7);
  }
}

// ==================== 动画效果 ====================

// 淡入淡出 + 滑动动画
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

// ==================== 响应式设计 ====================

// 平板设备
@media (max-width: 1024px) {
  .tender-document-floating-button {
    right: 20px;
    bottom: 20px;

    .floating-btn {
      height: 44px;
      padding: 0 20px 0 16px;
      font-size: 14px;

      .btn-icon {
        font-size: 18px;
      }
    }
  }
}

// 移动设备 - 只显示图标
@media (max-width: 768px) {
  .tender-document-floating-button {
    right: 16px;
    bottom: 16px;

    .floating-btn {
      height: 48px;
      width: 48px;
      padding: 0;
      border-radius: 50%;

      .btn-text {
        display: none; // 移动端隐藏文字
      }

      .btn-icon {
        font-size: 22px;
      }
    }
  }
}

// 小屏移动设备
@media (max-width: 480px) {
  .tender-document-floating-button {
    right: 12px;
    bottom: 12px;

    .floating-btn {
      height: 44px;
      width: 44px;

      .btn-icon {
        font-size: 20px;
      }
    }
  }
}
</style>
