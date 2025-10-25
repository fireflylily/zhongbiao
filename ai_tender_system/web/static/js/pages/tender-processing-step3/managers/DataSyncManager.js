/**
 * 数据同步管理器
 * 统一管理标书处理流程中的数据保存和同步
 *
 * 依赖:
 * - core/api-client.js (API调用)
 * - core/notification.js (提示信息)
 * - core/global-state-manager.js (全局状态)
 * - tender-processing-step3/api/tender-api-extension.js (标书API扩展)
 *
 * 用法:
 * const syncManager = new DataSyncManager();
 * await syncManager.saveBasicInfo(basicInfoData);
 * await syncManager.saveAndComplete();
 */

class DataSyncManager {
    constructor() {
        // 防重复提交标志
        this.isSavingBasicInfo = false;
        this.isSavingComplete = false;

        console.log('[DataSyncManager] 数据同步管理器已初始化');
    }

    /**
     * 保存基本信息到 tender_projects 表
     * @param {Object} basicInfo - 基本信息对象（可选，默认从DOM收集）
     * @param {string} projectId - 项目ID（可选，默认从全局状态获取）
     * @returns {Promise<Object>} 保存结果 { success, projectId, message }
     */
    async saveBasicInfo(basicInfo = null, projectId = null) {
        console.log('[DataSyncManager] 开始保存基本信息');

        // 防止重复提交
        if (this.isSavingBasicInfo) {
            console.warn('[DataSyncManager] 正在保存中，忽略重复请求');
            return { success: false, message: '正在保存中...' };
        }

        this.isSavingBasicInfo = true;

        try {
            // 收集基本信息
            const data = basicInfo || this._collectBasicInfo();

            // 验证必填字段
            if (!data.company_id) {
                throw new Error('请先选择应答公司');
            }

            // 确定项目ID
            const currentProjectId = projectId || this._getProjectId();

            // 判断是创建还是更新
            const isUpdate = currentProjectId !== null && currentProjectId !== '';
            const url = isUpdate
                ? `/api/tender-projects/${currentProjectId}`
                : '/api/tender-projects';
            const method = isUpdate ? 'PUT' : 'POST';

            console.log(`[DataSyncManager] 执行${isUpdate ? '更新' : '创建'}操作，URL: ${url}`);

            // 更新按钮状态
            const btn = document.getElementById('saveBasicInfoBtn');
            this._setButtonLoading(btn, true, '保存中...');

            // 发送请求
            const response = await window.apiClient.request(method, url, data);

            if (response.success) {
                // 保存/更新项目ID到全局状态
                if (!isUpdate && response.project_id) {
                    this._setProjectId(response.project_id);
                    console.log('[DataSyncManager] 新项目已创建，ID:', response.project_id);
                }

                window.notifications.success(isUpdate ? '项目更新成功' : '项目创建成功');

                // 刷新项目列表（如果存在HITLConfigManager）
                if (typeof HITLConfigManager !== 'undefined') {
                    await HITLConfigManager.loadProjects();
                    const projectSelect = document.getElementById('hitlProjectSelect');
                    if (projectSelect && response.project_id) {
                        projectSelect.value = response.project_id;
                    }
                }

                // 更新按钮状态为成功
                this._setButtonSuccess(btn, '已保存');

                return {
                    success: true,
                    projectId: response.project_id || currentProjectId,
                    message: isUpdate ? '项目更新成功' : '项目创建成功'
                };
            } else {
                throw new Error(response.message || '保存失败');
            }

        } catch (error) {
            console.error('[DataSyncManager] 保存失败:', error);
            window.notifications.error('保存失败: ' + error.message);

            // 恢复按钮状态
            const btn = document.getElementById('saveBasicInfoBtn');
            this._setButtonLoading(btn, false);

            return { success: false, message: error.message };

        } finally {
            this.isSavingBasicInfo = false;
        }
    }

    /**
     * 保存并完成 - 保存完整项目数据到 tender_projects 表
     * @returns {Promise<Object>} 保存结果
     */
    async saveAndComplete() {
        console.log('[DataSyncManager] 开始保存并完成');

        // 防止重复提交
        if (this.isSavingComplete) {
            console.warn('[DataSyncManager] 正在保存中，忽略重复请求');
            return { success: false, message: '正在保存中...' };
        }

        this.isSavingComplete = true;

        const btn = document.getElementById('saveAndCompleteBtn');
        this._setButtonLoading(btn, true, '保存中...');

        try {
            // 1. 先保存基本信息（会创建或更新项目）
            const basicInfoResult = await this.saveBasicInfo();
            if (!basicInfoResult.success) {
                throw new Error(basicInfoResult.message || '保存基本信息失败');
            }

            // 2. 收集并同步资格要求、技术需求、评分办法等数据
            console.log('[DataSyncManager] 开始收集各类数据...');

            const [qualificationsData, technicalData, scoringData] = await Promise.all([
                this.collectQualificationsData(),
                this.collectTechnicalData(),
                this.collectScoringData()
            ]);

            console.log('[DataSyncManager] 数据收集完成:', {
                qualifications: Object.keys(qualificationsData).length,
                technical: Object.keys(technicalData).length,
                scoring: Object.keys(scoringData).length
            });

            // 3. 更新项目表，同步汇总数据
            const projectId = basicInfoResult.projectId || this._getProjectId();
            if (projectId) {
                const updatePayload = {
                    status: 'active'  // 标记为进行中
                };

                // 只有当数据不为空时才添加到payload
                if (Object.keys(qualificationsData).length > 0) {
                    updatePayload.qualifications_data = qualificationsData;
                }
                if (Object.keys(scoringData).length > 0) {
                    updatePayload.scoring_data = scoringData;
                }
                if (Object.keys(technicalData).length > 0) {
                    updatePayload.technical_data = technicalData;
                }

                console.log('[DataSyncManager] 准备更新项目数据');

                await window.apiClient.tenderProcessing.updateProject(projectId, updatePayload);

                console.log('[DataSyncManager] 项目数据更新成功');
            }

            window.notifications.success('✅ 所有数据已保存，HITL流程完成！');

            // 更新按钮状态
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已完成';
                btn.classList.remove('btn-success');
                btn.classList.add('btn-secondary');
            }

            return { success: true, message: '所有数据已保存' };

        } catch (error) {
            console.error('[DataSyncManager] 保存失败:', error);
            window.notifications.error('保存失败: ' + error.message);

            // 恢复按钮状态
            this._setButtonLoading(btn, false);

            return { success: false, message: error.message };

        } finally {
            this.isSavingComplete = false;
        }
    }

    /**
     * 收集资格要求数据
     * @returns {Promise<Object>} 资格要求JSON数据
     */
    async collectQualificationsData() {
        console.log('[DataSyncManager] 开始收集资格要求数据');

        try {
            const projectId = this._getProjectId();
            if (!projectId) {
                console.warn('[DataSyncManager] 项目ID不存在，返回空数据');
                return {};
            }

            const data = await window.apiClient.tenderProcessing.getRequirementsByCategory(
                projectId,
                'qualification'
            );

            if (!data.success) {
                throw new Error(data.error || '获取资格要求失败');
            }

            console.log(`[DataSyncManager] 获取到 ${data.requirements.length} 条资格要求`);

            // 转换为JSON格式
            return this._convertRequirementsToJSON(data.requirements);

        } catch (error) {
            console.error('[DataSyncManager] 收集资格要求数据失败:', error);
            return {};
        }
    }

    /**
     * 收集技术需求数据
     * @returns {Promise<Object>} 技术需求JSON数据
     */
    async collectTechnicalData() {
        console.log('[DataSyncManager] 开始收集技术需求数据');

        try {
            const projectId = this._getProjectId();
            if (!projectId) {
                console.warn('[DataSyncManager] 项目ID不存在，返回空数据');
                return {};
            }

            const data = await window.apiClient.tenderProcessing.getRequirementsByCategory(
                projectId,
                'technical'
            );

            if (!data.success) {
                throw new Error(data.error || '获取技术需求失败');
            }

            console.log(`[DataSyncManager] 获取到 ${data.requirements.length} 条技术需求`);

            // 转换为JSON格式
            return this._convertRequirementsToJSON(data.requirements);

        } catch (error) {
            console.error('[DataSyncManager] 收集技术需求数据失败:', error);
            return {};
        }
    }

    /**
     * 收集评分办法数据
     * @returns {Promise<Object>} 评分办法JSON数据
     */
    async collectScoringData() {
        console.log('[DataSyncManager] 开始收集评分办法数据');

        try {
            const projectId = this._getProjectId();
            if (!projectId) {
                console.warn('[DataSyncManager] 项目ID不存在，返回空数据');
                return {};
            }

            const data = await window.apiClient.tenderProcessing.getRequirementsByCategory(
                projectId,
                'commercial'
            );

            if (!data.success) {
                throw new Error(data.error || '获取评分办法失败');
            }

            console.log(`[DataSyncManager] 获取到 ${data.requirements.length} 条评分办法`);

            // 转换为JSON格式
            return this._convertRequirementsToJSON(data.requirements);

        } catch (error) {
            console.error('[DataSyncManager] 收集评分办法数据失败:', error);
            return {};
        }
    }

    // ============================================
    // 私有方法
    // ============================================

    /**
     * 从DOM收集基本信息
     * @returns {Object}
     * @private
     */
    _collectBasicInfo() {
        // 获取公司ID
        let companyId = null;
        if (typeof HITLConfigManager !== 'undefined') {
            const config = HITLConfigManager.getConfig();
            companyId = config.companyId;
        } else if (window.globalState) {
            const company = window.globalState.getCompany();
            companyId = company?.id;
        }

        return {
            project_name: document.getElementById('projectName')?.value || '',
            project_number: document.getElementById('projectNumber')?.value || '',
            tenderer: document.getElementById('tenderParty')?.value || '',
            agency: document.getElementById('tenderAgent')?.value || '',
            bidding_method: document.getElementById('tenderMethod')?.value || '',
            bidding_location: document.getElementById('tenderLocation')?.value || '',
            bidding_time: document.getElementById('tenderDeadline')?.value || '',
            winner_count: document.getElementById('winnerCount')?.value || '',
            company_id: companyId,
            tender_document_path: '',  // HITL从章节选择开始，无上传文件路径
            original_filename: ''
        };
    }

    /**
     * 获取项目ID
     * @returns {string|null}
     * @private
     */
    _getProjectId() {
        // 优先从HITLConfigManager获取
        if (typeof HITLConfigManager !== 'undefined') {
            return HITLConfigManager.currentProjectId;
        }

        // 其次从全局状态获取
        if (window.globalState) {
            const project = window.globalState.getProject();
            return project?.id || null;
        }

        return null;
    }

    /**
     * 设置项目ID
     * @param {string} projectId - 项目ID
     * @private
     */
    _setProjectId(projectId) {
        // 保存到HITLConfigManager
        if (typeof HITLConfigManager !== 'undefined') {
            HITLConfigManager.currentProjectId = projectId;
        }

        // 保存到全局状态
        if (window.globalState) {
            window.globalState.setProject(projectId, '');
        }
    }

    /**
     * 将需求数组转换为JSON对象格式
     * @param {Array} requirements - 需求数组
     * @returns {Object} JSON格式的需求数据
     * @private
     */
    _convertRequirementsToJSON(requirements) {
        const result = {};

        if (!requirements || requirements.length === 0) {
            return result;
        }

        requirements.forEach(req => {
            // 使用 subcategory 作为key，如果没有则用 summary 或 requirement_id
            const key = req.subcategory || req.summary || `requirement_${req.requirement_id}`;

            result[key] = {
                requirement_id: req.requirement_id,
                constraint_type: req.constraint_type,
                detail: req.detail,
                summary: req.summary,
                source_location: req.source_location,
                priority: req.priority,
                extraction_confidence: req.extraction_confidence,
                is_verified: req.is_verified || false,
                created_at: req.created_at
            };
        });

        console.log(`[DataSyncManager] 转换了 ${requirements.length} 条需求为JSON格式`);
        return result;
    }

    /**
     * 设置按钮加载状态
     * @param {HTMLElement} btn - 按钮元素
     * @param {boolean} loading - 是否加载中
     * @param {string} text - 加载文本
     * @private
     */
    _setButtonLoading(btn, loading, text = '保存中...') {
        if (!btn) return;

        if (loading) {
            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
        } else {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-save me-2"></i>保存基本信息';
        }
    }

    /**
     * 设置按钮成功状态
     * @param {HTMLElement} btn - 按钮元素
     * @param {string} text - 成功文本
     * @private
     */
    _setButtonSuccess(btn, text = '已保存') {
        if (!btn) return;

        btn.innerHTML = `<i class="bi bi-check-lg me-2"></i>${text}`;
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-success');
    }
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataSyncManager;
}
