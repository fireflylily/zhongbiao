/**
 * 企业信息库管理模块
 * 负责企业基础信息、资质文件、人员档案、财务文档的管理
 */

class CompanyProfileManager {
    constructor() {
        this.currentCompanyId = null;
        this.currentTab = 'basic';
        this.allCompanies = [];
        this.currentFilters = {
            industry: null,
            searchKeyword: ''
        };

        // 支持多文件上传的资质类型配置
        this.multiFileQualifications = {
            'audit_report': {
                versionLabel: '年份',
                placeholder: '请输入年份（如：2023）',
                multiple: true
            },
            'software_copyright': {
                versionLabel: '软著名称',
                placeholder: '请输入软著名称',
                multiple: true
            },
            'patent_certificate': {
                versionLabel: '专利号',
                placeholder: '请输入专利号',
                multiple: true
            }
        };
    }

    /**
     * 初始化企业信息库管理器
     */
    init() {
        this.bindEvents();
    }

    /**
     * 设置当前企业ID
     * @param {number} companyId 企业ID
     */
    setCurrentCompanyId(companyId) {
        this.currentCompanyId = companyId;
    }

    /**
     * 渲染企业列表视图
     */
    async renderCompanyListView() {
        console.log('渲染企业列表视图...');

        const mainContent = document.getElementById('mainContent');
        if (!mainContent) {
            console.error('未找到主内容区域');
            return;
        }

        // 渲染列表界面
        const html = `
            <!-- 顶部操作栏 + 统计 -->
            <div class="case-library-header">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center gap-3">
                        <h4 class="mb-0">
                            <i class="bi bi-building me-2"></i>企业信息库管理
                        </h4>
                        <span class="badge bg-primary" style="font-size: 0.9rem; padding: 8px 16px;">
                            总企业数：<strong id="companyTotalCount">0</strong>
                        </span>
                    </div>
                    <div>
                        <button type="button" class="btn btn-primary" onclick="window.companyProfileManager.createNewCompany()">
                            <i class="bi bi-plus-circle me-1"></i>新建企业
                        </button>
                    </div>
                </div>
            </div>

            <!-- 筛选器区域 -->
            <div class="case-filters-horizontal">
                <div class="row g-2 align-items-end">
                    <div class="col-lg-4 col-md-6">
                        <label class="form-label small text-muted mb-1">搜索</label>
                        <input type="text" class="form-control" id="companySearchInput"
                               placeholder="搜索企业名称、统一社会信用代码..."
                               onkeyup="window.companyProfileManager.handleSearch()">
                    </div>
                    <div class="col-lg-3 col-md-4">
                        <label class="form-label small text-muted mb-1">行业类型</label>
                        <select class="form-select" id="companyFilterIndustry"
                                onchange="window.companyProfileManager.handleFilterChange()">
                            <option value="">全部行业</option>
                            <option value="technology">科技</option>
                            <option value="manufacturing">制造业</option>
                            <option value="finance">金融</option>
                            <option value="education">教育</option>
                            <option value="healthcare">医疗</option>
                            <option value="retail">零售</option>
                            <option value="construction">建筑</option>
                            <option value="other">其他</option>
                        </select>
                    </div>
                    <div class="col-lg-2 col-md-2">
                        <button class="btn btn-secondary w-100" onclick="window.companyProfileManager.resetFilters()" title="重置筛选">
                            <i class="bi bi-arrow-counterclockwise"></i> 重置
                        </button>
                    </div>
                </div>
            </div>

            <!-- 企业列表 -->
            <div class="case-list-full-width">
                <div id="companyListContainer">
                    <!-- 企业列表将动态渲染在这里 -->
                    <div class="case-loading">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3 text-muted">正在加载企业...</p>
                    </div>
                </div>

                <!-- 空状态 -->
                <div id="companyEmptyState" class="case-empty-state" style="display: none;">
                    <i class="bi bi-building-x"></i>
                    <h5>暂无企业</h5>
                    <p class="text-muted">点击右上角"新建企业"按钮创建第一个企业</p>
                </div>
            </div>
        `;

        mainContent.innerHTML = html;

        // 加载数据
        await this.loadCompanies();
    }

    /**
     * 加载企业列表
     */
    async loadCompanies() {
        try {
            const response = await axios.get('/api/companies');

            if (response.data.success) {
                this.allCompanies = response.data.data || [];

                // 同时加载每个企业的资质信息
                for (let company of this.allCompanies) {
                    try {
                        const qualResp = await axios.get(`/api/companies/${company.company_id}/qualifications`);
                        if (qualResp.data.success) {
                            company.qualifications = qualResp.data.qualifications || {};
                        }
                    } catch (error) {
                        console.error(`加载企业${company.company_id}的资质信息失败:`, error);
                        company.qualifications = {};
                    }
                }

                this.renderCompanyList(this.allCompanies);
            } else {
                throw new Error(response.data.error || '加载失败');
            }
        } catch (error) {
            console.error('加载企业列表失败:', error);
            if (window.showAlert) {
                window.showAlert('加载企业列表失败: ' + error.message, 'danger');
            }
            this.renderCompanyList([]);
        }
    }

    /**
     * 渲染企业列表
     */
    renderCompanyList(companies) {
        const container = document.getElementById('companyListContainer');
        const emptyState = document.getElementById('companyEmptyState');

        if (!container) return;

        // 应用筛选
        let filteredCompanies = companies;

        // 行业筛选
        if (this.currentFilters.industry) {
            filteredCompanies = filteredCompanies.filter(c =>
                c.industry_type === this.currentFilters.industry
            );
        }

        // 搜索关键词筛选
        if (this.currentFilters.searchKeyword) {
            const keyword = this.currentFilters.searchKeyword.toLowerCase();
            filteredCompanies = filteredCompanies.filter(c =>
                (c.company_name && c.company_name.toLowerCase().includes(keyword)) ||
                (c.company_code && c.company_code.toLowerCase().includes(keyword)) ||
                (c.social_credit_code && c.social_credit_code.toLowerCase().includes(keyword))
            );
        }

        // 显示空状态或企业列表
        if (filteredCompanies.length === 0) {
            container.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        container.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';

        // 渲染企业卡片
        const html = filteredCompanies.map(company => this.renderCompanyCard(company)).join('');
        container.innerHTML = html;

        // 更新统计数字
        const countElement = document.getElementById('companyTotalCount');
        if (countElement) {
            countElement.textContent = filteredCompanies.length;
        }
    }

    /**
     * 渲染单个企业卡片
     */
    renderCompanyCard(company) {
        // 计算资质完成度
        const qualProgress = this.calculateQualificationProgress(company.qualifications || {});
        const progressPercent = (qualProgress.completed / qualProgress.total * 100).toFixed(0);

        // 行业类型映射
        const industryMap = {
            'technology': '科技',
            'manufacturing': '制造业',
            'finance': '金融',
            'education': '教育',
            'healthcare': '医疗',
            'retail': '零售',
            'construction': '建筑',
            'other': '其他'
        };
        const industryLabel = industryMap[company.industry_type] || company.industry_type || '未知';

        return `
            <div class="case-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h5>${this.escapeHtml(company.company_name)}</h5>
                        <div class="case-meta">
                            <i class="bi bi-tag"></i>行业: ${this.escapeHtml(industryLabel)}
                            ${company.establish_date ? `<span class="ms-2"><i class="bi bi-calendar"></i>成立: ${company.establish_date}</span>` : ''}
                            ${company.social_credit_code ? `<span class="ms-2"><i class="bi bi-credit-card"></i>${this.escapeHtml(company.social_credit_code)}</span>` : ''}
                        </div>
                        <div class="case-meta mt-2">
                            <i class="bi bi-award"></i>资质完成度:
                            <div class="progress d-inline-block ms-2" style="width: 150px; height: 20px; vertical-align: middle;">
                                <div class="progress-bar bg-success" role="progressbar"
                                     style="width: ${progressPercent}%"
                                     aria-valuenow="${progressPercent}" aria-valuemin="0" aria-valuemax="100">
                                    ${progressPercent}%
                                </div>
                            </div>
                            <span class="ms-2 text-muted">${qualProgress.completed}/${qualProgress.total}</span>
                        </div>
                    </div>
                    <div class="case-actions">
                        <button type="button" class="btn btn-sm btn-primary"
                                onclick="window.companyProfileManager.viewCompanyDetail(${company.company_id})"
                                title="查看详情">
                            <i class="bi bi-eye"></i> 查看详情
                        </button>
                        <button type="button" class="btn btn-sm btn-danger"
                                onclick="window.companyProfileManager.deleteCompany(${company.company_id})"
                                title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 计算资质完成度
     */
    calculateQualificationProgress(qualifications) {
        // 标准资质类型总数（基于现有的标准资质列表，与后端保持一致）
        const standardQualificationTypes = [
            'business_license', 'legal_id_front', 'legal_id_back',
            'iso9001', 'iso14001', 'iso45001', 'iso20000', 'iso27001',
            'dishonest_executor', 'tax_violation_check', 'gov_procurement_creditchina', 'gov_procurement_ccgp',
            'software_copyright', 'patent_certificate', 'high_tech', 'software_enterprise', 'cmmi'
        ];

        const total = standardQualificationTypes.length;
        const completed = Object.keys(qualifications).length;

        return { completed, total };
    }

    /**
     * 查看企业详情
     */
    async viewCompanyDetail(companyId) {
        await this.renderCompanyProfile(companyId);
    }

    /**
     * 创建新企业 - 复用编辑界面
     */
    async createNewCompany() {
        try {
            // 步骤1: 调用后端API创建空企业记录
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await axios.post('/api/companies', {
                companyName: '新建企业',  // 默认名称
                companyDescription: '请完善企业信息'
            }, {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.data.success) {
                const newCompanyId = response.data.company.id;

                if (window.showAlert) {
                    window.showAlert('企业创建成功,请完善企业信息', 'success');
                }

                // 步骤2: 跳转到编辑界面(复用renderCompanyProfile)
                await this.renderCompanyProfile(parseInt(newCompanyId));

            } else {
                throw new Error(response.data.error || '创建失败');
            }

        } catch (error) {
            console.error('创建新企业失败:', error);
            if (window.showAlert) {
                window.showAlert('创建企业失败: ' + error.message, 'danger');
            }
        }
    }

    /**
     * 删除企业
     */
    async deleteCompany(companyId) {
        if (!confirm('确定要删除这个企业吗？此操作将同时删除企业的所有产品和文档，且不可恢复。')) {
            return;
        }

        try {
            const response = await axios.delete(`/api/companies/${companyId}`);

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert(response.data.message || '删除成功', 'success');
                }
                await this.loadCompanies();
            } else {
                throw new Error(response.data.error || '删除失败');
            }
        } catch (error) {
            console.error('删除企业失败:', error);
            if (window.showAlert) {
                window.showAlert('删除企业失败: ' + error.message, 'danger');
            }
        }
    }

    /**
     * 返回企业列表
     */
    async backToCompanyList() {
        await this.renderCompanyListView();
    }

    /**
     * 处理筛选器变更
     */
    handleFilterChange() {
        const industryFilter = document.getElementById('companyFilterIndustry');
        if (industryFilter) {
            this.currentFilters.industry = industryFilter.value || null;
        }

        this.renderCompanyList(this.allCompanies);
    }

    /**
     * 处理搜索
     */
    handleSearch() {
        const searchInput = document.getElementById('companySearchInput');
        if (searchInput) {
            this.currentFilters.searchKeyword = searchInput.value.trim();
            this.renderCompanyList(this.allCompanies);
        }
    }

    /**
     * 重置筛选器
     */
    resetFilters() {
        const industryFilter = document.getElementById('companyFilterIndustry');
        const searchInput = document.getElementById('companySearchInput');

        if (industryFilter) industryFilter.value = '';
        if (searchInput) searchInput.value = '';

        this.currentFilters = {
            industry: null,
            searchKeyword: ''
        };

        this.renderCompanyList(this.allCompanies);
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
     * 渲染企业信息库完整界面
     * @param {number} companyId 企业ID
     */
    async renderCompanyProfile(companyId) {
        // 设置当前企业ID
        this.currentCompanyId = companyId;

        // 先获取企业完整数据
        let companyData = null;
        try {
            const response = await axios.get(`/api/companies/${companyId}`);
            if (response.data.success) {
                companyData = response.data.data;
            }
        } catch (error) {
            console.error('加载企业数据失败:', error);
            if (window.showAlert) {
                window.showAlert('加载企业数据失败：' + error.message, 'danger');
            }
            return;
        }

        // 渲染界面
        const html = `
            <div class="container-fluid px-0">
                <!-- 顶部导航栏 -->
                <div class="case-edit-header mb-3">
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="d-flex align-items-center">
                            <button type="button" class="btn btn-outline-secondary me-3"
                                    onclick="window.companyProfileManager.backToCompanyList()">
                                <i class="bi bi-arrow-left me-1"></i>返回列表
                            </button>
                            <h4 class="mb-0">
                                <i class="bi bi-building text-primary me-2"></i>${companyData.company_name || '企业信息'}
                            </h4>
                        </div>
                    </div>
                </div>

                <!-- Tab导航 -->
                <ul class="nav nav-tabs mb-3" id="companyProfileTabs">
                    <li class="nav-item">
                        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-basic" onclick="window.companyProfileManager.switchTab('basic')">
                            <i class="bi bi-globe text-success"></i> 基础信息
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-qualification" onclick="window.companyProfileManager.switchTab('qualification')">
                            <i class="bi bi-award text-primary"></i> 资质信息
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-personnel" onclick="window.companyProfileManager.switchTab('personnel')">
                            <i class="bi bi-people text-warning"></i> 被授权人信息
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-financial" onclick="window.companyProfileManager.switchTab('financial')">
                            <i class="bi bi-bank text-danger"></i> 财务信息
                        </button>
                    </li>
                </ul>

                <!-- Tab内容 -->
                <div class="tab-content">
                    <!-- 基础信息Tab -->
                    <div class="tab-pane fade show active" id="tab-basic">
                        <div class="card">
                            <div class="card-body">
                                ${this.renderBasicInfoSection(companyData)}
                            </div>
                        </div>
                    </div>

                    <!-- 资质信息Tab -->
                    <div class="tab-pane fade" id="tab-qualification">
                        <div class="card">
                            <div class="card-body">
                                ${this.renderQualificationSection()}
                            </div>
                        </div>
                    </div>

                    <!-- 人员信息Tab -->
                    <div class="tab-pane fade" id="tab-personnel">
                        <div class="card">
                            <div class="card-body">
                                ${this.renderPersonnelSection(companyData)}
                            </div>
                        </div>
                    </div>

                    <!-- 财务信息Tab -->
                    <div class="tab-pane fade" id="tab-financial">
                        <div class="card">
                            <div class="card-body">
                                ${this.renderFinancialSection(companyData)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('mainContent').innerHTML = html;

        // 延迟加载资质文件状态
        setTimeout(() => this.loadExistingQualifications(), 500);
    }

    /**
     * 切换Tab页面
     * @param {string} tabName Tab名称
     */
    switchTab(tabName) {
        this.currentTab = tabName;

        // 如果切换到资质、人员或财务页面，延迟加载资质文件状态
        if (tabName === 'qualification' || tabName === 'personnel' || tabName === 'financial') {
            setTimeout(() => this.loadExistingQualifications(), 200);
        }
    }

    /**
     * 渲染基础信息部分
     * @param {Object} companyData 企业数据
     */
    renderBasicInfoSection(companyData) {
        const data = companyData || {};
        return `
            <form id="basicInfoForm">
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label">企业名称</label>
                        <input type="text" class="form-control" id="prof-companyName" value="${data.company_name || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">成立日期</label>
                        <input type="date" class="form-control" id="prof-establishDate" value="${data.establish_date || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">法定代表人</label>
                        <input type="text" class="form-control" id="prof-legalRepresentative" value="${data.legal_representative || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">法定代表人职务</label>
                        <input type="text" class="form-control" id="prof-legalRepresentativePosition" value="${data.legal_representative_position || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">法定代表人性别</label>
                        <select class="form-select" id="prof-legalRepresentativeGender">
                            <option value="">请选择</option>
                            <option value="男" ${data.legal_representative_gender === '男' ? 'selected' : ''}>男</option>
                            <option value="女" ${data.legal_representative_gender === '女' ? 'selected' : ''}>女</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">法定代表人年龄</label>
                        <input type="number" class="form-control" id="prof-legalRepresentativeAge" value="${data.legal_representative_age || ''}" min="18" max="100">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">统一社会信用代码</label>
                        <input type="text" class="form-control" id="prof-socialCreditCode" value="${data.social_credit_code || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">注册资本</label>
                        <input type="text" class="form-control" id="prof-registeredCapital" value="${data.registered_capital || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">企业类型</label>
                        <input type="text" class="form-control" id="prof-companyType" value="${data.company_type || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">注册地址</label>
                        <input type="text" class="form-control" id="prof-registeredAddress" value="${data.registered_address || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">联系电话</label>
                        <input type="text" class="form-control" id="prof-fixedPhone" value="${data.fixed_phone || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">传真</label>
                        <input type="text" class="form-control" id="prof-fax" value="${data.fax || ''}">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">邮政编码</label>
                        <input type="text" class="form-control" id="prof-postalCode" value="${data.postal_code || ''}" maxlength="6">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">电子邮箱</label>
                        <input type="email" class="form-control" id="prof-email" value="${data.email || ''}">
                    </div>
                    <div class="col-12">
                        <label class="form-label">经营范围</label>
                        <textarea class="form-control" id="prof-businessScope" rows="3">${data.business_scope || ''}</textarea>
                    </div>
                    <div class="col-12">
                        <label class="form-label">企业简介</label>
                        <textarea class="form-control" id="prof-companyDescription" rows="3">${data.description || ''}</textarea>
                    </div>
                </div>
                <div class="mt-3">
                    <button type="button" class="btn btn-success" onclick="window.companyProfileManager.saveBasicInfo()">
                        <i class="bi bi-save"></i> 保存基础信息
                    </button>
                </div>
            </form>
        `;
    }

    /**
     * 渲染资质信息部分
     */
    renderQualificationSection() {
        return `
            <div class="qualification-section">
                <h6 class="text-primary mb-3"><i class="bi bi-award"></i> 标准资质</h6>
                <div id="profileStandardQualifications">
                    ${this.renderStandardQualifications()}
                </div>
                <div class="mt-4">
                    <h6 class="text-success mb-3"><i class="bi bi-plus-circle"></i> 自定义资质</h6>
                    <div class="row">
                        <div class="col-md-8">
                            <input type="text" class="form-control" id="profileCustomQualificationName" placeholder="输入资质名称">
                        </div>
                        <div class="col-md-4">
                            <button type="button" class="btn btn-success w-100" onclick="window.companyProfileManager.addCustomQualification()">
                                <i class="bi bi-plus"></i> 添加资质项
                            </button>
                        </div>
                    </div>
                    <div id="profileCustomQualifications" class="mt-3"></div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染人员信息部分
     * @param {Object} companyData 企业数据
     */
    renderPersonnelSection(companyData) {
        const data = companyData || {};
        return `
            <div class="personnel-section">
                <!-- 被授权人信息表单 -->
                <div class="mb-4">
                    <h6 class="text-warning mb-3"><i class="bi bi-person-badge"></i> 被授权人基本信息</h6>
                    <form id="authorizedPersonForm">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">姓名</label>
                                <input type="text" class="form-control" id="auth-name" placeholder="请输入被授权人姓名" value="${data.authorized_person_name || ''}">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">身份证号</label>
                                <input type="text" class="form-control" id="auth-idcard" placeholder="请输入身份证号" maxlength="18" value="${data.authorized_person_id || ''}">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">性别</label>
                                <select class="form-select" id="auth-gender">
                                    <option value="">请选择</option>
                                    <option value="男" ${data.authorized_person_gender === '男' ? 'selected' : ''}>男</option>
                                    <option value="女" ${data.authorized_person_gender === '女' ? 'selected' : ''}>女</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">职位</label>
                                <input type="text" class="form-control" id="auth-position" placeholder="请输入职位" value="${data.authorized_person_position || ''}">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">职称</label>
                                <input type="text" class="form-control" id="auth-title" placeholder="请输入职称" value="${data.authorized_person_title || ''}">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">年龄</label>
                                <input type="number" class="form-control" id="auth-age" placeholder="请输入年龄" min="18" max="100" value="${data.authorized_person_age || ''}">
                            </div>
                        </div>
                        <div class="mt-3">
                            <button type="button" class="btn btn-warning" onclick="window.companyProfileManager.saveAuthorizedPersonInfo()">
                                <i class="bi bi-save"></i> 保存被授权人信息
                            </button>
                        </div>
                    </form>
                </div>

                <!-- 附件上传区域 -->
                <div class="mb-4">
                    <h6 class="text-secondary mb-3">
                        <i class="bi bi-file-earmark-person"></i> 相关附件
                        <small class="text-muted ms-2">(上传的身份证将用于商务应答文档生成)</small>
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('被授权人身份证(正面)', 'auth_id_front', 'bi-person-check')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('被授权人身份证(反面)', 'auth_id_back', 'bi-person-check')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('项目经理简历', 'project_manager_resume', 'bi-person-badge')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('被授权人社保证明', 'social_security', 'bi-people')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染财务信息部分
     * @param {Object} companyData 企业数据
     */
    renderFinancialSection(companyData) {
        const data = companyData || {};

        // 解析股东信息JSON
        let shareholders = [];
        try {
            shareholders = data.shareholders_info ? JSON.parse(data.shareholders_info) : [];
        } catch (e) {
            console.error('解析股东信息失败:', e);
            shareholders = [];
        }

        return `
            <div class="financial-section">
                <div class="mb-4">
                    <h6 class="text-danger mb-3"><i class="bi bi-bank"></i> 财务文档</h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            ${this.renderFinancialItem('财务审计报告', 'audit_report', 'bi-file-earmark-check')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderFinancialItem('纳税人资格证明', 'taxpayer_certificate', 'bi-receipt')}
                        </div>
                    </div>
                </div>
                <div class="mb-4">
                    <h6 class="text-info mb-3"><i class="bi bi-bank2"></i> 银行账户信息</h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">开户行全称</label>
                            <input type="text" class="form-control" id="prof-bankName" value="${data.bank_name || ''}" placeholder="例：中国工商银行股份有限公司北京分行">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">银行账号</label>
                            <input type="text" class="form-control" id="prof-bankAccount" value="${data.bank_account || ''}" placeholder="请输入银行账号">
                        </div>
                    </div>
                </div>

                <!-- 【新增】股权结构信息 -->
                <div class="mb-4">
                    <h6 class="text-warning mb-3">
                        <i class="bi bi-diagram-3"></i> 股权结构信息
                    </h6>

                    <!-- 实际控制人和控股股东 -->
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">实际控制人</label>
                            <input type="text" class="form-control" id="prof-actualController"
                                   value="${data.actual_controller || ''}"
                                   placeholder="请输入实际控制人姓名/名称">
                            <small class="text-muted">实际控制公司经营决策的个人或组织</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">控股股东</label>
                            <input type="text" class="form-control" id="prof-controllingShareholder"
                                   value="${data.controlling_shareholder || ''}"
                                   placeholder="请输入控股股东名称">
                            <small class="text-muted">持股比例最大或有实际控制权的股东</small>
                        </div>
                    </div>

                    <!-- 管理关系信息 -->
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">管理关系单位名称</label>
                            <input type="text" class="form-control" id="prof-managingUnitName"
                                   value="${data.managing_unit_name || ''}"
                                   placeholder="本公司管理的单位名称">
                            <small class="text-muted">本公司所管理的下级单位或分支机构</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">被管理关系单位名称</label>
                            <input type="text" class="form-control" id="prof-managedUnitName"
                                   value="${data.managed_unit_name || ''}"
                                   placeholder="管理本公司的单位名称">
                            <small class="text-muted">管理本公司的上级单位或集团</small>
                        </div>
                    </div>

                    <!-- 股东/投资人列表 -->
                    <div class="card">
                        <div class="card-header bg-light d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-people-fill"></i> 股东/投资人列表</span>
                            <button type="button" class="btn btn-sm btn-success"
                                    onclick="window.companyProfileManager.addShareholder()">
                                <i class="bi bi-plus-circle"></i> 添加股东
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="shareholdersList">
                                ${this.renderShareholdersList(shareholders)}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="text-center mt-4">
                    <button type="button" class="btn btn-danger btn-lg" onclick="window.companyProfileManager.saveFinancialInfo()">
                        <i class="bi bi-save"></i> 保存财务信息
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * 渲染股东列表
     * @param {Array} shareholders 股东数组
     */
    renderShareholdersList(shareholders) {
        if (!shareholders || shareholders.length === 0) {
            return `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                    <p class="mt-2">暂无股东信息，请点击上方"添加股东"按钮</p>
                </div>
            `;
        }

        return `
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 30%">股东名称</th>
                        <th style="width: 20%">类型</th>
                        <th style="width: 20%">出资比例</th>
                        <th style="width: 25%">操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${shareholders.map((shareholder, index) => this.renderShareholderRow(shareholder, index)).join('')}
                </tbody>
            </table>
        `;
    }

    /**
     * 渲染单个股东行
     * @param {Object} shareholder 股东信息
     * @param {number} index 索引
     */
    renderShareholderRow(shareholder, index) {
        const typeIcon = shareholder.type === '企业' ? 'bi-building' : 'bi-person';
        const typeBadge = shareholder.type === '企业'
            ? '<span class="badge bg-primary"><i class="bi bi-building"></i> 企业</span>'
            : '<span class="badge bg-success"><i class="bi bi-person"></i> 自然人</span>';

        return `
            <tr>
                <td>${index + 1}</td>
                <td>
                    <i class="bi ${typeIcon} text-muted me-2"></i>
                    ${this.escapeHtml(shareholder.name || '')}
                </td>
                <td>${typeBadge}</td>
                <td>
                    <strong class="text-primary">${this.escapeHtml(shareholder.ratio || '')}</strong>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-warning"
                                onclick="window.companyProfileManager.editShareholder(${index})"
                                title="编辑">
                            <i class="bi bi-pencil"></i> 编辑
                        </button>
                        <button type="button" class="btn btn-outline-danger"
                                onclick="window.companyProfileManager.removeShareholder(${index})"
                                title="删除">
                            <i class="bi bi-trash"></i> 删除
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * 渲染标准资质列表
     */
    renderStandardQualifications() {
        const standardQualificationTypes = [
            // 基本证件资质
            { key: 'business_license', name: '营业执照', icon: 'bi-building', category: 'basic', required: true },
            { key: 'legal_id_front', name: '法人身份证（正面）', icon: 'bi-person-badge', category: 'basic', required: true },
            { key: 'legal_id_back', name: '法人身份证（反面）', icon: 'bi-person-badge', category: 'basic', required: true },

            // ISO体系认证
            { key: 'iso9001', name: '质量管理体系认证（ISO9001）', icon: 'bi-award', category: 'iso' },
            { key: 'iso20000', name: '信息技术服务管理体系认证（ISO20000）', icon: 'bi-gear', category: 'iso' },
            { key: 'iso27001', name: '信息安全管理体系认证（ISO27001）', icon: 'bi-shield-lock', category: 'iso' },
            { key: 'level_protection', name: '信息安全等级保护三级认证', icon: 'bi-shield-check', category: 'iso' },

            // 信用资质（与后端 qualification_matcher.py 保持一致）
            { key: 'dishonest_executor', name: '失信被执行人名单（信用中国）', icon: 'bi-shield-x', category: 'credit' },
            { key: 'tax_violation_check', name: '重大税收违法案件当事人名单（信用中国）', icon: 'bi-exclamation-triangle', category: 'credit' },
            { key: 'gov_procurement_creditchina', name: '政府采购严重违法失信（信用中国）', icon: 'bi-flag', category: 'credit' },
            { key: 'gov_procurement_ccgp', name: '政府采购严重违法失信行为信息记录（政府采购网）', icon: 'bi-check-circle', category: 'credit' },

            // 知识产权和行业资质
            { key: 'basic_telecom_permit', name: '基础电信业务许可证', icon: 'bi-broadcast', category: 'industry' },
            { key: 'value_added_telecom_permit', name: '增值电信业务许可证', icon: 'bi-broadcast-pin', category: 'industry' },
            { key: 'software_copyright', name: '软件著作权登记证书', icon: 'bi-code-square', category: 'industry' },
            { key: 'patent_certificate', name: '专利证书', icon: 'bi-lightbulb', category: 'industry' },
            { key: 'high_tech', name: '高新技术企业证书', icon: 'bi-rocket', category: 'industry' },
            { key: 'software_enterprise', name: '软件企业认定证书', icon: 'bi-cpu', category: 'industry' },
            { key: 'cmmi', name: 'CMMI成熟度等级证书', icon: 'bi-diagram-3', category: 'industry' }
        ];

        const categories = {
            'basic': { name: '基本证件资质', color: 'primary' },
            'iso': { name: 'ISO体系认证', color: 'success' },
            'credit': { name: '信用资质证明', color: 'info' },
            'industry': { name: '行业专业资质', color: 'danger' }
        };

        let html = '';

        Object.keys(categories).forEach(categoryKey => {
            const category = categories[categoryKey];
            const categoryQuals = standardQualificationTypes.filter(qual => qual.category === categoryKey);

            if (categoryQuals.length > 0) {
                html += `<div class="mb-4">
                    <h6 class="text-${category.color} mb-3 border-bottom pb-2">
                        <i class="bi bi-folder"></i> ${category.name}
                    </h6>
                    <div class="row g-3">`;

                categoryQuals.forEach(qual => {
                    html += `<div class="col-lg-6">
                        ${this.renderQualificationItem(qual.name, qual.key, qual.icon, qual.required)}
                    </div>`;
                });

                html += '</div></div>';
            }
        });

        return html;
    }

    /**
     * 渲染单个资质项
     * @param {string} name 资质名称
     * @param {string} id 资质ID
     * @param {string} icon 图标类名
     * @param {boolean} required 是否必需
     */
    renderQualificationItem(name, id, icon, required = false) {
        const borderClass = required ? 'border-warning' : '';
        const requiredBadge = required ? '<span class="badge bg-warning text-dark ms-2">必需</span>' : '';

        // 检查是否为支持多文件的资质类型
        const isMultiFile = this.multiFileQualifications.hasOwnProperty(id);
        const multipleAttr = isMultiFile ? 'multiple' : '';
        const multiBadge = isMultiFile ? '<span class="badge bg-info text-white ms-2"><i class="bi bi-files"></i> 多文件</span>' : '';

        return `
            <div class="card mb-3 shadow-sm ${borderClass}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="flex-grow-1">
                            <i class="bi ${icon} me-2 text-primary"></i>
                            <span>${name}</span>
                            ${requiredBadge}
                            ${multiBadge}
                        </div>
                        <div class="btn-group">
                            <input type="file" class="d-none" id="profile-qual-${id}" accept=".pdf,.jpg,.png,.jpeg" ${multipleAttr} onchange="window.companyProfileManager.uploadQualificationFile('${id}', this)">
                            <button class="btn btn-sm btn-outline-primary" onclick="document.getElementById('profile-qual-${id}').click()" title="上传文件">
                                <i class="bi bi-upload"></i> ${isMultiFile ? '批量' : ''}
                            </button>
                        </div>
                    </div>
                    <div class="mt-2 d-none" id="profile-status-${id}">
                        <small class="text-muted">未上传文件</small>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染人员项目
     * @param {string} name 项目名称
     * @param {string} id 项目ID
     * @param {string} icon 图标类名
     */
    renderPersonnelItem(name, id, icon) {
        return `
            <div class="personnel-item">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center">
                                <i class="bi ${icon} text-warning me-2"></i>
                                <span>${name}</span>
                            </div>
                            <div>
                                <input type="file" class="d-none" id="pers-${id}" accept=".pdf,.jpg,.png" onchange="window.companyProfileManager.uploadPersonnelFile('${id}', this)">
                                <button class="btn btn-sm btn-outline-warning" onclick="document.getElementById('pers-${id}').click()">
                                    <i class="bi bi-upload"></i>
                                </button>
                            </div>
                        </div>
                        <div class="mt-2 d-none" id="pers-status-${id}">
                            <small class="text-muted">未上传文件</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染财务项目
     * @param {string} name 项目名称
     * @param {string} id 项目ID
     * @param {string} icon 图标类名
     */
    renderFinancialItem(name, id, icon) {
        // 检查是否为支持多文件的资质类型（财务审计报告支持多年份）
        const isMultiFile = this.multiFileQualifications.hasOwnProperty(id);
        const multipleAttr = isMultiFile ? 'multiple' : '';
        const multiBadge = isMultiFile ? '<span class="badge bg-info text-white ms-2"><i class="bi bi-files"></i> 多文件</span>' : '';

        return `
            <div class="financial-item">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center flex-grow-1">
                                <i class="bi ${icon} text-danger me-2"></i>
                                <span>${name}</span>
                                ${multiBadge}
                            </div>
                            <div>
                                <input type="file" class="d-none" id="fin-${id}" accept=".pdf,.xls,.xlsx" ${multipleAttr} onchange="window.companyProfileManager.uploadFinancialFile('${id}', this)">
                                <button class="btn btn-sm btn-outline-danger" onclick="document.getElementById('fin-${id}').click()">
                                    <i class="bi bi-upload"></i> ${isMultiFile ? '批量' : ''}
                                </button>
                            </div>
                        </div>
                        <div class="mt-2 d-none" id="fin-status-${id}">
                            <small class="text-muted">未上传文件</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 添加股东
     */
    addShareholder() {
        // 使用prompt收集股东信息
        const name = prompt('请输入股东名称:');
        if (!name || !name.trim()) {
            return; // 用户取消或输入为空
        }

        const type = prompt('请选择类型（输入1为企业，输入2为自然人）:');
        let shareholderType;
        if (type === '1') {
            shareholderType = '企业';
        } else if (type === '2') {
            shareholderType = '自然人';
        } else {
            if (window.showAlert) {
                window.showAlert('类型选择无效，请输入1或2', 'warning');
            }
            return;
        }

        const ratio = prompt('请输入出资比例（如：30%）:');
        if (!ratio || !ratio.trim()) {
            return; // 用户取消或输入为空
        }

        // 获取当前股东列表
        const currentShareholders = this.getCurrentShareholders();

        // 添加新股东
        currentShareholders.push({
            name: name.trim(),
            type: shareholderType,
            ratio: ratio.trim()
        });

        // 重新渲染股东列表
        this.refreshShareholdersList(currentShareholders);

        if (window.showAlert) {
            window.showAlert('股东添加成功，请点击底部"保存财务信息"按钮保存', 'success');
        }
    }

    /**
     * 编辑股东
     * @param {number} index 股东索引
     */
    editShareholder(index) {
        const currentShareholders = this.getCurrentShareholders();
        const shareholder = currentShareholders[index];

        if (!shareholder) {
            if (window.showAlert) {
                window.showAlert('未找到该股东信息', 'danger');
            }
            return;
        }

        // 编辑股东名称
        const name = prompt('请输入股东名称:', shareholder.name);
        if (name === null) return; // 用户取消

        // 编辑类型
        const typePrompt = shareholder.type === '企业' ? '1' : '2';
        const type = prompt(`请选择类型（输入1为企业，输入2为自然人）[当前:${shareholder.type}]:`, typePrompt);
        if (type === null) return; // 用户取消

        let shareholderType;
        if (type === '1') {
            shareholderType = '企业';
        } else if (type === '2') {
            shareholderType = '自然人';
        } else {
            if (window.showAlert) {
                window.showAlert('类型选择无效，请输入1或2', 'warning');
            }
            return;
        }

        // 编辑出资比例
        const ratio = prompt('请输入出资比例（如：30%）:', shareholder.ratio);
        if (ratio === null) return; // 用户取消

        // 更新股东信息
        currentShareholders[index] = {
            name: name.trim(),
            type: shareholderType,
            ratio: ratio.trim()
        };

        // 重新渲染股东列表
        this.refreshShareholdersList(currentShareholders);

        if (window.showAlert) {
            window.showAlert('股东信息更新成功，请点击底部"保存财务信息"按钮保存', 'success');
        }
    }

    /**
     * 删除股东
     * @param {number} index 股东索引
     */
    removeShareholder(index) {
        if (!confirm('确定要删除这个股东吗？')) {
            return;
        }

        const currentShareholders = this.getCurrentShareholders();
        currentShareholders.splice(index, 1);

        // 重新渲染股东列表
        this.refreshShareholdersList(currentShareholders);

        if (window.showAlert) {
            window.showAlert('股东删除成功，请点击底部"保存财务信息"按钮保存', 'success');
        }
    }

    /**
     * 获取当前股东列表
     * @returns {Array} 股东数组
     */
    getCurrentShareholders() {
        const shareholdersListDiv = document.getElementById('shareholdersList');
        if (!shareholdersListDiv) return [];

        // 从DOM中提取当前股东数据
        // 如果存在table，说明有股东数据
        const table = shareholdersListDiv.querySelector('table');
        if (!table) return [];

        const shareholders = [];
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 4) {
                // 提取股东名称（移除前面的图标）
                const nameCell = cells[1];
                const name = nameCell.textContent.trim();

                // 提取类型（从badge中）
                const typeBadge = cells[2].querySelector('.badge');
                const type = typeBadge ? typeBadge.textContent.trim().replace(/企业|自然人/, match => match) : '';

                // 提取出资比例
                const ratioCell = cells[3];
                const ratio = ratioCell.textContent.trim();

                shareholders.push({
                    name: name,
                    type: type.includes('企业') ? '企业' : '自然人',
                    ratio: ratio
                });
            }
        });

        return shareholders;
    }

    /**
     * 刷新股东列表显示
     * @param {Array} shareholders 股东数组
     */
    refreshShareholdersList(shareholders) {
        const shareholdersListDiv = document.getElementById('shareholdersList');
        if (!shareholdersListDiv) return;

        shareholdersListDiv.innerHTML = this.renderShareholdersList(shareholders);
    }

    /**
     * 保存基础信息
     */
    async saveBasicInfo() {
        const data = {
            companyName: document.getElementById('prof-companyName').value,
            establishDate: document.getElementById('prof-establishDate').value,
            legalRepresentative: document.getElementById('prof-legalRepresentative').value,
            legalRepresentativePosition: document.getElementById('prof-legalRepresentativePosition').value,
            legalRepresentativeGender: document.getElementById('prof-legalRepresentativeGender').value,
            legalRepresentativeAge: document.getElementById('prof-legalRepresentativeAge').value,
            socialCreditCode: document.getElementById('prof-socialCreditCode').value,
            registeredCapital: document.getElementById('prof-registeredCapital').value,
            companyType: document.getElementById('prof-companyType').value,
            registeredAddress: document.getElementById('prof-registeredAddress').value,
            fixedPhone: document.getElementById('prof-fixedPhone').value,
            fax: document.getElementById('prof-fax').value,
            postalCode: document.getElementById('prof-postalCode').value,
            email: document.getElementById('prof-email').value,
            businessScope: document.getElementById('prof-businessScope').value,
            companyDescription: document.getElementById('prof-companyDescription').value
        };

        try {
            // Get CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await axios.put('/api/companies/' + this.currentCompanyId, data, {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('基础信息保存成功', 'success');
                }
            }
        } catch (error) {
            console.error('保存失败:', error);
            if (window.showAlert) {
                window.showAlert('保存失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 保存财务信息
     */
    async saveFinancialInfo() {
        // 获取股东信息
        const shareholders = this.getCurrentShareholders();

        const data = {
            bank_name: document.getElementById('prof-bankName').value,
            bank_account: document.getElementById('prof-bankAccount').value,
            // 【新增】股权结构字段
            actual_controller: document.getElementById('prof-actualController').value,
            controlling_shareholder: document.getElementById('prof-controllingShareholder').value,
            shareholders_info: JSON.stringify(shareholders), // 将股东数组转换为JSON字符串
            // 【新增】管理关系字段
            managing_unit_name: document.getElementById('prof-managingUnitName').value,
            managed_unit_name: document.getElementById('prof-managedUnitName').value
        };

        try {
            // Get CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await axios.put('/api/companies/' + this.currentCompanyId, data, {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('财务信息保存成功', 'success');
                }
            }
        } catch (error) {
            console.error('保存财务信息失败:', error);
            if (window.showAlert) {
                window.showAlert('保存失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 保存被授权人信息
     */
    async saveAuthorizedPersonInfo() {
        const data = {
            authorized_person_name: document.getElementById('auth-name').value,
            authorized_person_id: document.getElementById('auth-idcard').value,
            authorized_person_gender: document.getElementById('auth-gender').value,
            authorized_person_position: document.getElementById('auth-position').value,
            authorized_person_title: document.getElementById('auth-title').value,
            authorized_person_age: document.getElementById('auth-age').value
        };

        try {
            // Get CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await axios.put('/api/companies/' + this.currentCompanyId, data, {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('被授权人信息保存成功', 'success');
                }
            }
        } catch (error) {
            console.error('保存被授权人信息失败:', error);
            if (window.showAlert) {
                window.showAlert('保存失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 上传资质文件（支持多文件）
     * @param {string} qualificationId 资质ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadQualificationFile(qualificationId, input) {
        const files = input.files;
        if (!files || files.length === 0) return;

        // 检查是否为多文件资质
        const isMultiFile = this.multiFileQualifications.hasOwnProperty(qualificationId);

        if (isMultiFile) {
            // 多文件上传：逐个文件询问版本信息并上传
            await this.uploadMultipleQualificationFiles(qualificationId, files);
        } else {
            // 单文件上传：直接上传第一个文件
            await this.uploadSingleQualificationFile(qualificationId, files[0]);
        }

        // 上传完成后重新加载资质列表
        await this.loadExistingQualifications();

        // 清空文件输入
        input.value = '';
    }

    /**
     * 上传单个资质文件
     * @param {string} qualificationId 资质ID
     * @param {File} file 文件对象
     * @param {string} version 版本号（可选）
     */
    async uploadSingleQualificationFile(qualificationId, file, version = null) {
        try {
            const formData = new FormData();
            formData.append(`qualifications[${qualificationId}]`, file);

            // 如果有版本号，添加到FormData
            if (version) {
                const fileVersions = {};
                fileVersions[qualificationId] = version;
                formData.append('file_versions', JSON.stringify(fileVersions));
            }

            // Get CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await axios.post(`/api/companies/${this.currentCompanyId}/qualifications/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.data.success) {
                return { success: true, filename: file.name };
            } else {
                throw new Error(response.data.error || '上传失败');
            }
        } catch (error) {
            console.error('资质文件上传失败:', error);
            throw error;
        }
    }

    /**
     * 批量上传多个资质文件
     * @param {string} qualificationId 资质ID
     * @param {FileList} files 文件列表
     */
    async uploadMultipleQualificationFiles(qualificationId, files) {
        const config = this.multiFileQualifications[qualificationId];
        const versionLabel = config.versionLabel || '版本';
        const placeholder = config.placeholder || '请输入版本信息';

        let successCount = 0;
        let failCount = 0;

        // 逐个处理文件
        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            // 弹窗询问版本号
            const version = prompt(`请输入 "${file.name}" 的${versionLabel}:\n${placeholder}`);

            // 用户取消则跳过该文件
            if (version === null) {
                console.log(`用户取消上传文件: ${file.name}`);
                continue;
            }

            // 版本号不能为空
            if (!version.trim()) {
                if (window.showAlert) {
                    window.showAlert(`文件 "${file.name}" 的${versionLabel}不能为空，已跳过`, 'warning');
                }
                continue;
            }

            // 上传文件
            try {
                await this.uploadSingleQualificationFile(qualificationId, file, version.trim());
                successCount++;
                console.log(`成功上传: ${file.name} (${versionLabel}: ${version})`);
            } catch (error) {
                failCount++;
                console.error(`上传失败: ${file.name}`, error);
            }
        }

        // 显示结果
        if (successCount > 0 || failCount > 0) {
            const message = `上传完成：成功 ${successCount} 个，失败 ${failCount} 个`;
            const alertType = failCount === 0 ? 'success' : 'warning';

            if (window.showAlert) {
                window.showAlert(message, alertType);
            }
        }
    }

    /**
     * 上传人员文件
     * @param {string} personnelId 人员ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadPersonnelFile(personnelId, input) {
        const file = input.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append(`qualifications[${personnelId}]`, file);

            // Get CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const response = await axios.post(`/api/companies/${this.currentCompanyId}/qualifications/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('人员文件上传成功', 'success');
                }
                this.updatePersonnelStatus(personnelId, file.name, 'success');
            }
        } catch (error) {
            console.error('人员文件上传失败:', error);
            if (window.showAlert) {
                window.showAlert('上传失败：' + error.message, 'danger');
            }
            this.updatePersonnelStatus(personnelId, '上传失败', 'error');
        }
    }

    /**
     * 上传财务文件（支持多文件）
     * @param {string} financialId 财务ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadFinancialFile(financialId, input) {
        const files = input.files;
        if (!files || files.length === 0) return;

        // 检查是否为多文件资质（审计报告支持多年份）
        const isMultiFile = this.multiFileQualifications.hasOwnProperty(financialId);

        if (isMultiFile) {
            // 多文件上传：逐个文件询问版本信息并上传
            await this.uploadMultipleQualificationFiles(financialId, files);
        } else {
            // 单文件上传：直接上传第一个文件
            await this.uploadSingleQualificationFile(financialId, files[0]);

            if (window.showAlert) {
                window.showAlert('财务文件上传成功', 'success');
            }
        }

        // 上传完成后重新加载资质列表
        await this.loadExistingQualifications();

        // 清空文件输入
        input.value = '';
    }

    /**
     * 更新资质状态显示
     * @param {string} qualificationId 资质ID
     * @param {string} fileName 文件名
     * @param {string} status 状态
     */
    updateQualificationStatus(qualificationId, fileName, status) {
        const statusElement = document.getElementById(`profile-status-${qualificationId}`);
        if (statusElement) {
            statusElement.classList.remove('d-none');
            // 使用柔和图标 + 更优雅的样式
            if (status === 'success') {
                statusElement.innerHTML = `
                    <div class="d-flex align-items-center">
                        <i class="bi bi-check-circle-fill text-success me-2"></i>
                        <small class="text-dark">${fileName}</small>
                    </div>
                `;
            } else {
                statusElement.innerHTML = `
                    <div class="d-flex align-items-center">
                        <i class="bi bi-exclamation-circle text-warning me-2"></i>
                        <small class="text-muted">${fileName}</small>
                    </div>
                `;
            }
        }
    }

    /**
     * 更新人员状态显示
     * @param {string} personnelId 人员ID
     * @param {string} fileName 文件名
     * @param {string} status 状态
     */
    updatePersonnelStatus(personnelId, fileName, status) {
        const statusElement = document.getElementById(`pers-status-${personnelId}`);
        if (statusElement) {
            statusElement.classList.remove('d-none');
            statusElement.innerHTML = `<small class="text-${status === 'success' ? 'success' : 'danger'}">${fileName}</small>`;
        }
    }

    /**
     * 更新财务状态显示
     * @param {string} financialId 财务ID
     * @param {string} fileName 文件名
     * @param {string} status 状态
     */
    updateFinancialStatus(financialId, fileName, status) {
        const statusElement = document.getElementById(`fin-status-${financialId}`);
        if (statusElement) {
            statusElement.classList.remove('d-none');
            statusElement.innerHTML = `<small class="text-${status === 'success' ? 'success' : 'danger'}">${fileName}</small>`;
        }
    }

    /**
     * 添加自定义资质
     */
    addCustomQualification() {
        const name = document.getElementById('profileCustomQualificationName').value.trim();
        if (!name) {
            if (window.showAlert) {
                window.showAlert('请输入资质名称', 'warning');
            }
            return;
        }

        const customId = 'custom_' + Date.now();
        const customContainer = document.getElementById('profileCustomQualifications');
        const customHtml = this.renderQualificationItem(name, customId, 'bi-file-plus');
        customContainer.insertAdjacentHTML('beforeend', customHtml);

        // 清空输入框
        document.getElementById('profileCustomQualificationName').value = '';
    }

    /**
     * 加载现有资质文件
     */
    async loadExistingQualifications() {
        if (!this.currentCompanyId) return;

        try {
            console.log('正在加载公司', this.currentCompanyId, '的资质文件信息...');
            const response = await axios.get(`/api/companies/${this.currentCompanyId}/qualifications`);
            console.log('API响应:', response.data);

            if (response.data.success) {
                const qualifications = response.data.qualifications;
                console.log('找到资质文件数量:', Object.keys(qualifications).length);

                // 更新每个资质文件的显示状态
                Object.keys(qualifications).forEach(qualKey => {
                    const fileInfo = qualifications[qualKey];
                    console.log('处理资质文件:', qualKey, fileInfo);
                    this.refreshQualificationDisplay(qualKey, fileInfo);
                });
            } else {
                console.error('API返回失败:', response.data);
            }
        } catch (error) {
            console.error('加载资质文件信息失败:', error);
        }
    }

    /**
     * 刷新资质文件显示（支持多文件）
     * @param {string} qualKey 资质键名
     * @param {Object} fileInfo 文件信息
     */
    refreshQualificationDisplay(qualKey, fileInfo) {
        console.log('refreshQualificationDisplay 被调用:', qualKey, fileInfo);

        // 先尝试查找资质页面的元素
        let statusElement = document.getElementById(`profile-status-${qualKey}`);
        console.log('找到资质DOM元素:', statusElement ? 'YES' : 'NO', `profile-status-${qualKey}`);

        // 如果找不到资质页面元素，尝试查找人员页面的元素
        if (!statusElement) {
            statusElement = document.getElementById(`pers-status-${qualKey}`);
            console.log('找到人员DOM元素:', statusElement ? 'YES' : 'NO', `pers-status-${qualKey}`);
        }

        // 如果找不到人员页面元素，尝试查找财务页面的元素
        if (!statusElement) {
            statusElement = document.getElementById(`fin-status-${qualKey}`);
            console.log('找到财务DOM元素:', statusElement ? 'YES' : 'NO', `fin-status-${qualKey}`);
        }

        if (statusElement && fileInfo) {
            statusElement.classList.remove('d-none');

            // 检查是否为多文件资质
            if (fileInfo.allow_multiple_files && fileInfo.files && fileInfo.files.length > 0) {
                // 多文件资质显示
                const versionLabel = fileInfo.version_label || '版本';
                let filesHtml = fileInfo.files.map((file, index) => {
                    const formattedTime = this.formatDateTime(file.upload_time);
                    const formattedSize = this.formatFileSize(file.file_size);
                    const versionText = file.file_version ? `${versionLabel}: ${file.file_version}` : `文件 ${index + 1}`;

                    return `
                        <div class="d-flex justify-content-between align-items-center mb-2 ${index > 0 ? 'mt-2 pt-2 border-top' : ''}">
                            <div class="flex-grow-1">
                                <small class="text-success">✓ ${file.original_filename}</small>
                                <br><small class="text-muted">${versionText} | ${formattedSize} | ${formattedTime}</small>
                            </div>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm"
                                        onclick="window.companyProfileManager.downloadQualificationFileById('${file.qualification_id}')"
                                        title="下载">
                                    <i class="bi bi-download"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm"
                                        onclick="window.companyProfileManager.deleteQualificationFileById('${file.qualification_id}')"
                                        title="删除">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');

                statusElement.innerHTML = `
                    <div class="multi-file-list">
                        <div class="mb-2">
                            <small class="text-primary"><strong>已上传 ${fileInfo.files.length} 个文件</strong></small>
                        </div>
                        ${filesHtml}
                    </div>
                `;
            } else {
                // 单文件资质显示（保持向后兼容）
                const formattedTime = this.formatDateTime(fileInfo.upload_time);
                const formattedSize = this.formatFileSize(fileInfo.file_size);

                statusElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <small class="text-success">✓ ${fileInfo.original_filename}</small>
                            <br><small class="text-muted">${formattedSize} | ${formattedTime}</small>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-sm" onclick="window.companyProfileManager.downloadQualificationFile('${this.currentCompanyId}', '${qualKey}')" title="下载">
                                <i class="bi bi-download"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="window.companyProfileManager.deleteQualificationFile('${qualKey}')" title="删除">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            }
            console.log('资质文件显示已更新:', qualKey);
        } else {
            console.error('无法更新资质文件显示 - statusElement:', statusElement, 'fileInfo:', fileInfo);
        }
    }

    /**
     * 下载资质文件（通过资质键）
     * @param {number} companyId 企业ID
     * @param {string} qualKey 资质键名
     */
    async downloadQualificationFile(companyId, qualKey) {
        try {
            window.open(`/api/companies/${companyId}/qualifications/${qualKey}/download`);
        } catch (error) {
            console.error('下载资质文件失败:', error);
            if (window.showAlert) {
                window.showAlert('下载资质文件失败', 'danger');
            }
        }
    }

    /**
     * 下载资质文件（通过文件ID）- 用于多文件资质
     * @param {number} qualificationId 资质文件ID
     */
    async downloadQualificationFileById(qualificationId) {
        try {
            window.open(`/api/qualifications/${qualificationId}/download`);
        } catch (error) {
            console.error('下载资质文件失败:', error);
            if (window.showAlert) {
                window.showAlert('下载资质文件失败', 'danger');
            }
        }
    }

    /**
     * 删除资质文件（通过资质键）- 用于单文件资质
     * @param {string} qualKey 资质键名
     */
    async deleteQualificationFile(qualKey) {
        if (!confirm('确定要删除这个资质文件吗？')) return;

        try {
            const response = await axios.delete(`/api/companies/${this.currentCompanyId}/qualifications/${qualKey}`);

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('资质文件删除成功', 'success');
                }
                // 隐藏状态显示
                const statusElement = document.getElementById(`profile-status-${qualKey}`);
                if (statusElement) {
                    statusElement.classList.add('d-none');
                    statusElement.innerHTML = '<small class="text-muted">未上传文件</small>';
                }
            } else {
                if (window.showAlert) {
                    window.showAlert('删除失败: ' + response.data.error, 'danger');
                }
            }
        } catch (error) {
            console.error('删除资质文件失败:', error);
            if (window.showAlert) {
                window.showAlert('删除资质文件失败', 'danger');
            }
        }
    }

    /**
     * 删除资质文件（通过文件ID）- 用于多文件资质
     * @param {number} qualificationId 资质文件ID
     */
    async deleteQualificationFileById(qualificationId) {
        if (!confirm('确定要删除这个资质文件吗？')) return;

        try {
            const response = await axios.delete(`/api/qualifications/${qualificationId}`);

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('资质文件删除成功', 'success');
                }
                // 重新加载资质文件列表
                await this.loadExistingQualifications();
            } else {
                if (window.showAlert) {
                    window.showAlert('删除失败: ' + response.data.error, 'danger');
                }
            }
        } catch (error) {
            console.error('删除资质文件失败:', error);
            if (window.showAlert) {
                window.showAlert('删除资质文件失败', 'danger');
            }
        }
    }

    /**
     * 格式化文件大小
     * @param {number} bytes 字节数
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 格式化时间
     * @param {string|number} timestamp 时间戳
     */
    formatDateTime(timestamp) {
        try {
            // 如果是字符串格式的时间戳（如"2025-09-26 13:24:24"）
            if (typeof timestamp === 'string') {
                return new Date(timestamp).toLocaleString('zh-CN');
            }
            // 如果是Unix时间戳数字
            else if (typeof timestamp === 'number') {
                return new Date(timestamp * 1000).toLocaleString('zh-CN');
            }
            // 其他情况直接转换
            return new Date(timestamp).toLocaleString('zh-CN');
        } catch (error) {
            console.error('时间格式化错误:', error, '原始时间戳:', timestamp);
            return timestamp || '未知时间';
        }
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 可以在这里添加其他事件监听器
    }

    // Getter methods
    getCurrentCompanyId() {
        return this.currentCompanyId;
    }

    getCurrentTab() {
        return this.currentTab;
    }
}

// 创建全局实例
window.companyProfileManager = new CompanyProfileManager();