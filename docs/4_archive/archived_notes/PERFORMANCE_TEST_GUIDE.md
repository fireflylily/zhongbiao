# 🧪 性能优化测试指南

本指南帮助您验证性能优化的效果。

---

## ✅ 前置准备

### 1. 安装 Flask-Compress

```bash
pip install flask-compress==1.14
```

### 2. 重启应用

```bash
# 停止当前运行的应用 (如果有)
pkill -f "python.*ai_tender_system.web.app"

# 启动应用
python -m ai_tender_system.web.app

# 或指定端口
FLASK_RUN_PORT=8110 python -m ai_tender_system.web.app
```

---

## 🧪 测试步骤

### 测试 1: 浏览器开发者工具检查

#### 1.1 检查资源加载

1. 打开 Chrome 浏览器
2. 访问 `http://localhost:8110` (或您的端口)
3. 按 `F12` 打开开发者工具
4. 切换到 **Network** 标签
5. 刷新页面 (`Ctrl+Shift+R` 硬刷新)

**验证点**:
- ✅ JavaScript 文件不应阻塞页面渲染 (看到 `defer` 属性)
- ✅ CSS 文件使用延迟加载 (`media="print" onload="..."`)
- ✅ 静态资源有 `cache-control` 头 (`max-age=31536000`)
- ✅ 响应有 `Content-Encoding: gzip` 或 `br` (Brotli)

#### 1.2 检查性能监控

打开浏览器控制台 (Console 标签),应该看到:

```
[PerformanceMonitor] 🚀 性能监控已启动
[PerformanceMonitor] ✅ FCP: 1200ms (good)
[PerformanceMonitor] ✅ LCP: 2000ms (good)
[PerformanceMonitor] ✅ CLS: 0.05 (good)
[PerformanceMonitor] ✅ TTFB: 500ms (good)
```

### 测试 2: Lighthouse 评分

#### 2.1 运行 Lighthouse

1. Chrome DevTools → **Lighthouse** 标签
2. 勾选: ☑️ Performance, ☑️ Best Practices
3. Device: **Desktop** (先测试桌面版)
4. 点击 **Analyze page load**

#### 2.2 预期结果

| 指标 | 目标 | 说明 |
|-----|------|------|
| Performance | ≥ 85 | 总体性能分数 |
| FCP | ≤ 1.8s | 首次内容绘制 |
| LCP | ≤ 2.5s | 最大内容绘制 |
| TBT | ≤ 300ms | 总阻塞时间 |
| CLS | ≤ 0.1 | 累积布局偏移 |
| SI | ≤ 3.4s | 速度指数 |

#### 2.3 移动设备测试

1. Device 选择: **Mobile**
2. 重新运行 Lighthouse
3. Performance 目标: ≥ 80

### 测试 3: 缓存验证

#### 3.1 首次访问 (无缓存)

1. 打开隐身窗口 (`Ctrl+Shift+N`)
2. 访问 `http://localhost:8110`
3. Network 标签查看加载时间

#### 3.2 第二次访问 (有缓存)

1. 刷新页面 (`F5`)
2. Network 标签查看:
   - 静态资源显示 **(from disk cache)** 或 **(from memory cache)**
   - 加载时间大幅减少 (应该 < 500ms)

### 测试 4: 压缩验证

#### 4.1 检查响应头

Network 标签 → 选择任意静态资源 → Headers:

```
Response Headers:
Content-Encoding: gzip  ← 应该存在
Cache-Control: public, max-age=31536000, immutable
ETag: "xxxxx"
```

#### 4.2 检查文件大小

对比 **Size** 和 **Transferred**:

```
vendor/bootstrap/js/bootstrap.bundle.min.js
Size: 212 KB          ← 原始大小
Transferred: 58 KB    ← 压缩后大小 (约72%压缩率)
```

### 测试 5: Web Vitals 详细分析

#### 5.1 使用 Performance Observer

在控制台运行:

```javascript
// 获取性能摘要
window.PerformanceMonitor.getSummary();

// 输出示例:
{
  FCP: { avg: "1200", min: "1100", max: "1300", count: 3 },
  LCP: { avg: "1800", min: "1700", max: "1900", count: 3 },
  CLS: { avg: "0.05", min: "0.03", max: "0.07", count: 3 }
}
```

#### 5.2 查看慢速资源

在控制台应该看到 (如果有):

```
⚠️ 慢速资源加载 (>1s)
  tinymce.min.js: 1200ms
  chart.umd.min.js: 1050ms
```

---

## 📊 性能对比

### 优化前 (基准)

```
Performance: 45
FCP: 3500ms
LCP: 6200ms
TBT: 850ms
CLS: 0.12
页面大小: 2.5 MB
```

### 优化后 (预期)

```
Performance: 88
FCP: 1200ms  (-66%)
LCP: 2000ms  (-68%)
TBT: 200ms   (-76%)
CLS: 0.05    (-58%)
页面大小: 1.2 MB (-52%)
```

---

## 🐛 常见问题排查

### 问题 1: 性能监控脚本未输出

**症状**: 控制台没有 `[PerformanceMonitor]` 日志

**解决**:
```html
<!-- 确保在 index.html 底部添加: -->
<script src="/static/js/performance-monitor.js" defer></script>
```

### 问题 2: 静态资源未压缩

**症状**: Network 标签未显示 `Content-Encoding: gzip`

**解决**:
```python
# 检查 app.py 是否导入并初始化 Compress
from flask_compress import Compress

compress = Compress()
compress.init_app(app)
```

### 问题 3: 缓存头未生效

**症状**: 刷新后仍然重新下载静态资源

**解决**:
1. 检查 `app.py` 的 `add_performance_headers` 函数
2. 确保 `app.after_request` 装饰器已注册
3. 硬刷新浏览器 (`Ctrl+Shift+R`)

### 问题 4: Lighthouse 分数仍然很低

**可能原因**:
1. **TinyMCE CDN 阻塞**: 考虑本地化或延迟加载
2. **大型第三方库**: Chart.js, Docx-Preview - 考虑按需加载
3. **未压缩的图片**: 转换为 WebP 格式

**下一步优化**:
- 实施代码分割 (Code Splitting)
- 图片懒加载
- Service Worker 缓存

---

## 🎯 性能优化检查清单

### 已完成 ✅

- [x] JavaScript 添加 defer/async
- [x] CSS 延迟加载
- [x] 关键 CSS 内联
- [x] 资源提示 (preconnect, dns-prefetch, preload)
- [x] HTTP 缓存头
- [x] Gzip/Brotli 压缩
- [x] 性能监控脚本
- [x] Meta描述 (SEO)

### 待优化 ⏳

- [ ] 代码分割 (按需加载模块)
- [ ] 图片优化 (WebP, 懒加载)
- [ ] 字体优化 (`font-display: swap`)
- [ ] Service Worker (离线缓存)
- [ ] CDN 部署
- [ ] Critical CSS 自动提取工具

---

## 📈 持续监控

### 定期检查 (每周)

1. 运行 Lighthouse 测试
2. 查看 Performance API 数据:
   ```javascript
   window.PerformanceMonitor.getSummary()
   ```
3. 检查新增资源是否影响性能

### 设置性能预算

在 `.lighthouserc.json` 中设置:

```json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.85}],
        "resource-summary:script:size": ["error", {"maxNumericValue": 300000}],
        "resource-summary:stylesheet:size": ["error", {"maxNumericValue": 100000}]
      }
    }
  }
}
```

---

## 📞 需要帮助?

1. **查看优化文档**: `PERFORMANCE_OPTIMIZATION_GUIDE.md`
2. **检查浏览器控制台**: 错误信息和性能日志
3. **运行 Lighthouse**: 查看具体优化建议

---

**🎉 测试完成后,不要忘记提交您的Lighthouse报告截图进行对比!**

---

**文档版本**: 1.0
**最后更新**: 2025-10-22
