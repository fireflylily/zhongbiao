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
                                    <strong>处理状态：</strong>
                                    <span class="badge bg-${doc.parse_status === 'completed' ? 'success' : 'warning'}">${doc.parse_status || 'pending'}</span><br>
                                    <strong>向量状态：</strong>
                                    <span class="badge bg-${doc.vector_status === 'completed' ? 'success' : 'warning'}">${doc.vector_status || 'pending'}</span>
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
}

// 全局函数，供HTML模板调用
window.uploadDocuments = () => window.documentManager.uploadDocuments();
window.uploadQualificationFile = (qualificationId, input) => window.documentManager.uploadQualificationFile(qualificationId, input);
window.uploadFinancialFile = (financialId, input) => window.documentManager.uploadFinancialFile(financialId, input);

// 创建全局实例
window.documentManager = new DocumentManager();