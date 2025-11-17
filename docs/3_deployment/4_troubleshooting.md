# 阿里云部署502错误修复指南

> **文档版本**: 1.0
> **创建日期**: 2025-11-02
> **问题**: HTTP 502 Bad Gateway
> **根本原因**: `main.py` 路径配置错误导致模块导入失败

---

## 📋 问题摘要

### 现象
```
该网页无法正常运作
8.140.21.235 目前无法处理此请求。
HTTP ERROR 502
```

### 症状
- ✅ Nginx运行正常
- ✅ Supervisor运行正常
- ✅ Gunicorn进程存在且监听8000端口
- ❌ 访问任何页面都返回502错误
- ❌ 应用日志无任何输出

### 根本原因

**`main.py` 文件的Python路径配置错误**:

```python
# ❌ 错误的配置（旧版本）
project_root = Path(__file__).parent / "ai_tender_system"
sys.path.insert(0, str(project_root))
```

**问题分析**:

阿里云服务器目录结构:
```
/var/www/ai-tender-system/          # 项目根目录
├── main.py                         # 入口文件（这里）
├── ai_tender_system/               # 应用代码目录
│   ├── common/
│   ├── modules/
│   └── web/
│       └── app.py
└── requirements-prod.txt
```

当 `main.py` 执行时:
1. `Path(__file__).parent` = `/var/www/ai-tender-system/`
2. `project_root` = `/var/www/ai-tender-system/ai_tender_system/` ← **拼接了子目录**
3. `from web.app import create_app` 实际查找路径变成:
   `/var/www/ai-tender-system/ai_tender_system/ai_tender_system/web/app.py` ← **多了一层!**
4. **模块导入失败** → Gunicorn进程"假死" → **502错误**

---

## ✅ 修复方案

### 1. 更新 `main.py` 文件

已修复的新版本:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境启动入口文件
适配多种部署环境（本地、Railway、阿里云等）
"""

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent

# 检测是否在 ai_tender_system 子目录中
# Railway部署: /app/ai_tender_system/
# 阿里云部署: /var/www/ai-tender-system/
if (project_root / "ai_tender_system").exists():
    # 如果存在 ai_tender_system 子目录,说明在项目根目录
    # 需要添加 ai_tender_system 到路径
    sys.path.insert(0, str(project_root / "ai_tender_system"))
else:
    # 否则当前目录就是 ai_tender_system,直接添加父目录
    sys.path.insert(0, str(project_root))

# 导入 Flask 应用
from web.app import create_app

# 创建应用实例供 gunicorn 使用
app = create_app()

if __name__ == '__main__':
    # 本地开发运行
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

**修复逻辑**:
- ✅ 智能检测当前目录结构
- ✅ 根据实际部署环境自适应调整路径
- ✅ 兼容Railway、阿里云、本地开发等多种环境

---

## 🚀 部署步骤（阿里云服务器）

### 步骤1: SSH登录服务器

```bash
ssh deploy@8.140.21.235
cd /var/www/ai-tender-system
```

### 步骤2: 备份当前版本

```bash
# 备份main.py（以防万一）
cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)

# 查看备份
ls -lh main.py*
```

### 步骤3: 拉取最新代码

```bash
# 方式1: 通过Git拉取（推荐）
git pull origin master

# 方式2: 手动更新main.py
nano main.py
# 粘贴上面的新代码,保存
```

### 步骤4: 重启应用

```bash
# 重启Gunicorn进程
sudo supervisorctl restart ai-tender-system

# 等待3秒让应用启动
sleep 3

# 检查状态
sudo supervisorctl status ai-tender-system
```

**预期输出**:
```
ai-tender-system    RUNNING   pid 12345, uptime 0:00:03
```

### 步骤5: 验证修复

```bash
# 1. 检查进程
ps aux | grep gunicorn

# 2. 检查端口监听
sudo netstat -tlnp | grep 8000

# 3. 测试HTTP响应
curl http://localhost:8000
# 应该返回HTML内容（登录页面），而不是Connection refused

# 4. 检查Nginx代理
curl http://localhost
# 应该返回完整的登录页面

# 5. 查看应用日志
tail -50 /var/www/ai-tender-system/logs/supervisor-stdout.log
tail -50 /var/www/ai-tender-system/logs/gunicorn-error.log
```

**成功标志**:
- ✅ `curl http://localhost:8000` 返回HTML内容
- ✅ 日志中出现 "AI标书系统Web应用初始化完成"
- ✅ 浏览器访问 `http://8.140.21.235` 显示登录页面

### 步骤6: 浏览器测试

打开浏览器访问:
```
http://8.140.21.235
```

**预期结果**:
- ✅ 显示登录页面
- ✅ 页面样式正常
- ✅ 无502错误

---

## 🔍 故障排查

### 如果仍然出现502错误

#### 1. 检查Python模块导入

```bash
cd /var/www/ai-tender-system
source venv/bin/activate

# 手动测试导入
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'ai_tender_system'))
from web.app import create_app
app = create_app()
print('✅ 应用创建成功')
"
```

**预期输出**:
```
✅ 应用创建成功
```

**如果报错**，检查:
- Python版本: `python3 --version` (应该是3.11+)
- 依赖安装: `pip list | grep Flask`
- 环境变量: `cat .env`

#### 2. 检查Supervisor配置

```bash
# 查看Supervisor配置
cat /etc/supervisor/conf.d/ai-tender-system.conf

# 确认command行正确
# 应该是: command=/var/www/ai-tender-system/venv/bin/gunicorn ... main:app
```

**关键检查**:
- ✅ `main:app` 而不是 `ai_tender_system.web.app:app`
- ✅ 工作目录 `directory=/var/www/ai-tender-system`

#### 3. 检查Gunicorn日志

```bash
# 查看详细错误
tail -100 /var/www/ai-tender-system/logs/gunicorn-error.log

# 如果日志为空，手动启动Gunicorn看错误
cd /var/www/ai-tender-system
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 --workers 1 main:app
# Ctrl+C 停止
```

#### 4. 检查文件权限

```bash
# main.py应该可执行
ls -l main.py
# -rwxr-xr-x 1 deploy deploy ...

# 如果权限不对
chmod +x main.py
```

#### 5. 检查.env文件

```bash
# 确认.env存在且有必要的配置
cat .env | grep -E "SECRET_KEY|ACCESS_TOKEN|DEBUG"

# 必须有的配置:
# SECRET_KEY=xxx
# ACCESS_TOKEN=xxx
# DEBUG=False
```

---

## 📊 部署架构说明

### 正确的目录结构

```
/var/www/ai-tender-system/          # Supervisor的working directory
├── main.py                         # ✅ Gunicorn入口: main:app
├── ai_tender_system/               # Python包根目录
│   ├── __init__.py
│   ├── common/
│   │   ├── config.py
│   │   └── database.py
│   ├── modules/
│   │   ├── business_response/
│   │   ├── knowledge_base/
│   │   └── tender_info/
│   ├── web/
│   │   ├── app.py              # Flask应用工厂
│   │   ├── blueprints/
│   │   ├── static/
│   │   └── templates/
│   └── data/
│       ├── knowledge_base.db
│       ├── uploads/
│       └── outputs/
├── venv/                           # 虚拟环境
├── logs/                           # 日志目录
├── .env                            # 环境变量（生产配置）
├── requirements-prod.txt
└── scripts/
    └── deploy.sh
```

### Python导入路径

修复后的导入路径:

```python
# main.py 中:
sys.path.insert(0, '/var/www/ai-tender-system/ai_tender_system')

# 然后可以导入:
from web.app import create_app              # ✅
from common.config import get_config        # ✅
from modules.business_response import ...   # ✅
```

---

## 🛡️ 预防措施

### 1. 使用GitHub Actions自动部署

文档已存在: `docs/archived_notes/GITHUB_AUTO_DEPLOY_SETUP.md`

**优势**:
- ✅ 每次部署前自动备份数据库
- ✅ 部署失败自动回滚
- ✅ 统一的部署流程，减少人为错误
- ✅ Git push后1分钟自动部署

### 2. 添加健康检查端点

在 `ai_tender_system/web/app.py` 中已有:

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

**使用**:
```bash
curl http://localhost:8000/api/health
# {"status":"healthy","timestamp":"2025-11-02T10:30:00"}
```

### 3. 配置监控告警

**Supervisor进程监控**:
```bash
# 添加到crontab
*/5 * * * * supervisorctl status ai-tender-system | grep -q RUNNING || /path/to/alert.sh
```

**Nginx日志监控**:
```bash
# 监控502错误
tail -f /var/log/nginx/ai-tender-error.log | grep 502
```

---

## 📝 部署清单

在每次部署时，按此清单检查:

- [ ] **代码更新**: `git pull origin master`
- [ ] **依赖更新**: `pip install -r requirements-prod.txt --upgrade`
- [ ] **数据库备份**: `bash scripts/backup_database.sh`
- [ ] **环境变量**: `.env` 文件存在且配置正确
- [ ] **重启服务**: `sudo supervisorctl restart ai-tender-system`
- [ ] **检查状态**: `sudo supervisorctl status ai-tender-system`
- [ ] **测试访问**: `curl http://localhost:8000/api/health`
- [ ] **浏览器验证**: 访问 `http://8.140.21.235`
- [ ] **检查日志**: 无错误信息

---

## 🔗 相关文档

- [GitHub自动部署配置](./archived_notes/GITHUB_AUTO_DEPLOY_SETUP.md)
- [完整部署指南](./archived_notes/DEPLOYMENT_GUIDE.md)
- [项目架构文档](./archived_notes/CLAUDE.md)

---

## 📞 技术支持

如遇到其他问题:

1. **查看日志**:
   ```bash
   tail -100 /var/www/ai-tender-system/logs/gunicorn-error.log
   tail -100 /var/www/ai-tender-system/logs/supervisor-stderr.log
   tail -100 /var/log/nginx/ai-tender-error.log
   ```

2. **手动测试**:
   ```bash
   cd /var/www/ai-tender-system
   source venv/bin/activate
   python3 main.py
   ```

3. **提交Issue**: 在GitHub仓库提交详细的错误信息

---

**最后更新**: 2025-11-02
**文档版本**: 1.0
**作者**: Claude Code

**祝部署顺利！🚀**
