/**
 * 标书智能处理 - 步骤1：章节选择
 * 功能：文档结构解析、章节树展示、人工选择
 *
 * @file tender-processing-step1.js
 * @author AI Tender System
 * @version 2.0.0 (优化版)
 */

// ========== 类型定义 ==========
/**
 * @typedef {Object} Chapter
 * @property {string} id - 章节唯一标识
 * @property {string} title - 章节标题
 * @property {number} level - 章节层级
 * @property {number} word_count - 字数统计
 * @property {number} para_start_idx - 开始段落索引
 * @property {number} para_end_idx - 结束段落索引
 * @property {string} preview_text - 预览文本
 * @property {boolean} auto_selected - 是否自动选中
 * @property {boolean} skip_recommended - 是否建议跳过
 * @property {string[]} content_tags - 内容标签
 * @property {Chapter[]} children - 子章节
 */

/**
 * @typedef {Object} Statistics
 * @property {number} selectedCount - 已选章节数
 * @property {number} selectedWords - 已选字数
 * @property {number} totalChapters - 总章节数
 */

// ========== 配置常量 ==========
const CHAPTER_CONFIG = {
    // 搜索防抖延迟（毫秒）
    SEARCH_DEBOUNCE_DELAY: 300,

    // 通知自动消失时间（毫秒）
    NOTIFICATION_DURATION: 4000,

    // 标签颜色映射
    TAG_COLOR_MAP: {
        '评分办法': 'primary',
        '评分表': 'warning text-dark',
        '供应商资质': 'success',
        '文件格式': 'secondary',
        '技术需求': 'info'
    },

    // 状态图标映射
    STATUS_ICONS: {
        AUTO_SELECTED: '✅',
        SKIP_RECOMMENDED: '❌',
        UNSELECTED: '⚪'
    },

    // 错误类型映射
    ERROR_TYPES: {
        NETWORK: 'network',
        VALIDATION: 'validation',
        SERVER: 'server',
        TIMEOUT: 'timeout',
        UNKNOWN: 'unknown'
    },

    // 用户友好的错误消息
    ERROR_MESSAGES: {
        network: '网络连接失败，请检查您的网络设置',
        validation: '数据验证失败，请检查输入内容',
        server: '服务器处理失败，请稍后重试',
        timeout: '请求超时，请重试或联系管理员',
        unknown: '发生未知错误，请刷新页面重试'
    }
};

/**
 * 章节选择管理器
 * 负责文档章节的解析、展示、选择和导出功能
 *
 * @class ChapterSelectionManager
 */
class ChapterSelectionManager {
    /**
     * 创建章节选择管理器实例
     * @constructor
     */
    constructor() {
        /** @type {string|null} 当前任务ID */
        this.currentTaskId = null;

        /** @type {Chapter[]} 章节数据（扁平化） */
        this.chaptersData = [];

        /** @type {Set<string>} 已选中的章节ID集合 */
        this.selectedChapterIds = new Set();

        /** @type {Object} 统计信息 */
        this.statistics = {};

        /** @type {Statistics|null} 性能优化：缓存统计计算结果 */
        this._cachedStatistics = null;

        /** @type {number|null} 搜索防抖计时器 */
        this._searchTimeout = null;

        /** @type {boolean} 防重复提交标志 - 确认选择 */
        this._isSubmitting = false;

        /** @type {boolean} 防重复提交标志 - 导出章节 */
        this._isExporting = false;

        /** @type {boolean} 防重复提交标志 - 保存文件 */
        this._isSaving = false;

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
            // 忽略在输入框中的按键
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

        // 添加快捷键提示（可选）
        console.log('[ChapterSelection] 键盘快捷键已启用:');
        console.log('  Ctrl/Cmd + A: 全选章节');
        console.log('  Ctrl/Cmd + D: 取消全选');
        console.log('  /: 聚焦搜索框');
        console.log('  Esc: 清空搜索');
    }

    /**
     * 显示加载骨架屏
     */
    _showLoadingSkeleton() {
        const container = document.getElementById('chapterTreeContainer');
        container.innerHTML = `
            <div class="skeleton-loading">
                ${Array(5).fill(0).map((_, i) => `
                    <div class="skeleton-item" style="animation-delay: ${i * 0.1}s">
                        <div class="skeleton-checkbox"></div>
                        <div class="skeleton-text" style="width: ${60 + Math.random() * 30}%"></div>
                        <div class="skeleton-badge"></div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * 隐藏加载骨架屏
     */
    _hideLoadingSkeleton() {
        const container = document.getElementById('chapterTreeContainer');
        const skeleton = container.querySelector('.skeleton-loading');
        if (skeleton) {
            skeleton.remove();
        }
    }

    /**
     * 处理文档结构解析
     */
    async handleParseStructure() {
        const fileInput = document.getElementById('tenderDocFile');

        // 使用 HITLConfigManager 获取配置
        const config = HITLConfigManager.getConfig();

        // 检查是否有新文件上传
        const hasNewFile = fileInput.files && fileInput.files[0];

        // 检查是否有历史文件（从 projectDataBridge 获取）
        const historicalFile = typeof window.projectDataBridge !== 'undefined'
            ? window.projectDataBridge.getFileInfo('originalTender')
            : null;

        if (!hasNewFile && !historicalFile) {
            this.showNotification('请先选择文件', 'warning');
            return;
        }

        // 验证必填项：company_id
        if (!config.companyId) {
            this.showNotification('请先选择应答公司', 'warning');
            return;
        }

        // projectId 可以为空（新建项目）或有值（关联已有项目）

        const parseBtn = document.getElementById('parseStructureBtn');
        const originalText = parseBtn.innerHTML;
        parseBtn.disabled = true;
        parseBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>解析中...';

        // 显示加载骨架屏
        const chapterSelectionSection = document.getElementById('chapterSelectionSection');
        if (chapterSelectionSection) {
            chapterSelectionSection.style.display = 'block';
            this._showLoadingSkeleton();
        }

        try {
            // 构建 FormData
            const formData = new FormData();

            if (hasNewFile) {
                // 使用新上传的文件
                formData.append('file', fileInput.files[0]);
                console.log('[handleParseStructure] 使用新上传的文件');
            } else {
                // 使用历史文件路径
                formData.append('file_path', historicalFile.filePath);
                console.log('[handleParseStructure] 使用历史文件:', historicalFile.filePath);
            }

            formData.append('company_id', config.companyId);

            // 如果选择了项目，传递project_id；否则后端会创建新项目
            if (config.projectId) {
                formData.append('project_id', config.projectId);
            }

            // 调用解析API
            const response = await fetch('/api/tender-processing/parse-structure', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentTaskId = result.task_id;
                this.statistics = result.statistics;

                // 如果后端返回了新的project_id（新建项目的情况），更新配置管理器
                if (result.project_id && !config.projectId) {
                    HITLConfigManager.currentProjectId = result.project_id;
                    console.log(`✅ 新项目已创建并关联: ${result.project_id}`);
                    this.showNotification(`新项目已创建: ${result.project_id}`, 'info');

                    // 刷新项目列表并更新选择器
                    await HITLConfigManager.loadProjects();
                    const projectSelect = document.getElementById('hitlProjectSelect');
                    if (projectSelect) {
                        projectSelect.value = result.project_id;
                        console.log(`✅ 项目选择器已同步: ${result.project_id}`);
                    }
                }

                // 扁平化章节树
                this.chaptersData = this.flattenChapters(result.chapters);

                // ✅ 保存章节树到全局变量，供预览功能使用
                window.parsedChapters = result.chapters;
                window.currentTaskId = this.currentTaskId;
                console.log('[handleParseStructure] 章节数据已保存到window.parsedChapters，task_id:', this.currentTaskId);

                // 隐藏骨架屏并渲染章节树
                this._hideLoadingSkeleton();
                this.renderChapterTree(result.chapters);

                // 更新统计信息
                this.updateStatistics();

                // 显示章节选择区域
                document.getElementById('uploadSection').style.display = 'none';
                document.getElementById('chapterSelectionSection').style.display = 'block';

                this.showNotification('文档解析成功！', 'success');
            } else {
                throw new Error(result.error || '解析失败');
            }

        } catch (error) {
            // 使用统一错误处理
            const { message } = this._handleError(error, 'handleParseStructure');
            this.showNotification(message, 'error');
            // 解析失败时也要隐藏骨架屏
            this._hideLoadingSkeleton();
        } finally {
            parseBtn.disabled = false;
            parseBtn.innerHTML = originalText;
        }
    }

    /**
     * 将章节树扁平化为一维数组
     * @param {Chapter[]} chapters - 章节树
     * @param {Chapter[]} result - 累积结果数组
     * @returns {Chapter[]} 扁平化的章节数组
     */
    flattenChapters(chapters, result = []) {
        for (const ch of chapters) {
            result.push(ch);
            if (ch.children && ch.children.length > 0) {
                this.flattenChapters(ch.children, result);
            }
        }
        return result;
    }

    /**
     * 渲染章节树（使用DocumentFragment优化性能）
     * @param {Array} chapters - 章节数组
     * @param {HTMLElement} container - 容器元素
     * @param {number} level - 章节层级
     */
    renderChapterTree(chapters, container = null, level = 0) {
        if (!container) {
            container = document.getElementById('chapterTreeContainer');
            container.innerHTML = '';
        }

        // 使用DocumentFragment批量添加DOM元素，减少重排次数
        const fragment = document.createDocumentFragment();

        for (const chapter of chapters) {
            const chapterDiv = this.createChapterElement(chapter, level);
            fragment.appendChild(chapterDiv);

            // 递归渲染子章节
            if (chapter.children && chapter.children.length > 0) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'chapter-children ms-3';
                childrenContainer.id = `children-${chapter.id}`;
                this.renderChapterTree(chapter.children, childrenContainer, level + 1);
                fragment.appendChild(childrenContainer);
            }
        }

        // 一次性添加所有元素到DOM
        container.appendChild(fragment);
    }

    /**
     * 创建章节DOM元素
     * @param {Chapter} chapter - 章节数据
     * @param {number} level - 章节层级
     * @returns {HTMLDivElement} 章节DOM元素
     */
    createChapterElement(chapter, level) {
        const div = document.createElement('div');
        div.className = `chapter-item level-${chapter.level}`;
        div.dataset.chapterId = chapter.id;

        // 章节状态标记（使用配置常量）
        let statusIcon = CHAPTER_CONFIG.STATUS_ICONS.UNSELECTED;
        let statusClass = '';
        if (chapter.auto_selected) {
            statusIcon = CHAPTER_CONFIG.STATUS_ICONS.AUTO_SELECTED;
            statusClass = 'auto-selected';
            this.selectedChapterIds.add(chapter.id);
        } else if (chapter.skip_recommended) {
            statusIcon = CHAPTER_CONFIG.STATUS_ICONS.SKIP_RECOMMENDED;
            statusClass = 'skip-recommended';
        }

        // 生成标签HTML（使用配置常量）
        let tagsHtml = '';
        if (chapter.content_tags && chapter.content_tags.length > 0) {
            tagsHtml = chapter.content_tags.map(tag => {
                const colorClass = CHAPTER_CONFIG.TAG_COLOR_MAP[tag] || 'secondary';
                return `<span class="badge bg-${colorClass} ms-1">${tag}</span>`;
            }).join('');
        }

        div.innerHTML = `
            <div class="d-flex align-items-center chapter-row ${statusClass}">
                <input type="checkbox"
                       class="form-check-input me-2 chapter-checkbox"
                       id="ch-${chapter.id}"
                       ${chapter.auto_selected ? 'checked' : ''}>
                <span class="chapter-status me-2">${statusIcon}</span>
                <label class="chapter-title flex-grow-1" for="ch-${chapter.id}">
                    ${chapter.title}
                    <small class="text-muted">(${chapter.word_count}字)</small>
                    ${tagsHtml}
                </label>
                <button class="btn btn-sm btn-outline-secondary preview-btn"
                        data-chapter-id="${chapter.id}"
                        title="预览章节内容">
                    <i class="bi bi-eye"></i> 预览
                </button>
            </div>
        `;

        // 绑定事件
        const checkbox = div.querySelector('.chapter-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedChapterIds.add(chapter.id);
            } else {
                this.selectedChapterIds.delete(chapter.id);
            }
            // 清除缓存并更新统计
            this._clearStatisticsCache();
            this.updateStatistics();
        });

        const previewBtn = div.querySelector('.preview-btn');
        previewBtn.addEventListener('click', () => this.showPreview(chapter));

        return div;
    }

    /**
     * 显示章节预览
     * @param {Chapter} chapter - 章节数据
     */
    showPreview(chapter) {
        // 使用全局的showChapterPreviewModal函数（来自step3-enhanced.js）
        if (typeof showChapterPreviewModal === 'function') {
            showChapterPreviewModal(chapter.id);
        } else {
            console.error('[showPreview] showChapterPreviewModal函数未定义，无法显示预览');
            this.showNotification('预览功能未加载，请刷新页面重试', 'error');
        }
    }

    /**
     * 统一错误处理方法
     * @param {Error} error - 错误对象
     * @param {string} context - 错误上下文
     * @returns {{type: string, message: string}} 错误信息
     */
    _handleError(error, context = '') {
        console.error(`[${context}] 错误:`, error);

        let errorType = CHAPTER_CONFIG.ERROR_TYPES.UNKNOWN;
        let errorMessage = '';

        // 判断错误类型
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorType = CHAPTER_CONFIG.ERROR_TYPES.NETWORK;
        } else if (error.message && error.message.includes('超时')) {
            errorType = CHAPTER_CONFIG.ERROR_TYPES.TIMEOUT;
        } else if (error.message && error.message.includes('验证')) {
            errorType = CHAPTER_CONFIG.ERROR_TYPES.VALIDATION;
        } else if (error.message) {
            errorType = CHAPTER_CONFIG.ERROR_TYPES.SERVER;
            errorMessage = error.message;
        }

        // 获取用户友好的错误消息
        const friendlyMessage = CHAPTER_CONFIG.ERROR_MESSAGES[errorType];

        // 组合最终消息
        const finalMessage = errorMessage
            ? `${friendlyMessage}：${errorMessage}`
            : friendlyMessage;

        return {
            type: errorType,
            message: finalMessage
        };
    }

    /**
     * 计算统计数据（内部方法）
     * @returns {{selectedCount: number, selectedWords: number, totalChapters: number}}
     */
    _calculateStatistics() {
        const selectedCount = this.selectedChapterIds.size;
        const selectedWords = this.chaptersData
            .filter(ch => this.selectedChapterIds.has(ch.id))
            .reduce((sum, ch) => sum + ch.word_count, 0);

        return {
            selectedCount,
            selectedWords,
            totalChapters: this.chaptersData.length
        };
    }

    /**
     * 清除统计缓存（在选择变更时调用）
     */
    _clearStatisticsCache() {
        this._cachedStatistics = null;
    }

    /**
     * 更新统计信息显示（使用缓存优化）
     */
    updateStatistics() {
        // 如果有缓存，使用缓存；否则重新计算
        if (!this._cachedStatistics) {
            this._cachedStatistics = this._calculateStatistics();
        }

        const { selectedCount, selectedWords, totalChapters } = this._cachedStatistics;

        document.getElementById('statTotalChapters').textContent = totalChapters;
        document.getElementById('statSelectedChapters').textContent = selectedCount;
        document.getElementById('statSelectedWords').textContent = selectedWords;

        // 更新导出按钮状态
        const exportBtn = document.getElementById('exportSelectedChaptersBtn');
        if (exportBtn) {
            exportBtn.disabled = selectedCount === 0;
        }

        // 更新另存为应答文件按钮状态
        const saveBtn = document.getElementById('saveAsResponseFileBtn');
        if (saveBtn) {
            saveBtn.disabled = selectedCount === 0;
        }
    }

    /**
     * 全选章节（优化版：批量DOM操作）
     */
    selectAll() {
        // 批量更新Set
        this.chaptersData.forEach(ch => {
            if (!ch.skip_recommended) {
                this.selectedChapterIds.add(ch.id);
            }
        });

        // 批量更新DOM：使用requestAnimationFrame优化渲染
        requestAnimationFrame(() => {
            this.chaptersData.forEach(ch => {
                if (!ch.skip_recommended) {
                    const checkbox = document.getElementById(`ch-${ch.id}`);
                    if (checkbox) checkbox.checked = true;
                }
            });
        });

        this._clearStatisticsCache();
        this.updateStatistics();
        this.showNotification(`已选择 ${this.selectedChapterIds.size} 个章节`, 'success');
    }

    /**
     * 取消全选（优化版：批量DOM操作）
     */
    unselectAll() {
        const previousCount = this.selectedChapterIds.size;
        this.selectedChapterIds.clear();

        // 批量更新DOM：使用requestAnimationFrame优化渲染
        requestAnimationFrame(() => {
            document.querySelectorAll('.chapter-checkbox').forEach(cb => cb.checked = false);
        });

        this._clearStatisticsCache();
        this.updateStatistics();
        this.showNotification(`已取消选择 ${previousCount} 个章节`, 'info');
    }

    selectByKeyword(keyword) {
        this.chaptersData.forEach(ch => {
            if (ch.title.includes(keyword) && !ch.skip_recommended) {
                this.selectedChapterIds.add(ch.id);
                const checkbox = document.getElementById(`ch-${ch.id}`);
                if (checkbox) checkbox.checked = true;
            }
        });
        this._clearStatisticsCache();
        this.updateStatistics();
        this.showNotification(`已选中包含"${keyword}"的章节`, 'info');
    }

    excludeByKeyword(keyword) {
        this.chaptersData.forEach(ch => {
            if (ch.title.includes(keyword)) {
                this.selectedChapterIds.delete(ch.id);
                const checkbox = document.getElementById(`ch-${ch.id}`);
                if (checkbox) checkbox.checked = false;
            }
        });
        this._clearStatisticsCache();
        this.updateStatistics();
        this.showNotification(`已排除包含"${keyword}"的章节`, 'info');
    }

    handleSearch(query) {
        // 清除之前的防抖计时器
        if (this._searchTimeout) {
            clearTimeout(this._searchTimeout);
        }

        // 设置新的防抖计时器
        this._searchTimeout = setTimeout(() => {
            const normalizedQuery = query.toLowerCase();

            document.querySelectorAll('.chapter-item').forEach(item => {
                const title = item.querySelector('.chapter-title').textContent.toLowerCase();
                if (title.includes(normalizedQuery)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }, CHAPTER_CONFIG.SEARCH_DEBOUNCE_DELAY);
    }

    async confirmSelection() {
        console.log('[Step1] confirmSelection 开始执行');

        // 防重复提交
        if (this._isSubmitting) {
            console.log('[Step1] 已有提交任务正在进行，忽略重复点击');
            return;
        }

        if (this.selectedChapterIds.size === 0) {
            this.showNotification('请至少选择一个章节', 'warning');
            return;
        }

        this._isSubmitting = true;

        const confirmBtn = document.getElementById('confirmSelectionBtn');
        const originalText = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>提交中...';

        try {
            console.log('[Step1] 发送API请求，taskId:', this.currentTaskId);
            const response = await fetch('/api/tender-processing/select-chapters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: this.currentTaskId,
                    selected_chapter_ids: Array.from(this.selectedChapterIds)
                })
            });

            const result = await response.json();
            console.log('[Step1] API响应结果:', result);

            if (result.success) {
                this.showNotification('章节选择已确认！正在进入下一步...', 'success');

                console.log('[Step1] 准备调用 proceedToStep3');
                console.log('[Step1] proceedToStep3 是否存在:', typeof proceedToStep3);
                console.log('[Step1] hitl_task_id:', result.hitl_task_id, 'project_id:', result.project_id);

                // 直接进入步骤3，不显示提示框
                setTimeout(() => {
                    console.log('[Step1] 开始执行 proceedToStep3');
                    if (typeof proceedToStep3 === 'function') {
                        proceedToStep3(result.hitl_task_id, result.project_id);
                    } else {
                        console.error('[Step1] proceedToStep3 函数不存在！');
                        alert('错误：proceedToStep3 函数未定义，请刷新页面重试');
                    }
                }, 500);
            } else {
                throw new Error(result.error || '提交失败');
            }

        } catch (error) {
            // 使用统一错误处理
            const { message } = this._handleError(error, 'confirmSelection');
            this.showNotification(message, 'error');
        } finally {
            this._isSubmitting = false;
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    }

    /**
     * 导出选中的章节为Word模板
     */
    async exportSelectedChapters() {
        // 防重复点击
        if (this._isExporting) {
            console.log('[exportSelectedChapters] 已有导出任务正在进行，忽略重复点击');
            return;
        }

        if (this.selectedChapterIds.size === 0) {
            this.showNotification('请先选择要导出的章节', 'warning');
            return;
        }

        // 获取选中章节的标题列表
        const selectedChapters = this.chaptersData
            .filter(ch => this.selectedChapterIds.has(ch.id))
            .map(ch => ch.title)
            .join('、');

        const confirmMsg = `确定要导出以下章节吗？\n\n${selectedChapters}\n\n导出后将获得一个包含所有选中章节的Word文档。`;

        if (!confirm(confirmMsg)) {
            return;
        }

        this._isExporting = true;

        try {
            const chapterIds = Array.from(this.selectedChapterIds);
            const apiUrl = `/api/tender-processing/export-chapters/${this.currentTaskId}`;

            this.showNotification('正在导出选中章节...', 'info');

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chapter_ids: chapterIds })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '导出失败');
            }

            // 获取文件Blob
            const blob = await response.blob();

            // 创建下载链接
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // 从响应头获取文件名
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = '选中章节_应答模板.docx';

            if (contentDisposition) {
                const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (match?.[1]) {
                    filename = decodeURIComponent(match[1].replace(/['"]/g, ''));
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showNotification('✅ 选中章节已成功导出！', 'success');

        } catch (error) {
            // 使用统一错误处理
            const { message } = this._handleError(error, 'exportSelectedChapters');
            this.showNotification(message, 'error');
        } finally {
            this._isExporting = false;
        }
    }

    /**
     * 另存为应答文件
     */
    async saveAsResponseFile() {
        // 防重复点击
        if (this._isSaving) {
            console.log('[saveAsResponseFile] 已有保存任务正在进行，忽略重复点击');
            return;
        }

        if (this.selectedChapterIds.size === 0) {
            this.showNotification('请先选择要保存的章节', 'warning');
            return;
        }

        this._isSaving = true;

        try {
            const chapterIds = Array.from(this.selectedChapterIds);
            const apiUrl = `/api/tender-processing/save-response-file/${this.currentTaskId}`;

            this.showNotification('正在保存应答文件...', 'info');

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chapter_ids: chapterIds })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '保存失败');
            }

            this.showNotification(`✅ 应答文件已成功保存！文件名: ${result.filename}`, 'success');

            // 刷新商务应答Tab的文件信息显示
            if (typeof loadFileInfo === 'function') {
                console.log('[saveAsResponseFile] 调用 loadFileInfo 刷新商务应答Tab');
                await loadFileInfo('response', this.currentTaskId);
            } else {
                console.warn('[saveAsResponseFile] loadFileInfo 函数未定义');
            }

            // 保存成功后，显示填充应答信息区域
            if (typeof showFillSection === 'function') {
                console.log('[saveAsResponseFile] 调用 showFillSection 显示填充区域');
                showFillSection();
            } else {
                console.warn('[saveAsResponseFile] showFillSection 函数未定义');
            }

        } catch (error) {
            // 使用统一错误处理
            const { message } = this._handleError(error, 'saveAsResponseFile');
            this.showNotification(message, 'error');
        } finally {
            this._isSaving = false;
        }
    }

    /**
     * 【新增】加载历史项目的章节数据
     * 当用户选择历史项目时，从数据库恢复章节树和选中状态
     */
    async loadHistoricalChapters(hitlTaskId) {
        console.log('[ChapterSelectionManager] 加载历史章节数据，taskId:', hitlTaskId);

        try {
            // 1. 从API获取章节列表（从tender_document_chapters表）
            const chaptersResponse = await fetch(`/api/tender-processing/chapters/${hitlTaskId}`);
            const chaptersData = await chaptersResponse.json();

            if (!chaptersData.success || !chaptersData.chapters) {
                throw new Error('无法加载章节数据');
            }

            console.log('[ChapterSelectionManager] 加载了', chaptersData.chapters.length, '个章节');

            // 2. 获取已选中的章节ID列表（从step1_data）
            const taskResponse = await fetch(`/api/tender-processing/hitl-tasks/${hitlTaskId}`);
            const taskData = await taskResponse.json();

            let selectedIds = [];
            if (taskData.success && taskData.task && taskData.task.step1_data) {
                try {
                    const step1Data = typeof taskData.task.step1_data === 'string'
                        ? JSON.parse(taskData.task.step1_data)
                        : taskData.task.step1_data;

                    if (step1Data.selected_ids && Array.isArray(step1Data.selected_ids)) {
                        selectedIds = step1Data.selected_ids;
                        console.log('[ChapterSelectionManager] 找到已选中章节:', selectedIds.length, '个');
                    }
                } catch (parseError) {
                    console.warn('[ChapterSelectionManager] 解析step1_data失败:', parseError);
                }
            }

            // 3. 保存taskId
            this.currentTaskId = hitlTaskId;

            // 4. 构建章节树结构
            const chaptersTree = this.buildChapterTree(chaptersData.chapters);

            // 5. 扁平化章节数据
            this.chaptersData = this.flattenChapters(chaptersTree);

            // ✅ 保存章节树到全局变量，供预览功能使用
            window.parsedChapters = chaptersTree;
            window.currentTaskId = this.currentTaskId;
            console.log('[loadHistoricalChapters] 章节数据已保存到window.parsedChapters，task_id:', this.currentTaskId);

            // 6. 恢复已选中的章节
            this.selectedChapterIds = new Set(selectedIds);
            console.log('[ChapterSelectionManager] 恢复已选中章节:', this.selectedChapterIds.size, '个');

            // 7. 渲染章节树
            this.renderChapterTree(chaptersTree);

            // 8. 更新统计信息
            this.updateStatistics();

            // 9. 显示章节选择区域
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('chapterSelectionSection').style.display = 'block';

            this.showNotification('历史章节数据加载成功！', 'success');
            console.log('[ChapterSelectionManager] 历史章节加载完成');

        } catch (error) {
            console.error('[ChapterSelectionManager] 加载历史章节失败:', error);
            this.showNotification('加载历史章节失败: ' + error.message, 'error');
        }
    }

    /**
     * 从扁平化的章节列表构建树形结构
     */
    buildChapterTree(chapters) {
        // 按章节ID排序
        const sortedChapters = [...chapters].sort((a, b) => {
            const aId = a.id || a.chapter_node_id || '';
            const bId = b.id || b.chapter_node_id || '';
            return aId.localeCompare(bId);
        });

        // 转换数据格式（兼容两种格式：API返回的和数据库格式）
        const formatted = sortedChapters.map(ch => ({
            id: ch.id || ch.chapter_node_id,
            title: ch.title,
            level: ch.level,
            word_count: ch.word_count || 0,
            para_start_idx: ch.para_start_idx,
            para_end_idx: ch.para_end_idx,
            preview_text: ch.preview_text || '',
            auto_selected: ch.auto_selected || false,
            skip_recommended: ch.skip_recommended || false,
            is_selected: ch.is_selected || false,
            content_tags: ch.content_tags || [],
            children: []
        }));

        // 构建父子关系
        const nodeMap = new Map();
        const rootNodes = [];

        // 第一遍：建立映射
        formatted.forEach(node => {
            nodeMap.set(node.id, node);
        });

        // 第二遍：建立父子关系
        formatted.forEach(node => {
            const parts = node.id.split('_').slice(1); // 去掉 'ch_' 前缀
            if (parts.length === 1) {
                // 一级章节
                rootNodes.push(node);
            } else {
                // 子章节，找到父节点
                const parentParts = parts.slice(0, -1);
                const parentId = 'ch_' + parentParts.join('_');
                const parent = nodeMap.get(parentId);
                if (parent) {
                    parent.children.push(node);
                } else {
                    // 如果找不到父节点，作为根节点
                    rootNodes.push(node);
                }
            }
        });

        return rootNodes;
    }

    /**
     * 显示通知消息（使用Bootstrap Toast）
     * @param {string} message - 通知消息
     * @param {string} type - 通知类型：success, error, warning, info
     */
    showNotification(message, type = 'info') {
        // 确保有toast容器
        let toastContainer = document.getElementById('chapterToastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'chapterToastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // 类型到图标和颜色的映射
        const typeConfig = {
            'success': { icon: '✓', bgClass: 'bg-success', title: '成功' },
            'error': { icon: '✕', bgClass: 'bg-danger', title: '错误' },
            'warning': { icon: '⚠', bgClass: 'bg-warning', title: '警告' },
            'info': { icon: 'ℹ', bgClass: 'bg-info', title: '提示' }
        };

        const config = typeConfig[type] || typeConfig['info'];

        // 创建toast元素
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

        // 初始化并显示toast
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: CHAPTER_CONFIG.NOTIFICATION_DURATION
        });

        // Toast隐藏后移除DOM元素
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });

        toast.show();
    }
}

// 初始化 - 将 chapterSelectionManager 设为全局变量，以便其他模块访问
document.addEventListener('DOMContentLoaded', () => {
    window.chapterSelectionManager = new ChapterSelectionManager();
});

// 进入步骤2的函数（占位）
function proceedToStep2(taskId) {
    alert(`准备进入步骤2，任务ID: ${taskId}`);
    // TODO: 实现步骤2的逻辑
}
