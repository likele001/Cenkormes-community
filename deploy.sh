#!/usr/bin/env bash
# LightMes 生产环境一键部署脚本
# 用于服务器迁移后快速部署

set -e

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR="$ROOT_DIR/backend"

echo "=== LightMes 生产环境部署 ==="

# 检查 Python 环境
PYTHON_BIN="/www/server/pyporject_evn/lightmes/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "警告: Python 虚拟环境不存在，使用系统 Python"
    PYTHON_BIN="python3"
fi

# 创建 systemd 服务文件
echo ">>> 配置 Celery Worker 服务..."
cat > /etc/systemd/system/lightmes-celery-worker.service << 'EOF'
[Unit]
Description=LightMes Celery Worker
After=network.target redis.target mysql.target

[Service]
Type=simple
User=root
WorkingDirectory=/www/wwwroot/lightmes/backend
ExecStart=/www/server/pyporject_evn/lightmes/bin/celery -A app.celery_app worker -l info --concurrency=4 -Q celery,default,ai -n lightmes@%%h
Restart=always
RestartSec=5
KillSignal=SIGTERM
StandardOutput=file:/tmp/celery_worker.log
StandardError=file:/tmp/celery_worker_error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建 Celery Beat 服务文件
echo ">>> 配置 Celery Beat 服务..."
cat > /etc/systemd/system/lightmes-celery-beat.service << 'EOF'
[Unit]
Description=LightMes Celery Beat Scheduler
After=network.target redis.target mysql.target

[Service]
Type=simple
User=root
WorkingDirectory=/www/wwwroot/lightmes/backend
ExecStart=/www/server/pyporject_evn/lightmes/bin/celery -A app.celery_app beat -l info -S app.schedulers.database:DatabaseScheduler
Restart=always
RestartSec=5
KillSignal=SIGTERM
StandardOutput=file:/tmp/celery_beat.log
StandardError=file:/tmp/celery_beat_error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建 Uvicorn 服务文件
echo ">>> 配置 FastAPI 服务..."
cat > /etc/systemd/system/lightmes-api.service << 'EOF'
[Unit]
Description=LightMes FastAPI Server
After=network.target redis.target mysql.target

[Service]
Type=simple
User=root
WorkingDirectory=/www/wwwroot/lightmes/backend
ExecStart=/www/server/pyporject_evn/lightmes/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
KillSignal=SIGTERM
StandardOutput=file:/tmp/lightmes_api.log
StandardError=file:/tmp/lightmes_api_error.log

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
echo ">>> 重载 systemd 配置..."
systemctl daemon-reload

# 启用并启动服务
echo ">>> 启动服务..."
systemctl enable lightmes-celery-worker
systemctl enable lightmes-celery-beat
systemctl enable lightmes-api

systemctl restart lightmes-celery-worker
systemctl restart lightmes-celery-beat
systemctl restart lightmes-api

# 检查服务状态
echo ""
echo "=== 服务状态 ==="
systemctl status lightmes-celery-worker --no-pager -l
systemctl status lightmes-celery-beat --no-pager -l
systemctl status lightmes-api --no-pager -l

echo ""
echo "=== 部署完成 ==="
echo "管理命令:"
echo "  查看状态: systemctl status lightmes-celery-worker"
echo "  重启服务: systemctl restart lightmes-celery-worker"
echo "  查看日志: tail -f /tmp/celery_worker.log"
echo ""