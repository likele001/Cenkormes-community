#!/usr/bin/env bash
set -euo pipefail

cd /app

wait_for_mysql() {
  local host="${MYSQL_HOST:-mysql}"
  local port="${MYSQL_PORT:-3306}"
  local max="${MYSQL_WAIT_SECONDS:-60}"
  local i=0
  echo "等待 MySQL ${host}:${port} ..."
  while ! python -c "
import socket, sys
s = socket.socket()
s.settimeout(2)
try:
    s.connect(('${host}', int('${port}')))
except OSError:
    sys.exit(1)
finally:
    s.close()
" 2>/dev/null; do
    i=$((i + 1))
    if [ "$i" -ge "$max" ]; then
      echo "错误: MySQL 在 ${max}s 内未就绪"
      exit 1
    fi
    sleep 1
  done
  echo "MySQL 已就绪"
}

if [ "${SKIP_DB_WAIT:-0}" != "1" ]; then
  wait_for_mysql
fi

if [ "${SKIP_MIGRATE:-0}" != "1" ]; then
  echo "执行数据库迁移..."
  alembic upgrade head
fi

exec "$@"
