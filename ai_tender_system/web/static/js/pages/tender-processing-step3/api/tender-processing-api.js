/**
 * 标书处理API封装
 * 统一错误处理、Loading状态、重试逻辑
 *
 * @module TenderProcessingAPI
 */

/**
 * API配置常量
 */
const API_CONFIG = {
    baseURL: '/api/tender-processing',
    retryAttempts: 3,
    timeout: 30000,
    retryDelay: 1000, // 初始重试延迟（毫秒）
};

/**
 * HTTP方法常量
 */
const HTTP_METHODS = {
    GET: 'GET',
    POST: 'POST',
    PUT: 'PUT',
    DELETE: 'DELETE'
};

/**
 * 标书处理API类
 */
class TenderProcessingAPI {
    constructor(config = {}) {
        this.baseURL = config.baseURL || API_CONFIG.baseURL;
        this.retryAttempts = config.retryAttempts || API_CONFIG.retryAttempts;
        this.timeout = config.timeout || API_CONFIG.timeout;
        this.retryDelay = config.retryDelay || API_CONFIG.retryDelay;
    }

    /**
     * 延迟函数（用于重试）
     * @param {number} ms - 延迟毫秒数
     * @returns {Promise} Promise对象
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 通用HTTP请求方法
     * @param {string} endpoint - API端点
     * @param {Object} options - 请求选项
     * @returns {Promise<Object>} API响应数据
     */
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        let lastError = null;

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                console.log(`[API] 请求 ${url} (尝试 ${attempt}/${this.retryAttempts})`);

                const response = await fetch(url, defaultOptions);
                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.message || '请求失败');
                }

                console.log(`[API] 请求成功 ${url}`);
                return data;

            } catch (error) {
                lastError = error;
                console.warn(`[API] 请求失败 ${url} (尝试 ${attempt}/${this.retryAttempts}):`, error.message);

                // 如果还有重试次数，等待后重试
                if (attempt < this.retryAttempts) {
                    const delayMs = this.retryDelay * Math.pow(2, attempt - 1); // 指数退避
                    console.log(`[API] 等待 ${delayMs}ms 后重试...`);
                    await this.delay(delayMs);
                }
            }
        }

        // 所有重试都失败
        const errorMessage = `API请求失败 (${this.retryAttempts}次重试): ${lastError.message}`;
        console.error(`[API] ${errorMessage}`);
        throw new Error(errorMessage);
    }

    /**
     * GET请求
     * @param {string} endpoint - API端点
     * @param {Object} params - 查询参数
     * @returns {Promise<Object>} API响应数据
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;

        return this.request(url, {
            method: HTTP_METHODS.GET
        });
    }

    /**
     * POST请求
     * @param {string} endpoint - API端点
     * @param {Object} data - 请求数据
     * @returns {Promise<Object>} API响应数据
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: HTTP_METHODS.POST,
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT请求
     * @param {string} endpoint - API端点
     * @param {Object} data - 请求数据
     * @returns {Promise<Object>} API响应数据
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: HTTP_METHODS.PUT,
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE请求
     * @param {string} endpoint - API端点
     * @returns {Promise<Object>} API响应数据
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: HTTP_METHODS.DELETE
        });
    }

    // ============================================
    // 需求相关API
    // ============================================

    /**
     * 加载需求列表
     * @param {string} taskId - 任务ID
     * @param {string} projectId - 项目ID
     * @param {Object} filters - 过滤条件
     * @returns {Promise<Object>} 需求数据
     */
    async loadRequirements(taskId, projectId, filters = {}) {
        return this.get(`/requirements/${taskId}`, {
            project_id: projectId,
            ...filters
        });
    }

    /**
     * 提取详细需求
     * @param {string} taskId - 任务ID
     * @returns {Promise<Object>} 提取结果
     */
    async extractDetailedRequirements(taskId) {
        return this.post(`/extract-detailed-requirements/${taskId}`);
    }

    /**
     * 更新需求
     * @param {string} requirementId - 需求ID
     * @param {Object} data - 更新数据
     * @returns {Promise<Object>} 更新结果
     */
    async updateRequirement(requirementId, data) {
        return this.put(`/requirements/${requirementId}`, data);
    }

    // ============================================
    // 章节相关API
    // ============================================

    /**
     * 加载章节列表
     * @param {string} taskId - 任务ID
     * @returns {Promise<Object>} 章节数据
     */
    async loadChapters(taskId) {
        return this.get(`/chapters/${taskId}`);
    }

    /**
     * 保存章节选择
     * @param {string} taskId - 任务ID
     * @param {string} type - 章节类型 ('technical', 'business', 'point_to_point')
     * @param {Array} chapters - 选中的章节列表
     * @returns {Promise<Object>} 保存结果
     */
    async saveChapterSelection(taskId, type, chapters) {
        return this.post(`/chapters/${taskId}`, {
            type,
            chapters
        });
    }

    // ============================================
    // 文件相关API
    // ============================================

    /**
     * 加载文件信息
     * @param {string} type - 文件类型 ('technical', 'business', 'response', etc.)
     * @param {string} taskId - 任务ID
     * @returns {Promise<Object>} 文件信息
     */
    async loadFileInfo(type, taskId) {
        return this.get(`/${type}-file-info/${taskId}`);
    }

    /**
     * 下载文件
     * @param {string} type - 文件类型
     * @param {string} taskId - 任务ID
     * @returns {string} 下载URL
     */
    getDownloadUrl(type, taskId) {
        return `${this.baseURL}/download-${type}-file/${taskId}`;
    }

    // ============================================
    // 段落相关API
    // ============================================

    /**
     * 加载筛选后的段落
     * @param {string} taskId - 任务ID
     * @returns {Promise<Object>} 段落数据
     */
    async loadFilteredChunks(taskId) {
        return this.get(`/filtered-chunks/${taskId}`);
    }

    // ============================================
    // 项目相关API
    // ============================================

    /**
     * 创建项目
     * @param {Object} data - 项目数据
     * @returns {Promise<Object>} 创建结果
     */
    async createProject(data) {
        return this.request('/api/tender-projects', {
            method: HTTP_METHODS.POST,
            body: JSON.stringify(data)
        });
    }

    /**
     * 更新项目
     * @param {string} projectId - 项目ID
     * @param {Object} data - 更新数据
     * @returns {Promise<Object>} 更新结果
     */
    async updateProject(projectId, data) {
        return this.request(`/api/tender-projects/${projectId}`, {
            method: HTTP_METHODS.PUT,
            body: JSON.stringify(data)
        });
    }

    /**
     * 获取项目详情
     * @param {string} projectId - 项目ID
     * @returns {Promise<Object>} 项目数据
     */
    async getProject(projectId) {
        return this.request(`/api/tender-projects/${projectId}`, {
            method: HTTP_METHODS.GET
        });
    }

    // ============================================
    // HITL任务相关API
    // ============================================

    /**
     * 保存HITL任务数据
     * @param {string} hitlTaskId - HITL任务ID
     * @param {Object} data - 任务数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveHitlTask(hitlTaskId, data) {
        return this.put(`/hitl-tasks/${hitlTaskId}`, data);
    }

    /**
     * 获取HITL任务
     * @param {Object} params - 查询参数
     * @returns {Promise<Object>} 任务数据
     */
    async getHitlTask(params = {}) {
        return this.get('/hitl-tasks', params);
    }

    // ============================================
    // 基本信息提取
    // ============================================

    /**
     * AI提取基本信息
     * @param {string} taskId - 任务ID
     * @param {string} modelName - 模型名称
     * @returns {Promise<Object>} 提取结果
     */
    async extractBasicInfo(taskId, modelName) {
        return this.post(`/extract-basic-info/${taskId}`, {
            model_name: modelName
        });
    }

    // ============================================
    // 资格要求API
    // ============================================

    /**
     * 获取资格要求
     * @param {string} projectId - 项目ID
     * @param {string} category - 类别 ('qualification', 'technical', 'commercial')
     * @returns {Promise<Object>} 资格要求数据
     */
    async getRequirementsByCategory(projectId, category) {
        return this.get(`/requirements/${projectId}`, {
            category
        });
    }
}

// 创建单例实例
const tenderProcessingAPI = new TenderProcessingAPI();

// 导出API类和单例实例
export { TenderProcessingAPI };
export default tenderProcessingAPI;
