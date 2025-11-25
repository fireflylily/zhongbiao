import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

// Element Plus 样式（自动按需引入组件）
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

// Bootstrap Icons 图标库
import 'bootstrap-icons/font/bootstrap-icons.css'

// Umo Editor 富文本编辑器
import { useUmoEditor } from '@umoteam/editor'
import '@umoteam/editor/style'  // 导入 Umo Editor 样式

// Umo Viewer 文档查看器
import { useUmoViewer } from '@umoteam/viewer'
import '@umoteam/viewer/style'  // 导入 Umo Viewer 样式

import App from './App.vue'
import router from './router'

// 全局样式
import './assets/styles/global.scss'
import './assets/styles/editor.scss'

// 全局错误处理 - 捕获外部插件引起的错误
window.addEventListener('error', (event) => {
  // 忽略外部脚本（浏览器插件）的错误
  const filename = event.filename || ''
  const message = event.message || ''

  if (
    filename.includes('extension://') ||
    filename.includes('evmAsk') ||
    filename.includes('chrome-extension://') ||
    message.includes('ethereum') ||
    message.includes('Cannot redefine property')
  ) {
    console.warn('[Global] 已忽略外部插件错误:', message)
    event.preventDefault()
    return true
  }
}, true)

// 初始化CSRF Token（后台异步执行，不阻塞应用启动）
async function initCsrfToken() {
  try {
    // 调用后端API获取CSRF token并设置到cookie
    // 添加10秒超时避免无限等待
    await axios.get('/api/csrf-token', {
      withCredentials: true,
      timeout: 10000
    })
    console.log('[CSRF] Token initialized successfully')
  } catch (error) {
    console.warn('[CSRF] Failed to initialize token (app will continue):', error)
  }
}

// 初始化应用
async function initApp() {
  // CSRF token 初始化不再阻塞应用启动
  // 在后台异步执行，失败也不影响应用加载
  initCsrfToken().catch(err => {
    console.warn('[App] CSRF token init failed, but app continues:', err)
  })

  const app = createApp(App)

  // 状态管理
  app.use(createPinia())

  // 路由
  app.use(router)

  // Umo Editor 富文本编辑器 (v8.x)
  try {
    app.use(useUmoEditor, {
      // 简化配置，避免循环依赖
      toolbar: {
        defaultMode: 'ribbon'
      }
    })
    console.log('[App] Umo Editor v8.x 注册成功')
  } catch (error) {
    console.error('[App] Umo Editor 注册失败:', error)
  }

  // Umo Viewer 文档查看器（暂时不使用）
  // try {
  //   app.use(useUmoViewer, {})
  //   console.log('[App] Umo Viewer 注册成功')
  // } catch (error) {
  //   console.error('[App] Umo Viewer 注册失败:', error)
  // }

  // Element Plus 组件会通过 unplugin-vue-components 自动按需引入
  // 不再需要 app.use(ElementPlus)

  app.mount('#app')
}

// 启动应用
initApp()
