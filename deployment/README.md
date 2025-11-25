# 部署配置文件

本目录包含阿里云服务器的部署配置文件。

## 目录结构

```
deployment/
├── nginx/
│   └── ai-tender.conf.template  # Nginx配置模板
├── update_nginx.sh              # Nginx配置更新脚本（已废弃）
└── README.md                    # 本文件
```

## ⚠️ 重要说明

**当前生产环境配置不在Git仓库中！**

- 📁 **生产配置位置**: `/etc/nginx/conf.d/ai-tender-system.conf`（服务器上）
- 📄 **Git仓库模板**: `deployment/nginx/ai-tender.conf.template`（仅供参考）
- ✅ **安全性**: `git pull` 不会影响生产配置

## 使用说明

### 方案1: 首次部署到新服务器（使用模板）

如果在新服务器上首次部署，可以使用模板：

```bash
# 1. SSH连接到服务器
ssh root@YOUR_SERVER_IP

# 2. 进入项目目录
cd /var/www/ai-tender-system

# 3. 复制模板并修改
cp deployment/nginx/ai-tender.conf.template /tmp/ai-tender-system.conf

# 4. 编辑配置文件，修改所有标记 TODO 的地方
nano /tmp/ai-tender-system.conf

# 需要修改的配置项：
# - server_name: 改为您的IP或域名
# - proxy_pass: 确认Flask应用端口（默认8110）
# - alias 路径: 改为实际项目路径（默认 /var/www/ai-tender-system）

# 5. 复制到nginx配置目录
sudo cp /tmp/ai-tender-system.conf /etc/nginx/conf.d/

# 6. 测试配置
sudo nginx -t

# 7. 重启Nginx
sudo systemctl reload nginx

# 8. 检查状态
sudo systemctl status nginx
```

### 方案2: 更新现有服务器配置（推荐）

**如果服务器已经在运行，直接修改生产配置：**

```bash
# 1. SSH连接到服务器
ssh root@YOUR_SERVER_IP

# 2. 备份当前配置
sudo cp /etc/nginx/conf.d/ai-tender-system.conf \
        /etc/nginx/conf.d/ai-tender-system.conf.backup.$(date +%Y%m%d_%H%M%S)

# 3. 编辑生产配置
sudo nano /etc/nginx/conf.d/ai-tender-system.conf

# 4. 测试配置
sudo nginx -t

# 5. 重启Nginx
sudo systemctl reload nginx
```

## 关键配置说明

### 1. 文件上传限制

```nginx
client_max_body_size 100M;
```

- **默认值**: 1MB（Nginx默认）
- **当前值**: 100MB
- **用途**: 支持上传大型审计报告PDF

### 2. 超时配置

```nginx
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;
```

- **默认值**: 60秒
- **当前值**: 600秒（10分钟）
- **用途**: 大文件上传和PDF转换需要时间

### 3. 静态文件缓存

```nginx
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

- **缓存时间**: 1年
- **用途**: 加速静态资源加载

## 验证配置是否生效

### 检查文件上传限制

```bash
# 查看配置值
sudo grep -r "client_max_body_size" /etc/nginx/

# 应该输出: client_max_body_size 100M;
```

### 查看Nginx日志

```bash
# 访问日志
tail -f /var/log/nginx/ai-tender-access.log

# 错误日志
tail -f /var/log/nginx/ai-tender-error.log
```

### 测试上传功能

访问系统并尝试上传15MB的审计报告PDF：
- ✅ 成功：配置生效
- ❌ 失败（413错误）：配置未生效，检查Nginx配置

## 常见问题

### 1. 413 Request Entity Too Large

**原因**: Nginx文件大小限制未生效

**解决**:
```bash
# 检查是否有其他配置覆盖
sudo nginx -T | grep client_max_body_size

# 确保在http、server或location块中都有配置
```

### 2. 504 Gateway Timeout

**原因**: 后端处理超时（PDF转换慢）

**解决**:
```bash
# 增加超时时间
proxy_read_timeout 1200;  # 20分钟
```

### 3. Nginx配置测试失败

**原因**: 配置文件语法错误

**解决**:
```bash
# 查看详细错误
sudo nginx -t

# 检查配置文件
sudo nano /etc/nginx/sites-available/ai-tender
```

## 更新历史

- **2025-11-23**: 初始版本，支持100MB文件上传
