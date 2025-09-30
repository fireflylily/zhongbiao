/**
 * 企业信息库管理模块
 * 负责企业基础信息、资质文件、人员档案、财务文档的管理
 */

class CompanyProfileManager {
    constructor() {
        this.currentCompanyId = null;
        this.currentTab = 'basic';
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
                            <i class="bi bi-people text-warning"></i> 人员信息
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
                                ${this.renderPersonnelSection()}
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

        // 如果切换到资质页面，延迟加载资质文件状态
        if (tabName === 'qualification') {
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
     */
    renderPersonnelSection() {
        return `
            <div class="personnel-section">
                <div class="mb-4">
                    <h6 class="text-warning mb-3"><i class="bi bi-people"></i> 人员档案</h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('法定代表人身份证（正面）', 'legal_id', 'bi-person-badge')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('法定代表人身份证（反面）', 'legal_id_back', 'bi-person-badge')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('被授权人身份证', 'auth_id', 'bi-person-check')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('项目经理简历', 'project_manager_resume', 'bi-person-badge')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('团队成员简历', 'team_resume', 'bi-file-person')}
                        </div>
                    </div>
                </div>
                <div class="mb-4">
                    <h6 class="text-secondary mb-3"><i class="bi bi-shield-check"></i> 社保资质</h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('社会保险参保证明', 'social_security', 'bi-people')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderPersonnelItem('员工社保证明', 'employee_social_security', 'bi-file-medical')}
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
        return `
            <div class="financial-section">
                <div class="mb-4">
                    <h6 class="text-danger mb-3"><i class="bi bi-bank"></i> 财务文档</h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            ${this.renderFinancialItem('近三年财务审计报告', 'financial_audit', 'bi-graph-up')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderFinancialItem('财务审计报告', 'audit_report', 'bi-file-earmark-check')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderFinancialItem('纳税人资格证明', 'taxpayer_certificate', 'bi-receipt')}
                        </div>
                        <div class="col-md-6">
                            ${this.renderFinancialItem('银行开户许可证', 'bank_account', 'bi-bank')}
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
                <div class="text-center">
                    <button type="button" class="btn btn-danger btn-lg" onclick="window.companyProfileManager.saveFinancialInfo()">
                        <i class="bi bi-save"></i> 保存财务信息
                    </button>
                </div>
            </div>
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
            // 已移除授权人身份证相关项
            // { key: 'auth_id_front', name: '授权人身份证（正面）', icon: 'bi-person-check', category: 'basic' },
            // { key: 'auth_id_back', name: '授权人身份证（反面）', icon: 'bi-person-check', category: 'basic' },

            // ISO体系认证
            { key: 'iso9001', name: '质量管理体系认证（ISO9001）', icon: 'bi-award', category: 'iso' },
            { key: 'iso14001', name: '环境管理体系认证（ISO14001）', icon: 'bi-tree', category: 'iso' },
            { key: 'iso45001', name: '职业健康安全管理体系认证（ISO45001）', icon: 'bi-shield-check', category: 'iso' },
            { key: 'iso20000', name: '信息技术服务管理体系认证（ISO20000）', icon: 'bi-gear', category: 'iso' },
            { key: 'iso27001', name: '信息安全管理体系认证（ISO27001）', icon: 'bi-shield-lock', category: 'iso' },

            // 信用资质
            { key: 'credit_dishonest', name: '信用中国-失信被执行人查询', icon: 'bi-shield-x', category: 'credit' },
            { key: 'credit_corruption', name: '信用中国-重大税收违法案件查询', icon: 'bi-exclamation-triangle', category: 'credit' },
            { key: 'credit_tax', name: '信用中国-政府采购严重违法失信查询', icon: 'bi-flag', category: 'credit' },
            { key: 'credit_procurement', name: '政府采购信用查询结果', icon: 'bi-check-circle', category: 'credit' },

            // 知识产权和行业资质
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

        return `
            <div class="card mb-3 shadow-sm ${borderClass}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="flex-grow-1">
                            <i class="bi ${icon} me-2 text-primary"></i>
                            <span>${name}</span>
                            ${requiredBadge}
                        </div>
                        <div class="btn-group">
                            <input type="file" class="d-none" id="profile-qual-${id}" accept=".pdf,.jpg,.png,.jpeg" onchange="window.companyProfileManager.uploadQualificationFile('${id}', this)">
                            <button class="btn btn-sm btn-outline-primary" onclick="document.getElementById('profile-qual-${id}').click()" title="上传文件">
                                <i class="bi bi-upload"></i>
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
        return `
            <div class="financial-item">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center">
                                <i class="bi ${icon} text-danger me-2"></i>
                                <span>${name}</span>
                            </div>
                            <div>
                                <input type="file" class="d-none" id="fin-${id}" accept=".pdf,.xls,.xlsx" onchange="window.companyProfileManager.uploadFinancialFile('${id}', this)">
                                <button class="btn btn-sm btn-outline-danger" onclick="document.getElementById('fin-${id}').click()">
                                    <i class="bi bi-upload"></i>
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
     * 保存基础信息
     */
    async saveBasicInfo() {
        const data = {
            companyName: document.getElementById('prof-companyName').value,
            establishDate: document.getElementById('prof-establishDate').value,
            legalRepresentative: document.getElementById('prof-legalRepresentative').value,
            legalRepresentativePosition: document.getElementById('prof-legalRepresentativePosition').value,
            socialCreditCode: document.getElementById('prof-socialCreditCode').value,
            registeredCapital: document.getElementById('prof-registeredCapital').value,
            companyType: document.getElementById('prof-companyType').value,
            registeredAddress: document.getElementById('prof-registeredAddress').value,
            fixedPhone: document.getElementById('prof-fixedPhone').value,
            email: document.getElementById('prof-email').value,
            businessScope: document.getElementById('prof-businessScope').value,
            companyDescription: document.getElementById('prof-companyDescription').value
        };

        try {
            const response = await axios.put('/api/companies/' + this.currentCompanyId, data);
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
        const data = {
            bank_name: document.getElementById('prof-bankName').value,
            bank_account: document.getElementById('prof-bankAccount').value
        };

        try {
            const response = await axios.put('/api/companies/' + this.currentCompanyId, data);
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
     * 上传资质文件
     * @param {string} qualificationId 资质ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadQualificationFile(qualificationId, input) {
        const file = input.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append(`qualifications[${qualificationId}]`, file);

            const response = await axios.post(`/api/companies/${this.currentCompanyId}/qualifications/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('资质文件上传成功', 'success');
                }
                this.updateQualificationStatus(qualificationId, file.name, 'success');
            }
        } catch (error) {
            console.error('资质文件上传失败:', error);
            if (window.showAlert) {
                window.showAlert('上传失败：' + error.message, 'danger');
            }
            this.updateQualificationStatus(qualificationId, '上传失败', 'error');
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

            const response = await axios.post(`/api/companies/${this.currentCompanyId}/qualifications/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
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
     * 上传财务文件
     * @param {string} financialId 财务ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadFinancialFile(financialId, input) {
        const file = input.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append(`qualifications[${financialId}]`, file);

            const response = await axios.post(`/api/companies/${this.currentCompanyId}/qualifications/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('财务文件上传成功', 'success');
                }
                this.updateFinancialStatus(financialId, file.name, 'success');
            }
        } catch (error) {
            console.error('财务文件上传失败:', error);
            if (window.showAlert) {
                window.showAlert('上传失败：' + error.message, 'danger');
            }
            this.updateFinancialStatus(financialId, '上传失败', 'error');
        }
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
     * 刷新资质文件显示
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
            console.log('资质文件显示已更新:', qualKey);
        } else {
            console.error('无法更新资质文件显示 - statusElement:', statusElement, 'fileInfo:', fileInfo);
        }
    }

    /**
     * 下载资质文件
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
     * 删除资质文件
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