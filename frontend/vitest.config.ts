import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  test: {
    // 使用jsdom模拟浏览器环境
    environment: 'jsdom',

    // 全局API（不需要import就能用describe, it, expect等）
    globals: true,

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{js,ts,vue}'],
      exclude: [
        'node_modules/',
        'src/**/*.spec.{js,ts}',
        'src/**/__tests__/',
        'src/main.ts',
        'src/**/*.d.ts'
      ]
    },

    // 测试文件匹配规则
    include: [
      'src/**/*.{test,spec}.{js,ts}',
      'src/**/__tests__/*.{js,ts}'
    ],

    // 设置超时时间
    testTimeout: 10000,
    hookTimeout: 10000
  },

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
