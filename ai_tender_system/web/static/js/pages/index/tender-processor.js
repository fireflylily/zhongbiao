/**
 * 招标文件处理模块 - 分步骤处理重构版本
 * 负责招标文件上传和分步信息处理
 *
 * 重构说明：
 * 1. 分离上传和处理：先上传文件，再分步处理信息
 * 2. 参考资质上传模式：使用纯上传的UniversalUploader
 * 3. 用户可控制：选择处理哪些信息类型
 * 4. 清晰的步骤流程：上传 → 处理控制 → 结果展示
 *
 * 设计架构：
 * - 步骤1：文件上传 (UniversalUploader + /upload API)
 * - 步骤2：信息处理控制 (选择处理类型)
 * - 步骤3：分步API调用 (/extract-tender-info-step)
 * - 步骤4：结果分类展示 (基本信息/资质要求/评分信息)
 */

class TenderProcessor {
    constructor() {
        this.isProcessing = false;
        this.currentController = null;
        this.uploader = null;
        this.uploaderInitialized = false;
        this.uploadedFilePath = null; // 存储上传文件的路径

        // 新增：项目和公司选择状态
        this.selectedCompanyId = null;
        this.selectedProjectId = null;
        this.currentProjectId = null;  // 当前正在编辑的项目ID（用于创建/更新判断）

        // 上传文件名（用于保存项目）
        this.uploadedFileName = null;

        this.init();
    }

    /**
     * 初始化处理器 - 重构版本
     */
    init() {
        // 绑定新的UI元素
        this.bindElements();
        // 绑定选择器事件
        this.bindSelectorEvents();
        // 加载公司和项目列表
        this.loadCompanies();
        console.log('[TenderProcessor] 基础初始化完成，等待tab激活后初始化上传组件');
    }

    /**
     * 检查上传容器是否可见和可操作
     */
    isUploadContainerReady() {
        const container = document.getElementById('tenderUploadContainer');
        if (!container) {
            console.log('[TenderProcessor] 容器不存在');
            return false;
        }

        // 检查容器是否可见（不在隐藏的tab中）
        const isVisible = container.offsetParent !== null;
        if (!isVisible) {
            console.log('[TenderProcessor] 容器存在但不可见（可能在隐藏的tab中）');
            return false;
        }

        console.log('[TenderProcessor] 容器已就绪，可以初始化上传组件');
        return true;
    }

    /**
     * 带重试机制的初始化UniversalUploader
     */
    initializeUploaderWithRetry(retryCount = 0, maxRetries = 3) {
        if (!this.uploaderInitialized) {
            console.log(`[TenderProcessor] 尝试初始化上传组件 (第${retryCount + 1}次)`);

            if (this.isUploadContainerReady()) {
                this.setupUniversalUploader();
            } else if (retryCount < maxRetries) {
                console.log(`[TenderProcessor] 容器未就绪，${500}ms后重试`);
                setTimeout(() => {
                    this.initializeUploaderWithRetry(retryCount + 1, maxRetries);
                }, 500);
            } else {
                console.error('[TenderProcessor] 已达到最大重试次数，上传组件初始化失败');
            }
        } else {
            console.log('[TenderProcessor] 上传组件已初始化');
        }
    }

    /**
     * 设置通用上传组件 - 重构为纯上传模式
     */
    setupUniversalUploader() {
        // 检查是否已经初始化
        if (this.uploaderInitialized && this.uploader) {
            console.log('[TenderProcessor] UniversalUploader已经初始化，跳过重复初始化');
            return;
        }

        // 检查容器是否就绪
        if (!this.isUploadContainerReady()) {
            console.log('[TenderProcessor] 容器未就绪，延迟初始化UniversalUploader');
            return;
        }

        console.log('[TenderProcessor] 开始初始化UniversalUploader（纯上传模式）...');

        // 配置为紧凑模式上传，使用通用的upload端点
        this.uploader = new UniversalUploader({
            containerId: 'tenderUploadContainer',
            apiEndpoint: '/upload', // 使用通用上传端点
            businessType: 'tender_document',
            acceptedTypes: '.docx,.doc,.txt,.pdf',
            uploadText: '招标文档上传',
            supportText: '支持Word、PDF、TXT格式',
            maxFileSize: 50 * 1024 * 1024, // 50MB
            autoUpload: true, // 启用自动上传 - 选择文件后立即上传
            compactMode: true, // 启用紧凑模式
            theme: 'primary', // 使用主要颜色主题
            icon: 'bi-cloud-upload', // 云上传图标
            onSuccess: (result) => this.handleFileUploadSuccess(result),
            onError: (error) => this.handleFileUploadError(error),
            onProgress: (percent, text) => this.handleProgress(percent, text)
        });

        // 重写buildFormData方法以添加文件类型参数
        const originalBuildFormData = this.uploader.buildFormData.bind(this.uploader);
        this.uploader.buildFormData = () => {
            const formData = originalBuildFormData();

            // 添加文件类型标识
            formData.append('type', 'tender_info');

            return formData;
        };

        // 标记为已初始化
        this.uploaderInitialized = true;
        console.log('[TenderProcessor] UniversalUploader初始化完成（纯上传模式）');
    }

    /**
     * 绑定DOM元素 - 重构版本
     */
    bindElements() {
        // 文件上传信息显示
        this.uploadedFileInfo = document.getElementById('uploadedFileInfo');
        this.uploadedFileName = document.getElementById('uploadedFileName');
        this.uploadedFileSize = document.getElementById('uploadedFileSize');

        // 处理控制区域
        this.processingControlArea = document.getElementById('processingControlArea');
        this.processBasicInfoBtn = document.getElementById('processBasicInfoBtn');
        this.processQualificationBtn = document.getElementById('processQualificationBtn');
        this.processScoringBtn = document.getElementById('processScoringBtn');
        this.processAllBtn = document.getElementById('processAllBtn');

        // 进度显示
        this.processingProgress = document.getElementById('processingProgress');
        this.processingProgressBar = document.getElementById('processingProgressBar');
        this.processingProgressText = document.getElementById('processingProgressText');

        // 结果展示区域
        this.resultsDisplayArea = document.getElementById('resultsDisplayArea');
        this.basicInfoDisplay = document.getElementById('basicInfoDisplay');
        this.basicInfoFooter = document.getElementById('basicInfoFooter');
        this.qualificationDisplay = document.getElementById('qualificationDisplay');
        this.scoringDisplay = document.getElementById('scoringDisplay');

        // 操作按钮
        this.saveProjectBtn = document.getElementById('saveProjectBtn');
        this.saveBasicInfoBtn = document.getElementById('saveBasicInfoBtn');
        this.resetAllBtn = document.getElementById('resetAllBtn');

        // 错误显示区域（保留原有的）
        this.errorArea = document.getElementById('tenderErrorArea');

        // 绑定事件
        this.bindEvents();

        console.log('[TenderProcessor] DOM元素绑定完成');
    }

    /**
     * 绑定事件 - 重构版本
     */
    bindEvents() {
        // 处理按钮事件
        if (this.processBasicInfoBtn) {
            this.processBasicInfoBtn.addEventListener('click', () => this.processStep('basic'));
        }
        if (this.processQualificationBtn) {
            this.processQualificationBtn.addEventListener('click', () => this.processStep('qualification'));
        }
        if (this.processScoringBtn) {
            this.processScoringBtn.addEventListener('click', () => this.processStep('scoring'));
        }
        if (this.processAllBtn) {
            this.processAllBtn.addEventListener('click', () => this.processAllSteps());
        }

        // 操作按钮事件
        if (this.saveProjectBtn) {
            this.saveProjectBtn.addEventListener('click', () => this.saveProject());
        }
        if (this.saveBasicInfoBtn) {
            this.saveBasicInfoBtn.addEventListener('click', () => this.saveBasicInfo());
        }
        if (this.resetAllBtn) {
            this.resetAllBtn.addEventListener('click', () => this.resetAll());
        }

        console.log('[TenderProcessor] 事件绑定完成');
    }

    /**
     * 处理文件上传成功 - 新方法
     */
    handleFileUploadSuccess(result) {
        console.log('[TenderProcessor] 文件上传成功:', result);

        if (result && result.success) {
            // 保存文件路径和文件名（包括原始文件名）
            this.uploadedFilePath = result.file_path;
            this.uploadedFileName = result.filename;  // 安全文件名（用于后端处理）
            this.originalFileName = result.original_filename || result.filename;  // 原始文件名（用于显示）
            this.fileSizeMB = result.file_size_mb;

            // 显示上传成功信息（使用原始文件名）
            this.showFileUploadSuccess(result);

            // 激活处理控制区域
            this.activateProcessingControls();

            // 显示结果展示区域
            this.showResultsArea();

        } else {
            this.showError('文件上传失败：' + (result.message || '未知错误'));
        }
    }

    /**
     * 处理文件上传错误 - 重构版本
     */
    handleFileUploadError(error) {
        console.error('[TenderProcessor] 文件上传失败:', error);
        this.showError('文件上传失败：' + (error.message || error));
    }

    /**
     * 显示文件上传成功信息
     */
    showFileUploadSuccess(result) {
        // 显示原始文件名
        const fileNameElement = document.getElementById('uploadedFileName');
        if (fileNameElement) {
            fileNameElement.textContent = result.original_filename || result.filename;
            // 添加title属性，鼠标悬停时显示完整信息
            fileNameElement.title = `原始文件名: ${result.original_filename}\n服务器文件名: ${result.filename}`;
        }

        // 显示文件大小
        const fileSizeElement = document.getElementById('uploadedFileSize');
        if (fileSizeElement) {
            if (result.file_size_mb) {
                fileSizeElement.textContent = `${result.file_size_mb} MB`;
            } else {
                fileSizeElement.textContent = '上传完成';
            }
        }

        // 显示上传信息区域
        if (this.uploadedFileInfo) {
            this.uploadedFileInfo.classList.remove('d-none');
        }

        // 绑定预览按钮事件（使用安全文件名）
        const previewBtn = document.getElementById('previewTenderBtn');
        if (previewBtn) {
            previewBtn.onclick = () => this.previewTenderDocument(result.filename);
        }

        console.log('[TenderProcessor] 文件上传成功信息已显示:', result.original_filename);
    }

    /**
     * 激活处理控制区域
     */
    activateProcessingControls() {
        if (this.processingControlArea) {
            this.processingControlArea.classList.remove('d-none');
        }

        // 激活所有处理按钮
        [this.processBasicInfoBtn, this.processQualificationBtn,
         this.processScoringBtn, this.processAllBtn].forEach(btn => {
            if (btn) {
                btn.disabled = false;
            }
        });

        console.log('[TenderProcessor] 处理控制区域已激活');
    }

    /**
     * 显示结果展示区域
     */
    showResultsArea() {
        if (this.resultsDisplayArea) {
            this.resultsDisplayArea.classList.remove('d-none');
        }

        console.log('[TenderProcessor] 结果展示区域已显示');
    }

    /**
     * 处理进度更新
     */
    handleProgress(percent, text) {
        console.log(`[TenderProcessor] 进度: ${percent}% - ${text}`);
        // 可以在这里更新自定义的进度显示
    }

    /**
     * 处理单个步骤 - 核心方法
     */
    async processStep(stepType) {
        if (this.isProcessing || !this.uploadedFilePath) {
            return;
        }

        this.isProcessing = true;
        console.log(`[TenderProcessor] 开始处理步骤: ${stepType}`);

        // 显示进度
        this.showProcessingProgress(stepType);

        try {
            // 调用分步处理API
            const result = await this.callStepAPI(stepType);

            // 保存结果到 latestResults
            if (!this.latestResults) {
                this.latestResults = {};
            }
            this.latestResults[stepType] = result.data;

            // 显示结果
            this.displayStepResult(stepType, result);

            // 如果处理了基本信息,显示并激活保存基本信息按钮
            if (stepType === 'basic' && result.data && result.data.project_name) {
                if (this.basicInfoFooter) {
                    this.basicInfoFooter.classList.remove('d-none');
                }
                if (this.saveBasicInfoBtn) {
                    this.saveBasicInfoBtn.disabled = false;
                }
                if (this.saveProjectBtn) {
                    this.saveProjectBtn.disabled = false;
                }
            }

            console.log(`[TenderProcessor] 步骤 ${stepType} 处理完成`);
        } catch (error) {
            console.error(`[TenderProcessor] 步骤 ${stepType} 处理失败:`, error);
            this.showError(`${this.getStepDisplayName(stepType)}处理失败: ${error.message}`);
            // 重新抛出错误，以便 processAllSteps 可以捕获
            throw error;
        } finally {
            this.isProcessing = false;
            this.hideProcessingProgress();
        }
    }

    /**
     * 处理所有步骤
     */
    async processAllSteps() {
        const steps = ['basic', 'qualification', 'scoring'];
        let hasError = false;

        for (const step of steps) {
            try {
                await this.processStep(step);

                // 小延迟，避免过于频繁的API调用
                await new Promise(resolve => setTimeout(resolve, 500));
            } catch (error) {
                console.error(`[TenderProcessor] 步骤 ${step} 处理失败，停止后续处理:`, error);
                hasError = true;
                break;
            }
        }

        // 只有全部成功才激活保存按钮
        if (!hasError && this.saveProjectBtn) {
            this.saveProjectBtn.disabled = false;
        }

        console.log('[TenderProcessor] 全部步骤处理完成');
    }

    /**
     * 调用分步处理API
     */
    async callStepAPI(stepType) {
        const stepMap = {
            'basic': '1',
            'qualification': '2',
            'scoring': '3'
        };

        const formData = new FormData();
        formData.append('step', stepMap[stepType]);
        formData.append('file_path', this.uploadedFilePath);

        // 添加公司ID
        if (this.selectedCompanyId) {
            formData.append('company_id', this.selectedCompanyId);
            console.log(`[TenderProcessor] 传递公司ID: ${this.selectedCompanyId}`);
        }

        // 添加项目ID
        if (this.selectedProjectId) {
            formData.append('project_id', this.selectedProjectId);
            console.log(`[TenderProcessor] 传递项目ID: ${this.selectedProjectId}`);
        }

        // 获取选择的AI模型
        const selectedModel = this.getSelectedAIModel();
        if (selectedModel) {
            formData.append('ai_model', selectedModel);
        }

        const response = await fetch('/extract-tender-info-step', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || '处理失败');
        }

        return data;
    }

    /**
     * 显示处理进度
     */
    showProcessingProgress(stepType) {
        if (this.processingProgress) {
            this.processingProgress.classList.remove('d-none');
        }

        const stepName = this.getStepDisplayName(stepType);
        this.updateProcessingProgress(0, `正在处理${stepName}...`);
    }

    /**
     * 隐藏处理进度
     */
    hideProcessingProgress() {
        if (this.processingProgress) {
            this.processingProgress.classList.add('d-none');
        }
    }

    /**
     * 更新处理进度
     */
    updateProcessingProgress(percent, text) {
        if (this.processingProgressBar) {
            this.processingProgressBar.style.width = `${percent}%`;
        }

        if (this.processingProgressText) {
            this.processingProgressText.textContent = text;
        }
    }

    /**
     * 获取步骤显示名称
     */
    getStepDisplayName(stepType) {
        const names = {
            'basic': '基本信息',
            'qualification': '资质要求',
            'scoring': '评分信息'
        };
        return names[stepType] || stepType;
    }

    /**
     * 显示步骤结果
     */
    displayStepResult(stepType, result) {
        const displayElement = this.getDisplayElement(stepType);
        if (!displayElement) return;

        const data = result.data || {};
        let html = '';

        switch (stepType) {
            case 'basic':
                html = this.formatBasicInfo(data);
                break;
            case 'qualification':
                html = this.formatQualificationInfo(data);
                break;
            case 'scoring':
                html = this.formatScoringInfo(data);
                break;
        }

        displayElement.innerHTML = html;
        console.log(`[TenderProcessor] 步骤 ${stepType} 结果已显示`);
    }

    /**
     * 获取显示元素
     */
    getDisplayElement(stepType) {
        const elements = {
            'basic': this.basicInfoDisplay,
            'qualification': this.qualificationDisplay,
            'scoring': this.scoringDisplay
        };
        return elements[stepType];
    }

    /**
     * 获取选择的AI模型
     */
    getSelectedAIModel() {
        const tenderAiModelSelect = document.getElementById('tenderAiModel');
        if (tenderAiModelSelect && tenderAiModelSelect.value) {
            return tenderAiModelSelect.value;
        }

        // 如果没有找到招标模型选择器，则使用默认的模型选择器
        const aiModelSelect = document.getElementById('aiModel');
        if (aiModelSelect && aiModelSelect.value) {
            return aiModelSelect.value;
        }

        // 默认模型
        return 'shihuang-gpt4o-mini';
    }

    /**
     * 显示成功结果
     */
    showSuccess(data) {
        console.log('[TenderProcessor] 显示提取结果', data);

        // 显示提取结果
        if (this.tenderInfoDisplay && data.tender_info) {
            this.displayTenderInfo(data.tender_info);
        }

        // 显示拆分文档
        if (data.split_documents && data.split_documents.length > 0) {
            this.displaySplitDocuments(data.split_documents);
        }

        if (this.resultArea) {
            this.resultArea.classList.remove('d-none');
        }

        // 隐藏错误区域
        this.hideError();

        if (typeof showNotification === 'function') {
            showNotification('招标信息提取完成', 'success');
        }
    }

    /**
     * 显示招标信息
     */
    displayTenderInfo(tenderInfo) {
        let html = '<div class="row">';

        Object.keys(tenderInfo).forEach(key => {
            const value = tenderInfo[key] || '未提取到';
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${this.getFieldDisplayName(key)}</h6>
                            <p class="card-text">${value}</p>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        this.tenderInfoDisplay.innerHTML = html;
    }

    /**
     * 获取字段显示名称
     */
    getFieldDisplayName(fieldKey) {
        const fieldNames = {
            'tender_party': '招标人',
            'tender_agent': '招标代理',
            'tender_method': '投标方式',
            'tender_location': '投标地点',
            'tender_deadline': '投标时间',
            'winner_count': '中标人数量',
            'project_name': '项目名称',
            'project_number': '项目编号'
        };
        return fieldNames[fieldKey] || fieldKey;
    }

    /**
     * 显示拆分文档
     */
    displaySplitDocuments(splitDocuments) {
        let html = '';

        splitDocuments.forEach((doc, index) => {
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i class="bi bi-file-earmark-text"></i> ${doc.name || `文档 ${index + 1}`}
                            </h6>
                            <p class="card-text small text-muted">
                                页数: ${doc.pages || 'N/A'} | 大小: ${doc.size || 'N/A'}
                            </p>
                            <a href="${doc.download_url}" class="btn btn-outline-primary btn-sm" download="${doc.filename}">
                                <i class="bi bi-download"></i> 下载
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });

        this.splitDocumentsList.innerHTML = html;
        if (this.splitDocumentsArea) {
            this.splitDocumentsArea.classList.remove('d-none');
        }
    }

    /**
     * 显示错误信息
     */
    showError(errorMessage) {
        console.log('[TenderProcessor] 显示错误信息', errorMessage);

        const errorMessageElement = document.getElementById('tenderErrorMessage');
        if (errorMessageElement) {
            errorMessageElement.textContent = errorMessage;
        }

        if (this.errorArea) {
            this.errorArea.classList.remove('d-none');
        }

        // 隐藏结果区域
        if (this.resultArea) {
            this.resultArea.classList.add('d-none');
        }

        if (typeof showNotification === 'function') {
            showNotification('招标信息提取失败', 'error');
        }
    }

    /**
     * 隐藏错误信息
     */
    hideError() {
        if (this.errorArea) {
            this.errorArea.classList.add('d-none');
        }
    }

    /**
     * 隐藏结果区域
     */
    hideResults() {
        if (this.resultArea) {
            this.resultArea.classList.add('d-none');
        }
        if (this.errorArea) {
            this.errorArea.classList.add('d-none');
        }
        if (this.splitDocumentsArea) {
            this.splitDocumentsArea.classList.add('d-none');
        }
        this.hideStepMessage();
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
     * 格式化基本信息
     */
    formatBasicInfo(data) {
        const fields = {
            'tender_party': '招标人',
            'tender_agent': '招标代理',
            'tender_method': '投标方式',
            'tender_location': '投标地点',
            'tender_deadline': '投标时间',
            'winner_count': '中标人数量',
            'project_name': '项目名称',
            'project_number': '项目编号'
        };

        let html = '<div class="row">';
        Object.keys(fields).forEach(key => {
            const value = data[key] || '未提取到';
            html += `
                <div class="col-12 mb-2">
                    <strong>${fields[key]}:</strong><br>
                    <span class="text-muted">${value}</span>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    /**
     * 格式化资质要求信息 - 表格对比显示
     */
    formatQualificationInfo(data, companyId = null) {
        if (!data || !data.qualifications || Object.keys(data.qualifications).length === 0) {
            return '<div class="text-muted text-center">暂无资质要求信息</div>';
        }

        // 使用传入的companyId，如果没有则使用selectedCompanyId
        const currentCompanyId = companyId || this.selectedCompanyId;

        const summary = data.summary || {};
        const qualifications = data.qualifications || {};

        // 生成汇总信息 - 使用共享CSS类
        let html = `
            <div class="qualification-summary">
                <div class="qualification-stat-card stat-total">
                    <h6>资质要求总数</h6>
                    <h4>${summary.required_count || 0}</h4>
                </div>
                <div class="qualification-stat-card stat-uploaded">
                    <h6>已上传数量</h6>
                    <h4>${summary.uploaded_count || 0}</h4>
                </div>
                <div class="qualification-stat-card stat-missing">
                    <h6>缺失数量</h6>
                    <h4>${summary.missing_count || 0}</h4>
                </div>
                <div class="qualification-stat-card stat-match ${summary.uploaded_count === summary.required_count ? 'stat-complete' : ''}">
                    <h6>资质匹配度</h6>
                    <h4>${summary.required_count > 0 ? Math.round((summary.uploaded_count / summary.required_count) * 100) : 0}%</h4>
                </div>
            </div>
        `;

        // 生成资质对比表格 - 卡片式设计（两列布局）
        html += `<div class="mt-3"><div class="row g-3">`;

        // 先显示要求的资质
        const requiredQuals = [];
        const optionalQuals = [];

        // 过时证件列表（三证合一后已废弃）
        const obsoleteQualifications = ['bank_permit', 'tax_registration', 'organization_code'];

        Object.keys(qualifications).forEach(key => {
            // 跳过过时的证件
            if (obsoleteQualifications.includes(key)) {
                return;
            }

            const qual = qualifications[key];
            if (qual.tender_requirement.required) {
                requiredQuals.push({key, ...qual});
            } else {
                // 显示所有可选资质（无论是否已上传）
                optionalQuals.push({key, ...qual});
            }
        });

        // 显示必需的资质 - 使用Bootstrap标准类（两列布局）
        requiredQuals.forEach(qual => {
            const isUploaded = qual.company_status.uploaded;
            const context = qual.tender_requirement.context || '';
            const keywords = qual.tender_requirement.keywords_found || [];

            const statusIcon = '<i class="bi bi-check-circle-fill text-primary"></i>';

            html += `
                <div class="col-md-6">
                    <div class="card mb-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-auto">
                                ${statusIcon}
                            </div>
                            <div class="col">
                                <div class="mb-1">
                                    <span class="fw-medium">${qual.qualification_name}</span>
                                </div>
                                ${context ? `
                                    <div class="mt-2 p-2 bg-light border-start border-3 border-info rounded">
                                        <small class="text-muted fst-italic"><i class="bi bi-quote"></i> ${context.substring(0, 120)}${context.length > 120 ? '...' : ''}</small>
                                    </div>
                                ` : ''}
                            </div>
                            <div class="col-auto text-end" style="min-width: 200px;">
                                <div class="d-flex gap-2 justify-content-end mb-2">
                                    <span class="badge bg-warning text-dark">必需</span>
                                    ${isUploaded ? `
                                        <span class="badge bg-success text-white">✓ 已上传</span>
                                    ` : `
                                        <span class="badge bg-secondary text-white">✗ 未上传</span>
                                    `}
                                </div>
                                ${isUploaded ? `
                                    <div class="mt-1">
                                        <small class="text-muted">
                                            <i class="bi bi-file-earmark"></i> ${qual.company_status.original_filename || '未知文件'}
                                        </small>
                                        ${qual.company_status.upload_time ?
                                            `<br><small class="text-muted"><i class="bi bi-clock"></i> ${new Date(qual.company_status.upload_time).toLocaleDateString('zh-CN')}</small>`
                                            : ''}
                                        <br>
                                        <button class="btn btn-sm btn-outline-primary mt-1"
                                                onclick="window.tenderProcessor.previewQualificationFile('${currentCompanyId}', '${qual.key}', '${qual.company_status.original_filename || ''}')">
                                            <i class="bi bi-eye"></i> 预览
                                        </button>
                                    </div>
                                ` : `
                                    <div class="mt-1">
                                        <small class="text-muted">需补充此资质</small>
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>
                    </div>
                </div>
            `;
        });

        // 关闭必需资质的row，准备显示可选资质
        html += `</div>`;

        // 显示已上传但非必需的资质 - 使用Bootstrap标准类（两列布局）
        if (optionalQuals.length > 0) {
            html += `
                <div class="d-flex align-items-center gap-2 mt-4 mb-3 pb-2 border-bottom">
                    <i class="bi bi-plus-circle text-info"></i>
                    <h6 class="mb-0">额外资质 <small class="text-muted">(非必需但已上传，可提升竞争力)</small></h6>
                </div>
                <div class="row g-3">
            `;

            optionalQuals.forEach(qual => {
                html += `
                    <div class="col-md-6">
                        <div class="card mb-0 shadow-sm h-100">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-auto">
                                    <i class="bi bi-check-circle text-primary"></i>
                                </div>
                                <div class="col">
                                    <div class="mb-1">
                                        <span class="fw-medium">${qual.qualification_name}</span>
                                    </div>
                                </div>
                                <div class="col-auto text-end" style="min-width: 200px;">
                                    <div class="d-flex gap-2 justify-content-end mb-2">
                                        <span class="badge bg-light text-dark border">可选</span>
                                        ${qual.company_status.uploaded ? `
                                            <span class="badge bg-success text-white">✓ 已上传</span>
                                        ` : `
                                            <span class="badge bg-secondary text-white">✗ 未上传</span>
                                        `}
                                    </div>
                                    ${qual.company_status.uploaded ? `
                                        <div class="mt-1">
                                            <small class="text-muted">
                                                <i class="bi bi-file-earmark"></i> ${qual.company_status.original_filename || '未知文件'}
                                            </small>
                                            ${qual.company_status.upload_time ?
                                                `<br><small class="text-muted"><i class="bi bi-clock"></i> ${new Date(qual.company_status.upload_time).toLocaleDateString('zh-CN')}</small>`
                                                : ''}
                                            <br>
                                            <button class="btn btn-sm btn-outline-primary mt-1"
                                                    onclick="window.tenderProcessor.previewQualificationFile('${currentCompanyId}', '${qual.key}', '${qual.company_status.original_filename || ''}')">
                                                <i class="bi bi-eye"></i> 预览
                                            </button>
                                        </div>
                                    ` : `
                                        <div class="mt-1">
                                            <small class="text-muted">可提升竞争力</small>
                                        </div>
                                    `}
                                </div>
                            </div>
                        </div>
                        </div>
                    </div>
                `;
            });

            html += `</div>`;  // 关闭可选资质的row
        }

        html += `</div>`;

        // 添加说明卡片
        html += `
            <div class="card mt-4 bg-light border-0">
                <div class="card-body p-3">
                    <h6 class="mb-3"><i class="bi bi-info-circle text-primary"></i> 资质状态说明</h6>
                    <div class="d-flex flex-wrap gap-3 align-items-center">
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-warning text-dark">必需</span>
                            <small class="text-muted">招标文件明确要求</small>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-success text-white">✓ 已上传</span>
                            <small class="text-muted">资质已准备</small>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-secondary text-white">✗ 未上传</span>
                            <small class="text-muted">需补充资质</small>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-light text-dark border">可选</span>
                            <small class="text-muted">非必需的额外资质</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    /**
     * 格式化评分信息
     */
    formatScoringInfo(data) {
        if (!data || Object.keys(data).length === 0) {
            return '<div class="text-muted text-center">暂无评分信息</div>';
        }

        let html = '<div>';
        Object.keys(data).forEach(key => {
            const value = data[key];
            html += `
                <div class="mb-2">
                    <strong>${key}:</strong><br>
                    <span class="text-muted">${value || '未提取到'}</span>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    /**
     * 保存基本信息（统一保存逻辑）
     */
    async saveBasicInfo() {
        try {
            // 检查是否已提取基本信息
            if (!this.latestResults || !this.latestResults.basic) {
                if (typeof showNotification === 'function') {
                    showNotification('请先提取基本信息', 'warning');
                }
                return;
            }

            // 检查是否选择了公司
            if (!this.selectedCompanyId) {
                if (typeof showNotification === 'function') {
                    showNotification('请先选择应答公司', 'warning');
                }
                return;
            }

            // 禁用按钮，防止重复点击
            if (this.saveBasicInfoBtn) {
                this.saveBasicInfoBtn.disabled = true;
                this.saveBasicInfoBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 保存中...';
            }

            // 准备完整项目数据（基本+资质+评分）
            const projectData = {
                project_name: this.latestResults.basic.project_name || '',
                project_number: this.latestResults.basic.project_number || '',
                tenderer: this.latestResults.basic.tender_party || '',
                agency: this.latestResults.basic.tender_agent || '',
                bidding_method: this.latestResults.basic.tender_method || '',
                bidding_location: this.latestResults.basic.tender_location || '',
                bidding_time: this.latestResults.basic.tender_deadline || '',
                tender_document_path: this.uploadedFilePath || '',
                original_filename: this.uploadedFileName || '',
                company_id: this.selectedCompanyId,
                // 添加资质和评分数据（如果已处理）
                qualifications_data: this.latestResults.qualification || null,
                scoring_data: this.latestResults.scoring || null
            };

            console.log('[TenderProcessor] 保存项目数据:', projectData);
            console.log('[TenderProcessor] 当前项目ID:', this.currentProjectId);

            // 判断是创建还是更新
            const isUpdate = this.currentProjectId !== null && this.currentProjectId !== '';
            const url = isUpdate
                ? `/api/tender-projects/${this.currentProjectId}`
                : '/api/tender-projects';
            const method = isUpdate ? 'PUT' : 'POST';

            console.log(`[TenderProcessor] 执行${isUpdate ? '更新' : '创建'}操作，URL: ${url}`);

            // 调用API保存项目
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });

            const data = await response.json();

            if (data.success) {
                // 保存/更新项目ID
                if (!isUpdate && data.project_id) {
                    this.currentProjectId = data.project_id;
                    console.log('[TenderProcessor] 新项目已创建，ID:', this.currentProjectId);
                }

                if (typeof showNotification === 'function') {
                    showNotification(isUpdate ? '项目更新成功' : '项目创建成功', 'success');
                }

                // 更新全局状态（顶部项目信息卡片）
                if (window.companyStateManager) {
                    window.companyStateManager.setProjectInfo({
                        project_id: this.currentProjectId,
                        project_name: projectData.project_name,
                        project_number: projectData.project_number
                    });
                }

                // 更新项目选择器并选中当前项目
                await this.loadProjects();
                const projectSelect = document.getElementById('tenderProjectSelect');
                if (projectSelect && this.currentProjectId) {
                    projectSelect.value = this.currentProjectId;
                }

                // 按钮改为已保存状态
                if (this.saveBasicInfoBtn) {
                    this.saveBasicInfoBtn.innerHTML = '<i class="bi bi-check-lg"></i> 已保存';
                    this.saveBasicInfoBtn.classList.remove('btn-primary');
                    this.saveBasicInfoBtn.classList.add('btn-success');
                }
            } else {
                throw new Error(data.message || '保存失败');
            }

        } catch (error) {
            console.error('[TenderProcessor] 保存失败:', error);
            if (typeof showNotification === 'function') {
                showNotification('保存失败: ' + error.message, 'error');
            }

            // 恢复按钮
            if (this.saveBasicInfoBtn) {
                this.saveBasicInfoBtn.disabled = false;
                this.saveBasicInfoBtn.innerHTML = '<i class="bi bi-save"></i> 保存基本信息';
            }
        }
    }

    /**
     * 保存项目（统一保存逻辑）
     */
    async saveProject() {
        try {
            // 检查是否已提取基本信息
            if (!this.latestResults || !this.latestResults.basic) {
                if (typeof showNotification === 'function') {
                    showNotification('请先提取基本信息', 'warning');
                }
                return;
            }

            // 检查是否选择了公司
            if (!this.selectedCompanyId) {
                if (typeof showNotification === 'function') {
                    showNotification('请先选择应答公司', 'warning');
                }
                return;
            }

            // 禁用按钮，防止重复点击
            if (this.saveProjectBtn) {
                this.saveProjectBtn.disabled = true;
                this.saveProjectBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 保存中...';
            }

            // 准备完整项目数据（基本+资质+评分）
            const projectData = {
                project_name: this.latestResults.basic.project_name || '',
                project_number: this.latestResults.basic.project_number || '',
                tenderer: this.latestResults.basic.tender_party || '',
                agency: this.latestResults.basic.tender_agent || '',
                bidding_method: this.latestResults.basic.tender_method || '',
                bidding_location: this.latestResults.basic.tender_location || '',
                bidding_time: this.latestResults.basic.tender_deadline || '',
                tender_document_path: this.uploadedFilePath || '',
                original_filename: this.uploadedFileName || '',
                company_id: this.selectedCompanyId,
                // 添加资质和评分数据（如果已处理）
                qualifications_data: this.latestResults.qualification || null,
                scoring_data: this.latestResults.scoring || null
            };

            console.log('[TenderProcessor] 保存项目数据:', projectData);
            console.log('[TenderProcessor] 当前项目ID:', this.currentProjectId);

            // 判断是创建还是更新
            const isUpdate = this.currentProjectId !== null && this.currentProjectId !== '';
            const url = isUpdate
                ? `/api/tender-projects/${this.currentProjectId}`
                : '/api/tender-projects';
            const method = isUpdate ? 'PUT' : 'POST';

            console.log(`[TenderProcessor] 执行${isUpdate ? '更新' : '创建'}操作，URL: ${url}`);

            // 调用API保存项目
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });

            const data = await response.json();

            if (data.success) {
                // 保存/更新项目ID
                if (!isUpdate && data.project_id) {
                    this.currentProjectId = data.project_id;
                    console.log('[TenderProcessor] 新项目已创建，ID:', this.currentProjectId);
                }

                if (typeof showNotification === 'function') {
                    showNotification(isUpdate ? '项目更新成功' : '项目创建成功', 'success');
                }

                // 更新全局状态（顶部项目信息卡片）
                if (window.companyStateManager) {
                    window.companyStateManager.setProjectInfo({
                        project_id: this.currentProjectId,
                        project_name: projectData.project_name,
                        project_number: projectData.project_number
                    });
                }

                // 更新项目选择器并选中当前项目
                await this.loadProjects();
                const projectSelect = document.getElementById('tenderProjectSelect');
                if (projectSelect && this.currentProjectId) {
                    projectSelect.value = this.currentProjectId;
                }

                // 按钮改为已保存状态
                if (this.saveProjectBtn) {
                    this.saveProjectBtn.innerHTML = '<i class="bi bi-check-lg"></i> 已保存';
                    this.saveProjectBtn.classList.remove('btn-primary');
                    this.saveProjectBtn.classList.add('btn-success');
                }
            } else {
                throw new Error(data.message || '保存失败');
            }

        } catch (error) {
            console.error('[TenderProcessor] 保存失败:', error);
            if (typeof showNotification === 'function') {
                showNotification('保存失败: ' + error.message, 'error');
            }

            // 恢复按钮
            if (this.saveProjectBtn) {
                this.saveProjectBtn.disabled = false;
                this.saveProjectBtn.innerHTML = '<i class="bi bi-save"></i> 保存项目';
            }
        }
    }

    /**
     * 重新开始
     */
    resetAll() {
        // 重置上传器
        if (this.uploader) {
            this.uploader.reset();
        }

        // 隐藏所有区域
        this.hideAll();

        // 重置状态
        this.uploadedFilePath = null;
        this.isProcessing = false;

        if (typeof showNotification === 'function') {
            showNotification('已重新开始', 'info');
        }

        console.log('[TenderProcessor] 已重新开始');
    }

    /**
     * 隐藏所有区域
     */
    hideAll() {
        // 隐藏文件信息
        if (this.uploadedFileInfo) {
            this.uploadedFileInfo.classList.add('d-none');
        }

        // 隐藏处理控制区域
        if (this.processingControlArea) {
            this.processingControlArea.classList.add('d-none');
        }

        // 隐藏结果区域
        if (this.resultsDisplayArea) {
            this.resultsDisplayArea.classList.add('d-none');
        }

        // 隐藏进度
        this.hideProcessingProgress();

        // 重置结果显示
        [this.basicInfoDisplay, this.qualificationDisplay, this.scoringDisplay].forEach(element => {
            if (element) {
                element.innerHTML = `
                    <div class="text-muted text-center">
                        <i class="bi bi-hourglass-split"></i><br>
                        等待处理...
                    </div>
                `;
            }
        });

        // 禁用按钮
        [this.processBasicInfoBtn, this.processQualificationBtn,
         this.processScoringBtn, this.processAllBtn, this.saveProjectBtn].forEach(btn => {
            if (btn) {
                btn.disabled = true;
            }
        });
    }

    /**
     * 加载公司列表
     */
    async loadCompanies() {
        const companySelect = document.getElementById('tenderCompanySelect');
        if (!companySelect) {
            console.log('[TenderProcessor] 公司选择器不存在');
            return;
        }

        try {
            console.log('[TenderProcessor] 开始加载公司列表...');
            const response = await fetch('/api/companies');
            const data = await response.json();

            companySelect.innerHTML = '<option value="">请选择公司...</option>';

            if (data.success && data.data && data.data.length > 0) {
                data.data.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.company_id;
                    option.textContent = company.company_name;
                    companySelect.appendChild(option);
                });

                console.log(`[TenderProcessor] 成功加载 ${data.data.length} 家公司`);

                // 恢复之前选择的公司
                if (window.companyStateManager) {
                    const savedCompany = window.companyStateManager.getSelectedCompany();
                    if (savedCompany && savedCompany.company_id) {
                        companySelect.value = savedCompany.company_id;
                        this.selectedCompanyId = savedCompany.company_id;
                        this.updateCompanyDisplay(savedCompany.company_name);
                        console.log('[TenderProcessor] 已恢复公司选择状态', savedCompany);
                        // 加载该公司的项目
                        this.loadProjects();
                    }
                }
            }
        } catch (error) {
            console.error('[TenderProcessor] 加载公司列表失败:', error);
            companySelect.innerHTML = '<option value="">加载失败，请刷新重试</option>';
        }
    }

    /**
     * 加载项目列表
     */
    async loadProjects() {
        const projectSelect = document.getElementById('tenderProjectSelect');
        if (!projectSelect) {
            console.log('[TenderProcessor] 项目选择器不存在');
            return;
        }

        try {
            console.log('[TenderProcessor] 开始加载项目列表...');
            const url = this.selectedCompanyId
                ? `/api/tender-projects?company_id=${this.selectedCompanyId}`
                : '/api/tender-projects';

            const response = await fetch(url);
            const data = await response.json();

            projectSelect.innerHTML = '<option value="">新建项目</option>';

            if (data.success && data.data && data.data.length > 0) {
                data.data.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.project_id;
                    const projectNumber = project.project_number || '无编号';
                    const status = project.status || 'draft';
                    option.textContent = `${project.project_name} (${projectNumber}) [${status}]`;
                    projectSelect.appendChild(option);
                });

                console.log(`[TenderProcessor] 成功加载 ${data.data.length} 个项目`);
            } else {
                console.log('[TenderProcessor] 没有找到项目数据');
            }
        } catch (error) {
            console.error('[TenderProcessor] 加载项目列表失败:', error);
        }
    }

    /**
     * 更新公司显示
     */
    updateCompanyDisplay(companyName) {
        const displayElement = document.getElementById('tenderSelectedCompanyName');
        if (displayElement) {
            displayElement.textContent = companyName || '未选择';
            displayElement.className = companyName ? 'text-primary fw-bold' : 'text-muted';
        }
    }

    /**
     * 预览招标文档
     */
    async previewTenderDocument(filename) {
        try {
            // 调用API获取文档内容
            const response = await fetch(`/api/document/preview/${encodeURIComponent(filename)}`);
            const data = await response.json();

            if (data.success) {
                // 创建预览窗口
                const previewWindow = window.open('', '_blank', 'width=1200,height=800');
                previewWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>文档预览 - ${filename}</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body { padding: 20px; }
                            .document-preview { max-width: 1000px; margin: 0 auto; }
                            .document-preview h1 { font-size: 1.8rem; margin-top: 20px; }
                            .document-preview h2 { font-size: 1.5rem; margin-top: 15px; }
                            .document-preview h3 { font-size: 1.2rem; margin-top: 10px; }
                            .document-preview p { margin: 10px 0; line-height: 1.6; }
                            .document-preview table { margin: 15px 0; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="mb-3">
                                <button class="btn btn-secondary btn-sm" onclick="window.close()">关闭</button>
                                <span class="ms-3 text-muted">文件名: ${filename}</span>
                            </div>
                            ${data.html_content}
                        </div>
                    </body>
                    </html>
                `);
                previewWindow.document.close();
            } else {
                throw new Error(data.error || '预览失败');
            }

            console.log('[TenderProcessor] 文档预览成功:', filename);
        } catch (error) {
            console.error('[TenderProcessor] 预览文档失败:', error);
            if (typeof showNotification === 'function') {
                showNotification('预览文档失败: ' + error.message, 'error');
            } else {
                alert('预览文档失败: ' + error.message);
            }
        }
    }

    /**
     * 预览资质文件（图片/PDF等）
     */
    async previewQualificationFile(companyId, qualKey, filename) {
        try {
            // 调用API获取资质文件预览内容
            const response = await fetch(`/api/companies/${companyId}/qualifications/${qualKey}/preview`);
            const data = await response.json();

            if (data.success) {
                // 创建预览窗口
                const previewWindow = window.open('', '_blank', 'width=1200,height=800');
                previewWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>资质预览 - ${data.filename || filename}</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
                        <style>
                            body { padding: 20px; background: #f8f9fa; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="mb-3">
                                <button class="btn btn-secondary btn-sm" onclick="window.close()">
                                    <i class="bi bi-x-circle"></i> 关闭
                                </button>
                                <span class="ms-3 text-muted">
                                    <i class="bi bi-file-earmark"></i> 文件名: ${data.filename || filename}
                                </span>
                            </div>
                            <hr>
                            ${data.content}
                        </div>
                    </body>
                    </html>
                `);
                previewWindow.document.close();
            } else {
                throw new Error(data.error || '预览失败');
            }

            console.log('[TenderProcessor] 资质预览成功:', filename);
        } catch (error) {
            console.error('[TenderProcessor] 预览资质失败:', error);
            if (typeof showNotification === 'function') {
                showNotification('预览资质失败: ' + error.message, 'error');
            } else {
                alert('预览资质失败: ' + error.message);
            }
        }
    }

    /**
     * 绑定选择器事件
     */
    bindSelectorEvents() {
        // 公司选择变更
        const companySelect = document.getElementById('tenderCompanySelect');
        if (companySelect) {
            companySelect.addEventListener('change', (e) => {
                this.selectedCompanyId = e.target.value || null;
                const selectedOption = e.target.options[e.target.selectedIndex];
                const companyName = e.target.value ? selectedOption.text : '';

                console.log('[TenderProcessor] 公司选择变更:', this.selectedCompanyId, companyName);
                this.updateCompanyDisplay(companyName);

                // 保存到全局状态
                if (this.selectedCompanyId && window.companyStateManager) {
                    window.companyStateManager.setSelectedCompany({
                        company_id: this.selectedCompanyId,
                        company_name: companyName
                    });
                    console.log('[TenderProcessor] 已保存公司选择到全局状态');
                }

                // 重新加载项目列表
                this.loadProjects();
            });
            console.log('[TenderProcessor] 公司选择器事件已绑定');
        }

        // 项目选择变更
        const projectSelect = document.getElementById('tenderProjectSelect');
        if (projectSelect) {
            projectSelect.addEventListener('change', (e) => {
                this.selectedProjectId = e.target.value || null;
                // 同步当前项目ID（用于判断创建/更新）
                this.currentProjectId = this.selectedProjectId;
                console.log('[TenderProcessor] 项目选择变更:', this.selectedProjectId);

                // 根据选择显示或隐藏项目详情
                if (this.selectedProjectId) {
                    // 选择了具体项目，加载并显示项目详情
                    this.loadAndDisplayProjectDetails(this.selectedProjectId);
                } else {
                    // 选择"新建项目"，隐藏项目详情
                    this.hideProjectDetailsInResultArea();
                }

                // 保存项目信息到全局状态
                if (this.selectedProjectId && window.companyStateManager) {
                    const selectedOption = projectSelect.options[projectSelect.selectedIndex];
                    const projectText = selectedOption.textContent;
                    // 解析项目名称（格式：项目名 (编号) [状态]）
                    const match = projectText.match(/^(.+?)\s*\((.+?)\)\s*\[.+?\]$/);
                    if (match) {
                        const projectInfo = {
                            project_name: match[1].trim(),
                            project_number: match[2].trim()
                        };
                        window.companyStateManager.setProjectInfo(projectInfo);
                        console.log('[TenderProcessor] 项目信息已保存到全局状态:', projectInfo);
                    }
                } else if (!this.selectedProjectId && window.companyStateManager) {
                    // 选择"新建项目"时清除项目信息
                    window.companyStateManager.setProjectInfo({
                        project_name: null,
                        project_number: null
                    });
                    console.log('[TenderProcessor] 已清除项目信息（新建项目）');
                }
            });
            console.log('[TenderProcessor] 项目选择器事件已绑定');
        }

        // 刷新项目按钮
        const refreshBtn = document.getElementById('refreshProjectsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                console.log('[TenderProcessor] 刷新项目列表');
                this.loadProjects();
            });
            console.log('[TenderProcessor] 刷新按钮事件已绑定');
        }
    }

    /**
     * 获取当前配置
     */
    getCurrentConfig() {
        return {
            action: 'extract_tender_info'
        };
    }

    /**
     * 设置配置
     */
    setConfig(config) {
        // 招标信息提取不需要特殊配置
        console.log('招标信息提取器配置设置:', config);
    }

    /**
     * 加载并显示项目详情
     */
    async loadAndDisplayProjectDetails(projectId) {
        try {
            console.log('[TenderProcessor] 开始加载项目详情:', projectId);

            // 调用API获取项目详情
            const response = await fetch(`/api/tender-projects/${projectId}`);
            const data = await response.json();

            if (data.success && data.data) {
                const project = data.data;

                // 格式化为显示所需的格式
                const formattedData = {
                    basic: {
                        project_name: project.project_name || '-',
                        project_number: project.project_number || '-',
                        tenderer: project.tenderer || '-',
                        agency: project.agency || '-',
                        bidding_method: project.bidding_method || '-',
                        bidding_location: project.bidding_location || '-',
                        bidding_time: project.bidding_time || '-',
                        status: project.status || 'draft'
                    }
                };

                // 解析资质数据（JSON格式）
                if (project.qualifications_data) {
                    try {
                        const qualData = typeof project.qualifications_data === 'string'
                            ? JSON.parse(project.qualifications_data)
                            : project.qualifications_data;
                        formattedData.qualification = qualData;
                        console.log('[TenderProcessor] 已解析资质数据:', qualData);
                    } catch (e) {
                        console.error('[TenderProcessor] 解析资质数据失败:', e);
                    }
                }

                // 解析评分数据（JSON格式）
                if (project.scoring_data) {
                    try {
                        const scoreData = typeof project.scoring_data === 'string'
                            ? JSON.parse(project.scoring_data)
                            : project.scoring_data;
                        formattedData.scoring = scoreData;
                        console.log('[TenderProcessor] 已解析评分数据:', scoreData);
                    } catch (e) {
                        console.error('[TenderProcessor] 解析评分数据失败:', e);
                    }
                }

                // 显示结果展示区域
                if (this.resultsDisplayArea) {
                    this.resultsDisplayArea.classList.remove('d-none');
                }

                // 在基本信息卡片中显示
                if (this.basicInfoDisplay) {
                    this.basicInfoDisplay.innerHTML = `
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">项目名称</label>
                                <div class="fw-bold">${formattedData.basic.project_name}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">项目编号</label>
                                <div class="fw-bold">${formattedData.basic.project_number}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">招标方</label>
                                <div>${formattedData.basic.tenderer}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">代理机构</label>
                                <div>${formattedData.basic.agency}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">招标方式</label>
                                <div>${formattedData.basic.bidding_method}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">招标地点</label>
                                <div>${formattedData.basic.bidding_location}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">招标时间</label>
                                <div>${formattedData.basic.bidding_time}</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="text-muted small">项目状态</label>
                                <div>
                                    <span class="badge bg-${formattedData.basic.status === 'completed' ? 'success' : formattedData.basic.status === 'active' ? 'primary' : 'secondary'}">
                                        ${formattedData.basic.status === 'completed' ? '已完成' : formattedData.basic.status === 'active' ? '进行中' : '草稿'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    `;
                }

                // 显示资质要求（如果有）
                if (formattedData.qualification && this.qualificationDisplay) {
                    // 传递项目的公司ID或当前选择的公司ID
                    this.qualificationDisplay.innerHTML = this.formatQualificationInfo(formattedData.qualification, project.company_id || this.selectedCompanyId);
                    this.qualificationDisplay.closest('.card').classList.remove('d-none');
                    console.log('[TenderProcessor] 已显示资质信息');
                } else if (this.qualificationDisplay) {
                    this.qualificationDisplay.innerHTML = '<div class="text-muted text-center py-3"><i class="bi bi-hourglass-split"></i><br>暂无资质数据</div>';
                    this.qualificationDisplay.closest('.card').classList.remove('d-none');
                }

                // 显示评分信息（如果有）
                if (formattedData.scoring && this.scoringDisplay) {
                    this.scoringDisplay.innerHTML = this.formatScoringInfo(formattedData.scoring);
                    this.scoringDisplay.closest('.card').classList.remove('d-none');
                    console.log('[TenderProcessor] 已显示评分信息');
                } else if (this.scoringDisplay) {
                    this.scoringDisplay.innerHTML = '<div class="text-muted text-center py-3"><i class="bi bi-hourglass-split"></i><br>暂无评分数据</div>';
                    this.scoringDisplay.closest('.card').classList.remove('d-none');
                }

                // 隐藏保存按钮（因为是已有项目，不需要保存）
                if (this.saveProjectBtn) {
                    this.saveProjectBtn.classList.add('d-none');
                }
                if (this.saveBasicInfoBtn) {
                    this.saveBasicInfoBtn.classList.add('d-none');
                }

                console.log('[TenderProcessor] 项目详情显示成功');
            } else {
                throw new Error(data.message || '获取项目详情失败');
            }
        } catch (error) {
            console.error('[TenderProcessor] 加载项目详情失败:', error);
            if (typeof showNotification === 'function') {
                showNotification('加载项目详情失败: ' + error.message, 'error');
            }
        }
    }

    /**
     * 隐藏项目详情（在结果展示区域）
     */
    hideProjectDetailsInResultArea() {
        // 隐藏结果展示区域
        if (this.resultsDisplayArea) {
            this.resultsDisplayArea.classList.add('d-none');
        }

        // 清空基本信息显示
        if (this.basicInfoDisplay) {
            this.basicInfoDisplay.innerHTML = `
                <div class="text-muted text-center">
                    <i class="bi bi-hourglass-split"></i><br>
                    等待处理...
                </div>
            `;
        }

        // 恢复资质要求和评分信息卡片的显示
        if (this.qualificationDisplay) {
            this.qualificationDisplay.closest('.card').classList.remove('d-none');
        }
        if (this.scoringDisplay) {
            this.scoringDisplay.closest('.card').classList.remove('d-none');
        }

        console.log('[TenderProcessor] 已隐藏项目详情');
    }

    /**
     * 销毁处理器
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

// 全局招标处理器实例变量
window.tenderProcessor = null;

// 监听选项卡切换事件，确保在切换到上传标书页面时初始化上传组件
document.addEventListener('DOMContentLoaded', function() {
    // 在DOM准备好后创建实例
    if (!window.tenderProcessor) {
        window.tenderProcessor = new TenderProcessor();
    }
    const tenderNavLink = document.getElementById('tender-info-nav');
    if (tenderNavLink) {
        tenderNavLink.addEventListener('click', function() {
            console.log('[TenderProcessor] 上传标书tab被点击');

            // 延迟确保tab切换动画完成，DOM已渲染
            setTimeout(() => {
                if (window.tenderProcessor) {
                    // 重新绑定元素（使用新方法名）
                    window.tenderProcessor.bindElements();

                    // 检查并初始化UniversalUploader（带重试机制）
                    window.tenderProcessor.initializeUploaderWithRetry();

                    console.log('[TenderProcessor] 上传标书页面激活完成');
                }
            }, 300); // 增加延迟时间确保tab完全切换
        });
    }
});

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TenderProcessor;
}