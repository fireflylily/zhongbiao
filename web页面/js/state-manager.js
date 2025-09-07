/**
 * AI标书系统状态管理器
 * 负责跨页面状态保持和数据共享
 */
const StateManager = {
    // 存储键名常量
    KEYS: {
        API_KEY: 'ai_tender_api_key_encrypted',
        COMPANY_ID: 'current_company_id',
        UPLOAD_FILES: 'upload_files_info',
        PAGE_CONTEXT: 'page_context'
    },

    /**
     * 基础存储操作
     */
    set(key, value) {
        try {
            localStorage.setItem(key, typeof value === 'object' ? JSON.stringify(value) : value);
        } catch (e) {
            console.warn('存储失败:', e);
        }
    },

    get(key) {
        try {
            const value = localStorage.getItem(key);
            if (!value) return null;
            
            // 尝试解析JSON
            try {
                return JSON.parse(value);
            } catch {
                return value;
            }
        } catch (e) {
            console.warn('读取失败:', e);
            return null;
        }
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    clear() {
        localStorage.clear();
    },

    /**
     * 特定业务状态管理
     */
    
    // 公司ID管理
    setCompanyId(companyId) {
        this.set(this.KEYS.COMPANY_ID, companyId);
        // 同时更新URL参数（如果需要）
        this.updateUrlParam('companyId', companyId);
    },

    getCompanyId() {
        // 优先从URL获取，其次从存储获取
        const urlCompanyId = this.getUrlParam('companyId');
        if (urlCompanyId) {
            this.set(this.KEYS.COMPANY_ID, urlCompanyId);
            return urlCompanyId;
        }
        return this.get(this.KEYS.COMPANY_ID);
    },

    // API密钥管理
    setApiKey(apiKey) {
        this.set(this.KEYS.API_KEY, apiKey);
    },

    getApiKey() {
        return this.get(this.KEYS.API_KEY);
    },

    // 文件上传信息管理
    setUploadInfo(fileInfo) {
        this.set(this.KEYS.UPLOAD_FILES, fileInfo);
    },

    getUploadInfo() {
        return this.get(this.KEYS.UPLOAD_FILES) || {};
    },

    // 页面上下文管理
    setPageContext(context) {
        this.set(this.KEYS.PAGE_CONTEXT, {
            ...this.getPageContext(),
            ...context
        });
    },

    getPageContext() {
        return this.get(this.KEYS.PAGE_CONTEXT) || {};
    },

    /**
     * URL参数操作
     */
    getUrlParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },

    updateUrlParam(name, value) {
        const url = new URL(window.location);
        if (value) {
            url.searchParams.set(name, value);
        } else {
            url.searchParams.delete(name);
        }
        // 静默更新URL，不触发页面刷新
        window.history.replaceState({}, '', url);
    },

    /**
     * 页面导航
     */
    navigateToPage(page, params = {}) {
        let url = page;
        const queryParams = new URLSearchParams();
        
        // 添加参数
        Object.keys(params).forEach(key => {
            if (params[key]) {
                queryParams.set(key, params[key]);
            }
        });

        // 保持重要状态参数
        const companyId = this.getCompanyId();
        if (companyId && !params.companyId) {
            queryParams.set('companyId', companyId);
        }

        if (queryParams.toString()) {
            url += '?' + queryParams.toString();
        }

        window.location.href = url;
    },

    /**
     * 页面间消息传递
     */
    sendMessage(type, data) {
        const message = {
            type,
            data,
            timestamp: Date.now(),
            source: window.location.pathname
        };
        
        // 使用localStorage事件进行跨页面通信
        this.set('_message_' + Date.now(), message);
    },

    // 监听其他页面发送的消息
    onMessage(callback) {
        window.addEventListener('storage', (e) => {
            if (e.key && e.key.startsWith('_message_')) {
                try {
                    const message = JSON.parse(e.newValue);
                    callback(message);
                    // 清理消息
                    localStorage.removeItem(e.key);
                } catch (err) {
                    console.warn('消息解析失败:', err);
                }
            }
        });
    }
};

// 全局暴露
window.StateManager = StateManager;