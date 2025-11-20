# 阿里云 Linux (Alinux) 部署特别说明

> **重要**: 阿里云ECS默认使用 Alinux 系统，与 Ubuntu/Debian 有所不同

## 🔑 关键差异

| 项目 | Ubuntu/Debian | 阿里云 Linux (Alinux) |
|------|--------------|---------------------|
| 包管理器 | `apt` / `apt-get` | `yum` / `dnf` |
| Python包安装 | `apt install python3-pip` | `yum install python3-pip` |
| 系统更新 | `apt update` | `yum update` |
| Docker | 需要手动安装 | ✅ 通常已预装 |

---

## ✅ 当前服务器环境（已确认）

```bash
服务器IP: 8.140.21.235
操作系统: 阿里云 Linux (Alinux)
Docker: 26.1.3 ✅ 已安装
docker-compose: v2.20.0 ✅ 已安装
python3-pip: 9.0.3 ✅ 已安装
```

---

## 📝 常用命令对照表

### 软件包管理

| 操作 | Ubuntu/Debian | 阿里云 Linux |
|------|--------------|-------------|
| 更新索引 | `sudo apt update` | `sudo yum check-update` |
| 安装软件 | `sudo apt install xxx` | `sudo yum install xxx` |
| 删除软件 | `sudo apt remove xxx` | `sudo yum remove xxx` |
| 搜索软件 | `apt search xxx` | `yum search xxx` |
| 清理缓存 | `sudo apt clean` | `sudo yum clean all` |

### Docker相关

```bash
# 启动Docker服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker

# 检查服务状态
sudo systemctl status docker

# 查看Docker版本
docker --version

# 查看docker-compose版本
docker-compose --version
```

---

## 🚀 快速部署命令（已验证可用）

### 1. 检查环境
```bash
# 检查Docker
docker --version
docker-compose --version

# 检查服务状态
sudo systemctl status docker
```

### 2. 部署应用
```bash
# 进入项目目录
cd /var/www/ai-tender-system

# 拉取最新代码
git pull origin master

# 一键部署
./scripts/docker-deploy.sh
```

### 3. 验证部署
```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试API
curl http://localhost:8110/api/health
```

---

## 🔧 故障排查

### 问题1: 权限不够
```bash
# 症状: permission denied while trying to connect to Docker
# 解决: 将用户加入docker组
sudo usermod -aG docker $USER

# 退出并重新登录
exit
ssh lvhe@8.140.21.235
```

### 问题2: 端口被占用
```bash
# 查找占用8110端口的进程
sudo lsof -ti:8110

# 杀掉进程
sudo lsof -ti:8110 | xargs kill -9

# 或者使用netstat
sudo netstat -tulpn | grep 8110
```

### 问题3: 磁盘空间不足
```bash
# 检查磁盘使用
df -h

# 清理Docker镜像和容器
docker system prune -a

# 清理yum缓存
sudo yum clean all
```

---

## 📦 安装额外软件包

如果需要安装其他工具：

```bash
# 安装开发工具
sudo yum groupinstall -y "Development Tools"

# 安装Git（通常已有）
sudo yum install -y git

# 安装vim编辑器
sudo yum install -y vim

# 安装htop监控工具
sudo yum install -y htop

# 安装网络工具
sudo yum install -y net-tools
```

---

## 🎯 最佳实践

1. **使用yum而非apt**: 阿里云Linux基于CentOS/RHEL，使用yum
2. **Docker已预装**: 大多数阿里云ECS实例已预装Docker
3. **用户组配置**: 记得将用户加入docker组，避免sudo
4. **定期清理**: 使用 `docker system prune` 清理无用镜像
5. **日志监控**: 定期检查 `docker-compose logs`

---

## 📞 技术支持

如遇到问题：
1. 查看Docker日志: `docker-compose logs`
2. 检查系统日志: `journalctl -xe`
3. 验证网络连接: `curl http://localhost:8110/api/health`

---

**创建日期**: 2025-11-20
**维护者**: lvhe
**服务器**: 阿里云ECS (Alinux)
