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
    'taxpayer_qualification': '纳税人资格证明',
    'performance_certificate': '业绩证明',
    'authorization_letter': '授权书',
    'credit_report': '信用报告',
    'audit_report': '审计报告',
    'social_security_proof': '社保证明',
    'labor_contract': '劳动合同'
};

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
        option.textContent = company.name;
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

function createQualificationItem(key, name, container, isCustom = false) {
    const qualItem = document.createElement('div');
    qualItem.className = 'mb-3';
    qualItem.setAttribute('data-qual-key', key);
    
    qualItem.innerHTML = `
        <div class="card border-secondary">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-3">
                        <h6 class="mb-0">${isCustom ? '📄' : '📋'} ${name}</h6>
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
    if (!currentCompanyId) {
        showCompanyMessage('请先保存公司基本信息', 'error');
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
                        name: info.filename,
                        uploaded: true,
                        uploadDate: info.upload_date
                    };
                    
                    const statusElement = document.getElementById(`${key}Status`);
                    const previewBtn = document.querySelector(`[onclick="previewQualificationFile('${key}')"]`);
                    const deleteBtn = document.querySelector(`[onclick="removeQualificationFile('${key}')"]`);
                    
                    if (statusElement) {
                        statusElement.textContent = `已上传: ${info.filename} (${info.upload_date})`;
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