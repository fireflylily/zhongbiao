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
     * @param {Object} options - 预览选项
     * @param {boolean} options.newWindow - 是否在新窗口中打开（默认false，使用模态框）
     */
    preview(fileUrl, fileName, fileType = null, options = {}) {
        if (!fileType) {
            // 从文件名推断类型
            const ext = fileName.split('.').pop().toLowerCase();
            fileType = ext;
        }

        console.log('[DocumentPreview] 预览文件:', {
            fileUrl,
            fileName,
            fileType,
            options
        });

        const lowerType = fileType.toLowerCase();

        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(lowerType)) {
            this.previewImage(fileUrl, fileName);
        } else if (['doc', 'docx'].includes(lowerType)) {
            if (options.newWindow) {
                this.previewWordInNewWindow(fileUrl, fileName);
            } else {
                this.previewWord(fileUrl, fileName);
            }
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
     * 在新窗口中预览Word文档
     */
    previewWordInNewWindow(fileUrl, fileName) {
        console.log('[DocumentPreview] 在新窗口中预览Word文档:', fileName);

        // 打开新窗口
        const previewWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');

        if (!previewWindow) {
            if (window.notifications) {
                window.notifications.warning('浏览器阻止了弹出窗口，请检查弹出窗口设置');
            } else {
                alert('浏览器阻止了弹出窗口，请检查弹出窗口设置');
            }
            return;
        }

        // 显示加载状态
        previewWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>预览: ${this.escapeHtml(fileName)}</title>
                <meta charset="utf-8">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
                <script src="/static/vendor/docx-preview/docx-preview.min.js"></script>
            </head>
            <body>
                <div class="preview-header" style="background: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 1rem; position: sticky; top: 0; z-index: 1000;">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="bi bi-file-earmark-text me-2"></i>${this.escapeHtml(fileName)}</h5>
                        <button class="btn btn-outline-secondary btn-sm" onclick="window.close()">
                            <i class="bi bi-x-lg"></i> 关闭
                        </button>
                    </div>
                </div>
                <div class="container-fluid">
                    <div class="d-flex justify-content-center align-items-center" style="height: 80vh;">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                            <p class="mt-3">正在加载文档预览...</p>
                        </div>
                    </div>
                </div>
                <div id="preview-content" class="container-fluid" style="display:none; padding: 2rem;"></div>
            </body>
            </html>
        `);

        // 关闭文档流，确保DOM已完全渲染
        previewWindow.document.close();

        // 等待新窗口加载完成后再fetch文档
        previewWindow.addEventListener('load', () => {
            // 使用docx-preview在前端转换Word文档
            fetch(fileUrl)
                .then(response => response.arrayBuffer())
                .then(arrayBuffer => {
                    const loadingDiv = previewWindow.document.querySelector('.d-flex.justify-content-center');
                    const contentDiv = previewWindow.document.getElementById('preview-content');

                    if (!contentDiv) {
                        console.error('[DocumentPreview] 未找到preview-content元素');
                        return;
                    }

                    // 隐藏加载状态，显示内容区域
                    if (loadingDiv) loadingDiv.style.display = 'none';
                    if (contentDiv) contentDiv.style.display = 'block';

                    // 使用docx-preview渲染，保留所有原始格式
                    previewWindow.docx.renderAsync(arrayBuffer, contentDiv, null, {
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
                        console.log('[DocumentPreview] 新窗口文档预览成功');
                    }).catch(err => {
                        console.error('[DocumentPreview] docx-preview渲染失败:', err);
                        if (contentDiv) {
                            contentDiv.style.display = 'block';
                            contentDiv.innerHTML = '<div class="alert alert-danger m-4">文档渲染失败，请尝试下载文档</div>';
                        }
                    });
                })
                .catch(error => {
                    console.error('[DocumentPreview] 文档预览失败:', error);
                    previewWindow.document.body.innerHTML = `
                        <div class="container mt-5">
                            <div class="alert alert-danger">
                                <h5><i class="bi bi-exclamation-triangle me-2"></i>预览失败</h5>
                                <p>无法预览此文档: ${this.escapeHtml(error.message)}</p>
                                <button class="btn btn-outline-secondary" onclick="window.close()">关闭</button>
                            </div>
                        </div>
                    `;
                });
        });
    }

    /**
     * 预览Word文档（模态框方式）
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
