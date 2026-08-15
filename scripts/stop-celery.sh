#!/usr/bin/env bash
# 停止 LightMes Celery worker + beat
set -euo pipefail

LOG_DIR="${LOG_DIR:-/tmp/lightmes-celery}"

stop_pid_file() {
  local name="$1"
  local pf="$LOG_DIR/${name}.pid"
  if [ -f "$pf" ]; then
    local pid
    pid="$(cat "$pf")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "已停止 ${name} (PID $pid)"
    fi
    rm -f "$pf"
  fi
}

stop_pid_file worker
stop_pid_file beat

# 兜底：结束本项目 celery 进程
pkill -f '/www/server/pyporject_evn/lightmes/bin/celery -A app.celery_app' 2>/dev/null || true
echo "Celery 已停止"
