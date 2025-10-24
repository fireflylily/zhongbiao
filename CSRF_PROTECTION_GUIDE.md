# CSRF 保护实施指南

## 🛡️ 什么是 CSRF 保护？

**CSRF**（Cross-Site Request Forgery，跨站请求伪造）是一种 Web 攻击方式。本系统已实施完整的 CSRF 保护机制。

---

## ✅ 已实施的保护措施

### 1. 后端保护（Flask-WTF）

**文件**: `ai_tender_system/web/app.py`

```python
from flask_wtf.csrf import CSRFProtect, generate_csrf

# 启用CSRF保护
csrf = CSRFProtect(app)

# 提供CSRF token的API端点
@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """获取CSRF token（用于AJAX请求）"""
    token = generate_csrf()
    return jsonify({'csrf_token': token})
```

**说明**:
- 所有 POST、PUT、DELETE 请求自动要求 CSRF token
- 没有有效 token 的请求将被拒绝（400 Bad Request）

---

### 2. 前端保护（自动化）

#### 2.1 HTML 模板中的 Meta 标签

**所有模板已添加**:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

**已更新的模板**（7个）:
- ✅ `index.html`
- ✅ `knowledge_base.html`
- ✅ `login.html`
- ✅ `tender_processing_hitl.html`
- ✅ `tender_processing.html`
- ✅ `help.html`
- ✅ `system_status.html`

---

#### 2.2 JavaScript 自动保护

**文件**: `ai_tender_system/web/static/js/csrf-protection.js`

**功能**:
1. ✅ 自动拦截所有 `fetch()` 请求
2. ✅ 自动在 POST/PUT/DELETE 请求头中添加 CSRF token
3. ✅ 支持 jQuery AJAX（如果存在）
4. ✅ 提供 `csrfFetch()` 显式调用接口
5. ✅ 提供 Token 刷新机制

**使用方法**:

```html
<!-- 在模板中引入（已自动添加到主要模板） -->
<script src="/static/js/csrf-protection.js"></script>
```

然后直接使用 `fetch()`，CSRF token 会自动添加：

```javascript
// ✅ 自动添加 CSRF token
fetch('/api/companies/1', {
    method: 'DELETE'
})
.then(response => response.json())
.then(data => console.log(data));

// ✅ 或者显式使用 csrfFetch()
csrfFetch('/api/upload', {
    method: 'POST',
    body: formData
});
```

---

## 📋 对于 FormData 的特殊处理

如果使用 `FormData` 提交表单：

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

// 方式1：使用 fetch（自动添加 header）
fetch('/api/upload', {
    method: 'POST',
    body: formData  // CSRF token自动添加到header
});

// 方式2：如果后端需要 form field，手动添加
addCSRFToFormData(formData);  // 添加 csrf_token 字段
```

---

## 🔧 CSRF Token 刷新

对于长时间运行的页面（如编辑器），可以刷新 token：

```javascript
// 手动刷新 token
await refreshCSRFToken();
```

Token 会自动从服务器获取并更新到页面的 meta 标签中。

---

## 🚨 安全注意事项

### 1. **谨慎使用 CSRF 豁免**
⚠️ **仅对登录端点使用豁免**：
```python
# ✅ 正确：登录端点需要豁免（用户还没有token）
@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf_exempt
def login():
    pass
```

❌ 错误做法：
```python
@csrf.exempt  # 不要对其他端点这样做！
@app.route('/api/sensitive-operation', methods=['POST'])
def sensitive_operation():
    pass
```

### 2. **确保 CORS 配置正确**
```python
# app.py 中已配置
CORS(app, supports_credentials=True)  # ✅ 允许携带 cookie
```

### 3. **HTTPS 生产环境**
- 生产环境必须使用 HTTPS
- CSRF token 通过 cookie 传输，HTTP 不安全

---

## 🐛 故障排除

### 问题 1: "CSRF token missing"

**原因**: HTML 模板中缺少 meta 标签

**解决**:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

---

### 问题 2: "CSRF token invalid"

**原因**: Token 过期或 session 失效

**解决**: 刷新页面或调用 `refreshCSRFToken()`

---

### 问题 3: 控制台警告 "CSRF token not found"

**原因**: `csrf-protection.js` 在 meta 标签之前加载

**解决**: 确保 meta 标签在 `<head>` 中，脚本在 `<body>` 末尾

---

## 📝 添加新页面的检查清单

如果添加新的 HTML 模板：

- [ ] 在 `<head>` 添加: `<meta name="csrf-token" content="{{ csrf_token() }}">`
- [ ] 引入保护脚本: `<script src="/static/js/csrf-protection.js"></script>`
- [ ] 测试所有 POST/PUT/DELETE 请求

---

## ✅ 验证 CSRF 保护是否工作

### 1. 打开浏览器开发者工具
```
F12 → Console
```

### 2. 查看加载消息
```
CSRF Protection: Enabled ✓
```

### 3. 测试 API 请求
```javascript
// 在控制台执行
fetch('/api/companies/1', { method: 'DELETE' })
  .then(r => r.json())
  .then(console.log)
```

### 4. 检查请求头
在 Network 标签中查看请求，应包含：
```
X-CSRFToken: eyJ0eXAiOiJKV1QiLCJhbGc...
X-CSRF-Token: eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📊 安全提升总结

| 方面 | 修复前 | 修复后 |
|------|--------|--------|
| CSRF 防护 | ❌ 无 | ✅ 全面启用 |
| 恶意删除风险 | 🔴 高 | ✅ 已阻止 |
| 钓鱼攻击风险 | 🔴 高 | ✅ 已阻止 |
| 自动化攻击 | 🔴 可行 | ✅ 已阻止 |

---

## 🎯 下一步安全改进

1. ⏭️ 修复硬编码密码 (`admin/admin123`)
2. ⏭️ 实施完整的用户认证系统（JWT）
3. ⏭️ 添加 Rate Limiting（API 限流）
4. ⏭️ 实施 HTTPS（生产环境）

---

**最后更新**: 2025-10-24
**维护者**: AI标书系统开发团队

---

## 📝 更新日志

### 2025-10-24
- ✅ **重新启用CSRF保护** - 之前因登录问题暂时禁用，现已完全启用
- ✅ **配置登录端点豁免** - 为 `/login` 端点添加 `@csrf_exempt` 装饰器
- ✅ **验证应用启动** - 确认CSRF保护与所有功能正常工作
- 📄 **文件变更**:
  - `ai_tender_system/web/app.py`: 取消CSRF保护注释
  - `ai_tender_system/web/blueprints/auth_bp.py`: 添加 `@csrf_exempt` 到登录路由
