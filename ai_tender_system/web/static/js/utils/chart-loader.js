/**
 * Chart.js 懒加载器
 * 按需加载 Chart.js，避免初始加载阻塞
 *
 * 使用方法:
 * const chart = await ChartLoader.create(ctx, config);
 */

const ChartLoader = {
    loaded: false,
    loading: false,
    chartClass: null,

    /**
     * 加载 Chart.js 库
     * @returns {Promise<object>} Chart类
     */
    async load() {
        // 如果已加载，直接返回
        if (this.loaded && this.chartClass) {
            return Promise.resolve(this.chartClass);
        }

        // 如果正在加载，等待加载完成
        if (this.loading) {
            return new Promise((resolve) => {
                const check = setInterval(() => {
                    if (this.loaded && this.chartClass) {
                        clearInterval(check);
                        resolve(this.chartClass);
                    }
                }, 50);
            });
        }

        this.loading = true;
        console.log('[ChartLoader] 开始加载 Chart.js...');

        try {
            // 动态导入 Chart.js
            const script = document.createElement('script');
            script.src = '/static/vendor/chart.js/chart.umd.min.js';

            await new Promise((resolve, reject) => {
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });

            // Chart.js 加载后应该在 window.Chart
            if (typeof window.Chart !== 'undefined') {
                this.chartClass = window.Chart;
                this.loaded = true;
                this.loading = false;
                console.log('[ChartLoader] ✅ Chart.js 加载完成');
                return this.chartClass;
            } else {
                throw new Error('Chart.js 加载失败，全局对象未找到');
            }

        } catch (error) {
            this.loading = false;
            console.error('[ChartLoader] ❌ Chart.js 加载失败:', error);
            throw error;
        }
    },

    /**
     * 创建图表实例
     * @param {CanvasRenderingContext2D|HTMLCanvasElement} ctx - 画布上下文或元素
     * @param {object} config - Chart.js配置对象
     * @returns {Promise<object>} Chart实例
     */
    async create(ctx, config) {
        try {
            const Chart = await this.load();

            console.log('[ChartLoader] 创建图表实例');
            const chart = new Chart(ctx, config);

            return chart;

        } catch (error) {
            console.error('[ChartLoader] 图表创建失败:', error);
            throw error;
        }
    },

    /**
     * 销毁图表实例
     * @param {object} chart - Chart实例
     */
    destroy(chart) {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
            console.log('[ChartLoader] 图表已销毁');
        }
    },

    /**
     * 创建常用图表类型的快捷方法
     */

    /**
     * 创建柱状图
     * @param {string} canvasId - Canvas元素ID
     * @param {object} data - 数据对象 {labels: [], datasets: []}
     * @param {object} options - 可选配置
     * @returns {Promise<object>} Chart实例
     */
    async createBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            throw new Error(`Canvas元素未找到: ${canvasId}`);
        }

        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                ...options
            }
        };

        return this.create(ctx, config);
    },

    /**
     * 创建折线图
     * @param {string} canvasId - Canvas元素ID
     * @param {object} data - 数据对象
     * @param {object} options - 可选配置
     * @returns {Promise<object>} Chart实例
     */
    async createLineChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            throw new Error(`Canvas元素未找到: ${canvasId}`);
        }

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                ...options
            }
        };

        return this.create(ctx, config);
    },

    /**
     * 创建饼图
     * @param {string} canvasId - Canvas元素ID
     * @param {object} data - 数据对象
     * @param {object} options - 可选配置
     * @returns {Promise<object>} Chart实例
     */
    async createPieChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            throw new Error(`Canvas元素未找到: ${canvasId}`);
        }

        const config = {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                ...options
            }
        };

        return this.create(ctx, config);
    },

    /**
     * 创建环形图
     * @param {string} canvasId - Canvas元素ID
     * @param {object} data - 数据对象
     * @param {object} options - 可选配置
     * @returns {Promise<object>} Chart实例
     */
    async createDoughnutChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            throw new Error(`Canvas元素未找到: ${canvasId}`);
        }

        const config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                ...options
            }
        };

        return this.create(ctx, config);
    }
};

// 暴露到全局
window.ChartLoader = ChartLoader;
