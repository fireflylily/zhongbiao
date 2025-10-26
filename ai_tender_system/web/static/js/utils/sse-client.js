/**
 * SSE (Server-Sent Events) 客户端工具类
 * 提供统一的SSE流处理接口，支持进度追踪和事件处理
 *
 * 使用示例:
 * ```javascript
 * const sseClient = new SSEClient();
 * await sseClient.stream({
 *     url: '/api/generate-proposal-stream',
 *     formData: formData,
 *     onEvent: (data) => {
 *         console.log('SSE事件:', data);
 *         if (data.progress !== undefined) {
 *             updateProgress(data.progress);
 *         }
 *     },
 *     onComplete: (data) => {
 *         console.log('生成完成:', data);
 *     },
 *     onError: (error) => {
 *         console.error('生成失败:', error);
 *     }
 * });
 * ```
 */
class SSEClient {
    constructor() {
        this.reader = null;
        this.controller = null;
    }

    /**
     * 开始SSE流式请求
     * @param {Object} options - 配置选项
     * @param {string} options.url - API端点URL
     * @param {FormData|Object} options.formData - 请求数据（FormData或普通对象）
     * @param {Function} options.onEvent - 每个SSE事件的回调 (data) => void
     * @param {Function} options.onComplete - 完成时的回调 (finalData) => void
     * @param {Function} options.onError - 错误时的回调 (error) => void
     * @param {Object} options.requestOptions - 额外的fetch选项
     * @returns {Promise<void>}
     */
    async stream({ url, formData, onEvent, onComplete, onError, requestOptions = {} }) {
        return new Promise((resolve, reject) => {
            // 创建AbortController用于取消请求
            this.controller = new AbortController();

            // 准备请求配置
            const fetchOptions = {
                method: 'POST',
                body: formData,
                signal: this.controller.signal,
                ...requestOptions
            };

            fetch(url, fetchOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    this.reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';

                    const readStream = () => {
                        this.reader.read().then(({ done, value }) => {
                            if (done) {
                                resolve();
                                return;
                            }

                            // 解码数据并累积到缓冲区
                            buffer += decoder.decode(value, { stream: true });

                            // 按照SSE格式分割（以\n\n分隔）
                            const lines = buffer.split('\n\n');
                            buffer = lines.pop() || '';

                            // 处理每一行
                            for (const line of lines) {
                                if (line.startsWith('data: ')) {
                                    try {
                                        const data = JSON.parse(line.substring(6));

                                        // 触发事件回调
                                        if (onEvent) {
                                            onEvent(data);
                                        }

                                        // 检查是否完成
                                        if (data.stage === 'completed') {
                                            if (onComplete) {
                                                onComplete(data);
                                            }
                                            resolve(data);
                                            return;
                                        }
                                        // 检查是否出错
                                        else if (data.stage === 'error') {
                                            const error = new Error(data.error || data.message || '未知错误');
                                            if (onError) {
                                                onError(error);
                                            }
                                            reject(error);
                                            return;
                                        }
                                    } catch (e) {
                                        console.error('[SSEClient] 解析SSE数据失败:', e);
                                        console.error('[SSEClient] 原始数据:', line);
                                    }
                                }
                            }

                            // 继续读取下一块数据
                            readStream();
                        }).catch(error => {
                            if (onError) {
                                onError(error);
                            }
                            reject(error);
                        });
                    };

                    // 开始读取流
                    readStream();
                })
                .catch(error => {
                    if (onError) {
                        onError(error);
                    }
                    reject(error);
                });
        });
    }

    /**
     * 取消当前SSE请求
     */
    abort() {
        if (this.controller) {
            this.controller.abort();
            this.controller = null;
        }
        if (this.reader) {
            this.reader.cancel();
            this.reader = null;
        }
    }

    /**
     * 检查是否正在进行SSE请求
     * @returns {boolean}
     */
    isActive() {
        return this.reader !== null;
    }
}

// 导出为全局变量
if (typeof window !== 'undefined') {
    window.SSEClient = SSEClient;
}

// 支持模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SSEClient;
}
