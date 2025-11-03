# Vue 前端部署指南

> **项目**: 元景AI智能标书生成平台 - 现代化 Vue 3 前端
> **技术栈**: Vue 3 + TypeScript + Vite + Element Plus + Pinia

---

## 📋 目录

- [开发环境访问](#开发环境访问)
- [生产环境构建](#生产环境构建)
- [阿里云部署](#阿里云部署)
- [访问地址](#访问地址)
- [常见问题](#常见问题)

---

## 🚀 开发环境访问

### 前置条件

- Node.js >= 18.0.0
- npm >= 9.0.0
- Flask 后端运行在 `localhost:8110`

### 启动步骤

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（首次运行）
npm install

# 3. 启动开发服务器
npm run dev
```

### 访问地址

开发服务器启动后，访问：

```
http://localhost:5173
```

### 开发模式特性

✅ **热模块替换（HMR）** - 代码改动实时更新，无需刷新
✅ **API自动代理** - 自动代理 `/api/*` 请求到 Flask 后端
✅ **TypeScript检查** - 实时类型检查和错误提示
✅ **快速构建** - Vite 闪电般的启动速度

### API 代理配置

开发环境下，所有 `/api/*` 请求会自动代理到：

```
http://localhost:8110
```

如需修改后端地址，编辑 `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8110',  // 修改此处
      changeOrigin: true
    }
  }
}
```

---

## 🏗️ 生产环境构建

### 构建命令

```bash
# 1. 进入前端目录
cd frontend

# 2. 运行构建（包含 TypeScript 类型检查）
npm run build

# 3. 或仅构建（跳过类型检查，更快）
vite build
```

### 构建输出

构建产物会输出到：

```
ai_tender_system/web/static/dist/
├── index.html          # 入口 HTML
├── js/                 # JavaScript bundles
├── css/                # 样式文件
├── images/             # 图片资源
├── fonts/              # 字体文件
└── manifest.json       # 资源清单
```

### 构建优化

✅ **代码分割** - 自动拆分 vendor 和业务代码
✅ **Tree Shaking** - 移除未使用的代码
✅ **压缩混淆** - Terser 压缩，移除 console
✅ **资源哈希** - 文件名包含内容哈希，利于缓存
✅ **CSS 提取** - 提取为独立文件，并行加载

---

## ☁️ 阿里云部署

### 方案一：开发模式（推荐用于开发/测试）

在阿里云服务器上同时运行 Vite 开发服务器和 Flask 后端：

```bash
# SSH 登录阿里云
ssh lvhe@8.140.21.235

# 启动 Flask 后端（终端1）
cd /var/www/ai-tender-system
source venv/bin/activate
FLASK_RUN_PORT=8110 python3 -m ai_tender_system.web.app

# 启动 Vue 前端（终端2，需要安装 screen 或 tmux）
cd /var/www/ai-tender-system/frontend
npm run dev -- --host 0.0.0.0
```

**访问地址**:
```
http://8.140.21.235:5173
```

⚠️ **注意**: 需要在阿里云安全组开放 5173 端口

---

### 方案二：生产模式（推荐用于生产环境）

构建后集成到 Flask 应用：

#### 步骤 1: 本地构建

```bash
# 在本地开发机执行
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao/frontend
npm run build
```

#### 步骤 2: 部署到阿里云

```bash
# 提交代码到 Git
git add .
git commit -m "build: Vue前端构建产物"
git push origin master

# SSH 登录阿里云
ssh lvhe@8.140.21.235

# 拉取最新代码
cd /var/www/ai-tender-system
git pull origin master

# 检查构建产物
ls -lh ai_tender_system/web/static/dist/

# 重启应用
sudo supervisorctl restart ai-tender-system
```

#### 步骤 3: 访问 Vue 前端

**访问地址**:
```
http://8.140.21.235/app
```

**路由示例**:
- `/app` - Vue 应用根路径
- `/app/dashboard` - 仪表板
- `/app/knowledge` - 知识库
- `/app/tender` - 标书处理

> **Note**: 所有 `/app/*` 路径都由 Vue Router 处理（SPA 模式）

---

### 方案三：Nginx 反向代理（最佳实践）

修改 Nginx 配置，让 Vue 前端作为默认页面：

```nginx
# /etc/nginx/sites-available/ai-tender-system

server {
    listen 80;
    server_name 8.140.21.235;

    # Vue 前端（默认）
    location / {
        alias /var/www/ai-tender-system/ai_tender_system/web/static/dist/;
        try_files $uri $uri/ /index.html;

        # 缓存策略
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Flask API（旧后端）
    location /api {
        proxy_pass http://localhost:8110;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Flask 传统页面（兼容）
    location /dashboard {
        proxy_pass http://localhost:8110;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

重启 Nginx:

```bash
sudo nginx -t                    # 检查配置
sudo systemctl reload nginx      # 重新加载
```

**访问地址**:
```
http://8.140.21.235              # Vue 前端（默认）
http://8.140.21.235/dashboard    # Flask 旧前端（兼容）
```

---

## 🌐 访问地址总结

### 开发环境

| 前端类型 | 地址 | 说明 |
|---------|------|------|
| Vue 前端 (开发) | http://localhost:5173 | Vite 开发服务器 |
| Flask 旧前端 | http://localhost:8110 | 传统模板渲染 |

### 阿里云生产环境

| 前端类型 | 地址 | 说明 |
|---------|------|------|
| Vue 前端 (集成) | http://8.140.21.235/app | 推荐方式 |
| Vue 前端 (独立) | http://8.140.21.235:5173 | 需开放端口 |
| Flask 旧前端 | http://8.140.21.235 | 当前默认 |
| Flask 仪表板 | http://8.140.21.235/dashboard | 登录后页面 |

---

## ❓ 常见问题

### 1. 构建后访问 `/app` 出现 404

**原因**: 构建产物未生成或路径错误

**解决**:
```bash
# 检查构建产物
ls -lh ai_tender_system/web/static/dist/

# 如果不存在，重新构建
cd frontend && npm run build

# 重启 Flask
sudo supervisorctl restart ai-tender-system
```

---

### 2. API 请求 CORS 错误

**原因**: 跨域配置问题

**解决**:

确保 Flask 启用了 CORS（已在 `app.py` 中配置）:

```python
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

---

### 3. 页面空白，浏览器控制台报错

**原因**: 资源路径错误或构建配置问题

**解决**:

1. 检查 `vite.config.ts` 中的 `base` 配置:

```typescript
export default defineConfig({
  base: '/app/',  // 如果部署到子路径
  // 或
  base: '/',      // 如果部署到根路径
})
```

2. 重新构建:

```bash
npm run build
```

---

### 4. 开发环境 API 代理不工作

**原因**: Flask 后端未启动或端口错误

**解决**:

```bash
# 确认 Flask 运行在 8110 端口
lsof -ti:8110

# 如果没有，启动 Flask
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
FLASK_RUN_PORT=8110 python3 -m ai_tender_system.web.app
```

---

### 5. TypeScript 类型错误导致构建失败

**解决**:

```bash
# 仅构建，跳过类型检查
vite build

# 或修复类型错误后再构建
npm run type-check
npm run build
```

---

## 📊 性能对比

| 指标 | Flask 传统前端 | Vue 3 现代前端 |
|------|--------------|---------------|
| 首屏加载 | ~2.5s | ~800ms |
| 页面切换 | 刷新整页 | 无刷新路由 |
| 交互响应 | 同步阻塞 | 异步流畅 |
| 代码组织 | 混合 HTML/JS | 组件化 |
| 开发体验 | 手动刷新 | HMR 热更新 |
| 类型安全 | 无 | TypeScript |

---

## 🎯 推荐部署流程

### 本地开发

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

### 生产部署

```bash
# 1. 本地构建
cd frontend
npm run build

# 2. 提交代码
git add .
git commit -m "build: 更新Vue前端"
git push

# 3. 阿里云部署
ssh lvhe@8.140.21.235
cd /var/www/ai-tender-system
git pull
sudo supervisorctl restart ai-tender-system

# 4. 访问验证
# http://8.140.21.235/app
```

---

## 📝 版本信息

- **前端版本**: 2.0.0
- **Vue**: 3.4.0
- **Element Plus**: 2.5.4
- **Vite**: 5.0.11
- **构建输出**: `ai_tender_system/web/static/dist/`
- **访问路径**: `/app`

---

**最后更新**: 2025-11-03
**维护者**: lvhe
