# 环境管理指南

## 📋 概述

本项目采用**双环境依赖策略**：
- **本地开发环境**：完整依赖 (`requirements.txt`) - 约2-3GB
- **阿里云生产环境**：轻量依赖 (`requirements-prod.txt`) - 约500MB

这是**有意设计**的架构，而非问题！

---

## 🔄 两种环境的差异

### 本地开发环境 (`requirements.txt`)

**特点**：
- ✅ 包含完整的机器学习库
- ✅ 可以离线运行模型
- ✅ 适合开发和调试
- ❌ 磁盘占用大 (~2-3GB)
- ❌ 安装时间长

**包含的大型依赖**：
```python
torch>=2.0.0              # ~2GB - PyTorch深度学习框架
transformers>=4.30.0      # ~500MB - HuggingFace模型
sentence-transformers     # ~100MB - 句子嵌入
scikit-learn              # 机器学习工具
celery                    # 异步任务队列
redis                     # 缓存
```

**适用场景**：
- 本地开发和测试
- 离线环境
- 需要训练/微调模型
- 性能调优和实验

---

### 阿里云生产环境 (`requirements-prod.txt`)

**特点**：
- ✅ 轻量级，快速部署
- ✅ 磁盘占用小 (~500MB)
- ✅ 通过API调用AI服务
- ❌ 需要网络连接
- ❌ 依赖外部API

**移除的大型依赖**：
```python
# 已移除（改用API）:
# torch>=2.0.0              (~2GB) - 改用 Embeddings API
# transformers>=4.30.0      (~500MB) - 改用 Embeddings API
# sentence-transformers     (~100MB) - 改用 Embeddings API
# scikit-learn              - 向量计算改用numpy
# celery                    - 暂不需要异步队列
# redis                     - 暂不需要缓存
```

**保留的核心依赖**：
```python
Flask==2.3.3              # Web框架
openai>=1.0.0             # OpenAI SDK (用于API调用)
PyMuPDF>=1.23.0           # PDF解析
python-docx>=0.8.11       # Word文档
langchain>=0.1.0          # 文本处理
faiss-cpu>=1.7.4          # 向量检索
numpy>=1.24.0             # 数值计算
```

**适用场景**：
- 生产服务器部署
- 云端运行
- 磁盘空间有限
- 快速部署和更新

---

## 🛠️ 环境检查和切换

### 检查当前环境

```bash
# 本地环境检查
bash scripts/check_environment.sh local

# 生产环境检查（阿里云）
bash scripts/check_environment.sh remote
```

**检查内容**：
- Python版本 (>= 3.11)
- 虚拟环境状态
- 核心依赖包安装情况
- 环境特定依赖
- .env配置完整性

---

### 本地切换到生产依赖

如果你想在本地测试生产环境配置：

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 备份当前环境（可选）
pip freeze > requirements-backup.txt

# 3. 卸载大型依赖（可选）
pip uninstall torch transformers sentence-transformers -y

# 4. 安装生产依赖
pip install -r requirements-prod.txt

# 5. 验证环境
bash scripts/check_environment.sh remote
```

---

### 生产环境切换到完整依赖

**⚠️ 不推荐在阿里云服务器上安装完整依赖！**

原因：
- 磁盘空间不足（torch需要2GB+）
- 安装时间过长（可能超时）
- 内存占用大
- 无必要（API方式更高效）

如果确实需要：

```bash
# 在阿里云服务器执行
cd /var/www/ai-tender-system
source venv/bin/activate

# 检查磁盘空间
df -h  # 确保至少有5GB可用空间

# 安装完整依赖（预计10-30分钟）
pip install -r requirements.txt --no-cache-dir

# ⚠️ 注意：这会大幅增加磁盘占用和部署时间
```

---

## 📝 环境配置清单

### 本地开发环境 `.env`

```ini
# 开发模式
DEBUG=True
FLASK_ENV=development
SECRET_KEY=your-development-secret-key

# 数据库（相对路径）
DATABASE_PATH=ai_tender_system/data/knowledge_base.db

# AI模型（至少配置一个）
ACCESS_TOKEN=your_unicom_access_token

# API端点
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1

# 端口
FLASK_RUN_PORT=5000
```

### 阿里云生产环境 `.env`

```ini
# 生产模式
DEBUG=False
FLASK_ENV=production
SECRET_KEY=<强密钥，使用: python -c "import secrets; print(secrets.token_hex(32))">

# 数据库（绝对路径）
DATABASE_PATH=/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db

# AI模型（必需）
ACCESS_TOKEN=<生产环境token>
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1

# 日志
LOG_LEVEL=INFO
LOG_FILE=/var/www/ai-tender-system/logs/app.log

# 文件上传
MAX_CONTENT_LENGTH=104857600  # 100MB
```

---

## 🚀 部署流程对比

### 本地开发环境部署

```bash
# 1. 克隆代码
git clone <repository-url>
cd zhongbiao

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖（完整版）
pip install -r requirements.txt

# 4. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 5. 初始化数据库
python -m ai_tender_system.database.init_db

# 6. 启动应用
python -m ai_tender_system.web.app

# 总耗时：约15-30分钟（取决于网络）
```

---

### 阿里云生产环境部署

```bash
# 1. SSH登录
ssh lvhe@8.140.21.235

# 2. 进入项目目录
cd /var/www/ai-tender-system

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 拉取最新代码
git pull origin master

# 5. 安装/更新依赖（轻量版）
pip install -r requirements-prod.txt --upgrade

# 6. 重启应用
sudo supervisorctl restart ai-tender-system

# 总耗时：约2-5分钟
```

或者使用**自动部署脚本**：

```bash
# 在阿里云服务器执行
cd /var/www/ai-tender-system
bash scripts/deploy.sh

# 脚本会自动：
# - 备份数据库
# - 拉取代码
# - 更新依赖（使用 requirements-prod.txt）
# - 构建前端
# - 重启服务
# - 健康检查
```

---

## ⚠️ 常见问题

### Q1: 阿里云安装依赖时报错 "No module named 'torch'"

**原因**：生产环境不应该安装torch

**解决**：
```bash
# 确认使用的是生产依赖
cat requirements-prod.txt | grep torch
# 应该没有输出

# 如果代码中引用了torch，需要修改为API调用
```

---

### Q2: 本地运行提示 "Embeddings API调用失败"

**原因**：本地可以使用离线模型，不需要API

**解决**：
1. 检查 `common/config.py` 中的模型配置
2. 确保安装了完整依赖 (`requirements.txt`)
3. 或者配置 `ACCESS_TOKEN` 使用API

---

### Q3: 如何在阿里云减少磁盘占用？

**方案**：

```bash
# 1. 清理pip缓存
pip cache purge

# 2. 清理Python缓存
find /var/www/ai-tender-system -type d -name "__pycache__" -exec rm -rf {} +
find /var/www/ai-tender-system -type f -name "*.pyc" -delete

# 3. 清理旧日志
find /var/www/ai-tender-system/logs -name "*.log" -mtime +30 -delete

# 4. 清理旧备份
find /var/backups/ai-tender-system -name "*.db" -mtime +7 -delete

# 5. 检查磁盘占用
du -sh /var/www/ai-tender-system
```

---

### Q4: 部署脚本自动选择依赖文件吗？

**是的！** `scripts/deploy.sh` 会自动检测：

```bash
# 172-193行：自动选择依赖文件
if [ -f "requirements-prod.txt" ]; then
    log INFO "使用 requirements-prod.txt"
    pip install -r requirements-prod.txt --upgrade -q
elif [ -f "requirements.txt" ]; then
    log INFO "使用 requirements.txt"
    pip install -r requirements.txt --upgrade -q
fi
```

**优先级**：
1. **首选** `requirements-prod.txt`（生产环境）
2. **备选** `requirements.txt`（开发环境）

---

## 📊 环境对比表

| 项目 | 本地开发 (`requirements.txt`) | 阿里云生产 (`requirements-prod.txt`) |
|------|-------------------------------|-------------------------------------|
| **磁盘占用** | ~2-3GB | ~500MB |
| **安装时间** | 15-30分钟 | 2-5分钟 |
| **torch** | ✅ 已安装 | ❌ 已移除 |
| **transformers** | ✅ 已安装 | ❌ 已移除 |
| **离线运行** | ✅ 支持 | ❌ 需要网络 |
| **API依赖** | 可选 | 必需 |
| **部署速度** | 慢 | 快 |
| **适用场景** | 开发/测试 | 生产部署 |

---

## 🎯 最佳实践

### 1. **本地开发时**

```bash
# 使用完整依赖
pip install -r requirements.txt

# 定期检查环境
bash scripts/check_environment.sh local

# 提交代码前测试生产依赖
pip install -r requirements-prod.txt
python -m ai_tender_system.web.app
```

---

### 2. **部署到阿里云前**

```bash
# 本地验证生产依赖可用
source venv/bin/activate
pip install -r requirements-prod.txt
python -m ai_tender_system.web.app

# 确保API配置正确
grep ACCESS_TOKEN .env
```

---

### 3. **阿里云服务器上**

```bash
# 始终使用部署脚本
bash scripts/deploy.sh

# 部署后验证环境
bash scripts/check_environment.sh remote

# 检查服务状态
sudo supervisorctl status ai-tender-system
```

---

## 📚 相关文档

- `requirements.txt` - 完整开发依赖
- `requirements-prod.txt` - 生产环境依赖
- `scripts/deploy.sh` - 自动部署脚本
- `scripts/check_environment.sh` - 环境检查脚本
- `数据库同步操作手册.md` - 数据库同步指南
- `docs/archived_notes/DEPLOYMENT_GUIDE.md` - 部署详细指南

---

**创建日期**: 2025-11-14
**适用版本**: AI标书系统 v2.0
**维护**: 定期更新
