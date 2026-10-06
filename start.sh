#!/usr/bin/env bash
set -e

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

START_ADMIN=0
START_H5=0
START_CELERY=1

for arg in "$@"; do
  case "$arg" in
    all|--all)
      START_ADMIN=1
      START_H5=1
      ;;
    admin|--admin)
      START_ADMIN=1
      ;;
    h5|--h5)
      START_H5=1
      ;;
    celery|--celery)
      START_CELERY=1
      ;;
    --no-celery)
      START_CELERY=0
      ;;
    -h|--help)
      echo "用法: ./start.sh [all|admin|h5] [--celery|--no-celery]"
      exit 0
      ;;
    *)
      echo "未知参数: $arg"
      echo "用法: ./start.sh [all|admin|h5] [--celery|--no-celery]"
      exit 1
      ;;
  esac
done

pids=()

cleanup() {
  for pid in "${pids[@]}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}

trap cleanup EXIT INT TERM

if [ "$START_ADMIN" -eq 1 ]; then
  (
    cd "$ROOT_DIR/frontend-admin-pro"
    npm install
    npm run dev -- --host 0.0.0.0 --port 5173
  ) &
  pids+=("$!")
fi

if [ "$START_H5" -eq 1 ]; then
  (
    cd "$ROOT_DIR/frontend-h5"
    npm install
    npm run dev -- --host 0.0.0.0 --port 5174
  ) &
  pids+=("$!")
fi

cd "$ROOT_DIR/backend"

PYTHON_BIN=python3
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python
fi

if [ "$START_CELERY" -eq 1 ]; then
  (
    "$PYTHON_BIN" -m celery -A app.celery_app.celery worker -l info
  ) &
  pids+=("$!")

  (
    "$PYTHON_BIN" -m celery -A app.celery_app.celery beat -l info
  ) &
  pids+=("$!")
fi

"$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
