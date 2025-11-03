import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Element Plus 样式（自动按需引入组件）
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

// Element Plus 组件会通过 unplugin-vue-components 自动按需引入
// 不再需要 app.use(ElementPlus)

app.mount('#app')
