<!--
  Footer - 页脚组件

  功能：
  - 显示版权信息
  - 显示系统版本
  - 显示技术支持信息
  - 响应式适配
-->

<template>
  <footer class="app-footer" :class="footerClasses">
    <div class="footer-content">
      <!-- 版权信息 -->
      <div class="footer-section footer-copyright">
        <span>© {{ currentYear }} 元景AI. All rights reserved.</span>
      </div>

      <!-- 分隔符 -->
      <div class="footer-divider" v-if="!isMobile">|</div>

      <!-- 版本信息 -->
      <div class="footer-section footer-version" v-if="showVersion">
        <span>版本 {{ version }}</span>
      </div>

      <!-- 分隔符 -->
      <div class="footer-divider" v-if="!isMobile && showTechSupport">|</div>

      <!-- 技术支持 -->
      <div class="footer-section footer-support" v-if="showTechSupport">
        <span>技术支持：元景AI团队</span>
      </div>

      <!-- 备案信息（如需要） -->
      <div class="footer-divider" v-if="!isMobile && beian">|</div>
      <div class="footer-section footer-beian" v-if="beian">
        <a :href="beianLink" target="_blank" rel="noopener noreferrer">
          {{ beian }}
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

// ==================== Props ====================

interface Props {
  showVersion?: boolean
  showTechSupport?: boolean
  beian?: string
  beianLink?: string
}

const props = withDefaults(defineProps<Props>(), {
  showVersion: true,
  showTechSupport: true,
  beian: '',
  beianLink: 'https://beian.miit.gov.cn/'
})

// ==================== State ====================

const isMobile = ref(false)

// ==================== Computed ====================

/**
 * 当前年份
 */
const currentYear = computed(() => {
  return new Date().getFullYear()
})

/**
 * 系统版本
 */
const version = computed(() => {
  return import.meta.env.VITE_APP_VERSION || '2.0.0'
})

/**
 * Footer类名
 */
const footerClasses = computed(() => ({
  'footer--mobile': isMobile.value
}))

// ==================== Methods ====================

/**
 * 检查屏幕尺寸
 */
function checkScreenSize(): void {
  isMobile.value = window.innerWidth < 768
}

// ==================== Lifecycle ====================

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<style scoped lang="scss">
.app-footer {
  padding: 16px 24px;
  background: var(--bg-white, #ffffff);
  border-top: 1px solid var(--border-light, #e5e7eb);
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
}

.footer-section {
  display: flex;
  align-items: center;
}

.footer-divider {
  color: var(--border-light, #e5e7eb);
}

.footer-beian {
  a {
    color: var(--text-secondary, #6c757d);
    text-decoration: none;
    transition: color 0.3s;

    &:hover {
      color: var(--brand-primary, #4a89dc);
    }
  }
}

// ==================== 响应式 ====================

.footer--mobile {
  padding: 12px 16px;

  .footer-content {
    flex-direction: column;
    gap: 8px;
    font-size: 12px;
  }
}
</style>
