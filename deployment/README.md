# 部署配置文件

本目录包含阿里云服务器的部署配置文件。

## 目录结构

```
deployment/
├── nginx/
│   └── ai-tender.conf      # Nginx配置文件
├── update_nginx.sh         # Nginx配置更新脚本
└── README.md               # 本文件
```

## 使用说明

### 在阿里云服务器上更新Nginx配置

#### 方法1: 使用自动化脚本（推荐）

```bash
# 1. SSH连接到阿里云服务器
ssh root@8.140.21.235

# 2. 进入项目目录
cd /var/www/zhongbiao

# 3. 拉取最新配置
git pull origin master

# 4. 运行更新脚本
cd deployment
sudo ./update_nginx.sh
```

脚本会自动：
- ✅ 备份当前配置
- ✅ 复制新配置
- ✅ 测试配置正确性
- ✅ 重启Nginx服务
- ✅ 验证服务状态

#### 方法2: 手动配置

```bash
# 1. 复制配置文件
sudo cp deployment/nginx/ai-tender.conf /etc/nginx/sites-available/ai-tender

# 2. 创建软链接（如果不存在）
sudo ln -s /etc/nginx/sites-available/ai-tender /etc/nginx/sites-enabled/

# 3. 测试配置
sudo nginx -t

# 4. 重启Nginx
sudo systemctl restart nginx

# 5. 检查状态
sudo systemctl status nginx
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
