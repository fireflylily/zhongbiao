/**
 * tender-processing-step3 模块化主入口
 *
 * 这是简化的入口文件，用于逐步迁移到模块化架构
 * 当前版本：与原版tender-processing-step3-enhanced.js共存
 *
 * 依赖加载顺序:
 * 1. core/notification.js
 * 2. core/validation.js
 * 3. core/api-client.js
 * 4. core/global-state-manager.js
 * 5. tender-processing-step3/api/tender-api-extension.js
 * 6. tender-processing-step3/utils/formatter.js
 * 7. tender-processing-step3/config/eligibility-checklist.js
 * 8. tender-processing-step3/managers/*.js (本文件加载)
 *
 * 用法:
 * <script src="core/notification.js"></script>
 * <script src="core/validation.js"></script>
 * <script src="core/api-client.js"></script>
 * <script src="core/global-state-manager.js"></script>
 * <script src="tender-processing-step3/api/tender-api-extension.js"></script>
 * <script src="tender-processing-step3/utils/formatter.js"></script>
 * <script src="tender-processing-step3/config/eligibility-checklist.js"></script>
 * <script src="tender-processing-step3/managers/ChapterSelectorManager.js"></script>
 * <script src="tender-processing-step3/managers/DataSyncManager.js"></script>
 * <script src="tender-processing-step3/managers/RequirementsTableManager.js"></script>
 * <script src="tender-processing-step3/index.js"></script>
 */

(function() {
    'use strict';

    console.log('[Step3Modular] 开始加载模块化Step3');

    // ============================================
    // 依赖检查
    // ============================================

    const requiredDependencies = [
        { name: 'window.notifications', obj: window.notifications, desc: 'core/notification.js' },
        { name: 'window.validator', obj: window.validator, desc: 'core/validation.js' },
        { name: 'window.apiClient', obj: window.apiClient, desc: 'core/api-client.js' },
        { name: 'window.globalState', obj: window.globalState, desc: 'core/global-state-manager.js' },
        { name: 'ChapterSelectorManager', obj: window.ChapterSelectorManager || (typeof ChapterSelectorManager !== 'undefined' ? ChapterSelectorManager : null), desc: 'managers/ChapterSelectorManager.js' },
        { name: 'DataSyncManager', obj: window.DataSyncManager || (typeof DataSyncManager !== 'undefined' ? DataSyncManager : null), desc: 'managers/DataSyncManager.js' },
        { name: 'RequirementsTableManager', obj: window.RequirementsTableManager || (typeof RequirementsTableManager !== 'undefined' ? RequirementsTableManager : null), desc: 'managers/RequirementsTableManager.js' }
    ];

    const missingDeps = requiredDependencies.filter(dep => !dep.obj);

    if (missingDeps.length > 0) {
        console.error('[Step3Modular] ❌ 缺少必要依赖:');
        missingDeps.forEach(dep => {
            console.error(`  - ${dep.name} (${dep.desc})`);
        });
        console.error('[Step3Modular] 模块化加载失败，将继续使用原版step3-enhanced.js');
        return;
    }

    console.log('[Step3Modular] ✅ 所有依赖已加载');

    // ============================================
    // 初始化管理器实例
    // ============================================

    // 数据同步管理器（全局单例）
    window.dataSyncManager = new DataSyncManager();
    console.log('[Step3Modular] DataSyncManager 已初始化');

    // 需求表格管理器（全局单例）
    window.requirementsTableManager = new RequirementsTableManager('requirementsTableBody', {
        enableEdit: true,
        enableDelete: true,
        enableExport: true
    });
    console.log('[Step3Modular] RequirementsTableManager 已初始化');

    // 章节选择管理器（按需创建）
    window.chapterSelectors = {};

    /**
     * 获取或创建章节选择管理器
     * @param {string} type - 类型 ('response', 'technical')
     * @param {Object} config - 配置
     * @returns {ChapterSelectorManager}
     */
    window.getChapterSelector = function(type, config = {}) {
        if (!window.chapterSelectors[type]) {
            window.chapterSelectors[type] = new ChapterSelectorManager(type, config);
            console.log(`[Step3Modular] ChapterSelectorManager[${type}] 已创建`);
        }
        return window.chapterSelectors[type];
    };

    // ============================================
    // 向后兼容的全局函数
    // ============================================

    /**
     * 保存基本信息（向后兼容）
     */
    window.saveBasicInfo = async function() {
        return await window.dataSyncManager.saveBasicInfo();
    };

    /**
     * 保存并完成（向后兼容）
     */
    window.saveAndComplete = async function() {
        return await window.dataSyncManager.saveAndComplete();
    };

    /**
     * 显示章节选择（向后兼容）
     * @param {string} type - 类型 ('response', 'technical')
     */
    window.showChapterSelection = async function(type) {
        const configs = {
            'response': {
                prefix: 'inline',
                contentId: 'responseFileContent',
                selectionAreaId: 'inlineChapterSelectionArea',
                confirmBtnId: 'confirmInlineSaveResponseFileBtn',
                fileTypeName: '应答文件',
                apiSave: '/api/tender-processing/save-response-file',
                apiInfo: '/api/tender-processing/response-file-info'
            },
            'technical': {
                prefix: 'technical',
                contentId: 'technicalFileContent',
                selectionAreaId: 'technicalChapterSelectionArea',
                confirmBtnId: 'confirmTechnicalSaveBtn',
                fileTypeName: '技术需求',
                apiSave: '/api/tender-processing/save-technical-chapters',
                apiInfo: '/api/tender-processing/technical-file-info'
            }
        };

        const config = configs[type];
        if (!config) {
            console.error(`[Step3Modular] 未知的章节类型: ${type}`);
            return;
        }

        const selector = window.getChapterSelector(type, config);
        await selector.showChapterSelection();
    };

    /**
     * 隐藏章节选择（向后兼容）
     * @param {string} type - 类型
     */
    window.hideChapterSelection = function(type) {
        const selector = window.chapterSelectors[type];
        if (selector) {
            selector.hideChapterSelection();
        }
    };

    /**
     * 确认保存章节（向后兼容）
     * @param {string} type - 类型
     */
    window.confirmSave = async function(type) {
        const selector = window.chapterSelectors[type];
        if (selector) {
            await selector.confirmSave();
        } else {
            console.error(`[Step3Modular] ChapterSelector[${type}] 未初始化`);
        }
    };

    /**
     * 全选章节（向后兼容）
     * @param {string} type - 类型
     */
    window.selectAll = function(type) {
        const selector = window.chapterSelectors[type];
        if (selector) {
            selector.selectAll();
        }
    };

    /**
     * 全不选章节（向后兼容）
     * @param {string} type - 类型
     */
    window.unselectAll = function(type) {
        const selector = window.chapterSelectors[type];
        if (selector) {
            selector.unselectAll();
        }
    };

    /**
     * 按关键词选择章节（向后兼容）
     * @param {string} type - 类型
     * @param {string} keyword - 关键词
     */
    window.selectByKeyword = function(type, keyword) {
        const selector = window.chapterSelectors[type];
        if (selector) {
            selector.selectByKeyword(keyword);
        }
    };

    /**
     * 排除关键词章节（向后兼容）
     * @param {string} type - 类型
     * @param {string} keyword - 关键词
     */
    window.excludeByKeyword = function(type, keyword) {
        const selector = window.chapterSelectors[type];
        if (selector) {
            selector.excludeByKeyword(keyword);
        }
    };

    // ============================================
    // 事件监听
    // ============================================

    // 监听文件信息更新事件
    window.addEventListener('fileInfoUpdated', (e) => {
        console.log('[Step3Modular] 文件信息已更新:', e.detail);
        // 可以在这里触发UI刷新
    });

    // 监听需求编辑请求
    window.addEventListener('requirementEditRequested', (e) => {
        console.log('[Step3Modular] 需求编辑请求:', e.detail.requirement);
        // TODO: 实现编辑模态框
        window.notifications.info('编辑功能即将推出');
    });

    // 监听需求删除请求
    window.addEventListener('requirementDeleteRequested', async (e) => {
        console.log('[Step3Modular] 需求删除请求:', e.detail.requirementId);
        // TODO: 实现删除API调用
        window.notifications.info('删除功能即将推出');
    });

    // 监听章节预览请求
    window.addEventListener('chapterPreviewRequested', (e) => {
        console.log('[Step3Modular] 章节预览请求:', e.detail);
        // 调用原版的预览功能（如果存在）
        if (typeof showChapterPreviewModal !== 'undefined') {
            showChapterPreviewModal(e.detail.chapterId);
        } else {
            window.notifications.info('预览功能需要加载原版step3-enhanced.js');
        }
    });

    // ============================================
    // 功能标志
    // ============================================

    // 标记模块化版本已加载
    window.STEP3_MODULAR_LOADED = true;

    console.log('[Step3Modular] ✅ 模块化Step3已加载完成');
    console.log('[Step3Modular] 可用管理器:');
    console.log('  - window.dataSyncManager (DataSyncManager)');
    console.log('  - window.requirementsTableManager (RequirementsTableManager)');
    console.log('  - window.getChapterSelector(type) (ChapterSelectorManager工厂)');

    // 触发加载完成事件
    window.dispatchEvent(new CustomEvent('step3ModularLoaded', {
        detail: {
            version: '1.0.0',
            timestamp: new Date().toISOString()
        }
    }));

})();
