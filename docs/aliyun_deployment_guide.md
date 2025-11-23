# 阿里云部署指南

## 前提条件

### 1. 阿里云资源
- ✅ ECS服务器 (推荐配置: 4核8G,Ubuntu 20.04/22.04)
- ✅ 公网IP地址
- ✅ 安全组配置(开放8110端口)
- ✅ (可选) 域名和SSL证书

### 2. 本地准备
- ✅ GitHub仓库已更新
- ✅ 代码已提交和推送

## 部署步骤

### 第一步: 连接到阿里云服务器

```bash
# SSH连接到服务器
ssh root@你的服务器IP

# 或使用密钥
ssh -i ~/.ssh/your_key.pem root@你的服务器IP
```

### 第二步: 安装基础环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# 安装Git
sudo apt install git -y

# 安装Node.js (用于前端构建,可选)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 验证安装
python3 --version
node --version
npm --version
git --version
```

### 第三步: 克隆项目代码

```bash
# 创建项目目录
mkdir -p /var/www
cd /var/www

# 克隆GitHub仓库
git clone https://github.com/fireflylily/zhongbiao.git
cd zhongbiao

# 检查代码
ls -la
```

### 第四步: 安装Python依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 安装Playwright(可选,如需浏览器自动化)
pip install playwright
playwright install chromium
```

### 第五步: 配置环境变量

```bash
# 复制环境变量模板
cd ai_tender_system
cp .env.example .env

# 编辑配置
nano .env
```

配置示例:
```ini
# Web服务配置
WEB_HOST=0.0.0.0
WEB_PORT=8110
WEB_DEBUG=False  # 生产环境必须设为False
WEB_SECRET_KEY=你的随机密钥字符串

# LLM API配置
LLM_API_BASE=https://maas-gz.ai-yuanjing.com/maas/v1
LLM_API_KEY=你的API密钥
LLM_MODEL=gpt-4o-mini

# 文件路径(使用绝对路径)
DATA_DIR=/var/www/zhongbiao/ai_tender_system/data
```

生成随机密钥:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 第六步: 初始化数据库

```bash
# 确保数据目录存在
mkdir -p data/{uploads,outputs,logs}

# 首次运行会自动初始化数据库
python3 -m ai_tender_system.web.app &

# 检查日志
tail -f data/logs/web_app.log

# 如果成功,停止测试进程
pkill -f "python3 -m ai_tender_system.web.app"
```

### 第七步: 配置Systemd服务(推荐)

创建服务文件:

```bash
sudo nano /etc/systemd/system/ai-tender.service
```

内容:
```ini
[Unit]
Description=AI Tender System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/zhongbiao
Environment="PATH=/var/www/zhongbiao/venv/bin"
ExecStart=/var/www/zhongbiao/venv/bin/python3 -m ai_tender_system.web.app
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/ai-tender/access.log
StandardError=append:/var/log/ai-tender/error.log

[Install]
WantedBy=multi-user.target
```

创建日志目录:
```bash
sudo mkdir -p /var/log/ai-tender
sudo chown root:root /var/log/ai-tender
```

启动服务:
```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start ai-tender

# 设置开机自启
sudo systemctl enable ai-tender

# 查看状态
sudo systemctl status ai-tender

# 查看日志
sudo journalctl -u ai-tender -f
```

### 第八步: 配置Nginx反向代理(推荐)

安装Nginx:
```bash
sudo apt install nginx -y
```

配置Nginx:
```bash
sudo nano /etc/nginx/sites-available/ai-tender
```

内容:
```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    # 客户端最大上传大小
    client_max_body_size 100M;

    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8110;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时配置
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }

    # 静态文件缓存
    location /static/ {
        alias /var/www/zhongbiao/ai_tender_system/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

启用配置:
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/ai-tender /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx

# 设置开机自启
sudo systemctl enable nginx
```

### 第九步: 配置SSL证书(可选,推荐)

使用Let's Encrypt免费证书:

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书(自动配置Nginx)
sudo certbot --nginx -d 你的域名

# 证书自动续期
sudo certbot renew --dry-run
```

### 第十步: 配置防火墙

```bash
# 安装UFW
sudo apt install ufw -y

# 允许SSH
sudo ufw allow 22/tcp

# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果直接访问8110端口
sudo ufw allow 8110/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

## 更新部署

当有代码更新时:

```bash
# 连接到服务器
ssh root@你的服务器IP

# 进入项目目录
cd /var/www/zhongbiao

# 激活虚拟环境
source venv/bin/activate

# 拉取最新代码
git pull origin master

# 更新依赖(如有变化)
pip install -r requirements.txt

# 重启服务
sudo systemctl restart ai-tender

# 查看状态
sudo systemctl status ai-tender
```

## 监控和维护

### 查看日志

```bash
# 查看应用日志
tail -f /var/log/ai-tender/access.log
tail -f /var/log/ai-tender/error.log

# 查看系统服务日志
sudo journalctl -u ai-tender -f

# 查看应用内部日志
tail -f /var/www/zhongbiao/ai_tender_system/data/logs/web_app.log
```

### 性能监控

```bash
# 查看进程资源占用
htop

# 查看端口监听
sudo netstat -tulpn | grep 8110

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 常见问题排查

#### 1. 服务无法启动

```bash
# 查看详细错误
sudo journalctl -u ai-tender -n 50

# 手动测试运行
cd /var/www/zhongbiao
source venv/bin/activate
python3 -m ai_tender_system.web.app
```

#### 2. 端口被占用

```bash
# 查找占用进程
sudo lsof -i :8110

# 杀死进程
sudo kill -9 PID
```

#### 3. 权限问题

```bash
# 设置正确的文件权限
cd /var/www/zhongbiao
sudo chown -R root:root .
sudo chmod -R 755 ai_tender_system
sudo chmod -R 777 ai_tender_system/data  # 数据目录需要写权限
```

## 数据备份

### 备份脚本

创建备份脚本:
```bash
nano /root/backup_ai_tender.sh
```

内容:
```bash
#!/bin/bash
BACKUP_DIR="/root/backups/ai-tender"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /var/www/zhongbiao/ai_tender_system/data/knowledge_base.db \
   $BACKUP_DIR/knowledge_base_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz \
    /var/www/zhongbiao/ai_tender_system/data/uploads

# 删除7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
```

设置定时任务:
```bash
# 添加执行权限
chmod +x /root/backup_ai_tender.sh

# 编辑crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /root/backup_ai_tender.sh >> /var/log/ai-tender-backup.log 2>&1
```

## 性能优化

### 1. 使用Gunicorn替代Flask开发服务器

安装Gunicorn:
```bash
source /var/www/zhongbiao/venv/bin/activate
pip install gunicorn
```

修改systemd服务文件:
```ini
[Service]
ExecStart=/var/www/zhongbiao/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8110 \
    --timeout 300 \
    --access-logfile /var/log/ai-tender/gunicorn-access.log \
    --error-logfile /var/log/ai-tender/gunicorn-error.log \
    ai_tender_system.web.app:create_app()
```

### 2. 配置数据库优化

编辑 `.env`:
```ini
# SQLite性能优化
DB_PRAGMA_CACHE_SIZE=10000
DB_PRAGMA_JOURNAL_MODE=WAL
```

### 3. 启用CDN(可选)

将静态资源上传到阿里云OSS,配置CDN加速。

## 监控告警(可选)

### 使用阿里云监控

1. 登录阿里云控制台
2. 进入云监控服务
3. 添加ECS监控
4. 配置告警规则:
   - CPU使用率 > 80%
   - 内存使用率 > 80%
   - 磁盘使用率 > 85%
   - 应用进程存活检查

## 安全加固

### 1. 修改SSH端口

```bash
sudo nano /etc/ssh/sshd_config
# 修改 Port 22 为其他端口,如 2222

sudo systemctl restart sshd
```

### 2. 配置fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. 定期更新系统

```bash
# 设置自动安全更新
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 快速部署脚本

将以下内容保存为 `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "=== AI标书系统 - 阿里云部署脚本 ==="

# 变量配置
PROJECT_DIR="/var/www/zhongbiao"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="ai-tender"

# 1. 更新代码
echo "[1/5] 拉取最新代码..."
cd $PROJECT_DIR
git pull origin master

# 2. 更新依赖
echo "[2/5] 更新Python依赖..."
source $VENV_DIR/bin/activate
pip install -r requirements.txt

# 3. 前端构建(如果有变化)
echo "[3/5] 构建前端..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 4. 数据库迁移(如果需要)
echo "[4/5] 检查数据库..."
# 这里添加数据库迁移脚本

# 5. 重启服务
echo "[5/5] 重启服务..."
sudo systemctl restart $SERVICE_NAME

# 验证
sleep 3
sudo systemctl status $SERVICE_NAME

echo "=== 部署完成 ==="
echo "访问地址: http://$(curl -s ifconfig.me):8110"
```

使用方法:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 域名配置

### 1. 解析域名到服务器

在域名DNS管理中添加A记录:
```
类型: A
主机记录: @  (或 www)
记录值: 你的服务器公网IP
TTL: 600
```

### 2. 更新Nginx配置

```bash
sudo nano /etc/nginx/sites-available/ai-tender
```

修改 `server_name`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # ... 其他配置
}
```

重启Nginx:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 3. 配置SSL(使用Let's Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 故障恢复

### 从备份恢复

```bash
# 停止服务
sudo systemctl stop ai-tender

# 恢复数据库
cp /root/backups/ai-tender/knowledge_base_YYYYMMDD_HHMMSS.db \
   /var/www/zhongbiao/ai_tender_system/data/knowledge_base.db

# 恢复上传文件
tar -xzf /root/backups/ai-tender/uploads_YYYYMMDD_HHMMSS.tar.gz -C /

# 启动服务
sudo systemctl start ai-tender
```

## 检查清单

部署完成后,检查以下项目:

- [ ] 服务正常运行: `sudo systemctl status ai-tender`
- [ ] 端口正常监听: `sudo netstat -tulpn | grep 8110`
- [ ] 网页可以访问: `curl http://localhost:8110`
- [ ] 数据库正常: 检查 `data/knowledge_base.db` 文件存在
- [ ] 日志正常输出: `tail -f /var/log/ai-tender/access.log`
- [ ] 文件上传功能正常
- [ ] PDF转图片功能正常
- [ ] LLM API调用正常

## 技术支持

如遇问题:
1. 查看日志: `/var/log/ai-tender/` 和 `ai_tender_system/data/logs/`
2. 检查GitHub Issues
3. 联系技术团队

## 附录

### A. 阿里云ECS推荐配置

| 项目 | 最低配置 | 推荐配置 | 说明 |
|------|---------|---------|------|
| CPU | 2核 | 4核 | 用于AI处理和并发请求 |
| 内存 | 4GB | 8GB | 运行Python和Playwright |
| 硬盘 | 40GB | 100GB SSD | 存储上传文件和数据库 |
| 带宽 | 1Mbps | 5Mbps | 影响文件下载速度 |
| 系统 | Ubuntu 20.04 | Ubuntu 22.04 LTS | 稳定性和兼容性 |

### B. 成本估算

- ECS(4核8G,5M带宽): 约300-500元/月
- 域名: 约50-100元/年
- SSL证书: 免费(Let's Encrypt)
- OSS存储(可选): 按使用量计费

**总计: 约350-550元/月**

### C. 扩展性建议

当用户量增长时:
1. 升级ECS配置
2. 使用Redis缓存
3. 配置负载均衡(SLB)
4. 分离数据库服务(RDS)
5. 使用OSS存储文件

## 更新历史

- **2025-11-23**: 初始版本,基于当前系统架构
