/**
 * AI标书系统公共JavaScript函数库
 */

/**
 * API密钥加密解密功能
 */
function encryptApiKey(key) {
    if (!key) return '';
    const encoded = btoa(unescape(encodeURIComponent(key)));
    return encoded.split('').reverse().join('');
}

function decryptApiKey(encrypted) {
    if (!encrypted) return '';
    try {
        const reversed = encrypted.split('').reverse().join('');
        return decodeURIComponent(escape(atob(reversed)));
    } catch (e) {
        console.error('解密失败:', e);
        return '';
    }
}

/**
 * 通知显示功能
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

/**
 * 文件下载功能
 */
function downloadFile(url, filename) {
    try {
        showNotification('开始下载...', 'info');
        
        // 创建隐藏的下载链接
        const link = document.createElement('a');
        link.href = url;
        link.download = filename || '';
        link.style.display = 'none';
        
        // 添加到DOM并触发下载
        document.body.appendChild(link);
        link.click();
        
        // 清理
        setTimeout(() => {
            if (link.parentNode) {
                link.remove();
            }
        }, 100);
        
        showNotification('下载已开始', 'success');
    } catch (error) {
        console.error('下载失败:', error);
        showNotification('下载失败: ' + error.message, 'error');
    }
}

/**
 * 拖拽文件处理功能
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function setupDragDrop(uploadAreaId, fileInputId, onFileSelected) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);
    
    if (!uploadArea || !fileInput) return;

    // 拖拽事件
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
    });

    uploadArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            if (onFileSelected) {
                onFileSelected(files[0]);
            }
        }
    }, false);

    // 点击选择文件
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0 && onFileSelected) {
            onFileSelected(e.target.files[0]);
        }
    });
}

/**
 * 文件信息显示
 */
function displayFileInfo(file, fileInfoElement) {
    if (!file || !fileInfoElement) return;
    
    const fileName = fileInfoElement.querySelector('.file-name') || fileInfoElement;
    const fileSize = fileInfoElement.querySelector('.file-size');
    
    fileName.textContent = file.name;
    if (fileSize) {
        fileSize.textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';
    }
    
    fileInfoElement.style.display = 'block';
}

/**
 * 进度条管理
 */
function updateProgressBar(progressBar, percent, text = '') {
    if (!progressBar) return;
    
    const progressElement = progressBar.querySelector('.progress-bar') || progressBar;
    progressElement.style.width = percent + '%';
    progressElement.setAttribute('aria-valuenow', percent);
    
    if (text) {
        progressElement.textContent = text;
    }
    
    progressBar.style.display = percent > 0 ? 'block' : 'none';
}

/**
 * API请求辅助函数
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('API请求失败:', error);
        return { success: false, error: error.message };
    }
}

/**
 * 表单数据收集
 */
function collectFormData(formElement) {
    const formData = new FormData(formElement);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            // 如果键已存在，转换为数组
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

/**
 * 页面加载完成时初始化
 */
function onPageReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

/**
 * 启用粘贴上传图片功能
 * @param {HTMLElement} targetElement - 目标元素，用于接收粘贴事件
 * @param {Function} onImagePasted - 图片粘贴后的回调函数
 */
function enablePasteImageUpload(targetElement, onImagePasted) {
    if (!targetElement) return;
    
    // 添加粘贴事件监听
    targetElement.addEventListener('paste', function(e) {
        e.preventDefault();
        
        const items = e.clipboardData?.items;
        if (!items) return;
        
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            
            // 检查是否为图片
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                if (file) {
                    // 创建一个新的文件对象，设置文件名
                    const timestamp = new Date().getTime();
                    const fileName = `pasted_image_${timestamp}.${file.type.split('/')[1] || 'png'}`;
                    const newFile = new File([file], fileName, { type: file.type });
                    
                    // 调用回调函数处理图片
                    if (typeof onImagePasted === 'function') {
                        onImagePasted(newFile);
                    }
                    
                    showNotification('已粘贴图片：' + fileName, 'success');
                }
                break;
            }
        }
    });
    
    // 添加拖放支持
    targetElement.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        targetElement.classList.add('drag-over');
    });
    
    targetElement.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        targetElement.classList.remove('drag-over');
    });
    
    targetElement.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        targetElement.classList.remove('drag-over');
        
        const files = e.dataTransfer?.files;
        if (files && files.length > 0) {
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (file.type.startsWith('image/')) {
                    if (typeof onImagePasted === 'function') {
                        onImagePasted(file);
                    }
                    showNotification('已上传图片：' + file.name, 'success');
                    break;
                }
            }
        }
    });
    
    // 添加提示信息
    const hint = document.createElement('small');
    hint.className = 'text-muted d-block mt-1';
    hint.innerHTML = '<i class="bi bi-info-circle"></i> 支持 Ctrl+V 粘贴图片或拖放图片文件';
    targetElement.appendChild(hint);
}

/**
 * 格式化时间
 */
function formatDateTime(date = new Date()) {
    return date.getFullYear() + 
           ('0' + (date.getMonth() + 1)).slice(-2) + 
           ('0' + date.getDate()).slice(-2) + '_' +
           ('0' + date.getHours()).slice(-2) + 
           ('0' + date.getMinutes()).slice(-2) + 
           ('0' + date.getSeconds()).slice(-2);
}