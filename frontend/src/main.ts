import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

// Element Plus 样式（自动按需引入组件）
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import App from './App.vue'
import router from './router'

// 全局样式
import './assets/styles/global.scss'

// 初始化CSRF Token
async function initCsrfToken() {
  try {
    // 调用后端API获取CSRF token并设置到cookie
    await axios.get('/api/csrf-token', { withCredentials: true })
    console.log('[CSRF] Token initialized successfully')
  } catch (error) {
    console.error('[CSRF] Failed to initialize token:', error)
  }
}

// 初始化应用
async function initApp() {
  // 先获取CSRF token
  await initCsrfToken()

  const app = createApp(App)

  // 状态管理
  app.use(createPinia())

  // 路由
  app.use(router)

  // Element Plus 组件会通过 unplugin-vue-components 自动按需引入
  // 不再需要 app.use(ElementPlus)

  app.mount('#app')
}

// 启动应用
initApp()
