/**
 * HITL 文件加载器 - 统一处理从 HITL 页面加载文件的逻辑
 * 用于商务应答、点对点应答等多个模块
 */
class HITLFileLoader {
    constructor(config) {
        this.fileType = config.fileType;  // 'business', 'technical', 'pointToPoint' 等
        this.fileInfoElementId = config.fileInfoElementId;  // 显示文件信息的元素ID
        this.uploadAreaId = config.uploadAreaId;  // 上传区域的元素ID（需要隐藏）
        this.onFileLoaded = config.onFileLoaded || null;  // 加载完成回调
        this.debug = config.debug || false;  // 是否启用调试日志
    }

    /**
     * 从 GlobalStateManager 加载文件信息并显示
     * @returns {boolean} 是否成功加载文件
     */
    load() {
        this.log('开始从HITL加载数据');

        if (!window.globalState) {
            console.warn(`[HITLFileLoader:${this.fileType}] globalState 未定义`);
            return false;
        }

        // 从 GlobalStateManager 获取文件信息
        const fileData = window.globalState.getFile(this.fileType);

        if (!fileData || !fileData.fileName) {
            this.log('未找到文件信息', fileData);
            return false;
        }

        this.log('找到文件信息:', fileData);

        // 显示文件信息
        const success = this.displayFileInfo(fileData);

        if (success) {
            // 隐藏上传区域
            this.hideUploadArea();

            // 触发回调
            if (this.onFileLoaded) {
                this.onFileLoaded(fileData);
            }
        }

        return success;
    }

    /**
     * 显示文件信息
     */
    displayFileInfo(fileData) {
        const fileInfoElement = document.getElementById(this.fileInfoElementId);

        if (!fileInfoElement) {
            console.error(`[HITLFileLoader:${this.fileType}] 未找到元素: ${this.fileInfoElementId}`);
            return false;
        }

        // 计算文件大小
        let sizeText = '';
        if (fileData.fileSize) {
            const sizeKB = (parseInt(fileData.fileSize) / 1024).toFixed(2);
            sizeText = ` <span class="text-muted">(${sizeKB} KB)</span>`;
        }

        // 设置文件信息HTML
        fileInfoElement.innerHTML = `
            <div class="alert alert-success py-2 d-flex align-items-center">
                <i class="bi bi-file-earmark-text me-2"></i>
                <div>
                    已选择文件：<strong>${this.escapeHtml(fileData.fileName)}</strong>${sizeText}
                    <span class="badge bg-success ms-2">已从投标项目加载</span>
                </div>
            </div>
        `;

        // 移除隐藏类
        fileInfoElement.classList.remove('d-none');

        this.log('文件信息已显示');
        return true;
    }

    /**
     * 隐藏上传区域
     */
    hideUploadArea() {
        if (!this.uploadAreaId) return;

        const uploadArea = document.getElementById(this.uploadAreaId);

        if (uploadArea) {
            uploadArea.classList.add('d-none');
            uploadArea.style.display = 'none';
            uploadArea.onclick = null;  // 移除点击事件
            uploadArea.style.pointerEvents = 'none';  // 禁用所有鼠标事件
            uploadArea.style.cursor = 'default';  // 改变鼠标样式
            this.log('已隐藏上传区域');
        }
    }

    /**
     * HTML 转义
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 调试日志
     */
    log(...args) {
        if (this.debug) {
            console.log(`[HITLFileLoader:${this.fileType}]`, ...args);
        }
    }
}

// 导出到全局
window.HITLFileLoader = HITLFileLoader;
