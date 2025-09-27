/**
 * 公司选择器组件
 * 提供统一的公司选择和管理功能
 */

class CompanySelectorComponent {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            placeholder: '请选择公司',
            allowNew: true,
            searchable: true,
            required: false,
            autoLoad: true,
            showDetails: true,
            api: {
                list: '/api/companies',
                create: '/api/companies',
                update: '/api/companies/{id}'
            },
            ...options
        };

        this.companies = [];
        this.selectedCompany = null;
        this.isLoading = false;
        this.searchTimeout = null;

        this.init();
    }

    /**
     * 初始化组件
     */
    async init() {
        this.createHTML();
        this.bindEvents();

        if (this.options.autoLoad) {
            await this.loadCompanies();
        }

        // 如果有预设值，设置选中状态
        const presetValue = this.element.getAttribute('data-value');
        if (presetValue) {
            this.selectCompany(parseInt(presetValue));
        }
    }

    /**
     * 创建HTML结构
     */
    createHTML() {
        this.element.innerHTML = `
            <div class="company-selector">
                <div class="company-selector-input">
                    <div class="input-group">
                        <input type="text"
                               class="form-control"
                               placeholder="${this.options.placeholder}"
                               data-company-search
                               readonly>
                        <button class="btn btn-outline-secondary dropdown-toggle"
                                type="button"
                                data-company-dropdown
                                data-bs-toggle="dropdown">
                            <i class="bi bi-chevron-down"></i>
                        </button>
                        <div class="dropdown-menu dropdown-menu-end company-dropdown">
                            <div class="company-search-container" style="display: none;">
                                <div class="px-3 py-2">
                                    <input type="text"
                                           class="form-control form-control-sm"
                                           placeholder="搜索公司..."
                                           data-search-input>
                                </div>
                                <div class="dropdown-divider"></div>
                            </div>
                            <div class="company-list" data-company-list>
                                <div class="text-center py-3">
                                    <div class="search-loading-spinner"></div>
                                    <div class="mt-2 text-muted">加载中...</div>
                                </div>
                            </div>
                            <div class="dropdown-divider" data-actions-divider style="display: none;"></div>
                            <div class="company-actions" data-company-actions style="display: none;">
                                <button type="button"
                                        class="dropdown-item"
                                        data-add-company>
                                    <i class="bi bi-plus-circle me-2"></i>
                                    添加新公司
                                </button>
                                <button type="button"
                                        class="dropdown-item"
                                        data-manage-companies>
                                    <i class="bi bi-gear me-2"></i>
                                    管理公司
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="company-details mt-2" data-company-details style="display: none;">
                    <div class="card card-body small bg-light">
                        <div class="row">
                            <div class="col-md-6">
                                <strong>公司全称:</strong> <span data-detail-name></span><br>
                                <strong>统一社会信用代码:</strong> <span data-detail-code></span>
                            </div>
                            <div class="col-md-6">
                                <strong>联系人:</strong> <span data-detail-contact></span><br>
                                <strong>联系电话:</strong> <span data-detail-phone></span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <strong>地址:</strong> <span data-detail-address></span>
                        </div>
                    </div>
                </div>
                <input type="hidden" data-company-value name="${this.options.name || 'company_id'}">
            </div>
        `;

        this.setupElements();
    }

    /**
     * 设置元素引用
     */
    setupElements() {
        this.searchInput = this.element.querySelector('[data-company-search]');
        this.dropdownButton = this.element.querySelector('[data-company-dropdown]');
        this.dropdown = this.element.querySelector('.company-dropdown');
        this.searchContainer = this.element.querySelector('.company-search-container');
        this.searchField = this.element.querySelector('[data-search-input]');
        this.companyList = this.element.querySelector('[data-company-list]');
        this.companyDetails = this.element.querySelector('[data-company-details]');
        this.hiddenInput = this.element.querySelector('[data-company-value]');
        this.actionsContainer = this.element.querySelector('[data-company-actions]');
        this.actionsDivider = this.element.querySelector('[data-actions-divider]');

        // 如果启用搜索功能
        if (this.options.searchable) {
            this.searchInput.removeAttribute('readonly');
            this.searchContainer.style.display = 'block';
        }

        // 如果允许添加新公司
        if (this.options.allowNew) {
            this.actionsContainer.style.display = 'block';
            this.actionsDivider.style.display = 'block';
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 搜索功能
        if (this.options.searchable) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });

            this.searchField.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // 下拉框显示时聚焦搜索框
        this.dropdown.addEventListener('shown.bs.dropdown', () => {
            if (this.options.searchable) {
                this.searchField.focus();
            }
        });

        // 添加新公司
        const addButton = this.element.querySelector('[data-add-company]');
        addButton?.addEventListener('click', () => {
            this.showAddCompanyModal();
        });

        // 管理公司
        const manageButton = this.element.querySelector('[data-manage-companies]');
        manageButton?.addEventListener('click', () => {
            this.showManageModal();
        });

        // 阻止下拉框关闭
        this.searchField?.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    /**
     * 加载公司列表
     */
    async loadCompanies() {
        this.isLoading = true;
        this.showLoading();

        try {
            const response = await window.apiClient?.company.getCompanies();
            this.companies = response?.companies || response || [];
            this.renderCompanyList();
        } catch (error) {
            console.error('加载公司列表失败:', error);
            this.showError('加载公司列表失败');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * 渲染公司列表
     */
    renderCompanyList(filteredCompanies = null) {
        const companies = filteredCompanies || this.companies;

        if (companies.length === 0) {
            this.companyList.innerHTML = `
                <div class="text-center py-3 text-muted">
                    <i class="bi bi-building"></i>
                    <div>暂无公司数据</div>
                </div>
            `;
            return;
        }

        const listHTML = companies.map(company => `
            <button type="button"
                    class="dropdown-item company-item ${this.selectedCompany?.id === company.id ? 'active' : ''}"
                    data-company-id="${company.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="fw-semibold">${company.name}</div>
                        <div class="small text-muted">${company.unified_social_credit_code || '暂无代码'}</div>
                    </div>
                    <div class="text-end">
                        <div class="small text-muted">${company.contact_person || ''}</div>
                    </div>
                </div>
            </button>
        `).join('');

        this.companyList.innerHTML = listHTML;

        // 绑定点击事件
        this.companyList.addEventListener('click', (e) => {
            const companyItem = e.target.closest('.company-item');
            if (companyItem) {
                const companyId = parseInt(companyItem.getAttribute('data-company-id'));
                this.selectCompany(companyId);

                // 关闭下拉框
                const bsDropdown = bootstrap.Dropdown.getInstance(this.dropdownButton);
                bsDropdown?.hide();
            }
        });
    }

    /**
     * 处理搜索
     */
    handleSearch(query) {
        clearTimeout(this.searchTimeout);

        this.searchTimeout = setTimeout(() => {
            if (!query.trim()) {
                this.renderCompanyList();
                return;
            }

            const filteredCompanies = this.companies.filter(company =>
                company.name.toLowerCase().includes(query.toLowerCase()) ||
                (company.unified_social_credit_code && company.unified_social_credit_code.includes(query)) ||
                (company.contact_person && company.contact_person.toLowerCase().includes(query.toLowerCase()))
            );

            this.renderCompanyList(filteredCompanies);
        }, 300);
    }

    /**
     * 选择公司
     */
    selectCompany(companyId) {
        const company = this.companies.find(c => c.id === companyId);
        if (!company) return;

        this.selectedCompany = company;
        this.searchInput.value = company.name;
        this.hiddenInput.value = company.id;

        // 显示公司详情
        if (this.options.showDetails) {
            this.showCompanyDetails(company);
        }

        // 更新列表中的选中状态
        this.companyList.querySelectorAll('.company-item').forEach(item => {
            item.classList.toggle('active',
                parseInt(item.getAttribute('data-company-id')) === companyId
            );
        });

        // 触发选择事件
        this.dispatchEvent('companySelected', { company });

        // 如果是必填项，移除验证错误
        if (this.options.required) {
            this.searchInput.classList.remove('is-invalid');
        }
    }

    /**
     * 显示公司详情
     */
    showCompanyDetails(company) {
        const detailElements = {
            name: this.element.querySelector('[data-detail-name]'),
            code: this.element.querySelector('[data-detail-code]'),
            contact: this.element.querySelector('[data-detail-contact]'),
            phone: this.element.querySelector('[data-detail-phone]'),
            address: this.element.querySelector('[data-detail-address]')
        };

        detailElements.name.textContent = company.name || '';
        detailElements.code.textContent = company.unified_social_credit_code || '暂无';
        detailElements.contact.textContent = company.contact_person || '暂无';
        detailElements.phone.textContent = company.contact_phone || '暂无';
        detailElements.address.textContent = company.address || '暂无';

        this.companyDetails.style.display = 'block';
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        this.companyList.innerHTML = `
            <div class="text-center py-3">
                <div class="search-loading-spinner"></div>
                <div class="mt-2 text-muted">加载中...</div>
            </div>
        `;
    }

    /**
     * 显示错误信息
     */
    showError(message) {
        this.companyList.innerHTML = `
            <div class="text-center py-3 text-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <div>${message}</div>
            </div>
        `;
    }

    /**
     * 显示添加公司模态框
     */
    showAddCompanyModal() {
        // 这里可以集成到模态框管理器中
        window.modalManager?.show({
            title: '添加新公司',
            content: this.getAddCompanyForm(),
            size: 'lg',
            onConfirm: (modal) => this.handleAddCompany(modal)
        });
    }

    /**
     * 获取添加公司表单
     */
    getAddCompanyForm() {
        return `
            <form data-add-company-form data-validate="true">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">公司名称 *</label>
                            <input type="text" class="form-control" name="name"
                                   data-validate-rule="required" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">统一社会信用代码</label>
                            <input type="text" class="form-control" name="unified_social_credit_code">
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">联系人</label>
                            <input type="text" class="form-control" name="contact_person">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">联系电话</label>
                            <input type="tel" class="form-control" name="contact_phone">
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">地址</label>
                    <textarea class="form-control" name="address" rows="2"></textarea>
                </div>
            </form>
        `;
    }

    /**
     * 处理添加公司
     */
    async handleAddCompany(modal) {
        const form = modal.querySelector('[data-add-company-form]');
        if (!window.validator?.validateForm(form)) {
            return false; // 阻止关闭模态框
        }

        const formData = new FormData(form);
        const companyData = Object.fromEntries(formData);

        try {
            const response = await window.apiClient?.company.createCompany(companyData);
            const newCompany = response?.company || response;

            // 添加到列表并选中
            this.companies.push(newCompany);
            this.renderCompanyList();
            this.selectCompany(newCompany.id);

            window.notifications?.success('公司添加成功');
            return true; // 允许关闭模态框
        } catch (error) {
            console.error('添加公司失败:', error);
            window.notifications?.error('添加公司失败: ' + error.message);
            return false;
        }
    }

    /**
     * 显示管理模态框
     */
    showManageModal() {
        // 可以跳转到公司管理页面或显示管理模态框
        window.open('/companies', '_blank');
    }

    /**
     * 验证选择
     */
    validate() {
        if (this.options.required && !this.selectedCompany) {
            this.searchInput.classList.add('is-invalid');
            return false;
        }

        this.searchInput.classList.remove('is-invalid');
        return true;
    }

    /**
     * 清空选择
     */
    clear() {
        this.selectedCompany = null;
        this.searchInput.value = '';
        this.hiddenInput.value = '';
        this.companyDetails.style.display = 'none';

        this.companyList.querySelectorAll('.company-item').forEach(item => {
            item.classList.remove('active');
        });

        this.dispatchEvent('companyCleared');
    }

    /**
     * 获取选中的公司
     */
    getSelectedCompany() {
        return this.selectedCompany;
    }

    /**
     * 设置选中的公司
     */
    setSelectedCompany(companyId) {
        this.selectCompany(companyId);
    }

    /**
     * 刷新公司列表
     */
    refresh() {
        return this.loadCompanies();
    }

    /**
     * 触发自定义事件
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, { detail });
        this.element.dispatchEvent(event);
    }

    /**
     * 销毁组件
     */
    destroy() {
        clearTimeout(this.searchTimeout);
        this.element.innerHTML = '';
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    const selectorElements = document.querySelectorAll('[data-company-selector]');
    selectorElements.forEach(element => {
        const options = JSON.parse(element.getAttribute('data-company-selector') || '{}');
        new CompanySelectorComponent(element, options);
    });
});

// 导出给其他模块使用
window.CompanySelectorComponent = CompanySelectorComponent;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = CompanySelectorComponent;
}