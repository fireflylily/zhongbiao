/**
 * 项目总览管理器
 * 负责项目列表的展示、搜索、筛选和跳转等功能
 * 适配Tab模式，作为首页的一个嵌入Tab
 */
class ProjectOverviewManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.searchKeyword = '';
        this.statusFilter = '';
        this.selectedProjectIds = new Set();
        this.projects = [];
        this.totalCount = 0;
        this.initialized = false;
    }

    /**
     * 初始化管理器
     */
    async initialize() {
        // 防止重复初始化
        if (this.initialized) {
            console.log('[ProjectOverviewManager] 已经初始化，跳过重复初始化');
            return;
        }

        console.log('[ProjectOverviewManager] 初始化项目总览...');

        // 绑定事件
        this.bindEvents();

        // 监听Tab切换事件，延迟加载数据
        const projectOverviewTab = document.getElementById('project-overview-nav');
        if (projectOverviewTab) {
            projectOverviewTab.addEventListener('shown.bs.tab', () => {
                console.log('[ProjectOverviewManager] Tab被激活，加载项目列表');
                this.loadProjects();
            });
        }

        this.initialized = true;
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 搜索框回车事件
        const searchInput = document.getElementById('projectSearchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchProjects();
                }
            });
        }

        // 状态筛选变化
        const statusFilter = document.getElementById('projectStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                this.applyFilters();
            });
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
            console.error('[ProjectOverviewManager] 加载项目失败:', error);
            this.showError('加载项目失败');
        }
    }

    /**
     * 渲染项目列表
     */
    renderProjects() {
        const tbody = document.getElementById('projectOverviewListBody');
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
                    <td class="ps-3">
                        <input type="checkbox" class="form-check-input project-checkbox"
                               value="${project.project_id}"
                               ${isSelected ? 'checked' : ''}
                               onchange="projectOverviewManager.toggleProjectSelection(${project.project_id})">
                    </td>
                    <td>
                        <a href="javascript:void(0)" onclick="projectOverviewManager.enterProcessing(${project.project_id})"
                           class="text-decoration-none fw-semibold text-primary">
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
                            <button class="btn btn-sm btn-outline-primary btn-action"
                                    onclick="projectOverviewManager.enterProcessing(${project.project_id})"
                                    title="进入处理">
                                <i class="bi bi-gear"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger btn-action"
                                    onclick="projectOverviewManager.deleteProject(${project.project_id})"
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
     * 渲染进度单元格 - 简化版本，只显示完成/未完成状态，已完成时显示预览按钮
     */
    renderProgressCell(progressInfo) {
        const status = progressInfo.status;

        // 判断是否已完成
        const isCompleted = status === '已完成';

        // 根据完成状态决定样式和文本
        const statusClass = isCompleted ? 'status-completed' : 'status-not-started';
        const statusText = isCompleted ? '已完成' : '未完成';
        const badgeColor = isCompleted ? 'bg-success' : 'bg-secondary';

        // 如果已完成且有文件路径，显示预览按钮
        const hasFile = isCompleted && progressInfo.file_path;

        // 从文件路径中提取文件名
        let fileName = '';
        if (hasFile && progressInfo.file_path) {
            const pathParts = progressInfo.file_path.split('/');
            fileName = pathParts[pathParts.length - 1];
        }

        return `
            <div class="text-center">
                <span class="badge ${badgeColor} ${statusClass}">${statusText}</span>
                ${hasFile ? `
                    <br>
                    <button class="btn btn-sm btn-outline-primary mt-1"
                            onclick="projectOverviewManager.previewFile('${this.escapeHtml(progressInfo.file_path)}', '${this.escapeHtml(fileName)}')"
                            title="预览文件">
                        <i class="bi bi-eye"></i>
                    </button>
                ` : ''}
            </div>
        `;
    }

    /**
     * 渲染分页
     */
    renderPagination(data) {
        const container = document.getElementById('projectPaginationContainer');
        if (!container) return;

        const totalPages = data.total_pages || 1;
        const currentPage = data.page || 1;

        let html = '<nav><ul class="pagination pagination-sm mb-0">';

        // 上一页
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="javascript:void(0)"
                   onclick="projectOverviewManager.goToPage(${currentPage - 1})">
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
                           onclick="projectOverviewManager.goToPage(${i})}">${i}</a>
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
                   onclick="projectOverviewManager.goToPage(${currentPage + 1})">
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
        const searchInput = document.getElementById('projectSearchInput');
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
        const statusFilter = document.getElementById('projectStatusFilter');
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
     * 创建新项目 - 切换到投标管理Tab
     */
    createNewProject() {
        // 切换到投标管理Tab，让用户在那里创建新项目
        const tenderManagementNav = document.getElementById('tender-management-nav');
        if (tenderManagementNav) {
            const tab = new bootstrap.Tab(tenderManagementNav);
            tab.show();

            // 提示用户
            if (typeof showNotification === 'function') {
                showNotification('请在投标管理页面创建新项目', 'info');
            }
        }
    }

    /**
     * 进入标书处理页面 - 切换到投标管理Tab并加载项目
     */
    enterProcessing(projectId) {
        console.log(`[ProjectOverviewManager] 进入项目处理: ${projectId}`);

        // 获取项目信息
        const project = this.projects.find(p => p.project_id === projectId);
        if (!project) {
            console.error('[ProjectOverviewManager] 未找到项目:', projectId);
            return;
        }

        // ✅ 使用 globalState 批量保存项目和公司信息
        if (window.globalState) {
            window.globalState.setBulk({
                company: {
                    id: project.company_id,
                    name: project.company_name
                },
                project: {
                    id: projectId,
                    name: project.project_name
                }
            });
            console.log('[ProjectOverviewManager] 已保存项目信息到 globalState');
        } else {
            console.error('[ProjectOverviewManager] globalState 未初始化');
        }

        // 切换到投标管理Tab
        const tenderManagementNav = document.getElementById('tender-management-nav');
        if (tenderManagementNav) {
            const tab = new bootstrap.Tab(tenderManagementNav);
            tab.show();

            // 延迟一下等Tab切换完成后，触发项目加载
            setTimeout(() => {
                // 触发自定义事件，通知投标管理页面加载特定项目
                const event = new CustomEvent('loadProjectFromOverview', {
                    detail: {
                        projectId: projectId,
                        companyId: project.company_id,
                        companyName: project.company_name,
                        projectName: project.project_name
                    }
                });
                document.dispatchEvent(event);
            }, 300);
        }
    }

    /**
     * 删除项目
     */
    async deleteProject(projectId) {
        // 获取项目信息
        const project = this.projects.find(p => p.project_id === projectId);
        const projectName = project ? project.project_name : `项目${projectId}`;

        // 二次确认
        if (!confirm(`确定要删除项目"${projectName}"吗？\n\n此操作将删除:\n- 项目基本信息\n- 所有处理任务和日志\n- 文档分块和要求提取结果\n\n此操作不可恢复！`)) {
            return;
        }

        try {
            console.log(`[ProjectOverviewManager] 删除项目: ${projectId}`);

            // 调用删除API
            const response = await fetch(`/api/tender-management/project/${projectId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                // 显示成功消息
                if (typeof showNotification === 'function') {
                    showNotification(result.message || '项目已成功删除', 'success');
                } else {
                    alert(result.message || '项目已成功删除');
                }

                console.log('[ProjectOverviewManager] 删除统计:', result.deleted_counts);

                // 刷新列表
                await this.loadProjects();
            } else {
                throw new Error(result.error || '删除失败');
            }
        } catch (error) {
            console.error('[ProjectOverviewManager] 删除项目失败:', error);

            // 显示错误消息
            const errorMsg = error.message || '删除项目失败';
            if (typeof showNotification === 'function') {
                showNotification(errorMsg, 'error');
            } else {
                alert(errorMsg);
            }
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
        const tbody = document.getElementById('projectOverviewListBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center">
                        <div class="py-4">
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
        const tbody = document.getElementById('projectOverviewListBody');
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
     * 预览文件
     */
    previewFile(filePath, fileName) {
        console.log(`[ProjectOverviewManager] 预览文件: ${fileName} (${filePath})`);

        // 将文件路径转换为下载URL（使用point-to-point的下载API）
        const downloadUrl = `/api/point-to-point/download?file_path=${encodeURIComponent(filePath)}`;

        // 使用全局的文档预览工具
        if (window.documentPreviewUtil) {
            window.documentPreviewUtil.preview(downloadUrl, fileName);
        } else {
            console.error('[ProjectOverviewManager] DocumentPreviewUtil 未初始化');
            if (window.notifications) {
                window.notifications.error('文档预览工具未初始化');
            } else {
                alert('文档预览工具未初始化');
            }
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
window.projectOverviewManager = new ProjectOverviewManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    window.projectOverviewManager.initialize();
});