#!/usr/bin/env bash
# 在 api 容器内初始化演示数据与平台管理员
set -euo pipefail

cd /app

PLATFORM_USER="${PLATFORM_USER:-platform}"
PLATFORM_PASS="${PLATFORM_PASS:-platform123}"

echo "==> 演示工厂数据 (demo_data.py) ..."
PYTHONPATH=. python scripts/demo_data.py

echo "==> 平台管理员 (init_platform_admin.py) ..."
PYTHONPATH=. python scripts/init_platform_admin.py "$PLATFORM_USER" "$PLATFORM_PASS"

echo ""
echo "完成。演示租户 DEMO / admin / admin123"
echo "平台管理员 ${PLATFORM_USER} / ${PLATFORM_PASS}"
