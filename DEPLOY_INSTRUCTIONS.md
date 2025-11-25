# 🚀 阿里云服务器部署指南

> **服务器信息** (最后更新: 2025-11-25)
> - 🌐 **公网IP**: 60.205.130.182
> - 🔗 **域名**: toubiao.succtech.com (HTTPS)
> - 📁 **项目路径**: /var/www/ai-tender-system
> - 🐍 **Python版本**: 3.11.13 (venv)
> - 🗄️ **数据库**: SQLite (knowledge_base.db)
> - 🔐 **SSL证书**: Let's Encrypt (已配置)

> **当前部署方式**: 传统部署 (Supervisor + Nginx + Gunicorn)
> - ✅ 阿里云环境已完全配置好
> - ✅ Python版本问题已解决
> - ✅ 所有依赖已安装完成
> - ✅ 部署流程稳定可靠
> - ✅ HTTPS域名访问已启用

> **注意**: Docker配置文件(Dockerfile、docker-compose.yml)保留用于Railway等其他平台部署,**阿里云不需要使用Docker**

---

## 📋 部署架构说明

### 当前生产环境 (阿里云)

```
用户请求 (HTTP:80 / HTTPS:443)
    ↓
Nginx 反向代理
    ↓
Gunicorn + Flask (127.0.0.1:8110)
    ↓
Supervisor 进程管理
```

**优势**:
- ✅ 无需Docker,减少复杂度
- ✅ Supervisor自动重启,稳定可靠
- ✅ Nginx静态资源缓存优化
- ✅ HTTPS加密传输,安全可靠
- ✅ 部署流程简单快速

---

## ⚡ 快速参考

### 重启服务

```bash
# 重启应用
sudo supervisorctl restart ai-tender-system

# 重启 Nginx
sudo systemctl reload nginx

# 查看服务状态
sudo supervisorctl status
sudo systemctl status nginx
```

### 查看日志

```bash
# 应用日志
tail -f /var/www/ai-tender-system/logs/supervisor-stdout.log

# Nginx 错误日志
tail -f /var/log/nginx/ai-tender-system-error.log

# Nginx 访问日志
tail -f /var/log/nginx/ai-tender-system-access.log
```

### 更新代码

```bash
cd /var/www/ai-tender-system
git pull origin master
sudo supervisorctl restart ai-tender-system
```

**注意**: Git 仓库中的 nginx 配置文件是模板，实际使用的配置文件在 `/etc/nginx/conf.d/`，不会被 `git pull` 影响。

---

## 🚀 阿里云部署流程 (推荐)

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

### ✅ 4. 环境配置优化
- 修复main.py路径配置问题
- 优化Supervisor进程管理
- 所有依赖已正确安装

---

## 📝 阿里云部署步骤

### 第一步: SSH登录服务器

```bash
ssh root@60.205.130.182
# 密码: BJsdtc@20250912#
```

### 第二步: 进入项目目录并拉取代码

```bash
cd /var/www/ai-tender-system
git pull origin master
```

**注意**: 由于硬盘直接迁移，代码和数据已在服务器上，只需拉取最新更新即可。

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

确保Flask应用正在运行(通过Supervisor管理):

```bash
# 检查Supervisor状态
sudo supervisorctl status ai-tender-system

# 如果未运行,重启服务
sudo supervisorctl restart ai-tender-system

# 查看应用日志
sudo supervisorctl tail -f ai-tender-system stdout
```

### 第七步: 验证部署

在浏览器访问:

```
https://toubiao.succtech.com (推荐，HTTPS加密)
http://60.205.130.182 (备用，IP访问)
```

应该能看到Vue前端应用! 🎉

---

## 🌐 访问地址汇总

部署完成后,可以通过以下地址访问:

### 主应用（推荐）

| URL | 说明 |
|-----|------|
| `https://toubiao.succtech.com` | **HTTPS域名访问** (推荐，安全加密) |
| `http://toubiao.succtech.com` | HTTP访问 (自动跳转到HTTPS) |
| `http://60.205.130.182` | **IP访问** (无HTTPS，仅HTTP) |

### 功能页面

| URL | 说明 |
|-----|------|
| `https://toubiao.succtech.com/#/parser-comparison` | 目录解析对比工具 |
| `https://toubiao.succtech.com/#/tender-management` | 投标管理 |
| `https://toubiao.succtech.com/#/knowledge` | 知识中心 |
| `https://toubiao.succtech.com/api/health` | API健康检查 |
| `https://toubiao.succtech.com/health` | Nginx健康检查 |

### 兼容方式

| URL | 说明 |
|-----|------|
| `http://60.205.130.182/static/dist/index.html` | IP直接访问静态文件 |
| `http://127.0.0.1:8110` | 本地访问Flask后端 (仅服务器内部) |

---

## 🔍 故障排查

### 问题1: 访问 http://60.205.130.182 仍然403

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

**原因**: Flask后端未运行或Supervisor异常

**检查**:
```bash
# 检查Supervisor状态
sudo supervisorctl status ai-tender-system

# 检查端口监听
sudo lsof -ti:8110
```

**修复**:
```bash
# 重启应用
sudo supervisorctl restart ai-tender-system

# 查看错误日志
sudo supervisorctl tail ai-tender-system stderr
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

## 🐳 附录: Docker配置说明

项目中保留了Docker相关配置文件,但**阿里云不使用Docker部署**。这些文件的用途:

### Docker文件列表

| 文件 | 用途 |
|------|------|
| `Dockerfile` | Railway等PaaS平台部署 |
| `Dockerfile.aliyun` | 历史配置,已废弃 |
| `docker-compose.yml` | 本地开发环境(可选) |
| `scripts/docker-deploy.sh` | 历史脚本,已废弃 |
| `scripts/docker-update.sh` | 历史脚本,已废弃 |

### 为什么阿里云不用Docker?

1. ✅ **环境已配置好** - Python、依赖、Nginx等已完全设置
2. ✅ **Supervisor更简单** - 进程管理稳定可靠
3. ✅ **性能更好** - 无容器开销
4. ✅ **运维更方便** - 直接访问文件系统和日志

### 其他平台使用Docker

如需在Railway、Heroku等平台部署,参考:
- Railway: 使用 `Dockerfile`
- 本地开发: 使用 `docker-compose.yml`

---

---

## 🎉 部署完成总结

### ✅ 当前服务器状态（2025-11-25）

**服务器配置**：
- 公网IP: 60.205.130.182
- 域名: toubiao.succtech.com
- 操作系统: Alibaba Cloud Linux 3
- Python: 3.11.13 (虚拟环境)
- 数据库: SQLite

**运行服务**：
- ✅ Supervisor: 管理应用进程（开机自启）
- ✅ Nginx: Web服务器和反向代理（开机自启）
- ✅ Flask应用: 运行在 127.0.0.1:8110
- ✅ SSL证书: Let's Encrypt（已配置）

**配置文件位置**：
- Nginx: `/etc/nginx/conf.d/ai-tender-system.conf`
- Supervisor: `/etc/supervisord.d/ai-tender-system.ini`
- 环境变量: `/var/www/ai-tender-system/.env`
- 数据库: `/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db`

**访问地址**：
- 主域名（推荐）: https://toubiao.succtech.com
- 备用IP: http://60.205.130.182

**部署说明**：
- 硬盘直接从旧服务器(8.140.21.235)迁移
- 代码、数据库、上传文件均完整保留
- 只需更新nginx配置中的IP地址即可

**最后更新**: 2025-11-25
**维护者**: lvhe
**部署方式**: Supervisor + Nginx + Gunicorn（传统部署）
