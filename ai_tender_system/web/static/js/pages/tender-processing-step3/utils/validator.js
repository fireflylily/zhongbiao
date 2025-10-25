/**
 * 数据验证工具
 * 用于表单验证、数据完整性检查等
 *
 * @module Validator
 */

/**
 * 验证结果对象
 * @typedef {Object} ValidationResult
 * @property {boolean} valid - 是否验证通过
 * @property {string} [message] - 错误消息（如果验证失败）
 * @property {Object} [errors] - 详细错误信息（字段级别）
 */

/**
 * 验证必填字段
 * @param {Object} data - 要验证的数据对象
 * @param {string[]} requiredFields - 必填字段列表
 * @returns {ValidationResult} 验证结果
 */
export function validateRequiredFields(data, requiredFields) {
    const errors = {};
    let hasErrors = false;

    for (const field of requiredFields) {
        const value = data[field];
        if (value === undefined || value === null || value === '') {
            errors[field] = `${field} 是必填项`;
            hasErrors = true;
        } else if (typeof value === 'string' && value.trim() === '') {
            errors[field] = `${field} 不能为空`;
            hasErrors = true;
        }
    }

    if (hasErrors) {
        return {
            valid: false,
            message: '请填写所有必填项',
            errors
        };
    }

    return { valid: true };
}

/**
 * 验证基本信息（项目基本信息）
 * @param {Object} data - 项目数据
 * @returns {ValidationResult} 验证结果
 */
export function validateBasicInfo(data) {
    const requiredFields = ['project_name', 'project_number'];
    return validateRequiredFields(data, requiredFields);
}

/**
 * 验证章节选择
 * @param {Array} selectedChapters - 选中的章节列表
 * @returns {ValidationResult} 验证结果
 */
export function validateChapterSelection(selectedChapters) {
    if (!selectedChapters || selectedChapters.length === 0) {
        return {
            valid: false,
            message: '请至少选择一个章节'
        };
    }

    return { valid: true };
}

/**
 * 验证需求数据
 * @param {Object} requirement - 需求对象
 * @returns {ValidationResult} 验证结果
 */
export function validateRequirement(requirement) {
    const requiredFields = ['summary', 'category', 'constraint_type'];
    const result = validateRequiredFields(requirement, requiredFields);

    if (!result.valid) {
        return result;
    }

    // 验证类别
    const validCategories = ['qualification', 'technical', 'commercial', 'other'];
    if (!validCategories.includes(requirement.category)) {
        return {
            valid: false,
            message: `无效的需求类别: ${requirement.category}`
        };
    }

    // 验证约束类型
    const validConstraintTypes = ['mandatory', 'optional', 'scoring'];
    if (!validConstraintTypes.includes(requirement.constraint_type)) {
        return {
            valid: false,
            message: `无效的约束类型: ${requirement.constraint_type}`
        };
    }

    return { valid: true };
}

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
export function isValidEmail(email) {
    if (!email) return false;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * 验证电话号码（中国手机号）
 * @param {string} phone - 电话号码
 * @returns {boolean} 是否有效
 */
export function isValidPhone(phone) {
    if (!phone) return false;
    const phoneRegex = /^1[3-9]\d{9}$/;
    return phoneRegex.test(phone);
}

/**
 * 验证URL格式
 * @param {string} url - URL地址
 * @returns {boolean} 是否有效
 */
export function isValidUrl(url) {
    if (!url) return false;
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * 验证文件类型
 * @param {string} fileName - 文件名
 * @param {string[]} allowedExtensions - 允许的扩展名列表（如 ['.pdf', '.doc', '.docx']）
 * @returns {ValidationResult} 验证结果
 */
export function validateFileType(fileName, allowedExtensions) {
    if (!fileName) {
        return {
            valid: false,
            message: '文件名不能为空'
        };
    }

    const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();

    if (!allowedExtensions.includes(ext)) {
        return {
            valid: false,
            message: `不支持的文件类型: ${ext}，允许的类型: ${allowedExtensions.join(', ')}`
        };
    }

    return { valid: true };
}

/**
 * 验证文件大小
 * @param {number} fileSize - 文件大小（字节）
 * @param {number} maxSize - 最大允许大小（字节）
 * @returns {ValidationResult} 验证结果
 */
export function validateFileSize(fileSize, maxSize) {
    if (fileSize > maxSize) {
        const maxSizeMB = (maxSize / 1024 / 1024).toFixed(2);
        const fileSizeMB = (fileSize / 1024 / 1024).toFixed(2);
        return {
            valid: false,
            message: `文件大小 (${fileSizeMB}MB) 超过最大限制 (${maxSizeMB}MB)`
        };
    }

    return { valid: true };
}

/**
 * 验证数字范围
 * @param {number} value - 数值
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {ValidationResult} 验证结果
 */
export function validateNumberRange(value, min, max) {
    if (typeof value !== 'number' || isNaN(value)) {
        return {
            valid: false,
            message: '必须是有效的数字'
        };
    }

    if (value < min || value > max) {
        return {
            valid: false,
            message: `数值必须在 ${min} 和 ${max} 之间`
        };
    }

    return { valid: true };
}

/**
 * 验证日期格式（YYYY-MM-DD）
 * @param {string} dateStr - 日期字符串
 * @returns {ValidationResult} 验证结果
 */
export function validateDateFormat(dateStr) {
    if (!dateStr) {
        return {
            valid: false,
            message: '日期不能为空'
        };
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateStr)) {
        return {
            valid: false,
            message: '日期格式必须为 YYYY-MM-DD'
        };
    }

    // 验证日期是否有效
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
        return {
            valid: false,
            message: '无效的日期'
        };
    }

    return { valid: true };
}

/**
 * 批量验证
 * @param {Array<Function>} validators - 验证器函数数组
 * @returns {ValidationResult} 验证结果
 */
export function validateAll(...validators) {
    const errors = [];

    for (const validator of validators) {
        const result = validator();
        if (!result.valid) {
            errors.push(result.message);
        }
    }

    if (errors.length > 0) {
        return {
            valid: false,
            message: errors.join('; '),
            errors
        };
    }

    return { valid: true };
}
