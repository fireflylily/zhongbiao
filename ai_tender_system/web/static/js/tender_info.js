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
    
    // 清空Tab内容
    document.getElementById('basicInfoDisplay').innerHTML = '';
    document.getElementById('qualificationDisplay').innerHTML = '';
    document.getElementById('technicalScoringDisplay').innerHTML = '';
    
    // 重置为第一个Tab
    const firstTab = document.getElementById('basic-info-tab');
    if (firstTab) {
        firstTab.click();
    }
    
    // 清理状态
    StateManager.remove(StateManager.KEYS.UPLOAD_FILES);
}

async function performStepwiseExtraction(formData, progressBar, tenderResultArea, tenderErrorArea, progressInterval, timeoutId) {
    try {
        // 清空之前的结果容器
        document.getElementById('basicInfoDisplay').innerHTML = '';
        document.getElementById('qualificationDisplay').innerHTML = '';
        document.getElementById('technicalScoringDisplay').innerHTML = '';
        
        // 步骤1：上传文件并处理
        document.getElementById('stepMessage').textContent = '正在上传文件...';
        progressBar.style.width = '20%';
        
        await new Promise(resolve => setTimeout(resolve, 500)); // 模拟延迟
        
        // 步骤2：提取基本信息
        document.getElementById('stepMessage').textContent = '正在提取基本信息...';
        progressBar.style.width = '40%';
        
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // 步骤3：分析资质要求
        document.getElementById('stepMessage').textContent = '正在分析资质要求...';
        progressBar.style.width = '70%';
        
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // 步骤4：提取技术评分
        document.getElementById('stepMessage').textContent = '正在提取技术评分...';
        progressBar.style.width = '90%';
        
        // 发送请求到统一的API端点
        const response = await fetch('/extract-tender-info', {
            method: 'POST',
            body: formData
        });
        
        // 检查HTTP状态
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('API响应数据:', data);
        
        if (!data.success) {
            let errorMsg = '未知错误';
            if (typeof data.error === 'string') {
                errorMsg = data.error;
            } else if (typeof data.message === 'string') {
                errorMsg = data.message;
            } else if (data.error && typeof data.error === 'object') {
                errorMsg = data.error.message || JSON.stringify(data.error);
            } else if (data.message && typeof data.message === 'object') {
                errorMsg = data.message.message || JSON.stringify(data.message);
            } else {
                errorMsg = JSON.stringify(data);
            }
            console.error('API返回错误:', data);
            throw new Error(errorMsg);
        }
        
        // 处理返回的数据
        const result = data.data;
        
        // 提取基本信息（招标相关的基本字段）
        const basicInfo = {
            tenderer: result.tenderer,
            agency: result.agency,
            bidding_method: result.bidding_method,
            bidding_location: result.bidding_location,
            bidding_time: result.bidding_time,
            winner_count: result.winner_count,
            project_name: result.project_name,
            project_number: result.project_number
        };
        
        // 提取资质要求（以qualification_开头的字段）
        const qualificationRequirements = {};
        for (const [key, value] of Object.entries(result)) {
            if (key.startsWith('qualification_') || key.includes('requirements') || 
                ['business_license', 'taxpayer_qualification', 'performance_requirements', 
                 'authorization_requirements', 'credit_china', 'commitment_letter', 
                 'audit_report', 'social_security', 'labor_contract', 'other_requirements'].includes(key)) {
                qualificationRequirements[key] = value;
            }
        }
        
        // 提取技术评分（以technical_开头的字段或包含scoring的字段）
        const technicalScoring = {};
        for (const [key, value] of Object.entries(result)) {
            if (key.startsWith('technical_') || key.includes('scoring') || key.includes('score')) {
                technicalScoring[key] = value;
            }
        }
        
        // 显示提取结果
        displayBasicInfo(basicInfo);
        displayQualificationRequirements(qualificationRequirements);
        const hasTechnicalScoring = displayTechnicalScoring(technicalScoring);
        
        // 完成
        progressBar.style.width = '100%';
        document.getElementById('stepMessage').textContent = hasTechnicalScoring ? 
            '所有信息提取完成！' : '信息提取完成（未检测到技术评分标准）！';
        
        // 清理定时器
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        
        tenderResultArea.style.display = 'block';
        
        // 保存提取结果
        StateManager.setPageContext({
            tenderInfoExtracted: true,
            extractionComplete: true,
            extractedData: result
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

    const formData = new FormData();
    formData.append('file', tenderFileInput.files[0]);
    
    // 尝试获取用户输入的API密钥，如果没有就让后端使用环境变量
    const apiKeyInput = document.getElementById('tenderApiKey');
    if (apiKeyInput && apiKeyInput.value.trim()) {
        formData.append('api_key', apiKeyInput.value.trim());
    }

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
        } else if (error.message && error.message.includes('Failed to fetch')) {
            errorMsg += '网络连接失败，请检查网络状态后重试';
        } else if (typeof error === 'string') {
            errorMsg += error;
        } else if (error.message && typeof error.message === 'string') {
            errorMsg += error.message;
        } else if (error && typeof error === 'object') {
            errorMsg += JSON.stringify(error);
        } else {
            errorMsg += '未知错误';
        }
        
        console.error('提取错误详情:', error);
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
    
    document.getElementById('basicInfoDisplay').innerHTML = html;
}

function displayQualificationRequirements(qualificationRequirements) {
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
    
    document.getElementById('qualificationDisplay').innerHTML = html;
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
    
    // 如果没有有效的技术评分数据，显示提示信息
    if (!hasValidScoring) {
        document.getElementById('technicalScoringDisplay').innerHTML = `
            <div class="alert alert-info text-center">
                <i class="bi bi-info-circle"></i>
                <h6>未检测到技术评分标准</h6>
                <p class="mb-0 small">该招标文件可能不包含技术评分相关内容，或者评分标准格式特殊无法自动识别。</p>
            </div>
        `;
        return false;
    }
    
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
    document.getElementById('technicalScoringDisplay').innerHTML = html;
    return true;
}