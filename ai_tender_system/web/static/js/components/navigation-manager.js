/**
 * 导航管理器模块
 * 负责处理侧边栏导航的状态管理和交互逻辑
 */

const NavigationManager = {
    /**
     * 切换到指定的选项卡
     * @param {string} tabId - 选项卡ID（不含#）
     */
    switchToTab(tabId) {
        console.log('[NavigationManager] 切换到Tab:', tabId);

        // 移除所有导航项的活跃状态（包括一级和二级菜单）
        document.querySelectorAll('.list-group-item-action[data-bs-toggle="pill"]').forEach(item => {
            item.classList.remove('active');
        });

        // 移除所有tab内容的活跃状态
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
        });

        // 激活指定的导航项和选项卡
        const navItem = document.querySelector(`[data-bs-target="#${tabId}"]`);
        const tabPane = document.querySelector(`#${tabId}`);

        if (navItem && tabPane) {
            navItem.classList.add('active');
            tabPane.classList.add('show', 'active');
            console.log('[NavigationManager] 已激活Tab:', tabId);
        } else {
            console.warn('[NavigationManager] 未找到Tab:', tabId);
        }
    },

    /**
     * 初始化导航状态管理
     * 确保同一时间只有一个导航项处于激活状态
     */
    initNavigationManager() {
        console.log('[NavigationManager] 初始化导航状态管理器');

        // 获取所有导航链接（一级和二级）
        const allNavLinks = document.querySelectorAll('.list-group-item-action[data-bs-toggle="pill"]');

        allNavLinks.forEach(navLink => {
            // 点击事件：清除其他导航项的active状态
            navLink.addEventListener('click', function(e) {
                // 清除所有导航项的active状态
                allNavLinks.forEach(link => {
                    link.classList.remove('active');
                });

                // 设置当前点击的导航项为active
                this.classList.add('active');

                console.log('[NavigationManager] 已激活:', this.getAttribute('data-bs-target'));
            });

            // 监听Bootstrap Tab显示事件（确保状态同步）
            navLink.addEventListener('shown.bs.tab', function(event) {
                // 再次确保只有当前项是active
                allNavLinks.forEach(link => {
                    if (link !== event.target) {
                        link.classList.remove('active');
                    }
                });

                console.log('[NavigationManager] Tab已显示:', this.getAttribute('data-bs-target'));
            });
        });

        // 确保知识库管理折叠菜单本身不会被标记为active
        const knowledgeToggle = document.querySelector('[data-bs-target="#knowledgeSubmenu"]');
        if (knowledgeToggle) {
            knowledgeToggle.addEventListener('click', function(e) {
                // 移除自身的active状态（它只是折叠触发器）
                this.classList.remove('active');
            });
        }

        console.log('[NavigationManager] 导航状态管理器初始化完成');
    },

    /**
     * 侧边栏切换功能 - 适配响应式网格布局
     */
    initSidebarToggle() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (!sidebarToggle) {
            console.log('[NavigationManager] 未找到侧边栏切换按钮');
            return;
        }

        sidebarToggle.addEventListener('click', function() {
            const sidebarCol = document.querySelector('.col-lg-3.col-md-4');
            const contentCol = document.querySelector('.col-lg-9.col-md-8');

            if (window.innerWidth <= 768) {
                // 移动端：使用显示/隐藏
                sidebarCol.classList.toggle('d-none');
            } else {
                // 桌面端：调整网格比例
                if (sidebarCol.classList.contains('col-lg-1')) {
                    // 展开状态
                    sidebarCol.className = 'col-lg-3 col-md-4 p-0';
                    contentCol.className = 'col-lg-9 col-md-8 app-main-content';
                } else {
                    // 收缩状态
                    sidebarCol.className = 'col-lg-1 col-md-2 p-0';
                    contentCol.className = 'col-lg-11 col-md-10 app-main-content';
                }
            }
        });

        // 移动端点击其他区域关闭侧边栏
        document.addEventListener('click', function(e) {
            const sidebarCol = document.querySelector('.col-lg-3.col-md-4');
            const toggle = document.getElementById('sidebarToggle');

            if (window.innerWidth <= 768 &&
                sidebarCol &&
                !sidebarCol.classList.contains('d-none') &&
                !sidebarCol.contains(e.target) &&
                toggle &&
                !toggle.contains(e.target)) {
                sidebarCol.classList.add('d-none');
            }
        });

        console.log('[NavigationManager] 侧边栏切换功能已初始化');
    },

    /**
     * 初始化导航管理器
     */
    init() {
        console.log('[NavigationManager] 正在初始化...');

        // 初始化导航状态管理
        this.initNavigationManager();

        // 初始化侧边栏切换功能
        this.initSidebarToggle();

        console.log('[NavigationManager] 初始化完成');
    }
};

// 暴露到全局作用域，供其他模块使用
window.NavigationManager = NavigationManager;

// 兼容性：暴露 switchToTab 为全局函数（用于旧代码兼容）
window.switchToTab = function(tabId) {
    NavigationManager.switchToTab(tabId);
};

console.log('[NavigationManager] 导航管理器模块已加载');
