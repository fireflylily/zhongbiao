# 数据库同步脚本使用说明

## 📁 脚本文件

| 脚本 | 用途 | 推荐度 |
|------|------|--------|
| `quick_sync_db.sh` | 快速同步核心数据库 | ⭐⭐⭐⭐⭐ |
| `sync_database_to_aliyun.sh` | 同步所有数据库 | ⭐⭐⭐ |

---

## 🚀 快速开始

### 一键同步（推荐）

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
./scripts/quick_sync_db.sh
```

**耗时**: 约 30-60 秒
**同步内容**: knowledge_base.db（包含公司、文档、简历、案例、项目等所有业务数据）

---

## 📊 同步前检查

查看本地数据：

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao

sqlite3 ai_tender_system/data/knowledge_base.db << 'SQL'
SELECT
    (SELECT COUNT(*) FROM companies) as 公司,
    (SELECT COUNT(*) FROM documents) as 文档,
    (SELECT COUNT(*) FROM resumes) as 简历,
    (SELECT COUNT(*) FROM case_studies) as 案例;
SQL
```

---

## ✅ 同步后验证

SSH 登录阿里云查看：

```bash
ssh lvhe@8.140.21.235

cd /var/www/ai-tender-system

# 查看数据
sqlite3 ai_tender_system/data/knowledge_base.db << 'SQL'
SELECT
    (SELECT COUNT(*) FROM companies) as 公司,
    (SELECT COUNT(*) FROM documents) as 文档,
    (SELECT COUNT(*) FROM resumes) as 简历,
    (SELECT COUNT(*) FROM case_studies) as 案例;
SQL
```

---

## 🔧 手动同步（如果脚本失败）

```bash
# 1. 备份（可选）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ssh lvhe@8.140.21.235 "cd /var/www/ai-tender-system && \
    mkdir -p ai_tender_system/data/db_backups && \
    cp ai_tender_system/data/knowledge_base.db \
       ai_tender_system/data/db_backups/knowledge_base_${TIMESTAMP}.db"

# 2. 上传数据库
scp ai_tender_system/data/knowledge_base.db \
    lvhe@8.140.21.235:/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db

# 3. 重启应用
ssh lvhe@8.140.21.235 "sudo supervisorctl restart ai-tender-system"
```

---

## 📖 详细文档

查看完整操作指南: [DATABASE_SYNC_GUIDE.md](../DATABASE_SYNC_GUIDE.md)

---

**最后更新**: 2025-11-03
