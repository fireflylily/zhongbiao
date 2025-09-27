/**
 * 表单验证模块
 * 提供统一的表单验证和错误提示功能
 */

class ValidationManager {
    constructor() {
        this.validators = new Map();
        this.errorMessages = new Map();
        this.rules = this.getDefaultRules();
        this.init();
    }

    /**
     * 初始化验证管理器
     */
    init() {
        // 监听表单提交事件
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.hasAttribute('data-validate')) {
                e.preventDefault();
                this.validateForm(form);
            }
        });

        // 监听输入事件进行实时验证
        document.addEventListener('input', (e) => {
            const input = e.target;
            if (input.hasAttribute('data-validate-rule')) {
                this.validateField(input);
            }
        });

        // 监听失焦事件
        document.addEventListener('blur', (e) => {
            const input = e.target;
            if (input.hasAttribute('data-validate-rule')) {
                this.validateField(input);
            }
        }, true);
    }

    /**
     * 获取默认验证规则
     */
    getDefaultRules() {
        return {
            required: {
                test: (value) => value !== null && value !== undefined && value.toString().trim() !== '',
                message: '此字段为必填项'
            },
            email: {
                test: (value) => !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
                message: '请输入有效的邮箱地址'
            },
            phone: {
                test: (value) => !value || /^1[3-9]\d{9}$/.test(value),
                message: '请输入有效的手机号码'
            },
            url: {
                test: (value) => !value || /^https?:\/\/.+/.test(value),
                message: '请输入有效的URL地址'
            },
            minLength: {
                test: (value, params) => !value || value.length >= parseInt(params),
                message: (params) => `最少需要${params}个字符`
            },
            maxLength: {
                test: (value, params) => !value || value.length <= parseInt(params),
                message: (params) => `最多允许${params}个字符`
            },
            min: {
                test: (value, params) => !value || parseFloat(value) >= parseFloat(params),
                message: (params) => `值不能小于${params}`
            },
            max: {
                test: (value, params) => !value || parseFloat(value) <= parseFloat(params),
                message: (params) => `值不能大于${params}`
            },
            number: {
                test: (value) => !value || !isNaN(value) && !isNaN(parseFloat(value)),
                message: '请输入有效的数字'
            },
            integer: {
                test: (value) => !value || Number.isInteger(parseFloat(value)),
                message: '请输入整数'
            },
            positive: {
                test: (value) => !value || parseFloat(value) > 0,
                message: '请输入正数'
            },
            fileSize: {
                test: (value, params, element) => {
                    if (!element.files || element.files.length === 0) return true;
                    const maxSize = parseInt(params) * 1024 * 1024; // MB转字节
                    for (let file of element.files) {
                        if (file.size > maxSize) return false;
                    }
                    return true;
                },
                message: (params) => `文件大小不能超过${params}MB`
            },
            fileType: {
                test: (value, params, element) => {
                    if (!element.files || element.files.length === 0) return true;
                    const allowedTypes = params.split(',').map(t => t.trim());
                    for (let file of element.files) {
                        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
                        if (!allowedTypes.includes(fileExt)) return false;
                    }
                    return true;
                },
                message: (params) => `只允许上传${params}格式的文件`
            },
            match: {
                test: (value, params, element) => {
                    const targetElement = document.querySelector(params);
                    return !value || !targetElement || value === targetElement.value;
                },
                message: '两次输入不一致'
            }
        };
    }

    /**
     * 添加自定义验证规则
     */
    addRule(name, rule) {
        this.rules[name] = rule;
    }

    /**
     * 验证单个字段
     */
    validateField(element) {
        const rules = element.getAttribute('data-validate-rule');
        if (!rules) return true;

        this.clearFieldError(element);

        const ruleList = rules.split('|');
        const value = element.value;

        for (let ruleStr of ruleList) {
            const [ruleName, params] = ruleStr.split(':');
            const rule = this.rules[ruleName];

            if (!rule) {
                console.warn(`验证规则 "${ruleName}" 不存在`);
                continue;
            }

            const isValid = rule.test(value, params, element);
            if (!isValid) {
                const message = typeof rule.message === 'function'
                    ? rule.message(params)
                    : rule.message;
                this.showFieldError(element, message);
                return false;
            }
        }

        this.showFieldSuccess(element);
        return true;
    }

    /**
     * 验证整个表单
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('[data-validate-rule]');
        let isValid = true;
        let firstInvalidField = null;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = input;
                }
            }
        });

        if (isValid) {
            // 表单验证通过，触发自定义事件
            const event = new CustomEvent('formValidated', {
                detail: { form: form }
            });
            form.dispatchEvent(event);
        } else if (firstInvalidField) {
            // 聚焦到第一个错误字段
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }

        return isValid;
    }

    /**
     * 显示字段错误
     */
    showFieldError(element, message) {
        element.classList.add('is-invalid');
        element.classList.remove('is-valid');

        // 移除现有错误消息
        this.clearFieldError(element);

        // 添加错误消息
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        errorDiv.setAttribute('data-validation-error', '');

        // 插入错误消息
        const parent = element.parentNode;
        parent.insertBefore(errorDiv, element.nextSibling);

        // 存储错误信息
        this.errorMessages.set(element, message);
    }

    /**
     * 显示字段成功状态
     */
    showFieldSuccess(element) {
        element.classList.remove('is-invalid');
        element.classList.add('is-valid');
        this.clearFieldError(element);
        this.errorMessages.delete(element);
    }

    /**
     * 清除字段错误
     */
    clearFieldError(element) {
        element.classList.remove('is-invalid', 'is-valid');

        // 移除错误消息
        const parent = element.parentNode;
        const errorElement = parent.querySelector('[data-validation-error]');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * 清除表单所有错误
     */
    clearFormErrors(form) {
        const inputs = form.querySelectorAll('[data-validate-rule]');
        inputs.forEach(input => {
            this.clearFieldError(input);
            this.errorMessages.delete(input);
        });
    }

    /**
     * 获取表单错误
     */
    getFormErrors(form) {
        const errors = {};
        const inputs = form.querySelectorAll('[data-validate-rule]');

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                const name = input.name || input.id || 'unknown';
                errors[name] = this.errorMessages.get(input);
            }
        });

        return errors;
    }

    /**
     * 批量设置字段错误（通常用于服务器端验证结果）
     */
    setFieldErrors(errors) {
        Object.keys(errors).forEach(fieldName => {
            const element = document.querySelector(`[name="${fieldName}"], #${fieldName}`);
            if (element) {
                this.showFieldError(element, errors[fieldName]);
            }
        });
    }

    /**
     * 验证单个值
     */
    validateValue(value, rules) {
        const ruleList = rules.split('|');

        for (let ruleStr of ruleList) {
            const [ruleName, params] = ruleStr.split(':');
            const rule = this.rules[ruleName];

            if (!rule) continue;

            const isValid = rule.test(value, params);
            if (!isValid) {
                const message = typeof rule.message === 'function'
                    ? rule.message(params)
                    : rule.message;
                return { valid: false, message };
            }
        }

        return { valid: true };
    }

    /**
     * 启用表单验证
     */
    enableValidation(form) {
        form.setAttribute('data-validate', 'true');
    }

    /**
     * 禁用表单验证
     */
    disableValidation(form) {
        form.removeAttribute('data-validate');
        this.clearFormErrors(form);
    }
}

// 添加CSS样式
const style = document.createElement('style');
style.textContent = `
    .is-invalid {
        border-color: #da4453 !important;
        box-shadow: 0 0 0 0.2rem rgba(218, 68, 83, 0.25) !important;
    }

    .is-valid {
        border-color: #48cfad !important;
        box-shadow: 0 0 0 0.2rem rgba(72, 207, 173, 0.25) !important;
    }

    .invalid-feedback {
        display: block !important;
        color: #da4453;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }

    .valid-feedback {
        display: block !important;
        color: #48cfad;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }

    /* 美化文件输入框验证状态 */
    input[type="file"].is-invalid {
        border-color: #da4453;
    }

    input[type="file"].is-valid {
        border-color: #48cfad;
    }

    /* 验证动画效果 */
    .form-control, .form-select {
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }

    .invalid-feedback {
        animation: shake 0.5s ease-in-out;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
        20%, 40%, 60%, 80% { transform: translateX(2px); }
    }
`;
document.head.appendChild(style);

// 创建全局验证管理器实例
window.validator = new ValidationManager();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ValidationManager;
}