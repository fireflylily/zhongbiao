// 标书智能处理 - 步骤1：章节选择
// 功能：文档结构解析、章节树展示、人工选择

class ChapterSelectionManager {
    constructor() {
        this.currentTaskId = null;
        this.chaptersData = [];  // 章节数据（扁平化）
        this.selectedChapterIds = new Set();  // 已选中的章节ID
        this.statistics = {};

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
    }

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

                // 渲染章节树
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
            console.error('解析失败:', error);
            this.showNotification('解析失败: ' + error.message, 'error');
        } finally {
            parseBtn.disabled = false;
            parseBtn.innerHTML = originalText;
        }
    }

    flattenChapters(chapters, result = []) {
        for (const ch of chapters) {
            result.push(ch);
            if (ch.children && ch.children.length > 0) {
                this.flattenChapters(ch.children, result);
            }
        }
        return result;
    }

    renderChapterTree(chapters, container = null, level = 0) {
        if (!container) {
            container = document.getElementById('chapterTreeContainer');
            container.innerHTML = '';
        }

        for (const chapter of chapters) {
            const chapterDiv = this.createChapterElement(chapter, level);
            container.appendChild(chapterDiv);

            // 递归渲染子章节
            if (chapter.children && chapter.children.length > 0) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'chapter-children ms-3';
                childrenContainer.id = `children-${chapter.id}`;
                this.renderChapterTree(chapter.children, childrenContainer, level + 1);
                container.appendChild(childrenContainer);
            }
        }
    }

    createChapterElement(chapter, level) {
        const div = document.createElement('div');
        div.className = `chapter-item level-${chapter.level}`;
        div.dataset.chapterId = chapter.id;

        // 章节状态标记
        let statusIcon = '⚪';
        let statusClass = '';
        if (chapter.auto_selected) {
            statusIcon = '✅';
            statusClass = 'auto-selected';
            this.selectedChapterIds.add(chapter.id);
        } else if (chapter.skip_recommended) {
            statusIcon = '❌';
            statusClass = 'skip-recommended';
        }

        // 生成标签HTML
        let tagsHtml = '';
        if (chapter.content_tags && chapter.content_tags.length > 0) {
            const tagColorMap = {
                '评分办法': 'primary',
                '评分表': 'warning text-dark',
                '供应商资质': 'success',
                '文件格式': 'secondary',
                '技术需求': 'info'
            };

            tagsHtml = chapter.content_tags.map(tag => {
                const colorClass = tagColorMap[tag] || 'secondary';
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
            this.updateStatistics();
        });

        const previewBtn = div.querySelector('.preview-btn');
        previewBtn.addEventListener('click', () => this.showPreview(chapter));

        return div;
    }

    showPreview(chapter) {
        const previewContainer = document.getElementById('chapterPreview');

        previewContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">${chapter.title}</h6>
                </div>
                <div class="card-body">
                    <p><strong>层级：</strong> ${chapter.level}级标题</p>
                    <p><strong>字数：</strong> ${chapter.word_count} 字</p>
                    <p><strong>段落范围：</strong> ${chapter.para_start_idx} - ${chapter.para_end_idx || '文档末尾'}</p>
                    <hr>
                    <h6>内容预览：</h6>
                    <pre class="preview-text">${chapter.preview_text || '(无内容)'}</pre>
                </div>
            </div>
        `;
    }

    updateStatistics() {
        const selectedCount = this.selectedChapterIds.size;
        const selectedWords = this.chaptersData
            .filter(ch => this.selectedChapterIds.has(ch.id))
            .reduce((sum, ch) => sum + ch.word_count, 0);

        document.getElementById('statTotalChapters').textContent = this.chaptersData.length;
        document.getElementById('statSelectedChapters').textContent = selectedCount;
        document.getElementById('statSelectedWords').textContent = selectedWords;

        // 更新导出按钮状态
        const exportBtn = document.getElementById('exportSelectedChaptersBtn');
        if (exportBtn) {
            exportBtn.disabled = this.selectedChapterIds.size === 0;
        }

        // 更新另存为应答文件按钮状态
        const saveBtn = document.getElementById('saveAsResponseFileBtn');
        if (saveBtn) {
            saveBtn.disabled = this.selectedChapterIds.size === 0;
        }
    }

    selectAll() {
        this.chaptersData.forEach(ch => {
            if (!ch.skip_recommended) {
                this.selectedChapterIds.add(ch.id);
                const checkbox = document.getElementById(`ch-${ch.id}`);
                if (checkbox) checkbox.checked = true;
            }
        });
        this.updateStatistics();
    }

    unselectAll() {
        this.selectedChapterIds.clear();
        document.querySelectorAll('.chapter-checkbox').forEach(cb => cb.checked = false);
        this.updateStatistics();
    }

    selectByKeyword(keyword) {
        this.chaptersData.forEach(ch => {
            if (ch.title.includes(keyword) && !ch.skip_recommended) {
                this.selectedChapterIds.add(ch.id);
                const checkbox = document.getElementById(`ch-${ch.id}`);
                if (checkbox) checkbox.checked = true;
            }
        });
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
        this.updateStatistics();
        this.showNotification(`已排除包含"${keyword}"的章节`, 'info');
    }

    handleSearch(query) {
        const normalizedQuery = query.toLowerCase();

        document.querySelectorAll('.chapter-item').forEach(item => {
            const title = item.querySelector('.chapter-title').textContent.toLowerCase();
            if (title.includes(normalizedQuery)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async confirmSelection() {
        console.log('[Step1] confirmSelection 开始执行');

        if (this.selectedChapterIds.size === 0) {
            this.showNotification('请至少选择一个章节', 'warning');
            return;
        }

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
            console.error('[Step1] 确认选择失败:', error);
            console.error('[Step1] 错误详情:', error.stack);
            this.showNotification('提交失败: ' + error.message, 'error');
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    }

    /**
     * 导出选中的章节为Word模板
     */
    async exportSelectedChapters() {
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
            console.error('导出失败:', error);
            this.showNotification(`导出失败: ${error.message}`, 'error');
        }
    }

    /**
     * 另存为应答文件
     */
    async saveAsResponseFile() {
        if (this.selectedChapterIds.size === 0) {
            this.showNotification('请先选择要保存的章节', 'warning');
            return;
        }

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
            console.error('保存失败:', error);
            this.showNotification(`保存失败: ${error.message}`, 'error');
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

    showNotification(message, type = 'info') {
        // 简单的通知实现（可以后续用 Bootstrap Toast 替换）
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), 3000);
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
