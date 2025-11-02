# 环境同步完整指南

> 解决"换机器功能不一样"问题的完整解决方案

---

## 📋 目录

- [问题说明](#问题说明)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
  - [方案A：从备份恢复（推荐）](#方案a从备份恢复推荐)
  - [方案B：手动同步](#方案b手动同步)
- [工具说明](#工具说明)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)

---

## 问题说明

### 为什么换机器后功能不一样？

项目中的 `.gitignore` 忽略了以下关键文件：

| 文件类型 | 被忽略的内容 | 影响 |
|---------|-------------|------|
| **数据库** | `*.db`, `*.sqlite*` | ❌ 企业信息、资质、案例、简历数据丢失 |
| **环境配置** | `.env` | ❌ API密钥、模型配置缺失 |
| **上传文件** | `ai_tender_system/data/uploads/` | ❌ 用户上传的招标文档、资质文件丢失 |
| **输出文件** | `ai_tender_system/data/output/` | ❌ 生成的标书文档丢失 |
| **公司配置** | `company_configs/*.json` | ❌ 公司特定配置丢失 |

### 设计原因

这是**标准的开源项目实践**：
- ✅ 不提交敏感数据（API密钥、用户数据）到Git
- ✅ 不提交生成的文件和缓存
- ❌ 但缺少数据迁移工具

---

## 快速开始

### 在旧机器上（创建备份）

```bash
# 1. 创建完整备份（包含数据库和文件）
python3 scripts/backup_environment.py

# 输出: exports/backup_YYYYMMDD_HHMMSS.tar.gz
```

### 在新机器上（恢复环境）

```bash
# 1. 克隆代码
git clone <repository-url>
cd zhongbiao

# 2. 传输备份文件到新机器
scp user@old-machine:path/to/exports/backup_*.tar.gz ./

# 3. 恢复环境
python3 scripts/restore_environment.py backup_*.tar.gz

# 4. 配置API密钥
vim ai_tender_system/.env  # 填入你的API密钥

# 5. 安装依赖
pip install -r requirements.lock

# 6. 验证环境
python3 scripts/check_env.py

# 7. 启动应用
python3 -m ai_tender_system.web.app
```

---

## 详细步骤

### 方案A：从备份恢复（推荐）

#### 步骤1：在旧机器上创建备份

```bash
cd /path/to/zhongbiao

# 完整备份（包含数据库和文件，推荐）
python3 scripts/backup_environment.py

# 或者仅备份数据库（文件较小）
python3 scripts/backup_environment.py --no-files
```

**备份内容**：
```
backup_YYYYMMDD_HHMMSS.tar.gz
├── databases/              # 数据库文件
│   ├── knowledge_base.db
│   ├── knowledge_base.sql
│   ├── tender.db
│   ├── tender.sql
│   └── resume_library.db
├── files/                  # 数据文件
│   ├── uploads/
│   └── outputs/
├── config/                 # 配置文件
│   ├── .env.template      # 环境配置模板（已脱敏）
│   ├── requirements.txt
│   └── requirements.lock  # 精确版本
├── MANIFEST.json          # 备份清单
└── README.md              # 备份说明
```

#### 步骤2：传输备份到新机器

```bash
# 方式1: scp传输
scp exports/backup_*.tar.gz user@new-machine:/path/to/

# 方式2: 通过中转服务器
# 上传到云存储、NAS或文件分享服务
```

#### 步骤3：在新机器上克隆代码

```bash
# 克隆仓库
git clone <repository-url>
cd zhongbiao

# 查看当前分支
git branch -a
```

#### 步骤4：恢复环境

```bash
# 自动恢复（推荐）
python3 scripts/restore_environment.py /path/to/backup_*.tar.gz

# 强制覆盖（不提示确认）
python3 scripts/restore_environment.py --force backup_*.tar.gz
```

#### 步骤5：配置环境变量

```bash
# 编辑.env文件，填入实际API密钥
vim ai_tender_system/.env
```

**必需配置**：
```ini
# 联通MaaS平台（必需）
ACCESS_TOKEN=your_actual_token_here
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1

# Flask密钥（必需）
SECRET_KEY=your_random_secret_key_here

# 可选配置
OPENAI_API_KEY=your_openai_key_here     # 可选
SHIHUANG_API_KEY=your_shihuang_key_here  # 可选
DEBUG=False                              # 生产环境设为False
```

#### 步骤6：安装依赖

```bash
# 推荐：使用锁定版本（保证版本一致）
pip install -r requirements.lock

# 或者：使用基础版本
pip install -r requirements.txt
```

#### 步骤7：验证环境

```bash
# 运行环境检查
python3 scripts/check_env.py

# 输出示例：
# ✅ 成功: 15 项
# ⚠️  警告: 2 项
# ❌ 错误: 0 项
```

#### 步骤8：启动应用

```bash
# 启动应用
python3 -m ai_tender_system.web.app

# 或使用自定义端口
FLASK_RUN_PORT=8080 python3 -m ai_tender_system.web.app
```

---

### 方案B：手动同步

如果无法使用自动化工具，可以手动同步：

#### 1. 同步数据库

```bash
# 在旧机器上导出数据库
python3 scripts/export_database.py

# 传输SQL文件到新机器
scp exports/*.sql user@new-machine:/path/to/

# 在新机器上导入（需要sqlite3命令）
cd ai_tender_system/data
sqlite3 knowledge_base.db < /path/to/knowledge_base_export_*.sql
sqlite3 tender.db < /path/to/tender_export_*.sql
```

#### 2. 同步文件目录

```bash
# 从旧机器复制文件
scp -r ai_tender_system/data/uploads user@new-machine:/path/to/ai_tender_system/data/
scp -r ai_tender_system/data/outputs user@new-machine:/path/to/ai_tender_system/data/
```

#### 3. 同步环境配置

```bash
# 复制.env文件（注意安全，不要上传到Git）
scp ai_tender_system/.env user@new-machine:/path/to/ai_tender_system/

# 或者手动创建
cp ai_tender_system/.env.example ai_tender_system/.env
vim ai_tender_system/.env  # 填入API密钥
```

#### 4. 锁定依赖版本

```bash
# 在旧机器上生成
pip freeze > requirements.lock

# 复制到新机器
scp requirements.lock user@new-machine:/path/to/

# 在新机器上安装
pip install -r requirements.lock
```

---

## 工具说明

### 1. 环境检查工具 (`scripts/check_env.py`)

**功能**：检测缺失的配置、数据库、文件等

```bash
python3 scripts/check_env.py
```

**检查项目**：
- ✅ `.env` 环境配置
- ✅ 数据库文件（knowledge_base.db, tender.db等）
- ✅ 数据目录（uploads/, outputs/）
- ✅ Python依赖包
- ✅ 配置文件完整性

**输出示例**：
```
================================================================================
                      AI标书系统 - 环境完整性检查
================================================================================

1. 环境配置检查 (.env)
  ✅ ACCESS_TOKEN: 已配置
  ✅ SECRET_KEY: 已配置
  ⚠️  OPENAI_API_KEY: 未配置 (可选)

2. 数据库文件检查
  ✅ knowledge_base.db: 存在 (744.0 KB) - 主数据库
  ❌ tender.db: 不存在 - 招标项目数据库

检查报告汇总
  ✅ 成功: 12 项
  ⚠️  警告: 3 项
  ❌ 错误: 1 项
```

---

### 2. 备份工具 (`scripts/backup_environment.py`)

**功能**：创建完整环境备份

```bash
# 完整备份（推荐）
python3 scripts/backup_environment.py

# 仅备份数据库（不含uploads/outputs）
python3 scripts/backup_environment.py --no-files

# 指定输出目录
python3 scripts/backup_environment.py --output /path/to/output
```

**备份内容**：
- 所有数据库（.db + .sql双格式）
- 上传文件（uploads/）
- 输出文件（outputs/）
- 环境配置模板（.env.template，已脱敏）
- 依赖清单（requirements.lock）
- 备份清单（MANIFEST.json）

---

### 3. 恢复工具 (`scripts/restore_environment.py`)

**功能**：从备份恢复完整环境

```bash
# 交互式恢复（推荐）
python3 scripts/restore_environment.py backup_*.tar.gz

# 强制覆盖（不提示确认）
python3 scripts/restore_environment.py --force backup_*.tar.gz
```

**恢复流程**：
1. 解压备份文件
2. 显示备份信息
3. 确认恢复操作
4. 恢复数据库
5. 恢复文件目录
6. 恢复配置文件
7. 显示后续步骤

---

### 4. 数据库导出工具 (`scripts/export_database.py`)

**功能**：导出数据库为SQL（用于Railway等云平台同步）

```bash
python3 scripts/export_database.py
```

**输出**：
```
exports/
├── knowledge_base_export_20251031_123456.sql
├── tender_export_20251031_123456.sql
└── resume_library_export_20251031_123456.sql
```

---

## 常见问题

### Q1: 恢复后仍然缺少数据？

**可能原因**：
- 备份时数据库为空
- 恢复过程中断
- .gitignore 规则过滤了关键文件

**解决方案**：
```bash
# 检查备份内容
tar -tzf backup_*.tar.gz

# 手动验证数据库
sqlite3 ai_tender_system/data/knowledge_base.db "SELECT COUNT(*) FROM companies;"

# 重新恢复
python3 scripts/restore_environment.py --force backup_*.tar.gz
```

---

### Q2: 依赖版本不一致导致错误？

**症状**：
```
ModuleNotFoundError: No module named 'xxx'
ImportError: cannot import name 'xxx'
```

**解决方案**：
```bash
# 使用锁定版本
pip install -r requirements.lock

# 或者重新安装所有依赖
pip uninstall -y -r <(pip freeze)
pip install -r requirements.lock
```

---

### Q3: API密钥配置后仍然报错？

**可能原因**：
- .env文件格式错误（多余空格、换行符）
- API密钥包含不可见字符

**解决方案**：
```bash
# 使用诊断工具检查
python3 scripts/diagnose_env.py

# 手动检查
cat -A ai_tender_system/.env  # 查看不可见字符

# 重新配置
cp ai_tender_system/.env.example ai_tender_system/.env
vim ai_tender_system/.env
```

---

### Q4: 数据库文件存在但内容为空？

**可能原因**：
- 数据库文件损坏
- 恢复SQL失败
- 原始备份时数据库为空

**解决方案**：
```bash
# 检查数据库完整性
sqlite3 ai_tender_system/data/knowledge_base.db "PRAGMA integrity_check;"

# 从SQL重新导入
sqlite3 ai_tender_system/data/knowledge_base.db < backup/databases/knowledge_base.sql

# 检查表和数据
sqlite3 ai_tender_system/data/knowledge_base.db ".tables"
sqlite3 ai_tender_system/data/knowledge_base.db "SELECT * FROM companies LIMIT 5;"
```

---

### Q5: 权限问题导致恢复失败？

**症状**：
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**：
```bash
# 检查文件权限
ls -lh ai_tender_system/data/

# 修复权限
chmod 755 ai_tender_system/data/
chmod 644 ai_tender_system/data/*.db

# 使用sudo恢复（谨慎）
sudo python3 scripts/restore_environment.py backup_*.tar.gz
```

---

## 最佳实践

### 1. 定期备份

```bash
# 方式1: 手动备份
python3 scripts/backup_environment.py

# 方式2: 定时任务（每天凌晨2点）
# crontab -e
0 2 * * * cd /path/to/zhongbiao && python3 scripts/backup_environment.py

# 方式3: Git Hook（每次push前）
# .git/hooks/pre-push
#!/bin/bash
python3 scripts/backup_environment.py --no-files
```

---

### 2. 备份存储策略

```bash
# 本地保留最近7天
find exports/ -name "backup_*.tar.gz" -mtime +7 -delete

# 定期上传到云存储
# 腾讯云COS
coscmd upload exports/backup_*.tar.gz /backups/

# 阿里云OSS
ossutil cp exports/backup_*.tar.gz oss://bucket/backups/

# AWS S3
aws s3 cp exports/backup_*.tar.gz s3://bucket/backups/
```

---

### 3. 版本控制最佳实践

```bash
# 确保.gitignore正确
cat .gitignore | grep -E "\.env|\.db|uploads|outputs"

# 添加README说明数据同步
echo "数据同步指南：查看 ENVIRONMENT_SYNC_GUIDE.md" >> README.md

# 提交requirements.lock到Git
git add requirements.lock
git commit -m "chore: 添加依赖版本锁定文件"
```

---

### 4. 团队协作同步

```bash
# 团队成员A（旧环境）
python3 scripts/backup_environment.py
# 上传到团队共享目录：共享盘/backups/

# 团队成员B（新环境）
# 从共享目录下载备份
python3 scripts/restore_environment.py /path/to/backup_*.tar.gz
python3 scripts/check_env.py
```

---

### 5. CI/CD集成

```yaml
# .github/workflows/backup.yml
name: 定期备份
on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点
  workflow_dispatch:     # 手动触发

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: 创建备份
        run: python3 scripts/backup_environment.py --no-files
      - name: 上传备份
        uses: actions/upload-artifact@v3
        with:
          name: database-backup
          path: exports/backup_*.tar.gz
```

---

## 安全注意事项

⚠️ **重要提醒**：

1. **不要将备份文件提交到Git**
   ```bash
   # 确认.gitignore已包含
   exports/
   *.tar.gz
   ```

2. **保护API密钥**
   - `.env` 文件永远不要提交到版本控制
   - 使用 `.env.template` 分享配置结构
   - 定期更换API密钥

3. **加密敏感备份**
   ```bash
   # 加密备份文件
   gpg -c exports/backup_*.tar.gz
   # 生成: backup_*.tar.gz.gpg

   # 解密
   gpg -d backup_*.tar.gz.gpg > backup_*.tar.gz
   ```

4. **限制备份访问权限**
   ```bash
   chmod 600 exports/backup_*.tar.gz
   ```

---

## 快速参考卡片

```
┌─────────────────────────────────────────────────────────────────┐
│                    环境同步快速参考                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  旧机器（创建备份）                                             │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ python3 scripts/backup_environment.py                  │   │
│  │ # 输出: exports/backup_YYYYMMDD_HHMMSS.tar.gz          │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  新机器（恢复环境）                                             │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ git clone <repo> && cd zhongbiao                       │   │
│  │ python3 scripts/restore_environment.py backup_*.tar.gz │   │
│  │ vim ai_tender_system/.env  # 填入API密钥               │   │
│  │ pip install -r requirements.lock                       │   │
│  │ python3 scripts/check_env.py                           │   │
│  │ python3 -m ai_tender_system.web.app                    │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  验证环境                                                       │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ python3 scripts/check_env.py                           │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 相关文档

- [项目README](README.md) - 项目概览和基础使用
- [CLAUDE.md](CLAUDE.md) - 开发指南和架构说明
- [DATABASE_SYNC_GUIDE.md](DATABASE_SYNC_GUIDE.md) - 数据库同步详细指南
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 生产环境部署指南

---

## 问题反馈

如遇到问题，请：
1. 运行环境检查：`python3 scripts/check_env.py`
2. 查看日志文件：`ai_tender_system/data/logs/`
3. 创建GitHub Issue并附上检查结果

---

**最后更新**: 2025-10-31
**文档版本**: 1.0
