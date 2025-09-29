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

        this.init();
    }

    /**
     * 初始化处理器 - 重构版本
     */
    init() {
        // 绑定新的UI元素
        this.bindElements();
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
        this.qualificationDisplay = document.getElementById('qualificationDisplay');
        this.scoringDisplay = document.getElementById('scoringDisplay');

        // 操作按钮
        this.exportResultsBtn = document.getElementById('exportResultsBtn');
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
        if (this.exportResultsBtn) {
            this.exportResultsBtn.addEventListener('click', () => this.exportResults());
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
            // 保存文件路径
            this.uploadedFilePath = result.file_path;

            // 显示上传成功信息
            this.showFileUploadSuccess(result.filename);

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
    showFileUploadSuccess(filename) {
        if (this.uploadedFileName) {
            this.uploadedFileName.textContent = filename;
        }

        // 可以添加文件大小显示逻辑
        if (this.uploadedFileSize) {
            this.uploadedFileSize.textContent = '上传完成';
        }

        if (this.uploadedFileInfo) {
            this.uploadedFileInfo.classList.remove('d-none');
        }

        console.log('[TenderProcessor] 文件上传成功信息已显示');
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

            // 显示结果
            this.displayStepResult(stepType, result);

            console.log(`[TenderProcessor] 步骤 ${stepType} 处理完成`);
        } catch (error) {
            console.error(`[TenderProcessor] 步骤 ${stepType} 处理失败:`, error);
            this.showError(`${this.getStepDisplayName(stepType)}处理失败: ${error.message}`);
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

        for (const step of steps) {
            await this.processStep(step);

            // 如果中途失败，停止处理
            if (!this.isProcessing) {
                break;
            }

            // 小延迟，避免过于频繁的API调用
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        // 激活导出按钮
        if (this.exportResultsBtn) {
            this.exportResultsBtn.disabled = false;
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
     * 格式化资质要求信息
     */
    formatQualificationInfo(data) {
        if (!data || Object.keys(data).length === 0) {
            return '<div class="text-muted text-center">暂无资质要求信息</div>';
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
     * 导出结果
     */
    exportResults() {
        // TODO: 实现导出功能
        console.log('[TenderProcessor] 导出结果功能待实现');
        if (typeof showNotification === 'function') {
            showNotification('导出功能开发中', 'info');
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
         this.processScoringBtn, this.processAllBtn, this.exportResultsBtn].forEach(btn => {
            if (btn) {
                btn.disabled = true;
            }
        });
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