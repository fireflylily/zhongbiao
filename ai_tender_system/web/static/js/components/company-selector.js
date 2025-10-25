/**
 * 公司选择器组件 - 优化版
 * 提供统一的公司选择和管理功能
 */

// HTML模板配置
const TEMPLATES = {
    dropdown: (placeholder) => `
        <div class="company-selector">
            <div class="company-selector-input">
                <div class="input-group">
                    <input type="text" class="form-control" placeholder="${placeholder}" data-company-search readonly>
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-company-dropdown data-bs-toggle="dropdown">
                        <i class="bi bi-chevron-down"></i>
                    </button>
                    <div class="dropdown-menu dropdown-menu-end company-dropdown">
                        <div class="company-search-container" style="display: none;">
                            <div class="px-3 py-2">
                                <input type="text" class="form-control form-control-sm" placeholder="搜索公司..." data-search-input>
                            </div>
                            <div class="dropdown-divider"></div>
                        </div>
                        <div class="company-list" data-company-list></div>
                        <div class="dropdown-divider" data-actions-divider style="display: none;"></div>
                        <div class="company-actions" data-company-actions style="display: none;">
                            <button type="button" class="dropdown-item" data-add-company>
                                <i class="bi bi-plus-circle me-2"></i>添加新公司
                            </button>
                            <button type="button" class="dropdown-item" data-manage-companies>
                                <i class="bi bi-gear me-2"></i>管理公司
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
                    <div class="mt-2"><strong>地址:</strong> <span data-detail-address></span></div>
                </div>
            </div>
            <input type="hidden" data-company-value>
        </div>`,

    status: (type, message, icon = '') => `
        <div class="text-center py-3 ${type === 'error' ? 'text-danger' : 'text-muted'}">
            ${icon ? `<i class="${icon}"></i>` : type === 'loading' ? '<div class="search-loading-spinner"></div>' : ''}
            <div${type === 'loading' ? ' class="mt-2"' : ''}>${message}</div>
        </div>`,

    companyItem: (company, isActive) => `
        <button type="button" class="dropdown-item company-item ${isActive ? 'active' : ''}" data-company-id="${company.id}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="fw-semibold">${company.name}</div>
                    <div class="small text-muted">${company.unified_social_credit_code || '暂无代码'}</div>
                </div>
                <div class="text-end">
                    <div class="small text-muted">${company.contact_person || ''}</div>
                </div>
            </div>
        </button>`,

    form: () => {
        const fields = [
            { name: 'name', label: '公司名称 *', type: 'text', required: true, col: 6 },
            { name: 'unified_social_credit_code', label: '统一社会信用代码', type: 'text', col: 6 },
            { name: 'contact_person', label: '联系人', type: 'text', col: 6 },
            { name: 'contact_phone', label: '联系电话', type: 'tel', col: 6 },
            { name: 'address', label: '地址', type: 'textarea', rows: 2, col: 12 }
        ];

        return `<form data-add-company-form data-validate="true">
            <div class="row">
                ${fields.map(f => `
                    <div class="col-md-${f.col}">
                        <div class="mb-3">
                            <label class="form-label">${f.label}</label>
                            ${f.type === 'textarea'
                                ? `<textarea class="form-control" name="${f.name}" rows="${f.rows || 3}"></textarea>`
                                : `<input type="${f.type}" class="form-control" name="${f.name}"
                                    ${f.required ? 'data-validate-rule="required" required' : ''}>`}
                        </div>
                    </div>
                `).join('')}
            </div>
        </form>`;
    }
};

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
            syncGlobalState: true,
            api: { list: '/api/companies', create: '/api/companies', update: '/api/companies/{id}' },
            ...options
        };

        this.companies = [];
        this.selectedCompany = null;
        this.isLoading = false;
        this.searchTimeout = null;

        this.init();
    }

    async init() {
        this.createHTML();
        this.bindEvents();
        if (this.options.autoLoad) await this.loadCompanies();

        const presetValue = this.element.getAttribute('data-value');
        if (presetValue) this.selectCompany(parseInt(presetValue));
    }

    createHTML() {
        this.element.innerHTML = TEMPLATES.dropdown(this.options.placeholder);
        const hiddenInput = this.element.querySelector('[data-company-value]');
        hiddenInput.name = this.options.name || 'company_id';
        this.setupElements();
    }

    setupElements() {
        Object.assign(this, {
            searchInput: this.element.querySelector('[data-company-search]'),
            dropdownButton: this.element.querySelector('[data-company-dropdown]'),
            dropdown: this.element.querySelector('.company-dropdown'),
            searchContainer: this.element.querySelector('.company-search-container'),
            searchField: this.element.querySelector('[data-search-input]'),
            companyList: this.element.querySelector('[data-company-list]'),
            companyDetails: this.element.querySelector('[data-company-details]'),
            hiddenInput: this.element.querySelector('[data-company-value]'),
            actionsContainer: this.element.querySelector('[data-company-actions]'),
            actionsDivider: this.element.querySelector('[data-actions-divider]')
        });

        if (this.options.searchable) {
            this.searchInput.removeAttribute('readonly');
            this.searchContainer.style.display = 'block';
        }

        if (this.options.allowNew) {
            this.actionsContainer.style.display = 'block';
            this.actionsDivider.style.display = 'block';
        }
    }

    bindEvents() {
        if (this.options.searchable) {
            const handleSearch = (e) => this.handleSearch(e.target.value);
            this.searchInput.addEventListener('input', handleSearch);
            this.searchField.addEventListener('input', handleSearch);
            this.dropdown.addEventListener('shown.bs.dropdown', () => this.searchField.focus());
            this.searchField.addEventListener('click', (e) => e.stopPropagation());
        }

        this.element.querySelector('[data-add-company]')?.addEventListener('click', () => this.showAddCompanyModal());
        this.element.querySelector('[data-manage-companies]')?.addEventListener('click', () => this.showManageModal());
    }

    async loadCompanies() {
        this.isLoading = true;
        this.showStatus('loading', '加载中...');

        try {
            const response = await window.apiClient?.company.getCompanies();
            this.companies = response?.companies || response || [];
            this.renderCompanyList();
        } catch (error) {
            console.error('加载公司列表失败:', error);
            this.showStatus('error', '加载公司列表失败');
        } finally {
            this.isLoading = false;
        }
    }

    renderCompanyList(filteredCompanies = null) {
        const companies = filteredCompanies || this.companies;

        if (companies.length === 0) {
            this.companyList.innerHTML = TEMPLATES.status('empty', '暂无公司数据', 'bi bi-building');
            return;
        }

        this.companyList.innerHTML = companies.map(c => TEMPLATES.companyItem(c, this.selectedCompany?.id === c.id)).join('');

        this.companyList.onclick = (e) => {
            const item = e.target.closest('.company-item');
            if (item) {
                this.selectCompany(parseInt(item.getAttribute('data-company-id')));
                bootstrap.Dropdown.getInstance(this.dropdownButton)?.hide();
            }
        };
    }

    handleSearch(query) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            if (!query.trim()) return this.renderCompanyList();

            const filtered = this.companies.filter(c =>
                c.name.toLowerCase().includes(query.toLowerCase()) ||
                c.unified_social_credit_code?.includes(query) ||
                c.contact_person?.toLowerCase().includes(query.toLowerCase())
            );
            this.renderCompanyList(filtered);
        }, 300);
    }

    selectCompany(companyId) {
        const company = this.companies.find(c => c.id === companyId);
        if (!company) return;

        this.selectedCompany = company;
        this.searchInput.value = company.name;
        this.hiddenInput.value = company.id;

        if (this.options.showDetails) this.showCompanyDetails(company);

        this.companyList.querySelectorAll('.company-item').forEach(item => {
            item.classList.toggle('active', parseInt(item.getAttribute('data-company-id')) === companyId);
        });

        this.dispatchEvent('companySelected', { company });

        if (this.options.syncGlobalState && window.globalState) {
            window.globalState.setCompany(company.id, company.name, company);
            console.log('[CompanySelector] 已同步公司信息到全局状态:', company.name);
        }

        if (this.options.required) this.searchInput.classList.remove('is-invalid');
    }

    showCompanyDetails(company) {
        const fields = ['name', 'code', 'contact', 'phone', 'address'];
        const mapping = {
            name: company.name,
            code: company.unified_social_credit_code,
            contact: company.contact_person,
            phone: company.contact_phone,
            address: company.address
        };

        fields.forEach(field => {
            const el = this.element.querySelector(`[data-detail-${field}]`);
            el.textContent = mapping[field] || '暂无';
        });

        this.companyDetails.style.display = 'block';
    }

    showStatus(type, message) {
        this.companyList.innerHTML = TEMPLATES.status(type, message);
    }

    showAddCompanyModal() {
        window.modalManager?.show({
            title: '添加新公司',
            content: TEMPLATES.form(),
            size: 'lg',
            onConfirm: (modal) => this.handleAddCompany(modal)
        });
    }

    async handleAddCompany(modal) {
        const form = modal.querySelector('[data-add-company-form]');
        if (!window.validator?.validateForm(form)) return false;

        const companyData = Object.fromEntries(new FormData(form));

        try {
            const response = await window.apiClient?.company.createCompany(companyData);
            const newCompany = response?.company || response;

            this.companies.push(newCompany);
            this.renderCompanyList();
            this.selectCompany(newCompany.id);

            window.notifications?.success('公司添加成功');
            return true;
        } catch (error) {
            console.error('添加公司失败:', error);
            window.notifications?.error('添加公司失败: ' + error.message);
            return false;
        }
    }

    showManageModal() {
        window.open('/companies', '_blank');
    }

    validate() {
        if (this.options.required && !this.selectedCompany) {
            this.searchInput.classList.add('is-invalid');
            return false;
        }
        this.searchInput.classList.remove('is-invalid');
        return true;
    }

    clear() {
        this.selectedCompany = null;
        this.searchInput.value = '';
        this.hiddenInput.value = '';
        this.companyDetails.style.display = 'none';

        this.companyList.querySelectorAll('.company-item').forEach(item => item.classList.remove('active'));

        this.dispatchEvent('companyCleared');

        if (this.options.syncGlobalState && window.globalState) {
            window.globalState.clearCompany();
            console.log('[CompanySelector] 已清空全局状态中的公司信息');
        }
    }

    getSelectedCompany() {
        return this.selectedCompany;
    }

    setSelectedCompany(companyId) {
        this.selectCompany(companyId);
    }

    refresh() {
        return this.loadCompanies();
    }

    dispatchEvent(eventName, detail = {}) {
        this.element.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

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