# 数据库同步操作指南

> **目的**: 将本地开发环境的 SQLite 数据库同步到阿里云生产环境
> **创建日期**: 2025-11-03
> **适用场景**: 本地数据更新后需要同步到线上环境

---

## 📊 当前数据库状态

### 本地数据库文件

```
ai_tender_system/data/
├── knowledge_base.db       (744KB) ⭐ 主数据库
├── tender.db              (216KB)
└── resume_library.db      (0B)

ai_tender_system/database/
├── companies.db           (84KB)
├── knowledge_base.db      (0B - 旧版)
└── tender_system.db       (0B - 旧版)
```

### 主数据库内容 (knowledge_base.db)

| 数据类型 | 数量 |
|---------|------|
| 公司信息 | 2 |
| 文档资料 | 0 |
| 简历库 | 1 |
| 案例库 | 1 |
| 招标项目 | (待统计) |

**所有业务数据都在** `ai_tender_system/data/knowledge_base.db` **这一个文件中！**

---

## 🚀 快速同步（推荐）

### 方法一：使用快速同步脚本

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
./scripts/quick_sync_db.sh
```

**这个脚本会**:
1. ✓ 检查本地数据库
2. ✓ 显示本地数据统计
3. ✓ 在阿里云备份现有数据库
4. ✓ 上传新数据库到阿里云
5. ✓ 验证数据库完整性
6. ✓ 重启应用

**预计耗时**: 30-60秒

---

### 方法二：使用完整同步脚本

如果需要同步**所有数据库文件**（包括旧版数据库）:

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
./scripts/sync_database_to_aliyun.sh
```

---

## 🔧 手动同步（高级用户）

如果自动脚本失败，可以手动执行以下步骤：

### 步骤 1: 创建本地备份

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao

# 创建备份目录
mkdir -p ai_tender_system/data/db_backups

# 备份数据库（带时间戳）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp ai_tender_system/data/knowledge_base.db \
   ai_tender_system/data/db_backups/knowledge_base_${TIMESTAMP}.db

echo "本地备份完成: knowledge_base_${TIMESTAMP}.db"
```

---

### 步骤 2: 在阿里云备份现有数据库

```bash
# SSH 登录阿里云
ssh lvhe@8.140.21.235

# 创建备份目录
cd /var/www/ai-tender-system
mkdir -p ai_tender_system/data/db_backups

# 备份现有数据库
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -f ai_tender_system/data/knowledge_base.db ]; then
    cp ai_tender_system/data/knowledge_base.db \
       ai_tender_system/data/db_backups/knowledge_base_${TIMESTAMP}.db
    echo "阿里云备份完成"
else
    echo "阿里云暂无数据库，跳过备份"
fi

# 退出SSH
exit
```

---

### 步骤 3: 上传数据库到阿里云

```bash
# 在本地执行
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao

# 上传数据库
scp ai_tender_system/data/knowledge_base.db \
    lvhe@8.140.21.235:/var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db

# 验证上传成功
if [ $? -eq 0 ]; then
    echo "✓ 数据库上传成功"
else
    echo "✗ 数据库上传失败"
fi
```

---

### 步骤 4: 验证阿里云数据库

```bash
# SSH 登录阿里云
ssh lvhe@8.140.21.235

# 进入项目目录
cd /var/www/ai-tender-system

# 检查文件大小
ls -lh ai_tender_system/data/knowledge_base.db

# 验证数据库完整性
sqlite3 ai_tender_system/data/knowledge_base.db "PRAGMA integrity_check;"
# 应该输出: ok

# 查看数据统计
sqlite3 ai_tender_system/data/knowledge_base.db << 'SQL'
.headers on
.mode column
SELECT
    (SELECT COUNT(*) FROM companies) as companies,
    (SELECT COUNT(*) FROM documents) as documents,
    (SELECT COUNT(*) FROM resumes) as resumes,
    (SELECT COUNT(*) FROM case_studies) as cases;
SQL
```

**预期输出**:
```
companies   documents   resumes     cases
----------  ----------  ----------  ----------
2           0           1           1
```

---

### 步骤 5: 重启应用

```bash
# 在阿里云服务器上执行

# 重启应用
sudo supervisorctl restart ai-tender-system

# 等待启动
sleep 3

# 检查状态
sudo supervisorctl status ai-tender-system
```

**预期输出**:
```
ai-tender-system    RUNNING   pid 12345, uptime 0:00:03
```

---

### 步骤 6: 浏览器验证

访问: **http://8.140.21.235**

1. 登录系统 (admin/admin123)
2. 检查以下页面:
   - [ ] 公司管理 - 应该看到 2 家公司
   - [ ] 知识库 - 检查文档是否存在
   - [ ] 简历库 - 应该看到 1 份简历
   - [ ] 案例库 - 应该看到 1 个案例

---

## 🔄 定期同步建议

### 同步时机

建议在以下情况下同步数据库：

- ✅ 添加了新公司信息
- ✅ 上传了新的知识库文档
- ✅ 更新了简历库
- ✅ 添加了新案例
- ✅ 修改了重要配置

### 同步频率

- **开发期**: 每天同步 1 次
- **稳定期**: 每周同步 1 次
- **按需**: 重要更新后立即同步

---

## 🛡️ 安全注意事项

### 备份策略

1. **本地备份**: 每次同步前自动创建本地备份
2. **远程备份**: 每次同步前自动创建阿里云备份
3. **保留期限**: 建议保留最近 7 天的备份

### 备份位置

**本地**:
```
ai_tender_system/data/db_backups/
└── knowledge_base_YYYYMMDD_HHMMSS.db
```

**阿里云**:
```
/var/www/ai-tender-system/ai_tender_system/data/db_backups/
└── knowledge_base_YYYYMMDD_HHMMSS.db
```

### 清理旧备份

```bash
# 在阿里云上执行 - 删除 7 天前的备份
ssh lvhe@8.140.21.235 << 'ENDSSH'
cd /var/www/ai-tender-system/ai_tender_system/data/db_backups
find . -name "knowledge_base_*.db" -mtime +7 -delete
echo "已清理 7 天前的备份"
ENDSSH
```

---

## ❓ 常见问题

### 1. 同步失败: Permission denied

**原因**: SSH 密钥未配置或权限不足

**解决**:
```bash
# 检查 SSH 连接
ssh lvhe@8.140.21.235 "echo 'SSH 连接成功'"

# 如果失败，配置 SSH 密钥
ssh-copy-id lvhe@8.140.21.235
```

---

### 2. 同步后数据丢失

**原因**: 上传的数据库文件损坏

**解决**:
```bash
# 1. 从备份恢复（阿里云）
ssh lvhe@8.140.21.235
cd /var/www/ai-tender-system
ls -lt ai_tender_system/data/db_backups/ | head -5

# 2. 恢复最近的备份
LATEST_BACKUP=$(ls -t ai_tender_system/data/db_backups/knowledge_base_*.db | head -1)
cp "$LATEST_BACKUP" ai_tender_system/data/knowledge_base.db

# 3. 重启应用
sudo supervisorctl restart ai-tender-system
```

---

### 3. 数据库被锁定

**症状**: 应用访问数据库时报错 "database is locked"

**原因**: 有其他进程正在访问数据库

**解决**:
```bash
# 在阿里云执行
ssh lvhe@8.140.21.235

# 检查占用数据库的进程
lsof /var/www/ai-tender-system/ai_tender_system/data/knowledge_base.db

# 重启应用释放锁
sudo supervisorctl restart ai-tender-system
```

---

### 4. 同步后仍然看不到数据

**原因**: 应用未重启或缓存问题

**解决**:
```bash
# 1. 重启应用
ssh lvhe@8.140.21.235
sudo supervisorctl restart ai-tender-system

# 2. 清除浏览器缓存
# 在浏览器按 Ctrl+Shift+R 强制刷新

# 3. 检查应用日志
tail -50 /var/www/ai-tender-system/logs/supervisor-stdout.log
```

---

## 📝 同步检查清单

执行同步操作后，依次检查：

- [ ] 本地数据库已备份
- [ ] 阿里云数据库已备份
- [ ] 数据库上传成功（检查文件大小）
- [ ] 数据库完整性检查通过
- [ ] 应用成功重启
- [ ] 浏览器可以访问系统
- [ ] 公司数据正确显示
- [ ] 知识库数据正确显示
- [ ] 简历库数据正确显示
- [ ] 案例库数据正确显示

---

## 🔍 数据库结构说明

### 核心表

| 表名 | 用途 | 重要程度 |
|------|------|---------|
| `companies` | 公司信息 | ⭐⭐⭐⭐⭐ |
| `company_profiles` | 公司详细资料 | ⭐⭐⭐⭐ |
| `company_qualifications` | 公司资质 | ⭐⭐⭐⭐ |
| `documents` | 知识库文档 | ⭐⭐⭐⭐⭐ |
| `document_chunks` | 文档向量化分块 | ⭐⭐⭐⭐ |
| `resumes` | 简历库 | ⭐⭐⭐⭐ |
| `case_studies` | 案例库 | ⭐⭐⭐⭐ |
| `tender_projects` | 招标项目 | ⭐⭐⭐⭐⭐ |
| `tender_requirements` | 需求清单 | ⭐⭐⭐⭐⭐ |
| `tender_hitl_tasks` | 人工介入任务 | ⭐⭐⭐⭐ |

### 查看表结构

```bash
sqlite3 ai_tender_system/data/knowledge_base.db << 'SQL'
.schema companies
.schema documents
.schema resumes
SQL
```

---

## 🎯 最佳实践

1. **同步前检查**
   - 检查本地数据库是否最新
   - 确认要同步的数据是否正确
   - 查看数据统计确认数量

2. **同步中监控**
   - 观察上传进度
   - 检查网络连接稳定性
   - 记录同步开始和结束时间

3. **同步后验证**
   - 验证数据库完整性
   - 对比本地和远程数据统计
   - 在浏览器中抽查数据

4. **备份管理**
   - 定期清理旧备份（保留最近 7 天）
   - 重要更新前手动创建额外备份
   - 记录每次同步的备份文件名

---

## 📞 技术支持

如果遇到问题，请提供：

1. 执行的命令和完整输出
2. 本地数据库统计信息
3. 阿里云数据库统计信息
4. 应用日志最后 50 行
5. 错误截图（如有）

---

**最后更新**: 2025-11-03
**维护者**: lvhe
**版本**: 1.0
