/**
 * 知识库搜索管理模块
 * 负责知识库搜索功能
 */

class SearchManager {
    constructor() {
        this.currentSearchResults = [];
        this.searchHistory = [];
    }

    /**
     * 初始化搜索管理器
     */
    init() {
        this.bindEvents();
    }

    /**
     * 显示搜索模态框
     */
    showSearchModal() {
        const modalHtml = `
            <div class="modal fade" id="searchModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-search me-2"></i>知识库搜索
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <!-- 搜索配置区域 -->
                                <div class="col-md-4 border-end">
                                    <div class="sticky-top" style="top: 1rem;">
                                        <!-- 搜索输入 -->
                                        <div class="mb-3">
                                            <label class="form-label">搜索问题</label>
                                            <div class="input-group">
                                                <input type="text" class="form-control" id="searchQuery"
                                                       placeholder="输入您要搜索的问题..."
                                                       onkeypress="if(event.key==='Enter') window.searchManager.performSearch()">
                                                <button class="btn btn-primary" onclick="window.searchManager.performSearch()">
                                                    <i class="bi bi-search"></i>
                                                </button>
                                            </div>
                                        </div>

                                        <!-- 搜索模式 -->
                                        <div class="mb-3">
                                            <label class="form-label">搜索模式</label>
                                            <div class="d-flex gap-3">
                                                <div class="form-check">
                                                    <input class="form-check-input" type="radio" name="searchMode" value="keyword" id="modeKeyword" checked>
                                                    <label class="form-check-label" for="modeKeyword">关键词</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="radio" name="searchMode" value="semantic" id="modeSemantic">
                                                    <label class="form-check-label" for="modeSemantic">语义搜索</label>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- 文档类型筛选 -->
                                        <div class="mb-3">
                                            <label class="form-label">文档类型</label>
                                            <select class="form-select" id="searchCategory">
                                                <option value="">全部类型</option>
                                                <option value="tech">技术文档</option>
                                                <option value="product">产品文档</option>
                                                <option value="manual">使用手册</option>
                                                <option value="other">其他</option>
                                            </select>
                                        </div>

                                        <!-- 隐私级别筛选 -->
                                        <div class="mb-3">
                                            <label class="form-label">隐私级别</label>
                                            <select class="form-select" id="searchPrivacy">
                                                <option value="">全部级别</option>
                                                <option value="1">公开</option>
                                                <option value="2">内部</option>
                                                <option value="3">机密</option>
                                                <option value="4">绝密</option>
                                            </select>
                                        </div>

                                        <!-- 结果数量限制 -->
                                        <div class="mb-3">
                                            <label class="form-label">结果数量</label>
                                            <select class="form-select" id="searchLimit">
                                                <option value="10">10条</option>
                                                <option value="20" selected>20条</option>
                                                <option value="50">50条</option>
                                                <option value="100">100条</option>
                                            </select>
                                        </div>

                                        <!-- 相似度阈值（仅语义搜索） -->
                                        <div class="mb-3" id="thresholdContainer" style="display: none;">
                                            <label class="form-label">相似度阈值</label>
                                            <div class="d-flex align-items-center">
                                                <input type="range" class="form-range me-2" id="similarityThreshold"
                                                       min="0.3" max="0.9" step="0.1" value="0.7">
                                                <span id="thresholdValue">0.7</span>
                                            </div>
                                        </div>

                                        <button type="button" class="btn btn-primary w-100" onclick="window.searchManager.performSearch()">
                                            <i class="bi bi-search me-1"></i>开始搜索
                                        </button>
                                    </div>
                                </div>

                                <!-- 搜索结果区域 -->
                                <div class="col-md-8">
                                    <div id="searchResults">
                                        <div class="text-center py-5 text-muted">
                                            <i class="bi bi-search fs-1"></i>
                                            <p class="mt-3">请输入搜索条件开始搜索</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" onclick="window.searchManager.exportSearchResults()">
                                <i class="bi bi-download me-1"></i>导出结果
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的搜索模态框
        const existingModal = document.getElementById('searchModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新的模态框到页面
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('searchModal'));
        modal.show();

        // 绑定事件
        this.bindSearchModalEvents();
    }

    /**
     * 绑定搜索模态框事件
     */
    bindSearchModalEvents() {
        // 搜索模式切换事件
        const modeRadios = document.querySelectorAll('input[name="searchMode"]');
        modeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                const thresholdContainer = document.getElementById('thresholdContainer');
                if (radio.value === 'semantic') {
                    thresholdContainer.style.display = 'block';
                } else {
                    thresholdContainer.style.display = 'none';
                }
            });
        });

        // 相似度阈值滑块事件
        const thresholdSlider = document.getElementById('similarityThreshold');
        const thresholdValue = document.getElementById('thresholdValue');
        if (thresholdSlider && thresholdValue) {
            thresholdSlider.addEventListener('input', (e) => {
                thresholdValue.textContent = e.target.value;
            });
        }
    }

    /**
     * 执行搜索
     */
    async performSearch() {
        const query = document.getElementById('searchQuery').value.trim();
        const category = document.getElementById('searchCategory').value;
        const privacy = document.getElementById('searchPrivacy').value;
        const searchMode = document.querySelector('input[name="searchMode"]:checked').value;
        const limit = document.getElementById('searchLimit').value;
        const threshold = document.getElementById('similarityThreshold').value;

        if (!query) {
            if (window.showAlert) {
                window.showAlert('请输入搜索问题', 'warning');
            }
            return;
        }

        const resultsContainer = document.getElementById('searchResults');

        // 显示加载状态
        const searchModeText = searchMode === 'semantic' ? '语义搜索' : '关键词搜索';
        resultsContainer.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">搜索中...</span>
                </div>
                <p class="mt-3 text-muted">正在进行${searchModeText}...</p>
            </div>
        `;

        try {
            const startTime = Date.now();

            // 构建搜索参数
            const params = {
                query: query,
                mode: searchMode,
                limit: parseInt(limit)
            };

            if (category) params.category = category;
            if (privacy) params.privacy_level = privacy;
            if (searchMode === 'semantic' && threshold) {
                params.similarity_threshold = parseFloat(threshold);
            }

            // 发送搜索请求
            const response = await axios.post('/api/knowledge_base/search', params);

            const searchTime = Date.now() - startTime;

            if (response.data.success) {
                this.currentSearchResults = response.data.data || [];
                this.displaySearchResults(this.currentSearchResults, searchMode, searchTime);

                // 添加到搜索历史
                this.addToSearchHistory(query, searchMode, this.currentSearchResults.length);
            } else {
                throw new Error(response.data.error || '搜索失败');
            }

        } catch (error) {
            console.error('搜索失败:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="bi bi-exclamation-triangle me-2"></i>搜索失败</h6>
                    <p class="mb-2">${error.message}</p>
                    <div class="mt-3">
                        <button class="btn btn-outline-danger btn-sm" onclick="window.searchManager.performSearch()">
                            <i class="bi bi-arrow-clockwise me-1"></i>重试
                        </button>
                    </div>
                </div>
            `;
        }
    }

    /**
     * 显示搜索结果
     * @param {Array} results 搜索结果
     * @param {string} searchMode 搜索模式
     * @param {number} searchTime 搜索时间（毫秒）
     */
    displaySearchResults(results, searchMode = 'keyword', searchTime = 0) {
        const resultsContainer = document.getElementById('searchResults');

        if (!results || results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong>未找到相关文档</strong>
                    <div class="mt-2 small">
                        <p class="mb-1">建议尝试：</p>
                        <ul class="mb-0">
                            <li>使用不同的关键词</li>
                            <li>尝试语义搜索模式</li>
                            <li>调低相似度阈值</li>
                            <li>选择不同的文档类型或隐私级别</li>
                        </ul>
                    </div>
                </div>
            `;
            return;
        }

        const searchModeText = searchMode === 'semantic' ? '语义搜索' : '关键词搜索';

        let html = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h6 class="mb-0">搜索结果</h6>
                    <small class="text-muted">
                        找到 ${results.length} 个相关文档，用时 ${searchTime}ms（${searchModeText}）
                    </small>
                </div>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="window.searchManager.sortResults('relevance')">
                        <i class="bi bi-sort-alpha-down me-1"></i>按相关性
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="window.searchManager.sortResults('date')">
                        <i class="bi bi-calendar me-1"></i>按时间
                    </button>
                </div>
            </div>
        `;

        html += '<div class="search-results-list">';

        results.forEach((result, index) => {
            html += this.renderSearchResultItem(result, index, searchMode);
        });

        html += '</div>';

        resultsContainer.innerHTML = html;
    }

    /**
     * 渲染搜索结果项
     * @param {Object} result 搜索结果项
     * @param {number} index 索引
     * @param {string} searchMode 搜索模式
     */
    renderSearchResultItem(result, index, searchMode) {
        const privacyNames = ['', '公开', '内部', '机密', '绝密'];
        const categoryNames = {
            'tech': '技术文档',
            'product': '产品文档',
            'manual': '使用手册',
            'other': '其他'
        };

        const privacyLevel = result.privacy_classification || 1;
        const category = result.document_category || 'tech';
        const fileSize = result.file_size ? (result.file_size / (1024 * 1024)).toFixed(2) : '0';

        return `
            <div class="card mb-3 search-result-item" data-doc-id="${result.doc_id}">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <div class="d-flex align-items-start">
                                <div class="bg-primary bg-opacity-10 rounded p-2 me-3 flex-shrink-0">
                                    <i class="bi bi-file-earmark-text text-primary fs-5"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">
                                        <a href="javascript:void(0)" onclick="window.searchManager.viewDocument(${result.doc_id})"
                                           class="text-decoration-none">${result.original_filename}</a>
                                    </h6>

                                    <div class="d-flex align-items-center mb-2">
                                        <span class="badge bg-${privacyLevel === 1 ? 'success' : privacyLevel === 2 ? 'primary' : privacyLevel === 3 ? 'warning' : 'danger'} me-2">
                                            ${privacyNames[privacyLevel]}
                                        </span>
                                        <span class="badge bg-secondary me-2">
                                            ${categoryNames[category] || '其他'}
                                        </span>
                                        ${searchMode === 'semantic' && result.similarity_score ?
                                            `<span class="badge bg-info">相似度: ${(result.similarity_score * 100).toFixed(1)}%</span>` :
                                            ''
                                        }
                                    </div>

                                    ${result.content_snippet ? `
                                        <div class="search-snippet">
                                            <p class="mb-0 text-muted small">${this.highlightSearchTerms(result.content_snippet)}</p>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-end">
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <i class="bi bi-building me-1"></i>${result.company_name || '未知企业'}
                                    </small>
                                </div>
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <i class="bi bi-box me-1"></i>${result.product_name || '未知产品'}
                                    </small>
                                </div>
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <i class="bi bi-hdd me-1"></i>${fileSize} MB
                                    </small>
                                </div>
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <i class="bi bi-calendar me-1"></i>${result.upload_time ? new Date(result.upload_time).toLocaleDateString() : '未知'}
                                    </small>
                                </div>
                                <div class="btn-group-vertical w-100">
                                    <button class="btn btn-outline-primary btn-sm" onclick="window.searchManager.viewDocument(${result.doc_id})">
                                        <i class="bi bi-eye me-1"></i>查看
                                    </button>
                                    <button class="btn btn-outline-secondary btn-sm" onclick="window.searchManager.downloadDocument(${result.doc_id})">
                                        <i class="bi bi-download me-1"></i>下载
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 高亮搜索关键词
     * @param {string} text 文本内容
     */
    highlightSearchTerms(text) {
        const query = document.getElementById('searchQuery')?.value.trim();
        if (!query || !text) return text;

        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark class="bg-warning">$1</mark>');
    }

    /**
     * 排序搜索结果
     * @param {string} sortBy 排序方式
     */
    sortResults(sortBy) {
        if (!this.currentSearchResults || this.currentSearchResults.length === 0) return;

        const sortedResults = [...this.currentSearchResults];

        switch (sortBy) {
            case 'relevance':
                sortedResults.sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0));
                break;
            case 'date':
                sortedResults.sort((a, b) => new Date(b.upload_time || 0) - new Date(a.upload_time || 0));
                break;
        }

        this.currentSearchResults = sortedResults;
        const searchMode = document.querySelector('input[name="searchMode"]:checked')?.value || 'keyword';
        this.displaySearchResults(this.currentSearchResults, searchMode, 0);
    }

    /**
     * 查看文档
     * @param {number} docId 文档ID
     */
    async viewDocument(docId) {
        try {
            const response = await axios.get(`/api/knowledge_base/documents/${docId}`);
            if (response.data.success) {
                // 这里可以打开文档查看窗口
                console.log('查看文档:', response.data.data);
                if (window.showAlert) {
                    window.showAlert('文档查看功能开发中...', 'info');
                }
            }
        } catch (error) {
            console.error('获取文档失败:', error);
            if (window.showAlert) {
                window.showAlert('获取文档失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 下载文档
     * @param {number} docId 文档ID
     */
    async downloadDocument(docId) {
        try {
            const response = await axios.get(`/api/knowledge_base/documents/${docId}/download`, {
                responseType: 'blob'
            });

            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            // 从响应头获取文件名
            const contentDisposition = response.headers['content-disposition'];
            let filename = 'document';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            if (window.showAlert) {
                window.showAlert('文档下载成功', 'success');
            }

        } catch (error) {
            console.error('下载文档失败:', error);
            if (window.showAlert) {
                window.showAlert('下载文档失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 导出搜索结果
     */
    exportSearchResults() {
        if (!this.currentSearchResults || this.currentSearchResults.length === 0) {
            if (window.showAlert) {
                window.showAlert('没有搜索结果可导出', 'warning');
            }
            return;
        }

        // 创建CSV内容
        const headers = ['文件名', '企业', '产品', '分类', '隐私级别', '上传时间', '文件大小(MB)'];
        const csvContent = [
            headers.join(','),
            ...this.currentSearchResults.map(result => [
                `"${result.original_filename || ''}"`,
                `"${result.company_name || ''}"`,
                `"${result.product_name || ''}"`,
                `"${result.document_category || ''}"`,
                `"${result.privacy_classification || ''}"`,
                `"${result.upload_time || ''}"`,
                `"${result.file_size ? (result.file_size / (1024 * 1024)).toFixed(2) : '0'}"`
            ].join(','))
        ].join('\n');

        // 创建下载链接
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `搜索结果_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        if (window.showAlert) {
            window.showAlert('搜索结果导出成功', 'success');
        }
    }

    /**
     * 添加到搜索历史
     * @param {string} query 搜索查询
     * @param {string} mode 搜索模式
     * @param {number} resultCount 结果数量
     */
    addToSearchHistory(query, mode, resultCount) {
        const historyItem = {
            query,
            mode,
            resultCount,
            timestamp: new Date().toISOString()
        };

        this.searchHistory.unshift(historyItem);

        // 只保留最近20条搜索历史
        if (this.searchHistory.length > 20) {
            this.searchHistory = this.searchHistory.slice(0, 20);
        }

        // 可以将搜索历史保存到localStorage
        try {
            localStorage.setItem('kb_search_history', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.warn('无法保存搜索历史:', error);
        }
    }

    /**
     * 加载搜索历史
     */
    loadSearchHistory() {
        try {
            const saved = localStorage.getItem('kb_search_history');
            if (saved) {
                this.searchHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.warn('无法加载搜索历史:', error);
            this.searchHistory = [];
        }
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 页面加载时加载搜索历史
        document.addEventListener('DOMContentLoaded', () => {
            this.loadSearchHistory();
        });
    }

    // Getter methods
    getCurrentSearchResults() {
        return this.currentSearchResults;
    }

    getSearchHistory() {
        return this.searchHistory;
    }
}

// 全局函数，供HTML模板调用
window.showSearchModal = () => window.searchManager.showSearchModal();

// 创建全局实例
window.searchManager = new SearchManager();