/**
 * CSS动态加载工具
 * 用于按需加载CSS文件,优化首屏加载性能
 *
 * @module CSSLoader
 */

const CSSLoader = {
    // 已加载的CSS文件缓存
    loadedCSS: new Set(),

    // 正在加载的CSS文件Promise缓存
    loadingCSS: new Map(),

    /**
     * 动态加载CSS文件
     * @param {string} href - CSS文件路径
     * @param {Object} options - 加载选项
     * @param {string} options.id - link标签的id
     * @param {string} options.media - media属性,默认'all'
     * @returns {Promise} 加载完成的Promise
     */
    load(href, options = {}) {
        // 如果已经加载过,直接返回成功的Promise
        if (this.loadedCSS.has(href)) {
            console.log(`[CSSLoader] CSS已加载,跳过: ${href}`);
            return Promise.resolve();
        }

        // 如果正在加载,返回缓存的Promise
        if (this.loadingCSS.has(href)) {
            console.log(`[CSSLoader] CSS正在加载,等待: ${href}`);
            return this.loadingCSS.get(href);
        }

        console.log(`[CSSLoader] 开始加载CSS: ${href}`);

        // 创建加载Promise
        const loadPromise = new Promise((resolve, reject) => {
            // 检查是否已存在相同的link标签
            const existingLink = document.querySelector(`link[href="${href}"]`);
            if (existingLink) {
                this.loadedCSS.add(href);
                resolve();
                return;
            }

            // 创建link标签
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = options.media || 'all';

            if (options.id) {
                link.id = options.id;
            }

            // 加载完成事件
            link.onload = () => {
                console.log(`[CSSLoader] CSS加载成功: ${href}`);
                this.loadedCSS.add(href);
                this.loadingCSS.delete(href);
                resolve();
            };

            // 加载失败事件
            link.onerror = () => {
                console.error(`[CSSLoader] CSS加载失败: ${href}`);
                this.loadingCSS.delete(href);
                // 移除失败的link标签
                if (link.parentNode) {
                    link.parentNode.removeChild(link);
                }
                reject(new Error(`Failed to load CSS: ${href}`));
            };

            // 添加到head
            document.head.appendChild(link);
        });

        // 缓存Promise
        this.loadingCSS.set(href, loadPromise);

        return loadPromise;
    },

    /**
     * 批量加载多个CSS文件
     * @param {Array<string|Object>} cssFiles - CSS文件路径数组或配置对象数组
     * @returns {Promise} 所有CSS加载完成的Promise
     */
    loadMultiple(cssFiles) {
        const loadPromises = cssFiles.map(file => {
            if (typeof file === 'string') {
                return this.load(file);
            } else {
                return this.load(file.href, file.options);
            }
        });

        return Promise.all(loadPromises);
    },

    /**
     * 预加载CSS文件(不阻塞渲染)
     * @param {string} href - CSS文件路径
     */
    preload(href) {
        if (this.loadedCSS.has(href) || this.loadingCSS.has(href)) {
            return;
        }

        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = href;

        // 当预加载完成后,转换为stylesheet
        link.onload = () => {
            link.rel = 'stylesheet';
            this.loadedCSS.add(href);
        };

        document.head.appendChild(link);
    },

    /**
     * 卸载CSS文件
     * @param {string} href - CSS文件路径
     */
    unload(href) {
        const link = document.querySelector(`link[href="${href}"]`);
        if (link && link.parentNode) {
            link.parentNode.removeChild(link);
            this.loadedCSS.delete(href);
            console.log(`[CSSLoader] CSS已卸载: ${href}`);
        }
    },

    /**
     * 检查CSS是否已加载
     * @param {string} href - CSS文件路径
     * @returns {boolean}
     */
    isLoaded(href) {
        return this.loadedCSS.has(href);
    },

    /**
     * 清除所有缓存
     */
    clearCache() {
        this.loadedCSS.clear();
        this.loadingCSS.clear();
        console.log('[CSSLoader] 缓存已清除');
    }
};

// 定义各个页面/tab需要的CSS文件 (使用压缩版本)
const CSS_DEPENDENCIES = {
    // 投标管理tab
    'tender-management': [
        '/static/css/tender-processing-hitl.min.css',
        '/static/css/tender-processing-step3-enhanced.min.css'
    ],

    // 案例库tab
    'knowledge-case-library': [
        '/static/css/components/case-library.min.css'
    ],

    // 简历库tab
    'knowledge-resume-library': [
        '/static/css/components/resume-library.min.css'
    ],

    // 企业信息库tab
    'knowledge-company-library': [
        '/static/css/components/qualifications.min.css'
    ]
};

/**
 * 为指定tab加载所需的CSS
 * @param {string} tabId - tab的ID
 * @returns {Promise}
 */
function loadCSSForTab(tabId) {
    const cssFiles = CSS_DEPENDENCIES[tabId];

    if (!cssFiles || cssFiles.length === 0) {
        return Promise.resolve();
    }

    console.log(`[CSSLoader] 为tab "${tabId}" 加载CSS:`, cssFiles);
    return CSSLoader.loadMultiple(cssFiles);
}

// 导出到全局
window.CSSLoader = CSSLoader;
window.loadCSSForTab = loadCSSForTab;

console.log('[CSSLoader] CSS动态加载工具已初始化');
