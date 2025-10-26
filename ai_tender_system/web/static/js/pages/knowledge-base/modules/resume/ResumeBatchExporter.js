/**
 * 简历批量导出器
 * 负责简历的批量导出功能
 */
class ResumeBatchExporter {
    constructor(mainManager) {
        this.mainManager = mainManager;
    }

    /**
     * 显示批量导出模态框
     */
    showBatchExportModal() {
        const selectedIds = this.mainManager.selectedResumeIds;

        if (selectedIds.size === 0) {
            window.notifications.warning('请先选择要导出的简历');
            return;
        }

        const modalHtml = `
            <div class="modal fade" id="batchExportModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-download me-2"></i>批量导出简历
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                已选择 <strong>${selectedIds.size}</strong> 份简历
                            </div>

                            <div class="mb-3">
                                <label class="form-label">导出选项</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="includeAttachments" checked>
                                    <label class="form-check-label" for="includeAttachments">
                                        包含附件
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="includeSummary" checked>
                                    <label class="form-check-label" for="includeSummary">
                                        生成汇总文件
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="organizeByCategory" checked>
                                    <label class="form-check-label" for="organizeByCategory">
                                        按类别组织文件
                                    </label>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">附件类别</label>
                                <div class="row g-2">
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="resume" id="cat_resume" checked>
                                            <label class="form-check-label" for="cat_resume">简历文件</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="id_card" id="cat_id_card" checked>
                                            <label class="form-check-label" for="cat_id_card">身份证</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="education" id="cat_education" checked>
                                            <label class="form-check-label" for="cat_education">学历证书</label>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="degree" id="cat_degree" checked>
                                            <label class="form-check-label" for="cat_degree">学位证书</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="qualification" id="cat_qualification" checked>
                                            <label class="form-check-label" for="cat_qualification">资质证书</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input attachment-category" type="checkbox"
                                                   value="award" id="cat_award" checked>
                                            <label class="form-check-label" for="cat_award">获奖证书</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="window.resumeLibraryManager.batchExporter.executeExport()">
                                <i class="bi bi-download me-2"></i>开始导出
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('resumeModalsContainer');
        container.innerHTML = modalHtml;

        const modal = new bootstrap.Modal(document.getElementById('batchExportModal'));
        modal.show();
    }

    /**
     * 执行导出
     */
    async executeExport() {
        // 收集选项
        const options = {
            include_attachments: document.getElementById('includeAttachments').checked,
            include_summary: document.getElementById('includeSummary').checked,
            organize_by_category: document.getElementById('organizeByCategory').checked,
            attachment_categories: []
        };

        // 收集选中的附件类别
        document.querySelectorAll('.attachment-category:checked').forEach(checkbox => {
            options.attachment_categories.push(checkbox.value);
        });

        // 准备导出数据
        const exportData = {
            resume_ids: Array.from(this.mainManager.selectedResumeIds),
            options: options
        };

        try {
            // 使用apiClient进行API调用
            const result = await window.apiClient.post('/api/resume_library/export', exportData);

            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('batchExportModal'));
            modal.hide();

            // 下载文件
            if (result.data.download_url) {
                window.location.href = result.data.download_url;
            }

            // 显示统计信息
            window.notifications.success(
                `导出成功！共导出 ${result.data.stats.total_resumes} 份简历，${result.data.stats.total_attachments} 个附件`
            );
        } catch (error) {
            console.error('[ResumeBatchExporter] 导出失败:', error);
            window.notifications.error('导出失败: ' + error.message);
        }
    }
}

// 导出类
window.ResumeBatchExporter = ResumeBatchExporter;
