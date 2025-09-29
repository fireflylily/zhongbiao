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
        this.autoUpload = config.autoUpload || false; // 自动上传功能
        this.compactMode = config.compactMode || false; // 紧凑模式
        this.theme = config.theme || 'primary'; // 主题颜色: primary, warning, success, info
        this.icon = config.icon || 'bi-cloud-upload'; // 图标

        // 额外表单字段
        this.additionalFields = config.additionalFields || [];

        // 回调函数
        this.onSuccess = config.onSuccess || this.defaultOnSuccess;
        this.onError = config.onError || this.defaultOnError;
        this.onProgress = config.onProgress || this.defaultOnProgress;

        // 内部状态
        this.isUploading = false;
        this.selectedFiles = [];

        this.init();
    }

    /**
     * 初始化组件
     */
    init() {
        this.createUploadUI();
        this.bindEvents();
        console.log(`[UniversalUploader] ${this.businessType} 上传组件初始化完成`);
    }

    /**
     * 创建上传界面 - 基于资质上传UI设计
     */
    createUploadUI() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`[UniversalUploader] 容器 ${this.containerId} 不存在`);
            return;
        }

        // 根据模式和主题构建样式类
        const containerClasses = ['universal-upload-container'];
        if (this.compactMode) {
            containerClasses.push('compact-mode');
            if (this.theme !== 'primary') {
                containerClasses.push(`theme-${this.theme}`);
            }
        }

        container.innerHTML = `
            <!-- 卡片式上传UI设计 -->
            <div class="${containerClasses.join(' ')}">
                <!-- 文件上传区域 - 卡片式布局 -->
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
                    ${this.supportText ? `
                    <div class="upload-support-text">
                        <small class="text-muted">${this.supportText}</small>
                    </div>
                    ` : ''}
                    <input type="file"
                           class="d-none"
                           id="${this.containerId}_fileInput"
                           accept="${this.acceptedTypes}"
                           ${this.multiple ? 'multiple' : ''}>
                </div>

                <!-- 文件状态显示 -->
                ${this.compactMode ? `
                <div class="file-status d-none" id="${this.containerId}_fileStatus">
                    <small class="text-muted">未上传文件</small>
                </div>
                ` : !this.autoUpload ? `
                <div class="mt-3 d-none" id="${this.containerId}_fileInfo">
                    <div class="alert alert-info">
                        <i class="bi bi-file-earmark-text"></i>
                        <span id="${this.containerId}_fileStatus">已选择文件：</span><span id="${this.containerId}_fileList"></span>
                    </div>
                </div>
                ` : ''}

                <!-- 额外表单字段 -->
                <div id="${this.containerId}_additionalFields">
                    ${this.renderAdditionalFields()}
                </div>

                <!-- 上传进度 -->
                <div id="${this.containerId}_progress" class="mt-3 d-none">
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated"
                             role="progressbar" style="width: 0%">
                            <span class="progress-text">准备上传...</span>
                        </div>
                    </div>
                </div>

                <!-- 操作按钮 -->
                <div class="text-center mt-4" id="${this.containerId}_uploadBtnContainer" ${this.autoUpload ? 'style="display: none;"' : ''}>
                    <button type="button"
                            class="btn btn-primary"
                            id="${this.containerId}_uploadBtn"
                            disabled>
                        <i class="bi bi-upload"></i> 开始上传
                    </button>
                </div>

                <!-- 结果显示区域 -->
                <div id="${this.containerId}_result" class="mt-3 d-none"></div>

                <!-- 错误显示区域 -->
                <div id="${this.containerId}_error" class="mt-3 d-none">
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle"></i>
                        <span id="${this.containerId}_errorMessage"></span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染额外表单字段
     */
    renderAdditionalFields() {
        if (!this.additionalFields.length) return '';

        return this.additionalFields.map(field => {
            switch (field.type) {
                case 'select':
                    return `
                        <div class="mb-3">
                            <label for="${field.id}" class="form-label">${field.label}</label>
                            <select class="form-select" id="${field.id}" name="${field.name}">
                                ${field.options.map(opt =>
                                    `<option value="${opt.value}">${opt.text}</option>`
                                ).join('')}
                            </select>
                        </div>
                    `;
                case 'text':
                    return `
                        <div class="mb-3">
                            <label for="${field.id}" class="form-label">${field.label}</label>
                            <input type="text" class="form-control" id="${field.id}"
                                   name="${field.name}" placeholder="${field.placeholder || ''}">
                        </div>
                    `;
                default:
                    return '';
            }
        }).join('');
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        const uploadZone = document.getElementById(`${this.containerId}_uploadZone`);
        const fileInput = document.getElementById(`${this.containerId}_fileInput`);
        const uploadBtn = document.getElementById(`${this.containerId}_uploadBtn`);
        const uploadTrigger = uploadZone?.querySelector('.upload-trigger');

        // 上传按钮点击事件（卡片式布局的按钮）
        uploadTrigger?.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput?.click();
        });

        // 上传区域点击事件（整个区域也可以点击）
        uploadZone?.addEventListener('click', () => fileInput?.click());

        // 文件选择事件
        fileInput?.addEventListener('change', (e) => this.handleFileSelect(e));

        // 拖拽事件
        uploadZone?.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadZone?.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadZone?.addEventListener('drop', (e) => this.handleDrop(e));

        // 上传按钮事件
        uploadBtn?.addEventListener('click', () => this.startUpload());
    }

    /**
     * 处理文件选择
     */
    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.updateSelectedFiles(files);
    }

    /**
     * 处理拖拽悬停
     */
    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    /**
     * 处理拖拽离开
     */
    handleDragLeave(event) {
        event.currentTarget.classList.remove('dragover');
    }

    /**
     * 处理文件拖放
     */
    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');

        const files = Array.from(event.dataTransfer.files);
        this.updateSelectedFiles(files);
    }

    /**
     * 更新选中的文件
     */
    updateSelectedFiles(files) {
        // 验证文件
        const validFiles = files.filter(file => this.validateFile(file));

        if (validFiles.length === 0) {
            this.showError('请选择有效的文件');
            return;
        }

        this.selectedFiles = validFiles;
        this.displaySelectedFiles();
        this.enableUploadButton();

        // 自动上传功能
        if (this.autoUpload && validFiles.length > 0) {
            console.log(`[UniversalUploader] 自动上传已启用，开始上传文件`);
            // 自动上传时不显示状态，直接开始上传
            setTimeout(() => {
                this.startUpload();
            }, 100); // 延迟100ms确保UI更新完成
        }
    }

    /**
     * 验证文件
     */
    validateFile(file) {
        // 检查文件大小
        if (file.size > this.maxFileSize) {
            this.showError(`文件 ${file.name} 太大，最大支持 ${this.formatFileSize(this.maxFileSize)}`);
            return false;
        }

        // 检查文件类型
        const allowedTypes = this.acceptedTypes.split(',').map(type => type.trim());
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedTypes.includes(fileExtension)) {
            this.showError(`文件 ${file.name} 格式不支持，支持格式：${this.acceptedTypes}`);
            return false;
        }

        return true;
    }

    /**
     * 显示选中的文件
     */
    displaySelectedFiles() {
        // 自动上传模式下不显示文件信息
        if (this.autoUpload) {
            return;
        }

        if (this.compactMode) {
            // 紧凑模式的状态显示
            const fileStatus = document.getElementById(`${this.containerId}_fileStatus`);
            if (fileStatus) {
                if (this.selectedFiles.length > 0) {
                    const fileName = this.selectedFiles[0].name; // 紧凑模式只显示第一个文件名
                    fileStatus.innerHTML = `<small class="text-success">已选择: ${fileName}</small>`;
                    fileStatus.classList.remove('d-none');
                } else {
                    fileStatus.innerHTML = `<small class="text-muted">未上传文件</small>`;
                    fileStatus.classList.remove('d-none');
                }
            }
        } else {
            // 普通模式的文件信息显示
            const fileInfo = document.getElementById(`${this.containerId}_fileInfo`);
            const fileList = document.getElementById(`${this.containerId}_fileList`);

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

    /**
     * 启用上传按钮
     */
    enableUploadButton() {
        const uploadBtn = document.getElementById(`${this.containerId}_uploadBtn`);
        if (uploadBtn && this.selectedFiles.length > 0) {
            uploadBtn.disabled = false;
        }
    }

    /**
     * 开始上传
     */
    async startUpload() {
        if (this.isUploading || this.selectedFiles.length === 0) {
            return;
        }

        this.isUploading = true;
        this.showProgress();
        this.hideError();

        try {
            const formData = this.buildFormData();
            const result = await this.uploadFiles(formData);
            this.onSuccess(result);
        } catch (error) {
            console.error(`[UniversalUploader] ${this.businessType} 上传失败:`, error);
            this.onError(error);
        } finally {
            this.isUploading = false;
            this.hideProgress();
        }
    }

    /**
     * 构建表单数据
     */
    buildFormData() {
        const formData = new FormData();

        // 添加文件
        if (this.multiple) {
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });
        } else {
            formData.append('file', this.selectedFiles[0]);
        }

        // 添加额外字段
        this.additionalFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (element) {
                formData.append(field.name, element.value);
            }
        });

        // 添加业务类型标识
        formData.append('business_type', this.businessType);

        return formData;
    }

    /**
     * 上传文件到服务器
     */
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

    /**
     * 显示进度条
     */
    showProgress() {
        const progress = document.getElementById(`${this.containerId}_progress`);
        progress?.classList.remove('d-none');
        this.updateProgress(0, '正在上传...');
    }

    /**
     * 隐藏进度条
     */
    hideProgress() {
        const progress = document.getElementById(`${this.containerId}_progress`);
        progress?.classList.add('d-none');
    }

    /**
     * 更新进度
     */
    updateProgress(percent, text) {
        const progressBar = document.querySelector(`#${this.containerId}_progress .progress-bar`);
        const progressText = document.querySelector(`#${this.containerId}_progress .progress-text`);

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        if (progressText) {
            progressText.textContent = text;
        }

        this.onProgress(percent, text);
    }

    /**
     * 显示错误信息
     */
    showError(message) {
        const error = document.getElementById(`${this.containerId}_error`);
        const errorMessage = document.getElementById(`${this.containerId}_errorMessage`);

        if (errorMessage) {
            errorMessage.textContent = message;
        }

        error?.classList.remove('d-none');
    }

    /**
     * 隐藏错误信息
     */
    hideError() {
        const error = document.getElementById(`${this.containerId}_error`);
        error?.classList.add('d-none');
    }

    /**
     * 显示结果
     */
    showResult(html) {
        const result = document.getElementById(`${this.containerId}_result`);
        if (result) {
            result.innerHTML = html;
            result.classList.remove('d-none');
        }
    }

    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 重置组件状态
     */
    reset() {
        this.selectedFiles = [];
        const fileInput = document.getElementById(`${this.containerId}_fileInput`);
        const uploadBtn = document.getElementById(`${this.containerId}_uploadBtn`);
        const fileInfo = document.getElementById(`${this.containerId}_fileInfo`);
        const result = document.getElementById(`${this.containerId}_result`);

        if (fileInput) fileInput.value = '';
        if (uploadBtn) uploadBtn.disabled = true;
        fileInfo?.classList.add('d-none');
        result?.classList.add('d-none');

        this.hideError();
        this.hideProgress();
    }

    // 默认回调函数
    defaultOnSuccess(result) {
        console.log(`[UniversalUploader] ${this.businessType} 上传成功:`, result);
        this.showResult(`<div class="alert alert-success">上传成功！</div>`);
    }

    defaultOnError(error) {
        console.error(`[UniversalUploader] ${this.businessType} 上传失败:`, error);
        this.showError(error.message || '上传失败，请重试');
    }

    defaultOnProgress(percent, text) {
        console.log(`[UniversalUploader] ${this.businessType} 上传进度: ${percent}% - ${text}`);
    }
}

// 导出组件
window.UniversalUploader = UniversalUploader;