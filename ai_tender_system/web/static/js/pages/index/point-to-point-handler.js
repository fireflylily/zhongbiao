// 点对点应答功能处理
document.addEventListener('DOMContentLoaded', function() {
    console.log('初始化点对点应答页面...');

    // 初始化应答方式切换逻辑
    initResponseModeToggle();

    // 初始化公司状态管理
    initCompanyStateManagement();

    // 初始化文件上传功能
    initFileUpload();

    // 初始化表单提交
    initFormSubmission();
});

// 初始化应答方式切换逻辑
function initResponseModeToggle() {
    const responseModeSelect = document.getElementById('responseMode');
    const aiModelSelection = document.getElementById('aiModelSelection');

    if (!responseModeSelect || !aiModelSelection) {
        console.log('应答方式或AI模型选择元素未找到');
        return;
    }

    // 添加变化监听器
    responseModeSelect.addEventListener('change', function() {
        const selectedMode = this.value;
        console.log('应答方式切换为:', selectedMode);

        if (selectedMode === 'ai') {
            aiModelSelection.style.display = 'block';
            aiModelSelection.classList.remove('d-none');
        } else {
            aiModelSelection.style.display = 'none';
            aiModelSelection.classList.add('d-none');
        }
    });

    // 初始状态设置
    const initialMode = responseModeSelect.value;
    if (initialMode === 'ai') {
        aiModelSelection.style.display = 'block';
        aiModelSelection.classList.remove('d-none');
    } else {
        aiModelSelection.style.display = 'none';
        aiModelSelection.classList.add('d-none');
    }

    console.log('应答方式切换功能初始化完成');
}

// 初始化公司状态管理
function initCompanyStateManagement() {
    console.log('初始化点对点应答公司状态管理...');

    // 注意：公司项目信息的显示已由共用组件 company-project-display.js 自动处理
    // 这里只需要更新隐藏的表单字段
    updatePointToPointHiddenFields();

    // 监听公司状态变更
    if (window.companyStateManager) {
        window.companyStateManager.addListener(function(companyData) {
            console.log('点对点应答页面：接收到公司状态变更', companyData);
            updatePointToPointHiddenFields();
        });
    }
}

// 更新点对点应答页面的隐藏表单字段
function updatePointToPointHiddenFields() {
    const companySelect = document.getElementById('companySelect');

    if (!window.companyStateManager) {
        console.error('公司状态管理器未初始化');
        return;
    }

    const companyData = window.companyStateManager.getSelectedCompany();

    if (companySelect) {
        companySelect.value = companyData && companyData.company_id ? companyData.company_id : '';
    }

    console.log('点对点应答页面：隐藏字段已更新', companyData);
}


// 初始化文件上传功能
function initFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const processBtn = document.getElementById('processBtn');

    if (!uploadArea || !fileInput) {
        console.log('文件上传元素未找到');
        return;
    }

    // 上传区域点击事件
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择事件
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            displayFileInfo(file);
            updateProcessButton();
        }
    });

    // 拖拽上传
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            displayFileInfo(files[0]);
            updateProcessButton();
        }
    }

    function displayFileInfo(file) {
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = `(${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        if (fileInfo) fileInfo.classList.remove('d-none');
    }

    function updateProcessButton() {
        const companySelect = document.getElementById('pointToPointCompanyId');
        const technicalFileTaskId = document.getElementById('technicalFileTaskId');

        // 检查是否有上传的文件或从HITL传递过来的技术需求文件
        const hasFile = fileInput.files.length > 0 || (technicalFileTaskId && technicalFileTaskId.value);
        const hasCompany = companySelect && companySelect.value;

        if (processBtn) {
            processBtn.disabled = !(hasFile && hasCompany);
        }

        console.log('[updateProcessButton] 按钮状态更新:', {
            hasFile,
            hasCompany,
            disabled: !(hasFile && hasCompany)
        });
    }

    // 公司选择变化时也要更新按钮状态
    const companySelect = document.getElementById('pointToPointCompanyId');
    if (companySelect) {
        companySelect.addEventListener('change', updateProcessButton);
    }

    // 监听技术需求文件加载事件
    document.addEventListener('technicalFileLoaded', function(e) {
        console.log('[point-to-point] 收到技术需求文件加载事件:', e.detail);
        updateProcessButton();
    });
}

// 防止默认拖拽行为
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// 初始化表单提交
function initFormSubmission() {
    const uploadForm = document.getElementById('uploadForm');
    if (!uploadForm) {
        console.log('上传表单未找到');
        return;
    }

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitPointToPointForm();
    });
}

// 提交点对点应答表单
function submitPointToPointForm() {
    const fileInput = document.getElementById('fileInput');
    const companySelect = document.getElementById('pointToPointCompanyId');
    const responseFrequency = document.getElementById('responseFrequency');
    const responseMode = document.getElementById('responseMode');
    const aiModel = document.getElementById('aiModel');
    const technicalFileTaskId = document.getElementById('technicalFileTaskId');
    const technicalFileUrl = document.getElementById('technicalFileUrl');

    // 检查是否有上传的文件或从HITL传递的技术需求文件
    const hasUploadedFile = fileInput.files[0];
    const hasTechnicalFile = technicalFileTaskId && technicalFileTaskId.value;

    // 验证必填字段
    if (!hasUploadedFile && !hasTechnicalFile) {
        alert('请选择文件或从HITL页面传递技术需求文件');
        return;
    }

    if (!companySelect || !companySelect.value) {
        alert('请选择公司');
        return;
    }

    // 显示进度条
    const progressBar = document.getElementById('progressBar');
    const resultArea = document.getElementById('resultArea');
    const errorArea = document.getElementById('errorArea');
    const processBtn = document.getElementById('processBtn');

    if (progressBar) progressBar.classList.remove('d-none');
    if (resultArea) resultArea.classList.add('d-none');
    if (errorArea) errorArea.classList.add('d-none');

    // 构建FormData
    const formData = new FormData();

    // 如果有上传的文件，使用上传的文件
    if (hasUploadedFile) {
        formData.append('file', fileInput.files[0]);
    }
    // 否则，传递HITL任务ID，让后端从HITL任务中获取技术需求文件
    else if (hasTechnicalFile) {
        formData.append('hitl_task_id', technicalFileTaskId.value);
        formData.append('use_hitl_technical_file', 'true');
    }

    formData.append('companyId', companySelect.value);
    formData.append('responseFrequency', responseFrequency?.value || 'every_paragraph');
    formData.append('responseMode', responseMode?.value || 'simple');

    // 添加项目名称（如果有）
    if (window.companyStateManager) {
        const projectName = window.companyStateManager.getProjectName();
        if (projectName) {
            formData.append('projectName', projectName);
        }
    }

    if (responseMode?.value === 'ai' && aiModel) {
        formData.append('aiModel', aiModel.value);
    }

    // 禁用提交按钮
    if (processBtn) {
        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 处理中...';
    }

    // 模拟进度
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        const progressBarInner = document.querySelector('#progressBar .progress-bar');
        if (progressBarInner) progressBarInner.style.width = progress + '%';
    }, 500);

    // 创建超时控制器
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟超时

    fetch('/process-point-to-point', {
        method: 'POST',
        body: formData,
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        clearInterval(progressInterval);
        const progressBarInner = document.querySelector('#progressBar .progress-bar');
        if (progressBarInner) progressBarInner.style.width = '100%';

        if (data.success) {
            const resultMessage = document.getElementById('resultMessage');
            if (resultMessage) resultMessage.textContent = data.message;

            // 设置下载按钮事件
            const downloadBtn = document.getElementById('downloadBtn');
            if (data.download_url && data.filename && downloadBtn) {
                downloadBtn.onclick = function(e) {
                    e.preventDefault();
                    downloadFile(data.download_url, data.filename);
                };
            }

            // 设置预览按钮事件
            const previewBtn = document.getElementById('previewBtn');
            if (data.filename && previewBtn) {
                previewBtn.onclick = function(e) {
                    e.preventDefault();
                    // 使用预览API而不是直接打开下载URL，避免触发文件下载
                    previewPointToPointResultDocument(data.filename);
                };
            }

            // 设置"确认完成并返回主页"按钮事件
            const confirmCompleteBtn = document.getElementById('confirmCompleteBtn');
            if (confirmCompleteBtn) {
                confirmCompleteBtn.onclick = function(e) {
                    e.preventDefault();
                    // 返回主页
                    window.location.href = '/';
                };
            }

            if (resultArea) resultArea.classList.remove('d-none');
        } else {
            const errorMessage = document.getElementById('errorMessage');
            // 处理错误信息，如果是对象则转换为字符串
            let errorText = data.error || data.message || '处理失败';
            if (typeof errorText === 'object') {
                errorText = JSON.stringify(errorText, null, 2);
            }
            if (errorMessage) errorMessage.textContent = errorText;
            if (errorArea) errorArea.classList.remove('d-none');
            console.error('[submitPointToPointForm] 处理失败:', data);
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        let errorMsg = '上传失败: ';

        if (error.name === 'AbortError') {
            errorMsg += '请求超时，文档过大或网络不稳定。建议：1) 检查网络连接 2) 尝试更小的文档 3) 点击重试';
        } else if (error.message.includes('Failed to fetch')) {
            errorMsg += '网络连接失败，请检查网络状态后重试';
        } else {
            errorMsg += error.message;
        }

        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) errorMessage.textContent = errorMsg;
        if (errorArea) errorArea.classList.remove('d-none');
        console.error('[submitPointToPointForm] 请求失败:', error);
    })
    .finally(() => {
        setTimeout(() => {
            if (progressBar) progressBar.classList.add('d-none');
            const progressBarInner = document.querySelector('#progressBar .progress-bar');
            if (progressBarInner) progressBarInner.style.width = '0%';
            if (processBtn) {
                processBtn.disabled = false;
                processBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始处理';
            }
        }, 1000);
    });
}

// 下载文件功能
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 刷新公司列表
function refreshCompanies() {
    loadCompaniesToSelector();
}

// 重试和重置功能
document.addEventListener('DOMContentLoaded', function() {
    const retryBtn = document.getElementById('retryBtn');
    const resetBtn = document.getElementById('resetBtn');

    if (retryBtn) {
        retryBtn.addEventListener('click', function() {
            submitPointToPointForm();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // 重置表单
            const uploadForm = document.getElementById('uploadForm');
            if (uploadForm) uploadForm.reset();

            // 隐藏文件信息
            const fileInfo = document.getElementById('fileInfo');
            if (fileInfo) fileInfo.classList.add('d-none');

            // 隐藏结果和错误区域
            const resultArea = document.getElementById('resultArea');
            const errorArea = document.getElementById('errorArea');
            if (resultArea) resultArea.classList.add('d-none');
            if (errorArea) errorArea.classList.add('d-none');

            // 重新设置按钮状态
            const processBtn = document.getElementById('processBtn');
            if (processBtn) {
                processBtn.disabled = true;
                processBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始处理';
            }
        });
    }
});

// 刷新模型列表（与ModelManager集成）
function refreshModels() {
    if (typeof ModelManager !== 'undefined' && ModelManager.loadModels) {
        ModelManager.loadModels();
    } else {
        console.log('ModelManager未找到，无法刷新模型列表');
    }
}

// 模型选择变化事件（与ModelManager集成）
function onModelChange() {
    if (typeof ModelManager !== 'undefined') {
        const aiModelSelect = document.getElementById('aiModel');
        if (aiModelSelect) {
            ModelManager.currentModel = aiModelSelect.value;
            if (ModelManager.updateModelStatus) {
                ModelManager.updateModelStatus();
            }
        }
    }
}

// 加载点对点应答历史文件列表
function loadPointToPointFilesList() {
    console.log('开始加载点对点应答历史文件列表...');

    const tableBody = document.getElementById('pointToPointFilesTableBody');
    const noFilesDiv = document.getElementById('pointToPointNoFiles');

    if (!tableBody) {
        console.error('找不到点对点应答文件列表表格体');
        return;
    }

    // 显示加载状态
    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center text-muted">
                <i class="bi bi-hourglass-split"></i> 加载中...
            </td>
        </tr>
    `;

    // 隐藏空状态
    if (noFilesDiv) {
        noFilesDiv.classList.add('d-none');
    }

    fetch('/api/point-to-point/files')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误! 状态: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('点对点应答文件列表API返回:', data);

            if (data.success && data.data && data.data.length > 0) {
                displayPointToPointFilesList(data.data);
            } else {
                // 显示空状态
                tableBody.innerHTML = '';
                if (noFilesDiv) {
                    noFilesDiv.classList.remove('d-none');
                }
            }
        })
        .catch(error => {
            console.error('加载点对点应答文件列表失败:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        <i class="bi bi-exclamation-triangle"></i> 加载失败: ${error.message}
                        <br>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadPointToPointFilesList()">
                            <i class="bi bi-arrow-clockwise"></i> 重试
                        </button>
                    </td>
                </tr>
            `;
        });
}

// 显示点对点应答文件列表
function displayPointToPointFilesList(files) {
    const tableBody = document.getElementById('pointToPointFilesTableBody');
    const template = document.getElementById('pointToPointFileRowTemplate');

    if (!tableBody || !template) {
        console.error('找不到表格体或行模板元素');
        return;
    }

    // 清空表格
    tableBody.innerHTML = '';

    files.forEach(file => {
        // 克隆模板
        const row = template.content.cloneNode(true);

        // 填充数据
        row.querySelector('.file-name').textContent = file.original_filename || file.filename || '未知文件';
        row.querySelector('.company-name').textContent = file.company_name || '未知公司';
        row.querySelector('.process-time').textContent = formatDateTime(file.created_at || file.process_time);

        // 设置状态
        const statusCell = row.querySelector('.status');
        if (file.status === 'completed' || file.status === 'success') {
            statusCell.innerHTML = '<span class="badge bg-success">已完成</span>';
        } else if (file.status === 'processing') {
            statusCell.innerHTML = '<span class="badge bg-warning">处理中</span>';
        } else if (file.status === 'failed' || file.status === 'error') {
            statusCell.innerHTML = '<span class="badge bg-danger">失败</span>';
        } else {
            statusCell.innerHTML = '<span class="badge bg-secondary">未知</span>';
        }

        // 设置按钮的数据属性
        const previewBtn = row.querySelector('.preview-btn');
        const editBtn = row.querySelector('.edit-btn');
        const downloadBtn = row.querySelector('.download-btn');

        const filePath = file.output_path || file.file_path || '';
        const fileId = file.id || file.file_id || '';

        if (previewBtn) {
            previewBtn.setAttribute('data-file-path', filePath);
            previewBtn.setAttribute('data-file-id', fileId);
            previewBtn.setAttribute('data-filename', file.original_filename || file.filename || '');
        }

        if (editBtn) {
            editBtn.setAttribute('data-file-path', filePath);
            editBtn.setAttribute('data-file-id', fileId);
            editBtn.setAttribute('data-filename', file.original_filename || file.filename || '');
        }

        if (downloadBtn) {
            downloadBtn.setAttribute('data-file-path', filePath);
            downloadBtn.setAttribute('data-file-id', fileId);
            downloadBtn.setAttribute('data-filename', file.original_filename || file.filename || '');
        }

        // 添加到表格
        tableBody.appendChild(row);
    });

    console.log(`成功显示 ${files.length} 个点对点应答文件`);
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '未知时间';

    try {
        const date = new Date(dateTimeStr);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('日期格式化失败:', error);
        return dateTimeStr;
    }
}

// 预览点对点应答文档
function previewPointDocument(button) {
    const filePath = button.getAttribute('data-file-path');
    const fileId = button.getAttribute('data-file-id');
    const filename = button.getAttribute('data-filename');

    if (!filePath && !fileId) {
        alert('无法获取文件信息');
        return;
    }

    console.log('预览点对点应答文档:', { filePath, fileId, filename });

    // 构建预览URL
    let previewUrl = '/api/point-to-point/preview';
    if (fileId) {
        previewUrl += `?file_id=${fileId}`;
    } else if (filePath) {
        previewUrl += `?file_path=${encodeURIComponent(filePath)}`;
    }

    // 在新窗口中打开预览
    const previewWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');

    if (!previewWindow) {
        alert('浏览器阻止了弹出窗口，请检查弹出窗口设置');
        return;
    }

    // 显示加载状态
    previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>预览: ${filename || '文档'}</title>
            <meta charset="utf-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body>
            <div class="container-fluid">
                <div class="d-flex justify-content-center align-items-center" style="height: 100vh;">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3">正在加载文档预览...</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    `);

    // 使用mammoth.js在前端转换Word文档
    fetch(previewUrl)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            // 使用mammoth转换Word为HTML
            return mammoth.convertToHtml({arrayBuffer: arrayBuffer});
        })
        .then(result => {
            const html = result.value || '<p>文档内容为空</p>';

            // 显示转换警告信息(如果有)
            if (result.messages && result.messages.length > 0) {
                console.log('Mammoth转换消息:', result.messages);
            }

            previewWindow.document.open();
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>预览: ${filename || '文档'}</title>
                    <meta charset="utf-8">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
                    <style>
                        body { font-family: 'SimSun', 'Microsoft YaHei', serif; }
                        .preview-header { background: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 1rem; position: sticky; top: 0; z-index: 1000; }
                        .preview-content {
                            padding: 2rem;
                            max-width: 900px;
                            margin: 0 auto;
                            line-height: 1.8;
                        }
                        .preview-content p { margin: 10px 0; }
                        .preview-content h1,
                        .preview-content h2,
                        .preview-content h3,
                        .preview-content h4,
                        .preview-content h5,
                        .preview-content h6 {
                            margin: 20px 0 10px 0;
                            font-weight: bold;
                        }
                        .preview-content table {
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }
                        .preview-content table td,
                        .preview-content table th {
                            border: 1px solid #ddd;
                            padding: 8px;
                        }
                        .preview-content table th {
                            background-color: #f2f2f2;
                            font-weight: bold;
                        }
                        .preview-content ul,
                        .preview-content ol {
                            margin: 10px 0;
                            padding-left: 30px;
                        }
                    </style>
                </head>
                <body>
                    <div class="preview-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="bi bi-file-earmark-text me-2"></i>${filename || '文档预览'}</h5>
                            <button class="btn btn-outline-secondary btn-sm" onclick="window.close()">
                                <i class="bi bi-x-lg"></i> 关闭
                            </button>
                        </div>
                    </div>
                    <div class="preview-content">
                        ${html}
                    </div>
                </body>
                </html>
            `);
            previewWindow.document.close();
        })
        .catch(error => {
            console.error('文档预览失败:', error);
            previewWindow.document.open();
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>预览错误</title>
                    <meta charset="utf-8">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="alert alert-danger">
                            <h5><i class="bi bi-exclamation-triangle me-2"></i>预览失败</h5>
                            <p>无法预览此文档: ${error.message}</p>
                            <button class="btn btn-outline-secondary" onclick="window.close()">关闭</button>
                        </div>
                    </div>
                </body>
                </html>
            `);
            previewWindow.document.close();
        });
}

// 预览点对点处理结果文档（处理完成后的预览按钮）
function previewPointToPointResultDocument(filename) {
    if (!filename) {
        alert('无法获取文件信息');
        return;
    }

    console.log('预览点对点结果文档:', filename);

    // 使用预览API而不是直接下载URL
    const previewApiUrl = `/api/document/preview/${encodeURIComponent(filename)}`;

    // 在新窗口中打开预览
    const previewWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');

    if (!previewWindow) {
        alert('浏览器阻止了弹出窗口，请检查弹出窗口设置');
        return;
    }

    // 显示加载状态
    previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>预览: ${filename}</title>
            <meta charset="utf-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body>
            <div class="container-fluid">
                <div class="d-flex justify-content-center align-items-center" style="height: 100vh;">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3">正在加载文档预览...</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    `);

    // 使用mammoth.js在前端转换Word文档
    fetch(previewApiUrl)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            // 使用mammoth转换Word为HTML
            return mammoth.convertToHtml({arrayBuffer: arrayBuffer});
        })
        .then(result => {
            const html = result.value || '<p>文档内容为空</p>';

            // 显示转换警告信息(如果有)
            if (result.messages && result.messages.length > 0) {
                console.log('Mammoth转换消息:', result.messages);
            }

            previewWindow.document.open();
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>预览: ${filename}</title>
                    <meta charset="utf-8">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
                    <style>
                        body { font-family: 'SimSun', 'Microsoft YaHei', serif; }
                        .preview-header { background: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 1rem; position: sticky; top: 0; z-index: 1000; }
                        .preview-content {
                            padding: 2rem;
                            max-width: 900px;
                            margin: 0 auto;
                            line-height: 1.8;
                        }
                        .preview-content p { margin: 10px 0; }
                        .preview-content h1,
                        .preview-content h2,
                        .preview-content h3,
                        .preview-content h4,
                        .preview-content h5,
                        .preview-content h6 {
                            margin: 20px 0 10px 0;
                            font-weight: bold;
                        }
                        .preview-content table {
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }
                        .preview-content table td,
                        .preview-content table th {
                            border: 1px solid #ddd;
                            padding: 8px;
                        }
                        .preview-content table th {
                            background-color: #f2f2f2;
                            font-weight: bold;
                        }
                        .preview-content ul,
                        .preview-content ol {
                            margin: 10px 0;
                            padding-left: 30px;
                        }
                    </style>
                </head>
                <body>
                    <div class="preview-header">
                        <div class="container-fluid">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0"><i class="bi bi-file-earmark-text me-2"></i>${filename}</h5>
                                <button class="btn btn-secondary btn-sm" onclick="window.close()">
                                    <i class="bi bi-x-lg me-1"></i>关闭
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="container">
                        <div class="preview-content">
                            ${html}
                        </div>
                    </div>
                </body>
                </html>
            `);
            previewWindow.document.close();
        })
        .catch(error => {
            console.error('文档预览失败:', error);
            previewWindow.document.open();
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>预览错误</title>
                    <meta charset="utf-8">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="alert alert-danger">
                            <h5><i class="bi bi-exclamation-triangle me-2"></i>预览失败</h5>
                            <p>无法预览此文档: ${error.message}</p>
                            <button class="btn btn-outline-secondary" onclick="window.close()">关闭</button>
                        </div>
                    </div>
                </body>
                </html>
            `);
            previewWindow.document.close();
        });
}

// 编辑点对点应答文档
function editPointDocument(button) {
    const filePath = button.getAttribute('data-file-path');
    const fileId = button.getAttribute('data-file-id');
    const filename = button.getAttribute('data-filename');

    if (!filePath && !fileId) {
        alert('无法获取文件信息');
        return;
    }

    console.log('编辑点对点应答文档:', { filePath, fileId, filename });

    // 构建编辑URL
    let editUrl = '/api/point-to-point/edit';
    if (fileId) {
        editUrl += `?file_id=${fileId}`;
    } else if (filePath) {
        editUrl += `?file_path=${encodeURIComponent(filePath)}`;
    }

    // 在新窗口中打开编辑器
    const editWindow = window.open('', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');

    if (!editWindow) {
        alert('浏览器阻止了弹出窗口，请检查弹出窗口设置');
        return;
    }

    // 显示加载状态
    editWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>编辑: ${filename || '文档'}</title>
            <meta charset="utf-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body>
            <div class="container-fluid">
                <div class="d-flex justify-content-center align-items-center" style="height: 100vh;">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3">正在加载文档编辑器...</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    `);

    // 获取编辑内容
    fetch(editUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误! 状态: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const editableContent = data.content || data.html || '';
                createDocumentEditor(editWindow, filename, editableContent, editUrl);
            } else {
                throw new Error(data.error || '加载编辑内容失败');
            }
        })
        .catch(error => {
            console.error('文档编辑失败:', error);
            editWindow.document.open();
            editWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>编辑错误</title>
                    <meta charset="utf-8">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="alert alert-danger">
                            <h5><i class="bi bi-exclamation-triangle me-2"></i>编辑失败</h5>
                            <p>无法编辑此文档: ${error.message}</p>
                            <button class="btn btn-outline-secondary" onclick="window.close()">关闭</button>
                        </div>
                    </div>
                </body>
                </html>
            `);
            editWindow.document.close();
        });
}

// 创建文档编辑器
function createDocumentEditor(editWindow, filename, content, saveUrl) {
    editWindow.document.open();
    editWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>编辑: ${filename || '文档'}</title>
            <meta charset="utf-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css" rel="stylesheet">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
                .editor-header { background: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 1rem; position: sticky; top: 0; z-index: 1000; }
                .editor-content { padding: 1rem; }
                .editor-textarea { font-family: 'Courier New', monospace; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="editor-header">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-pencil me-2"></i>编辑: ${filename || '文档'}</h5>
                    <div>
                        <button class="btn btn-primary btn-sm me-2" onclick="saveDocument()">
                            <i class="bi bi-check-lg"></i> 保存
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="window.close()">
                            <i class="bi bi-x-lg"></i> 关闭
                        </button>
                    </div>
                </div>
            </div>
            <div class="editor-content">
                <textarea class="form-control editor-textarea" rows="30" id="documentContent">${content}</textarea>
                <div class="mt-3">
                    <small class="text-muted">提示：修改完成后点击"保存"按钮保存更改</small>
                </div>
            </div>

            <script>
                function saveDocument() {
                    const content = document.getElementById('documentContent').value;
                    const saveBtn = document.querySelector('.btn-primary');

                    // 显示保存状态
                    saveBtn.disabled = true;
                    saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 保存中...';

                    fetch('${saveUrl}', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            content: content
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('保存成功！');
                            // 刷新父窗口的文件列表
                            if (window.opener && window.opener.loadPointToPointFilesList) {
                                window.opener.loadPointToPointFilesList();
                            }
                        } else {
                            throw new Error(data.error || '保存失败');
                        }
                    })
                    .catch(error => {
                        console.error('保存失败:', error);
                        alert('保存失败: ' + error.message);
                    })
                    .finally(() => {
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = '<i class="bi bi-check-lg"></i> 保存';
                    });
                }
            </script>
        </body>
        </html>
    `);
    editWindow.document.close();
}

// 下载点对点应答文档
function downloadPointDocument(button) {
    const filePath = button.getAttribute('data-file-path');
    const fileId = button.getAttribute('data-file-id');
    const filename = button.getAttribute('data-filename');

    if (!filePath && !fileId) {
        alert('无法获取文件信息');
        return;
    }

    console.log('下载点对点应答文档:', { filePath, fileId, filename });

    // 构建下载URL
    let downloadUrl = '/api/point-to-point/download';
    if (fileId) {
        downloadUrl += `?file_id=${fileId}`;
    } else if (filePath) {
        downloadUrl += `?file_path=${encodeURIComponent(filePath)}`;
    }

    // 触发下载
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'document';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 在页面加载完成后自动加载历史文件列表
document.addEventListener('DOMContentLoaded', function() {
    // 延迟一下确保其他组件初始化完成
    setTimeout(() => {
        loadPointToPointFilesList();
    }, 1000);
});