#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# LightMes MySQL 自动备份脚本
# 用法：
#   bash scripts/backup-db.sh                # 手动备份
#   BACKUP_DIR=/data/backups bash scripts/backup-db.sh  # 指定备份目录
#
# 定时任务（cron）示例：每天凌晨 2 点自动备份，保留最近 30 天
#   0 2 * * * cd /www/wwwroot/lightmes && bash scripts/backup-db.sh >> /var/log/lightmes-backup.log 2>&1
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 从 .env 读取数据库配置（如果存在）
if [[ -f "$PROJECT_DIR/backend/.env" ]]; then
    # shellcheck disable=SC1091
    set -a
    source "$PROJECT_DIR/backend/.env"
    set +a
fi

# 默认值
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-${DB_URL##*://}}"
DB_USER="${DB_USER%%:*}"
DB_PASS="${DB_PASS:-${DB_URL##*:}}"
DB_PASS="${DB_PASS%%@*}"
DB_NAME="${DB_NAME:-${DB_URL##*/}}"
DB_NAME="${DB_NAME%%\?*}"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
KEEP_DAYS="${KEEP_DAYS:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/lightmes_backup_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] 开始备份数据库: $DB_NAME@$DB_HOST:$DB_PORT"

# 执行备份
if command -v mysqldump &>/dev/null; then
    mysqldump \
        -h "$DB_HOST" \
        -P "$DB_PORT" \
        -u "$DB_USER" \
        -p"$DB_PASS" \
        --single-transaction \
        --routines \
        --triggers \
        --set-gtid-purged=OFF \
        "$DB_NAME" > "$BACKUP_FILE"

    # 压缩备份
    if command -v gzip &>/dev/null; then
        gzip "$BACKUP_FILE"
        BACKUP_FILE="${BACKUP_FILE}.gz"
    fi

    FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] 备份完成: $BACKUP_FILE ($FILESIZE)"
else
    echo "[$(date)] 错误: 未找到 mysqldump 命令，请安装 mysql-client"
    exit 1
fi

# 清理旧备份（保留最近 KEEP_DAYS 天）
DELETED=$(find "$BACKUP_DIR" -name "lightmes_backup_*" -type f -mtime "+$KEEP_DAYS" -delete -print | wc -l)
if [[ "$DELETED" -gt 0 ]]; then
    echo "[$(date)] 已清理 $DELETED 个超过 ${KEEP_DAYS} 天的旧备份"
fi

echo "[$(date)] 备份任务完成"
