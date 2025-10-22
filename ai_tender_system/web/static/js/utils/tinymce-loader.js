/**
 * TinyMCE 懒加载器
 * 按需加载 TinyMCE，避免初始加载阻塞
 *
 * 使用方法:
 * await TinyMCELoader.init('#myTextarea', { plugins: 'lists' });
 */

const TinyMCELoader = {
    loaded: false,
    loading: false,
    pendingPromises: [],

    /**
     * 加载 TinyMCE 脚本
     * @returns {Promise<void>}
     */
    async load() {
        // 如果已加载，直接返回
        if (this.loaded) {
            return Promise.resolve();
        }

        // 如果正在加载，等待加载完成
        if (this.loading) {
            return new Promise((resolve) => {
                this.pendingPromises.push(resolve);
            });
        }

        this.loading = true;
        console.log('[TinyMCELoader] 开始加载 TinyMCE...');

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js';
            script.referrerpolicy = 'origin';

            script.onload = () => {
                this.loaded = true;
                this.loading = false;
                console.log('[TinyMCELoader] ✅ TinyMCE 加载完成');

                // 解决所有等待的 Promise
                this.pendingPromises.forEach(r => r());
                this.pendingPromises = [];

                resolve();
            };

            script.onerror = (error) => {
                this.loading = false;
                console.error('[TinyMCELoader] ❌ TinyMCE 加载失败:', error);
                reject(new Error('TinyMCE 加载失败'));
            };

            document.head.appendChild(script);
        });
    },

    /**
     * 初始化 TinyMCE 编辑器
     * @param {string} selector - CSS选择器
     * @param {object} config - TinyMCE配置对象
     * @returns {Promise<object>} TinyMCE实例
     */
    async init(selector, config = {}) {
        try {
            // 先加载 TinyMCE
            await this.load();

            // 如果 tinymce 未定义，说明加载失败
            if (typeof tinymce === 'undefined') {
                throw new Error('TinyMCE 加载失败，全局对象未找到');
            }

            // 默认配置
            const defaultConfig = {
                selector: selector,
                height: 500,
                menubar: false,
                plugins: [
                    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
                    'preview', 'anchor', 'searchreplace', 'visualblocks', 'code',
                    'fullscreen', 'insertdatetime', 'media', 'table', 'help', 'wordcount'
                ],
                toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | bullist numlist | removeformat | help',
                language: 'zh_CN',
                content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
            };

            // 合并配置
            const finalConfig = { ...defaultConfig, ...config };

            console.log('[TinyMCELoader] 初始化编辑器:', selector);

            // 初始化 TinyMCE
            const editors = await tinymce.init(finalConfig);

            console.log('[TinyMCELoader] ✅ 编辑器初始化完成');
            return editors;

        } catch (error) {
            console.error('[TinyMCELoader] 编辑器初始化失败:', error);
            throw error;
        }
    },

    /**
     * 移除编辑器
     * @param {string} selector - CSS选择器
     */
    remove(selector) {
        if (typeof tinymce !== 'undefined') {
            const editor = tinymce.get(selector.replace('#', ''));
            if (editor) {
                editor.remove();
                console.log('[TinyMCELoader] 编辑器已移除:', selector);
            }
        }
    },

    /**
     * 获取编辑器实例
     * @param {string} id - 编辑器ID（不含#）
     * @returns {object|null}
     */
    getEditor(id) {
        if (typeof tinymce !== 'undefined') {
            return tinymce.get(id);
        }
        return null;
    }
};

// 暴露到全局
window.TinyMCELoader = TinyMCELoader;
