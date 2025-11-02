// ai_tender_system/web/static/js/pages/index/document-merger-handler.js

class DocumentMergerHandler {
    constructor(projectId, projectName, companyName) {
        this.projectId = projectId;
        this.projectName = projectName;
        this.companyName = companyName;
        this.mergeOptionsModal = new bootstrap.Modal(document.getElementById('mergeOptionsModal'));
        this.mergeDocumentsBtn = document.getElementById('mergeDocumentsBtn');
        this.confirmMergeBtn = document.getElementById('confirmMergeBtn');
        this.businessDocNameSpan = document.getElementById('businessDocName');
        this.p2pDocNameSpan = document.getElementById('p2pDocName');
        this.techDocNameSpan = document.getElementById('techDocName');
        this.previewButtons = document.querySelectorAll('.preview-btn');
        this.sourceFiles = {}; // To store file paths/URLs for preview

        this.init();
    }

    init() {
        this.displayProjectInfo();
        this.fetchSourceFiles();
        this.addEventListeners();
    }

    displayProjectInfo() {
        document.getElementById('displayProjectId').textContent = this.projectId;
        document.getElementById('displayProjectName').textContent = this.projectName;
        document.getElementById('displayCompanyName').textContent = this.companyName;
    }

    addEventListeners() {
        this.mergeDocumentsBtn.addEventListener('click', () => {
            this.mergeOptionsModal.show();
        });

        this.confirmMergeBtn.addEventListener('click', () => {
            this.handleConfirmMerge();
        });

        this.previewButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const docType = event.target.dataset.docType;
                this.handlePreviewButtonClick(docType);
            });
        });
    }

    async fetchSourceFiles() {
        if (!this.projectId) {
            window.notifications.warn('项目ID缺失，无法加载源文件。');
            return;
        }
        try {
            // Assuming an API endpoint to get project's source document paths
            const response = await window.apiClient.get(`/api/projects/${this.projectId}/source-documents`);
            if (response.success && response.data) {
                this.sourceFiles = response.data; // {business_doc_path, p2p_doc_path, tech_doc_path}
                this.renderSourceFiles();
            } else {
                window.notifications.error(response.error || '加载源文件失败。');
            }
        } catch (error) {
            console.error('Error fetching source files:', error);
            window.notifications.error('加载源文件时发生错误。');
        }
    }

    renderSourceFiles() {
        const files = this.sourceFiles;
        if (files.business_doc_path) {
            this.businessDocNameSpan.textContent = this.getFileName(files.business_doc_path);
            document.querySelector('.preview-btn[data-doc-type="business"]').style.display = 'inline-block';
        }
        if (files.p2p_doc_path) {
            this.p2pDocNameSpan.textContent = this.getFileName(files.p2p_doc_path);
            document.querySelector('.preview-btn[data-doc-type="p2p"]').style.display = 'inline-block';
        }
        if (files.tech_doc_path) {
            this.techDocNameSpan.textContent = this.getFileName(files.tech_doc_path);
            document.querySelector('.preview-btn[data-doc-type="tech"]').style.display = 'inline-block';
        }
    }

    getFileName(filePath) {
        return filePath.split('/').pop().split('\\').pop(); // Handles both / and \ 
    }

    handlePreviewButtonClick(docType) {
        const filePath = this.sourceFiles[`${docType}_doc_path`];
        if (filePath) {
            // Assuming a download/preview URL for the file path
            const fileUrl = `/api/download-file?path=${encodeURIComponent(filePath)}`;
            window.documentPreviewUtil.preview(fileUrl, this.getFileName(filePath));
        } else {
            window.notifications.info('文件路径未找到。');
        }
    }

    async handleConfirmMerge() {
        this.mergeOptionsModal.hide();
        const styleOption = document.querySelector('input[name="styleOption"]:checked').value;

        this.mergeDocumentsBtn.disabled = true;
        this.mergeDocumentsBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>融合中...';
        window.notifications.info('文件融合任务已启动...');

        try {
            // 使用正确的 API 路径,包含项目ID
            const response = await window.apiClient.post(`/api/projects/${this.projectId}/merge-documents`, {
                business_doc_path: this.sourceFiles.business_doc_path,
                p2p_doc_path: this.sourceFiles.p2p_doc_path,
                tech_doc_path: this.sourceFiles.tech_doc_path,
                style_option: styleOption
            });

            if (response.message === 'Merge task started' && response.task_id) {
                window.notifications.success('文件融合任务已成功启动！');
                this.startMergeProgressStream(response.task_id);
            } else {
                throw new Error(response.error || '启动融合任务失败。');
            }
        } catch (error) {
            console.error('Error starting merge task:', error);
            window.notifications.error('启动融合任务时发生错误: ' + error.message);
            this.mergeDocumentsBtn.disabled = false;
            this.mergeDocumentsBtn.innerHTML = '<i class="fas fa-file-import me-2"></i>融合文件';
        }
    }

    startMergeProgressStream(taskId) {
        const sseClient = new window.SSEClient();
        const mergeStepEl = document.querySelector('.step-item[data-step="merging"]');
        
        mergeStepEl.classList.add('active');
        mergeStepEl.querySelector('.step-stats').textContent = '初始化中...';

        sseClient.stream({
            url: `/api/merge-status/${taskId}`,
            onEvent: (data) => {
                this.updateMergeProgressUI(data);
            },
            onComplete: (data) => {
                window.notifications.success('文件融合完成！');
                mergeStepEl.classList.remove('active');
                mergeStepEl.classList.add('completed');
                mergeStepEl.querySelector('.step-stats').textContent = '✓ 已完成';
                this.mergeDocumentsBtn.disabled = false;
                this.mergeDocumentsBtn.innerHTML = '<i class="fas fa-file-import me-2"></i>融合文件';
                // Optionally, provide download links for merged_document_path and index_file_path
                if (data.merged_document_path) {
                    window.notifications.info(`融合文档已生成: <a href="/api/download-file?path=${encodeURIComponent(data.merged_document_path)}" target="_blank">下载</a>`);
                }
                if (data.index_file_path) {
                    window.notifications.info(`索引文件已生成: <a href="/api/download-file?path=${encodeURIComponent(data.index_file_path)}" target="_blank">下载</a>`);
                }
            },
            onError: (error) => {
                console.error('SSE Stream Error:', error);
                window.notifications.error('文件融合过程中发生错误: ' + error.message);
                mergeStepEl.classList.remove('active');
                mergeStepEl.classList.add('failed'); // Assuming a 'failed' class for styling
                mergeStepEl.querySelector('.step-stats').textContent = 'X 失败';
                this.mergeDocumentsBtn.disabled = false;
                this.mergeDocumentsBtn.innerHTML = '<i class="fas fa-file-import me-2"></i>融合文件';
            }
        });
    }

    updateMergeProgressUI(data) {
        const mergeStepEl = document.querySelector('.step-item[data-step="merging"]');
        if (data.current_step) {
            mergeStepEl.querySelector('.step-stats').textContent = `${data.current_step} ${data.progress_percentage ? `(${data.progress_percentage.toFixed(0)}%)` : ''}`;
        }
        if (data.overall_status === 'failed') {
            mergeStepEl.classList.remove('active');
            mergeStepEl.classList.add('failed');
            mergeStepEl.querySelector('.step-stats').textContent = `X 失败: ${data.current_step}`;
        }
    }
}
