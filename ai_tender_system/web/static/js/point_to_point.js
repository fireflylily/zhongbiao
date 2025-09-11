/**
 * 点对点应答页面JavaScript
 */

// 点对点应答页面变量

// 继承原有的点对点应答功能
// 这里包含原始的上传处理逻辑

onPageReady(function() {
    // 显示当前选中的公司信息
    displayCurrentCompany();
    
    // 设置拖拽上传
    setupDragDrop('uploadArea', 'fileInput', handleFileSelect);
    
    // 设置表单提交
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', submitUpload);
    }
    
    // 监听公司状态变化（跨页面同步）
    StateManager.onStateChangeByKey('companyId', function(newCompanyId, oldCompanyId) {
        console.log('[点对点应答] 接收到公司状态变更:', {
            new: newCompanyId,
            old: oldCompanyId
        });
        
        // 重新显示公司信息
        displayCurrentCompany();
    });
});

function handleFileSelect(file) {
    displayFileInfo(file, document.getElementById('fileInfo'));
    document.getElementById('processBtn').disabled = false;
}

function submitUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files[0]) {
        showNotification('请先选择文件', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    const progressBar = document.getElementById('progressBar');
    const resultArea = document.getElementById('resultArea');
    const errorArea = document.getElementById('errorArea');
    const processBtn = document.getElementById('processBtn');
    
    // 显示进度
    progressBar.style.display = 'block';
    resultArea.style.display = 'none';
    errorArea.style.display = 'none';
    
    processBtn.disabled = true;
    processBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 处理中...';
    
    // 模拟进度更新
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        updateProgressBar(progressBar, progress);
    }, 200);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        updateProgressBar(progressBar, 100);
        
        setTimeout(() => {
            progressBar.style.display = 'none';
            processBtn.disabled = false;
            processBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始处理';
            
            if (data.success) {
                document.getElementById('resultMessage').textContent = data.message || '文档处理完成';
                
                const downloadBtn = document.getElementById('downloadBtn');
                const previewBtn = document.getElementById('previewBtn');
                
                if (downloadBtn && data.download_url) {
                    downloadBtn.onclick = () => downloadFile(data.download_url, data.filename);
                }
                
                if (previewBtn && data.download_url) {
                    previewBtn.onclick = () => previewDocument(data.download_url, data.filename, '点对点应答');
                }
                
                resultArea.style.display = 'block';
                showNotification('文档处理成功！', 'success');
            } else {
                document.getElementById('errorMessage').textContent = data.error || '处理失败';
                errorArea.style.display = 'block';
                showNotification('文档处理失败', 'error');
            }
        }, 1000);
    })
    .catch(error => {
        clearInterval(progressInterval);
        progressBar.style.display = 'none';
        processBtn.disabled = false;
        processBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始处理';
        
        document.getElementById('errorMessage').textContent = '网络错误: ' + error.message;
        errorArea.style.display = 'block';
        showNotification('文档处理失败', 'error');
    });
}

// ==================== 文档预览功能 ====================

/**
 * 通用预览文档函数
 */
function previewDocument(downloadUrl, filename, docType) {
    const previewUrl = `/preview-document?file=${encodeURIComponent(downloadUrl)}&filename=${encodeURIComponent(filename)}&type=${encodeURIComponent(docType)}`;
    window.open(previewUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
}

// ==================== 公司信息显示功能 ====================

/**
 * 显示当前选中的公司信息
 */
function displayCurrentCompany() {
    const companyId = StateManager.getCompanyId();
    console.log('[点对点应答] 当前公司ID:', companyId);
    
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
                    console.warn('[点对点应答] 未找到公司信息，ID:', companyId);
                    showNoCompanyWarning();
                }
            } else {
                console.error('[点对点应答] 加载公司列表失败:', data.error);
                showNoCompanyWarning();
            }
        })
        .catch(error => {
            console.error('[点对点应答] 网络错误:', error);
            showNoCompanyWarning();
        });
}

/**
 * 显示公司信息
 */
function showCompanyInfo(company) {
    const companyInfo = document.getElementById('pointToPointCompanyInfo');
    const noCompanyWarning = document.getElementById('pointToPointNoCompany');
    const companyName = document.getElementById('pointToPointCompanyName');
    
    if (companyInfo && companyName) {
        companyName.textContent = company.companyName;
        companyInfo.style.display = 'block';
    }
    
    if (noCompanyWarning) {
        noCompanyWarning.style.display = 'none';
    }
    
    console.log('[点对点应答] 已显示公司信息:', company.companyName);
}

/**
 * 显示未选择公司的警告
 */
function showNoCompanyWarning() {
    const companyInfo = document.getElementById('pointToPointCompanyInfo');
    const noCompanyWarning = document.getElementById('pointToPointNoCompany');
    
    if (companyInfo) {
        companyInfo.style.display = 'none';
    }
    
    if (noCompanyWarning) {
        noCompanyWarning.style.display = 'block';
    }
    
    console.log('[点对点应答] 显示未选择公司警告');
}