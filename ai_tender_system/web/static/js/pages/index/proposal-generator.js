/**
 * 技术方案生成模块 - 前端交互管理
 * 负责技术方案生成的文件上传、配置管理和结果展示
 */

class ProposalGenerator {
    constructor() {
        this.isGenerating = false;
        this.currentController = null;
        this.progressInterval = null;

        this.init();
    }

    /**
     * 初始化生成器
     */
    init() {
        this.bindElements();
        this.bindEvents();
        this.loadCompanies();
        this.parseUrlParams(); // 解析URL参数并自动填充
    }

    /**
     * 绑定DOM元素
     */
    bindElements() {
        // 表单和文件输入
        this.techProposalForm = document.getElementById('techProposalForm');
        this.techTenderFileInput = document.getElementById('techTenderFileInput');
        this.productFileInput = document.getElementById('productFileInput');
        this.outputPrefix = document.getElementById('outputPrefix');

        // 文件信息显示
        this.techTenderFileInfo = document.getElementById('techTenderFileInfo');
        this.techTenderFileName = document.getElementById('techTenderFileName');
        this.productFileInfo = document.getElementById('productFileInfo');
        this.productFileName = document.getElementById('productFileName');

        // 按钮
        this.generateProposalBtn = document.getElementById('generateProposalBtn');

        // 公司选择
        this.techCompanySelect = document.getElementById('techCompanySelect');

        // 进度和结果
        this.techProgressBar = document.getElementById('techProgressBar');
        this.techResultArea = document.getElementById('techResultArea');
        this.techErrorArea = document.getElementById('techErrorArea');
        this.techDownloadArea = document.getElementById('techDownloadArea');
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 招标文件选择
        if (this.techTenderFileInput) {
            this.techTenderFileInput.addEventListener('change', () => {
                this.handleTenderFileSelect();
            });
        }

        // 产品文件选择
        if (this.productFileInput) {
            this.productFileInput.addEventListener('change', () => {
                this.handleProductFileSelect();
            });
        }

        // 表单提交
        if (this.techProposalForm) {
            this.techProposalForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitTechProposal();
            });
        }

        // 文件上传区域点击事件
        const techTenderUpload = document.getElementById('techTenderUpload');
        const productUpload = document.getElementById('productUpload');

        if (techTenderUpload) {
            techTenderUpload.addEventListener('click', () => {
                if (this.techTenderFileInput) {
                    this.techTenderFileInput.click();
                }
            });
        }

        if (productUpload) {
            productUpload.addEventListener('click', () => {
                if (this.productFileInput) {
                    this.productFileInput.click();
                }
            });
        }

        // 监听公司状态变化,同步到下拉框
        window.addEventListener('companyChanged', (e) => {
            if (e.detail && e.detail.company_id && this.techCompanySelect) {
                console.log('[ProposalGenerator] 收到公司变化事件:', e.detail);
                this.techCompanySelect.value = e.detail.company_id;
            }
        });
    }

    /**
     * 处理招标文件选择
     */
    handleTenderFileSelect() {
        const file = this.techTenderFileInput.files[0];
        if (file) {
            if (this.validateFile(file, '招标文件')) {
                this.techTenderFileName.textContent = file.name;
                this.techTenderFileInfo.classList.remove('d-none');
                this.checkFormReady();
            }
        }
    }

    /**
     * 处理产品文件选择
     */
    handleProductFileSelect() {
        const file = this.productFileInput.files[0];
        if (file) {
            if (this.validateFile(file, '产品文件')) {
                this.productFileName.textContent = file.name;
                this.productFileInfo.classList.remove('d-none');
                this.checkFormReady();
            }
        }
    }

    /**
     * 验证文件
     */
    validateFile(file, fileType) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/pdf'
        ];

        // 检查文件大小
        if (file.size > maxSize) {
            window.notifications?.error(`${fileType}大小不能超过50MB`);
            return false;
        }

        // 检查文件类型
        if (!allowedTypes.includes(file.type)) {
            window.notifications?.error(`${fileType}只支持Word文档(.docx, .doc)和PDF文件`);
            return false;
        }

        return true;
    }

    /**
     * 检查表单是否就绪
     */
    checkFormReady() {
        const hasTenderFile = this.techTenderFileInput && this.techTenderFileInput.files.length > 0;
        const hasProductFile = this.productFileInput && this.productFileInput.files.length > 0;

        if (this.generateProposalBtn) {
            this.generateProposalBtn.disabled = !(hasTenderFile && hasProductFile);
        }
    }

    /**
     * 提交技术方案生成
     */
    async submitTechProposal() {
        if (this.isGenerating) {
            window.notifications?.warning('正在生成中，请稍候...');
            return;
        }

        // 验证文件
        if (!this.techTenderFileInput.files[0] || !this.productFileInput.files[0]) {
            window.notifications?.error('请选择招标文件和产品文件');
            return;
        }

        this.isGenerating = true;
        this.showProgress();
        this.hideResults();

        try {
            // 创建表单数据
            const formData = new FormData();
            formData.append('tender_file', this.techTenderFileInput.files[0]);
            formData.append('product_file', this.productFileInput.files[0]);
            formData.append('output_prefix', this.outputPrefix?.value?.trim() || '技术方案');

            // 添加公司信息
            const companyId = this.techCompanySelect?.value;
            if (companyId) {
                formData.append('companyId', companyId);
            }

            // 添加项目名称（如果有）
            if (window.companyStateManager) {
                const projectName = window.companyStateManager.getProjectName();
                if (projectName) {
                    formData.append('projectName', projectName);
                }
            }

            // 创建超时控制器
            this.currentController = new AbortController();
            const timeoutId = setTimeout(() => {
                this.currentController.abort();
            }, 600000); // 10分钟超时

            // 发送请求
            const response = await window.apiClient?.post('/generate-proposal', formData);

            clearTimeout(timeoutId);

            if (response.success) {
                this.showSuccess(response);
            } else {
                this.showError(response.error || '生成失败');
            }

        } catch (error) {
            console.error('技术方案生成失败:', error);

            let errorMsg = '生成失败: ';
            if (error.name === 'AbortError') {
                errorMsg += '请求超时，文档过大或网络不稳定';
            } else if (error.message.includes('Failed to fetch')) {
                errorMsg += '网络连接失败，请检查网络状态后重试';
            } else {
                errorMsg += error.message;
            }

            this.showError(errorMsg);
        } finally {
            this.isGenerating = false;
            this.hideProgress();
        }
    }

    /**
     * 显示生成进度
     */
    showProgress() {
        if (this.techProgressBar) {
            this.techProgressBar.style.display = 'block';
        }

        if (this.generateProposalBtn) {
            this.generateProposalBtn.disabled = true;
            this.generateProposalBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 生成中...';
        }

        // 模拟进度增长
        let progress = 0;
        this.progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;
            this.updateProgressBar(progress);
        }, 1000);
    }

    /**
     * 更新进度条
     */
    updateProgressBar(progress) {
        const progressBarElement = this.techProgressBar?.querySelector('.progress-bar');
        if (progressBarElement) {
            progressBarElement.style.width = `${progress}%`;
        }
    }

    /**
     * 隐藏进度条
     */
    hideProgress() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }

        setTimeout(() => {
            if (this.techProgressBar) {
                this.techProgressBar.style.display = 'none';
            }

            this.updateProgressBar(0);

            if (this.generateProposalBtn) {
                this.generateProposalBtn.disabled = false;
                this.generateProposalBtn.innerHTML = '<i class="bi bi-magic"></i> 生成技术方案';
            }

            this.checkFormReady(); // 重新检查表单状态
        }, 1000);
    }

    /**
     * 显示成功结果
     */
    showSuccess(data) {
        this.updateProgressBar(100);

        // 更新统计信息
        const techResultMessage = document.getElementById('techResultMessage');
        if (techResultMessage) {
            const stats = this.formatStatistics(data);
            techResultMessage.innerHTML = stats;
        }

        // 生成下载按钮
        if (this.techDownloadArea && data.output_files) {
            this.createDownloadButtons(data.output_files);
        }

        if (this.techResultArea) {
            this.techResultArea.style.display = 'block';
        }

        window.notifications?.success('技术方案生成完成');
    }

    /**
     * 格式化统计信息
     */
    formatStatistics(data) {
        const matchRate = data.requirements_count > 0
            ? Math.round((data.matches_count / data.requirements_count * 100) || 0)
            : 0;

        return `
            <strong>生成统计：</strong><br>
            • 需求数量：${data.requirements_count || 0}<br>
            • 功能数量：${data.features_count || 0}<br>
            • 匹配数量：${data.matches_count || 0}<br>
            • 章节数量：${data.sections_count || 0}<br>
            • 匹配成功率：${matchRate}%
        `;
    }

    /**
     * 创建下载按钮
     */
    createDownloadButtons(outputFiles) {
        this.techDownloadArea.innerHTML = '';

        Object.keys(outputFiles).forEach(fileType => {
            const filePath = outputFiles[fileType];
            const fileName = filePath.split('/').pop();

            const buttonConfig = this.getButtonConfig(fileType);

            const button = document.createElement('button');
            button.className = `btn ${buttonConfig.class} me-2 mb-2`;
            button.innerHTML = `<i class="${buttonConfig.icon}"></i> ${buttonConfig.text}`;

            button.onclick = (e) => {
                e.preventDefault();
                this.downloadFile(filePath, fileName);
            };

            this.techDownloadArea.appendChild(button);
        });
    }

    /**
     * 获取按钮配置
     */
    getButtonConfig(fileType) {
        const configs = {
            proposal: {
                class: 'btn-success',
                icon: 'bi-file-earmark-word',
                text: '下载技术方案'
            },
            analysis: {
                class: 'btn-success',
                icon: 'bi-file-earmark-text',
                text: '下载需求分析'
            },
            mapping: {
                class: 'btn-success',
                icon: 'bi-file-earmark-spreadsheet',
                text: '下载匹配表'
            },
            summary: {
                class: 'btn-success',
                icon: 'bi-file-earmark-pdf',
                text: '下载生成报告'
            }
        };

        return configs[fileType] || {
            class: 'btn-success',
            icon: 'bi-download',
            text: '下载文件'
        };
    }

    /**
     * 显示错误信息
     */
    showError(errorMessage) {
        const techErrorMessage = document.getElementById('techErrorMessage');
        if (techErrorMessage) {
            techErrorMessage.textContent = errorMessage;
        }

        if (this.techErrorArea) {
            this.techErrorArea.style.display = 'block';
        }

        window.notifications?.error('技术方案生成失败');
    }

    /**
     * 隐藏结果区域
     */
    hideResults() {
        if (this.techResultArea) {
            this.techResultArea.style.display = 'none';
        }
        if (this.techErrorArea) {
            this.techErrorArea.style.display = 'none';
        }
    }

    /**
     * 下载文件
     */
    downloadFile(url, filename) {
        try {
            window.notifications?.info('开始下载...');

            const link = document.createElement('a');
            link.href = url;
            link.download = filename || '';
            link.style.display = 'none';

            document.body.appendChild(link);
            link.click();

            setTimeout(() => {
                document.body.removeChild(link);
                window.notifications?.success('下载已开始');
            }, 100);

        } catch (error) {
            console.error('下载失败:', error);
            window.notifications?.error('下载失败: ' + error.message);
        }
    }

    /**
     * 重置表单
     */
    resetForm() {
        // 取消当前生成
        if (this.currentController) {
            this.currentController.abort();
        }

        this.isGenerating = false;
        this.hideProgress();
        this.hideResults();

        // 清除文件选择
        if (this.techTenderFileInput) {
            this.techTenderFileInput.value = '';
        }
        if (this.productFileInput) {
            this.productFileInput.value = '';
        }

        // 隐藏文件信息
        if (this.techTenderFileInfo) {
            this.techTenderFileInfo.classList.add('d-none');
        }
        if (this.productFileInfo) {
            this.productFileInfo.classList.add('d-none');
        }

        // 重置输出前缀
        if (this.outputPrefix) {
            this.outputPrefix.value = '技术方案';
        }

        this.checkFormReady();
        window.notifications?.info('表单已重置');
    }

    /**
     * 获取当前配置
     */
    getCurrentConfig() {
        return {
            outputPrefix: this.outputPrefix?.value?.trim() || '技术方案'
        };
    }

    /**
     * 设置配置
     */
    setConfig(config) {
        if (this.outputPrefix && config.outputPrefix) {
            this.outputPrefix.value = config.outputPrefix;
        }
    }

    /**
     * 解析URL参数并自动填充表单
     */
    parseUrlParams() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const companyId = urlParams.get('company_id');
            const companyName = urlParams.get('company_name');
            const projectId = urlParams.get('project_id');
            const projectName = urlParams.get('project_name');
            const hitlTaskId = urlParams.get('hitl_task_id');

            console.log('[ProposalGenerator] 解析URL参数:', {
                companyId, companyName, projectId, projectName, hitlTaskId
            });

            // 如果有公司和项目信息,通过companyStateManager设置
            if (companyId && companyName && window.companyStateManager) {
                console.log('[ProposalGenerator] 设置公司和项目信息到状态管理器');
                window.companyStateManager.selectCompany({
                    company_id: parseInt(companyId),
                    company_name: companyName,
                    project_id: projectId ? parseInt(projectId) : null,
                    project_name: projectName || null
                });
            }

            // 保存hitl_task_id供后续使用(如果需要同步回HITL)
            if (hitlTaskId) {
                this.hitlTaskId = hitlTaskId;
                console.log('[ProposalGenerator] 保存HITL任务ID:', hitlTaskId);
            }

            // 保存URL参数供loadCompanies使用
            this.urlCompanyId = companyId;
        } catch (error) {
            console.error('[ProposalGenerator] 解析URL参数失败:', error);
        }
    }

    /**
     * 加载公司列表
     */
    async loadCompanies() {
        if (!this.techCompanySelect) {
            console.log('技术方案公司选择器不存在');
            return;
        }

        console.log('开始加载技术方案公司列表...');

        try {
            const response = await fetch('/api/companies');
            const data = await response.json();

            console.log('技术方案API返回的公司数据:', data);

            // 清空现有选项
            this.techCompanySelect.innerHTML = '<option value="">请选择公司...</option>';

            if (data.success && data.data && data.data.length > 0) {
                // 遍历公司列表并添加选项
                data.data.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.company_id;
                    option.textContent = company.company_name;
                    this.techCompanySelect.appendChild(option);
                });

                console.log(`技术方案成功加载 ${data.data.length} 家公司`);

                // 加载完成后,如果有URL参数中的company_id,自动选中
                if (this.urlCompanyId) {
                    this.techCompanySelect.value = this.urlCompanyId;
                    console.log('[ProposalGenerator] 自动选中URL传递的公司ID:', this.urlCompanyId);
                }
            } else {
                console.log('技术方案没有找到公司数据');
                this.techCompanySelect.innerHTML = '<option value="">暂无公司数据</option>';
            }
        } catch (error) {
            console.error('技术方案加载公司列表失败:', error);
            this.techCompanySelect.innerHTML = '<option value="">加载失败，请刷新重试</option>';
        }
    }

    /**
     * 销毁生成器
     */
    destroy() {
        if (this.currentController) {
            this.currentController.abort();
        }

        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }
}

// 全局技术方案生成器实例变量
window.proposalGenerator = null;

// 在DOM准备好后创建实例
document.addEventListener('DOMContentLoaded', function() {
    if (!window.proposalGenerator) {
        window.proposalGenerator = new ProposalGenerator();
    }
});

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProposalGenerator;
}