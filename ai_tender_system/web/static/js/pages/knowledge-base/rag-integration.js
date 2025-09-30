/**
 * RAG知识库集成模块
 * 负责文档自动向量化和智能检索功能
 */

class RAGIntegration {
    constructor() {
        this.ragAvailable = false;
        this.checkRAGStatus();
    }

    /**
     * 检查RAG服务状态
     */
    async checkRAGStatus() {
        try {
            const response = await axios.get('/api/rag/status');
            this.ragAvailable = response.data.available;

            if (this.ragAvailable) {
                console.log('✅ RAG服务可用', response.data.stats);
            } else {
                console.warn('⚠️ RAG服务不可用:', response.data.message);
            }
        } catch (error) {
            console.error('❌ RAG服务检查失败:', error);
            this.ragAvailable = false;
        }
    }

    /**
     * 文档上传成功后自动向量化
     * @param {Object} docInfo 文档信息
     * @param {string} docInfo.file_path 文档路径
     * @param {number} docInfo.company_id 公司ID
     * @param {number} docInfo.product_id 产品ID
     * @param {number} docInfo.document_id 文档ID
     * @param {string} docInfo.document_type 文档类型
     * @param {string} docInfo.document_name 文档名称
     */
    async vectorizeDocument(docInfo) {
        if (!this.ragAvailable) {
            console.log('⏭️ RAG服务不可用，跳过向量化');
            return { success: false, skipped: true };
        }

        try {
            console.log('🔄 开始向量化文档:', docInfo.document_name);

            // 显示处理提示
            if (window.showAlert) {
                window.showAlert('正在处理文档，建立智能索引...', 'info');
            }

            const response = await axios.post('/api/rag/vectorize_document', {
                file_path: docInfo.file_path,
                metadata: {
                    company_id: docInfo.company_id,
                    product_id: docInfo.product_id,
                    document_id: docInfo.document_id,
                    document_type: docInfo.document_type,
                    document_name: docInfo.document_name,
                    upload_time: new Date().toISOString()
                }
            });

            if (response.data.success) {
                console.log('✅ 文档向量化成功:', response.data);
                if (window.showAlert) {
                    window.showAlert(
                        `文档已建立智能索引（${response.data.chunks_count}个文本块）`,
                        'success'
                    );
                }
                return response.data;
            } else {
                console.error('❌ 文档向量化失败:', response.data.error);
                return response.data;
            }

        } catch (error) {
            console.error('❌ 向量化请求异常:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 智能检索
     * @param {string} query 查询问题
     * @param {Object} filters 过滤条件
     * @param {number} filters.company_id 公司ID
     * @param {number} filters.product_id 产品ID
     * @param {number} k 返回结果数量
     */
    async search(query, filters = {}, k = 5) {
        if (!this.ragAvailable) {
            if (window.showAlert) {
                window.showAlert('RAG服务不可用，请先安装依赖', 'warning');
            }
            return { success: false, results: [] };
        }

        try {
            const response = await axios.post('/api/rag/search', {
                query: query,
                company_id: filters.company_id,
                product_id: filters.product_id,
                k: k
            });

            return response.data;

        } catch (error) {
            console.error('智能检索失败:', error);
            if (window.showAlert) {
                window.showAlert('智能检索失败：' + error.message, 'danger');
            }
            return { success: false, results: [] };
        }
    }

    /**
     * 删除文档的向量数据
     * @param {number} documentId 文档ID
     * @param {number} companyId 公司ID
     */
    async deleteDocumentVectors(documentId, companyId) {
        if (!this.ragAvailable) {
            return { success: false, skipped: true };
        }

        try {
            const response = await axios.delete('/api/rag/delete_document', {
                data: {
                    document_id: documentId,
                    company_id: companyId
                }
            });

            return response.data;

        } catch (error) {
            console.error('删除向量数据失败:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 批量向量化公司的所有文档
     * @param {number} companyId 公司ID
     */
    async batchVectorizeCompanyDocs(companyId) {
        if (!this.ragAvailable) {
            console.log('RAG服务不可用，跳过批量向量化');
            return;
        }

        // TODO: 实现批量向量化逻辑
        // 1. 获取公司所有文档列表
        // 2. 逐个调用vectorizeDocument
        // 3. 显示进度

        console.log('批量向量化功能待实现');
    }
}

// 创建全局实例
window.ragIntegration = new RAGIntegration();