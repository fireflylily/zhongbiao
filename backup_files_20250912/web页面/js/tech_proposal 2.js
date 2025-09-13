/**
 * 技术方案页面JavaScript
 */

// 页面元素和状态  
let techProposalForm, techTenderFileInput, productFileInput;
let techProgressBar, techResultArea, techErrorArea;
let generateProposalBtn;

onPageReady(function() {
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