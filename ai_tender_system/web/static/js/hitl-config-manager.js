/**
 * HITL 配置管理器
 * 用于投标管理页面的配置管理、项目选择、公司选择、AI模型选择等功能
 * 同时包含快捷跳转函数(支持双模式: Tab切换/URL跳转)
 */

// HITL页面的模型和公司管理
const HITLConfigManager = {
    // ✅ 加载锁状态变量
    _loadingProjectId: null,     // 正在加载的项目ID
    _lastLoadedProjectId: null,  // 上次加载的项目ID
    _isLoadingFromOverview: false, // 是否正在从总览页面加载

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
            // ✅ 优先从 globalState 获取模型列表
            if (window.globalState && window.globalState.getAvailableModels().length > 0) {
                const models = window.globalState.getAvailableModels();
                this.updateModelSelect(models);
                console.log(`[HITLConfigManager] 从 globalState 加载了 ${models.length} 个AI模型`);
                return;
            }

            // 如果 globalState 没有数据，从API加载
            const response = await fetch('/api/models');
            const data = await response.json();

            if (data.success && data.models) {
                // ✅ 保存到 globalState
                if (window.globalState) {
                    window.globalState.setAvailableModels(data.models);
                }

                this.updateModelSelect(data.models);
                console.log(`[HITLConfigManager] 从API加载了 ${data.count} 个AI模型`);
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载模型列表失败:', error);
        }
    },

    // 加载项目列表
    async loadProjects() {
        try {
            console.log('[HITLConfigManager] 开始加载项目列表...');
            // ✅ 从 globalState 读取公司ID
            const companyId = window.globalState.getCompanyId();
            const url = companyId
                ? `/api/tender-projects?company_id=${companyId}`
                : '/api/tender-projects';

            const response = await fetch(url);
            const data = await response.json();

            const select = document.getElementById('hitlProjectSelect');

            // ✅ 保存当前选中的项目ID,避免触发change事件
            const currentValue = select.value;

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

                // ✅ 恢复之前选中的值 (如果存在)
                if (currentValue) {
                    select.value = currentValue;
                    console.log('[HITLConfigManager] 已恢复项目选择器值:', currentValue);
                }
            } else {
                console.log('[HITLConfigManager] 没有找到项目数据');
            }
        } catch (error) {
            console.error('[HITLConfigManager] 加载项目列表失败:', error);
        }
    },

    // 自动填充被授权人信息
    async autoFillAuthorizedPerson(companyId) {
        try {
            console.log('[HITLConfigManager] 自动填充被授权人信息, 公司ID:', companyId);

            const response = await fetch(`/api/companies/${companyId}`);
            const data = await response.json();

            if (data.success && data.data) {
                const company = data.data;

                // 填充被授权人字段
                const authorizedPersonName = document.getElementById('authorizedPersonName');
                const authorizedPersonId = document.getElementById('authorizedPersonId');
                const authorizedPersonPosition = document.getElementById('authorizedPersonPosition');

                if (authorizedPersonName) {
                    authorizedPersonName.value = company.authorized_person_name || '';
                }
                if (authorizedPersonId) {
                    authorizedPersonId.value = company.authorized_person_id || '';
                }
                if (authorizedPersonPosition) {
                    authorizedPersonPosition.value = company.authorized_person_position || '';
                }

                console.log('[HITLConfigManager] 被授权人信息已自动填充:', {
                    name: company.authorized_person_name,
                    position: company.authorized_person_position
                });
            }
        } catch (error) {
            console.error('[HITLConfigManager] 自动填充被授权人信息失败:', error);
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

                        // 更新公司名称显示并同步到 globalState
                        if (companyNameSpan) {
                            const companyName = this.getSelectedCompanyName(); // ✅ 使用辅助方法
                            companyNameSpan.textContent = companyName;
                            companyNameSpan.className = 'text-primary fw-bold';

                            // ✅ 同步到 globalState
                            window.globalState.setCompany(project.company_id, companyName);
                        }

                        console.log('[HITLConfigManager] 已设置公司:', project.company_id);
                    }
                }

                // 填充基本信息表单 (对象映射驱动，避免重复代码)
                const formFieldMapping = {
                    'projectName': 'project_name',
                    'projectNumber': 'project_number',
                    'tenderParty': 'tenderer',
                    'tenderAgent': 'agency',
                    'tenderMethod': 'bidding_method',
                    'tenderLocation': 'bidding_location',
                    'tenderDeadline': 'bidding_time',
                    'winnerCount': 'winner_count',
                    'authorizedPersonName': 'authorized_person_name',
                    'authorizedPersonId': 'authorized_person_id',
                    'authorizedPersonPosition': 'authorized_person_position'
                };

                Object.entries(formFieldMapping).forEach(([elementId, projectKey]) => {
                    const element = document.getElementById(elementId);
                    if (element) element.value = project[projectKey] || '';
                });

                // 显示项目信息提示
                const projectInfo = document.getElementById('hitlProjectInfo');
                const projectName = document.getElementById('hitlProjectName');
                if (projectInfo && projectName) {
                    projectName.textContent = `已加载: ${project.project_name}`;
                    projectInfo.style.display = 'block';
                }

                // ✅ 保存到 globalState（统一数据源）
                if (typeof window.globalState !== 'undefined') {
                    // ✅ 使用辅助方法获取公司名称
                    const companyName = this.getSelectedCompanyName();

                    // ✅ 使用 setBulk 批量设置公司和项目信息
                    window.globalState.setBulk({
                        company: {
                            id: project.company_id,
                            name: companyName
                        },
                        project: {
                            id: projectId,
                            name: project.project_name
                        }
                    });

                    console.log('[HITLConfigManager] 已保存到 globalState:', {
                        projectId: projectId,
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

                // ✅ 保存 HITL 任务 ID 到 globalState
                if (typeof window.globalState !== 'undefined') {
                    window.globalState.setHitlTaskId(hitlTask.hitl_task_id);
                }

                // ✅ 显示原标书文件信息并保存到 globalState
                if (hitlTask.step1_data) {
                    try {
                        const step1Data = typeof hitlTask.step1_data === 'string'
                            ? JSON.parse(hitlTask.step1_data)
                            : hitlTask.step1_data;

                        if (step1Data.file_path && step1Data.file_name) {
                            console.log('[HITLConfigManager] 找到原标书文件:', step1Data.file_name);
                            this.displayUploadedFile(step1Data.file_name, step1Data.file_path);

                            // ✅ 使用 setBulk 批量保存三种文件信息到 globalState
                            if (typeof window.globalState !== 'undefined') {
                                const filesToSet = {};

                                // 1. 原始标书文件
                                filesToSet.originalTender = {
                                    fileName: step1Data.file_name,
                                    filePath: step1Data.file_path
                                };
                                console.log('[HITLConfigManager] 准备保存原始标书文件:', step1Data.file_name);

                                // 2. 技术需求文件
                                if (step1Data.technical_file) {
                                    filesToSet.technical = {
                                        fileName: step1Data.technical_file.filename,
                                        filePath: step1Data.technical_file.file_path,
                                        fileSize: step1Data.technical_file.file_size || 0,
                                        fileUrl: `/api/tender-processing/download-technical-file/${hitlTask.hitl_task_id}`
                                    };
                                    console.log('[HITLConfigManager] 准备保存技术需求文件:', step1Data.technical_file.filename);
                                }

                                // 3. 应答文件格式（用于商务应答）
                                if (step1Data.response_file) {
                                    filesToSet.business = {
                                        fileName: step1Data.response_file.filename,
                                        filePath: step1Data.response_file.file_path,
                                        fileSize: step1Data.response_file.file_size || 0,
                                        fileUrl: `/api/tender-processing/download-response-file/${hitlTask.hitl_task_id}`
                                    };
                                    console.log('[HITLConfigManager] 准备保存应答文件格式:', step1Data.response_file.filename);
                                }

                                // 批量设置文件
                                window.globalState.setBulk({
                                    files: filesToSet,
                                    hitlTaskId: hitlTask.hitl_task_id
                                });
                                console.log('[HITLConfigManager] 所有文件信息已通过 setBulk 保存到 globalState');
                            }
                        }
                    } catch (parseError) {
                        console.error('[HITLConfigManager] 解析step1_data失败:', parseError);
                    }
                }

                // 【修改】主动加载所有Tab的数据 (数组驱动，避免重复代码)
                console.log('[HITLConfigManager] 开始加载所有Tab数据...');

                // 定义需要加载的文件类型
                const fileTypesToLoad = [
                    { type: 'response', name: '应答文件' },
                    { type: 'technical', name: '技术需求文件' },
                    { type: 'point_to_point', name: '点对点应答文件' },
                    { type: 'tech_proposal', name: '技术方案文件' },
                    { type: 'business_response', name: '商务应答文件' }
                ];

                // 批量加载文件信息
                if (typeof loadFileInfo === 'function') {
                    for (const {type, name} of fileTypesToLoad) {
                        console.log(`[HITLConfigManager] 加载${name}...`);
                        await loadFileInfo(type, hitlTask.hitl_task_id);
                    }
                } else {
                    console.error('[HITLConfigManager] loadFileInfo函数未定义，无法加载文件信息');
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

                // 【新增】5. 加载历史章节列表
                if (window.chapterSelectionManager && window.chapterSelectionManager.loadHistoricalChapters) {
                    console.log('[HITLConfigManager] 加载历史章节列表...');
                    await window.chapterSelectionManager.loadHistoricalChapters(hitlTask.hitl_task_id);
                } else {
                    console.warn('[HITLConfigManager] window.chapterSelectionManager 未定义或缺少 loadHistoricalChapters 方法');
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
        const uploadSection = document.querySelector('#uploadSection');
        const fileInput = document.getElementById('tenderDocFile');

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
            companySelect.addEventListener('change', async (e) => {
                const companyId = e.target.value;
                const companyName = e.target.options[e.target.selectedIndex].text;

                // ✅ 同步到 globalState
                if (companyId) {
                    window.globalState.setCompany(companyId, companyName);
                } else {
                    window.globalState.clearCompany();
                }

                // UI更新
                const nameSpan = document.getElementById('hitlSelectedCompanyName');
                nameSpan.textContent = companyId ? companyName : '未选择';
                nameSpan.className = companyId ? 'text-primary fw-bold' : 'text-muted';

                console.log(`[HITLConfigManager] 选择公司: ${companyName} (ID: ${companyId})`);

                // 自动填充被授权人信息
                if (companyId) {
                    await this.autoFillAuthorizedPerson(companyId);
                    // 重新加载项目列表
                    this.loadProjects();
                }
            });
        }

        // 模型选择变化
        const modelSelect = document.getElementById('hitlAiModel');
        if (modelSelect) {
            modelSelect.addEventListener('change', (e) => {
                // ✅ 保存到 globalState
                if (window.globalState) {
                    window.globalState.setSelectedModel(e.target.value);
                }

                this.updateModelStatus();
                console.log(`[HITLConfigManager] 选择模型: ${e.target.value}`);
            });
        }

        // 项目选择变化
        const projectSelect = document.getElementById('hitlProjectSelect');
        if (projectSelect) {
            projectSelect.addEventListener('change', async (e) => {
                const projectId = e.target.value || null;

                console.log(`[HITLConfigManager] 项目选择变更: ${projectId}`);

                // ✅ 如果正在从总览页面加载,跳过 (总览页面会直接调用 loadProjectDetails)
                if (this._isLoadingFromOverview) {
                    console.log('[HITLConfigManager] 正在从总览页面加载,跳过change处理');
                    return;
                }

                // ✅ 防止重复加载同一个项目
                if (projectId && this._loadingProjectId === projectId) {
                    console.log('[HITLConfigManager] 项目正在加载中，跳过重复请求:', projectId);
                    return;
                }

                if (projectId) {
                    // 设置加载锁
                    this._loadingProjectId = projectId;
                    try {
                        // 加载项目详情（包括章节列表），会自动同步到 globalState
                        await this.loadProjectDetails(projectId);

                        // 记录最后加载的项目
                        this._lastLoadedProjectId = projectId;

                        // 【新增】加载完成后导航到步骤3
                        this.navigateToStep3();
                    } finally {
                        // 释放加载锁
                        this._loadingProjectId = null;
                    }
                } else {
                    // 选择"新建项目",刷新页面
                    console.log('[HITLConfigManager] 刷新页面以重置状态');
                    location.reload();
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

        // 【新增】监听从项目总览页面跳转过来的事件
        document.addEventListener('loadProjectFromOverview', async (e) => {
            const {projectId, companyId, companyName, projectName} = e.detail;
            console.log('[HITLConfigManager] 接收到项目总览跳转事件:', e.detail);

            // ✅ 设置标志位,防止change监听器重复处理
            this._isLoadingFromOverview = true;

            try {
                // 1. 设置公司选择器并同步到 globalState
                if (companyId) {
                    const companySelect = document.getElementById('hitlCompanySelect');
                    if (companySelect) {
                        companySelect.value = companyId;

                        // ✅ 同步到 globalState
                        window.globalState.setCompany(companyId, companyName);

                        const nameSpan = document.getElementById('hitlSelectedCompanyName');
                        if (nameSpan) {
                            nameSpan.textContent = companyName || '';
                            nameSpan.className = 'text-primary fw-bold';
                        }
                        console.log('[HITLConfigManager] 已设置公司选择器:', companyId, companyName);
                    }
                }

                // 2. 重新加载项目列表（确保下拉框有最新数据）
                await this.loadProjects();

                // 3. 设置项目选择器的值 (但不触发change事件)
                if (projectId) {
                    const projectSelect = document.getElementById('hitlProjectSelect');
                    if (projectSelect) {
                        projectSelect.value = projectId;
                        console.log('[HITLConfigManager] 已设置项目选择器值:', projectId);
                    }

                    // ✅ 防止重复加载
                    if (this._loadingProjectId === projectId) {
                        console.log('[HITLConfigManager] 项目正在加载中，跳过:', projectId);
                        return;
                    }

                    // 4. 直接调用加载逻辑 (不通过change事件)
                    this._loadingProjectId = projectId;
                    try {
                        console.log('[HITLConfigManager] 开始加载项目详情 (从总览页面)');
                        await this.loadProjectDetails(projectId);
                        this._lastLoadedProjectId = projectId;
                        this.navigateToStep3();
                        console.log('[HITLConfigManager] 项目加载完成 (从总览页面)');
                    } finally {
                        this._loadingProjectId = null;
                    }
                }
            } finally {
                // ✅ 重置标志位
                this._isLoadingFromOverview = false;
            }
        });
        console.log('[HITLConfigManager] 项目总览跳转事件监听器已绑定');
    },

    // 【新增】获取当前选中的公司名称（辅助方法，消除重复代码）
    getSelectedCompanyName() {
        const select = document.getElementById('hitlCompanySelect');
        if (select && select.value) {
            const option = select.options[select.selectedIndex];
            return option ? option.text : '';
        }
        return '';
    },

    // 获取当前配置（供其他模块使用）
    getConfig() {
        // ✅ 从 globalState 读取所有状态
        return {
            companyId: window.globalState.getCompanyId(),
            model: window.globalState.getSelectedModel(),
            projectId: window.globalState.getProjectId()
        };
    },

    // 【新增】导航到步骤3
    navigateToStep3() {
        console.log('[HITLConfigManager] 导航到步骤3');

        const step1Section = document.getElementById('chapterSelectionSection');
        const step2Section = document.getElementById('step2Section');
        const step3Section = document.getElementById('step3Section');
        const uploadSection = document.getElementById('uploadSection');

        // ✅ 保持步骤1（章节选择）显示
        if (step1Section) step1Section.style.display = 'block';

        // ✅ 隐藏上传区域（历史项目已有文件）
        if (uploadSection) uploadSection.style.display = 'none';

        // 隐藏步骤2（已废弃）
        if (step2Section) step2Section.style.display = 'none';

        // 显示步骤3
        if (step3Section) {
            step3Section.style.display = 'block';
            console.log('[HITLConfigManager] 已显示步骤3');
        }

        // 滚动到步骤3位置
        if (step3Section) {
            step3Section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
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
 * 通用Tab跳转函数（消除重复代码）
 * @param {Object} config - 跳转配置
 * @param {string} config.tabSelector - Tab选择器，如 '[data-bs-target="#point-to-point"]'
 * @param {string} config.fileType - 文件类型：'technical', 'business', 'originalTender'
 * @param {string} config.eventName - 自定义事件名称，如 'loadPointToPoint'
 * @param {string} config.apiEndpoint - API端点（可选），用于获取文件信息
 * @param {string} config.urlHash - URL哈希值，如 '#point-to-point'
 * @param {string} config.logPrefix - 日志前缀，如 '[goToPointToPoint]'
 */
async function navigateToTabImpl(config) {
    const isInIndexPage = typeof window.globalState !== 'undefined';

    if (isInIndexPage) {
        // 模式 1: Tab 切换模式 (首页内)
        console.log(`${config.logPrefix} 使用 Tab 切换模式`);

        // ✅ 使用 globalState 读取数据
        const company = window.globalState.getCompany();
        const project = window.globalState.getProject();
        const projectName = project.name || '';
        const companyId = company.id || '';
        const companyName = company.name || '';
        const hitlTaskId = window.globalState.getHitlTaskId() || '';

        console.log(`${config.logPrefix} 跳转参数:`, { projectName, companyId, companyName, hitlTaskId });

        // ✅ 获取文件信息 - 支持 API fallback
        let fileData = window.globalState.getFile(config.fileType);

        // 如果 globalState 中没有数据且提供了 API 端点，从 API 获取
        if ((!fileData || !fileData.fileName) && hitlTaskId && config.apiEndpoint) {
            console.log(`${config.logPrefix} globalState 中无文件,尝试从 API 获取`);

            try {
                const response = await fetch(`${config.apiEndpoint}/${hitlTaskId}`);
                const data = await response.json();

                // ✅ 修复：支持两种API响应格式
                // 格式1: technical-file-info 返回 { success, has_file, file: {...} }
                // 格式2: response-file-info 返回 { success, has_file, filename, file_size, download_url }
                if (data.success && data.has_file) {
                    // 优先使用嵌套的 data.file 对象 (technical-file-info)
                    if (data.file) {
                        fileData = {
                            fileName: data.file.filename,
                            fileSize: data.file.file_size || 0,
                            filePath: data.file.file_path,
                            fileUrl: `${config.apiEndpoint.replace('-info', '')}/download-${config.fileType}-file/${hitlTaskId}`
                        };
                    }
                    // 回退到扁平结构 (response-file-info)
                    else if (data.filename) {
                        fileData = {
                            fileName: data.filename,
                            fileSize: data.file_size || 0,
                            filePath: null,  // response-file-info不返回file_path
                            fileUrl: data.download_url || `${config.apiEndpoint.replace('-info', '')}/download-${config.fileType}-file/${hitlTaskId}`
                        };
                    }

                    if (fileData && fileData.fileName) {
                        // ✅ 保存到 globalState 供后续使用
                        window.globalState.setFile(config.fileType, fileData);
                        console.log(`${config.logPrefix} 从 API 获取到文件:`, fileData.fileName);
                    } else {
                        console.warn(`${config.logPrefix} API响应中缺少filename字段`);
                    }
                } else {
                    console.warn(`${config.logPrefix} API 返回无文件数据`);
                }
            } catch (error) {
                console.error(`${config.logPrefix} 从 API 获取文件失败:`, error);
            }
        }

        // ✅ 使用 setBulk 批量设置状态
        if (hitlTaskId && fileData?.fileName) {
            console.log(`${config.logPrefix} 使用文件:`, fileData.fileName);

            window.globalState.setBulk({
                company: { id: companyId, name: companyName },
                project: { id: project.id, name: projectName },
                files: {
                    [config.fileType]: {
                        fileName: fileData.fileName,
                        fileSize: fileData.fileSize || 0,
                        fileUrl: fileData.fileUrl,
                        filePath: fileData.filePath
                    }
                },
                hitlTaskId: hitlTaskId
            });
            console.log(`${config.logPrefix} 所有状态已通过 setBulk 设置完成`);
        } else {
            console.warn(`${config.logPrefix} 文件未找到,请先上传相关文件`);
        }

        // 切换到目标 Tab
        const targetTab = document.querySelector(config.tabSelector);
        if (targetTab) {
            const tab = new bootstrap.Tab(targetTab);
            tab.show();

            // 派发自定义事件
            window.dispatchEvent(new CustomEvent(config.eventName, {
                detail: {
                    fromHITL: true,
                    taskId: hitlTaskId
                }
            }));

            console.log(`${config.logPrefix} 已切换到 Tab`);
        } else {
            console.error(`${config.logPrefix} 未找到 Tab:`, config.tabSelector);
        }
    } else {
        // 模式 2: URL 参数跳转模式 (独立 HITL 页面，向后兼容)
        console.log(`${config.logPrefix} 使用 URL 参数跳转模式`);

        // 构建URL参数
        const params = new URLSearchParams();
        const company = window.globalState?.getCompany() || {};
        const project = window.globalState?.getProject() || {};
        const hitlTaskId = window.globalState?.getHitlTaskId();

        if (project.name) params.append('project_name', project.name);
        if (company.id) params.append('company_id', company.id);
        if (company.name) params.append('company_name', company.name);
        if (hitlTaskId) params.append('hitl_task_id', hitlTaskId);

        // 跳转到首页
        window.location.href = `/?${params.toString()}${config.urlHash}`;
    }
}

/**
 * 跳转到点对点应答页面
 * 支持两种模式:
 * 1. 如果在首页(有 globalState),使用 Tab 切换 + 全局状态传递
 * 2. 如果在独立 HITL 页面,使用 URL 参数跳转(向后兼容)
 */
async function goToPointToPoint() {
    return navigateToTabImpl({
        tabSelector: '[data-bs-target="#point-to-point"]',
        fileType: 'technical',
        eventName: 'loadPointToPoint',
        apiEndpoint: '/api/tender-processing/technical-file-info',
        urlHash: '#point-to-point',
        logPrefix: '[goToPointToPoint]'
    });
}

/**
 * 跳转到技术方案编写页面
 * 支持两种模式:
 * 1. 如果在首页(有 globalState),使用 Tab 切换 + 全局状态传递
 * 2. 如果在独立 HITL 页面,使用 URL 参数跳转(向后兼容)
 */
async function goToTechProposal() {
    return navigateToTabImpl({
        tabSelector: '[data-bs-target="#tech-proposal"]',
        fileType: 'technical',
        eventName: 'loadTechnicalProposal',
        apiEndpoint: '/api/tender-processing/technical-file-info',
        urlHash: '#tech-proposal',
        logPrefix: '[goToTechProposal]'
    });
}

/**
 * 跳转到商务应答页面
 * 支持两种模式:
 * 1. 如果在首页(有 globalState),使用 Tab 切换 + 全局状态传递
 * 2. 如果在独立 HITL 页面,使用 URL 参数跳转(向后兼容)
 */
async function goToBusinessResponse() {
    return navigateToTabImpl({
        tabSelector: '[data-bs-target="#business-response"]',
        fileType: 'business',
        eventName: 'loadBusinessResponse',
        apiEndpoint: '/api/tender-processing/response-file-info',
        urlHash: '#business-response',
        logPrefix: '[goToBusinessResponse]'
    });
}
