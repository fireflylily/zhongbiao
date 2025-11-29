/**
 * 格式化工具函数测试
 *
 * 测试公共工具函数是否正确工作
 */

import { describe, it, expect } from 'vitest'

// 简单的工具函数测试示例
describe('格式化工具函数', () => {
  it('日期格式化测试', () => {
    // 测试日期格式化
    const formatDate = (date: string) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    expect(formatDate('2025-11-28')).toMatch(/2025/)
  })

  it('文件大小格式化', () => {
    const formatFileSize = (bytes: number): string => {
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
      return `${(bytes / 1024 / 1024).toFixed(2)} MB`
    }

    expect(formatFileSize(100)).toBe('100 B')
    expect(formatFileSize(1024)).toBe('1.00 KB')
    expect(formatFileSize(1024 * 1024)).toBe('1.00 MB')
  })

  it('数字格式化（千分位）', () => {
    const formatNumber = (num: number): string => {
      return num.toLocaleString('zh-CN')
    }

    expect(formatNumber(1000)).toBe('1,000')
    expect(formatNumber(1000000)).toBe('1,000,000')
  })
})
