#!/bin/bash
#
# AI智能标书生成平台 - 数据库备份脚本
# 备份SQLite数据库，保留最近7天的备份
#
# 使用方法:
#   bash scripts/backup_database.sh
#
# 作者: Claude Code
# 日期: 2025-10-31
#

set -e  # 遇到错误立即退出

# ==================== 配置变量 ====================

# 应用目录
APP_DIR="/var/www/ai-tender-system"

# 数据库路径
DB_PATH="${APP_DIR}/ai_tender_system/data/knowledge_base.db"

# 备份目录
BACKUP_DIR="/var/backups/ai-tender-system"

# 保留天数
RETENTION_DAYS=7

# 日期格式（用于备份文件名）
DATE_FORMAT=$(date '+%Y%m%d_%H%M%S')

# 备份文件名
BACKUP_FILE="${BACKUP_DIR}/knowledge_base_${DATE_FORMAT}.db"

# 压缩备份文件名
BACKUP_ARCHIVE="${BACKUP_DIR}/knowledge_base_${DATE_FORMAT}.db.gz"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== 辅助函数 ====================

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# ==================== 备份流程 ====================

main() {
    log INFO "=========================================="
    log INFO "开始数据库备份"
    log INFO "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log INFO "=========================================="

    # 1. 检查数据库文件是否存在
    if [ ! -f "$DB_PATH" ]; then
        log ERROR "数据库文件不存在: $DB_PATH"
        exit 1
    fi

    # 2. 创建备份目录
    if [ ! -d "$BACKUP_DIR" ]; then
        log INFO "创建备份目录: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi

    # 3. 检查数据库完整性
    log INFO "检查数据库完整性..."
    if sqlite3 "$DB_PATH" "PRAGMA integrity_check;" | grep -q "ok"; then
        log SUCCESS "数据库完整性检查通过"
    else
        log ERROR "数据库完整性检查失败"
        sqlite3 "$DB_PATH" "PRAGMA integrity_check;"
        exit 1
    fi

    # 4. 使用SQLite的.backup命令备份（推荐方法，支持热备份）
    log INFO "备份数据库到: $BACKUP_FILE"
    sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

    if [ $? -eq 0 ]; then
        log SUCCESS "数据库备份成功"
    else
        log ERROR "数据库备份失败"
        exit 1
    fi

    # 5. 验证备份文件
    log INFO "验证备份文件..."
    if [ -f "$BACKUP_FILE" ]; then
        local backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
        log SUCCESS "备份文件大小: $backup_size"

        # 验证备份文件的完整性
        if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
            log SUCCESS "备份文件完整性检查通过"
        else
            log ERROR "备份文件损坏"
            exit 1
        fi
    else
        log ERROR "备份文件未找到"
        exit 1
    fi

    # 6. 压缩备份文件（可选）
    log INFO "压缩备份文件..."
    if gzip -c "$BACKUP_FILE" > "$BACKUP_ARCHIVE"; then
        local archive_size=$(du -h "$BACKUP_ARCHIVE" | cut -f1)
        log SUCCESS "压缩完成，压缩后大小: $archive_size"

        # 删除未压缩的备份文件
        rm -f "$BACKUP_FILE"
    else
        log WARNING "压缩失败，保留未压缩的备份文件"
    fi

    # 7. 清理旧备份（保留最近N天）
    log INFO "清理${RETENTION_DAYS}天前的旧备份..."

    local deleted_count=0
    for old_backup in $(find "$BACKUP_DIR" -name "knowledge_base_*.db*" -mtime +$RETENTION_DAYS); do
        log INFO "删除: $(basename $old_backup)"
        rm -f "$old_backup"
        deleted_count=$((deleted_count + 1))
    done

    if [ $deleted_count -gt 0 ]; then
        log SUCCESS "删除了 $deleted_count 个旧备份"
    else
        log INFO "没有需要清理的旧备份"
    fi

    # 8. 列出当前所有备份
    log INFO "=========================================="
    log INFO "当前备份列表:"
    log INFO "=========================================="

    local backup_count=$(ls -1 "$BACKUP_DIR"/knowledge_base_*.db* 2>/dev/null | wc -l)

    if [ $backup_count -gt 0 ]; then
        ls -lh "$BACKUP_DIR"/knowledge_base_*.db* | while read line; do
            echo "  $line"
        done
        log INFO "总计: $backup_count 个备份文件"
    else
        log WARNING "没有备份文件"
    fi

    # 9. 完成
    log SUCCESS "=========================================="
    log SUCCESS "✅ 数据库备份完成！"
    log SUCCESS "备份文件: $(basename $BACKUP_ARCHIVE)"
    log SUCCESS "=========================================="

    exit 0
}

# 执行主流程
main
