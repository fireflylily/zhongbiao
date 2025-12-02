<!--
  登录页面
-->

<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo和标题 -->
      <div class="login-header">
        <div class="logo">
          <i class="bi bi-lightbulb-fill"></i>
        </div>
        <h1 class="title">AI智能标书生成平台</h1>
        <p class="subtitle">让投标更简单、更智能</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <i class="bi bi-person-fill"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <i class="bi bi-lock-fill"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码?</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 页脚信息 -->
      <div class="login-footer">
        <p class="copyright">© 2025 AI智能标书生成平台. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables'
import type { FormInstance, FormRules } from 'element-plus'

// ==================== Composables ====================

const router = useRouter()
const userStore = useUserStore()
const { success, error: showError } = useNotification()

// ==================== State ====================

const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度在 6 到 32 个字符', trigger: 'blur' }
  ]
}

// ==================== Lifecycle ====================

/**
 * 组件挂载时恢复记住的用户名和密码
 */
onMounted(() => {
  try {
    const savedUsername = localStorage.getItem('remembered_username')
    const savedPassword = localStorage.getItem('remembered_password')
    const savedRemember = localStorage.getItem('remember_me')

    if (savedRemember === 'true' && savedUsername && savedPassword) {
      loginForm.username = savedUsername
      loginForm.password = savedPassword
      loginForm.remember = true
    }
  } catch (err) {
    console.error('恢复记住的密码失败:', err)
  }
})

// ==================== Methods ====================

/**
 * 处理登录
 */
async function handleLogin(): Promise<void> {
  if (!formRef.value) return

  try {
    // 验证表单
    await formRef.value.validate()

    loading.value = true

    // 调用登录API
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    // 处理"记住我"功能
    if (loginForm.remember) {
      // 保存用户名和密码
      localStorage.setItem('remembered_username', loginForm.username)
      localStorage.setItem('remembered_password', loginForm.password)
      localStorage.setItem('remember_me', 'true')
    } else {
      // 清除保存的用户名和密码
      localStorage.removeItem('remembered_username')
      localStorage.removeItem('remembered_password')
      localStorage.removeItem('remember_me')
    }

    success('登录成功')

    // 跳转到首页
    router.push('/')
  } catch (err: any) {
    if (err.message) {
      showError('登录失败: ' + err.message)
    }
    // 表单验证失败时不显示错误
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

// ==================== 背景装饰 ====================

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 400px;
  height: 400px;
  bottom: -150px;
  right: -150px;
  animation-delay: 2s;
}

.circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: 10%;
  animation-delay: 4s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-30px) scale(1.05);
  }
}

// ==================== 登录卡片 ====================

.login-card {
  width: 100%;
  max-width: 440px;
  padding: var(--spacing-xl, 48px);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg, 16px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 2;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// ==================== 头部 ====================

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl, 32px);
}

.logo {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--spacing-lg, 24px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);

  i {
    font-size: 40px;
    color: white;
  }
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin: 0 0 var(--spacing-sm, 8px) 0;
}

.subtitle {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0;
}

// ==================== 表单 ====================

.login-form {
  margin-bottom: var(--spacing-lg, 24px);

  :deep(.el-form-item) {
    margin-bottom: var(--spacing-lg, 24px);
  }

  :deep(.el-input__wrapper) {
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  :deep(.el-input__prefix) {
    font-size: 18px;
    color: var(--text-secondary, #666);
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }
}

// ==================== 页脚 ====================

.login-footer {
  text-align: center;
  padding-top: var(--spacing-lg, 24px);
  border-top: 1px solid var(--border-light, #e8e8e8);
}

.copyright {
  font-size: 12px;
  color: var(--text-secondary, #999);
  margin: 0;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .login-card {
    max-width: 90%;
    padding: var(--spacing-lg, 24px);
  }

  .logo {
    width: 64px;
    height: 64px;

    i {
      font-size: 32px;
    }
  }

  .title {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }
}
</style>
