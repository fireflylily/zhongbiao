/**
 * 定时器统一管理器
 * 解决 index.html 页面"死机"问题
 *
 * 问题原因：多个 setInterval/setTimeout 未正确清理导致资源泄漏
 * 解决方案：统一管理所有定时器，确保正确清理
 */

class TimerManager {
    constructor() {
        this.timers = new Map(); // 存储所有活动定时器
        this.intervals = new Map(); // 存储所有活动间隔定时器
        this.nextId = 1; // 定时器ID生成器

        // 监听页面卸载事件，自动清理所有定时器
        this.setupPageUnloadHandler();

        console.log('[TimerManager] 定时器管理器初始化完成');
    }

    /**
     * 创建超时定时器 (setTimeout 的封装)
     * @param {Function} callback 回调函数
     * @param {number} delay 延迟时间(毫秒)
     * @param {string} description 定时器描述(用于调试)
     * @returns {number} 定时器ID
     */
    setTimeout(callback, delay, description = '') {
        const id = this.nextId++;
        const timerId = setTimeout(() => {
            try {
                callback();
            } catch (error) {
                console.error(`[TimerManager] 定时器执行错误 [${description}]:`, error);
            } finally {
                // 执行完成后自动清理
                this.timers.delete(id);
            }
        }, delay);

        this.timers.set(id, {
            id: timerId,
            type: 'timeout',
            description,
            createdAt: new Date(),
            delay
        });

        console.log(`[TimerManager] 创建超时定时器 #${id}: ${description} (${delay}ms)`);
        return id;
    }

    /**
     * 创建间隔定时器 (setInterval 的封装)
     * @param {Function} callback 回调函数
     * @param {number} interval 间隔时间(毫秒)
     * @param {string} description 定时器描述
     * @param {number} maxExecutions 最大执行次数(0表示无限制)
     * @returns {number} 定时器ID
     */
    setInterval(callback, interval, description = '', maxExecutions = 0) {
        const id = this.nextId++;
        let executionCount = 0;

        const timerId = setInterval(() => {
            try {
                executionCount++;
                callback();

                // 检查是否达到最大执行次数
                if (maxExecutions > 0 && executionCount >= maxExecutions) {
                    this.clearInterval(id);
                    console.log(`[TimerManager] 定时器 #${id} 达到最大执行次数 (${maxExecutions})`);
                }
            } catch (error) {
                console.error(`[TimerManager] 间隔定时器执行错误 [${description}]:`, error);
                // 发生错误时清理定时器，防止继续出错
                this.clearInterval(id);
            }
        }, interval);

        this.intervals.set(id, {
            id: timerId,
            type: 'interval',
            description,
            createdAt: new Date(),
            interval,
            maxExecutions,
            executionCount: 0
        });

        console.log(`[TimerManager] 创建间隔定时器 #${id}: ${description} (${interval}ms${maxExecutions > 0 ? `, 最大${maxExecutions}次` : ''})`);
        return id;
    }

    /**
     * 清除超时定时器
     * @param {number} id 定时器ID
     */
    clearTimeout(id) {
        const timer = this.timers.get(id);
        if (timer) {
            clearTimeout(timer.id);
            this.timers.delete(id);
            console.log(`[TimerManager] 清除超时定时器 #${id}: ${timer.description}`);
        }
    }

    /**
     * 清除间隔定时器
     * @param {number} id 定时器ID
     */
    clearInterval(id) {
        const timer = this.intervals.get(id);
        if (timer) {
            clearInterval(timer.id);
            this.intervals.delete(id);
            console.log(`[TimerManager] 清除间隔定时器 #${id}: ${timer.description}`);
        }
    }

    /**
     * 清除所有定时器
     */
    clearAll() {
        // 清除所有超时定时器
        for (const [id, timer] of this.timers) {
            clearTimeout(timer.id);
            console.log(`[TimerManager] 强制清除超时定时器 #${id}: ${timer.description}`);
        }
        this.timers.clear();

        // 清除所有间隔定时器
        for (const [id, timer] of this.intervals) {
            clearInterval(timer.id);
            console.log(`[TimerManager] 强制清除间隔定时器 #${id}: ${timer.description}`);
        }
        this.intervals.clear();

        console.log('[TimerManager] 所有定时器已清理');
    }

    /**
     * 获取当前活动定时器数量
     * @returns {Object} 定时器统计信息
     */
    getStats() {
        return {
            timeouts: this.timers.size,
            intervals: this.intervals.size,
            total: this.timers.size + this.intervals.size
        };
    }

    /**
     * 获取所有活动定时器详情(用于调试)
     * @returns {Array} 定时器详情列表
     */
    getActiveTimers() {
        const result = [];

        for (const [id, timer] of this.timers) {
            result.push({
                id,
                type: timer.type,
                description: timer.description,
                createdAt: timer.createdAt,
                age: Date.now() - timer.createdAt.getTime()
            });
        }

        for (const [id, timer] of this.intervals) {
            result.push({
                id,
                type: timer.type,
                description: timer.description,
                createdAt: timer.createdAt,
                age: Date.now() - timer.createdAt.getTime(),
                executionCount: timer.executionCount
            });
        }

        return result;
    }

    /**
     * 设置页面卸载事件处理器
     */
    setupPageUnloadHandler() {
        // 页面卸载前清理所有定时器
        window.addEventListener('beforeunload', () => {
            console.log('[TimerManager] 页面卸载，清理所有定时器');
            this.clearAll();
        });

        // 页面隐藏时也清理定时器(移动端场景)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('[TimerManager] 页面隐藏，清理所有定时器');
                this.clearAll();
            }
        });
    }

    /**
     * 监控定时器使用情况，超过阈值时警告
     * @param {number} maxTimers 最大定时器数量阈值
     */
    startMonitoring(maxTimers = 20) {
        this.setInterval(() => {
            const stats = this.getStats();
            if (stats.total > maxTimers) {
                console.warn(`[TimerManager] 警告：当前活动定时器数量过多 (${stats.total}个)，可能存在内存泄漏！`);
                console.log('[TimerManager] 活动定时器详情:', this.getActiveTimers());
            }
        }, 10000, '定时器监控', 0); // 每10秒检查一次
    }
}

// 创建全局定时器管理器实例
window.timerManager = new TimerManager();

// 开始监控定时器使用情况
window.timerManager.startMonitoring(15); // 超过15个定时器时警告

console.log('[TimerManager] 全局定时器管理器已就绪');