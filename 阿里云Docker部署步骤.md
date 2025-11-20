# 阿里云Docker部署 - 最简步骤

> **服务器系统**: 阿里云 Linux (Alinux) - 使用 `yum` 包管理器

## 📋 一、首次部署（3步完成）

### 1. 登录服务器
```bash
ssh lvhe@8.140.21.235
cd /var/www/ai-tender-system
```

### 2. 确认Docker环境（通常已预装）
```bash
# 检查Docker版本
docker --version
# 输出: Docker version 26.1.3, build b72abbb

# 检查docker-compose版本
docker-compose --version
# 输出: Docker Compose version v2.20.0

# 启动并启用Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户加入docker组（避免每次使用sudo）
sudo usermod -aG docker $USER
```

**如果 docker-compose 未安装**，使用以下命令：
```bash
# 阿里云Linux使用yum安装pip3
sudo yum install -y python3-pip
sudo pip3 install docker-compose

# 验证安装
docker-compose --version
```

**然后重新登录SSH使配置生效**

### 3. 一键部署
```bash
git pull origin master
./scripts/docker-deploy.sh
```

等待10分钟，完成！✅

---

## 🔄 二、日常更新代码（1步完成）

```bash
cd /var/www/ai-tender-system
./scripts/docker-update.sh
```

等待30秒，完成！✅

---

## 🔍 三、常用检查命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试API
curl http://localhost:8110/api/health
```

---

## 🆘 四、遇到问题怎么办

### 问题1: docker-compose命令不存在
```bash
# 阿里云Linux使用yum（不是apt）
sudo yum install -y python3-pip
sudo pip3 install docker-compose
```

### 问题2: 权限拒绝 (permission denied)
```bash
# 将用户加入docker组
sudo usermod -aG docker $USER

# 退出并重新登录SSH
exit
ssh lvhe@8.140.21.235
```

### 问题3: 端口被占用
```bash
sudo lsof -ti:8110 | xargs kill -9
docker-compose down
docker-compose up -d
```

### 问题4: 服务无法启动
```bash
# 查看详细错误
docker-compose logs

# 进入容器调试
docker-compose exec ai-tender-web bash
python -m ai_tender_system.web.app
```

---

## 📊 五、对比传统部署的优势

| 操作 | Docker方式 | 传统方式 |
|------|-----------|---------|
| 首次部署 | ✅ 10分钟 | ❌ 30分钟+ |
| 日常更新 | ✅ 30秒 | ❌ 5分钟 |
| Python版本 | ✅ 3.11统一 | ❌ 3.6不兼容 |
| 依赖安装 | ✅ 稳定快速 | ❌ 经常中断 |
| 回滚速度 | ✅ 10秒 | ❌ 5分钟 |

---

## 📚 更多文档

- 详细部署指南: [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)
- Docker快速参考: [DOCKER_README.md](DOCKER_README.md)
- Nginx配置: [nginx/README.md](nginx/README.md)

---

## 💻 服务器环境信息

- **服务器IP**: 8.140.21.235
- **操作系统**: 阿里云 Linux (Alinux)
- **包管理器**: yum (不是apt)
- **Docker版本**: 26.1.3
- **Docker Compose**: v2.20.0
- **Python**: 3.x (系统自带)
- **应用端口**: 8110

---

**最后更新**: 2025-11-20
**问题反馈**: lvhe
**服务器**: 阿里云ECS (Alinux系统)
