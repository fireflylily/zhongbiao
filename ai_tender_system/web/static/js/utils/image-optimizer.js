/**
 * 图片优化工具
 * 提供图片懒加载、WebP转换、响应式加载等优化功能
 *
 * 使用方法:
 * ImageOptimizer.lazyLoad('.lazy-image');
 * ImageOptimizer.convertToWebP(imageFile, quality);
 */

const ImageOptimizer = {
    /**
     * 懒加载图片
     * @param {string} selector - 图片选择器
     * @param {object} options - 配置选项
     */
    lazyLoad(selector = '.lazy', options = {}) {
        const defaultOptions = {
            root: null,
            rootMargin: '50px',
            threshold: 0.01
        };

        const config = { ...defaultOptions, ...options };

        // 检查浏览器是否支持 IntersectionObserver
        if (!('IntersectionObserver' in window)) {
            console.warn('[ImageOptimizer] IntersectionObserver 不支持，直接加载所有图片');
            this.loadAllImages(selector);
            return;
        }

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    this.loadImage(img);
                    observer.unobserve(img);
                }
            });
        }, config);

        const images = document.querySelectorAll(selector);
        images.forEach(img => {
            imageObserver.observe(img);
        });

        console.log(`[ImageOptimizer] 已启用懒加载，监控 ${images.length} 张图片`);
    },

    /**
     * 加载单张图片
     * @param {HTMLImageElement} img - 图片元素
     */
    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;

        if (!src && !srcset) {
            return;
        }

        // 创建临时图片对象预加载
        const tempImg = new Image();

        tempImg.onload = () => {
            if (srcset) {
                img.srcset = srcset;
            }
            if (src) {
                img.src = src;
            }
            img.classList.add('loaded');
            console.log('[ImageOptimizer] 图片已加载:', src || srcset);
        };

        tempImg.onerror = () => {
            console.error('[ImageOptimizer] 图片加载失败:', src || srcset);
            img.classList.add('error');
        };

        // 开始加载
        if (src) {
            tempImg.src = src;
        }
    },

    /**
     * 直接加载所有图片（不支持懒加载时）
     * @param {string} selector - 图片选择器
     */
    loadAllImages(selector) {
        const images = document.querySelectorAll(selector);
        images.forEach(img => {
            this.loadImage(img);
        });
    },

    /**
     * 将图片转换为WebP格式
     * @param {File|Blob} imageFile - 图片文件
     * @param {number} quality - 质量 (0-1)
     * @returns {Promise<Blob>} WebP格式的图片
     */
    async convertToWebP(imageFile, quality = 0.8) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                const img = new Image();

                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;

                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);

                    canvas.toBlob(
                        (blob) => {
                            if (blob) {
                                console.log('[ImageOptimizer] WebP转换成功，原始大小:', imageFile.size, '转换后:', blob.size);
                                resolve(blob);
                            } else {
                                reject(new Error('WebP转换失败'));
                            }
                        },
                        'image/webp',
                        quality
                    );
                };

                img.onerror = () => {
                    reject(new Error('图片加载失败'));
                };

                img.src = e.target.result;
            };

            reader.onerror = () => {
                reject(new Error('文件读取失败'));
            };

            reader.readAsDataURL(imageFile);
        });
    },

    /**
     * 压缩图片
     * @param {File|Blob} imageFile - 图片文件
     * @param {object} options - 压缩选项
     * @returns {Promise<Blob>}
     */
    async compress(imageFile, options = {}) {
        const defaultOptions = {
            maxWidth: 1920,
            maxHeight: 1080,
            quality: 0.8,
            format: 'image/jpeg'
        };

        const config = { ...defaultOptions, ...options };

        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                const img = new Image();

                img.onload = () => {
                    let width = img.width;
                    let height = img.height;

                    // 计算缩放比例
                    if (width > config.maxWidth || height > config.maxHeight) {
                        const ratio = Math.min(
                            config.maxWidth / width,
                            config.maxHeight / height
                        );
                        width = Math.floor(width * ratio);
                        height = Math.floor(height * ratio);
                    }

                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;

                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);

                    canvas.toBlob(
                        (blob) => {
                            if (blob) {
                                console.log('[ImageOptimizer] 压缩成功，原始大小:', imageFile.size, '压缩后:', blob.size);
                                resolve(blob);
                            } else {
                                reject(new Error('图片压缩失败'));
                            }
                        },
                        config.format,
                        config.quality
                    );
                };

                img.onerror = () => {
                    reject(new Error('图片加载失败'));
                };

                img.src = e.target.result;
            };

            reader.onerror = () => {
                reject(new Error('文件读取失败'));
            };

            reader.readAsDataURL(imageFile);
        });
    },

    /**
     * 获取图片尺寸
     * @param {File|Blob} imageFile - 图片文件
     * @returns {Promise<object>} {width, height}
     */
    async getImageDimensions(imageFile) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                const img = new Image();

                img.onload = () => {
                    resolve({
                        width: img.width,
                        height: img.height
                    });
                };

                img.onerror = () => {
                    reject(new Error('图片加载失败'));
                };

                img.src = e.target.result;
            };

            reader.onerror = () => {
                reject(new Error('文件读取失败'));
            };

            reader.readAsDataURL(imageFile);
        });
    },

    /**
     * 检查浏览器是否支持WebP
     * @returns {Promise<boolean>}
     */
    async supportsWebP() {
        if (!self.createImageBitmap) return false;

        const webpData = 'data:image/webp;base64,UklGRh4AAABXRUJQVlA4TBEAAAAvAAAAAAfQ//73v/+BiOh/AAA=';
        const blob = await fetch(webpData).then(r => r.blob());

        return createImageBitmap(blob).then(() => true, () => false);
    },

    /**
     * 生成响应式图片srcset
     * @param {string} imageUrl - 图片URL
     * @param {array} sizes - 尺寸数组 [640, 1024, 1920]
     * @returns {string} srcset字符串
     */
    generateSrcset(imageUrl, sizes = [640, 1024, 1920]) {
        const baseUrl = imageUrl.replace(/\.[^.]+$/, '');
        const extension = imageUrl.match(/\.[^.]+$/)[0];

        return sizes.map(size => {
            return `${baseUrl}-${size}w${extension} ${size}w`;
        }).join(', ');
    },

    /**
     * 应用图片优化到表单
     * @param {string} formId - 表单ID
     * @param {object} options - 优化选项
     */
    optimizeFormImages(formId, options = {}) {
        const form = document.getElementById(formId);
        if (!form) {
            console.error('[ImageOptimizer] 表单未找到:', formId);
            return;
        }

        const fileInputs = form.querySelectorAll('input[type="file"][accept*="image"]');

        fileInputs.forEach(input => {
            input.addEventListener('change', async (e) => {
                const files = Array.from(e.target.files);
                const optimizedFiles = [];

                for (const file of files) {
                    try {
                        // 检查文件类型
                        if (!file.type.startsWith('image/')) {
                            optimizedFiles.push(file);
                            continue;
                        }

                        // 压缩或转换
                        let optimizedBlob;
                        if (options.convertToWebP && await this.supportsWebP()) {
                            optimizedBlob = await this.convertToWebP(file, options.quality || 0.8);
                        } else {
                            optimizedBlob = await this.compress(file, options);
                        }

                        // 创建新的File对象
                        const optimizedFile = new File(
                            [optimizedBlob],
                            file.name.replace(/\.[^.]+$/, '.webp'),
                            { type: optimizedBlob.type }
                        );

                        optimizedFiles.push(optimizedFile);
                        console.log('[ImageOptimizer] 图片已优化:', file.name);

                    } catch (error) {
                        console.error('[ImageOptimizer] 图片优化失败:', error);
                        optimizedFiles.push(file); // 使用原始文件
                    }
                }

                // 更新input文件列表（注意：某些浏览器可能不支持）
                const dt = new DataTransfer();
                optimizedFiles.forEach(file => dt.items.add(file));
                input.files = dt.files;

                console.log('[ImageOptimizer] 表单图片优化完成');
            });
        });
    }
};

// 暴露到全局
window.ImageOptimizer = ImageOptimizer;

// 自动启用懒加载（如果页面有.lazy类的图片）
document.addEventListener('DOMContentLoaded', () => {
    const lazyImages = document.querySelectorAll('.lazy, .lazy-image, img[loading="lazy"]');
    if (lazyImages.length > 0) {
        ImageOptimizer.lazyLoad('.lazy, .lazy-image, img[loading="lazy"]');
        console.log('[ImageOptimizer] 已自动启用懒加载');
    }
});
