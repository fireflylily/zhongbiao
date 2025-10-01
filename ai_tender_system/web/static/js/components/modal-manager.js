/**
 * 模态框管理器
 * 提供统一的模态框创建、管理和交互功能
 */

class ModalManager {
    constructor() {
        this.modals = new Map();
        this.zIndexCounter = 1050;
        this.init();
    }

    /**
     * 初始化管理器
     */
    init() {
        // 确保DOM加载完成后再初始化
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.createContainer());
        } else {
            this.createContainer();
        }

        // 监听键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });
    }

    /**
     * 创建模态框容器
     */
    createContainer() {
        // 创建模态框容器
        this.container = document.createElement('div');
        this.container.id = 'modal-container';
        document.body.appendChild(this.container);
    }

    /**
     * 显示模态框
     * @param {Object} options - 模态框选项
     * @returns {string} 模态框ID
     */
    show(options = {}) {
        const config = {
            id: options.id || 'modal_' + Date.now(),
            title: options.title || '提示',
            content: options.content || '',
            size: options.size || 'md', // sm, md, lg, xl
            backdrop: options.backdrop !== false,
            keyboard: options.keyboard !== false,
            centered: options.centered !== false,
            scrollable: options.scrollable || false,
            buttons: options.buttons || null,
            onShow: options.onShow || null,
            onHide: options.onHide || null,
            onConfirm: options.onConfirm || null,
            onCancel: options.onCancel || null,
            autoDestroy: options.autoDestroy !== false,
            ...options
        };

        // 如果模态框已存在，先关闭
        if (this.modals.has(config.id)) {
            this.hide(config.id);
        }

        const modalElement = this.createModal(config);
        this.container.appendChild(modalElement);

        // 存储模态框信息
        this.modals.set(config.id, {
            element: modalElement,
            config: config,
            bsModal: null
        });

        // 初始化Bootstrap模态框
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: config.backdrop,
            keyboard: config.keyboard
        });

        this.modals.get(config.id).bsModal = bsModal;

        // 绑定事件
        this.bindModalEvents(config.id);

        // 显示模态框
        bsModal.show();

        return config.id;
    }

    /**
     * 创建模态框元素
     */
    createModal(config) {
        const modal = document.createElement('div');
        modal.className = `modal fade`;
        modal.id = config.id;
        modal.tabIndex = -1;
        modal.setAttribute('aria-hidden', 'true');

        if (config.title) {
            modal.setAttribute('aria-labelledby', `${config.id}-title`);
        }

        const sizeClass = config.size !== 'md' ? `modal-${config.size}` : '';
        const centeredClass = config.centered ? 'modal-dialog-centered' : '';
        const scrollableClass = config.scrollable ? 'modal-dialog-scrollable' : '';

        modal.innerHTML = `
            <div class="modal-dialog ${sizeClass} ${centeredClass} ${scrollableClass}">
                <div class="modal-content">
                    ${this.createModalHeader(config)}
                    ${this.createModalBody(config)}
                    ${this.createModalFooter(config)}
                </div>
            </div>
        `;

        return modal;
    }

    /**
     * 创建模态框头部
     */
    createModalHeader(config) {
        if (!config.title && !config.showCloseButton) return '';

        return `
            <div class="modal-header">
                ${config.title ? `<h5 class="modal-title" id="${config.id}-title">${config.title}</h5>` : ''}
                ${config.showCloseButton !== false ? `
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
                ` : ''}
            </div>
        `;
    }

    /**
     * 创建模态框主体
     */
    createModalBody(config) {
        return `
            <div class="modal-body">
                ${config.content}
            </div>
        `;
    }

    /**
     * 创建模态框底部
     */
    createModalFooter(config) {
        if (!config.buttons && !config.onConfirm && !config.onCancel) return '';

        let buttons = '';

        if (config.buttons) {
            // 自定义按钮
            buttons = config.buttons.map(button => `
                <button type="button"
                        class="btn btn-${button.variant || 'secondary'} ${button.class || ''}"
                        data-action="${button.action || 'custom'}"
                        ${button.dismiss ? 'data-bs-dismiss="modal"' : ''}
                        ${button.disabled ? 'disabled' : ''}>
                    ${button.icon ? `<i class="${button.icon}"></i> ` : ''}
                    ${button.text}
                </button>
            `).join('');
        } else {
            // 默认按钮
            if (config.onCancel) {
                buttons += `
                    <button type="button" class="btn btn-secondary" data-action="cancel" data-bs-dismiss="modal">
                        取消
                    </button>
                `;
            }

            if (config.onConfirm) {
                buttons += `
                    <button type="button" class="btn btn-primary" data-action="confirm">
                        确定
                    </button>
                `;
            }
        }

        return buttons ? `<div class="modal-footer">${buttons}</div>` : '';
    }

    /**
     * 绑定模态框事件
     */
    bindModalEvents(modalId) {
        const modalInfo = this.modals.get(modalId);
        if (!modalInfo) return;

        const { element, config } = modalInfo;

        // 显示事件
        element.addEventListener('shown.bs.modal', () => {
            // 自动聚焦第一个输入框
            const firstInput = element.querySelector('input, textarea, select');
            if (firstInput && !firstInput.disabled) {
                firstInput.focus();
            }

            if (config.onShow) {
                config.onShow(element);
            }
        });

        // 隐藏事件
        element.addEventListener('hidden.bs.modal', () => {
            if (config.onHide) {
                config.onHide(element);
            }

            if (config.autoDestroy) {
                this.destroy(modalId);
            }
        });

        // 按钮点击事件
        element.addEventListener('click', async (e) => {
            const actionButton = e.target.closest('[data-action]');
            if (!actionButton) return;

            const action = actionButton.getAttribute('data-action');
            let shouldClose = true;

            try {
                switch (action) {
                    case 'confirm':
                        if (config.onConfirm) {
                            const result = await config.onConfirm(element);
                            shouldClose = result !== false;
                        }
                        break;

                    case 'cancel':
                        if (config.onCancel) {
                            const result = await config.onCancel(element);
                            shouldClose = result !== false;
                        }
                        break;

                    case 'custom':
                        // 自定义按钮事件由外部处理
                        break;
                }

                if (shouldClose && !actionButton.hasAttribute('data-bs-dismiss')) {
                    this.hide(modalId);
                }
            } catch (error) {
                console.error('模态框按钮事件处理失败:', error);
                window.notifications?.error('操作失败: ' + error.message);
            }
        });
    }

    /**
     * 隐藏模态框
     */
    hide(modalId) {
        const modalInfo = this.modals.get(modalId);
        if (!modalInfo) return;

        const { bsModal } = modalInfo;
        if (bsModal) {
            bsModal.hide();
        }
    }

    /**
     * 关闭顶层模态框
     */
    closeTopModal() {
        const visibleModals = Array.from(this.modals.entries())
            .filter(([id, info]) => info.element.classList.contains('show'))
            .sort((a, b) => {
                const aZIndex = parseInt(a[1].element.style.zIndex) || 0;
                const bZIndex = parseInt(b[1].element.style.zIndex) || 0;
                return bZIndex - aZIndex;
            });

        if (visibleModals.length > 0) {
            this.hide(visibleModals[0][0]);
        }
    }

    /**
     * 销毁模态框
     */
    destroy(modalId) {
        const modalInfo = this.modals.get(modalId);
        if (!modalInfo) return;

        const { element, bsModal } = modalInfo;

        // 销毁Bootstrap实例
        if (bsModal) {
            bsModal.dispose();
        }

        // 移除DOM元素
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }

        // 从管理器中移除
        this.modals.delete(modalId);
    }

    /**
     * 销毁所有模态框
     */
    destroyAll() {
        const modalIds = Array.from(this.modals.keys());
        modalIds.forEach(id => this.destroy(id));
    }

    /**
     * 获取模态框元素
     */
    getModal(modalId) {
        const modalInfo = this.modals.get(modalId);
        return modalInfo ? modalInfo.element : null;
    }

    /**
     * 检查模态框是否可见
     */
    isVisible(modalId) {
        const modalInfo = this.modals.get(modalId);
        return modalInfo ? modalInfo.element.classList.contains('show') : false;
    }

    /**
     * 更新模态框内容
     */
    updateContent(modalId, content) {
        const modalInfo = this.modals.get(modalId);
        if (!modalInfo) return;

        const bodyElement = modalInfo.element.querySelector('.modal-body');
        if (bodyElement) {
            bodyElement.innerHTML = content;
        }
    }

    /**
     * 更新模态框标题
     */
    updateTitle(modalId, title) {
        const modalInfo = this.modals.get(modalId);
        if (!modalInfo) return;

        const titleElement = modalInfo.element.querySelector('.modal-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
    }

    /**
     * 便捷方法：确认对话框
     */
    confirm(message, title = '确认', options = {}) {
        return new Promise((resolve) => {
            this.show({
                title: title,
                content: `<p>${message}</p>`,
                onConfirm: () => {
                    resolve(true);
                },
                onCancel: () => {
                    resolve(false);
                },
                ...options
            });
        });
    }

    /**
     * 便捷方法：警告对话框
     */
    alert(message, title = '提示', options = {}) {
        return new Promise((resolve) => {
            this.show({
                title: title,
                content: `<p>${message}</p>`,
                buttons: [{
                    text: '确定',
                    variant: 'primary',
                    action: 'confirm'
                }],
                onConfirm: () => {
                    resolve();
                },
                ...options
            });
        });
    }

    /**
     * 便捷方法：输入对话框
     */
    prompt(message, defaultValue = '', title = '输入', options = {}) {
        return new Promise((resolve) => {
            const inputId = 'prompt_input_' + Date.now();
            this.show({
                title: title,
                content: `
                    <div class="mb-3">
                        <label for="${inputId}" class="form-label">${message}</label>
                        <input type="text" class="form-control" id="${inputId}" value="${defaultValue}">
                    </div>
                `,
                onConfirm: (modal) => {
                    const input = modal.querySelector(`#${inputId}`);
                    resolve(input ? input.value : null);
                },
                onCancel: () => {
                    resolve(null);
                },
                ...options
            });
        });
    }

    /**
     * 便捷方法：加载对话框
     */
    loading(message = '加载中...', options = {}) {
        return this.show({
            title: options.title || '请稍候',
            content: `
                <div class="text-center py-4">
                    <div class="search-loading-spinner mb-3"></div>
                    <p class="mb-0">${message}</p>
                </div>
            `,
            backdrop: 'static',
            keyboard: false,
            showCloseButton: false,
            ...options
        });
    }

    /**
     * 便捷方法：显示表单模态框
     */
    form(formContent, title = '表单', options = {}) {
        return new Promise((resolve, reject) => {
            this.show({
                title: title,
                content: formContent,
                size: options.size || 'lg',
                onConfirm: async (modal) => {
                    const form = modal.querySelector('form');
                    if (form && window.validator) {
                        if (!window.validator.validateForm(form)) {
                            return false; // 阻止关闭
                        }
                    }

                    const formData = new FormData(form);
                    const data = Object.fromEntries(formData);
                    resolve(data);
                },
                onCancel: () => {
                    reject(new Error('用户取消'));
                },
                ...options
            });
        });
    }
}

// 添加CSS样式增强
(function() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addModalStyles);
    } else {
        addModalStyles();
    }

    function addModalStyles() {
        const styleElement = document.createElement('style');
        styleElement.textContent = `
    /* 模态框动画优化 */
    .modal.fade .modal-dialog {
        transition: transform 0.25s ease-out;
    }

    .modal.show .modal-dialog {
        transform: none;
    }

    /* 模态框层叠样式 */
    .modal-backdrop.show {
        opacity: 0.6;
    }

    /* 表单验证在模态框中的样式 */
    .modal .is-invalid {
        border-color: #da4453;
        box-shadow: 0 0 0 0.2rem rgba(218, 68, 83, 0.25);
    }

    .modal .invalid-feedback {
        display: block;
    }

    /* 模态框中的加载状态 */
    .modal .search-loading-spinner {
        width: 32px;
        height: 32px;
        border-width: 3px;
        margin: 0 auto;
    }

    /* 响应式模态框 */
    @media (max-width: 576px) {
        .modal-dialog {
            margin: 10px;
            max-width: none;
        }
    }
        `;
        document.head.appendChild(styleElement);
    }
})();

// 创建全局模态框管理器实例
window.modalManager = new ModalManager();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalManager;
}