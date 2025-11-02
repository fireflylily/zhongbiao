// 商务应答功能处理

// 标记是否从HITL加载了文件（用于保护已加载的格式文件）
let isFileLoadedFromHITL = false;

document.addEventListener('DOMContentLoaded', function() {
    // 从全局状态管理器加载公司和项目信息
    loadBusinessCompanyInfo();

    // 延迟加载历史文件列表（确保DOM完全加载）
    setTimeout(() => {
        loadBusinessFilesList();
    }, 500);

    // ✅ 订阅全局状态变化（自动更新）
    if (window.globalState) {
        // 订阅文件变化
        window.globalState.subscribe('files', function(fileData) {
            if (fileData.type === 'business' && fileData.data) {
                console.log('[Business Response] 收到文件变化通知，自动加载');
                loadBusinessResponseFromHITL();
            }
        });

        // 订阅公司变化
        window.globalState.subscribe('company', function(companyData) {
            console.log('[Business Response] 收到公司变化通知:', companyData);
            const companySelect = document.getElementById('businessCompanyId');
            if (companySelect && companyData.id) {
                companySelect.value = companyData.id;
            }
        });

        // 订阅 AI 模型变化
        window.globalState.subscribe('ai', function(aiData) {
            if (aiData.type === 'selectedModel') {
                console.log('[Business Response] 收到AI模型变化通知:', aiData.data);
                const modelDisplay = document.querySelector('.modelNameDisplay[data-section="business"]');
                if (modelDisplay) {
                    const models = window.globalState.getAvailableModels();
                    const modelInfo = models.find(m => m.name === aiData.data);
                    modelDisplay.textContent = modelInfo ? modelInfo.display_name : aiData.data;
                }
            }
        });
    }

    // 【新增】监听从 HITL Tab 切换过来的事件
    window.addEventListener('loadBusinessResponse', function(event) {
        console.log('[Business Response] loadBusinessResponse 事件触发，event.detail:', event.detail);
        if (event.detail && event.detail.fromHITL) {
            console.log('[Business Response] 条件满足（fromHITL=true），准备调用 loadFromHITL()');
            console.log('[Business Response] 收到来自 HITL 的加载事件:', event.detail);

            // 【修复】延迟执行，确保Tab切换完成后再操作DOM
            console.log('[Business Response] 延迟200ms执行 loadFromHITL()，等待Tab渲染完成...');
            setTimeout(() => {
                console.log('[Business Response] 即将执行 loadBusinessResponseFromHITL()...');
                loadBusinessResponseFromHITL();
                console.log('[Business Response] loadBusinessResponseFromHITL() 调用完成');
            }, 200);
        } else {
            console.warn('[Business Response] 条件不满足，不调用 loadFromHITL()，event.detail:', event.detail);
        }
    });

    // 【新增】监听商务应答Tab显示事件（Bootstrap Tab的shown事件）
    document.addEventListener('shown.bs.tab', function(event) {
        if (event.target.getAttribute('data-bs-target') === '#business-response') {
            console.log('[Business Response] Tab已显示，检查是否需要重新加载文件信息');

            // 检查是否有待显示的文件信息
            if (window.projectDataBridge) {
                const businessFile = window.projectDataBridge.getFileInfo('business');
                if (businessFile?.fileUrl && businessFile?.fileName) {
                    console.log('[Business Response] 检测到有文件信息，重新执行显示逻辑');
                    setTimeout(() => {
                        loadBusinessResponseFromHITL();
                    }, 100);
                }
            }

            // 【新增】如果已经从HITL加载了文件，确保文件信息持续显示
            const currentBusinessFile = window.globalState ? window.globalState.getFile('business') : null;
            if (isFileLoadedFromHITL && currentBusinessFile && currentBusinessFile.fileName) {
                console.log('[Business Response] Tab显示后重新确认文件信息:', currentBusinessFile.fileName);

                setTimeout(() => {
                    const fileNameDiv = document.getElementById('businessTemplateFileName');
                    // 如果文件信息区域是空的，重新设置
                    if (fileNameDiv && !fileNameDiv.innerHTML.trim()) {
                        console.log('[Business Response] 文件信息区域为空，重新设置');
                        fileNameDiv.innerHTML = `
                            <div class="alert alert-success py-2 d-flex align-items-center">
                                <i class="bi bi-file-earmark-word me-2"></i>
                                <span>${currentBusinessFile.fileName}</span>
                                <span class="badge bg-success ms-2">已从投标项目加载</span>
                            </div>
                        `;

                        // 确保上传区域被隐藏
                        const uploadArea = document.getElementById('businessUploadArea');
                        if (uploadArea) {
                            uploadArea.style.display = 'none';
                            uploadArea.onclick = null;
                            uploadArea.style.pointerEvents = 'none';
                            console.log('[Business Response] 已重新隐藏上传区域');
                        }
                    } else if (fileNameDiv) {
                        console.log('[Business Response] 文件信息仍然存在，无需重新设置');
                    }
                }, 150);  // 稍微延迟一点，确保Tab内容完全渲染
            }
        }
    });

    // 商务应答文件上传处理
    const businessTemplateFile = document.getElementById('businessTemplateFile');
    if (businessTemplateFile) {
        businessTemplateFile.addEventListener('change', function() {
            // 如果文件是从HITL加载的，且用户没有选择新文件（点击了取消），则忽略此事件
            if (isFileLoadedFromHITL && !this.files.length) {
                console.log('[Business] 忽略change事件，保护HITL加载的文件信息');
                return;
            }

            const fileName = this.files[0]?.name;
            const fileNameDiv = document.getElementById('businessTemplateFileName');
            if (fileName && fileNameDiv) {
                // 清除HITL标记（用户手动选择了新文件）
                isFileLoadedFromHITL = false;
                fileNameDiv.innerHTML = `<div class="alert alert-info py-2"><i class="bi bi-file-earmark-word"></i> ${fileName}</div>`;
            } else if (fileNameDiv && !isFileLoadedFromHITL) {
                // 只在非HITL加载状态下才清空
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
            const projectName = window.globalState ? window.globalState.getProjectName() : '';

            // ✅ 从 GlobalStateManager 检查是否有从HITL加载的文件
            const loadedBusinessFile = window.globalState ? window.globalState.getFile('business') : null;
            const hasLoadedFile = loadedBusinessFile && loadedBusinessFile.fileUrl && loadedBusinessFile.fileName;

            // 验证必填字段 - 需要上传文件或已加载文件
            if (!templateFile && !hasLoadedFile) {
                window.notifications.warning('请选择商务应答模板');
                return;
            }

            if (!companyId) {
                window.notifications.warning('请选择应答公司');
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
                // 构建FormData
                const formData = new FormData();

                // ✅ 如果使用已加载的HITL文件，传递文件路径而不是重新上传
                if (!templateFile && hasLoadedFile && loadedBusinessFile.filePath) {
                    console.log('[Business] 使用HITL文件路径:', loadedBusinessFile.filePath);
                    formData.append('hitl_file_path', loadedBusinessFile.filePath);
                } else if (templateFile) {
                    // 用户手动上传的文件
                    console.log('[Business] 使用用户上传的文件:', templateFile.name);
                    formData.append('template_file', templateFile);
                } else {
                    // 没有文件路径但有fileUrl，回退到下载文件的方式(向后兼容)
                    console.log('[Business] 从URL下载文件:', loadedBusinessFile.fileUrl);
                    const fileResponse = await fetch(loadedBusinessFile.fileUrl);
                    const fileBlob = await fileResponse.blob();
                    templateFile = new File([fileBlob], loadedBusinessFile.fileName, {
                        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    });
                    formData.append('template_file', templateFile);
                    console.log('[Business] 文件下载完成:', templateFile.name);
                }
                formData.append('company_id', companyId);
                formData.append('project_name', projectName);
                formData.append('tender_no', tenderNo);
                formData.append('date_text', dateText);
                formData.append('use_mcp', useMcp);

                // 注意：图片配置现在由后端自动从数据库加载，无需前端传递

                // ✅ 使用 APIClient 发送请求（支持自动重试）
                const data = await window.apiClient.post('/process-business-response', formData);

                if (progress) progress.style.display = 'none';

                if (data.success) {
                    // 清除HITL标记（已经处理完成，允许用户重新上传新文件）
                    isFileLoadedFromHITL = false;
                    console.log('[Business] 处理成功，已清除HITL标记');

                    // 隐藏错误提示，显示成功结果
                    if (error) error.classList.add('d-none');

                    const resultMessage = document.getElementById('businessResultMessage');
                    if (resultMessage) resultMessage.textContent = data.message;

                    const downloadLink = document.getElementById('businessDownloadLink');
                    if (downloadLink) downloadLink.href = data.download_url;

                    if (result) result.classList.remove('d-none');

                    // 显示处理统计（新增详细资质统计）
                    if (data.image_insertion || data.info_filling || data.table_processing) {
                        const statsContent = document.getElementById('businessStatsContent');
                        let statsHtml = '';

                        // 1. 信息填充统计
                        if (data.info_filling) {
                            const totalFilled = data.info_filling.total_filled || 0;
                            const unfilled = data.info_filling.unfilled_fields || [];
                            if (totalFilled > 0) {
                                statsHtml += `<p><strong>📝 信息填充：</strong> 填充了${totalFilled}个字段`;
                                if (unfilled.length > 0) {
                                    statsHtml += `（${unfilled.length}个字段因数据库无记录未填充）`;
                                }
                                statsHtml += `</p>`;
                            }
                        }

                        // 2. 表格处理统计
                        if (data.table_processing) {
                            const tablesProcessed = data.table_processing.tables_processed || 0;
                            const cellsFilled = data.table_processing.cells_filled || 0;
                            if (tablesProcessed > 0 || cellsFilled > 0) {
                                statsHtml += `<p><strong>📋 表格处理：</strong>`;
                                if (tablesProcessed > 0) statsHtml += ` 处理了${tablesProcessed}个表格`;
                                if (cellsFilled > 0) statsHtml += `，填充了${cellsFilled}个单元格`;
                                statsHtml += `</p>`;
                            }
                        }

                        // 3. 图片插入统计（三分类详细统计）
                        if (data.image_insertion) {
                            const totalImages = data.image_insertion.images_inserted || 0;
                            const filled = data.image_insertion.filled_qualifications || [];
                            const missing = data.image_insertion.missing_qualifications || [];
                            const appended = data.image_insertion.appended_qualifications || [];

                            if (totalImages > 0 || filled.length > 0) {
                                statsHtml += `<p><strong>🖼️ 资质图片插入：</strong>`;

                                // 成功填充统计
                                if (filled.length > 0) {
                                    statsHtml += ` 成功填充${filled.length}个资质（${totalImages}张图片）`;
                                }

                                // 追加资质统计
                                if (appended.length > 0) {
                                    statsHtml += `，追加了${appended.length}个项目要求的资质`;
                                }

                                // 缺失资质统计
                                if (missing.length > 0) {
                                    statsHtml += `，${missing.length}个模板资质因无文件未填充`;
                                }

                                statsHtml += `</p>`;

                                // 显示缺失资质详情（折叠面板）
                                if (missing.length > 0) {
                                    statsHtml += `
                                        <div class="alert alert-warning py-2 mb-2">
                                            <i class="bi bi-exclamation-triangle"></i>
                                            <strong>未填充的资质：</strong>
                                            <ul class="mb-0 mt-2" style="font-size: 0.9em;">
                                    `;
                                    missing.forEach(qual => {
                                        const qualName = qual.qual_name || qual.qual_key || '未知资质';
                                        statsHtml += `<li>${qualName}</li>`;
                                    });
                                    statsHtml += `
                                            </ul>
                                            <small class="text-muted">提示：请在企业信息库中上传相应资质文件</small>
                                        </div>
                                    `;
                                }

                                // 显示追加资质详情
                                if (appended.length > 0) {
                                    statsHtml += `
                                        <div class="alert alert-info py-2 mb-2">
                                            <i class="bi bi-info-circle"></i>
                                            <strong>已追加的资质：</strong>
                                            <ul class="mb-0 mt-2" style="font-size: 0.9em;">
                                    `;
                                    appended.forEach(qual => {
                                        const qualName = qual.qual_name || qual.qual_key || '未知资质';
                                        statsHtml += `<li>${qualName}</li>`;
                                    });
                                    statsHtml += `
                                            </ul>
                                            <small class="text-muted">这些资质在模板中没有预设位置，已追加到文档末尾</small>
                                        </div>
                                    `;
                                }
                            }
                        }

                        if (statsHtml && statsContent) {
                            statsContent.innerHTML = statsHtml;
                            if (stats) stats.classList.remove('d-none');
                        }
                    }

                    // ✅ 检查是否从HITL页面跳转过来,如果是则显示"同步到投标项目"按钮
                    // 优先从全局状态获取 hitlTaskId，兼容URL参数方式
                    let hitlTaskId = null;
                    if (window.globalState) {
                        hitlTaskId = window.globalState.getHitlTaskId();
                        console.log('[Business] 从全局状态获取 HITL 任务ID:', hitlTaskId);
                    }

                    // 如果全局状态中没有，尝试从URL参数获取（向后兼容）
                    if (!hitlTaskId) {
                        const urlParams = new URLSearchParams(window.location.search);
                        hitlTaskId = urlParams.get('hitl_task_id');
                        console.log('[Business] 从URL参数获取 HITL 任务ID:', hitlTaskId);
                    }

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

// ✅ 预览商务应答文档 - 使用 DocumentPreviewUtil
function previewBusinessDocument(customUrl = null) {
    // 确定文件URL：优先使用传入的customUrl，否则从下载按钮获取
    let downloadUrl;
    if (customUrl) {
        downloadUrl = customUrl;
    } else {
        const downloadLink = document.getElementById('businessDownloadLink');
        if (!downloadLink || !downloadLink.href) {
            window.notifications.warning('没有可预览的文档');
            return;
        }
        downloadUrl = downloadLink.href;
    }

    // 从URL获取文件名
    const url = new URL(downloadUrl, window.location.href);
    const filename = url.pathname.split('/').pop();

    // 保存当前文档路径供编辑功能使用
    currentDocumentPath = filename;

    // ✅ 使用 DocumentPreviewUtil 统一预览
    if (window.documentPreviewUtil) {
        window.documentPreviewUtil.preview(downloadUrl, filename);
    } else {
        console.error('[Business Response] DocumentPreviewUtil 未加载');
        window.notifications.error('文档预览功能暂不可用');
    }
}

// 编辑商务应答文档
function editBusinessDocument() {
    const downloadLink = document.getElementById('businessDownloadLink');
    if (!downloadLink || !downloadLink.href) {
        window.notifications.warning('没有可编辑的文档');
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
        window.notifications.warning('没有可加载的文档');
        return;
    }

    if (!wordEditor) {
        window.notifications.error('编辑器未初始化，请先打开编辑窗口');
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
            window.notifications.error('编辑器初始化超时，请刷新页面重试');
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
                window.notifications.success('文档内容加载成功');
            } else {
                throw new Error(data.error || '无法获取文档内容');
            }
        })
        .catch(error => {
            console.error('Document loading error:', error);
            window.notifications.warning('文档加载失败，尝试备用方案...');

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
            window.notifications.success('文档加载成功');
        })
        .catch(error => {
            console.error('Fallback document loading error:', error);
            window.notifications.error('文档加载失败: ' + error.message);
        });
}

// 保存编辑的文档
function saveEditedDocument() {
    if (!wordEditor || !wordEditor.editor) {
        window.notifications.error('编辑器未初始化或还在加载中，请稍后再试');
        return;
    }

    const filename = currentDocumentPath ? currentDocumentPath.replace('.docx', '_edited') : 'edited_document';
    wordEditor.saveDocument(filename)
        .then(() => {
            window.notifications.success('文档保存成功');
        })
        .catch(error => {
            window.notifications.error('文档保存失败: ' + error.message);
        });
}

// 清空编辑器
function clearEditor() {
    if (!wordEditor || !wordEditor.editor) {
        window.notifications.error('编辑器未初始化或还在加载中，请稍后再试');
        return;
    }

    if (confirm('确定要清空编辑器内容吗？')) {
        wordEditor.clearContent();
        window.notifications.info('编辑器已清空');
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
    if (window.globalState) {
        window.globalState.subscribe('company', function(companyData) {
            console.log('商务应答页面：接收到公司状态变更', companyData);
            updateBusinessHiddenFields();
        });
        window.globalState.subscribe('project', function(projectData) {
            console.log('商务应答页面：接收到项目状态变更', projectData);
            updateBusinessHiddenFields();
        });
    }
}

// 更新商务应答页面的表单字段
function updateBusinessHiddenFields() {
    if (!window.globalState) {
        console.error('全局状态管理器未初始化');
        return;
    }

    const company = window.globalState.getCompany();
    const project = window.globalState.getProject();

    // 更新公司ID（隐藏字段）
    const companyIdInput = document.getElementById('businessCompanyId');
    if (companyIdInput) {
        companyIdInput.value = company && company.id ? company.id : '';
    }

    // 注意：项目名称现在显示在共用组件中，不需要单独的输入框
    // 可以在这里添加招标编号和日期的同步逻辑（如果需要的话）

    console.log('商务应答页面：表单字段已更新', { company, project });
}

// 注意：图片配置相关函数已移除
// 图片配置现在由后端自动从数据库加载，提高可靠性并消除前端时序问题

// 加载历史文件列表
function loadBusinessFilesList() {
    console.log('开始加载商务应答历史文件列表...');

    const tableBody = document.getElementById('businessFilesTableBody');
    const noFilesDiv = document.getElementById('businessNoFiles');

    if (!tableBody) {
        console.error('找不到商务应答文件列表表格体');
        return;
    }

    // 显示加载状态
    tableBody.innerHTML = `
        <tr>
            <td colspan="3" class="text-center text-muted">
                <i class="bi bi-hourglass-split"></i> 加载中...
            </td>
        </tr>
    `;

    // 隐藏空状态
    if (noFilesDiv) {
        noFilesDiv.classList.add('d-none');
    }

    // ✅ 使用 APIClient 获取文件列表
    window.apiClient.get('/api/business-files')
        .then(data => {
            console.log('商务应答文件列表API返回:', data);

            if (data.success && data.files && data.files.length > 0) {
                displayBusinessFilesList(data.files);
            } else {
                // 显示空状态
                tableBody.innerHTML = '';
                if (noFilesDiv) {
                    noFilesDiv.classList.remove('d-none');
                }
            }
        })
        .catch(error => {
            console.error('加载商务应答文件列表失败:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-danger">
                        <i class="bi bi-exclamation-triangle"></i> 加载失败: ${error.message}
                        <br>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadBusinessFilesList()">
                            <i class="bi bi-arrow-clockwise"></i> 重试
                        </button>
                    </td>
                </tr>
            `;
        });
}

// 显示商务应答文件列表
function displayBusinessFilesList(files) {
    const tableBody = document.getElementById('businessFilesTableBody');
    const template = document.getElementById('businessFileRowTemplate');

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
        row.querySelector('.file-name').textContent = file.name || '未知文件';
        row.querySelector('.process-time').textContent = file.date || '未知时间';

        // 设置按钮
        const previewBtn = row.querySelector('.preview-btn');
        const downloadBtn = row.querySelector('.download-btn');

        if (previewBtn) {
            previewBtn.setAttribute('data-download-url', file.download_url);
            previewBtn.onclick = function() {
                previewBusinessDocument(file.download_url);
            };
        }

        if (downloadBtn) {
            downloadBtn.setAttribute('href', file.download_url);
        }

        // 添加到表格
        tableBody.appendChild(row);
    });

    console.log(`成功显示 ${files.length} 个商务应答文件`);
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

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>同步中...';

    try {
        // ✅ 使用 APIClient 同步文件
        const data = await window.apiClient.post(`/api/tender-processing/sync-file/${hitlTaskId}`, {
            file_path: filePath,
            file_type: 'business_response'  // 指定文件类型
        });
        console.log('[syncToHitlProject] API响应:', data);

        if (data.success) {
            // 显示成功状态
            btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>已同步';
            btn.classList.remove('btn-info');
            btn.classList.add('btn-outline-success');

            // 显示成功通知
            window.notifications.success(data.message || '文件已成功同步到投标项目');

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
        window.notifications.error(errorMsg);
    }
}

/**
 * ✅ 从HITL投标管理加载数据（使用 HITLFileLoader 简化）
 */
function loadBusinessResponseFromHITL() {
    console.log('[Business Response] 开始从HITL加载数据');

    if (!window.globalState) {
        console.warn('[Business Response] globalState 未定义');
        return;
    }

    // ✅ 1. 更新公司信息
    const company = window.globalState.getCompany();
    if (company && company.id) {
        const companySelect = document.getElementById('businessCompanyId');
        if (companySelect) {
            companySelect.value = company.id || '';
        }
    }

    // ✅ 2. 使用 HITLFileLoader 加载文件（简化100+行代码）
    if (window.HITLFileLoader) {
        const loader = new window.HITLFileLoader({
            fileType: 'business',
            fileInfoElementId: 'businessTemplateFileName',
            uploadAreaId: 'businessUploadArea',  // 正确指向上传区域
            onFileLoaded: (fileData) => {
                // 设置HITL加载标记
                isFileLoadedFromHITL = true;
                console.log('[Business Response] 文件加载完成:', fileData.fileName);
            },
            debug: false  // 关闭详细日志
        });

        const success = loader.load();

        if (!success) {
            console.warn('[Business Response] 未找到商务应答文件');
        }
    } else {
        console.error('[Business Response] HITLFileLoader 未加载');
    }

    console.log('[Business Response] 从HITL加载数据完成');
}