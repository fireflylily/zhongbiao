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
        const oldCompanyId = this.get(this.KEYS.COMPANY_ID);
        this.set(this.KEYS.COMPANY_ID, companyId);
        // 同时更新URL参数（如果需要）
        this.updateUrlParam('companyId', companyId);
        
        // 广播公司状态变更（如果值有变化）
        if (oldCompanyId !== companyId) {
            this.broadcastStateChange('companyId', companyId, oldCompanyId);
        }
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
    },

    /**
     * 增强的跨页面状态管理
     */
    
    // 广播状态变更
    broadcastStateChange(key, newValue, oldValue) {
        const changeEvent = {
            type: 'stateChange',
            key: key,
            newValue: newValue,
            oldValue: oldValue,
            timestamp: Date.now(),
            source: window.location.pathname
        };
        
        console.log('[StateManager] 广播状态变更:', changeEvent);
        
        // 触发storage事件以通知其他页面
        const eventKey = '_state_change_' + Date.now() + '_' + Math.random();
        localStorage.setItem(eventKey, JSON.stringify(changeEvent));
        
        // 短暂延迟后清理事件数据
        setTimeout(() => {
            localStorage.removeItem(eventKey);
        }, 100);
    },
    
    // 监听状态变更
    onStateChange(callback) {
        window.addEventListener('storage', (e) => {
            if (e.key && e.key.startsWith('_state_change_') && e.newValue) {
                try {
                    const changeEvent = JSON.parse(e.newValue);
                    // 不处理来自当前页面的变更事件
                    if (changeEvent.source !== window.location.pathname) {
                        console.log('[StateManager] 接收到状态变更:', changeEvent);
                        callback(changeEvent);
                    }
                } catch (err) {
                    console.warn('[StateManager] 状态变更事件解析失败:', err);
                }
            }
        });
    },
    
    // 监听特定键的状态变更
    onStateChangeByKey(key, callback) {
        this.onStateChange((changeEvent) => {
            if (changeEvent.key === key) {
                callback(changeEvent.newValue, changeEvent.oldValue, changeEvent);
            }
        });
    },
    
    // 验证公司状态一致性
    validateCompanyState() {
        const companyId = this.getCompanyId();
        const urlCompanyId = this.getUrlParam('companyId');
        const storedCompanyId = this.get(this.KEYS.COMPANY_ID);
        
        console.log('[StateManager] 公司状态验证:', {
            current: companyId,
            url: urlCompanyId, 
            stored: storedCompanyId
        });
        
        // 如果状态不一致，使用优先级进行同步
        if (urlCompanyId && urlCompanyId !== storedCompanyId) {
            console.log('[StateManager] URL参数优先，同步存储状态');
            this.set(this.KEYS.COMPANY_ID, urlCompanyId);
            return urlCompanyId;
        }
        
        return companyId;
    },
    
    // 强制同步所有页面状态
    syncAllPages() {
        const currentState = {
            companyId: this.getCompanyId(),
            timestamp: Date.now()
        };
        
        console.log('[StateManager] 强制同步所有页面状态:', currentState);
        
        this.sendMessage('syncState', currentState);
    }
};

// 全局暴露
window.StateManager = StateManager;