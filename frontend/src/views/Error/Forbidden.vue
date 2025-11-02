<!--
  403 无权限访问
-->

<template>
  <div class="error-page forbidden-page">
    <div class="error-container">
      <div class="error-code">403</div>
      <div class="error-title">无权限访问</div>
      <div class="error-description">
        抱歉，您没有权限访问此页面<br />
        请联系管理员获取相应权限
      </div>

      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <i class="bi bi-house-fill"></i>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <i class="bi bi-arrow-left"></i>
          返回上一页
        </el-button>
      </div>
    </div>

    <div class="error-illustration">
      <i class="bi bi-shield-lock illustration-icon"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

/**
 * 返回首页
 */
function goHome(): void {
  router.push('/')
}

/**
 * 返回上一页
 */
function goBack(): void {
  router.back()
}
</script>

<style scoped lang="scss">
.forbidden-page {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-xl, 32px);
  position: relative;
  overflow: hidden;
}

.error-container {
  text-align: center;
  color: white;
  z-index: 2;
  max-width: 600px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: var(--spacing-lg, 24px);
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.error-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: var(--spacing-md, 16px);
}

.error-description {
  font-size: 16px;
  margin-bottom: var(--spacing-xl, 32px);
  opacity: 0.9;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: var(--spacing-md, 16px);
  justify-content: center;
  flex-wrap: wrap;

  :deep(.el-button) {
    padding: 12px 24px;
    font-size: 14px;

    i {
      margin-right: 8px;
    }
  }
}

.error-illustration {
  position: absolute;
  right: -100px;
  bottom: -100px;
  opacity: 0.1;
  z-index: 1;
}

.illustration-icon {
  font-size: 400px;
  color: white;
}

@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }

  .error-title {
    font-size: 24px;
  }

  .error-description {
    font-size: 14px;
  }

  .illustration-icon {
    font-size: 250px;
  }
}
</style>
