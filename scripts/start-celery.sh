#!/usr/bin/env bash
# LightMes Celery worker + beat 启动脚本（需 Redis 已运行）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${VENV:-/www/server/pyporject_evn/lightmes}"
BACKEND="$ROOT/backend"
LOG_DIR="${LOG_DIR:-/tmp/lightmes-celery}"
mkdir -p "$LOG_DIR"

cd "$BACKEND"

if ! "$VENV/bin/python" -c "import redis; r=redis.from_url('${REDIS_URL:-redis://127.0.0.1:6379/0}'); r.ping()" 2>/dev/null; then
  echo "错误: Redis 不可达，请先启动 Redis（见 docs/宝塔部署常见错误排查.md）"
  exit 1
fi

# 幂等：worker / beat 已经在跑就直接退出（用于 @reboot + */5 自愈 cron）
if pgrep -fa 'celery -A app.celery_app worker' | grep -q "$VENV/bin/celery" && pgrep -fa 'celery -A app.celery_app beat' | grep -q "$VENV/bin/celery"; then
  echo "Celery worker + beat 已在运行（$VENV），跳过启动"
  exit 0
fi

echo "启动 Celery worker..."
nohup "$VENV/bin/celery" -A app.celery_app worker -l info \
  >> "$LOG_DIR/worker.log" 2>&1 &
echo $! > "$LOG_DIR/worker.pid"

echo "启动 Celery beat..."
nohup "$VENV/bin/celery" -A app.celery_app beat -l info -S app.schedulers.database:DatabaseScheduler \
  >> "$LOG_DIR/beat.log" 2>&1 &
echo $! > "$LOG_DIR/beat.pid"

echo "Celery 已后台启动"
echo "  worker PID: $(cat "$LOG_DIR/worker.pid")"
echo "  beat   PID: $(cat "$LOG_DIR/beat.pid")"
echo "  日志目录: $LOG_DIR"
