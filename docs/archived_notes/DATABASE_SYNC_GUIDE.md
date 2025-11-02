# Railway 数据库同步指南

本指南详细说明如何将本地SQLite数据库同步到Railway部署环境。

## 概述

已导出的数据库文件：
- ✅ **knowledge_base.db** → `exports/knowledge_base_export_YYYYMMDD_HHMMSS.sql` (0.19 MB, 298条记录)
- ✅ **tender.db** → `exports/tender_export_YYYYMMDD_HHMMSS.sql` (0.02 MB, 空数据库)
- ⚠️ **resume_library.db** → 空数据库，已跳过

## 同步方案

### 方案A: 使用Railway CLI（推荐）

**适用场景**: 快速同步，一次性迁移

#### 步骤1: 安装Railway CLI

```bash
# macOS (Homebrew)
brew install railway

# 或使用官方安装脚本
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Linux
curl -fsSL https://railway.app/install.sh | sh
```

验证安装:
```bash
railway --version
```

#### 步骤2: 登录Railway

```bash
railway login
```

这会打开浏览器进行身份验证。

#### 步骤3: 链接到您的Railway项目

```bash
# 在项目根目录执行
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
railway link
```

选择您的项目和环境（production/staging）。

#### 步骤4: 上传数据库文件

**选项A - 直接复制数据库文件**（最简单）:

```bash
# 上传knowledge_base.db到Railway
railway run cp ai_tender_system/data/knowledge_base.db /app/ai_tender_system/data/knowledge_base.db

# 或通过Railway Volumes（如果已配置）
railway volumes upload knowledge_base.db ai_tender_system/data/knowledge_base.db
```

**选项B - 通过SQL文件导入**（更可控）:

```bash
# 1. 进入Railway Shell
railway shell

# 2. 在Railway环境中执行以下命令
cd /app
python3 << 'EOF'
import sqlite3
import sys

# 读取SQL文件
with open('/path/to/knowledge_base_export_YYYYMMDD_HHMMSS.sql', 'r') as f:
    sql_script = f.read()

# 连接数据库并执行
conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
conn.executescript(sql_script)
conn.close()
print("数据库导入成功!")
EOF
```

**选项C - 使用Railway上传API**:

```bash
# 1. 创建上传脚本（在Railway Shell中）
railway shell

# 2. 使用Python上传
python3 << 'EOF'
import sqlite3
import os

# 如果数据库已存在，备份
if os.path.exists('ai_tender_system/data/knowledge_base.db'):
    import shutil
    shutil.copy(
        'ai_tender_system/data/knowledge_base.db',
        'ai_tender_system/data/knowledge_base.db.backup'
    )
    print("已备份现有数据库")

# 这里需要先将SQL文件上传到Railway
# 方法: railway run curl https://your-server.com/knowledge_base_export.sql > /tmp/db.sql
# 或者使用railway cp命令上传文件
EOF
```

#### 步骤5: 验证数据同步

```bash
railway shell

# 在Railway环境中验证
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
cursor = conn.cursor()

# 检查表数量
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]
print(f"表数量: {table_count}")

# 检查companies表
cursor.execute("SELECT COUNT(*) FROM companies")
company_count = cursor.fetchone()[0]
print(f"公司数量: {company_count}")

# 检查projects表
cursor.execute("SELECT COUNT(*) FROM tender_projects")
project_count = cursor.fetchone()[0]
print(f"项目数量: {project_count}")

conn.close()
EOF
```

---

### 方案B: 使用Railway Web界面

**适用场景**: 没有CLI访问权限，小文件上传

#### 步骤1: 访问Railway Dashboard

登录 [Railway Dashboard](https://railway.app/dashboard)

#### 步骤2: 打开项目Shell

1. 选择您的项目
2. 进入 "Deployments" 标签
3. 点击最新部署
4. 点击 "Shell" 按钮

#### 步骤3: 手动上传SQL文件

由于Railway Web Shell不支持直接文件上传，需要通过以下方式：

**方法1: 使用临时URL**

```bash
# 1. 将SQL文件上传到临时存储（如GitHub Gist、Pastebin等）
# 2. 在Railway Shell中下载
curl -o /tmp/knowledge_base.sql https://your-temp-url/knowledge_base.sql

# 3. 导入数据库
cd /app
python3 << 'EOF'
import sqlite3

with open('/tmp/knowledge_base.sql', 'r') as f:
    sql_script = f.read()

conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
conn.executescript(sql_script)
conn.close()
print("导入完成!")
EOF
```

**方法2: 使用Base64编码**（小文件）

```bash
# 本地编码SQL文件
base64 exports/knowledge_base_export_YYYYMMDD_HHMMSS.sql > db_base64.txt

# 在Railway Shell中解码并导入
# (粘贴base64内容到环境变量)
echo "YOUR_BASE64_CONTENT" | base64 -d > /tmp/knowledge_base.sql
python3 -c "import sqlite3; conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db'); conn.executescript(open('/tmp/knowledge_base.sql').read()); conn.close()"
```

---

### 方案C: 通过应用API上传（推荐生产环境）

**适用场景**: 自动化同步，定期备份

#### 创建数据库同步API

在 `ai_tender_system/web/blueprints/api_database_sync.py` 创建：

```python
from flask import Blueprint, request, jsonify
import sqlite3
import os
from pathlib import Path

database_sync_bp = Blueprint('database_sync', __name__)

@database_sync_bp.route('/api/database/import', methods=['POST'])
def import_database():
    """
    导入数据库SQL文件

    安全注意: 此端点应该受到严格的认证保护
    """
    # TODO: 添加管理员认证
    if not request.is_json:
        return jsonify({"error": "请求必须是JSON格式"}), 400

    data = request.get_json()
    sql_content = data.get('sql')
    db_name = data.get('database', 'knowledge_base')

    if not sql_content:
        return jsonify({"error": "缺少SQL内容"}), 400

    # 数据库路径
    db_path = Path(__file__).parent.parent / 'data' / f'{db_name}.db'

    try:
        # 备份现有数据库
        if db_path.exists():
            backup_path = db_path.with_suffix('.db.backup')
            import shutil
            shutil.copy(db_path, backup_path)

        # 导入新数据
        conn = sqlite3.connect(db_path)
        conn.executescript(sql_content)
        conn.close()

        return jsonify({
            "success": True,
            "message": "数据库导入成功",
            "database": db_name
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

#### 使用API同步

```bash
# 读取SQL文件并POST到Railway
curl -X POST https://your-railway-app.railway.app/api/database/import \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d @- << EOF
{
  "database": "knowledge_base",
  "sql": $(cat exports/knowledge_base_export_YYYYMMDD_HHMMSS.sql | jq -Rs .)
}
EOF
```

---

### 方案D: 使用Railway Volumes（持久存储）

**适用场景**: 需要持久化数据，防止重启丢失

#### 步骤1: 配置Railway Volume

在 `railway.json` 中添加:

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "volumes": [
      {
        "name": "database-storage",
        "mountPath": "/app/ai_tender_system/data"
      }
    ]
  }
}
```

#### 步骤2: 部署更新

```bash
railway up
```

#### 步骤3: 上传数据库到Volume

```bash
# 使用railway cp命令
railway cp ai_tender_system/data/knowledge_base.db /app/ai_tender_system/data/knowledge_base.db
```

---

## 自动化同步脚本

创建 `scripts/sync_to_railway.sh`:

```bash
#!/bin/bash

# Railway数据库同步脚本
# 使用方法: ./scripts/sync_to_railway.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "Railway 数据库同步工具"
echo "环境: $ENVIRONMENT"
echo "================================================"
echo

# 1. 导出数据库
echo "步骤 1/4: 导出本地数据库..."
python3 "$SCRIPT_DIR/export_database.py"

# 获取最新导出的文件
LATEST_EXPORT=$(ls -t "$PROJECT_ROOT/exports"/*.sql | head -1)
echo "最新导出文件: $LATEST_EXPORT"
echo

# 2. 检查Railway CLI
if ! command -v railway &> /dev/null; then
    echo "错误: Railway CLI 未安装"
    echo "请运行: brew install railway"
    exit 1
fi

# 3. 链接项目
echo "步骤 2/4: 链接Railway项目..."
railway link

# 4. 切换环境
echo "步骤 3/4: 切换到 $ENVIRONMENT 环境..."
railway environment $ENVIRONMENT

# 5. 上传数据库
echo "步骤 4/4: 上传数据库到Railway..."

# 读取SQL文件
SQL_CONTENT=$(cat "$LATEST_EXPORT")

# 在Railway环境中执行导入
railway run python3 << EOF
import sqlite3
import sys

sql_content = '''$SQL_CONTENT'''

try:
    conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
    conn.executescript(sql_content)
    conn.close()
    print("✓ 数据库同步成功!")
except Exception as e:
    print(f"✗ 同步失败: {e}", file=sys.stderr)
    sys.exit(1)
EOF

echo
echo "================================================"
echo "同步完成!"
echo "================================================"
```

赋予执行权限:
```bash
chmod +x scripts/sync_to_railway.sh
```

使用:
```bash
# 同步到生产环境
./scripts/sync_to_railway.sh production

# 同步到测试环境
./scripts/sync_to_railway.sh staging
```

---

## 数据库验证清单

同步后，在Railway环境中运行以下检查：

```bash
railway shell

python3 << 'EOF'
import sqlite3
import sys

def validate_database():
    """验证数据库完整性"""

    conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
    cursor = conn.cursor()

    checks = {
        "表数量": ("SELECT COUNT(*) FROM sqlite_master WHERE type='table'", 35),
        "公司数据": ("SELECT COUNT(*) FROM companies", 1),
        "项目数据": ("SELECT COUNT(*) FROM tender_projects", 2),
        "资质类型": ("SELECT COUNT(*) FROM qualification_types", 20),
        "公司资质": ("SELECT COUNT(*) FROM company_qualifications", 16),
    }

    print("数据库验证报告:")
    print("=" * 50)

    all_passed = True
    for check_name, (query, expected) in checks.items():
        cursor.execute(query)
        actual = cursor.fetchone()[0]
        status = "✓" if actual == expected else "✗"
        print(f"{status} {check_name}: {actual} (期望: {expected})")
        if actual != expected:
            all_passed = False

    conn.close()

    print("=" * 50)
    if all_passed:
        print("✓ 所有检查通过!")
        return 0
    else:
        print("✗ 部分检查失败，请检查数据")
        return 1

sys.exit(validate_database())
EOF
```

---

## 常见问题

### Q1: Railway Shell执行超时

**问题**: SQL文件太大，导入时超时

**解决方案**:
1. 分批导入（按表分割SQL文件）
2. 使用Railway CLI而非Web Shell
3. 增加超时时间: `railway run --timeout 600 python3 import.py`

### Q2: 数据库文件权限问题

**问题**: 无法写入数据库文件

**解决方案**:
```bash
railway shell
chmod 666 ai_tender_system/data/*.db
```

### Q3: 数据重复

**问题**: 重复执行导入导致数据重复

**解决方案**:
- 导入前清空数据库
- 或使用 `INSERT OR REPLACE` 语句
- 在导出脚本中添加 `DROP TABLE IF EXISTS` 语句

### Q4: 外键约束错误

**问题**: 导入时出现外键约束错误

**解决方案**:
已在导出脚本中处理:
```sql
PRAGMA foreign_keys=OFF;
-- 导入数据...
PRAGMA foreign_keys=ON;
```

### Q5: Railway环境变量未配置

**问题**: 应用无法找到数据库路径

**解决方案**:
在Railway Dashboard中添加环境变量:
```bash
DATABASE_PATH=/app/ai_tender_system/data/knowledge_base.db
```

---

## 最佳实践

### 1. 定期备份

```bash
# 从Railway下载当前数据库
railway run cat ai_tender_system/data/knowledge_base.db > backups/knowledge_base_$(date +%Y%m%d).db
```

### 2. 版本控制

不要将 `.db` 文件提交到Git，但可以提交SQL导出文件：

```bash
# .gitignore
*.db
!exports/*.sql  # 允许导出的SQL文件
```

### 3. 环境隔离

- 开发环境: 本地SQLite
- 测试环境: Railway Staging + SQLite
- 生产环境: Railway Production + PostgreSQL（推荐）

### 4. 迁移到PostgreSQL（生产推荐）

对于生产环境，建议迁移到PostgreSQL:

```bash
# 1. 在Railway添加PostgreSQL插件
railway add postgresql

# 2. 使用pgloader迁移
pgloader knowledge_base.db $DATABASE_URL
```

---

## 监控与维护

### 数据库大小监控

```python
import os
from pathlib import Path

db_path = Path('ai_tender_system/data/knowledge_base.db')
size_mb = db_path.stat().st_size / 1024 / 1024

print(f"数据库大小: {size_mb:.2f} MB")

# 如果超过500MB，考虑清理或优化
if size_mb > 500:
    print("⚠️ 数据库较大，建议优化")
```

### 数据库优化

```bash
railway shell

python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('ai_tender_system/data/knowledge_base.db')
conn.execute("VACUUM")  # 清理和优化
conn.execute("ANALYZE")  # 更新查询优化器统计
conn.close()
print("数据库优化完成")
EOF
```

---

## 下一步

1. ✅ 已导出数据库为SQL文件
2. ⬜ 安装Railway CLI（如遇网络问题可稍后重试）
3. ⬜ 登录并链接Railway项目
4. ⬜ 选择同步方案（推荐方案A或方案C）
5. ⬜ 执行同步并验证

## 支持

如有问题，请参考：
- Railway官方文档: https://docs.railway.app/
- SQLite文档: https://www.sqlite.org/docs.html
- 项目Issue: GitHub Issues

---

**创建时间**: 2025-10-26
**维护者**: AI Tender System Team
