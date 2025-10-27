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
LATEST_EXPORT=$(ls -t "$PROJECT_ROOT/exports"/knowledge_base_export_*.sql | head -1)
echo "最新导出文件: $LATEST_EXPORT"
echo

# 2. 检查Railway CLI
if ! command -v railway &> /dev/null; then
    echo "错误: Railway CLI 未安装"
    echo "请运行以下命令安装:"
    echo "  macOS: brew install railway"
    echo "  Linux/Windows: curl -fsSL https://railway.app/install.sh | sh"
    echo ""
    echo "或者手动使用导出的SQL文件:"
    echo "  1. 登录Railway Dashboard"
    echo "  2. 打开项目Shell"
    echo "  3. 上传并导入 $LATEST_EXPORT"
    exit 1
fi

# 3. 链接项目（如果还未链接）
echo "步骤 2/4: 检查Railway项目链接..."
if [ ! -f ".railway/config.json" ]; then
    echo "未检测到Railway项目链接，正在链接..."
    railway link
else
    echo "已链接到Railway项目"
fi

# 4. 切换环境
echo "步骤 3/4: 切换到 $ENVIRONMENT 环境..."
railway environment $ENVIRONMENT

# 5. 创建临时导入脚本
IMPORT_SCRIPT=$(mktemp /tmp/railway_import_XXXXXX.py)
cat > "$IMPORT_SCRIPT" << 'PYEOF'
import sqlite3
import sys
import os
from pathlib import Path

def import_database(sql_file_path):
    """导入SQL文件到数据库"""

    db_path = Path('ai_tender_system/data/knowledge_base.db')

    # 确保目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 备份现有数据库
    if db_path.exists():
        backup_path = db_path.with_suffix('.db.backup')
        import shutil
        shutil.copy(db_path, backup_path)
        print(f"已备份现有数据库到: {backup_path}")

    # 读取SQL文件
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 导入数据
    try:
        conn = sqlite3.connect(str(db_path))
        conn.executescript(sql_content)
        conn.close()

        print("✓ 数据库导入成功!")

        # 验证导入
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        print(f"  导入的表数量: {table_count}")
        conn.close()

        return True

    except Exception as e:
        print(f"✗ 导入失败: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python import.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    if not os.path.exists(sql_file):
        print(f"错误: SQL文件不存在: {sql_file}")
        sys.exit(1)

    success = import_database(sql_file)
    sys.exit(0 if success else 1)
PYEOF

# 6. 上传导入脚本和SQL文件到Railway
echo "步骤 4/4: 上传并导入数据库到Railway..."

# 方案A: 尝试使用railway cp命令
echo "尝试使用railway cp命令上传文件..."
if railway cp "$LATEST_EXPORT" /tmp/db_import.sql 2>/dev/null; then
    railway cp "$IMPORT_SCRIPT" /tmp/import.py 2>/dev/null
    railway run python3 /tmp/import.py /tmp/db_import.sql
    SUCCESS=true
else
    # 方案B: 使用railway shell和heredoc
    echo "railway cp 不可用，使用替代方案..."

    # 读取SQL文件内容（对于小文件）
    SQL_SIZE=$(wc -c < "$LATEST_EXPORT")
    SQL_SIZE_MB=$((SQL_SIZE / 1024 / 1024))

    if [ $SQL_SIZE_MB -lt 1 ]; then
        echo "SQL文件较小 ($SQL_SIZE_MB MB)，使用直接导入..."

        # 创建包含SQL内容的临时脚本
        TEMP_IMPORT=$(mktemp /tmp/railway_direct_import_XXXXXX.py)

        cat > "$TEMP_IMPORT" << EOF
import sqlite3
from pathlib import Path

sql_content = '''
$(cat "$LATEST_EXPORT")
'''

db_path = Path('ai_tender_system/data/knowledge_base.db')
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(db_path))
conn.executescript(sql_content)
conn.close()
print("✓ 数据库导入成功!")
EOF

        # 上传并执行
        cat "$TEMP_IMPORT" | railway run python3
        rm "$TEMP_IMPORT"
        SUCCESS=true
    else
        echo "SQL文件较大 ($SQL_SIZE_MB MB)，请使用手动方式:"
        echo ""
        echo "1. 登录Railway Dashboard: https://railway.app/dashboard"
        echo "2. 选择您的项目并打开Shell"
        echo "3. 将以下文件上传到临时URL（如GitHub Gist）:"
        echo "   - $LATEST_EXPORT"
        echo "4. 在Railway Shell中执行:"
        echo "   curl -o /tmp/db.sql YOUR_GIST_URL"
        echo "   python3 << 'EOF'"
        cat "$IMPORT_SCRIPT"
        echo "   EOF"
        echo ""
        SUCCESS=false
    fi
fi

# 清理临时文件
rm "$IMPORT_SCRIPT"

if [ "$SUCCESS" = true ]; then
    echo
    echo "================================================"
    echo "✓ 同步完成!"
    echo "================================================"
    echo
    echo "验证同步结果:"
    echo "  railway shell"
    echo "  python3 -c 'import sqlite3; c=sqlite3.connect(\"ai_tender_system/data/knowledge_base.db\"); print(\"表数量:\", c.execute(\"SELECT COUNT(*) FROM sqlite_master WHERE type=\\\"table\\\"\").fetchone()[0])'"
    exit 0
else
    echo
    echo "================================================"
    echo "⚠ 需要手动完成同步"
    echo "================================================"
    echo "已导出的SQL文件: $LATEST_EXPORT"
    exit 1
fi
