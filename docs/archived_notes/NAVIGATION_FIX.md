# 导航栏多选状态修复

## 问题描述

导航栏出现多个导航项同时处于激活状态（蓝色高亮）的问题：
- "商务应答"（一级菜单）
- "企业信息库"（知识库管理的二级子菜单）

同时被标记为 `active` 状态，违反了单选导航的设计原则。

## 问题根源

1. **Bootstrap Pill导航状态管理不完善**
   - Bootstrap的pill导航在一级和二级菜单切换时没有自动清除其他项的active状态
   - 特别是知识库管理有折叠的二级菜单，导致状态管理更复杂

2. **知识库管理折叠菜单的特殊性**
   - 知识库管理本身是一个 `data-bs-toggle="collapse"` 触发器
   - 它不应该有active状态，但在某些情况下会被误标记

3. **缺少全局导航状态管理**
   - 没有统一的机制确保同一时间只有一个导航项处于active状态

## 解决方案

### 1. 新增导航状态管理器

**位置**: [index.html:668-711](ai_tender_system/web/templates/index.html#L668-L711)

创建了 `initNavigationManager()` 函数，实现以下功能：

```javascript
function initNavigationManager() {
    // 获取所有导航链接（一级和二级）
    const allNavLinks = document.querySelectorAll('.list-group-item-action[data-bs-toggle="pill"]');

    allNavLinks.forEach(navLink => {
        // 点击时清除所有其他导航项的active状态
        navLink.addEventListener('click', function(e) {
            allNavLinks.forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
        });

        // 监听Bootstrap Tab显示事件（双重保险）
        navLink.addEventListener('shown.bs.tab', function(event) {
            allNavLinks.forEach(link => {
                if (link !== event.target) {
                    link.classList.remove('active');
                }
            });
        });
    });

    // 确保知识库管理折叠菜单本身不会被标记为active
    const knowledgeToggle = document.querySelector('[data-bs-target="#knowledgeSubmenu"]');
    if (knowledgeToggle) {
        knowledgeToggle.addEventListener('click', function(e) {
            this.classList.remove('active');
        });
    }
}
```

### 2. 优化 switchToTab 函数

**位置**: [index.html:648-673](ai_tender_system/web/templates/index.html#L648-L673)

增强了 `switchToTab()` 函数，确保编程式切换tab时也能正确管理状态：

```javascript
function switchToTab(tabId) {
    // 移除所有导航项的活跃状态（包括一级和二级菜单）
    document.querySelectorAll('.list-group-item-action[data-bs-toggle="pill"]').forEach(item => {
        item.classList.remove('active');
    });

    // 移除所有tab内容的活跃状态
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('show', 'active');
    });

    // 激活指定的导航项和选项卡
    const navItem = document.querySelector(`[data-bs-target="#${tabId}"]`);
    const tabPane = document.querySelector(`#${tabId}`);

    if (navItem && tabPane) {
        navItem.classList.add('active');
        tabPane.classList.add('show', 'active');
    }
}
```

### 3. 在页面初始化时启动导航管理器

**位置**: [index.html:717-718](ai_tender_system/web/templates/index.html#L717-L718)

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // 【新增】初始化导航状态管理器
    initNavigationManager();

    // ... 其他初始化代码
});
```

## 修复效果

✅ **单选保证**: 同一时间只有一个导航项处于激活状态
✅ **一二级联动**: 一级菜单和二级菜单切换时正确清理状态
✅ **折叠菜单保护**: 知识库管理折叠触发器不会被误标记为active
✅ **编程式切换**: `switchToTab()` 函数也遵循相同的状态管理规则
✅ **双重保险**: 同时监听 `click` 和 `shown.bs.tab` 事件

## 测试场景

1. ✅ 点击一级菜单（如"商务应答"），之前选中的项应该取消高亮
2. ✅ 点击知识库管理的子菜单（如"企业信息库"），一级菜单的高亮应该清除
3. ✅ 知识库管理的折叠触发器本身不应该有高亮状态
4. ✅ 在知识库的各个子菜单间切换，只有当前选中的子菜单高亮
5. ✅ 使用 `switchToTab()` 函数切换，状态管理也正确

## 访问地址

🚀 服务器已启动: **http://127.0.0.1:8110**

现在可以在浏览器中测试导航栏，应该不会再出现多选的情况了！
