# 🚀 阿里云服务器部署指南

> **推荐部署方式**: 使用Docker（见下方Docker部署章节）
> - ✅ 解决Python版本不兼容问题
> - ✅ 依赖安装稳定快速
> - ✅ 日常更新仅需30秒
> - ✅ 环境完全一致

---

## 📋 部署方式选择

| 特性 | Docker部署 ⭐推荐 | 传统部署 |
|------|-----------------|---------|
| Python版本 | ✅ 3.11统一 | ❌ 3.6不兼容 |
| 依赖安装 | ✅ 2分钟 | ❌ 10-15分钟 |
| 日常更新 | ✅ 30秒 | ❌ 5分钟 |
| 环境一致性 | ✅ 完全一致 | ❌ 容易出问题 |
| 回滚速度 | ✅ 10秒 | ❌ 5分钟 |
| 学习成本 | 🟡 需要了解Docker | ✅ 无 |

---

## 🐳 方式一：Docker部署（推荐）

### 优势
1. **解决Python版本问题** - 阿里云Python 3.6 → Docker Python 3.11
2. **依赖安装快速稳定** - 使用清华镜像源，首次5分钟，后续秒级
3. **环境完全隔离** - 不影响系统原有环境
4. **一键部署更新** - 简化运维流程

### 前置要求

检查Docker是否安装：
```bash
docker --version
docker-compose --version
```

如果未安装：
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 安装docker-compose
sudo apt install docker-compose

# 将当前用户加入docker组（避免每次sudo）
sudo usermod -aG docker $USER
# 重新登录生效
```

### 首次部署步骤

```bash
# 1. SSH登录服务器
ssh lvhe@8.140.21.235

# 2. 进入项目目录
cd /var/www/ai-tender-system

# 3. 拉取最新代码（包含Docker配置）
git pull origin master

# 4. 确认环境变量已配置
cat ai_tender_system/.env | grep AZURE

# 5. 一键部署（首次约10分钟）
./scripts/docker-deploy.sh
```

### 日常更新（30秒）

```bash
cd /var/www/ai-tender-system
./scripts/docker-update.sh
```

### 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 进入容器调试
docker-compose exec ai-tender-web bash
```

### Docker部署故障排查

#### 问题1: docker-compose: command not found
```bash
sudo apt update
sudo apt install docker-compose
```

#### 问题2: 权限拒绝 (Permission denied)
```bash
sudo usermod -aG docker $USER
# 重新登录SSH
```

#### 问题3: 服务无法启动
```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
sudo lsof -ti:8110 | xargs kill -9

# 重新部署
docker-compose down
./scripts/docker-deploy.sh
```

#### 问题4: 健康检查失败
```bash
# 进入容器检查
docker-compose exec ai-tender-web bash
python -m ai_tender_system.web.app

# 检查环境变量
docker-compose exec ai-tender-web env | grep AZURE
```

---

## 🔧 方式二：传统部署（不推荐，仅作备份）

> ⚠️ 注意：阿里云默认Python 3.6无法运行，需要先升级Python或手动降级依赖版本

### 本次更新内容

已完成以下修复和优化:

### ✅ 1. 修复根路径403错误
- 创建完整Nginx配置
- 支持直接访问 `http://8.140.21.235` 显示Vue应用
- 优化静态资源缓存策略

### ✅ 2. 修复parser-comparison页面
- 添加 `requiresAuth: false` 配置
- 无需登录即可访问调试工具
- 重新构建Vue应用

### ✅ 3. 添加新用户
- huangjf (智慧足迹公司,内部员工)
- lvhe (智慧足迹公司,内部员工)

### ✅ 4. Docker化部署支持
- 添加Dockerfile.aliyun和docker-compose.yml
- 提供一键部署和更新脚本
- 解决Python版本和依赖问题

---

## 🔧 阿里云部署步骤

### 第一步: SSH登录服务器

```bash
ssh lvhe@8.140.21.235
```

### 第二步: 进入项目目录并拉取代码

```bash
cd /var/www/ai-tender-system
git pull origin master
```

你应该看到:

```
From https://github.com/fireflylily/zhongbiao
   63f7f301..2aa81f06  master     -> origin/master
Updating 63f7f301..2aa81f06
Fast-forward
 ai_tender_system/database/add_users.py         | 136 +++++++++
 ai_tender_system/web/static/dist/js/index.js   |   2 +-
 frontend/src/router/routes.ts                  |   3 +-
 nginx/README.md                                | 421 +++++++++++++++++++++++++
 nginx/ai-tender-system.conf                    | 167 ++++++++++
 5 files changed, 727 insertions(+), 2 deletions(-)
```

### 第三步: 添加新用户到数据库 (可选)

如果需要在阿里云上也添加这两个用户:

```bash
python3 ai_tender_system/database/add_users.py
```

### 第四步: 部署Nginx配置

```bash
# 1. 复制Nginx配置文件
sudo cp nginx/ai-tender-system.conf /etc/nginx/sites-available/

# 2. 创建软链接
sudo ln -sf /etc/nginx/sites-available/ai-tender-system /etc/nginx/sites-enabled/

# 3. 测试配置
sudo nginx -t
```

应该看到:

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 第五步: 重启Nginx

```bash
sudo systemctl reload nginx
```

或者:

```bash
sudo systemctl restart nginx
```

### 第六步: 检查Flask后端

确保Flask应用正在运行:

```bash
# 检查8110端口
sudo lsof -ti:8110

# 如果没有输出,启动Flask
cd /var/www/ai-tender-system
FLASK_RUN_PORT=8110 python3 -m ai_tender_system.web.app &
```

### 第七步: 验证部署

在浏览器访问:

```
http://8.140.21.235
```

应该能看到Vue前端应用! 🎉

---

## 🌐 访问地址汇总

部署完成后,可以通过以下地址访问:

### 主应用

| URL | 说明 |
|-----|------|
| `http://8.140.21.235` | **Vue前端首页** (推荐,通过Nginx) |
| `http://8.140.21.235:8110/#/` | Vue前端首页 (直接访问Flask) |

### 功能页面

| URL | 说明 |
|-----|------|
| `http://8.140.21.235/#/parser-comparison` | 目录解析对比工具 |
| `http://8.140.21.235/#/tender-management` | 投标管理 |
| `http://8.140.21.235/#/knowledge` | 知识中心 |
| `http://8.140.21.235/api/health` | API健康检查 |
| `http://8.140.21.235/health` | Nginx健康检查 |

### 兼容方式

| URL | 说明 |
|-----|------|
| `http://8.140.21.235/static/dist/index.html` | 直接访问静态文件 |
| `http://8.140.21.235:8110` | Flask旧版前端 (如果需要) |

---

## 🔍 故障排查

### 问题1: 访问 http://8.140.21.235 仍然403

**检查**:
```bash
# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/ai-tender-system-error.log

# 检查静态文件权限
ls -lh /var/www/ai-tender-system/ai_tender_system/web/static/dist/
```

**修复**:
```bash
# 修改文件权限
sudo chown -R www-data:www-data /var/www/ai-tender-system/ai_tender_system/web/static/dist/
sudo chmod -R 755 /var/www/ai-tender-system/ai_tender_system/web/static/dist/
```

### 问题2: 502 Bad Gateway

**原因**: Flask后端未运行

**检查**:
```bash
sudo lsof -ti:8110
```

**修复**:
```bash
cd /var/www/ai-tender-system
FLASK_RUN_PORT=8110 python3 -m ai_tender_system.web.app &
```

### 问题3: API请求失败

**检查**:
```bash
# 测试Flask API
curl http://localhost:8110/api/health

# 查看Flask日志
tail -f /var/www/ai-tender-system/logs/app.log
```

### 问题4: 页面空白

**原因**: 静态资源路径错误

**检查**:
```bash
# 确认构建产物存在
ls -lh /var/www/ai-tender-system/ai_tender_system/web/static/dist/

# 查看浏览器控制台错误
# F12 -> Console
```

---

## 📝 Nginx配置说明

新的Nginx配置包含以下特性:

### ✅ 根路径映射
```nginx
location / {
    root /var/www/ai-tender-system/ai_tender_system/web;
    try_files /static/dist$uri /static/dist$uri/ /static/dist/index.html;
}
```

### ✅ API反向代理
```nginx
location /api {
    proxy_pass http://localhost:8110;
    # 支持长时间请求(300秒)
    # 支持WebSocket
}
```

### ✅ 静态资源优化
- JS/CSS文件缓存1年
- HTML文件不缓存
- Gzip压缩

### ✅ 安全配置
- 隐藏Nginx版本号
- 防止点击劫持
- XSS保护

---

## 🎯 推荐的生产环境配置

### 1. 使用Systemd管理Flask

创建服务文件:

```bash
sudo nano /etc/systemd/system/ai-tender-system.service
```

内容:

```ini
[Unit]
Description=AI Tender System Flask Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-tender-system
Environment="FLASK_RUN_PORT=8110"
ExecStart=/usr/bin/python3 -m ai_tender_system.web.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-tender-system
sudo systemctl start ai-tender-system
sudo systemctl status ai-tender-system
```

### 2. 配置日志轮转

```bash
sudo nano /etc/logrotate.d/ai-tender-system
```

内容:

```
/var/log/nginx/ai-tender-system-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1
    endscript
}
```

### 3. 设置防火墙

```bash
# 允许HTTP
sudo ufw allow 80/tcp

# 允许HTTPS (如果配置了SSL)
sudo ufw allow 443/tcp

# 检查状态
sudo ufw status
```

---

## 📊 性能监控

### 检查Nginx状态

```bash
# 查看连接数
sudo netstat -anp | grep nginx | wc -l

# 查看访问日志
sudo tail -f /var/log/nginx/ai-tender-system-access.log

# 查看错误日志
sudo tail -f /var/log/nginx/ai-tender-system-error.log
```

### 检查Flask性能

```bash
# 查看进程
ps aux | grep python

# 查看内存使用
free -h

# 查看磁盘使用
df -h
```

---

## 🔐 安全建议

### 1. 配置HTTPS (推荐)

使用Let's Encrypt免费SSL证书:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 2. 限制IP访问 (可选)

在Nginx配置中添加:

```nginx
location / {
    allow 192.168.1.0/24;  # 允许的IP段
    deny all;               # 拒绝其他所有IP
    # ...
}
```

### 3. 配置fail2ban防止暴力破解

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📞 联系支持

如有问题,请:

1. 检查日志文件
2. 查看本文档的故障排查部分
3. 联系维护人员

---

## 📌 重要提示

✅ **记得重启Nginx**: 修改配置后必须重启
✅ **检查端口**: 确保8110端口的Flask应用正在运行
✅ **文件权限**: 确保www-data用户有权限访问静态文件
✅ **防火墙**: 确保80端口已开放

---

**部署完成后访问**: `http://8.140.21.235`
**最后更新**: 2025-11-16
**维护者**: lvhe
