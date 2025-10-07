// 标书智能处理 - 步骤2：章节要求预览
// 功能：查看章节及其要求统计、取消不需要的章节

class ChapterReviewManager {
    constructor(taskId) {
        this.taskId = taskId;
        this.chapters = [];
        this.selectedChapterIds = new Set();

        this.initializeEventListeners();
        this.loadChapterRequirements();
    }

    initializeEventListeners() {
        // 确认继续按钮
        document.getElementById('confirmStep2Btn')?.addEventListener('click', () => this.confirmAndProceed());
    }

    async loadChapterRequirements() {
        try {
            const response = await fetch(`/api/tender-processing/chapter-requirements/${this.taskId}`);
            const result = await response.json();

            if (result.success) {
                this.chapters = result.chapters;

                // 初始化选中状态
                this.selectedChapterIds = new Set(
                    this.chapters.filter(ch => ch.is_selected).map(ch => ch.chapter_id)
                );

                this.renderChapters();
                this.updateStatistics(result.summary);
            } else {
                throw new Error(result.error || '加载失败');
            }
        } catch (error) {
            console.error('加载章节要求失败:', error);
            this.showNotification('加载失败: ' + error.message, 'error');
        }
    }

    renderChapters() {
        const container = document.getElementById('chapterRequirementsContainer');

        if (this.chapters.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                    <p class="mt-3">没有章节数据</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.chapters.map(chapter => this.createChapterCard(chapter)).join('');

        // 绑定复选框事件
        container.querySelectorAll('.chapter-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const chapterId = parseInt(e.target.dataset.chapterId);
                if (e.target.checked) {
                    this.selectedChapterIds.add(chapterId);
                } else {
                    this.selectedChapterIds.delete(chapterId);
                }
                this.updateStatistics();
            });
        });
    }

    createChapterCard(chapter) {
        const stats = chapter.requirement_stats;
        const isSelected = this.selectedChapterIds.has(chapter.chapter_id);
        const indent = (chapter.level - 1) * 20;  // 根据层级缩进

        return `
            <div class="card mb-2 shadow-sm chapter-card" style="margin-left: ${indent}px;">
                <div class="card-body py-3">
                    <div class="d-flex align-items-start">
                        <input type="checkbox"
                               class="form-check-input me-3 chapter-checkbox"
                               data-chapter-id="${chapter.chapter_id}"
                               ${isSelected ? 'checked' : ''}>

                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    <h6 class="mb-0">
                                        <span class="badge bg-light text-dark me-2">L${chapter.level}</span>
                                        ${chapter.title}
                                    </h6>
                                    <small class="text-muted">
                                        <i class="bi bi-file-text"></i> ${chapter.word_count || 0} 字
                                    </small>
                                </div>
                            </div>

                            <!-- 要求数量统计 -->
                            <div class="requirement-stats d-flex gap-3 mt-2">
                                <div>
                                    <span class="badge bg-primary">总计: ${stats.total}</span>
                                </div>
                                ${stats.mandatory > 0 ? `
                                    <div>
                                        <span class="badge bg-danger">强制性: ${stats.mandatory}</span>
                                    </div>
                                ` : ''}
                                ${stats.scoring > 0 ? `
                                    <div>
                                        <span class="badge bg-warning">加分项: ${stats.scoring}</span>
                                    </div>
                                ` : ''}
                                ${stats.optional > 0 ? `
                                    <div>
                                        <span class="badge bg-info">可选: ${stats.optional}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateStatistics(summaryData) {
        // 如果提供了汇总数据，直接使用
        if (summaryData) {
            document.getElementById('statTotalChapters').textContent = summaryData.total_chapters || 0;
            document.getElementById('statSelectedChapters').textContent = summaryData.selected_chapters || 0;
            document.getElementById('statTotalRequirementsStep2').textContent = summaryData.total_requirements || 0;
        } else {
            // 否则重新计算选中数量
            const selectedCount = this.selectedChapterIds.size;
            document.getElementById('statSelectedChapters').textContent = selectedCount;
        }
    }

    async confirmAndProceed() {
        const confirmBtn = document.getElementById('confirmStep2Btn');
        const originalText = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>处理中...';

        try {
            // 找出被取消选中的章节
            const allChapterIds = this.chapters.map(ch => ch.chapter_id);
            const deselectedIds = allChapterIds.filter(id => !this.selectedChapterIds.has(id));
            const selectedIds = Array.from(this.selectedChapterIds);

            // 如果章节选择有变化，更新数据库
            if (deselectedIds.length > 0 || selectedIds.length < allChapterIds.length) {
                const response = await fetch('/api/tender-processing/update-chapter-selection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_id: this.taskId,
                        chapter_ids: selectedIds,
                        deselected_chapter_ids: deselectedIds
                    })
                });

                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || '更新失败');
                }
            }

            this.showNotification('步骤2已完成！', 'success');

            // 触发步骤3
            setTimeout(() => {
                if (typeof proceedToStep3 === 'function') {
                    proceedToStep3(this.taskId);
                }
            }, 1000);

        } catch (error) {
            console.error('确认失败:', error);
            this.showNotification('操作失败: ' + error.message, 'error');
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    }

    showNotification(message, type = 'info') {
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

// 全局变量
let chapterReviewManager;

// 从步骤1进入步骤2的函数
function proceedToStep2(taskId) {
    console.log('进入步骤2，任务ID:', taskId);

    // 隐藏步骤1
    document.getElementById('chapterSelectionSection').style.display = 'none';

    // 显示步骤2
    document.getElementById('step2Section').style.display = 'block';

    // 更新步骤指示器
    document.getElementById('stepIndicator1').classList.remove('active');
    document.getElementById('stepIndicator1').classList.add('completed');
    document.getElementById('stepIndicator2').classList.add('active');

    // 初始化步骤2管理器
    chapterReviewManager = new ChapterReviewManager(taskId);
}
