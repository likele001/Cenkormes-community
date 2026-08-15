#!/bin/bash
# LightMes Celery 服务部署脚本
# 用法：在新服务器上部署项目后，执行此脚本注册 systemd 服务
# 前提：项目代码已在 /www/wwwroot/lightmes 下，Python 虚拟环境已就绪

set -e

PROJECT_DIR="/www/wwwroot/lightmes"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== 部署 LightMes Celery 系统服务 ==="

# 检查项目目录
if [ ! -d "$PROJECT_DIR/backend" ]; then
    echo "❌ 未找到项目目录: $PROJECT_DIR/backend"
    echo "请确认项目代码已放置到 $PROJECT_DIR"
    exit 1
fi

# 检查 Python 虚拟环境
if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    echo "⚠️  未找到 .env 文件，请确保已配置环境变量"
fi

# 复制服务文件
echo "1. 复制 systemd 服务文件..."
cp "$PROJECT_DIR/scripts/systemd/lightmes-celery.service" "$SYSTEMD_DIR/"
cp "$PROJECT_DIR/scripts/systemd/lightmes-beat.service" "$SYSTEMD_DIR/"

# 重新加载并启用
echo "2. 重新加载 systemd 配置..."
systemctl daemon-reload

echo "3. 启用并启动服务..."
systemctl enable lightmes-celery.service
systemctl enable lightmes-beat.service
systemctl start lightmes-celery.service
systemctl start lightmes-beat.service

# 检查状态
sleep 2
echo ""
echo "=== 服务状态 ==="
systemctl is-active lightmes-celery.service lightmes-beat.service

echo ""
echo "✅ 部署完成！Celery Worker 和 Beat 已启动并设为开机自启。"
