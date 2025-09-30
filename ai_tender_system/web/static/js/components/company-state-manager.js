/**
 * 全局公司状态管理器
 * 用于在不同页面间同步选择的公司和项目信息
 */

class CompanyStateManager {
    constructor() {
        this.storageKey = 'selected_company_data';
        this.listeners = [];
    }

    /**
     * 保存选择的公司信息
     * @param {Object} companyData - 公司数据
     * @param {string} companyData.company_id - 公司ID
     * @param {string} companyData.company_name - 公司名称
     * @param {Object} [companyData.details] - 公司详细信息（可选）
     */
    setSelectedCompany(companyData) {
        if (!companyData || !companyData.company_id || !companyData.company_name) {
            console.error('无效的公司数据:', companyData);
            return false;
        }

        // 获取当前存储的数据（保留项目信息）
        const currentData = this.getSelectedCompany();

        const dataToStore = {
            company_id: companyData.company_id,
            company_name: companyData.company_name,
            details: companyData.details || null,
            project_name: currentData?.project_name || null,
            project_number: currentData?.project_number || null,
            timestamp: Date.now()
        };

        try {
            localStorage.setItem(this.storageKey, JSON.stringify(dataToStore));
            console.log('公司状态已保存:', dataToStore);

            // 通知所有监听器
            this.notifyListeners(dataToStore);
            return true;
        } catch (error) {
            console.error('保存公司状态失败:', error);
            return false;
        }
    }

    /**
     * 获取当前选择的公司信息
     * @returns {Object|null} 公司数据或null
     */
    getSelectedCompany() {
        try {
            const storedData = localStorage.getItem(this.storageKey);
            if (!storedData) {
                return null;
            }

            const companyData = JSON.parse(storedData);

            // 检查数据是否过期（24小时）
            const maxAge = 24 * 60 * 60 * 1000; // 24小时
            if (Date.now() - companyData.timestamp > maxAge) {
                console.log('公司状态已过期，清除数据');
                this.clearSelectedCompany();
                return null;
            }

            return companyData;
        } catch (error) {
            console.error('读取公司状态失败:', error);
            return null;
        }
    }

    /**
     * 清除选择的公司信息
     */
    clearSelectedCompany() {
        try {
            localStorage.removeItem(this.storageKey);
            console.log('公司状态已清除');

            // 通知所有监听器
            this.notifyListeners(null);
            return true;
        } catch (error) {
            console.error('清除公司状态失败:', error);
            return false;
        }
    }

    /**
     * 检查是否有选择的公司
     * @returns {boolean}
     */
    hasSelectedCompany() {
        return this.getSelectedCompany() !== null;
    }

    /**
     * 添加状态变更监听器
     * @param {Function} callback - 回调函数，参数为公司数据或null
     */
    addListener(callback) {
        if (typeof callback === 'function') {
            this.listeners.push(callback);
        }
    }

    /**
     * 移除状态变更监听器
     * @param {Function} callback - 要移除的回调函数
     */
    removeListener(callback) {
        const index = this.listeners.indexOf(callback);
        if (index > -1) {
            this.listeners.splice(index, 1);
        }
    }

    /**
     * 通知所有监听器状态变更
     * @private
     * @param {Object|null} companyData - 新的公司数据
     */
    notifyListeners(companyData) {
        this.listeners.forEach(callback => {
            try {
                callback(companyData);
            } catch (error) {
                console.error('监听器回调执行失败:', error);
            }
        });
    }

    /**
     * 更新公司详细信息（保持company_id和company_name不变）
     * @param {Object} details - 公司详细信息
     */
    updateCompanyDetails(details) {
        const currentCompany = this.getSelectedCompany();
        if (!currentCompany) {
            console.warn('没有选择的公司，无法更新详细信息');
            return false;
        }

        currentCompany.details = details;
        currentCompany.timestamp = Date.now();

        try {
            localStorage.setItem(this.storageKey, JSON.stringify(currentCompany));
            console.log('公司详细信息已更新:', details);

            // 通知所有监听器
            this.notifyListeners(currentCompany);
            return true;
        } catch (error) {
            console.error('更新公司详细信息失败:', error);
            return false;
        }
    }

    /**
     * 获取公司ID（简便方法）
     * @returns {string|null}
     */
    getSelectedCompanyId() {
        const company = this.getSelectedCompany();
        return company ? company.company_id : null;
    }

    /**
     * 获取公司名称（简便方法）
     * @returns {string|null}
     */
    getSelectedCompanyName() {
        const company = this.getSelectedCompany();
        return company ? company.company_name : null;
    }

    /**
     * 保存项目信息
     * @param {Object} projectData - 项目数据
     * @param {string} [projectData.project_name] - 项目名称
     * @param {string} [projectData.project_number] - 项目编号
     */
    setProjectInfo(projectData) {
        const currentCompany = this.getSelectedCompany();
        if (!currentCompany) {
            console.warn('没有选择的公司，无法保存项目信息');
            return false;
        }

        currentCompany.project_name = projectData.project_name || null;
        currentCompany.project_number = projectData.project_number || null;
        currentCompany.timestamp = Date.now();

        try {
            localStorage.setItem(this.storageKey, JSON.stringify(currentCompany));
            console.log('项目信息已保存:', projectData);

            // 通知所有监听器
            this.notifyListeners(currentCompany);
            return true;
        } catch (error) {
            console.error('保存项目信息失败:', error);
            return false;
        }
    }

    /**
     * 获取项目信息
     * @returns {Object|null} 项目数据或null
     */
    getProjectInfo() {
        const company = this.getSelectedCompany();
        if (!company) {
            return null;
        }

        return {
            project_name: company.project_name || null,
            project_number: company.project_number || null
        };
    }

    /**
     * 获取项目名称（简便方法）
     * @returns {string|null}
     */
    getProjectName() {
        const company = this.getSelectedCompany();
        return company?.project_name || null;
    }

    /**
     * 获取项目编号（简便方法）
     * @returns {string|null}
     */
    getProjectNumber() {
        const company = this.getSelectedCompany();
        return company?.project_number || null;
    }

    /**
     * 检查是否有项目信息
     * @returns {boolean}
     */
    hasProjectInfo() {
        const projectInfo = this.getProjectInfo();
        return !!(projectInfo?.project_name || projectInfo?.project_number);
    }
}

// 创建全局单例实例
window.companyStateManager = new CompanyStateManager();

// 调试方法（开发环境使用）
if (typeof window !== 'undefined' && window.location && window.location.hostname === 'localhost') {
    window.debugCompanyState = {
        get: () => window.companyStateManager.getSelectedCompany(),
        set: (data) => window.companyStateManager.setSelectedCompany(data),
        clear: () => window.companyStateManager.clearSelectedCompany(),
        has: () => window.companyStateManager.hasSelectedCompany(),
        getProject: () => window.companyStateManager.getProjectInfo(),
        setProject: (data) => window.companyStateManager.setProjectInfo(data)
    };
}