/**
 * 验证工具函数
 *
 * 提供各种数据验证功能：
 * - 基础验证（必填、长度、范围）
 * - 格式验证（邮箱、手机号、URL等）
 * - 文件验证（类型、大小）
 * - 业务验证（身份证、信用代码等）
 * - Element Plus表单规则
 */

/**
 * 验证规则类型
 */
export interface ValidationRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  validator?: (rule: any, value: any, callback: any) => void
  min?: number
  max?: number
  pattern?: RegExp
  type?: string
}

/**
 * 正则表达式常量
 */
export const PATTERNS = {
  // 邮箱
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  // 手机号（中国大陆）
  PHONE: /^1[3-9]\d{9}$/,
  // 固定电话
  TEL: /^0\d{2,3}-?\d{7,8}$/,
  // URL
  URL: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  // IP地址
  IP: /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/,
  // 身份证号（18位）
  ID_CARD: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
  // 统一社会信用代码
  CREDIT_CODE: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/,
  // 邮政编码
  POSTAL_CODE: /^\d{6}$/,
  // 中文字符
  CHINESE: /^[\u4e00-\u9fa5]+$/,
  // 英文字母
  LETTER: /^[a-zA-Z]+$/,
  // 数字
  NUMBER: /^\d+$/,
  // 字母数字
  ALPHANUMERIC: /^[a-zA-Z0-9]+$/,
  // 用户名（字母开头，字母数字下划线，3-16位）
  USERNAME: /^[a-zA-Z][a-zA-Z0-9_]{2,15}$/,
  // 密码（至少包含字母和数字，6-20位）
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,20}$/
}

/**
 * 是否为空
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 是否为邮箱
 */
export function isEmail(value: string): boolean {
  return PATTERNS.EMAIL.test(value)
}

/**
 * 是否为手机号
 */
export function isPhone(value: string): boolean {
  return PATTERNS.PHONE.test(value)
}

/**
 * 是否为固定电话
 */
export function isTel(value: string): boolean {
  return PATTERNS.TEL.test(value)
}

/**
 * 是否为URL
 */
export function isURL(value: string): boolean {
  return PATTERNS.URL.test(value)
}

/**
 * 是否为IP地址
 */
export function isIP(value: string): boolean {
  return PATTERNS.IP.test(value)
}

/**
 * 是否为身份证号
 */
export function isIdCard(value: string): boolean {
  if (!PATTERNS.ID_CARD.test(value)) return false

  // 校验码验证
  const factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
  const codes = '10X98765432'
  const sum = value
    .substring(0, 17)
    .split('')
    .reduce((acc, char, i) => acc + parseInt(char) * factors[i], 0)
  return codes[sum % 11] === value[17].toUpperCase()
}

/**
 * 是否为统一社会信用代码
 */
export function isCreditCode(value: string): boolean {
  if (!PATTERNS.CREDIT_CODE.test(value)) return false

  // 校验码验证
  const chars = '0123456789ABCDEFGHJKLMNPQRTUWXY'
  const weights = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]
  let sum = 0

  for (let i = 0; i < 17; i++) {
    sum += chars.indexOf(value[i]) * weights[i]
  }

  const checkCode = 31 - (sum % 31)
  return chars[checkCode === 31 ? 0 : checkCode] === value[17]
}

/**
 * 是否为邮政编码
 */
export function isPostalCode(value: string): boolean {
  return PATTERNS.POSTAL_CODE.test(value)
}

/**
 * 是否为中文
 */
export function isChinese(value: string): boolean {
  return PATTERNS.CHINESE.test(value)
}

/**
 * 是否为英文字母
 */
export function isLetter(value: string): boolean {
  return PATTERNS.LETTER.test(value)
}

/**
 * 是否为数字
 */
export function isNumber(value: any): boolean {
  return !isNaN(parseFloat(value)) && isFinite(value)
}

/**
 * 是否为整数
 */
export function isInteger(value: any): boolean {
  return Number.isInteger(Number(value))
}

/**
 * 是否在范围内
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * 是否为有效文件类型
 */
export function isValidFileType(file: File, acceptTypes: string[]): boolean {
  const extension = file.name.split('.').pop()?.toLowerCase()
  return acceptTypes.some((type) => {
    // 支持通配符，如 'image/*'
    if (type.endsWith('/*')) {
      const category = type.split('/')[0]
      return file.type.startsWith(`${category}/`)
    }
    // 支持扩展名，如 '.jpg'
    if (type.startsWith('.')) {
      return extension === type.slice(1)
    }
    // 支持MIME类型，如 'image/jpeg'
    return file.type === type
  })
}

/**
 * 是否超过文件大小限制
 */
export function isValidFileSize(file: File, maxSize: number): boolean {
  return file.size <= maxSize
}

/**
 * 密码强度检查
 * @returns 0-弱 1-中 2-强
 */
export function checkPasswordStrength(password: string): number {
  let strength = 0

  // 长度
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++

  // 包含小写字母
  if (/[a-z]/.test(password)) strength++

  // 包含大写字母
  if (/[A-Z]/.test(password)) strength++

  // 包含数字
  if (/\d/.test(password)) strength++

  // 包含特殊字符
  if (/[@$!%*?&]/.test(password)) strength++

  // 映射到0-2
  if (strength <= 2) return 0 // 弱
  if (strength <= 4) return 1 // 中
  return 2 // 强
}

// ============ Element Plus 表单规则 ============

/**
 * 必填规则
 */
export function required(message: string = '此项为必填项'): ValidationRule {
  return {
    required: true,
    message,
    trigger: ['blur', 'change']
  }
}

/**
 * 邮箱验证规则
 */
export function emailRule(message: string = '请输入正确的邮箱地址'): ValidationRule {
  return {
    pattern: PATTERNS.EMAIL,
    message,
    trigger: 'blur'
  }
}

/**
 * 手机号验证规则
 */
export function phoneRule(message: string = '请输入正确的手机号'): ValidationRule {
  return {
    pattern: PATTERNS.PHONE,
    message,
    trigger: 'blur'
  }
}

/**
 * URL验证规则
 */
export function urlRule(message: string = '请输入正确的URL'): ValidationRule {
  return {
    pattern: PATTERNS.URL,
    message,
    trigger: 'blur'
  }
}

/**
 * 身份证验证规则
 */
export function idCardRule(message: string = '请输入正确的身份证号'): ValidationRule {
  return {
    validator: (rule: any, value: any, callback: any) => {
      if (!value) {
        callback()
      } else if (!isIdCard(value)) {
        callback(new Error(message))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }
}

/**
 * 统一社会信用代码验证规则
 */
export function creditCodeRule(
  message: string = '请输入正确的统一社会信用代码'
): ValidationRule {
  return {
    validator: (rule: any, value: any, callback: any) => {
      if (!value) {
        callback()
      } else if (!isCreditCode(value)) {
        callback(new Error(message))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }
}

/**
 * 长度验证规则
 */
export function lengthRule(
  min: number,
  max: number,
  message?: string
): ValidationRule {
  return {
    min,
    max,
    message: message || `长度应在 ${min} 到 ${max} 个字符之间`,
    trigger: 'blur'
  }
}

/**
 * 范围验证规则
 */
export function rangeRule(
  min: number,
  max: number,
  message?: string
): ValidationRule {
  return {
    validator: (rule: any, value: any, callback: any) => {
      if (value === null || value === undefined || value === '') {
        callback()
      } else if (!isInRange(Number(value), min, max)) {
        callback(new Error(message || `值应在 ${min} 到 ${max} 之间`))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }
}

/**
 * 密码强度验证规则
 */
export function passwordRule(
  minStrength: number = 1,
  message?: string
): ValidationRule {
  return {
    validator: (rule: any, value: any, callback: any) => {
      if (!value) {
        callback()
      } else {
        const strength = checkPasswordStrength(value)
        if (strength < minStrength) {
          const levels = ['弱', '中', '强']
          callback(new Error(message || `密码强度过低，至少需要${levels[minStrength]}强度`))
        } else {
          callback()
        }
      }
    },
    trigger: 'blur'
  }
}

/**
 * 自定义正则验证规则
 */
export function patternRule(pattern: RegExp, message: string): ValidationRule {
  return {
    pattern,
    message,
    trigger: 'blur'
  }
}

/**
 * 组合规则工厂函数
 *
 * @example
 * createRules([
 *   required('请输入用户名'),
 *   lengthRule(3, 16, '用户名长度应在3-16个字符'),
 *   patternRule(PATTERNS.USERNAME, '用户名格式不正确')
 * ])
 */
export function createRules(rules: ValidationRule[]): ValidationRule[] {
  return rules
}
