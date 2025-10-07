/**
 * 向量搜索性能监控组件
 * 功能：实时显示向量搜索系统性能指标
 */

class PerformanceMonitor {
    constructor() {
        this.refreshInterval = 30000; // 30秒刷新一次
        this.charts = {};
        this.intervalId = null;
    }

    /**
     * 初始化性能监控面板
     */
    async initialize() {
        console.log('初始化性能监控组件...');

        // 加载初始数据
        await this.loadPerformanceData();

        // 启动自动刷新
        this.startAutoRefresh();

        // 绑定事件
        this.bindEvents();
    }

    /**
     * 加载性能数据
     */
    async loadPerformanceData() {
        try {
            // 获取性能总览
            const overviewResponse = await fetch('/api/vector_search/analytics/performance_overview');
            const overviewData = await overviewResponse.json();

            if (overviewData.success) {
                this.updatePerformanceOverview(overviewData.data);
            }

            // 获取搜索时间序列
            const timeSeriesResponse = await fetch('/api/vector_search/analytics/search_time_series?days=7&interval=hour');
            const timeSeriesData = await timeSeriesResponse.json();

            if (timeSeriesData.success) {
                this.updateSearchTimeSeriesChart(timeSeriesData.data.time_series);
            }

            // 获取热门关键词
            const keywordsResponse = await fetch('/api/vector_search/analytics/hot_keywords?days=7&limit=10');
            const keywordsData = await keywordsResponse.json();

            if (keywordsData.success) {
                this.updateHotKeywords(keywordsData.data.keywords);
            }

        } catch (error) {
            console.error('加载性能数据失败:', error);
            this.showError('加载性能数据失败');
        }
    }

    /**
     * 更新性能总览卡片
     */
    updatePerformanceOverview(data) {
        const { system_status, vector_store_stats, document_stats, search_performance } = data;

        // 系统状态
        const statusElement = document.getElementById('system-status');
        if (statusElement) {
            statusElement.innerHTML = system_status.initialized
                ? '<span class="badge bg-success">运行中</span>'
                : '<span class="badge bg-danger">未初始化</span>';
        }

        // 向量存储统计
        this.updateCard('total-documents', vector_store_stats.total_documents || 0);
        this.updateCard('total-vectors', vector_store_stats.total_vectors || 0);
        this.updateCard('storage-size', this.formatBytes(vector_store_stats.storage_size || 0));
        this.updateCard('index-type', vector_store_stats.index_type || 'N/A');

        // 文档统计
        this.updateCard('doc-total', document_stats.total || 0);
        this.updateCard('doc-vectorized', document_stats.vectorized || 0);
        this.updateCard('doc-pending', document_stats.pending || 0);
        this.updateCard('doc-failed', document_stats.failed || 0);

        // 搜索性能
        this.updateCard('total-searches', search_performance.total_searches || 0);
        this.updateCard('avg-search-time', (search_performance.avg_search_time || 0).toFixed(3) + 's');
        this.updateCard('avg-results-count', Math.round(search_performance.avg_results_count || 0));

        // 更新进度条
        if (document_stats.total > 0) {
            const vectorizedPercent = (document_stats.vectorized / document_stats.total * 100).toFixed(1);
            const progressBar = document.getElementById('vectorization-progress');
            if (progressBar) {
                progressBar.style.width = vectorizedPercent + '%';
                progressBar.textContent = vectorizedPercent + '%';
            }
        }
    }

    /**
     * 更新卡片值
     */
    updateCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * 更新搜索耗时时间序列图表
     */
    updateSearchTimeSeriesChart(timeSeries) {
        const chartElement = document.getElementById('search-time-chart');
        if (!chartElement) return;

        // 准备图表数据
        const labels = timeSeries.map(item => item.time_bucket).reverse();
        const avgTimes = timeSeries.map(item => (item.avg_search_time || 0).toFixed(3)).reverse();
        const searchCounts = timeSeries.map(item => item.search_count || 0).reverse();

        // 如果图表已存在，先销毁
        if (this.charts.searchTimeChart) {
            this.charts.searchTimeChart.destroy();
        }

        // 创建新图表
        const ctx = chartElement.getContext('2d');
        this.charts.searchTimeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '平均搜索耗时 (秒)',
                        data: avgTimes,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        yAxisID: 'y',
                        tension: 0.1
                    },
                    {
                        label: '搜索次数',
                        data: searchCounts,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        yAxisID: 'y1',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    title: {
                        display: true,
                        text: '搜索性能趋势（最近7天）'
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '搜索耗时 (秒)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '搜索次数'
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    }
                }
            }
        });
    }

    /**
     * 更新热门关键词列表
     */
    updateHotKeywords(keywords) {
        const listElement = document.getElementById('hot-keywords-list');
        if (!listElement) return;

        if (!keywords || keywords.length === 0) {
            listElement.innerHTML = '<li class="list-group-item text-muted">暂无搜索记录</li>';
            return;
        }

        listElement.innerHTML = keywords.map((keyword, index) => `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <span class="badge bg-primary me-2">${index + 1}</span>
                    <strong>${this.escapeHtml(keyword.query_text)}</strong>
                </div>
                <div class="text-end">
                    <small class="text-muted d-block">搜索 ${keyword.search_count} 次</small>
                    <small class="text-muted d-block">平均耗时 ${(keyword.avg_search_time || 0).toFixed(3)}s</small>
                </div>
            </li>
        `).join('');
    }

    /**
     * 启动自动刷新
     */
    startAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }

        this.intervalId = setInterval(() => {
            this.loadPerformanceData();
        }, this.refreshInterval);
    }

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-performance');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadPerformanceData();
            });
        }

        // 导出报告按钮
        const exportBtn = document.getElementById('export-report');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportPerformanceReport();
            });
        }
    }

    /**
     * 导出性能报告
     */
    async exportPerformanceReport() {
        try {
            const response = await fetch('/api/vector_search/analytics/performance_overview');
            const data = await response.json();

            if (data.success) {
                const report = this.generateReportText(data.data);
                this.downloadReport(report);
            }
        } catch (error) {
            console.error('导出报告失败:', error);
            this.showError('导出报告失败');
        }
    }

    /**
     * 生成报告文本
     */
    generateReportText(data) {
        const timestamp = new Date().toLocaleString('zh-CN');
        return `
向量搜索性能监控报告
生成时间: ${timestamp}
================================

系统状态
--------------------------------
初始化状态: ${data.system_status.initialized ? '已初始化' : '未初始化'}

向量存储统计
--------------------------------
文档总数: ${data.vector_store_stats.total_documents || 0}
向量总数: ${data.vector_store_stats.total_vectors || 0}
存储大小: ${this.formatBytes(data.vector_store_stats.storage_size || 0)}
索引类型: ${data.vector_store_stats.index_type || 'N/A'}

文档统计
--------------------------------
总文档数: ${data.document_stats.total || 0}
已向量化: ${data.document_stats.vectorized || 0}
待处理: ${data.document_stats.pending || 0}
失败: ${data.document_stats.failed || 0}

搜索性能（最近30天）
--------------------------------
总搜索次数: ${data.search_performance.total_searches || 0}
平均搜索耗时: ${(data.search_performance.avg_search_time || 0).toFixed(3)}秒
平均结果数: ${Math.round(data.search_performance.avg_results_count || 0)}
        `.trim();
    }

    /**
     * 下载报告文件
     */
    downloadReport(content) {
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `performance_report_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * 格式化字节数
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * HTML转义
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 显示错误消息
     */
    showError(message) {
        // 使用项目中的通用提示方法
        if (window.showToast) {
            window.showToast('error', message);
        } else {
            alert(message);
        }
    }

    /**
     * 清理资源
     */
    destroy() {
        this.stopAutoRefresh();

        // 销毁所有图表
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });

        this.charts = {};
    }
}

// 导出为全局变量
window.PerformanceMonitor = PerformanceMonitor;
