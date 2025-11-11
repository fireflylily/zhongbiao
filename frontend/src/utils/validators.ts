/**
 * 表单验证工具函数
 * @module utils/validators
 */

import type { FormItemRule } from 'element-plus'

/**
 * 验证中国大陆手机号
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validatePhone, trigger: 'blur' }
 */
export const validatePhone = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  const regex = /^1[3-9]\d{9}$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('请输入正确的手机号码'))
  }
}

/**
 * 验证中国大陆身份证号
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateIdCard, trigger: 'blur' }
 */
export const validateIdCard = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  // 18位身份证号正则
  const regex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/

  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('请输入正确的身份证号码'))
  }
}

/**
 * 验证电子邮箱
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateEmail, trigger: 'blur' }
 */
export const validateEmail = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('请输入正确的邮箱地址'))
  }
}

/**
 * 验证邮政编码
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validatePostalCode, trigger: 'blur' }
 */
export const validatePostalCode = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  const regex = /^\d{6}$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('邮政编码必须是6位数字'))
  }
}

/**
 * 验证统一社会信用代码
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateSocialCreditCode, trigger: 'blur' }
 */
export const validateSocialCreditCode = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  // 统一社会信用代码是18位
  const regex = /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/
  if (regex.test(value) && value.length === 18) {
    callback()
  } else {
    callback(new Error('请输入正确的统一社会信用代码（18位）'))
  }
}

/**
 * 验证网址 URL
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateUrl, trigger: 'blur' }
 */
export const validateUrl = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  const regex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('请输入正确的网址'))
  }
}

/**
 * 验证 IP 地址
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateIP, trigger: 'blur' }
 */
export const validateIP = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  const regex = /^(\d{1,3}\.){3}\d{1,3}$/
  if (regex.test(value)) {
    const parts = value.split('.')
    const valid = parts.every(part => {
      const num = parseInt(part, 10)
      return num >= 0 && num <= 255
    })
    if (valid) {
      callback()
    } else {
      callback(new Error('IP地址每段必须在0-255之间'))
    }
  } else {
    callback(new Error('请输入正确的IP地址'))
  }
}

/**
 * 验证银行卡号
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateBankCard, trigger: 'blur' }
 */
export const validateBankCard = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  // 银行卡号通常是16-19位数字
  const regex = /^\d{16,19}$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('请输入正确的银行卡号（16-19位数字）'))
  }
}

/**
 * 验证数字范围
 * @param min 最小值
 * @param max 最大值
 * @param message 错误提示
 * @returns 验证函数
 * @example
 * { validator: validateNumberRange(0, 100, '请输入0-100的数字'), trigger: 'blur' }
 */
export const validateNumberRange = (
  min: number,
  max: number,
  message?: string
) => {
  return (
    rule: FormItemRule,
    value: number,
    callback: (error?: Error) => void
  ): void => {
    if (value === null || value === undefined) {
      callback()
      return
    }

    if (value >= min && value <= max) {
      callback()
    } else {
      callback(new Error(message || `请输入${min}-${max}之间的数字`))
    }
  }
}

/**
 * 验证字符串长度范围
 * @param min 最小长度
 * @param max 最大长度
 * @param message 错误提示
 * @returns 验证函数
 * @example
 * { validator: validateLengthRange(2, 20, '长度必须在2-20个字符'), trigger: 'blur' }
 */
export const validateLengthRange = (
  min: number,
  max: number,
  message?: string
) => {
  return (
    rule: FormItemRule,
    value: string,
    callback: (error?: Error) => void
  ): void => {
    if (!value) {
      callback()
      return
    }

    const length = value.length
    if (length >= min && length <= max) {
      callback()
    } else {
      callback(new Error(message || `长度必须在${min}-${max}个字符`))
    }
  }
}

/**
 * 验证密码强度
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @description 密码必须包含大小写字母、数字，长度8-20位
 * @example
 * { validator: validatePasswordStrength, trigger: 'blur' }
 */
export const validatePasswordStrength = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  // 密码必须包含大小写字母、数字，长度8-20位
  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,20}$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('密码必须包含大小写字母和数字，长度8-20位'))
  }
}

/**
 * 验证两次输入是否一致（通常用于确认密码）
 * @param targetValue 目标值（第一次输入）
 * @param message 错误提示
 * @returns 验证函数
 * @example
 * { validator: validateSameAs(password, '两次密码输入不一致'), trigger: 'blur' }
 */
export const validateSameAs = (
  targetValue: () => string,
  message: string = '两次输入不一致'
) => {
  return (
    rule: FormItemRule,
    value: string,
    callback: (error?: Error) => void
  ): void => {
    if (!value) {
      callback()
      return
    }

    if (value === targetValue()) {
      callback()
    } else {
      callback(new Error(message))
    }
  }
}

/**
 * 验证中文姓名
 * @param rule 验证规则
 * @param value 验证值
 * @param callback 回调函数
 * @example
 * { validator: validateChineseName, trigger: 'blur' }
 */
export const validateChineseName = (
  rule: FormItemRule,
  value: string,
  callback: (error?: Error) => void
): void => {
  if (!value) {
    callback()
    return
  }

  const regex = /^[\u4e00-\u9fa5·]{2,20}$/
  if (regex.test(value)) {
    callback()
  } else {
    callback(new Error('请输入正确的中文姓名（2-20个汉字）'))
  }
}

/**
 * 验证文件类型
 * @param allowedTypes 允许的文件类型数组
 * @param message 错误提示
 * @returns 验证函数
 * @example
 * { validator: validateFileType(['.jpg', '.png', '.pdf']), trigger: 'change' }
 */
export const validateFileType = (
  allowedTypes: string[],
  message?: string
) => {
  return (
    rule: FormItemRule,
    value: File,
    callback: (error?: Error) => void
  ): void => {
    if (!value) {
      callback()
      return
    }

    const fileName = value.name.toLowerCase()
    const isValid = allowedTypes.some(type => fileName.endsWith(type.toLowerCase()))

    if (isValid) {
      callback()
    } else {
      callback(new Error(message || `只允许上传 ${allowedTypes.join(', ')} 格式的文件`))
    }
  }
}

/**
 * 验证文件大小
 * @param maxSize 最大文件大小（MB）
 * @param message 错误提示
 * @returns 验证函数
 * @example
 * { validator: validateFileSize(10, '文件大小不能超过10MB'), trigger: 'change' }
 */
export const validateFileSize = (
  maxSize: number,
  message?: string
) => {
  return (
    rule: FormItemRule,
    value: File,
    callback: (error?: Error) => void
  ): void => {
    if (!value) {
      callback()
      return
    }

    const fileSizeMB = value.size / 1024 / 1024
    if (fileSizeMB <= maxSize) {
      callback()
    } else {
      callback(new Error(message || `文件大小不能超过${maxSize}MB`))
    }
  }
}
