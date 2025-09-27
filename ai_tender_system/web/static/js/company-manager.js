/*!
 * 统一公司管理模块
 * 提供公司数据管理、状态管理、缓存等功能
 */

class CompanyAPIClient {
    constructor() {
        this.baseURL = CompanyConfig.api.baseUrl;
        this.timeout = CompanyConfig.api.timeout;
        this.retryAttempts = CompanyConfig.api.retryAttempts;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        let lastError;
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(url, config);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;
            } catch (error) {
                lastError = error;
                console.warn(`API请求失败 (尝试 ${attempt}/${this.retryAttempts}):`, error.message);

                if (attempt < this.retryAttempts) {
                    await this.delay(1000 * attempt); // 指数退避
                }
            }
        }

        this.handleError(lastError);
        throw lastError;
    }

    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    handleError(error) {
        console.error('API请求失败:', error);
        // 可以在这里添加用户通知逻辑
    }

    // API方法
    async getCompanies() {
        const response = await this.request('');
        return response.success ? response.data : [];
    }

    async getCompanyDetail(id) {
        const response = await this.request(`/${id}`);
        return response.success ? response.company : null;
    }

    async createCompany(data) {
        return await this.request('', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateCompany(id, data) {
        return await this.request(`/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteCompany(id) {
        return await this.request(`/${id}`, {
            method: 'DELETE'
        });
    }

    async getCompanyQualifications(id) {
        const response = await this.request(`/${id}/qualifications`);
        return response.success ? response.qualifications : {};
    }

    async uploadQualifications(id, formData) {
        return await this.request(`/${id}/qualifications/upload`, {
            method: 'POST',
            headers: {}, // 让浏览器自动设置Content-Type
            body: formData
        });
    }

    async deleteQualification(id, qualificationKey) {
        return await this.request(`/${id}/qualifications/${qualificationKey}`, {
            method: 'DELETE'
        });
    }
}

class CompanyDataCache {
    constructor() {
        this.cache = new Map();
        this.ttl = CompanyConfig.cache.ttl;
        this.maxSize = CompanyConfig.cache.maxSize;
    }

    set(key, data) {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;

        if (Date.now() - item.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }

        return item.data;
    }

    invalidate(key) {
        if (key) {
            this.cache.delete(key);
        } else {
            this.cache.clear();
        }
    }

    invalidateCompany(companyId) {
        // 删除特定公司相关的所有缓存
        const patterns = [
            CompanyConfig.cache.keys.company.replace('{id}', companyId),
            CompanyConfig.cache.keys.qualifications.replace('{id}', companyId)
        ];

        for (const key of this.cache.keys()) {
            for (const pattern of patterns) {
                if (key === pattern) {
                    this.cache.delete(key);
                }
            }
        }

        // 同时清除公司列表缓存
        this.invalidate(CompanyConfig.cache.keys.companies);
    }
}

class CompanySelector {
    constructor(selectElementId, options = {}) {
        this.selectElement = document.getElementById(selectElementId);
        this.options = {
            placeholder: '请选择公司...',
            showManageButton: false,
            allowEmpty: true,
            onSelectionChange: null,
            ...options
        };

        if (!this.selectElement) {
            console.warn(`公司选择器初始化失败: 找不到元素 ${selectElementId}`);
            return;
        }

        this.init();
    }

    init() {
        // 绑定选择变化事件
        this.selectElement.addEventListener('change', (e) => {
            const companyId = e.target.value;
            if (this.options.onSelectionChange) {
                this.options.onSelectionChange(companyId);
            }
        });
    }

    async loadOptions(companies) {
        if (!this.selectElement) return;

        // 清空现有选项
        this.selectElement.innerHTML = '';

        // 添加占位符选项
        if (this.options.allowEmpty) {
            const placeholderOption = document.createElement('option');
            placeholderOption.value = '';
            placeholderOption.textContent = this.options.placeholder;
            this.selectElement.appendChild(placeholderOption);
        }

        // 添加公司选项
        companies.forEach(company => {
            const option = document.createElement('option');
            option.value = company.company_id || company.id;
            option.textContent = company.company_name;
            this.selectElement.appendChild(option);
        });
    }

    setValue(companyId) {
        if (this.selectElement) {
            this.selectElement.value = companyId || '';
        }
    }

    getValue() {
        return this.selectElement ? this.selectElement.value : '';
    }

    disable(disabled = true) {
        if (this.selectElement) {
            this.selectElement.disabled = disabled;
        }
    }
}

class UnifiedCompanyManager extends EventTarget {
    constructor() {
        super();
        this.apiClient = new CompanyAPIClient();
        this.cache = new CompanyDataCache();
        this.currentCompanyId = null;
        this.companies = [];
        this.selectors = new Map();
        this.isLoading = false;

        // 初始化
        this.init();
    }

    init() {
        console.log('统一公司管理器初始化');
        this.loadCompanies();
    }

    // 注册选择器
    registerSelector(id, selector) {
        this.selectors.set(id, selector);

        // 如果已有公司数据，立即更新选择器
        if (this.companies.length > 0) {
            selector.loadOptions(this.companies);
        }
    }

    // 移除选择器
    unregisterSelector(id) {
        this.selectors.delete(id);
    }

    // 同步所有选择器
    syncAllSelectors(selectedCompanyId = null) {
        const companyId = selectedCompanyId || this.currentCompanyId;

        for (const [id, selector] of this.selectors) {
            selector.setValue(companyId);
        }
    }

    // 设置当前公司
    setCurrentCompany(companyId) {
        if (this.currentCompanyId !== companyId) {
            this.currentCompanyId = companyId;
            this.syncAllSelectors();

            // 触发公司变更事件
            this.dispatchEvent(new CustomEvent('companyChanged', {
                detail: { companyId, company: this.getCompanyById(companyId) }
            }));
        }
    }

    // 获取当前公司
    getCurrentCompany() {
        return this.getCompanyById(this.currentCompanyId);
    }

    // 根据ID获取公司信息
    getCompanyById(companyId) {
        if (!companyId) return null;
        return this.companies.find(c => c.company_id == companyId || c.id == companyId);
    }

    // 加载公司列表
    async loadCompanies(forceReload = false) {
        if (this.isLoading) return this.companies;

        const cacheKey = CompanyConfig.cache.keys.companies;

        if (!forceReload) {
            const cached = this.cache.get(cacheKey);
            if (cached) {
                this.companies = cached;
                this.updateAllSelectors();
                return this.companies;
            }
        }

        try {
            this.isLoading = true;
            console.log('加载公司列表...');

            const companies = await this.apiClient.getCompanies();
            this.companies = companies;

            // 缓存结果
            this.cache.set(cacheKey, companies);

            // 更新所有选择器
            this.updateAllSelectors();

            // 自动选择逻辑
            this.handleAutoSelection();

            // 触发加载完成事件
            this.dispatchEvent(new CustomEvent('companiesLoaded', {
                detail: { companies }
            }));

            console.log(`加载完成，共 ${companies.length} 家公司`);
            return companies;

        } catch (error) {
            console.error('加载公司列表失败:', error);
            this.companies = [];
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    // 更新所有选择器选项
    updateAllSelectors() {
        for (const [id, selector] of this.selectors) {
            selector.loadOptions(this.companies);
        }
    }

    // 自动选择逻辑
    handleAutoSelection() {
        // 如果只有一个公司，自动选择
        if (this.companies.length === 1 && !this.currentCompanyId) {
            this.setCurrentCompany(this.companies[0].company_id || this.companies[0].id);
        }
    }

    // 加载公司详情
    async loadCompanyDetail(companyId, forceReload = false) {
        if (!companyId) return null;

        const cacheKey = CompanyConfig.cache.keys.company.replace('{id}', companyId);

        if (!forceReload) {
            const cached = this.cache.get(cacheKey);
            if (cached) return cached;
        }

        try {
            const company = await this.apiClient.getCompanyDetail(companyId);
            if (company) {
                this.cache.set(cacheKey, company);
            }
            return company;
        } catch (error) {
            console.error('加载公司详情失败:', error);
            throw error;
        }
    }

    // 保存公司信息
    async saveCompany(data, companyId = null) {
        try {
            let result;
            if (companyId) {
                // 更新现有公司
                result = await this.apiClient.updateCompany(companyId, data);
            } else {
                // 创建新公司
                result = await this.apiClient.createCompany(data);
            }

            if (result.success) {
                // 清除相关缓存
                this.cache.invalidateCompany(companyId || result.company_id);

                // 重新加载公司列表
                await this.loadCompanies(true);

                // 触发保存成功事件
                this.dispatchEvent(new CustomEvent('companySaved', {
                    detail: { companyId: companyId || result.company_id, result }
                }));
            }

            return result;
        } catch (error) {
            console.error('保存公司失败:', error);
            throw error;
        }
    }

    // 删除公司
    async deleteCompany(companyId) {
        try {
            const result = await this.apiClient.deleteCompany(companyId);

            if (result.success) {
                // 清除相关缓存
                this.cache.invalidateCompany(companyId);

                // 如果删除的是当前选中公司，清除选择
                if (this.currentCompanyId == companyId) {
                    this.setCurrentCompany(null);
                }

                // 重新加载公司列表
                await this.loadCompanies(true);

                // 触发删除成功事件
                this.dispatchEvent(new CustomEvent('companyDeleted', {
                    detail: { companyId, result }
                }));
            }

            return result;
        } catch (error) {
            console.error('删除公司失败:', error);
            throw error;
        }
    }

    // 加载公司资质
    async loadCompanyQualifications(companyId, forceReload = false) {
        if (!companyId) return {};

        const cacheKey = CompanyConfig.cache.keys.qualifications.replace('{id}', companyId);

        if (!forceReload) {
            const cached = this.cache.get(cacheKey);
            if (cached) return cached;
        }

        try {
            const qualifications = await this.apiClient.getCompanyQualifications(companyId);
            this.cache.set(cacheKey, qualifications);
            return qualifications;
        } catch (error) {
            console.error('加载公司资质失败:', error);
            throw error;
        }
    }

    // 上传资质文件
    async uploadQualifications(companyId, formData) {
        try {
            const result = await this.apiClient.uploadQualifications(companyId, formData);

            if (result.success) {
                // 清除资质缓存
                const cacheKey = CompanyConfig.cache.keys.qualifications.replace('{id}', companyId);
                this.cache.invalidate(cacheKey);

                // 触发上传成功事件
                this.dispatchEvent(new CustomEvent('qualificationsUploaded', {
                    detail: { companyId, result }
                }));
            }

            return result;
        } catch (error) {
            console.error('上传资质文件失败:', error);
            throw error;
        }
    }

    // 删除资质文件
    async deleteQualification(companyId, qualificationKey) {
        try {
            const result = await this.apiClient.deleteQualification(companyId, qualificationKey);

            if (result.success) {
                // 清除资质缓存
                const cacheKey = CompanyConfig.cache.keys.qualifications.replace('{id}', companyId);
                this.cache.invalidate(cacheKey);

                // 触发删除成功事件
                this.dispatchEvent(new CustomEvent('qualificationDeleted', {
                    detail: { companyId, qualificationKey, result }
                }));
            }

            return result;
        } catch (error) {
            console.error('删除资质文件失败:', error);
            throw error;
        }
    }

    // 数据验证
    validateCompanyData(data) {
        const errors = [];
        const rules = CompanyConfig.validation;

        // 检查必填字段
        if (rules.companyName.required && !data.companyName?.trim()) {
            errors.push('公司名称为必填项');
        }

        // 检查公司名称长度
        if (data.companyName) {
            const name = data.companyName.trim();
            if (name.length < rules.companyName.minLength) {
                errors.push(`公司名称不能少于${rules.companyName.minLength}个字符`);
            }
            if (name.length > rules.companyName.maxLength) {
                errors.push(`公司名称不能超过${rules.companyName.maxLength}个字符`);
            }
        }

        // 检查统一社会信用代码格式
        if (data.socialCreditCode && !rules.socialCreditCode.pattern.test(data.socialCreditCode)) {
            errors.push(rules.socialCreditCode.message);
        }

        // 检查邮箱格式
        if (data.email && !rules.email.pattern.test(data.email)) {
            errors.push(rules.email.message);
        }

        // 检查电话格式
        if (data.fixedPhone && !rules.phone.pattern.test(data.fixedPhone)) {
            errors.push(rules.phone.message);
        }

        return errors;
    }

    // 清理缓存
    clearCache() {
        this.cache.invalidate();
    }

    // 获取统计信息
    getStats() {
        return {
            totalCompanies: this.companies.length,
            currentCompany: this.getCurrentCompany(),
            cacheSize: this.cache.cache.size,
            selectorsCount: this.selectors.size
        };
    }
}

// 创建全局实例
window.UnifiedCompanyManager = UnifiedCompanyManager;
window.CompanySelector = CompanySelector;

// 在DOM加载完成后初始化全局管理器
document.addEventListener('DOMContentLoaded', function() {
    if (!window.globalCompanyManager) {
        window.globalCompanyManager = new UnifiedCompanyManager();
    }
});

// 导出（支持不同的模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UnifiedCompanyManager, CompanySelector, CompanyAPIClient };
} else if (typeof define === 'function' && define.amd) {
    define([], function() {
        return { UnifiedCompanyManager, CompanySelector, CompanyAPIClient };
    });
}