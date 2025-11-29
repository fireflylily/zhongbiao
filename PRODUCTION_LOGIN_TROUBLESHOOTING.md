# 生产环境登录500错误排查指南

## 问题描述
生产环境 `https://toubiao.succtech.com` 登录接口返回 500 Internal Server Error

## 已完成的改进
1. ✅ 添加详细的错误日志（auth_bp.py:148-193）
2. ✅ 增加数据库文件存在性检查
3. ✅ 增加session保存异常处理
4. ✅ 记录完整的堆栈跟踪信息

## 最可能的原因及解决方案

### 1. 🔴 数据库文件不存在或路径错误（最常见）

**症状**：500错误，日志显示"数据库文件不存在"

**排查方法**：
```bash
# SSH登录到阿里云服务器
ssh your-server

# 检查数据库文件是否存在
ls -la /path/to/project/ai_tender_system/data/knowledge_base.db

# 检查文件权限
ls -lh /path/to/project/ai_tender_system/data/
```

**解决方案**：
```bash
# 1. 如果文件不存在，从本地上传数据库
scp ai_tender_system/data/knowledge_base.db user@server:/path/to/project/ai_tender_system/data/

# 2. 确保文件权限正确
chmod 644 /path/to/project/ai_tender_system/data/knowledge_base.db
chown www-data:www-data /path/to/project/ai_tender_system/data/knowledge_base.db
```

### 2. 🔴 bcrypt模块未安装

**症状**：500错误，日志显示密码验证相关错误

**排查方法**：
```bash
# 在服务器上检查bcrypt是否安装
python3 -c "import bcrypt; print('bcrypt已安装')"
```

**解决方案**：
```bash
# 安装bcrypt
pip3 install bcrypt

# 或使用requirements.txt安装所有依赖
pip3 install -r requirements.txt
```

### 3. 🟡 Flask SECRET_KEY未配置

**症状**：Session保存失败

**排查方法**：
查看Flask配置文件或环境变量中是否设置了SECRET_KEY

**解决方案**：
在 `ai_tender_system/config/config.ini` 中确保有以下配置：
```ini
[web]
secret_key = your-secret-key-here-change-this-in-production
```

### 4. 🟡 数据库文件损坏

**排查方法**：
```bash
# 尝试打开数据库
sqlite3 /path/to/knowledge_base.db "SELECT * FROM users LIMIT 1;"
```

**解决方案**：
如果数据库损坏，从备份恢复或重新初始化数据库

### 5. 🟢 文件系统权限问题

**症状**：无法读取数据库文件

**解决方案**：
```bash
# 确保Web服务器用户有读权限
chmod 755 /path/to/project/ai_tender_system/data/
chmod 644 /path/to/project/ai_tender_system/data/knowledge_base.db
```

## 查看日志的方法

### 1. 应用日志
```bash
# 如果使用systemd
journalctl -u your-app-name -f

# 如果使用supervisor
tail -f /var/log/supervisor/your-app.log

# 如果使用uWSGI
tail -f /var/log/uwsgi/app.log

# 如果使用Gunicorn
tail -f /var/log/gunicorn/error.log
```

### 2. Nginx错误日志
```bash
tail -f /var/log/nginx/error.log
```

### 3. 应用自定义日志
查看 `ai_tender_system/logs/` 目录下的日志文件

## 测试登录接口

在服务器上直接测试登录接口：
```bash
curl -X POST http://localhost:端口号/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -v
```

## 紧急修复步骤

1. **立即重启应用服务**
   ```bash
   # systemd
   sudo systemctl restart your-app-name

   # supervisor
   sudo supervisorctl restart your-app-name
   ```

2. **检查是否是数据库文件问题**
   - 确认数据库文件存在
   - 确认文件权限正确

3. **检查Python依赖**
   ```bash
   pip3 list | grep bcrypt
   pip3 list | grep Flask
   ```

4. **查看最新的错误日志**
   - 现在日志会包含详细的堆栈跟踪
   - 查找"登录过程发生错误"关键字

## 下次部署前的检查清单

- [ ] 确认数据库文件已上传
- [ ] 确认bcrypt已安装
- [ ] 确认SECRET_KEY已配置
- [ ] 确认文件权限正确
- [ ] 测试登录接口
- [ ] 检查应用日志是否正常

## 需要的信息

请提供以下信息以便进一步诊断：

1. **服务器日志**（最重要）
   - 应用错误日志
   - Nginx错误日志

2. **数据库文件状态**
   ```bash
   ls -la /path/to/ai_tender_system/data/knowledge_base.db
   ```

3. **Python环境信息**
   ```bash
   python3 --version
   pip3 list
   ```

4. **部署方式**
   - 使用的是 uWSGI/Gunicorn/其他？
   - 使用的是 systemd/supervisor/其他？

## 联系方式

如需进一步帮助，请提供：
1. 完整的错误日志（最近50行）
2. 数据库文件状态
3. Python依赖列表
