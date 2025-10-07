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
    }

    async handleParseStructure() {
        const fileInput = document.getElementById('tenderDocFile');
        const projectId = document.getElementById('projectId').value;

        if (!fileInput.files || !fileInput.files[0]) {
            this.showNotification('请先选择文件', 'warning');
            return;
        }

        if (!projectId) {
            this.showNotification('请输入项目ID', 'warning');
            return;
        }

        const parseBtn = document.getElementById('parseStructureBtn');
        const originalText = parseBtn.innerHTML;
        parseBtn.disabled = true;
        parseBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>解析中...';

        try {
            // 构建 FormData
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('project_id', projectId);

            // 调用解析API
            const response = await fetch('/api/tender-processing/parse-structure', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentTaskId = result.task_id;
                this.statistics = result.statistics;

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
        document.getElementById('statEstCost').textContent = `$${((selectedWords / 1000) * 0.002).toFixed(4)}`;

        // 更新导出按钮状态
        const exportBtn = document.getElementById('exportSelectedChaptersBtn');
        if (exportBtn) {
            exportBtn.disabled = this.selectedChapterIds.size === 0;
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
        if (this.selectedChapterIds.size === 0) {
            this.showNotification('请至少选择一个章节', 'warning');
            return;
        }

        const confirmBtn = document.getElementById('confirmSelectionBtn');
        const originalText = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>提交中...';

        try {
            const response = await fetch('/api/tender-processing/select-chapters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: this.currentTaskId,
                    selected_chapter_ids: Array.from(this.selectedChapterIds)
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('章节选择已确认！', 'success');

                // 触发步骤2（可以在这里调用步骤2的初始化）
                // 暂时显示成功消息
                document.getElementById('step1CompleteMessage').style.display = 'block';
                document.getElementById('step1CompleteMessage').innerHTML = `
                    <div class="alert alert-success">
                        <h5>✅ 步骤1完成</h5>
                        <p>已选择 ${result.selected_count} 个章节，共 ${result.selected_words} 字</p>
                        <p>预估处理成本：$${result.estimated_cost.toFixed(4)}</p>
                        <button class="btn btn-primary" onclick="proceedToStep2('${this.currentTaskId}')">
                            下一步：AI筛选
                        </button>
                    </div>
                `;
            } else {
                throw new Error(result.error || '提交失败');
            }

        } catch (error) {
            console.error('确认选择失败:', error);
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

// 初始化
let chapterSelectionManager;
document.addEventListener('DOMContentLoaded', () => {
    chapterSelectionManager = new ChapterSelectionManager();
});

// 进入步骤2的函数（占位）
function proceedToStep2(taskId) {
    alert(`准备进入步骤2，任务ID: ${taskId}`);
    // TODO: 实现步骤2的逻辑
}
