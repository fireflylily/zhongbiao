/**
 * 知识库文档管理模块
 * 负责文档上传、管理和渲染
 */

class DocumentManager {
    constructor() {
        this.selectedFiles = [];
        this.currentProductId = null;
        this.currentLibraryId = null;
        this.currentCompanyId = null;
    }

    /**
     * 初始化文档管理器
     */
    init() {
        this.setupUploadZone();
        this.bindEvents();
    }

    /**
     * 渲染产品详情页面
     * @param {Object} product 产品信息
     */
    renderProductDetail(product) {
        const html = `
            <div class="container-fluid px-0">
                <div class="card">
                    <div class="card-header bg-light">
                        <div class="row align-items-center">
                            <div class="col">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-box text-success fs-3 me-3"></i>
                                    <div>
                                        <h5 class="mb-0">${product.product_name}</h5>
                                        <small class="text-muted">${product.description || '暂无描述'}</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-auto">
                                <button class="btn btn-outline-primary" onclick="window.documentManager.showUploadModal(${product.product_id})">
                                    <i class="bi bi-upload"></i> 上传文档
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            ${product.libraries ? product.libraries.map(library => this.renderLibrarySection(product.product_id, library)).join('') : '<div class="col-12"><p class="text-muted">暂无文档库</p></div>'}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('mainContent').innerHTML = html;
    }

    /**
     * 渲染文档库区域
     * @param {number} productId 产品ID
     * @param {Object} library 文档库信息
     */
    renderLibrarySection(productId, library) {
        return `
            <div class="col-12 mb-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">${library.library_name}</h6>
                            <button class="btn btn-sm btn-primary" onclick="window.documentManager.showUploadModal(${productId}, ${library.library_id})">
                                <i class="bi bi-upload"></i> 上传文档
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row g-3" id="documents-${library.library_id}">
                            ${library.documents && library.documents.length > 0 ?
                                library.documents.map(doc => this.renderDocument(doc)).join('') :
                                '<div class="col-12"><div class="text-center py-5"><i class="bi bi-folder text-muted fs-1"></i><p class="text-muted mt-3">暂无文档</p><button class="btn btn-primary" onclick="document.getElementById(\'fileInput\').click()"><i class="bi bi-plus me-2"></i>上传第一个文档</button></div></div>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染文档卡片（增强版 - 基于原版本）
     * @param {Object} doc 文档信息
     */
    renderDocument(doc) {
        const privacyClasses = ['', 'privacy-1', 'privacy-2', 'privacy-3', 'privacy-4'];
        const privacyNames = ['', '公开', '内部', '机密', '绝密'];
        const categoryNames = {
            'tech': '技术文档',
            'impl': '实施方案',
            'service': '服务文档',
            'product': '产品文档',
            'manual': '使用手册',
            'other': '其他'
        };

        const privacyLevel = doc.privacy_classification || 1;
        const category = doc.document_category || 'tech';
        const fileSize = doc.file_size ? (doc.file_size / (1024 * 1024)).toFixed(2) : '0';

        return `
            <div class="col-md-6 col-lg-4">
                <div class="card shadow-sm border-0 kb-document-card h-100" onclick="window.documentManager.viewDocumentDetail(${doc.doc_id})">
                    <div class="card-header bg-light border-0 p-3">
                        <div class="d-flex align-items-center">
                            <div class="bg-primary bg-opacity-10 rounded p-2 me-3">
                                <i class="bi bi-file-earmark-text text-primary fs-5"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-0 text-truncate" title="${doc.original_filename}">${doc.original_filename.length > 20 ? doc.original_filename.substring(0, 20) + '...' : doc.original_filename}</h6>
                                <div class="d-flex align-items-center mt-1">
                                    <span class="badge ${privacyLevel === 1 ? 'bg-success' : privacyLevel === 2 ? 'bg-primary' : privacyLevel === 3 ? 'bg-warning' : 'bg-danger'} me-2 small">
                                        ${privacyNames[privacyLevel]}
                                    </span>
                                    <span class="badge bg-secondary small">
                                        ${categoryNames[category] || '其他'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card-body p-3">
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="text-muted small">
                                    <i class="bi bi-hdd me-1"></i>
                                    ${fileSize} MB
                                </span>
                                <span class="text-muted small">
                                    <i class="bi bi-calendar me-1"></i>
                                    ${doc.upload_time ? new Date(doc.upload_time).toLocaleDateString() : '未知'}
                                </span>
                            </div>
                            ${doc.tags ? `
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <i class="bi bi-tags me-1"></i>
                                        ${JSON.parse(doc.tags).slice(0, 2).join(', ')}
                                    </small>
                                </div>
                            ` : ''}
                        </div>

                        <!-- 状态指示器 -->
                        <div class="mb-3">
                            <div class="row g-2">
                                <div class="col-6">
                                    <div class="d-flex align-items-center justify-content-center p-2 rounded ${doc.parse_status === 'completed' ? 'bg-success bg-opacity-10' : 'bg-warning bg-opacity-10'}">
                                        <i class="bi ${doc.parse_status === 'completed' ? 'bi-check-circle text-success' : 'bi-clock text-warning'} me-1"></i>
                                        <small class="${doc.parse_status === 'completed' ? 'text-success' : 'text-warning'}">
                                            ${doc.parse_status === 'completed' ? '已解析' : '待处理'}
                                        </small>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="d-flex align-items-center justify-content-center p-2 rounded ${doc.vector_status === 'completed' ? 'bg-info bg-opacity-10' : 'bg-secondary bg-opacity-10'}">
                                        <i class="bi ${doc.vector_status === 'completed' ? 'bi-database text-info' : 'bi-hourglass text-secondary'} me-1"></i>
                                        <small class="${doc.vector_status === 'completed' ? 'text-info' : 'text-secondary'}">
                                            ${doc.vector_status === 'completed' ? '已索引' : '待索引'}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card-footer bg-white border-0 p-3">
                        <div class="d-grid">
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); window.documentManager.downloadDocument(${doc.doc_id})" title="下载">
                                    <i class="bi bi-download"></i>
                                </button>
                                <button type="button" class="btn btn-outline-info btn-sm" onclick="event.stopPropagation(); window.documentManager.previewDocument(${doc.doc_id})" title="预览">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <button type="button" class="btn btn-outline-danger btn-sm" onclick="event.stopPropagation(); window.documentManager.deleteDocument(${doc.doc_id})" title="删除">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 显示上传模态框
     * @param {number} productId 产品ID
     * @param {number} libraryId 文档库ID（可选）
     */
    showUploadModal(productId, libraryId = null) {
        this.currentProductId = productId;
        this.currentLibraryId = libraryId;
        this.selectedFiles = [];
        document.getElementById('fileList').innerHTML = '';
        new bootstrap.Modal(document.getElementById('uploadDocumentModal')).show();
    }

    /**
     * 设置上传区域拖拽功能
     */
    setupUploadZone() {
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');

        if (!uploadZone || !fileInput) return;

        // 拖拽事件
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // 文件选择事件
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    /**
     * 处理选择的文件
     * @param {FileList} files 文件列表
     */
    handleFiles(files) {
        this.selectedFiles = Array.from(files);

        const listHtml = this.selectedFiles.map((file, index) =>
            `<div class="alert alert-info d-flex justify-content-between align-items-center">
                <span>${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                <button class="btn btn-sm btn-danger" onclick="window.documentManager.removeFile(${index})">
                    <i class="bi bi-x"></i>
                </button>
            </div>`
        ).join('');

        document.getElementById('fileList').innerHTML = listHtml;
    }

    /**
     * 移除选中的文件
     * @param {number} index 文件索引
     */
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.handleFiles(this.selectedFiles);
    }

    /**
     * 上传文档
     */
    async uploadDocuments() {
        if (this.selectedFiles.length === 0) {
            if (window.showAlert) {
                window.showAlert('请选择要上传的文件', 'warning');
            }
            return;
        }

        // 显示上传进度
        const progressContainer = document.getElementById('uploadProgress');
        if (progressContainer) {
            progressContainer.classList.remove('d-none');
        }

        try {
            let uploadedCount = 0;
            for (const file of this.selectedFiles) {
                await this.uploadSingleFile(file, uploadedCount + 1, this.selectedFiles.length);
                uploadedCount++;
            }

            if (window.showAlert) {
                window.showAlert('所有文件上传成功！', 'success');
            }

            // 关闭模态框并刷新视图
            bootstrap.Modal.getInstance(document.getElementById('uploadDocumentModal')).hide();
            this.refreshCurrentView();

        } catch (error) {
            console.error('上传失败:', error);
            if (window.showAlert) {
                window.showAlert('上传失败：' + error.message, 'danger');
            }
        } finally {
            // 隐藏进度条
            if (progressContainer) {
                progressContainer.classList.add('d-none');
            }
        }
    }

    /**
     * 上传单个文件
     * @param {File} file 文件对象
     * @param {number} current 当前文件序号
     * @param {number} total 总文件数
     */
    async uploadSingleFile(file, current, total) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('product_id', this.currentProductId);
        if (this.currentLibraryId) {
            formData.append('library_id', this.currentLibraryId);
        }

        // 获取分类和隐私级别
        const category = document.getElementById('documentCategory')?.value || 'tech';
        const privacy = document.getElementById('privacyLevel')?.value || '1';
        const tags = document.getElementById('documentTags')?.value || '';

        formData.append('category', category);
        formData.append('privacy_classification', privacy);
        formData.append('tags', tags);

        const percent = Math.round((current / total) * 100);
        this.updateUploadProgress(current, total, percent, file.name);

        const response = await axios.post('/api/knowledge_base/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        if (!response.data.success) {
            throw new Error(response.data.error || '上传失败');
        }

        return response.data;
    }

    /**
     * 更新上传进度
     * @param {number} current 当前文件数
     * @param {number} total 总文件数
     * @param {number} percent 百分比
     * @param {string} fileName 文件名
     */
    updateUploadProgress(current, total, percent, fileName) {
        const progressBar = document.querySelector('#uploadProgress .progress-bar');
        const progressText = document.querySelector('#uploadProgress .progress-text');
        const progressPercent = document.querySelector('#uploadProgress .progress-percent');

        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
        if (progressText) {
            progressText.textContent = `正在上传: ${fileName} (${current}/${total})`;
        }
        if (progressPercent) {
            progressPercent.textContent = percent + '%';
        }
    }

    /**
     * 查看文档详情
     * @param {number} docId 文档ID
     */
    async viewDocumentDetail(docId) {
        try {
            const response = await axios.get(`/api/knowledge_base/documents/${docId}`);
            if (response.data.success) {
                this.showDocumentModal(response.data.data);
            }
        } catch (error) {
            console.error('获取文档详情失败:', error);
            if (window.showAlert) {
                window.showAlert('获取文档详情失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 显示文档详情模态框
     * @param {Object} document 文档信息
     */
    showDocumentModal(document) {
        // 这里可以实现文档详情模态框的显示
        console.log('显示文档详情:', document);
    }

    /**
     * 刷新当前视图
     */
    refreshCurrentView() {
        if (this.currentProductId && window.categoryManager) {
            // 重新选择当前产品以刷新文档列表
            const productName = ''; // 这里可以从当前状态获取产品名称
            window.categoryManager.selectProduct(this.currentProductId, productName);
        }
    }

    /**
     * 上传资质文件
     * @param {string} qualificationId 资质ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadQualificationFile(qualificationId, input) {
        const file = input.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('qualification_type', qualificationId);
            formData.append('company_id', this.currentCompanyId || window.categoryManager?.getCurrentCompanyId());

            const response = await axios.post('/api/knowledge_base/qualifications/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('资质文件上传成功', 'success');
                }
                this.updateQualificationStatus(qualificationId, file.name, 'success');
            }
        } catch (error) {
            console.error('资质文件上传失败:', error);
            if (window.showAlert) {
                window.showAlert('上传失败：' + error.message, 'danger');
            }
            this.updateQualificationStatus(qualificationId, '上传失败', 'error');
        }
    }

    /**
     * 上传财务文件
     * @param {string} financialId 财务文件ID
     * @param {HTMLInputElement} input 文件输入元素
     */
    async uploadFinancialFile(financialId, input) {
        const file = input.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('financial_type', financialId);
            formData.append('company_id', this.currentCompanyId || window.categoryManager?.getCurrentCompanyId());

            const response = await axios.post('/api/knowledge_base/financial/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('财务文件上传成功', 'success');
                }
                this.updateFinancialStatus(financialId, file.name, 'success');
            }
        } catch (error) {
            console.error('财务文件上传失败:', error);
            if (window.showAlert) {
                window.showAlert('上传失败：' + error.message, 'danger');
            }
            this.updateFinancialStatus(financialId, '上传失败', 'error');
        }
    }

    /**
     * 更新资质状态显示
     * @param {string} qualificationId 资质ID
     * @param {string} fileName 文件名
     * @param {string} status 状态
     */
    updateQualificationStatus(qualificationId, fileName, status) {
        const statusElement = document.getElementById(`profile-status-${qualificationId}`);
        if (statusElement) {
            statusElement.classList.remove('d-none');
            statusElement.innerHTML = `<small class="text-${status === 'success' ? 'success' : 'danger'}">${fileName}</small>`;
        }
    }

    /**
     * 更新财务状态显示
     * @param {string} financialId 财务文件ID
     * @param {string} fileName 文件名
     * @param {string} status 状态
     */
    updateFinancialStatus(financialId, fileName, status) {
        const statusElement = document.getElementById(`fin-status-${financialId}`);
        if (statusElement) {
            statusElement.classList.remove('d-none');
            statusElement.innerHTML = `<small class="text-${status === 'success' ? 'success' : 'danger'}">${fileName}</small>`;
        }
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 页面加载完成后初始化上传区域
        document.addEventListener('DOMContentLoaded', () => {
            this.setupUploadZone();
        });
    }

    // Getter methods
    getCurrentProductId() {
        return this.currentProductId;
    }

    getCurrentLibraryId() {
        return this.currentLibraryId;
    }

    /**
     * 查看文档详情
     * @param {number} docId 文档ID
     */
    async viewDocumentDetail(docId) {
        try {
            const response = await axios.get('/api/knowledge_base/documents/' + docId);
            if (response.data.success) {
                const doc = response.data.data;
                this.showDocumentDetailModal(doc);
            }
        } catch (error) {
            console.error('获取文档详情失败:', error);
            if (window.showAlert) {
                window.showAlert('获取文档详情失败', 'danger');
            }
        }
    }

    /**
     * 显示文档详情模态框
     * @param {Object} doc 文档信息
     */
    showDocumentDetailModal(doc) {
        const privacyNames = ['', '🌐 公开', '🏢 内部', '🔒 机密', '🚫 绝密'];
        const categoryNames = {
            'tech': '🔧 技术文档',
            'impl': '📋 实施方案',
            'service': '🛠️ 服务文档',
            'product': '📦 产品文档',
            'manual': '📖 使用手册',
            'other': '📄 其他'
        };

        const modalHtml = `
            <div class="modal fade" id="documentDetailModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">文档详情</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6>${doc.original_filename}</h6>
                                    <p class="text-muted mb-3">${doc.description || '暂无描述'}</p>
                                </div>
                                <div class="col-md-4 text-end">
                                    <span class="privacy-badge privacy-${doc.privacy_classification || 1}">
                                        ${privacyNames[doc.privacy_classification || 1]}
                                    </span>
                                    <br>
                                    <span class="doc-category-badge doc-category-${doc.document_category || 'tech'} mt-2">
                                        ${categoryNames[doc.document_category || 'tech']}
                                    </span>
                                </div>
                            </div>

                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <strong>文件大小：</strong>${doc.file_size ? (doc.file_size / (1024 * 1024)).toFixed(2) : '0'} MB<br>
                                    <strong>文件类型：</strong>${doc.file_type || '未知'}<br>
                                    <strong>上传时间：</strong>${doc.upload_time ? new Date(doc.upload_time).toLocaleString() : '未知'}
                                </div>
                                <div class="col-md-6">
                                    <strong>处理状态：</strong>
                                    <span class="badge bg-${doc.parse_status === 'completed' ? 'success' : 'warning'}">${doc.parse_status || 'pending'}</span><br>
                                    <strong>向量状态：</strong>
                                    <span class="badge bg-${doc.vector_status === 'completed' ? 'success' : 'warning'}">${doc.vector_status || 'pending'}</span>
                                </div>
                            </div>

                            ${doc.tags ? `
                            <div class="mt-3">
                                <strong>标签：</strong>
                                ${JSON.parse(doc.tags).map(tag => '<span class="badge bg-light text-dark me-1">' + tag + '</span>').join('')}
                            </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="btn btn-primary" onclick="window.documentManager.downloadDocument(${doc.doc_id})">下载文档</button>
                            <button type="button" class="btn btn-info" onclick="window.documentManager.previewDocument(${doc.doc_id})">预览文档</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的模态框
        const existingModal = document.getElementById('documentDetailModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新模态框并显示
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        new bootstrap.Modal(document.getElementById('documentDetailModal')).show();
    }

    /**
     * 下载文档
     * @param {number} docId 文档ID
     */
    downloadDocument(docId) {
        window.open('/api/knowledge_base/documents/' + docId + '/download', '_blank');
    }

    /**
     * 预览文档
     * @param {number} docId 文档ID
     */
    async previewDocument(docId) {
        try {
            const response = await axios.get('/api/knowledge_base/documents/' + docId + '/preview');
            if (response.data.success) {
                this.showDocumentPreview(response.data.content);
            }
        } catch (error) {
            console.error('预览文档失败:', error);
            if (window.showAlert) {
                window.showAlert('预览文档失败', 'danger');
            }
        }
    }

    /**
     * 显示文档预览
     * @param {string} content 文档内容
     */
    showDocumentPreview(content) {
        const previewHtml = `
            <div class="modal fade" id="documentPreviewModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">文档预览</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="document-preview" style="max-height: 500px; overflow-y: auto;">
                                ${content}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的预览模态框
        const existingModal = document.getElementById('documentPreviewModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新预览模态框并显示
        document.body.insertAdjacentHTML('beforeend', previewHtml);
        new bootstrap.Modal(document.getElementById('documentPreviewModal')).show();
    }

    /**
     * 删除文档
     * @param {number} docId 文档ID
     */
    async deleteDocument(docId) {
        if (!confirm('确定要删除这个文档吗？')) {
            return;
        }

        try {
            const response = await axios.delete('/api/knowledge_base/documents/' + docId);
            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('文档删除成功', 'success');
                }
                // 刷新当前产品详情
                if (this.currentProductId) {
                    // 通知其他模块刷新
                    if (window.categoryManager) {
                        window.categoryManager.selectProduct(this.currentProductId, '');
                    }
                }
            }
        } catch (error) {
            console.error('删除文档失败:', error);
            if (window.showAlert) {
                window.showAlert('删除文档失败', 'danger');
            }
        }
    }

    /**
     * 渲染分类文档
     * @param {number} productId 产品ID
     * @param {string} category 文档分类
     * @param {Array} documents 文档列表
     */
    renderCategoryDocuments(productId, category) {
        const categoryNames = {
            'tech': '🔧 技术文档',
            'impl': '📋 实施方案',
            'service': '🛠️ 服务文档'
        };

        const html = `
            <div class="container-fluid px-0">
                <div class="card">
                    <div class="card-header bg-light">
                        <div class="row align-items-center">
                            <div class="col">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-folder text-primary fs-3 me-3"></i>
                                    <div>
                                        <h5 class="mb-0">${categoryNames[category] || category}</h5>
                                        <small class="text-muted">产品分类文档</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-auto">
                                <button class="btn btn-outline-primary" onclick="window.documentManager.showUploadModal(${productId})">
                                    <i class="bi bi-upload"></i> 上传文档
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row g-3" id="category-documents-${category}">
                            <div class="col-12">
                                <div class="text-center py-5">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">加载中...</span>
                                    </div>
                                    <p class="text-muted mt-3">正在加载文档...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('mainContent').innerHTML = html;
    }

    setCurrentCompanyId(companyId) {
        this.currentCompanyId = companyId;
    }
}

// 全局函数，供HTML模板调用
window.uploadDocuments = () => window.documentManager.uploadDocuments();
window.uploadQualificationFile = (qualificationId, input) => window.documentManager.uploadQualificationFile(qualificationId, input);
window.uploadFinancialFile = (financialId, input) => window.documentManager.uploadFinancialFile(financialId, input);

// 创建全局实例
window.documentManager = new DocumentManager();