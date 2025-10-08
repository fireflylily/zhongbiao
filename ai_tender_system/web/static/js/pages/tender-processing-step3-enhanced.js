// ============================================
// Step 3 增强版: 详细需求提取和编辑
// ============================================

// ============================================
// 全局状态管理
// ============================================
let currentTaskId = null;
let currentProjectId = null;
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
        if (currentTaskId && currentProjectId) {
            loadRequirements(currentTaskId, currentProjectId);
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
        const tbody = document.querySelector('#requirementsTable tbody');
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
                <td class="text-center">
                    <input type="checkbox" class="form-check-input req-checkbox" value="${req.requirement_id || index}">
                </td>
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

    const loadingEl = document.getElementById('requirementsLoading');
    const contentEl = document.getElementById('requirementsContent');
    const emptyEl = document.getElementById('requirementsEmpty');
    const neverExtractedEl = document.getElementById('requirementsNeverExtracted');

    try {
        // 显示加载状态
        if (loadingEl) loadingEl.classList.remove('d-none');
        if (contentEl) contentEl.classList.add('d-none');
        if (emptyEl) emptyEl.classList.add('d-none');
        if (neverExtractedEl) neverExtractedEl.classList.add('d-none');

        console.log('[loadRequirements] 发起API请求...');
        const response = await fetch(`/api/tender-processing/requirements/${projectId}`);
        const data = await response.json();
        console.log('[loadRequirements] API响应:', data);

        // 隐藏加载状态
        if (loadingEl) loadingEl.classList.add('d-none');

        if (!response.ok) {
            throw new Error(data.error || '加载失败');
        }

        // 判断是从未提取过，还是提取了但为空
        if (!data.has_extracted) {
            // 从未提取过
            console.log('[loadRequirements] 从未提取过需求');
            if (neverExtractedEl) neverExtractedEl.classList.remove('d-none');
        } else if (data.requirements.length === 0) {
            // 提取过但为空
            console.log('[loadRequirements] 提取过但结果为空');
            if (emptyEl) emptyEl.classList.remove('d-none');
        } else {
            // 有数据
            console.log('[loadRequirements] 加载到', data.requirements.length, '条需求');
            currentRequirements = data.requirements;
            requirementsTableManager.setRequirements(data.requirements);
            if (contentEl) contentEl.classList.remove('d-none');
        }

    } catch (error) {
        console.error('[loadRequirements] 加载失败:', error);
        if (loadingEl) loadingEl.classList.add('d-none');
        alert('加载需求失败: ' + error.message);
    }
}

// 提取详细需求
async function extractDetailedRequirements() {
    console.log('[extractDetailedRequirements] 开始提取需求');

    if (!currentTaskId || !currentProjectId) {
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

        console.log('[extractDetailedRequirements] 发起提取请求, 模型:', selectedModel);
        const response = await fetch(`/api/tender-processing/extract-requirements/${currentTaskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: selectedModel })
        });

        const data = await response.json();
        console.log('[extractDetailedRequirements] 提取结果:', data);

        if (!response.ok) {
            throw new Error(data.error || '提取失败');
        }

        // 提取成功，加载需求并显示清单
        alert(`✅ 提取成功！共提取 ${data.requirements_extracted} 条需求`);

        // 重新加载需求数据
        const reqResponse = await fetch(`/api/tender-processing/requirements/${currentTaskId}`);
        const reqData = await reqResponse.json();

        if (reqData.success && reqData.requirements) {
            // 显示13条资格清单
            displayEligibilityChecklist(reqData.requirements);
        }

    } catch (error) {
        console.error('[extractDetailedRequirements] 提取失败:', error);
        alert('提取失败: ' + error.message);
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
        const response = await fetch(`/api/tender-processing/filtered-chunks/${taskId}`);
        const data = await response.json();
        console.log('[loadFilteredChunksData] API响应:', data);

        // 隐藏加载状态
        if (loadingEl) loadingEl.classList.add('d-none');

        if (!response.ok) {
            throw new Error(data.error || '加载失败');
        }

        if (data.chunks.length === 0) {
            console.log('[loadFilteredChunksData] 没有筛选后的段落');
            if (emptyEl) emptyEl.classList.remove('d-none');
        } else {
            console.log('[loadFilteredChunksData] 加载到', data.chunks.length, '个段落');
            currentChunks = data.chunks;
            renderFilteredChunks(data.chunks);
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

// 加载应答文件信息
async function loadResponseFileInfo(taskId) {
    console.log('[loadResponseFileInfo] 开始执行, taskId:', taskId);
    try {
        console.log('[loadResponseFileInfo] 发起API请求...');
        const response = await fetch(`/api/tender-processing/response-file-info/${taskId}`);
        const data = await response.json();
        console.log('[loadResponseFileInfo] API响应数据:', data);

        const noFileMessage = document.getElementById('noResponseFileMessage');
        const fileInfoDiv = document.getElementById('responseFileInfo');
        console.log('[loadResponseFileInfo] DOM元素查找结果:');
        console.log('  - noResponseFileMessage:', noFileMessage);
        console.log('  - responseFileInfo:', fileInfoDiv);

        if (data.success && data.has_file) {
            console.log('[loadResponseFileInfo] 检测到有文件，准备显示文件信息');

            // 计算文件大小显示
            const fileSizeKB = (data.file_size / 1024).toFixed(2);
            const savedDate = new Date(data.saved_at).toLocaleString('zh-CN');
            console.log('[loadResponseFileInfo] 文件信息 - 名称:', data.filename, '大小:', fileSizeKB, 'KB');

            const htmlContent = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>
                    <strong>已保存应答文件模板</strong>
                    <div class="mt-3">
                        <p class="mb-2"><strong>文件名:</strong> ${data.filename}</p>
                        <p class="mb-2"><strong>文件大小:</strong> ${fileSizeKB} KB</p>
                        <p class="mb-3"><strong>保存时间:</strong> ${savedDate}</p>
                        <button class="btn btn-outline-secondary btn-sm me-2" onclick="previewResponseFile('${taskId}')">
                            <i class="bi bi-eye me-2"></i>预览
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="downloadResponseFile('${taskId}')">
                            <i class="bi bi-download me-2"></i>下载应答文件
                        </button>
                    </div>
                </div>
            `;

            // 获取响应文件内容容器并直接替换内容
            const responseFileContent = document.getElementById('responseFileContent');

            if (responseFileContent) {
                console.log('[loadResponseFileInfo] 直接替换responseFileContent的内容');
                responseFileContent.innerHTML = htmlContent;
                console.log('[loadResponseFileInfo] 替换完成，HTML长度:', responseFileContent.innerHTML.length);

                // 不要修改tab panel的classes，让Bootstrap自己管理tab切换
                console.log('[loadResponseFileInfo] 内容已更新，Bootstrap会自动处理tab显示');
            } else {
                console.error('[loadResponseFileInfo] responseFileContent元素不存在！');
            }
        } else {
            console.log('[loadResponseFileInfo] 没有文件或API返回失败，显示空状态');
            // 没有文件，显示空状态
            if (noFileMessage) {
                noFileMessage.style.display = 'block';
                console.log('[loadResponseFileInfo] 显示空消息提示');
            }
            if (fileInfoDiv) {
                fileInfoDiv.style.display = 'none';
                console.log('[loadResponseFileInfo] 隐藏文件信息区域');
            }
        }
        console.log('[loadResponseFileInfo] 函数执行完成');
    } catch (error) {
        console.error('[loadResponseFileInfo] 加载应答文件信息失败:', error);
        console.error('[loadResponseFileInfo] 错误堆栈:', error.stack);
    }
}

// 预览应答文件
function previewResponseFile(taskId) {
    console.log('[previewResponseFile] 预览文件, taskId:', taskId);
    window.open(`/api/tender-processing/preview-response-file/${taskId}`, '_blank');
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
    currentProjectId = projectId;

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

        if (data.success && data.basic_info) {
            // 填充表单字段
            const info = data.basic_info;
            if (info.project_name) document.getElementById('projectName').value = info.project_name;
            if (info.project_number) document.getElementById('projectNumber').value = info.project_number;
            if (info.tender_party) document.getElementById('tenderParty').value = info.tender_party;
            if (info.tender_agent) document.getElementById('tenderAgent').value = info.tender_agent;
            if (info.tender_method) document.getElementById('tenderMethod').value = info.tender_method;
            if (info.tender_location) document.getElementById('tenderLocation').value = info.tender_location;
            if (info.tender_deadline) document.getElementById('tenderDeadline').value = info.tender_deadline;
            if (info.winner_count) document.getElementById('winnerCount').value = info.winner_count;

            alert('✅ AI提取基本信息完成!');
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
// 保存基本信息
// ============================================
async function saveBasicInfo() {
    console.log('[saveBasicInfo] 开始保存基本信息');

    if (!currentTaskId) {
        alert('缺少任务ID');
        return;
    }

    const btn = document.getElementById('saveBasicInfoBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>保存中...';
    }

    try {
        // 从表单获取基本信息
        const basicInfo = {
            project_name: document.getElementById('projectName')?.value || '',
            project_number: document.getElementById('projectNumber')?.value || '',
            tender_party: document.getElementById('tenderParty')?.value || '',
            tender_agent: document.getElementById('tenderAgent')?.value || '',
            tender_method: document.getElementById('tenderMethod')?.value || '',
            tender_location: document.getElementById('tenderLocation')?.value || '',
            tender_deadline: document.getElementById('tenderDeadline')?.value || '',
            winner_count: document.getElementById('winnerCount')?.value || ''
        };

        console.log('[saveBasicInfo] 基本信息:', basicInfo);

        // 保存到step3_data
        const response = await fetch(`/api/tender-processing/save-basic-info/${currentTaskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ basic_info: basicInfo })
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ 基本信息保存成功');
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-lg me-2"></i>已保存';
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-success');
            }
        } else {
            throw new Error(data.error || '保存失败');
        }

    } catch (error) {
        console.error('[saveBasicInfo] 保存失败:', error);
        alert('保存失败: ' + error.message);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-save me-2"></i>保存基本信息';
        }
    }
}

// ============================================
// 保存并完成
// ============================================
async function saveAndComplete() {
    console.log('[saveAndComplete] 开始保存并完成');

    if (!currentTaskId) {
        alert('缺少任务ID');
        return;
    }

    const btn = document.getElementById('saveAndCompleteBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>保存并完成中...';
    }

    try {
        // 先保存基本信息
        await saveBasicInfo();

        // 标记任务完成
        const response = await fetch(`/api/tender-processing/complete-hitl/${currentTaskId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ 所有数据已保存，HITL流程完成！');
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已完成';
                btn.classList.remove('btn-success');
                btn.classList.add('btn-secondary');
            }
        } else {
            throw new Error(data.error || '完成失败');
        }

    } catch (error) {
        console.error('[saveAndComplete] 保存失败:', error);
        alert('保存失败: ' + error.message);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>保存并完成';
        }
    }
}

// ============================================
// 13条供应商资格要求清单
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
    {id: 13, name: "保证金要求", keywords: ["保证金", "投标保证金"]}
];

// 显示13条资格要求清单
function displayEligibilityChecklist(requirements) {
    console.log('[displayEligibilityChecklist] 显示资格清单, 需求数量:', requirements.length);

    // 过滤出资格类需求
    const qualificationReqs = requirements.filter(req => req.category === 'qualification');
    console.log('[displayEligibilityChecklist] 资格类需求数量:', qualificationReqs.length);

    // 初始化13条清单数据
    const checklistData = ELIGIBILITY_CHECKLIST.map(item => ({
        ...item,
        found: false,
        requirements: []
    }));

    // 将提取的需求匹配到13条清单
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
    const notFoundCount = 13 - foundCount;

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
                html += `
                    <div class="mb-2 p-2 bg-light rounded">
                        <div class="small text-muted mb-1">
                            <span class="badge bg-${getConstraintTypeBadge(req.constraint_type)}">${getConstraintTypeLabel(req.constraint_type)}</span>
                            ${req.subcategory ? '<span class="ms-2">' + req.subcategory + '</span>' : ''}
                        </div>
                        <div class="fw-medium">${req.summary || req.detail}</div>
                        ${req.summary && req.detail !== req.summary ? '<div class="small text-secondary mt-1">' + req.detail + '</div>' : ''}
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
