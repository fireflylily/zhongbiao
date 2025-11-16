# 🐳 Docker部署快速参考

## ⚡ 一分钟快速开始

```bash
# 安装Docker（如果未安装）
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose

# 首次部署
cd /var/www/ai-tender-system
./scripts/docker-deploy.sh

# 日常更新
./scripts/docker-update.sh
```

## 📚 常用命令速查

### 服务管理
```bash
docker-compose ps          # 查看状态
docker-compose logs -f     # 查看日志
docker-compose restart     # 重启服务
docker-compose down        # 停止服务
```

### 故障排查
```bash
# 进入容器
docker-compose exec ai-tender-web bash

# 查看环境变量
docker-compose exec ai-tender-web env | grep AZURE

# 手动运行应用（调试）
docker-compose exec ai-tender-web python -m ai_tender_system.web.app
```

### 清理与优化
```bash
# 清理无用镜像（释放空间）
docker system prune -a

# 查看磁盘占用
docker system df

# 重建镜像（解决缓存问题）
docker-compose build --no-cache
```

## 🔧 配置文件说明

- `Dockerfile.aliyun` - Docker镜像定义
- `docker-compose.yml` - 服务编排配置
- `.dockerignore` - 构建时忽略的文件
- `scripts/docker-deploy.sh` - 首次部署脚本
- `scripts/docker-update.sh` - 快速更新脚本

## 📊 性能对比

| 操作 | Docker方式 | 传统方式 |
|------|-----------|---------|
| 首次部署 | 10分钟 | 30分钟+ |
| 日常更新 | 30秒 | 5分钟 |
| 依赖更新 | 2分钟 | 10-15分钟 |
| 回滚 | 10秒 | 5分钟 |

## 🐛 常见问题

### Q: 如何查看服务是否正常？
```bash
docker-compose ps
# 应该显示 "Up" 状态
```

### Q: 如何更新代码？
```bash
./scripts/docker-update.sh
# 或手动
git pull
docker-compose up -d --build
```

### Q: 如何修改环境变量？
```bash
# 1. 编辑.env文件
nano ai_tender_system/.env

# 2. 重启服务生效
docker-compose restart
```

### Q: 端口被占用怎么办？
```bash
# 查看占用8110端口的进程
sudo lsof -ti:8110

# 杀掉进程
sudo lsof -ti:8110 | xargs kill -9

# 重新启动Docker服务
docker-compose up -d
```

## 🔗 相关文档

- 完整部署指南: [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)
- Nginx配置: [nginx/README.md](nginx/README.md)

## 💡 最佳实践

1. **定期清理** - 每周执行 `docker system prune`
2. **查看日志** - 遇到问题先看 `docker-compose logs`
3. **数据备份** - 定期备份 `ai_tender_system/data` 目录
4. **监控资源** - 使用 `docker stats` 查看资源使用

## 🚀 生产环境建议

### 1. 使用systemd管理Docker服务
```bash
sudo nano /etc/systemd/system/ai-tender-docker.service
```

内容：
```ini
[Unit]
Description=AI Tender System Docker Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/ai-tender-system
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

启用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-tender-docker
sudo systemctl start ai-tender-docker
```

### 2. 配置Nginx反向代理（已有配置可跳过）
参考 [nginx/ai-tender-system.conf](nginx/ai-tender-system.conf)

### 3. 设置自动更新（可选）
```bash
# 创建更新cron任务（每天凌晨2点）
crontab -e

# 添加：
0 2 * * * cd /var/www/ai-tender-system && ./scripts/docker-update.sh >> /var/log/ai-tender-update.log 2>&1
```

---

**最后更新**: 2025-11-16
**维护者**: lvhe
