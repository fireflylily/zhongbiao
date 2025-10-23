/**
 * 工作流程图管理器
 * 负责流程图的交互逻辑、Tab跳转等功能
 */
class WorkflowDiagramManager {
    constructor() {
        this.currentActiveTab = null;
        this.initialized = false;
    }

    /**
     * 初始化管理器
     */
    initialize() {
        if (this.initialized) {
            console.log('[WorkflowDiagramManager] 已经初始化，跳过重复初始化');
            return;
        }

        console.log('[WorkflowDiagramManager] 初始化工作流程图...');

        // 监听Tab切换事件，高亮当前模块
        this.bindTabSwitchEvents();

        this.initialized = true;
    }

    /**
     * 绑定Tab切换事件，高亮当前激活的模块
     */
    bindTabSwitchEvents() {
        // 监听所有Tab切换事件
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tabLink => {
            tabLink.addEventListener('shown.bs.tab', (event) => {
                const targetTab = event.target.getAttribute('data-bs-target');
                if (targetTab) {
                    const tabId = targetTab.replace('#', '');
                    this.highlightActiveModule(tabId);
                }
            });
        });

        // 初始化时高亮当前激活的Tab
        const activeTab = document.querySelector('.nav-link.active[data-bs-toggle="pill"]');
        if (activeTab) {
            const targetTab = activeTab.getAttribute('data-bs-target');
            if (targetTab) {
                const tabId = targetTab.replace('#', '');
                this.highlightActiveModule(tabId);
            }
        }
    }

    /**
     * 高亮当前激活的模块
     * @param {string} tabId - Tab的ID
     */
    highlightActiveModule(tabId) {
        console.log(`[WorkflowDiagramManager] 高亮模块: ${tabId}`);
        this.currentActiveTab = tabId;

        // 移除所有模块的激活状态
        document.querySelectorAll('.module-card').forEach(card => {
            card.classList.remove('active');
        });

        // 高亮对应的模块卡片
        const moduleCard = document.querySelector(`.module-card[data-tab="${tabId}"]`);
        if (moduleCard) {
            moduleCard.classList.add('active');
        }
    }

    /**
     * 导航到指定模块（Tab跳转）
     * @param {string} tabId - 要跳转的Tab ID
     */
    navigateToModule(tabId) {
        console.log(`[WorkflowDiagramManager] 跳转到模块: ${tabId}`);

        // 查找对应的导航链接
        const navLink = document.querySelector(`[data-bs-target="#${tabId}"]`);
        if (navLink) {
            // 使用Bootstrap的Tab API切换
            const tab = new bootstrap.Tab(navLink);
            tab.show();

            // 添加平滑滚动到顶部
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });

            // 显示提示信息
            if (typeof showNotification === 'function') {
                const moduleNames = {
                    'business-response': '商务应答',
                    'point-to-point': '点对点应答',
                    'tech-proposal': '技术方案',
                    'tender-management': '投标管理'
                };
                const moduleName = moduleNames[tabId] || tabId;
                showNotification(`已切换到 ${moduleName} 模块`, 'success');
            }
        } else {
            console.error(`[WorkflowDiagramManager] 找不到Tab: ${tabId}`);
        }
    }

    /**
     * 更新模块状态
     * @param {string} tabId - Tab ID
     * @param {string} status - 状态: 'not-started', 'in-progress', 'completed'
     */
    updateModuleStatus(tabId, status) {
        const moduleCard = document.querySelector(`.module-card[data-tab="${tabId}"]`);
        if (!moduleCard) return;

        // 移除所有状态类
        moduleCard.classList.remove('status-not-started', 'status-in-progress', 'status-completed');

        // 添加新状态类
        moduleCard.classList.add(`status-${status}`);

        // 更新状态文本
        const statusText = moduleCard.querySelector('.status-text');
        if (statusText) {
            const statusTexts = {
                'not-started': '未开始',
                'in-progress': '进行中',
                'completed': '已完成'
            };
            statusText.textContent = statusTexts[status] || '未开始';
        }

        console.log(`[WorkflowDiagramManager] 更新模块状态: ${tabId} -> ${status}`);
    }

    /**
     * 获取当前激活的Tab
     */
    getCurrentActiveTab() {
        return this.currentActiveTab;
    }

    /**
     * 销毁管理器（清理事件监听器）
     */
    destroy() {
        // 这里可以添加清理逻辑，如果需要的话
        this.initialized = false;
        console.log('[WorkflowDiagramManager] 管理器已销毁');
    }
}

// 创建全局实例
window.workflowDiagramManager = new WorkflowDiagramManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否在首页
    const homeTab = document.getElementById('home');
    if (homeTab) {
        console.log('[WorkflowDiagramManager] 检测到首页，准备初始化...');

        // 延迟初始化，确保DOM完全加载
        setTimeout(() => {
            window.workflowDiagramManager.initialize();
        }, 100);
    }
});

// 如果首页Tab被重新激活，确保管理器已初始化
document.addEventListener('DOMContentLoaded', function() {
    const homeNav = document.querySelector('[data-bs-target="#home"]');
    if (homeNav) {
        homeNav.addEventListener('shown.bs.tab', function() {
            if (!window.workflowDiagramManager.initialized) {
                console.log('[WorkflowDiagramManager] 首页Tab激活，初始化管理器');
                window.workflowDiagramManager.initialize();
            }
        });
    }
});
