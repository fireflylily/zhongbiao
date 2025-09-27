/**
 * 进度条管理器
 * 解决 index.html 中多个进度条动画定时器泄漏问题
 *
 * 原问题定位：
 * - 行1943: 点对点上传进度条 setInterval
 * - 行2104: 标书生成进度条 setInterval
 * - 行2477: 招标文件处理进度条 setInterval
 *
 * 解决方案：统一管理所有进度条，避免重复创建和泄漏
 */

class ProgressManager {
    constructor() {
        this.activeProgresses = new Map(); // 存储所有活动的进度条
        this.defaultConfig = {
            updateInterval: 100, // 默认更新间隔100ms
            animationDuration: 2000, // 默认动画时长2秒
            maxProgress: 90, // 最大进度(避免100%时卡住)
            autoHideDelay: 1000 // 完成后自动隐藏延迟
        };

        console.log('[ProgressManager] 进度条管理器初始化完成');
    }

    /**
     * 创建新的进度条动画
     * @param {string} progressBarId 进度条元素ID
     * @param {Object} config 配置选项
     * @returns {string} 进度条任务ID
     */
    startProgress(progressBarId, config = {}) {
        // 合并配置
        const finalConfig = { ...this.defaultConfig, ...config };

        // 如果该进度条已存在，先清理
        this.stopProgress(progressBarId);

        const progressBar = document.querySelector(progressBarId);
        if (!progressBar) {
            console.error(`[ProgressManager] 找不到进度条元素: ${progressBarId}`);
            return null;
        }

        // 显示进度条
        const progressContainer = progressBar.closest('.progress');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        let currentProgress = 0;
        const startTime = Date.now();

        // 使用定时器管理器创建动画定时器
        const timerId = window.timerManager.setInterval(() => {
            // 计算进度增量
            const elapsed = Date.now() - startTime;
            const progressIncrement = Math.random() * 15 + 5; // 5-20的随机增量

            currentProgress = Math.min(currentProgress + progressIncrement, finalConfig.maxProgress);

            // 更新进度条
            progressBar.style.width = `${currentProgress}%`;
            progressBar.textContent = `${Math.round(currentProgress)}%`;

            // 如果达到最大进度或超时，停止动画
            if (currentProgress >= finalConfig.maxProgress || elapsed > finalConfig.animationDuration) {
                this.pauseProgress(progressBarId);
            }
        }, finalConfig.updateInterval, `进度条动画-${progressBarId}`);

        // 记录进度条状态
        this.activeProgresses.set(progressBarId, {
            timerId,
            progressBar,
            progressContainer,
            currentProgress,
            config: finalConfig,
            startTime,
            status: 'running'
        });

        console.log(`[ProgressManager] 启动进度条: ${progressBarId}`);
        return progressBarId;
    }

    /**
     * 暂停进度条动画(保持当前进度)
     * @param {string} progressBarId 进度条ID
     */
    pauseProgress(progressBarId) {
        const progress = this.activeProgresses.get(progressBarId);
        if (progress && progress.status === 'running') {
            window.timerManager.clearInterval(progress.timerId);
            progress.status = 'paused';
            console.log(`[ProgressManager] 暂停进度条: ${progressBarId} (${progress.currentProgress}%)`);
        }
    }

    /**
     * 完成进度条(设置为100%)
     * @param {string} progressBarId 进度条ID
     * @param {boolean} autoHide 是否自动隐藏
     */
    completeProgress(progressBarId, autoHide = true) {
        const progress = this.activeProgresses.get(progressBarId);
        if (!progress) return;

        // 停止动画定时器
        if (progress.timerId) {
            window.timerManager.clearInterval(progress.timerId);
        }

        // 设置为100%
        progress.progressBar.style.width = '100%';
        progress.progressBar.textContent = '100%';
        progress.currentProgress = 100;
        progress.status = 'completed';

        console.log(`[ProgressManager] 完成进度条: ${progressBarId}`);

        // 自动隐藏
        if (autoHide) {
            window.timerManager.setTimeout(() => {
                this.hideProgress(progressBarId);
            }, progress.config.autoHideDelay, `隐藏进度条-${progressBarId}`);
        }
    }

    /**
     * 停止并隐藏进度条
     * @param {string} progressBarId 进度条ID
     */
    stopProgress(progressBarId) {
        const progress = this.activeProgresses.get(progressBarId);
        if (!progress) return;

        // 清理定时器
        if (progress.timerId) {
            window.timerManager.clearInterval(progress.timerId);
        }

        // 隐藏进度条
        this.hideProgress(progressBarId);

        // 从映射中移除
        this.activeProgresses.delete(progressBarId);

        console.log(`[ProgressManager] 停止进度条: ${progressBarId}`);
    }

    /**
     * 隐藏进度条UI
     * @param {string} progressBarId 进度条ID
     */
    hideProgress(progressBarId) {
        const progress = this.activeProgresses.get(progressBarId);
        if (!progress) return;

        // 隐藏进度条容器
        if (progress.progressContainer) {
            progress.progressContainer.style.display = 'none';
        }

        // 重置进度条
        progress.progressBar.style.width = '0%';
        progress.progressBar.textContent = '0%';
    }

    /**
     * 设置特定进度值
     * @param {string} progressBarId 进度条ID
     * @param {number} percentage 进度百分比 (0-100)
     */
    setProgress(progressBarId, percentage) {
        const progress = this.activeProgresses.get(progressBarId);
        if (!progress) return;

        const clampedPercentage = Math.max(0, Math.min(100, percentage));
        progress.progressBar.style.width = `${clampedPercentage}%`;
        progress.progressBar.textContent = `${Math.round(clampedPercentage)}%`;
        progress.currentProgress = clampedPercentage;

        console.log(`[ProgressManager] 设置进度条 ${progressBarId}: ${clampedPercentage}%`);
    }

    /**
     * 清理所有进度条
     */
    clearAll() {
        for (const [progressBarId] of this.activeProgresses) {
            this.stopProgress(progressBarId);
        }
        console.log('[ProgressManager] 清理所有进度条');
    }

    /**
     * 获取进度条状态
     * @param {string} progressBarId 进度条ID
     * @returns {Object|null} 进度条状态
     */
    getProgressStatus(progressBarId) {
        const progress = this.activeProgresses.get(progressBarId);
        if (!progress) return null;

        return {
            id: progressBarId,
            progress: progress.currentProgress,
            status: progress.status,
            elapsed: Date.now() - progress.startTime
        };
    }

    /**
     * 获取所有活动进度条状态
     * @returns {Array} 所有进度条状态
     */
    getAllProgressStatus() {
        const result = [];
        for (const [id] of this.activeProgresses) {
            result.push(this.getProgressStatus(id));
        }
        return result;
    }

    /**
     * 预设的进度条配置
     */
    static getPresetConfigs() {
        return {
            // 文件上传配置
            upload: {
                updateInterval: 50,
                animationDuration: 3000,
                maxProgress: 95,
                autoHideDelay: 1500
            },
            // 数据处理配置
            processing: {
                updateInterval: 100,
                animationDuration: 5000,
                maxProgress: 90,
                autoHideDelay: 2000
            },
            // 快速操作配置
            quick: {
                updateInterval: 80,
                animationDuration: 1500,
                maxProgress: 92,
                autoHideDelay: 800
            }
        };
    }
}

// 创建全局进度条管理器实例
window.progressManager = new ProgressManager();

// 页面卸载时清理所有进度条
window.addEventListener('beforeunload', () => {
    window.progressManager.clearAll();
});

console.log('[ProgressManager] 全局进度条管理器已就绪');