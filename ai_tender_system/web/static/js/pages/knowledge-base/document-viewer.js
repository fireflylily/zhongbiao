/**
 * 文档查看器模块
 * 负责文档详情和预览功能
 */

class DocumentViewer {
    constructor() {
        this.currentDocId = null;
    }

    /**
     * 查看完整文档
     * @param {String|Number} docId - 文档ID
     */
    async viewDocument(docId) {
        console.log('查看文档:', docId);
        this.currentDocId = docId;

        try {
            // 创建并显示模态框
            this.createModal();
            this.showModal();

            // 获取文档信息
            const response = await axios.get(`/api/knowledge_base/documents/${docId}`);

            if (response.data.success && response.data.data) {
                const doc = response.data.data;
                this.renderDocumentContent(doc);

                // 加载文档预览
                this.loadDocumentPreview(doc.file_name);
            } else {
                throw new Error(response.data.error || '获取文档信息失败');
            }

        } catch (error) {
            console.error('查看文档失败:', error);
            this.showError(error.message);

            if (window.showAlert) {
                window.showAlert('查看文档失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 创建模态框
     */
    createModal() {
        // 移除旧模态框
        const oldModal = document.getElementById('documentViewModal');
        if (oldModal) {
            oldModal.remove();
        }

        // 创建新模态框
        const modalHtml = `
            <div class="modal fade" id="documentViewModal" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-text me-2"></i>文档详情
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="documentViewBody">
                            <div class="text-center py-5">
                                <div class="spinner-border text-primary" role="status"></div>
                                <p class="text-muted mt-2">正在加载文档...</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    /**
     * 显示模态框
     */
    showModal() {
        const modalElement = document.getElementById('documentViewModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    /**
     * 渲染文档内容
     * @param {Object} doc - 文档数据对象
     */
    renderDocumentContent(doc) {
        const bodyHtml = `
            <div class="document-view-content">
                <!-- 文档元信息 -->
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${doc.file_name}</h5>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <p class="mb-1"><strong>文档类型:</strong> ${doc.document_category || '未分类'}</p>
                                <p class="mb-1"><strong>文件大小:</strong> ${this.formatFileSize(doc.file_size)}</p>
                            </div>
                            <div class="col-md-6">
                                <p class="mb-1"><strong>上传时间:</strong> ${this.formatDate(doc.created_at)}</p>
                                <p class="mb-1"><strong>解析状态:</strong>
                                    <span class="badge ${doc.parse_status === 'completed' ? 'bg-success' : 'bg-warning'}">
                                        ${doc.parse_status === 'completed' ? '已解析' : '待解析'}
                                    </span>
                                </p>
                            </div>
                        </div>

                        <!-- 标签 -->
                        ${doc.tags ? `
                        <div class="mt-3">
                            <strong>标签:</strong>
                            ${doc.tags.split(',').map(tag =>
                                `<span class="badge bg-light text-dark me-1">${tag.trim()}</span>`
                            ).join('')}
                        </div>
                        ` : ''}
                    </div>
                </div>

                <!-- 文档内容预览 -->
                <div class="card">
                    <div class="card-header bg-light d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-eye me-2"></i>文档内容预览</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="window.documentViewer.downloadDocument('${doc.file_path}', '${doc.file_name}')">
                            <i class="bi bi-download"></i> 下载
                        </button>
                    </div>
                    <div class="card-body" id="documentContentPreview">
                        <div class="text-center py-3">
                            <div class="spinner-border text-primary spinner-border-sm" role="status"></div>
                            <p class="text-muted small mt-2">正在加载预览...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('documentViewBody').innerHTML = bodyHtml;
    }

    /**
     * 加载文档预览内容
     * @param {String} filename - 文件名
     */
    async loadDocumentPreview(filename) {
        try {
            const response = await axios.get(`/api/document/preview/${filename}`);

            if (response.data.success) {
                document.getElementById('documentContentPreview').innerHTML =
                    response.data.html_content || '<p class="text-muted">暂无预览内容</p>';
            } else {
                throw new Error(response.data.error || '预览失败');
            }
        } catch (error) {
            console.error('预览失败:', error);
            document.getElementById('documentContentPreview').innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-info-circle me-2"></i>
                    无法预览此文档：${error.message}
                </div>
            `;
        }
    }

    /**
     * 显示错误信息
     * @param {String} message - 错误消息
     */
    showError(message) {
        const bodyElement = document.getElementById('documentViewBody');
        if (bodyElement) {
            bodyElement.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>加载失败</strong>
                    <p class="mb-0 mt-2">${message}</p>
                </div>
            `;
        }
    }

    /**
     * 下载文档
     * @param {String} filePath - 文件路径
     * @param {String} fileName - 文件名
     */
    downloadDocument(filePath, fileName) {
        try {
            // 创建隐藏的下载链接
            const link = document.createElement('a');
            link.href = `/api/document/download/${fileName}`;
            link.download = fileName;
            link.style.display = 'none';

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            if (window.showAlert) {
                window.showAlert('开始下载文档...', 'success');
            }
        } catch (error) {
            console.error('下载失败:', error);
            if (window.showAlert) {
                window.showAlert('下载失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 格式化文件大小
     * @param {Number} bytes - 字节数
     * @returns {String} 格式化后的文件大小
     */
    formatFileSize(bytes) {
        if (!bytes) return '未知';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }

    /**
     * 格式化日期
     * @param {String} dateString - 日期字符串
     * @returns {String} 格式化后的日期
     */
    formatDate(dateString) {
        if (!dateString) return '未知';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }
}

// 创建全局实例
window.documentViewer = new DocumentViewer();

// 提供便捷的全局函数（向后兼容）
function viewFullDocument(docId) {
    window.documentViewer.viewDocument(docId);
}