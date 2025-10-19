/**
 * CSRF Protection Utility
 * 为所有 AJAX 请求自动添加 CSRF Token
 *
 * 使用方法：
 * 1. 在HTML中引入此文件：<script src="/static/js/csrf-protection.js"></script>
 * 2. 确保HTML <head> 中有：<meta name="csrf-token" content="{{ csrf_token() }}">
 * 3. 使用 csrfFetch() 替代 fetch()，或者直接使用 fetch()（已自动包装）
 */

(function() {
    'use strict';

    /**
     * 从 meta 标签获取 CSRF Token
     */
    function getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : null;
    }

    /**
     * 保存原生 fetch 引用
     */
    const originalFetch = window.fetch;

    /**
     * 带 CSRF 保护的 fetch 包装器
     * @param {string} url - 请求URL
     * @param {object} options - fetch选项
     * @returns {Promise} fetch Promise
     */
    window.csrfFetch = function(url, options = {}) {
        // 默认选项
        options = options || {};
        options.headers = options.headers || {};
        options.credentials = options.credentials || 'same-origin';

        // 对于 POST, PUT, DELETE 请求，添加 CSRF token
        const method = (options.method || 'GET').toUpperCase();
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
            const token = getCSRFToken();
            if (token) {
                // 支持多种 header 格式
                options.headers['X-CSRFToken'] = token;
                options.headers['X-CSRF-Token'] = token;
            } else {
                console.warn('CSRF token not found in page meta tags');
            }
        }

        // 使用原生 fetch，避免递归
        return originalFetch(url, options);
    };

    /**
     * 包装原生 fetch，自动添加 CSRF token
     */
    window.fetch = function(url, options = {}) {
        return window.csrfFetch(url, options);
    };

    /**
     * jQuery AJAX 支持（如果存在）
     */
    if (window.jQuery) {
        jQuery.ajaxSetup({
            beforeSend: function(xhr, settings) {
                // 对于跨域请求，不添加 CSRF token
                if (!this.crossDomain && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(settings.type.toUpperCase())) {
                    const token = getCSRFToken();
                    if (token) {
                        xhr.setRequestHeader('X-CSRFToken', token);
                        xhr.setRequestHeader('X-CSRF-Token', token);
                    }
                }
            }
        });
    }

    /**
     * 为 FormData 添加 CSRF token
     * @param {FormData} formData - 表单数据
     * @returns {FormData} 添加了token的表单数据
     */
    window.addCSRFToFormData = function(formData) {
        const token = getCSRFToken();
        if (token) {
            formData.append('csrf_token', token);
        }
        return formData;
    };

    /**
     * 刷新 CSRF Token（用于长时间运行的页面）
     */
    window.refreshCSRFToken = async function() {
        try {
            const response = await originalFetch('/api/csrf-token', {
                credentials: 'same-origin'
            });
            const data = await response.json();
            if (data.csrf_token) {
                const meta = document.querySelector('meta[name="csrf-token"]');
                if (meta) {
                    meta.setAttribute('content', data.csrf_token);
                    console.log('CSRF token refreshed successfully');
                    return data.csrf_token;
                }
            }
        } catch (error) {
            console.error('Failed to refresh CSRF token:', error);
        }
        return null;
    };

    // 页面加载完成后验证 token 是否存在
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            const token = getCSRFToken();
            if (!token) {
                console.warn('CSRF Protection: Token not found. Please add <meta name="csrf-token"> to your HTML.');
            } else {
                console.log('CSRF Protection: Enabled ✓');
            }
        });
    } else {
        const token = getCSRFToken();
        if (!token) {
            console.warn('CSRF Protection: Token not found. Please add <meta name="csrf-token"> to your HTML.');
        } else {
            console.log('CSRF Protection: Enabled ✓');
        }
    }

    /**
     * 处理 CSRF 错误的辅助函数
     */
    window.handleCSRFError = async function(response) {
        if (response.status === 400 && response.headers.get('content-type')?.includes('application/json')) {
            try {
                const data = await response.json();
                if (data.error && data.error.includes('CSRF')) {
                    // CSRF token 过期或无效，尝试刷新
                    console.log('CSRF token invalid, refreshing...');
                    await window.refreshCSRFToken();
                    return true; // 表示需要重试请求
                }
            } catch (e) {
                // 忽略解析错误
            }
        }
        return false;
    };

})();
