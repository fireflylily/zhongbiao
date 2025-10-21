/**
 * 案例库管理器
 * 用于知识库页面中的案例库功能模块
 */

class CaseLibraryManager {
    constructor() {
        this.allCases = [];
        this.companies = [];
        this.products = [];
        this.currentFilters = {
            companyId: null,
            productId: null,
            industry: null,
            contractType: null,
            status: null,
            searchKeyword: ''
        };
    }

    /**
     * 初始化案例库管理器
     */
    async initialize() {
        console.log('案例库管理器初始化...');
        await this.loadCompanies();
    }

    /**
     * 渲染案例库主界面
     */
    async renderCaseLibraryView() {
        console.log('渲染案例库视图...');

        const container = document.getElementById('caseLibraryContainer');
        if (!container) {
            console.error('未找到案例库容器');
            return;
        }

        // 清空容器
        container.innerHTML = '';

        // 渲染案例库界面
        const html = `
            <!-- 顶部操作栏 + 统计 -->
            <div class="case-library-header">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center gap-3">
                        <h4 class="mb-0">
                            <i class="bi bi-folder-open me-2"></i>案例库管理
                        </h4>
                        <span class="badge bg-primary" style="font-size: 0.9rem; padding: 8px 16px;">
                            总案例数：<strong id="caseTotalCount">0</strong>
                        </span>
                    </div>
                    <div>
                        <button type="button" class="btn btn-secondary me-2" onclick="window.caseLibraryManager.showImportFromDocumentModal()">
                            <i class="bi bi-file-earmark-arrow-up me-1"></i>从文档导入
                        </button>
                        <button type="button" class="btn btn-primary" onclick="window.caseLibraryManager.renderCaseEditView()">
                            <i class="bi bi-plus-circle me-1"></i>新建案例
                        </button>
                    </div>
                </div>
            </div>

            <!-- 筛选器区域（水平布局） -->
            <div class="case-filters-horizontal">
                <div class="row g-2 align-items-end">
                    <div class="col-lg-3 col-md-4">
                        <label class="form-label small text-muted mb-1">搜索</label>
                        <input type="text" class="form-control" id="caseSearchInput"
                               placeholder="搜索案例标题、客户..."
                               onkeyup="window.caseLibraryManager.handleSearch()">
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">公司</label>
                        <select class="form-select" id="caseFilterCompany"
                                onchange="window.caseLibraryManager.handleFilterChange()">
                            <option value="">全部公司</option>
                        </select>
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">产品</label>
                        <select class="form-select" id="caseFilterProduct"
                                onchange="window.caseLibraryManager.handleFilterChange()">
                            <option value="">全部产品</option>
                        </select>
                    </div>
                    <div class="col-lg-1 col-md-2">
                        <label class="form-label small text-muted mb-1">行业</label>
                        <select class="form-select" id="caseFilterIndustry"
                                onchange="window.caseLibraryManager.handleFilterChange()">
                            <option value="">全部</option>
                            <option value="政府">政府</option>
                            <option value="教育">教育</option>
                            <option value="医疗">医疗</option>
                            <option value="金融">金融</option>
                            <option value="能源">能源</option>
                            <option value="交通">交通</option>
                            <option value="制造业">制造</option>
                            <option value="其他">其他</option>
                        </select>
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">合同类型</label>
                        <select class="form-select" id="caseFilterContractType"
                                onchange="window.caseLibraryManager.handleFilterChange()">
                            <option value="">全部类型</option>
                            <option value="合同">合同</option>
                            <option value="订单">订单</option>
                        </select>
                    </div>
                    <div class="col-lg-1 col-md-2">
                        <label class="form-label small text-muted mb-1">状态</label>
                        <select class="form-select" id="caseFilterStatus"
                                onchange="window.caseLibraryManager.handleFilterChange()">
                            <option value="">全部</option>
                            <option value="success">成功</option>
                            <option value="进行中">进行中</option>
                            <option value="待验收">待验收</option>
                        </select>
                    </div>
                    <div class="col-lg-1 col-md-3">
                        <button class="btn btn-secondary w-100" onclick="window.caseLibraryManager.resetFilters()" title="重置筛选">
                            <i class="bi bi-arrow-counterclockwise"></i>
                        </button>
                    </div>
                </div>
            </div>

            <!-- 案例列表（全宽显示） -->
            <div class="case-list-full-width">
                <div id="caseListContainer">
                    <!-- 案例列表将动态渲染在这里 -->
                </div>

                <!-- 空状态 -->
                <div id="caseEmptyState" class="case-empty-state" style="display: none;">
                    <i class="bi bi-folder-x"></i>
                    <h5>暂无案例</h5>
                    <p class="text-muted">点击右上角"新建案例"按钮创建第一个案例</p>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // 加载数据
        await this.loadCompanyFilters();
        await this.loadCases();
        await this.loadStatistics();
    }

    /**
     * 渲染案例编辑视图（新建或编辑）
     */
    async renderCaseEditView(caseId = null) {
        console.log('渲染案例编辑视图...', caseId);

        const container = document.getElementById('caseLibraryContainer');
        if (!container) {
            console.error('未找到案例库容器');
            return;
        }

        const isEdit = !!caseId;
        const pageTitle = isEdit ? '编辑案例' : '新建案例';

        // 渲染编辑视图（简化结构，减少嵌套）
        const html = `
            <!-- 顶部操作栏 -->
            <div class="case-edit-header">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <button type="button" class="btn btn-outline-secondary me-3" onclick="window.caseLibraryManager.showCaseListView()">
                            <i class="bi bi-arrow-left me-1"></i>返回列表
                        </button>
                        <h4 class="mb-0">${pageTitle}</h4>
                    </div>
                    <div>
                        <button type="button" class="btn btn-secondary me-2" onclick="window.caseLibraryManager.showCaseListView()">取消</button>
                        <button type="button" class="btn btn-primary" onclick="window.caseLibraryManager.saveCase()">
                            <i class="bi bi-save me-1"></i>保存案例
                        </button>
                    </div>
                </div>
            </div>

            <!-- 表单内容（扁平化结构，无需form标签包装） -->
            <div class="case-edit-content">
                <input type="hidden" id="caseId" value="${caseId || ''}">

                <!-- 基本信息 -->
                <div class="case-form-section">
                    <h6>基本信息</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">所属公司 <span class="text-danger">*</span></label>
                            <select class="form-select" id="caseCompanyId" required>
                                <option value="">请选择公司</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">关联产品</label>
                            <select class="form-select" id="caseProductId">
                                <option value="">请选择产品（可选）</option>
                            </select>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <label class="form-label">合同名称/案例标题 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="caseTitle" required placeholder="案例名称即合同名称">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">合同编号/案例编号</label>
                            <input type="text" class="form-control" id="caseNumber">
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <label class="form-label">甲方客户名称 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="caseCustomerName" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">所属行业</label>
                            <select class="form-select" id="caseIndustry">
                                <option value="">请选择</option>
                                <option value="政府">政府</option>
                                <option value="教育">教育</option>
                                <option value="医疗">医疗</option>
                                <option value="金融">金融</option>
                                <option value="能源">能源</option>
                                <option value="交通">交通</option>
                                <option value="制造业">制造业</option>
                                <option value="其他">其他</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- 合同信息 -->
                <div class="case-form-section">
                    <h6>合同信息</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">合同类型 <span class="text-danger">*</span></label>
                            <select class="form-select" id="caseContractType"
                                    onchange="window.caseLibraryManager.toggleFinalCustomerField()" required>
                                <option value="">请选择</option>
                                <option value="合同">合同</option>
                                <option value="订单">订单</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">合同金额</label>
                            <input type="text" class="form-control" id="caseContractAmount" placeholder="如: 100万元 或 百万级 或 500">
                            <small class="text-muted">可填写具体金额（万元）或描述性文字（如"百万级"）</small>
                        </div>
                    </div>
                    <div class="row mt-3" id="caseFinalCustomerRow" style="display: none;">
                        <div class="col-md-12">
                            <label class="form-label">最终客户名称</label>
                            <input type="text" class="form-control" id="caseFinalCustomerName">
                            <small class="text-muted">仅订单类型时填写</small>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <label class="form-label">合同开始日期</label>
                            <input type="date" class="form-control" id="caseContractStartDate">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">合同结束日期</label>
                            <input type="date" class="form-control" id="caseContractEndDate">
                        </div>
                    </div>
                </div>

                <!-- 甲方客户信息（详细信息） -->
                <div class="case-form-section">
                    <h6>甲方客户详细信息</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">联系人姓名</label>
                            <input type="text" class="form-control" id="casePartyAContactName">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">联系电话</label>
                            <input type="tel" class="form-control" id="casePartyAContactPhone">
                        </div>
                    </div>
                </div>

                <!-- 乙方公司信息（详细信息） -->
                <div class="case-form-section">
                    <h6>乙方公司详细信息</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">联系人姓名</label>
                            <input type="text" class="form-control" id="casePartyBContactName">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">联系电话</label>
                            <input type="tel" class="form-control" id="casePartyBContactPhone">
                        </div>
                    </div>
                </div>

                <!-- 附件管理 -->
                <div class="case-form-section" id="caseAttachmentsSection">
                    <h6>
                        <i class="bi bi-paperclip me-2"></i>案例附件
                        <span class="badge bg-secondary ms-2" id="caseAttachmentCount">0</span>
                    </h6>

                    ${!isEdit ? `
                    <!-- 新建模式提示 -->
                    <div class="alert alert-info d-flex align-items-center" id="caseAttachmentNewTip">
                        <i class="bi bi-info-circle me-2"></i>
                        <span>请先保存案例基本信息后，再上传附件</span>
                    </div>
                    ` : ''}

                    <!-- 上传区域 -->
                    <div class="case-attachment-upload-area" id="caseAttachmentUploadArea" ${!isEdit ? 'style="display: none;"' : ''}>
                        <div class="upload-box">
                            <input type="file" id="caseAttachmentInput" multiple
                                   accept="image/*,.pdf,.doc,.docx" style="display: none;"
                                   onchange="window.caseLibraryManager.handleAttachmentSelect(event)">
                            <div class="upload-prompt" onclick="document.getElementById('caseAttachmentInput').click()">
                                <i class="bi bi-cloud-upload text-primary" style="font-size: 2rem;"></i>
                                <p class="mt-2 mb-1">点击或拖拽文件到这里上传</p>
                                <small class="text-muted">支持图片、PDF、Word文档，单个文件不超过10MB</small>
                            </div>
                        </div>
                    </div>

                    <!-- 附件类型选择 -->
                    <div class="row mt-3" id="caseAttachmentTypeRow" ${!isEdit ? 'style="display: none;"' : ''}>
                        <div class="col-md-6">
                            <label class="form-label">附件类型</label>
                            <select class="form-select" id="caseAttachmentType">
                                <option value="contract_order">合同/订单</option>
                                <option value="invoice">发票</option>
                                <option value="statement">对账单</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">附件说明</label>
                            <input type="text" class="form-control" id="caseAttachmentDescription"
                                   placeholder="选填，简要说明附件内容">
                        </div>
                    </div>

                    <!-- 附件列表 -->
                    <div class="case-attachment-list mt-3" id="caseAttachmentList" ${!isEdit ? 'style="display: none;"' : ''}>
                        <!-- 附件列表将动态渲染在这里 -->
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // 加载公司和产品选项
        await this.loadCompanyProductSelectOptions();

        // 如果是编辑模式，加载案例数据
        if (isEdit) {
            await this.loadCaseDataForEdit(caseId);
        }
    }

    /**
     * 切换回列表视图
     */
    async showCaseListView() {
        await this.renderCaseLibraryView();
    }

    /**
     * 加载公司列表
     */
    async loadCompanies() {
        try {
            const response = await axios.get('/api/companies');
            if (response.data.success) {
                this.companies = response.data.data;
            }
        } catch (error) {
            console.error('加载公司列表失败:', error);
        }
    }

    /**
     * 加载公司筛选器
     */
    async loadCompanyFilters() {
        const filterSelect = document.getElementById('caseFilterCompany');
        if (!filterSelect || this.companies.length === 0) return;

        let options = '<option value="">全部公司</option>';
        this.companies.forEach(company => {
            options += `<option value="${company.company_id}">${company.company_name}</option>`;
        });
        filterSelect.innerHTML = options;
    }

    /**
     * 加载案例列表
     */
    async loadCases() {
        console.log('[DEBUG] 开始加载案例列表...');
        try {
            // 构建查询参数
            const params = new URLSearchParams();
            if (this.currentFilters.companyId) {
                params.append('company_id', this.currentFilters.companyId);
            }
            if (this.currentFilters.productId) {
                params.append('product_id', this.currentFilters.productId);
            }
            if (this.currentFilters.industry) {
                params.append('industry', this.currentFilters.industry);
            }
            if (this.currentFilters.contractType) {
                params.append('contract_type', this.currentFilters.contractType);
            }
            if (this.currentFilters.status) {
                params.append('status', this.currentFilters.status);
            }

            const url = `/api/case_library/cases?${params.toString()}`;
            console.log('[DEBUG] API URL:', url);
            const response = await axios.get(url);
            console.log('[DEBUG] API响应:', response.data);

            if (response.data.success) {
                this.allCases = response.data.data || [];
                console.log('[DEBUG] 加载了', this.allCases.length, '个案例');
                this.renderCaseList(this.allCases);
            } else {
                throw new Error(response.data.error || '加载失败');
            }
        } catch (error) {
            console.error('[DEBUG] 加载案例列表失败:', error);
            showAlert('加载案例列表失败: ' + error.message, 'danger');
            this.renderCaseList([]);
        }
    }

    /**
     * 渲染案例列表
     */
    renderCaseList(cases) {
        console.log('[DEBUG] 开始渲染案例列表, 案例数:', cases.length);
        const container = document.getElementById('caseListContainer');
        const emptyState = document.getElementById('caseEmptyState');
        console.log('[DEBUG] 容器元素:', container);

        if (!container) {
            console.error('[DEBUG] 未找到caseListContainer元素!');
            return;
        }

        // 应用搜索关键词过滤
        let filteredCases = cases;
        if (this.currentFilters.searchKeyword) {
            const keyword = this.currentFilters.searchKeyword.toLowerCase();
            filteredCases = cases.filter(c =>
                (c.case_title && c.case_title.toLowerCase().includes(keyword)) ||
                (c.customer_name && c.customer_name.toLowerCase().includes(keyword)) ||
                (c.contract_name && c.contract_name.toLowerCase().includes(keyword)) ||
                (c.case_number && c.case_number.toLowerCase().includes(keyword))
            );
        }

        // 显示空状态或案例列表
        if (filteredCases.length === 0) {
            container.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        container.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';

        // 渲染案例卡片
        const html = filteredCases.map(caseItem => this.renderCaseCard(caseItem)).join('');
        container.innerHTML = html;

        // 更新统计数字
        const countElement = document.getElementById('caseTotalCount');
        if (countElement) {
            countElement.textContent = filteredCases.length;
        }
    }

    /**
     * 渲染单个案例卡片
     */
    renderCaseCard(caseItem) {
        const statusClass = caseItem.case_status === 'success' ? 'case-status-success' :
                           caseItem.case_status === '进行中' ? 'case-status-progress' : 'case-status-pending';
        const statusIcon = caseItem.case_status === 'success' ? '✅' :
                          caseItem.case_status === '进行中' ? '🔄' : '⏳';
        const statusText = caseItem.case_status === 'success' ? '成功' :
                          caseItem.case_status === '进行中' ? '进行中' : '待验收';

        return `
            <div class="case-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h5>${this.escapeHtml(caseItem.case_title)}</h5>
                        <div class="case-meta">
                            <i class="bi bi-building"></i>客户: ${this.escapeHtml(caseItem.customer_name)}
                            ${caseItem.industry ? `<span class="ms-2"><i class="bi bi-tag"></i>${this.escapeHtml(caseItem.industry)}</span>` : ''}
                            ${caseItem.contract_type ? `<span class="ms-2"><i class="bi bi-file-text"></i>${this.escapeHtml(caseItem.contract_type)}</span>` : ''}
                        </div>
                        ${caseItem.party_b_company_name ? `
                        <div class="case-meta">
                            <i class="bi bi-building"></i>乙方: ${this.escapeHtml(caseItem.party_b_company_name)}
                        </div>
                        ` : ''}
                        ${caseItem.contract_amount || caseItem.contract_start_date ? `
                        <div class="case-meta">
                            ${caseItem.contract_amount ? `<i class="bi bi-cash"></i>金额: ${caseItem.contract_amount}万元` : ''}
                            ${caseItem.contract_start_date ? `<span class="ms-2"><i class="bi bi-calendar"></i>${caseItem.contract_start_date}${caseItem.contract_end_date ? ' ~ ' + caseItem.contract_end_date : ''}</span>` : ''}
                        </div>
                        ` : ''}
                        <div class="case-meta mt-2">
                            <span class="case-status-badge ${statusClass}">${statusIcon} ${statusText}</span>
                            <span class="ms-2 text-muted">
                                <i class="bi bi-paperclip"></i>${caseItem.attachment_count || 0}个附件
                            </span>
                        </div>
                    </div>
                    <div class="case-actions">
                        <button type="button" class="btn btn-sm btn-info" onclick="window.caseLibraryManager.viewCaseDetail(${caseItem.case_id})" title="查看详情">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-primary" onclick="window.caseLibraryManager.editCase(${caseItem.case_id})" title="编辑">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-danger" onclick="window.caseLibraryManager.deleteCase(${caseItem.case_id})" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 加载统计信息
     */
    async loadStatistics() {
        try {
            const response = await axios.get('/api/case_library/statistics');
            if (response.data.success) {
                const countElement = document.getElementById('caseTotalCount');
                if (countElement) {
                    countElement.textContent = response.data.data.total_cases || 0;
                }
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }

    /**
     * 显示创建案例模态框
     */
    async showCreateCaseModal() {
        const modal = document.getElementById('caseModal');
        if (!modal) {
            console.error('未找到案例模态框');
            return;
        }

        // 重置表单
        const form = document.getElementById('caseForm');
        if (form) form.reset();

        // 设置标题
        const title = document.getElementById('caseModalTitle');
        if (title) title.textContent = '新建案例';

        // 清空case_id
        const caseIdInput = document.getElementById('caseId');
        if (caseIdInput) caseIdInput.value = '';

        // 隐藏最终客户字段
        const finalCustomerRow = document.getElementById('caseFinalCustomerRow');
        if (finalCustomerRow) finalCustomerRow.style.display = 'none';

        // 隐藏附件区域（新建时不显示）
        const attachmentsSection = document.getElementById('caseAttachmentsSection');
        if (attachmentsSection) attachmentsSection.style.display = 'none';

        // 加载公司和产品下拉列表
        await this.loadCompanyProductSelectOptions();

        // 显示模态框
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    /**
     * 加载公司和产品下拉选项
     */
    async loadCompanyProductSelectOptions() {
        // 加载公司列表
        const companySelect = document.getElementById('caseCompanyId');
        if (companySelect && this.companies.length > 0) {
            let options = '<option value="">请选择公司</option>';
            this.companies.forEach(company => {
                options += `<option value="${company.company_id}">${this.escapeHtml(company.company_name)}</option>`;
            });
            companySelect.innerHTML = options;
        }

        // 加载产品列表（所有公司的产品）
        try {
            const response = await axios.get('/api/products');
            if (response.data.success) {
                const products = response.data.data || [];
                const productSelect = document.getElementById('caseProductId');
                if (productSelect) {
                    let options = '<option value="">请选择产品（可选）</option>';
                    products.forEach(product => {
                        options += `<option value="${product.product_id}">${this.escapeHtml(product.product_name)}</option>`;
                    });
                    productSelect.innerHTML = options;
                }
            }
        } catch (error) {
            console.error('加载产品列表失败:', error);
        }
    }

    /**
     * 查看案例详情
     */
    async viewCaseDetail(caseId) {
        try {
            const response = await axios.get(`/api/case_library/cases/${caseId}`);
            if (!response.data.success) {
                throw new Error(response.data.error || '获取案例详情失败');
            }

            const c = response.data.data;
            let content = `
                <div class="case-detail-section">
                    <h6>基本信息</h6>
                    <p><strong>案例标题:</strong> ${this.escapeHtml(c.case_title)}</p>
                    <p><strong>案例编号:</strong> ${c.case_number || '无'}</p>
                    <p><strong>客户名称:</strong> ${this.escapeHtml(c.customer_name)}</p>
                    <p><strong>所属行业:</strong> ${c.industry || '无'}</p>
                </div>
                <div class="case-detail-section">
                    <h6>合同信息</h6>
                    <p><strong>合同名称:</strong> ${c.contract_name || '无'}</p>
                    <p><strong>合同类型:</strong> ${c.contract_type || '无'}</p>
                    ${c.final_customer_name ? `<p><strong>最终客户:</strong> ${this.escapeHtml(c.final_customer_name)}</p>` : ''}
                    <p><strong>合同金额:</strong> ${c.contract_amount ? c.contract_amount + '万元' : '无'}</p>
                    <p><strong>合同期限:</strong> ${c.contract_start_date || ''} ${c.contract_end_date ? '~ ' + c.contract_end_date : ''}</p>
                    ${c.party_a_customer_name ? `<p><strong>甲方客户名称:</strong> ${this.escapeHtml(c.party_a_customer_name)}</p>` : ''}
                    ${c.party_b_company_name ? `<p><strong>乙方公司名称:</strong> ${this.escapeHtml(c.party_b_company_name)}</p>` : ''}
                </div>
                ${c.party_a_name || c.party_a_contact_name ? `
                <div class="case-detail-section">
                    <h6>甲方信息</h6>
                    ${c.party_a_name ? `<p><strong>甲方名称:</strong> ${this.escapeHtml(c.party_a_name)}</p>` : ''}
                    ${c.party_a_contact_name ? `<p><strong>联系人:</strong> ${this.escapeHtml(c.party_a_contact_name)}</p>` : ''}
                    ${c.party_a_contact_phone ? `<p><strong>电话:</strong> ${this.escapeHtml(c.party_a_contact_phone)}</p>` : ''}
                </div>
                ` : ''}
                ${c.party_b_name || c.party_b_contact_name ? `
                <div class="case-detail-section">
                    <h6>乙方信息</h6>
                    ${c.party_b_name ? `<p><strong>乙方名称:</strong> ${this.escapeHtml(c.party_b_name)}</p>` : ''}
                    ${c.party_b_contact_name ? `<p><strong>联系人:</strong> ${this.escapeHtml(c.party_b_contact_name)}</p>` : ''}
                    ${c.party_b_contact_phone ? `<p><strong>电话:</strong> ${this.escapeHtml(c.party_b_contact_phone)}</p>` : ''}
                </div>
                ` : ''}
                <div class="case-detail-section">
                    <h6>其他信息</h6>
                    <p><strong>案例状态:</strong> ${c.case_status}</p>
                    <p><strong>创建时间:</strong> ${c.created_at || '无'}</p>
                    <p><strong>更新时间:</strong> ${c.updated_at || '无'}</p>
                </div>
            `;

            // 如果有附件，添加附件区域
            if (c.attachments && c.attachments.length > 0) {
                content += `
                    <div class="case-detail-section">
                        <h6><i class="bi bi-paperclip me-2"></i>附件列表 (${c.attachments.length})</h6>
                        <div class="list-group">
                            ${c.attachments.map(att => {
                                const typeLabel = this.getAttachmentTypeLabel(att.attachment_type);
                                const fileIcon = this.getFileIcon(att.file_type);
                                const sizeText = att.file_size_mb ? `${att.file_size_mb}MB` : '未知';
                                const fileType = att.file_type?.toLowerCase();
                                const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(fileType);
                                const isDoc = ['doc', 'docx'].includes(fileType);
                                const isPdf = fileType === 'pdf';
                                const canPreview = isImage || isDoc || isPdf;
                                return `
                                    <div class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="bi ${fileIcon} me-2"></i>
                                            ${this.escapeHtml(att.original_filename)}
                                            <span class="badge bg-info ms-2">${typeLabel}</span>
                                            <small class="text-muted ms-2">${sizeText}</small>
                                            ${att.attachment_description ? `<div class="text-muted small mt-1">${this.escapeHtml(att.attachment_description)}</div>` : ''}
                                        </div>
                                        <div class="btn-group">
                                            ${canPreview ? `<button type="button" class="btn btn-sm btn-outline-primary" onclick="window.caseLibraryManager.previewAttachment(${att.attachment_id}, '${att.file_path}', '${fileType}')" title="预览">
                                                <i class="bi bi-eye"></i> 预览
                                            </button>` : ''}
                                            <button type="button" class="btn btn-sm btn-outline-secondary" onclick="window.caseLibraryManager.downloadAttachment(${att.attachment_id}, '${att.file_path}', '${this.escapeHtml(att.original_filename)}')" title="下载">
                                                <i class="bi bi-download"></i>
                                            </button>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            }

            const detailContent = document.getElementById('caseDetailContent');
            if (detailContent) {
                detailContent.innerHTML = content;
            }

            const detailModal = document.getElementById('caseDetailModal');
            if (detailModal) {
                const bsModal = new bootstrap.Modal(detailModal);
                bsModal.show();
            }
        } catch (error) {
            console.error('查看案例详情失败:', error);
            showAlert('查看案例详情失败: ' + error.message, 'danger');
        }
    }

    /**
     * 编辑案例
     */
    /**
     * 编辑案例 - 切换到编辑视图
     */
    async editCase(caseId) {
        await this.renderCaseEditView(caseId);
    }

    /**
     * 加载案例数据用于编辑
     */
    async loadCaseDataForEdit(caseId) {
        try {
            const response = await axios.get(`/api/case_library/cases/${caseId}`);
            if (!response.data.success) {
                throw new Error(response.data.error || '获取案例信息失败');
            }

            const c = response.data.data;

            // 填充表单
            document.getElementById('caseId').value = c.case_id;
            document.getElementById('caseCompanyId').value = c.company_id || '';
            document.getElementById('caseProductId').value = c.product_id || '';
            document.getElementById('caseTitle').value = c.case_title || '';
            document.getElementById('caseNumber').value = c.case_number || '';
            document.getElementById('caseCustomerName').value = c.customer_name || '';
            document.getElementById('caseIndustry').value = c.industry || '';
            document.getElementById('caseContractType').value = c.contract_type || '';
            document.getElementById('caseFinalCustomerName').value = c.final_customer_name || '';
            document.getElementById('caseContractAmount').value = c.contract_amount || '';
            document.getElementById('caseContractStartDate').value = c.contract_start_date || '';
            document.getElementById('caseContractEndDate').value = c.contract_end_date || '';
            document.getElementById('casePartyAContactName').value = c.party_a_contact_name || '';
            document.getElementById('casePartyAContactPhone').value = c.party_a_contact_phone || '';
            document.getElementById('casePartyBContactName').value = c.party_b_contact_name || '';
            document.getElementById('casePartyBContactPhone').value = c.party_b_contact_phone || '';
            document.getElementById('caseStatus').value = c.case_status || 'success';

            // 触发合同类型变更以显示/隐藏最终客户字段
            this.toggleFinalCustomerField();

            // 加载附件
            await this.loadCaseAttachments(caseId);

        } catch (error) {
            console.error('加载案例数据失败:', error);
            showAlert('加载案例数据失败: ' + error.message, 'danger');
        }
    }

    /**
     * 保存案例（创建或更新）
     */
    async saveCase() {
        // 防止重复提交
        if (this._saving) {
            console.log('正在保存中，忽略重复点击');
            return;
        }

        const caseId = document.getElementById('caseId').value;
        const companyId = document.getElementById('caseCompanyId').value;

        if (!companyId) {
            showAlert('请选择公司', 'warning');
            return;
        }

        // 获取基本字段
        const caseTitle = document.getElementById('caseTitle').value;
        const customerName = document.getElementById('caseCustomerName').value;
        const contractType = document.getElementById('caseContractType').value;

        // 前端验证必填字段
        if (!caseTitle || !caseTitle.trim()) {
            showAlert('请填写合同名称/案例标题', 'warning');
            document.getElementById('caseTitle').focus();
            return;
        }

        if (!customerName || !customerName.trim()) {
            showAlert('请填写甲方客户名称', 'warning');
            document.getElementById('caseCustomerName').focus();
            return;
        }

        if (!contractType) {
            showAlert('请选择合同类型', 'warning');
            document.getElementById('caseContractType').focus();
            return;
        }

        const data = {
            company_id: parseInt(companyId),
            product_id: document.getElementById('caseProductId').value ? parseInt(document.getElementById('caseProductId').value) : null,
            case_title: caseTitle,  // 案例标题（即合同名称）
            case_number: document.getElementById('caseNumber').value,
            customer_name: customerName,  // 客户名称（即甲方名称）
            industry: document.getElementById('caseIndustry').value,
            contract_name: caseTitle,  // 合同名称 = 案例标题
            contract_type: document.getElementById('caseContractType').value,
            final_customer_name: document.getElementById('caseFinalCustomerName').value,
            contract_amount: document.getElementById('caseContractAmount').value,  // 支持文字描述或数字
            contract_start_date: document.getElementById('caseContractStartDate').value,
            contract_end_date: document.getElementById('caseContractEndDate').value,
            party_a_customer_name: customerName,  // 甲方客户名称 = 客户名称
            party_b_company_name: '',  // 乙方公司名称（可从所属公司获取）
            party_a_name: customerName,  // 甲方名称 = 客户名称
            party_a_address: '',  // 地址字段已移除
            party_a_contact_name: document.getElementById('casePartyAContactName').value,
            party_a_contact_phone: document.getElementById('casePartyAContactPhone').value,
            party_a_contact_email: '',  // 邮箱字段已移除
            party_b_name: '',  // 乙方名称（可从所属公司获取）
            party_b_address: '',  // 地址字段已移除
            party_b_contact_name: document.getElementById('casePartyBContactName').value,
            party_b_contact_phone: document.getElementById('casePartyBContactPhone').value,
            party_b_contact_email: '',  // 邮箱字段已移除
            case_status: document.getElementById('caseStatus').value
        };

        try {
            // 设置保存中标志，禁用按钮
            this._saving = true;
            const saveBtn = document.querySelector('button[onclick*="saveCase"]');
            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>保存中...';
            }

            const url = caseId ? `/api/case_library/cases/${caseId}` : '/api/case_library/cases';
            const method = caseId ? 'put' : 'post';

            const response = await axios[method](url, data);

            if (response.data.success) {
                const savedCaseId = response.data.data?.case_id || caseId;

                if (!caseId) {
                    // 新建模式：保存成功后切换到编辑模式以便上传附件
                    showAlert('案例保存成功！现在可以上传附件了', 'success');
                    await this.renderCaseEditView(savedCaseId);
                } else {
                    // 编辑模式：保存成功后返回列表
                    showAlert(response.data.message || '保存成功', 'success');
                    await this.showCaseListView();
                }

                await this.loadStatistics();
            } else {
                throw new Error(response.data.error || '保存失败');
            }
        } catch (error) {
            console.error('保存案例失败:', error);
            // 尝试从axios错误响应中获取详细错误信息
            let errorMessage = '保存失败';
            if (error.response && error.response.data && error.response.data.error) {
                errorMessage = error.response.data.error;
            } else if (error.message) {
                errorMessage = error.message;
            }
            showAlert('保存失败：' + errorMessage, 'danger');
        } finally {
            // 无论成功或失败，都要重置保存状态
            this._saving = false;
            const saveBtn = document.querySelector('button[onclick*="saveCase"]');
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="bi bi-save me-1"></i>保存案例';
            }
        }
    }

    /**
     * 删除案例
     */
    async deleteCase(caseId) {
        if (!confirm('确定要删除这个案例吗？此操作不可恢复。')) {
            return;
        }

        try {
            const response = await axios.delete(`/api/case_library/cases/${caseId}`);

            if (response.data.success) {
                showAlert(response.data.message || '删除成功', 'success');
                await this.loadCases();
                await this.loadStatistics();
            } else {
                throw new Error(response.data.error || '删除失败');
            }
        } catch (error) {
            console.error('删除案例失败:', error);
            showAlert('删除案例失败: ' + error.message, 'danger');
        }
    }

    /**
     * 处理筛选器变更
     */
    handleFilterChange() {
        this.currentFilters.companyId = document.getElementById('caseFilterCompany').value || null;
        this.currentFilters.productId = document.getElementById('caseFilterProduct').value || null;
        this.currentFilters.industry = document.getElementById('caseFilterIndustry').value || null;
        this.currentFilters.contractType = document.getElementById('caseFilterContractType').value || null;
        this.currentFilters.status = document.getElementById('caseFilterStatus').value || null;

        this.loadCases();
    }

    /**
     * 处理搜索
     */
    handleSearch() {
        const searchInput = document.getElementById('caseSearchInput');
        if (searchInput) {
            this.currentFilters.searchKeyword = searchInput.value.trim();
            this.renderCaseList(this.allCases);
        }
    }

    /**
     * 重置筛选器
     */
    resetFilters() {
        document.getElementById('caseFilterCompany').value = '';
        document.getElementById('caseFilterProduct').value = '';
        document.getElementById('caseFilterIndustry').value = '';
        document.getElementById('caseFilterContractType').value = '';
        document.getElementById('caseFilterStatus').value = '';
        document.getElementById('caseSearchInput').value = '';

        this.currentFilters = {
            companyId: null,
            productId: null,
            industry: null,
            contractType: null,
            status: null,
            searchKeyword: ''
        };

        this.loadCases();
    }

    /**
     * 切换最终客户字段显示
     */
    toggleFinalCustomerField() {
        const contractType = document.getElementById('caseContractType').value;
        const finalCustomerRow = document.getElementById('caseFinalCustomerRow');

        if (finalCustomerRow) {
            finalCustomerRow.style.display = contractType === '订单' ? 'block' : 'none';
            if (contractType !== '订单') {
                document.getElementById('caseFinalCustomerName').value = '';
            }
        }
    }

    /**
     * HTML转义
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 显示文档导入模态框
     */
    showImportFromDocumentModal() {
        const modal = document.getElementById('caseDocumentImportModal');
        if (!modal) {
            console.error('未找到文档导入模态框');
            return;
        }

        // 重置文件输入
        const fileInput = document.getElementById('caseDocumentFile');
        if (fileInput) fileInput.value = '';

        // 隐藏进度提示
        const progressDiv = document.getElementById('extractionProgress');
        if (progressDiv) progressDiv.style.display = 'none';

        // 显示模态框
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    /**
     * 处理文档导入
     */
    async handleDocumentImport() {
        const fileInput = document.getElementById('caseDocumentFile');
        const file = fileInput.files[0];

        if (!file) {
            showAlert('请选择文件', 'warning');
            return;
        }

        // 检查文件大小 (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            showAlert('文件大小不能超过10MB', 'warning');
            return;
        }

        // 检查文件类型
        const allowedTypes = ['.doc', '.docx', '.pdf'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExt)) {
            showAlert('仅支持 DOC、DOCX、PDF 格式', 'warning');
            return;
        }

        // 显示进度提示
        const progressDiv = document.getElementById('extractionProgress');
        const statusText = document.getElementById('extractionStatusText');
        const startBtn = document.getElementById('startExtractionBtn');

        if (progressDiv) progressDiv.style.display = 'block';
        if (statusText) statusText.textContent = '正在上传文档...';
        if (startBtn) startBtn.disabled = true;

        try {
            // 1. 上传文档
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await axios.post('/api/case_library/upload-case-document', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (!uploadResponse.data.success) {
                throw new Error(uploadResponse.data.error || '文档上传失败');
            }

            const filePath = uploadResponse.data.file_path;
            console.log('文档上传成功:', filePath);

            // 2. 提取案例信息
            if (statusText) statusText.textContent = '正在使用AI提取案例信息...（约30秒）';

            const extractResponse = await axios.post('/api/case_library/extract-from-document', {
                file_path: filePath
            });

            if (!extractResponse.data.success) {
                throw new Error(extractResponse.data.error || '信息提取失败');
            }

            const caseData = extractResponse.data.data;
            console.log('案例信息提取成功:', caseData);

            // 3. 关闭导入模态框
            const importModal = bootstrap.Modal.getInstance(document.getElementById('caseDocumentImportModal'));
            if (importModal) importModal.hide();

            // 4. 切换到新建案例页面并预填充数据
            await this.renderCaseEditView();  // 渲染新建案例表单
            this.prefillCaseForm(caseData);   // 预填充提取的数据

            showAlert('✨ 案例信息提取成功！请检查并完善信息', 'success');

        } catch (error) {
            console.error('文档导入失败:', error);
            showAlert('文档导入失败: ' + error.message, 'danger');
        } finally {
            if (progressDiv) progressDiv.style.display = 'none';
            if (startBtn) startBtn.disabled = false;
        }
    }

    /**
     * 预填充案例表单
     */
    prefillCaseForm(data) {
        console.log('[CaseLibrary] 开始预填充表单', data);

        // 基本信息
        if (data.case_title) document.getElementById('caseTitle').value = data.case_title;
        if (data.case_number) document.getElementById('caseNumber').value = data.case_number;
        if (data.customer_name) document.getElementById('caseCustomerName').value = data.customer_name;
        if (data.industry) document.getElementById('caseIndustry').value = data.industry;

        // 合同信息
        // contract_name字段已移除，合同名称=案例标题
        if (data.contract_type) {
            document.getElementById('caseContractType').value = data.contract_type;
            this.toggleFinalCustomerField();  // 触发显示/隐藏最终客户字段
        }
        if (data.final_customer_name) document.getElementById('caseFinalCustomerName').value = data.final_customer_name;
        if (data.contract_amount) document.getElementById('caseContractAmount').value = data.contract_amount;
        if (data.contract_start_date) document.getElementById('caseContractStartDate').value = data.contract_start_date;
        if (data.contract_end_date) document.getElementById('caseContractEndDate').value = data.contract_end_date;
        // party_a_customer_name, party_b_company_name, party_a_name, party_b_name字段已移除

        // 甲方信息（地址和邮箱字段已移除）
        if (data.party_a_contact_name) document.getElementById('casePartyAContactName').value = data.party_a_contact_name;
        if (data.party_a_contact_phone) document.getElementById('casePartyAContactPhone').value = data.party_a_contact_phone;

        // 乙方信息（地址和邮箱字段已移除）
        if (data.party_b_contact_name) document.getElementById('casePartyBContactName').value = data.party_b_contact_name;
        if (data.party_b_contact_phone) document.getElementById('casePartyBContactPhone').value = data.party_b_contact_phone;

        // 其他
        if (data.case_status) document.getElementById('caseStatus').value = data.case_status;

        console.log('[CaseLibrary] 表单预填充完成');
    }

    // =========================
    // 附件管理相关方法
    // =========================

    /**
     * 加载案例附件列表
     */
    async loadCaseAttachments(caseId) {
        try {
            const response = await axios.get(`/api/case_library/cases/${caseId}/attachments`);
            if (response.data.success) {
                const attachments = response.data.data || [];
                this.renderAttachmentList(attachments);

                // 更新附件数量
                const countBadge = document.getElementById('caseAttachmentCount');
                if (countBadge) {
                    countBadge.textContent = attachments.length;
                }
            }
        } catch (error) {
            console.error('加载附件列表失败:', error);
            showAlert('加载附件列表失败: ' + error.message, 'danger');
        }
    }

    /**
     * 渲染附件列表
     */
    renderAttachmentList(attachments) {
        const container = document.getElementById('caseAttachmentList');
        if (!container) return;

        if (attachments.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-3">暂无附件</div>';
            return;
        }

        const html = attachments.map(att => {
            const typeLabel = this.getAttachmentTypeLabel(att.attachment_type);
            const fileIcon = this.getFileIcon(att.file_type);
            const sizeText = att.file_size_mb ? `${att.file_size_mb}MB` : '未知';
            const fileType = att.file_type?.toLowerCase();
            const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(fileType);
            const isDoc = ['doc', 'docx'].includes(fileType);
            const isPdf = fileType === 'pdf';
            const canPreview = isImage || isDoc || isPdf;

            return `
                <div class="case-attachment-item">
                    <div class="attachment-info">
                        <i class="bi ${fileIcon} me-2 text-primary"></i>
                        <div class="attachment-details">
                            <div class="attachment-name">${this.escapeHtml(att.original_filename)}</div>
                            <div class="attachment-meta">
                                <span class="badge bg-info">${typeLabel}</span>
                                <span class="text-muted ms-2">${sizeText}</span>
                                ${att.attachment_description ? `<span class="text-muted ms-2">· ${this.escapeHtml(att.attachment_description)}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="attachment-actions">
                        ${canPreview ? `<button type="button" class="btn btn-sm btn-outline-primary me-1" onclick="window.caseLibraryManager.previewAttachment(${att.attachment_id}, '${att.file_path}', '${fileType}')" title="预览">
                            <i class="bi bi-eye"></i> 预览
                        </button>` : ''}
                        <button type="button" class="btn btn-sm btn-outline-secondary me-1" onclick="window.caseLibraryManager.downloadAttachment(${att.attachment_id}, '${att.file_path}', '${this.escapeHtml(att.original_filename)}')" title="下载">
                            <i class="bi bi-download"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="window.caseLibraryManager.deleteAttachment(${att.attachment_id})" title="删除">
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

        const caseId = document.getElementById('caseId').value;
        if (!caseId) {
            showAlert('请先保存案例后再上传附件', 'warning');
            event.target.value = '';
            return;
        }

        const attachmentType = document.getElementById('caseAttachmentType').value;
        const description = document.getElementById('caseAttachmentDescription').value;

        // 遍历所有选中的文件并上传
        for (let file of files) {
            // 检查文件大小
            if (file.size > 10 * 1024 * 1024) {
                showAlert(`文件 "${file.name}" 超过10MB，跳过上传`, 'warning');
                continue;
            }

            await this.uploadAttachment(caseId, file, attachmentType, description);
        }

        // 清空文件输入
        event.target.value = '';

        // 清空说明
        document.getElementById('caseAttachmentDescription').value = '';

        // 重新加载附件列表
        await this.loadCaseAttachments(caseId);
    }

    /**
     * 上传单个附件
     */
    async uploadAttachment(caseId, file, attachmentType, description) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('attachment_type', attachmentType);
            formData.append('description', description);

            const response = await axios.post(
                `/api/case_library/cases/${caseId}/attachments`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            if (response.data.success) {
                showAlert(`附件 "${file.name}" 上传成功`, 'success');
            } else {
                throw new Error(response.data.error || '上传失败');
            }
        } catch (error) {
            console.error('上传附件失败:', error);
            showAlert(`上传附件 "${file.name}" 失败: ${error.message}`, 'danger');
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
            const response = await axios.delete(`/api/case_library/attachments/${attachmentId}`);

            if (response.data.success) {
                showAlert('附件删除成功', 'success');

                // 重新加载附件列表
                const caseId = document.getElementById('caseId').value;
                if (caseId) {
                    await this.loadCaseAttachments(caseId);
                }
            } else {
                throw new Error(response.data.error || '删除失败');
            }
        } catch (error) {
            console.error('删除附件失败:', error);
            showAlert('删除附件失败: ' + error.message, 'danger');
        }
    }

    /**
     * 下载附件
     */
    downloadAttachment(attachmentId, filePath, filename) {
        // 构建下载URL
        const downloadUrl = `/api/case_library/attachments/${attachmentId}/download`;

        // 创建临时链接并触发下载
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * 预览附件（支持图片、Word、PDF）- 使用通用预览工具
     */
    previewAttachment(attachmentId, filePath, fileType) {
        console.log('[CaseLibrary] 预览附件:', { attachmentId, filePath, fileType });

        // 检查通用预览工具是否已加载
        if (!window.documentPreviewUtil) {
            console.error('[CaseLibrary] DocumentPreviewUtil未加载');
            alert('文档预览功能未正确加载，请刷新页面重试');
            return;
        }

        // 使用下载API构建文件URL (确保可以访问到文件)
        const fileUrl = `/api/case_library/attachments/${attachmentId}/download`;
        const fileName = filePath.split('/').pop() || `attachment_${attachmentId}`;

        console.log('[CaseLibrary] 预览文件URL:', fileUrl);

        // 使用通用预览工具进行预览
        window.documentPreviewUtil.preview(fileUrl, fileName, fileType);
    }

    /**
     * 获取附件类型标签
     */
    getAttachmentTypeLabel(type) {
        const labels = {
            'contract_order': '合同/订单',
            'invoice': '发票',
            'statement': '对账单',
            // 兼容旧类型
            'contract': '合同文件',
            'acceptance': '验收证明',
            'testimony': '客户证明',
            'photo': '项目照片',
            'other': '其他'
        };
        return labels[type] || '其他';
    }

    /**
     * 获取文件图标
     */
    getFileIcon(fileType) {
        const type = fileType?.toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(type)) {
            return 'bi-file-image';
        } else if (type === 'pdf') {
            return 'bi-file-pdf';
        } else if (['doc', 'docx'].includes(type)) {
            return 'bi-file-word';
        } else {
            return 'bi-file-earmark';
        }
    }
}

// 创建全局实例
window.caseLibraryManager = new CaseLibraryManager();
