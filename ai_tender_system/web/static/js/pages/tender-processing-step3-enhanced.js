// ============================================
// Step 3 增强版: 详细需求提取和编辑
// ============================================

// ============================================
// 全局状态管理
// ============================================
let currentTaskId = null;
// 注意：currentProjectId已移除，统一使用HITLConfigManager.currentProjectId
let currentRequirements = [];
let currentChunks = [];

// ============================================
// 标签页管理
// ============================================
class TabManager {
    constructor() {
        this.tabs = {
            'detailed-requirements': this.loadDetailedRequirements.bind(this),
            'filtered-chunks': this.loadFilteredChunks.bind(this),
            'document-format': this.loadDocumentFormat.bind(this)
        };
        this.init();
    }

    init() {
        console.log('[TabManager] 初始化标签页管理器');
        // 监听所有标签页切换事件
        Object.keys(this.tabs).forEach(tabId => {
            const tabEl = document.querySelector(`button[data-bs-target="#${tabId}Panel"]`);
            if (tabEl) {
                tabEl.addEventListener('shown.bs.tab', (event) => {
                    console.log(`[TabManager] 切换到标签页: ${tabId}`);
                    this.tabs[tabId]();
                });
            }
        });
    }

    loadDetailedRequirements() {
        console.log('[TabManager] 加载详细需求');
        if (currentTaskId && HITLConfigManager.currentProjectId) {
            loadRequirements(currentTaskId, HITLConfigManager.currentProjectId);
        }
    }

    loadFilteredChunks() {
        console.log('[TabManager] 加载筛选后的段落');
        if (currentTaskId) {
            loadFilteredChunksData(currentTaskId);
        }
    }

    loadDocumentFormat() {
        console.log('[TabManager] 加载应答文件格式');
        if (currentTaskId) {
            loadResponseFileInfo(currentTaskId);
        }
    }
}

// ============================================
// 需求表格管理器
// ============================================
class RequirementsTableManager {
    constructor() {
        this.requirements = [];
        this.filteredRequirements = [];
        this.currentFilters = {
            constraint_type: 'all',
            category: 'all',
            priority: 'all',
            search: ''
        };
        this.editingRow = null;
    }

    setRequirements(requirements) {
        this.requirements = requirements;
        this.applyFilters();
    }

    applyFilters() {
        this.filteredRequirements = this.requirements.filter(req => {
            if (this.currentFilters.constraint_type !== 'all' && req.constraint_type !== this.currentFilters.constraint_type) {
                return false;
            }
            if (this.currentFilters.category !== 'all' && req.category !== this.currentFilters.category) {
                return false;
            }
            if (this.currentFilters.priority !== 'all' && req.priority !== this.currentFilters.priority) {
                return false;
            }
            if (this.currentFilters.search) {
                const searchLower = this.currentFilters.search.toLowerCase();
                return req.detail.toLowerCase().includes(searchLower) ||
                       (req.summary && req.summary.toLowerCase().includes(searchLower));
            }
            return true;
        });
        this.render();
    }

    render() {
        const tbody = document.getElementById('requirementsTableBody');
        if (!tbody) {
            console.error('[RequirementsTableManager] 未找到表格tbody');
            return;
        }

        if (this.filteredRequirements.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">
                        <i class="bi bi-inbox"></i> 暂无需求数据
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.filteredRequirements.map((req, index) => `
            <tr data-req-id="${req.requirement_id || index}">
                <td class="text-center">${req.requirement_id || (index + 1)}</td>
                <td><span class="badge bg-${this.getConstraintTypeColor(req.constraint_type)}">${this.getConstraintTypeLabel(req.constraint_type)}</span></td>
                <td><span class="badge bg-${this.getCategoryColor(req.category)}">${this.getCategoryLabel(req.category)}</span></td>
                <td>${req.subcategory || '-'}</td>
                <td class="requirement-detail">${this.escapeHtml(req.detail)}</td>
                <td class="text-center"><span class="badge bg-${this.getPriorityColor(req.priority)}">${this.getPriorityLabel(req.priority)}</span></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="requirementsTableManager.editRequirement(${req.requirement_id || index})" title="编辑">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="requirementsTableManager.deleteRequirement(${req.requirement_id || index})" title="删除">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        // 更新统计信息
        this.updateStats();
    }

    updateStats() {
        const totalEl = document.getElementById('totalRequirements');
        const mandatoryEl = document.getElementById('mandatoryCount');
        const optionalEl = document.getElementById('optionalCount');
        const scoringEl = document.getElementById('scoringCount');

        if (totalEl) totalEl.textContent = this.filteredRequirements.length;
        if (mandatoryEl) mandatoryEl.textContent = this.filteredRequirements.filter(r => r.constraint_type === 'mandatory').length;
        if (optionalEl) optionalEl.textContent = this.filteredRequirements.filter(r => r.constraint_type === 'optional').length;
        if (scoringEl) scoringEl.textContent = this.filteredRequirements.filter(r => r.constraint_type === 'scoring').length;
    }

    getConstraintTypeColor(type) {
        const colors = {
            'mandatory': 'danger',
            'optional': 'warning',
            'scoring': 'info'
        };
        return colors[type] || 'secondary';
    }

    getConstraintTypeLabel(type) {
        const labels = {
            'mandatory': '强制性',
            'optional': '可选',
            'scoring': '加分项'
        };
        return labels[type] || type;
    }

    getCategoryColor(category) {
        const colors = {
            'qualification': 'primary',
            'technical': 'success',
            'commercial': 'warning',
            'service': 'info'
        };
        return colors[category] || 'secondary';
    }

    getCategoryLabel(category) {
        const labels = {
            'qualification': '资质',
            'technical': '技术',
            'commercial': '商务',
            'service': '服务'
        };
        return labels[category] || category;
    }

    getPriorityColor(priority) {
        const colors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'secondary'
        };
        return colors[priority] || 'secondary';
    }

    getPriorityLabel(priority) {
        const labels = {
            'high': '高',
            'medium': '中',
            'low': '低'
        };
        return labels[priority] || priority;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    editRequirement(reqId) {
        console.log('[RequirementsTableManager] 编辑需求:', reqId);
        // TODO: 实现编辑功能
        alert('编辑功能开发中...');
    }

    deleteRequirement(reqId) {
        console.log('[RequirementsTableManager] 删除需求:', reqId);
        if (confirm('确定要删除这条需求吗？')) {
            // TODO: 实现删除功能
            alert('删除功能开发中...');
        }
    }
}

// 创建全局实例
const requirementsTableManager = new RequirementsTableManager();

// ============================================
// 数据加载函数
// ============================================

// 加载详细需求
async function loadRequirements(taskId, projectId) {
    console.log('[loadRequirements] 开始加载需求, taskId:', taskId, 'projectId:', projectId);

    const loadingEl = document.getElementById('requirementsExtractionProgress');
    const emptyStateEl = document.getElementById('eligibilityEmptyState');
    const checklistContainer = document.getElementById('eligibilityChecklistContainer');
    const tableContainer = document.getElementById('requirementsTableContainer');

    try {
        // 显示加载状态
        if (loadingEl) loadingEl.style.display = 'block';
        if (emptyStateEl) emptyStateEl.style.display = 'none';
        if (checklistContainer) checklistContainer.style.display = 'none';
        if (tableContainer) tableContainer.style.display = 'none';

        console.log('[loadRequirements] 发起API请求...');
        const response = await fetch(`/api/tender-processing/requirements/${projectId}`);
        const data = await response.json();
        console.log('[loadRequirements] API响应:', data);

        // 隐藏加载状态
        if (loadingEl) loadingEl.style.display = 'none';

        if (!response.ok) {
            throw new Error(data.error || '加载失败');
        }

        // 判断是从未提取过，还是提取了但为空
        if (!data.has_extracted || data.requirements.length === 0) {
            // 从未提取过或提取后为空
            console.log('[loadRequirements] 没有数据，显示空状态');
            if (emptyStateEl) emptyStateEl.style.display = 'block';
        } else {
            // 有数据 - 显示表格
            console.log('[loadRequirements] 加载到', data.requirements.length, '条需求');
            currentRequirements = data.requirements;

            // 显示表格容器
            if (tableContainer) {
                tableContainer.style.display = 'block';
                console.log('[loadRequirements] 显示表格容器');
            }

            // 使用 requirementsTableManager 渲染数据
            if (typeof requirementsTableManager !== 'undefined') {
                requirementsTableManager.setRequirements(data.requirements);
                console.log('[loadRequirements] 调用requirementsTableManager渲染数据');
            } else {
                console.warn('[loadRequirements] requirementsTableManager未定义');
            }

            // 更新Tab上的badge数字
            const eligBadge = document.getElementById('eligBadge');
            if (eligBadge) {
                eligBadge.textContent = data.requirements.length;
                console.log('[loadRequirements] 更新badge数字为', data.requirements.length);
            }
        }

    } catch (error) {
        console.error('[loadRequirements] 加载失败:', error);
        if (loadingEl) loadingEl.style.display = 'none';
        alert('加载需求失败: ' + error.message);
    }
}

// 提取详细需求
async function extractDetailedRequirements() {
    console.log('[extractDetailedRequirements] 开始提取需求');

    if (!currentTaskId || !HITLConfigManager.currentProjectId) {
        alert('缺少任务ID或项目ID');
        return;
    }

    const btn = document.getElementById('extractRequirementsBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>AI提取中...';
    }

    try {
        // 获取选择的模型
        const modelSelect = document.getElementById('hitlAiModel');
        const selectedModel = modelSelect ? modelSelect.value : 'gpt-4o-mini';

        console.log('[extractDetailedRequirements] 发起19条资格要求提取请求, 模型:', selectedModel);
        // 改为调用新的专用API
        const response = await fetch(`/api/tender-processing/extract-eligibility-requirements/${currentTaskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: selectedModel })
        });

        const data = await response.json();
        console.log('[extractDetailedRequirements] 提取结果:', data);

        if (!response.ok) {
            throw new Error(data.error || '提取失败');
        }

        // 提取成功，直接显示API返回的19条清单（不使用弹窗）
        console.log(`[extractDetailedRequirements] ✅ 提取成功！找到 ${data.found_count} 项，未找到 ${data.not_found_count} 项`);
        displayEligibilityChecklistFromAPI(data.checklist, data.found_count, data.not_found_count);

        // 在页面顶部显示成功提示（3秒后自动消失）
        showSuccessToast(`提取成功！找到 ${data.found_count} 项，未找到 ${data.not_found_count} 项`);

    } catch (error) {
        console.error('[extractDetailedRequirements] 提取失败:', error);
        // 在页面顶部显示错误提示
        showErrorToast('提取失败: ' + error.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic me-2"></i>AI提取资格要求';
        }
    }
}

// 加载筛选后的段落
async function loadFilteredChunksData(taskId) {
    console.log('[loadFilteredChunksData] 开始加载段落, taskId:', taskId);

    const loadingEl = document.getElementById('chunksLoading');
    const contentEl = document.getElementById('chunksContent');
    const emptyEl = document.getElementById('chunksEmpty');

    try {
        // 显示加载状态
        if (loadingEl) loadingEl.classList.remove('d-none');
        if (contentEl) contentEl.classList.add('d-none');
        if (emptyEl) emptyEl.classList.add('d-none');

        console.log('[loadFilteredChunksData] 发起API请求...');
        const response = await fetch(`/api/tender-processing/filtered-blocks/${taskId}`);
        const data = await response.json();
        console.log('[loadFilteredChunksData] API响应:', data);

        // 隐藏加载状态
        if (loadingEl) loadingEl.classList.add('d-none');

        if (!response.ok) {
            throw new Error(data.error || '加载失败');
        }

        // 后端返回的是 filtered_blocks，不是 chunks
        const blocks = data.filtered_blocks || [];

        if (blocks.length === 0) {
            console.log('[loadFilteredChunksData] 没有筛选后的段落');
            if (emptyEl) emptyEl.classList.remove('d-none');
        } else {
            console.log('[loadFilteredChunksData] 加载到', blocks.length, '个段落');
            currentChunks = blocks;
            renderFilteredChunks(blocks);
            if (contentEl) contentEl.classList.remove('d-none');
        }

    } catch (error) {
        console.error('[loadFilteredChunksData] 加载失败:', error);
        if (loadingEl) loadingEl.classList.add('d-none');
        alert('加载段落失败: ' + error.message);
    }
}

// 渲染筛选后的段落
function renderFilteredChunks(chunks) {
    const container = document.getElementById('chunksListContainer');
    if (!container) {
        console.error('[renderFilteredChunks] 未找到容器');
        return;
    }

    container.innerHTML = chunks.map((chunk, index) => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">段落 ${index + 1}</h6>
                    <span class="badge bg-${chunk.ai_decision === 'REQUIREMENT' ? 'success' : 'secondary'}">
                        ${chunk.ai_decision === 'REQUIREMENT' ? '需求' : '非需求'}
                    </span>
                </div>
                <p class="mb-2">${chunk.content}</p>
                ${chunk.ai_reasoning ? `<small class="text-muted">AI判断理由: ${chunk.ai_reasoning}</small>` : ''}
            </div>
        </div>
    `).join('');
}

// 通用文件信息加载函数
async function loadFileInfo(type, taskId) {
    const configs = {
        response: {
            api: `/api/tender-processing/response-file-info/${taskId}`,
            contentId: 'responseFileContent',
            noFileMessageId: 'noResponseFileMessage',
            title: '已保存应答文件模板',
            previewFunc: 'previewResponseFile',
            downloadFunc: 'downloadResponseFile',
            downloadText: '下载应答文件'
        },
        technical: {
            api: `/api/tender-processing/technical-file-info/${taskId}`,
            contentId: 'technicalFileContent',
            noFileMessageId: 'noTechnicalFileMessage',
            title: '已保存技术需求文件',
            previewFunc: 'previewTechnicalFile',
            downloadFunc: 'downloadTechnicalFile',
            downloadText: '下载技术文件'
        }
    };

    const config = configs[type];
    if (!config) {
        console.error(`[loadFileInfo] 未知的文件类型: ${type}`);
        return;
    }

    console.log(`[loadFileInfo] 开始加载${type}文件, taskId:`, taskId);
    try {
        const response = await fetch(config.api);
        const data = await response.json();
        console.log(`[loadFileInfo] ${type}文件API响应:`, data);

        const noFileMessage = document.getElementById(config.noFileMessageId);
        const fileContent = document.getElementById(config.contentId);

        if (data.success && data.has_file) {
            const fileSizeKB = (data.file_size / 1024).toFixed(2);
            const savedDate = new Date(data.saved_at).toLocaleString('zh-CN');

            const htmlContent = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>
                    <strong>${config.title}</strong>
                    <div class="mt-3">
                        <p class="mb-2"><strong>文件名:</strong> ${data.filename}</p>
                        <p class="mb-2"><strong>文件大小:</strong> ${fileSizeKB} KB</p>
                        <p class="mb-3"><strong>保存时间:</strong> ${savedDate}</p>
                        <button class="btn btn-outline-secondary btn-sm me-2" onclick="${config.previewFunc}('${taskId}')">
                            <i class="bi bi-eye me-2"></i>预览
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="${config.downloadFunc}('${taskId}')">
                            <i class="bi bi-download me-2"></i>${config.downloadText}
                        </button>
                    </div>
                </div>
            `;

            if (fileContent) {
                fileContent.innerHTML = htmlContent;
                console.log(`[loadFileInfo] ${type}文件内容已更新`);
            }
        } else {
            // 显示空状态
            if (noFileMessage) {
                noFileMessage.style.display = 'block';
            }
        }
    } catch (error) {
        console.error(`[loadFileInfo] 加载${type}文件失败:`, error);
    }
}

// 保持向后兼容
async function loadResponseFileInfo(taskId) {
    return loadFileInfo('response', taskId);
}

// 预览应答文件
function previewResponseFile(taskId) {
    console.log('[previewResponseFile] 预览文件, taskId:', taskId);

    const previewUrl = `/api/tender-processing/preview-response-file/${taskId}`;

    // 显示加载状态
    const previewContent = document.getElementById('documentPreviewContent');
    if (previewContent) {
        previewContent.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在加载文档...</p></div>';
    }

    // 显示预览模态框
    const previewModal = new bootstrap.Modal(document.getElementById('documentPreviewModal'));
    previewModal.show();

    // 使用mammoth.js在前端直接转换Word文档
    fetch(previewUrl)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            // 使用mammoth转换Word为HTML
            return mammoth.convertToHtml({arrayBuffer: arrayBuffer});
        })
        .then(result => {
            if (previewContent) {
                const html = result.value || '<p>文档内容为空</p>';
                // 添加样式包装
                previewContent.innerHTML = `
                    <style>
                        #documentPreviewContent {
                            font-family: 'Microsoft YaHei', sans-serif;
                            line-height: 1.8;
                            padding: 20px;
                        }
                        #documentPreviewContent p { margin: 10px 0; }
                        #documentPreviewContent h1, #documentPreviewContent h2, #documentPreviewContent h3 {
                            color: #333;
                            margin: 20px 0 10px 0;
                        }
                        #documentPreviewContent table {
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }
                        #documentPreviewContent table td, #documentPreviewContent table th {
                            border: 1px solid #ddd;
                            padding: 8px;
                        }
                        #documentPreviewContent table th {
                            background-color: #f2f2f2;
                        }
                    </style>
                    <div>${html}</div>
                `;

                // 显示转换警告信息(如果有)
                if (result.messages && result.messages.length > 0) {
                    console.log('Mammoth转换消息:', result.messages);
                }
            }
        })
        .catch(error => {
            console.error('预览失败:', error);
            if (previewContent) {
                previewContent.innerHTML = '<div class="text-center text-danger"><i class="bi bi-exclamation-triangle fs-1"></i><p class="mt-2">预览失败，请尝试下载文档</p></div>';
            }
        });
}

// 下载应答文件
function downloadResponseFile(taskId) {
    console.log('[downloadResponseFile] 下载文件, taskId:', taskId);
    window.location.href = `/api/tender-processing/download-response-file/${taskId}`;
}

// ============================================
// 过滤器函数
// ============================================
function filterByConstraintType(type) {
    requirementsTableManager.currentFilters.constraint_type = type;
    requirementsTableManager.applyFilters();
}

function filterByCategory(category) {
    requirementsTableManager.currentFilters.category = category;
    requirementsTableManager.applyFilters();
}

function filterByPriority(priority) {
    requirementsTableManager.currentFilters.priority = priority;
    requirementsTableManager.applyFilters();
}

function searchRequirements(query) {
    requirementsTableManager.currentFilters.search = query;
    requirementsTableManager.applyFilters();
}

// ============================================
// 导出函数
// ============================================
function exportRequirements() {
    console.log('[exportRequirements] 导出需求');
    if (currentRequirements.length === 0) {
        alert('没有可导出的需求');
        return;
    }

    // TODO: 实现导出功能
    alert('导出功能开发中...');
}

function exportFinalResults() {
    console.log('[exportFinalResults] 导出最终结果');
    // TODO: 实现导出功能
    alert('导出功能开发中...');
}

// ============================================
// 进入步骤3
// ============================================

// 全局变量存储当前任务ID
let currentHitlTaskId = null;

function proceedToStep3(taskId, projectId) {
    console.log('[proceedToStep3] 进入步骤3，任务ID:', taskId, '项目ID:', projectId);

    // 保存taskId到全局变量
    currentHitlTaskId = taskId;
    currentTaskId = taskId;
    HITLConfigManager.currentProjectId = projectId;

    // 隐藏步骤1和步骤2，显示步骤3（使用正确的ID）
    const step1Section = document.getElementById('chapterSelectionSection');
    const step2Section = document.getElementById('step2Section');
    const step3Section = document.getElementById('step3Section');

    console.log('[proceedToStep3] DOM元素查找结果:');
    console.log('  - chapterSelectionSection:', step1Section);
    console.log('  - step2Section:', step2Section);
    console.log('  - step3Section:', step3Section);

    if (step1Section) {
        step1Section.style.display = 'none';
        console.log('[proceedToStep3] 隐藏步骤1');
    }
    if (step2Section) {
        step2Section.style.display = 'none';
        console.log('[proceedToStep3] 隐藏步骤2');
    }
    if (step3Section) {
        step3Section.style.display = 'block';
        console.log('[proceedToStep3] 显示步骤3');
    } else {
        console.error('[proceedToStep3] 步骤3元素不存在！');
    }

    console.log('[proceedToStep3] 页面切换完成，开始加载数据');

    // 初始化标签页管理器
    new TabManager();

    console.log('[proceedToStep3] 初始化完成，Bootstrap会处理tab切换和数据加载');
}

// ============================================
// 返回步骤2
// ============================================
function backToStep2() {
    console.log('[backToStep2] 返回步骤2');

    const step1Section = document.getElementById('chapterSelectionSection');
    const step2Section = document.getElementById('step2Section');
    const step3Section = document.getElementById('step3Section');

    if (step1Section) step1Section.style.display = 'none';
    if (step2Section) step2Section.style.display = 'block';
    if (step3Section) step3Section.style.display = 'none';
}

// ============================================
// 页面初始化
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DOMContentLoaded] 页面初始化');

    // 绑定提取按钮
    const extractBtn = document.getElementById('extractRequirementsBtn');
    if (extractBtn) {
        extractBtn.addEventListener('click', extractDetailedRequirements);
    }

    // 绑定导出按钮
    const exportBtn = document.getElementById('exportRequirementsBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportRequirements);
    }

    // 绑定搜索框
    const searchInput = document.getElementById('requirementsSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => searchRequirements(e.target.value));
    }

    // 绑定AI提取基本信息按钮
    const extractBasicInfoBtn = document.getElementById('extractBasicInfoBtn');
    if (extractBasicInfoBtn) {
        extractBasicInfoBtn.addEventListener('click', extractBasicInfo);
    }

    // 绑定保存基本信息按钮
    const saveBasicInfoBtn = document.getElementById('saveBasicInfoBtn');
    if (saveBasicInfoBtn) {
        saveBasicInfoBtn.addEventListener('click', saveBasicInfo);
    }

    // 绑定保存并完成按钮
    const saveAndCompleteBtn = document.getElementById('saveAndCompleteBtn');
    if (saveAndCompleteBtn) {
        saveAndCompleteBtn.addEventListener('click', saveAndComplete);
    }

    console.log('[DOMContentLoaded] 初始化完成');
});

// ============================================
// AI提取基本信息
// ============================================
async function extractBasicInfo() {
    console.log('[extractBasicInfo] 开始AI提取基本信息');

    if (!currentTaskId) {
        alert('缺少任务ID');
        return;
    }

    const btn = document.getElementById('extractBasicInfoBtn');
    const form = document.getElementById('basicInfoForm');
    const loading = document.getElementById('basicInfoLoading');

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>AI提取中...';
    }

    if (form) form.style.display = 'none';
    if (loading) loading.style.display = 'block';

    try {
        const response = await fetch(`/api/tender-processing/extract-basic-info/${currentTaskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (data.success && data.data) {
            // 填充表单字段
            const info = data.data;
            if (info.project_name) document.getElementById('projectName').value = info.project_name;
            if (info.project_number) document.getElementById('projectNumber').value = info.project_number;
            if (info.tender_party) document.getElementById('tenderParty').value = info.tender_party;
            if (info.tender_agent) document.getElementById('tenderAgent').value = info.tender_agent;
            if (info.tender_method) document.getElementById('tenderMethod').value = info.tender_method;
            if (info.tender_location) document.getElementById('tenderLocation').value = info.tender_location;
            if (info.tender_deadline) document.getElementById('tenderDeadline').value = info.tender_deadline;
            if (info.winner_count) document.getElementById('winnerCount').value = info.winner_count;

            showSuccessToast('AI提取基本信息完成!');
        } else {
            throw new Error(data.error || '提取失败');
        }
    } catch (error) {
        console.error('[extractBasicInfo] 提取失败:', error);
        alert('提取失败: ' + error.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-magic me-2"></i>AI提取基本信息';
        }
        if (form) form.style.display = 'block';
        if (loading) loading.style.display = 'none';
    }
}

// ============================================
// 保存基本信息 - 统一保存到 tender_projects 表
// ============================================

// 防重复提交标志
let isSavingBasicInfo = false;

async function saveBasicInfo() {
    console.log('[saveBasicInfo] 开始保存基本信息');

    // 【新增】防止重复提交
    if (isSavingBasicInfo) {
        console.warn('[saveBasicInfo] 正在保存中，忽略重复请求');
        return;
    }

    // 获取公司和项目配置
    const config = HITLConfigManager.getConfig();

    if (!config.companyId) {
        showErrorToast('请先选择应答公司');
        return;
    }

    const btn = document.getElementById('saveBasicInfoBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>保存中...';
    }

    // 【新增】设置保存中标志
    isSavingBasicInfo = true;

    try {
        // 收集基本信息
        const basicInfo = {
            project_name: document.getElementById('projectName')?.value || '',
            project_number: document.getElementById('projectNumber')?.value || '',
            tenderer: document.getElementById('tenderParty')?.value || '',
            agency: document.getElementById('tenderAgent')?.value || '',
            bidding_method: document.getElementById('tenderMethod')?.value || '',
            bidding_location: document.getElementById('tenderLocation')?.value || '',
            bidding_time: document.getElementById('tenderDeadline')?.value || '',
            winner_count: document.getElementById('winnerCount')?.value || '',
            company_id: config.companyId,
            tender_document_path: '',  // HITL从章节选择开始,无上传文件路径
            original_filename: ''
        };

        console.log('[saveBasicInfo] 基本信息:', basicInfo);
        console.log('[saveBasicInfo] 当前项目ID:', HITLConfigManager.currentProjectId);

        // 判断是创建还是更新
        const isUpdate = HITLConfigManager.currentProjectId !== null && HITLConfigManager.currentProjectId !== '';
        const url = isUpdate
            ? `/api/tender-projects/${HITLConfigManager.currentProjectId}`
            : '/api/tender-projects';
        const method = isUpdate ? 'PUT' : 'POST';

        console.log(`[saveBasicInfo] 执行${isUpdate ? '更新' : '创建'}操作，URL: ${url}`);

        // 发送请求
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(basicInfo)
        });

        const data = await response.json();

        if (data.success) {
            // 保存/更新项目ID
            if (!isUpdate && data.project_id) {
                HITLConfigManager.currentProjectId = data.project_id;
                console.log('[saveBasicInfo] 新项目已创建，ID:', HITLConfigManager.currentProjectId);
            }

            showSuccessToast(isUpdate ? '项目更新成功' : '项目创建成功');

            // 刷新项目列表
            await HITLConfigManager.loadProjects();
            const projectSelect = document.getElementById('hitlProjectSelect');
            if (projectSelect && HITLConfigManager.currentProjectId) {
                projectSelect.value = HITLConfigManager.currentProjectId;
            }

            // 更新按钮状态
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-lg me-2"></i>已保存';
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-success');
            }
        } else {
            throw new Error(data.message || '保存失败');
        }

    } catch (error) {
        console.error('[saveBasicInfo] 保存失败:', error);
        showErrorToast('保存失败: ' + error.message);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-save me-2"></i>保存基本信息';
        }
    } finally {
        // 【新增】清除保存中标志
        isSavingBasicInfo = false;
    }
}

// ============================================
// 保存并完成 - 保存完整项目数据到 tender_projects 表
// ============================================

// 防重复提交标志
let isSavingComplete = false;

async function saveAndComplete() {
    console.log('[saveAndComplete] 开始保存并完成');

    // 【新增】防止重复提交
    if (isSavingComplete) {
        console.warn('[saveAndComplete] 正在保存中，忽略重复请求');
        return;
    }

    // 获取公司和项目配置
    const config = HITLConfigManager.getConfig();

    if (!config.companyId) {
        showErrorToast('请先选择应答公司');
        return;
    }

    const btn = document.getElementById('saveAndCompleteBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>保存中...';
    }

    // 【新增】设置保存中标志
    isSavingComplete = true;

    try {
        // 1. 先保存基本信息(会创建或更新项目)
        await saveBasicInfo();

        // 2. 收集并同步资格要求、技术需求、评分办法等数据
        console.log('[saveAndComplete] 开始收集各类数据...');

        const qualificationsData = await collectQualificationsData();
        const technicalData = await collectTechnicalData();
        const scoringData = await collectScoringData();

        console.log('[saveAndComplete] 数据收集完成:', {
            qualifications: Object.keys(qualificationsData).length,
            technical: Object.keys(technicalData).length,
            scoring: Object.keys(scoringData).length
        });

        // 3. 更新项目表，同步汇总数据
        if (HITLConfigManager.currentProjectId) {
            const updatePayload = {
                status: 'active'  // 标记为进行中
            };

            // 只有当数据不为空时才添加到payload
            if (Object.keys(qualificationsData).length > 0) {
                updatePayload.qualifications_data = qualificationsData;
            }
            if (Object.keys(scoringData).length > 0) {
                updatePayload.scoring_data = scoringData;
            }

            console.log('[saveAndComplete] 准备更新项目数据:', updatePayload);

            const updateResponse = await fetch(`/api/tender-projects/${HITLConfigManager.currentProjectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatePayload)
            });

            const updateData = await updateResponse.json();
            if (!updateData.success) {
                console.warn('[saveAndComplete] 更新项目数据失败:', updateData.message);
            } else {
                console.log('[saveAndComplete] 项目数据更新成功');
            }
        }

        showSuccessToast('✅ 所有数据已保存，HITL流程完成！');
        if (btn) {
            btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已完成';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-secondary');
        }

    } catch (error) {
        console.error('[saveAndComplete] 保存失败:', error);
        showErrorToast('保存失败: ' + error.message);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>保存并完成';
        }
    } finally {
        // 【新增】清除保存中标志
        isSavingComplete = false;
    }
}

// ============================================
// 19条供应商资格要求清单
// ============================================
const ELIGIBILITY_CHECKLIST = [
    {id: 1, name: "营业执照信息", keywords: ["营业执照", "注册", "法人", "注册资金", "注册资本", "注册时间", "成立时间"]},
    {id: 2, name: "财务要求", keywords: ["审计报告", "财务报表", "财务", "财务会计制度"]},
    {id: 3, name: "依法纳税", keywords: ["增值税", "纳税", "税收", "税务"]},
    {id: 4, name: "缴纳社保", keywords: ["社保", "社会保险", "缴费人数", "缴纳人数"]},
    {id: 5, name: "失信被执行人", keywords: ["失信被执行人", "失信名单"]},
    {id: 6, name: "信用中国：严重违法失信", keywords: ["信用中国", "严重违法失信", "违法失信"]},
    {id: 7, name: "严重违法失信行为记录名单", keywords: ["违法失信", "记录名单", "失信行为"]},
    {id: 8, name: "信用中国：重大税收违法", keywords: ["重大税收违法", "税收违法失信"]},
    {id: 9, name: "采购人黑名单", keywords: ["黑名单", "采购人"]},
    {id: 10, name: "承诺函", keywords: ["承诺函", "承诺书"]},
    {id: 11, name: "营业办公场所房产证明", keywords: ["房产", "办公场所", "经营场所", "房产证明"]},
    {id: 12, name: "业绩案例要求", keywords: ["业绩", "类似项目", "同类项目", "项目经验"]},
    {id: 13, name: "保证金要求", keywords: ["保证金", "投标保证金"]},
    {id: 14, name: "增值电信业务许可证", keywords: ["增值电信业务许可证", "ICP许可证", "IDC许可证", "ISP许可证", "CDN许可证", "增值电信"]},
    {id: 15, name: "基础电信业务许可证", keywords: ["基础电信业务许可证", "电信业务经营许可证", "基础电信"]},
    {id: 16, name: "ISO9001质量管理体系认证", keywords: ["ISO9001", "ISO 9001", "质量管理体系", "质量认证", "GB/T19001", "质量体系认证"]},
    {id: 17, name: "ISO20000信息技术服务管理体系认证", keywords: ["ISO20000", "ISO 20000", "信息技术服务管理", "IT服务管理", "ISO/IEC 20000", "信息技术服务"]},
    {id: 18, name: "ISO27001信息安全管理体系认证", keywords: ["ISO27001", "ISO 27001", "信息安全管理", "信息安全认证", "ISO/IEC 27001", "信息安全体系"]},
    {id: 19, name: "等保三级认证", keywords: ["等保三级", "等级保护三级", "信息安全等级保护", "等保", "三级等保", "等级保护备案"]}
];

// 显示19条资格要求清单
function displayEligibilityChecklist(requirements) {
    console.log('[displayEligibilityChecklist] 显示资格清单, 需求数量:', requirements.length);

    // 过滤出资格类需求
    const qualificationReqs = requirements.filter(req => req.category === 'qualification');
    console.log('[displayEligibilityChecklist] 资格类需求数量:', qualificationReqs.length);

    // 初始化19条清单数据
    const checklistData = ELIGIBILITY_CHECKLIST.map(item => ({
        ...item,
        found: false,
        requirements: []
    }));

    // 将提取的需求匹配到19条清单
    qualificationReqs.forEach(req => {
        const detail = (req.detail || '').toLowerCase();
        const summary = (req.summary || '').toLowerCase();
        const subcategory = (req.subcategory || '').toLowerCase();
        const fullText = `${detail} ${summary} ${subcategory}`;

        // 遍历13条清单，找到匹配的条目
        for (let i = 0; i < checklistData.length; i++) {
            const item = checklistData[i];
            const matched = item.keywords.some(keyword =>
                fullText.includes(keyword.toLowerCase())
            );

            if (matched) {
                item.found = true;
                item.requirements.push(req);
                break; // 匹配到第一个就跳出
            }
        }
    });

    // 统计
    const foundCount = checklistData.filter(item => item.found).length;
    const notFoundCount = 19 - foundCount;

    // 更新统计显示
    const foundCountEl = document.getElementById('eligFoundCount');
    const notFoundCountEl = document.getElementById('eligNotFoundCount');
    if (foundCountEl) foundCountEl.textContent = foundCount;
    if (notFoundCountEl) notFoundCountEl.textContent = notFoundCount;

    // 生成清单HTML
    const container = document.getElementById('eligibilityChecklistItems');
    if (!container) {
        console.warn('[displayEligibilityChecklist] 找不到清单项容器');
        return;
    }

    let html = '';
    checklistData.forEach(item => {
        const icon = item.found ? '✅' : '⚠️';
        const statusClass = item.found ? 'found' : 'not-found';

        html += `
            <div class="checklist-item ${statusClass} mb-3">
                <div class="d-flex align-items-start">
                    <span class="me-2" style="font-size: 1.2em;">${icon}</span>
                    <div class="flex-grow-1">
                        <div class="fw-bold mb-1">
                            <span class="badge bg-secondary me-2">${item.id}</span>
                            ${item.name}
                        </div>
        `;

        if (item.found && item.requirements.length > 0) {
            html += '<div class="ms-3">';
            item.requirements.forEach(req => {
                // 使用新的格式化函数处理detail字段，支持展开/收起
                const formattedDetail = req.summary && req.detail !== req.summary
                    ? `<div class="small text-secondary mt-1">${formatDetailTextWithToggle(req.detail, 150)}</div>`
                    : '';

                html += `
                    <div class="mb-2 p-2 bg-light rounded">
                        <div class="small text-muted mb-1">
                            <span class="badge bg-${getConstraintTypeBadge(req.constraint_type)}">${getConstraintTypeLabel(req.constraint_type)}</span>
                            ${req.subcategory ? '<span class="ms-2">' + req.subcategory + '</span>' : ''}
                        </div>
                        <div class="fw-medium">${req.summary || formatDetailTextWithToggle(req.detail, 150)}</div>
                        ${formattedDetail}
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<div class="ms-3 text-muted small">（未在文档中找到相关要求）</div>';
        }

        html += `
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    // 隐藏空状态，显示清单容器
    const emptyState = document.getElementById('eligibilityEmptyState');
    const checklistContainer = document.getElementById('eligibilityChecklistContainer');
    if (emptyState) emptyState.style.display = 'none';
    if (checklistContainer) checklistContainer.style.display = 'block';

    console.log('[displayEligibilityChecklist] 清单显示完成');
}

// 显示API返回的19条资格要求清单（新版本，使用API结构化数据）
function displayEligibilityChecklistFromAPI(checklist, foundCount, notFoundCount) {
    console.log('[displayEligibilityChecklistFromAPI] 显示API清单, 找到:', foundCount, '未找到:', notFoundCount);

    // 更新统计显示
    const foundCountEl = document.getElementById('eligFoundCount');
    const notFoundCountEl = document.getElementById('eligNotFoundCount');
    if (foundCountEl) foundCountEl.textContent = foundCount;
    if (notFoundCountEl) notFoundCountEl.textContent = notFoundCount;

    // 生成清单HTML
    const container = document.getElementById('eligibilityChecklistItems');
    if (!container) {
        console.warn('[displayEligibilityChecklistFromAPI] 找不到清单项容器');
        return;
    }

    let html = '';
    checklist.forEach(item => {
        const icon = item.found ? '✅' : '⚠️';
        const statusClass = item.found ? 'found' : 'not-found';

        html += `
            <div class="checklist-item ${statusClass} mb-3">
                <div class="d-flex align-items-start">
                    <span class="me-2" style="font-size: 1.2em;">${icon}</span>
                    <div class="flex-grow-1">
                        <div class="fw-bold mb-1">
                            <span class="badge bg-secondary me-2">${item.checklist_id}</span>
                            ${item.checklist_name}
                        </div>
        `;

        if (item.found && item.requirements && item.requirements.length > 0) {
            html += '<div class="ms-3">';
            item.requirements.forEach(req => {
                // 使用新的格式化函数处理detail字段，支持展开/收起
                const formattedDetail = req.summary && req.detail && req.detail !== req.summary
                    ? `<div class="small text-secondary mt-1">${formatDetailTextWithToggle(req.detail, 150)}</div>`
                    : '';

                html += `
                    <div class="mb-2 p-2 bg-light rounded">
                        <div class="small text-muted mb-1">
                            <span class="badge bg-${getConstraintTypeBadge(req.constraint_type)}">${getConstraintTypeLabel(req.constraint_type)}</span>
                            ${req.source_location ? '<span class="ms-2 text-muted">来源: ' + req.source_location + '</span>' : ''}
                        </div>
                        <div class="fw-medium">${req.summary || formatDetailTextWithToggle(req.detail, 150)}</div>
                        ${formattedDetail}
                        ${req.extraction_confidence ? '<div class="small text-muted mt-1">置信度: ' + (req.extraction_confidence * 100).toFixed(0) + '%</div>' : ''}
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<div class="ms-3 text-muted small">（未在文档中找到相关要求）</div>';
        }

        html += `
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    // 隐藏空状态，显示清单容器
    const emptyState = document.getElementById('eligibilityEmptyState');
    const checklistContainer = document.getElementById('eligibilityChecklistContainer');
    if (emptyState) emptyState.style.display = 'none';
    if (checklistContainer) checklistContainer.style.display = 'block';

    console.log('[displayEligibilityChecklistFromAPI] 清单显示完成');
}

// 辅助函数：获取约束类型徽章颜色
function getConstraintTypeBadge(type) {
    const badges = {
        'mandatory': 'danger',
        'optional': 'info',
        'scoring': 'success'
    };
    return badges[type] || 'secondary';
}

// 辅助函数：获取约束类型标签
function getConstraintTypeLabel(type) {
    const labels = {
        'mandatory': '强制性',
        'optional': '可选',
        'scoring': '加分项'
    };
    return labels[type] || type;
}

// ============================================
// 长文本展开/收起功能
// ============================================

/**
 * 格式化detail文本，对于长文本添加展开/收起功能
 * @param {string} text - 要显示的文本
 * @param {number} maxLength - 默认显示的最大长度（默认150字符）
 * @returns {string} 格式化后的HTML
 */
function formatDetailTextWithToggle(text, maxLength = 150) {
    if (!text) return '';

    // HTML转义
    const escapeHtml = (str) => {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    };

    const escapedText = escapeHtml(text);

    // 如果文本长度小于等于最大长度，直接返回
    if (text.length <= maxLength) {
        return escapedText;
    }

    // 生成唯一ID
    const uniqueId = 'detail_' + Math.random().toString(36).substr(2, 9);

    // 智能截断：优先在句号、分号等强分隔符处截断
    let shortText = text.substring( 0, maxLength);

    // 定义标点符号优先级（从高到低）
    const punctuations = [
        { char: '。', priority: 5 },   // 句号 - 最高优先级
        { char: '；', priority: 4 },   // 中文分号
        { char: ';', priority: 4 },    // 英文分号
        { char: '！', priority: 4 },   // 感叹号
        { char: '？', priority: 4 },   // 问号
        { char: '，', priority: 3 },   // 中文逗号
        { char: ',', priority: 3 },    // 英文逗号
        { char: '、', priority: 2 },   // 顿号
        { char: '）', priority: 2 },   // 右括号
        { char: ')', priority: 2 }     // 英文右括号
    ];

    // 查找所有标点符号的位置
    let bestCutPoint = -1;
    let bestPriority = 0;

    for (const punct of punctuations) {
        const pos = shortText.lastIndexOf(punct.char);
        // 如果找到标点，且在合理范围内（至少显示50%的内容）
        if (pos > maxLength * 0.5 && punct.priority > bestPriority) {
            bestCutPoint = pos;
            bestPriority = punct.priority;
        }
    }

    // 如果找到了合适的截断点，在标点符号之后截断
    if (bestCutPoint > 0) {
        shortText = text.substring(0, bestCutPoint + 1);
    }

    const escapedShortText = escapeHtml(shortText);

    return `
        <span id="${uniqueId}_short">
            ${escapedShortText}...
            <a href="#" class="text-primary ms-1 small" onclick="toggleDetailText('${uniqueId}', event)" style="text-decoration:none;">
                <i class="bi bi-chevron-down"></i> 展开
            </a>
        </span>
        <span id="${uniqueId}_full" style="display:none;">
            ${escapedText}
            <a href="#" class="text-primary ms-1 small" onclick="toggleDetailText('${uniqueId}', event)" style="text-decoration:none;">
                <i class="bi bi-chevron-up"></i> 收起
            </a>
        </span>
    `;
}

/**
 * 切换detail文本的展开/收起状态
 * @param {string} id - 元素ID前缀
 * @param {Event} event - 点击事件
 */
function toggleDetailText(id, event) {
    event.preventDefault();
    const shortEl = document.getElementById(id + '_short');
    const fullEl = document.getElementById(id + '_full');

    if (!shortEl || !fullEl) {
        console.error('[toggleDetailText] 找不到元素:', id);
        return;
    }

    if (shortEl.style.display === 'none') {
        // 收起
        shortEl.style.display = '';
        fullEl.style.display = 'none';
    } else {
        // 展开
        shortEl.style.display = 'none';
        fullEl.style.display = '';
    }
}

// ============================================
// Toast 提示功能（替代alert弹窗）
// ============================================

/**
 * 显示成功提示（绿色toast，3秒后自动消失）
 * @param {string} message - 提示消息
 */
function showSuccessToast(message) {
    showToast(message, 'success');
}

/**
 * 显示错误提示（红色toast，5秒后自动消失）
 * @param {string} message - 错误消息
 */
function showErrorToast(message) {
    showToast(message, 'error', 5000);
}

/**
 * 显示提示消息（通用函数）
 * @param {string} message - 提示消息
 * @param {string} type - 类型：'success', 'error', 'info', 'warning'
 * @param {number} duration - 显示时长（毫秒），默认3000ms
 */
function showToast(message, type = 'info', duration = 3000) {
    // 创建toast容器（如果不存在）
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(toastContainer);
    }

    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = 'toast-message';

    // 根据类型设置样式和图标
    let bgColor, icon;
    switch (type) {
        case 'success':
            bgColor = '#28a745';
            icon = '<i class="bi bi-check-circle-fill me-2"></i>';
            break;
        case 'error':
            bgColor = '#dc3545';
            icon = '<i class="bi bi-exclamation-circle-fill me-2"></i>';
            break;
        case 'warning':
            bgColor = '#ffc107';
            icon = '<i class="bi bi-exclamation-triangle-fill me-2"></i>';
            break;
        default:
            bgColor = '#17a2b8';
            icon = '<i class="bi bi-info-circle-fill me-2"></i>';
    }

    toast.style.cssText = `
        background-color: ${bgColor};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        animation: slideIn 0.3s ease-out;
        font-size: 14px;
        line-height: 1.5;
    `;

    toast.innerHTML = `${icon}<span>${message}</span>`;

    // 添加CSS动画（如果还没有添加）
    if (!document.getElementById('toastAnimationStyles')) {
        const style = document.createElement('style');
        style.id = 'toastAnimationStyles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // 添加到容器
    toastContainer.appendChild(toast);

    // 自动移除
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            // 如果容器为空，移除容器
            if (toastContainer.children.length === 0) {
                toastContainer.remove();
            }
        }, 300);
    }, duration);
}

// ============================================
// 章节选择通用功能（支持多个标签页复用）
// ============================================

// 章节选择配置（支持应答文件格式和技术需求两种类型）
const CHAPTER_SELECTION_CONFIG = {
    'response': {
        prefix: 'inline',
        confirmBtnId: 'confirmInlineSaveResponseFileBtn',
        apiSave: '/api/tender-processing/save-response-file',
        apiInfo: '/api/tender-processing/response-file-info',
        apiDownload: '/api/tender-processing/download-response-file',
        apiPreview: '/api/tender-processing/preview-response-file',
        fileTypeName: '应答文件',
        contentId: 'responseFileContent',
        selectionAreaId: 'inlineChapterSelectionArea',
        noFileMessageId: 'noResponseFileMessage'
    },
    'technical': {
        prefix: 'technical',
        confirmBtnId: 'confirmTechnicalSaveBtn',
        apiSave: '/api/tender-processing/save-technical-chapters',
        apiInfo: '/api/tender-processing/technical-file-info',
        apiDownload: '/api/tender-processing/download-technical-file',
        apiPreview: '/api/tender-processing/preview-technical-file',
        fileTypeName: '技术需求',
        contentId: 'technicalFileContent',
        selectionAreaId: 'technicalChapterSelectionArea',
        noFileMessageId: 'noTechnicalFileMessage'
    }
};

// 使用Map存储不同类型的选中状态和章节数据
const selectedChapterIdsMap = new Map();
const chaptersDataMap = new Map();

/**
 * 显示章节选择区域（通用函数）
 * @param {string} type - 类型：'response'（应答文件）或 'technical'（技术需求）
 */
async function showChapterSelection(type) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    console.log(`[showChapterSelection] 开始显示${config.fileTypeName}章节选择区域`);

    // 先尝试从步骤1获取章节数据
    let chaptersData = null;
    if (typeof chapterSelectionManager !== 'undefined' && chapterSelectionManager.chaptersData && chapterSelectionManager.chaptersData.length > 0) {
        console.log('[showChapterSelection] 从步骤1获取章节数据');
        chaptersData = chapterSelectionManager.chaptersData;
    } else {
        // 步骤1没有数据，尝试从API加载
        console.log('[showChapterSelection] 步骤1无数据，从API加载');
        if (!currentTaskId) {
            showErrorToast('任务ID不存在，请刷新页面重试');
            return;
        }

        try {
            chaptersData = await loadChaptersFromAPI(currentTaskId);
            if (!chaptersData || chaptersData.length === 0) {
                showErrorToast('未找到章节数据，请先在步骤1解析文档');
                return;
            }
        } catch (error) {
            showErrorToast(error.message || '加载章节数据失败');
            return;
        }
    }

    // 初始化并重置选中状态
    if (!selectedChapterIdsMap.has(type)) {
        selectedChapterIdsMap.set(type, new Set());
    }
    selectedChapterIdsMap.get(type).clear();

    // 渲染章节树
    renderChapterTree(type, chaptersData);

    // 更新统计信息
    updateStatistics(type, chaptersData);

    // 隐藏文件信息区域，显示章节选择区域
    const fileContent = document.getElementById(config.contentId);
    const selectionArea = document.getElementById(config.selectionAreaId);
    if (fileContent) fileContent.style.display = 'none';
    if (selectionArea) selectionArea.style.display = 'block';

    console.log(`[showChapterSelection] ${config.fileTypeName}章节选择区域已显示`);
}

// 向后兼容：保留旧函数名作为别名
async function showChapterSelectionModalForResponseFile() {
    return showChapterSelection('response');
}

/**
 * 从API加载章节数据
 */
async function loadChaptersFromAPI(taskId) {
    console.log('[loadChaptersFromAPI] 开始从API加载章节数据');

    const response = await fetch(`/api/tender-processing/chapters/${taskId}`);
    const data = await response.json();

    if (!response.ok || !data.success) {
        throw new Error(data.error || '加载失败');
    }

    console.log('[loadChaptersFromAPI] 成功加载', data.chapters.length, '个章节');
    return data.chapters;
}

/**
 * 在页面内渲染章节树（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 * @param {Array} chaptersData - 章节数据
 */
function renderChapterTree(type, chaptersData) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    console.log(`[renderChapterTree] 渲染${config.fileTypeName}章节树，章节数:`, chaptersData.length);

    const container = document.getElementById(`${config.prefix}ChapterTreeContainer`);
    if (!container) {
        console.error(`[renderChapterTree] 找不到容器: ${config.prefix}ChapterTreeContainer`);
        return;
    }

    container.innerHTML = '';

    // 扁平化渲染所有章节
    chaptersData.forEach(chapter => {
        const chapterDiv = createChapterElement(type, chapter);
        container.appendChild(chapterDiv);
    });

    console.log(`[renderChapterTree] ${config.fileTypeName}章节树渲染完成`);
}

/**
 * 创建章节元素（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 * @param {Object} chapter - 章节数据
 */
function createChapterElement(type, chapter) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    const div = document.createElement('div');
    div.className = `chapter-item level-${chapter.level}`;
    div.dataset.chapterId = chapter.id;
    div.style.marginLeft = `${(chapter.level - 1) * 20}px`;

    // 章节状态标记
    let statusIcon = '⚪';
    let statusClass = '';
    if (chapter.auto_selected) {
        statusIcon = '✅';
        statusClass = 'auto-selected';
    } else if (chapter.skip_recommended) {
        statusIcon = '❌';
        statusClass = 'skip-recommended';
    }

    // 生成标签HTML
    let tagsHtml = '';
    if (chapter.content_tags && chapter.content_tags.length > 0) {
        const tagColorMap = {
            '评分办法': 'primary',
            '评分表': 'warning text-dark',
            '供应商资质': 'success',
            '文件格式': 'secondary',
            '技术需求': 'info'
        };

        tagsHtml = chapter.content_tags.map(tag => {
            const colorClass = tagColorMap[tag] || 'secondary';
            return `<span class="badge bg-${colorClass} ms-1">${tag}</span>`;
        }).join('');
    }

    const checkboxId = `${config.prefix}-ch-${chapter.id}`;
    div.innerHTML = `
        <div class="d-flex align-items-center chapter-row ${statusClass} py-2">
            <input type="checkbox"
                   class="form-check-input me-2 ${config.prefix}-chapter-checkbox"
                   id="${checkboxId}"
                   data-chapter-id="${chapter.id}">
            <span class="chapter-status me-2">${statusIcon}</span>
            <label class="chapter-title flex-grow-1" for="${checkboxId}" style="cursor: pointer;">
                ${chapter.title}
                <small class="text-muted">(${chapter.word_count}字)</small>
                ${tagsHtml}
            </label>
        </div>
    `;

    // 绑定复选框事件
    const checkbox = div.querySelector(`.${config.prefix}-chapter-checkbox`);
    checkbox.addEventListener('change', (e) => {
        const selectedIds = selectedChapterIdsMap.get(type);
        if (e.target.checked) {
            selectedIds.add(chapter.id);
        } else {
            selectedIds.delete(chapter.id);
        }
        updateStatistics(type);
    });

    return div;
}

/**
 * 更新统计信息（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 * @param {Array} chaptersData - 章节数据（可选，首次调用时传入）
 */
function updateStatistics(type, chaptersData) {
    const config = CHAPTER_SELECTION_CONFIG[type];

    // 如果传入了章节数据，更新Map
    if (chaptersData) {
        chaptersDataMap.set(type, chaptersData);
    }

    const data = chaptersDataMap.get(type) || [];
    const selectedIds = selectedChapterIdsMap.get(type) || new Set();

    const totalChapters = data.length;
    const selectedCount = selectedIds.size;

    // 计算选中章节的总字数
    const selectedWords = data
        .filter(ch => selectedIds.has(ch.id))
        .reduce((sum, ch) => sum + ch.word_count, 0);

    document.getElementById(`${config.prefix}StatTotalChapters`).textContent = totalChapters;
    document.getElementById(`${config.prefix}StatSelectedChapters`).textContent = selectedCount;
    document.getElementById(`${config.prefix}StatSelectedWords`).textContent = selectedWords;
}

/**
 * 全选（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 */
function selectAll(type) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    const data = chaptersDataMap.get(type) || [];
    const selectedIds = selectedChapterIdsMap.get(type);

    data.forEach(ch => {
        if (!ch.skip_recommended) {
            selectedIds.add(ch.id);
            const checkbox = document.getElementById(`${config.prefix}-ch-${ch.id}`);
            if (checkbox) checkbox.checked = true;
        }
    });
    updateStatistics(type);
}

/**
 * 全不选（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 */
function unselectAll(type) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    const selectedIds = selectedChapterIdsMap.get(type);

    selectedIds.clear();
    document.querySelectorAll(`.${config.prefix}-chapter-checkbox`).forEach(cb => cb.checked = false);
    updateStatistics(type);
}

/**
 * 按关键词选择（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 * @param {string} keyword - 关键词
 */
function selectByKeyword(type, keyword) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    const data = chaptersDataMap.get(type) || [];
    const selectedIds = selectedChapterIdsMap.get(type);

    data.forEach(ch => {
        if (ch.title.includes(keyword) && !ch.skip_recommended) {
            selectedIds.add(ch.id);
            const checkbox = document.getElementById(`${config.prefix}-ch-${ch.id}`);
            if (checkbox) checkbox.checked = true;
        }
    });
    updateStatistics(type);
    showSuccessToast(`已选中包含"${keyword}"的章节`);
}

/**
 * 排除关键词（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 * @param {string} keyword - 关键词
 */
function excludeByKeyword(type, keyword) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    const data = chaptersDataMap.get(type) || [];
    const selectedIds = selectedChapterIdsMap.get(type);

    data.forEach(ch => {
        if (ch.title.includes(keyword)) {
            selectedIds.delete(ch.id);
            const checkbox = document.getElementById(`${config.prefix}-ch-${ch.id}`);
            if (checkbox) checkbox.checked = false;
        }
    });
    updateStatistics(type);
    showSuccessToast(`已排除包含"${keyword}"的章节`);
}

/**
 * 隐藏章节选择区域（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 */
function hideChapterSelection(type) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    const fileContent = document.getElementById(config.contentId);
    const selectionArea = document.getElementById(config.selectionAreaId);
    if (fileContent) fileContent.style.display = 'block';
    if (selectionArea) selectionArea.style.display = 'none';
}

/**
 * 确认保存选中章节（通用函数）
 * @param {string} type - 类型：'response'或'technical'
 */
async function confirmSave(type) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    console.log(`[confirmSave] 开始保存${config.fileTypeName}`);

    const selectedIds = selectedChapterIdsMap.get(type);
    if (!selectedIds || selectedIds.size === 0) {
        showErrorToast('请至少选择一个章节');
        return;
    }

    if (!currentTaskId) {
        showErrorToast('任务ID不存在，请刷新页面重试');
        return;
    }

    const btn = document.getElementById(config.confirmBtnId);
    if (!btn) {
        console.error(`找不到确认按钮: ${config.confirmBtnId}`);
        return;
    }

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';

    try {
        const chapterIds = Array.from(selectedIds);
        const apiUrl = `${config.apiSave}/${currentTaskId}`;

        console.log(`[confirmSave] 发起API请求，章节数:`, chapterIds.length);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chapter_ids: chapterIds })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '保存失败');
        }

        showSuccessToast(`✅ ${config.fileTypeName}已成功保存！文件名: ${result.filename}`);

        // 隐藏章节选择区域
        hideChapterSelection(type);

        // 刷新文件信息显示
        setTimeout(() => {
            loadFileInfo(type, currentTaskId);
        }, 500);

    } catch (error) {
        console.error(`[confirmSave] 保存${config.fileTypeName}失败:`, error);
        showErrorToast(`保存失败: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// 通用文件信息加载函数
async function loadFileInfo(type, taskId) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    console.log(`[loadFileInfo] 加载${config.fileTypeName}文件信息, taskId:`, taskId);

    try {
        const response = await fetch(`${config.apiInfo}/${taskId}`);
        const data = await response.json();
        console.log(`[loadFileInfo] API响应:`, data);

        const contentDiv = document.getElementById(config.contentId);

        if (data.success && data.has_file) {
            console.log(`[loadFileInfo] 检测到已保存的${config.fileTypeName}文件`);

            // 计算文件大小显示
            const fileSizeKB = (data.file_size / 1024).toFixed(2);
            const savedDate = new Date(data.saved_at).toLocaleString('zh-CN');

            const htmlContent = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>
                    <strong>已保存${config.fileTypeName}文件</strong>
                    <div class="mt-3">
                        <p class="mb-2"><strong>文件名:</strong> ${data.filename}</p>
                        <p class="mb-2"><strong>文件大小:</strong> ${fileSizeKB} KB</p>
                        <p class="mb-3"><strong>保存时间:</strong> ${savedDate}</p>
                        <button class="btn btn-outline-secondary btn-sm me-2" onclick="previewFile('${type}', '${taskId}')">
                            <i class="bi bi-eye me-2"></i>预览
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="downloadFile('${type}', '${taskId}')">
                            <i class="bi bi-download me-2"></i>下载
                        </button>
                    </div>
                </div>
            `;

            if (contentDiv) {
                contentDiv.innerHTML = htmlContent;
                contentDiv.style.display = 'block';
            }
        } else {
            console.log(`[loadFileInfo] 未找到${config.fileTypeName}文件`);
            const noFileMessage = document.getElementById(config.noFileMessageId);
            if (noFileMessage) {
                noFileMessage.style.display = 'block';
            }
            if (contentDiv) {
                contentDiv.innerHTML = '';
            }
        }
    } catch (error) {
        console.error(`[loadFileInfo] 加载${config.fileTypeName}文件信息失败:`, error);
    }
}

// 通用文件预览函数
function previewFile(type, taskId) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    console.log(`[previewFile] 预览${config.fileTypeName}文件, taskId:`, taskId);

    const previewUrl = `${config.apiPreview}/${taskId}`;

    // 显示加载状态
    const previewContent = document.getElementById('documentPreviewContent');
    if (previewContent) {
        previewContent.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在加载文档...</p></div>';
    }

    // 显示预览模态框
    const previewModal = new bootstrap.Modal(document.getElementById('documentPreviewModal'));
    previewModal.show();

    // 使用mammoth.js在前端直接转换Word文档
    fetch(previewUrl)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            return mammoth.convertToHtml({arrayBuffer: arrayBuffer});
        })
        .then(result => {
            if (previewContent) {
                const html = result.value || '<p>文档内容为空</p>';
                previewContent.innerHTML = `<div class="mammoth-preview-content">${html}</div>`;
            }
        })
        .catch(error => {
            console.error(`[previewFile] 预览${config.fileTypeName}失败:`, error);
            if (previewContent) {
                previewContent.innerHTML = '<div class="alert alert-danger">预览失败，请稍后重试</div>';
            }
        });
}

// 通用文件下载函数
function downloadFile(type, taskId) {
    const config = CHAPTER_SELECTION_CONFIG[type];
    console.log(`[downloadFile] 下载${config.fileTypeName}文件, taskId:`, taskId);
    window.location.href = `${config.apiDownload}/${taskId}`;
}

// 向后兼容：保留旧函数名
async function confirmInlineSaveResponseFile() {
    return confirmSave('response');
}

// ============================================
// 绑定章节选择事件（统一处理）
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DOMContentLoaded] 绑定章节选择事件');

    // ========== 应答文件格式标签页 ==========

    // 绑定"从章节目录选择"按钮
    const responseSelectBtn = document.getElementById('selectChaptersForResponseFileBtn');
    if (responseSelectBtn) {
        responseSelectBtn.addEventListener('click', () => showChapterSelection('response'));
        console.log('[DOMContentLoaded] 已绑定应答文件"从章节目录选择"按钮');
    }

    // 绑定批量操作按钮
    document.getElementById('inlineSelectAllBtn')?.addEventListener('click', () => selectAll('response'));
    document.getElementById('inlineUnselectAllBtn')?.addEventListener('click', () => unselectAll('response'));
    document.getElementById('inlineSelectTechBtn')?.addEventListener('click', () => selectByKeyword('response', '技术'));
    document.getElementById('inlineExcludeContractBtn')?.addEventListener('click', () => excludeByKeyword('response', '合同'));

    // 绑定确认保存按钮
    const confirmResponseBtn = document.getElementById('confirmInlineSaveResponseFileBtn');
    if (confirmResponseBtn) {
        confirmResponseBtn.addEventListener('click', () => confirmSave('response'));
        console.log('[DOMContentLoaded] 已绑定应答文件确认保存按钮');
    }

    // 绑定取消/隐藏按钮
    document.getElementById('hideChapterSelectionBtn')?.addEventListener('click', () => hideChapterSelection('response'));
    document.getElementById('cancelInlineSelectionBtn')?.addEventListener('click', () => hideChapterSelection('response'));

    // ========== 技术需求标签页 ==========

    // 绑定"从章节目录选择"按钮（技术需求）
    const technicalSelectBtn = document.getElementById('selectChaptersForTechnicalBtn');
    if (technicalSelectBtn) {
        technicalSelectBtn.addEventListener('click', () => showChapterSelection('technical'));
        console.log('[DOMContentLoaded] 已绑定技术需求"从章节目录选择"按钮');
    }

    // 绑定批量操作按钮（技术需求）
    document.getElementById('technicalSelectAllBtn')?.addEventListener('click', () => selectAll('technical'));
    document.getElementById('technicalUnselectAllBtn')?.addEventListener('click', () => unselectAll('technical'));
    document.getElementById('technicalSelectTechBtn')?.addEventListener('click', () => selectByKeyword('technical', '技术'));
    document.getElementById('technicalExcludeContractBtn')?.addEventListener('click', () => excludeByKeyword('technical', '合同'));

    // 绑定确认保存按钮（技术需求）
    const confirmTechnicalBtn = document.getElementById('confirmTechnicalSaveBtn');
    if (confirmTechnicalBtn) {
        confirmTechnicalBtn.addEventListener('click', () => confirmSave('technical'));
        console.log('[DOMContentLoaded] 已绑定技术需求确认保存按钮');
    }

    // 绑定取消/隐藏按钮（技术需求）
    document.getElementById('hideTechnicalChapterSelectionBtn')?.addEventListener('click', () => hideChapterSelection('technical'));
    document.getElementById('cancelTechnicalSelectionBtn')?.addEventListener('click', () => hideChapterSelection('technical'));
});

// ============================================
// 数据收集和同步功能（新增）
// ============================================

/**
 * 收集资格要求数据
 * @returns {Promise<Object>} 资格要求JSON数据
 */
async function collectQualificationsData() {
    console.log('[collectQualificationsData] 开始收集资格要求数据');

    try {
        if (!HITLConfigManager.currentProjectId) {
            console.warn('[collectQualificationsData] 项目ID不存在，返回空数据');
            return {};
        }

        const response = await fetch(
            `/api/tender-processing/requirements/${HITLConfigManager.currentProjectId}?category=qualification`
        );
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || '获取资格要求失败');
        }

        console.log(`[collectQualificationsData] 获取到 ${data.requirements.length} 条资格要求`);

        // 转换为JSON格式
        return convertRequirementsToJSON(data.requirements);

    } catch (error) {
        console.error('[collectQualificationsData] 收集资格要求数据失败:', error);
        return {};
    }
}

/**
 * 收集技术需求数据
 * @returns {Promise<Object>} 技术需求JSON数据
 */
async function collectTechnicalData() {
    console.log('[collectTechnicalData] 开始收集技术需求数据');

    try {
        if (!HITLConfigManager.currentProjectId) {
            console.warn('[collectTechnicalData] 项目ID不存在，返回空数据');
            return {};
        }

        const response = await fetch(
            `/api/tender-processing/requirements/${HITLConfigManager.currentProjectId}?category=technical`
        );
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || '获取技术需求失败');
        }

        console.log(`[collectTechnicalData] 获取到 ${data.requirements.length} 条技术需求`);

        // 转换为JSON格式
        return convertRequirementsToJSON(data.requirements);

    } catch (error) {
        console.error('[collectTechnicalData] 收集技术需求数据失败:', error);
        return {};
    }
}

/**
 * 收集评分办法数据
 * @returns {Promise<Object>} 评分办法JSON数据
 */
async function collectScoringData() {
    console.log('[collectScoringData] 开始收集评分办法数据');

    try {
        if (!HITLConfigManager.currentProjectId) {
            console.warn('[collectScoringData] 项目ID不存在，返回空数据');
            return {};
        }

        const response = await fetch(
            `/api/tender-processing/requirements/${HITLConfigManager.currentProjectId}?category=commercial`
        );
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || '获取评分办法失败');
        }

        console.log(`[collectScoringData] 获取到 ${data.requirements.length} 条评分办法`);

        // 转换为JSON格式
        return convertRequirementsToJSON(data.requirements);

    } catch (error) {
        console.error('[collectScoringData] 收集评分办法数据失败:', error);
        return {};
    }
}

/**
 * 将需求数组转换为JSON对象格式
 * @param {Array} requirements - 需求数组
 * @returns {Object} JSON格式的需求数据
 */
function convertRequirementsToJSON(requirements) {
    const result = {};

    if (!requirements || requirements.length === 0) {
        return result;
    }

    requirements.forEach(req => {
        // 使用 subcategory 作为key，如果没有则用 summary 或 requirement_id
        const key = req.subcategory || req.summary || `requirement_${req.requirement_id}`;

        result[key] = {
            requirement_id: req.requirement_id,
            constraint_type: req.constraint_type,
            detail: req.detail,
            summary: req.summary,
            source_location: req.source_location,
            priority: req.priority,
            extraction_confidence: req.extraction_confidence,
            is_verified: req.is_verified || false,
            created_at: req.created_at
        };
    });

    console.log(`[convertRequirementsToJSON] 转换了 ${requirements.length} 条需求为JSON格式`);
    return result;
}

// ============================================
// 填充应答文件功能
// ============================================

/**
 * 显示填充应答信息区域
 * 在保存应答文件格式后调用
 */
function showFillSection() {
    console.log('[showFillSection] 显示填充应答信息区域');

    const fillSection = document.getElementById('responseFileFillSection');
    if (!fillSection) {
        console.error('[showFillSection] 未找到填充区域元素');
        return;
    }

    // 显示填充区域
    fillSection.classList.remove('d-none');

    // 自动填充项目信息
    const projectNameInput = document.getElementById('fillProjectName');
    const tenderNoInput = document.getElementById('fillTenderNo');
    const dateInput = document.getElementById('fillDate');

    // 从基本信息表单获取数据
    const projectNameFromForm = document.getElementById('hitlProjectName');
    const tenderNoFromForm = document.getElementById('hitlTenderNo');

    if (projectNameInput && projectNameFromForm) {
        projectNameInput.value = projectNameFromForm.value || '';
    }

    if (tenderNoInput && tenderNoFromForm) {
        tenderNoInput.value = tenderNoFromForm.value || '';
    }

    // 设置默认日期为当前日期（格式：YYYY年MM月DD日）
    if (dateInput) {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        dateInput.value = `${year}年${month}月${day}日`;
    }

    // 加载公司资质信息
    if (HITLConfigManager.currentCompanyId) {
        loadQualificationsForFill(HITLConfigManager.currentCompanyId);
    } else {
        console.warn('[showFillSection] 当前未选择公司，无法加载资质信息');
    }

    // 滚动到填充区域
    fillSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * 加载公司资质信息用于填充
 * @param {number} companyId - 公司ID
 */
async function loadQualificationsForFill(companyId) {
    console.log(`[loadQualificationsForFill] 加载公司 ${companyId} 的资质信息`);

    try {
        const response = await fetch(`/api/knowledge-base/company/${companyId}/qualifications`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.qualifications) {
            console.log(`[loadQualificationsForFill] 成功加载 ${data.qualifications.length} 条资质`);
            renderQualificationCheckboxes(data.qualifications);
        } else {
            console.warn('[loadQualificationsForFill] 未找到资质信息');
            renderQualificationCheckboxes([]);
        }
    } catch (error) {
        console.error('[loadQualificationsForFill] 加载资质失败:', error);
        showErrorMessage('fillQualificationsList', '加载资质信息失败，请重试');
    }
}

/**
 * 渲染资质复选框列表
 * @param {Array} qualifications - 资质列表
 */
function renderQualificationCheckboxes(qualifications) {
    console.log(`[renderQualificationCheckboxes] 渲染 ${qualifications.length} 个资质复选框`);

    const container = document.getElementById('fillQualificationsList');
    if (!container) {
        console.error('[renderQualificationCheckboxes] 未找到容器元素');
        return;
    }

    if (qualifications.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                当前公司暂无资质证明图片
            </div>
        `;
        return;
    }

    // 按类别分组
    const grouped = {};
    qualifications.forEach(qual => {
        const category = qual.category || '其他';
        if (!grouped[category]) {
            grouped[category] = [];
        }
        grouped[category].push(qual);
    });

    let html = '';

    // 渲染各个类别
    Object.keys(grouped).sort().forEach(category => {
        html += `
            <div class="mb-3">
                <h6 class="text-primary mb-2">${category}</h6>
                <div class="row g-2">
        `;

        grouped[category].forEach(qual => {
            const imageUrl = qual.image_url || qual.image_path || '';
            const thumbUrl = imageUrl.replace('/uploads/', '/uploads/thumbnails/') || imageUrl;

            html += `
                <div class="col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox"
                               id="qual_${qual.qualification_id}"
                               name="selected_qualifications"
                               value="${qual.qualification_id}"
                               data-image-url="${imageUrl}"
                               data-name="${qual.name || ''}">
                        <label class="form-check-label d-flex align-items-center" for="qual_${qual.qualification_id}">
                            ${thumbUrl ? `<img src="${thumbUrl}" class="me-2" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" onerror="this.src='/static/images/no-image.png'">` : ''}
                            <span>${qual.name || '未命名资质'}</span>
                        </label>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

/**
 * 开始填充应答文件
 */
async function startFillResponseFile() {
    console.log('[startFillResponseFile] 开始填充应答文件');

    // 获取表单数据
    const projectName = document.getElementById('fillProjectName')?.value;
    const tenderNo = document.getElementById('fillTenderNo')?.value;
    const dateText = document.getElementById('fillDate')?.value;

    // 验证必填项
    if (!projectName || !tenderNo || !dateText) {
        showErrorMessage('fillErrorMessage', '请填写完整的项目信息');
        return;
    }

    // 获取选中的资质
    const imageConfig = buildImageConfigFromCheckboxes();

    if (Object.keys(imageConfig).length === 0) {
        showErrorMessage('fillErrorMessage', '请至少选择一个资质证明图片');
        return;
    }

    // 构建请求数据
    const formData = {
        project_name: projectName,
        tender_no: tenderNo,
        date_text: dateText,
        image_config: imageConfig
    };

    console.log('[startFillResponseFile] 请求数据:', formData);

    // 显示进度条
    const progressBar = document.getElementById('fillProgress');
    const progressBarInner = progressBar?.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.classList.remove('d-none');
        if (progressBarInner) {
            progressBarInner.style.width = '30%';
        }
    }

    // 隐藏之前的结果
    document.getElementById('fillResult')?.classList.add('d-none');
    document.getElementById('fillError')?.classList.add('d-none');

    try {
        const response = await fetch(`/api/tender-processing/fill-response-file/${currentTaskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (progressBarInner) {
            progressBarInner.style.width = '60%';
        }

        const data = await response.json();

        if (progressBarInner) {
            progressBarInner.style.width = '100%';
        }

        if (data.success) {
            console.log('[startFillResponseFile] 填充成功:', data);

            // 显示成功消息
            const resultCard = document.getElementById('fillResult');
            const resultMessage = document.getElementById('fillResultMessage');

            if (resultCard && resultMessage) {
                resultMessage.textContent = data.message || '应答文件填充完成！';
                resultCard.classList.remove('d-none');
            }

            // 设置下载链接
            if (data.download_url) {
                const downloadLink = document.getElementById('fillDownloadLink');
                if (downloadLink) {
                    downloadLink.href = data.download_url;
                }
            }

            // 隐藏进度条
            setTimeout(() => {
                if (progressBar) {
                    progressBar.classList.add('d-none');
                }
            }, 1000);

        } else {
            throw new Error(data.message || '填充失败');
        }

    } catch (error) {
        console.error('[startFillResponseFile] 填充失败:', error);

        if (progressBar) {
            progressBar.classList.add('d-none');
        }

        showErrorMessage('fillErrorMessage', error.message || '填充应答文件时发生错误，请重试');
    }
}

/**
 * 从复选框构建图片配置
 * @returns {Object} 图片配置对象
 */
function buildImageConfigFromCheckboxes() {
    const imageConfig = {};
    const checkboxes = document.querySelectorAll('input[name="selected_qualifications"]:checked');

    checkboxes.forEach((checkbox, index) => {
        const imageUrl = checkbox.getAttribute('data-image-url');
        const qualName = checkbox.getAttribute('data-name');

        if (imageUrl) {
            // 使用资质名称作为key，如果没有则使用序号
            const key = qualName || `image_${index + 1}`;
            imageConfig[key] = imageUrl;
        }
    });

    console.log(`[buildImageConfigFromCheckboxes] 构建了 ${Object.keys(imageConfig).length} 个图片配置`);
    return imageConfig;
}

/**
 * 预览填充后的文档
 */
function previewFilledDocument() {
    console.log('[previewFilledDocument] 预览填充后的文档');

    const downloadLink = document.getElementById('fillDownloadLink');
    if (!downloadLink || !downloadLink.href) {
        alert('无法预览：未找到文件链接');
        return;
    }

    // 使用与预览应答文件格式相同的逻辑
    // 可以复用现有的预览功能或新建预览窗口
    window.open(downloadLink.href, '_blank');
}

/**
 * 显示错误消息的辅助函数
 * @param {string} elementId - 错误消息元素ID
 * @param {string} message - 错误消息
 */
function showErrorMessage(elementId, message) {
    const errorCard = document.getElementById('fillError');
    const errorMessage = document.getElementById(elementId);

    if (errorCard && errorMessage) {
        errorMessage.textContent = message;
        errorCard.classList.remove('d-none');
    }
}

