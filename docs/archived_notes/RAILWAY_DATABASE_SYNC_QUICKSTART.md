# Railway 数据库同步 - 快速开始

## 📋 已完成的准备工作

✅ **数据库已导出**
- `exports/knowledge_base_export_20251026_195125.sql` (197 KB, 298条记录)
- `exports/tender_export_20251026_195125.sql` (16 KB, 空数据库)

✅ **工具已创建**
- `scripts/export_database.py` - 数据库导出脚本
- `scripts/sync_to_railway.sh` - 自动同步脚本（推荐）

✅ **文档已准备**
- `DATABASE_SYNC_GUIDE.md` - 完整同步指南（多种方案）

---

## 🚀 快速同步（3步）

### 方案1: 自动脚本（推荐）⭐

如果您已安装Railway CLI：

```bash
# 1. 运行同步脚本
./scripts/sync_to_railway.sh production

# 或同步到测试环境
./scripts/sync_to_railway.sh staging
```

脚本会自动：
- ✅ 导出最新数据库
- ✅ 链接Railway项目
- ✅ 上传并导入数据
- ✅ 验证同步结果

---

### 方案2: Railway CLI 手动操作

```bash
# 1. 安装Railway CLI（如果还没安装）
# macOS
brew install railway

# 或使用官方安装脚本（需要解决网络问题）
curl -fsSL https://railway.app/install.sh | sh

# 2. 登录Railway
railway login

# 3. 链接项目
railway link

# 4. 进入Railway Shell
railway shell

# 5. 在Railway环境中执行（复制粘贴以下内容）
python3 << 'EOF'
import sqlite3
import sys

# 这里需要将SQL内容粘贴进来，或通过URL下载
# 由于文件较大，建议使用下面的URL方式

# 方法A: 从GitHub或Gist下载
import urllib.request
sql_url = "YOUR_SQL_FILE_URL"  # 需要先上传SQL文件到网络
with urllib.request.urlopen(sql_url) as response:
    sql_content = response.read().decode('utf-8')

# 方法B: 如果SQL文件较小，可以直接粘贴
# sql_content = '''
#   (粘贴 exports/knowledge_base_export_20251026_195125.sql 的内容)
# '''

# 导入数据库
conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
conn.executescript(sql_content)
conn.close()
print("✓ 数据库导入成功!")
EOF
```

---

### 方案3: Railway Web界面

适合没有CLI或网络受限的情况：

#### 步骤1: 上传SQL文件到临时位置

选择以下任一方式：

**选项A - GitHub Gist（推荐）**:
1. 访问 https://gist.github.com/
2. 创建新Gist
3. 复制 `exports/knowledge_base_export_20251026_195125.sql` 内容
4. 粘贴并创建Gist
5. 点击 "Raw" 按钮获取URL

**选项B - Pastebin**:
1. 访问 https://pastebin.com/
2. 粘贴SQL内容
3. 设置过期时间（建议1天）
4. 获取Raw URL

**选项C - 文件传输服务**:
- https://transfer.sh/
- https://tmpfiles.org/
- 或您自己的服务器

#### 步骤2: 在Railway执行导入

1. 登录 [Railway Dashboard](https://railway.app/dashboard)
2. 选择您的项目
3. 打开最新部署的Shell
4. 复制粘贴以下命令（替换YOUR_SQL_URL）:

```bash
# 下载SQL文件
curl -o /tmp/knowledge_base.sql YOUR_SQL_URL

# 导入数据库
cd /app
python3 << 'EOF'
import sqlite3
from pathlib import Path

# 备份现有数据库
db_path = Path('ai_tender_system/data/knowledge_base.db')
if db_path.exists():
    import shutil
    shutil.copy(db_path, db_path.with_suffix('.db.backup'))
    print("已备份现有数据库")

# 读取SQL文件
with open('/tmp/knowledge_base.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 导入
conn = sqlite3.connect(str(db_path))
conn.executescript(sql_content)
conn.close()

# 验证
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM companies")
company_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM tender_projects")
project_count = cursor.fetchone()[0]

print(f"✓ 导入成功!")
print(f"  表数量: {table_count}")
print(f"  公司数量: {company_count}")
print(f"  项目数量: {project_count}")

conn.close()
EOF

# 清理临时文件
rm /tmp/knowledge_base.sql
```

---

## ✅ 验证同步结果

在Railway Shell中运行：

```bash
railway shell

# 快速验证
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
cursor = conn.cursor()

print("\n数据库验证报告:")
print("=" * 50)

checks = [
    ("表数量", "SELECT COUNT(*) FROM sqlite_master WHERE type='table'", 35),
    ("公司数据", "SELECT COUNT(*) FROM companies", 1),
    ("公司资料", "SELECT COUNT(*) FROM company_profiles", 4),
    ("产品数据", "SELECT COUNT(*) FROM products", 3),
    ("项目数据", "SELECT COUNT(*) FROM tender_projects", 2),
    ("资质类型", "SELECT COUNT(*) FROM qualification_types", 20),
    ("公司资质", "SELECT COUNT(*) FROM company_qualifications", 16),
    ("招标需求", "SELECT COUNT(*) FROM tender_requirements", 75),
]

all_passed = True
for name, query, expected in checks:
    cursor.execute(query)
    actual = cursor.fetchone()[0]
    status = "✓" if actual == expected else "✗"
    print(f"{status} {name}: {actual} (期望: {expected})")
    if actual != expected:
        all_passed = False

conn.close()

print("=" * 50)
if all_passed:
    print("✓ 所有验证通过!")
else:
    print("✗ 部分检查失败，请检查数据")
EOF
```

---

## 🔧 故障排除

### 问题1: Railway CLI安装失败

您遇到了这个问题（网络连接错误）。解决方案：

```bash
# 方案A: 稍后重试（可能是临时网络问题）
brew install railway

# 方案B: 使用代理
export https_proxy=http://your-proxy:port
brew install railway

# 方案C: 手动下载
# 访问 https://github.com/railwayapp/cli/releases
# 下载适合您系统的版本并手动安装

# 方案D: 使用Web界面（见方案3）
```

### 问题2: SQL文件太大无法粘贴

使用URL方式：

```python
# 在Railway Shell中
import urllib.request
urllib.request.urlretrieve(
    'YOUR_GIST_RAW_URL',
    '/tmp/knowledge_base.sql'
)
```

### 问题3: 数据库路径不存在

```bash
# 在Railway Shell中
mkdir -p /app/ai_tender_system/data
```

### 问题4: 权限错误

```bash
# 在Railway Shell中
chmod 666 /app/ai_tender_system/data/*.db
```

---

## 📊 数据库内容摘要

已导出的 `knowledge_base.db` 包含：

| 数据类型 | 记录数 | 说明 |
|---------|--------|------|
| 公司信息 | 1 | companies表 |
| 公司资料 | 4 | company_profiles |
| 产品信息 | 3 | products |
| 知识库配置 | 13 | knowledge_base_configs |
| 用户角色 | 4 | user_roles |
| 招标项目 | 2 | tender_projects |
| 案例研究 | 1 | case_studies |
| 文件存储 | 55 | file_storage |
| 简历 | 1 | resumes |
| 简历附件 | 1 | resume_attachments |
| 招标需求 | 75 | tender_requirements |
| 文档章节 | 73 | tender_document_chapters |
| HITL任务 | 13 | tender_hitl_tasks |
| 资质类型 | 20 | qualification_types |
| 公司资质 | 16 | company_qualifications |
| **总计** | **298** | 35张表 |

---

## 🔄 定期同步

如果需要定期更新Railway数据库：

```bash
# 1. 导出最新数据
python3 scripts/export_database.py

# 2. 同步到Railway
./scripts/sync_to_railway.sh production
```

或创建定时任务（cron）：

```bash
# 每天凌晨2点同步
0 2 * * * cd /Users/lvhe/Downloads/zhongbiao/zhongbiao && ./scripts/sync_to_railway.sh production >> /tmp/railway_sync.log 2>&1
```

---

## 📚 相关文档

- **完整指南**: `DATABASE_SYNC_GUIDE.md` - 详细的同步方案和最佳实践
- **Railway部署**: `ai_tender_system/RAILWAY_DEPLOYMENT.md` - Railway部署说明
- **导出工具**: `scripts/export_database.py` - 数据库导出脚本源码
- **同步脚本**: `scripts/sync_to_railway.sh` - 自动同步脚本源码

---

## ⚠️ 重要提示

1. **备份**: 同步前Railway会自动备份现有数据库为 `.db.backup`
2. **环境隔离**: 建议先在staging环境测试
3. **生产迁移**: 对于生产环境，考虑迁移到PostgreSQL
4. **数据安全**: 不要将数据库文件提交到Git仓库

---

## 🆘 需要帮助？

如果遇到问题：

1. 查看 `DATABASE_SYNC_GUIDE.md` 获取详细方案
2. 检查Railway Dashboard的日志
3. 使用 `railway logs` 查看实时日志
4. 在项目Issue中提问

---

**创建时间**: 2025-10-26
**状态**: ✅ 准备完成，等待执行同步

**下一步**: 选择方案1、2或3执行数据库同步
