/**
 * 简历库管理器
 * 负责简历的增删改查、智能解析、批量导出等功能
 */
class ResumeLibraryManager {
    constructor() {
        this.container = null;
        this.currentPage = 1;
        this.pageSize = 20;
        this.searchKeyword = '';
        this.selectedResumeIds = new Set();
        this.currentCompanyId = null;
        this.uploader = null;
        this.initialized = false;
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

            const response = await fetch(`/api/resume_library/list?${params}`);
            const result = await response.json();

            if (result.success) {
                this.renderResumeList(result.data.resumes);
                this.renderPagination(result.data);
                this.updateStats(result.data);
            } else {
                this.showError('加载简历列表失败: ' + result.error);
            }
        } catch (error) {
            console.error('加载简历失败:', error);
            this.showError('加载简历失败');
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
        const modal = this.createResumeFormModal(null, '添加简历');
        modal.show();
    }

    /**
     * 显示智能解析模态框
     */
    showParseResumeModal() {
        const modalHtml = `
            <div class="modal fade" id="parseResumeModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-earmark-text me-2"></i>智能简历解析
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- 上传区域 -->
                            <div id="resumeUploadArea" class="mb-4">
                                <div class="alert alert-info">
                                    <i class="bi bi-info-circle me-2"></i>
                                    上传Word或PDF格式的简历文件，系统将自动解析并填充人员信息
                                </div>

                                <!-- 原生文件上传区域 -->
                                <div class="upload-zone border rounded p-4 text-center" id="resumeNativeUploadZone"
                                     style="cursor: pointer; background: #f8f9fa; border: 2px dashed #dee2e6 !important;">
                                    <i class="bi bi-cloud-upload text-primary" style="font-size: 3rem;"></i>
                                    <p class="mt-3 mb-2">点击或拖拽文件到这里上传</p>
                                    <small class="text-muted">支持 PDF、Word 文档（最大10MB）</small>
                                    <input type="file" id="resumeFileInput" accept=".pdf,.doc,.docx"
                                           style="display: none;">
                                </div>

                                <!-- 文件信息显示 -->
                                <div id="resumeFileInfo" class="mt-3 d-none">
                                    <div class="alert alert-success">
                                        <i class="bi bi-file-earmark-text me-2"></i>
                                        已选择文件：<strong id="resumeFileName"></strong>
                                        <span id="resumeFileSize" class="text-muted"></span>
                                    </div>
                                </div>

                                <!-- 上传进度 -->
                                <div id="resumeUploadProgress" class="mt-3 d-none">
                                    <div class="progress">
                                        <div class="progress-bar progress-bar-striped progress-bar-animated"
                                             role="progressbar" style="width: 0%">
                                            正在上传...
                                        </div>
                                    </div>
                                </div>

                                <!-- 错误提示 -->
                                <div id="resumeUploadError" class="mt-3 d-none">
                                    <div class="alert alert-danger">
                                        <i class="bi bi-exclamation-triangle me-2"></i>
                                        <span id="resumeErrorMessage"></span>
                                    </div>
                                </div>
                            </div>

                            <!-- 解析结果 -->
                            <div id="parseResultSection" style="display:none;">
                                <h6 class="mb-3">解析结果</h6>
                                <form id="parsedResumeForm">
                                    <div class="row g-3">
                                        <div class="col-md-6">
                                            <label class="form-label">姓名 <span class="text-danger">*</span></label>
                                            <input type="text" class="form-control" name="name" required>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">性别</label>
                                            <select class="form-select" name="gender">
                                                <option value="">请选择</option>
                                                <option value="男">男</option>
                                                <option value="女">女</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">手机号码</label>
                                            <input type="tel" class="form-control" name="phone">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">邮箱</label>
                                            <input type="email" class="form-control" name="email">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">学历</label>
                                            <select class="form-select" name="education_level">
                                                <option value="">请选择</option>
                                                <option value="博士">博士</option>
                                                <option value="硕士">硕士</option>
                                                <option value="本科">本科</option>
                                                <option value="大专">大专</option>
                                                <option value="高中">高中</option>
                                                <option value="中专">中专</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">毕业院校</label>
                                            <input type="text" class="form-control" name="university">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">专业</label>
                                            <input type="text" class="form-control" name="major">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">当前职位</label>
                                            <input type="text" class="form-control" name="current_position">
                                        </div>
                                        <div class="col-md-12">
                                            <label class="form-label">当前工作单位</label>
                                            <input type="text" class="form-control" name="current_company">
                                        </div>
                                        <div class="col-md-12">
                                            <label class="form-label">个人简介</label>
                                            <textarea class="form-control" name="introduction" rows="3"></textarea>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="saveParseResultBtn"
                                    style="display:none;" onclick="window.resumeLibraryManager.saveParsedResume()">
                                <i class="bi bi-check-circle me-2"></i>保存简历
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 添加到页面
        const container = document.getElementById('resumeModalsContainer');
        container.innerHTML = modalHtml;

        // 初始化原生文件上传
        this.initResumeUploader();

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('parseResumeModal'));
        modal.show();
    }

    /**
     * 初始化简历上传组件（原生文件上传）
     */
    initResumeUploader() {
        const uploadZone = document.getElementById('resumeNativeUploadZone');
        const fileInput = document.getElementById('resumeFileInput');
        const fileInfo = document.getElementById('resumeFileInfo');
        const fileName = document.getElementById('resumeFileName');
        const fileSize = document.getElementById('resumeFileSize');

        if (!uploadZone || !fileInput) {
            console.error('[ResumeUploader] 上传区域或文件输入元素未找到');
            return;
        }

        console.log('[ResumeUploader] 初始化原生文件上传...');

        // 上传区域点击事件
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        // 文件选择事件
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                console.log('[ResumeUploader] 文件已选择:', file.name);
                this.displayResumeFileInfo(file);
                this.uploadAndParseResume(file);
            }
        });

        // 拖拽上传事件
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.style.borderColor = '#4a89dc';
                uploadZone.style.background = '#e8f4ff';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.style.borderColor = '#dee2e6';
                uploadZone.style.background = '#f8f9fa';
            }, false);
        });

        uploadZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                console.log('[ResumeUploader] 拖拽文件:', file.name);
                fileInput.files = files;
                this.displayResumeFileInfo(file);
                this.uploadAndParseResume(file);
            }
        }, false);

        console.log('[ResumeUploader] 初始化完成');
    }

    /**
     * 防止默认拖拽行为
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * 显示文件信息
     */
    displayResumeFileInfo(file) {
        const fileName = document.getElementById('resumeFileName');
        const fileSize = document.getElementById('resumeFileSize');
        const fileInfo = document.getElementById('resumeFileInfo');

        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = `(${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        if (fileInfo) fileInfo.classList.remove('d-none');

        console.log('[ResumeUploader] 文件信息已显示');
    }

    /**
     * 上传并解析简历
     */
    async uploadAndParseResume(file) {
        console.log('[ResumeUploader] 开始上传并解析简历...');

        // 验证文件类型
        const allowedTypes = ['.pdf', '.doc', '.docx'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExt)) {
            this.showResumeError('不支持的文件格式，请上传 PDF 或 Word 文档');
            return;
        }

        // 验证文件大小（10MB）
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showResumeError('文件太大，最大支持 10MB');
            return;
        }

        // 显示上传进度
        this.showResumeProgress(true);
        this.hideResumeError();

        // 构建FormData
        const formData = new FormData();
        formData.append('file', file);
        if (this.currentCompanyId) {
            formData.append('company_id', this.currentCompanyId);
        }

        try {
            const response = await fetch('/api/resume_library/parse-resume', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            console.log('[ResumeUploader] 解析结果:', result);

            if (result.success && result.data && result.data.parsed_data) {
                // 填充解析结果
                this.fillParsedData(result.data.parsed_data);

                // 显示解析结果表单
                const resultSection = document.getElementById('parseResultSection');
                const saveBtn = document.getElementById('saveParseResultBtn');
                if (resultSection) resultSection.style.display = 'block';
                if (saveBtn) saveBtn.style.display = 'inline-block';

                // 隐藏上传区域
                const uploadArea = document.getElementById('resumeUploadArea');
                if (uploadArea) uploadArea.style.display = 'none';

                console.log('[ResumeUploader] 解析成功，已填充数据');
            } else {
                throw new Error(result.error || result.message || '解析失败');
            }
        } catch (error) {
            console.error('[ResumeUploader] 上传解析失败:', error);
            this.showResumeError('简历解析失败: ' + error.message);
        } finally {
            this.showResumeProgress(false);
        }
    }

    /**
     * 显示/隐藏上传进度
     */
    showResumeProgress(show) {
        const progress = document.getElementById('resumeUploadProgress');
        if (progress) {
            if (show) {
                progress.classList.remove('d-none');
            } else {
                progress.classList.add('d-none');
            }
        }
    }

    /**
     * 显示错误信息
     */
    showResumeError(message) {
        const errorDiv = document.getElementById('resumeUploadError');
        const errorMsg = document.getElementById('resumeErrorMessage');
        if (errorDiv && errorMsg) {
            errorMsg.textContent = message;
            errorDiv.classList.remove('d-none');
        }
        console.error('[ResumeUploader] 错误:', message);
    }

    /**
     * 隐藏错误信息
     */
    hideResumeError() {
        const errorDiv = document.getElementById('resumeUploadError');
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }
    }

    /**
     * 填充解析的数据到表单
     */
    fillParsedData(data) {
        const form = document.getElementById('parsedResumeForm');
        if (!form) return;

        // 填充表单字段
        Object.keys(data).forEach(key => {
            const input = form.elements[key];
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = data[key];
                } else {
                    input.value = data[key] || '';
                }
            }
        });
    }

    /**
     * 保存解析的简历
     */
    async saveParsedResume() {
        const form = document.getElementById('parsedResumeForm');
        if (!form) return;

        // 收集表单数据
        const formData = new FormData(form);
        const resumeData = {};
        formData.forEach((value, key) => {
            resumeData[key] = value;
        });

        // 添加公司ID
        if (this.currentCompanyId) {
            resumeData.company_id = this.currentCompanyId;
        }

        try {
            const response = await fetch('/api/resume_library/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(resumeData)
            });

            const result = await response.json();
            if (result.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('parseResumeModal'));
                modal.hide();

                // 刷新列表
                await this.loadResumes();

                // 显示成功消息
                this.showSuccess('简历保存成功');
            } else {
                this.showError('保存失败: ' + result.error);
            }
        } catch (error) {
            console.error('保存简历失败:', error);
            this.showError('保存失败');
        }
    }

    /**
     * 显示批量导出模态框
     */
    showBatchExportModal() {
        if (this.selectedResumeIds.size === 0) {
            this.showWarning('请先选择要导出的简历');
            return;
        }

        const modalHtml = `
            <div class="modal fade" id="batchExportModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-download me-2"></i>批量导出简历
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                已选择 <strong>${this.selectedResumeIds.size}</strong> 份简历
                            </div>

                            <div class="mb-3">
                                <label class="form-label">导出选项</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="includeAttachments" checked>
                                    <label class="form-check-label" for="includeAttachments">
                                        包含附件
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="includeS Summary" checked>
                                    <label class="form-check-label" for="includeSummary">
                                        生成汇总文件
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="organizeByCategory" checked>
                                    <label class="form-check-label" for="organizeByCategory">
                                        按类别组织文件
                                    </label>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">附件类别</label>
                                <div class="row g-2">
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="resume" id="cat_resume" checked>
                                            <label class="form-check-label" for="cat_resume">简历文件</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="id_card" id="cat_id_card" checked>
                                            <label class="form-check-label" for="cat_id_card">身份证</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="education" id="cat_education" checked>
                                            <label class="form-check-label" for="cat_education">学历证书</label>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="degree" id="cat_degree" checked>
                                            <label class="form-check-label" for="cat_degree">学位证书</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="qualification" id="cat_qualification" checked>
                                            <label class="form-check-label" for="cat_qualification">资质证书</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="award" id="cat_award" checked>
                                            <label class="form-check-label" for="cat_award">获奖证书</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="window.resumeLibraryManager.executeExport()">
                                <i class="bi bi-download me-2"></i>开始导出
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('resumeModalsContainer');
        container.innerHTML = modalHtml;

        const modal = new bootstrap.Modal(document.getElementById('batchExportModal'));
        modal.show();
    }

    /**
     * 执行导出
     */
    async executeExport() {
        // 收集选项
        const options = {
            include_attachments: document.getElementById('includeAttachments').checked,
            include_summary: document.getElementById('includeSummary').checked,
            organize_by_category: document.getElementById('organizeByCategory').checked,
            attachment_categories: []
        };

        // 收集选中的附件类别
        document.querySelectorAll('.attachment-category:checked').forEach(checkbox => {
            options.attachment_categories.push(checkbox.value);
        });

        // 准备导出数据
        const exportData = {
            resume_ids: Array.from(this.selectedResumeIds),
            options: options
        };

        try {
            // 显示进度提示
            this.showLoading('正在导出，请稍候...');

            const response = await fetch('/api/resume_library/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exportData)
            });

            const result = await response.json();
            if (result.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('batchExportModal'));
                modal.hide();

                // 下载文件
                if (result.data.download_url) {
                    window.location.href = result.data.download_url;
                }

                // 显示统计信息
                this.showSuccess(`导出成功！共导出 ${result.data.stats.total_resumes} 份简历，${result.data.stats.total_attachments} 个附件`);
            } else {
                this.showError('导出失败: ' + result.error);
            }
        } catch (error) {
            console.error('导出失败:', error);
            this.showError('导出失败');
        } finally {
            this.hideLoading();
        }
    }

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

    /**
     * 更新统计信息
     */
    updateStats(data) {
        const statsText = document.getElementById('resumeStatsText');
        if (statsText) {
            statsText.textContent = `共 ${data.total} 份简历，当前显示第 ${data.page} 页`;
        }
    }

    /**
     * 查看简历详情
     */
    async viewResumeDetail(resumeId) {
        await this.renderResumeDetailView(resumeId);
    }


    /**
     * 删除简历
     */
    async deleteResume(resumeId) {
        if (!confirm('确定要删除这份简历吗？此操作不可恢复。')) {
            return;
        }

        try {
            const response = await fetch(`/api/resume_library/delete/${resumeId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            if (result.success) {
                // 从选中列表中移除
                this.selectedResumeIds.delete(resumeId);

                // 刷新列表
                await this.loadResumes();

                this.showSuccess('简历已删除');
            } else {
                this.showError('删除失败: ' + result.error);
            }
        } catch (error) {
            console.error('删除简历失败:', error);
            this.showError('删除失败');
        }
    }


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

    /**
     * 显示加载提示
     */
    showLoading(message = '加载中...') {
        // TODO: 实现加载提示
        console.log('Loading:', message);
    }

    /**
     * 隐藏加载提示
     */
    hideLoading() {
        // TODO: 实现隐藏加载提示
        console.log('Hide loading');
    }

    /**
     * 显示成功消息
     */
    showSuccess(message) {
        // 使用Bootstrap toast或其他通知组件
        if (window.showNotification) {
            window.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    /**
     * 显示错误消息
     */
    showError(message) {
        if (window.showNotification) {
            window.showNotification(message, 'error');
        } else {
            alert('错误: ' + message);
        }
    }

    /**
     * 显示警告消息
     */
    showWarning(message) {
        if (window.showNotification) {
            window.showNotification(message, 'warning');
        } else {
            alert('警告: ' + message);
        }
    }

    // ==================== 详情页面相关方法 ====================

    /**
     * 渲染简历详情/编辑页面
     */
    async renderResumeDetailView(resumeId) {
        console.log('渲染简历详情页面...', resumeId);

        if (!this.container) {
            console.error('Container not found');
            return;
        }

        const html = `
            <div class="resume-detail-wrapper">
                <!-- 顶部操作栏 -->
                <div class="case-edit-header mb-4">
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="d-flex align-items-center">
                            <button type="button" class="btn btn-outline-secondary me-3"
                                    onclick="window.resumeLibraryManager.showResumeListView()">
                                <i class="bi bi-arrow-left me-1"></i>返回列表
                            </button>
                            <h4 class="mb-0">简历详情</h4>
                        </div>
                        <div>
                            <button type="button" class="btn btn-primary"
                                    onclick="window.resumeLibraryManager.saveResume()">
                                <i class="bi bi-save me-1"></i>保存
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 详情内容 -->
                <div class="resume-detail-content">
                    <input type="hidden" id="resumeId" value="${resumeId}">

                    <!-- 基本信息 -->
                    <div class="case-form-section">
                        <h6>基本信息</h6>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">姓名 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="resumeName" required>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">性别</label>
                                <select class="form-select" id="resumeGender">
                                    <option value="">请选择</option>
                                    <option value="男">男</option>
                                    <option value="女">女</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">出生日期</label>
                                <input type="date" class="form-control" id="resumeBirthDate">
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-4">
                                <label class="form-label">民族</label>
                                <input type="text" class="form-control" id="resumeNationality">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">籍贯</label>
                                <input type="text" class="form-control" id="resumeNativePlace">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">政治面貌</label>
                                <select class="form-select" id="resumePoliticalStatus">
                                    <option value="">请选择</option>
                                    <option value="中共党员">中共党员</option>
                                    <option value="共青团员">共青团员</option>
                                    <option value="群众">群众</option>
                                    <option value="民主党派">民主党派</option>
                                </select>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <label class="form-label">身份证号</label>
                                <input type="text" class="form-control" id="resumeIdNumber">
                            </div>
                        </div>
                    </div>

                    <!-- 联系方式 -->
                    <div class="case-form-section">
                        <h6>联系方式</h6>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">手机号码</label>
                                <input type="tel" class="form-control" id="resumePhone">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">电子邮箱</label>
                                <input type="email" class="form-control" id="resumeEmail">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">联系地址</label>
                                <input type="text" class="form-control" id="resumeAddress">
                            </div>
                        </div>
                    </div>

                    <!-- 教育信息 -->
                    <div class="case-form-section">
                        <h6>教育信息</h6>
                        <div class="row">
                            <div class="col-md-3">
                                <label class="form-label">学历</label>
                                <select class="form-select" id="resumeEducationLevel">
                                    <option value="">请选择</option>
                                    <option value="博士">博士</option>
                                    <option value="硕士">硕士</option>
                                    <option value="本科">本科</option>
                                    <option value="大专">大专</option>
                                    <option value="高中">高中</option>
                                    <option value="中专">中专</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">学位</label>
                                <input type="text" class="form-control" id="resumeDegree" placeholder="如：工学硕士">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">毕业院校</label>
                                <input type="text" class="form-control" id="resumeUniversity">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">专业</label>
                                <input type="text" class="form-control" id="resumeMajor">
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-3">
                                <label class="form-label">毕业时间</label>
                                <input type="date" class="form-control" id="resumeGraduationDate">
                            </div>
                        </div>
                    </div>

                    <!-- 工作信息 -->
                    <div class="case-form-section">
                        <h6>工作信息</h6>
                        <div class="row">
                            <div class="col-md-3">
                                <label class="form-label">当前职位</label>
                                <input type="text" class="form-control" id="resumeCurrentPosition">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">职称</label>
                                <input type="text" class="form-control" id="resumeProfessionalTitle">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">工作年限</label>
                                <input type="number" class="form-control" id="resumeWorkYears" min="0">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">状态</label>
                                <select class="form-select" id="resumeStatus">
                                    <option value="active">在职</option>
                                    <option value="inactive">离职</option>
                                    <option value="archived">归档</option>
                                </select>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <label class="form-label">当前工作单位</label>
                                <input type="text" class="form-control" id="resumeCurrentCompany">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">所在部门</label>
                                <input type="text" class="form-control" id="resumeDepartment">
                            </div>
                        </div>
                    </div>

                    <!-- 其他信息 -->
                    <div class="case-form-section">
                        <h6>其他信息</h6>
                        <div class="row">
                            <div class="col-md-12">
                                <label class="form-label">获奖情况</label>
                                <textarea class="form-control" id="resumeAwards" rows="3"></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- 附件管理 -->
                    <div class="case-form-section">
                        <h6>
                            <i class="bi bi-paperclip me-2"></i>简历附件
                            <span class="badge bg-secondary ms-2" id="resumeAttachmentCount">0</span>
                        </h6>

                        <!-- 上传区域 -->
                        <div class="case-attachment-upload-area mb-3">
                            <div class="upload-box">
                                <input type="file" id="resumeAttachmentInput" multiple
                                       accept="image/*,.pdf,.doc,.docx" style="display: none;"
                                       onchange="window.resumeLibraryManager.handleAttachmentSelect(event)">
                                <div class="upload-prompt" onclick="document.getElementById('resumeAttachmentInput').click()">
                                    <i class="bi bi-cloud-upload text-primary" style="font-size: 2rem;"></i>
                                    <p class="mt-2 mb-1">点击或拖拽文件到这里上传</p>
                                    <small class="text-muted">支持图片、PDF、Word文档，单个文件不超过10MB</small>
                                </div>
                            </div>
                        </div>

                        <!-- 附件类型选择 -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">附件类型</label>
                                <select class="form-select" id="resumeAttachmentCategory">
                                    <option value="resume">简历文件</option>
                                    <option value="id_card">身份证</option>
                                    <option value="education">学历证书</option>
                                    <option value="degree">学位证书</option>
                                    <option value="qualification">资质证书</option>
                                    <option value="award">获奖证书</option>
                                    <option value="other">其他</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">附件说明</label>
                                <input type="text" class="form-control" id="resumeAttachmentDescription"
                                       placeholder="选填，简要说明附件内容">
                            </div>
                        </div>

                        <!-- 附件列表 -->
                        <div class="case-attachment-list mt-3" id="resumeAttachmentList">
                            <!-- 附件列表将动态渲染在这里 -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;

        // 加载简历数据
        await this.loadResumeData(resumeId);
    }

    /**
     * 返回列表视图
     */
    async showResumeListView() {
        await this.renderResumeLibraryView();
    }

    /**
     * 加载简历数据
     */
    async loadResumeData(resumeId) {
        try {
            const response = await fetch(`/api/resume_library/detail/${resumeId}`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || '获取简历信息失败');
            }

            const resume = result.data;

            // 填充基本信息
            document.getElementById('resumeName').value = resume.name || '';
            document.getElementById('resumeGender').value = resume.gender || '';
            document.getElementById('resumeBirthDate').value = resume.birth_date || '';
            document.getElementById('resumeNationality').value = resume.nationality || '';
            document.getElementById('resumeNativePlace').value = resume.native_place || '';
            document.getElementById('resumePoliticalStatus').value = resume.political_status || '';
            document.getElementById('resumeIdNumber').value = resume.id_number || '';

            // 填充联系方式
            document.getElementById('resumePhone').value = resume.phone || '';
            document.getElementById('resumeEmail').value = resume.email || '';
            document.getElementById('resumeAddress').value = resume.address || '';

            // 填充教育信息
            document.getElementById('resumeEducationLevel').value = resume.education_level || '';
            document.getElementById('resumeDegree').value = resume.degree || '';
            document.getElementById('resumeUniversity').value = resume.university || '';
            document.getElementById('resumeMajor').value = resume.major || '';
            document.getElementById('resumeGraduationDate').value = resume.graduation_date || '';

            // 填充工作信息
            document.getElementById('resumeCurrentPosition').value = resume.current_position || '';
            document.getElementById('resumeProfessionalTitle').value = resume.professional_title || '';
            document.getElementById('resumeWorkYears').value = resume.work_years || '';
            document.getElementById('resumeStatus').value = resume.status || 'active';
            document.getElementById('resumeCurrentCompany').value = resume.current_company || '';
            document.getElementById('resumeDepartment').value = resume.department || '';

            // 填充其他信息
            document.getElementById('resumeAwards').value = resume.awards || '';

            // 加载附件
            await this.loadResumeAttachments(resumeId);

        } catch (error) {
            console.error('加载简历数据失败:', error);
            this.showError('加载简历数据失败: ' + error.message);
        }
    }

    /**
     * 保存简历
     */
    async saveResume() {
        const resumeId = document.getElementById('resumeId').value;

        // 验证必填字段
        const name = document.getElementById('resumeName').value;
        if (!name || !name.trim()) {
            this.showWarning('请填写姓名');
            document.getElementById('resumeName').focus();
            return;
        }

        // 收集表单数据
        const data = {
            name: name,
            gender: document.getElementById('resumeGender').value,
            birth_date: document.getElementById('resumeBirthDate').value,
            nationality: document.getElementById('resumeNationality').value,
            native_place: document.getElementById('resumeNativePlace').value,
            political_status: document.getElementById('resumePoliticalStatus').value,
            id_number: document.getElementById('resumeIdNumber').value,
            phone: document.getElementById('resumePhone').value,
            email: document.getElementById('resumeEmail').value,
            address: document.getElementById('resumeAddress').value,
            education_level: document.getElementById('resumeEducationLevel').value,
            degree: document.getElementById('resumeDegree').value,
            university: document.getElementById('resumeUniversity').value,
            major: document.getElementById('resumeMajor').value,
            graduation_date: document.getElementById('resumeGraduationDate').value,
            current_position: document.getElementById('resumeCurrentPosition').value,
            professional_title: document.getElementById('resumeProfessionalTitle').value,
            work_years: document.getElementById('resumeWorkYears').value ? parseInt(document.getElementById('resumeWorkYears').value) : null,
            status: document.getElementById('resumeStatus').value,
            current_company: document.getElementById('resumeCurrentCompany').value,
            department: document.getElementById('resumeDepartment').value,
            awards: document.getElementById('resumeAwards').value
        };

        try {
            const response = await fetch(`/api/resume_library/update/${resumeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess('保存成功');
                await this.showResumeListView();
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('保存简历失败:', error);
            this.showError('保存失败：' + error.message);
        }
    }

    /**
     * 加载简历附件列表
     */
    async loadResumeAttachments(resumeId) {
        try {
            const response = await fetch(`/api/resume_library/attachments/${resumeId}`);
            const result = await response.json();

            if (result.success) {
                const attachments = result.data || [];
                this.renderAttachmentList(attachments);

                // 更新附件数量
                const countBadge = document.getElementById('resumeAttachmentCount');
                if (countBadge) {
                    countBadge.textContent = attachments.length;
                }
            }
        } catch (error) {
            console.error('加载附件列表失败:', error);
        }
    }

    /**
     * 渲染附件列表
     */
    renderAttachmentList(attachments) {
        const container = document.getElementById('resumeAttachmentList');
        if (!container) return;

        if (attachments.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-3">暂无附件</div>';
            return;
        }

        const html = attachments.map(att => {
            const typeLabel = this.getAttachmentCategoryLabel(att.attachment_category);
            const fileIcon = this.getFileIcon(att.file_path);

            return `
                <div class="case-attachment-item">
                    <div class="attachment-info">
                        <i class="bi ${fileIcon} me-2 text-primary"></i>
                        <div class="attachment-details">
                            <div class="attachment-name">${this.escapeHtml(att.original_filename || '未知文件')}</div>
                            <div class="attachment-meta">
                                <span class="badge bg-info">${typeLabel}</span>
                                ${att.attachment_description ? `<span class="text-muted ms-2">· ${this.escapeHtml(att.attachment_description)}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="attachment-actions">
                        <button type="button" class="btn btn-sm btn-outline-secondary me-1"
                                onclick="window.resumeLibraryManager.downloadAttachment(${att.attachment_id})" title="下载">
                            <i class="bi bi-download"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger"
                                onclick="window.resumeLibraryManager.deleteAttachment(${att.attachment_id})" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    /**
     * 处理附件选择
     */
    async handleAttachmentSelect(event) {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        const resumeId = document.getElementById('resumeId').value;
        if (!resumeId) {
            this.showWarning('无法获取简历ID');
            event.target.value = '';
            return;
        }

        const category = document.getElementById('resumeAttachmentCategory').value;
        const description = document.getElementById('resumeAttachmentDescription').value;

        // 遍历所有选中的文件并上传
        for (let file of files) {
            // 检查文件大小
            if (file.size > 10 * 1024 * 1024) {
                this.showWarning(`文件 "${file.name}" 超过10MB，跳过上传`);
                continue;
            }

            await this.uploadAttachment(resumeId, file, category, description);
        }

        // 清空文件输入和说明
        event.target.value = '';
        document.getElementById('resumeAttachmentDescription').value = '';

        // 重新加载附件列表
        await this.loadResumeAttachments(resumeId);
    }

    /**
     * 上传单个附件
     */
    async uploadAttachment(resumeId, file, category, description) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('resume_id', resumeId);
            formData.append('attachment_category', category);
            formData.append('attachment_description', description || '');

            const response = await fetch('/api/resume_library/upload-attachment', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess(`附件 "${file.name}" 上传成功`);
            } else {
                throw new Error(result.error || '上传失败');
            }
        } catch (error) {
            console.error('上传附件失败:', error);
            this.showError(`上传附件 "${file.name}" 失败: ${error.message}`);
        }
    }

    /**
     * 删除附件
     */
    async deleteAttachment(attachmentId) {
        if (!confirm('确定要删除这个附件吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/resume_library/attachment/${attachmentId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess('附件删除成功');

                // 重新加载附件列表
                const resumeId = document.getElementById('resumeId').value;
                if (resumeId) {
                    await this.loadResumeAttachments(resumeId);
                }
            } else {
                throw new Error(result.error || '删除失败');
            }
        } catch (error) {
            console.error('删除附件失败:', error);
            this.showError('删除附件失败: ' + error.message);
        }
    }

    /**
     * 下载附件
     */
    downloadAttachment(attachmentId) {
        // 构建下载URL（需要根据实际API调整）
        const downloadUrl = `/api/resume_library/attachment/${attachmentId}/download`;
        window.location.href = downloadUrl;
    }

    /**
     * 获取附件类别标签
     */
    getAttachmentCategoryLabel(category) {
        const labels = {
            'resume': '简历文件',
            'id_card': '身份证',
            'education': '学历证书',
            'degree': '学位证书',
            'qualification': '资质证书',
            'award': '获奖证书',
            'other': '其他'
        };
        return labels[category] || '其他';
    }

    /**
     * 获取文件图标
     */
    getFileIcon(filePath) {
        if (!filePath) return 'bi-file-earmark';

        const ext = filePath.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
            return 'bi-file-image';
        } else if (ext === 'pdf') {
            return 'bi-file-pdf';
        } else if (['doc', 'docx'].includes(ext)) {
            return 'bi-file-word';
        } else {
            return 'bi-file-earmark';
        }
    }
}

// 创建全局实例
window.resumeLibraryManager = new ResumeLibraryManager();