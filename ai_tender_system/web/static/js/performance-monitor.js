/**
 * 性能监控脚本 - Web Vitals监控
 * 监控关键性能指标: FCP, LCP, CLS, FID, TTFB
 *
 * 使用方法:
 * 1. 在index.html底部引入: <script src="/static/js/performance-monitor.js" defer></script>
 * 2. 或者使用Web Vitals库(推荐): https://github.com/GoogleChrome/web-vitals
 */

(function() {
    'use strict';

    // 性能监控配置
    const CONFIG = {
        enabled: true,  // 是否启用监控
        logToConsole: true,  // 是否输出到控制台
        sendToServer: false,  // 是否发送到服务器
        endpoint: '/api/performance-metrics',  // 服务器端点
    };

    // 性能阈值 (Lighthouse标准)
    const THRESHOLDS = {
        FCP: { good: 1800, needsImprovement: 3000 },  // First Contentful Paint (ms)
        LCP: { good: 2500, needsImprovement: 4000 },  // Largest Contentful Paint (ms)
        FID: { good: 100, needsImprovement: 300 },    // First Input Delay (ms)
        CLS: { good: 0.1, needsImprovement: 0.25 },   // Cumulative Layout Shift
        TTFB: { good: 800, needsImprovement: 1800 },  // Time to First Byte (ms)
    };

    /**
     * 获取性能评分
     */
    function getScore(metric, value) {
        const threshold = THRESHOLDS[metric];
        if (!threshold) return 'unknown';

        if (value <= threshold.good) return 'good';
        if (value <= threshold.needsImprovement) return 'needs-improvement';
        return 'poor';
    }

    /**
     * 监控 FCP (First Contentful Paint)
     */
    function monitorFCP() {
        if (!window.PerformanceObserver) return;

        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.name === 'first-contentful-paint') {
                    const value = entry.startTime;
                    const score = getScore('FCP', value);
                    logMetric('FCP', value, score);
                }
            }
        });

        try {
            observer.observe({ type: 'paint', buffered: true });
        } catch (e) {
            console.warn('[PerformanceMonitor] FCP监控失败:', e);
        }
    }

    /**
     * 监控 LCP (Largest Contentful Paint)
     */
    function monitorLCP() {
        if (!window.PerformanceObserver) return;

        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            const value = lastEntry.renderTime || lastEntry.loadTime;
            const score = getScore('LCP', value);
            logMetric('LCP', value, score);
        });

        try {
            observer.observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (e) {
            console.warn('[PerformanceMonitor] LCP监控失败:', e);
        }
    }

    /**
     * 监控 CLS (Cumulative Layout Shift)
     */
    function monitorCLS() {
        if (!window.PerformanceObserver) return;

        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            }
            const score = getScore('CLS', clsValue);
            logMetric('CLS', clsValue.toFixed(3), score);
        });

        try {
            observer.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {
            console.warn('[PerformanceMonitor] CLS监控失败:', e);
        }
    }

    /**
     * 监控 FID (First Input Delay)
     */
    function monitorFID() {
        if (!window.PerformanceObserver) return;

        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                const value = entry.processingStart - entry.startTime;
                const score = getScore('FID', value);
                logMetric('FID', value, score);
            }
        });

        try {
            observer.observe({ type: 'first-input', buffered: true });
        } catch (e) {
            console.warn('[PerformanceMonitor] FID监控失败:', e);
        }
    }

    /**
     * 监控 TTFB (Time to First Byte)
     */
    function monitorTTFB() {
        if (!window.performance || !window.performance.timing) return;

        window.addEventListener('load', () => {
            const timing = window.performance.timing;
            const value = timing.responseStart - timing.requestStart;
            const score = getScore('TTFB', value);
            logMetric('TTFB', value, score);
        });
    }

    /**
     * 监控资源加载时间
     */
    function monitorResources() {
        window.addEventListener('load', () => {
            if (!window.performance || !window.performance.getEntriesByType) return;

            const resources = window.performance.getEntriesByType('resource');
            const slowResources = resources
                .filter(r => r.duration > 1000)  // 大于1秒的资源
                .sort((a, b) => b.duration - a.duration)
                .slice(0, 5);  // 前5个最慢的资源

            if (slowResources.length > 0 && CONFIG.logToConsole) {
                console.group('⚠️ 慢速资源加载 (>1s)');
                slowResources.forEach(r => {
                    console.log(`${r.name.split('/').pop()}: ${r.duration.toFixed(0)}ms`);
                });
                console.groupEnd();
            }
        });
    }

    /**
     * 记录性能指标
     */
    function logMetric(name, value, score) {
        const metric = {
            name: name,
            value: typeof value === 'number' ? Math.round(value) : value,
            score: score,
            timestamp: new Date().toISOString(),
            url: window.location.href,
        };

        // 控制台输出
        if (CONFIG.logToConsole) {
            const icon = score === 'good' ? '✅' : score === 'needs-improvement' ? '⚠️' : '❌';
            console.log(`[PerformanceMonitor] ${icon} ${name}: ${metric.value}${name === 'CLS' ? '' : 'ms'} (${score})`);
        }

        // 发送到服务器
        if (CONFIG.sendToServer) {
            sendMetricToServer(metric);
        }

        // 存储到 localStorage (可选)
        try {
            const metrics = JSON.parse(localStorage.getItem('performanceMetrics') || '[]');
            metrics.push(metric);
            // 只保留最近100条记录
            if (metrics.length > 100) {
                metrics.shift();
            }
            localStorage.setItem('performanceMetrics', JSON.stringify(metrics));
        } catch (e) {
            // localStorage可能被禁用
        }
    }

    /**
     * 发送指标到服务器
     */
    function sendMetricToServer(metric) {
        if (!navigator.sendBeacon) {
            // 降级到fetch
            fetch(CONFIG.endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(metric),
                keepalive: true,
            }).catch(e => console.warn('[PerformanceMonitor] 发送指标失败:', e));
        } else {
            // 使用sendBeacon (不阻塞页面卸载)
            navigator.sendBeacon(
                CONFIG.endpoint,
                JSON.stringify(metric)
            );
        }
    }

    /**
     * 获取性能摘要
     */
    function getPerformanceSummary() {
        try {
            const metrics = JSON.parse(localStorage.getItem('performanceMetrics') || '[]');
            if (metrics.length === 0) return null;

            const summary = {
                FCP: [],
                LCP: [],
                CLS: [],
                FID: [],
                TTFB: [],
            };

            metrics.forEach(m => {
                if (summary[m.name]) {
                    summary[m.name].push(parseFloat(m.value));
                }
            });

            // 计算平均值
            const result = {};
            Object.keys(summary).forEach(key => {
                const values = summary[key];
                if (values.length > 0) {
                    result[key] = {
                        avg: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(0),
                        min: Math.min(...values).toFixed(0),
                        max: Math.max(...values).toFixed(0),
                        count: values.length,
                    };
                }
            });

            return result;
        } catch (e) {
            return null;
        }
    }

    /**
     * 初始化性能监控
     */
    function init() {
        if (!CONFIG.enabled) return;

        console.log('[PerformanceMonitor] 🚀 性能监控已启动');

        // 监控核心Web Vitals
        monitorFCP();
        monitorLCP();
        monitorCLS();
        monitorFID();
        monitorTTFB();

        // 监控资源加载
        monitorResources();

        // 页面卸载时输出摘要
        window.addEventListener('beforeunload', () => {
            const summary = getPerformanceSummary();
            if (summary && CONFIG.logToConsole) {
                console.table(summary);
            }
        });

        // 暴露API给全局
        window.PerformanceMonitor = {
            getSummary: getPerformanceSummary,
            clearMetrics: () => localStorage.removeItem('performanceMetrics'),
        };
    }

    // DOMContentLoaded后启动
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
