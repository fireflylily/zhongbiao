/**
 * 标书智能处理 - 步骤1：章节选择（模块化架构版本）
 *
 * @file tender-processing-step1-modular.js
 * @author AI Tender System
 * @version 3.0.0 (模块化重构版)
 *
 * 架构说明：
 * - ChapterAPIService: API调用层，负责所有后端通信
 * - ChapterStateManager: 状态管理层，负责数据状态维护
 * - ChapterTreeRenderer: UI渲染层，负责DOM操作
 * - ChapterSelectionController: 协调器，组合各服务协同工作
 */

// ========== 类型定义（复用原配置） ==========
/**
 * @typedef {Object} Chapter
 * @property {string} id
 * @property {string} title
 * @property {number} level
 * @property {number} word_count
 * @property {boolean} auto_selected
 * @property {boolean} skip_recommended
 * @property {string[]} content_tags
 * @property {Chapter[]} children
 */

// ========== 配置常量（从原文件导入） ==========
// 注意：实际使用时应从原文件引用 CHAPTER_CONFIG

// ========================================================================
// 1. API调用层 - ChapterAPIService
// 职责：统一处理所有后端API请求
// ========================================================================

/**
 * 章节API服务类
 * 负责所有与后端的通信，提供统一的API调用接口
 *
 * @class ChapterAPIService
 */
class ChapterAPIService {
    /**
     * 解析文档结构
     * @param {FormData} formData - 包含文件和配置的表单数据
     * @returns {Promise<Object>} 解析结果
     */
    async parseStructure(formData) {
        const response = await fetch('/api/tender-processing/parse-structure', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * 提交选中的章节
     * @param {string} taskId - 任务ID
     * @param {string[]} chapterIds - 选中的章节ID列表
     * @returns {Promise<Object>} 提交结果
     */
    async selectChapters(taskId, chapterIds) {
        const response = await fetch('/api/tender-processing/select-chapters', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                task_id: taskId,
                selected_chapter_ids: chapterIds
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * 导出选中章节为Word文档
     * @param {string} taskId - 任务ID
     * @param {string[]} chapterIds - 章节ID列表
     * @returns {Promise<Blob>} Word文档Blob
     */
    async exportChapters(taskId, chapterIds) {
        const response = await fetch(`/api/tender-processing/export-chapters/${taskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chapter_ids: chapterIds })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || '导出失败');
        }

        return await response.blob();
    }

    /**
     * 保存应答文件
     * @param {string} taskId - 任务ID
     * @param {string[]} chapterIds - 章节ID列表
     * @returns {Promise<Object>} 保存结果
     */
    async saveResponseFile(taskId, chapterIds) {
        const response = await fetch(`/api/tender-processing/save-response-file/${taskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chapter_ids: chapterIds })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '保存失败');
        }

        return result;
    }

    /**
     * 加载历史章节数据
     * @param {string} hitlTaskId - HITL任务ID
     * @returns {Promise<{chapters: Array, selectedIds: string[]}>}
     */
    async loadHistoricalChapters(hitlTaskId) {
        // 获取章节列表
        const chaptersResponse = await fetch(`/api/tender-processing/chapters/${hitlTaskId}`);
        const chaptersData = await chaptersResponse.json();

        if (!chaptersData.success || !chaptersData.chapters) {
            throw new Error('无法加载章节数据');
        }

        // 获取已选中的章节ID
        const taskResponse = await fetch(`/api/tender-processing/hitl-tasks/${hitlTaskId}`);
        const taskData = await taskResponse.json();

        let selectedIds = [];
        if (taskData.success && taskData.task && taskData.task.step1_data) {
            const step1Data = typeof taskData.task.step1_data === 'string'
                ? JSON.parse(taskData.task.step1_data)
                : taskData.task.step1_data;

            if (step1Data.selected_ids && Array.isArray(step1Data.selected_ids)) {
                selectedIds = step1Data.selected_ids;
            }
        }

        return {
            chapters: chaptersData.chapters,
            selectedIds
        };
    }
}

// ========================================================================
// 2. 状态管理层 - ChapterStateManager
// 职责：管理章节数据和选择状态
// ========================================================================

/**
 * 章节状态管理类
 * 负责维护章节数据、选择状态和统计信息
 *
 * @class ChapterStateManager
 */
class ChapterStateManager {
    constructor() {
        /** @type {string|null} 当前任务ID */
        this.taskId = null;

        /** @type {Chapter[]} 章节树（原始结构） */
        this.chaptersTree = [];

        /** @type {Chapter[]} 章节数据（扁平化） */
        this.chaptersFlat = [];

        /** @type {Set<string>} 已选中的章节ID */
        this.selectedIds = new Set();

        /** @type {Object|null} 缓存的统计数据 */
        this._cachedStats = null;
    }

    /**
     * 设置章节数据
     * @param {Chapter[]} chaptersTree - 章节树
     * @param {string} taskId - 任务ID
     */
    setChapters(chaptersTree, taskId) {
        this.taskId = taskId;
        this.chaptersTree = chaptersTree;
        this.chaptersFlat = this._flattenChapters(chaptersTree);

        // 自动选中auto_selected的章节
        this.selectedIds.clear();
        this.chaptersFlat.forEach(ch => {
            if (ch.auto_selected) {
                this.selectedIds.add(ch.id);
            }
        });

        this._clearStatsCache();
    }

    /**
     * 切换章节选择状态
     * @param {string} chapterId - 章节ID
     * @param {boolean} selected - 是否选中
     */
    toggleSelection(chapterId, selected) {
        if (selected) {
            this.selectedIds.add(chapterId);
        } else {
            this.selectedIds.delete(chapterId);
        }
        this._clearStatsCache();
    }

    /**
     * 全选章节（排除skip_recommended）
     * @returns {number} 选中的章节数
     */
    selectAll() {
        this.chaptersFlat.forEach(ch => {
            if (!ch.skip_recommended) {
                this.selectedIds.add(ch.id);
            }
        });
        this._clearStatsCache();
        return this.selectedIds.size;
    }

    /**
     * 取消全选
     * @returns {number} 之前选中的章节数
     */
    unselectAll() {
        const previousCount = this.selectedIds.size;
        this.selectedIds.clear();
        this._clearStatsCache();
        return previousCount;
    }

    /**
     * 根据关键词选择章节
     * @param {string} keyword - 关键词
     * @returns {number} 新选中的章节数
     */
    selectByKeyword(keyword) {
        let count = 0;
        this.chaptersFlat.forEach(ch => {
            if (ch.title.includes(keyword) && !ch.skip_recommended && !this.selectedIds.has(ch.id)) {
                this.selectedIds.add(ch.id);
                count++;
            }
        });
        this._clearStatsCache();
        return count;
    }

    /**
     * 根据关键词排除章节
     * @param {string} keyword - 关键词
     * @returns {number} 取消选中的章节数
     */
    excludeByKeyword(keyword) {
        let count = 0;
        this.chaptersFlat.forEach(ch => {
            if (ch.title.includes(keyword) && this.selectedIds.has(ch.id)) {
                this.selectedIds.delete(ch.id);
                count++;
            }
        });
        this._clearStatsCache();
        return count;
    }

    /**
     * 获取统计信息（带缓存）
     * @returns {{selectedCount: number, selectedWords: number, totalChapters: number}}
     */
    getStatistics() {
        if (!this._cachedStats) {
            this._cachedStats = this._calculateStatistics();
        }
        return this._cachedStats;
    }

    /**
     * 获取选中的章节ID数组
     * @returns {string[]}
     */
    getSelectedIds() {
        return Array.from(this.selectedIds);
    }

    /**
     * 获取选中的章节数据
     * @returns {Chapter[]}
     */
    getSelectedChapters() {
        return this.chaptersFlat.filter(ch => this.selectedIds.has(ch.id));
    }

    /**
     * 清除统计缓存
     * @private
     */
    _clearStatsCache() {
        this._cachedStats = null;
    }

    /**
     * 计算统计数据
     * @private
     * @returns {{selectedCount: number, selectedWords: number, totalChapters: number}}
     */
    _calculateStatistics() {
        const selectedCount = this.selectedIds.size;
        const selectedWords = this.chaptersFlat
            .filter(ch => this.selectedIds.has(ch.id))
            .reduce((sum, ch) => sum + ch.word_count, 0);

        return {
            selectedCount,
            selectedWords,
            totalChapters: this.chaptersFlat.length
        };
    }

    /**
     * 扁平化章节树
     * @private
     * @param {Chapter[]} chapters
     * @param {Chapter[]} result
     * @returns {Chapter[]}
     */
    _flattenChapters(chapters, result = []) {
        for (const ch of chapters) {
            result.push(ch);
            if (ch.children && ch.children.length > 0) {
                this._flattenChapters(ch.children, result);
            }
        }
        return result;
    }

    /**
     * 从扁平列表构建树形结构
     * @param {Chapter[]} flatChapters
     * @returns {Chapter[]}
     */
    buildChapterTree(flatChapters) {
        const sorted = [...flatChapters].sort((a, b) => {
            const aId = a.id || a.chapter_node_id || '';
            const bId = b.id || b.chapter_node_id || '';
            return aId.localeCompare(bId);
        });

        const formatted = sorted.map(ch => ({
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

        const nodeMap = new Map();
        const rootNodes = [];

        formatted.forEach(node => nodeMap.set(node.id, node));

        formatted.forEach(node => {
            const parts = node.id.split('_').slice(1);
            if (parts.length === 1) {
                rootNodes.push(node);
            } else {
                const parentParts = parts.slice(0, -1);
                const parentId = 'ch_' + parentParts.join('_');
                const parent = nodeMap.get(parentId);
                if (parent) {
                    parent.children.push(node);
                } else {
                    rootNodes.push(node);
                }
            }
        });

        return rootNodes;
    }
}

// ========================================================================
// 3. UI渲染层 - ChapterTreeRenderer
// 职责：负责所有DOM渲染和UI更新
// ========================================================================

/**
 * 章节树渲染类
 * 负责将章节数据渲染为DOM，处理UI交互
 *
 * @class ChapterTreeRenderer
 */
class ChapterTreeRenderer {
    constructor(config) {
        this.config = config || window.CHAPTER_CONFIG;
        this.container = null;
        this.onSelectionChange = null;
        this.onPreview = null;
    }

    /**
     * 设置容器元素
     * @param {HTMLElement|string} container
     */
    setContainer(container) {
        this.container = typeof container === 'string'
            ? document.getElementById(container)
            : container;
    }

    /**
     * 渲染章节树
     * @param {Chapter[]} chapters
     * @param {Set<string>} selectedIds
     */
    renderTree(chapters, selectedIds) {
        if (!this.container) {
            console.error('[ChapterTreeRenderer] 未设置容器');
            return;
        }

        this.container.innerHTML = '';
        const fragment = this._createTreeFragment(chapters, selectedIds);
        this.container.appendChild(fragment);
    }

    /**
     * 更新统计信息显示
     * @param {{selectedCount: number, selectedWords: number, totalChapters: number}} stats
     */
    updateStatistics(stats) {
        const totalEl = document.getElementById('statTotalChapters');
        const selectedEl = document.getElementById('statSelectedChapters');
        const wordsEl = document.getElementById('statSelectedWords');

        if (totalEl) totalEl.textContent = stats.totalChapters;
        if (selectedEl) selectedEl.textContent = stats.selectedCount;
        if (wordsEl) wordsEl.textContent = stats.selectedWords;

        // 更新按钮状态
        this._updateButtonStates(stats.selectedCount);
    }

    /**
     * 显示加载骨架屏
     */
    showLoadingSkeleton() {
        if (!this.container) return;

        this.container.innerHTML = `
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
    hideLoadingSkeleton() {
        if (!this.container) return;

        const skeleton = this.container.querySelector('.skeleton-loading');
        if (skeleton) {
            skeleton.remove();
        }
    }

    /**
     * 创建章节树Fragment
     * @private
     */
    _createTreeFragment(chapters, selectedIds, level = 0) {
        const fragment = document.createDocumentFragment();

        for (const chapter of chapters) {
            const chapterDiv = this._createChapterElement(chapter, selectedIds.has(chapter.id));
            fragment.appendChild(chapterDiv);

            if (chapter.children && chapter.children.length > 0) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'chapter-children ms-3';
                childrenContainer.id = `children-${chapter.id}`;

                const childFragment = this._createTreeFragment(chapter.children, selectedIds, level + 1);
                childrenContainer.appendChild(childFragment);
                fragment.appendChild(childrenContainer);
            }
        }

        return fragment;
    }

    /**
     * 创建章节元素
     * @private
     */
    _createChapterElement(chapter, isSelected) {
        const div = document.createElement('div');
        div.className = `chapter-item level-${chapter.level}`;
        div.dataset.chapterId = chapter.id;

        // 状态图标
        let statusIcon = this.config.STATUS_ICONS.UNSELECTED;
        let statusClass = '';
        if (chapter.auto_selected) {
            statusIcon = this.config.STATUS_ICONS.AUTO_SELECTED;
            statusClass = 'auto-selected';
        } else if (chapter.skip_recommended) {
            statusIcon = this.config.STATUS_ICONS.SKIP_RECOMMENDED;
            statusClass = 'skip-recommended';
        }

        // 标签HTML
        const tagsHtml = this._generateTagsHtml(chapter.content_tags);

        div.innerHTML = `
            <div class="d-flex align-items-center chapter-row ${statusClass}">
                <input type="checkbox"
                       class="form-check-input me-2 chapter-checkbox"
                       id="ch-${chapter.id}"
                       ${isSelected ? 'checked' : ''}>
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
            if (this.onSelectionChange) {
                this.onSelectionChange(chapter.id, e.target.checked);
            }
        });

        const previewBtn = div.querySelector('.preview-btn');
        previewBtn.addEventListener('click', () => {
            if (this.onPreview) {
                this.onPreview(chapter);
            }
        });

        return div;
    }

    /**
     * 生成标签HTML
     * @private
     */
    _generateTagsHtml(tags) {
        if (!tags || tags.length === 0) return '';

        return tags.map(tag => {
            const colorClass = this.config.TAG_COLOR_MAP[tag] || 'secondary';
            return `<span class="badge bg-${colorClass} ms-1">${tag}</span>`;
        }).join('');
    }

    /**
     * 更新按钮状态
     * @private
     */
    _updateButtonStates(selectedCount) {
        const exportBtn = document.getElementById('exportSelectedChaptersBtn');
        const saveBtn = document.getElementById('saveAsResponseFileBtn');

        if (exportBtn) exportBtn.disabled = selectedCount === 0;
        if (saveBtn) saveBtn.disabled = selectedCount === 0;
    }

    /**
     * 批量更新复选框状态
     * @param {Map<string, boolean>} updates - chapterId -> checked
     */
    batchUpdateCheckboxes(updates) {
        requestAnimationFrame(() => {
            updates.forEach((checked, chapterId) => {
                const checkbox = document.getElementById(`ch-${chapterId}`);
                if (checkbox) {
                    checkbox.checked = checked;
                }
            });
        });
    }
}

// ========================================================================
// 4. 协调器 - ChapterSelectionController
// 职责：组合各服务，协调业务流程
// ========================================================================

/**
 * 章节选择控制器（协调器）
 * 组合API服务、状态管理和UI渲染，提供统一的业务接口
 *
 * @class ChapterSelectionController
 */
class ChapterSelectionController {
    constructor(config) {
        this.config = config || window.CHAPTER_CONFIG;

        // 组合各服务
        this.apiService = new ChapterAPIService();
        this.stateManager = new ChapterStateManager();
        this.renderer = new ChapterTreeRenderer(this.config);

        // 防重复提交标志
        this._isSubmitting = false;
        this._isExporting = false;
        this._isSaving = false;

        // 搜索防抖
        this._searchTimeout = null;

        // 绑定回调
        this.renderer.onSelectionChange = (chapterId, selected) => {
            this.handleSelectionChange(chapterId, selected);
        };
        this.renderer.onPreview = (chapter) => {
            this.handlePreview(chapter);
        };
    }

    /**
     * 初始化（设置容器）
     */
    initialize(containerId = 'chapterTreeContainer') {
        this.renderer.setContainer(containerId);
    }

    /**
     * 解析文档结构
     */
    async parseStructure(fileInput, config) {
        // 验证输入
        const hasNewFile = fileInput.files && fileInput.files[0];
        const historicalFile = typeof window.projectDataBridge !== 'undefined'
            ? window.projectDataBridge.getFileInfo('originalTender')
            : null;

        if (!hasNewFile && !historicalFile) {
            throw new Error('请先选择文件');
        }

        if (!config.companyId) {
            throw new Error('请先选择应答公司');
        }

        // 显示loading
        this.renderer.showLoadingSkeleton();

        try {
            // 构建FormData
            const formData = new FormData();
            if (hasNewFile) {
                formData.append('file', fileInput.files[0]);
            } else {
                formData.append('file_path', historicalFile.filePath);
            }
            formData.append('company_id', config.companyId);
            if (config.projectId) {
                formData.append('project_id', config.projectId);
            }

            // 调用API
            const result = await this.apiService.parseStructure(formData);

            if (result.success) {
                // 更新状态
                this.stateManager.setChapters(result.chapters, result.task_id);

                // 保存到全局（兼容性）
                window.parsedChapters = result.chapters;
                window.currentTaskId = result.task_id;

                // 渲染UI
                this.renderer.hideLoadingSkeleton();
                this.renderer.renderTree(
                    this.stateManager.chaptersTree,
                    this.stateManager.selectedIds
                );
                this.updateStatistics();

                return {
                    taskId: result.task_id,
                    projectId: result.project_id,
                    statistics: result.statistics
                };
            } else {
                throw new Error(result.error || '解析失败');
            }
        } catch (error) {
            this.renderer.hideLoadingSkeleton();
            throw error;
        }
    }

    /**
     * 处理选择变更
     */
    handleSelectionChange(chapterId, selected) {
        this.stateManager.toggleSelection(chapterId, selected);
        this.updateStatistics();
    }

    /**
     * 更新统计信息
     */
    updateStatistics() {
        const stats = this.stateManager.getStatistics();
        this.renderer.updateStatistics(stats);
    }

    /**
     * 全选
     */
    selectAll() {
        const count = this.stateManager.selectAll();

        // 批量更新UI
        const updates = new Map();
        this.stateManager.chaptersFlat.forEach(ch => {
            if (!ch.skip_recommended) {
                updates.set(ch.id, true);
            }
        });
        this.renderer.batchUpdateCheckboxes(updates);

        this.updateStatistics();
        return count;
    }

    /**
     * 取消全选
     */
    unselectAll() {
        const previousCount = this.stateManager.unselectAll();

        // 批量更新UI
        const updates = new Map();
        this.stateManager.chaptersFlat.forEach(ch => {
            updates.set(ch.id, false);
        });
        this.renderer.batchUpdateCheckboxes(updates);

        this.updateStatistics();
        return previousCount;
    }

    /**
     * 按关键词选择
     */
    selectByKeyword(keyword) {
        const count = this.stateManager.selectByKeyword(keyword);

        // 更新UI
        const updates = new Map();
        this.stateManager.chaptersFlat.forEach(ch => {
            if (ch.title.includes(keyword) && !ch.skip_recommended) {
                updates.set(ch.id, true);
            }
        });
        this.renderer.batchUpdateCheckboxes(updates);

        this.updateStatistics();
        return count;
    }

    /**
     * 排除关键词
     */
    excludeByKeyword(keyword) {
        const count = this.stateManager.excludeByKeyword(keyword);

        // 更新UI
        const updates = new Map();
        this.stateManager.chaptersFlat.forEach(ch => {
            if (ch.title.includes(keyword)) {
                updates.set(ch.id, false);
            }
        });
        this.renderer.batchUpdateCheckboxes(updates);

        this.updateStatistics();
        return count;
    }

    /**
     * 搜索（带防抖）
     */
    search(query) {
        clearTimeout(this._searchTimeout);

        this._searchTimeout = setTimeout(() => {
            const normalizedQuery = query.toLowerCase();

            document.querySelectorAll('.chapter-item').forEach(item => {
                const title = item.querySelector('.chapter-title').textContent.toLowerCase();
                item.style.display = title.includes(normalizedQuery) ? 'block' : 'none';
            });
        }, this.config.SEARCH_DEBOUNCE_DELAY);
    }

    /**
     * 确认选择并提交
     */
    async confirmSelection() {
        if (this._isSubmitting) return;
        if (this.stateManager.selectedIds.size === 0) {
            throw new Error('请至少选择一个章节');
        }

        this._isSubmitting = true;
        try {
            const result = await this.apiService.selectChapters(
                this.stateManager.taskId,
                this.stateManager.getSelectedIds()
            );

            if (result.success) {
                return {
                    hitlTaskId: result.hitl_task_id,
                    projectId: result.project_id
                };
            } else {
                throw new Error(result.error || '提交失败');
            }
        } finally {
            this._isSubmitting = false;
        }
    }

    /**
     * 导出选中章节
     */
    async exportChapters() {
        if (this._isExporting) return;
        if (this.stateManager.selectedIds.size === 0) {
            throw new Error('请先选择要导出的章节');
        }

        this._isExporting = true;
        try {
            const blob = await this.apiService.exportChapters(
                this.stateManager.taskId,
                this.stateManager.getSelectedIds()
            );

            // 触发下载
            this._downloadBlob(blob, '选中章节_应答模板.docx');
        } finally {
            this._isExporting = false;
        }
    }

    /**
     * 保存应答文件
     */
    async saveResponseFile() {
        if (this._isSaving) return;
        if (this.stateManager.selectedIds.size === 0) {
            throw new Error('请先选择要保存的章节');
        }

        this._isSaving = true;
        try {
            const result = await this.apiService.saveResponseFile(
                this.stateManager.taskId,
                this.stateManager.getSelectedIds()
            );

            return result;
        } finally {
            this._isSaving = false;
        }
    }

    /**
     * 加载历史章节
     */
    async loadHistoricalChapters(hitlTaskId) {
        this.renderer.showLoadingSkeleton();

        try {
            const { chapters, selectedIds } = await this.apiService.loadHistoricalChapters(hitlTaskId);

            // 构建树形结构
            const chaptersTree = this.stateManager.buildChapterTree(chapters);

            // 更新状态
            this.stateManager.setChapters(chaptersTree, hitlTaskId);
            this.stateManager.selectedIds = new Set(selectedIds);

            // 保存到全局
            window.parsedChapters = chaptersTree;
            window.currentTaskId = hitlTaskId;

            // 渲染
            this.renderer.hideLoadingSkeleton();
            this.renderer.renderTree(chaptersTree, this.stateManager.selectedIds);
            this.updateStatistics();
        } catch (error) {
            this.renderer.hideLoadingSkeleton();
            throw error;
        }
    }

    /**
     * 处理预览
     */
    handlePreview(chapter) {
        if (typeof showChapterPreviewModal === 'function') {
            showChapterPreviewModal(chapter.id);
        } else {
            console.error('[Controller] showChapterPreviewModal未定义');
            throw new Error('预览功能未加载，请刷新页面重试');
        }
    }

    /**
     * 下载Blob文件
     * @private
     */
    _downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
}

// ========================================================================
// 导出（供外部使用）
// ========================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ChapterAPIService,
        ChapterStateManager,
        ChapterTreeRenderer,
        ChapterSelectionController
    };
}
