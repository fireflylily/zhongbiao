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
    
    // 从状态管理器恢复选中的公司
    const savedCompanyId = StateManager.getCompanyId();
    if (savedCompanyId && businessCompanySelect) {
        businessCompanySelect.value = savedCompanyId;
    }
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
                    option.textContent = company.name;
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