/**
 * 需求表格管理器
 * 管理需求数据的展示、过滤、编辑和统计
 *
 * 依赖:
 * - core/notification.js (提示信息)
 * - tender-processing-step3/utils/formatter.js (HTML转义)
 *
 * 用法:
 * const tableManager = new RequirementsTableManager('requirementsTableBody');
 * tableManager.setRequirements(requirements);
 * tableManager.applyFilters({ constraint_type: 'mandatory' });
 */

class RequirementsTableManager {
    /**
     * 构造函数
     * @param {string} tableBodyId - 表格tbody元素的ID
     * @param {Object} options - 配置选项
     */
    constructor(tableBodyId = 'requirementsTableBody', options = {}) {
        this.tableBodyId = tableBodyId;
        this.options = {
            enableEdit: options.enableEdit !== false,
            enableDelete: options.enableDelete !== false,
            enableExport: options.enableExport || false,
            ...options
        };

        // 数据管理
        this.requirements = [];
        this.filteredRequirements = [];

        // 过滤器状态
        this.currentFilters = {
            constraint_type: 'all',
            category: 'all',
            priority: 'all',
            search: ''
        };

        // 编辑状态
        this.editingRow = null;

        console.log('[RequirementsTableManager] 管理器已初始化，表格ID:', tableBodyId);
    }

    /**
     * 设置需求数据并重新渲染
     * @param {Array} requirements - 需求数组
     */
    setRequirements(requirements) {
        this.requirements = requirements || [];
        console.log(`[RequirementsTableManager] 设置需求数据，共 ${this.requirements.length} 条`);
        this.applyFilters();
    }

    /**
     * 应用过滤器
     * @param {Object} filters - 过滤条件（可选）
     */
    applyFilters(filters = null) {
        // 更新过滤器状态
        if (filters) {
            this.currentFilters = { ...this.currentFilters, ...filters };
        }

        console.log('[RequirementsTableManager] 应用过滤器:', this.currentFilters);

        // 过滤数据
        this.filteredRequirements = this.requirements.filter(req => {
            // 约束类型过滤
            if (this.currentFilters.constraint_type !== 'all' &&
                req.constraint_type !== this.currentFilters.constraint_type) {
                return false;
            }

            // 类别过滤
            if (this.currentFilters.category !== 'all' &&
                req.category !== this.currentFilters.category) {
                return false;
            }

            // 优先级过滤
            if (this.currentFilters.priority !== 'all' &&
                req.priority !== this.currentFilters.priority) {
                return false;
            }

            // 搜索过滤
            if (this.currentFilters.search) {
                const searchLower = this.currentFilters.search.toLowerCase();
                const detail = (req.detail || '').toLowerCase();
                const summary = (req.summary || '').toLowerCase();
                return detail.includes(searchLower) || summary.includes(searchLower);
            }

            return true;
        });

        console.log(`[RequirementsTableManager] 过滤后剩余 ${this.filteredRequirements.length} 条`);

        // 重新渲染
        this.render();
    }

    /**
     * 渲染表格
     */
    render() {
        const tbody = document.getElementById(this.tableBodyId);
        if (!tbody) {
            console.error(`[RequirementsTableManager] 未找到表格tbody: ${this.tableBodyId}`);
            return;
        }

        // 空状态处理
        if (this.filteredRequirements.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                        <div class="mt-2">暂无需求数据</div>
                    </td>
                </tr>
            `;
            this.updateStats();
            return;
        }

        // 渲染行
        tbody.innerHTML = this.filteredRequirements.map((req, index) =>
            this._renderRow(req, index)
        ).join('');

        // 绑定事件
        this._bindRowEvents();

        // 更新统计
        this.updateStats();

        console.log('[RequirementsTableManager] 表格渲染完成');
    }

    /**
     * 更新统计信息
     */
    updateStats() {
        const stats = {
            total: this.filteredRequirements.length,
            mandatory: this.filteredRequirements.filter(r => r.constraint_type === 'mandatory').length,
            optional: this.filteredRequirements.filter(r => r.constraint_type === 'optional').length,
            scoring: this.filteredRequirements.filter(r => r.constraint_type === 'scoring').length
        };

        this._updateElement('totalRequirements', stats.total);
        this._updateElement('mandatoryCount', stats.mandatory);
        this._updateElement('optionalCount', stats.optional);
        this._updateElement('scoringCount', stats.scoring);

        console.log('[RequirementsTableManager] 统计更新:', stats);
    }

    /**
     * 编辑需求
     * @param {number} requirementId - 需求ID
     */
    editRequirement(requirementId) {
        console.log('[RequirementsTableManager] 编辑需求:', requirementId);

        const requirement = this.requirements.find(r => r.requirement_id === requirementId);
        if (!requirement) {
            console.error('[RequirementsTableManager] 未找到需求:', requirementId);
            return;
        }

        // 触发编辑事件，由外部处理
        window.dispatchEvent(new CustomEvent('requirementEditRequested', {
            detail: { requirement }
        }));
    }

    /**
     * 删除需求
     * @param {number} requirementId - 需求ID
     */
    async deleteRequirement(requirementId) {
        console.log('[RequirementsTableManager] 删除需求:', requirementId);

        // 确认对话框
        const confirmed = await window.modalManager.confirm(
            '确定要删除这条需求吗？此操作不可恢复。',
            '确认删除'
        );

        if (!confirmed) {
            return;
        }

        // 触发删除事件，由外部处理
        window.dispatchEvent(new CustomEvent('requirementDeleteRequested', {
            detail: { requirementId }
        }));
    }

    /**
     * 导出需求数据
     * @param {string} format - 导出格式 ('csv', 'json', 'excel')
     */
    exportRequirements(format = 'csv') {
        console.log('[RequirementsTableManager] 导出需求数据，格式:', format);

        switch (format) {
            case 'csv':
                this._exportToCSV();
                break;
            case 'json':
                this._exportToJSON();
                break;
            case 'excel':
                window.notifications.info('Excel导出功能即将推出');
                break;
            default:
                window.notifications.error('不支持的导出格式');
        }
    }

    /**
     * 清除所有过滤器
     */
    clearFilters() {
        this.currentFilters = {
            constraint_type: 'all',
            category: 'all',
            priority: 'all',
            search: ''
        };
        this.applyFilters();
        console.log('[RequirementsTableManager] 已清除所有过滤器');
    }

    // ============================================
    // 私有方法
    // ============================================

    /**
     * 渲染单行
     * @param {Object} req - 需求对象
     * @param {number} index - 索引
     * @returns {string} HTML字符串
     * @private
     */
    _renderRow(req, index) {
        const reqId = req.requirement_id || index;

        return `
            <tr data-req-id="${reqId}">
                <td class="text-center">${reqId}</td>
                <td>
                    <span class="badge bg-${this._getConstraintTypeColor(req.constraint_type)}">
                        ${this._getConstraintTypeLabel(req.constraint_type)}
                    </span>
                </td>
                <td>
                    <span class="badge bg-${this._getCategoryColor(req.category)}">
                        ${this._getCategoryLabel(req.category)}
                    </span>
                </td>
                <td>${req.subcategory || '-'}</td>
                <td class="requirement-detail">${this._escapeHtml(req.detail || req.summary || '')}</td>
                <td class="text-center">
                    <span class="badge bg-${this._getPriorityColor(req.priority)}">
                        ${this._getPriorityLabel(req.priority)}
                    </span>
                </td>
                <td class="text-center">
                    ${this._renderActionButtons(reqId)}
                </td>
            </tr>
        `;
    }

    /**
     * 渲染操作按钮
     * @param {number} reqId - 需求ID
     * @returns {string}
     * @private
     */
    _renderActionButtons(reqId) {
        let html = '';

        if (this.options.enableEdit) {
            html += `
                <button class="btn btn-sm btn-outline-primary me-1 edit-btn"
                        data-req-id="${reqId}"
                        title="编辑">
                    <i class="bi bi-pencil"></i>
                </button>
            `;
        }

        if (this.options.enableDelete) {
            html += `
                <button class="btn btn-sm btn-outline-danger delete-btn"
                        data-req-id="${reqId}"
                        title="删除">
                    <i class="bi bi-trash"></i>
                </button>
            `;
        }

        return html;
    }

    /**
     * 绑定行事件
     * @private
     */
    _bindRowEvents() {
        const tbody = document.getElementById(this.tableBodyId);
        if (!tbody) return;

        // 编辑按钮
        tbody.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reqId = parseInt(e.currentTarget.dataset.reqId);
                this.editRequirement(reqId);
            });
        });

        // 删除按钮
        tbody.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reqId = parseInt(e.currentTarget.dataset.reqId);
                this.deleteRequirement(reqId);
            });
        });
    }

    /**
     * 约束类型颜色
     * @private
     */
    _getConstraintTypeColor(type) {
        const colors = {
            'mandatory': 'danger',
            'optional': 'warning',
            'scoring': 'info'
        };
        return colors[type] || 'secondary';
    }

    /**
     * 约束类型标签
     * @private
     */
    _getConstraintTypeLabel(type) {
        const labels = {
            'mandatory': '强制性',
            'optional': '可选',
            'scoring': '加分项'
        };
        return labels[type] || type;
    }

    /**
     * 类别颜色
     * @private
     */
    _getCategoryColor(category) {
        const colors = {
            'qualification': 'primary',
            'technical': 'success',
            'commercial': 'warning',
            'service': 'info'
        };
        return colors[category] || 'secondary';
    }

    /**
     * 类别标签
     * @private
     */
    _getCategoryLabel(category) {
        const labels = {
            'qualification': '资质',
            'technical': '技术',
            'commercial': '商务',
            'service': '服务'
        };
        return labels[category] || category;
    }

    /**
     * 优先级颜色
     * @private
     */
    _getPriorityColor(priority) {
        const colors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'secondary'
        };
        return colors[priority] || 'secondary';
    }

    /**
     * 优先级标签
     * @private
     */
    _getPriorityLabel(priority) {
        const labels = {
            'high': '高',
            'medium': '中',
            'low': '低'
        };
        return labels[priority] || priority;
    }

    /**
     * HTML转义
     * @private
     */
    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 更新DOM元素内容
     * @private
     */
    _updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * 导出为CSV
     * @private
     */
    _exportToCSV() {
        // CSV标题行
        const headers = ['ID', '约束类型', '类别', '子类别', '详细内容', '摘要', '优先级', '来源位置'];
        const rows = [headers];

        // 数据行
        this.filteredRequirements.forEach(req => {
            rows.push([
                req.requirement_id,
                this._getConstraintTypeLabel(req.constraint_type),
                this._getCategoryLabel(req.category),
                req.subcategory || '',
                req.detail || '',
                req.summary || '',
                this._getPriorityLabel(req.priority),
                req.source_location || ''
            ]);
        });

        // 转换为CSV字符串
        const csv = rows.map(row =>
            row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
        ).join('\n');

        // 下载
        this._downloadFile(csv, 'requirements.csv', 'text/csv;charset=utf-8;');

        window.notifications.success('CSV导出成功');
    }

    /**
     * 导出为JSON
     * @private
     */
    _exportToJSON() {
        const json = JSON.stringify(this.filteredRequirements, null, 2);
        this._downloadFile(json, 'requirements.json', 'application/json');
        window.notifications.success('JSON导出成功');
    }

    /**
     * 下载文件
     * @private
     */
    _downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RequirementsTableManager;
}
