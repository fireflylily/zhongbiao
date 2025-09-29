/**
 * 页面工具模块 - 通用功能和工具函数
 * 包含错误处理、文件管理、API测试等通用功能
 */

class PageUtilities {
    constructor() {
        this.init();
    }

    /**
     * 初始化工具模块
     */
    init() {
        this.setupGlobalErrorHandler();
        this.bindUtilityEvents();
    }

    /**
     * 设置全局错误处理
     */
    setupGlobalErrorHandler() {
        // 全局错误处理 - 捕获所有TypeError并给出友好提示
        window.addEventListener('error', function(e) {
            if (e.error && e.error.message && e.error.message.includes("Cannot read properties of null")) {
                console.warn('捕获到null元素错误，但已处理:', e.error.message);
                e.preventDefault(); // 阻止错误显示在控制台
                return true;
            }
        });

        // Promise 拒绝处理
        window.addEventListener('unhandledrejection', function(e) {
            console.error('未处理的Promise拒绝:', e.reason);
            // 可以选择是否阻止显示在控制台
            // e.preventDefault();
        });
    }

    /**
     * 绑定工具事件
     */
    bindUtilityEvents() {
        // API测试按钮
        this.bindApiTestButton();

        // 查看文件列表按钮
        this.bindViewFilesButton();

        // 安全事件绑定
        this.bindSafeEvents();
    }

    /**
     * 绑定API测试按钮
     */
    bindApiTestButton() {
        const testApiBtn = document.getElementById('testApiBtn');
        if (testApiBtn) {
            testApiBtn.addEventListener('click', async () => {
                await this.testAPI();
            });
        }
    }

    /**
     * 绑定查看文件列表按钮
     */
    bindViewFilesButton() {
        const viewFilesBtn = document.getElementById('viewFilesBtn');
        if (viewFilesBtn) {
            viewFilesBtn.addEventListener('click', async () => {
                await this.viewFilesList();
            });
        }
    }

    /**
     * 安全的事件绑定函数，避免null元素错误
     */
    safeAddEventListener(elementId, eventType, handler) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener(eventType, handler);
            return true;
        } else {
            console.log(`元素 ${elementId} 不存在，跳过 ${eventType} 事件绑定`);
            return false;
        }
    }

    /**
     * 绑定安全事件
     */
    bindSafeEvents() {
        // 这里可以添加更多需要安全绑定的事件
        // 示例：
        // this.safeAddEventListener('someButton', 'click', () => {
        //     console.log('安全事件处理');
        // });
    }

    /**
     * API测试功能
     */
    async testAPI() {
        const apiKey = window.apiKeyManager?.getCurrentApiKey() || '';
        const btn = document.getElementById('testApiBtn');
        const statusDiv = document.getElementById('apiStatus');

        if (!btn || !statusDiv) return;

        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> 测试中...';
        btn.disabled = true;

        try {
            const response = await window.apiClient?.post('/api/test', { api_key: apiKey });

            statusDiv.style.display = 'block';
            if (response.success) {
                statusDiv.className = 'api-status success';
                statusDiv.innerHTML = `<i class="bi bi-check-circle"></i> ${response.message} ${response.model ? `(模型: ${response.model})` : ''}`;
                window.notifications?.success('API测试成功');
            } else {
                statusDiv.className = 'api-status error';
                statusDiv.innerHTML = `<i class="bi bi-x-circle"></i> ${response.message || 'API测试失败'}`;
                window.notifications?.error('API测试失败');
            }
        } catch (error) {
            console.error('API测试失败:', error);
            statusDiv.style.display = 'block';
            statusDiv.className = 'api-status error';
            statusDiv.innerHTML = `<i class="bi bi-x-circle"></i> 连接失败: ${error.message}`;
            window.notifications?.error('API连接失败');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }

    /**
     * 查看文件列表
     */
    async viewFilesList() {
        try {
            const data = await window.apiClient?.get('/api/files');

            if (data.files && data.files.length > 0) {
                let fileList = '可下载的文件：\n\n';
                data.files.forEach((file, index) => {
                    const size = (file.size / 1024 / 1024).toFixed(2);
                    const date = new Date(file.created).toLocaleString('zh-CN');
                    fileList += `${index + 1}. ${file.name}\n   大小: ${size} MB\n   创建时间: ${date}\n\n`;
                });

                // 使用模态框显示文件列表
                if (window.modalManager) {
                    window.modalManager.alert(fileList, '文件列表', {
                        size: 'lg'
                    });
                } else {
                    alert(fileList);
                }
            } else {
                window.notifications?.info('暂无可下载的文件');
            }
        } catch (error) {
            console.error('获取文件列表失败:', error);
            window.notifications?.error('获取文件列表失败: ' + error.message);
        }
    }

    /**
     * 显示通知（兼容旧版本）
     */
    showNotification(message, type = 'info') {
        if (window.notifications) {
            // 使用新的通知系统
            switch (type) {
                case 'success':
                    window.notifications.success(message);
                    break;
                case 'error':
                case 'danger':
                    window.notifications.error(message);
                    break;
                case 'warning':
                    window.notifications.warning(message);
                    break;
                default:
                    window.notifications.info(message);
            }
        } else {
            // 回退到传统Bootstrap通知
            this.showBootstrapNotification(message, type);
        }
    }

    /**
     * Bootstrap通知（回退方案）
     */
    showBootstrapNotification(message, type = 'info') {
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
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 格式化日期时间
     */
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 节流函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * 复制文本到剪贴板
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('已复制到剪贴板', 'success');
            return true;
        } catch (error) {
            console.error('复制失败:', error);
            // 回退方案
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showNotification('已复制到剪贴板', 'success');
                return true;
            } catch (fallbackError) {
                this.showNotification('复制失败', 'error');
                return false;
            } finally {
                document.body.removeChild(textArea);
            }
        }
    }

    /**
     * 检查浏览器兼容性
     */
    checkBrowserCompatibility() {
        const features = {
            fetch: typeof fetch !== 'undefined',
            asyncAwait: (async () => {})() instanceof Promise,
            localStorage: typeof localStorage !== 'undefined',
            fileAPI: typeof File !== 'undefined',
            formData: typeof FormData !== 'undefined'
        };

        const unsupported = Object.keys(features).filter(key => !features[key]);

        if (unsupported.length > 0) {
            console.warn('不支持的浏览器功能:', unsupported);
            this.showNotification(
                '您的浏览器版本过低，部分功能可能无法正常使用。建议升级到最新版本。',
                'warning'
            );
            return false;
        }

        return true;
    }

    /**
     * 获取设备信息
     */
    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenResolution: `${screen.width}x${screen.height}`,
            viewportSize: `${window.innerWidth}x${window.innerHeight}`,
            colorDepth: screen.colorDepth,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
        };
    }

    /**
     * 性能监控
     */
    performanceMonitor() {
        if (performance && performance.timing) {
            const timing = performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            const domReady = timing.domContentLoadedEventEnd - timing.navigationStart;

            console.log('页面性能:', {
                '总加载时间': loadTime + 'ms',
                'DOM就绪时间': domReady + 'ms',
                'DNS查询时间': (timing.domainLookupEnd - timing.domainLookupStart) + 'ms',
                'TCP连接时间': (timing.connectEnd - timing.connectStart) + 'ms',
                '服务器响应时间': (timing.responseEnd - timing.requestStart) + 'ms'
            });
        }
    }

    /**
     * 导出工具函数到全局（向后兼容）
     */
    exportGlobalFunctions() {
        // 导出常用函数到全局作用域，保持向后兼容
        window.showNotification = (message, type) => this.showNotification(message, type);
        window.safeAddEventListener = (elementId, eventType, handler) =>
            this.safeAddEventListener(elementId, eventType, handler);
        window.formatFileSize = (bytes) => this.formatFileSize(bytes);
        window.formatDateTime = (dateString) => this.formatDateTime(dateString);
        window.copyToClipboard = (text) => this.copyToClipboard(text);
    }
}

// 创建全局页面工具实例
window.pageUtilities = new PageUtilities();

// 导出全局函数
window.pageUtilities.exportGlobalFunctions();

// 页面加载完成后进行性能监控和兼容性检查
document.addEventListener('DOMContentLoaded', () => {
    window.pageUtilities.checkBrowserCompatibility();

    // 延迟进行性能监控
    setTimeout(() => {
        window.pageUtilities.performanceMonitor();
    }, 1000);
});

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PageUtilities;
}