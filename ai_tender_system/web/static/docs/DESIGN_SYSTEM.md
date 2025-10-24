# 🎨 AI智能标书生成平台 - 设计系统文档

> **版本**: v1.0.0
> **最后更新**: 2025-10-24
> **状态**: ✅ 基础架构已完成

---

## 📖 目录

1. [设计原则](#设计原则)
2. [设计令牌](#设计令牌)
3. [组件库](#组件库)
4. [使用指南](#使用指南)
5. [可访问性](#可访问性)
6. [响应式设计](#响应式设计)

---

## 🎯 设计原则

### 核心理念

**一致性优先** - 统一的视觉语言贯穿整个应用
**可访问性第一** - 符合WCAG AA标准的对比度和交互设计
**性能优化** - 基于CSS变量的主题系统,易于定制和维护
**组件化思维** - 原子设计方法论,可复用的UI积木

### 设计语言

- **专业商务风格** - 蓝色主色调,传递专业可靠的品牌形象
- **清晰的信息层级** - 明确的字体大小和颜色层次
- **柔和的交互反馈** - 流畅的过渡动画和微交互
- **现代化的视觉效果** - 微阴影、圆角、渐变等现代设计元素

---

## 🎨 设计令牌

### 色彩系统

#### 品牌色彩

```css
/* 主色 - 品牌蓝 */
--color-primary-500: #4a89dc;  /* 主品牌色 */
--color-primary-50 至 -900     /* 9级色阶 */

/* 次要色 - 青色 */
--color-secondary-500: #48cfad;

/* 语义色彩 */
--color-success-500: #48cfad;   /* 成功-绿色 */
--color-warning-500: #f39c12;   /* 警告-橙色 */
--color-error-500: #e74c3c;     /* 错误-红色 */
--color-info-500: #5dade2;      /* 信息-浅蓝 */
```

#### 中性灰度 (10级精细灰度)

```css
--color-gray-50: #fafafa;   /* 页面背景 */
--color-gray-100: #f5f5f5;  /* 卡片背景 */
--color-gray-500: #9e9e9e;  /* 辅助文本 */
--color-gray-900: #212121;  /* 主标题 */
```

#### 使用场景

| 场景 | 令牌 | 示例 |
|------|------|------|
| 页面背景 | `--surface-background` | 整个应用背景 |
| 卡片背景 | `--surface-card` | Card组件 |
| 主要文本 | `--text-primary` | 标题、正文 |
| 次要文本 | `--text-secondary` | 辅助说明 |
| 边框 | `--border-light` | 分割线、卡片边框 |
| 焦点边框 | `--border-focus` | 表单聚焦状态 |

### 字体排印

#### 字号比例尺 (基于1.25倍模块化比例)

```css
--font-size-xs: 0.75rem;    /* 12px - 辅助文字 */
--font-size-sm: 0.875rem;   /* 14px - 小按钮文字 */
--font-size-base: 1rem;     /* 16px - 正文 */
--font-size-lg: 1.25rem;    /* 20px - 小标题 */
--font-size-xl: 1.5rem;     /* 24px - 二级标题 */
--font-size-2xl: 2rem;      /* 32px - 一级标题 */
```

#### 行高系统

```css
--line-height-tight: 1.2;   /* 标题 */
--line-height-normal: 1.5;  /* 正文 */
--line-height-relaxed: 1.8; /* 长文本 */
```

#### 字重

```css
--font-weight-normal: 400;    /* 正文 */
--font-weight-medium: 500;    /* 强调 */
--font-weight-semibold: 600;  /* 子标题 */
--font-weight-bold: 700;      /* 标题 */
```

### 间距系统 (8点网格)

```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-4: 1rem;     /* 16px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
```

**语义化间距**:
- `--spacing-component-gap`: 16px (组件内元素间距)
- `--spacing-section-gap`: 32px (区块间距)
- `--spacing-page-gap`: 48px (页面级间距)

### 圆角系统

```css
--radius-sm: 0.25rem;   /* 4px - 小按钮 */
--radius-md: 0.5rem;    /* 8px - 卡片、输入框 */
--radius-lg: 0.75rem;   /* 12px - 大卡片 */
--radius-full: 9999px;  /* 圆形 */
```

### 阴影系统 (4层海拔)

```css
--shadow-xs: 0 1px 2px rgba(0,0,0,0.05);    /* 微阴影 */
--shadow-sm: 0 2px 4px rgba(0,0,0,0.08);    /* 卡片默认 */
--shadow-md: 0 4px 6px rgba(0,0,0,0.12);    /* 悬浮提升 */
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1);   /* 模态框 */
```

### 动画与过渡

```css
--duration-fast: 150ms;     /* 快速交互 */
--duration-normal: 250ms;   /* 标准过渡 */
--duration-slow: 350ms;     /* 复杂动画 */

--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);  /* 标准缓动 */
```

---

## 🧩 组件库

### 原子级组件 (Atoms)

#### 徽章 (Badges)

**用途**: 状态标识、计数显示、分类标签

**变体**:
- 实心: `.badge-solid-primary`
- 轮廓: `.badge-outline-success`
- 柔和: `.badge-soft-warning`

**尺寸**:
- 小: `.badge-sm`
- 中: `.badge-md`
- 大: `.badge-lg`

**示例**:
```html
<!-- 实心主色徽章 -->
<span class="badge badge-solid-primary">新功能</span>

<!-- 柔和成功徽章 -->
<span class="badge badge-soft-success">已完成</span>

<!-- 带计数的通知徽章 -->
<span class="badge-container">
    <i class="bi bi-bell"></i>
    <span class="badge-notification">5</span>
</span>
```

#### 标签 (Tags)

**用途**: 关键词标记、可删除标签、分类过滤

**变体**:
- 默认: `.tag`
- 彩色: `.tag-primary`
- 可移除: `.tag-removable`
- 可选择: `.tag-selectable`

**示例**:
```html
<!-- 基础标签 -->
<span class="tag">Python</span>

<!-- 可移除标签 -->
<span class="tag tag-removable tag-primary">
    Flask
    <button class="tag-remove-btn" aria-label="移除">
        <i class="bi bi-x"></i>
    </button>
</span>

<!-- 标签组 -->
<div class="tag-group">
    <span class="tag">AI</span>
    <span class="tag">机器学习</span>
    <span class="tag">NLP</span>
</div>
```

#### 图标系统

**尺寸类**:
```html
<i class="bi bi-star icon-xs"></i>  <!-- 12px -->
<i class="bi bi-star icon-sm"></i>  <!-- 16px -->
<i class="bi bi-star icon-md"></i>  <!-- 20px -->
<i class="bi bi-star icon-lg"></i>  <!-- 24px -->
```

**颜色类**:
```html
<i class="bi bi-check-circle icon-success"></i>
<i class="bi bi-exclamation-triangle icon-warning"></i>
<i class="bi bi-x-circle icon-error"></i>
```

**状态类**:
```html
<i class="bi bi-arrow-clockwise icon-spin"></i>  <!-- 旋转动画 -->
<i class="bi bi-bell icon-pulse"></i>           <!-- 脉冲动画 -->
```

### 分子级组件 (Molecules)

#### 按钮 (Buttons) - 已有

详见 `static/css/components/buttons.css`

**变体**: primary, success, warning, danger, outline
**尺寸**: sm, md, lg
**状态**: loading, disabled, active

#### 表单 (Forms) - 已有

详见 `static/css/components/form-common.css`

**组件**: 输入框、下拉框、复选框、单选按钮
**状态**: 成功、错误、禁用
**增强**: 焦点阴影、验证反馈

#### 卡片 (Cards) - 已有

详见 `static/css/components/cards.css`

**变体**: 基础、悬浮、特色、数据卡片
**交互**: 悬浮提升、点击效果

---

## 📐 使用指南

### 快速开始

1. **引入设计令牌**

```html
<link rel="stylesheet" href="/static/css/base/design-tokens.css">
<link rel="stylesheet" href="/static/css/base/iconography.css">
```

2. **使用组件**

```html
<!-- 原子组件 -->
<link rel="stylesheet" href="/static/css/atoms/badges.css">
<link rel="stylesheet" href="/static/css/atoms/tags.css">

<!-- 分子组件 -->
<link rel="stylesheet" href="/static/css/components/buttons.css">
<link rel="stylesheet" href="/static/css/components/cards.css">
```

3. **在HTML中应用**

```html
<div class="card">
    <div class="card-header">
        <h5>项目标题</h5>
        <span class="badge badge-soft-success">进行中</span>
    </div>
    <div class="card-body">
        <p>项目描述内容...</p>
        <div class="tag-group">
            <span class="tag tag-primary">AI</span>
            <span class="tag tag-info">投标</span>
        </div>
    </div>
</div>
```

### 主题定制

#### 修改品牌色

编辑 `design-tokens.css`:

```css
:root {
    --color-primary-500: #YOUR_BRAND_COLOR;
}
```

#### 暗色主题

系统已内置暗色模式支持,会根据用户系统偏好自动切换:

```css
@media (prefers-color-scheme: dark) {
    /* 自动应用暗色主题 */
}
```

---

## ♿ 可访问性

### WCAG AA 合规

所有颜色组合均满足4.5:1的对比度要求

### 键盘导航

- 所有交互元素可通过Tab键访问
- 焦点状态有明显视觉反馈 (`--shadow-focus-primary`)

### 屏幕阅读器

- 装饰性图标使用 `aria-hidden="true"`
- 交互式图标包含 `aria-label`
- 使用 `.sr-only` 类提供额外的上下文

示例:
```html
<button class="btn-icon-only" aria-label="关闭">
    <i class="bi bi-x" aria-hidden="true"></i>
</button>
```

### 减少动画

系统自动检测用户偏好:

```css
@media (prefers-reduced-motion: reduce) {
    /* 禁用或简化动画 */
}
```

---

## 📱 响应式设计

### 断点系统

```css
--breakpoint-sm: 576px;   /* 手机横屏 */
--breakpoint-md: 768px;   /* 平板竖屏 */
--breakpoint-lg: 992px;   /* 平板横屏 */
--breakpoint-xl: 1200px;  /* 桌面 */
--breakpoint-xxl: 1400px; /* 大屏桌面 */
```

### 移动端优化

- 触摸目标最小48x48px
- 自适应字体大小
- 简化的交互模式
- 响应式间距调整

---

## 🚀 最佳实践

### DO ✅

- 使用设计令牌而不是硬编码值
- 选择语义化的组件类名
- 保持一致的间距和圆角
- 为交互元素提供反馈
- 测试暗色模式兼容性

### DON'T ❌

- 不要直接修改Bootstrap默认类
- 不要使用内联样式
- 不要忽略可访问性要求
- 不要在组件外定义特定于组件的样式
- 不要混用多种设计模式

---

## 📚 参考资源

- [设计令牌](../css/base/design-tokens.css)
- [图标系统](../css/base/iconography.css)
- [原子组件](../css/atoms/)
- [分子组件](../css/components/)
- [Bootstrap 5文档](https://getbootstrap.com/docs/5.0/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)

---

## 🔄 变更日志

### v1.0.0 (2025-10-24)

- ✅ 完整的设计令牌系统
- ✅ 图标使用规范
- ✅ 原子级组件 (徽章、标签)
- ✅ 暗色主题支持
- ✅ 可访问性标准
- ✅ 响应式设计系统

---

**维护者**: AI标书系统开发团队
**联系方式**: [GitHub Issues](https://github.com/your-org/ai-tender-system/issues)
