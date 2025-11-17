# 部署指南

本文档提供AI智能标书生成平台的完整部署指南，包括开发环境、生产环境的部署步骤和注意事项。

## 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [维护和监控](#维护和监控)

---

## 系统要求

### 硬件要求

- **CPU**: 4核心及以上（推荐8核心）
- **内存**: 8GB RAM（推荐16GB）
- **磁盘**: 50GB可用空间（数据库和文件存储）
- **网络**: 稳定的互联网连接（用于AI模型API调用）

### 软件要求

- **操作系统**:
  - Linux (Ubuntu 20.04+, CentOS 7+)
  - macOS 10.15+
  - Windows 10/11 with WSL2
- **Python**: 3.11 或更高版本
- **数据库**: SQLite 3.x（已内置）
- **Web服务器**（生产环境）: Nginx 1.18+ 或 Apache 2.4+

---

## 快速开始

### 1. 克隆代码仓库

```bash
git clone <repository-url>
cd zhongbiao
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 4. 配置环境变量

创建 `.env` 文件（参考下方[配置说明](#配置说明)章节）：

```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

### 5. 初始化数据库

```bash
python -m ai_tender_system.database.init_db
```

### 6. 启动应用

```bash
# 开发模式（默认端口5000）
python -m ai_tender_system.web.app

# 使用自定义端口
FLASK_RUN_PORT=8080 python -m ai_tender_system.web.app
```

访问 `http://localhost:5000`（或您配置的端口）即可使用系统。

---

## 开发环境部署

### 详细步骤

#### 1. 环境准备

```bash
# 检查Python版本
python3 --version  # 应该 >= 3.11

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv \
    build-essential libssl-dev libffi-dev git

# macOS (使用Homebrew)
brew install python@3.11
```

#### 2. 项目设置

```bash
# 克隆并进入项目目录
git clone <repository-url>
cd zhongbiao

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 包含测试和代码检查工具
```

#### 3. 配置开发环境

创建 `.env` 文件：

```ini
# 开发模式配置
DEBUG=True
FLASK_ENV=development
SECRET_KEY=your-development-secret-key

# 数据库（开发环境使用相对路径）
DATABASE_PATH=ai_tender_system/data/knowledge_base.db

# AI模型配置（至少配置一个）
ACCESS_TOKEN=your_unicom_access_token
# OPENAI_API_KEY=your_openai_key  # 可选
# SHIHUANG_API_KEY=your_shihuang_key  # 可选

# API端点
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1

# 应用端口
FLASK_RUN_PORT=5000
```

#### 4. 初始化数据库

```bash
# 初始化数据库结构
python -m ai_tender_system.database.init_db

# 验证数据库创建
ls -lh ai_tender_system/data/
# 应该看到 knowledge_base.db 文件
```

#### 5. 运行开发服务器

```bash
# 方式1: 直接运行
python -m ai_tender_system.web.app

# 方式2: 使用调试模式
export DEBUG=True
python -m ai_tender_system.web.app

# 方式3: 指定端口
FLASK_RUN_PORT=8080 python -m ai_tender_system.web.app
```

#### 6. 验证安装

打开浏览器访问 `http://localhost:5000`，应该能看到登录页面。

---

## 生产环境部署

### 使用 Gunicorn + Nginx（推荐）

#### 1. 准备生产服务器

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx supervisor

# CentOS/RHEL
sudo yum install -y python3-pip python3-venv nginx supervisor
```

#### 2. 部署应用代码

```bash
# 创建应用目录
sudo mkdir -p /var/www/ai-tender-system
sudo chown $USER:$USER /var/www/ai-tender-system

# 克隆代码
cd /var/www/ai-tender-system
git clone <repository-url> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # 生产环境WSGI服务器
```

#### 3. 配置生产环境

创建 `/var/www/ai-tender-system/.env` 文件：

```ini
# 生产模式配置
DEBUG=False
FLASK_ENV=production
SECRET_KEY=<生成强密钥，使用: python -c "import secrets; print(secrets.token_hex(32))">

# 数据库（生产环境使用绝对路径）
DATABASE_PATH=/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db

# AI模型配置
ACCESS_TOKEN=<生产环境的access_token>
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/www/ai-tender-system/logs/app.log

# 文件上传限制
MAX_CONTENT_LENGTH=104857600  # 100MB
```

#### 4. 初始化数据库

```bash
source venv/bin/activate
python -m ai_tender_system.database.init_db

# 设置数据目录权限
sudo chown -R www-data:www-data ai_tender_system/data/
sudo chmod 755 ai_tender_system/data/
```

#### 5. 配置 Gunicorn

创建 `/var/www/ai-tender-system/gunicorn_config.py`：

```python
# Gunicorn配置文件
import multiprocessing

# 服务器socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # AI调用可能较慢，设置5分钟超时
keepalive = 2

# 日志
accesslog = "/var/www/ai-tender-system/logs/gunicorn-access.log"
errorlog = "/var/www/ai-tender-system/logs/gunicorn-error.log"
loglevel = "info"

# 进程命名
proc_name = "ai-tender-system"

# 安全
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
```

创建日志目录：

```bash
mkdir -p /var/www/ai-tender-system/logs
sudo chown -R www-data:www-data /var/www/ai-tender-system/logs
```

#### 6. 配置 Supervisor（进程管理）

创建 `/etc/supervisor/conf.d/ai-tender-system.conf`：

```ini
[program:ai-tender-system]
command=/var/www/ai-tender-system/venv/bin/gunicorn \
    --config /var/www/ai-tender-system/gunicorn_config.py \
    ai_tender_system.web.app:app
directory=/var/www/ai-tender-system
user=www-data
group=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/www/ai-tender-system/logs/supervisor-stderr.log
stdout_logfile=/var/www/ai-tender-system/logs/supervisor-stdout.log
environment=PATH="/var/www/ai-tender-system/venv/bin"
```

启动Supervisor：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-tender-system

# 检查状态
sudo supervisorctl status ai-tender-system
```

#### 7. 配置 Nginx

创建 `/etc/nginx/sites-available/ai-tender-system`：

```nginx
# AI智能标书生成平台 - Nginx配置
upstream ai_tender_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

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

        # WebSocket支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

启用站点并重启Nginx：

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/ai-tender-system /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

#### 8. 配置 SSL（可选但推荐）

使用 Let's Encrypt 免费SSL证书：

```bash
# 安装certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：
# 0 3 * * * certbot renew --quiet
```

---

## 配置说明

### 环境变量详解

#### 核心配置

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|----------|
| `DEBUG` | 调试模式 | `False` | 否 |
| `FLASK_ENV` | Flask环境 | `production` | 否 |
| `SECRET_KEY` | Flask密钥（用于CSRF保护） | - | **是** |
| `FLASK_RUN_PORT` | 应用端口 | `5000` | 否 |

#### AI模型配置

| 变量名 | 说明 | 是否必需 |
|--------|------|----------|
| `ACCESS_TOKEN` | 中国联通MaaS平台API密钥 | **是**（至少一个） |
| `OPENAI_API_KEY` | OpenAI API密钥 | 否 |
| `SHIHUANG_API_KEY` | 始皇API密钥 | 否 |
| `UNICOM_BASE_URL` | 联通API端点 | 否（有默认值） |

#### 数据库配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_PATH` | SQLite数据库路径 | `ai_tender_system/data/knowledge_base.db` |

#### 文件上传配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MAX_CONTENT_LENGTH` | 最大上传大小（字节） | `104857600` (100MB) |
| `UPLOAD_FOLDER` | 上传文件存储目录 | `ai_tender_system/data/uploads` |

### 生成安全的SECRET_KEY

```bash
# 方法1: Python
python -c "import secrets; print(secrets.token_hex(32))"

# 方法2: OpenSSL
openssl rand -hex 32

# 方法3: 在线生成器（不推荐生产环境）
# https://randomkeygen.com/
```

---

## 常见问题

### Q1: 启动时报错 "ModuleNotFoundError"

**原因**: 未安装依赖或虚拟环境未激活

**解决**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Q2: AI模型调用失败

**原因**:
- API密钥未配置或无效
- 网络连接问题
- API配额超限

**解决**:
1. 检查 `.env` 文件中的 `ACCESS_TOKEN` 是否正确
2. 测试网络连接：`curl https://maas-api.ai-yuanjing.com`
3. 查看日志：`tail -f logs/app.log`

### Q3: 文件上传失败

**原因**:
- 文件过大
- 磁盘空间不足
- 权限问题

**解决**:
```bash
# 检查上传目录权限
ls -ld ai_tender_system/data/uploads/

# 修复权限（生产环境）
sudo chown -R www-data:www-data ai_tender_system/data/

# 检查磁盘空间
df -h
```

### Q4: 数据库锁定错误

**原因**: SQLite在高并发下的限制

**解决**:
1. 短期：重启应用
2. 长期：考虑迁移到PostgreSQL或MySQL

### Q5: Nginx 502 Bad Gateway

**原因**:
- Gunicorn未运行
- 端口配置错误
- 防火墙阻止

**解决**:
```bash
# 检查Gunicorn状态
sudo supervisorctl status ai-tender-system

# 检查端口监听
sudo netstat -tlnp | grep 8000

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/ai-tender-error.log
```

---

## 维护和监控

### 日常维护

#### 1. 日志管理

```bash
# 查看应用日志
tail -f /var/www/ai-tender-system/logs/app.log

# 查看Gunicorn日志
tail -f /var/www/ai-tender-system/logs/gunicorn-error.log

# 清理旧日志（建议定期执行）
find /var/www/ai-tender-system/logs/ -name "*.log" -mtime +30 -delete
```

#### 2. 数据库备份

```bash
# 创建备份脚本 /var/www/ai-tender-system/backup.sh
#!/bin/bash
BACKUP_DIR="/var/backups/ai-tender-system"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db"

mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/knowledge_base_$DATE.db'"

# 保留最近7天的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete

# 添加到crontab
# 0 2 * * * /var/www/ai-tender-system/backup.sh
```

#### 3. 应用更新

```bash
# 1. 停止应用
sudo supervisorctl stop ai-tender-system

# 2. 备份当前版本
cd /var/www
sudo tar -czf ai-tender-system-backup-$(date +%Y%m%d).tar.gz ai-tender-system/

# 3. 拉取最新代码
cd /var/www/ai-tender-system
git pull origin master

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. 运行数据库迁移（如有）
python -m ai_tender_system.database.migrate

# 6. 重启应用
sudo supervisorctl start ai-tender-system

# 7. 验证
sudo supervisorctl status ai-tender-system
curl http://localhost:8000  # 应该返回200
```

### 性能监控

#### 1. 系统资源监控

```bash
# 安装监控工具
sudo apt-get install -y htop iotop

# 实时监控
htop

# 磁盘IO监控
sudo iotop

# 查看应用进程
ps aux | grep gunicorn
```

#### 2. 应用性能监控

建议集成以下工具：
- **APM工具**: New Relic, DataDog, Sentry
- **日志聚合**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **指标监控**: Prometheus + Grafana

#### 3. 数据库优化

```bash
# 分析数据库
sqlite3 ai_tender_system/data/knowledge_base.db "PRAGMA integrity_check;"

# 重建索引
sqlite3 ai_tender_system/data/knowledge_base.db "REINDEX;"

# 清理碎片
sqlite3 ai_tender_system/data/knowledge_base.db "VACUUM;"
```

### 安全加固

1. **防火墙配置**（UFW）:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

2. **定期更新系统**:
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

3. **限制文件权限**:
```bash
sudo chmod 640 /var/www/ai-tender-system/.env
sudo chown www-data:www-data /var/www/ai-tender-system/.env
```

---

## 故障恢复

### 应用崩溃恢复

```bash
# 1. 查看错误日志
sudo tail -100 /var/www/ai-tender-system/logs/gunicorn-error.log

# 2. 重启应用
sudo supervisorctl restart ai-tender-system

# 3. 如果无法重启，检查配置
sudo supervisorctl status
python -m ai_tender_system.web.app  # 测试运行
```

### 数据库损坏恢复

```bash
# 1. 停止应用
sudo supervisorctl stop ai-tender-system

# 2. 备份损坏的数据库
cp ai_tender_system/data/knowledge_base.db ai_tender_system/data/knowledge_base.db.corrupted

# 3. 尝试修复
sqlite3 ai_tender_system/data/knowledge_base.db ".recover" > recovered.sql
sqlite3 new_db.db < recovered.sql
mv new_db.db ai_tender_system/data/knowledge_base.db

# 4. 如果修复失败，从备份恢复
cp /var/backups/ai-tender-system/knowledge_base_latest.db ai_tender_system/data/knowledge_base.db

# 5. 重启应用
sudo supervisorctl start ai-tender-system
```

---

## 扩展阅读

- [Flask生产环境部署最佳实践](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn文档](https://docs.gunicorn.org/)
- [Nginx配置指南](https://nginx.org/en/docs/)
- [Supervisor文档](http://supervisord.org/)

---

## 技术支持

如遇到问题，请：
1. 查看 `logs/` 目录下的日志文件
2. 参考本文档的[常见问题](#常见问题)章节
3. 提交Issue到项目仓库

---

**最后更新时间**: 2025-10-25
**文档版本**: 1.0
