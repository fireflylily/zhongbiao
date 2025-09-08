/**
 * 点对点应答页面JavaScript
 */

// 点对点应答页面变量

// 继承原有的点对点应答功能
// 这里包含原始的上传处理逻辑

onPageReady(function() {
    // 设置拖拽上传
    setupDragDrop('uploadArea', 'fileInput', handleFileSelect);
    
    // 设置表单提交
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', submitUpload);
    }
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