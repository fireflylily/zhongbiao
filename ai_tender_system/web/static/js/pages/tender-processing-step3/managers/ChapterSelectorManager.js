/**
 * 章节选择管理器
 * 统一管理章节选择逻辑，支持多种文件类型
 *
 * 依赖:
 * - core/api-client.js (API调用)
 * - core/notification.js (提示信息)
 * - tender-processing-step3/api/tender-api-extension.js (标书API扩展)
 *
 * 用法:
 * const manager = new ChapterSelectorManager('response', {
 *     prefix: 'inline',
 *     contentId: 'responseFileContent',
 *     selectionAreaId: 'inlineChapterSelectionArea'
 * });
 * await manager.showChapterSelection();
 */

class ChapterSelectorManager {
    /**
     * 构造函数
     * @param {string} type - 文件类型 ('response', 'technical', 'point_to_point')
     * @param {Object} config - 配置对象
     */
    constructor(type, config = {}) {
        this.type = type;
        this.config = {
            prefix: config.prefix || type,
            contentId: config.contentId,
            selectionAreaId: config.selectionAreaId,
            confirmBtnId: config.confirmBtnId,
            fileTypeName: config.fileTypeName || '文件',
            apiSave: config.apiSave,
            apiInfo: config.apiInfo,
            ...config
        };

        // 状态管理
        this.chaptersData = [];
        this.selectedIds = new Set();
        this.taskId = null;

        console.log(`[ChapterSelectorManager] 初始化管理器，类型: ${type}`);
    }

    /**
     * 显示章节选择区域
     * @param {string} taskId - 任务ID（可选，默认从全局状态获取）
     * @param {Array} chaptersData - 章节数据（可选，默认从API加载）
     */
    async showChapterSelection(taskId = null, chaptersData = null) {
        console.log(`[ChapterSelectorManager] 显示${this.config.fileTypeName}章节选择`);

        // 确定任务ID
        this.taskId = taskId || this._getTaskId();
        if (!this.taskId) {
            window.notifications.error('未找到HITL任务，请先在"标书智能处理"页面解析文档');
            return;
        }

        // 加载章节数据
        try {
            if (chaptersData && chaptersData.length > 0) {
                console.log('[ChapterSelectorManager] 使用传入的章节数据');
                this.chaptersData = chaptersData;
            } else {
                console.log('[ChapterSelectorManager] 从API加载章节数据');
                this.chaptersData = await this._loadChaptersFromAPI();

                if (!this.chaptersData || this.chaptersData.length === 0) {
                    window.notifications.error('未找到章节数据，请先在步骤1解析文档');
                    return;
                }
            }
        } catch (error) {
            window.notifications.error(error.message || '加载章节数据失败');
            return;
        }

        // 重置选中状态
        this.selectedIds.clear();

        // 渲染章节树
        this.renderChapterTree();

        // 更新统计信息
        this.updateStatistics();

        // 切换显示区域
        this._toggleDisplayArea(true);

        console.log(`[ChapterSelectorManager] ${this.config.fileTypeName}章节选择区域已显示`);
    }

    /**
     * 隐藏章节选择区域
     */
    hideChapterSelection() {
        this._toggleDisplayArea(false);
        console.log(`[ChapterSelectorManager] ${this.config.fileTypeName}章节选择区域已隐藏`);
    }

    /**
     * 渲染章节树
     */
    renderChapterTree() {
        const containerId = `${this.config.prefix}ChapterTreeContainer`;
        const container = document.getElementById(containerId);

        if (!container) {
            console.error(`[ChapterSelectorManager] 找不到容器: ${containerId}`);
            return;
        }

        console.log(`[ChapterSelectorManager] 渲染章节树，章节数: ${this.chaptersData.length}`);

        // 清空容器
        container.innerHTML = '';

        // 渲染所有章节
        this.chaptersData.forEach(chapter => {
            const chapterElement = this._createChapterElement(chapter);
            container.appendChild(chapterElement);
        });

        console.log('[ChapterSelectorManager] 章节树渲染完成');
    }

    /**
     * 创建章节元素
     * @param {Object} chapter - 章节数据
     * @returns {HTMLElement}
     */
    _createChapterElement(chapter) {
        const div = document.createElement('div');
        div.className = `chapter-item level-${chapter.level}`;
        div.dataset.chapterId = chapter.id;
        div.style.marginLeft = `${(chapter.level - 1) * 20}px`;

        // 状态标记
        let statusIcon = '⚪';
        let statusClass = '';
        if (chapter.auto_selected) {
            statusIcon = '✅';
            statusClass = 'auto-selected';
        } else if (chapter.skip_recommended) {
            statusIcon = '❌';
            statusClass = 'skip-recommended';
        }

        // 标签HTML
        const tagsHtml = this._generateTagsHtml(chapter.content_tags);

        // 复选框ID
        const checkboxId = `${this.config.prefix}-ch-${chapter.id}`;

        // 生成HTML
        div.innerHTML = `
            <div class="d-flex align-items-center chapter-row ${statusClass} py-2">
                <input type="checkbox"
                       class="form-check-input me-2 ${this.config.prefix}-chapter-checkbox"
                       id="${checkboxId}"
                       data-chapter-id="${chapter.id}">
                <span class="chapter-status me-2">${statusIcon}</span>
                <label class="chapter-title flex-grow-1" for="${checkboxId}" style="cursor: pointer;">
                    ${chapter.title}
                    <small class="text-muted">(${chapter.word_count}字)</small>
                    ${tagsHtml}
                </label>
                <button class="btn btn-sm btn-outline-info ms-2 preview-chapter-btn"
                        data-chapter-id="${chapter.id}"
                        title="预览章节内容">
                    <i class="bi bi-eye"></i>
                </button>
            </div>
        `;

        // 绑定复选框事件
        const checkbox = div.querySelector(`.${this.config.prefix}-chapter-checkbox`);
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedIds.add(chapter.id);
            } else {
                this.selectedIds.delete(chapter.id);
            }
            this.updateStatistics();
        });

        // 绑定预览按钮事件
        const previewBtn = div.querySelector('.preview-chapter-btn');
        previewBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this._previewChapter(chapter.id);
        });

        return div;
    }

    /**
     * 生成标签HTML
     * @param {Array} tags - 标签数组
     * @returns {string}
     */
    _generateTagsHtml(tags) {
        if (!tags || tags.length === 0) return '';

        const tagColorMap = {
            '评分办法': 'primary',
            '评分表': 'warning text-dark',
            '供应商资质': 'success',
            '文件格式': 'secondary',
            '技术需求': 'info'
        };

        return tags.map(tag => {
            const colorClass = tagColorMap[tag] || 'secondary';
            return `<span class="badge bg-${colorClass} ms-1">${tag}</span>`;
        }).join('');
    }

    /**
     * 更新统计信息
     */
    updateStatistics() {
        const totalChapters = this.chaptersData.length;
        const selectedCount = this.selectedIds.size;

        // 计算选中章节的总字数
        const selectedWords = this.chaptersData
            .filter(ch => this.selectedIds.has(ch.id))
            .reduce((sum, ch) => sum + ch.word_count, 0);

        // 更新DOM元素
        const prefix = this.config.prefix;
        this._updateElement(`${prefix}StatTotalChapters`, totalChapters);
        this._updateElement(`${prefix}StatSelectedChapters`, selectedCount);
        this._updateElement(`${prefix}StatSelectedWords`, selectedWords);

        console.log(`[ChapterSelectorManager] 统计更新 - 总数:${totalChapters} 选中:${selectedCount} 字数:${selectedWords}`);
    }

    /**
     * 全选
     */
    selectAll() {
        this.chaptersData.forEach(ch => {
            if (!ch.skip_recommended) {
                this.selectedIds.add(ch.id);
                const checkbox = document.getElementById(`${this.config.prefix}-ch-${ch.id}`);
                if (checkbox) checkbox.checked = true;
            }
        });
        this.updateStatistics();
        console.log('[ChapterSelectorManager] 已全选');
    }

    /**
     * 全不选
     */
    unselectAll() {
        this.selectedIds.clear();
        document.querySelectorAll(`.${this.config.prefix}-chapter-checkbox`)
            .forEach(cb => cb.checked = false);
        this.updateStatistics();
        console.log('[ChapterSelectorManager] 已全不选');
    }

    /**
     * 按关键词选择
     * @param {string} keyword - 关键词
     */
    selectByKeyword(keyword) {
        let count = 0;
        this.chaptersData.forEach(ch => {
            if (ch.title.includes(keyword) && !ch.skip_recommended) {
                this.selectedIds.add(ch.id);
                const checkbox = document.getElementById(`${this.config.prefix}-ch-${ch.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    count++;
                }
            }
        });
        this.updateStatistics();
        window.notifications.success(`已选中包含"${keyword}"的 ${count} 个章节`);
    }

    /**
     * 排除关键词
     * @param {string} keyword - 关键词
     */
    excludeByKeyword(keyword) {
        let count = 0;
        this.chaptersData.forEach(ch => {
            if (ch.title.includes(keyword)) {
                this.selectedIds.delete(ch.id);
                const checkbox = document.getElementById(`${this.config.prefix}-ch-${ch.id}`);
                if (checkbox) {
                    checkbox.checked = false;
                    count++;
                }
            }
        });
        this.updateStatistics();
        window.notifications.success(`已排除包含"${keyword}"的 ${count} 个章节`);
    }

    /**
     * 确认保存选中章节
     */
    async confirmSave() {
        console.log(`[ChapterSelectorManager] 开始保存${this.config.fileTypeName}`);

        // 验证
        if (this.selectedIds.size === 0) {
            window.notifications.warning('请至少选择一个章节');
            return;
        }

        if (!this.taskId) {
            window.notifications.error('未找到任务ID');
            return;
        }

        // 获取确认按钮
        const btn = document.getElementById(this.config.confirmBtnId);
        if (!btn) {
            console.error(`找不到确认按钮: ${this.config.confirmBtnId}`);
            return;
        }

        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';

        try {
            const chapterIds = Array.from(this.selectedIds);
            console.log(`[ChapterSelectorManager] 保存章节数: ${chapterIds.length}`);

            // 调用API保存
            const response = await fetch(`${this.config.apiSave}/${this.taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chapter_ids: chapterIds })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '保存失败');
            }

            window.notifications.success(
                `✅ ${this.config.fileTypeName}已成功保存！文件名: ${result.filename}`
            );

            // 隐藏章节选择区域
            this.hideChapterSelection();

            // 触发文件信息刷新事件
            window.dispatchEvent(new CustomEvent('fileInfoUpdated', {
                detail: { type: this.type, taskId: this.taskId }
            }));

        } catch (error) {
            console.error(`[ChapterSelectorManager] 保存失败:`, error);
            window.notifications.error(`保存失败: ${error.message}`);
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    /**
     * 获取选中的章节ID数组
     * @returns {Array}
     */
    getSelectedIds() {
        return Array.from(this.selectedIds);
    }

    /**
     * 设置选中的章节ID
     * @param {Array} ids - 章节ID数组
     */
    setSelectedIds(ids) {
        this.selectedIds = new Set(ids);

        // 更新UI
        this.chaptersData.forEach(ch => {
            const checkbox = document.getElementById(`${this.config.prefix}-ch-${ch.id}`);
            if (checkbox) {
                checkbox.checked = this.selectedIds.has(ch.id);
            }
        });

        this.updateStatistics();
    }

    // ============================================
    // 私有方法
    // ============================================

    /**
     * 获取任务ID
     * @returns {string|null}
     * @private
     */
    _getTaskId() {
        // 优先从全局状态获取
        if (window.globalState) {
            const taskId = window.globalState.getHitlTaskId();
            if (taskId) {
                console.log('[ChapterSelectorManager] 从全局状态获取任务ID:', taskId);
                return taskId;
            }
        }

        // 尝试从当前页面上下文获取
        if (typeof currentTaskId !== 'undefined' && currentTaskId) {
            console.log('[ChapterSelectorManager] 从当前上下文获取任务ID:', currentTaskId);
            return currentTaskId;
        }

        console.warn('[ChapterSelectorManager] 未找到任务ID');
        return null;
    }

    /**
     * 从API加载章节数据
     * @returns {Promise<Array>}
     * @private
     */
    async _loadChaptersFromAPI() {
        console.log('[ChapterSelectorManager] 从API加载章节数据');

        if (!window.apiClient || !window.apiClient.tenderProcessing) {
            throw new Error('API客户端未加载，请确保已加载 tender-api-extension.js');
        }

        try {
            const data = await window.apiClient.tenderProcessing.loadChapters(this.taskId);
            console.log('[ChapterSelectorManager] 成功加载', data.chapters?.length || 0, '个章节');
            return data.chapters || [];
        } catch (error) {
            console.error('[ChapterSelectorManager] 加载章节失败:', error);
            throw new Error('加载章节数据失败: ' + error.message);
        }
    }

    /**
     * 切换显示区域
     * @param {boolean} showSelection - true=显示章节选择, false=显示文件内容
     * @private
     */
    _toggleDisplayArea(showSelection) {
        const fileContent = document.getElementById(this.config.contentId);
        const selectionArea = document.getElementById(this.config.selectionAreaId);

        if (fileContent) {
            fileContent.style.display = showSelection ? 'none' : 'block';
        }
        if (selectionArea) {
            selectionArea.style.display = showSelection ? 'block' : 'none';
        }
    }

    /**
     * 更新DOM元素内容
     * @param {string} elementId - 元素ID
     * @param {any} value - 值
     * @private
     */
    _updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * 预览章节
     * @param {number} chapterId - 章节ID
     * @private
     */
    _previewChapter(chapterId) {
        // 触发预览事件，由外部处理
        window.dispatchEvent(new CustomEvent('chapterPreviewRequested', {
            detail: { chapterId, type: this.type }
        }));

        console.log(`[ChapterSelectorManager] 触发章节预览: ${chapterId}`);
    }
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChapterSelectorManager;
}
