/**
 * 简历详情管理器
 * 负责简历详情/编辑页面的渲染和数据管理
 * 复用 form-common.css 的样式
 */
class ResumeDetailManager {
    constructor(mainManager) {
        this.mainManager = mainManager;
    }

    /**
     * 渲染简历详情/编辑页面
     * @param {number} resumeId - 简历ID
     */
    async renderDetailView(resumeId) {
        console.log('[ResumeDetailManager] 渲染简历详情页面...', resumeId);

        const container = this.mainManager.container;
        if (!container) {
            console.error('[ResumeDetailManager] Container not found');
            return;
        }

        const html = `
            <div class="resume-detail-wrapper">
                <!-- 顶部操作栏 -->
                <div class="case-edit-header mb-4">
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="d-flex align-items-center">
                            <button type="button" class="btn btn-outline-secondary me-3"
                                    onclick="window.resumeLibraryManager.detailManager.backToList()">
                                <i class="bi bi-arrow-left me-1"></i>返回列表
                            </button>
                            <h4 class="mb-0">简历详情</h4>
                        </div>
                        <div>
                            <button type="button" class="btn btn-primary"
                                    onclick="window.resumeLibraryManager.detailManager.saveResume()">
                                <i class="bi bi-save me-1"></i>保存
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 详情内容 -->
                <div class="resume-detail-content">
                    <input type="hidden" id="resumeId" value="${resumeId}">

                    <!-- 基本信息 -->
                    <div class="case-form-section">
                        <h6>基本信息</h6>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">姓名 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="resumeName" required>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">性别</label>
                                <select class="form-select" id="resumeGender">
                                    <option value="">请选择</option>
                                    <option value="男">男</option>
                                    <option value="女">女</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">出生日期</label>
                                <input type="date" class="form-control" id="resumeBirthDate">
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-4">
                                <label class="form-label">民族</label>
                                <input type="text" class="form-control" id="resumeNationality">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">籍贯</label>
                                <input type="text" class="form-control" id="resumeNativePlace">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">政治面貌</label>
                                <select class="form-select" id="resumePoliticalStatus">
                                    <option value="">请选择</option>
                                    <option value="中共党员">中共党员</option>
                                    <option value="共青团员">共青团员</option>
                                    <option value="群众">群众</option>
                                    <option value="民主党派">民主党派</option>
                                </select>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <label class="form-label">身份证号</label>
                                <input type="text" class="form-control" id="resumeIdNumber">
                            </div>
                        </div>
                    </div>

                    <!-- 联系方式 -->
                    <div class="case-form-section">
                        <h6>联系方式</h6>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">手机号码</label>
                                <input type="tel" class="form-control" id="resumePhone">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">电子邮箱</label>
                                <input type="email" class="form-control" id="resumeEmail">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">联系地址</label>
                                <input type="text" class="form-control" id="resumeAddress">
                            </div>
                        </div>
                    </div>

                    <!-- 教育信息 -->
                    <div class="case-form-section">
                        <h6>教育信息</h6>
                        <div class="row">
                            <div class="col-md-3">
                                <label class="form-label">学历</label>
                                <select class="form-select" id="resumeEducationLevel">
                                    <option value="">请选择</option>
                                    <option value="博士">博士</option>
                                    <option value="硕士">硕士</option>
                                    <option value="本科">本科</option>
                                    <option value="大专">大专</option>
                                    <option value="高中">高中</option>
                                    <option value="中专">中专</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">学位</label>
                                <input type="text" class="form-control" id="resumeDegree" placeholder="如：工学硕士">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">毕业院校</label>
                                <input type="text" class="form-control" id="resumeUniversity">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">专业</label>
                                <input type="text" class="form-control" id="resumeMajor">
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-3">
                                <label class="form-label">毕业时间</label>
                                <input type="date" class="form-control" id="resumeGraduationDate">
                            </div>
                        </div>
                    </div>

                    <!-- 工作信息 -->
                    <div class="case-form-section">
                        <h6>工作信息</h6>
                        <div class="row">
                            <div class="col-md-3">
                                <label class="form-label">当前职位</label>
                                <input type="text" class="form-control" id="resumeCurrentPosition">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">职称</label>
                                <input type="text" class="form-control" id="resumeProfessionalTitle">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">工作年限</label>
                                <input type="number" class="form-control" id="resumeWorkYears" min="0">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">状态</label>
                                <select class="form-select" id="resumeStatus">
                                    <option value="active">在职</option>
                                    <option value="inactive">离职</option>
                                    <option value="archived">归档</option>
                                </select>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <label class="form-label">当前工作单位</label>
                                <input type="text" class="form-control" id="resumeCurrentCompany">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">所在部门</label>
                                <input type="text" class="form-control" id="resumeDepartment">
                            </div>
                        </div>
                    </div>

                    <!-- 工作经历 -->
                    <div class="case-form-section">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="mb-0">
                                <i class="bi bi-briefcase me-2"></i>工作经历
                            </h6>
                            <button type="button" class="btn btn-sm btn-outline-primary"
                                    onclick="window.resumeLibraryManager.experienceManager.addWorkExperience()">
                                <i class="bi bi-plus-circle me-1"></i>添加
                            </button>
                        </div>
                        <div id="workExperienceList" class="experience-list">
                            <!-- 工作经历将动态渲染在这里 -->
                        </div>
                    </div>

                    <!-- 项目经历 -->
                    <div class="case-form-section">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="mb-0">
                                <i class="bi bi-diagram-3 me-2"></i>项目经历
                            </h6>
                            <button type="button" class="btn btn-sm btn-outline-primary"
                                    onclick="window.resumeLibraryManager.experienceManager.addProjectExperience()">
                                <i class="bi bi-plus-circle me-1"></i>添加
                            </button>
                        </div>
                        <div id="projectExperienceList" class="experience-list">
                            <!-- 项目经历将动态渲染在这里 -->
                        </div>
                    </div>

                    <!-- 附件管理 -->
                    <div class="case-form-section">
                        <h6>
                            <i class="bi bi-paperclip me-2"></i>简历附件
                            <span class="badge bg-secondary ms-2" id="resumeAttachmentCount">0</span>
                        </h6>

                        <!-- 上传区域 -->
                        <div class="case-attachment-upload-area mb-3">
                            <div class="upload-box">
                                <input type="file" id="resumeAttachmentInput" multiple
                                       accept="image/*,.pdf,.doc,.docx" style="display: none;"
                                       onchange="window.resumeLibraryManager.attachmentManager.handleAttachmentSelect(event)">
                                <div class="upload-prompt" onclick="document.getElementById('resumeAttachmentInput').click()">
                                    <i class="bi bi-cloud-upload text-primary" style="font-size: 2rem;"></i>
                                    <p class="mt-2 mb-1">点击或拖拽文件到这里上传</p>
                                    <small class="text-muted">支持图片、PDF、Word文档，单个文件不超过10MB</small>
                                </div>
                            </div>
                        </div>

                        <!-- 附件类型选择 -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">附件类型</label>
                                <select class="form-select" id="resumeAttachmentCategory">
                                    <option value="resume">简历文件</option>
                                    <option value="id_card">身份证</option>
                                    <option value="education">学历证书</option>
                                    <option value="degree">学位证书</option>
                                    <option value="qualification">资质证书</option>
                                    <option value="award">获奖证书</option>
                                    <option value="other">其他</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">附件说明</label>
                                <input type="text" class="form-control" id="resumeAttachmentDescription"
                                       placeholder="选填，简要说明附件内容">
                            </div>
                        </div>

                        <!-- 附件列表 -->
                        <div class="case-attachment-list mt-3" id="resumeAttachmentList">
                            <!-- 附件列表将动态渲染在这里 -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // 加载简历数据
        await this.loadResumeData(resumeId);
    }

    /**
     * 返回列表视图
     */
    async backToList() {
        await this.mainManager.renderResumeLibraryView();
    }

    /**
     * 加载简历数据
     * @param {number} resumeId - 简历ID
     */
    async loadResumeData(resumeId) {
        try {
            const result = await window.apiClient.get(`/api/resume_library/detail/${resumeId}`);

            if (!result.success) {
                throw new Error(result.error || '获取简历信息失败');
            }

            const resume = result.data;

            // 填充基本信息
            document.getElementById('resumeName').value = resume.name || '';
            document.getElementById('resumeGender').value = resume.gender || '';
            document.getElementById('resumeBirthDate').value = resume.birth_date || '';
            document.getElementById('resumeNationality').value = resume.nationality || '';
            document.getElementById('resumeNativePlace').value = resume.native_place || '';
            document.getElementById('resumePoliticalStatus').value = resume.political_status || '';
            document.getElementById('resumeIdNumber').value = resume.id_number || '';

            // 填充联系方式
            document.getElementById('resumePhone').value = resume.phone || '';
            document.getElementById('resumeEmail').value = resume.email || '';
            document.getElementById('resumeAddress').value = resume.address || '';

            // 填充教育信息
            document.getElementById('resumeEducationLevel').value = resume.education_level || '';
            document.getElementById('resumeDegree').value = resume.degree || '';
            document.getElementById('resumeUniversity').value = resume.university || '';
            document.getElementById('resumeMajor').value = resume.major || '';
            document.getElementById('resumeGraduationDate').value = resume.graduation_date || '';

            // 填充工作信息
            document.getElementById('resumeCurrentPosition').value = resume.current_position || '';
            document.getElementById('resumeProfessionalTitle').value = resume.professional_title || '';
            document.getElementById('resumeWorkYears').value = resume.work_years || '';
            document.getElementById('resumeStatus').value = resume.status || 'active';
            document.getElementById('resumeCurrentCompany').value = resume.current_company || '';
            document.getElementById('resumeDepartment').value = resume.department || '';

            // 加载工作经历（使用经历管理器）
            this.mainManager.experienceManager.loadWorkExperience(resume.work_experience);

            // 加载项目经历（使用经历管理器）
            this.mainManager.experienceManager.loadProjectExperience(resume.project_experience);

            // 加载附件（使用附件管理器）
            await this.mainManager.attachmentManager.loadAttachments(resumeId);

        } catch (error) {
            console.error('[ResumeDetailManager] 加载简历数据失败:', error);
            window.notifications.error('加载简历数据失败: ' + error.message);
        }
    }

    /**
     * 保存简历
     */
    async saveResume() {
        const resumeId = document.getElementById('resumeId').value;

        // 验证必填字段
        const name = document.getElementById('resumeName').value;
        if (!name || !name.trim()) {
            window.notifications.warning('请填写姓名');
            document.getElementById('resumeName').focus();
            return;
        }

        // 收集表单数据
        const data = {
            name: name,
            gender: document.getElementById('resumeGender').value,
            birth_date: document.getElementById('resumeBirthDate').value,
            nationality: document.getElementById('resumeNationality').value,
            native_place: document.getElementById('resumeNativePlace').value,
            political_status: document.getElementById('resumePoliticalStatus').value,
            id_number: document.getElementById('resumeIdNumber').value,
            phone: document.getElementById('resumePhone').value,
            email: document.getElementById('resumeEmail').value,
            address: document.getElementById('resumeAddress').value,
            education_level: document.getElementById('resumeEducationLevel').value,
            degree: document.getElementById('resumeDegree').value,
            university: document.getElementById('resumeUniversity').value,
            major: document.getElementById('resumeMajor').value,
            graduation_date: document.getElementById('resumeGraduationDate').value,
            current_position: document.getElementById('resumeCurrentPosition').value,
            professional_title: document.getElementById('resumeProfessionalTitle').value,
            work_years: document.getElementById('resumeWorkYears').value ? parseInt(document.getElementById('resumeWorkYears').value) : null,
            status: document.getElementById('resumeStatus').value,
            current_company: document.getElementById('resumeCurrentCompany').value,
            department: document.getElementById('resumeDepartment').value,
            // 添加工作经历和项目经历（从经历管理器获取）
            work_experience: this.mainManager.experienceManager.getExperienceData('work'),
            project_experience: this.mainManager.experienceManager.getExperienceData('project')
        };

        try {
            const result = await window.apiClient.put(`/api/resume_library/update/${resumeId}`, data);

            if (result.success) {
                window.notifications.success('保存成功');
                await this.backToList();
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('[ResumeDetailManager] 保存简历失败:', error);
            window.notifications.error('保存失败：' + error.message);
        }
    }
}

// 导出类
window.ResumeDetailManager = ResumeDetailManager;
