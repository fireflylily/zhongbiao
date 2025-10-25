/**
 * 章节选择管理器适配器
 * 提供向后兼容的接口，内部使用模块化架构
 *
 * @file tender-processing-step1-adapter.js
 * @version 3.0.0
 *
 * 使用说明：
 * 1. 引入此文件替代原 tender-processing-step1.js
 * 2. 保持原有API接口不变
 * 3. 内部使用职责分离的模块化架构
 */

/**
 * 兼容性包装器 - 模拟原 ChapterSelectionManager 接口
 * 内部委托给模块化的 ChapterSelectionController
 *
 * @class ChapterSelectionManager
 */
class ChapterSelectionManagerAdapter {
    constructor() {
        // 使用新的控制器
        this.controller = new ChapterSelectionController(window.CHAPTER_CONFIG);
        this.controller.initialize('chapterTreeContainer');

        // 兼容性属性（映射到controller.stateManager）
        Object.defineProperty(this, 'currentTaskId', {
            get: () => this.controller.stateManager.taskId,
            set: (value) => { this.controller.stateManager.taskId = value; }
        });

        Object.defineProperty(this, 'chaptersData', {
            get: () => this.controller.stateManager.chaptersFlat
        });

        Object.defineProperty(this, 'selectedChapterIds', {
            get: () => this.controller.stateManager.selectedIds
        });

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // 文件选择后的解析按钮
        const parseBtn = document.getElementById('parseStructureBtn');
        if (parseBtn) {
            parseBtn.addEventListener('click', () => this.handleParseStructure());
        }

        // 章节搜索
        const searchBox = document.getElementById('chapterSearch');
        if (searchBox) {
            searchBox.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // 批量操作按钮
        document.getElementById('selectAllBtn')?.addEventListener('click', () => this.selectAll());
        document.getElementById('unselectAllBtn')?.addEventListener('click', () => this.unselectAll());
        document.getElementById('selectTechBtn')?.addEventListener('click', () => this.selectByKeyword('技术'));
        document.getElementById('excludeContractBtn')?.addEventListener('click', () => this.excludeByKeyword('合同'));

        // 确认选择按钮
        document.getElementById('confirmSelectionBtn')?.addEventListener('click', () => this.confirmSelection());

        // 批量导出按钮
        document.getElementById('exportSelectedChaptersBtn')?.addEventListener('click', () => this.exportSelectedChapters());

        // 另存为应答文件按钮
        document.getElementById('saveAsResponseFileBtn')?.addEventListener('click', () => this.saveAsResponseFile());

        // 键盘快捷键
        this._initKeyboardShortcuts();
    }

    /**
     * 初始化键盘快捷键
     */
    _initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            // Ctrl/Cmd + A: 全选
            if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
                e.preventDefault();
                this.selectAll();
            }

            // Ctrl/Cmd + D: 取消全选
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.unselectAll();
            }

            // /: 聚焦搜索框
            if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                const searchBox = document.getElementById('chapterSearch');
                if (searchBox) {
                    searchBox.focus();
                }
            }

            // Esc: 清空搜索
            if (e.key === 'Escape') {
                const searchBox = document.getElementById('chapterSearch');
                if (searchBox && searchBox.value) {
                    searchBox.value = '';
                    this.handleSearch('');
                }
            }
        });

        console.log('[ChapterSelection] 键盘快捷键已启用 (模块化版本)');
    }

    async handleParseStructure() {
        const fileInput = document.getElementById('tenderDocFile');
        const config = HITLConfigManager.getConfig();

        const parseBtn = document.getElementById('parseStructureBtn');
        const originalText = parseBtn.innerHTML;
        parseBtn.disabled = true;
        parseBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>解析中...';

        // 显示章节选择区域（提前显示loading）
        const chapterSelectionSection = document.getElementById('chapterSelectionSection');
        if (chapterSelectionSection) {
            chapterSelectionSection.style.display = 'block';
        }

        try {
            const result = await this.controller.parseStructure(fileInput, config);

            // 如果后端返回了新的project_id，更新配置
            if (result.projectId && !config.projectId) {
                HITLConfigManager.currentProjectId = result.projectId;
                this.showNotification(`新项目已创建: ${result.projectId}`, 'info');

                await HITLConfigManager.loadProjects();
                const projectSelect = document.getElementById('hitlProjectSelect');
                if (projectSelect) {
                    projectSelect.value = result.projectId;
                }
            }

            // 显示章节选择区域
            document.getElementById('uploadSection').style.display = 'none';
            chapterSelectionSection.style.display = 'block';

            this.showNotification('文档解析成功！', 'success');

        } catch (error) {
            const { message } = this._handleError(error, 'handleParseStructure');
            this.showNotification(message, 'error');
        } finally {
            parseBtn.disabled = false;
            parseBtn.innerHTML = originalText;
        }
    }

    updateStatistics() {
        this.controller.updateStatistics();
    }

    selectAll() {
        const count = this.controller.selectAll();
        this.showNotification(`已选择 ${count} 个章节`, 'success');
    }

    unselectAll() {
        const previousCount = this.controller.unselectAll();
        this.showNotification(`已取消选择 ${previousCount} 个章节`, 'info');
    }

    selectByKeyword(keyword) {
        const count = this.controller.selectByKeyword(keyword);
        this.showNotification(`已选中包含"${keyword}"的章节`, 'info');
    }

    excludeByKeyword(keyword) {
        const count = this.controller.excludeByKeyword(keyword);
        this.showNotification(`已排除包含"${keyword}"的章节`, 'info');
    }

    handleSearch(query) {
        this.controller.search(query);
    }

    async confirmSelection() {
        console.log('[Step1] confirmSelection 开始执行 (模块化版本)');

        const confirmBtn = document.getElementById('confirmSelectionBtn');
        const originalText = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>提交中...';

        try {
            const result = await this.controller.confirmSelection();
            this.showNotification('章节选择已确认！正在进入下一步...', 'success');

            setTimeout(() => {
                if (typeof proceedToStep3 === 'function') {
                    proceedToStep3(result.hitlTaskId, result.projectId);
                } else {
                    console.error('[Step1] proceedToStep3 函数不存在！');
                    alert('错误：proceedToStep3 函数未定义，请刷新页面重试');
                }
            }, 500);

        } catch (error) {
            const { message } = this._handleError(error, 'confirmSelection');
            this.showNotification(message, 'error');
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    }

    async exportSelectedChapters() {
        const selectedChapters = this.controller.stateManager.getSelectedChapters()
            .map(ch => ch.title)
            .join('、');

        const confirmMsg = `确定要导出以下章节吗？\n\n${selectedChapters}\n\n导出后将获得一个包含所有选中章节的Word文档。`;

        if (!confirm(confirmMsg)) {
            return;
        }

        try {
            this.showNotification('正在导出选中章节...', 'info');
            await this.controller.exportChapters();
            this.showNotification('✅ 选中章节已成功导出！', 'success');

        } catch (error) {
            const { message } = this._handleError(error, 'exportSelectedChapters');
            this.showNotification(message, 'error');
        }
    }

    async saveAsResponseFile() {
        try {
            this.showNotification('正在保存应答文件...', 'info');
            const result = await this.controller.saveResponseFile();
            this.showNotification(`✅ 应答文件已成功保存！文件名: ${result.filename}`, 'success');

            // 刷新商务应答Tab的文件信息显示
            if (typeof loadFileInfo === 'function') {
                await loadFileInfo('response', this.currentTaskId);
            }

            // 显示填充应答信息区域
            if (typeof showFillSection === 'function') {
                showFillSection();
            }

        } catch (error) {
            const { message } = this._handleError(error, 'saveAsResponseFile');
            this.showNotification(message, 'error');
        }
    }

    async loadHistoricalChapters(hitlTaskId) {
        console.log('[ChapterSelectionManager] 加载历史章节数据 (模块化版本)，taskId:', hitlTaskId);

        try {
            await this.controller.loadHistoricalChapters(hitlTaskId);

            // 显示章节选择区域
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('chapterSelectionSection').style.display = 'block';

            this.showNotification('历史章节数据加载成功！', 'success');

        } catch (error) {
            const { message } = this._handleError(error, 'loadHistoricalChapters');
            this.showNotification(message, 'error');
        }
    }

    /**
     * 统一错误处理（从原版本复制）
     */
    _handleError(error, context = '') {
        console.error(`[${context}] 错误:`, error);

        let errorType = window.CHAPTER_CONFIG.ERROR_TYPES.UNKNOWN;
        let errorMessage = '';

        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorType = window.CHAPTER_CONFIG.ERROR_TYPES.NETWORK;
        } else if (error.message && error.message.includes('超时')) {
            errorType = window.CHAPTER_CONFIG.ERROR_TYPES.TIMEOUT;
        } else if (error.message && error.message.includes('验证')) {
            errorType = window.CHAPTER_CONFIG.ERROR_TYPES.VALIDATION;
        } else if (error.message) {
            errorType = window.CHAPTER_CONFIG.ERROR_TYPES.SERVER;
            errorMessage = error.message;
        }

        const friendlyMessage = window.CHAPTER_CONFIG.ERROR_MESSAGES[errorType];
        const finalMessage = errorMessage
            ? `${friendlyMessage}：${errorMessage}`
            : friendlyMessage;

        return {
            type: errorType,
            message: finalMessage
        };
    }

    /**
     * 显示通知（使用Bootstrap Toast）
     */
    showNotification(message, type = 'info') {
        let toastContainer = document.getElementById('chapterToastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'chapterToastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const typeConfig = {
            'success': { icon: '✓', bgClass: 'bg-success', title: '成功' },
            'error': { icon: '✕', bgClass: 'bg-danger', title: '错误' },
            'warning': { icon: '⚠', bgClass: 'bg-warning', title: '警告' },
            'info': { icon: 'ℹ', bgClass: 'bg-info', title: '提示' }
        };

        const config = typeConfig[type] || typeConfig['info'];

        const toastEl = document.createElement('div');
        toastEl.className = 'toast';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
            <div class="toast-header ${config.bgClass} text-white">
                <strong class="me-auto">
                    <span class="me-2">${config.icon}</span>${config.title}
                </strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;

        toastContainer.appendChild(toastEl);

        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: window.CHAPTER_CONFIG.NOTIFICATION_DURATION
        });

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });

        toast.show();
    }
}

// 初始化 - 兼容原有接口
document.addEventListener('DOMContentLoaded', () => {
    window.chapterSelectionManager = new ChapterSelectionManagerAdapter();
    console.log('[ChapterSelection] 使用模块化架构 v3.0.0');
});
