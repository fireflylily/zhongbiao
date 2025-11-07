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

  // 公共路径 - 部署到 /static/dist/
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
        }
      }
    },

    // 代码分割策略
    chunkSizeWarningLimit: 1000,

    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
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
