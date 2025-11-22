import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // Element Plus 按需引入
    AutoImport({
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    })
  ],

  // 公共路径 - 静态资源路径(必须匹配Flask的static路由)
  base: '/static/dist/',

  // 公共静态资源目录（明确指定，修复logo.svg加载问题）
  publicDir: 'public',

  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },

  // 开发服务器配置
  server: {
    port: 5173,
    proxy: {
      // 代理所有API请求到Flask后端
      '/api': {
        target: 'http://localhost:8110',
        changeOrigin: true
      },
      // 代理文件下载请求
      '/download': {
        target: 'http://localhost:8110',
        changeOrigin: true
      },
      // 代理静态文件请求
      '/static/uploads': {
        target: 'http://localhost:8110',
        changeOrigin: true
      },
      '/static/outputs': {
        target: 'http://localhost:8110',
        changeOrigin: true
      }
    }
  },

  // 构建配置
  build: {
    // 输出到Flask的static目录
    outDir: path.resolve(__dirname, '../ai_tender_system/web/static/dist'),
    emptyOutDir: true,

    // 生成manifest文件,方便Flask引用
    manifest: true,

    rollupOptions: {
      output: {
        // 固定chunk名称,避免hash变化
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]

          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(assetInfo.name)) {
            return 'images/[name]-[hash][extname]'
          }

          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return 'fonts/[name]-[hash][extname]'
          }

          if (ext === 'css') {
            return 'css/[name]-[hash][extname]'
          }

          return 'assets/[name]-[hash][extname]'
        },
        // 🚀 优化代码分割 - 将超大依赖单独打包
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            // 将超大依赖单独打包，避免阻塞主包
            if (id.includes('onnxruntime-web')) {
              return 'onnxruntime'
            }
            if (id.includes('@umoteam')) {
              return 'umo-editor'
            }
            if (id.includes('element-plus')) {
              return 'element-plus'
            }
            if (id.includes('echarts')) {
              return 'echarts'
            }
            if (id.includes('mermaid')) {
              return 'mermaid'
            }
            // 其他依赖打包到vendor
            return 'vendor'
          }
        }
      }
    },

    // 代码分割策略
    chunkSizeWarningLimit: 2000,

    // 压缩配置 - 使用esbuild替代terser，速度快10倍以上
    minify: 'esbuild',

    // 禁用source map以加快构建
    sourcemap: false
  },

  // CSS配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  }
})
