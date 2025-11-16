# Nginx 配置部署指南

## 📋 配置说明

本目录包含AI智能标书生成平台的Nginx配置文件,用于在阿里云服务器上部署生产环境。

## 🚀 快速部署

### 步骤1: 提交配置文件到Git

在本地执行:

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao

# 添加Nginx配置文件
git add nginx/

# 提交
git commit -m "feat: 添加Nginx配置,修复根路径403错误"

# 推送到远程仓库
git push origin master
```

### 步骤2: 部署到阿里云

SSH登录到阿里云服务器:

```bash
ssh lvhe@8.140.21.235
```

拉取最新代码:

```bash
cd /var/www/ai-tender-system
git pull origin master
```

### 步骤3: 安装Nginx配置

```bash
# 复制配置文件到Nginx目录
sudo cp nginx/ai-tender-system.conf /etc/nginx/sites-available/

# 创建软链接(如果不存在)
sudo ln -sf /etc/nginx/sites-available/ai-tender-system /etc/nginx/sites-enabled/

# 删除默认配置(可选)
sudo rm -f /etc/nginx/sites-enabled/default
```

### 步骤4: 检查配置并重启

```bash
# 测试配置文件语法
sudo nginx -t

# 如果没有错误,重新加载Nginx
sudo systemctl reload nginx

# 或者重启Nginx
sudo systemctl restart nginx
```

### 步骤5: 验证部署

在浏览器访问:

```
http://8.140.21.235
```

应该能看到Vue前端应用的首页! 🎉

## 📁 配置文件说明

### `ai-tender-system.conf`

完整的Nginx配置文件,包含:

#### 1. **根路径映射** (解决403问题)
```nginx
location / {
    root /var/www/ai-tender-system/ai_tender_system/web;
    try_files /static/dist$uri /static/dist$uri/ /static/dist/index.html;
}
```
- ✅ 直接访问 `http://8.140.21.235` 显示Vue应用
- ✅ 支持Vue Router的History模式
- ✅ 刷新页面不会404

#### 2. **API反向代理**
```nginx
location /api {
    proxy_pass http://localhost:8110;
    # ... 其他配置
}
```
- ✅ 所有 `/api/*` 请求转发到Flask后端
- ✅ 支持长时间请求(超时300秒)
- ✅ 支持WebSocket(如果需要)

#### 3. **静态资源优化**
```nginx
location ~* \.(js|css|png|jpg|...)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```
- ✅ JS/CSS文件缓存1年
- ✅ HTML文件不缓存
- ✅ 减少服务器负载

#### 4. **安全配置**
- ✅ 隐藏Nginx版本号
- ✅ 防止点击劫持(X-Frame-Options)
- ✅ 防止XSS攻击
- ✅ 禁止访问隐藏文件

#### 5. **其他功能**
- ✅ 健康检查端点 (`/health`)
- ✅ 错误页面配置
- ✅ 访问日志和错误日志
- ✅ 最大上传文件100MB

## 🌐 URL映射关系

| URL | 映射到 | 说明 |
|-----|--------|------|
| `http://8.140.21.235/` | Vue应用首页 | 默认页面 |
| `http://8.140.21.235/#/parser-comparison` | Vue路由页面 | 目录解析对比 |
| `http://8.140.21.235/api/*` | Flask后端 | API接口 |
| `http://8.140.21.235/static/dist/*` | 静态文件 | 直接访问(兼容) |
| `http://8.140.21.235/health` | 健康检查 | 返回"healthy" |

## 🔧 常见问题

### 1. 403 Forbidden 错误

**原因**: 文件权限问题

**解决**:
```bash
# 修改文件所有者
sudo chown -R www-data:www-data /var/www/ai-tender-system/ai_tender_system/web/static/dist/

# 修改文件权限
sudo chmod -R 755 /var/www/ai-tender-system/ai_tender_system/web/static/dist/
```

### 2. 502 Bad Gateway 错误

**原因**: Flask后端未运行

**解决**:
```bash
# 检查Flask是否在8110端口运行
sudo lsof -ti:8110

# 如果没有,启动Flask
cd /var/www/ai-tender-system
FLASK_RUN_PORT=8110 python3 -m ai_tender_system.web.app
```

### 3. 页面刷新后404

**原因**: `try_files` 配置错误

**解决**: 确保配置文件中有:
```nginx
try_files /static/dist$uri /static/dist$uri/ /static/dist/index.html;
```

### 4. 静态资源加载失败

**原因**: 路径配置错误

**解决**: 检查 `root` 路径是否正确:
```bash
ls -lh /var/www/ai-tender-system/ai_tender_system/web/static/dist/
```

### 5. API请求失败

**原因**: 代理配置错误或Flask未运行

**解决**:
```bash
# 测试Flask是否可访问
curl http://localhost:8110/api/health

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/ai-tender-system-error.log
```

## 📊 性能优化建议

### 1. 启用Gzip压缩

在 `http` 块添加:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript
           application/x-javascript application/xml+rss
           application/json application/javascript;
```

### 2. 启用HTTP/2

```nginx
listen 443 ssl http2;
```

### 3. 添加SSL证书

使用Let's Encrypt免费证书:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🔒 HTTPS配置(可选)

如果有SSL证书,可以启用配置文件末尾的HTTPS部分:

```nginx
server {
    listen 443 ssl http2;
    server_name 8.140.21.235;

    ssl_certificate /etc/nginx/ssl/ai-tender-system.crt;
    ssl_certificate_key /etc/nginx/ssl/ai-tender-system.key;
    # ...
}
```

## 📝 维护命令

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 重新加载配置(不中断服务)
sudo systemctl reload nginx

# 重启Nginx
sudo systemctl restart nginx

# 查看访问日志
sudo tail -f /var/log/nginx/ai-tender-system-access.log

# 查看错误日志
sudo tail -f /var/log/nginx/ai-tender-system-error.log

# 测试配置文件
sudo nginx -t

# 查看当前配置
sudo nginx -T
```

## ✅ 部署检查清单

- [ ] Nginx配置文件已复制到 `/etc/nginx/sites-available/`
- [ ] 软链接已创建到 `/etc/nginx/sites-enabled/`
- [ ] Nginx配置测试通过 (`nginx -t`)
- [ ] Vue构建产物存在于 `/var/www/ai-tender-system/ai_tender_system/web/static/dist/`
- [ ] 文件权限正确 (755, www-data:www-data)
- [ ] Flask后端运行在8110端口
- [ ] Nginx已重新加载
- [ ] 浏览器访问 `http://8.140.21.235` 显示Vue应用
- [ ] API请求正常工作
- [ ] 日志文件可写入

## 📞 支持

如有问题,请查看:
- Nginx错误日志: `/var/log/nginx/ai-tender-system-error.log`
- Flask应用日志: 项目日志目录
- 或联系维护人员

---

**最后更新**: 2025-11-16
**维护者**: lvhe
