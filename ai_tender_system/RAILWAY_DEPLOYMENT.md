# Railway 部署指南

本文档说明如何将 AI 标书系统部署到 Railway 平台。

## 前置要求

1. [Railway 账号](https://railway.app/)
2. GitHub 账号（用于连接代码仓库）
3. Git 已安装并配置

## 部署步骤

### 1. 准备代码仓库

首先，确保你的代码已经推送到 GitHub 仓库：

```bash
git add .
git commit -m "准备 Railway 部署"
git push origin main
```

### 2. 在 Railway 创建项目

1. 访问 [Railway Dashboard](https://railway.app/dashboard)
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权 Railway 访问你的 GitHub 账号
5. 选择包含此项目的仓库

### 3. 配置环境变量

在 Railway 项目设置中，添加以下环境变量：

#### 必需的环境变量

```bash
# Flask 配置
FLASK_ENV=production
SECRET_KEY=<生成一个强随机密钥>

# AI 模型配置
AI_MODEL_API_KEY=<你的 AI 模型 API 密钥>
AI_MODEL_BASE_URL=<AI 模型 API 地址>
DEFAULT_MODEL=<默认使用的模型名称>

# 数据库配置（如果使用外部数据库）
DATABASE_URL=<数据库连接字符串>

# 其他配置
MAX_CONTENT_LENGTH=52428800  # 50MB 文件上传限制
```

#### 可选环境变量

```bash
# Redis 配置（如果需要缓存）
REDIS_URL=<Redis 连接字符串>

# 日志级别
LOG_LEVEL=INFO
```

### 4. 生成 SECRET_KEY

使用 Python 生成一个安全的密钥：

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### 5. 部署

Railway 会自动检测到以下文件并开始部署：

- `Procfile` - 定义如何运行应用
- `requirements.txt` - Python 依赖
- `runtime.txt` - Python 版本
- `railway.json` - Railway 配置

部署过程包括：
1. 安装 Python 3.11.9
2. 安装依赖包（`pip install -r requirements.txt`）
3. 启动 Gunicorn WSGI 服务器

### 6. 数据库迁移

如果需要初始化数据库，可以在 Railway 的终端中运行：

```bash
python -c "from database.db_manager import init_database; init_database()"
```

或者添加到部署后钩子。

### 7. 检查部署状态

1. 在 Railway Dashboard 中查看部署日志
2. 等待部署完成（通常 2-5 分钟）
3. 点击 "View Logs" 查看应用运行日志
4. 访问 Railway 提供的 URL 测试应用

### 8. 自定义域名（可选）

1. 在项目设置中点击 "Settings"
2. 找到 "Domains" 部分
3. 点击 "Add Domain"
4. 输入你的自定义域名
5. 按照提示配置 DNS 记录

## 文件说明

### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 "web.app:create_app()"
```

- `web`: 定义 web 服务
- `--bind 0.0.0.0:$PORT`: 绑定到 Railway 提供的端口
- `--workers 4`: 使用 4 个工作进程
- `--timeout 120`: 请求超时时间 120 秒（适合 AI 处理）

### runtime.txt
```
python-3.11.9
```
指定 Python 版本

### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

配置构建和部署参数

### .railwayignore
排除不需要部署的文件，减小部署包大小

## 常见问题

### 1. 部署失败：依赖安装错误

检查 `requirements.txt` 中的包版本是否兼容。某些包可能需要系统级依赖。

**解决方案**：
- 查看构建日志中的错误信息
- 更新或固定包版本
- 某些包可能需要添加系统依赖到 `nixpacks.toml`

### 2. 应用启动失败

**可能原因**：
- 环境变量未正确配置
- 数据库连接失败
- 端口配置错误

**解决方案**：
- 检查所有必需的环境变量
- 查看应用日志：`railway logs`
- 确保使用 `$PORT` 环境变量

### 3. 文件上传失败

Railway 的临时文件系统在重启后会清空。

**解决方案**：
- 使用外部对象存储（如 AWS S3, Cloudinary）
- 配置持久化卷（Railway Volumes）

### 4. AI 模型请求超时

某些 AI 处理可能耗时较长。

**解决方案**：
- 增加 Gunicorn 的 `--timeout` 值
- 使用异步任务队列（Celery + Redis）
- 实现请求重试机制

### 5. 内存不足

AI 模型和向量处理可能占用大量内存。

**解决方案**：
- 升级 Railway 计划以获得更多资源
- 优化代码，减少内存占用
- 使用批处理和流式处理

## 性能优化建议

1. **启用 CDN**：对静态文件使用 CDN
2. **数据库优化**：使用数据库索引，优化查询
3. **缓存策略**：使用 Redis 缓存频繁访问的数据
4. **异步处理**：将耗时任务移至后台队列
5. **监控告警**：配置应用监控和错误追踪

## 扩展资源

- [Railway 官方文档](https://docs.railway.app/)
- [Gunicorn 配置](https://docs.gunicorn.org/en/stable/settings.html)
- [Flask 生产部署](https://flask.palletsprojects.com/en/2.3.x/deploying/)

## 持续集成

Railway 支持自动部署。当你推送代码到 GitHub 时，Railway 会自动：
1. 拉取最新代码
2. 重新构建应用
3. 执行部署
4. 进行健康检查

## 回滚

如果新部署出现问题：
1. 在 Railway Dashboard 中找到 "Deployments"
2. 选择之前的稳定版本
3. 点击 "Redeploy" 回滚

## 成本估算

Railway 提供免费额度，超出部分按使用量计费：
- **Free Tier**: $5/月免费额度
- **Pro Plan**: $20/月起

建议在生产环境中使用 Pro 计划以获得更好的性能和支持。

## 支持

如有问题，请参考：
- Railway Discord 社区
- GitHub Issues
- 项目文档
