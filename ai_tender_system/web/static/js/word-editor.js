/**
 * 通用Word编辑器组件
 * 支持文档读取和保存功能
 */
class WordEditor {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            height: 600,
            placeholder: '请输入内容或点击"读取文档"导入Word文档...',
            ...options
        };
        this.editor = null;
        this.isLoading = false;
        this.init();
    }
    
    /**
     * 初始化TinyMCE编辑器
     */
    init() {
        const self = this;
        
        // 检查TinyMCE是否已加载
        if (typeof tinymce === 'undefined') {
            console.error('TinyMCE未加载，等待重试...');
            setTimeout(() => this.init(), 500);
            return;
        }
        
        console.log('开始初始化TinyMCE编辑器:', this.containerId);
        
        tinymce.init({
            selector: `#${this.containerId}`,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
                'preview', 'anchor', 'searchreplace', 'code',
                'fullscreen', 'insertdatetime', 'media', 'table', 'help',
                'wordcount', 'paste', 'importcss', 'autosave'
            ],
            toolbar: [
                'undo redo | formatselect fontselect fontsizeselect',
                'bold italic underline strikethrough | alignleft aligncenter alignright alignjustify',
                'bullist numlist outdent indent | table link image',
                'forecolor backcolor | code fullscreen help'
            ],
            // language: 'zh_CN', // 移除语言配置，使用默认英文以避免加载错误
            height: this.options.height,
            menubar: 'file edit view insert format tools table help',
            content_style: `
                body {
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    margin: 20px;
                }
                p { margin: 0 0 10px 0; }
                table { border-collapse: collapse; width: 100%; }
                table td, table th { border: 1px solid #ccc; padding: 8px; }
            `,
            paste_data_images: true,
            paste_as_text: false,
            paste_word_valid_elements: 'b,strong,i,em,h1,h2,h3,h4,h5,h6,p,ol,ul,li,a[href],span,color,font-size,font-color,font-family,mark,table,tr,td,th',
            paste_retain_style_properties: 'color font-size font-family',
            placeholder: this.options.placeholder,
            // 禁用不可见字符显示
            show_invisible_characters: false,
            visualblocks_default_state: false,
            setup: function(editor) {
                self.editor = editor;
                
                editor.on('init', function() {
                    console.log('Word编辑器初始化完成');
                    self.onEditorReady();
                });
                
                editor.on('change', function() {
                    self.onContentChange();
                });
            },
            // 文件上传配置
            images_upload_handler: function (blobInfo, success, failure, progress) {
                // 这里可以实现图片上传功能
                const formData = new FormData();
                formData.append('image', blobInfo.blob(), blobInfo.filename());
                
                fetch('/api/editor/upload-image', {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                .then(result => {
                    if (result.success) {
                        success(result.location);
                    } else {
                        failure('图片上传失败: ' + result.error);
                    }
                }).catch(error => {
                    failure('图片上传失败: ' + error.message);
                });
            }
        }).catch(error => {
            console.error('TinyMCE初始化失败:', error);
        });
    }
    
    /**
     * 编辑器就绪回调
     */
    onEditorReady() {
        this.hideLoading();
    }
    
    /**
     * 内容变更回调
     */
    onContentChange() {
        // 可以在这里实现自动保存功能
    }
    
    /**
     * 读取Word文档
     */
    async loadDocument(file) {
        if (!file) {
            throw new Error('请选择文件');
        }
        
        // 检查文件类型 - 优先检查文件扩展名，因为某些浏览器可能不正确设置MIME类型
        const fileName = file.name.toLowerCase();
        const allowedExtensions = ['.docx', '.doc'];
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        const allowedTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const hasValidType = allowedTypes.includes(file.type);
        
        if (!hasValidExtension && !hasValidType) {
            throw new Error('只支持 .docx 和 .doc 格式的Word文档');
        }
        
        // 检查文件大小 (限制10MB)
        if (file.size > 10 * 1024 * 1024) {
            throw new Error('文件大小不能超过10MB');
        }
        
        this.showLoading('正在读取文档...');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/editor/load-document', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 设置编辑器内容
                this.editor.setContent(result.html_content);
                this.showMessage(`文档"${result.original_filename}"加载成功`, 'success');
                return result;
            } else {
                throw new Error(result.error || '文档加载失败');
            }
        } catch (error) {
            console.error('文档加载失败:', error);
            this.showMessage('文档加载失败: ' + error.message, 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * 保存为Word文档
     */
    async saveDocument(filename = '文档') {
        const content = this.editor.getContent();
        
        if (!content.trim()) {
            this.showMessage('文档内容为空，无法保存', 'warning');
            return;
        }
        
        // 清理文件名，移除特殊字符
        filename = filename.replace(/[^\w\u4e00-\u9fa5\-_\s]/g, '').trim() || '文档';
        
        this.showLoading('正在生成Word文档...');
        
        try {
            const response = await fetch('/api/editor/save-document', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    html_content: content,
                    filename: filename
                })
            });
            
            if (response.ok) {
                // 获取文件blob
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                
                // 创建下载链接
                const a = document.createElement('a');
                a.href = url;
                a.download = `${filename}.docx`;
                a.style.display = 'none';
                
                // 触发下载
                document.body.appendChild(a);
                a.click();
                
                // 清理
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showMessage('文档保存成功', 'success');
            } else {
                const result = await response.json();
                throw new Error(result.error || '文档保存失败');
            }
        } catch (error) {
            console.error('文档保存失败:', error);
            this.showMessage('文档保存失败: ' + error.message, 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * 获取编辑器内容
     */
    getContent() {
        return this.editor ? this.editor.getContent() : '';
    }
    
    /**
     * 设置编辑器内容
     */
    setContent(content) {
        if (this.editor) {
            this.editor.setContent(content);
        }
    }
    
    /**
     * 清空编辑器内容
     */
    clearContent() {
        if (this.editor) {
            this.editor.setContent('');
        }
    }
    
    /**
     * 显示加载状态
     */
    showLoading(message = '加载中...') {
        this.isLoading = true;
        // 创建遮罩层
        const overlay = document.createElement('div');
        overlay.id = 'editor-loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
                <div class="loading-text mt-2">${message}</div>
            </div>
        `;
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
        `;
        document.body.appendChild(overlay);
    }
    
    /**
     * 隐藏加载状态
     */
    hideLoading() {
        this.isLoading = false;
        const overlay = document.getElementById('editor-loading-overlay');
        if (overlay) {
            document.body.removeChild(overlay);
        }
    }
    
    /**
     * 显示消息提示
     */
    showMessage(message, type = 'info') {
        // 创建消息提示
        const alert = document.createElement('div');
        alert.className = `alert alert-${this.getBootstrapAlertType(type)} alert-dismissible fade show`;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9998;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // 自动移除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
    
    /**
     * 转换消息类型为Bootstrap样式
     */
    getBootstrapAlertType(type) {
        const typeMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return typeMap[type] || 'info';
    }
    
    /**
     * 销毁编辑器
     */
    destroy() {
        if (this.editor) {
            tinymce.get(this.containerId).destroy();
            this.editor = null;
        }
        this.hideLoading();
    }
}

// CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .loading-content {
        text-align: center;
    }
    
    .loading-text {
        font-size: 16px;
        font-weight: 500;
    }
`;
document.head.appendChild(style);