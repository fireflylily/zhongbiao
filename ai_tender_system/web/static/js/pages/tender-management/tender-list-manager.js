/**
 * 标书管理列表页管理器
 * 负责项目列表的展示、搜索、筛选和跳转等功能
 */
class TenderListManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.searchKeyword = '';
        this.statusFilter = '';
        this.selectedProjectIds = new Set();
        this.projects = [];
        this.totalCount = 0;
    }

    /**
     * 初始化管理器
     */
    async initialize() {
        console.log('初始化标书管理列表...');

        // 绑定事件
        this.bindEvents();

        // 加载项目列表
        await this.loadProjects();
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 搜索框回车事件
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchProjects();
                }
            });
        }

        // 状态筛选变化
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            this.statusFilter = statusFilter.value;
        }
    }

    /**
     * 加载项目列表
     */
    async loadProjects() {
        try {
            // 显示加载状态
            this.showLoading();

            // 构建查询参数
            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize,
                search: this.searchKeyword,
                status: this.statusFilter
            });

            // 请求API
            const response = await fetch(`/api/tender-management/list?${params}`);
            const result = await response.json();

            if (result.success) {
                this.projects = result.data.projects;
                this.totalCount = result.data.total;

                // 渲染项目列表
                this.renderProjects();

                // 渲染分页
                this.renderPagination(result.data);
            } else {
                this.showError('加载项目列表失败: ' + result.error);
            }
        } catch (error) {
            console.error('加载项目失败:', error);
            this.showError('加载项目失败');
        }
    }

    /**
     * 渲染项目列表
     */
    renderProjects() {
        const tbody = document.getElementById('projectListBody');
        if (!tbody) return;

        if (this.projects.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center">
                        <div class="empty-state">
                            <i class="bi bi-inbox"></i>
                            <p>暂无项目数据</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.projects.map(project => {
            const isSelected = this.selectedProjectIds.has(project.project_id);

            return `
                <tr data-project-id="${project.project_id}">
                    <td>
                        <input type="checkbox" class="form-check-input project-checkbox"
                               value="${project.project_id}"
                               ${isSelected ? 'checked' : ''}
                               onchange="tenderListManager.toggleProjectSelection(${project.project_id})">
                    </td>
                    <td>
                        <a href="javascript:void(0)" onclick="tenderListManager.viewProjectDetail(${project.project_id})"
                           class="text-decoration-none fw-bold">
                            ${this.escapeHtml(project.project_name)}
                        </a>
                        ${project.project_number ? `<br><small class="text-muted">${project.project_number}</small>` : ''}
                    </td>
                    <td>${this.escapeHtml(project.company_name)}</td>
                    <td>${this.escapeHtml(project.authorized_person)}</td>
                    <td>${this.renderProgressCell(project.business_response)}</td>
                    <td>${this.renderProgressCell(project.tech_response)}</td>
                    <td>${this.renderProgressCell(project.tech_proposal)}</td>
                    <td>${this.renderProgressCell(project.fusion)}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-action"
                                    onclick="tenderListManager.viewProjectDetail(${project.project_id})"
                                    title="查看详情">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-outline-info btn-action"
                                    onclick="tenderListManager.enterProcessing(${project.project_id})"
                                    title="进入处理">
                                <i class="bi bi-gear"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-action"
                                    onclick="tenderListManager.deleteProject(${project.project_id})"
                                    title="删除">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    /**
     * 渲染进度单元格
     */
    renderProgressCell(progressInfo) {
        const status = progressInfo.status;
        const progress = progressInfo.progress;

        // 根据状态决定样式
        let statusClass = 'status-not-started';
        let progressBarClass = 'bg-secondary';

        if (status === '进行中') {
            statusClass = 'status-in-progress';
            progressBarClass = 'bg-warning';
        } else if (status === '已完成') {
            statusClass = 'status-completed';
            progressBarClass = 'bg-success';
        }

        return `
            <div>
                <div class="status-badge ${statusClass} mb-1">${status}</div>
                <div class="progress">
                    <div class="progress-bar ${progressBarClass}"
                         role="progressbar"
                         style="width: ${progress}%"
                         aria-valuenow="${progress}"
                         aria-valuemin="0"
                         aria-valuemax="100">
                        ${progress}%
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染分页
     */
    renderPagination(data) {
        const container = document.getElementById('paginationContainer');
        if (!container) return;

        const totalPages = data.total_pages || 1;
        const currentPage = data.page || 1;

        let html = '<nav><ul class="pagination">';

        // 上一页
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="javascript:void(0)"
                   onclick="tenderListManager.goToPage(${currentPage - 1})">
                    上一页
                </a>
            </li>
        `;

        // 页码
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                html += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="javascript:void(0)"
                           onclick="tenderListManager.goToPage(${i})">${i}</a>
                    </li>
                `;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                html += '<li class="page-item disabled"><a class="page-link">...</a></li>';
            }
        }

        // 下一页
        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="javascript:void(0)"
                   onclick="tenderListManager.goToPage(${currentPage + 1})">
                    下一页
                </a>
            </li>
        `;

        html += '</ul></nav>';
        container.innerHTML = html;
    }

    /**
     * 跳转到指定页
     */
    goToPage(page) {
        if (page < 1) return;
        this.currentPage = page;
        this.loadProjects();
    }

    /**
     * 搜索项目
     */
    searchProjects() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            this.searchKeyword = searchInput.value.trim();
        }
        this.currentPage = 1;
        this.loadProjects();
    }

    /**
     * 应用筛选
     */
    applyFilters() {
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            this.statusFilter = statusFilter.value;
        }
        this.currentPage = 1;
        this.loadProjects();
    }

    /**
     * 刷新列表
     */
    refreshList() {
        this.loadProjects();
    }

    /**
     * 创建新项目
     */
    createNewProject() {
        // 跳转到招标信息提取页面创建新项目
        window.location.href = '/tender_info_extraction.html';
    }

    /**
     * 查看项目详情
     */
    async viewProjectDetail(projectId) {
        try {
            // 获取项目统计信息
            const response = await fetch(`/api/tender-management/stats/${projectId}`);
            const result = await response.json();

            if (result.success) {
                // 可以显示详情模态框或跳转到详情页
                // 这里暂时直接跳转到处理页面
                this.enterProcessing(projectId);
            } else {
                this.showError('获取项目信息失败');
            }
        } catch (error) {
            console.error('获取项目详情失败:', error);
            this.showError('获取项目详情失败');
        }
    }

    /**
     * 进入标书处理页面
     */
    enterProcessing(projectId) {
        // 跳转到标书处理页面，并传递项目ID
        window.location.href = `/tender_processing.html?project_id=${projectId}`;
    }

    /**
     * 删除项目
     */
    async deleteProject(projectId) {
        if (!confirm('确定要删除这个项目吗？此操作不可恢复。')) {
            return;
        }

        try {
            // 这里可以调用删除API（需要后端实现）
            alert('删除功能尚未实现');

            // 刷新列表
            // await this.loadProjects();
        } catch (error) {
            console.error('删除项目失败:', error);
            this.showError('删除项目失败');
        }
    }

    /**
     * 切换项目选择
     */
    toggleProjectSelection(projectId) {
        if (this.selectedProjectIds.has(projectId)) {
            this.selectedProjectIds.delete(projectId);
        } else {
            this.selectedProjectIds.add(projectId);
        }
    }

    /**
     * 切换全选
     */
    toggleSelectAll(checkbox) {
        const checkboxes = document.querySelectorAll('.project-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = checkbox.checked;
            const projectId = parseInt(cb.value);
            if (checkbox.checked) {
                this.selectedProjectIds.add(projectId);
            } else {
                this.selectedProjectIds.delete(projectId);
            }
        });
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        const tbody = document.getElementById('projectListBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center">
                        <div class="loading-container">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                            <p class="mt-3 text-muted">正在加载项目列表...</p>
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * 显示错误信息
     */
    showError(message) {
        const tbody = document.getElementById('projectListBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center">
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle me-2"></i>
                            ${message}
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * 工具方法：转义HTML
     */
    escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// 创建全局实例
window.tenderListManager = new TenderListManager();