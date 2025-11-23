#!/bin/bash
# AI标书系统 - 更新Nginx配置脚本
# 用途：在阿里云服务器上快速应用Nginx配置

set -e  # 遇到错误立即退出

echo "=== AI标书系统 - 更新Nginx配置 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root权限运行此脚本"
    echo "   使用命令: sudo ./update_nginx.sh"
    exit 1
fi

# 配置文件路径
NGINX_CONF_SOURCE="./nginx/ai-tender.conf"
NGINX_CONF_TARGET="/etc/nginx/sites-available/ai-tender"
NGINX_CONF_ENABLED="/etc/nginx/sites-enabled/ai-tender"

# 1. 检查源配置文件是否存在
if [ ! -f "$NGINX_CONF_SOURCE" ]; then
    echo "❌ 配置文件不存在: $NGINX_CONF_SOURCE"
    exit 1
fi

echo "[1/5] 备份当前Nginx配置..."
if [ -f "$NGINX_CONF_TARGET" ]; then
    BACKUP_FILE="$NGINX_CONF_TARGET.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$NGINX_CONF_TARGET" "$BACKUP_FILE"
    echo "✅ 备份完成: $BACKUP_FILE"
else
    echo "ℹ️  首次配置，无需备份"
fi

# 2. 复制新配置
echo "[2/5] 复制新配置文件..."
cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_TARGET"
echo "✅ 配置文件已复制"

# 3. 创建软链接（如果不存在）
echo "[3/5] 创建软链接..."
if [ ! -L "$NGINX_CONF_ENABLED" ]; then
    ln -s "$NGINX_CONF_TARGET" "$NGINX_CONF_ENABLED"
    echo "✅ 软链接已创建"
else
    echo "ℹ️  软链接已存在"
fi

# 4. 测试Nginx配置
echo "[4/5] 测试Nginx配置..."
if nginx -t; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败！"
    echo "   正在恢复备份..."
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$NGINX_CONF_TARGET"
        echo "✅ 已恢复备份配置"
    fi
    exit 1
fi

# 5. 重启Nginx
echo "[5/5] 重启Nginx服务..."
systemctl restart nginx

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务重启成功"
else
    echo "❌ Nginx服务启动失败！"
    systemctl status nginx
    exit 1
fi

# 验证配置
echo ""
echo "=== 配置验证 ==="
echo "📋 关键配置项："
grep -E "client_max_body_size|proxy_.*_timeout" "$NGINX_CONF_TARGET" | sed 's/^/  /'

echo ""
echo "=== 部署完成 ==="
echo "✅ Nginx配置已更新"
echo "✅ 文件上传限制: 100MB"
echo "✅ 超时时间: 600秒"
echo ""
echo "🎉 现在可以上传大型审计报告PDF了！"
