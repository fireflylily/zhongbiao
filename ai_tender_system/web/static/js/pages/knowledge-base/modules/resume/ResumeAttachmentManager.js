/**
 * 简历附件管理器
 * 负责简历附件的增删改查功能
 * 复用 form-common.css 的 .case-attachment-* 样式
 */
class ResumeAttachmentManager {
    constructor(mainManager) {
        this.mainManager = mainManager;
    }

    /**
     * 加载简历附件列表
     * @param {number} resumeId - 简历ID
     */
    async loadAttachments(resumeId) {
        try {
            const result = await window.apiClient.get(`/api/resume_library/attachments/${resumeId}`);

            if (result.success) {
                const attachments = result.data || [];
                this.renderAttachmentList(attachments);

                // 更新附件数量徽章
                const countBadge = document.getElementById('resumeAttachmentCount');
                if (countBadge) {
                    countBadge.textContent = attachments.length;
                }
            }
        } catch (error) {
            console.error('[ResumeAttachmentManager] 加载附件列表失败:', error);
            window.notifications.error('加载附件列表失败');
        }
    }

    /**
     * 渲染附件列表
     * @param {Array} attachments - 附件数组
     */
    renderAttachmentList(attachments) {
        const container = document.getElementById('resumeAttachmentList');
        if (!container) return;

        if (attachments.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-3">暂无附件</div>';
            return;
        }

        const html = attachments.map(att => {
            const typeLabel = this.getAttachmentCategoryLabel(att.attachment_category);
            const fileIcon = this.getFileIcon(att.file_path);

            return `
                <div class="case-attachment-item">
                    <div class="attachment-info">
                        <i class="bi ${fileIcon} me-2 text-primary"></i>
                        <div class="attachment-details">
                            <div class="attachment-name">${this.escapeHtml(att.original_filename || '未知文件')}</div>
                            <div class="attachment-meta">
                                <span class="badge bg-info">${typeLabel}</span>
                                ${att.attachment_description ? `<span class="text-muted ms-2">· ${this.escapeHtml(att.attachment_description)}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="attachment-actions">
                        <button type="button" class="btn btn-sm btn-outline-secondary me-1"
                                onclick="window.resumeLibraryManager.attachmentManager.downloadAttachment(${att.attachment_id})" title="下载">
                            <i class="bi bi-download"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger"
                                onclick="window.resumeLibraryManager.attachmentManager.deleteAttachment(${att.attachment_id})" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    /**
     * 处理附件选择
     * @param {Event} event - 文件输入事件
     */
    async handleAttachmentSelect(event) {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        const resumeId = document.getElementById('resumeId').value;
        if (!resumeId) {
            window.notifications.warning('无法获取简历ID');
            event.target.value = '';
            return;
        }

        const category = document.getElementById('resumeAttachmentCategory').value;
        const description = document.getElementById('resumeAttachmentDescription').value;

        // 遍历所有选中的文件并上传
        for (let file of files) {
            // 检查文件大小（10MB）
            if (file.size > 10 * 1024 * 1024) {
                window.notifications.warning(`文件 "${file.name}" 超过10MB，跳过上传`);
                continue;
            }

            await this.uploadAttachment(resumeId, file, category, description);
        }

        // 清空文件输入和说明
        event.target.value = '';
        document.getElementById('resumeAttachmentDescription').value = '';

        // 重新加载附件列表
        await this.loadAttachments(resumeId);
    }

    /**
     * 上传单个附件
     * @param {number} resumeId - 简历ID
     * @param {File} file - 文件对象
     * @param {string} category - 附件类别
     * @param {string} description - 附件说明
     */
    async uploadAttachment(resumeId, file, category, description) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('resume_id', resumeId);
            formData.append('attachment_category', category);
            formData.append('attachment_description', description || '');

            const result = await window.apiClient.post('/api/resume_library/upload-attachment', formData);

            if (result.success) {
                window.notifications.success(`附件 "${file.name}" 上传成功`);
            } else {
                throw new Error(result.error || '上传失败');
            }
        } catch (error) {
            console.error('[ResumeAttachmentManager] 上传附件失败:', error);
            window.notifications.error(`上传附件 "${file.name}" 失败: ${error.message}`);
        }
    }

    /**
     * 删除附件
     * @param {number} attachmentId - 附件ID
     */
    async deleteAttachment(attachmentId) {
        if (!confirm('确定要删除这个附件吗？')) {
            return;
        }

        try {
            const result = await window.apiClient.delete(`/api/resume_library/attachment/${attachmentId}`);

            if (result.success) {
                window.notifications.success('附件删除成功');

                // 重新加载附件列表
                const resumeId = document.getElementById('resumeId').value;
                if (resumeId) {
                    await this.loadAttachments(resumeId);
                }
            } else {
                throw new Error(result.error || '删除失败');
            }
        } catch (error) {
            console.error('[ResumeAttachmentManager] 删除附件失败:', error);
            window.notifications.error('删除附件失败: ' + error.message);
        }
    }

    /**
     * 下载附件
     * @param {number} attachmentId - 附件ID
     */
    downloadAttachment(attachmentId) {
        // 构建下载URL
        const downloadUrl = `/api/resume_library/attachment/${attachmentId}/download`;
        window.location.href = downloadUrl;
    }

    /**
     * 获取附件类别标签
     * @param {string} category - 附件类别
     * @returns {string} 类别标签
     */
    getAttachmentCategoryLabel(category) {
        const labels = {
            'resume': '简历文件',
            'id_card': '身份证',
            'education': '学历证书',
            'degree': '学位证书',
            'qualification': '资质证书',
            'award': '获奖证书',
            'other': '其他'
        };
        return labels[category] || '其他';
    }

    /**
     * 获取文件图标
     * @param {string} filePath - 文件路径
     * @returns {string} Bootstrap图标类名
     */
    getFileIcon(filePath) {
        if (!filePath) return 'bi-file-earmark';

        const ext = filePath.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
            return 'bi-file-image';
        } else if (ext === 'pdf') {
            return 'bi-file-pdf';
        } else if (['doc', 'docx'].includes(ext)) {
            return 'bi-file-word';
        } else {
            return 'bi-file-earmark';
        }
    }

    /**
     * HTML转义
     * @param {string} text - 待转义的文本
     * @returns {string} 转义后的文本
     */
    escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// 导出类
window.ResumeAttachmentManager = ResumeAttachmentManager;
