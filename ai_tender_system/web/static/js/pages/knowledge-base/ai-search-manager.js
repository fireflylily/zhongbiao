/**
 * AI智能搜索管理器
 * 负责知识库的智能检索和结果展示
 */

class AISearchManager {
    constructor() {
        this.currentCompanyId = null;
        this.currentProductId = null;
    }

    /**
     * 设置搜索范围
     */
    setSearchScope(companyId, productId) {
        this.currentCompanyId = companyId;
        this.currentProductId = productId;
    }

    /**
     * 显示AI检索面板
     */
    showSearchPanel() {
        const searchCard = document.getElementById('aiSearchCard');
        if (searchCard) {
            searchCard.style.display = 'block';
            document.getElementById('aiQueryInput')?.focus();
        }
    }

    /**
     * 隐藏AI检索面板
     */
    hideSearchPanel() {
        const searchCard = document.getElementById('aiSearchCard');
        if (searchCard) {
            searchCard.style.display = 'none';
        }
    }

    /**
     * 执行AI智能检索（使用Chroma向量搜索）
     */
    async performSearch() {
        const query = document.getElementById('aiQueryInput')?.value.trim();
        if (!query) {
            if (window.showAlert) {
                window.showAlert('请输入查询问题', 'warning');
            }
            return;
        }

        // 获取当前选中的范围
        const filters = {};
        if (this.currentCompanyId) {
            filters.company_id = this.currentCompanyId;
        }
        if (this.currentProductId) {
            filters.product_id = this.currentProductId;
        }

        // 显示加载状态
        const resultsDiv = document.getElementById('aiSearchResults');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">搜索中...</span>
                </div>
                <p class="text-muted mt-2">正在智能检索... (Chroma向量搜索)</p>
            </div>
        `;

        // 隐藏提示
        const tips = document.getElementById('aiSearchTips');
        if (tips) {
            tips.style.display = 'none';
        }

        try {
            // 调用RAG智能搜索API（使用text2vec-base-chinese高质量语义模型）
            const response = await axios.post('/api/rag/search', {
                query: query,
                k: 10,  // RAG API使用k参数
                company_id: filters.company_id,
                product_id: filters.product_id
            });

            console.log('搜索响应:', response.data);

            if (response.data.success) {
                // 获取目录搜索结果和内容搜索结果
                const tocResults = response.data.toc_results || [];
                const contentResults = response.data.content_results || [];
                const searchTime = 0.1; // RAG API暂不返回时间，使用估计值

                if ((tocResults && tocResults.length > 0) || (contentResults && contentResults.length > 0)) {
                    // 渲染结果（支持目录和内容分层显示）
                    this.displaySearchResults(tocResults, contentResults, searchTime, query);
                } else {
                    resultsDiv.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="bi bi-info-circle"></i>
                            <strong>未找到相关内容</strong>
                            <p class="mb-0 mt-2">建议：</p>
                            <ul class="mb-0">
                                <li>尝试使用不同的关键词</li>
                                <li>减少搜索条件限制</li>
                                <li>确保已上传相关文档</li>
                            </ul>
                        </div>
                    `;
                }
            } else {
                throw new Error(response.data.error || '搜索失败');
            }

        } catch (error) {
            console.error('智能检索失败:', error);

            let errorMessage = error.message;
            if (error.response) {
                errorMessage = error.response.data?.error || error.response.statusText || error.message;
            }

            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <strong>检索失败</strong>
                    <p class="mb-0 mt-2">${errorMessage}</p>
                    ${error.response?.status === 404 ?
                        '<small class="text-muted">提示：可能是向量搜索服务未正确配置</small>' : ''}
                </div>
            `;
        }
    }

    /**
     * 显示检索结果（支持目录和内容分层显示）
     * @param {Array} tocResults - 目录搜索结果数组
     * @param {Array} contentResults - 内容搜索结果数组
     * @param {Number} searchTime - 搜索耗时（秒）
     * @param {String} query - 搜索关键词
     */
    displaySearchResults(tocResults, contentResults, searchTime = 0, query = '') {
        const resultsDiv = document.getElementById('aiSearchResults');
        if (!resultsDiv) return;

        const totalCount = (tocResults?.length || 0) + (contentResults?.length || 0);

        let html = `<div class="search-results">
            <!-- 结果统计 -->
            <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
                <div>
                    <i class="bi bi-check-circle text-success"></i>
                    <strong>找到 ${totalCount} 条相关内容</strong>
                    ${tocResults?.length > 0 ? `<span class="badge bg-primary ms-2">${tocResults.length}个目录匹配</span>` : ''}
                    ${contentResults?.length > 0 ? `<span class="badge bg-secondary ms-2">${contentResults.length}个内容匹配</span>` : ''}
                </div>
                <small class="text-muted">
                    <i class="bi bi-lightning-charge"></i>
                    耗时: ${(searchTime * 1000).toFixed(0)}ms
                </small>
            </div>`;

        // 📑 目录结果区域（优先显示）
        if (tocResults && tocResults.length > 0) {
            html += `
            <div class="toc-results mb-4">
                <h6 class="text-primary mb-3">
                    <i class="bi bi-bookmarks-fill"></i> 目录匹配
                </h6>
                ${tocResults.map((result, index) => this.renderTocResult(result, index, query)).join('')}
            </div>`;
        }

        // 📄 内容结果区域
        if (contentResults && contentResults.length > 0) {
            html += `
            <div class="content-results">
                <h6 class="text-secondary mb-3">
                    <i class="bi bi-file-text-fill"></i> 内容匹配
                </h6>
                ${contentResults.map((result, index) => this.renderSearchResult(result, index, query)).join('')}
            </div>`;
        }

        html += `</div>
        <!-- CSS样式 -->
        <style>
            .hover-lift:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            .gap-2 {
                gap: 0.5rem !important;
            }
            mark {
                background-color: #fff3cd;
                padding: 2px 4px;
                border-radius: 3px;
                font-weight: 500;
            }
        </style>`;

        resultsDiv.innerHTML = html;
    }

    /**
     * 渲染单个目录搜索结果
     */
    renderTocResult(result, index, query) {
        // 计算相似度并限制上限
        const similarity = Math.min((result.score || 0) * 100, 100);
        const badgeColor = result.match_type === 'keyword' ? 'success' : 'primary';
        const matchTypeText = result.match_type === 'keyword' ? '关键词精确匹配' : '文本模糊匹配';

        return `
        <div class="card mb-2 shadow-sm hover-lift border-primary" style="transition: transform 0.2s;">
            <div class="card-body py-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">
                            <i class="bi bi-bookmark-star-fill text-primary me-2"></i>
                            <span class="fw-bold">${result.section_number || ''}</span>
                            <span class="ms-2">${this.highlightKeywords(result.heading_text, query)}</span>
                        </h6>
                        <small class="text-muted">
                            <span class="badge bg-light text-dark me-2">
                                <i class="bi bi-layers"></i> 级别 ${result.heading_level}
                            </span>
                            <span class="badge bg-${badgeColor}">
                                ${matchTypeText}
                            </span>
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-success fs-6">
                            <i class="bi bi-star-fill"></i> ${similarity.toFixed(0)}%
                        </span>
                    </div>
                </div>
            </div>
        </div>`;
    }

    /**
     * 渲染单个内容搜索结果卡片
     */
    renderSearchResult(result, index, query) {
        // 计算相似度百分比并限制上限为100%，防止显示177.7%这样的异常值
        const similarity = Math.min((result.similarity_score || result.score || 0) * 100, 100);
        const badgeColor = similarity >= 70 ? 'success' : similarity >= 50 ? 'primary' : 'secondary';

        // 获取元数据
        const metadata = result.metadata || {};
        const docName = metadata.document_name || metadata.filename || '文档';
        const docType = metadata.document_type || metadata.content_type || '';
        const docId = metadata.doc_id || result.document_id || `doc_${index}`;

        // 截取内容预览
        const content = result.content || result.snippet || '';
        const preview = content.length > 300 ? content.substring(0, 300) + '...' : content;

        return `
        <div class="card mb-3 shadow-sm hover-lift" style="transition: transform 0.2s;">
            <div class="card-body">
                <!-- 标题和相似度 -->
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-subtitle mb-0 d-flex align-items-center">
                        <i class="bi bi-file-text-fill text-primary me-2"></i>
                        <span class="text-primary">${docName}</span>
                    </h6>
                    <div class="d-flex align-items-center">
                        <span class="badge bg-${badgeColor} me-2">
                            <i class="bi bi-star-fill"></i> ${similarity.toFixed(0)}%
                        </span>
                        <span class="badge bg-light text-dark">
                            #${result.rank || index + 1}
                        </span>
                    </div>
                </div>

                <!-- 内容预览 -->
                <p class="card-text mt-3 mb-3" style="line-height: 1.6;">
                    ${this.highlightKeywords(preview, query)}
                </p>

                <!-- 元数据标签 -->
                <div class="d-flex flex-wrap gap-2 align-items-center">
                    ${docType ? `<span class="badge bg-secondary"><i class="bi bi-tag"></i> ${docType}</span>` : ''}
                    ${metadata.company_id ? `<span class="badge bg-info"><i class="bi bi-building"></i> 企业 ${metadata.company_id}</span>` : ''}
                    ${metadata.product_id ? `<span class="badge bg-warning text-dark"><i class="bi bi-box"></i> 产品 ${metadata.product_id}</span>` : ''}
                    ${metadata.chunk_index !== undefined ? `<span class="badge bg-light text-muted">分块 ${metadata.chunk_index}</span>` : ''}
                </div>

                <!-- 操作按钮 -->
                <div class="mt-3 pt-2 border-top">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewFullDocument('${docId}')">
                        <i class="bi bi-eye"></i> 查看完整文档
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="window.aiSearchManager.copyContent(\`${content.replace(/`/g, '\\`')}\`)">
                        <i class="bi bi-clipboard"></i> 复制内容
                    </button>
                </div>
            </div>
        </div>
        `;
    }

    /**
     * 高亮关键词（增强版）
     */
    highlightKeywords(text, query) {
        if (!query) return this.escapeHtml(text);

        // 转义HTML特殊字符
        text = this.escapeHtml(text);

        // 分词并高亮
        const keywords = query.split(/\s+/).filter(k => k.length > 1);
        let highlighted = text;

        keywords.forEach(keyword => {
            // 转义正则表达式特殊字符
            const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`(${escapedKeyword})`, 'gi');
            highlighted = highlighted.replace(regex, '<mark>$1</mark>');
        });

        return highlighted;
    }

    /**
     * 转义HTML特殊字符
     */
    escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * 复制内容到剪贴板
     */
    copyContent(content) {
        if (!content) {
            if (window.showAlert) {
                window.showAlert('未找到可复制的内容', 'warning');
            }
            return;
        }

        navigator.clipboard.writeText(content).then(() => {
            if (window.showAlert) {
                window.showAlert('内容已复制到剪贴板', 'success');
            }
        }).catch(err => {
            if (window.showAlert) {
                window.showAlert('复制失败：' + err.message, 'danger');
            }
        });
    }
}

// 创建全局实例
window.aiSearchManager = new AISearchManager();

// 提供便捷的全局函数（向后兼容）
function showAISearch() {
    window.aiSearchManager.showSearchPanel();
}

function performAISearch() {
    window.aiSearchManager.performSearch();
}