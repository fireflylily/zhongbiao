/**
 * 技术方案页面JavaScript
 */

// 技术方案页面变量

// 页面元素和状态  
let techProposalForm, techTenderFileInput, productFileInput;
let techProgressBar, techResultArea, techErrorArea;
let generateProposalBtn;

onPageReady(function() {
    // 显示当前选中的公司信息
    displayCurrentCompany();
    
    // 初始化页面元素
    techProposalForm = document.getElementById('techProposalForm');
    techTenderFileInput = document.getElementById('techTenderFileInput');
    productFileInput = document.getElementById('productFileInput');
    techProgressBar = document.getElementById('techProgressBar');
    techResultArea = document.getElementById('techResultArea');
    techErrorArea = document.getElementById('techErrorArea');
    generateProposalBtn = document.getElementById('generateProposalBtn');

    // 设置事件监听器
    if (techProposalForm) {
        techProposalForm.addEventListener('submit', handleTechProposalSubmit);
    }
    
    if (techTenderFileInput) {
        techTenderFileInput.addEventListener('change', handleTechTenderFileSelect);
    }
    
    if (productFileInput) {
        productFileInput.addEventListener('change', handleProductFileSelect);
    }

    // 检查表单准备状态
    checkTechFormReady();
    
    // 监听公司状态变化（跨页面同步）
    StateManager.onStateChangeByKey('companyId', function(newCompanyId, oldCompanyId) {
        console.log('[技术方案] 接收到公司状态变更:', {
            new: newCompanyId,
            old: oldCompanyId
        });
        
        // 重新显示公司信息
        displayCurrentCompany();
    });
});

function handleTechTenderFileSelect(event) {
    const file = event.target.files[0];
    const fileInfo = document.getElementById('techTenderFileInfo');
    const fileName = document.getElementById('techTenderFileName');
    
    if (file && fileInfo && fileName) {
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        checkTechFormReady();
        showNotification('招标文件已选择', 'success');
    }
}

function handleProductFileSelect(event) {
    const file = event.target.files[0];
    const fileInfo = document.getElementById('productFileInfo');
    const fileName = document.getElementById('productFileName');
    
    if (file && fileInfo && fileName) {
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        checkTechFormReady();
        showNotification('产品文档已选择', 'success');
    }
}

function checkTechFormReady() {
    if (!generateProposalBtn) return;
    
    const hasTenderFile = techTenderFileInput && techTenderFileInput.files[0];
    const hasProductFile = productFileInput && productFileInput.files[0];
    
    generateProposalBtn.disabled = !(hasTenderFile && hasProductFile);
}

function handleTechProposalSubmit(event) {
    event.preventDefault();
    
    if (!techTenderFileInput.files[0]) {
        showNotification('请选择招标文件', 'error');
        return;
    }
    
    if (!productFileInput.files[0]) {
        showNotification('请选择产品文档', 'error');
        return;
    }
    
    const formData = new FormData(techProposalForm);
    
    // 显示进度条
    techProgressBar.style.display = 'block';
    techResultArea.style.display = 'none';
    techErrorArea.style.display = 'none';
    
    generateProposalBtn.disabled = true;
    generateProposalBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 生成中...';
    
    // 更新进度条
    const progressBar = techProgressBar.querySelector('.progress-bar');
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 85) progress = 85;
        progressBar.style.width = progress + '%';
    }, 500);
    
    fetch('/generate-proposal', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        setTimeout(() => {
            techProgressBar.style.display = 'none';
            generateProposalBtn.disabled = false;
            generateProposalBtn.innerHTML = '<i class="bi bi-play-circle"></i> 生成技术方案';
            
            if (data.success) {
                const resultMessage = document.getElementById('techResultMessage');
                const downloadArea = document.getElementById('techDownloadArea');
                
                if (resultMessage) {
                    resultMessage.textContent = data.message || '技术方案生成完成';
                }
                
                // 生成下载按钮
                if (downloadArea && data.files) {
                    let downloadHtml = '';
                    data.files.forEach(file => {
                        downloadHtml += `
                            <button class="btn btn-primary me-2 mb-2" onclick="downloadFile('${file.url}', '${file.filename}')">
                                <i class="bi bi-download"></i> ${file.name}
                            </button>
                        `;
                    });
                    downloadArea.innerHTML = downloadHtml;
                }
                
                // 生成预览按钮
                const previewArea = document.getElementById('techPreviewArea');
                if (previewArea && data.files) {
                    let previewHtml = '';
                    data.files.forEach(file => {
                        // 只为Word文档生成预览按钮
                        if (file.filename && (file.filename.endsWith('.docx') || file.filename.endsWith('.doc'))) {
                            previewHtml += `
                                <button class="btn btn-success me-2 mb-2" onclick="previewTechDocument('${file.url}', '${file.filename}')">
                                    <i class="bi bi-eye"></i> 预览 ${file.name}
                                </button>
                            `;
                        }
                    });
                    previewArea.innerHTML = previewHtml;
                }
                
                techResultArea.style.display = 'block';
                showNotification('技术方案生成成功！', 'success');
            } else {
                const errorMessage = document.getElementById('techErrorMessage');
                if (errorMessage) {
                    errorMessage.textContent = data.error || '生成失败';
                }
                techErrorArea.style.display = 'block';
                showNotification('技术方案生成失败', 'error');
            }
        }, 1000);
    })
    .catch(error => {
        clearInterval(progressInterval);
        techProgressBar.style.display = 'none';
        generateProposalBtn.disabled = false;
        generateProposalBtn.innerHTML = '<i class="bi bi-play-circle"></i> 生成技术方案';
        
        const errorMessage = document.getElementById('techErrorMessage');
        if (errorMessage) {
            errorMessage.textContent = '网络错误: ' + error.message;
        }
        techErrorArea.style.display = 'block';
        showNotification('技术方案生成失败', 'error');
    });
}

// ==================== 文档预览功能 ====================

/**
 * 预览技术方案文档
 */
function previewTechDocument(downloadUrl, filename) {
    const previewUrl = `/preview-document?file=${encodeURIComponent(downloadUrl)}&filename=${encodeURIComponent(filename)}&type=技术方案`;
    window.open(previewUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
}

// ==================== 公司信息显示功能 ====================

/**
 * 显示当前选中的公司信息
 */
function displayCurrentCompany() {
    const companyId = StateManager.getCompanyId();
    console.log('[技术方案] 当前公司ID:', companyId);
    
    if (companyId) {
        loadAndDisplayCompanyInfo(companyId);
    } else {
        showNoCompanyWarning();
    }
}

/**
 * 加载并显示公司信息
 */
function loadAndDisplayCompanyInfo(companyId) {
    fetch('/api/companies')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const company = data.companies.find(c => c.id === companyId);
                if (company) {
                    showCompanyInfo(company);
                } else {
                    console.warn('[技术方案] 未找到公司信息，ID:', companyId);
                    showNoCompanyWarning();
                }
            } else {
                console.error('[技术方案] 加载公司列表失败:', data.error);
                showNoCompanyWarning();
            }
        })
        .catch(error => {
            console.error('[技术方案] 网络错误:', error);
            showNoCompanyWarning();
        });
}

/**
 * 显示公司信息
 */
function showCompanyInfo(company) {
    const companyInfo = document.getElementById('techProposalCompanyInfo');
    const noCompanyWarning = document.getElementById('techProposalNoCompany');
    const companyName = document.getElementById('techProposalCompanyName');
    
    if (companyInfo && companyName) {
        companyName.textContent = company.companyName;
        companyInfo.style.display = 'block';
    }
    
    if (noCompanyWarning) {
        noCompanyWarning.style.display = 'none';
    }
    
    console.log('[技术方案] 已显示公司信息:', company.companyName);
}

/**
 * 显示未选择公司的警告
 */
function showNoCompanyWarning() {
    const companyInfo = document.getElementById('techProposalCompanyInfo');
    const noCompanyWarning = document.getElementById('techProposalNoCompany');
    
    if (companyInfo) {
        companyInfo.style.display = 'none';
    }
    
    if (noCompanyWarning) {
        noCompanyWarning.style.display = 'block';
    }
    
    console.log('[技术方案] 显示未选择公司警告');
}