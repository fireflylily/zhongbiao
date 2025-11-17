<!--
  用户管理页面
  通过iframe嵌入用户管理系统
-->

<template>
  <div class="user-management-wrapper">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <i class="bi-people header-icon"></i>
          <div class="title-group">
            <h1 class="page-title">用户管理</h1>
            <p class="page-description">管理系统用户和角色权限</p>
          </div>
        </div>

        <div class="action-buttons">
          <el-button @click="refreshFrame" :icon="RefreshIcon" circle title="刷新"></el-button>
          <el-button @click="openInNewTab" :icon="ExternalLinkIcon" circle title="在新标签页打开"></el-button>
        </div>
      </div>
    </div>

    <!-- iframe容器 -->
    <div class="iframe-container" v-loading="loading" element-loading-text="加载中...">


      <iframe
        ref="userManagementFrame"
        :src="iframeUrl"
        class="user-management-iframe"
        frameborder="0"
        @load="handleIframeLoad"
        @error="handleIframeError"
      ></iframe>

      <div v-if="error" class="error-overlay">
        <el-result icon="error" title="加载失败" :sub-title="errorMessage">
          <template #extra>
            <el-button type="primary" @click="refreshFrame">重新加载</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh as RefreshIcon, Link as ExternalLinkIcon } from '@element-plus/icons-vue'
import { ElButton, ElResult } from 'element-plus'

// ==================== State ====================

const userManagementFrame = ref<HTMLIFrameElement | null>(null)
const loading = ref(true)
const error = ref(false)
const errorMessage = ref('')

// ==================== Computed ====================

/**
 * iframe URL
 * 使用相对路径指向后端的用户管理页面
 */
const iframeUrl = computed(() => {
  return '/abtest/management'
})

// ==================== Methods ====================

/**
 * iframe加载完成
 */
function handleIframeLoad() {
  loading.value = false
  error.value = false
}

/**
 * iframe加载错误
 */
function handleIframeError() {
  loading.value = false
  error.value = true
  errorMessage.value = '无法加载用户管理页面,请检查服务是否正常运行'
}

/**
 * 刷新iframe
 */
function refreshFrame() {
  if (userManagementFrame.value) {
    loading.value = true
    error.value = false
    userManagementFrame.value.src = userManagementFrame.value.src
  }
}

/**
 * 在新标签页打开
 */
function openInNewTab() {
  window.open(iframeUrl.value, '_blank')
}

// ==================== Lifecycle ====================

onMounted(() => {
  // 设置加载超时
  setTimeout(() => {
    if (loading.value) {
      error.value = true
      loading.value = false
      errorMessage.value = '加载超时,请刷新页面重试'
    }
  }, 10000) // 10秒超时
})
</script>

<style scoped lang="scss">
.user-management-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-light, #f8f9fa);
}

// ==================== 页面头部 ====================

.page-header {
  background: var(--bg-white, #ffffff);
  border-bottom: 1px solid var(--border-light, #e5e7eb);
  padding: 20px 24px;
  flex-shrink: 0;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 32px;
  color: var(--brand-primary, #4a89dc);
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

// ==================== iframe容器 ====================

.iframe-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--bg-white, #ffffff);
  margin: 16px;
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.1));
}

.user-management-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

// ==================== 错误状态 ====================

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-white, #ffffff);
  z-index: 10;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .page-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 20px;
  }

  .iframe-container {
    margin: 12px;
  }
}
</style>
