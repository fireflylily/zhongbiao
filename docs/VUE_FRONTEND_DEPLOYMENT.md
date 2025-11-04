# Vue前端部署流程文档

> **重要提醒**: Vue前端更新需要**构建**步骤，与Python后端不同！

---

## 📋 快速对比

| 项目 | Python后端 | Vue前端 |
|------|-----------|---------|
| **语言类型** | 解释型 | 编译型（需构建） |
| **是否需要构建** | ❌ 否 | ✅ **是**（关键！） |
| **Git需提交** | 仅源代码 | 源代码 + **构建产物** |
| **阿里云操作** | pull + restart | pull + restart |
| **本地测试命令** | `python -m ...` | `npm run dev` |

---

## 🚀 Vue前端完整更新流程（5步）

### 步骤1: 修改Vue源代码

```bash
# 修改任何Vue文件
vim frontend/src/views/Tender/Management.vue
vim frontend/src/components/**/*.vue
vim frontend/src/router/routes.ts
```

---

### 步骤2: 构建生产版本 ⭐ **关键步骤**

```bash
cd frontend
npm run build

# 构建产物输出到:
# ../ai_tender_system/web/static/dist/
#   ├── index.html
#   ├── js/
#   └── css/
```

**为什么必须构建？**
- 阿里云服务器**没有安装npm**环境
- 无法在服务器上执行`npm run build`
- 必须在本地构建好，提交到Git

---

### 步骤3: 提交源码 + 构建产物

```bash
cd ..  # 回到项目根目录

# 查看更改
git status

# 添加源代码
git add frontend/src/

# ⭐ 必须添加构建产物
git add ai_tender_system/web/static/dist/

# 提交
git commit -m "feat: 前端界面优化 - 投标管理功能增强"

# 推送到GitHub
git push origin master
```

---

### 步骤4: 阿里云拉取代码

```bash
# SSH登录阿里云
ssh lvhe@8.140.21.235

# 进入项目目录
cd /var/www/ai-tender-system

# 拉取最新代码
git pull origin master
```

---

### 步骤5: 重启服务

```bash
# 重启Flask应用
sudo supervisorctl restart ai-tender-system

# 查看状态
sudo supervisorctl status ai-tender-system
```

---

## 🔍 Python后端更新流程（对比）

```bash
# 1. 修改Python代码
vim ai_tender_system/modules/**/*.py

# 2. 提交（无需构建）
git add .
git commit -m "feat: 后端功能更新"
git push origin master

# 3. 阿里云部署
ssh lvhe@8.140.21.235
cd /var/www/ai-tender-system
git pull origin master
sudo supervisorctl restart ai-tender-system
```

**区别**: Python无需构建，直接提交源代码即可。

---

## ⚠️ 常见问题排查

### 问题1: 阿里云显示旧界面

**症状**:
- 本地 `npm run dev` 显示新界面
- 阿里云显示旧界面

**原因**: 忘记构建或忘记提交dist目录

**解决**:
```bash
# 检查最新提交是否包含dist
git log --stat -1 | grep dist

# 如果没有，重新构建并提交
cd frontend && npm run build && cd ..
git add ai_tender_system/web/static/dist/
git commit -m "build: 补充前端构建产物"
git push origin master
```

---

### 问题2: 构建失败

**症状**: `npm run build` 报错

**常见原因**:
- TypeScript类型错误
- 依赖缺失

**解决**:
```bash
# 跳过类型检查构建
npm run build:no-check

# 或先安装依赖
npm install
npm run build
```

---

### 问题3: dist目录太大

**症状**: Git提交很慢，dist目录几MB

**说明**: 这是正常的
- dist包含压缩后的JS/CSS
- 一般2-5MB
- 已在`.gitignore`配置，但构建产物**必须提交**

---

## ✅ 提交前检查清单

在执行`git push`前，确认：

- [ ] 已修改Vue源代码（frontend/src/）
- [ ] 已执行 `npm run build`
- [ ] dist目录有最新文件（检查修改时间）
- [ ] git add包含了dist目录
- [ ] git commit消息清晰
- [ ] 准备好登录阿里云拉取和重启

---

## 🎯 快捷脚本（可选）

创建 `scripts/deploy-frontend.sh`:

```bash
#!/bin/bash
# Vue前端快速部署脚本

echo "🔨 开始构建Vue前端..."
cd frontend
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败，请检查错误信息"
    exit 1
fi

cd ..
echo "✅ 构建完成"

echo "📦 添加构建产物到Git..."
git add ai_tender_system/web/static/dist/
git add frontend/src/

echo "📝 请输入提交信息:"
read -r commit_msg

git commit -m "feat: $commit_msg"
git push origin master

echo "✅ 代码已推送到GitHub"
echo ""
echo "📌 接下来请执行:"
echo "   ssh lvhe@8.140.21.235"
echo "   cd /var/www/ai-tender-system"
echo "   git pull origin master"
echo "   sudo supervisorctl restart ai-tender-system"
```

使用方法:
```bash
chmod +x scripts/deploy-frontend.sh
./scripts/deploy-frontend.sh
```

---

## 📚 相关文档

- `frontend/DEPLOYMENT.md` - 详细部署指南
- `docs/DEPLOYMENT_GUIDE.md` - 生产环境部署
- `frontend/README.md` - 前端开发说明

---

## 🔄 更新记录

| 日期 | 说明 |
|------|------|
| 2025-11-04 | 创建文档，记录Vue前端标准部署流程 |

---

**最后更新**: 2025-11-04
**维护者**: lvhe
