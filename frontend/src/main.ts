import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

// Element Plus 样式 - 只引入必要的基础样式（组件样式由unplugin自动按需引入）
// import 'element-plus/dist/index.css'  // 删除完整CSS，减少800KB
import 'element-plus/theme-chalk/base.css'  // 基础样式（必需）
import 'element-plus/theme-chalk/dark/css-vars.css'  // 暗色主题变量

// Bootstrap Icons 图标库
import 'bootstrap-icons/font/bootstrap-icons.css'

// Umo Editor 富文本编辑器 - 移至组件内按需导入（优化首屏加载）
// import { useUmoEditor } from '@umoteam/editor'
// import '@umoteam/editor/style'

// Umo Viewer 文档查看器 - 暂不使用
// import { useUmoViewer } from '@umoteam/viewer'
// import '@umoteam/viewer/style'

import App from './App.vue'
import router from './router'

// 全局样式
import './assets/styles/global.scss'
import './assets/styles/editor.scss'

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

  // Umo Editor 富文本编辑器 - 已改为组件内按需导入，减少首屏加载3MB
  // 每个使用RichTextEditor的页面会自动加载Umo Editor
  // 登录页不需要，因此不加载，优化首屏速度

  // Element Plus 组件会通过 unplugin-vue-components 自动按需引入
  // 不再需要 app.use(ElementPlus)

  app.mount('#app')
}

// 启动应用
initApp()
