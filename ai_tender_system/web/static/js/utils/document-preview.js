/**
 * 通用文档预览工具类
 * 支持图片、Word文档和PDF的预览
 * 可在多个模块中复用
 */

class DocumentPreviewUtil {
    constructor() {
        this.modalId = 'documentPreviewModal';
        this.contentId = 'documentPreviewContent';
    }

    /**
     * 预览文档（自动识别文件类型）
     * @param {string} fileUrl - 文件URL
     * @param {string} fileName - 文件名
     * @param {string} fileType - 文件类型（可选，如果不传会从fileName推断）
     */
    preview(fileUrl, fileName, fileType = null) {
        if (!fileType) {
            // 从文件名推断类型
            const ext = fileName.split('.').pop().toLowerCase();
            fileType = ext;
        }

        console.log('[DocumentPreview] 预览文件:', {
            fileUrl,
            fileName,
            fileType
        });

        const lowerType = fileType.toLowerCase();

        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(lowerType)) {
            this.previewImage(fileUrl, fileName);
        } else if (['doc', 'docx'].includes(lowerType)) {
            this.previewWord(fileUrl, fileName);
        } else if (lowerType === 'pdf') {
            this.previewPDF(fileUrl, fileName);
        } else {
            console.warn('[DocumentPreview] 不支持的文件类型:', fileType);
            alert(`不支持预览此文件类型: ${fileType}\n请下载后查看`);
        }
    }

    /**
     * 预览图片
     */
    previewImage(fileUrl, fileName) {
        const modalHtml = `
            <div class="modal fade" id="${this.modalId}" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-image me-2"></i>图片预览 - ${this.escapeHtml(fileName)}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center" style="background: #f5f5f5; padding: 20px;">
                            <img src="${fileUrl}" class="img-fluid" alt="${this.escapeHtml(fileName)}"
                                 style="max-height: 70vh; object-fit: contain;">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.showModal(modalHtml);
    }

    /**
     * 预览Word文档
     */
    previewWord(fileUrl, fileName) {
        console.log('[DocumentPreview] 开始预览Word文档:', fileName);
        console.log('[DocumentPreview] docx库是否已加载:', typeof docx !== 'undefined');

        const modalHtml = `
            <div class="modal fade" id="${this.modalId}" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-word me-2"></i>文档预览 - ${this.escapeHtml(fileName)}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="${this.contentId}"
                             style="max-height: 70vh; overflow-y: auto; background: #f5f5f5;">
                            <div class="text-center py-5">
                                <div class="spinner-border text-primary" role="status"></div>
                                <p class="mt-3">正在加载文档...</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.showModal(modalHtml);

        // 使用docx-preview渲染Word文档
        console.log('[DocumentPreview] 文档URL:', fileUrl);

        fetch(fileUrl)
            .then(response => {
                console.log('[DocumentPreview] fetch响应状态:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP错误: ${response.status}`);
                }
                return response.arrayBuffer();
            })
            .then(arrayBuffer => {
                console.log('[DocumentPreview] 文档已下载，大小:', arrayBuffer.byteLength, '字节');
                const container = document.getElementById(this.contentId);

                if (!container) {
                    console.error('[DocumentPreview] 未找到预览容器');
                    return;
                }

                if (typeof docx !== 'undefined') {
                    console.log('[DocumentPreview] 开始渲染文档...');
                    container.innerHTML = '';

                    // 使用docx-preview渲染，保留所有原始格式
                    docx.renderAsync(arrayBuffer, container, null, {
                        className: 'docx-preview',
                        inWrapper: true,
                        ignoreWidth: false,
                        ignoreHeight: false,
                        ignoreFonts: false,  // 保留字体格式
                        breakPages: true,
                        ignoreLastRenderedPageBreak: true,
                        experimental: true,
                        trimXmlDeclaration: true
                    }).then(() => {
                        console.log('[DocumentPreview] 文档渲染成功');
                    }).catch(err => {
                        console.error('[DocumentPreview] 文档渲染失败:', err);
                        container.innerHTML = `
                            <div class="alert alert-warning m-4">
                                <i class="bi bi-exclamation-triangle me-2"></i>
                                <strong>文档预览失败</strong><br>
                                错误信息: ${this.escapeHtml(err.message)}<br>
                                请尝试下载后查看
                            </div>
                        `;
                    });
                } else {
                    console.error('[DocumentPreview] docx库未加载');
                    container.innerHTML = `
                        <div class="alert alert-warning m-4">
                            <i class="bi bi-exclamation-triangle me-2"></i>
                            文档预览功能暂不可用（docx库未加载），请下载后查看
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('[DocumentPreview] 加载文档失败:', error);
                const container = document.getElementById(this.contentId);
                if (container) {
                    container.innerHTML = `
                        <div class="alert alert-danger m-4">
                            <i class="bi bi-exclamation-triangle me-2"></i>
                            <strong>文档加载失败</strong><br>
                            错误信息: ${this.escapeHtml(error.message)}<br>
                            请检查文件是否存在或尝试重新上传
                        </div>
                    `;
                }
            });
    }

    /**
     * 预览PDF
     */
    previewPDF(fileUrl, fileName) {
        const modalHtml = `
            <div class="modal fade" id="${this.modalId}" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-pdf me-2"></i>PDF预览 - ${this.escapeHtml(fileName)}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-0">
                            <iframe src="${fileUrl}"
                                    style="width: 100%; height: 70vh; border: none;"
                                    title="${this.escapeHtml(fileName)}">
                            </iframe>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.showModal(modalHtml);
    }

    /**
     * 显示模态框
     */
    showModal(modalHtml) {
        // 移除旧的模态框
        const oldModal = document.getElementById(this.modalId);
        if (oldModal) {
            oldModal.remove();
        }

        // 添加新的模态框
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById(this.modalId));
        modal.show();

        // 模态框关闭后移除
        document.getElementById(this.modalId).addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    /**
     * HTML转义
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 创建全局实例
window.documentPreviewUtil = new DocumentPreviewUtil();
