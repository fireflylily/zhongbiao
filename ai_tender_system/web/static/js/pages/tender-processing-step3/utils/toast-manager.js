/**
 * Toast 提示管理器
 * 用于显示成功、错误、警告、信息等提示消息
 *
 * @module ToastManager
 */

/**
 * Toast类型常量
 */
export const TOAST_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

/**
 * Toast配置常量
 */
const TOAST_CONFIG = {
    defaultDuration: 3000,
    errorDuration: 5000,
    containerPosition: {
        top: '80px',
        right: '20px'
    },
    maxWidth: '400px',
    zIndex: 9999
};

/**
 * Toast样式配置
 */
const TOAST_STYLES = {
    [TOAST_TYPES.SUCCESS]: {
        bgColor: '#28a745',
        icon: '<i class="bi bi-check-circle-fill me-2"></i>'
    },
    [TOAST_TYPES.ERROR]: {
        bgColor: '#dc3545',
        icon: '<i class="bi bi-exclamation-circle-fill me-2"></i>'
    },
    [TOAST_TYPES.WARNING]: {
        bgColor: '#ffc107',
        icon: '<i class="bi bi-exclamation-triangle-fill me-2"></i>'
    },
    [TOAST_TYPES.INFO]: {
        bgColor: '#17a2b8',
        icon: '<i class="bi bi-info-circle-fill me-2"></i>'
    }
};

/**
 * Toast管理器类
 */
class ToastManager {
    constructor() {
        this.container = null;
        this.animationStylesAdded = false;
    }

    /**
     * 获取或创建Toast容器
     * @returns {HTMLElement} Toast容器元素
     */
    getOrCreateContainer() {
        if (!this.container || !document.body.contains(this.container)) {
            this.container = document.getElementById('toastContainer');

            if (!this.container) {
                this.container = document.createElement('div');
                this.container.id = 'toastContainer';
                this.container.style.cssText = `
                    position: fixed;
                    top: ${TOAST_CONFIG.containerPosition.top};
                    right: ${TOAST_CONFIG.containerPosition.right};
                    z-index: ${TOAST_CONFIG.zIndex};
                    max-width: ${TOAST_CONFIG.maxWidth};
                `;
                document.body.appendChild(this.container);
            }
        }
        return this.container;
    }

    /**
     * 添加Toast动画样式
     */
    addAnimationStyles() {
        if (this.animationStylesAdded || document.getElementById('toastAnimationStyles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'toastAnimationStyles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
        this.animationStylesAdded = true;
    }

    /**
     * 创建Toast元素
     * @param {string} message - 提示消息
     * @param {string} type - Toast类型
     * @returns {HTMLElement} Toast元素
     */
    createToastElement(message, type) {
        const toast = document.createElement('div');
        toast.className = 'toast-message';

        const style = TOAST_STYLES[type] || TOAST_STYLES[TOAST_TYPES.INFO];
        const { bgColor, icon } = style;

        toast.style.cssText = `
            background-color: ${bgColor};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            animation: slideIn 0.3s ease-out;
            font-size: 14px;
            line-height: 1.5;
        `;

        toast.innerHTML = `${icon}<span>${message}</span>`;
        return toast;
    }

    /**
     * 移除Toast元素
     * @param {HTMLElement} toast - Toast元素
     * @param {HTMLElement} container - 容器元素
     */
    removeToast(toast, container) {
        toast.style.animation = 'slideOut 0.3s ease-out';

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }

            // 如果容器为空，移除容器
            if (container.children.length === 0) {
                container.remove();
                this.container = null;
            }
        }, 300);
    }

    /**
     * 显示Toast消息
     * @param {string} message - 提示消息
     * @param {string} type - Toast类型
     * @param {number} duration - 显示时长（毫秒）
     */
    show(message, type = TOAST_TYPES.INFO, duration = TOAST_CONFIG.defaultDuration) {
        // 确保动画样式已添加
        this.addAnimationStyles();

        // 获取容器
        const container = this.getOrCreateContainer();

        // 创建Toast元素
        const toast = this.createToastElement(message, type);

        // 添加到容器
        container.appendChild(toast);

        // 自动移除
        setTimeout(() => {
            this.removeToast(toast, container);
        }, duration);
    }

    /**
     * 显示成功提示
     * @param {string} message - 提示消息
     */
    success(message) {
        this.show(message, TOAST_TYPES.SUCCESS);
    }

    /**
     * 显示错误提示
     * @param {string} message - 错误消息
     */
    error(message) {
        this.show(message, TOAST_TYPES.ERROR, TOAST_CONFIG.errorDuration);
    }

    /**
     * 显示警告提示
     * @param {string} message - 警告消息
     */
    warning(message) {
        this.show(message, TOAST_TYPES.WARNING);
    }

    /**
     * 显示信息提示
     * @param {string} message - 信息消息
     */
    info(message) {
        this.show(message, TOAST_TYPES.INFO);
    }
}

// 创建单例实例
const toastManager = new ToastManager();

// 导出单例实例
export default toastManager;

// 导出便捷函数（向后兼容）
export function showToast(message, type = TOAST_TYPES.INFO, duration = TOAST_CONFIG.defaultDuration) {
    toastManager.show(message, type, duration);
}

export function showSuccessToast(message) {
    toastManager.success(message);
}

export function showErrorToast(message) {
    toastManager.error(message);
}

export function showWarningToast(message) {
    toastManager.warning(message);
}

export function showInfoToast(message) {
    toastManager.info(message);
}
