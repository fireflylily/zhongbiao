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

        // 文档库筛选器
        this.docFilters = {
            companyId: null,
            productId: null,
            category: null,
            privacy: null,
            searchKeyword: ''
        };
        this.allDocuments = [];
    }

    /**
     * 初始化文档管理器
     */
    init() {
        // 上传功能已迁移到 UniversalUploader，在 showUploadModal() 中动态初始化
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
                                        ${(() => {
                                            try {
                                                const tags = typeof doc.tags === 'string' ? JSON.parse(doc.tags) : doc.tags;
                                                return Array.isArray(tags) ? tags.slice(0, 2).join(', ') : '';
                                            } catch(e) {
                                                return doc.tags;
                                            }
                                        })()}
                                    </small>
                                </div>
                            ` : ''}
                        </div>

                        <!-- 状态指示器（只显示向量索引状态，隐藏解析状态） -->
                        <div class="mb-3">
                            <div class="row g-2">
                                <div class="col-12">
                                    ${doc.vector_status === 'completed'
                                        ? `<div class="d-flex align-items-center justify-content-center p-2 rounded bg-info bg-opacity-10">
                                               <i class="bi bi-database text-info me-1"></i>
                                               <small class="text-info">已索引</small>
                                           </div>`
                                        : `<button type="button"
                                               class="btn btn-sm btn-outline-primary w-100 py-2"
                                               onclick="event.stopPropagation(); window.documentManager.vectorizeDocument(${doc.doc_id})"
                                               title="点击建立智能索引">
                                               <i class="bi bi-lightning-charge me-1"></i>
                                               <small>建立索引</small>
                                           </button>`
                                    }
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
     * 显示上传模态框 - 使用 UniversalUploader 组件
     * @param {number} productId 产品ID
     * @param {number} libraryId 文档库ID（可选）
     */
    showUploadModal(productId, libraryId = null) {
        this.currentProductId = productId;
        this.currentLibraryId = libraryId;

        // 清理旧的上传器实例
        if (this.uploader) {
            this.uploader = null;
        }

        // 创建新的 UniversalUploader 实例
        this.uploader = new UniversalUploader({
            containerId: 'kbUploadContainer',
            businessType: 'knowledge_base_document',
            multiple: true,
            acceptedTypes: '.pdf,.doc,.docx',
            uploadText: '点击或拖拽文档到这里',
            supportText: '支持 PDF、Word 文档，可批量上传',
            autoUpload: false,  // 不自动上传，需点击按钮
            maxFileSize: 50 * 1024 * 1024, // 50MB

            // 额外表单字段
            additionalFields: [
                {
                    type: 'select',
                    id: 'kbPrivacyLevel',
                    name: 'privacy_classification',
                    label: '隐私级别',
                    options: [
                        {value: '1', text: '🌐 公开 - 所有用户可访问'},
                        {value: '2', text: '🏢 内部 - 内部用户可访问'},
                        {value: '3', text: '🔒 机密 - 管理员可访问'},
                        {value: '4', text: '🚫 绝密 - 超级管理员可访问'}
                    ]
                },
                {
                    type: 'text',
                    id: 'kbDocumentTags',
                    name: 'tags',
                    label: '标签 (可选)',
                    placeholder: '用逗号分隔，例如：技术规格, 用户指南, 安装说明'
                }
            ],

            // 关键：自定义上传逻辑
            customUpload: async (files, formData) => {
                return await this.uploadToKnowledgeBase(files, formData);
            },

            onSuccess: async (result) => {
                console.log('文档上传成功', result);

                // 显示上传成功消息
                if (window.showAlert) {
                    window.showAlert(result.message || '所有文档上传成功！', 'success');
                }

                // 关闭 modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('uploadDocumentModal'));
                if (modal) modal.hide();

                // 🆕 自动触发向量化
                if (window.ragIntegration && result.results) {
                    for (const docResult of result.results) {
                        if (docResult.success && docResult.file_path) {
                            console.log('触发文档向量化:', docResult.original_filename);
                            await window.ragIntegration.vectorizeDocument({
                                file_path: docResult.file_path,
                                company_id: docResult.company_id,
                                product_id: docResult.product_id,
                                document_id: docResult.doc_id,
                                document_type: docResult.file_type || 'document',
                                document_name: docResult.original_filename
                            });
                        }
                    }
                }

                // 刷新当前视图
                this.refreshCurrentView();
            },

            onError: (error) => {
                console.error('文档上传失败', error);
                if (window.showAlert) {
                    window.showAlert('上传失败：' + error.message, 'danger');
                }
            }
        });

        // 显示 modal
        new bootstrap.Modal(document.getElementById('uploadDocumentModal')).show();
    }

    /**
     * 知识库文档上传适配器
     * @param {File[]} files 文件列表
     * @param {FormData} formData 表单数据（包含额外字段）
     */
    async uploadToKnowledgeBase(files, formData) {
        // 步骤1: 获取或创建 libraryId
        let libraryId = this.currentLibraryId;

        if (!libraryId && this.currentProductId) {
            // 获取产品的文档库列表
            const librariesResp = await axios.get(
                `/api/knowledge_base/product/${this.currentProductId}/libraries`
            );

            if (librariesResp.data.success) {
                const libraries = librariesResp.data.data;
                if (libraries && libraries.length > 0) {
                    libraryId = libraries[0].library_id;
                } else {
                    throw new Error('产品尚未创建文档库，请联系管理员');
                }
            } else {
                throw new Error('获取文档库列表失败');
            }
        }

        if (!libraryId) {
            throw new Error('无法确定文档库，上传失败');
        }

        // 步骤2: 提取额外字段
        const privacy = formData.get('privacy_classification') || '1';
        const tagsStr = formData.get('tags') || '';

        // 处理标签
        let tags = [];
        if (tagsStr) {
            tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);
        }

        // 步骤3: 逐个上传文件
        const results = [];
        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            // 构建单个文件的 FormData
            const fileFormData = new FormData();
            fileFormData.append('file', file);
            fileFormData.append('privacy_classification', privacy);

            if (tags.length > 0) {
                fileFormData.append('tags', JSON.stringify(tags));
            }

            // 调用知识库 API
            const response = await axios.post(
                `/api/knowledge_base/libraries/${libraryId}/documents`,
                fileFormData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            if (!response.data.success) {
                throw new Error(response.data.error || `文件 ${file.name} 上传失败`);
            }

            results.push(response.data);
        }

        return {
            success: true,
            message: `成功上传 ${results.length} 个文档`,
            results: results
        };
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
            window.categoryManager.selectProduct(this.currentProductId, '');
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
        // 上传功能已迁移到 UniversalUploader，无需在此初始化
        // 上传组件在 showUploadModal() 中动态创建
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
                                    <strong>索引状态：</strong>
                                    <span class="badge bg-${doc.vector_status === 'completed' ? 'success' : 'secondary'}">
                                        ${doc.vector_status === 'completed' ? '✓ 已索引' : '未索引'}
                                    </span>
                                    ${doc.chunk_count ? `<small class="text-muted ms-2">(${doc.chunk_count} 个向量块)</small>` : ''}
                                </div>
                            </div>

                            ${doc.tags ? `
                            <div class="mt-3">
                                <strong>标签：</strong>
                                ${(() => {
                                    try {
                                        const tags = typeof doc.tags === 'string' ? JSON.parse(doc.tags) : doc.tags;
                                        return Array.isArray(tags) ? tags.map(tag => '<span class="badge bg-light text-dark me-1">' + tag + '</span>').join('') : '';
                                    } catch(e) {
                                        return '<span class="badge bg-secondary me-1">' + doc.tags + '</span>';
                                    }
                                })()}
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
     * 预览文档（在新窗口打开）
     * @param {number} docId 文档ID
     */
    async previewDocument(docId) {
        try {
            // 首先获取文档信息
            const docResponse = await axios.get('/api/knowledge_base/documents/' + docId);
            if (!docResponse.data.success) {
                throw new Error('获取文档信息失败');
            }

            const document = docResponse.data.data;

            // 打开新窗口并显示加载状态
            const previewWindow = window.open('', '_blank', 'width=1000,height=800,menubar=no,toolbar=no');
            if (!previewWindow) {
                throw new Error('无法打开预览窗口，请检查浏览器弹窗拦截设置');
            }

            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>文档预览 - ${document.original_filename}</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="/static/css/base/variables.css" rel="stylesheet">
                    <style>
                        body {
                            margin: 0;
                            padding: 20px;
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        }
                        .preview-header {
                            position: sticky;
                            top: 0;
                            background: white;
                            z-index: 1000;
                            padding: 15px 0;
                            border-bottom: 2px solid #e9ecef;
                            margin-bottom: 20px;
                        }
                        .document-preview {
                            max-width: 900px;
                            margin: 0 auto;
                            line-height: 1.8;
                        }
                        .loading-spinner {
                            text-align: center;
                            padding: 100px 0;
                        }
                    </style>
                </head>
                <body>
                    <div class="preview-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">${document.original_filename}</h5>
                            <button class="btn btn-secondary btn-sm" onclick="window.close()">
                                <i class="bi bi-x-lg"></i> 关闭
                            </button>
                        </div>
                    </div>
                    <div class="loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3 text-muted">正在加载文档内容...</p>
                    </div>
                </body>
                </html>
            `);

            // 获取预览内容
            const response = await axios.get('/api/knowledge_base/documents/' + docId + '/preview');
            if (!response.data.success) {
                throw new Error(response.data.error || '获取预览内容失败');
            }

            // 渲染预览内容
            const bodyContent = `
                <div class="preview-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">${response.data.filename || document.original_filename}</h5>
                        <button class="btn btn-secondary btn-sm" onclick="window.close()">
                            <i class="bi bi-x-lg"></i> 关闭
                        </button>
                    </div>
                </div>
                <div class="document-preview">
                    ${response.data.content}
                </div>
            `;

            previewWindow.document.body.innerHTML = bodyContent;

        } catch (error) {
            console.error('预览文档失败:', error);
            if (window.showAlert) {
                window.showAlert('预览文档失败: ' + error.message, 'danger');
            }
        }
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
                // 刷新当前视图
                this.refreshCurrentView();
            }
        } catch (error) {
            console.error('删除文档失败:', error);
            if (window.showAlert) {
                window.showAlert('删除文档失败', 'danger');
            }
        }
    }

    /**
     * 向量化文档（手动触发）
     * @param {number} docId 文档ID
     */
    async vectorizeDocument(docId) {
        try {
            // 获取文档详细信息
            const doc = await this.getDocumentDetails(docId);
            if (!doc) {
                throw new Error('文档不存在');
            }

            // 获取library信息以获得company_id和product_id
            const libraryResp = await axios.get(`/api/knowledge_base/libraries/${doc.library_id}`);
            if (!libraryResp.data.success) {
                throw new Error('获取文档库信息失败');
            }

            const library = libraryResp.data.data;
            let company_id = null;
            let product_id = null;

            if (library.owner_type === 'product') {
                product_id = library.owner_id;
                // 获取产品信息
                const productResp = await axios.get(`/api/knowledge_base/products/${product_id}`);
                if (productResp.data.success) {
                    company_id = productResp.data.data.company_id;
                }
            }

            // 调用RAG向量化
            if (window.ragIntegration) {
                await window.ragIntegration.vectorizeDocument({
                    file_path: doc.file_path,
                    company_id: company_id,
                    product_id: product_id,
                    document_id: doc.doc_id,
                    document_type: doc.file_type || 'document',
                    document_name: doc.original_filename
                });

                // 刷新视图
                this.refreshCurrentView();
            } else {
                throw new Error('RAG服务未加载');
            }

        } catch (error) {
            console.error('向量化文档失败:', error);
            if (window.showAlert) {
                window.showAlert('向量化失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 获取文档详细信息
     * @param {number} docId 文档ID
     */
    async getDocumentDetails(docId) {
        try {
            const response = await axios.get(`/api/knowledge_base/documents/${docId}`);
            if (response.data.success) {
                return response.data.data;
            }
            return null;
        } catch (error) {
            console.error('获取文档详情失败:', error);
            return null;
        }
    }

    /**
     * 渲染分类文档
     * @param {number} productId 产品ID
     * @param {string} category 文档分类
     * @param {Array} documents 文档列表
     */
    /**
     * 渲染产品文档列表（简化版 - 不再区分分类）
     * @param {number} productId 产品ID
     * @param {string} productName 产品名称
     * @param {Array} documents 文档列表
     */
    renderProductDocuments(productId, productName, documents) {
        // 存储当前产品ID，以便上传和刷新时使用
        this.currentProductId = productId;
        this.currentCategory = null;  // 不再使用分类

        // 渲染文档列表内容
        let documentsHtml = '';
        if (!documents || documents.length === 0) {
            documentsHtml = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="bi bi-folder text-muted fs-1"></i>
                        <p class="text-muted mt-3">暂无文档</p>
                        <button class="btn btn-primary" onclick="window.documentManager.showUploadModal(${productId})">
                            <i class="bi bi-plus me-2"></i>上传第一个文档
                        </button>
                    </div>
                </div>
            `;
        } else {
            documentsHtml = documents.map(doc => this.renderDocument(doc)).join('');
        }

        const html = `
            <div class="container-fluid px-0">
                <div class="card">
                    <div class="card-header bg-light">
                        <div class="row align-items-center">
                            <div class="col">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-box-seam text-success fs-3 me-3"></i>
                                    <div>
                                        <h5 class="mb-0">${productName}</h5>
                                        <small class="text-muted">产品文档 (${documents ? documents.length : 0}个文档)</small>
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
                        <div class="row g-3" id="product-documents-${productId}">
                            ${documentsHtml}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('mainContent').innerHTML = html;
    }

    /**
     * 兼容性方法 - 保留以防其他地方调用
     * @deprecated 使用 renderProductDocuments 替代
     */
    renderCategoryDocuments(productId, category, documents) {
        // 转发到新方法
        this.renderProductDocuments(productId, `产品${productId}`, documents);
    }

    setCurrentCompanyId(companyId) {
        this.currentCompanyId = companyId;
    }

    // =========================
    // 文档库视图相关方法
    // =========================

    /**
     * 渲染文档库主界面
     */
    async renderDocumentLibraryView() {
        console.log('渲染文档库视图...');

        const mainContent = document.getElementById('documentLibraryMainContent');
        if (!mainContent) {
            console.error('未找到文档库主内容区域');
            return;
        }

        // 确保容器有尺寸
        mainContent.style.width = '100%';
        mainContent.style.minHeight = '500px';
        mainContent.style.display = 'block';

        // 清空主内容区
        mainContent.innerHTML = '';

        // 渲染文档库界面（复用案例库样式）
        const html = `
            <!-- 顶部操作栏 + 统计 -->
            <div class="case-library-header">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center gap-3">
                        <h4 class="mb-0">
                            <i class="bi bi-folder me-2"></i>文档库管理
                        </h4>
                        <span class="badge bg-primary" style="font-size: 0.9rem; padding: 8px 16px;">
                            总文档数：<strong id="docTotalCount">0</strong>
                        </span>
                    </div>
                    <div>
                        <button type="button" class="btn btn-primary" onclick="window.documentManager.showUploadModalForLibrary()">
                            <i class="bi bi-plus-circle me-1"></i>上传文档
                        </button>
                    </div>
                </div>
            </div>

            <!-- 筛选器区域（水平布局） -->
            <div class="case-filters-horizontal">
                <div class="row g-2 align-items-end">
                    <div class="col-lg-3 col-md-4">
                        <label class="form-label small text-muted mb-1">搜索</label>
                        <input type="text" class="form-control" id="docSearchInput"
                               placeholder="搜索文档名称、公司、产品..."
                               onkeyup="window.documentManager.handleDocSearch()">
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">公司</label>
                        <select class="form-select" id="docFilterCompany"
                                onchange="window.documentManager.handleDocFilterChange()">
                            <option value="">全部公司</option>
                        </select>
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">产品</label>
                        <select class="form-select" id="docFilterProduct"
                                onchange="window.documentManager.handleDocFilterChange()">
                            <option value="">全部产品</option>
                        </select>
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">技术类型</label>
                        <select class="form-select" id="docFilterCategory"
                                onchange="window.documentManager.handleDocFilterChange()">
                            <option value="">全部类型</option>
                            <option value="tech">技术文档</option>
                            <option value="impl">实施方案</option>
                            <option value="service">服务文档</option>
                            <option value="product">产品文档</option>
                            <option value="manual">使用手册</option>
                            <option value="other">其他</option>
                        </select>
                    </div>
                    <div class="col-lg-2 col-md-3">
                        <label class="form-label small text-muted mb-1">隐私级别</label>
                        <select class="form-select" id="docFilterPrivacy"
                                onchange="window.documentManager.handleDocFilterChange()">
                            <option value="">全部级别</option>
                            <option value="1">公开</option>
                            <option value="2">内部</option>
                            <option value="3">机密</option>
                            <option value="4">绝密</option>
                        </select>
                    </div>
                    <div class="col-lg-1 col-md-3">
                        <button class="btn btn-secondary w-100" onclick="window.documentManager.resetDocFilters()" title="重置筛选">
                            <i class="bi bi-arrow-counterclockwise"></i>
                        </button>
                    </div>
                </div>
            </div>

            <!-- 文档列表（全宽显示） -->
            <div class="case-list-full-width">
                <div id="docListContainer">
                    <!-- 文档列表将动态渲染在这里 -->
                    <div class="case-loading">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3 text-muted">正在加载文档...</p>
                    </div>
                </div>

                <!-- 空状态 -->
                <div id="docEmptyState" class="case-empty-state" style="display: none;">
                    <i class="bi bi-folder-x"></i>
                    <h5>暂无文档</h5>
                    <p class="text-muted">点击右上角"上传文档"按钮上传第一个文档</p>
                </div>
            </div>
        `;

        mainContent.innerHTML = html;

        // 强制设置子元素的宽度（修复布局问题）
        const header = mainContent.querySelector('.case-library-header');
        const filters = mainContent.querySelector('.case-filters-horizontal');
        const listContainer = mainContent.querySelector('.case-list-full-width');

        if (header) header.style.width = '100%';
        if (filters) filters.style.width = '100%';
        if (listContainer) listContainer.style.width = '100%';

        // 加载数据
        await this.loadCompanyFiltersForDocs();
        await this.loadAllDocuments();
    }

    /**
     * 加载公司筛选器（文档库用）
     */
    async loadCompanyFiltersForDocs() {
        try {
            const response = await axios.get('/api/companies');
            if (response.data.success) {
                const companies = response.data.data || [];
                const filterSelect = document.getElementById('docFilterCompany');
                if (filterSelect) {
                    let options = '<option value="">全部公司</option>';
                    companies.forEach(company => {
                        options += `<option value="${company.company_id}">${this.escapeHtml(company.company_name)}</option>`;
                    });
                    filterSelect.innerHTML = options;
                }
            }
        } catch (error) {
            console.error('加载公司筛选器失败:', error);
        }
    }

    /**
     * 加载产品筛选器（文档库用）
     */
    async loadProductFiltersForDocs(companyId) {
        try {
            const response = await axios.get(`/api/knowledge_base/companies/${companyId}/products`);
            if (response.data.success) {
                const products = response.data.data || [];
                const filterSelect = document.getElementById('docFilterProduct');
                if (filterSelect) {
                    let options = '<option value="">全部产品</option>';
                    products.forEach(product => {
                        options += `<option value="${product.product_id}">${this.escapeHtml(product.product_name)}</option>`;
                    });
                    filterSelect.innerHTML = options;
                }
            }
        } catch (error) {
            console.error('加载产品筛选器失败:', error);
        }
    }

    /**
     * 加载所有文档（带筛选）
     */
    async loadAllDocuments() {
        try {
            // 构建查询参数
            const params = new URLSearchParams();
            if (this.docFilters.companyId) {
                params.append('company_id', this.docFilters.companyId);
            }
            if (this.docFilters.productId) {
                params.append('product_id', this.docFilters.productId);
            }
            if (this.docFilters.category) {
                params.append('document_category', this.docFilters.category);
            }
            if (this.docFilters.privacy) {
                params.append('privacy_classification', this.docFilters.privacy);
            }

            const url = `/api/knowledge_base/documents/all?${params.toString()}`;
            const response = await axios.get(url);

            if (response.data.success) {
                this.allDocuments = response.data.data || [];
                this.renderDocumentList(this.allDocuments);
            } else {
                throw new Error(response.data.error || '加载失败');
            }
        } catch (error) {
            console.error('加载文档列表失败:', error);
            if (window.showAlert) {
                window.showAlert('加载文档列表失败: ' + error.message, 'danger');
            }
            this.renderDocumentList([]);
        }
    }

    /**
     * 渲染文档列表
     */
    renderDocumentList(documents) {
        const container = document.getElementById('docListContainer');
        const emptyState = document.getElementById('docEmptyState');

        if (!container) return;

        // 应用搜索关键词过滤
        let filteredDocs = documents;
        if (this.docFilters.searchKeyword) {
            const keyword = this.docFilters.searchKeyword.toLowerCase();
            filteredDocs = documents.filter(doc =>
                (doc.original_filename && doc.original_filename.toLowerCase().includes(keyword)) ||
                (doc.company_name && doc.company_name.toLowerCase().includes(keyword)) ||
                (doc.product_name && doc.product_name.toLowerCase().includes(keyword)) ||
                (doc.filename && doc.filename.toLowerCase().includes(keyword))
            );
        }

        // 显示空状态或文档列表
        if (filteredDocs.length === 0) {
            container.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        container.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';

        // 渲染文档卡片
        const html = filteredDocs.map(doc => this.renderDocumentCardForLibrary(doc)).join('');
        container.innerHTML = html;

        // 更新统计数字
        const countElement = document.getElementById('docTotalCount');
        if (countElement) {
            countElement.textContent = filteredDocs.length;
        }
    }

    /**
     * 渲染单个文档卡片（文档库专用）
     */
    renderDocumentCardForLibrary(doc) {
        // 技术类型标签
        const categoryLabels = {
            'tech': '技术文档',
            'impl': '实施方案',
            'service': '服务文档',
            'product': '产品文档',
            'manual': '使用手册',
            'other': '其他'
        };

        // 隐私级别标签和样式
        const privacyLabels = ['', '🌐 公开', '🏢 内部', '🔒 机密', '🚫 绝密'];
        const privacyClass = ['', 'case-status-success', 'case-status-progress', 'case-status-pending', 'case-status-pending'];

        const category = doc.document_category || 'tech';
        const privacy = doc.privacy_classification || 1;
        const fileSize = doc.file_size ? (doc.file_size / (1024 * 1024)).toFixed(2) : '0';

        return `
            <div class="case-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h5>${this.escapeHtml(doc.original_filename)}</h5>
                        <div class="case-meta">
                            <i class="bi bi-building"></i>公司: ${this.escapeHtml(doc.company_name || '未知')}
                            <span class="ms-2"><i class="bi bi-box-seam"></i>产品: ${this.escapeHtml(doc.product_name || '未知')}</span>
                        </div>
                        <div class="case-meta">
                            <i class="bi bi-tag"></i>${categoryLabels[category]}
                            <span class="ms-2"><i class="bi bi-file-earmark"></i>${(doc.file_type || 'pdf').toUpperCase()}</span>
                            <span class="ms-2"><i class="bi bi-hdd"></i>${fileSize} MB</span>
                        </div>
                        <div class="case-meta mt-2">
                            <span class="case-status-badge ${privacyClass[privacy]}">${privacyLabels[privacy]}</span>
                            <span class="ms-2 text-muted">
                                <i class="bi bi-calendar"></i>${doc.upload_time ? new Date(doc.upload_time).toLocaleDateString() : ''}
                            </span>
                            ${doc.vector_status === 'completed' ? '<span class="ms-2"><i class="bi bi-database text-info"></i>已索引</span>' : ''}
                        </div>
                    </div>
                    <div class="case-actions">
                        <button type="button" class="btn btn-sm btn-info" onclick="window.documentManager.previewDocument(${doc.doc_id})" title="预览">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-success" onclick="window.documentManager.downloadDocument(${doc.doc_id})" title="下载">
                            <i class="bi bi-download"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-danger" onclick="window.documentManager.deleteDocument(${doc.doc_id})" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 处理筛选器变更
     */
    handleDocFilterChange() {
        this.docFilters.companyId = document.getElementById('docFilterCompany').value || null;
        this.docFilters.productId = document.getElementById('docFilterProduct').value || null;
        this.docFilters.category = document.getElementById('docFilterCategory').value || null;
        this.docFilters.privacy = document.getElementById('docFilterPrivacy').value || null;

        // 当公司变化时，重新加载产品列表
        if (this.docFilters.companyId) {
            this.loadProductFiltersForDocs(this.docFilters.companyId);
        } else {
            // 清空产品筛选器
            const productSelect = document.getElementById('docFilterProduct');
            if (productSelect) {
                productSelect.innerHTML = '<option value="">全部产品</option>';
            }
            this.docFilters.productId = null;
        }

        this.loadAllDocuments();
    }

    /**
     * 处理搜索
     */
    handleDocSearch() {
        const searchInput = document.getElementById('docSearchInput');
        if (searchInput) {
            this.docFilters.searchKeyword = searchInput.value.trim();
            this.renderDocumentList(this.allDocuments);
        }
    }

    /**
     * 重置筛选器
     */
    resetDocFilters() {
        document.getElementById('docFilterCompany').value = '';
        document.getElementById('docFilterProduct').value = '';
        document.getElementById('docFilterCategory').value = '';
        document.getElementById('docFilterPrivacy').value = '';
        document.getElementById('docSearchInput').value = '';

        // 重置产品下拉列表
        const productSelect = document.getElementById('docFilterProduct');
        if (productSelect) {
            productSelect.innerHTML = '<option value="">全部产品</option>';
        }

        this.docFilters = {
            companyId: null,
            productId: null,
            category: null,
            privacy: null,
            searchKeyword: ''
        };

        this.loadAllDocuments();
    }

    /**
     * 显示上传文档模态框（文档库专用）
     */
    showUploadModalForLibrary() {
        // 提示用户先选择公司和产品
        if (window.showAlert) {
            window.showAlert('请先在左侧导航选择公司和产品，然后通过产品节点上传文档', 'info');
        }
    }

    /**
     * HTML转义（如果不存在）
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 全局函数，供HTML模板调用
window.uploadDocuments = () => window.documentManager.uploadDocuments();
window.uploadQualificationFile = (qualificationId, input) => window.documentManager.uploadQualificationFile(qualificationId, input);
window.uploadFinancialFile = (financialId, input) => window.documentManager.uploadFinancialFile(financialId, input);

// 创建全局实例
window.documentManager = new DocumentManager();