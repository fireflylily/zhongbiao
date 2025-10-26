/**
 * 简历智能解析上传器
 * 负责简历文件的上传和智能解析功能
 */
class ResumeParser {
    constructor(mainManager) {
        this.mainManager = mainManager;
    }

    /**
     * 显示智能解析模态框
     */
    showParseModal() {
        const modalHtml = `
            <div class="modal fade" id="parseResumeModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-earmark-text me-2"></i>智能简历解析
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- 上传区域 -->
                            <div id="resumeUploadArea" class="mb-4">
                                <div class="alert alert-info">
                                    <i class="bi bi-info-circle me-2"></i>
                                    上传Word或PDF格式的简历文件，系统将自动解析并填充人员信息
                                </div>

                                <!-- 原生文件上传区域 -->
                                <div class="upload-zone border rounded p-4 text-center" id="resumeNativeUploadZone"
                                     style="cursor: pointer; background: #f8f9fa; border: 2px dashed #dee2e6 !important;">
                                    <i class="bi bi-cloud-upload text-primary" style="font-size: 3rem;"></i>
                                    <p class="mt-3 mb-2">点击或拖拽文件到这里上传</p>
                                    <small class="text-muted">支持 PDF、Word 文档（最大10MB）</small>
                                    <input type="file" id="resumeFileInput" accept=".pdf,.doc,.docx"
                                           style="display: none;">
                                </div>

                                <!-- 文件信息显示 -->
                                <div id="resumeFileInfo" class="mt-3 d-none">
                                    <div class="alert alert-success">
                                        <i class="bi bi-file-earmark-text me-2"></i>
                                        已选择文件：<strong id="resumeFileName"></strong>
                                        <span id="resumeFileSize" class="text-muted"></span>
                                    </div>
                                </div>

                                <!-- 上传进度 -->
                                <div id="resumeUploadProgress" class="mt-3 d-none">
                                    <div class="progress">
                                        <div class="progress-bar progress-bar-striped progress-bar-animated"
                                             role="progressbar" style="width: 0%">
                                            正在上传...
                                        </div>
                                    </div>
                                </div>

                                <!-- 错误提示 -->
                                <div id="resumeUploadError" class="mt-3 d-none">
                                    <div class="alert alert-danger">
                                        <i class="bi bi-exclamation-triangle me-2"></i>
                                        <span id="resumeErrorMessage"></span>
                                    </div>
                                </div>
                            </div>

                            <!-- 解析结果 -->
                            <div id="parseResultSection" style="display:none;">
                                <h6 class="mb-3">解析结果</h6>
                                <form id="parsedResumeForm">
                                    <div class="row g-3">
                                        <div class="col-md-6">
                                            <label class="form-label">姓名 <span class="text-danger">*</span></label>
                                            <input type="text" class="form-control" name="name" required>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">性别</label>
                                            <select class="form-select" name="gender">
                                                <option value="">请选择</option>
                                                <option value="男">男</option>
                                                <option value="女">女</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">手机号码</label>
                                            <input type="tel" class="form-control" name="phone">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">邮箱</label>
                                            <input type="email" class="form-control" name="email">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">学历</label>
                                            <select class="form-select" name="education_level">
                                                <option value="">请选择</option>
                                                <option value="博士">博士</option>
                                                <option value="硕士">硕士</option>
                                                <option value="本科">本科</option>
                                                <option value="大专">大专</option>
                                                <option value="高中">高中</option>
                                                <option value="中专">中专</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">毕业院校</label>
                                            <input type="text" class="form-control" name="university">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">专业</label>
                                            <input type="text" class="form-control" name="major">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">当前职位</label>
                                            <input type="text" class="form-control" name="current_position">
                                        </div>
                                        <div class="col-md-12">
                                            <label class="form-label">当前工作单位</label>
                                            <input type="text" class="form-control" name="current_company">
                                        </div>
                                        <div class="col-md-12">
                                            <label class="form-label">个人简介</label>
                                            <textarea class="form-control" name="introduction" rows="3"></textarea>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="saveParseResultBtn"
                                    style="display:none;" onclick="window.resumeLibraryManager.parser.saveParsedResume()">
                                <i class="bi bi-check-circle me-2"></i>保存简历
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 添加到页面
        const container = document.getElementById('resumeModalsContainer');
        container.innerHTML = modalHtml;

        // 初始化原生文件上传
        this.initUploader();

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('parseResumeModal'));
        modal.show();
    }

    /**
     * 初始化简历上传组件（原生文件上传）
     */
    initUploader() {
        const uploadZone = document.getElementById('resumeNativeUploadZone');
        const fileInput = document.getElementById('resumeFileInput');

        if (!uploadZone || !fileInput) {
            console.error('[ResumeParser] 上传区域或文件输入元素未找到');
            return;
        }

        console.log('[ResumeParser] 初始化原生文件上传...');

        // 上传区域点击事件
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        // 文件选择事件
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                console.log('[ResumeParser] 文件已选择:', file.name);
                this.displayFileInfo(file);
                this.uploadAndParseResume(file);
            }
        });

        // 拖拽上传事件
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.style.borderColor = '#4a89dc';
                uploadZone.style.background = '#e8f4ff';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.style.borderColor = '#dee2e6';
                uploadZone.style.background = '#f8f9fa';
            }, false);
        });

        uploadZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                console.log('[ResumeParser] 拖拽文件:', file.name);
                fileInput.files = files;
                this.displayFileInfo(file);
                this.uploadAndParseResume(file);
            }
        }, false);

        console.log('[ResumeParser] 初始化完成');
    }

    /**
     * 防止默认拖拽行为
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * 显示文件信息
     */
    displayFileInfo(file) {
        const fileName = document.getElementById('resumeFileName');
        const fileSize = document.getElementById('resumeFileSize');
        const fileInfo = document.getElementById('resumeFileInfo');

        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = `(${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        if (fileInfo) fileInfo.classList.remove('d-none');

        console.log('[ResumeParser] 文件信息已显示');
    }

    /**
     * 上传并解析简历
     */
    async uploadAndParseResume(file) {
        console.log('[ResumeParser] 开始上传并解析简历...');

        // 验证文件类型
        const allowedTypes = ['.pdf', '.doc', '.docx'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExt)) {
            this.showError('不支持的文件格式，请上传 PDF 或 Word 文档');
            return;
        }

        // 验证文件大小（10MB）
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('文件太大，最大支持 10MB');
            return;
        }

        // 显示上传进度
        this.showProgress(true);
        this.hideError();

        // 构建FormData
        const formData = new FormData();
        formData.append('file', file);
        if (this.mainManager.currentCompanyId) {
            formData.append('company_id', this.mainManager.currentCompanyId);
        }

        try {
            const result = await window.apiClient.post('/api/resume_library/parse-resume', formData);
            console.log('[ResumeParser] 解析结果:', result);

            if (result.success && result.data && result.data.parsed_data) {
                // 填充解析结果
                this.fillParsedData(result.data.parsed_data);

                // 显示解析结果表单
                const resultSection = document.getElementById('parseResultSection');
                const saveBtn = document.getElementById('saveParseResultBtn');
                if (resultSection) resultSection.style.display = 'block';
                if (saveBtn) saveBtn.style.display = 'inline-block';

                // 隐藏上传区域
                const uploadArea = document.getElementById('resumeUploadArea');
                if (uploadArea) uploadArea.style.display = 'none';

                console.log('[ResumeParser] 解析成功，已填充数据');
            } else {
                throw new Error(result.error || result.message || '解析失败');
            }
        } catch (error) {
            console.error('[ResumeParser] 上传解析失败:', error);
            this.showError('简历解析失败: ' + error.message);
        } finally {
            this.showProgress(false);
        }
    }

    /**
     * 显示/隐藏上传进度
     */
    showProgress(show) {
        const progress = document.getElementById('resumeUploadProgress');
        if (progress) {
            if (show) {
                progress.classList.remove('d-none');
            } else {
                progress.classList.add('d-none');
            }
        }
    }

    /**
     * 显示错误信息
     */
    showError(message) {
        const errorDiv = document.getElementById('resumeUploadError');
        const errorMsg = document.getElementById('resumeErrorMessage');
        if (errorDiv && errorMsg) {
            errorMsg.textContent = message;
            errorDiv.classList.remove('d-none');
        }
        console.error('[ResumeParser] 错误:', message);
    }

    /**
     * 隐藏错误信息
     */
    hideError() {
        const errorDiv = document.getElementById('resumeUploadError');
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }
    }

    /**
     * 填充解析的数据到表单
     */
    fillParsedData(data) {
        const form = document.getElementById('parsedResumeForm');
        if (!form) return;

        // 填充表单字段
        Object.keys(data).forEach(key => {
            const input = form.elements[key];
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = data[key];
                } else {
                    input.value = data[key] || '';
                }
            }
        });
    }

    /**
     * 保存解析的简历
     */
    async saveParsedResume() {
        const form = document.getElementById('parsedResumeForm');
        if (!form) return;

        // 收集表单数据
        const formData = new FormData(form);
        const resumeData = {};
        formData.forEach((value, key) => {
            resumeData[key] = value;
        });

        // 添加公司ID
        if (this.mainManager.currentCompanyId) {
            resumeData.company_id = this.mainManager.currentCompanyId;
        }

        try {
            const result = await window.apiClient.post('/api/resume_library/create', resumeData);

            if (result.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('parseResumeModal'));
                modal.hide();

                // 刷新列表
                await this.mainManager.loadResumes();

                // 显示成功消息
                window.notifications.success('简历保存成功');
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('[ResumeParser] 保存简历失败:', error);
            window.notifications.error('保存失败: ' + error.message);
        }
    }
}

// 导出类
window.ResumeParser = ResumeParser;
