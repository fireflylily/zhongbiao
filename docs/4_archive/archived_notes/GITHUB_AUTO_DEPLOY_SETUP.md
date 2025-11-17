# GitHub自动部署到阿里云服务器 - 配置指南

> **文档版本**: 1.0
> **创建日期**: 2025-10-31
> **适用系统**: AI智能标书生成平台（Flask + 原生JS）
> **作者**: Claude Code

---

## 📋 目录

- [概述](#概述)
- [前置准备](#前置准备)
- [阶段1：阿里云服务器配置](#阶段1阿里云服务器配置)
- [阶段2：GitHub仓库配置](#阶段2github仓库配置)
- [阶段3：测试部署](#阶段3测试部署)
- [日常使用](#日常使用)
- [故障排查](#故障排查)
- [安全最佳实践](#安全最佳实践)
- [回滚操作](#回滚操作)

---

## 概述

### 部署架构

```
开发者 → GitHub (push到master)
           ↓
    GitHub Actions触发
           ↓
    SSH连接到阿里云服务器
           ↓
    执行部署脚本:
      1. 备份数据库
      2. 拉取最新代码
      3. 安装依赖
      4. 重启服务
      5. 健康检查
           ↓
    部署完成 / 失败回滚
```

### 自动部署功能

- ✅ **自动触发**: Push到master分支自动部署
- ✅ **数据安全**: 每次部署前自动备份数据库
- ✅ **零停机**: Gunicorn优雅重启，不中断服务
- ✅ **健康检查**: 部署后自动验证服务状态
- ✅ **失败回滚**: 部署失败自动回滚到上一版本
- ✅ **完整日志**: GitHub Actions提供详细部署日志

### 时间估算

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 阶段1 | 阿里云服务器配置 | 1-1.5小时 |
| 阶段2 | GitHub仓库配置 | 15分钟 |
| 阶段3 | 测试部署 | 10分钟 |
| **总计** | **首次配置** | **1.5-2小时** |

*注: 配置完成后，日常部署仅需1分钟（git push即可）*

---

## 前置准备

### 需要的信息

在开始前，请准备以下信息：

- [ ] **阿里云服务器信息**
  - 服务器IP地址: `_______________`
  - SSH端口（默认22）: `_______________`
  - 服务器操作系统: Ubuntu 20.04+ / CentOS 7+

- [ ] **GitHub仓库信息**
  - 仓库地址: `https://github.com/fireflylily/zhongbiao.git`
  - 你的GitHub账号是否有仓库管理权限: 是 / 否

- [ ] **生产环境配置**
  - AI模型API密钥（ACCESS_TOKEN）: `_______________`
  - Flask密钥（SECRET_KEY）: 稍后生成
  - 域名（可选）: `_______________`

### 需要的工具

- [ ] SSH客户端（终端、PuTTY等）
- [ ] 浏览器（用于访问GitHub）
- [ ] 文本编辑器（用于编辑配置文件）

---

## 阶段1：阿里云服务器配置

### 步骤1.1：登录服务器并创建部署用户

```bash
# 使用root账户登录（或有sudo权限的账户）
ssh root@your-aliyun-ip

# 创建专用的部署用户
sudo useradd -m -s /bin/bash deploy

# 添加到sudo组（允许执行管理命令）
sudo usermod -aG sudo deploy

# 设置密码（可选，如果需要sudo时输入密码）
# sudo passwd deploy

# 允许deploy用户无密码使用sudo（推荐）
echo "deploy ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/deploy
sudo chmod 440 /etc/sudoers.d/deploy
```

**验证**：
```bash
# 切换到deploy用户
sudo su - deploy

# 确认用户和主目录
whoami    # 应该输出: deploy
pwd       # 应该输出: /home/deploy
```

---

### 步骤1.2：生成SSH密钥对

```bash
# 确保已切换到deploy用户
sudo su - deploy

# 生成SSH密钥对
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy

# 按Enter键（不设置密码，允许无交互部署）
# 按Enter键（确认文件位置）

# 添加公钥到authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# 显示私钥（⚠️ 重要：复制完整内容，稍后添加到GitHub Secrets）
cat ~/.ssh/github_deploy
```

**复制私钥内容**：
- 从 `-----BEGIN OPENSSH PRIVATE KEY-----` 开始
- 到 `-----END OPENSSH PRIVATE KEY-----` 结束
- **包括首尾两行**
- 完整复制，不要遗漏任何字符

**验证SSH密钥**：
```bash
# 测试SSH密钥登录（在另一个终端测试）
ssh -i ~/.ssh/github_deploy deploy@localhost
# 应该能无密码登录成功
```

---

### 步骤1.3：安装必要软件

```bash
# 确保以deploy用户登录
sudo su - deploy

# 更新系统包列表
sudo apt-get update

# 安装Python 3.11和相关工具
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    python3.11-venv \
    build-essential \
    git \
    sqlite3

# 安装Nginx（Web服务器）
sudo apt-get install -y nginx

# 安装Supervisor（进程管理）
sudo apt-get install -y supervisor

# 验证安装
python3.11 --version  # 应该显示 Python 3.11.x
nginx -v              # 应该显示 nginx版本
supervisorctl version # 应该显示 supervisor版本
git --version         # 应该显示 git版本
```

**验证安装成功**：
```bash
# 所有命令都应该显示版本号，无错误
```

---

### 步骤1.4：创建应用目录并克隆代码

```bash
# 确保以deploy用户登录
sudo su - deploy

# 创建应用目录
sudo mkdir -p /var/www/ai-tender-system
sudo chown deploy:deploy /var/www/ai-tender-system

# 切换到应用目录
cd /var/www/ai-tender-system

# 克隆GitHub仓库
git clone https://github.com/fireflylily/zhongbiao.git .

# 验证克隆成功
ls -la
# 应该看到 main.py, requirements-prod.txt 等文件
```

---

### 步骤1.5：配置Python虚拟环境

```bash
# 切换到应用目录
cd /var/www/ai-tender-system

# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装Python依赖
pip install -r requirements-prod.txt

# 安装Gunicorn（WSGI服务器）
pip install gunicorn

# 验证安装
pip list | grep -E "Flask|gunicorn"
# 应该看到 Flask 和 gunicorn 已安装
```

---

### 步骤1.6：配置生产环境变量

```bash
# 切换到应用目录
cd /var/www/ai-tender-system

# 复制配置模板
cp .env.production.example .env

# 生成SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
# 复制输出的密钥

# 编辑.env文件
nano .env
```

**填写以下关键配置**：
```ini
# 必须修改的配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<刚才生成的密钥>
ACCESS_TOKEN=<你的AI模型API密钥>

# 路径配置（使用绝对路径）
DATABASE_PATH=/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db
UPLOAD_FOLDER=/var/www/ai-tender-system/ai_tender_system/data/uploads
OUTPUT_FOLDER=/var/www/ai-tender-system/ai_tender_system/data/outputs
LOG_FILE=/var/www/ai-tender-system/logs/app.log
```

保存并退出：`Ctrl+X` → `Y` → `Enter`

**验证配置**：
```bash
# 检查.env文件权限（应该只有deploy用户可读）
chmod 640 .env
ls -l .env
# 应该显示: -rw-r----- 1 deploy deploy
```

---

### 步骤1.7：初始化数据库

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 初始化数据库
python -m ai_tender_system.database.init_db

# 创建必要的目录
mkdir -p ai_tender_system/data/uploads
mkdir -p ai_tender_system/data/outputs
mkdir -p logs

# 设置数据目录权限
chmod 755 ai_tender_system/data
chmod 755 ai_tender_system/data/uploads
chmod 755 ai_tender_system/data/outputs

# 验证数据库创建
ls -lh ai_tender_system/data/
# 应该看到 knowledge_base.db 文件
```

---

### 步骤1.8：配置Supervisor（进程管理）

```bash
# 创建Supervisor配置文件
sudo nano /etc/supervisor/conf.d/ai-tender-system.conf
```

**粘贴以下内容**：
```ini
[program:ai-tender-system]
command=/var/www/ai-tender-system/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 300 \
    --worker-class sync \
    --preload \
    main:app
directory=/var/www/ai-tender-system
user=deploy
group=deploy
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/www/ai-tender-system/logs/supervisor-stderr.log
stdout_logfile=/var/www/ai-tender-system/logs/supervisor-stdout.log
environment=PATH="/var/www/ai-tender-system/venv/bin"
```

保存并退出：`Ctrl+X` → `Y` → `Enter`

**启动服务**：
```bash
# 重新加载Supervisor配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start ai-tender-system

# 检查状态
sudo supervisorctl status ai-tender-system
# 应该显示: ai-tender-system    RUNNING   pid xxxx, uptime 0:00:xx
```

**验证服务运行**：
```bash
# 检查进程
ps aux | grep gunicorn
# 应该看到多个gunicorn进程

# 测试HTTP响应
curl http://localhost:8000
# 应该返回HTML内容（登录页面）
```

---

### 步骤1.9：配置Nginx（Web服务器）

```bash
# 创建Nginx站点配置
sudo nano /etc/nginx/sites-available/ai-tender-system
```

**粘贴以下内容**（替换your-domain.com为你的域名或IP）：
```nginx
# AI智能标书生成平台 - Nginx配置

upstream ai_tender_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或IP

    # 访问日志
    access_log /var/log/nginx/ai-tender-access.log;
    error_log /var/log/nginx/ai-tender-error.log;

    # 客户端最大请求体大小（文件上传）
    client_max_body_size 100M;

    # 请求超时
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;

    # 静态文件
    location /static/ {
        alias /var/www/ai-tender-system/ai_tender_system/web/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 代理应用请求
    location / {
        proxy_pass http://ai_tender_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

保存并退出：`Ctrl+X` → `Y` → `Enter`

**启用站点并重启Nginx**：
```bash
# 启用站点（创建符号链接）
sudo ln -s /etc/nginx/sites-available/ai-tender-system /etc/nginx/sites-enabled/

# 删除默认站点（可选）
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
sudo nginx -t
# 应该显示: syntax is ok, test is successful

# 重启Nginx
sudo systemctl restart nginx

# 检查Nginx状态
sudo systemctl status nginx
# 应该显示: active (running)
```

**验证Nginx配置**：
```bash
# 测试HTTP访问
curl http://localhost
# 应该返回登录页面HTML

# 如果有公网IP，在浏览器访问
# http://your-aliyun-ip
# 应该看到登录页面
```

---

### 步骤1.10：给脚本添加执行权限

```bash
# 切换到应用目录
cd /var/www/ai-tender-system

# 给部署脚本添加执行权限
chmod +x scripts/deploy.sh
chmod +x scripts/backup_database.sh

# 验证
ls -l scripts/
# 应该看到: -rwxr-xr-x ... deploy.sh
```

---

## 阶段2：GitHub仓库配置

### 步骤2.1：添加GitHub Secrets

1. **访问GitHub仓库设置**：
   ```
   https://github.com/fireflylily/zhongbiao/settings/secrets/actions
   ```

2. **点击 "New repository secret"**

3. **依次添加以下Secrets**：

#### Secret 1: ALIYUN_HOST
- **Name**: `ALIYUN_HOST`
- **Value**: `你的阿里云服务器IP`（如：`123.123.123.123`）
- 点击 **"Add secret"**

#### Secret 2: ALIYUN_USERNAME
- **Name**: `ALIYUN_USERNAME`
- **Value**: `deploy`
- 点击 **"Add secret"**

#### Secret 3: ALIYUN_SSH_PRIVATE_KEY
- **Name**: `ALIYUN_SSH_PRIVATE_KEY`
- **Value**: 粘贴步骤1.2中复制的SSH私钥完整内容
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  （完整的私钥内容）
  -----END OPENSSH PRIVATE KEY-----
  ```
- ⚠️ **重要**: 必须包括首尾两行，不要遗漏任何字符
- 点击 **"Add secret"**

#### Secret 4: ALIYUN_PORT
- **Name**: `ALIYUN_PORT`
- **Value**: `22`（默认SSH端口，如有修改请填实际端口）
- 点击 **"Add secret"**

**验证Secrets已添加**：
- 刷新页面
- 应该看到4个Secrets：
  - `ALIYUN_HOST`
  - `ALIYUN_USERNAME`
  - `ALIYUN_SSH_PRIVATE_KEY`
  - `ALIYUN_PORT`

---

### 步骤2.2：启用GitHub Actions

1. **访问仓库Actions页面**：
   ```
   https://github.com/fireflylily/zhongbiao/actions
   ```

2. **如果提示启用Actions**：
   - 点击 **"I understand my workflows, go ahead and enable them"**

3. **验证Workflow文件存在**：
   - 访问：`https://github.com/fireflylily/zhongbiao/tree/master/.github/workflows`
   - 应该看到 `deploy-aliyun.yml` 文件

---

## 阶段3：测试部署

### 步骤3.1：触发首次部署

**方式1：通过git push触发（推荐）**

```bash
# 在本地项目目录
cd /path/to/zhongbiao

# 拉取最新代码（包含新创建的配置文件）
git pull origin master

# 查看新文件
git status
# 应该看到5个新文件:
#   .github/workflows/deploy-aliyun.yml
#   scripts/deploy.sh
#   scripts/backup_database.sh
#   .env.production.example
#   GITHUB_AUTO_DEPLOY_SETUP.md

# 如果有修改，提交并推送
git add .
git commit -m "feat: 配置GitHub自动部署"
git push origin master
```

**方式2：手动触发**

1. 访问：`https://github.com/fireflylily/zhongbiao/actions`
2. 点击左侧的 **"Deploy to Aliyun Server"**
3. 点击右侧的 **"Run workflow"**
4. 选择 **"master"** 分支
5. 点击 **"Run workflow"**

---

### 步骤3.2：查看部署进度

1. **访问Actions页面**：
   ```
   https://github.com/fireflylily/zhongbiao/actions
   ```

2. **点击最新的workflow运行**：
   - 应该看到黄色圆圈（正在运行）或绿色勾（成功）

3. **查看详细日志**：
   - 点击 **"Deploy to Production"** job
   - 展开各个步骤查看详细输出

**部署步骤日志**：
```
✓ Checkout code
✓ Setup SSH
✓ Add server to known hosts
✓ Deploy to server
  🚀 开始部署到生产环境
  时间: 2025-10-31 12:00:00
  ==========================================
  ✅ 前置检查通过
  ✅ 数据库备份完成
  ✅ 更新到版本: abc123
  ✅ 依赖更新完成
  ✅ 服务重启成功
  ✅ HTTP健康检查通过
  ✅ 部署成功！
✓ Verify deployment
✓ Notify on success
```

---

### 步骤3.3：验证部署成功

**1. 检查GitHub Actions状态**：
- 应该显示绿色勾 ✅

**2. 访问应用**：
```bash
# 在浏览器访问
http://your-aliyun-ip
```
- 应该看到登录页面
- 界面正常显示

**3. SSH登录服务器检查**：
```bash
ssh deploy@your-aliyun-ip

# 检查服务状态
sudo supervisorctl status ai-tender-system
# 应该显示: RUNNING

# 检查最新commit
cd /var/www/ai-tender-system
git log -1
# 应该显示最新的commit

# 查看部署日志
tail -50 logs/deploy.log
# 应该看到最新的部署日志

# 查看应用日志
tail -50 logs/gunicorn-error.log
# 检查是否有错误
```

---

## 日常使用

### 自动部署工作流

```bash
# 1. 本地开发
vim some_file.py

# 2. 提交更改
git add .
git commit -m "feat: 新功能"

# 3. 推送到master（自动触发部署）
git push origin master

# 4. 查看部署进度
# 访问: https://github.com/fireflylily/zhongbiao/actions

# 5. 等待2-3分钟后，新版本自动部署完成
```

**整个过程无需手动操作服务器！**

---

### 手动执行脚本（可选）

**手动部署**：
```bash
ssh deploy@your-aliyun-ip
cd /var/www/ai-tender-system
bash scripts/deploy.sh
```

**手动备份数据库**：
```bash
ssh deploy@your-aliyun-ip
cd /var/www/ai-tender-system
bash scripts/backup_database.sh
```

**查看备份文件**：
```bash
ssh deploy@your-aliyun-ip
ls -lh /var/backups/ai-tender-system/
```

---

## 故障排查

### 问题1：GitHub Actions失败 - SSH连接超时

**症状**：
```
Error: ssh: connect to host xxx.xxx.xxx.xxx port 22: Connection timed out
```

**原因**：
- 服务器防火墙阻止SSH连接
- SSH端口不是22
- 服务器IP地址错误

**解决方案**：

1. **检查防火墙**：
   ```bash
   # 登录服务器
   ssh root@your-aliyun-ip

   # 检查防火墙状态
   sudo ufw status
   # 如果启用了防火墙，添加SSH规则
   sudo ufw allow 22/tcp
   ```

2. **检查阿里云安全组**：
   - 登录阿里云控制台
   - 找到ECS实例 → 安全组
   - 确保允许入站端口22（TCP）

3. **验证SSH端口**：
   ```bash
   # 在服务器上
   sudo netstat -tlnp | grep sshd
   # 确认SSH监听的端口
   ```

---

### 问题2：部署失败 - Permission denied

**症状**：
```
Permission denied (publickey)
```

**原因**：
- SSH私钥配置错误
- authorized_keys权限不正确

**解决方案**：

1. **重新配置SSH密钥**：
   ```bash
   # 登录服务器
   ssh deploy@your-aliyun-ip

   # 检查authorized_keys
   cat ~/.ssh/authorized_keys

   # 检查权限
   ls -la ~/.ssh/
   # authorized_keys应该是600权限

   # 修复权限
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

2. **验证私钥**：
   - 重新查看私钥内容：`cat ~/.ssh/github_deploy`
   - 确保完整复制到GitHub Secrets

---

### 问题3：部署失败 - Gunicorn启动失败

**症状**：
```
❌ Gunicorn服务未运行
```

**原因**：
- 依赖安装失败
- .env配置错误
- 端口被占用

**解决方案**：

1. **查看Supervisor日志**：
   ```bash
   ssh deploy@your-aliyun-ip
   tail -100 /var/www/ai-tender-system/logs/supervisor-stderr.log
   # 查看具体错误信息
   ```

2. **手动测试启动**：
   ```bash
   cd /var/www/ai-tender-system
   source venv/bin/activate
   gunicorn --bind 127.0.0.1:8000 main:app
   # 查看是否有错误
   ```

3. **检查端口占用**：
   ```bash
   sudo netstat -tlnp | grep 8000
   # 如果端口被占用，杀掉进程
   sudo kill -9 <pid>
   ```

---

### 问题4：健康检查失败

**症状**：
```
❌ HTTP健康检查失败
```

**原因**：
- 应用启动慢
- 配置错误导致应用崩溃

**解决方案**：

1. **增加等待时间**：
   - 编辑 `.github/workflows/deploy-aliyun.yml`
   - 将 `sleep 3` 改为 `sleep 10`

2. **查看应用日志**：
   ```bash
   ssh deploy@your-aliyun-ip
   tail -100 /var/www/ai-tender-system/logs/app.log
   tail -100 /var/www/ai-tender-system/logs/gunicorn-error.log
   ```

---

### 问题5：数据库备份失败

**症状**：
```
❌ 数据库备份失败
```

**解决方案**：

1. **检查备份目录权限**：
   ```bash
   ssh deploy@your-aliyun-ip
   sudo mkdir -p /var/backups/ai-tender-system
   sudo chown deploy:deploy /var/backups/ai-tender-system
   sudo chmod 755 /var/backups/ai-tender-system
   ```

2. **手动测试备份**：
   ```bash
   cd /var/www/ai-tender-system
   bash scripts/backup_database.sh
   ```

---

## 安全最佳实践

### 1. SSH密钥管理

- ✅ **使用ed25519密钥**（比RSA更安全）
- ✅ **私钥存储在GitHub Secrets**（加密存储）
- ✅ **定期轮换SSH密钥**（每6个月）
- ❌ **不要在密钥中使用密码**（影响自动化）

### 2. 环境变量安全

- ✅ **SECRET_KEY使用强随机密钥**
- ✅ **.env文件权限设为640**
- ✅ **不要提交.env到git**（已在.gitignore）
- ✅ **定期更换API密钥**

### 3. 服务器安全

- ✅ **禁用root SSH登录**：
  ```bash
  sudo nano /etc/ssh/sshd_config
  # 设置: PermitRootLogin no
  sudo systemctl restart sshd
  ```

- ✅ **配置防火墙**：
  ```bash
  sudo ufw allow 22/tcp
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```

- ✅ **配置SSL证书**（使用Let's Encrypt）：
  ```bash
  sudo apt-get install -y certbot python3-certbot-nginx
  sudo certbot --nginx -d your-domain.com
  ```

### 4. 数据备份

- ✅ **每次部署前自动备份**（已配置）
- ✅ **保留7天备份**（可在.env调整）
- ✅ **定期下载备份到本地**：
  ```bash
  scp deploy@your-aliyun-ip:/var/backups/ai-tender-system/*.gz ./backups/
  ```

---

## 回滚操作

### 自动回滚

部署失败时，GitHub Actions会自动回滚到上一个版本。

### 手动回滚

**回滚到上一个版本**：
```bash
ssh deploy@your-aliyun-ip
cd /var/www/ai-tender-system

# 查看提交历史
git log --oneline -5

# 回滚到指定commit
git reset --hard <commit-hash>

# 重启服务
sudo supervisorctl restart ai-tender-system
```

**回滚数据库**：
```bash
# 查看备份
ls -lh /var/backups/ai-tender-system/

# 选择备份文件
BACKUP_FILE="/var/backups/ai-tender-system/knowledge_base_20251031_120000.db.gz"

# 停止应用
sudo supervisorctl stop ai-tender-system

# 解压并恢复
gunzip -c $BACKUP_FILE > /var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db

# 启动应用
sudo supervisorctl start ai-tender-system
```

---

## 监控和维护

### 定期检查

**每周检查**：
```bash
# 检查磁盘空间
df -h

# 检查备份
ls -lh /var/backups/ai-tender-system/

# 检查日志大小
du -sh /var/www/ai-tender-system/logs/
```

**每月检查**：
```bash
# 更新系统包
sudo apt-get update
sudo apt-get upgrade -y

# 清理旧日志
sudo find /var/www/ai-tender-system/logs -name "*.log" -mtime +30 -delete
```

### 日志查看

**应用日志**：
```bash
tail -f /var/www/ai-tender-system/logs/app.log
```

**Gunicorn日志**：
```bash
tail -f /var/www/ai-tender-system/logs/gunicorn-error.log
```

**Nginx日志**：
```bash
tail -f /var/log/nginx/ai-tender-error.log
```

**Supervisor日志**：
```bash
tail -f /var/www/ai-tender-system/logs/supervisor-stderr.log
```

---

## 常见命令速查

### 服务管理
```bash
# 查看状态
sudo supervisorctl status ai-tender-system

# 启动服务
sudo supervisorctl start ai-tender-system

# 停止服务
sudo supervisorctl stop ai-tender-system

# 重启服务
sudo supervisorctl restart ai-tender-system

# 平滑重启（推荐）
sudo supervisorctl signal HUP ai-tender-system
```

### Nginx管理
```bash
# 测试配置
sudo nginx -t

# 重新加载配置（不中断服务）
sudo nginx -s reload

# 重启Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx
```

### Git操作
```bash
# 查看当前版本
git log -1

# 查看状态
git status

# 拉取最新代码
git pull origin master

# 强制更新到远程版本
git fetch origin master
git reset --hard origin/master
```

---

## 下一步

- ✅ 配置SSL证书（HTTPS）
- ✅ 配置域名解析
- ✅ 集成监控告警（Sentry/钉钉）
- ✅ 配置自动化测试（在部署前运行）
- ✅ 实施蓝绿部署/金丝雀发布

---

## 技术支持

如遇到问题：

1. **查看本文档的[故障排查](#故障排查)章节**
2. **查看GitHub Actions日志**
3. **查看服务器日志**
4. **提交Issue到GitHub仓库**

---

**最后更新**: 2025-10-31
**文档版本**: 1.0
**作者**: Claude Code

**祝部署顺利！🚀**
