# AI标书系统 - 阿里云部署指南

## 📋 目录
- [系统要求](#系统要求)
- [方案一：快速部署（Docker）](#方案一快速部署docker)
- [方案二：传统部署（Python环境）](#方案二传统部署python环境)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 系统要求

### 服务器配置推荐
- **CPU**: 2核及以上
- **内存**: 4GB及以上（建议8GB）
- **硬盘**: 40GB及以上
- **操作系统**: CentOS 7+、Ubuntu 18.04+、Alibaba Cloud Linux

### 端口要求
- **8110**: Web服务端口（可在`.env`中修改）
- **22**: SSH端口
- **80/443**: （可选）用于Nginx反向代理

---

## 方案一：快速部署（Docker）

### 1. 安装Docker

```bash
# CentOS/Alibaba Cloud Linux
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Ubuntu
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 创建部署文件

**创建 `Dockerfile`:**

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    antiword \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY ai_tender_system/ /app/ai_tender_system/
COPY frontend/ /app/frontend/

# 安装Python依赖
RUN pip install --no-cache-dir \
    flask==2.3.3 \
    flask-cors==4.0.0 \
    flask-compress==1.14 \
    python-docx==0.8.11 \
    openpyxl==3.1.2 \
    python-dotenv==1.0.0 \
    requests==2.31.0 \
    azure-ai-formrecognizer>=3.3.0

# 暴露端口
EXPOSE 8110

# 启动命令
CMD ["python3", "-m", "ai_tender_system.web.app"]
```

**创建 `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  ai-tender-system:
    build: .
    container_name: ai_tender_system
    restart: always
    ports:
      - "8110:8110"
    volumes:
      - ./ai_tender_system/data:/app/ai_tender_system/data
      - ./logs:/app/logs
    environment:
      - WEB_HOST=0.0.0.0
      - WEB_PORT=8110
      - DEBUG=False
    env_file:
      - ./ai_tender_system/.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8110/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 3. 部署步骤

```bash
# 1. 上传代码到服务器
# 使用scp或git clone

# 2. 配置环境变量
cd /path/to/zhongbiao
cp ai_tender_system/.env.example ai_tender_system/.env
vi ai_tender_system/.env  # 编辑配置

# 3. 构建并启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 检查服务状态
docker-compose ps
```

### 4. 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并重启
docker-compose down
docker-compose up -d --build
```

---

## 方案二：传统部署（Python环境）

### 1. 安装系统依赖

```bash
# CentOS/Alibaba Cloud Linux
sudo yum update -y
sudo yum install -y python39 python39-devel gcc gcc-c++ antiword

# Ubuntu
sudo apt update
sudo apt install -y python3.9 python3.9-dev python3-pip gcc g++ antiword
```

### 2. 安装Python依赖

```bash
# 升级pip
python3 -m pip install --upgrade pip

# 安装核心依赖
pip3 install -r requirements.txt

# 或手动安装主要依赖
pip3 install flask==2.3.3 flask-cors==4.0.0 flask-compress==1.14
pip3 install python-docx==0.8.11 openpyxl==3.1.2
pip3 install python-dotenv==1.0.0 requests==2.31.0
pip3 install azure-ai-formrecognizer>=3.3.0
```

### 3. 配置环境变量

```bash
cd /path/to/zhongbiao
cp ai_tender_system/.env.example ai_tender_system/.env

# 编辑配置文件
vi ai_tender_system/.env
```

**关键配置项：**
```bash
# Web服务配置
WEB_HOST=0.0.0.0
WEB_PORT=8110
DEBUG=False
SECRET_KEY=your-secret-key-here  # 请修改为随机字符串

# API密钥（必填）
DEFAULT_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-key
ACCESS_TOKEN=your-unicom-token

# Azure Form Recognizer（如需OCR）
AZURE_FORM_RECOGNIZER_KEY=your-azure-key
AZURE_FORM_RECOGNIZER_ENDPOINT=your-azure-endpoint

# Gemini API（如需文档解析）
GEMINI_API_KEY=your-gemini-key
```

### 4. 启动服务

**方式1：直接运行（测试）**
```bash
cd ai_tender_system
python3 -m web.app
```

**方式2：使用Gunicorn（生产推荐）**
```bash
# 安装Gunicorn
pip3 install gunicorn

# 启动服务（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:8110 --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  ai_tender_system.web.app:create_app()
```

**方式3：使用Supervisor（开机自启）**

安装Supervisor:
```bash
# CentOS
sudo yum install -y supervisor
sudo systemctl enable supervisord
sudo systemctl start supervisord

# Ubuntu
sudo apt install -y supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor
```

创建配置文件 `/etc/supervisord.d/ai_tender_system.ini`:
```ini
[program:ai_tender_system]
command=/usr/bin/python3 -m web.app
directory=/path/to/zhongbiao/ai_tender_system
user=your_user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai_tender_system.log
environment=PYTHONPATH="/path/to/zhongbiao"
```

启动服务:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai_tender_system
sudo supervisorctl status
```

### 5. 配置Nginx反向代理（可选）

安装Nginx:
```bash
# CentOS
sudo yum install -y nginx

# Ubuntu
sudo apt install -y nginx
```

创建配置文件 `/etc/nginx/conf.d/ai_tender_system.conf`:
```nginx
upstream ai_tender_backend {
    server 127.0.0.1:8110;
}

server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或IP

    client_max_body_size 50M;

    # 前端静态文件
    location /static/ {
        alias /path/to/zhongbiao/ai_tender_system/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API代理
    location / {
        proxy_pass http://ai_tender_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

启动Nginx:
```bash
sudo nginx -t  # 测试配置
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 6. 配置防火墙

```bash
# CentOS/Alibaba Cloud Linux (firewalld)
sudo firewall-cmd --permanent --add-port=8110/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload

# Ubuntu (ufw)
sudo ufw allow 8110/tcp
sudo ufw allow 80/tcp
sudo ufw reload
```

**阿里云安全组配置：**
1. 登录阿里云控制台
2. 进入 ECS 实例管理
3. 点击"安全组" → "配置规则"
4. 添加入方向规则：
   - 端口范围: `8110/8110` 或 `80/80`
   - 授权对象: `0.0.0.0/0`（所有IP）或指定IP段

---

## 配置说明

### 环境变量配置

**必需配置：**
```bash
# API密钥（至少配置一个）
DEFAULT_API_KEY=xxx        # 默认AI模型密钥
OPENAI_API_KEY=xxx         # OpenAI密钥
ACCESS_TOKEN=xxx           # 联通元景密钥
GEMINI_API_KEY=xxx         # Google Gemini密钥

# Web服务
WEB_HOST=0.0.0.0          # 监听地址
WEB_PORT=8110             # 服务端口
DEBUG=False               # 生产环境必须为False
SECRET_KEY=random-string  # 会话密钥（请修改）
```

**可选配置：**
```bash
# OCR配置
ENABLE_OCR=true
AZURE_FORM_RECOGNIZER_KEY=xxx
AZURE_FORM_RECOGNIZER_ENDPOINT=xxx

# 上传限制
MAX_UPLOAD_SIZE=50        # MB
ALLOWED_EXTENSIONS=pdf,doc,docx,txt

# 企业征信API
ENTERPRISE_CREDIT_BASE_URL=xxx
ENTERPRISE_CREDIT_API_KEY=xxx
```

### 数据目录结构

```
ai_tender_system/data/
├── uploads/              # 上传文件存储
├── knowledge_base.db     # SQLite数据库
├── parser_debug/         # 解析调试文件
├── configs/              # 配置文件
└── logs/                 # 日志文件
```

**确保目录权限：**
```bash
chmod 755 ai_tender_system/data
chmod 777 ai_tender_system/data/uploads
chmod 777 ai_tender_system/data/logs
```

---

## 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
sudo lsof -i:8110
sudo netstat -tunlp | grep 8110

# 修改端口
vi ai_tender_system/.env
# 将 WEB_PORT 改为其他端口
```

### 2. 依赖安装失败

```bash
# 使用国内镜像
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 或手动安装问题包
pip3 install --upgrade pip setuptools wheel
pip3 install azure-ai-formrecognizer>=3.3.0
```

### 3. 数据库初始化

```bash
# 首次运行会自动创建数据库，如需手动初始化：
cd ai_tender_system
python3 -c "from common.database import get_knowledge_base_db; db = get_knowledge_base_db(); print('数据库初始化成功')"
```

### 4. 文件上传失败

检查：
- 文件大小是否超过`MAX_UPLOAD_SIZE`（默认50MB）
- 文件类型是否在`ALLOWED_EXTENSIONS`中
- `data/uploads`目录权限是否正确（需要写权限）

### 5. API调用失败

检查：
- API密钥是否正确配置
- 网络是否可以访问API端点
- API配额是否充足

查看日志：
```bash
tail -f ai_tender_system/data/logs/ai_tender_system.log
```

### 6. 内存不足

如果服务器内存小于4GB，建议：
```bash
# 减少Gunicorn工作进程数
gunicorn -w 2 -b 0.0.0.0:8110 ...

# 或关闭OCR功能
vi ai_tender_system/.env
# ENABLE_OCR=false
```

### 7. 服务自动重启

**使用Systemd（推荐）：**

创建 `/etc/systemd/system/ai-tender-system.service`:
```ini
[Unit]
Description=AI Tender System
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/zhongbiao/ai_tender_system
Environment="PYTHONPATH=/path/to/zhongbiao"
ExecStart=/usr/bin/python3 -m web.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-tender-system
sudo systemctl start ai-tender-system
sudo systemctl status ai-tender-system
```

### 8. 查看运行日志

```bash
# 应用日志
tail -f ai_tender_system/data/logs/ai_tender_system.log

# Supervisor日志
tail -f /var/log/ai_tender_system.log

# Systemd日志
sudo journalctl -u ai-tender-system -f

# Docker日志
docker-compose logs -f
```

### 9. 性能优化

**使用Redis缓存（可选）：**
```bash
# 安装Redis
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis

# 在代码中配置Redis（需要修改代码）
```

**数据库优化：**
```bash
# 如数据量大，建议迁移到MySQL/PostgreSQL
# 参考 database/migrate_to_mysql.sql
```

---

## 监控和维护

### 健康检查

```bash
# 检查服务是否正常
curl http://localhost:8110/api/health

# 预期响应
{"status": "healthy", "timestamp": "2025-12-24T15:00:00"}
```

### 备份数据

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/data/backups/ai_tender_system"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp ai_tender_system/data/knowledge_base.db $BACKUP_DIR/knowledge_base_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz ai_tender_system/data/uploads/

# 删除7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
```

定时备份（crontab）：
```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

---

## 安全建议

1. **修改默认密钥**：`.env`中的`SECRET_KEY`
2. **启用HTTPS**：配置SSL证书（Let's Encrypt）
3. **限制访问IP**：Nginx配置IP白名单
4. **定期更新**：定期更新系统和依赖包
5. **日志审计**：定期检查日志文件
6. **数据备份**：每日自动备份数据库

---

## 技术支持

如遇到部署问题，请查看：
- 项目GitHub仓库：https://github.com/fireflylily/zhongbiao
- 日志文件：`ai_tender_system/data/logs/ai_tender_system.log`
- 系统日志：`/var/log/messages` 或 `/var/log/syslog`

---

**部署完成后，访问 `http://your-server-ip:8110` 即可使用系统！** 🎉
