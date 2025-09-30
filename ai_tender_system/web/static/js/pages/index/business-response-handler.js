// 商务应答功能处理
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
        businessResponseForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const templateFile = document.getElementById('businessTemplateFile').files[0];
            const companyId = document.getElementById('businessCompanySelect').value;
            const projectName = document.getElementById('businessProjectName').value;
            const tenderNo = document.getElementById('businessTenderNo').value;
            const dateText = document.getElementById('businessDate').value;
            const useMcp = 'true'; // 默认使用MCP处理器

            // 验证必填字段
            if (!templateFile) {
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

            // 构建FormData
            const formData = new FormData();
            formData.append('template_file', templateFile);
            formData.append('company_id', companyId);
            formData.append('project_name', projectName);
            formData.append('tender_no', tenderNo);
            formData.append('date_text', dateText);
            formData.append('use_mcp', useMcp);

            // 发送请求
            fetch('/process-business-response', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
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
            })
            .catch(err => {
                if (progress) progress.style.display = 'none';
                // 处理网络错误
                const errorMsg = '网络错误：' + err.message;
                const errorMessage = document.getElementById('businessErrorMessage');
                if (errorMessage) errorMessage.textContent = errorMsg;
                if (error) error.classList.remove('d-none');
                console.error('商务应答处理失败:', err);
            });
        });
    }

    // 公司选择器变更处理
    const businessCompanySelect = document.getElementById('businessCompanySelect');
    if (businessCompanySelect) {
        businessCompanySelect.addEventListener('change', function() {
            updateSelectedCompanyDisplay();
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
function previewBusinessDocument() {
    const downloadLink = document.getElementById('businessDownloadLink');
    if (!downloadLink || !downloadLink.href) {
        if (typeof showNotification === 'function') {
            showNotification('没有可预览的文档', 'warning');
        } else {
            alert('没有可预览的文档');
        }
        return;
    }

    // 从下载链接获取文件路径
    const url = new URL(downloadLink.href, window.location.href);
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

    // 调用API获取文档内容
    fetch(`/api/document/preview/${filename}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (previewContent) {
                    previewContent.innerHTML = data.html_content || '<p>文档内容为空</p>';
                }
            } else {
                if (previewContent) {
                    previewContent.innerHTML = `<div class="alert alert-danger">预览失败: ${data.error || '未知错误'}</div>`;
                }
            }
        })
        .catch(error => {
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
        if (typeof loadDocumentToEditor === 'function') {
            loadDocumentToEditor();
        }
    }, 500);
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

// 更新商务应答页面的隐藏表单字段
function updateBusinessHiddenFields() {
    if (!window.companyStateManager) {
        console.error('公司状态管理器未初始化');
        return;
    }

    const companyData = window.companyStateManager.getSelectedCompany();
    const companySelect = document.getElementById('businessCompanySelect');
    const projectNameInput = document.getElementById('businessProjectName');
    const tenderNoInput = document.getElementById('businessTenderNo');
    const dateInput = document.getElementById('businessDate');

    if (companySelect) {
        companySelect.value = companyData && companyData.company_id ? companyData.company_id : '';
    }

    if (projectNameInput) {
        projectNameInput.value = companyData && companyData.project_name ? companyData.project_name : '';
    }

    // 可以在这里添加招标编号和日期的同步逻辑（如果需要的话）

    console.log('商务应答页面：隐藏字段已更新', companyData);
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
                                <div>
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