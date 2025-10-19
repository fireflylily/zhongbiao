/**
 * HITL 配置管理器
 * 用于投标管理页面的配置管理、项目选择、公司选择、AI模型选择等功能
 * 同时包含快捷跳转函数(支持双模式: Tab切换/URL跳转)
 */

// HITL页面的模型和公司管理
const HITLConfigManager = {
    currentCompanyId: null,
    currentModel: 'yuanjing-deepseek-v3',
    currentProjectId: null,        // 当前项目ID（用于创建/更新判断）
    selectedProjectId: null,        // 项目选择器的值

    // 初始化
    init() {
        console.log('[HITLConfigManager] 初始化配置管理器');

        // 加载公司列表
        this.loadCompanies();

        // 加载模型列表
        this.loadModels();

        // 加载项目列表（显示所有项目）
        this.loadProjects();

        // 绑定事件
        this.bindEvents();
    },

    // 加载公司列表
    async loadCompanies() {
        try {
            const response = await fetch('/api/companies');
            const data = await response.json();

            if (data.success && data.data) {
                const select = document.getElementById('hitlCompanySelect');
                const nameSpan = document.getElementById('hitlSelectedCompanyName');

                select.innerHTML = '<option value="">请选择公司...</option>';

                data.data.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.company_id;
                    option.textContent = company.company_name;
                    select.appendChild(option);
                });

                console.log(`[HITLConfigManager] 加载了 ${data.data.length} 个公司`);
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载公司列表失败:', error);
        }
    },

    // 加载模型列表
    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();

            if (data.success && data.models) {
                this.updateModelSelect(data.models);
                console.log(`[HITLConfigManager] 加载了 ${data.count} 个AI模型`);
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载模型列表失败:', error);
        }
    },

    // 加载项目列表
    async loadProjects() {
        try {
            console.log('[HITLConfigManager] 开始加载项目列表...');
            const url = this.currentCompanyId
                ? `/api/tender-projects?company_id=${this.currentCompanyId}`
                : '/api/tender-projects';

            const response = await fetch(url);
            const data = await response.json();

            const select = document.getElementById('hitlProjectSelect');
            select.innerHTML = '<option value="">新建项目</option>';

            if (data.success && data.data && data.data.length > 0) {
                data.data.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.project_id;
                    const projectNumber = project.project_number || '无编号';
                    const status = project.status || 'draft';
                    option.textContent = `${project.project_name} (${projectNumber}) [${status}]`;
                    select.appendChild(option);
                });

                console.log(`[HITLConfigManager] 成功加载 ${data.data.length} 个项目`);
            } else {
                console.log('[HITLConfigManager] 没有找到项目数据');
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载项目列表失败:', error);
        }
    },

    // 加载并显示项目详情
    async loadProjectDetails(projectId) {
        try {
            console.log('[HITLConfigManager] 开始加载项目详情:', projectId);
            const response = await fetch(`/api/tender-projects/${projectId}`);
            const data = await response.json();

            if (data.success && data.data) {
                const project = data.data;

                // 【新增】先设置公司选择器
                if (project.company_id) {
                    const companySelect = document.getElementById('hitlCompanySelect');
                    const companyNameSpan = document.getElementById('hitlSelectedCompanyName');

                    if (companySelect) {
                        companySelect.value = project.company_id;
                        this.currentCompanyId = project.company_id;

                        // 更新公司名称显示
                        if (companyNameSpan) {
                            const selectedOption = companySelect.options[companySelect.selectedIndex];
                            if (selectedOption) {
                                companyNameSpan.textContent = selectedOption.text;
                                companyNameSpan.className = 'text-primary fw-bold';
                            }
                        }

                        console.log('[HITLConfigManager] 已设置公司:', project.company_id);
                    }
                }

                // 填充基本信息表单
                if (document.getElementById('projectName')) {
                    document.getElementById('projectName').value = project.project_name || '';
                }
                if (document.getElementById('projectNumber')) {
                    document.getElementById('projectNumber').value = project.project_number || '';
                }
                if (document.getElementById('tenderParty')) {
                    document.getElementById('tenderParty').value = project.tenderer || '';
                }
                if (document.getElementById('tenderAgent')) {
                    document.getElementById('tenderAgent').value = project.agency || '';
                }
                if (document.getElementById('tenderMethod')) {
                    document.getElementById('tenderMethod').value = project.bidding_method || '';
                }
                if (document.getElementById('tenderLocation')) {
                    document.getElementById('tenderLocation').value = project.bidding_location || '';
                }
                if (document.getElementById('tenderDeadline')) {
                    document.getElementById('tenderDeadline').value = project.bidding_time || '';
                }
                if (document.getElementById('winnerCount')) {
                    document.getElementById('winnerCount').value = project.winner_count || '';
                }

                // 显示项目信息提示
                const projectInfo = document.getElementById('hitlProjectInfo');
                const projectName = document.getElementById('hitlProjectName');
                if (projectInfo && projectName) {
                    projectName.textContent = `已加载: ${project.project_name}`;
                    projectInfo.style.display = 'block';
                }

                // 【修改】保存到 companyStateManager（统一数据源）
                if (typeof window.companyStateManager !== 'undefined') {
                    // 从公司选择器获取公司名称
                    let companyName = '';
                    const companySelect = document.getElementById('hitlCompanySelect');
                    if (companySelect && companySelect.value) {
                        const selectedOption = companySelect.options[companySelect.selectedIndex];
                        if (selectedOption) {
                            companyName = selectedOption.text;
                        }
                    }

                    // 先设置公司信息
                    window.companyStateManager.setSelectedCompany({
                        company_id: project.company_id,
                        company_name: companyName
                    });

                    // 再设置项目信息
                    window.companyStateManager.setProjectInfo({
                        project_name: project.project_name,
                        project_number: null
                    });

                    console.log('[HITLConfigManager] 已保存到 companyStateManager:', {
                        projectName: project.project_name,
                        companyId: project.company_id,
                        companyName: companyName
                    });
                }

                console.log('[HITLConfigManager] 项目基本信息已加载:', project);

                // 【新增】查找并加载该项目最新的HITL任务数据
                await this.findAndLoadHitlTaskData(projectId);

                return project;
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载项目详情失败:', error);
            return null;
        }
    },

    // 【新增】查找并加载HITL任务数据
    async findAndLoadHitlTaskData(projectId) {
        try {
            console.log('[HITLConfigManager] 查找项目的HITL任务:', projectId);

            const response = await fetch(`/api/tender-processing/hitl-tasks?project_id=${projectId}&latest=true`);
            const data = await response.json();

            if (data.success && data.task) {
                const hitlTask = data.task;
                console.log('[HITLConfigManager] 找到HITL任务:', hitlTask.hitl_task_id);

                // 【修改】保存到 projectDataBridge（替代 window.current* 变量）
                if (typeof window.projectDataBridge !== 'undefined') {
                    window.projectDataBridge.hitlTaskId = hitlTask.hitl_task_id;
                }

                // 【新增】显示原标书文件信息
                if (hitlTask.step1_data) {
                    try {
                        const step1Data = typeof hitlTask.step1_data === 'string'
                            ? JSON.parse(hitlTask.step1_data)
                            : hitlTask.step1_data;

                        if (step1Data.file_path && step1Data.file_name) {
                            console.log('[HITLConfigManager] 找到原标书文件:', step1Data.file_name);
                            this.displayUploadedFile(step1Data.file_name, step1Data.file_path);

                            // 【修复】保存三种文件信息到 projectDataBridge（替代全局变量）
                            if (typeof window.projectDataBridge !== 'undefined') {
                                // 1. 原始标书文件
                                window.projectDataBridge.setFileInfo('originalTender', {
                                    fileName: step1Data.file_name,
                                    filePath: step1Data.file_path
                                });
                                console.log('[HITLConfigManager] 原始标书文件信息已保存:', step1Data.file_name);

                                // 2. 技术需求文件
                                if (step1Data.technical_file) {
                                    window.projectDataBridge.setFileInfo('technical', {
                                        fileName: step1Data.technical_file.filename,
                                        filePath: step1Data.technical_file.file_path,
                                        fileSize: step1Data.technical_file.file_size || 0
                                    });
                                    console.log('[HITLConfigManager] 技术需求文件信息已保存:', step1Data.technical_file.filename);
                                } else {
                                    console.log('[HITLConfigManager] 技术需求文件未保存');
                                }

                                // 3. 应答文件格式
                                if (step1Data.response_file) {
                                    window.projectDataBridge.setFileInfo('response', {
                                        fileName: step1Data.response_file.filename,
                                        filePath: step1Data.response_file.file_path,
                                        fileSize: step1Data.response_file.file_size || 0
                                    });
                                    console.log('[HITLConfigManager] 应答文件格式信息已保存:', step1Data.response_file.filename);
                                } else {
                                    console.log('[HITLConfigManager] 应答文件格式未保存');
                                }
                            }
                        }
                    } catch (parseError) {
                        console.error('[HITLConfigManager] 解析step1_data失败:', parseError);
                    }
                }

                // 【修改】主动加载所有Tab的数据
                console.log('[HITLConfigManager] 开始加载所有Tab数据...');
                console.log('[HITLConfigManager] loadFileInfo是否已定义:', typeof loadFileInfo);

                // 1. 加载应答文件格式
                if (typeof loadFileInfo === 'function') {
                    console.log('[HITLConfigManager] 加载应答文件信息...');
                    await loadFileInfo('response', hitlTask.hitl_task_id);
                } else {
                    console.error('[HITLConfigManager] loadFileInfo函数未定义，无法加载应答文件');
                }

                // 2. 加载技术需求文件
                if (typeof loadFileInfo === 'function') {
                    console.log('[HITLConfigManager] 加载技术需求文件...');
                    await loadFileInfo('technical', hitlTask.hitl_task_id);
                } else {
                    console.error('[HITLConfigManager] loadFileInfo函数未定义，无法加载技术需求文件');
                }

                // 2.5. 加载点对点应答完成文件
                if (typeof loadFileInfo === 'function') {
                    console.log('[HITLConfigManager] 加载点对点应答文件...');
                    await loadFileInfo('point_to_point', hitlTask.hitl_task_id);
                } else {
                    console.error('[HITLConfigManager] loadFileInfo函数未定义，无法加载点对点应答文件');
                }

                // 2.6. 加载技术方案完成文件
                if (typeof loadFileInfo === 'function') {
                    console.log('[HITLConfigManager] 加载技术方案文件...');
                    await loadFileInfo('tech_proposal', hitlTask.hitl_task_id);
                } else {
                    console.error('[HITLConfigManager] loadFileInfo函数未定义，无法加载技术方案文件');
                }

                // 2.7. 加载商务应答完成文件
                if (typeof loadFileInfo === 'function') {
                    console.log('[HITLConfigManager] 加载商务应答文件...');
                    await loadFileInfo('business_response', hitlTask.hitl_task_id);
                } else {
                    console.error('[HITLConfigManager] loadFileInfo函数未定义，无法加载商务应答文件');
                }

                // 3. 加载资格要求（qualifications）
                if (typeof loadRequirements === 'function') {
                    console.log('[HITLConfigManager] 加载资格要求...');
                    await loadRequirements(hitlTask.hitl_task_id, projectId);
                }

                // 4. 加载筛选后的段落
                if (typeof loadFilteredChunksData === 'function') {
                    console.log('[HITLConfigManager] 加载筛选段落...');
                    await loadFilteredChunksData(hitlTask.hitl_task_id);
                }

                console.log('[HITLConfigManager] HITL任务数据加载完成');
            } else {
                console.log('[HITLConfigManager] 该项目没有HITL任务');
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载HITL任务数据失败:', error);
        }
    },

    // 【新增】显示已上传的文件
    displayUploadedFile(fileName, filePath) {
        console.log('[HITLConfigManager] 显示已上传文件:', fileName);

        // 查找文件上传区域的元素
        const uploadSection = document.querySelector('.file-upload-section');
        const fileInput = document.getElementById('hitlFileInput');

        if (uploadSection) {
            // 创建文件显示元素
            let fileDisplay = uploadSection.querySelector('.uploaded-file-display');

            if (!fileDisplay) {
                fileDisplay = document.createElement('div');
                fileDisplay.className = 'uploaded-file-display alert alert-success d-flex align-items-center justify-content-between';
                fileDisplay.innerHTML = `
                    <div class="d-flex align-items-center">
                        <i class="bi bi-file-earmark-text-fill me-2"></i>
                        <span class="file-name"></span>
                    </div>
                    <span class="badge bg-success">已上传</span>
                `;

                // 插入到文件输入框之后
                if (fileInput && fileInput.parentNode) {
                    fileInput.parentNode.insertBefore(fileDisplay, fileInput.nextSibling);
                } else {
                    uploadSection.appendChild(fileDisplay);
                }
            }

            // 更新文件名
            const fileNameSpan = fileDisplay.querySelector('.file-name');
            if (fileNameSpan) {
                fileNameSpan.textContent = fileName;
            }

            fileDisplay.style.display = 'flex';

            // 隐藏文件输入框（因为已经有文件了）
            if (fileInput) {
                fileInput.style.display = 'none';
            }

            console.log('[HITLConfigManager] 文件显示已更新');
        }
    },

    // 更新模型选择器
    updateModelSelect(models) {
        const select = document.getElementById('hitlAiModel');
        if (!select) return;

        const currentValue = select.value;

        // 保持现有选项但更新状态
        Array.from(select.options).forEach(option => {
            const model = models.find(m => m.name === option.value);
            if (model) {
                const baseText = option.textContent.replace(' ✓', '').replace(' (未配置)', '');
                if (model.status === 'available') {
                    option.textContent = baseText + ' ✓';
                    option.disabled = false;
                } else if (model.status === 'no_api_key') {
                    option.textContent = baseText + ' (未配置)';
                    option.disabled = true;
                }
            }
        });

        // 恢复选择
        if (currentValue) {
            select.value = currentValue;
        }

        this.updateModelStatus();
    },

    // 更新模型状态显示
    updateModelStatus() {
        const select = document.getElementById('hitlAiModel');
        const statusDiv = document.getElementById('hitlModelStatus');
        const icon = document.getElementById('hitlModelStatusIcon');
        const text = document.getElementById('hitlModelStatusText');

        if (!select || !statusDiv) return;

        const selectedValue = select.value;

        if (selectedValue) {
            statusDiv.style.display = 'block';
            icon.innerHTML = '<i class="bi bi-check-circle text-success"></i>';
            text.textContent = '模型可用';
            text.className = 'text-success';
        } else {
            statusDiv.style.display = 'none';
        }
    },

    // 绑定事件
    bindEvents() {
        // 公司选择变化
        const companySelect = document.getElementById('hitlCompanySelect');
        if (companySelect) {
            companySelect.addEventListener('change', (e) => {
                this.currentCompanyId = e.target.value;
                const nameSpan = document.getElementById('hitlSelectedCompanyName');
                const selectedText = e.target.options[e.target.selectedIndex].text;
                nameSpan.textContent = e.target.value ? selectedText : '未选择';
                nameSpan.className = e.target.value ? 'text-primary fw-bold' : 'text-muted';

                console.log(`[HITLConfigManager] 选择公司: ${selectedText} (ID: ${e.target.value})`);

                // 重新加载项目列表
                if (this.currentCompanyId) {
                    this.loadProjects();
                }
            });
        }

        // 模型选择变化
        const modelSelect = document.getElementById('hitlAiModel');
        if (modelSelect) {
            modelSelect.addEventListener('change', (e) => {
                this.currentModel = e.target.value;
                this.updateModelStatus();
                console.log(`[HITLConfigManager] 选择模型: ${e.target.value}`);
            });
        }

        // 项目选择变化
        const projectSelect = document.getElementById('hitlProjectSelect');
        if (projectSelect) {
            projectSelect.addEventListener('change', async (e) => {
                this.selectedProjectId = e.target.value || null;
                this.currentProjectId = this.selectedProjectId;

                console.log(`[HITLConfigManager] 项目选择变更: ${this.selectedProjectId}`);

                if (this.selectedProjectId) {
                    // 加载项目详情
                    await this.loadProjectDetails(this.selectedProjectId);

                    // 【新增】自动跳转到步骤3，让用户可以看到加载的数据
                    this.navigateToStep3();
                } else {
                    // 选择"新建项目",清空表单
                    const projectInfo = document.getElementById('hitlProjectInfo');
                    if (projectInfo) projectInfo.style.display = 'none';

                    // 清空基本信息表单
                    ['projectName', 'projectNumber', 'tenderParty', 'tenderAgent',
                     'tenderMethod', 'tenderLocation', 'tenderDeadline', 'winnerCount'].forEach(id => {
                        const el = document.getElementById(id);
                        if (el) el.value = '';
                    });
                }
            });
            console.log('[HITLConfigManager] 项目选择器事件已绑定');
        }

        // 刷新项目按钮
        const refreshBtn = document.getElementById('refreshHitlProjectsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                console.log('[HITLConfigManager] 刷新项目列表');
                this.loadProjects();
            });
            console.log('[HITLConfigManager] 刷新按钮事件已绑定');
        }
    },

    // 获取当前配置（供其他模块使用）
    getConfig() {
        return {
            companyId: this.currentCompanyId,
            model: this.currentModel,
            projectId: this.currentProjectId  // 使用当前项目ID而非表单输入
        };
    },

    // 【新增】导航到步骤3
    navigateToStep3() {
        console.log('[HITLConfigManager] 导航到步骤3');

        // 隐藏步骤1和步骤2
        const step1Section = document.getElementById('chapterSelectionSection');
        const step2Section = document.getElementById('step2Section');
        const step3Section = document.getElementById('step3Section');

        if (step1Section) step1Section.style.display = 'none';
        if (step2Section) step2Section.style.display = 'none';
        if (step3Section) {
            step3Section.style.display = 'block';
            console.log('[HITLConfigManager] 已显示步骤3');
        }

        // 滚动到页面顶部，让用户看到步骤3
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

// 全局函数（供HTML调用）
function onHitlModelChange() {
    HITLConfigManager.updateModelStatus();
}

function refreshHitlModels() {
    HITLConfigManager.loadModels();
}

/**
 * 初始化模型选择器
 * - 从localStorage读取上次选择的模型
 * - 如果没有，默认选择 yuanjing-deepseek-v3（更适合智能提取）
 * - 保存用户选择到localStorage
 */
function initModelSelector() {
    const modelSelect = document.getElementById('hitlAiModel');
    if (!modelSelect) {
        console.warn('[initModelSelector] 未找到模型选择器');
        return;
    }

    // 从localStorage读取上次选择
    const STORAGE_KEY = 'hitl_selected_model';
    let savedModel = localStorage.getItem(STORAGE_KEY);

    // 如果没有保存的选择，使用智能默认值（DeepSeek-V3更适合提取任务）
    if (!savedModel) {
        savedModel = 'yuanjing-deepseek-v3';
        console.log('[initModelSelector] 首次使用，默认选择:', savedModel);
    } else {
        console.log('[initModelSelector] 恢复上次选择:', savedModel);
    }

    // 设置选中状态
    modelSelect.value = savedModel;

    // 监听变化，保存到localStorage
    modelSelect.addEventListener('change', function() {
        const selectedModel = this.value;
        localStorage.setItem(STORAGE_KEY, selectedModel);
        console.log('[initModelSelector] 模型已更改并保存:', selectedModel);
    });

    // 触发一次change事件，更新模型状态显示
    if (typeof onHitlModelChange === 'function') {
        onHitlModelChange();
    }
}

// 页面加载时初始化（使用已存在的DOMContentLoaded事件）
document.addEventListener('DOMContentLoaded', function() {
    console.log('[HITL] 初始化配置管理器');
    HITLConfigManager.init();

    // 初始化AI模型选择器
    initModelSelector();

    // Tab数据已在选择项目时自动加载，无需监听tab切换事件
});

/**
 * 跳转到点对点应答页面
 * 支持两种模式:
 * 1. 如果在首页(有 projectDataBridge),使用 Tab 切换 + 全局状态传递
 * 2. 如果在独立 HITL 页面,使用 URL 参数跳转(向后兼容)
 */
async function goToPointToPoint() {
    // 检测是否在首页环境(有 projectDataBridge)
    const isInIndexPage = typeof window.projectDataBridge !== 'undefined';

    if (isInIndexPage) {
        // 模式 1: Tab 切换模式 (首页内)
        console.log('[goToPointToPoint] 使用 Tab 切换模式');

        // 【修改】从 companyStateManager 读取数据（统一数据源）
        const companyData = window.companyStateManager.getSelectedCompany();
        const projectName = companyData?.project_name || '';
        const companyId = companyData?.company_id || '';
        const companyName = companyData?.company_name || '';
        const hitlTaskId = window.projectDataBridge.hitlTaskId || '';

        console.log('[goToPointToPoint] 跳转参数:', { projectName, companyId, companyName, hitlTaskId });

        // 【修复】使用技术需求文件
        const techFile = window.projectDataBridge.getFileInfo('technical');
        if (hitlTaskId && techFile?.fileName) {
            console.log('[goToPointToPoint] 使用技术需求文件:', techFile.fileName);

            // 设置到全局状态
            window.projectDataBridge.setTechnicalFile(
                hitlTaskId,
                techFile.fileName,
                techFile.fileSize || 0,
                `/api/tender-processing/download-technical-file/${hitlTaskId}`
            );
            console.log('[goToPointToPoint] 技术需求文件信息已设置到全局状态');
        } else {
            console.warn('[goToPointToPoint] 技术需求文件未保存,请先在技术需求Tab保存章节');
        }

        // 切换到点对点应答 Tab
        const pointToPointTab = document.querySelector('[data-bs-target="#point-to-point"]');
        if (pointToPointTab) {
            const tab = new bootstrap.Tab(pointToPointTab);
            tab.show();

            // 触发自定义事件通知点对点组件加载数据
            window.dispatchEvent(new CustomEvent('loadPointToPoint', {
                detail: {
                    fromHITL: true,
                    taskId: hitlTaskId
                }
            }));

            console.log('[goToPointToPoint] 已切换到点对点应答 Tab');
        } else {
            console.error('[goToPointToPoint] 未找到点对点应答 Tab');
        }
    } else {
        // 模式 2: URL 参数跳转模式 (独立 HITL 页面)
        console.log('[goToPointToPoint] 使用 URL 参数跳转模式');

        // 构建URL参数
        const params = new URLSearchParams();
        if (projectName) params.append('project_name', projectName);
        if (companyId) params.append('company_id', companyId);
        if (companyName) params.append('company_name', companyName);
        if (hitlTaskId) params.append('hitl_task_id', hitlTaskId);

        // 【修复】使用技术需求文件
        if (hitlTaskId && window.technicalFileName) {
            console.log('[goToPointToPoint] 使用技术需求文件:', window.technicalFileName);

            // 将技术需求文件信息添加到URL参数
            params.append('technical_file_name', window.technicalFileName);
            params.append('technical_file_size', window.technicalFileSize || '0');
            params.append('technical_file_url', `/api/tender-processing/download-technical-file/${hitlTaskId}`);
            console.log('[goToPointToPoint] 技术需求文件信息已添加到URL参数');
        } else {
            console.warn('[goToPointToPoint] 技术需求文件未保存,请先在技术需求Tab保存章节');
        }

        // 跳转到首页的点对点应答标签页
        window.location.href = `/?${params.toString()}#point-to-point`;
    }
}

/**
 * 跳转到技术方案编写页面
 * 支持两种模式:
 * 1. 如果在首页(有 projectDataBridge),使用 Tab 切换 + 全局状态传递
 * 2. 如果在独立 HITL 页面,使用 URL 参数跳转(向后兼容)
 */
async function goToTechProposal() {
    // 检测是否在首页环境(有 projectDataBridge)
    const isInIndexPage = typeof window.projectDataBridge !== 'undefined';

    if (isInIndexPage) {
        // 模式 1: Tab 切换模式 (首页内)
        console.log('[goToTechProposal] 使用 Tab 切换模式');

        // 【修改】从 companyStateManager 读取数据（统一数据源）
        const companyData = window.companyStateManager.getSelectedCompany();
        const projectName = companyData?.project_name || '';
        const companyId = companyData?.company_id || '';
        const companyName = companyData?.company_name || '';
        const hitlTaskId = window.projectDataBridge.hitlTaskId || '';

        console.log('[goToTechProposal] 跳转参数:', { projectName, companyId, companyName, hitlTaskId });

        // 【修复】使用技术需求文件
        const techFile = window.projectDataBridge.getFileInfo('technical');
        if (hitlTaskId && techFile?.fileName) {
            console.log('[goToTechProposal] 使用技术需求文件:', techFile.fileName);

            // 设置到全局状态
            window.projectDataBridge.setTechnicalFile(
                hitlTaskId,
                techFile.fileName,
                techFile.fileSize || 0,
                `/api/tender-processing/download-technical-file/${hitlTaskId}`
            );
            console.log('[goToTechProposal] 技术需求文件信息已设置到全局状态');
        } else {
            console.warn('[goToTechProposal] 技术需求文件未保存,请先在技术需求Tab保存章节');
        }

        // 切换到技术方案 Tab
        const techProposalTab = document.querySelector('[data-bs-target="#tech-proposal"]');
        if (techProposalTab) {
            const tab = new bootstrap.Tab(techProposalTab);
            tab.show();

            // 触发自定义事件通知技术方案组件加载数据
            window.dispatchEvent(new CustomEvent('loadTechnicalProposal', {
                detail: {
                    fromHITL: true,
                    taskId: hitlTaskId
                }
            }));

            console.log('[goToTechProposal] 已切换到技术方案 Tab');
        } else {
            console.error('[goToTechProposal] 未找到技术方案 Tab');
        }
    } else {
        // 模式 2: URL 参数跳转模式 (独立 HITL 页面)
        console.log('[goToTechProposal] 使用 URL 参数跳转模式');

        // 构建URL参数
        const params = new URLSearchParams();
        if (projectName) params.append('project_name', projectName);
        if (companyId) params.append('company_id', companyId);
        if (companyName) params.append('company_name', companyName);
        if (hitlTaskId) params.append('hitl_task_id', hitlTaskId);

        // 【修复】使用技术需求文件
        if (hitlTaskId && window.technicalFileName) {
            console.log('[goToTechProposal] 使用技术需求文件:', window.technicalFileName);

            // 将技术需求文件信息添加到URL参数
            params.append('technical_file_name', window.technicalFileName);
            params.append('technical_file_size', window.technicalFileSize || '0');
            params.append('technical_file_url', `/api/tender-processing/download-technical-file/${hitlTaskId}`);
            console.log('[goToTechProposal] 技术需求文件信息已添加到URL参数');
        } else {
            console.warn('[goToTechProposal] 技术需求文件未保存,请先在技术需求Tab保存章节');
        }

        // 跳转到首页的技术方案生成标签页
        window.location.href = `/?${params.toString()}#tech-proposal`;
    }
}

/**
 * 【新增】跳转到商务应答页面
 * 支持两种模式:
 * 1. 如果在首页(有 projectDataBridge),使用 Tab 切换 + 全局状态传递
 * 2. 如果在独立 HITL 页面,使用 URL 参数跳转(向后兼容)
 */
async function goToBusinessResponse() {
    // 检测是否在首页环境(有 projectDataBridge)
    const isInIndexPage = typeof window.projectDataBridge !== 'undefined';

    if (isInIndexPage) {
        // 模式 1: Tab 切换模式 (首页内)
        console.log('[goToBusinessResponse] 使用 Tab 切换模式');

        // 【修改】从 companyStateManager 读取数据（统一数据源）
        const companyData = window.companyStateManager.getSelectedCompany();
        const projectName = companyData?.project_name || '';
        const companyId = companyData?.company_id || '';
        const companyName = companyData?.company_name || '';
        const hitlTaskId = window.projectDataBridge.hitlTaskId || '';

        console.log('[goToBusinessResponse] 跳转参数:', { projectName, companyId, companyName, hitlTaskId });

        // 【修复】使用应答文件格式
        const responseFile = window.projectDataBridge.getFileInfo('response');
        if (hitlTaskId && responseFile?.fileName) {
            console.log('[goToBusinessResponse] 使用应答文件格式:', responseFile.fileName);

            // 设置到 projectDataBridge 供商务应答使用
            window.projectDataBridge.setFileInfo('business', {
                fileUrl: `/api/tender-processing/download-response-file/${hitlTaskId}`,
                fileName: responseFile.fileName
            });
            console.log('[goToBusinessResponse] 应答文件格式信息已设置');
        } else {
            console.warn('[goToBusinessResponse] 应答文件格式未保存,请先在应答文件格式Tab保存章节');
        }

        // 切换到商务应答 Tab
        const businessResponseTab = document.querySelector('[data-bs-target="#business-response"]');
        if (businessResponseTab) {
            const tab = new bootstrap.Tab(businessResponseTab);
            tab.show();

            // 触发自定义事件通知商务应答组件加载数据
            window.dispatchEvent(new CustomEvent('loadBusinessResponse', {
                detail: {
                    fromHITL: true,
                    taskId: hitlTaskId
                }
            }));

            console.log('[goToBusinessResponse] 已切换到商务应答 Tab');
        } else {
            console.error('[goToBusinessResponse] 未找到商务应答 Tab');
        }
    } else {
        // 模式 2: URL 参数跳转模式 (独立 HITL 页面)
        console.log('[goToBusinessResponse] 使用 URL 参数跳转模式');

        // 构建URL参数
        const params = new URLSearchParams();
        if (projectName) params.append('project_name', projectName);
        if (companyId) params.append('company_id', companyId);
        if (companyName) params.append('company_name', companyName);
        if (hitlTaskId) params.append('hitl_task_id', hitlTaskId);

        // 【修复】使用应答文件格式
        if (hitlTaskId && window.responseFileName) {
            console.log('[goToBusinessResponse] 使用应答文件格式:', window.responseFileName);

            // 将应答文件格式信息添加到URL参数
            params.append('business_file_name', window.responseFileName);
            params.append('business_file_url', `/api/tender-processing/download-response-file/${hitlTaskId}`);
            console.log('[goToBusinessResponse] 应答文件格式信息已添加到URL参数');
        } else {
            console.warn('[goToBusinessResponse] 应答文件格式未保存,请先在应答文件格式Tab保存章节');
        }

        // 跳转到首页的商务应答标签页
        window.location.href = `/?${params.toString()}#business-response`;
    }
}
