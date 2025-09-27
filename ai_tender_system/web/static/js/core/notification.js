/**
 * 统一通知系统
 * 提供一致的用户提示和通知体验
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.notifications = new Map();
        this.nextId = 1;
        this.defaultDuration = 5000;
        this.init();
    }

    /**
     * 初始化通知容器
     */
    init() {
        // 创建通知容器
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            pointer-events: none;
        `;

        document.body.appendChild(this.container);
    }

    /**
     * 显示通知
     * @param {string} message - 消息内容
     * @param {string} type - 通知类型 (success, error, warning, info)
     * @param {number} duration - 显示时长(毫秒)，0表示不自动关闭
     * @param {Object} options - 额外选项
     */
    show(message, type = 'info', duration = null, options = {}) {
        const id = this.nextId++;
        duration = duration !== null ? duration : this.defaultDuration;

        const notification = this.createNotification(id, message, type, options);
        this.container.appendChild(notification);
        this.notifications.set(id, {
            element: notification,
            timer: null
        });

        // 动画显示
        requestAnimationFrame(() => {
            notification.classList.add('notification-enter');
        });

        // 自动关闭
        if (duration > 0) {
            const timer = setTimeout(() => this.hide(id), duration);
            this.notifications.get(id).timer = timer;
        }

        return id;
    }

    /**
     * 创建通知元素
     */
    createNotification(id, message, type, options) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            margin-bottom: 12px;
            padding: 16px 20px;
            position: relative;
            pointer-events: auto;
            transform: translateX(100%);
            transition: all 0.3s ease;
            border-left: 4px solid ${this.getTypeColor(type)};
            display: flex;
            align-items: flex-start;
            gap: 12px;
            max-width: 100%;
            word-wrap: break-word;
        `;

        // 图标
        const icon = document.createElement('i');
        icon.className = `bi ${this.getTypeIcon(type)}`;
        icon.style.cssText = `
            color: ${this.getTypeColor(type)};
            font-size: 18px;
            flex-shrink: 0;
            margin-top: 2px;
        `;

        // 内容区域
        const content = document.createElement('div');
        content.style.cssText = `
            flex: 1;
            min-width: 0;
        `;

        // 消息文本
        const messageEl = document.createElement('div');
        messageEl.className = 'notification-message';
        messageEl.innerHTML = message;
        messageEl.style.cssText = `
            color: #333;
            font-size: 14px;
            line-height: 1.4;
            margin-bottom: ${options.actions ? '8px' : '0'};
        `;

        content.appendChild(messageEl);

        // 操作按钮
        if (options.actions) {
            const actionsEl = document.createElement('div');
            actionsEl.className = 'notification-actions';
            actionsEl.style.cssText = `
                display: flex;
                gap: 8px;
                margin-top: 8px;
            `;

            options.actions.forEach(action => {
                const button = document.createElement('button');
                button.className = `btn btn-sm btn-outline-${action.type || 'primary'}`;
                button.textContent = action.text;
                button.onclick = () => {
                    action.onClick && action.onClick();
                    if (action.close !== false) {
                        this.hide(id);
                    }
                };
                actionsEl.appendChild(button);
            });

            content.appendChild(actionsEl);
        }

        // 关闭按钮
        if (options.closable !== false) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'notification-close';
            closeBtn.innerHTML = '&times;';
            closeBtn.style.cssText = `
                background: none;
                border: none;
                color: #999;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-top: -2px;
            `;
            closeBtn.onclick = () => this.hide(id);

            notification.appendChild(icon);
            notification.appendChild(content);
            notification.appendChild(closeBtn);
        } else {
            notification.appendChild(icon);
            notification.appendChild(content);
        }

        return notification;
    }

    /**
     * 隐藏通知
     */
    hide(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        const { element, timer } = notification;

        // 清除定时器
        if (timer) {
            clearTimeout(timer);
        }

        // 动画隐藏
        element.classList.add('notification-exit');
        element.style.transform = 'translateX(100%)';
        element.style.opacity = '0';

        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            this.notifications.delete(id);
        }, 300);
    }

    /**
     * 清除所有通知
     */
    clear() {
        this.notifications.forEach((notification, id) => {
            this.hide(id);
        });
    }

    /**
     * 获取类型对应的颜色
     */
    getTypeColor(type) {
        const colors = {
            success: '#48cfad',
            error: '#da4453',
            warning: '#eb7d3c',
            info: '#4a89dc'
        };
        return colors[type] || colors.info;
    }

    /**
     * 获取类型对应的图标
     */
    getTypeIcon(type) {
        const icons = {
            success: 'bi-check-circle',
            error: 'bi-exclamation-circle',
            warning: 'bi-exclamation-triangle',
            info: 'bi-info-circle'
        };
        return icons[type] || icons.info;
    }

    // 便捷方法
    success(message, duration, options) {
        return this.show(message, 'success', duration, options);
    }

    error(message, duration, options) {
        return this.show(message, 'error', duration || 0, options); // 错误消息默认不自动关闭
    }

    warning(message, duration, options) {
        return this.show(message, 'warning', duration, options);
    }

    info(message, duration, options) {
        return this.show(message, 'info', duration, options);
    }

    /**
     * 显示加载通知
     */
    loading(message = '正在处理...', options = {}) {
        return this.show(
            `<div class="d-flex align-items-center">
                <div class="search-loading-spinner me-2"></div>
                ${message}
            </div>`,
            'info',
            0,
            { closable: false, ...options }
        );
    }

    /**
     * 显示确认对话框样式的通知
     */
    confirm(message, onConfirm, onCancel) {
        return this.show(message, 'warning', 0, {
            actions: [
                {
                    text: '确认',
                    type: 'danger',
                    onClick: onConfirm
                },
                {
                    text: '取消',
                    type: 'secondary',
                    onClick: onCancel
                }
            ]
        });
    }
}

// 添加CSS样式
const style = document.createElement('style');
style.textContent = `
    .notification-enter {
        transform: translateX(0) !important;
    }

    .notification-exit {
        transform: translateX(100%) !important;
        opacity: 0 !important;
    }

    .notification:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    }

    .notification-close:hover {
        color: #666 !important;
        background-color: #f5f5f5;
        border-radius: 50%;
    }
`;
document.head.appendChild(style);

// 创建全局通知管理器实例
window.notifications = new NotificationManager();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}