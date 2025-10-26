/**
 * 简历经历管理器
 * 负责工作经历和项目经历的增删改查
 * 使用配置驱动模式减少重复代码
 */
class ResumeExperienceManager {
    constructor(mainManager) {
        this.mainManager = mainManager;
        this.workExperienceData = [];
        this.projectExperienceData = [];

        // 经历类型配置（配置驱动，减少重复代码）
        this.experienceConfigs = {
            work: {
                dataKey: 'workExperienceData',
                containerId: 'workExperienceList',
                modalId: 'workExperienceModal',
                formId: 'workExperienceForm',
                title: '工作经历',
                fields: [
                    { name: 'company', label: '公司名称', type: 'text', required: true, placeholder: '' },
                    { name: 'position', label: '职位', type: 'text', required: true, placeholder: '' },
                    { name: 'period', label: '工作时间', type: 'text', required: true, placeholder: '如：2020-01至2023-12' },
                    { name: 'description', label: '工作描述', type: 'textarea', required: false, placeholder: '' }
                ],
                emptyIcon: 'bi-briefcase',
                emptyText: '暂无工作经历'
            },
            project: {
                dataKey: 'projectExperienceData',
                containerId: 'projectExperienceList',
                modalId: 'projectExperienceModal',
                formId: 'projectExperienceForm',
                title: '项目经历',
                fields: [
                    { name: 'name', label: '项目名称', type: 'text', required: true, placeholder: '' },
                    { name: 'role', label: '项目角色', type: 'text', required: true, placeholder: '' },
                    { name: 'period', label: '项目时间', type: 'text', required: true, placeholder: '如：2020-01至2023-12' },
                    { name: 'description', label: '项目描述', type: 'textarea', required: false, placeholder: '' }
                ],
                emptyIcon: 'bi-diagram-3',
                emptyText: '暂无项目经历'
            }
        };
    }

    // ==================== 工作经历方法 ====================

    /**
     * 加载工作经历列表
     * @param {Array|string} workExperienceData - 工作经历数据
     */
    loadWorkExperience(workExperienceData) {
        this.loadExperience('work', workExperienceData);
    }

    /**
     * 添加工作经历
     */
    addWorkExperience() {
        this.showExperienceModal('work', null);
    }

    /**
     * 编辑工作经历
     * @param {number} index - 经历索引
     */
    editWorkExperience(index) {
        if (!this.workExperienceData || !this.workExperienceData[index]) {
            window.notifications.warning('工作经历不存在');
            return;
        }
        this.showExperienceModal('work', index);
    }

    /**
     * 删除工作经历
     * @param {number} index - 经历索引
     */
    deleteWorkExperience(index) {
        this.deleteExperience('work', index);
    }

    /**
     * 保存工作经历
     * @param {number|null} index - 经历索引，null表示新增
     */
    saveWorkExperience(index) {
        this.saveExperience('work', index);
    }

    // ==================== 项目经历方法 ====================

    /**
     * 加载项目经历列表
     * @param {Array|string} projectExperienceData - 项目经历数据
     */
    loadProjectExperience(projectExperienceData) {
        this.loadExperience('project', projectExperienceData);
    }

    /**
     * 添加项目经历
     */
    addProjectExperience() {
        this.showExperienceModal('project', null);
    }

    /**
     * 编辑项目经历
     * @param {number} index - 经历索引
     */
    editProjectExperience(index) {
        if (!this.projectExperienceData || !this.projectExperienceData[index]) {
            window.notifications.warning('项目经历不存在');
            return;
        }
        this.showExperienceModal('project', index);
    }

    /**
     * 删除项目经历
     * @param {number} index - 经历索引
     */
    deleteProjectExperience(index) {
        this.deleteExperience('project', index);
    }

    /**
     * 保存项目经历
     * @param {number|null} index - 经历索引，null表示新增
     */
    saveProjectExperience(index) {
        this.saveExperience('project', index);
    }

    // ==================== 通用经历处理方法 ====================

    /**
     * 加载经历列表（通用方法）
     * @param {string} type - 经历类型：'work' 或 'project'
     * @param {Array|string} experienceData - 经历数据
     */
    loadExperience(type, experienceData) {
        const config = this.experienceConfigs[type];
        const container = document.getElementById(config.containerId);
        if (!container) return;

        let experiences = [];

        // 解析JSON数据
        if (typeof experienceData === 'string') {
            try {
                experiences = JSON.parse(experienceData);
            } catch (e) {
                console.error(`[ResumeExperienceManager] 解析${config.title}数据失败:`, e);
                experiences = [];
            }
        } else if (Array.isArray(experienceData)) {
            experiences = experienceData;
        }

        // 保存到实例
        this[config.dataKey] = experiences;

        if (experiences.length === 0) {
            container.innerHTML = `<div class="text-muted text-center py-3">${config.emptyText}</div>`;
            return;
        }

        // 渲染经历卡片
        const html = experiences.map((exp, index) => this.renderExperienceCard(type, exp, index)).join('');
        container.innerHTML = html;
    }

    /**
     * 渲染单个经历卡片
     * @param {string} type - 经历类型
     * @param {Object} exp - 经历数据
     * @param {number} index - 索引
     * @returns {string} HTML字符串
     */
    renderExperienceCard(type, exp, index) {
        const config = this.experienceConfigs[type];
        const isWork = type === 'work';
        const primaryField = isWork ? exp.company : exp.name;
        const secondaryField = isWork ? exp.position : exp.role;

        return `
            <div class="experience-item card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${this.escapeHtml(primaryField || '未知')}</h6>
                            <div class="text-muted small mb-2">
                                <span class="me-3">
                                    <i class="bi bi-person-badge me-1"></i>${this.escapeHtml(secondaryField || '未知')}
                                </span>
                                <span>
                                    <i class="bi bi-calendar-range me-1"></i>${this.escapeHtml(exp.period || '未知时间')}
                                </span>
                            </div>
                            ${exp.description ? `<p class="mb-0 small">${this.escapeHtml(exp.description)}</p>` : ''}
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button type="button" class="btn btn-outline-primary"
                                    onclick="window.resumeLibraryManager.experienceManager.edit${isWork ? 'Work' : 'Project'}Experience(${index})" title="编辑">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button type="button" class="btn btn-outline-danger"
                                    onclick="window.resumeLibraryManager.experienceManager.delete${isWork ? 'Work' : 'Project'}Experience(${index})" title="删除">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 显示经历编辑模态框（通用方法）
     * @param {string} type - 经历类型
     * @param {number|null} index - 经历索引，null表示新增
     */
    showExperienceModal(type, index) {
        const config = this.experienceConfigs[type];
        const isEdit = index !== null;
        const experience = isEdit ? this[config.dataKey][index] : {};

        // 生成表单字段HTML
        const fieldsHtml = config.fields.map(field => {
            const value = this.escapeHtml(experience[field.name] || '');
            const requiredMark = field.required ? '<span class="text-danger">*</span>' : '';

            if (field.type === 'textarea') {
                return `
                    <div class="mb-3">
                        <label class="form-label">${field.label} ${requiredMark}</label>
                        <textarea class="form-control" name="${field.name}" rows="3"
                                  ${field.required ? 'required' : ''}>${value}</textarea>
                    </div>
                `;
            } else {
                return `
                    <div class="mb-3">
                        <label class="form-label">${field.label} ${requiredMark}</label>
                        <input type="${field.type}" class="form-control" name="${field.name}"
                               value="${value}" ${field.required ? 'required' : ''}
                               placeholder="${field.placeholder}">
                    </div>
                `;
            }
        }).join('');

        const modalHtml = `
            <div class="modal fade" id="${config.modalId}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${isEdit ? '编辑' : '添加'}${config.title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="${config.formId}">
                                ${fieldsHtml}
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary"
                                    onclick="window.resumeLibraryManager.experienceManager.save${type === 'work' ? 'Work' : 'Project'}Experience(${index})">
                                <i class="bi bi-check-circle me-1"></i>保存
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('resumeModalsContainer');
        container.innerHTML = modalHtml;

        const modal = new bootstrap.Modal(document.getElementById(config.modalId));
        modal.show();
    }

    /**
     * 保存经历（通用方法）
     * @param {string} type - 经历类型
     * @param {number|null} index - 经历索引
     */
    saveExperience(type, index) {
        const config = this.experienceConfigs[type];
        const form = document.getElementById(config.formId);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const experience = {};
        formData.forEach((value, key) => {
            experience[key] = value;
        });

        if (!this[config.dataKey]) {
            this[config.dataKey] = [];
        }

        if (index !== null) {
            // 编辑现有项
            this[config.dataKey][index] = experience;
        } else {
            // 添加新项
            this[config.dataKey].push(experience);
        }

        // 刷新显示
        this.loadExperience(type, this[config.dataKey]);

        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById(config.modalId));
        modal.hide();
    }

    /**
     * 删除经历（通用方法）
     * @param {string} type - 经历类型
     * @param {number} index - 经历索引
     */
    deleteExperience(type, index) {
        const config = this.experienceConfigs[type];

        if (!confirm(`确定要删除这条${config.title}吗？`)) {
            return;
        }

        if (!this[config.dataKey]) {
            this[config.dataKey] = [];
        }

        this[config.dataKey].splice(index, 1);
        this.loadExperience(type, this[config.dataKey]);
    }

    /**
     * 获取经历数据
     * @param {string} type - 经历类型
     * @returns {Array} 经历数据数组
     */
    getExperienceData(type) {
        const config = this.experienceConfigs[type];
        return this[config.dataKey] || [];
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
window.ResumeExperienceManager = ResumeExperienceManager;
