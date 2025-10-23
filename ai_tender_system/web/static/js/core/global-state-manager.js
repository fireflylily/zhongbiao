/**
 * 全局状态管理器 - 单一数据源
 * 管理所有跨页面共享的状态
 *
 * 使用方式:
 * - 设置状态: window.globalState.setCompany('123', 'ABC公司')
 * - 获取状态: window.globalState.getCompany()
 * - 订阅变化: window.globalState.subscribe('company', (data) => { ... })
 * - 调试: window.globalState.debug()
 */
class GlobalStateManager {
    constructor() {
        // 状态存储
        this.state = {
            // 公司信息
            company: {
                id: null,
                name: null
            },

            // 项目信息
            project: {
                id: null,
                name: null
            },

            // HITL任务信息
            hitl: {
                taskId: null
            },

            // 文件管理（按类型分类）
            files: {
                originalTender: null,      // 原始招标文件
                technical: null,           // 技术需求文件
                business: null,            // 商务应答文件
                pointToPoint: null,        // 点对点应答文件
                techProposal: null         // 技术方案文件
            },

            // AI配置
            ai: {
                availableModels: [],       // 所有可用模型
                selectedModel: 'unicom-yuanjing'  // 当前选中模型
            }
        };

        // 监听器列表（观察者模式）
        this.listeners = {
            company: [],
            project: [],
            files: [],
            ai: [],
            hitl: []
        };

        console.log('[GlobalState] 全局状态管理器已初始化');
    }

    // ========================================
    // 公司管理
    // ========================================

    /**
     * 设置公司信息
     * @param {string} companyId - 公司ID
     * @param {string} companyName - 公司名称
     */
    setCompany(companyId, companyName) {
        this.state.company.id = companyId;
        this.state.company.name = companyName;
        this.notify('company', this.getCompany());
        console.log('[GlobalState] 公司信息已更新:', this.state.company);
    }

    /**
     * 获取公司信息
     * @returns {Object} {id, name}
     */
    getCompany() {
        return { ...this.state.company };
    }

    /**
     * 清空公司信息
     */
    clearCompany() {
        this.state.company.id = null;
        this.state.company.name = null;
        this.notify('company', this.getCompany());
        console.log('[GlobalState] 公司信息已清空');
    }

    // ========================================
    // 项目管理
    // ========================================

    /**
     * 设置项目信息
     * @param {string} projectId - 项目ID
     * @param {string} projectName - 项目名称
     */
    setProject(projectId, projectName) {
        this.state.project.id = projectId;
        this.state.project.name = projectName;
        this.notify('project', this.getProject());
        console.log('[GlobalState] 项目信息已更新:', this.state.project);
    }

    /**
     * 获取项目信息
     * @returns {Object} {id, name}
     */
    getProject() {
        return { ...this.state.project };
    }

    /**
     * 清空项目信息
     */
    clearProject() {
        this.state.project.id = null;
        this.state.project.name = null;
        this.notify('project', this.getProject());
        console.log('[GlobalState] 项目信息已清空');
    }

    // ========================================
    // 文件管理（统一接口）
    // ========================================

    /**
     * 设置文件信息
     * @param {string} fileType - 文件类型：originalTender, technical, business, pointToPoint, techProposal
     * @param {Object} fileInfo - 文件信息对象
     * @param {string} fileInfo.fileName - 文件名
     * @param {string} fileInfo.filePath - 文件路径
     * @param {string} fileInfo.fileUrl - 文件URL
     * @param {number} fileInfo.fileSize - 文件大小（字节）
     */
    setFile(fileType, fileInfo) {
        if (!this.state.files.hasOwnProperty(fileType)) {
            console.error(`[GlobalState] 无效的文件类型: ${fileType}`);
            return;
        }

        this.state.files[fileType] = {
            fileName: fileInfo.fileName || null,
            filePath: fileInfo.filePath || null,
            fileUrl: fileInfo.fileUrl || null,
            fileSize: fileInfo.fileSize || null,
            uploadedAt: new Date().toISOString()
        };

        this.notify('files', { type: fileType, data: this.state.files[fileType] });
        console.log(`[GlobalState] ${fileType} 文件信息已更新:`, this.state.files[fileType]);
    }

    /**
     * 获取文件信息
     * @param {string} fileType - 文件类型
     * @returns {Object|null} 文件信息对象
     */
    getFile(fileType) {
        return this.state.files[fileType] ? { ...this.state.files[fileType] } : null;
    }

    /**
     * 清空指定文件
     * @param {string} fileType - 文件类型
     */
    clearFile(fileType) {
        if (!this.state.files.hasOwnProperty(fileType)) {
            console.error(`[GlobalState] 无效的文件类型: ${fileType}`);
            return;
        }
        this.state.files[fileType] = null;
        this.notify('files', { type: fileType, data: null });
        console.log(`[GlobalState] ${fileType} 文件信息已清空`);
    }

    /**
     * 清空所有文件
     */
    clearAllFiles() {
        Object.keys(this.state.files).forEach(key => {
            this.state.files[key] = null;
        });
        this.notify('files', { type: 'all', data: null });
        console.log('[GlobalState] 所有文件信息已清空');
    }

    // ========================================
    // AI模型管理
    // ========================================

    /**
     * 设置可用AI模型列表
     * @param {Array} models - 模型列表
     */
    setAvailableModels(models) {
        this.state.ai.availableModels = models;
        this.notify('ai', { type: 'models', data: models });
        console.log(`[GlobalState] AI模型列表已更新，共 ${models.length} 个模型`);
    }

    /**
     * 获取可用AI模型列表
     * @returns {Array} 模型列表
     */
    getAvailableModels() {
        return [...this.state.ai.availableModels];
    }

    /**
     * 设置选中的AI模型
     * @param {string} modelName - 模型名称
     */
    setSelectedModel(modelName) {
        this.state.ai.selectedModel = modelName;
        this.notify('ai', { type: 'selectedModel', data: modelName });
        console.log(`[GlobalState] 已选择AI模型: ${modelName}`);
    }

    /**
     * 获取选中的AI模型
     * @returns {string} 模型名称
     */
    getSelectedModel() {
        return this.state.ai.selectedModel;
    }

    // ========================================
    // HITL任务管理
    // ========================================

    /**
     * 设置HITL任务ID
     * @param {string} taskId - 任务ID
     */
    setHitlTaskId(taskId) {
        this.state.hitl.taskId = taskId;
        this.notify('hitl', { taskId });
        console.log(`[GlobalState] HITL任务ID已设置: ${taskId}`);
    }

    /**
     * 获取HITL任务ID
     * @returns {string|null} 任务ID
     */
    getHitlTaskId() {
        return this.state.hitl.taskId;
    }

    /**
     * 清空HITL任务ID
     */
    clearHitlTaskId() {
        this.state.hitl.taskId = null;
        this.notify('hitl', { taskId: null });
        console.log('[GlobalState] HITL任务ID已清空');
    }

    // ========================================
    // 观察者模式（订阅/通知）
    // ========================================

    /**
     * 订阅状态变化
     * @param {string} category - 类别：company, project, files, ai, hitl
     * @param {Function} callback - 回调函数
     * @returns {Function} - 取消订阅函数
     */
    subscribe(category, callback) {
        if (!this.listeners[category]) {
            console.error(`[GlobalState] 无效的订阅类别: ${category}`);
            return () => {};
        }

        this.listeners[category].push(callback);
        console.log(`[GlobalState] 新订阅: ${category}, 当前订阅数: ${this.listeners[category].length}`);

        // 返回取消订阅函数
        return () => {
            const index = this.listeners[category].indexOf(callback);
            if (index > -1) {
                this.listeners[category].splice(index, 1);
                console.log(`[GlobalState] 已取消订阅: ${category}`);
            }
        };
    }

    /**
     * 通知所有订阅者
     * @param {string} category - 类别
     * @param {*} data - 数据
     */
    notify(category, data) {
        if (this.listeners[category]) {
            this.listeners[category].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[GlobalState] 监听器执行错误 (${category}):`, error);
                }
            });
        }
    }

    // ========================================
    // 批量操作
    // ========================================

    /**
     * 批量设置状态（用于从HITL页面跳转）
     * @param {Object} data - 批量数据
     * @param {Object} data.company - 公司信息 {id, name}
     * @param {Object} data.project - 项目信息 {id, name}
     * @param {Object} data.files - 文件信息 {technical: {...}, business: {...}}
     * @param {string} data.hitlTaskId - HITL任务ID
     */
    setBulk(data) {
        let updated = [];

        if (data.company) {
            this.setCompany(data.company.id, data.company.name);
            updated.push('company');
        }

        if (data.project) {
            this.setProject(data.project.id, data.project.name);
            updated.push('project');
        }

        if (data.files) {
            Object.keys(data.files).forEach(fileType => {
                if (data.files[fileType]) {
                    this.setFile(fileType, data.files[fileType]);
                }
            });
            updated.push('files');
        }

        if (data.hitlTaskId) {
            this.setHitlTaskId(data.hitlTaskId);
            updated.push('hitl');
        }

        console.log('[GlobalState] 批量更新完成:', updated.join(', '));
    }

    /**
     * 清空所有状态（退出项目时使用）
     */
    clearAll() {
        this.clearCompany();
        this.clearProject();
        this.clearAllFiles();
        this.clearHitlTaskId();
        console.log('[GlobalState] 所有状态已清空');
    }

    // ========================================
    // 兼容层（用于平滑迁移）
    // ========================================

    /**
     * 创建兼容层，模拟旧的 projectDataBridge API
     * @returns {Object} 兼容对象
     */
    createLegacyBridge() {
        const self = this;
        return {
            // 公司信息
            get companyId() {
                return self.state.company.id;
            },
            set companyId(value) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.companyId，请迁移到 globalState.setCompany()');
                if (self.state.company.id !== value) {
                    self.setCompany(value, self.state.company.name);
                }
            },

            get companyName() {
                return self.state.company.name;
            },
            set companyName(value) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.companyName，请迁移到 globalState.setCompany()');
                if (self.state.company.name !== value) {
                    self.setCompany(self.state.company.id, value);
                }
            },

            // 项目信息
            get projectId() {
                return self.state.project.id;
            },
            set projectId(value) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.projectId，请迁移到 globalState.setProject()');
                if (self.state.project.id !== value) {
                    self.setProject(value, self.state.project.name);
                }
            },

            get projectName() {
                return self.state.project.name;
            },
            set projectName(value) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.projectName，请迁移到 globalState.setProject()');
                if (self.state.project.name !== value) {
                    self.setProject(self.state.project.id, value);
                }
            },

            // HITL任务ID
            get hitlTaskId() {
                return self.state.hitl.taskId;
            },
            set hitlTaskId(value) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.hitlTaskId，请迁移到 globalState.setHitlTaskId()');
                self.setHitlTaskId(value);
            },

            // 技术需求文件
            technicalFile: {
                get taskId() {
                    return self.state.hitl.taskId;
                },
                get fileName() {
                    return self.state.files.technical?.fileName;
                },
                get fileSize() {
                    return self.state.files.technical?.fileSize;
                },
                get fileUrl() {
                    return self.state.files.technical?.fileUrl;
                }
            },

            // 旧方法
            setTechnicalFile(taskId, fileName, fileSize, fileUrl) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.setTechnicalFile()，请迁移到 globalState.setFile()');
                self.setFile('technical', { fileName, fileSize, fileUrl });
                self.setHitlTaskId(taskId);
            },

            getTechnicalFile() {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.getTechnicalFile()，请迁移到 globalState.getFile()');
                return self.getFile('technical');
            },

            clearTechnicalFile() {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.clearTechnicalFile()，请迁移到 globalState.clearFile()');
                self.clearFile('technical');
            },

            setFileInfo(fileType, fileData) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.setFileInfo()，请迁移到 globalState.setFile()');
                self.setFile(fileType, fileData);
            },

            getFileInfo(fileType) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.getFileInfo()，请迁移到 globalState.getFile()');
                return self.getFile(fileType);
            },

            // AI模型
            aiModels: {
                get currentModels() {
                    return self.state.ai.availableModels;
                },
                get selectedModel() {
                    return self.state.ai.selectedModel;
                }
            },

            setModels(models) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.setModels()，请迁移到 globalState.setAvailableModels()');
                self.setAvailableModels(models);
            },

            getModels() {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.getModels()，请迁移到 globalState.getAvailableModels()');
                return self.getAvailableModels();
            },

            setSelectedModel(modelName) {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.setSelectedModel()，请迁移到 globalState.setSelectedModel()');
                self.setSelectedModel(modelName);
            },

            getSelectedModel() {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.getSelectedModel()，请迁移到 globalState.getSelectedModel()');
                return self.getSelectedModel();
            },

            // 清空所有
            clearAll() {
                console.warn('[GlobalState] 使用了废弃的 projectDataBridge.clearAll()，请迁移到 globalState.clearAll()');
                self.clearAll();
            },

            // 文件对象（用于向后兼容）
            files: {
                get originalTender() {
                    return self.getFile('originalTender');
                },
                get technical() {
                    return self.getFile('technical');
                },
                get business() {
                    return self.getFile('business');
                },
                get pointToPoint() {
                    return self.getFile('pointToPoint');
                },
                get techProposal() {
                    return self.getFile('techProposal');
                }
            }
        };
    }

    // ========================================
    // 调试工具
    // ========================================

    /**
     * 获取完整状态快照（用于调试）
     * @returns {Object} 状态快照
     */
    getSnapshot() {
        return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * 打印当前状态（用于调试）
     */
    debug() {
        console.group('🔍 [GlobalState] 当前状态快照');
        console.log('📌 公司:', this.state.company);
        console.log('📌 项目:', this.state.project);
        console.log('📌 HITL任务:', this.state.hitl);
        console.log('📌 文件:', this.state.files);
        console.log('📌 AI配置:', this.state.ai);
        console.log('📊 订阅统计:', {
            company: this.listeners.company.length,
            project: this.listeners.project.length,
            files: this.listeners.files.length,
            ai: this.listeners.ai.length,
            hitl: this.listeners.hitl.length
        });
        console.groupEnd();
    }
}

// ========================================
// 初始化全局实例
// ========================================
if (!window.globalState) {
    window.globalState = new GlobalStateManager();

    // 创建兼容层（用于平滑迁移）
    window.projectDataBridge = window.globalState.createLegacyBridge();

    console.log('✅ [GlobalState] 全局状态管理器已初始化');
    console.log('✅ [GlobalState] 兼容层已创建 (window.projectDataBridge)');
} else {
    console.warn('[GlobalState] 全局状态管理器已存在，跳过重复初始化');
}
