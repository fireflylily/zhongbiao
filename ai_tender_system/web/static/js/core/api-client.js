/**
 * 统一API调用封装
 * 提供一致的API请求方法和错误处理
 */

class APIClient {
    constructor() {
        this.baseURL = '';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    /**
     * 通用HTTP请求方法
     * @param {string} method - HTTP方法 (GET, POST, PUT, DELETE)
     * @param {string} url - 请求URL
     * @param {Object} data - 请求数据
     * @param {Object} options - 请求选项
     * @returns {Promise} 请求结果
     */
    async request(method, url, data = null, options = {}) {
        const config = {
            method: method.toUpperCase(),
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        // 处理请求数据
        if (data) {
            if (method.toUpperCase() === 'GET') {
                url += '?' + new URLSearchParams(data).toString();
            } else if (!(data instanceof FormData)) {
                config.body = JSON.stringify(data);
            } else {
                // FormData 请求，移除 Content-Type 让浏览器自动设置
                delete config.headers['Content-Type'];
                config.body = data;
            }
        }

        try {
            const response = await fetch(this.baseURL + url, config);

            // 检查响应状态
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // 根据内容类型解析响应
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            return await response.text();

        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    // 便捷方法
    get(url, params = null, options = {}) {
        return this.request('GET', url, params, options);
    }

    post(url, data = null, options = {}) {
        return this.request('POST', url, data, options);
    }

    put(url, data = null, options = {}) {
        return this.request('PUT', url, data, options);
    }

    delete(url, data = null, options = {}) {
        return this.request('DELETE', url, data, options);
    }

    /**
     * 文件上传专用方法
     * @param {string} url - 上传URL
     * @param {File|FileList} files - 文件对象
     * @param {Object} additionalData - 额外数据
     * @param {Function} onProgress - 进度回调
     */
    async uploadFile(url, files, additionalData = {}, onProgress = null) {
        const formData = new FormData();

        // 添加文件
        if (files instanceof FileList) {
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }
        } else {
            formData.append('file', files);
        }

        // 添加额外数据
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        const xhr = new XMLHttpRequest();

        return new Promise((resolve, reject) => {
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });

            xhr.open('POST', this.baseURL + url);

            // 添加默认头部（除了Content-Type）
            Object.keys(this.defaultHeaders).forEach(key => {
                if (key !== 'Content-Type') {
                    xhr.setRequestHeader(key, this.defaultHeaders[key]);
                }
            });

            xhr.send(formData);
        });
    }

    /**
     * 知识库相关API
     */
    knowledgeBase = {
        // 搜索文档
        search: (query, mode = 'semantic', filters = {}) => {
            return this.post('/api/search', { query, mode, ...filters });
        },

        // 上传文档
        uploadDocument: (file, category = null, onProgress = null) => {
            const data = category ? { category } : {};
            return this.uploadFile('/api/upload', file, data, onProgress);
        },

        // 获取文档列表
        getDocuments: (category = null, page = 1, limit = 10) => {
            const params = { page, limit };
            if (category) params.category = category;
            return this.get('/api/documents', params);
        },

        // 删除文档
        deleteDocument: (documentId) => {
            return this.delete(`/api/documents/${documentId}`);
        },

        // 获取分类列表
        getCategories: () => {
            return this.get('/api/categories');
        },

        // 获取统计信息
        getStats: () => {
            return this.get('/api/stats');
        }
    };

    /**
     * 标书生成相关API
     */
    proposal = {
        // 生成标书
        generate: (config, onProgress = null) => {
            // 对于长时间运行的任务，使用WebSocket或Server-Sent Events
            return this.post('/api/generate', config);
        },

        // 获取生成进度
        getProgress: (taskId) => {
            return this.get(`/api/generate/progress/${taskId}`);
        },

        // 获取模板列表
        getTemplates: () => {
            return this.get('/api/templates');
        },

        // 处理招标文件
        processTenderFile: (file, companyId, onProgress = null) => {
            const data = { company_id: companyId };
            return this.uploadFile('/api/tender/process', file, data, onProgress);
        }
    };

    /**
     * 公司管理相关API
     */
    company = {
        // 获取公司列表
        getCompanies: () => {
            return this.get('/api/companies');
        },

        // 获取公司详情
        getCompany: (companyId) => {
            return this.get(`/api/companies/${companyId}`);
        },

        // 更新公司信息
        updateCompany: (companyId, data) => {
            return this.put(`/api/companies/${companyId}`, data);
        },

        // 上传资质文件
        uploadQualification: (companyId, file, category, onProgress = null) => {
            const data = { company_id: companyId, category };
            return this.uploadFile('/api/qualifications/upload', file, data, onProgress);
        }
    };
}

// 创建全局API客户端实例
window.apiClient = new APIClient();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}