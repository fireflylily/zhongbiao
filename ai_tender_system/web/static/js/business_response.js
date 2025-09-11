/**
 * 商务应答页面JavaScript
 */

// 商务应答页面变量

// 页面元素和状态
let businessResponseForm, businessTemplateFile, businessCompanySelect;
let businessProgress, businessResult, businessError;

onPageReady(function() {
    // 初始化页面元素
    businessResponseForm = document.getElementById('businessResponseForm');
    businessTemplateFile = document.getElementById('businessTemplateFile');
    businessCompanySelect = document.getElementById('businessCompanySelect');
    businessProgress = document.getElementById('businessProgress');
    businessResult = document.getElementById('businessResult');
    businessError = document.getElementById('businessError');

    // 设置事件监听器
    if (businessResponseForm) {
        businessResponseForm.addEventListener('submit', handleBusinessResponseSubmit);
    }
    
    if (businessTemplateFile) {
        businessTemplateFile.addEventListener('change', handleBusinessTemplateSelect);
    }

    // 加载公司列表
    loadBusinessCompanyList();
    
    // 加载项目信息
    loadProjectInfo();
    
    // 从状态管理器恢复选中的公司
    const savedCompanyId = StateManager.getCompanyId();
    if (savedCompanyId && businessCompanySelect) {
        businessCompanySelect.value = savedCompanyId;
    }
    
    // 添加公司选择变更事件监听器
    if (businessCompanySelect) {
        businessCompanySelect.addEventListener('change', function() {
            const selectedCompanyId = this.value;
            console.log('[商务应答] 用户选择公司ID:', selectedCompanyId);
            
            if (selectedCompanyId) {
                StateManager.setCompanyId(selectedCompanyId);
                console.log('[商务应答] 已同步状态到StateManager:', selectedCompanyId);
            } else {
                StateManager.setCompanyId('');
                console.log('[商务应答] 已清空StateManager中的公司状态');
            }
        });
    }
    
    // 监听来自其他页面的公司状态变更
    StateManager.onStateChangeByKey('companyId', function(newCompanyId, oldCompanyId) {
        console.log('[商务应答] 接收到公司状态变更:', {
            new: newCompanyId,
            old: oldCompanyId
        });
        
        // 更新本页面的公司选择框
        if (businessCompanySelect && businessCompanySelect.value !== newCompanyId) {
            businessCompanySelect.value = newCompanyId || '';
            console.log('[商务应答] 已同步公司选择框:', newCompanyId);
        }
    });
});

function loadBusinessCompanyList() {
    if (!businessCompanySelect) return;
    
    fetch('/api/companies')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                businessCompanySelect.innerHTML = '<option value="">请选择公司...</option>';
                data.companies.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.id;
                    option.textContent = company.companyName;
                    businessCompanySelect.appendChild(option);
                });
                
                // 恢复选中状态
                const savedCompanyId = StateManager.getCompanyId();
                if (savedCompanyId) {
                    businessCompanySelect.value = savedCompanyId;
                }
            }
        })
        .catch(error => {
            console.error('加载公司列表失败:', error);
        });
}

function loadProjectInfo() {
    fetch('/api/project-config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.project_info) {
                // 填充项目信息到表单
                const projectNameField = document.getElementById('businessProjectName');
                const tenderNoField = document.getElementById('businessTenderNo');
                const dateField = document.getElementById('businessDate');
                
                if (projectNameField && data.project_info.projectName) {
                    projectNameField.value = data.project_info.projectName;
                }
                
                if (tenderNoField && data.project_info.projectNumber) {
                    tenderNoField.value = data.project_info.projectNumber;
                }
                
                if (dateField && data.project_info.currentDate) {
                    dateField.value = data.project_info.currentDate;
                }
                
                // 显示招标文件名称
                if (data.project_info.tenderFileName) {
                    const tenderFileDisplay = document.getElementById('tenderFileNameDisplay');
                    const tenderFileText = document.getElementById('tenderFileNameText');
                    
                    if (tenderFileDisplay && tenderFileText) {
                        tenderFileText.textContent = data.project_info.tenderFileName;
                        tenderFileDisplay.style.display = 'block';
                    }
                }
                
                console.log('项目信息加载成功', data.project_info);
            } else {
                console.warn('项目信息加载失败:', data.error || '无项目信息');
            }
        })
        .catch(error => {
            console.warn('加载项目信息失败:', error);
        });
}

function handleBusinessTemplateSelect(event) {
    const file = event.target.files[0];
    const fileNameElement = document.getElementById('businessTemplateFileName');
    
    if (file && fileNameElement) {
        fileNameElement.innerHTML = `<small class="text-success"><i class="bi bi-check-circle"></i> 已选择: ${file.name}</small>`;
        fileNameElement.style.display = 'block';
    }
}

function handleBusinessResponseSubmit(event) {
    event.preventDefault();
    
    if (!businessTemplateFile.files[0]) {
        showNotification('请先选择商务应答模板文件', 'error');
        return;
    }
    
    if (!businessCompanySelect.value) {
        showNotification('请选择应答公司', 'error');
        return;
    }
    
    // 保存选中的公司到状态管理器
    StateManager.setCompanyId(businessCompanySelect.value);
    
    const formData = new FormData(businessResponseForm);
    formData.append('company_id', businessCompanySelect.value);
    
    // 显示进度条
    businessProgress.style.display = 'block';
    businessResult.style.display = 'none';
    businessError.style.display = 'none';
    
    // 更新进度条
    const progressBar = businessProgress.querySelector('.progress-bar');
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressBar.style.width = progress + '%';
    }, 200);
    
    fetch('/process-business-response', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        setTimeout(() => {
            businessProgress.style.display = 'none';
            
            if (data.success) {
                const resultMessage = document.getElementById('businessResultMessage');
                const downloadLink = document.getElementById('businessDownloadLink');
                
                if (resultMessage) {
                    resultMessage.textContent = data.message || '商务应答处理完成';
                }
                
                if (downloadLink && data.download_url) {
                    downloadLink.href = data.download_url;
                    downloadLink.onclick = () => downloadFile(data.download_url, data.filename);
                    
                    // 同时更新预览按钮，存储必要的数据
                    const previewBtn = document.getElementById('businessPreviewBtn');
                    if (previewBtn) {
                        previewBtn.setAttribute('data-file-url', data.download_url);
                        previewBtn.setAttribute('data-filename', data.filename || '商务应答文档');
                    }
                }
                
                // 显示处理步骤结果
                if (data.processing_steps) {
                    showProcessingSteps(data.processing_steps);
                }
                
                // 显示统计信息
                if (data.statistics) {
                    showStatistics(data.statistics);
                }
                
                businessResult.style.display = 'block';
                showNotification('商务应答处理成功！', 'success');
            } else {
                const errorMessage = document.getElementById('businessErrorMessage');
                if (errorMessage) {
                    errorMessage.textContent = data.error || '处理失败';
                }
                businessError.style.display = 'block';
                showNotification('商务应答处理失败', 'error');
            }
        }, 1000);
    })
    .catch(error => {
        clearInterval(progressInterval);
        businessProgress.style.display = 'none';
        
        const errorMessage = document.getElementById('businessErrorMessage');
        if (errorMessage) {
            errorMessage.textContent = '网络错误: ' + error.message;
        }
        businessError.style.display = 'block';
        showNotification('商务应答处理失败', 'error');
    });
}

/**
 * 显示处理步骤结果
 */
function showProcessingSteps(steps) {
    const statsElement = document.getElementById('businessStats');
    const statsContent = document.getElementById('businessStatsContent');
    
    if (!statsElement || !statsContent) return;
    
    let stepsHtml = '<div class="processing-steps">';
    
    // 文本填写步骤
    if (steps.text) {
        const textClass = steps.text.success ? 'text-success' : 'text-danger';
        const textIcon = steps.text.success ? 'bi-check-circle' : 'bi-x-circle';
        stepsHtml += `
            <div class="step mb-2">
                <i class="bi ${textIcon} ${textClass}"></i>
                <strong>文本填写：</strong>
                <span class="${textClass}">${steps.text.message || '未处理'}</span>
                ${steps.text.count ? `<small class="text-muted ms-2">(${steps.text.count}处替换)</small>` : ''}
            </div>
        `;
    }
    
    // 表格处理步骤
    if (steps.tables) {
        const tableClass = steps.tables.success ? 'text-success' : 'text-warning';
        const tableIcon = steps.tables.success ? 'bi-check-circle' : 'bi-exclamation-circle';
        stepsHtml += `
            <div class="step mb-2">
                <i class="bi ${tableIcon} ${tableClass}"></i>
                <strong>表格处理：</strong>
                <span class="${tableClass}">${steps.tables.message || '未处理'}</span>
                ${steps.tables.count ? `<small class="text-muted ms-2">(${steps.tables.count}个表格，${steps.tables.fields || 0}个字段)</small>` : ''}
            </div>
        `;
    }
    
    // 图片插入步骤
    if (steps.images) {
        const imageClass = steps.images.success ? 'text-success' : 'text-warning';
        const imageIcon = steps.images.success ? 'bi-check-circle' : 'bi-exclamation-circle';
        stepsHtml += `
            <div class="step mb-2">
                <i class="bi ${imageIcon} ${imageClass}"></i>
                <strong>图片插入：</strong>
                <span class="${imageClass}">${steps.images.message || '未处理'}</span>
                ${steps.images.count ? `<small class="text-muted ms-2">(${steps.images.count}张图片)</small>` : ''}
            </div>
        `;
    }
    
    stepsHtml += '</div>';
    statsContent.innerHTML = stepsHtml;
    statsElement.style.display = 'block';
}

/**
 * 显示统计信息
 */
function showStatistics(statistics) {
    const statsContent = document.getElementById('businessStatsContent');
    if (!statsContent) return;
    
    // 在处理步骤后添加统计摘要
    const summaryHtml = `
        <hr>
        <div class="statistics-summary">
            <h6 class="mb-3">处理统计</h6>
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-item text-center">
                        <i class="bi bi-pencil-square text-primary display-6"></i>
                        <div class="mt-2">
                            <strong>${statistics.text_replacements || 0}</strong>
                            <small class="d-block text-muted">文本替换</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item text-center">
                        <i class="bi bi-table text-info display-6"></i>
                        <div class="mt-2">
                            <strong>${statistics.tables_processed || 0}</strong>
                            <small class="d-block text-muted">表格处理</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item text-center">
                        <i class="bi bi-input-cursor text-warning display-6"></i>
                        <div class="mt-2">
                            <strong>${statistics.fields_filled || 0}</strong>
                            <small class="d-block text-muted">字段填充</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item text-center">
                        <i class="bi bi-image text-success display-6"></i>
                        <div class="mt-2">
                            <strong>${statistics.images_inserted || 0}</strong>
                            <small class="d-block text-muted">图片插入</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 追加到现有内容
    statsContent.innerHTML += summaryHtml;
}

// ==================== 文档预览功能 ====================

/**
 * 预览商务应答文档
 */
function previewBusinessDocument() {
    const previewBtn = document.getElementById('businessPreviewBtn');
    let fileUrl = null;
    let filename = '商务应答文档';
    
    // 优先使用data属性中存储的文件信息
    if (previewBtn && previewBtn.getAttribute('data-file-url')) {
        fileUrl = previewBtn.getAttribute('data-file-url');
        filename = previewBtn.getAttribute('data-filename') || '商务应答文档';
    } else {
        // 回退到原来的逻辑
        const downloadLink = document.getElementById('businessDownloadLink');
        if (downloadLink && downloadLink.href && downloadLink.href !== '#') {
            fileUrl = downloadLink.href;
        }
    }
    
    if (fileUrl) {
        const previewUrl = `/preview-document?file=${encodeURIComponent(fileUrl)}&filename=${encodeURIComponent(filename)}&type=商务应答`;
        window.open(previewUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    } else {
        showNotification('没有可预览的文档', 'error');
    }
}

/**
 * 测试预览功能（使用最新生成的文件）
 */
function testPreviewWithLatestFile() {
    // 使用最新生成的商务应答文件进行测试
    const testFileUrl = '/download/docx-商务应答-20250908_173139.docx';
    const testFilename = 'docx-商务应答-20250908_173139.docx';
    
    const previewUrl = `/preview-document?file=${encodeURIComponent(testFileUrl)}&filename=${encodeURIComponent(testFilename)}&type=商务应答`;
    window.open(previewUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    
    showNotification('正在打开预览窗口...', 'info');
}