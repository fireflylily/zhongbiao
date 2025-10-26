/**
 * 技术方案生成模块 - 前端交互管理
 * 负责技术方案生成的文件上传、配置管理和结果展示
 */

class ProposalGenerator {
    // ========================================
    // 静态配置
    // ========================================
    static CONFIG = {
        // 延迟时间配置（毫秒）
        DELAYS: {
            TAB_SWITCH: 200,              // 标签页切换延迟
            BUTTON_RESTORE: 3000,         // 按钮状态恢复时间
            DOWNLOAD_CLEANUP: 100,        // 下载清理延迟
            VERIFY_CONTENT: 100,          // 内容验证延迟
            BIND_CLEAR_BUTTON: 50,        // 绑定清除按钮延迟
            PROGRESS_HIDE: 1000           // 进度条隐藏延迟
        },

        // 文件限制配置
        FILE: {
            MAX_SIZE: 50 * 1024 * 1024,   // 50MB
            ALLOWED_TYPES: [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword',
                'application/pdf'
            ],
            ALLOWED_EXTENSIONS: ['.docx', '.doc', '.pdf']
        },

        // 复杂度样式映射
        COMPLEXITY: {
            COLORS: {
                low: 'success',
                medium: 'warning',
                high: 'danger'
            },
            TEXTS: {
                low: '低',
                medium: '中',
                high: '高'
            }
        },

        // 优先级样式映射
        PRIORITY: {
            COLORS: {
                high: 'danger',
                medium: 'warning',
                low: 'success'
            },
            TEXTS: {
                high: '高优先级',
                medium: '中优先级',
                low: '低优先级'
            }
        },

        // 按钮配置
        BUTTON_CONFIGS: {
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
        },

        // 按钮生成顺序配置
        BUTTON_ACTIONS: [
            {
                type: 'preview',
                condition: (files) => files.proposal,
                create: function(outputFiles) {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-primary me-2 mb-2';
                    btn.innerHTML = '<i class="bi bi-eye"></i> 预览';
                    btn.onclick = (e) => {
                        e.preventDefault();
                        this.previewProposal(outputFiles.proposal);
                    };
                    return btn;
                }
            },
            {
                type: 'downloads',
                condition: (files) => Object.keys(files).length > 0,
                create: function(outputFiles) {
                    const buttons = [];
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
                        buttons.push(button);
                    });
                    return buttons;
                }
            },
            {
                type: 'complete',
                condition: () => true,
                create: function() {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-secondary me-2 mb-2';
                    btn.innerHTML = '<i class="bi bi-check-circle"></i> 完成';
                    btn.onclick = (e) => {
                        e.preventDefault();
                        if (this.hitlTaskId) {
                            window.location.href = `/hitl?task_id=${this.hitlTaskId}`;
                        } else {
                            window.location.href = '/';
                        }
                    };
                    return btn;
                }
            },
            {
                type: 'sync',
                condition: function() { return this.hitlTaskId; },
                create: function(outputFiles, data) {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-info me-2 mb-2';
                    btn.id = 'syncTechProposalToHitlBtn';
                    btn.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>同步到投标项目';
                    btn.onclick = () => this.syncToHitl(this.hitlTaskId, data);
                    return btn;
                }
            }
        ],

        // 生成阶段名称映射
        STAGE_NAMES: {
            'init': '初始化',
            'analysis': '需求分析',
            'outline': '大纲生成',
            'matching': '文档匹配',
            'assembly': '方案组装',
            'export': '导出文件',
            'completed': '完成',
            'error': '错误'
        }
    };

    // 调试开关（可通过环境变量或控制台切换）
    static DEBUG = false;

    constructor() {
        this.isGenerating = false;
        this.currentController = null;
        this.progressInterval = null;
        this.boundListeners = {};          // 存储事件监听器引用
        this.unsubscribers = [];           // 存储GlobalState取消订阅函数
        this.sseClient = null;             // SSE客户端实例

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

        // ✅ 订阅全局状态变化（自动更新）
        if (window.globalState) {
            // 订阅技术文件变化
            const unsubFiles = window.globalState.subscribe('files', (fileData) => {
                if (fileData.type === 'technical' && fileData.data) {
                    this.log('收到技术文件变化通知，自动加载');
                    this.loadFromHITL();
                }
            });
            this.unsubscribers.push(unsubFiles);

            // 订阅公司变化
            const unsubCompany = window.globalState.subscribe('company', (companyData) => {
                this.log('收到公司变化通知:', companyData);
                if (this.techCompanySelect && companyData.id) {
                    this.techCompanySelect.value = companyData.id;
                }
            });
            this.unsubscribers.push(unsubCompany);

            // 订阅 AI 模型变化
            const unsubAI = window.globalState.subscribe('ai', (aiData) => {
                if (aiData.type === 'selectedModel') {
                    this.debug('收到AI模型变化通知:', aiData.data);
                    const modelDisplay = document.querySelector('.modelNameDisplay[data-section="tech-proposal"]');
                    if (modelDisplay) {
                        const models = window.globalState.getAvailableModels();
                        const modelInfo = models.find(m => m.name === aiData.data);
                        modelDisplay.textContent = modelInfo ? modelInfo.display_name : aiData.data;
                    }
                }
            });
            this.unsubscribers.push(unsubAI);
        }

        // 监听从 HITL Tab 切换过来的事件
        this.boundListeners.loadTechnicalProposal = (event) => {
            if (event.detail?.fromHITL) {
                this.log('收到来自 HITL 的加载事件:', event.detail);
                // 延迟执行,等待Tab渲染完成
                this.delay(this.getConfig('DELAYS.TAB_SWITCH')).then(() => {
                    this.log('即将执行 loadFromHITL()...');
                    this.loadFromHITL();
                    this.log('loadFromHITL() 调用完成');
                });
            }
        };
        window.addEventListener('loadTechnicalProposal', this.boundListeners.loadTechnicalProposal);
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

    // ========================================
    // 辅助工具方法
    // ========================================

    /**
     * 统一日志输出 - 支持日志分级
     * @param {string} level - 日志级别: 'debug', 'info', 'warn', 'error'
     * @param  {...any} args - 日志内容
     */
    log(level, ...args) {
        // 如果只传入一个参数，默认为debug级别（向后兼容）
        if (typeof level !== 'string' || !['debug', 'info', 'warn', 'error'].includes(level)) {
            args.unshift(level);
            level = 'debug';
        }

        const prefix = '[ProposalGenerator]';

        // debug级别的日志只在DEBUG模式下显示
        if (level === 'debug' && !ProposalGenerator.DEBUG) {
            return;
        }

        // 根据级别选择console方法
        const consoleMethod = console[level] || console.log;
        consoleMethod(prefix, ...args);
    }

    /**
     * 便捷方法 - 调试日志（仅DEBUG模式）
     */
    debug(...args) {
        this.log('debug', ...args);
    }

    /**
     * 便捷方法 - 信息日志（始终显示）
     */
    info(...args) {
        this.log('info', ...args);
    }

    /**
     * 便捷方法 - 警告日志（始终显示）
     */
    warn(...args) {
        this.log('warn', ...args);
    }

    /**
     * 便捷方法 - 错误日志（始终显示）
     */
    error(...args) {
        this.log('error', ...args);
    }

    /**
     * 通知辅助方法 - 统一通知接口
     */
    notify(type, message) {
        if (window.notifications) {
            window.notifications[type](message);
        }
    }

    /**
     * DOM 显示/隐藏辅助方法
     */
    showElement(element) {
        if (element) {
            element.classList.remove('d-none');
        }
    }

    hideElement(element) {
        if (element) {
            element.classList.add('d-none');
        }
    }

    toggleElement(element, show) {
        if (show) {
            this.showElement(element);
        } else {
            this.hideElement(element);
        }
    }

    /**
     * 设置元素HTML内容
     */
    setElementHTML(element, html) {
        if (element) {
            element.innerHTML = html;
        }
    }

    /**
     * 设置元素文本内容
     */
    setTextContent(element, text) {
        if (element) {
            element.textContent = text;
        }
    }

    /**
     * 设置元素值（input/select等）
     */
    setValue(element, value) {
        if (element) {
            element.value = value;
        }
    }

    /**
     * 获取元素值
     */
    getValue(element, defaultValue = '') {
        return element?.value || defaultValue;
    }

    /**
     * 切换CSS类
     */
    toggleClass(element, className, condition) {
        if (!element) return;
        if (condition) {
            element.classList.add(className);
        } else {
            element.classList.remove(className);
        }
    }

    /**
     * 添加CSS类
     */
    addClass(element, className) {
        if (element) {
            element.classList.add(className);
        }
    }

    /**
     * 移除CSS类
     */
    removeClass(element, className) {
        if (element) {
            element.classList.remove(className);
        }
    }

    /**
     * 设置元素样式
     */
    setStyle(element, property, value) {
        if (element && element.style) {
            element.style[property] = value;
        }
    }

    /**
     * 设置元素disabled状态
     */
    setDisabled(element, disabled) {
        if (element) {
            element.disabled = disabled;
        }
    }

    /**
     * 延迟执行辅助方法
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 文件大小格式化
     */
    formatFileSize(bytes) {
        if (!bytes) return '';
        const kb = (parseInt(bytes) / 1024).toFixed(2);
        return `${kb} KB`;
    }

    /**
     * HTML 转义
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 获取配置值（支持嵌套路径）
     */
    getConfig(path) {
        const keys = path.split('.');
        let value = ProposalGenerator.CONFIG;
        for (const key of keys) {
            value = value?.[key];
            if (value === undefined) break;
        }
        return value;
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
        this.boundListeners.companyChanged = (e) => {
            if (e.detail?.company_id && this.techCompanySelect) {
                this.debug('收到公司变化事件:', e.detail);
                this.techCompanySelect.value = e.detail.company_id;
            }
        };
        window.addEventListener('companyChanged', this.boundListeners.companyChanged);

        // 监听技术需求文件加载事件
        this.boundListeners.technicalFileLoaded = (e) => {
            this.debug('收到技术需求文件加载事件:', e.detail);
            this.checkFormReady();
        };
        document.addEventListener('technicalFileLoadedForTechProposal',
            this.boundListeners.technicalFileLoaded);
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
     * 验证文件 - 使用配置常量
     */
    validateFile(file, fileType) {
        const maxSize = this.getConfig('FILE.MAX_SIZE');
        const allowedTypes = this.getConfig('FILE.ALLOWED_TYPES');

        // 检查文件大小
        if (file.size > maxSize) {
            const maxSizeMB = maxSize / (1024 * 1024);
            this.notify('error', `${fileType}大小不能超过${maxSizeMB}MB`);
            return false;
        }

        // 检查文件类型
        if (!allowedTypes.includes(file.type)) {
            const extensions = this.getConfig('FILE.ALLOWED_EXTENSIONS').join(', ');
            this.notify('error', `${fileType}只支持 ${extensions} 格式`);
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

        this.debug('表单状态:', {
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
            this.notify('warning', '正在生成中，请稍候...');
            return;
        }

        // 验证招标文件（可以是上传的文件或从HITL传递的技术需求文件）
        const hasUploadedTenderFile = this.techTenderFileInput.files[0];
        const hasTechnicalFile = this.techTechnicalFileTaskId && this.techTechnicalFileTaskId.value;

        if (!hasUploadedTenderFile && !hasTechnicalFile) {
            this.notify('error', '请选择招标文件');
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
            if (window.globalState) {
                const projectName = window.globalState.getProjectName();
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
            this.error('技术方案生成失败:', error);

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
        // 创建SSE客户端实例
        if (!this.sseClient) {
            this.sseClient = new window.SSEClient();
        }

        const url = '/api/generate-proposal-stream';

        // 使用SSEClient统一处理SSE流
        return this.sseClient.stream({
            url: url,
            formData: formData,
            onEvent: (data) => this.handleSSEEvent(data),
            onComplete: (data) => {
                this.debug('SSE流完成:', data);
            },
            onError: (error) => {
                this.error('SSE流错误:', error);
                throw error;
            }
        });
    }

    /**
     * 处理SSE事件
     * @param {Object} data - 事件数据
     */
    handleSSEEvent(data) {
        this.debug('SSE事件:', data);

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

        // 处理大纲生成完成事件 - 显示大纲结果
        if (data.stage === 'outline_completed' && data.outline_data) {
            this.displayOutlineResult(data.outline_data);
        }

        // 处理完成事件
        this.debug('检查完成条件: stage=', data.stage, ', success=', data.success);
        if (data.stage === 'completed' && data.success) {
            this.debug('满足完成条件，调用showSuccess, output_files=', data.output_files);
            this.showSuccess(data);
        } else if (data.stage === 'completed') {
            this.warn('stage=completed但success不为true:', data.success);
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
        this.log(`阶段: ${stage}, 消息: ${message}`);

        // 更新按钮文本以显示当前阶段
        const stageNames = this.getConfig('STAGE_NAMES');
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
        this.debug('显示需求分析结果:', analysisResult);

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

        const complexityColors = this.getConfig('COMPLEXITY.COLORS');
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
        return this.getConfig('COMPLEXITY.TEXTS')[level] || '未知';
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

        const priorityColors = this.getConfig('PRIORITY.COLORS');

        const html = categories.map((category, index) => {
            const priorityColor = priorityColors[category.priority] || 'secondary';

            // 构建卡片内容
            const content = `
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
            `;

            // 使用通用方法渲染折叠卡片
            return this.renderCollapsibleCard({
                title: category.category,
                badges: [
                    {text: this.getPriorityText(category.priority), class: priorityColor},
                    {text: `${category.requirements_count || 0}项`, class: 'secondary'}
                ],
                content: content,
                index: `category-${index}`,
                iconClass: 'bi-folder2'
            });
        }).join('');

        container.innerHTML = html;
    }

    /**
     * 获取优先级文本
     * @param {string} priority - 优先级
     * @returns {string} 优先级文本
     */
    getPriorityText(priority) {
        return this.getConfig('PRIORITY.TEXTS')[priority] || '普通';
    }

    /**
     * 渲染折叠卡片（通用方法）
     * @param {Object} config - 卡片配置
     * @param {string} config.title - 卡片标题
     * @param {Array} config.badges - 徽章数组 [{text, class}]
     * @param {string} config.content - 卡片内容HTML
     * @param {string|number} config.index - 折叠元素索引
     * @param {string} config.iconClass - 标题图标类
     * @returns {string} HTML字符串
     */
    renderCollapsibleCard({title, badges = [], content, index, iconClass = 'bi-folder2'}) {
        const badgesHTML = badges.map(badge =>
            `<span class="badge bg-${badge.class} ms-${badge === badges[0] ? '2' : '1'}">${badge.text}</span>`
        ).join('');

        return `
            <div class="card mb-2">
                <div class="card-header py-2 bg-light">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>
                            <i class="${iconClass}"></i> <strong>${title}</strong>
                            ${badgesHTML}
                        </span>
                        <button class="btn btn-sm btn-link text-decoration-none"
                                type="button"
                                data-bs-toggle="collapse"
                                data-bs-target="#collapse-${index}">
                            <i class="bi bi-chevron-down"></i>
                        </button>
                    </div>
                </div>
                <div class="collapse" id="collapse-${index}">
                    <div class="card-body">${content}</div>
                </div>
            </div>
        `;
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
     * 统一的Toggle按钮设置方法
     * @param {string} btnId - 按钮ID
     * @param {string} contentId - 内容区域ID
     */
    setupToggle(btnId, contentId) {
        const toggleBtn = document.getElementById(btnId);
        const contentArea = document.getElementById(contentId);

        if (!toggleBtn || !contentArea) return;

        // 移除旧的事件监听器
        const newToggleBtn = toggleBtn.cloneNode(true);
        toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);

        // 添加新的事件监听器
        newToggleBtn.addEventListener('click', () => {
            const isHidden = contentArea.style.display === 'none';
            contentArea.style.display = isHidden ? 'block' : 'none';
            newToggleBtn.innerHTML = isHidden
                ? '<i class="bi bi-chevron-up"></i> 收起'
                : '<i class="bi bi-chevron-down"></i> 展开';
        });
    }

    /**
     * 设置分析结果展开/收起功能
     */
    setupAnalysisToggle() {
        this.setupToggle('toggleAnalysisDetail', 'analysisResultContent');
    }

    /**
     * 显示大纲结果
     * @param {Object} outlineData - 大纲数据
     */
    displayOutlineResult(outlineData) {
        this.debug('显示大纲结果:', outlineData);

        const outlineArea = document.getElementById('outlineResultArea');
        if (!outlineArea) return;

        // 显示大纲结果区域
        outlineArea.classList.remove('d-none');

        // 渲染大纲摘要
        this.renderOutlineSummary(outlineData);

        // 渲染章节树
        this.renderOutlineChapters(outlineData.chapters || []);

        // 添加展开/收起功能
        this.setupOutlineToggle();
    }

    /**
     * 渲染大纲摘要
     * @param {Object} outlineData - 大纲数据
     */
    renderOutlineSummary(outlineData) {
        const summaryContainer = document.getElementById('outlineSummary');
        if (!summaryContainer) return;

        const totalChapters = outlineData.total_chapters || 0;
        const estimatedPages = outlineData.estimated_pages || 0;
        const generationTime = outlineData.generation_time || '未知';

        summaryContainer.innerHTML = `
            <div class="col-md-4">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-file-earmark-text text-success fs-4"></i>
                    <div class="mt-2"><strong>${outlineData.outline_title || '技术方案应答大纲'}</strong></div>
                    <small class="text-muted">大纲标题</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-list-ol text-primary fs-4"></i>
                    <div class="mt-2"><strong>${totalChapters}</strong></div>
                    <small class="text-muted">总章节数</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-file-earmark-pdf text-info fs-4"></i>
                    <div class="mt-2"><strong>${estimatedPages}</strong></div>
                    <small class="text-muted">预计页数</small>
                </div>
            </div>
            <div class="col-md-2">
                <div class="text-center p-2 border rounded">
                    <i class="bi bi-clock text-secondary fs-4"></i>
                    <div class="mt-2"><small>${generationTime}</small></div>
                    <small class="text-muted">生成时间</small>
                </div>
            </div>
        `;
    }

    /**
     * 渲染章节树
     * @param {Array} chapters - 章节列表
     */
    renderOutlineChapters(chapters) {
        const container = document.getElementById('outlineChapters');
        if (!container) return;

        if (chapters.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无章节</p>';
            return;
        }

        let html = '<ul class="list-unstyled">';

        chapters.forEach(chapter => {
            const level = chapter.level || 1;
            const chapterNumber = chapter.chapter_number || '';
            const title = chapter.title || '';
            const description = chapter.description || '';

            // 根据层级设置缩进和样式
            const indentClass = level === 1 ? 'ps-0' : level === 2 ? 'ps-3' : 'ps-5';
            const iconClass = level === 1 ? 'bi-folder-fill text-primary' :
                             level === 2 ? 'bi-folder text-info' : 'bi-file-text text-secondary';
            const fontWeight = level === 1 ? 'fw-bold' : level === 2 ? 'fw-semibold' : '';

            html += `
                <li class="${indentClass} mb-2">
                    <div class="d-flex align-items-start">
                        <i class="bi ${iconClass} me-2 mt-1"></i>
                        <div class="flex-grow-1">
                            <span class="${fontWeight}">${chapterNumber} ${this.escapeHtml(title)}</span>
                            ${description ? `<br><small class="text-muted">${this.escapeHtml(description)}</small>` : ''}
                        </div>
                    </div>
            `;

            // 递归渲染子章节
            if (chapter.subsections && chapter.subsections.length > 0) {
                html += '<ul class="list-unstyled mt-1">';
                chapter.subsections.forEach(subsection => {
                    const subNumber = subsection.chapter_number || '';
                    const subTitle = subsection.title || '';
                    const subDesc = subsection.description || '';

                    html += `
                        <li class="ps-4 mb-1">
                            <div class="d-flex align-items-start">
                                <i class="bi bi-file-text text-secondary me-2 mt-1" style="font-size: 0.85rem;"></i>
                                <div class="flex-grow-1">
                                    <span class="small">${subNumber} ${this.escapeHtml(subTitle)}</span>
                                    ${subDesc ? `<br><small class="text-muted" style="font-size: 0.75rem;">${this.escapeHtml(subDesc)}</small>` : ''}
                                </div>
                            </div>
                        </li>
                    `;
                });
                html += '</ul>';
            }

            html += '</li>';
        });

        html += '</ul>';
        container.innerHTML = html;
    }

    /**
     * 设置大纲展开/收起功能
     */
    setupOutlineToggle() {
        this.setupToggle('toggleOutlineDetail', 'outlineResultContent');
    }

    /**
     * 隐藏进度条
     */
    hideProgress() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }

        this.delay(this.getConfig('DELAYS.PROGRESS_HIDE')).then(() => {
            this.hideElement(this.techProgressBar);
            this.updateProgressBar(0);

            if (this.generateProposalBtn) {
                this.generateProposalBtn.disabled = false;
                this.generateProposalBtn.innerHTML = '<i class="bi bi-magic"></i> 生成技术方案';
            }

            this.checkFormReady(); // 重新检查表单状态
        });
    }

    /**
     * 显示成功结果
     */
    showSuccess(data) {
        this.debug('showSuccess被调用, data=', data);
        this.updateProgressBar(100);

        // 更新统计信息
        const techResultMessage = document.getElementById('techResultMessage');
        this.debug('techResultMessage element=', techResultMessage);
        if (techResultMessage) {
            const stats = this.formatStatistics(data);
            techResultMessage.innerHTML = stats;
            this.debug('统计信息已更新');
        }

        // 生成下载按钮（配置驱动，自动处理同步按钮）
        this.debug('techDownloadArea=', this.techDownloadArea, ', output_files=', data.output_files);
        if (this.techDownloadArea && data.output_files) {
            this.debug('调用createDownloadButtons');
            this.createDownloadButtons(data.output_files, data);  // ✅ 传递完整的 data 对象
        } else {
            this.warn('无法创建下载按钮: techDownloadArea=', this.techDownloadArea, ', output_files=', data.output_files);
        }

        this.debug('techResultArea=', this.techResultArea);
        if (this.techResultArea) {
            this.techResultArea.classList.remove('d-none');
            this.debug('techResultArea已显示（移除d-none）');
        } else {
            this.warn('techResultArea元素不存在');
        }

        this.notify('success', '技术方案生成完成');
        this.debug('showSuccess完成');
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
     * 创建下载按钮（配置驱动）
     */
    createDownloadButtons(outputFiles, data = null) {
        this.debug('createDownloadButtons被调用, outputFiles=', outputFiles);
        this.techDownloadArea.innerHTML = '';

        // 使用配置驱动的方式生成按钮
        const buttonActions = this.getConfig('BUTTON_ACTIONS');

        buttonActions.forEach(action => {
            // 检查条件是否满足
            const conditionMet = action.condition.call(this, outputFiles);
            if (!conditionMet) {
                this.debug(`跳过按钮类型: ${action.type} (条件不满足)`);
                return;
            }

            this.debug(`创建按钮类型: ${action.type}`);

            // 调用create函数生成按钮
            const result = action.create.call(this, outputFiles, data);

            // 处理返回结果（可能是单个按钮或按钮数组）
            if (Array.isArray(result)) {
                result.forEach(btn => this.techDownloadArea.appendChild(btn));
            } else if (result) {
                this.techDownloadArea.appendChild(result);
            }
        });

        this.debug('所有按钮创建完成');
    }

    /**
     * 获取按钮配置
     */
    getButtonConfig(fileType) {
        const configs = this.getConfig('BUTTON_CONFIGS');

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

        this.showElement(this.techErrorArea);
        this.notify('error', '技术方案生成失败');
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
            this.notify('info', '开始下载...');

            const link = document.createElement('a');
            link.href = url;
            link.download = filename || '';
            link.style.display = 'none';

            document.body.appendChild(link);
            link.click();

            this.delay(this.getConfig('DELAYS.DOWNLOAD_CLEANUP')).then(() => {
                document.body.removeChild(link);
                this.notify('success', '下载已开始');
            });

        } catch (error) {
            this.error('下载失败:', error);
            this.notify('error', '下载失败: ' + error.message);
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
        this.hideElement(this.techTenderFileInfo);
        this.hideElement(this.productFileInfo);

        // 重置输出前缀
        if (this.outputPrefix) {
            this.outputPrefix.value = '技术方案';
        }

        this.checkFormReady();
        this.notify('info', '表单已重置');
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

            this.debug('解析URL参数:', {
                companyId, companyName, projectId, projectName, hitlTaskId,
                technicalFileName, technicalFileSize, technicalFileUrl
            });

            // 如果有公司和项目信息,通过globalState设置
            if (companyId && companyName && window.globalState) {
                this.debug('设置公司和项目信息到状态管理器');
                window.globalState.setCompany(parseInt(companyId), companyName);
                if (projectId && projectName) {
                    window.globalState.setProject(parseInt(projectId), projectName);
                }
            }

            // 保存hitl_task_id供后续使用(如果需要同步回HITL)
            if (hitlTaskId) {
                this.hitlTaskId = hitlTaskId;
                this.debug('保存HITL任务ID:', hitlTaskId);

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

                    this.debug('HITL技术需求文件详细信息已加载:', {
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

                    this.debug('HITL技术需求文件信息已加载(通用提示)');
                }
            }

            // 保存URL参数供loadCompanies使用
            this.urlCompanyId = companyId;
        } catch (error) {
            this.error('解析URL参数失败:', error);
        }
    }

    /**
     * ✅ 从 HITL Tab 加载数据（已优化重构）
     * 当用户从 HITL Tab 点击快捷按钮切换到技术方案 Tab 时调用
     */
    loadFromHITL() {
        this.log('开始从HITL加载数据');

        if (!window.globalState) {
            this.warn('globalState 未定义');
            return;
        }

        // 1. 加载公司信息
        this.loadCompanyFromState();

        // 2. 加载技术需求文件
        this.loadTechnicalFileFromState();

        // 3. 检查表单状态
        this.checkFormReady();

        this.log('从HITL加载数据完成');
    }

    /**
     * 从 GlobalState 加载公司信息
     */
    loadCompanyFromState() {
        const company = window.globalState.getCompany();
        if (company?.id && this.techCompanySelect) {
            this.techCompanySelect.value = company.id;
            this.log('公司信息已加载:', company.name);
        }
    }

    /**
     * 从 GlobalState 加载技术需求文件信息
     */
    loadTechnicalFileFromState() {
        const techFile = window.globalState.getFile('technical');
        const hitlTaskId = window.globalState.getHitlTaskId();

        this.log('====== 文件信息诊断开始 ======');
        this.log('techFile:', techFile);
        this.log('HITL任务ID:', hitlTaskId);

        if (!techFile?.fileName) {
            this.warn('[FAIL] 未找到技术需求文件');
            this.warn('techFile 完整对象:', JSON.stringify(techFile, null, 2));
            this.log('====== 文件信息诊断结束 ======');
            return;
        }

        this.log('[PASS] 找到技术需求文件:', techFile.fileName);

        // 保存任务ID
        this.hitlTaskId = hitlTaskId;
        this.log('已保存 hitlTaskId:', this.hitlTaskId);

        // 填充隐藏字段
        this.populateHiddenFields(hitlTaskId, techFile);

        // 显示文件信息
        this.displayTechnicalFileInfo(techFile);

        // 隐藏上传区域
        this.hideUploadArea();

        this.log('====== 文件信息诊断结束 ======');
    }

    /**
     * 填充隐藏字段（任务ID和文件URL）
     */
    populateHiddenFields(hitlTaskId, techFile) {
        if (this.techTechnicalFileTaskId && hitlTaskId) {
            this.techTechnicalFileTaskId.value = hitlTaskId;
            this.log('已设置 techTechnicalFileTaskId:', hitlTaskId);
        }

        if (this.techTechnicalFileUrl && techFile.fileUrl) {
            this.techTechnicalFileUrl.value = techFile.fileUrl;
            this.log('已设置 techTechnicalFileUrl:', techFile.fileUrl);
        }
    }

    /**
     * 显示技术需求文件信息
     */
    displayTechnicalFileInfo(techFile) {
        if (!this.techTechnicalFileDisplay) {
            this.error('[ERROR] 未找到 techTechnicalFileDisplay 元素');
            return;
        }

        this.log('[FOUND] 找到 techTechnicalFileDisplay 元素，准备设置 innerHTML');

        // 格式化文件大小
        const sizeText = techFile.fileSize
            ? ` <span class="text-muted small">(${this.formatFileSize(techFile.fileSize)})</span>`
            : '';

        // 设置完整HTML内容
        this.techTechnicalFileDisplay.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <i class="bi bi-file-earmark-check me-2"></i>
                    <strong>已从投标项目加载技术需求文件：</strong><br>
                    <span class="text-muted small">${this.escapeHtml(techFile.fileName)}</span>
                    ${sizeText}
                    <span class="badge bg-success ms-2">已从投标项目加载</span>
                </div>
                <button type="button" class="btn btn-sm btn-outline-secondary"
                        id="techClearTechnicalFile">
                    <i class="bi bi-x"></i> 重新上传
                </button>
            </div>
        `;

        // 显示元素
        this.showElement(this.techTechnicalFileDisplay);
        this.log('[SUCCESS] innerHTML 已设置成功');

        // 重新绑定清除按钮事件
        this.delay(this.getConfig('DELAYS.BIND_CLEAR_BUTTON')).then(() => {
            const clearBtn = document.getElementById('techClearTechnicalFile');
            if (clearBtn) {
                clearBtn.onclick = () => this.clearTechnicalFile();
                this.log('已重新绑定清除按钮事件');
            }
        });

        // 验证DOM内容（仅在DEBUG模式）
        if (ProposalGenerator.DEBUG) {
            this.delay(this.getConfig('DELAYS.VERIFY_CONTENT')).then(() => {
                this.verifyElementContent();
            });
        }
    }

    /**
     * 验证元素内容是否正确显示（调试用）
     */
    verifyElementContent() {
        const checkDiv = this.techTechnicalFileDisplay;
        this.log('[VERIFY] 验证元素内容:', checkDiv?.innerHTML);
        this.log('[VERIFY] 元素是否可见:', checkDiv?.offsetParent !== null);
        this.log('[VERIFY] 是否有d-none类:', checkDiv?.classList.contains('d-none'));

        if (!checkDiv || checkDiv.innerHTML.trim() === '') {
            this.error('[ERROR] 验证失败！innerHTML被清空了！');
        } else if (checkDiv.classList.contains('d-none')) {
            this.error('[ERROR] 验证失败！元素被重新隐藏了！');
        } else {
            this.log('[VERIFY] 验证成功，内容仍然存在且可见');
        }
    }

    /**
     * 隐藏上传区域
     */
    hideUploadArea() {
        this.log('查找 techTenderUpload 元素:', this.techTenderUpload);

        if (this.techTenderUpload) {
            this.techTenderUpload.style.display = 'none';
            this.techTenderUpload.onclick = null;
            this.techTenderUpload.style.pointerEvents = 'none';
            this.techTenderUpload.style.cursor = 'default';
            this.log('[SUCCESS] 已隐藏上传区域并禁用点击事件');
        } else {
            this.warn('[WARN] 未找到 techTenderUpload 元素');
        }
    }

    /**
     * 加载公司列表
     */
    async loadCompanies() {
        if (!this.techCompanySelect) {
            this.debug('技术方案公司选择器不存在');
            return;
        }

        this.debug('开始加载技术方案公司列表...');

        try {
            const response = await fetch('/api/companies');
            const data = await response.json();

            this.debug('技术方案API返回的公司数据:', data);

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

                this.debug(`技术方案成功加载 ${data.data.length} 家公司`);

                // 加载完成后,如果有URL参数中的company_id,自动选中
                if (this.urlCompanyId) {
                    this.techCompanySelect.value = this.urlCompanyId;
                    this.debug('自动选中URL传递的公司ID:', this.urlCompanyId);
                }
            } else {
                this.debug('技术方案没有找到公司数据');
                this.techCompanySelect.innerHTML = '<option value="">暂无公司数据</option>';
            }
        } catch (error) {
            this.error('技术方案加载公司列表失败:', error);
            this.techCompanySelect.innerHTML = '<option value="">加载失败，请刷新重试</option>';
        }
    }

    /**
     * 预览技术方案 - 使用统一预览工具
     */
    previewProposal(filePath) {
        this.log('预览文件:', filePath);

        // 从文件路径获取文件名
        const filename = filePath.split('/').pop();
        const downloadUrl = `/api/document/preview/${encodeURIComponent(filename)}`;

        // 使用统一的文档预览工具
        if (window.documentPreviewUtil) {
            window.documentPreviewUtil.preview(downloadUrl, filename);
        } else {
            // 降级方案：新窗口打开
            this.warn('documentPreviewUtil 不可用，使用新窗口打开');
            window.open(downloadUrl, '_blank');
        }
    }

    /**
     * 同步技术方案到HITL项目
     */
    async syncToHitl(hitlTaskId, data) {
        this.debug('开始同步技术方案到HITL项目');
        this.debug('任务ID:', hitlTaskId);
        this.debug('数据:', data);

        const btn = document.getElementById('syncTechProposalToHitlBtn');
        if (!btn) {
            this.error('未找到同步按钮');
            return;
        }

        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>同步中...';

        try {
            // ✅ 使用 output_file（文件系统路径），与商务应答/点对点应答保持一致
            const filePath = data.output_file;

            if (!filePath) {
                throw new Error('未找到技术方案文件路径');
            }

            this.debug('准备发送请求:',{
                url: `/api/tender-processing/sync-file/${hitlTaskId}`,
                file_path: filePath,
                file_type: 'tech_proposal'
            });

            // ✅ 使用 window.apiClient 统一处理API调用（自动CSRF、重试、错误处理）
            const responseData = await window.apiClient.post(
                `/api/tender-processing/sync-file/${hitlTaskId}`,
                {
                    file_path: filePath,
                    file_type: 'tech_proposal'  // 指定文件类型
                }
            );

            this.debug('API响应:', responseData);

            if (responseData.success) {
                // 显示成功状态
                btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已同步';
                btn.classList.remove('btn-info');
                btn.classList.add('btn-outline-success');

                // 显示成功通知
                this.notify('success', responseData.message || '技术方案已成功同步到投标项目');

                this.info('同步成功');

                // 恢复按钮(允许重新同步)
                this.delay(this.getConfig('DELAYS.BUTTON_RESTORE')).then(() => {
                    btn.innerHTML = originalText;
                    btn.classList.remove('btn-outline-success');
                    btn.classList.add('btn-info');
                    btn.disabled = false;
                });
            } else {
                throw new Error(responseData.error || responseData.message || '同步失败');
            }
        } catch (error) {
            this.error('同步失败:', error);
            btn.innerHTML = originalText;
            btn.disabled = false;

            // apiClient已经提供友好的错误信息，直接使用
            this.notify('error', `同步失败: ${error.message}`);
        }
    }

    /**
     * 加载技术需求文件信息（从HITL跳转时）
     */
    loadTechnicalFileInfo(fileName, fileSize, fileUrl, taskId) {
        this.debug('加载技术需求文件:', {
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
        this.debug('清除技术需求文件');

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
     * 销毁生成器 - 清理所有资源和监听器
     */
    destroy() {
        // 清理定时器和控制器
        if (this.currentController) {
            this.currentController.abort();
        }

        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        // 清理SSE客户端
        if (this.sseClient) {
            this.sseClient.abort();
            this.sseClient = null;
        }

        // 清理全局事件监听器
        if (this.boundListeners.loadTechnicalProposal) {
            window.removeEventListener('loadTechnicalProposal',
                this.boundListeners.loadTechnicalProposal);
        }

        if (this.boundListeners.companyChanged) {
            window.removeEventListener('companyChanged',
                this.boundListeners.companyChanged);
        }

        if (this.boundListeners.technicalFileLoaded) {
            document.removeEventListener('technicalFileLoadedForTechProposal',
                this.boundListeners.technicalFileLoaded);
        }

        // 取消 GlobalState 订阅
        if (this.unsubscribers && this.unsubscribers.length > 0) {
            this.unsubscribers.forEach(unsubscribe => {
                try {
                    unsubscribe();
                } catch (error) {
                    this.warn('取消订阅时出错:', error);
                }
            });
            this.unsubscribers = [];
        }

        this.log('ProposalGenerator 已销毁，所有资源已清理');
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

// ========================================
// 全局调试开关（可在浏览器控制台使用）
// ========================================
window.enableProposalGeneratorDebug = () => {
    ProposalGenerator.DEBUG = true;
    console.log('✅ ProposalGenerator 调试模式已启用');
    console.log('💡 使用 window.disableProposalGeneratorDebug() 关闭调试');
};

window.disableProposalGeneratorDebug = () => {
    ProposalGenerator.DEBUG = false;
    console.log('❌ ProposalGenerator 调试模式已禁用');
};