/**
 * 通用文件上传组件
 * 基于知识库资质上传UI设计，统一所有上传功能的界面和交互
 *
 * 设计架构：
 * 1. 前端UI统一：基于资质上传的成熟交互模式
 * 2. 后端存储分离：不同业务调用不同API端点
 * 3. 配置驱动：通过配置适配不同业务场景
 * 4. 渐进重构：先统一UI，再统一存储层
 *
 * 支持的业务场景：
 * - AI处理类：标书上传、商务应答、点对点应答、技术方案生成
 * - 存储管理类：资质文件、财务文档、产品文档、人员档案
 */

class UniversalUploader {
    constructor(config) {
        // 基础配置
        this.containerId = config.containerId;
        this.apiEndpoint = config.apiEndpoint;
        this.businessType = config.businessType;

        // 文件配置
        this.acceptedTypes = config.acceptedTypes || '.pdf,.doc,.docx';
        this.maxFileSize = config.maxFileSize || 50 * 1024 * 1024; // 50MB
        this.multiple = config.multiple || false;

        // UI配置
        this.uploadText = config.uploadText || '点击或拖拽文件到这里上传';
        this.supportText = config.supportText || '支持 PDF、Word 文档';
        this.autoUpload = config.autoUpload || false;
        this.compactMode = config.compactMode || false;
        this.theme = config.theme || 'primary';
        this.icon = config.icon || 'bi-cloud-upload';

        // 额外表单字段
        this.additionalFields = config.additionalFields || [];

        // 回调函数
        this.onSuccess = config.onSuccess || this.defaultOnSuccess.bind(this);
        this.onError = config.onError || this.defaultOnError.bind(this);
        this.onProgress = config.onProgress || this.defaultOnProgress.bind(this);
        this.customUpload = config.customUpload || null;

        // 内部状态
        this.isUploading = false;
        this.selectedFiles = [];

        this.init();
    }

    init() {
        this.createUploadUI();
        this.bindEvents();
        console.log(`[UniversalUploader] ${this.businessType} 上传组件初始化完成`);
    }

    createUploadUI() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`[UniversalUploader] 容器 ${this.containerId} 不存在`);
            return;
        }

        const containerClasses = ['universal-upload-container'];
        if (this.compactMode) {
            containerClasses.push('compact-mode');
            if (this.theme !== 'primary') containerClasses.push(`theme-${this.theme}`);
        }

        container.innerHTML = `
            <div class="${containerClasses.join(' ')}">
                <div class="upload-zone" id="${this.containerId}_uploadZone">
                    <div class="upload-zone-content">
                        <div class="upload-info">
                            <i class="bi ${this.icon} text-${this.theme} me-2"></i>
                            <span class="upload-text">${this.uploadText}</span>
                        </div>
                        <div class="upload-action">
                            <button type="button" class="btn btn-sm btn-outline-${this.theme} upload-trigger">
                                <i class="bi bi-upload"></i> ${this.compactMode ? '' : '上传'}
                            </button>
                        </div>
                    </div>
                    ${this.supportText ? `<div class="upload-support-text"><small class="text-muted">${this.supportText}</small></div>` : ''}
                    <input type="file" class="d-none" id="${this.containerId}_fileInput" accept="${this.acceptedTypes}" ${this.multiple ? 'multiple' : ''}>
                </div>
                ${this.compactMode ? `<div class="file-status d-none" id="${this.containerId}_fileStatus"><small class="text-muted">未上传文件</small></div>` :
                !this.autoUpload ? `<div class="mt-3 d-none" id="${this.containerId}_fileInfo"><div class="alert alert-info"><i class="bi bi-file-earmark-text"></i><span id="${this.containerId}_fileStatus">已选择文件：</span><span id="${this.containerId}_fileList"></span></div></div>` : ''}
                <div id="${this.containerId}_additionalFields">${this.renderAdditionalFields()}</div>
                <div id="${this.containerId}_progress" class="mt-3 d-none">
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%">
                            <span class="progress-text">准备上传...</span>
                        </div>
                    </div>
                </div>
                <div class="text-center mt-4" id="${this.containerId}_uploadBtnContainer" ${this.autoUpload ? 'style="display: none;"' : ''}>
                    <button type="button" class="btn btn-primary" id="${this.containerId}_uploadBtn" disabled>
                        <i class="bi bi-upload"></i> 开始上传
                    </button>
                </div>
                <div id="${this.containerId}_result" class="mt-3 d-none"></div>
                <div id="${this.containerId}_error" class="mt-3 d-none">
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle"></i>
                        <span id="${this.containerId}_errorMessage"></span>
                    </div>
                </div>
            </div>
        `;
    }

    renderAdditionalFields() {
        if (!this.additionalFields.length) return '';
        return this.additionalFields.map(field => {
            if (field.type === 'select') {
                return `<div class="mb-3"><label for="${field.id}" class="form-label">${field.label}</label><select class="form-select" id="${field.id}" name="${field.name}">${field.options.map(opt => `<option value="${opt.value}">${opt.text}</option>`).join('')}</select></div>`;
            }
            if (field.type === 'text') {
                return `<div class="mb-3"><label for="${field.id}" class="form-label">${field.label}</label><input type="text" class="form-control" id="${field.id}" name="${field.name}" placeholder="${field.placeholder || ''}"></div>`;
            }
            return '';
        }).join('');
    }

    bindEvents() {
        const uploadZone = this.getElement('uploadZone');
        const fileInput = this.getElement('fileInput');
        const uploadBtn = this.getElement('uploadBtn');
        const uploadTrigger = uploadZone?.querySelector('.upload-trigger');

        uploadTrigger?.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput?.click();
        });
        uploadZone?.addEventListener('click', () => fileInput?.click());
        fileInput?.addEventListener('change', (e) => this.handleFileSelect(e));
        uploadZone?.addEventListener('dragover', (e) => this.handleDrag(e, true));
        uploadZone?.addEventListener('dragleave', (e) => this.handleDrag(e, false));
        uploadZone?.addEventListener('drop', (e) => this.handleDrop(e));
        uploadBtn?.addEventListener('click', () => this.startUpload());
    }

    getElement(suffix) {
        return document.getElementById(`${this.containerId}_${suffix}`);
    }

    handleFileSelect(event) {
        this.updateSelectedFiles(Array.from(event.target.files));
    }

    handleDrag(event, isOver) {
        event.preventDefault();
        event.currentTarget.classList.toggle('dragover', isOver);
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        this.updateSelectedFiles(Array.from(event.dataTransfer.files));
    }

    updateSelectedFiles(files) {
        const validFiles = files.filter(file => this.validateFile(file));
        if (validFiles.length === 0) {
            this.toggleError(true, '请选择有效的文件');
            return;
        }

        this.selectedFiles = validFiles;
        this.displaySelectedFiles();
        this.enableUploadButton();

        if (this.autoUpload && validFiles.length > 0) {
            console.log(`[UniversalUploader] 自动上传已启用，开始上传文件`);
            setTimeout(() => this.startUpload(), 100);
        }
    }

    validateFile(file) {
        if (file.size > this.maxFileSize) {
            this.toggleError(true, `文件 ${file.name} 太大，最大支持 ${this.formatFileSize(this.maxFileSize)}`);
            return false;
        }

        const allowedTypes = this.acceptedTypes.split(',').map(type => type.trim());
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedTypes.includes(fileExtension)) {
            this.toggleError(true, `文件 ${file.name} 格式不支持，支持格式：${this.acceptedTypes}`);
            return false;
        }
        return true;
    }

    displaySelectedFiles() {
        if (this.autoUpload) return;

        if (this.compactMode) {
            const fileStatus = this.getElement('fileStatus');
            if (fileStatus) {
                const fileName = this.selectedFiles.length > 0 ? this.selectedFiles[0].name : '';
                fileStatus.innerHTML = fileName ?
                    `<small class="text-success">已选择: ${fileName}</small>` :
                    `<small class="text-muted">未上传文件</small>`;
                fileStatus.classList.remove('d-none');
            }
        } else {
            const fileInfo = this.getElement('fileInfo');
            const fileList = this.getElement('fileList');
            if (this.selectedFiles.length > 0) {
                const fileNames = this.selectedFiles.map(file =>
                    `<strong>${file.name}</strong> (${this.formatFileSize(file.size)})`
                ).join(', ');
                fileList.innerHTML = fileNames;
                fileInfo?.classList.remove('d-none');
            } else {
                fileInfo?.classList.add('d-none');
            }
        }
    }

    enableUploadButton() {
        const uploadBtn = this.getElement('uploadBtn');
        if (uploadBtn && this.selectedFiles.length > 0) {
            uploadBtn.disabled = false;
        }
    }

    async startUpload() {
        if (this.isUploading || this.selectedFiles.length === 0) return;

        this.isUploading = true;
        this.toggleProgress(true, 0, '正在上传...');
        this.toggleError(false);

        try {
            const formData = this.buildFormData();
            const result = this.customUpload ?
                await this.customUpload(this.selectedFiles, formData) :
                await this.uploadFiles(formData);

            this.onSuccess(result);
            this.reset();
        } catch (error) {
            console.error(`[UniversalUploader] ${this.businessType} 上传失败:`, error);
            this.onError(error);
        } finally {
            this.isUploading = false;
            this.toggleProgress(false);
        }
    }

    buildFormData() {
        const formData = new FormData();

        if (this.multiple) {
            this.selectedFiles.forEach(file => formData.append('files', file));
        } else {
            formData.append('file', this.selectedFiles[0]);
        }

        this.additionalFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (element) formData.append(field.name, element.value);
        });

        formData.append('business_type', this.businessType);
        return formData;
    }

    async uploadFiles(formData) {
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || '上传失败');
        }
        return data;
    }

    toggleProgress(show, percent = 0, text = '准备上传...') {
        const progress = this.getElement('progress');
        if (!progress) return;

        if (show) {
            progress.classList.remove('d-none');
            const progressBar = progress.querySelector('.progress-bar');
            const progressText = progress.querySelector('.progress-text');
            if (progressBar) progressBar.style.width = `${percent}%`;
            if (progressText) progressText.textContent = text;
            this.onProgress(percent, text);
        } else {
            progress.classList.add('d-none');
        }
    }

    toggleError(show, message = '') {
        const error = this.getElement('error');
        const errorMessage = this.getElement('errorMessage');

        if (show && message) {
            if (errorMessage) errorMessage.textContent = message;
            error?.classList.remove('d-none');
        } else {
            error?.classList.add('d-none');
        }
    }

    showResult(html) {
        const result = this.getElement('result');
        if (result) {
            result.innerHTML = html;
            result.classList.remove('d-none');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    reset() {
        this.selectedFiles = [];
        const fileInput = this.getElement('fileInput');
        const uploadBtn = this.getElement('uploadBtn');
        const fileInfo = this.getElement('fileInfo');
        const result = this.getElement('result');

        if (fileInput) fileInput.value = '';
        if (uploadBtn) uploadBtn.disabled = true;
        fileInfo?.classList.add('d-none');
        result?.classList.add('d-none');

        this.toggleError(false);
        this.toggleProgress(false);
    }

    defaultOnSuccess(result) {
        console.log(`[UniversalUploader] ${this.businessType} 上传成功:`, result);
        this.showResult(`<div class="alert alert-success">上传成功！</div>`);
    }

    defaultOnError(error) {
        console.error(`[UniversalUploader] ${this.businessType} 上传失败:`, error);
        this.toggleError(true, error.message || '上传失败，请重试');
    }

    defaultOnProgress(percent, text) {
        console.log(`[UniversalUploader] ${this.businessType} 上传进度: ${percent}% - ${text}`);
    }
}

window.UniversalUploader = UniversalUploader;
