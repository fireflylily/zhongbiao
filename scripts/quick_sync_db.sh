#!/bin/bash
################################################################################
# 快速数据库同步脚本（仅同步核心数据库）
# 用途: 将本地 knowledge_base.db 快速同步到阿里云
################################################################################

set -e

# 配置
ALIYUN_HOST="8.140.21.235"
ALIYUN_USER="lvhe"
DB_FILE="ai_tender_system/data/knowledge_base.db"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 快速同步 knowledge_base.db 到阿里云..."
echo ""

# 1. 检查本地数据库
if [ ! -f "$DB_FILE" ]; then
    echo "❌ 错误: 找不到本地数据库 $DB_FILE"
    exit 1
fi

LOCAL_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo "✓ 本地数据库: $DB_FILE ($LOCAL_SIZE)"

# 2. 显示本地数据统计
echo ""
echo "📊 本地数据统计:"
sqlite3 "$DB_FILE" << 'SQL'
.mode column
.headers on
SELECT
    (SELECT COUNT(*) FROM companies) as 公司数,
    (SELECT COUNT(*) FROM documents) as 文档数,
    (SELECT COUNT(*) FROM resumes) as 简历数,
    (SELECT COUNT(*) FROM case_studies) as 案例数,
    (SELECT COUNT(*) FROM tender_projects) as 项目数;
SQL

# 3. 在阿里云备份现有数据库
echo ""
echo "💾 备份阿里云现有数据库..."
ssh ${ALIYUN_USER}@${ALIYUN_HOST} << ENDSSH
cd /var/www/ai-tender-system
mkdir -p ai_tender_system/data/db_backups

if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "ai_tender_system/data/db_backups/knowledge_base_${BACKUP_TIMESTAMP}.db"
    echo "  ✓ 已备份到: knowledge_base_${BACKUP_TIMESTAMP}.db"
else
    echo "  ℹ️  阿里云暂无数据库，跳过备份"
fi
ENDSSH

# 4. 上传新数据库
echo ""
echo "📤 上传数据库到阿里云..."
scp "$DB_FILE" ${ALIYUN_USER}@${ALIYUN_HOST}:/var/www/ai-tender-system/$DB_FILE

if [ $? -eq 0 ]; then
    echo "  ✓ 上传成功"
else
    echo "  ❌ 上传失败"
    exit 1
fi

# 5. 验证并重启
echo ""
echo "✅ 验证并重启应用..."
ssh ${ALIYUN_USER}@${ALIYUN_HOST} << 'ENDSSH'
cd /var/www/ai-tender-system

# 验证数据库完整性
if sqlite3 ai_tender_system/data/knowledge_base.db "PRAGMA integrity_check;" > /dev/null 2>&1; then
    echo "  ✓ 数据库完整性检查通过"
else
    echo "  ❌ 数据库完整性检查失败"
    exit 1
fi

# 显示阿里云数据统计
echo ""
echo "📊 阿里云数据统计:"
sqlite3 ai_tender_system/data/knowledge_base.db << 'SQL'
.mode column
.headers on
SELECT
    (SELECT COUNT(*) FROM companies) as 公司数,
    (SELECT COUNT(*) FROM documents) as 文档数,
    (SELECT COUNT(*) FROM resumes) as 简历数,
    (SELECT COUNT(*) FROM case_studies) as 案例数,
    (SELECT COUNT(*) FROM tender_projects) as 项目数;
SQL

# 重启应用
echo ""
echo "🔄 重启应用..."
sudo supervisorctl restart ai-tender-system
sleep 2
sudo supervisorctl status ai-tender-system
ENDSSH

echo ""
echo "🎉 同步完成！"
echo ""
echo "下一步:"
echo "  访问 http://$ALIYUN_HOST 验证数据"
echo ""
