/**
 * 简历库管理器（重构后）
 * 负责简历列表视图、搜索筛选、分页等核心功能
 * 复杂功能已拆分为独立子模块
 */
class ResumeLibraryManager {
    constructor() {
        // 核心属性
        this.container = null;
        this.currentPage = 1;
        this.pageSize = 20;
        this.searchKeyword = '';
        this.selectedResumeIds = new Set();
        this.currentCompanyId = null;
        this.initialized = false;

        // 注入子模块（依赖注入模式）
        this.batchExporter = new ResumeBatchExporter(this);
        this.parser = new ResumeParser(this);
        this.detailManager = new ResumeDetailManager(this);

        // 经历管理器和附件管理器通过 detailManager 访问
        this.experienceManager = this.detailManager.experienceManager;
        this.attachmentManager = this.detailManager.attachmentManager;
    }

    /**
     * 初始化管理器
     */
    async initialize() {
        if (this.initialized) {
            console.log('ResumeLibraryManager already initialized');
            return;
        }

        console.log('Initializing ResumeLibraryManager...');
        this.container = document.getElementById('resumeLibraryContainer');

        // 获取当前公司ID
        const companySelector = document.getElementById('currentCompanyId');
        if (companySelector) {
            this.currentCompanyId = companySelector.value;
        }

        this.initialized = true;
        console.log('ResumeLibraryManager initialized successfully');
    }

    /**
     * 渲染简历库主视图
     */
    async renderResumeLibraryView() {
        if (!this.container) {
            console.error('Container not found');
            return;
        }

        const html = `
            <div class="resume-library-wrapper">
                <!-- 页面标题卡片 - 统一模板 -->
                <div class="page-header-card mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-0">
                                <i class="bi bi-person-vcard me-2"></i>简历库管理
                            </h5>
                            <small class="text-muted">管理人员简历信息，支持智能解析和批量导出</small>
                        </div>
                        <span class="badge bg-primary">
                            总简历数：<strong id="resumeTotalCount">0</strong>
                        </span>
                    </div>
                </div>

                <!-- 工具栏 -->
                <div class="toolbar-section mb-4">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <div class="btn-group" role="group">
                                <button class="btn btn-primary" onclick="window.resumeLibraryManager.showAddResumeModal()">
                                    <i class="bi bi-plus-circle me-2"></i>添加简历
                                </button>
                                <button class="btn btn-success" onclick="window.resumeLibraryManager.showParseResumeModal()">
                                    <i class="bi bi-file-earmark-text me-2"></i>智能解析
                                </button>
                                <button class="btn btn-info" onclick="window.resumeLibraryManager.showBatchExportModal()"
                                        id="batchExportBtn" disabled>
                                    <i class="bi bi-download me-2"></i>批量导出
                                </button>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="input-group">
                                <input type="text" class="form-control" placeholder="搜索姓名、职位、技能..."
                                       id="resumeSearchInput" value="${this.searchKeyword}">
                                <button class="btn btn-outline-secondary" onclick="window.resumeLibraryManager.searchResumes()">
                                    <i class="bi bi-search"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 筛选条件 -->
                <div class="filter-section mb-3">
                    <div class="row g-2">
                        <div class="col-md-3">
                            <select class="form-select form-select-sm" id="educationFilter">
                                <option value="">全部学历</option>
                                <option value="博士">博士</option>
                                <option value="硕士">硕士</option>
                                <option value="本科">本科</option>
                                <option value="大专">大专</option>
                                <option value="高中">高中</option>
                                <option value="中专">中专</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-select form-select-sm" id="statusFilter">
                                <option value="">全部状态</option>
                                <option value="active">在职</option>
                                <option value="inactive">离职</option>
                                <option value="archived">归档</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <input type="text" class="form-control form-control-sm"
                                   placeholder="职位筛选" id="positionFilter">
                        </div>
                        <div class="col-md-3">
                            <button class="btn btn-sm btn-primary w-100" onclick="window.resumeLibraryManager.applyFilters()">
                                <i class="bi bi-funnel me-1"></i>应用筛选
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 统计信息 -->
                <div class="stats-section mb-3" id="resumeStatsSection">
                    <div class="alert alert-info py-2">
                        <i class="bi bi-info-circle me-2"></i>
                        <span id="resumeStatsText">加载中...</span>
                    </div>
                </div>

                <!-- 简历列表 -->
                <div class="resume-list-section">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th width="40">
                                        <input type="checkbox" class="form-check-input"
                                               onchange="window.resumeLibraryManager.toggleSelectAll(this)">
                                    </th>
                                    <th>姓名</th>
                                    <th>性别</th>
                                    <th>学历</th>
                                    <th>职位</th>
                                    <th>工作单位</th>
                                    <th>联系方式</th>
                                    <th>附件</th>
                                    <th>状态</th>
                                    <th width="150">操作</th>
                                </tr>
                            </thead>
                            <tbody id="resumeListBody">
                                <tr>
                                    <td colspan="10" class="text-center py-4">
                                        <div class="spinner-border spinner-border-sm me-2"></div>
                                        加载中...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 分页 -->
                <div class="pagination-section mt-3" id="resumePagination"></div>
            </div>

            <!-- 模态框容器 -->
            <div id="resumeModalsContainer"></div>
        `;

        this.container.innerHTML = html;

        // 绑定搜索框回车事件
        const searchInput = document.getElementById('resumeSearchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchResumes();
                }
            });
        }

        // 加载简历列表
        await this.loadResumes();
    }

    /**
     * 加载简历列表
     */
    async loadResumes() {
        try {
            const filters = this.getFilters();
            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize,
                search: this.searchKeyword,
                ...filters
            });

            if (this.currentCompanyId) {
                params.append('company_id', this.currentCompanyId);
            }

            const result = await window.apiClient.get(`/api/resume_library/list?${params}`);

            if (result.success) {
                this.renderResumeList(result.data.resumes);
                this.renderPagination(result.data);
                this.updateStats(result.data);
            } else {
                window.notifications.error('加载简历列表失败: ' + result.error);
            }
        } catch (error) {
            console.error('加载简历失败:', error);
            window.notifications.error('加载简历失败');
        }
    }

    /**
     * 渲染简历列表
     */
    renderResumeList(resumes) {
        const tbody = document.getElementById('resumeListBody');
        if (!tbody) return;

        if (resumes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center py-4 text-muted">
                        <i class="bi bi-inbox fs-3 d-block mb-2"></i>
                        暂无简历数据
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = resumes.map(resume => `
            <tr data-resume-id="${resume.resume_id}">
                <td>
                    <input type="checkbox" class="form-check-input resume-checkbox"
                           value="${resume.resume_id}"
                           ${this.selectedResumeIds.has(resume.resume_id) ? 'checked' : ''}
                           onchange="window.resumeLibraryManager.toggleResumeSelection(${resume.resume_id})">
                </td>
                <td>
                    <a href="javascript:void(0)" onclick="window.resumeLibraryManager.viewResumeDetail(${resume.resume_id})"
                       class="text-decoration-none">
                        ${this.escapeHtml(resume.name || '')}
                    </a>
                </td>
                <td>${resume.gender || '-'}</td>
                <td>${resume.education_level || '-'}</td>
                <td>${resume.current_position || '-'}</td>
                <td>${this.escapeHtml(resume.current_company || '-')}</td>
                <td>
                    ${resume.phone ? `<i class="bi bi-telephone me-1"></i>${resume.phone}` : ''}
                    ${resume.email ? `<br><i class="bi bi-envelope me-1"></i>${resume.email}` : ''}
                </td>
                <td>
                    <span class="badge bg-secondary">
                        ${resume.attachment_count || 0} 个
                    </span>
                </td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(resume.status)}">
                        ${this.getStatusLabel(resume.status)}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary"
                                onclick="window.resumeLibraryManager.viewResumeDetail(${resume.resume_id})"
                                title="详情">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-outline-danger"
                                onclick="window.resumeLibraryManager.deleteResume(${resume.resume_id})"
                                title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    /**
     * 显示添加简历模态框
     */
    showAddResumeModal() {
        // 简单添加可以直接跳转到详情页（新建模式）
        // 或使用智能解析
        window.notifications.info('请使用智能解析功能上传简历');
        this.showParseResumeModal();
    }

    // ==================== 子模块调用（薄包装层） ====================

    /**
     * 显示智能解析模态框（调用 ResumeParser）
     */
    showParseResumeModal() {
        this.parser.showParseModal();
    }

    /**
     * 显示批量导出模态框（调用 ResumeBatchExporter）
     */
    showBatchExportModal() {
        this.batchExporter.showBatchExportModal();
    }

    /**
     * 查看简历详情（调用 ResumeDetailManager）
     */
    async viewResumeDetail(resumeId) {
        await this.detailManager.renderDetailView(resumeId);
    }

    /**
     * 返回列表视图（被 detailManager 调用）
     */
    async showResumeListView() {
        await this.renderResumeLibraryView();
    }

    // ==================== 搜索和筛选 ====================

    /**
     * 搜索简历
     */
    searchResumes() {
        const searchInput = document.getElementById('resumeSearchInput');
        if (searchInput) {
            this.searchKeyword = searchInput.value.trim();
        }
        this.currentPage = 1;
        this.loadResumes();
    }

    /**
     * 应用筛选条件
     */
    applyFilters() {
        this.currentPage = 1;
        this.loadResumes();
    }

    /**
     * 获取筛选条件
     */
    getFilters() {
        const filters = {};

        const educationFilter = document.getElementById('educationFilter');
        if (educationFilter && educationFilter.value) {
            filters.education_level = educationFilter.value;
        }

        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter && statusFilter.value) {
            filters.status = statusFilter.value;
        }

        const positionFilter = document.getElementById('positionFilter');
        if (positionFilter && positionFilter.value) {
            filters.position = positionFilter.value;
        }

        return filters;
    }

    // ==================== 批量选择 ====================

    /**
     * 切换简历选择
     */
    toggleResumeSelection(resumeId) {
        if (this.selectedResumeIds.has(resumeId)) {
            this.selectedResumeIds.delete(resumeId);
        } else {
            this.selectedResumeIds.add(resumeId);
        }

        // 更新批量导出按钮状态
        const exportBtn = document.getElementById('batchExportBtn');
        if (exportBtn) {
            exportBtn.disabled = this.selectedResumeIds.size === 0;
        }
    }

    /**
     * 切换全选
     */
    toggleSelectAll(checkbox) {
        const checkboxes = document.querySelectorAll('.resume-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = checkbox.checked;
            const resumeId = parseInt(cb.value);
            if (checkbox.checked) {
                this.selectedResumeIds.add(resumeId);
            } else {
                this.selectedResumeIds.delete(resumeId);
            }
        });

        // 更新批量导出按钮状态
        const exportBtn = document.getElementById('batchExportBtn');
        if (exportBtn) {
            exportBtn.disabled = this.selectedResumeIds.size === 0;
        }
    }

    // ==================== 分页 ====================

    /**
     * 渲染分页
     */
    renderPagination(data) {
        const container = document.getElementById('resumePagination');
        if (!container) return;

        const totalPages = data.total_pages || 1;
        const currentPage = data.page || 1;

        let html = '<nav><ul class="pagination justify-content-center">';

        // 上一页
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="javascript:void(0)"
               onclick="window.resumeLibraryManager.goToPage(${currentPage - 1})">上一页</a>
        </li>`;

        // 页码
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="javascript:void(0)"
                       onclick="window.resumeLibraryManager.goToPage(${i})">${i}</a>
                </li>`;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                html += '<li class="page-item disabled"><a class="page-link">...</a></li>';
            }
        }

        // 下一页
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="javascript:void(0)"
               onclick="window.resumeLibraryManager.goToPage(${currentPage + 1})">下一页</a>
        </li>`;

        html += '</ul></nav>';
        container.innerHTML = html;
    }

    /**
     * 跳转到指定页
     */
    goToPage(page) {
        if (page < 1) return;
        this.currentPage = page;
        this.loadResumes();
    }

    // ==================== 统计 ====================

    /**
     * 更新统计信息
     */
    updateStats(data) {
        const statsText = document.getElementById('resumeStatsText');
        if (statsText) {
            statsText.textContent = `共 ${data.total} 份简历，当前显示第 ${data.page} 页`;
        }

        // 更新页面标题卡片中的总数徽章
        const totalCountBadge = document.getElementById('resumeTotalCount');
        if (totalCountBadge) {
            totalCountBadge.textContent = data.total || 0;
        }
    }

    // ==================== 简历操作 ====================

    /**
     * 删除简历
     */
    async deleteResume(resumeId) {
        if (!confirm('确定要删除这份简历吗？此操作不可恢复。')) {
            return;
        }

        try {
            const result = await window.apiClient.delete(`/api/resume_library/delete/${resumeId}`);

            if (result.success) {
                // 从选中列表中移除
                this.selectedResumeIds.delete(resumeId);

                // 刷新列表
                await this.loadResumes();

                window.notifications.success('简历已删除');
            } else {
                window.notifications.error('删除失败: ' + result.error);
            }
        } catch (error) {
            console.error('删除简历失败:', error);
            window.notifications.error('删除失败');
        }
    }

    // ==================== 工具方法 ====================

    /**
     * 获取状态标签样式
     */
    getStatusBadgeClass(status) {
        const classes = {
            'active': 'bg-success',
            'inactive': 'bg-warning',
            'archived': 'bg-secondary'
        };
        return classes[status] || 'bg-secondary';
    }

    /**
     * 获取状态标签文本
     */
    getStatusLabel(status) {
        const labels = {
            'active': '在职',
            'inactive': '离职',
            'archived': '归档'
        };
        return labels[status] || status;
    }

    /**
     * HTML转义
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
window.resumeLibraryManager = new ResumeLibraryManager();
