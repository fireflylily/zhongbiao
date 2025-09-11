/**
 * 公司选择页面JavaScript
 */

// 页面元素和状态
let companySelect, companyInfoForm, saveCompanyBtn, loadCompanyBtn, newCompanyBtn;
let clearFormBtn, deleteCompanyBtn, companyResultArea, companyErrorArea;
let currentCompanyId = null;
let isLoadingCompany = false;
let qualificationFiles = {};
let customQualificationCounter = 0;

// 数据状态跟踪系统
const FormStateManager = {
    // 状态存储
    state: {
        companyInfoDirty: false,
        qualificationsDirty: false,
        originalCompanyData: {},
        originalQualificationData: {}
    },

    // 设置公司信息脏状态
    setCompanyInfoDirty(dirty = true) {
        this.state.companyInfoDirty = dirty;
        this.updateTabIndicators();
    },

    // 设置资质信息脏状态  
    setQualificationsDirty(dirty = true) {
        this.state.qualificationsDirty = dirty;
        this.updateTabIndicators();
    },

    // 更新标签页视觉指示器
    updateTabIndicators() {
        const companyTab = document.querySelector('a[href="#companyInfo"]');
        const qualTab = document.querySelector('a[href="#qualifications"]');
        
        if (companyTab) {
            if (this.state.companyInfoDirty) {
                if (!companyTab.querySelector('.unsaved-indicator')) {
                    companyTab.innerHTML += ' <span class="unsaved-indicator">●</span>';
                }
            } else {
                const indicator = companyTab.querySelector('.unsaved-indicator');
                if (indicator) indicator.remove();
            }
        }

        if (qualTab) {
            if (this.state.qualificationsDirty) {
                if (!qualTab.querySelector('.unsaved-indicator')) {
                    qualTab.innerHTML += ' <span class="unsaved-indicator">●</span>';
                }
            } else {
                const indicator = qualTab.querySelector('.unsaved-indicator');
                if (indicator) indicator.remove();
            }
        }
    },

    // 保存原始数据快照
    saveCompanyDataSnapshot() {
        if (companyInfoForm) {
            const formData = new FormData(companyInfoForm);
            this.state.originalCompanyData = {};
            for (let [key, value] of formData.entries()) {
                this.state.originalCompanyData[key] = value;
            }
        }
    },

    saveQualificationDataSnapshot() {
        this.state.originalQualificationData = {...qualificationFiles};
    },

    // 检查数据是否有变化
    hasCompanyInfoChanged() {
        if (!companyInfoForm) return false;
        
        const formData = new FormData(companyInfoForm);
        const currentData = {};
        for (let [key, value] of formData.entries()) {
            currentData[key] = value;
        }

        // 比较数据
        const originalKeys = Object.keys(this.state.originalCompanyData);
        const currentKeys = Object.keys(currentData);
        
        if (originalKeys.length !== currentKeys.length) return true;
        
        for (let key of originalKeys) {
            if (this.state.originalCompanyData[key] !== currentData[key]) {
                return true;
            }
        }
        return false;
    },

    hasQualificationChanged() {
        const originalKeys = Object.keys(this.state.originalQualificationData);
        const currentKeys = Object.keys(qualificationFiles);
        
        if (originalKeys.length !== currentKeys.length) return true;
        
        for (let key of originalKeys) {
            if (!qualificationFiles[key] || 
                this.state.originalQualificationData[key].name !== qualificationFiles[key].name) {
                return true;
            }
        }
        return false;
    },

    // 重置所有状态
    reset() {
        this.state.companyInfoDirty = false;
        this.state.qualificationsDirty = false;
        this.state.originalCompanyData = {};
        this.state.originalQualificationData = {};
        this.updateTabIndicators();
    }
};

// 公司信息字段映射
const companyFields = {
    'companyName': '公司名称',
    'establishDate': '成立日期',
    'legalRepresentative': '法定代表人',
    'legalRepresentativePosition': '法定代表人职务',
    'socialCreditCode': '统一社会信用代码',
    'authorizedPersonName': '被授权人名称',
    'authorizedPersonPosition': '被授权人职务',
    'email': '电子邮箱',
    'registeredCapital': '注册资本',
    'companyType': '公司类型',
    'fixedPhone': '固定电话',
    'fax': '传真',
    'postalCode': '邮政编码',
    'registeredAddress': '注册地址',
    'officeAddress': '办公地址',
    'website': '官方网址',
    'employeeCount': '员工人数',
    'companyDescription': '公司简介',
    'businessScope': '经营范围',
    'bankName': '开户行全称',
    'bankAccount': '银行账号'
};

// 标准资质类型定义
const standardQualifications = {
    'business_license': '营业执照',
    'auth_id_front': '被授权人身份证正面',
    'auth_id_back': '被授权人身份证反面', 
    'iso9001': '质量管理体系认证证书',
    'iso27001': '信息安全管理体系认证证书',
    'iso20000': '信息技术管理体系认证证书',
    'credit_corruption': '无贪污受贿记录证明',
    'credit_dishonest': '失信被执行人查询结果',
    'credit_procurement': '政府采购严重违法失信记录查询结果',
    'credit_tax': '重大税收失信主体查询结果'
};

// 存储必要资质要求
let requiredQualifications = [];

onPageReady(function() {
    // 初始化页面元素
    companySelect = document.getElementById('companySelect');
    companyInfoForm = document.getElementById('companyInfoForm');
    saveCompanyBtn = document.getElementById('saveCompanyBtn');
    loadCompanyBtn = document.getElementById('loadCompanyBtn');
    newCompanyBtn = document.getElementById('newCompanyBtn');
    clearFormBtn = document.getElementById('clearFormBtn');
    deleteCompanyBtn = document.getElementById('deleteCompanyBtn');
    companyResultArea = document.getElementById('companyResultArea');
    companyErrorArea = document.getElementById('companyErrorArea');

    // 加载公司列表和项目信息
    loadCompanyList();
    loadProjectInfo();
    initializeQualifications();

    // 设置事件监听器
    companySelect.addEventListener('change', handleCompanySelection);
    saveCompanyBtn.addEventListener('click', saveCompany);
    loadCompanyBtn.addEventListener('click', loadCompanyList);
    newCompanyBtn.addEventListener('click', clearCompanyForm);
    clearFormBtn.addEventListener('click', function() {
        clearCompanyForm();
        clearAllQualificationsInternal();
    });
    deleteCompanyBtn.addEventListener('click', deleteCompany);

    // 初始化资质文件相关事件
    document.getElementById('addCustomQualificationBtn')?.addEventListener('click', addCustomQualification);
    document.getElementById('saveAllQualificationsBtn')?.addEventListener('click', saveAllQualifications);
    document.getElementById('clearAllQualificationsBtn')?.addEventListener('click', clearAllQualifications);

    // 初始化表单变化监听
    initializeFormChangeListeners();
    
    // 初始化标签切换拦截
    initializeTabSwitchInterception();

    // 从状态管理器恢复公司ID
    const savedCompanyId = StateManager.getCompanyId();
    if (savedCompanyId) {
        currentCompanyId = savedCompanyId;
        loadCompanyInfo(savedCompanyId);
    }
});

function loadCompanyList() {
    fetch('/api/companies')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateCompanySelect(data.companies);
            } else {
                showCompanyMessage('加载公司列表失败: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showCompanyMessage('加载公司列表失败: ' + error.message, 'error');
        });
}

function populateCompanySelect(companies) {
    companySelect.innerHTML = '<option value="">请选择公司（选择后自动加载）</option>';
    
    companies.forEach(company => {
        const option = document.createElement('option');
        option.value = company.id;
        option.textContent = company.companyName;
        if (company.id === currentCompanyId) {
            option.selected = true;
        }
        companySelect.appendChild(option);
    });
}

function handleCompanySelection(event) {
    if (isLoadingCompany) return;
    
    const companyId = event.target.value;
    if (companyId) {
        loadCompanyInfo(companyId);
    } else {
        clearCompanyForm();
    }
}

function loadCompanyInfo(companyId) {
    isLoadingCompany = true;
    
    fetch(`/api/companies/${companyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateCompanyForm(data.company);
                currentCompanyId = companyId;
                deleteCompanyBtn.style.display = 'inline-block';
                
                // 保存到状态管理器
                StateManager.setCompanyId(companyId);
                
                // 加载资质文件信息
                loadCompanyQualifications(companyId);
                
                showCompanyMessage('公司信息加载成功', 'success');
            } else {
                showCompanyMessage('加载公司信息失败: ' + (data.error || '未知错误'), 'error');
            }
        })
        .catch(error => {
            showCompanyMessage('加载公司信息失败: ' + error.message, 'error');
        })
        .finally(() => {
            isLoadingCompany = false;
        });
}

function populateCompanyForm(company) {
    // 先清空所有表单字段，确保不会显示前一家公司的信息
    Object.keys(companyFields).forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            element.value = '';
        }
    });
    
    // 清空资质文件信息，避免显示前一家公司的资质文件
    clearAllQualificationsInternal();
    
    // 再填充新公司的信息
    Object.keys(companyFields).forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element && company.hasOwnProperty(fieldId)) {
            element.value = company[fieldId] || '';
        }
    });
    
    // 设置下拉选择
    if (company.id && companySelect) {
        companySelect.value = company.id;
    }
}

function clearCompanyForm() {
    isLoadingCompany = true;
    companyInfoForm.reset();
    companySelect.value = '';
    currentCompanyId = null;
    deleteCompanyBtn.style.display = 'none';
    hideCompanyMessages();
    
    // 清空状态管理器
    StateManager.remove(StateManager.KEYS.COMPANY_ID);
    
    isLoadingCompany = false;
}

function saveCompany() {
    const companyName = document.getElementById('companyName').value.trim();
    if (!companyName) {
        showCompanyMessage('公司名称不能为空', 'error');
        return;
    }

    const companyData = {};
    Object.keys(companyFields).forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            companyData[fieldId] = element.value.trim();
        }
    });

    const btn = saveCompanyBtn;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> 保存中...';
    btn.disabled = true;

    const url = currentCompanyId ? `/api/companies/${currentCompanyId}` : '/api/companies';
    const method = currentCompanyId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(companyData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentCompanyId = data.company_id || currentCompanyId;
            deleteCompanyBtn.style.display = 'inline-block';
            
            // 保存到状态管理器
            StateManager.setCompanyId(currentCompanyId);
            
            // 重置表单状态为干净状态
            FormStateManager.setCompanyInfoDirty(false);
            FormStateManager.saveCompanyDataSnapshot();
            
            showCompanyMessage(data.message || '公司信息保存成功', 'success');
            loadCompanyList(); // 刷新公司列表
        } else {
            showCompanyMessage('保存失败: ' + (data.error || '未知错误'), 'error');
        }
    })
    .catch(error => {
        showCompanyMessage('保存失败: ' + error.message, 'error');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function deleteCompany() {
    if (!currentCompanyId) {
        showCompanyMessage('没有选中的公司可删除', 'error');
        return;
    }

    if (!confirm('确定要删除这个公司信息吗？此操作不可撤销。')) {
        return;
    }

    const btn = deleteCompanyBtn;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> 删除中...';
    btn.disabled = true;

    fetch(`/api/companies/${currentCompanyId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            clearCompanyForm();
            showCompanyMessage(data.message || '公司信息删除成功', 'success');
            loadCompanyList(); // 刷新公司列表
        } else {
            showCompanyMessage('删除失败: ' + (data.error || '未知错误'), 'error');
        }
    })
    .catch(error => {
        showCompanyMessage('删除失败: ' + error.message, 'error');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function showCompanyMessage(message, type) {
    hideCompanyMessages();
    
    if (type === 'success') {
        document.getElementById('companyResultMessage').textContent = message;
        companyResultArea.style.display = 'block';
        setTimeout(() => {
            companyResultArea.style.display = 'none';
        }, 5000);
    } else {
        document.getElementById('companyErrorMessage').textContent = message;
        companyErrorArea.style.display = 'block';
    }
}

function hideCompanyMessages() {
    companyResultArea.style.display = 'none';
    companyErrorArea.style.display = 'none';
}

function loadProjectInfo() {
    fetch('/api/project-config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.project_info) {
                console.log('项目信息加载成功', data.project_info);
                
                // 存储必要资质要求
                if (data.project_info.requiredQualifications) {
                    requiredQualifications = data.project_info.requiredQualifications;
                    updateQualificationsWithStars();
                }
            }
        })
        .catch(error => {
            console.warn('加载项目信息失败:', error);
        });
}

// 资质文件管理相关函数
function initializeQualifications() {
    const standardQualContainer = document.getElementById('standardQualifications');
    if (!standardQualContainer) return;
    
    // 初始化标准资质项目
    Object.entries(standardQualifications).forEach(([key, name]) => {
        createQualificationItem(key, name, standardQualContainer, false);
    });
}

// 更新资质项目的星标显示
function updateQualificationsWithStars() {
    const allQualItems = document.querySelectorAll('[data-qual-key]');
    
    allQualItems.forEach(item => {
        const key = item.getAttribute('data-qual-key');
        const nameElement = item.querySelector('h6');
        if (!nameElement) return;
        
        // 获取资质名称（去除图标和星标）
        const name = nameElement.textContent.replace(/📋|📄|⭐/g, '').trim();
        
        // 检查是否为必要资质
        const isRequired = requiredQualifications.includes(name) || requiredQualifications.includes(key);
        
        if (isRequired) {
            // 更新边框样式
            const card = item.querySelector('.card');
            if (card) {
                card.classList.remove('border-secondary');
                card.classList.add('border-warning');
            }
            
            // 添加星标（如果还没有）
            if (!nameElement.innerHTML.includes('⭐')) {
                nameElement.innerHTML += '<span class="text-warning ms-2" title="本次招标必要内容">⭐</span>';
            }
        }
    });
}

function createQualificationItem(key, name, container, isCustom = false) {
    const qualItem = document.createElement('div');
    qualItem.className = 'mb-3';
    qualItem.setAttribute('data-qual-key', key);
    
    // 检查是否为必要资质
    const isRequired = requiredQualifications.includes(name) || requiredQualifications.includes(key);
    const starMark = isRequired ? '<span class="text-warning ms-2" title="本次招标必要内容">⭐</span>' : '';
    
    qualItem.innerHTML = `
        <div class="card ${isRequired ? 'border-warning' : 'border-secondary'}">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-3">
                        <h6 class="mb-0">${isCustom ? '📄' : '📋'} ${name}${starMark}</h6>
                    </div>
                    <div class="col-md-6">
                        <input type="file" class="form-control" id="${key}File" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png">
                    </div>
                    <div class="col-md-3">
                        <div class="btn-group w-100">
                            <button type="button" class="btn btn-outline-info btn-sm" onclick="previewQualificationFile('${key}')" disabled>
                                <i class="bi bi-eye"></i> 预览
                            </button>
                            <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeQualificationFile('${key}')" disabled>
                                <i class="bi bi-trash"></i> 删除
                            </button>
                            ${isCustom ? `<button type="button" class="btn btn-outline-secondary btn-sm" onclick="removeCustomQualification('${key}')"><i class="bi bi-x"></i> 移除</button>` : ''}
                        </div>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="text-muted" id="${key}Status">未选择文件</small>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(qualItem);
    
    // 设置文件选择事件
    const fileInput = qualItem.querySelector(`#${key}File`);
    fileInput.addEventListener('change', function(e) {
        handleQualificationFileSelect(key, e.target.files[0]);
    });
    
    // 启用粘贴图片功能
    const cardBody = qualItem.querySelector('.card-body');
    if (cardBody && typeof enablePasteImageUpload === 'function') {
        enablePasteImageUpload(cardBody, function(imageFile) {
            // 将粘贴的图片设置到文件输入框
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(imageFile);
            fileInput.files = dataTransfer.files;
            
            // 触发文件选择事件
            handleQualificationFileSelect(key, imageFile);
        });
    }
}

function handleQualificationFileSelect(key, file) {
    if (!file) return;
    
    const statusElement = document.getElementById(`${key}Status`);
    const previewBtn = document.querySelector(`[onclick="previewQualificationFile('${key}')"]`);
    const deleteBtn = document.querySelector(`[onclick="removeQualificationFile('${key}')"]`);
    
    qualificationFiles[key] = {
        file: file,
        name: file.name,
        size: file.size,
        uploaded: false
    };
    
    statusElement.textContent = `已选择: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    statusElement.className = 'text-success';
    
    previewBtn.disabled = false;
    deleteBtn.disabled = false;
}

function addCustomQualification() {
    const nameInput = document.getElementById('customQualificationName');
    const name = nameInput.value.trim();
    
    if (!name) {
        showCompanyMessage('请输入资质名称', 'error');
        return;
    }
    
    const key = `custom_${++customQualificationCounter}`;
    const container = document.getElementById('customQualifications');
    
    createQualificationItem(key, name, container, true);
    nameInput.value = '';
    
    showCompanyMessage(`已添加自定义资质：${name}`, 'success');
}

function removeCustomQualification(key) {
    const qualElement = document.querySelector(`[data-qual-key="${key}"]`);
    if (qualElement) {
        qualElement.remove();
        delete qualificationFiles[key];
        showCompanyMessage('已移除自定义资质', 'success');
    }
}

function previewQualificationFile(key) {
    const fileInfo = qualificationFiles[key];
    if (!fileInfo) return;
    
    if (fileInfo.uploaded && currentCompanyId) {
        const url = `/api/companies/${currentCompanyId}/qualifications/${key}/download`;
        window.open(url, '_blank');
    } else if (fileInfo.file) {
        const url = URL.createObjectURL(fileInfo.file);
        const newWindow = window.open(url, '_blank');
        if (!newWindow) {
            showCompanyMessage('无法打开文件预览，请检查浏览器弹窗设置', 'error');
        }
    }
}

function removeQualificationFile(key) {
    const fileInfo = qualificationFiles[key];
    if (!fileInfo) return;
    
    if (fileInfo.uploaded && currentCompanyId) {
        if (!confirm('确定要删除服务器上的文件吗？')) return;
        
        fetch(`/api/companies/${currentCompanyId}/qualifications/${key}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                clearQualificationFileUI(key);
                delete qualificationFiles[key];
                showCompanyMessage('服务器文件已删除', 'success');
            } else {
                showCompanyMessage('删除服务器文件失败: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showCompanyMessage('删除服务器文件失败: ' + error.message, 'error');
        });
    } else {
        clearQualificationFileUI(key);
        delete qualificationFiles[key];
        showCompanyMessage('已移除选择的文件', 'success');
    }
}

function clearQualificationFileUI(key) {
    const fileInput = document.getElementById(`${key}File`);
    const statusElement = document.getElementById(`${key}Status`);
    const previewBtn = document.querySelector(`[onclick="previewQualificationFile('${key}')"]`);
    const deleteBtn = document.querySelector(`[onclick="removeQualificationFile('${key}')"]`);
    
    if (fileInput) fileInput.value = '';
    if (statusElement) {
        statusElement.textContent = '未选择文件';
        statusElement.className = 'text-muted';
    }
    if (previewBtn) previewBtn.disabled = true;
    if (deleteBtn) deleteBtn.disabled = true;
}

function saveAllQualifications() {
    // 检查是否有公司ID
    if (!currentCompanyId) {
        showCompanyGuideModal();
        return;
    }

    const fileCount = Object.keys(qualificationFiles).length;
    if (fileCount === 0) {
        showCompanyMessage('没有选择任何资质文件', 'error');
        return;
    }

    const btn = document.getElementById('saveAllQualificationsBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> 上传中...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('company_id', currentCompanyId);

    // 添加所有文件
    for (const [key, fileInfo] of Object.entries(qualificationFiles)) {
        if (fileInfo.file) {
            formData.append(`qualifications[${key}]`, fileInfo.file);
            
            // 如果是自定义资质，添加名称信息
            if (key.startsWith('custom_')) {
                const qualElement = document.querySelector(`[data-qual-key="${key}"]`);
                const qualName = qualElement.querySelector('h6').textContent.replace(/.*\s/, '');
                formData.append(`custom_names[${key}]`, qualName);
            }
        }
    }

    fetch(`/api/companies/${currentCompanyId}/qualifications`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新文件状态
            Object.keys(qualificationFiles).forEach(key => {
                if (qualificationFiles[key]) {
                    qualificationFiles[key].uploaded = true;
                }
            });
            
            // 重置资质文件状态为干净状态
            FormStateManager.setQualificationsDirty(false);
            FormStateManager.saveQualificationDataSnapshot();
            
            showCompanyMessage(`成功上传 ${Object.keys(qualificationFiles).length} 个资质文件`, 'success');
        } else {
            showCompanyMessage('上传失败: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showCompanyMessage('上传失败: ' + error.message, 'error');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function clearAllQualifications() {
    if (!confirm('确定要清空所有资质文件吗？')) return;
    clearAllQualificationsInternal();
    showCompanyMessage('已清空所有资质文件', 'success');
}

function clearAllQualificationsInternal() {
    // 清空所有文件选择
    Object.keys(qualificationFiles).forEach(key => {
        clearQualificationFileUI(key);
    });
    
    // 移除所有自定义资质项
    document.querySelectorAll('[data-qual-key^="custom_"]').forEach(element => {
        element.remove();
    });
    
    qualificationFiles = {};
    customQualificationCounter = 0;
}

function loadCompanyQualifications(companyId) {
    fetch(`/api/companies/${companyId}/qualifications`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.qualifications) {
                // 加载已上传的资质文件状态
                Object.entries(data.qualifications).forEach(([key, info]) => {
                    qualificationFiles[key] = {
                        name: info.original_filename,
                        uploaded: true,
                        uploadDate: info.upload_time
                    };
                    
                    const statusElement = document.getElementById(`${key}Status`);
                    const previewBtn = document.querySelector(`[onclick="previewQualificationFile('${key}')"]`);
                    const deleteBtn = document.querySelector(`[onclick="removeQualificationFile('${key}')"]`);
                    
                    if (statusElement) {
                        statusElement.textContent = `已上传: ${info.original_filename} (${new Date(info.upload_time).toLocaleString('zh-CN')})`;
                        statusElement.className = 'text-primary';
                    }
                    if (previewBtn) previewBtn.disabled = false;
                    if (deleteBtn) deleteBtn.disabled = false;
                });
            }
        })
        .catch(error => {
            console.warn('加载资质文件信息失败:', error);
        });
}

// 初始化表单变化监听
function initializeFormChangeListeners() {
    // 监听公司信息表单的变化
    if (companyInfoForm) {
        const formElements = companyInfoForm.querySelectorAll('input, textarea, select');
        formElements.forEach(element => {
            element.addEventListener('input', () => {
                FormStateManager.setCompanyInfoDirty(true);
            });
            element.addEventListener('change', () => {
                FormStateManager.setCompanyInfoDirty(true);
            });
        });
        
        // 保存初始状态快照
        FormStateManager.saveCompanyDataSnapshot();
    }

    // 监听资质文件选择的变化
    document.addEventListener('change', function(e) {
        if (e.target.type === 'file' && e.target.id && e.target.id.endsWith('File')) {
            FormStateManager.setQualificationsDirty(true);
        }
    });
}

// 初始化标签切换拦截机制
function initializeTabSwitchInterception() {
    // 获取所有标签页链接
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('show.bs.tab', function(e) {
            // 获取当前活跃标签和目标标签
            const activeTab = document.querySelector('.nav-link.active');
            const targetTab = e.target.getAttribute('href');
            
            if (!activeTab) return true;
            
            const activeHref = activeTab.getAttribute('href');
            let shouldPrevent = false;
            let message = '';

            // 检查是否有未保存的更改
            if (activeHref === '#companyInfo' && FormStateManager.state.companyInfoDirty) {
                if (FormStateManager.hasCompanyInfoChanged()) {
                    shouldPrevent = true;
                    message = '公司基本信息已修改但未保存，确定要离开吗？\n未保存的更改将丢失。';
                }
            } else if (activeHref === '#qualifications' && FormStateManager.state.qualificationsDirty) {
                if (FormStateManager.hasQualificationChanged()) {
                    shouldPrevent = true;
                    message = '资质文件已选择但未保存，确定要离开吗？\n未保存的更改将丢失。';
                }
            }

            // 如果有未保存更改，询问用户
            if (shouldPrevent) {
                e.preventDefault();
                if (confirm(message)) {
                    // 用户确认离开，重置脏状态并手动切换
                    if (activeHref === '#companyInfo') {
                        FormStateManager.setCompanyInfoDirty(false);
                    } else if (activeHref === '#qualifications') {
                        FormStateManager.setQualificationsDirty(false);
                    }
                    
                    // 手动触发标签切换
                    setTimeout(() => {
                        const tab = new bootstrap.Tab(tabLink);
                        tab.show();
                    }, 10);
                }
                return false;
            }
            
            return true;
        });
    });
}

// 显示公司信息引导模态框
function showCompanyGuideModal() {
    const modalHtml = `
        <div class="modal fade" id="companyGuideModal" tabindex="-1" aria-labelledby="companyGuideModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="companyGuideModalLabel">
                            <i class="bi bi-info-circle text-primary"></i> 操作提示
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <i class="bi bi-lightbulb"></i>
                            <strong>需要先设置公司信息</strong>
                        </div>
                        <p>资质文件需要关联到特定的公司，请先完成以下步骤：</p>
                        <ol class="mb-3">
                            <li>切换到"公司基本信息"标签页</li>
                            <li>填写并保存公司基本信息</li>
                            <li>然后返回此页面上传资质文件</li>
                        </ol>
                        <div class="d-flex justify-content-end gap-2">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="navigateToCompanyInfo()">
                                <i class="bi bi-arrow-right"></i> 前往填写公司信息
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('companyGuideModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加新的模态框
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('companyGuideModal'));
    modal.show();
    
    // 模态框关闭后移除DOM元素
    document.getElementById('companyGuideModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// 导航到公司信息标签页
function navigateToCompanyInfo() {
    // 关闭模态框
    const modal = bootstrap.Modal.getInstance(document.getElementById('companyGuideModal'));
    if (modal) {
        modal.hide();
    }
    
    // 切换到公司信息标签页
    const companyInfoTab = document.querySelector('a[href="#companyInfo"]');
    if (companyInfoTab) {
        const tab = new bootstrap.Tab(companyInfoTab);
        tab.show();
        
        // 聚焦到公司名称输入框
        setTimeout(() => {
            const companyNameInput = document.getElementById('companyName');
            if (companyNameInput) {
                companyNameInput.focus();
            }
        }, 200);
    }
}