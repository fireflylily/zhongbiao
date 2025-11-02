import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import App from './App.vue'
import router from './router'

// 全局样式
import './assets/styles/global.scss'

const app = createApp(App)

// 状态管理
app.use(createPinia())

// 路由
app.use(router)

// UI组件库
app.use(ElementPlus)

app.mount('#app')
