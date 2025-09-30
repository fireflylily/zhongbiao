/**
 * 知识库分类管理模块
 * 负责企业和产品的树形结构管理
 */

class CategoryManager {
    constructor() {
        this.currentCompanyId = null;
        this.currentProductId = null;
        this.currentCategory = null;
    }

    /**
     * 渲染企业树形结构
     * @param {Array} companies 企业列表
     */
    renderCompanyTree(companies) {
        const treeHtml = companies.map(company => {
            return '<div class="list-group mb-3">' +
                '<!-- 企业节点 -->' +
                '<div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"' +
                     ' onclick="window.categoryManager.toggleCompanyNode(' + company.company_id + ', \'' + company.company_name + '\')">' +
                    '<div class="d-flex align-items-center">' +
                        '<i class="bi bi-chevron-right tree-toggle me-2" id="toggle-' + company.company_id + '"></i>' +
                        '<i class="bi bi-building text-primary me-2"></i>' +
                        '<span class="fw-medium">' + company.company_name + '</span>' +
                        '<span class="badge bg-secondary ms-2">' + (company.product_count || 0) + '</span>' +
                    '</div>' +
                '</div>' +
                '<!-- 企业子菜单 -->' +
                '<div class="list-group-item d-none" id="company-profile-' + company.company_id + '">' +
                    '<div class="list-group">' +
                        '<div class="list-group-item list-group-item-action" onclick="window.categoryManager.selectCompanyProfile(' + company.company_id + ')">' +
                            '<div class="d-flex align-items-center">' +
                                '<i class="bi bi-person-workspace text-info me-2"></i>' +
                                '<span>企业信息库</span>' +
                            '</div>' +
                        '</div>' +
                        '<div class="list-group" id="products-' + company.company_id + '">' +
                            '<!-- 产品列表将在这里动态加载 -->' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>';
        }).join('');

        document.getElementById('companyTree').innerHTML = treeHtml;
    }

    /**
     * 切换企业节点展开/折叠状态
     * @param {number} companyId 企业ID
     * @param {string} companyName 企业名称
     */
    async toggleCompanyNode(companyId, companyName) {
        const toggleIcon = document.getElementById('toggle-' + companyId);
        const profileContainer = document.getElementById('company-profile-' + companyId);
        const productsContainer = document.getElementById('products-' + companyId);

        const isExpanded = !profileContainer.classList.contains('d-none');

        if (isExpanded) {
            // 折叠
            profileContainer.classList.add('d-none');
            toggleIcon.classList.remove('bi-chevron-down');
            toggleIcon.classList.add('bi-chevron-right');
            productsContainer.innerHTML = '';
        } else {
            // 展开
            profileContainer.classList.remove('d-none');
            toggleIcon.classList.remove('bi-chevron-right');
            toggleIcon.classList.add('bi-chevron-down');

            // 加载产品列表
            await this.loadCompanyProducts(companyId);
        }

        // 更新当前选中的公司ID（不触发选择事件）
        this.currentCompanyId = companyId;
    }

    /**
     * 选择公司
     * @param {number} companyId 企业ID
     * @param {string} companyName 企业名称
     */
    async selectCompany(companyId, companyName) {
        this.currentCompanyId = companyId;
        this.currentProductId = null;

        // 更新活动状态
        document.querySelectorAll('.list-group-item-action').forEach(node => node.classList.remove('active'));
        document.querySelector('[onclick*="toggleCompanyNode(' + companyId + '"]').classList.add('active');

        // 加载公司详情
        try {
            const response = await axios.get('/api/companies/' + companyId);
            if (response.data.success && response.data.data) {
                // 通知其他模块公司已选择
                this.onCompanySelected(response.data.data);
            }
        } catch (error) {
            console.error('加载公司详情失败:', error);
            if (window.showAlert) {
                window.showAlert('加载公司详情失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 加载企业产品列表
     * @param {number} companyId 企业ID
     */
    async loadCompanyProducts(companyId) {
        try {
            const response = await axios.get('/api/knowledge_base/companies/' + companyId + '/products');
            if (response.data.success) {
                this.renderProductTree(companyId, response.data.data);
            }
        } catch (error) {
            console.error('加载产品列表失败:', error);
        }
    }

    /**
     * 渲染产品树形结构（简化版 - 点击产品直接显示文档）
     * @param {number} companyId 企业ID
     * @param {Array} products 产品列表
     */
    renderProductTree(companyId, products) {
        const productsContainer = document.getElementById('products-' + companyId);
        if (!products || products.length === 0) {
            productsContainer.innerHTML =
                '<div class="list-group-item text-muted small">' +
                    '<i class="bi bi-inbox me-2"></i>暂无产品' +
                '</div>';
            return;
        }

        const productHtml = products.map(product => {
            return '<div class="list-group-item list-group-item-action" ' +
                     'onclick="window.categoryManager.selectProduct(' + product.product_id + ', \'' + product.product_name + '\')">' +
                    '<div class="d-flex justify-content-between align-items-center">' +
                        '<div class="d-flex align-items-center">' +
                            '<i class="bi bi-box-seam text-success me-2"></i>' +
                            '<span>' + product.product_name + '</span>' +
                        '</div>' +
                        '<span class="badge bg-info">' + (product.document_count || 0) + '</span>' +
                    '</div>' +
                '</div>';
        }).join('');

        productsContainer.innerHTML = productHtml;
    }

    /**
     * 选择产品（直接加载产品的所有文档）
     * @param {number} productId 产品ID
     * @param {string} productName 产品名称
     */
    async selectProduct(productId, productName) {
        this.currentProductId = productId;
        this.currentCategory = null;  // 清除分类信息

        // 更新活动状态
        this.updateActiveState('[onclick*="selectProduct(' + productId + ',"]');

        try {
            // 步骤1: 获取产品的文档库（现在每个产品只有1个general库）
            const librariesResp = await axios.get(`/api/knowledge_base/product/${productId}/libraries`);

            if (!librariesResp.data.success) {
                throw new Error('获取文档库列表失败');
            }

            const libraries = librariesResp.data.data;
            if (!libraries || libraries.length === 0) {
                // 没有文档库，显示空状态
                if (window.documentManager) {
                    window.documentManager.renderProductDocuments(productId, productName, []);
                }
                return;
            }

            // 步骤2: 获取第一个文档库的文档（general库）
            const library = libraries[0];
            const docsResp = await axios.get(`/api/knowledge_base/libraries/${library.library_id}/documents`);

            if (docsResp.data.success) {
                // 通知文档管理器渲染产品文档
                if (window.documentManager) {
                    window.documentManager.renderProductDocuments(productId, productName, docsResp.data.data);
                }
            }
        } catch (error) {
            console.error('加载产品文档失败:', error);
            if (window.showAlert) {
                window.showAlert('加载文档失败：' + error.message, 'danger');
            }
        }

        // 通知其他模块产品已选择
        this.onProductSelected(productId, productName);
    }

    /**
     * 选择企业信息库
     * @param {number} companyId 企业ID
     */
    async selectCompanyProfile(companyId) {
        this.currentCompanyId = companyId;
        this.currentProductId = null;

        // 更新活动状态
        this.updateActiveState('[onclick*="selectCompanyProfile(' + companyId + '"]');

        // 通知其他模块企业信息库已选择
        this.onCompanyProfileSelected(companyId);
    }

    /**
     * 更新选中状态
     * @param {string} targetSelector 目标选择器
     */
    updateActiveState(targetSelector) {
        document.querySelectorAll('.list-group-item-action').forEach(node =>
            node.classList.remove('active')
        );

        const target = document.querySelector(targetSelector);
        if (target) {
            target.classList.add('active');
        }
    }

    /**
     * 显示添加公司模态框
     */
    showAddCompanyModal() {
        new bootstrap.Modal(document.getElementById('addCompanyModal')).show();
    }

    /**
     * 显示添加产品模态框
     * @param {number} companyId 企业ID
     */
    showAddProductModal(companyId) {
        this.currentCompanyId = companyId;
        new bootstrap.Modal(document.getElementById('addProductModal')).show();
    }

    /**
     * 添加新公司
     */
    async addCompany() {
        const data = {
            company_name: document.getElementById('companyName').value,
            company_code: document.getElementById('companyCode').value,
            industry_type: document.getElementById('industryType').value,
            description: document.getElementById('companyDesc').value
        };

        try {
            const response = await axios.post('/api/companies', data);
            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('公司添加成功', 'success');
                }
                bootstrap.Modal.getInstance(document.getElementById('addCompanyModal')).hide();
                document.getElementById('addCompanyForm').reset();

                // 重新加载公司列表
                if (window.loadCompanies) {
                    window.loadCompanies();
                }
            }
        } catch (error) {
            console.error('添加公司失败:', error);
            if (window.showAlert) {
                window.showAlert('添加公司失败：' + error.message, 'danger');
            }
        }
    }

    /**
     * 添加新产品
     */
    async addProduct() {
        const data = {
            company_id: this.currentCompanyId,
            product_name: document.getElementById('productName').value,
            product_code: document.getElementById('productCode').value,
            category: document.getElementById('productCategory').value,
            description: document.getElementById('productDesc').value
        };

        try {
            const response = await axios.post('/api/knowledge_base/products', data);
            if (response.data.success) {
                if (window.showAlert) {
                    window.showAlert('产品添加成功', 'success');
                }
                bootstrap.Modal.getInstance(document.getElementById('addProductModal')).hide();

                // 重新选择当前公司以刷新产品列表
                this.selectCompany(this.currentCompanyId, '');
                document.getElementById('addProductForm').reset();
            }
        } catch (error) {
            console.error('添加产品失败:', error);
            if (window.showAlert) {
                window.showAlert('添加产品失败：' + (error.response?.data?.error || error.message), 'danger');
            }
        }
    }

    // 事件回调方法，供其他模块监听
    onCompanySelected(companyData) {
        // 可以被其他模块重写
        console.log('Company selected:', companyData);
    }

    onProductSelected(productId, productName) {
        // 可以被其他模块重写
        console.log('Product selected:', productId, productName);
    }

    onCompanyProfileSelected(companyId) {
        // 可以被其他模块重写
        console.log('Company profile selected:', companyId);
    }

    onProductCategorySelected(productId, category) {
        // 可以被其他模块重写
        console.log('Product category selected:', productId, category);
    }

    // Getter methods
    getCurrentCompanyId() {
        return this.currentCompanyId;
    }

    getCurrentProductId() {
        return this.currentProductId;
    }

    getCurrentCategory() {
        return this.currentCategory;
    }
}

// 创建全局实例
window.categoryManager = new CategoryManager();