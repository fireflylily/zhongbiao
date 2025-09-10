/**
 * 招标信息提取页面JavaScript
 * 版本: 2025-09-10-v2.1 - 修复技术评分显示问题，强制缓存刷新
 */

// 页面元素
let tenderUploadArea, tenderFileInput, tenderFileInfo, tenderFileName, tenderFileSize;
let extractInfoBtn, tenderProgressBar, tenderResultArea, tenderErrorArea;

onPageReady(function() {
    // 初始化页面元素
    tenderUploadArea = document.getElementById('tenderUploadArea');
    tenderFileInput = document.getElementById('tenderFileInput');
    tenderFileInfo = document.getElementById('tenderFileInfo');
    tenderFileName = document.getElementById('tenderFileName');
    tenderFileSize = document.getElementById('tenderFileSize');
    extractInfoBtn = document.getElementById('extractInfoBtn');
    tenderProgressBar = document.getElementById('tenderProgressBar');
    tenderResultArea = document.getElementById('tenderResultArea');
    tenderErrorArea = document.getElementById('tenderErrorArea');

    // 设置拖拽上传
    setupDragDrop('tenderUploadArea', 'tenderFileInput', handleTenderFileSelect);

    // 设置事件监听器
    extractInfoBtn.addEventListener('click', submitTenderExtraction);
    
    document.getElementById('tenderRetryBtn')?.addEventListener('click', submitTenderExtraction);
    document.getElementById('tenderRetryBtn2')?.addEventListener('click', submitTenderExtraction);
    
    document.getElementById('tenderResetBtn')?.addEventListener('click', resetTenderForm);
    document.getElementById('tenderResetBtn2')?.addEventListener('click', resetTenderForm);
});

function handleTenderFileSelect(file) {
    if (!file) {
        const fileInput = document.getElementById('tenderFileInput');
        file = fileInput.files[0];
    }
    
    if (file) {
        displayFileInfo(file, tenderFileInfo);
        extractInfoBtn.disabled = false;
        
        // 保存文件信息到状态管理器
        StateManager.setUploadInfo({
            tenderFile: {
                name: file.name,
                size: file.size,
                type: file.type
            }
        });
    }
}

function resetTenderForm() {
    tenderFileInput.value = '';
    tenderFileInfo.style.display = 'none';
    tenderResultArea.style.display = 'none';
    tenderErrorArea.style.display = 'none';
    extractInfoBtn.disabled = true;
    
    // 清理状态
    StateManager.remove(StateManager.KEYS.UPLOAD_FILES);
}

async function performStepwiseExtraction(formData, progressBar, tenderResultArea, tenderErrorArea, progressInterval, timeoutId) {
    try {
        // 清空之前的结果容器
        ['basicInfoContainer', 'qualificationContainer', 'technicalContainer'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.remove();
        });
        
        // 第一步：提取基本信息
        document.getElementById('stepMessage').textContent = '正在提取基本信息...';
        progressBar.style.width = '20%';
        
        const step1FormData = new FormData();
        for (let pair of formData.entries()) {
            step1FormData.append(pair[0], pair[1]);
        }
        step1FormData.append('step', '1');
        
        const step1Response = await fetch('/extract-tender-info-step', {
            method: 'POST',
            body: step1FormData
        });
        const step1Data = await step1Response.json();
        
        if (!step1Data.success) {
            throw new Error(step1Data.error);
        }
        
        // 显示基本信息
        displayBasicInfo(step1Data.basic_info);
        progressBar.style.width = '40%';
        
        // 第二步：提取资质要求  
        document.getElementById('stepMessage').textContent = '正在提取资质要求...';
        
        const step2FormData = new FormData();
        step2FormData.append('step', '2');
        step2FormData.append('file_path', step1Data.file_path);
        step2FormData.append('result_file', step1Data.result_file || '');
        step2FormData.append('api_key', StateManager.getApiKey() || '');
        
        const step2Response = await fetch('/extract-tender-info-step', {
            method: 'POST',
            body: step2FormData
        });
        const step2Data = await step2Response.json();
        
        if (!step2Data.success) {
            throw new Error(step2Data.error);
        }
        
        // 显示资质要求
        displayQualificationRequirements(step2Data.qualification_requirements);
        progressBar.style.width = '70%';
        
        // 第三步：提取技术评分
        document.getElementById('stepMessage').textContent = '正在分析技术评分...';
        
        const step3FormData = new FormData();
        step3FormData.append('step', '3');
        step3FormData.append('file_path', step1Data.file_path);
        step3FormData.append('api_key', StateManager.getApiKey() || '');
        
        const step3Response = await fetch('/extract-tender-info-step', {
            method: 'POST',
            body: step3FormData
        });
        const step3Data = await step3Response.json();
        
        if (!step3Data.success) {
            throw new Error(step3Data.error);
        }
        
        // 显示技术评分（如果存在）
        const hasTechnicalScoring = displayTechnicalScoring(step3Data.technical_scoring);
        progressBar.style.width = '100%';
        document.getElementById('stepMessage').textContent = hasTechnicalScoring ? '所有信息提取完成！' : '信息提取完成（未检测到技术评分标准）！';
        
        // 清理定时器
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        
        tenderResultArea.style.display = 'block';
        
        // 保存提取结果
        StateManager.setPageContext({
            tenderInfoExtracted: true,
            extractionComplete: true
        });
        
    } catch (error) {
        throw error;
    }
}

function submitTenderExtraction() {
    if (!tenderFileInput.files[0]) {
        showNotification('请先选择招标文档', 'error');
        return;
    }

    const apiKey = StateManager.getApiKey();
    if (!apiKey) {
        showNotification('请先配置API密钥', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', tenderFileInput.files[0]);
    formData.append('api_key', apiKey);

    // 重置显示区域
    tenderResultArea.style.display = 'none';
    tenderErrorArea.style.display = 'none';
    
    // 显示进度条和步骤消息
    tenderProgressBar.style.display = 'block';
    document.getElementById('stepMessage').style.display = 'block';
    const progressBar = tenderProgressBar.querySelector('.progress-bar');
    
    // 设置按钮状态
    extractInfoBtn.disabled = true;
    extractInfoBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 提取中...';

    // 模拟进度更新
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressBar.style.width = progress + '%';
    }, 200);

    // 超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2分钟超时

    // 分步加载实现
    performStepwiseExtraction(formData, progressBar, tenderResultArea, tenderErrorArea, progressInterval, timeoutId)
    .catch(error => {
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        let errorMsg = '提取失败: ';
        
        if (error.name === 'AbortError') {
            errorMsg += '请求超时，文档过大或处理时间过长。建议：1) 检查网络连接 2) 尝试更小的文档 3) 点击重试';
        } else if (error.message.includes('Failed to fetch')) {
            errorMsg += '网络连接失败，请检查网络状态后重试';
        } else {
            errorMsg += error.message;
        }
        
        document.getElementById('tenderErrorMessage').textContent = errorMsg;
        tenderErrorArea.style.display = 'block';
    })
    .finally(() => {
        setTimeout(() => {
            tenderProgressBar.style.display = 'none';
            document.getElementById('stepMessage').style.display = 'none';
            tenderProgressBar.querySelector('.progress-bar').style.width = '0%';
            extractInfoBtn.disabled = false;
            extractInfoBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始提取信息';
        }, 1000);
    });
}

function displayTenderInfo(tenderInfo) {
    const fieldLabels = {
        'tenderer': '招标人',
        'agency': '招标代理',
        'bidding_method': '投标方式',
        'bidding_location': '投标地点',
        'bidding_time': '投标时间',
        'winner_count': '中标人数量',
        'project_name': '项目名称',
        'project_number': '项目编号'
    };

    // 基本信息部分
    let html = '<h5 class="text-primary mb-3"><i class="bi bi-info-circle"></i> 基本信息</h5>';
    let basicInfoHtml = '';
    
    for (const [key, value] of Object.entries(tenderInfo)) {
        if (fieldLabels[key]) {
            const label = fieldLabels[key];
            const displayValue = value || '未提取到';
            const textColor = value ? 'text-success' : 'text-muted';
            
            basicInfoHtml += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title text-primary">
                                <i class="bi bi-info-circle"></i> ${label}
                            </h6>
                            <p class="card-text ${textColor}">${displayValue}</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    html += `<div class="row">${basicInfoHtml}</div>`;
    
    document.getElementById('tenderInfoDisplay').innerHTML = html;
}

function displayBasicInfo(basicInfo) {
    const container = document.createElement('div');
    container.id = 'basicInfoContainer';
    container.innerHTML = `<h5 class="text-primary mb-3"><i class="bi bi-info-circle"></i> 基本信息</h5>`;
    
    let html = '<div class="row">';
    const fieldLabels = {
        'tenderer': '招标人',
        'agency': '招标代理',
        'bidding_method': '投标方式',
        'bidding_location': '投标地点',
        'bidding_time': '投标时间',
        'winner_count': '中标人数量',
        'project_name': '项目名称',
        'project_number': '项目编号'
    };
    
    for (const [key, value] of Object.entries(basicInfo)) {
        if (fieldLabels[key]) {
            const label = fieldLabels[key];
            const displayValue = value || '未提取到';
            const textColor = value ? 'text-success' : 'text-muted';
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title text-primary">
                                <i class="bi bi-info-circle"></i> ${label}
                            </h6>
                            <p class="card-text ${textColor}">${displayValue}</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    html += '</div>';
    container.innerHTML += html;
    
    document.getElementById('tenderInfoDisplay').appendChild(container);
}

function displayQualificationRequirements(qualificationRequirements) {
    const container = document.createElement('div');
    container.id = 'qualificationContainer';
    container.innerHTML = `<hr><h5 class="text-warning mb-3 mt-4"><i class="bi bi-list-check"></i> 资质要求</h5>`;
    
    const qualificationLabels = {
        'business_license': '营业执照',
        'taxpayer_qualification': '纳税人资格（增值税纳税人）',
        'performance_requirements': '业绩要求',
        'authorization_requirements': '授权要求',
        'credit_china': '信用中国',
        'commitment_letter': '承诺函（默认满足）',
        'audit_report': '审计报告（财务要求）',
        'social_security': '社保要求',
        'labor_contract': '劳动合同要求',
        'other_requirements': '其他要求'
    };
    
    let html = '<div class="row">';
    for (const [key, qualData] of Object.entries(qualificationRequirements)) {
        if (qualificationLabels[key]) {
            const label = qualificationLabels[key];
            const required = qualData.required;
            const description = qualData.description || '';
            const statusText = required ? '需要提供' : '不需要提供';
            const statusColor = required ? 'text-danger' : 'text-success';
            const iconClass = required ? 'bi-exclamation-triangle' : 'bi-check-circle';
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card ${required ? 'border-warning' : 'border-success'}">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i class="bi ${iconClass} ${statusColor}"></i> ${label}
                            </h6>
                            <p class="card-text ${statusColor} fw-bold">${statusText}</p>
                            ${description ? `<p class="card-text text-muted small">${description}</p>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
    }
    html += '</div>';
    container.innerHTML += html;
    
    document.getElementById('tenderInfoDisplay').appendChild(container);
}

function displayTechnicalScoring(technicalScoring) {
    // 检查是否有有效的技术评分数据
    let hasValidScoring = false;
    
    if (technicalScoring) {
        // 检查新的数据结构：technical_scoring_items数组
        if (technicalScoring.technical_scoring_items && 
            Array.isArray(technicalScoring.technical_scoring_items) && 
            technicalScoring.technical_scoring_items.length > 0) {
            hasValidScoring = true;
        } 
        // 检查旧的数据结构：直接的评分对象
        else if (Object.keys(technicalScoring).length > 0 && 
                 !Object.keys(technicalScoring).some(key => key === '未检测到评分项目')) {
            hasValidScoring = true;
        }
    }
    
    console.log('技术评分数据检查:', { technicalScoring, hasValidScoring });
    
    // 如果没有有效的技术评分数据，直接返回false，不显示任何内容
    if (!hasValidScoring) {
        return false;
    }
    
    const container = document.createElement('div');
    container.id = 'technicalContainer';
    container.innerHTML = `<hr><h5 class="text-info mb-3 mt-4"><i class="bi bi-award"></i> 技术评分标准</h5>`;
    
    let html = '<div class="row">';
    let itemsProcessed = 0;
    
    // 处理新的数据结构：technical_scoring_items数组
    if (technicalScoring.technical_scoring_items && Array.isArray(technicalScoring.technical_scoring_items)) {
        technicalScoring.technical_scoring_items.forEach(item => {
            const name = item.name || '未命名';
            const weight = item.weight || '未指定';
            const criteria = item.criteria || '无具体要求';
            const source = item.source || '位置未确定';
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card border-info">
                        <div class="card-body">
                            <h6 class="card-title text-info">
                                <i class="bi bi-award"></i> ${name}
                            </h6>
                            <p class="card-text"><strong>分值：</strong><span class="text-primary">${weight}</span></p>
                            <p class="card-text"><strong>评分标准：</strong></p>
                            <p class="small text-muted">${criteria}</p>
                            ${source && source !== '位置未确定' ? `<p class="card-text small"><strong>来源：</strong>${source}</p>` : ''}
                        </div>
                    </div>
                </div>
            `;
            itemsProcessed++;
        });
        
        // 添加总分信息
        if (technicalScoring.total_technical_score) {
            html += `
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <h6><i class="bi bi-calculator"></i> 技术评分总分：<strong class="text-primary">${technicalScoring.total_technical_score}</strong></h6>
                        ${technicalScoring.extraction_summary ? `<p class="mb-0 small">${technicalScoring.extraction_summary}</p>` : ''}
                        ${technicalScoring.confidence ? `<p class="mb-0 small">提取置信度：<span class="badge bg-${technicalScoring.confidence === 'high' ? 'success' : technicalScoring.confidence === 'medium' ? 'warning' : 'danger'}">${technicalScoring.confidence}</span></p>` : ''}
                    </div>
                </div>
            `;
        }
    } else {
        // 处理旧的数据结构（向后兼容）
        for (const [category, details] of Object.entries(technicalScoring)) {
            // 跳过元数据字段
            if (['total_technical_score', 'extraction_summary', 'confidence', 'items_count'].includes(category)) {
                continue;
            }
            
            const score = details.score || '未指定';
            const criteria = details.criteria || [];
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card border-info">
                        <div class="card-body">
                            <h6 class="card-title text-info">
                                <i class="bi bi-award"></i> ${category}
                            </h6>
                            <p class="card-text"><strong>分值：</strong><span class="text-primary">${score}</span></p>
                            ${criteria.length > 0 ? `
                                <p class="card-text"><strong>评分标准：</strong></p>
                                <ul class="small">
                                    ${criteria.map(criterion => `<li>${criterion}</li>`).join('')}
                                </ul>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            itemsProcessed++;
        }
    }
    
    console.log(`技术评分渲染完成，共处理 ${itemsProcessed} 个评分项`);
    
    html += '</div>';
    container.innerHTML += html;
    document.getElementById('tenderInfoDisplay').appendChild(container);
    return true;
}