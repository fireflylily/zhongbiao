/**
 * 格式化工具函数
 *
 * 提供各种数据格式化功能：
 * - 日期时间格式化
 * - 数字格式化
 * - 文件大小格式化
 * - 货币格式化
 * - 百分比格式化
 */

import dayjs from 'dayjs'

/**
 * 日期格式化
 *
 * @param date 日期对象、时间戳或日期字符串
 * @param format 格式化模板，默认 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 *
 * @example
 * formatDate(new Date()) // '2025-10-31'
 * formatDate(Date.now(), 'YYYY-MM-DD HH:mm:ss') // '2025-10-31 14:30:45'
 * formatDate('2025-10-31', 'YYYY年MM月DD日') // '2025年10月31日'
 */
export function formatDate(
  date: Date | number | string | null | undefined,
  format: string = 'YYYY-MM-DD'
): string {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 日期时间格式化
 *
 * @param date 日期对象、时间戳或日期字符串
 * @returns 格式化后的日期时间字符串
 *
 * @example
 * formatDateTime(new Date()) // '2025-10-31 14:30:45'
 */
export function formatDateTime(
  date: Date | number | string | null | undefined
): string {
  return formatDate(date, 'YYYY-MM-DD HH:mm:ss')
}

/**
 * 相对时间格式化
 *
 * @param date 日期对象、时间戳或日期字符串
 * @returns 相对时间描述
 *
 * @example
 * formatRelativeTime(Date.now()) // '刚刚'
 * formatRelativeTime(Date.now() - 60000) // '1分钟前'
 * formatRelativeTime(Date.now() - 3600000) // '1小时前'
 */
export function formatRelativeTime(
  date: Date | number | string | null | undefined
): string {
  if (!date) return ''

  const now = Date.now()
  const then = new Date(date).getTime()
  const diff = now - then

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day
  const year = 365 * day

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    const minutes = Math.floor(diff / minute)
    return `${minutes}分钟前`
  } else if (diff < day) {
    const hours = Math.floor(diff / hour)
    return `${hours}小时前`
  } else if (diff < week) {
    const days = Math.floor(diff / day)
    return `${days}天前`
  } else if (diff < month) {
    const weeks = Math.floor(diff / week)
    return `${weeks}周前`
  } else if (diff < year) {
    const months = Math.floor(diff / month)
    return `${months}个月前`
  } else {
    const years = Math.floor(diff / year)
    return `${years}年前`
  }
}

/**
 * 数字格式化（千分位）
 *
 * @param num 数字
 * @param decimals 小数位数，默认0
 * @returns 格式化后的数字字符串
 *
 * @example
 * formatNumber(1234567) // '1,234,567'
 * formatNumber(1234567.89, 2) // '1,234,567.89'
 */
export function formatNumber(
  num: number | string | null | undefined,
  decimals: number = 0
): string {
  if (num === null || num === undefined || num === '') return ''

  const number = typeof num === 'string' ? parseFloat(num) : num
  if (isNaN(number)) return String(num)

  return number.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 文件大小格式化
 *
 * @param bytes 字节数
 * @param decimals 小数位数，默认2
 * @returns 格式化后的文件大小字符串
 *
 * @example
 * formatFileSize(1024) // '1.00 KB'
 * formatFileSize(1048576) // '1.00 MB'
 * formatFileSize(1073741824) // '1.00 GB'
 */
export function formatFileSize(
  bytes: number | null | undefined,
  decimals: number = 2
): string {
  if (bytes === null || bytes === undefined || bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${(bytes / Math.pow(k, i)).toFixed(decimals)} ${sizes[i]}`
}

/**
 * 货币格式化
 *
 * @param amount 金额
 * @param currency 货币符号，默认'¥'
 * @param decimals 小数位数，默认2
 * @returns 格式化后的货币字符串
 *
 * @example
 * formatCurrency(1234567.89) // '¥1,234,567.89'
 * formatCurrency(1234567.89, '$') // '$1,234,567.89'
 * formatCurrency(1234567, '¥', 0) // '¥1,234,567'
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  currency: string = '¥',
  decimals: number = 2
): string {
  if (amount === null || amount === undefined || amount === '') return ''

  const number = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(number)) return String(amount)

  return `${currency}${formatNumber(number, decimals)}`
}

/**
 * 百分比格式化
 *
 * @param value 数值（0-1之间）
 * @param decimals 小数位数，默认2
 * @returns 格式化后的百分比字符串
 *
 * @example
 * formatPercentage(0.1234) // '12.34%'
 * formatPercentage(0.5, 0) // '50%'
 * formatPercentage(1.234, 1) // '123.4%'
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined) return ''
  return `${(value * 100).toFixed(decimals)}%`
}

/**
 * 手机号格式化（中间4位隐藏）
 *
 * @param phone 手机号
 * @returns 格式化后的手机号
 *
 * @example
 * formatPhone('13812345678') // '138****5678'
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 身份证号格式化（中间部分隐藏）
 *
 * @param idCard 身份证号
 * @returns 格式化后的身份证号
 *
 * @example
 * formatIdCard('110101199001011234') // '110101********1234'
 */
export function formatIdCard(idCard: string | null | undefined): string {
  if (!idCard) return ''
  return idCard.replace(/^(.{6})(.*)(.{4})$/, '$1********$3')
}

/**
 * 银行卡号格式化（每4位空格分隔）
 *
 * @param cardNo 银行卡号
 * @returns 格式化后的银行卡号
 *
 * @example
 * formatBankCard('6222000011112222') // '6222 0000 1111 2222'
 */
export function formatBankCard(cardNo: string | null | undefined): string {
  if (!cardNo) return ''
  return cardNo.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim()
}

/**
 * 文本截断
 *
 * @param text 文本
 * @param maxLength 最大长度
 * @param suffix 后缀，默认'...'
 * @returns 截断后的文本
 *
 * @example
 * truncateText('这是一段很长的文本内容', 10) // '这是一段很长的文本...'
 * truncateText('短文本', 10) // '短文本'
 */
export function truncateText(
  text: string | null | undefined,
  maxLength: number,
  suffix: string = '...'
): string {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + suffix
}

/**
 * 下划线转驼峰
 *
 * @param str 下划线字符串
 * @returns 驼峰字符串
 *
 * @example
 * toCamelCase('user_name') // 'userName'
 * toCamelCase('project_id') // 'projectId'
 */
export function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

/**
 * 驼峰转下划线
 *
 * @param str 驼峰字符串
 * @returns 下划线字符串
 *
 * @example
 * toSnakeCase('userName') // 'user_name'
 * toSnakeCase('projectId') // 'project_id'
 */
export function toSnakeCase(str: string): string {
  return str.replace(/([A-Z])/g, '_$1').toLowerCase().replace(/^_/, '')
}

/**
 * 首字母大写
 *
 * @param str 字符串
 * @returns 首字母大写的字符串
 *
 * @example
 * capitalize('hello') // 'Hello'
 * capitalize('WORLD') // 'WORLD'
 */
export function capitalize(str: string): string {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * 对象转URL参数
 *
 * @param params 参数对象
 * @returns URL参数字符串
 *
 * @example
 * objectToQueryString({ page: 1, size: 20 }) // 'page=1&size=20'
 */
export function objectToQueryString(params: Record<string, any>): string {
  return Object.keys(params)
    .filter((key) => params[key] !== null && params[key] !== undefined)
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')
}

/**
 * URL参数转对象
 *
 * @param queryString URL参数字符串
 * @returns 参数对象
 *
 * @example
 * queryStringToObject('page=1&size=20') // { page: '1', size: '20' }
 */
export function queryStringToObject(queryString: string): Record<string, string> {
  const params: Record<string, string> = {}
  const search = queryString.startsWith('?') ? queryString.slice(1) : queryString

  search.split('&').forEach((pair) => {
    const [key, value] = pair.split('=')
    if (key) {
      params[decodeURIComponent(key)] = decodeURIComponent(value || '')
    }
  })

  return params
}
