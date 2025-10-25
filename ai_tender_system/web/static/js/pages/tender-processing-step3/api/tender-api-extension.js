/**
 * 标书处理API扩展
 * 基于 core/api-client.js，添加标书处理专用API
 *
 * 依赖: core/api-client.js (必须先加载)
 * 用法: window.apiClient.tenderProcessing.loadRequirements(...)
 */

(function() {
    'use strict';

    // 检查依赖
    if (!window.apiClient) {
        console.error('[TenderAPI] core/api-client.js 未加载，无法扩展API');
        return;
    }

    /**
     * 标书处理API模块
     */
    window.apiClient.tenderProcessing = {

        // ============================================
        // 需求相关API
        // ============================================

        /**
         * 加载需求列表
         * @param {string} taskId - 任务ID
         * @param {string} projectId - 项目ID
         * @param {Object} filters - 过滤条件（可选）
         * @returns {Promise} 需求数据
         */
        loadRequirements(taskId, projectId, filters = {}) {
            return window.apiClient.get(`/api/tender-processing/requirements/${taskId}`, {
                project_id: projectId,
                ...filters
            });
        },

        /**
         * 提取详细需求
         * @param {string} taskId - 任务ID
         * @returns {Promise} 提取结果
         */
        extractDetailedRequirements(taskId) {
            return window.apiClient.post(`/api/tender-processing/extract-detailed-requirements/${taskId}`);
        },

        /**
         * 更新需求
         * @param {string} requirementId - 需求ID
         * @param {Object} data - 更新数据
         * @returns {Promise} 更新结果
         */
        updateRequirement(requirementId, data) {
            return window.apiClient.put(`/api/tender-processing/requirements/${requirementId}`, data);
        },

        /**
         * 获取指定类别的需求
         * @param {string} projectId - 项目ID
         * @param {string} category - 类别 ('qualification', 'technical', 'commercial')
         * @returns {Promise} 需求数据
         */
        getRequirementsByCategory(projectId, category) {
            return window.apiClient.get(`/api/tender-processing/requirements/${projectId}`, {
                category
            });
        },

        // ============================================
        // 章节相关API
        // ============================================

        /**
         * 加载章节列表
         * @param {string} taskId - 任务ID
         * @returns {Promise} 章节数据
         */
        loadChapters(taskId) {
            return window.apiClient.get(`/api/tender-processing/chapters/${taskId}`);
        },

        /**
         * 保存章节选择
         * @param {string} taskId - 任务ID
         * @param {string} type - 章节类型 ('technical', 'business', 'point_to_point')
         * @param {Array} chapters - 选中的章节列表
         * @returns {Promise} 保存结果
         */
        saveChapterSelection(taskId, type, chapters) {
            return window.apiClient.post(`/api/tender-processing/chapters/${taskId}`, {
                type,
                chapters
            });
        },

        // ============================================
        // 文件相关API
        // ============================================

        /**
         * 加载文件信息
         * @param {string} type - 文件类型 ('technical', 'business', 'response', etc.)
         * @param {string} taskId - 任务ID
         * @returns {Promise} 文件信息
         */
        loadFileInfo(type, taskId) {
            return window.apiClient.get(`/api/tender-processing/${type}-file-info/${taskId}`);
        },

        /**
         * 获取文件下载URL
         * @param {string} type - 文件类型
         * @param {string} taskId - 任务ID
         * @returns {string} 下载URL
         */
        getDownloadUrl(type, taskId) {
            return `/api/tender-processing/download-${type}-file/${taskId}`;
        },

        // ============================================
        // 段落相关API
        // ============================================

        /**
         * 加载筛选后的段落
         * @param {string} taskId - 任务ID
         * @returns {Promise} 段落数据
         */
        loadFilteredChunks(taskId) {
            return window.apiClient.get(`/api/tender-processing/filtered-chunks/${taskId}`);
        },

        // ============================================
        // 项目相关API
        // ============================================

        /**
         * 创建项目
         * @param {Object} data - 项目数据
         * @returns {Promise} 创建结果
         */
        createProject(data) {
            return window.apiClient.post('/api/tender-projects', data);
        },

        /**
         * 更新项目
         * @param {string} projectId - 项目ID
         * @param {Object} data - 更新数据
         * @returns {Promise} 更新结果
         */
        updateProject(projectId, data) {
            return window.apiClient.put(`/api/tender-projects/${projectId}`, data);
        },

        /**
         * 获取项目详情
         * @param {string} projectId - 项目ID
         * @returns {Promise} 项目数据
         */
        getProject(projectId) {
            return window.apiClient.get(`/api/tender-projects/${projectId}`);
        },

        // ============================================
        // HITL任务相关API
        // ============================================

        /**
         * 保存HITL任务数据
         * @param {string} hitlTaskId - HITL任务ID
         * @param {Object} data - 任务数据
         * @returns {Promise} 保存结果
         */
        saveHitlTask(hitlTaskId, data) {
            return window.apiClient.put(`/api/tender-processing/hitl-tasks/${hitlTaskId}`, data);
        },

        /**
         * 获取HITL任务
         * @param {Object} params - 查询参数
         * @returns {Promise} 任务数据
         */
        getHitlTask(params = {}) {
            return window.apiClient.get('/api/tender-processing/hitl-tasks', params);
        },

        // ============================================
        // AI提取相关API
        // ============================================

        /**
         * AI提取基本信息
         * @param {string} taskId - 任务ID
         * @param {string} modelName - 模型名称
         * @returns {Promise} 提取结果
         */
        extractBasicInfo(taskId, modelName) {
            return window.apiClient.post(`/api/tender-processing/extract-basic-info/${taskId}`, {
                model_name: modelName
            });
        }
    };

    console.log('[TenderAPI] 标书处理API扩展已加载');

})();
