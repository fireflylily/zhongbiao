#!/bin/bash
################################################################################
# 数据库同步到阿里云脚本
# 用途: 将本地 SQLite 数据库备份并上传到阿里云服务器
# 作者: AI Tender System
# 日期: 2025-11-03
################################################################################

set -e  # 遇到错误立即退出

# 配置变量
ALIYUN_HOST="8.140.21.235"
ALIYUN_USER="lvhe"
ALIYUN_PROJECT_DIR="/var/www/ai-tender-system"
LOCAL_PROJECT_DIR="/Users/lvhe/Downloads/zhongbiao/zhongbiao"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}数据库同步到阿里云${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 数据库列表（优先使用 data 目录下的数据库）
DATABASES=(
    "ai_tender_system/data/knowledge_base.db"
    "ai_tender_system/data/tender.db"
    "ai_tender_system/data/resume_library.db"
    "ai_tender_system/database/companies.db"
)

# 步骤1: 检查本地数据库
echo -e "${YELLOW}[1/6] 检查本地数据库...${NC}"
cd "$LOCAL_PROJECT_DIR"

for db in "${DATABASES[@]}"; do
    if [ -f "$db" ]; then
        size=$(du -h "$db" | cut -f1)
        echo "  ✓ $db ($size)"
    else
        echo "  ✗ $db (不存在)"
    fi
done
echo ""

# 步骤2: 创建本地备份
echo -e "${YELLOW}[2/6] 创建本地备份...${NC}"
BACKUP_DIR="ai_tender_system/data/db_backups"
mkdir -p "$BACKUP_DIR"

for db in "${DATABASES[@]}"; do
    if [ -f "$db" ]; then
        db_name=$(basename "$db")
        backup_file="${BACKUP_DIR}/${db_name%.db}_${BACKUP_TIMESTAMP}.db"
        cp "$db" "$backup_file"
        echo "  ✓ 已备份: $backup_file"
    fi
done
echo ""

# 步骤3: 在阿里云创建远程备份
echo -e "${YELLOW}[3/6] 在阿里云创建远程备份...${NC}"
ssh ${ALIYUN_USER}@${ALIYUN_HOST} << 'ENDSSH'
cd /var/www/ai-tender-system
mkdir -p ai_tender_system/data/db_backups

# 备份现有数据库
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "  阿里云备份时间戳: $BACKUP_TIMESTAMP"

for db in ai_tender_system/data/*.db ai_tender_system/database/*.db; do
    if [ -f "$db" ]; then
        db_name=$(basename "$db")
        backup_file="ai_tender_system/data/db_backups/${db_name%.db}_${BACKUP_TIMESTAMP}.db"
        cp "$db" "$backup_file" 2>/dev/null || true
        echo "  ✓ 已备份: $backup_file"
    fi
done
ENDSSH
echo ""

# 步骤4: 上传数据库到阿里云
echo -e "${YELLOW}[4/6] 上传数据库到阿里云...${NC}"

for db in "${DATABASES[@]}"; do
    if [ -f "$db" ]; then
        echo "  上传: $db"

        # 确保远程目录存在
        remote_dir=$(dirname "$db")
        ssh ${ALIYUN_USER}@${ALIYUN_HOST} "mkdir -p ${ALIYUN_PROJECT_DIR}/${remote_dir}"

        # 上传数据库
        scp "$db" ${ALIYUN_USER}@${ALIYUN_HOST}:${ALIYUN_PROJECT_DIR}/$db

        if [ $? -eq 0 ]; then
            echo "  ✓ 上传成功"
        else
            echo -e "  ${RED}✗ 上传失败${NC}"
            exit 1
        fi
    fi
done
echo ""

# 步骤5: 验证阿里云数据库
echo -e "${YELLOW}[5/6] 验证阿里云数据库...${NC}"
ssh ${ALIYUN_USER}@${ALIYUN_HOST} << 'ENDSSH'
cd /var/www/ai-tender-system

echo "  数据库文件列表:"
for db in ai_tender_system/data/*.db ai_tender_system/database/*.db; do
    if [ -f "$db" ]; then
        size=$(du -h "$db" | cut -f1)
        echo "    ✓ $db ($size)"

        # 检查数据库完整性
        if sqlite3 "$db" "PRAGMA integrity_check;" > /dev/null 2>&1; then
            echo "      → 完整性检查: 通过"
        else
            echo "      → 完整性检查: 失败"
        fi
    fi
done

# 显示数据统计
echo ""
echo "  knowledge_base.db 数据统计:"
sqlite3 ai_tender_system/data/knowledge_base.db << 'SQL'
.headers on
.mode column
SELECT
    (SELECT COUNT(*) FROM companies) as companies,
    (SELECT COUNT(*) FROM documents) as documents,
    (SELECT COUNT(*) FROM resumes) as resumes,
    (SELECT COUNT(*) FROM case_studies) as case_studies,
    (SELECT COUNT(*) FROM tender_projects) as projects;
SQL
ENDSSH
echo ""

# 步骤6: 重启阿里云应用
echo -e "${YELLOW}[6/6] 重启阿里云应用...${NC}"
ssh ${ALIYUN_USER}@${ALIYUN_HOST} << 'ENDSSH'
# 重启应用以加载新数据库
sudo supervisorctl restart ai-tender-system

# 等待启动
sleep 3

# 检查状态
sudo supervisorctl status ai-tender-system
ENDSSH
echo ""

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}数据库同步完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "备份位置:"
echo "  本地: $LOCAL_PROJECT_DIR/$BACKUP_DIR"
echo "  阿里云: $ALIYUN_PROJECT_DIR/ai_tender_system/data/db_backups"
echo ""
echo "验证步骤:"
echo "  1. 访问: http://$ALIYUN_HOST"
echo "  2. 登录系统"
echo "  3. 检查公司、知识库、简历等数据是否同步成功"
echo ""
