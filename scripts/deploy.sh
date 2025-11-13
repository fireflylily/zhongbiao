#!/bin/bash
#
# AI智能标书生成平台 - 自动部署脚本
# 用于生产环境部署，包含备份、更新、重启和验证功能
#
# 使用方法:
#   bash scripts/deploy.sh
#
# 作者: Claude Code
# 日期: 2025-10-31
#

set -e  # 遇到错误立即退出
set -o pipefail  # 管道命令出错也退出

# ==================== 配置变量 ====================

# 应用目录
APP_DIR="/var/www/ai-tender-system"

# 数据库路径
DB_PATH="${APP_DIR}/ai_tender_system/data/knowledge_base.db"

# 备份目录
BACKUP_DIR="/var/backups/ai-tender-system"

# 日志文件
LOG_FILE="${APP_DIR}/logs/deploy.log"

# 虚拟环境路径
VENV_PATH="${APP_DIR}/venv"

# Supervisor服务名称
SERVICE_NAME="ai-tender-system"

# 回滚标记文件
ROLLBACK_FILE="${APP_DIR}/.last_deploy_commit"

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
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # 输出到终端
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

    # 同时写入日志文件
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# 错误处理函数
handle_error() {
    log ERROR "部署失败！正在回滚..."
    rollback
    exit 1
}

# 设置错误处理
trap 'handle_error' ERR

# ==================== 部署步骤 ====================

# 1. 前置检查
pre_check() {
    log INFO "=========================================="
    log INFO "开始部署前检查..."
    log INFO "=========================================="

    # 检查是否在正确的目录
    if [ ! -f "${APP_DIR}/main.py" ]; then
        log ERROR "未找到main.py，请确认在正确的目录中"
        exit 1
    fi

    # 检查虚拟环境
    if [ ! -d "$VENV_PATH" ]; then
        log ERROR "虚拟环境不存在，请先运行初始化脚本"
        exit 1
    fi

    # 检查.env文件
    if [ ! -f "${APP_DIR}/.env" ]; then
        log WARNING ".env文件不存在，将使用默认配置"
    fi

    # 创建必要的目录
    mkdir -p "$BACKUP_DIR"
    mkdir -p "${APP_DIR}/logs"

    log SUCCESS "前置检查通过"
}

# 2. 记录当前版本（用于回滚）
save_current_version() {
    log INFO "记录当前版本..."

    cd "$APP_DIR"
    git rev-parse HEAD > "$ROLLBACK_FILE"

    local current_commit=$(cat "$ROLLBACK_FILE")
    log SUCCESS "当前版本: $current_commit"
}

# 3. 备份数据库
backup_database() {
    log INFO "=========================================="
    log INFO "开始备份数据库..."
    log INFO "=========================================="

    if [ -f "$DB_PATH" ]; then
        # 调用备份脚本
        bash "${APP_DIR}/scripts/backup_database.sh"

        if [ $? -eq 0 ]; then
            log SUCCESS "数据库备份完成"
        else
            log ERROR "数据库备份失败"
            exit 1
        fi
    else
        log WARNING "数据库文件不存在，跳过备份"
    fi
}

# 4. 拉取最新代码
pull_code() {
    log INFO "=========================================="
    log INFO "拉取最新代码..."
    log INFO "=========================================="

    cd "$APP_DIR"

    # 检查git状态
    if [ -n "$(git status --porcelain)" ]; then
        log WARNING "检测到未提交的更改，将暂存这些更改"
        git stash push -m "Auto-stash before deploy at $(date '+%Y-%m-%d %H:%M:%S')"
    fi

    # 拉取最新代码
    git fetch origin master
    git reset --hard origin/master

    local new_commit=$(git rev-parse HEAD)
    log SUCCESS "更新到版本: $new_commit"
}

# 5. 安装/更新依赖
update_dependencies() {
    log INFO "=========================================="
    log INFO "更新Python依赖..."
    log INFO "=========================================="

    cd "$APP_DIR"
    source "${VENV_PATH}/bin/activate"

    # 升级pip
    pip install --upgrade pip -q

    # 安装/更新依赖（使用生产依赖）
    if [ -f "requirements-prod.txt" ]; then
        log INFO "使用 requirements-prod.txt"
        pip install -r requirements-prod.txt --upgrade -q
    elif [ -f "requirements.txt" ]; then
        log INFO "使用 requirements.txt"
        pip install -r requirements.txt --upgrade -q
    else
        log ERROR "未找到依赖文件"
        exit 1
    fi

    # 确保gunicorn已安装
    if ! pip show gunicorn > /dev/null 2>&1; then
        log INFO "安装gunicorn..."
        pip install gunicorn -q
    fi

    log SUCCESS "依赖更新完成"
}

# 6. 执行数据库迁移（如果有）
run_migrations() {
    log INFO "=========================================="
    log INFO "检查数据库迁移..."
    log INFO "=========================================="

    cd "$APP_DIR"
    source "${VENV_PATH}/bin/activate"

    # 检查是否有迁移脚本
    MIGRATION_DIR="${APP_DIR}/ai_tender_system/database/migrations"

    if [ -d "$MIGRATION_DIR" ]; then
        # 查找所有.sql迁移文件
        for migration_file in $(ls "$MIGRATION_DIR"/*.sql 2>/dev/null | sort); do
            log INFO "发现迁移文件: $(basename $migration_file)"

            # 这里可以添加迁移执行逻辑
            # 暂时跳过，由管理员手动执行
            log WARNING "迁移需要手动执行: $migration_file"
        done
    else
        log INFO "未发现迁移文件"
    fi

    log SUCCESS "迁移检查完成"
}

# 7. 收集静态文件（构建前端）
collect_static() {
    log INFO "=========================================="
    log INFO "构建Vue.js前端..."
    log INFO "=========================================="

    cd "${APP_DIR}/frontend"

    # 检查Node.js和npm是否安装
    if ! command -v npm > /dev/null 2>&1; then
        log ERROR "npm未安装，请在服务器上安装Node.js和npm"
        exit 1
    fi

    log INFO "安装前端依赖..."
    npm install --quiet --legacy-peer-deps

    log INFO "开始构建前端应用 (npm run build)..."
    # 使用 --no-check 忽略TypeScript类型检查，加快部署速度
    npm run build:no-check

    log SUCCESS "前端构建完成！"
    cd "$APP_DIR" # 返回应用根目录
}

# 8. 重启应用
restart_app() {
    log INFO "=========================================="
    log INFO "重启应用服务..."
    log INFO "=========================================="

    # 使用supervisorctl重启
    if command -v supervisorctl > /dev/null 2>&1; then
        log INFO "使用Supervisor重启服务..."

        # 优雅重启（发送HUP信号，让Gunicorn平滑重启）
        sudo supervisorctl signal HUP "$SERVICE_NAME" 2>/dev/null || true

        # 等待2秒
        sleep 2

        # 检查状态
        if sudo supervisorctl status "$SERVICE_NAME" | grep -q RUNNING; then
            log SUCCESS "服务重启成功"
        else
            log WARNING "优雅重启可能失败，尝试硬重启..."
            sudo supervisorctl restart "$SERVICE_NAME"

            sleep 3

            if sudo supervisorctl status "$SERVICE_NAME" | grep -q RUNNING; then
                log SUCCESS "服务重启成功（硬重启）"
            else
                log ERROR "服务重启失败"
                sudo supervisorctl status "$SERVICE_NAME"
                exit 1
            fi
        fi
    else
        log ERROR "未找到supervisorctl命令"
        exit 1
    fi
}

# 9. 健康检查
health_check() {
    log INFO "=========================================="
    log INFO "执行健康检查..."
    log INFO "=========================================="

    local max_attempts=5
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log INFO "健康检查尝试 $attempt/$max_attempts..."

        # 检查HTTP响应
        if curl -f -s -o /dev/null http://localhost:8000; then
            log SUCCESS "HTTP健康检查通过"
            return 0
        fi

        log WARNING "健康检查失败，等待3秒后重试..."
        sleep 3
        attempt=$((attempt + 1))
    done

    log ERROR "健康检查失败，达到最大尝试次数"
    return 1
}

# 10. 清理旧文件
cleanup() {
    log INFO "=========================================="
    log INFO "清理临时文件..."
    log INFO "=========================================="

    cd "$APP_DIR"

    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    # 清理旧日志（保留最近7天）
    find "${APP_DIR}/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true

    log SUCCESS "清理完成"
}

# 11. 回滚函数
rollback() {
    log WARNING "=========================================="
    log WARNING "开始回滚到上一个版本..."
    log WARNING "=========================================="

    cd "$APP_DIR"

    if [ -f "$ROLLBACK_FILE" ]; then
        local last_commit=$(cat "$ROLLBACK_FILE")
        log INFO "回滚到: $last_commit"

        git reset --hard "$last_commit"

        # 重启服务
        sudo supervisorctl restart "$SERVICE_NAME"

        log SUCCESS "回滚完成"
    else
        log ERROR "未找到回滚信息，请手动修复"
    fi
}

# ==================== 主流程 ====================

main() {
    log INFO "=========================================="
    log INFO "🚀 AI智能标书生成平台 - 自动部署"
    log INFO "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log INFO "=========================================="

    # 执行部署步骤
    pre_check
    save_current_version
    backup_database
    pull_code
    update_dependencies
    run_migrations
    collect_static
    restart_app

    # 健康检查
    if health_check; then
        cleanup

        log SUCCESS "=========================================="
        log SUCCESS "✅ 部署成功！"
        log SUCCESS "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        log SUCCESS "=========================================="

        exit 0
    else
        log ERROR "健康检查失败，开始回滚"
        rollback
        exit 1
    fi
}

# 执行主流程
main
