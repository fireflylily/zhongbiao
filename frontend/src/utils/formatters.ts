/**
 * 格式化工具函数
 * @module utils/formatters
 */

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小字符串
 * @example
 * formatFileSize(1024) // '1 KB'
 * formatFileSize(1048576) // '1 MB'
 * formatFileSize(1073741824) // '1 GB'
 */
export const formatFileSize = (bytes: number): string => {
  if (!bytes || bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
}

/**
 * 格式化日期时间
 * @param dateStr 日期字符串或 Date 对象
 * @param format 格式类型
 * @returns 格式化后的日期字符串
 * @example
 * formatDate('2024-01-01T12:00:00') // '2024-01-01 12:00'
 * formatDate('2024-01-01', 'date') // '2024-01-01'
 * formatDate('2024-01-01', 'datetime-full') // '2024年01月01日 00:00:00'
 */
export const formatDate = (
  dateStr: string | Date,
  format: 'datetime' | 'date' | 'time' | 'datetime-full' = 'datetime'
): string => {
  if (!dateStr) return ''

  const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr

  // 检查日期是否有效
  if (isNaN(date.getTime())) return ''

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')

  switch (format) {
    case 'date':
      return `${year}-${month}-${day}`
    case 'time':
      return `${hour}:${minute}`
    case 'datetime-full':
      return `${year}年${month}月${day}日 ${hour}:${minute}:${second}`
    case 'datetime':
    default:
      return `${year}-${month}-${day} ${hour}:${minute}`
  }
}

/**
 * 格式化金额（人民币）
 * @param amount 金额
 * @param options 格式化选项
 * @returns 格式化后的金额字符串
 * @example
 * formatCurrency(1000) // '¥ 1,000.00'
 * formatCurrency(1000, { symbol: false }) // '1,000.00'
 * formatCurrency(1000.5, { decimals: 0 }) // '¥ 1,001'
 */
export const formatCurrency = (
  amount: number,
  options: {
    symbol?: boolean
    decimals?: number
    locale?: string
  } = {}
): string => {
  const {
    symbol = true,
    decimals = 2,
    locale = 'zh-CN'
  } = options

  if (amount === null || amount === undefined || isNaN(amount)) {
    return symbol ? '¥ 0.00' : '0.00'
  }

  const formatted = amount.toLocaleString(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })

  return symbol ? `¥ ${formatted}` : formatted
}

/**
 * 格式化百分比
 * @param value 数值（0-1 或 0-100）
 * @param options 格式化选项
 * @returns 格式化后的百分比字符串
 * @example
 * formatPercentage(0.5) // '50%'
 * formatPercentage(50, { isDecimal: false }) // '50%'
 * formatPercentage(0.12345, { decimals: 2 }) // '12.35%'
 */
export const formatPercentage = (
  value: number,
  options: {
    isDecimal?: boolean
    decimals?: number
  } = {}
): string => {
  const {
    isDecimal = true,
    decimals = 0
  } = options

  if (value === null || value === undefined || isNaN(value)) return '0%'

  const percentage = isDecimal ? value * 100 : value

  return `${percentage.toFixed(decimals)}%`
}

/**
 * 格式化数字（添加千分位）
 * @param num 数字
 * @param decimals 小数位数
 * @returns 格式化后的数字字符串
 * @example
 * formatNumber(1000) // '1,000'
 * formatNumber(1000.5, 2) // '1,000.50'
 */
export const formatNumber = (num: number, decimals: number = 0): string => {
  if (num === null || num === undefined || isNaN(num)) return '0'

  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 格式化手机号（隐藏中间4位）
 * @param phone 手机号
 * @returns 格式化后的手机号
 * @example
 * formatPhone('13812345678') // '138****5678'
 */
export const formatPhone = (phone: string): string => {
  if (!phone || phone.length !== 11) return phone

  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 格式化身份证号（隐藏中间部分）
 * @param idCard 身份证号
 * @returns 格式化后的身份证号
 * @example
 * formatIdCard('123456789012345678') // '1234**********5678'
 */
export const formatIdCard = (idCard: string): string => {
  if (!idCard || (idCard.length !== 15 && idCard.length !== 18)) return idCard

  if (idCard.length === 15) {
    return idCard.replace(/(\d{4})\d{7}(\d{4})/, '$1*******$2')
  } else {
    return idCard.replace(/(\d{4})\d{10}(\d{4})/, '$1**********$2')
  }
}

/**
 * 格式化银行卡号（每4位空格分隔）
 * @param cardNumber 银行卡号
 * @returns 格式化后的银行卡号
 * @example
 * formatBankCard('6222021234567890') // '6222 0212 3456 7890'
 */
export const formatBankCard = (cardNumber: string): string => {
  if (!cardNumber) return ''

  return cardNumber.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim()
}

/**
 * 截断文本（超出长度显示省略号）
 * @param text 文本
 * @param maxLength 最大长度
 * @param ellipsis 省略号
 * @returns 截断后的文本
 * @example
 * truncateText('这是一段很长的文本', 5) // '这是一段很...'
 */
export const truncateText = (
  text: string,
  maxLength: number,
  ellipsis: string = '...'
): string => {
  if (!text || text.length <= maxLength) return text

  return text.slice(0, maxLength) + ellipsis
}

/**
 * 格式化时间距离（多久之前）
 * @param dateStr 日期字符串
 * @returns 相对时间字符串
 * @example
 * formatTimeAgo('2024-01-01') // '3天前'
 * formatTimeAgo('2024-01-01T10:00:00') // '刚刚'
 */
export const formatTimeAgo = (dateStr: string | Date): string => {
  if (!dateStr) return ''

  const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)

  if (seconds < 60) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  if (months < 12) return `${months}个月前`
  return `${years}年前`
}
