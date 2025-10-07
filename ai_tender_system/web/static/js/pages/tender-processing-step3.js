// 标书智能处理 - 步骤3：可编辑表格
// 功能：编辑、新增、删除要求

class RequirementsEditorManager {
    constructor(taskId, projectId) {
        this.taskId = taskId;
        this.projectId = projectId;
        this.requirements = [];
        this.pendingChanges = [];  // 待保存的修改
        this.currentFilter = 'all';

        this.initializeEventListeners();
        this.loadRequirements();
    }

    initializeEventListeners() {
        // 类型过滤
        document.querySelectorAll('[data-type-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleTypeFilter(e.target.dataset.typeFilter);
            });
        });

        // 新增要求按钮
        document.getElementById('addRequirementBtn')?.addEventListener('click', () => this.addNewRequirement());

        // 导出按钮
        document.getElementById('exportExcelBtn')?.addEventListener('click', () => this.exportToExcel());

        // 保存并完成按钮
        document.getElementById('saveAndCompleteBtn')?.addEventListener('click', () => this.saveAndComplete());
    }

    async loadRequirements() {
        try {
            const response = await fetch(`/api/tender-processing/requirements/${this.projectId}`);
            const result = await response.json();

            if (result.success) {
                // 按requirement_id排序（数字排序）
                this.requirements = result.requirements.sort((a, b) => a.requirement_id - b.requirement_id);
                this.renderTable();
                this.updateStatistics(result.summary);
            } else {
                throw new Error(result.error || '加载失败');
            }
        } catch (error) {
            console.error('加载要求失败:', error);
            this.showNotification('加载失败: ' + error.message, 'error');
        }
    }

    renderTable(filter = 'all') {
        const tbody = document.getElementById('requirementsTableBody');

        // 过滤数据
        let reqsToShow = this.requirements;
        if (filter !== 'all') {
            reqsToShow = this.requirements.filter(r => r.constraint_type === filter);
        }

        if (reqsToShow.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        暂无数据
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = reqsToShow.map(req => this.createTableRow(req)).join('');

        // 绑定事件
        this.bindTableEvents();
    }

    createTableRow(req) {
        const typeLabels = {
            'mandatory': '强制性',
            'optional': '可选',
            'scoring': '加分项'
        };

        const categoryLabels = {
            'qualification': '资质',
            'technical': '技术',
            'commercial': '商务',
            'service': '服务'
        };

        const priorityLabels = {
            'high': '高',
            'medium': '中',
            'low': '低'
        };

        return `
            <tr data-req-id="${req.requirement_id}">
                <td>${req.requirement_id}</td>
                <td>
                    <select class="form-select form-select-sm editable-field"
                            data-field="constraint_type"
                            data-req-id="${req.requirement_id}">
                        ${Object.entries(typeLabels).map(([val, label]) => `
                            <option value="${val}" ${req.constraint_type === val ? 'selected' : ''}>
                                ${label}
                            </option>
                        `).join('')}
                    </select>
                </td>
                <td>
                    <select class="form-select form-select-sm editable-field"
                            data-field="category"
                            data-req-id="${req.requirement_id}">
                        ${Object.entries(categoryLabels).map(([val, label]) => `
                            <option value="${val}" ${req.category === val ? 'selected' : ''}>
                                ${label}
                            </option>
                        `).join('')}
                    </select>
                </td>
                <td>
                    <input type="text"
                           class="form-control form-control-sm editable-field"
                           data-field="subcategory"
                           data-req-id="${req.requirement_id}"
                           value="${req.subcategory || ''}"
                           placeholder="子分类">
                </td>
                <td>
                    <textarea class="form-control form-control-sm editable-field"
                              data-field="detail"
                              data-req-id="${req.requirement_id}"
                              rows="2"
                              style="min-width: 300px;">${req.detail}</textarea>
                </td>
                <td>
                    <select class="form-select form-select-sm editable-field"
                            data-field="priority"
                            data-req-id="${req.requirement_id}">
                        ${Object.entries(priorityLabels).map(([val, label]) => `
                            <option value="${val}" ${req.priority === val ? 'selected' : ''}>
                                ${label}
                            </option>
                        `).join('')}
                    </select>
                </td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-danger delete-btn"
                            data-req-id="${req.requirement_id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    bindTableEvents() {
        // 可编辑字段变更
        document.querySelectorAll('.editable-field').forEach(field => {
            field.addEventListener('change', (e) => {
                this.handleFieldChange(e.target);
            });
        });

        // 删除按钮
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reqId = parseInt(e.currentTarget.dataset.reqId);
                this.deleteRequirement(reqId);
            });
        });
    }

    handleFieldChange(field) {
        const reqId = parseInt(field.dataset.reqId);
        const fieldName = field.dataset.field;
        const newValue = field.value;

        // 标记为已修改
        field.classList.add('modified');

        // 更新本地数据
        const req = this.requirements.find(r => r.requirement_id === reqId);
        if (req) {
            req[fieldName] = newValue;
        }

        // 记录待保存的修改
        const existingChange = this.pendingChanges.find(c => c.requirement_id === reqId);
        if (existingChange) {
            existingChange[fieldName] = newValue;
        } else {
            this.pendingChanges.push({
                requirement_id: reqId,
                [fieldName]: newValue
            });
        }

        // 更新保存按钮状态
        this.updateSaveButton();
    }

    updateSaveButton() {
        const btn = document.getElementById('saveAndCompleteBtn');
        if (btn) {
            if (this.pendingChanges.length > 0) {
                btn.classList.add('btn-warning');
                btn.classList.remove('btn-success');
                btn.innerHTML = `
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    有 ${this.pendingChanges.length} 项未保存的修改
                `;
            } else {
                btn.classList.remove('btn-warning');
                btn.classList.add('btn-success');
                btn.innerHTML = `
                    <i class="bi bi-check-circle me-2"></i>
                    保存并完成
                `;
            }
        }
    }

    async deleteRequirement(reqId) {
        const confirmed = confirm('确定要删除这条要求吗？');
        if (!confirmed) return;

        try {
            // 从本地删除
            this.requirements = this.requirements.filter(r => r.requirement_id !== reqId);

            // 添加到待保存的操作
            this.pendingChanges.push({
                operation: 'delete',
                requirement_id: reqId
            });

            // 重新渲染
            this.renderTable(this.currentFilter);
            this.updateSaveButton();

            this.showNotification('已标记删除，请点击"保存并完成"确认', 'info');

        } catch (error) {
            console.error('删除失败:', error);
            this.showNotification('删除失败: ' + error.message, 'error');
        }
    }

    addNewRequirement() {
        const newReq = {
            requirement_id: `new_${Date.now()}`,  // 临时ID
            constraint_type: 'mandatory',
            category: 'technical',
            subcategory: '',
            detail: '',
            priority: 'medium',
            _isNew: true
        };

        this.requirements.unshift(newReq);
        this.renderTable(this.currentFilter);

        // 聚焦到详情字段
        setTimeout(() => {
            const detailField = document.querySelector(`[data-req-id="${newReq.requirement_id}"][data-field="detail"]`);
            if (detailField) detailField.focus();
        }, 100);

        this.showNotification('已添加新行，请填写内容', 'info');
    }

    handleTypeFilter(type) {
        this.currentFilter = type;

        // 更新按钮状态
        document.querySelectorAll('[data-type-filter]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.typeFilter === type);
        });

        // 重新渲染
        this.renderTable(type);
    }

    updateStatistics(summary) {
        let totalCount = 0;
        let mandatoryCount = 0;
        let scoringCount = 0;

        // 防御性类型检查：确保summary是数组
        if (Array.isArray(summary)) {
            summary.forEach(item => {
                totalCount += item.count || 0;
                if (item.constraint_type === 'mandatory') {
                    mandatoryCount += item.count || 0;
                } else if (item.constraint_type === 'scoring') {
                    scoringCount += item.count || 0;
                }
            });
        }

        document.getElementById('statTotalRequirements').textContent = totalCount;
        document.getElementById('statMandatory').textContent = mandatoryCount;
        document.getElementById('statScoring').textContent = scoringCount;
    }

    async saveAndComplete() {
        if (this.pendingChanges.length === 0) {
            this.showNotification('没有需要保存的修改', 'info');
            return;
        }

        const confirmed = confirm(`确定要保存 ${this.pendingChanges.length} 项修改吗？`);
        if (!confirmed) return;

        const saveBtn = document.getElementById('saveAndCompleteBtn');
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';

        try {
            // 批量保存修改
            for (const change of this.pendingChanges) {
                if (change.operation === 'delete') {
                    // 删除操作
                    await fetch(`/api/tender-processing/requirements/${change.requirement_id}`, {
                        method: 'DELETE'
                    });
                } else if (change._isNew) {
                    // 新增操作
                    await fetch('/api/tender-processing/requirements', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            task_id: this.taskId,
                            ...change
                        })
                    });
                } else {
                    // 更新操作
                    await fetch(`/api/tender-processing/requirements/${change.requirement_id}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            task_id: this.taskId,
                            ...change
                        })
                    });
                }
            }

            // 清空待保存列表
            this.pendingChanges = [];
            this.updateSaveButton();

            // 移除修改标记
            document.querySelectorAll('.modified').forEach(el => el.classList.remove('modified'));

            this.showNotification('所有修改已保存！', 'success');

            // 显示完成消息
            document.getElementById('step3CompleteMessage').style.display = 'block';
            document.getElementById('step3CompleteMessage').innerHTML = `
                <div class="alert alert-success mt-4">
                    <h5>✅ 全部完成！</h5>
                    <p>标书智能处理流程已完成，您可以：</p>
                    <div class="d-flex gap-2">
                        <button class="btn btn-primary" onclick="location.href='/'">
                            返回首页
                        </button>
                        <button class="btn btn-success" onclick="exportFinalResults()">
                            导出最终结果
                        </button>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('保存失败:', error);
            this.showNotification('保存失败: ' + error.message, 'error');
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    }

    async exportToExcel() {
        try {
            window.location.href = `/api/tender-processing/export/${this.projectId}`;
            this.showNotification('正在下载...', 'info');
        } catch (error) {
            console.error('导出失败:', error);
            this.showNotification('导出失败: ' + error.message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// 全局变量
let requirementsEditorManager;

// 从步骤2进入步骤3的函数
function proceedToStep3(taskId) {
    console.log('进入步骤3，任务ID:', taskId);

    // 隐藏步骤2
    document.getElementById('step2Section').style.display = 'none';

    // 显示步骤3
    document.getElementById('step3Section').style.display = 'block';

    // 更新步骤指示器
    document.getElementById('stepIndicator2').classList.remove('active');
    document.getElementById('stepIndicator2').classList.add('completed');
    document.getElementById('stepIndicator3').classList.add('active');

    // 初始化步骤3管理器（需要projectId）
    const projectId = document.getElementById('projectId')?.value || 1;
    requirementsEditorManager = new RequirementsEditorManager(taskId, projectId);
}

// 导出最终结果
function exportFinalResults() {
    if (requirementsEditorManager) {
        requirementsEditorManager.exportToExcel();
    }
}
