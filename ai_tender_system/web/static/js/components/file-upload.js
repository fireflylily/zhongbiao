/**
 * 文件上传组件
 * 提供拖拽上传、进度显示、文件验证等功能
 */

class FileUploadComponent {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            url: '/api/upload',
            method: 'POST',
            multiple: false,
            accept: '*/*',
            maxSize: 10, // MB
            maxFiles: 5,
            dragAndDrop: true,
            showProgress: true,
            showPreview: true,
            autoUpload: false,
            chunkSize: 1024 * 1024, // 1MB chunks for large files
            ...options
        };

        this.files = [];
        this.uploads = new Map();
        this.isUploading = false;

        this.init();
    }

    /**
     * 初始化组件
     */
    init() {
        this.createHTML();
        this.bindEvents();
        this.setupDragAndDrop();
    }

    /**
     * 创建HTML结构
     */
    createHTML() {
        this.element.innerHTML = `
            <div class="upload-zone" data-upload-zone>
                <div class="upload-zone-content">
                    <i class="bi bi-cloud-upload upload-icon"></i>
                    <h5 class="upload-title">点击或拖拽文件到此区域</h5>
                    <p class="upload-description">
                        支持${this.options.accept === '*/*' ? '所有格式' : this.options.accept}文件，
                        单个文件最大${this.options.maxSize}MB
                        ${this.options.multiple ? `，最多${this.options.maxFiles}个文件` : ''}
                    </p>
                    <input type="file"
                           class="upload-input"
                           ${this.options.multiple ? 'multiple' : ''}
                           accept="${this.options.accept}"
                           style="display: none;">
                </div>
            </div>
            <div class="upload-files" data-upload-files style="display: none;"></div>
            <div class="upload-actions" data-upload-actions style="display: none;">
                <button type="button" class="btn btn-primary btn-sm" data-upload-start>
                    <i class="bi bi-upload"></i> 开始上传
                </button>
                <button type="button" class="btn btn-secondary btn-sm" data-upload-clear>
                    <i class="bi bi-trash"></i> 清空列表
                </button>
            </div>
        `;

        this.uploadZone = this.element.querySelector('[data-upload-zone]');
        this.uploadInput = this.element.querySelector('.upload-input');
        this.filesContainer = this.element.querySelector('[data-upload-files]');
        this.actionsContainer = this.element.querySelector('[data-upload-actions]');
        this.startButton = this.element.querySelector('[data-upload-start]');
        this.clearButton = this.element.querySelector('[data-upload-clear]');
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 点击上传区域
        this.uploadZone.addEventListener('click', (e) => {
            if (e.target.closest('.file-item')) return; // 避免点击文件项时触发
            this.uploadInput.click();
        });

        // 文件选择
        this.uploadInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // 开始上传
        this.startButton.addEventListener('click', () => {
            this.startUpload();
        });

        // 清空列表
        this.clearButton.addEventListener('click', () => {
            this.clearFiles();
        });
    }

    /**
     * 设置拖拽上传
     */
    setupDragAndDrop() {
        if (!this.options.dragAndDrop) return;

        let dragCounter = 0;

        this.uploadZone.addEventListener('dragenter', (e) => {
            e.preventDefault();
            dragCounter++;
            this.uploadZone.classList.add('dragover');
        });

        this.uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                this.uploadZone.classList.remove('dragover');
            }
        });

        this.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        this.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dragCounter = 0;
            this.uploadZone.classList.remove('dragover');

            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });
    }

    /**
     * 处理选择的文件
     */
    handleFiles(fileList) {
        const files = Array.from(fileList);

        // 验证文件数量
        if (!this.options.multiple && files.length > 1) {
            window.notifications?.error('只能选择一个文件');
            return;
        }

        if (this.options.multiple && this.files.length + files.length > this.options.maxFiles) {
            window.notifications?.error(`最多只能选择${this.options.maxFiles}个文件`);
            return;
        }

        // 验证每个文件
        const validFiles = [];
        for (const file of files) {
            if (this.validateFile(file)) {
                validFiles.push(file);
            }
        }

        if (validFiles.length === 0) return;

        // 添加文件到列表
        validFiles.forEach(file => {
            const fileInfo = {
                id: Date.now() + Math.random(),
                file: file,
                status: 'pending', // pending, uploading, success, error
                progress: 0,
                error: null,
                response: null
            };

            this.files.push(fileInfo);
            this.renderFileItem(fileInfo);
        });

        this.updateUI();

        // 自动上传
        if (this.options.autoUpload) {
            this.startUpload();
        }

        // 触发文件添加事件
        this.dispatchEvent('filesAdded', { files: validFiles });
    }

    /**
     * 验证文件
     */
    validateFile(file) {
        // 检查文件大小
        if (file.size > this.options.maxSize * 1024 * 1024) {
            window.notifications?.error(`文件"${file.name}"超过${this.options.maxSize}MB限制`);
            return false;
        }

        // 检查文件类型
        if (this.options.accept !== '*/*') {
            const acceptTypes = this.options.accept.split(',').map(type => type.trim());
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            const mimeType = file.type;

            const isValidType = acceptTypes.some(type => {
                if (type.startsWith('.')) {
                    return fileExt === type;
                } else if (type.includes('/*')) {
                    return mimeType.startsWith(type.replace('/*', ''));
                } else {
                    return mimeType === type;
                }
            });

            if (!isValidType) {
                window.notifications?.error(`文件"${file.name}"格式不支持`);
                return false;
            }
        }

        // 检查重复文件
        const isDuplicate = this.files.some(fileInfo =>
            fileInfo.file.name === file.name &&
            fileInfo.file.size === file.size
        );

        if (isDuplicate) {
            window.notifications?.warning(`文件"${file.name}"已存在`);
            return false;
        }

        return true;
    }

    /**
     * 渲染文件项
     */
    renderFileItem(fileInfo) {
        const fileElement = document.createElement('div');
        fileElement.className = 'file-item';
        fileElement.setAttribute('data-file-id', fileInfo.id);

        fileElement.innerHTML = `
            <div class="file-icon">
                <i class="bi ${this.getFileIcon(fileInfo.file)}"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${fileInfo.file.name}</div>
                <div class="file-meta">
                    ${this.formatFileSize(fileInfo.file.size)} •
                    <span class="file-status">${this.getStatusText(fileInfo.status)}</span>
                </div>
                <div class="file-progress" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            <div class="file-actions">
                <button type="button" class="btn btn-sm btn-outline-danger" data-remove-file>
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `;

        // 绑定移除按钮事件
        const removeButton = fileElement.querySelector('[data-remove-file]');
        removeButton.addEventListener('click', () => {
            this.removeFile(fileInfo.id);
        });

        this.filesContainer.appendChild(fileElement);
    }

    /**
     * 开始上传
     */
    async startUpload() {
        if (this.isUploading) return;

        const pendingFiles = this.files.filter(f => f.status === 'pending');
        if (pendingFiles.length === 0) return;

        this.isUploading = true;
        this.updateUI();

        this.dispatchEvent('uploadStart');

        try {
            for (const fileInfo of pendingFiles) {
                await this.uploadFile(fileInfo);
            }

            window.notifications?.success('所有文件上传完成');
            this.dispatchEvent('uploadComplete');
        } catch (error) {
            console.error('上传失败:', error);
            window.notifications?.error('上传过程中发生错误');
        } finally {
            this.isUploading = false;
            this.updateUI();
        }
    }

    /**
     * 上传单个文件
     */
    async uploadFile(fileInfo) {
        fileInfo.status = 'uploading';
        this.updateFileItem(fileInfo);

        try {
            const response = await window.apiClient?.uploadFile(
                this.options.url,
                fileInfo.file,
                this.options.data || {},
                (progress) => {
                    fileInfo.progress = progress;
                    this.updateFileProgress(fileInfo);
                }
            );

            fileInfo.status = 'success';
            fileInfo.response = response;
            this.updateFileItem(fileInfo);

            this.dispatchEvent('fileUploaded', { fileInfo, response });
        } catch (error) {
            fileInfo.status = 'error';
            fileInfo.error = error.message;
            this.updateFileItem(fileInfo);

            this.dispatchEvent('fileError', { fileInfo, error });
        }
    }

    /**
     * 更新文件项状态
     */
    updateFileItem(fileInfo) {
        const fileElement = this.element.querySelector(`[data-file-id="${fileInfo.id}"]`);
        if (!fileElement) return;

        const statusElement = fileElement.querySelector('.file-status');
        const progressContainer = fileElement.querySelector('.file-progress');

        statusElement.textContent = this.getStatusText(fileInfo.status);

        if (fileInfo.status === 'uploading') {
            progressContainer.style.display = 'block';
        } else {
            progressContainer.style.display = 'none';
        }

        // 更新样式
        fileElement.className = `file-item file-item-${fileInfo.status}`;
    }

    /**
     * 更新文件进度
     */
    updateFileProgress(fileInfo) {
        const fileElement = this.element.querySelector(`[data-file-id="${fileInfo.id}"]`);
        if (!fileElement) return;

        const progressBar = fileElement.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${fileInfo.progress}%`;
        }
    }

    /**
     * 移除文件
     */
    removeFile(fileId) {
        const index = this.files.findIndex(f => f.id === fileId);
        if (index === -1) return;

        const fileInfo = this.files[index];

        // 如果正在上传，尝试取消
        if (fileInfo.status === 'uploading') {
            // TODO: 实现上传取消逻辑
        }

        this.files.splice(index, 1);

        const fileElement = this.element.querySelector(`[data-file-id="${fileId}"]`);
        if (fileElement) {
            fileElement.remove();
        }

        this.updateUI();
        this.dispatchEvent('fileRemoved', { fileInfo });
    }

    /**
     * 清空所有文件
     */
    clearFiles() {
        this.files = [];
        this.filesContainer.innerHTML = '';
        this.updateUI();
        this.dispatchEvent('filesCleared');
    }

    /**
     * 更新UI状态
     */
    updateUI() {
        const hasFiles = this.files.length > 0;
        const hasPendingFiles = this.files.some(f => f.status === 'pending');

        this.filesContainer.style.display = hasFiles ? 'block' : 'none';
        this.actionsContainer.style.display = hasFiles && !this.options.autoUpload ? 'block' : 'none';

        if (this.startButton) {
            this.startButton.disabled = this.isUploading || !hasPendingFiles;
        }
    }

    /**
     * 获取文件图标
     */
    getFileIcon(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        const iconMap = {
            pdf: 'bi-file-earmark-pdf',
            doc: 'bi-file-earmark-word',
            docx: 'bi-file-earmark-word',
            xls: 'bi-file-earmark-excel',
            xlsx: 'bi-file-earmark-excel',
            ppt: 'bi-file-earmark-ppt',
            pptx: 'bi-file-earmark-ppt',
            jpg: 'bi-file-earmark-image',
            jpeg: 'bi-file-earmark-image',
            png: 'bi-file-earmark-image',
            gif: 'bi-file-earmark-image',
            zip: 'bi-file-earmark-zip',
            rar: 'bi-file-earmark-zip',
            txt: 'bi-file-earmark-text',
            csv: 'bi-file-earmark-text'
        };

        return iconMap[ext] || 'bi-file-earmark';
    }

    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusMap = {
            pending: '等待上传',
            uploading: '上传中...',
            success: '上传成功',
            error: '上传失败'
        };
        return statusMap[status] || status;
    }

    /**
     * 触发自定义事件
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, { detail });
        this.element.dispatchEvent(event);
    }

    /**
     * 获取上传成功的文件
     */
    getSuccessFiles() {
        return this.files.filter(f => f.status === 'success');
    }

    /**
     * 获取所有文件信息
     */
    getFiles() {
        return this.files;
    }

    /**
     * 销毁组件
     */
    destroy() {
        this.element.innerHTML = '';
        this.files = [];
        this.uploads.clear();
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    const uploadElements = document.querySelectorAll('[data-file-upload]');
    uploadElements.forEach(element => {
        const options = JSON.parse(element.getAttribute('data-file-upload') || '{}');
        new FileUploadComponent(element, options);
    });
});

// 导出给其他模块使用
window.FileUploadComponent = FileUploadComponent;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = FileUploadComponent;
}