/**
 * 技术方案生成模块 - 前端交互管理
 * 负责技术方案生成的文件上传、配置管理和结果展示
 */

class ProposalGenerator {
    constructor() {
        this.isGenerating = false;
        this.currentController = null;
        this.progressInterval = null;

        this.init();
    }

    /**
     * 初始化生成器
     */
    init() {
        this.bindElements();
        this.bindEvents();
        this.loadCompanies();
        this.parseUrlParams(); // 解析URL参数并自动填充

        // 监听从 HITL Tab 切换过来的事件
        window.addEventListener('loadTechnicalProposal', (event) => {
            if (event.detail && event.detail.fromHITL) {
                console.log('[ProposalGenerator] 收到来自 HITL 的加载事件:', event.detail);
                this.loadFromHITL();
            }
        });
    }

    /**
     * 绑定DOM元素
     */
    bindElements() {
        // 表单和文件输入
        this.techProposalForm = document.getElementById('techProposalForm');
        this.techTenderFileInput = document.getElementById('techTenderFileInput');
        this.productFileInput = document.getElementById('productFileInput');
        this.outputPrefix = document.getElementById('outputPrefix');

        // 文件信息显示
        this.techTenderFileInfo = document.getElementById('techTenderFileInfo');
        this.techTenderFileName = document.getElementById('techTenderFileName');
        this.productFileInfo = document.getElementById('productFileInfo');
        this.productFileName = document.getElementById('productFileName');

        // HITL相关元素
        this.techTechnicalFileTaskId = document.getElementById('techTechnicalFileTaskId');
        this.techTechnicalFileUrl = document.getElementById('techTechnicalFileUrl');
        this.techTechnicalFileDisplay = document.getElementById('techTechnicalFileDisplay');
        this.techTechnicalFileDisplayName = document.getElementById('techTechnicalFileDisplayName');
        this.techTechnicalFileDisplaySize = document.getElementById('techTechnicalFileDisplaySize');
        this.techClearTechnicalFile = document.getElementById('techClearTechnicalFile');
        this.techTenderUpload = document.getElementById('techTenderUpload');

        // 按钮
        this.generateProposalBtn = document.getElementById('generateProposalBtn');

        // 公司选择
        this.techCompanySelect = document.getElementById('techCompanySelect');

        // 进度和结果
        this.techProgressBar = document.getElementById('techProgressBar');
        this.techResultArea = document.getElementById('techResultArea');
        this.techErrorArea = document.getElementById('techErrorArea');
        this.techDownloadArea = document.getElementById('techDownloadArea');
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 招标文件选择
        if (this.techTenderFileInput) {
            this.techTenderFileInput.addEventListener('change', () => {
                this.handleTenderFileSelect();
            });
        }

        // 产品文件选择
        if (this.productFileInput) {
            this.productFileInput.addEventListener('change', () => {
                this.handleProductFileSelect();
            });
        }

        // 表单提交
        if (this.techProposalForm) {
            this.techProposalForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitTechProposal();
            });
        }

        // 文件上传区域点击事件
        const techTenderUpload = document.getElementById('techTenderUpload');
        const productUpload = document.getElementById('productUpload');

        if (techTenderUpload) {
            techTenderUpload.addEventListener('click', () => {
                if (this.techTenderFileInput) {
                    this.techTenderFileInput.click();
                }
            });
        }

        if (productUpload) {
            productUpload.addEventListener('click', () => {
                if (this.productFileInput) {
                    this.productFileInput.click();
                }
            });
        }

        // 清除技术需求文件按钮
        if (this.techClearTechnicalFile) {
            this.techClearTechnicalFile.addEventListener('click', () => {
                this.clearTechnicalFile();
            });
        }

        // 监听公司状态变化,同步到下拉框
        window.addEventListener('companyChanged', (e) => {
            if (e.detail && e.detail.company_id && this.techCompanySelect) {
                console.log('[ProposalGenerator] 收到公司变化事件:', e.detail);
                this.techCompanySelect.value = e.detail.company_id;
            }
        });

        // 监听技术需求文件加载事件
        document.addEventListener('technicalFileLoadedForTechProposal', (e) => {
            console.log('[ProposalGenerator] 收到技术需求文件加载事件:', e.detail);
            this.checkFormReady();
        });
    }

    /**
     * 处理招标文件选择
     */
    handleTenderFileSelect() {
        const file = this.techTenderFileInput.files[0];
        if (file) {
            if (this.validateFile(file, '招标文件')) {
                this.techTenderFileName.textContent = file.name;
                this.techTenderFileInfo.classList.remove('d-none');
                this.checkFormReady();
            }
        }
    }

    /**
     * 处理产品文件选择
     */
    handleProductFileSelect() {
        const file = this.productFileInput.files[0];
        if (file) {
            if (this.validateFile(file, '产品文件')) {
                this.productFileName.textContent = file.name;
                this.productFileInfo.classList.remove('d-none');
                this.checkFormReady();
            }
        }
    }

    /**
     * 验证文件
     */
    validateFile(file, fileType) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/pdf'
        ];

        // 检查文件大小
        if (file.size > maxSize) {
            window.notifications?.error(`${fileType}大小不能超过50MB`);
            return false;
        }

        // 检查文件类型
        if (!allowedTypes.includes(file.type)) {
            window.notifications?.error(`${fileType}只支持Word文档(.docx, .doc)和PDF文件`);
            return false;
        }

        return true;
    }

    /**
     * 检查表单是否就绪
     */
    checkFormReady() {
        // 检查是否有招标文件（可以是上传的文件或从HITL传递的技术需求文件）
        const hasTenderFile = (this.techTenderFileInput && this.techTenderFileInput.files.length > 0) ||
                             (this.techTechnicalFileTaskId && this.techTechnicalFileTaskId.value);
        const hasProductFile = this.productFileInput && this.productFileInput.files.length > 0;

        // 只要有招标文件即可启用按钮，产品文件是可选的
        if (this.generateProposalBtn) {
            this.generateProposalBtn.disabled = !hasTenderFile;
        }

        console.log('[ProposalGenerator.checkFormReady] 表单状态:', {
            hasTenderFile,
            hasProductFile,
            disabled: !hasTenderFile
        });
    }

    /**
     * 提交技术方案生成
     */
    async submitTechProposal() {
        if (this.isGenerating) {
            window.notifications?.warning('正在生成中，请稍候...');
            return;
        }

        // 验证招标文件（可以是上传的文件或从HITL传递的技术需求文件）
        const hasUploadedTenderFile = this.techTenderFileInput.files[0];
        const hasTechnicalFile = this.techTechnicalFileTaskId && this.techTechnicalFileTaskId.value;

        if (!hasUploadedTenderFile && !hasTechnicalFile) {
            window.notifications?.error('请选择招标文件');
            return;
        }

        // 产品文件是可选的，不再强制要求

        this.isGenerating = true;
        this.showProgress();
        this.hideResults();

        try {
            // 创建表单数据
            const formData = new FormData();

            // 如果有上传的招标文件，使用上传的文件
            if (hasUploadedTenderFile) {
                formData.append('tender_file', this.techTenderFileInput.files[0]);
            }
            // 否则，传递HITL任务ID，让后端从HITL任务中获取技术需求文件
            else if (hasTechnicalFile) {
                formData.append('technicalFileTaskId', this.techTechnicalFileTaskId.value);
            }

            // 产品文件是可选的，只有上传时才添加到FormData
            if (this.productFileInput.files[0]) {
                formData.append('product_file', this.productFileInput.files[0]);
            }

            formData.append('outputPrefix', this.outputPrefix?.value?.trim() || '技术方案');

            // 添加公司信息
            const companyId = this.techCompanySelect?.value;
            if (companyId) {
                formData.append('companyId', companyId);
            }

            // 添加项目名称（如果有）
            if (window.companyStateManager) {
                const projectName = window.companyStateManager.getProjectName();
                if (projectName) {
                    formData.append('projectName', projectName);
                }
            }

            // 添加高级选项(默认全部启用)
            formData.append('includeAnalysis', document.getElementById('includeAnalysis')?.checked ?? true ? 'true' : 'false');
            formData.append('includeMapping', document.getElementById('includeMapping')?.checked ?? true ? 'true' : 'false');
            formData.append('includeSummary', document.getElementById('includeSummary')?.checked ?? true ? 'true' : 'false');

            // 使用 Server-Sent Events (SSE) 接收实时进度
            await this.generateWithSSE(formData);

        } catch (error) {
            console.error('技术方案生成失败:', error);

            let errorMsg = '生成失败: ';
            if (error.name === 'AbortError') {
                errorMsg += '请求超时，文档过大或网络不稳定';
            } else if (error.message.includes('Failed to fetch')) {
                errorMsg += '网络连接失败，请检查网络状态后重试';
            } else {
                errorMsg += error.message;
            }

            this.showError(errorMsg);
        } finally {
            this.isGenerating = false;
            this.hideProgress();
        }
    }

    /**
     * 使用SSE生成技术方案
     * @param {FormData} formData - 表单数据
     */
    async generateWithSSE(formData) {
        return new Promise((resolve, reject) => {
            // 将FormData转换为URL参数
            const params = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                if (!(value instanceof File)) {
                    params.append(key, value);
                }
            }

            // 创建EventSource连接（使用GET，文件通过技术需求文件路径）
            // 注意：EventSource只支持GET，所以我们需要另一种方式
            // 这里改用fetch的stream模式

            const url = '/api/generate-proposal-stream';

            fetch(url, {
                method: 'POST',
                body: formData
            }).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                const readStream = () => {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            resolve();
                            return;
                        }

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n\n');
                        buffer = lines.pop() || '';

                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.substring(6));
                                    this.handleSSEEvent(data);

                                    // 如果完成或出错，结束stream
                                    if (data.stage === 'completed') {
                                        resolve(data);
                                        return;
                                    } else if (data.stage === 'error') {
                                        reject(new Error(data.error || data.message));
                                        return;
                                    }
                                } catch (e) {
                                    console.error('解析SSE数据失败:', e);
                                }
                            }
                        }

                        readStream();
                    }).catch(error => {
                        reject(error);
                    });
                };

                readStream();
            }).catch(error => {
                reject(error);
            });
        });
    }

    /**
     * 处理SSE事件
     * @param {Object} data - 事件数据
     */
    handleSSEEvent(data) {
        console.log('SSE事件:', data);

        // 更新进度条
        if (data.progress !== undefined) {
            this.updateProgressBar(data.progress, data.message);
        }

        // 更新阶段状态
        if (data.stage) {
            this.updateStageStatus(data.stage, data.message);
        }

        // 处理需求分析完成事件 - 显示分析结果
        if (data.stage === 'analysis_completed' && data.analysis_result) {
            this.displayAnalysisResult(data.analysis_result);
        }

        // 处理完成事件
        console.log('[DEBUG] 检查完成条件: stage=', data.stage, ', success=', data.success);
        if (data.stage === 'completed' && data.success) {
            console.log('[DEBUG] 满足完成条件，调用showSuccess, output_files=', data.output_files);
            this.showSuccess(data);
        } else if (data.stage === 'completed') {
            console.warn('[WARN] stage=completed但success不为true:', data.success);
        }
    }

    /**
     * 显示生成进度
     */
    showProgress() {
        if (this.techProgressBar) {
            this.techProgressBar.classList.remove('d-none');
        }

        if (this.generateProposalBtn) {
            this.generateProposalBtn.disabled = true;
            this.generateProposalBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 准备中...';
        }

        // 不再使用模拟进度，使用真实SSE进度
        this.updateProgressBar(0, '准备生成...');
    }

    /**
     * 更新进度条
     * @param {number} progress - 进度百分比
     * @param {string} message - 进度消息
     */
    updateProgressBar(progress, message = '') {
        const progressBarElement = this.techProgressBar?.querySelector('.progress-bar');
        if (progressBarElement) {
            progressBarElement.style.width = `${progress}%`;
            // 在进度条上显示百分比
            progressBarElement.textContent = `${Math.round(progress)}%`;
        }

        // 如果有消息，更新按钮文本
        if (message && this.generateProposalBtn) {
            this.generateProposalBtn.innerHTML = `<i class="bi bi-hourglass-split"></i> ${message}`;
        }
    }

    /**
     * 更新阶段状态
     * @param {string} stage - 阶段名称
     * @param {string} message - 状态消息
     */
    updateStageStatus(stage, message) {
        // 这里可以扩展为显示阶段列表
        console.log(`阶段: ${stage}, 消息: ${message}`);

        // 更新按钮文本以显示当前阶段
        const stageNames = {
            'init': '初始化',
            'analysis': '需求分析',
            'outline': '大纲生成',
            'matching': '文档匹配',
            'assembly': '方案组装',
            'export': '导出文件',
            'completed': '完成',
            'error': '错误'
        };

        const stageName = stageNames[stage] || stage;
        if (this.generateProposalBtn) {
            this.generateProposalBtn.innerHTML = `<i class="bi bi-hourglass-split"></i> ${stageName}中...`;
        }
    }

    /**
     * 显示需求分析结果
     * @param {Object} analysisResult - 需求分析结果数据
     */
    displayAnalysisResult(analysisResult) {
        console.log('显示需求分析结果:', analysisResult);

        const analysisArea = document.getElementById('analysisResultArea');
        if (!analysisArea) return;

        // 显示分析结果区域
        analysisArea.classList.remove('d-none');

        // 渲染文档摘要
        this.renderAnalysisSummary(analysisResult.document_summary || {});

        // 渲染需求分类
        this.renderRequirementCategories(analysisResult.requirement_categories || []);

        // 渲染特别关注事项
        if (analysisResult.special_attention && analysisResult.special_attention.length > 0) {
            this.renderSpecialAttention(analysisResult.special_attention);
        }

        // 添加展开/收起功能
        this.setupAnalysisToggle();
    }

    /**
     * 渲染文档摘要
     * @param {Object} summary - 文档摘要数据
     */
    renderAnalysisSummary(summary) {
        const summaryContainer = document.getElementById('analysisSummary');
        if (!summaryContainer) return;

        const complexityColors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        };

        const complexityColor = complexityColors[summary.complexity_level] || 'secondary';

        summaryContainer.innerHTML = `
            <div class="col-md-3">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-list-check text-primary fs-4"></i>
                    <div class="mt-2"><strong>${summary.total_requirements || 0}</strong></div>
                    <small class="text-muted">总需求数</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-star-fill text-danger fs-4"></i>
                    <div class="mt-2"><strong>${summary.mandatory_count || 0}</strong></div>
                    <small class="text-muted">强制需求</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-star text-success fs-4"></i>
                    <div class="mt-2"><strong>${summary.optional_count || 0}</strong></div>
                    <small class="text-muted">可选需求</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-speedometer2 text-${complexityColor} fs-4"></i>
                    <div class="mt-2"><span class="badge bg-${complexityColor}">${this.getComplexityText(summary.complexity_level)}</span></div>
                    <small class="text-muted">复杂度</small>
                </div>
            </div>
        `;
    }

    /**
     * 获取复杂度文本
     * @param {string} level - 复杂度级别
     * @returns {string} 复杂度文本
     */
    getComplexityText(level) {
        const texts = {
            'low': '低',
            'medium': '中',
            'high': '高'
        };
        return texts[level] || '未知';
    }

    /**
     * 渲染需求分类
     * @param {Array} categories - 需求分类数组
     */
    renderRequirementCategories(categories) {
        const container = document.getElementById('requirementCategories');
        if (!container) return;

        if (categories.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无需求分类</p>';
            return;
        }

        const priorityColors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'success'
        };

        let html = '';
        categories.forEach((category, index) => {
            const priorityColor = priorityColors[category.priority] || 'secondary';

            html += `
                <div class="card mb-2">
                    <div class="card-header py-2 bg-light">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>
                                <i class="bi bi-folder2"></i> <strong>${category.category}</strong>
                                <span class="badge bg-${priorityColor} ms-2">${this.getPriorityText(category.priority)}</span>
                                <span class="badge bg-secondary ms-1">${category.requirements_count || 0}项</span>
                            </span>
                            <button class="btn btn-sm btn-link text-decoration-none"
                                    type="button"
                                    data-bs-toggle="collapse"
                                    data-bs-target="#category-${index}">
                                <i class="bi bi-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="collapse" id="category-${index}">
                        <div class="card-body">
                            ${category.summary ? `<p class="text-muted mb-2"><em>${category.summary}</em></p>` : ''}

                            ${category.keywords && category.keywords.length > 0 ? `
                                <div class="mb-2">
                                    <small class="text-muted">关键词：</small>
                                    ${category.keywords.map(kw => `<span class="badge bg-info me-1">${kw}</span>`).join('')}
                                </div>
                            ` : ''}

                            ${category.key_points && category.key_points.length > 0 ? `
                                <div>
                                    <small class="text-muted">要点：</small>
                                    <ul class="mb-0">
                                        ${category.key_points.map(point => `<li>${point}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    /**
     * 获取优先级文本
     * @param {string} priority - 优先级
     * @returns {string} 优先级文本
     */
    getPriorityText(priority) {
        const texts = {
            'high': '高优先级',
            'medium': '中优先级',
            'low': '低优先级'
        };
        return texts[priority] || '普通';
    }

    /**
     * 渲染特别关注事项
     * @param {Array} attentionList - 特别关注事项数组
     */
    renderSpecialAttention(attentionList) {
        const section = document.getElementById('specialAttentionSection');
        const listContainer = document.getElementById('specialAttentionList');

        if (!section || !listContainer || attentionList.length === 0) return;

        section.style.display = 'block';
        listContainer.innerHTML = attentionList.map(item =>
            `<li class="mb-1"><i class="bi bi-exclamation-circle text-warning"></i> ${item}</li>`
        ).join('');
    }

    /**
     * 设置分析结果展开/收起功能
     */
    setupAnalysisToggle() {
        const toggleBtn = document.getElementById('toggleAnalysisDetail');
        const contentArea = document.getElementById('analysisResultContent');

        if (!toggleBtn || !contentArea) return;

        // 移除旧的事件监听器
        const newToggleBtn = toggleBtn.cloneNode(true);
        toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);

        // 添加新的事件监听器
        newToggleBtn.addEventListener('click', () => {
            if (contentArea.style.display === 'none') {
                contentArea.style.display = 'block';
                newToggleBtn.innerHTML = '<i class="bi bi-chevron-up"></i> 收起';
            } else {
                contentArea.style.display = 'none';
                newToggleBtn.innerHTML = '<i class="bi bi-chevron-down"></i> 展开';
            }
        });
    }

    /**
     * 隐藏进度条
     */
    hideProgress() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }

        setTimeout(() => {
            if (this.techProgressBar) {
                this.techProgressBar.classList.add('d-none');
            }

            this.updateProgressBar(0);

            if (this.generateProposalBtn) {
                this.generateProposalBtn.disabled = false;
                this.generateProposalBtn.innerHTML = '<i class="bi bi-magic"></i> 生成技术方案';
            }

            this.checkFormReady(); // 重新检查表单状态
        }, 1000);
    }

    /**
     * 显示成功结果
     */
    showSuccess(data) {
        console.log('[DEBUG] showSuccess被调用, data=', data);
        this.updateProgressBar(100);

        // 更新统计信息
        const techResultMessage = document.getElementById('techResultMessage');
        console.log('[DEBUG] techResultMessage element=', techResultMessage);
        if (techResultMessage) {
            const stats = this.formatStatistics(data);
            techResultMessage.innerHTML = stats;
            console.log('[DEBUG] 统计信息已更新');
        }

        // 生成下载按钮
        console.log('[DEBUG] techDownloadArea=', this.techDownloadArea, ', output_files=', data.output_files);
        if (this.techDownloadArea && data.output_files) {
            console.log('[DEBUG] 调用createDownloadButtons');
            this.createDownloadButtons(data.output_files);

            // 如果有HITL任务ID，添加同步按钮
            if (this.hitlTaskId) {
                console.log('[ProposalGenerator] 检测到HITL任务ID,添加同步按钮:', this.hitlTaskId);
                const syncBtn = document.createElement('button');
                syncBtn.className = 'btn btn-info me-2 mb-2';
                syncBtn.id = 'syncTechProposalToHitlBtn';
                syncBtn.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>同步到投标项目';
                syncBtn.onclick = () => this.syncToHitl(this.hitlTaskId, data.output_files);
                this.techDownloadArea.appendChild(syncBtn);
            }
        } else {
            console.warn('[WARN] 无法创建下载按钮: techDownloadArea=', this.techDownloadArea, ', output_files=', data.output_files);
        }

        console.log('[DEBUG] techResultArea=', this.techResultArea);
        if (this.techResultArea) {
            this.techResultArea.classList.remove('d-none');
            console.log('[DEBUG] techResultArea已显示（移除d-none）');
        } else {
            console.warn('[WARN] techResultArea元素不存在');
        }

        window.notifications?.success('技术方案生成完成');
        console.log('[DEBUG] showSuccess完成');
    }

    /**
     * 格式化统计信息
     */
    formatStatistics(data) {
        const matchRate = data.requirements_count > 0
            ? Math.round((data.matches_count / data.requirements_count * 100) || 0)
            : 0;

        return `
            <strong>生成统计：</strong><br>
            • 需求数量：${data.requirements_count || 0}<br>
            • 功能数量：${data.features_count || 0}<br>
            • 匹配数量：${data.matches_count || 0}<br>
            • 章节数量：${data.sections_count || 0}<br>
            • 匹配成功率：${matchRate}%
        `;
    }

    /**
     * 创建下载按钮
     */
    createDownloadButtons(outputFiles) {
        console.log('[DEBUG] createDownloadButtons被调用, outputFiles=', outputFiles);
        this.techDownloadArea.innerHTML = '';

        // 标准按钮顺序：预览 → 下载 → 完成 → 同步HITL

        // 1. 添加预览按钮（针对技术方案主文件）
        if (outputFiles.proposal) {
            console.log('[DEBUG] 创建预览按钮');
            const previewBtn = document.createElement('button');
            previewBtn.className = 'btn btn-outline-primary me-2 mb-2';
            previewBtn.innerHTML = '<i class="bi bi-eye"></i> 预览';
            previewBtn.onclick = (e) => {
                e.preventDefault();
                this.previewProposal(outputFiles.proposal);
            };
            this.techDownloadArea.appendChild(previewBtn);
            console.log('[DEBUG] 预览按钮已添加');
        }

        // 2. 添加下载按钮
        console.log('[DEBUG] 创建下载按钮, 文件数量:', Object.keys(outputFiles).length);
        Object.keys(outputFiles).forEach(fileType => {
            const filePath = outputFiles[fileType];
            const fileName = filePath.split('/').pop();

            const buttonConfig = this.getButtonConfig(fileType);

            const button = document.createElement('button');
            button.className = `btn ${buttonConfig.class} me-2 mb-2`;
            button.innerHTML = `<i class="${buttonConfig.icon}"></i> ${buttonConfig.text}`;

            button.onclick = (e) => {
                e.preventDefault();
                this.downloadFile(filePath, fileName);
            };

            this.techDownloadArea.appendChild(button);
        });

        // 3. 添加"完成"按钮
        const completeBtn = document.createElement('button');
        completeBtn.className = 'btn btn-outline-secondary me-2 mb-2';
        completeBtn.innerHTML = '<i class="bi bi-check-circle"></i> 完成';
        completeBtn.onclick = (e) => {
            e.preventDefault();
            // 返回主页或HITL
            if (this.hitlTaskId) {
                window.location.href = `/hitl?task_id=${this.hitlTaskId}`;
            } else {
                window.location.href = '/';
            }
        };
        this.techDownloadArea.appendChild(completeBtn);
    }

    /**
     * 获取按钮配置
     */
    getButtonConfig(fileType) {
        const configs = {
            proposal: {
                class: 'btn-success',
                icon: 'bi-file-earmark-word',
                text: '下载技术方案'
            },
            analysis: {
                class: 'btn-success',
                icon: 'bi-file-earmark-text',
                text: '下载需求分析'
            },
            mapping: {
                class: 'btn-success',
                icon: 'bi-file-earmark-spreadsheet',
                text: '下载匹配表'
            },
            summary: {
                class: 'btn-success',
                icon: 'bi-file-earmark-pdf',
                text: '下载生成报告'
            }
        };

        return configs[fileType] || {
            class: 'btn-success',
            icon: 'bi-download',
            text: '下载文件'
        };
    }

    /**
     * 显示错误信息
     */
    showError(errorMessage) {
        const techErrorMessage = document.getElementById('techErrorMessage');
        if (techErrorMessage) {
            techErrorMessage.textContent = errorMessage;
        }

        if (this.techErrorArea) {
            this.techErrorArea.classList.remove('d-none');
        }

        window.notifications?.error('技术方案生成失败');
    }

    /**
     * 隐藏结果区域
     */
    hideResults() {
        if (this.techResultArea) {
            this.techResultArea.classList.add('d-none');
        }
        if (this.techErrorArea) {
            this.techErrorArea.classList.add('d-none');
        }
    }

    /**
     * 下载文件
     */
    downloadFile(url, filename) {
        try {
            window.notifications?.info('开始下载...');

            const link = document.createElement('a');
            link.href = url;
            link.download = filename || '';
            link.style.display = 'none';

            document.body.appendChild(link);
            link.click();

            setTimeout(() => {
                document.body.removeChild(link);
                window.notifications?.success('下载已开始');
            }, 100);

        } catch (error) {
            console.error('下载失败:', error);
            window.notifications?.error('下载失败: ' + error.message);
        }
    }

    /**
     * 重置表单
     */
    resetForm() {
        // 取消当前生成
        if (this.currentController) {
            this.currentController.abort();
        }

        this.isGenerating = false;
        this.hideProgress();
        this.hideResults();

        // 清除文件选择
        if (this.techTenderFileInput) {
            this.techTenderFileInput.value = '';
        }
        if (this.productFileInput) {
            this.productFileInput.value = '';
        }

        // 隐藏文件信息
        if (this.techTenderFileInfo) {
            this.techTenderFileInfo.classList.add('d-none');
        }
        if (this.productFileInfo) {
            this.productFileInfo.classList.add('d-none');
        }

        // 重置输出前缀
        if (this.outputPrefix) {
            this.outputPrefix.value = '技术方案';
        }

        this.checkFormReady();
        window.notifications?.info('表单已重置');
    }

    /**
     * 获取当前配置
     */
    getCurrentConfig() {
        return {
            outputPrefix: this.outputPrefix?.value?.trim() || '技术方案'
        };
    }

    /**
     * 设置配置
     */
    setConfig(config) {
        if (this.outputPrefix && config.outputPrefix) {
            this.outputPrefix.value = config.outputPrefix;
        }
    }

    /**
     * 解析URL参数并自动填充表单
     */
    parseUrlParams() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const companyId = urlParams.get('company_id');
            const companyName = urlParams.get('company_name');
            const projectId = urlParams.get('project_id');
            const projectName = urlParams.get('project_name');
            const hitlTaskId = urlParams.get('hitl_task_id');

            // 新增: 获取技术需求文件详细信息
            const technicalFileName = urlParams.get('technical_file_name');
            const technicalFileSize = urlParams.get('technical_file_size');
            const technicalFileUrl = urlParams.get('technical_file_url');

            console.log('[ProposalGenerator] 解析URL参数:', {
                companyId, companyName, projectId, projectName, hitlTaskId,
                technicalFileName, technicalFileSize, technicalFileUrl
            });

            // 如果有公司和项目信息,通过companyStateManager设置
            if (companyId && companyName && window.companyStateManager) {
                console.log('[ProposalGenerator] 设置公司和项目信息到状态管理器');
                window.companyStateManager.selectCompany({
                    company_id: parseInt(companyId),
                    company_name: companyName,
                    project_id: projectId ? parseInt(projectId) : null,
                    project_name: projectName || null
                });
            }

            // 保存hitl_task_id供后续使用(如果需要同步回HITL)
            if (hitlTaskId) {
                this.hitlTaskId = hitlTaskId;
                console.log('[ProposalGenerator] 保存HITL任务ID:', hitlTaskId);

                // 填充隐藏字段
                if (this.techTechnicalFileTaskId) {
                    this.techTechnicalFileTaskId.value = hitlTaskId;
                }
                if (this.techTechnicalFileUrl && technicalFileUrl) {
                    this.techTechnicalFileUrl.value = technicalFileUrl;
                }

                // 如果有技术文件详细信息,显示具体的文件名和大小
                if (technicalFileName && this.techTechnicalFileDisplay) {
                    this.techTechnicalFileDisplay.classList.remove('d-none');

                    // 显示文件名
                    if (this.techTechnicalFileDisplayName) {
                        this.techTechnicalFileDisplayName.textContent = technicalFileName;
                    }

                    // 格式化并显示文件大小
                    if (this.techTechnicalFileDisplaySize && technicalFileSize) {
                        const sizeKB = (parseInt(technicalFileSize) / 1024).toFixed(2);
                        this.techTechnicalFileDisplaySize.textContent = ` (${sizeKB} KB)`;
                    }

                    // 隐藏上传区域
                    if (this.techTenderUpload) {
                        this.techTenderUpload.style.display = 'none';
                    }

                    console.log('[ProposalGenerator] HITL技术需求文件详细信息已加载:', {
                        fileName: technicalFileName,
                        fileSize: technicalFileSize
                    });
                } else if (hitlTaskId) {
                    // 如果只有taskId但没有文件详细信息,显示通用提示(兼容旧版本)
                    if (this.techTechnicalFileDisplay) {
                        this.techTechnicalFileDisplay.classList.remove('d-none');
                    }
                    if (this.techTechnicalFileDisplayName) {
                        this.techTechnicalFileDisplayName.textContent = '技术需求文件';
                    }
                    if (this.techTechnicalFileDisplaySize) {
                        this.techTechnicalFileDisplaySize.textContent = ' (已从投标项目加载)';
                    }

                    // 隐藏上传区域
                    if (this.techTenderUpload) {
                        this.techTenderUpload.style.display = 'none';
                    }

                    console.log('[ProposalGenerator] HITL技术需求文件信息已加载(通用提示)');
                }
            }

            // 保存URL参数供loadCompanies使用
            this.urlCompanyId = companyId;
        } catch (error) {
            console.error('[ProposalGenerator] 解析URL参数失败:', error);
        }
    }

    /**
     * 从 HITL Tab 加载数据
     * 当用户从 HITL Tab 点击快捷按钮切换到技术方案 Tab 时调用
     */
    loadFromHITL() {
        if (!window.projectDataBridge) {
            console.warn('[ProposalGenerator] projectDataBridge 未定义,无法加载 HITL 数据');
            return;
        }

        const bridge = window.projectDataBridge;
        console.log('[ProposalGenerator] 开始从 HITL 加载数据:', bridge);

        // 公司和项目信息已通过 projectDataBridge 传递，无需额外设置
        if (bridge.companyId && bridge.companyName) {
            console.log('[ProposalGenerator] 公司和项目信息:', {
                companyId: bridge.companyId,
                companyName: bridge.companyName,
                projectName: bridge.projectName
            });
        }

        // 【修复】加载技术需求文件信息 - 改用通用方法 getFileInfo
        const techFile = bridge.getFileInfo('techProposal');
        if (techFile && (techFile.taskId || techFile.fileName)) {
            this.hitlTaskId = techFile.taskId;
            console.log('[ProposalGenerator] 加载技术需求文件信息:', techFile);

            // 填充隐藏字段
            if (this.techTechnicalFileTaskId && techFile.taskId) {
                this.techTechnicalFileTaskId.value = techFile.taskId;
            }
            if (this.techTechnicalFileUrl && techFile.fileUrl) {
                this.techTechnicalFileUrl.value = techFile.fileUrl;
            }

            // 显示文件信息
            if (techFile.fileName && this.techTechnicalFileDisplay) {
                this.techTechnicalFileDisplay.classList.remove('d-none');

                // 显示文件名
                if (this.techTechnicalFileDisplayName) {
                    this.techTechnicalFileDisplayName.textContent = techFile.fileName;
                }

                // 格式化并显示文件大小
                if (this.techTechnicalFileDisplaySize && techFile.fileSize) {
                    const sizeKB = (parseInt(techFile.fileSize) / 1024).toFixed(2);
                    this.techTechnicalFileDisplaySize.textContent = ` (${sizeKB} KB)`;
                }

                // 隐藏上传区域
                if (this.techTenderUpload) {
                    this.techTenderUpload.style.display = 'none';
                }

                console.log('[ProposalGenerator] 从 HITL 加载的技术需求文件信息已显示:', {
                    fileName: techFile.fileName,
                    fileSize: techFile.fileSize
                });
            }
        } else {
            console.log('[ProposalGenerator] 未找到技术需求文件信息');
        }

        // 检查表单状态
        this.checkFormReady();
    }

    /**
     * 加载公司列表
     */
    async loadCompanies() {
        if (!this.techCompanySelect) {
            console.log('技术方案公司选择器不存在');
            return;
        }

        console.log('开始加载技术方案公司列表...');

        try {
            const response = await fetch('/api/companies');
            const data = await response.json();

            console.log('技术方案API返回的公司数据:', data);

            // 清空现有选项
            this.techCompanySelect.innerHTML = '<option value="">请选择公司...</option>';

            if (data.success && data.data && data.data.length > 0) {
                // 遍历公司列表并添加选项
                data.data.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.company_id;
                    option.textContent = company.company_name;
                    this.techCompanySelect.appendChild(option);
                });

                console.log(`技术方案成功加载 ${data.data.length} 家公司`);

                // 加载完成后,如果有URL参数中的company_id,自动选中
                if (this.urlCompanyId) {
                    this.techCompanySelect.value = this.urlCompanyId;
                    console.log('[ProposalGenerator] 自动选中URL传递的公司ID:', this.urlCompanyId);
                }
            } else {
                console.log('技术方案没有找到公司数据');
                this.techCompanySelect.innerHTML = '<option value="">暂无公司数据</option>';
            }
        } catch (error) {
            console.error('技术方案加载公司列表失败:', error);
            this.techCompanySelect.innerHTML = '<option value="">加载失败，请刷新重试</option>';
        }
    }

    /**
     * 预览技术方案
     */
    previewProposal(filePath) {
        console.log('[previewProposal] 预览文件:', filePath);

        // 从文件路径获取文件名
        const filename = filePath.split('/').pop();

        // 打开预览模态框（如果页面中有docx preview组件）
        // 使用与商务应答类似的预览逻辑
        const previewModal = document.getElementById('documentPreviewModal');
        if (!previewModal) {
            // 如果没有预览模态框，使用新窗口预览
            window.open(`/api/document/preview/${encodeURIComponent(filename)}`, '_blank');
            return;
        }

        // 显示加载状态
        const previewContent = document.getElementById('documentPreviewContent');
        if (previewContent) {
            previewContent.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在加载文档...</p></div>';
        }

        // 显示预览模态框
        const modal = new bootstrap.Modal(previewModal);
        modal.show();

        // 获取文档并渲染
        const previewApiUrl = `/api/document/preview/${encodeURIComponent(filename)}`;

        fetch(previewApiUrl)
            .then(response => response.arrayBuffer())
            .then(arrayBuffer => {
                if (previewContent) {
                    // 清空容器
                    previewContent.innerHTML = '';

                    // 使用docx-preview渲染
                    if (typeof docx !== 'undefined' && docx.renderAsync) {
                        docx.renderAsync(arrayBuffer, previewContent, null, {
                            className: 'docx-preview',
                            inWrapper: true,
                            ignoreWidth: false,
                            ignoreHeight: false,
                            ignoreFonts: false,
                            breakPages: true,
                            ignoreLastRenderedPageBreak: true,
                            experimental: true,
                            trimXmlDeclaration: true
                        }).then(() => {
                            console.log('[previewProposal] 文档预览成功');
                        }).catch(err => {
                            console.error('[previewProposal] docx-preview渲染失败:', err);
                            previewContent.innerHTML = '<div class="text-center text-danger"><i class="bi bi-exclamation-triangle fs-1"></i><p class="mt-2">文档渲染失败，请尝试下载文档</p></div>';
                        });
                    } else {
                        previewContent.innerHTML = '<div class="text-center text-warning"><i class="bi bi-exclamation-triangle fs-1"></i><p class="mt-2">预览组件未加载，请尝试下载文档</p></div>';
                    }
                }
            })
            .catch(error => {
                console.error('[previewProposal] 预览失败:', error);
                if (previewContent) {
                    previewContent.innerHTML = '<div class="text-center text-danger"><i class="bi bi-exclamation-triangle fs-1"></i><p class="mt-2">预览失败，请尝试下载文档</p></div>';
                }
            });
    }

    /**
     * 同步技术方案到HITL项目
     */
    async syncToHitl(hitlTaskId, outputFiles) {
        console.log('[syncToHitl] 开始同步技术方案到HITL项目');
        console.log('[syncToHitl] 任务ID:', hitlTaskId);
        console.log('[syncToHitl] 输出文件:', outputFiles);

        const btn = document.getElementById('syncTechProposalToHitlBtn');
        if (!btn) {
            console.error('[syncToHitl] 未找到同步按钮');
            return;
        }

        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>同步中...';

        try {
            // 使用第一个输出文件（通常是技术方案主文件）
            const filePath = outputFiles.proposal || Object.values(outputFiles)[0];

            // 使用统一的文件同步API
            const response = await fetch(`/api/tender-processing/sync-file/${hitlTaskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_path: filePath,
                    file_type: 'tech_proposal'  // 指定文件类型
                })
            });

            const data = await response.json();
            console.log('[syncToHitl] API响应:', data);

            if (data.success) {
                // 显示成功状态
                btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已同步';
                btn.classList.remove('btn-info');
                btn.classList.add('btn-outline-success');

                // 显示成功通知
                window.notifications?.success(data.message || '技术方案已成功同步到投标项目');

                console.log('[syncToHitl] 同步成功');

                // 3秒后恢复按钮(允许重新同步)
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.classList.remove('btn-outline-success');
                    btn.classList.add('btn-info');
                    btn.disabled = false;
                }, 3000);
            } else {
                throw new Error(data.error || '同步失败');
            }
        } catch (error) {
            console.error('[syncToHitl] 同步失败:', error);
            btn.innerHTML = originalText;
            btn.disabled = false;

            // 显示错误通知
            window.notifications?.error('同步失败: ' + error.message);
        }
    }

    /**
     * 加载技术需求文件信息（从HITL跳转时）
     */
    loadTechnicalFileInfo(fileName, fileSize, fileUrl, taskId) {
        console.log('[ProposalGenerator.loadTechnicalFileInfo] 加载技术需求文件:', {
            fileName, fileSize, fileUrl, taskId
        });

        // 填充隐藏字段
        if (this.techTechnicalFileTaskId) {
            this.techTechnicalFileTaskId.value = taskId || '';
        }
        if (this.techTechnicalFileUrl) {
            this.techTechnicalFileUrl.value = fileUrl || '';
        }

        // 显示技术需求文件信息
        if (this.techTechnicalFileDisplayName) {
            this.techTechnicalFileDisplayName.textContent = fileName;
        }
        if (this.techTechnicalFileDisplaySize && fileSize) {
            this.techTechnicalFileDisplaySize.textContent = ` (${fileSize})`;
        }

        // 显示技术需求文件显示区域
        if (this.techTechnicalFileDisplay) {
            this.techTechnicalFileDisplay.classList.remove('d-none');
        }

        // 隐藏上传区域
        if (this.techTenderUpload) {
            this.techTenderUpload.style.display = 'none';
        }

        // 触发表单就绪检查
        this.checkFormReady();

        // 触发自定义事件
        document.dispatchEvent(new CustomEvent('technicalFileLoadedForTechProposal', {
            detail: { fileName, fileSize, fileUrl, taskId }
        }));
    }

    /**
     * 清除技术需求文件
     */
    clearTechnicalFile() {
        console.log('[ProposalGenerator.clearTechnicalFile] 清除技术需求文件');

        // 清空隐藏字段
        if (this.techTechnicalFileTaskId) {
            this.techTechnicalFileTaskId.value = '';
        }
        if (this.techTechnicalFileUrl) {
            this.techTechnicalFileUrl.value = '';
        }

        // 隐藏技术需求文件显示区域
        if (this.techTechnicalFileDisplay) {
            this.techTechnicalFileDisplay.classList.add('d-none');
        }

        // 显示上传区域
        if (this.techTenderUpload) {
            this.techTenderUpload.style.display = 'block';
        }

        // 触发表单就绪检查
        this.checkFormReady();
    }

    /**
     * 销毁生成器
     */
    destroy() {
        if (this.currentController) {
            this.currentController.abort();
        }

        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }
}

// 全局技术方案生成器实例变量
window.proposalGenerator = null;

// 在DOM准备好后创建实例
document.addEventListener('DOMContentLoaded', function() {
    if (!window.proposalGenerator) {
        window.proposalGenerator = new ProposalGenerator();
    }
});

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProposalGenerator;
}