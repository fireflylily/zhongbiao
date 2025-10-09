// 商务应答功能处理

// 存储当前公司的资质信息
let currentCompanyQualifications = null;

document.addEventListener('DOMContentLoaded', function() {
    // 从全局状态管理器加载公司和项目信息
    loadBusinessCompanyInfo();

    // 商务应答文件上传处理
    const businessTemplateFile = document.getElementById('businessTemplateFile');
    if (businessTemplateFile) {
        businessTemplateFile.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const fileNameDiv = document.getElementById('businessTemplateFileName');
            if (fileName && fileNameDiv) {
                fileNameDiv.innerHTML = `<div class="alert alert-info py-2"><i class="bi bi-file-earmark-word"></i> ${fileName}</div>`;
            } else if (fileNameDiv) {
                fileNameDiv.innerHTML = '';
            }
        });
    }

    // 商务应答表单提交处理
    const businessResponseForm = document.getElementById('businessResponseForm');
    if (businessResponseForm) {
        businessResponseForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            let templateFile = document.getElementById('businessTemplateFile').files[0];
            const companyId = document.getElementById('businessCompanyId').value;
            const tenderNo = document.getElementById('businessTenderNo').value;
            const dateText = document.getElementById('businessDate').value;
            const useMcp = 'true'; // 默认使用MCP处理器

            // 从全局状态管理器获取项目名称
            const companyData = window.companyStateManager ? window.companyStateManager.getSelectedCompany() : null;
            const projectName = companyData && companyData.project_name ? companyData.project_name : '';

            // 检查是否有从HITL加载的文件URL
            const hasLoadedFile = window.businessResponseFileUrl && window.businessResponseFileName;

            // 验证必填字段 - 需要上传文件或已加载文件
            if (!templateFile && !hasLoadedFile) {
                alert('请选择商务应答模板');
                return;
            }

            if (!companyId) {
                alert('请选择应答公司');
                return;
            }

            // 显示进度条
            const progress = document.getElementById('businessProgress');
            const result = document.getElementById('businessResult');
            const error = document.getElementById('businessError');
            const stats = document.getElementById('businessStats');

            if (progress) progress.style.display = 'block';
            if (result) result.classList.add('d-none');
            if (error) error.classList.add('d-none');
            if (stats) stats.classList.add('d-none');

            try {
                // 如果使用已加载的文件，先下载文件
                if (!templateFile && hasLoadedFile) {
                    console.log('[Business] 从URL下载文件:', window.businessResponseFileUrl);
                    const fileResponse = await fetch(window.businessResponseFileUrl);
                    const fileBlob = await fileResponse.blob();
                    templateFile = new File([fileBlob], window.businessResponseFileName, {
                        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    });
                    console.log('[Business] 文件下载完成:', templateFile.name);
                }

                // 构建FormData
                const formData = new FormData();
                formData.append('template_file', templateFile);
                formData.append('company_id', companyId);
                formData.append('project_name', projectName);
                formData.append('tender_no', tenderNo);
                formData.append('date_text', dateText);
                formData.append('use_mcp', useMcp);

                // 构建并添加图片配置
                const imageConfig = buildImageConfig(companyId);
                if (imageConfig) {
                    formData.append('image_config', JSON.stringify(imageConfig));
                    console.log('添加图片配置到请求:', imageConfig);
                } else {
                    console.log('没有可用的图片配置');
                }

                // 发送请求
                const response = await fetch('/process-business-response', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (progress) progress.style.display = 'none';

                if (data.success) {
                    // 隐藏错误提示，显示成功结果
                    if (error) error.classList.add('d-none');

                    const resultMessage = document.getElementById('businessResultMessage');
                    if (resultMessage) resultMessage.textContent = data.message;

                    const downloadLink = document.getElementById('businessDownloadLink');
                    if (downloadLink) downloadLink.href = data.download_url;

                    if (result) result.classList.remove('d-none');

                    // 显示处理统计
                    if (data.stats) {
                        const statsContent = document.getElementById('businessStatsContent');
                        let statsHtml = '';

                        if (data.stats.bidder_name) {
                            statsHtml += `<p><strong>投标人名称填写：</strong> 段落${data.stats.bidder_name.paragraphs_changed}个，表格${data.stats.bidder_name.tables_changed}个</p>`;
                        }
                        if (data.stats.project_info) {
                            statsHtml += `<p><strong>项目信息填写：</strong> 替换${data.stats.project_info.replacements_made}项，投标人字段${data.stats.project_info.bidder_fields_filled}个</p>`;
                        }
                        if (data.stats.qualification_images) {
                            statsHtml += `<p><strong>资质图片插入：</strong> 找到关键词${data.stats.qualification_images.keywords_found}个，插入图片${data.stats.qualification_images.images_inserted}张</p>`;
                        }

                        if (statsHtml && statsContent) {
                            statsContent.innerHTML = statsHtml;
                            if (stats) stats.classList.remove('d-none');
                        }
                    }

                    // 检查是否从HITL页面跳转过来,如果是则显示"同步到投标项目"按钮
                    const urlParams = new URLSearchParams(window.location.search);
                    const hitlTaskId = urlParams.get('hitl_task_id');

                    if (hitlTaskId) {
                        console.log('[Business] 检测到HITL任务ID,显示同步按钮:', hitlTaskId);
                        const syncBtn = document.getElementById('syncToHitlBtn');
                        if (syncBtn) {
                            syncBtn.style.display = 'inline-block';
                            // 绑定点击事件,传递任务ID和输出文件路径
                            syncBtn.onclick = () => syncToHitlProject(hitlTaskId, data.output_file);
                        }
                    }

                    // 刷新文件列表
                    if (typeof loadBusinessFilesList === 'function') {
                        loadBusinessFilesList();
                    }
                } else {
                    // 处理错误信息
                    const errorMsg = data.error || data.message || '处理失败';
                    const errorMessage = document.getElementById('businessErrorMessage');
                    if (errorMessage) errorMessage.textContent = errorMsg;
                    if (error) error.classList.remove('d-none');
                }
            } catch (err) {
                if (progress) progress.style.display = 'none';
                // 处理网络错误
                const errorMsg = '网络错误：' + err.message;
                const errorMessage = document.getElementById('businessErrorMessage');
                if (errorMessage) errorMessage.textContent = errorMsg;
                if (error) error.classList.remove('d-none');
                console.error('[Business] 处理失败:', err);
            }
        });
    }
    // 下一步按钮处理
    const businessNextStepBtn = document.getElementById('businessNextStepBtn');
    if (businessNextStepBtn) {
        businessNextStepBtn.addEventListener('click', function() {
            // 切换到点对点应答选项卡
            const pointToPointNav = document.getElementById('point-to-point-nav');
            if (pointToPointNav) {
                pointToPointNav.click();
            }
        });
    }
});

// 文档预览功能
let currentDocumentPath = null; // 存储当前文档路径
let wordEditor = null; // WordEditor实例

// 预览商务应答文档
function previewBusinessDocument(customUrl = null) {
    // 确定预览URL：优先使用传入的customUrl，否则从下载按钮获取
    let previewUrl;
    if (customUrl) {
        previewUrl = customUrl;
    } else {
        const downloadLink = document.getElementById('businessDownloadLink');
        if (!downloadLink || !downloadLink.href) {
            if (typeof showNotification === 'function') {
                showNotification('没有可预览的文档', 'warning');
            } else {
                alert('没有可预览的文档');
            }
            return;
        }
        previewUrl = downloadLink.href;
    }

    // 从URL获取文件路径
    const url = new URL(previewUrl, window.location.href);
    const filename = url.pathname.split('/').pop();
    currentDocumentPath = filename;

    // 显示加载状态
    const previewContent = document.getElementById('documentPreviewContent');
    if (previewContent) {
        previewContent.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在加载文档...</p></div>';
    }

    // 显示预览模态框
    const previewModal = new bootstrap.Modal(document.getElementById('documentPreviewModal'));
    previewModal.show();

    // 使用mammoth.js在前端直接转换Word文档
    fetch(previewUrl)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            // 使用mammoth转换Word为HTML
            return mammoth.convertToHtml({arrayBuffer: arrayBuffer});
        })
        .then(result => {
            if (previewContent) {
                const html = result.value || '<p>文档内容为空</p>';
                // 添加样式包装
                previewContent.innerHTML = `
                    <style>
                        #documentPreviewContent {
                            font-family: 'Microsoft YaHei', sans-serif;
                            line-height: 1.8;
                            padding: 20px;
                        }
                        #documentPreviewContent p { margin: 10px 0; }
                        #documentPreviewContent h1, #documentPreviewContent h2, #documentPreviewContent h3 {
                            color: #333;
                            margin: 20px 0 10px 0;
                        }
                        #documentPreviewContent table {
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }
                        #documentPreviewContent table td, #documentPreviewContent table th {
                            border: 1px solid #ddd;
                            padding: 8px;
                        }
                        #documentPreviewContent table th {
                            background-color: #f2f2f2;
                        }
                    </style>
                    <div>${html}</div>
                `;

                // 显示转换警告信息(如果有)
                if (result.messages && result.messages.length > 0) {
                    console.log('Mammoth转换消息:', result.messages);
                }
            }
        })
        .catch(error => {
            console.error('预览失败:', error);
            if (previewContent) {
                previewContent.innerHTML = `<div class="alert alert-danger">预览失败: ${error.message}</div>`;
            }
        });
}

// 编辑商务应答文档
function editBusinessDocument() {
    const downloadLink = document.getElementById('businessDownloadLink');
    if (!downloadLink || !downloadLink.href) {
        if (typeof showNotification === 'function') {
            showNotification('没有可编辑的文档', 'warning');
        } else {
            alert('没有可编辑的文档');
        }
        return;
    }

    // 从下载链接获取文件路径
    const url = new URL(downloadLink.href, window.location.href);
    const filename = url.pathname.split('/').pop();
    currentDocumentPath = filename;

    // 初始化编辑器（如果还没有初始化）
    if (!wordEditor && typeof WordEditor !== 'undefined') {
        wordEditor = new WordEditor('documentEditor', {
            height: 500,
            placeholder: '请点击"读取文档"加载商务应答文档内容...'
        });
    }

    // 显示编辑模态框
    const editModal = new bootstrap.Modal(document.getElementById('documentEditModal'));
    editModal.show();

    // 自动加载文档
    setTimeout(() => {
        loadDocumentToEditor();
    }, 500);
}

// 加载文档到编辑器
function loadDocumentToEditor(retryCount = 0) {
    const maxRetries = 15; // 最多重试15次 (3秒)

    if (!currentDocumentPath) {
        if (typeof showNotification === 'function') {
            showNotification('没有可加载的文档', 'warning');
        } else {
            alert('没有可加载的文档');
        }
        return;
    }

    if (!wordEditor) {
        if (typeof showNotification === 'function') {
            showNotification('编辑器未初始化，请先打开编辑窗口', 'error');
        } else {
            alert('编辑器未初始化，请先打开编辑窗口');
        }
        return;
    }

    // 检查 TinyMCE 编辑器实例是否已初始化
    if (!wordEditor.editor) {
        if (retryCount < maxRetries) {
            console.log(`编辑器还在初始化中，等待重试... (${retryCount + 1}/${maxRetries})`);
            setTimeout(() => {
                loadDocumentToEditor(retryCount + 1);
            }, 200);
            return;
        } else {
            if (typeof showNotification === 'function') {
                showNotification('编辑器初始化超时，请刷新页面重试', 'error');
            } else {
                alert('编辑器初始化超时，请刷新页面重试');
            }
            return;
        }
    }

    // 编辑器已ready，开始加载文档
    console.log('编辑器已就绪，开始加载文档');

    // 方案1：通过预览API获取HTML内容直接加载到编辑器
    fetch(`/api/document/preview/${currentDocumentPath}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.html_content) {
                wordEditor.setContent(data.html_content);
                if (typeof showNotification === 'function') {
                    showNotification('文档内容加载成功', 'success');
                }
            } else {
                throw new Error(data.error || '无法获取文档内容');
            }
        })
        .catch(error => {
            console.error('Document loading error:', error);
            if (typeof showNotification === 'function') {
                showNotification('文档加载失败，尝试备用方案...', 'warning');
            }

            // 方案2：如果预览失败，尝试原始文件加载
            tryLoadOriginalFile();
        });
}

// 尝试加载原始文件的备用方案
function tryLoadOriginalFile() {
    if (!currentDocumentPath || !wordEditor) return;

    fetch(`/download/${currentDocumentPath}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.blob();
        })
        .then(blob => {
            // 确保正确的MIME类型
            const mimeType = currentDocumentPath.endsWith('.docx')
                ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                : 'application/msword';

            const file = new File([blob], currentDocumentPath, {
                type: mimeType
            });

            return wordEditor.loadDocument(file);
        })
        .then(() => {
            if (typeof showNotification === 'function') {
                showNotification('文档加载成功', 'success');
            }
        })
        .catch(error => {
            console.error('Fallback document loading error:', error);
            if (typeof showNotification === 'function') {
                showNotification('文档加载失败: ' + error.message, 'error');
            } else {
                alert('文档加载失败: ' + error.message);
            }
        });
}

// 保存编辑的文档
function saveEditedDocument() {
    if (!wordEditor || !wordEditor.editor) {
        if (typeof showNotification === 'function') {
            showNotification('编辑器未初始化或还在加载中，请稍后再试', 'error');
        } else {
            alert('编辑器未初始化或还在加载中，请稍后再试');
        }
        return;
    }

    const filename = currentDocumentPath ? currentDocumentPath.replace('.docx', '_edited') : 'edited_document';
    wordEditor.saveDocument(filename)
        .then(() => {
            if (typeof showNotification === 'function') {
                showNotification('文档保存成功', 'success');
            }
        })
        .catch(error => {
            if (typeof showNotification === 'function') {
                showNotification('文档保存失败: ' + error.message, 'error');
            } else {
                alert('文档保存失败: ' + error.message);
            }
        });
}

// 清空编辑器
function clearEditor() {
    if (!wordEditor || !wordEditor.editor) {
        if (typeof showNotification === 'function') {
            showNotification('编辑器未初始化或还在加载中，请稍后再试', 'error');
        } else {
            alert('编辑器未初始化或还在加载中，请稍后再试');
        }
        return;
    }

    if (confirm('确定要清空编辑器内容吗？')) {
        wordEditor.clearContent();
        if (typeof showNotification === 'function') {
            showNotification('编辑器已清空', 'info');
        }
    }
}

// 切换到编辑模式
function switchToEditMode() {
    // 关闭预览模态框
    const previewModal = bootstrap.Modal.getInstance(document.getElementById('documentPreviewModal'));
    if (previewModal) {
        previewModal.hide();
    }

    // 打开编辑模态框
    setTimeout(() => {
        editBusinessDocument();
    }, 300);
}

// 加载商务应答页面的公司项目信息
function loadBusinessCompanyInfo() {
    console.log('商务应答页面：加载公司项目信息...');

    // 注意：公司项目信息的显示已由共用组件 company-project-display.js 自动处理
    // 这里只需要更新隐藏的表单字段
    updateBusinessHiddenFields();

    // 监听全局状态变更
    if (window.companyStateManager) {
        window.companyStateManager.addListener(function(companyData) {
            console.log('商务应答页面：接收到公司状态变更', companyData);
            updateBusinessHiddenFields();
        });
    }
}

// 更新商务应答页面的表单字段
function updateBusinessHiddenFields() {
    if (!window.companyStateManager) {
        console.error('公司状态管理器未初始化');
        return;
    }

    const companyData = window.companyStateManager.getSelectedCompany();

    // 更新公司ID（隐藏字段）
    const companyIdInput = document.getElementById('businessCompanyId');
    if (companyIdInput) {
        companyIdInput.value = companyData && companyData.company_id ? companyData.company_id : '';
    }

    // 注意：项目名称现在显示在共用组件中，不需要单独的输入框
    // 可以在这里添加招标编号和日期的同步逻辑（如果需要的话）

    console.log('商务应答页面：表单字段已更新', companyData);

    // 获取公司资质信息
    if (companyData && companyData.company_id) {
        fetchCompanyQualifications(companyData.company_id);
    }
}

// 获取公司资质信息
function fetchCompanyQualifications(companyId) {
    console.log('正在获取公司资质信息:', companyId);

    fetch(`/api/companies/${companyId}/qualifications`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentCompanyQualifications = data.qualifications;
                console.log('获取到公司资质:', currentCompanyQualifications);
            } else {
                console.warn('获取公司资质失败:', data.error);
                currentCompanyQualifications = null;
            }
        })
        .catch(error => {
            console.error('获取公司资质时发生错误:', error);
            currentCompanyQualifications = null;
        });
}

// 构建图片配置对象
function buildImageConfig(companyId) {
    if (!currentCompanyQualifications || Object.keys(currentCompanyQualifications).length === 0) {
        console.log('没有可用的资质信息');
        return null;
    }

    const imageConfig = {};

    // 营业执照
    if (currentCompanyQualifications.business_license) {
        imageConfig.license_path = `/api/companies/${companyId}/qualifications/business_license/download`;
        console.log('添加营业执照路径:', imageConfig.license_path);
    }

    // 公章 (如果有的话)
    if (currentCompanyQualifications.company_seal) {
        imageConfig.seal_path = `/api/companies/${companyId}/qualifications/company_seal/download`;
        console.log('添加公章路径:', imageConfig.seal_path);
    }

    // 资质证书 - 收集所有ISO认证和其他资质
    const qualificationPaths = [];
    const qualificationKeys = ['iso9001', 'iso14001', 'iso20000', 'iso27001', 'cmmi', 'itss',
                               'safety_production', 'software_copyright', 'patent_certificate'];

    for (const key of qualificationKeys) {
        if (currentCompanyQualifications[key]) {
            qualificationPaths.push(`/api/companies/${companyId}/qualifications/${key}/download`);
            console.log(`添加资质证书: ${key}`);
        }
    }

    if (qualificationPaths.length > 0) {
        imageConfig.qualification_paths = qualificationPaths;
    }

    console.log('构建的image_config:', imageConfig);
    return Object.keys(imageConfig).length > 0 ? imageConfig : null;
}

// 加载历史文件列表
function loadBusinessFilesList() {
    fetch('/api/business-files')
        .then(response => response.json())
        .then(data => {
            const filesList = document.getElementById('businessFilesList');
            if (!filesList) return;

            if (data.success && data.files && data.files.length > 0) {
                let html = '<div class="list-group">';
                data.files.forEach(file => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="mb-1">${file.name}</h6>
                                    <small class="text-muted">${file.date} | ${file.size}</small>
                                </div>
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-sm btn-success" onclick="previewBusinessDocument('${file.download_url}')">
                                        <i class="bi bi-eye"></i> 预览
                                    </button>
                                    <a href="${file.download_url}" class="btn btn-sm btn-primary">
                                        <i class="bi bi-download"></i> 下载
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                filesList.innerHTML = html;
            } else {
                filesList.innerHTML = '<p class="text-muted">暂无历史文件</p>';
            }
        })
        .catch(error => {
            console.error('加载历史文件失败:', error);
            const filesList = document.getElementById('businessFilesList');
            if (filesList) {
                filesList.innerHTML = '<p class="text-danger">加载失败</p>';
            }
        });
}

/**
 * 将商务应答生成的文件同步到HITL投标项目
 * @param {string} hitlTaskId - HITL任务ID
 * @param {string} filePath - 商务应答生成的文件路径
 */
async function syncToHitlProject(hitlTaskId, filePath) {
    console.log('[syncToHitlProject] 开始同步文件到HITL项目');
    console.log('[syncToHitlProject] 任务ID:', hitlTaskId);
    console.log('[syncToHitlProject] 文件路径:', filePath);

    const btn = document.getElementById('syncToHitlBtn');
    if (!btn) {
        console.error('[syncToHitlProject] 未找到同步按钮');
        return;
    }

    // 确认对话框
    if (!confirm('确认将此文件同步到投标项目吗?\n\n同步后,您可以在HITL投标项目的"应答完成文件"标签页中查看此文件。')) {
        return;
    }

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>同步中...';

    try {
        const response = await fetch(`/api/tender-processing/sync-business-response/${hitlTaskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_path: filePath
            })
        });

        const data = await response.json();
        console.log('[syncToHitlProject] API响应:', data);

        if (data.success) {
            // 显示成功状态
            btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已同步';
            btn.classList.remove('btn-info');
            btn.classList.add('btn-outline-success');

            // 显示成功通知
            if (typeof showNotification === 'function') {
                showNotification(data.message || '文件已成功同步到投标项目', 'success');
            } else {
                alert(data.message || '文件已成功同步到投标项目');
            }

            console.log('[syncToHitlProject] 同步成功');

            // 3秒后恢复按钮(允许重新同步)
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.classList.remove('btn-outline-success');
                btn.classList.add('btn-info');
                btn.disabled = false;
            }, 3000);
        } else {
            throw new Error(data.error || '同步失败');
        }
    } catch (error) {
        console.error('[syncToHitlProject] 同步失败:', error);
        btn.innerHTML = originalText;
        btn.disabled = false;

        // 显示错误通知
        const errorMsg = '同步失败: ' + error.message;
        if (typeof showNotification === 'function') {
            showNotification(errorMsg, 'error');
        } else {
            alert(errorMsg);
        }
    }
}