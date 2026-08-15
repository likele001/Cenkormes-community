#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# LightMes 前端源代码自动备份脚本
# 在 Sprint 0 改造前备份原始文件，支持回滚。
#
# 用法：
#   bash scripts/backup_frontend.sh                    # 全部备份（默认）
#   bash scripts/backup_frontend.sh snapshot           # 仅快照备份（同名覆盖）
#   bash scripts/backup_frontend.sh restore <backup_dir> # 还原到指定备份
#
# 环境变量：
#   BACKUP_DIR  - 备份根目录（默认 /www/backups/lightmes/frontend）
#   KEEP_COPIES - 保留最近快照数（默认 10）
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$PROJECT_DIR/frontend-admin-pro/src"
BACKUP_DIR="${BACKUP_DIR:-/www/backups/lightmes/frontend}"
KEEP_COPIES="${KEEP_COPIES:-10}"

MODE="${1:-backup}"

mkdir -p "$BACKUP_DIR"

backup() {
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  TARGET="$BACKUP_DIR/pre-sprint0_$TIMESTAMP"

  echo "[$(date)] 备份前端源码: $SRC_DIR"
  echo "[$(date)] 目标: $TARGET"

  cp -a "$SRC_DIR" "$TARGET"

  # git 当前 hash
  GIT_HASH=$(cd "$PROJECT_DIR" && git rev-parse --short HEAD 2>/dev/null || echo "no-git")
  echo "$GIT_HASH" > "$TARGET/.backup_git_hash"
  date -u +"%Y-%m-%dT%H:%M:%SZ" > "$TARGET/.backup_timestamp"

  SIZE=$(du -sh "$TARGET" | cut -f1)
  echo "[$(date)] 备份完成: $TARGET ($SIZE)"
  echo "$TARGET"
}

snapshot() {
  # 快照模式：始终覆盖同一目录（节省空间），用作"回滚基线"
  TARGET="$BACKUP_DIR/snapshot_latest"
  rm -rf "$TARGET"
  cp -a "$SRC_DIR" "$TARGET"
  echo "[$(date)] 快照已更新: $TARGET ($(du -sh "$TARGET" | cut -f1))"
}

restore() {
  SOURCE="${2:-$BACKUP_DIR/snapshot_latest}"
  if [[ ! -d "$SOURCE" ]]; then
    echo "[$(date)] 错误: 备份源不存在: $SOURCE"
    exit 1
  fi

  # 先备份当前状态
  auto_backup="$BACKUP_DIR/pre-restore_$(date +"%Y%m%d_%H%M%S")"
  cp -a "$SRC_DIR" "$auto_backup"
  echo "[$(date)] 当前状态已保留: $auto_backup"

  # 还原
  echo "[$(date)] 还原: $SOURCE -> $SRC_DIR"
  rm -rf "$SRC_DIR"
  cp -a "$SOURCE" "$SRC_DIR"
  echo "[$(date)] 还原完成"
}

cleanup() {
  # 保留最近 KEEP_COPIES 次 pre-sprint0 备份，删除旧的
  ALL=($(ls -1d "$BACKUP_DIR"/pre-sprint0_* 2>/dev/null | sort -r || true))
  COUNT=${#ALL[@]}
  if [[ "$COUNT" -gt "$KEEP_COPIES" ]]; then
    DELETE_COUNT=$((COUNT - KEEP_COPIES))
    for ((i = COUNT - 1; i >= KEEP_COPIES; i--)); do
      echo "[$(date)] 删除旧备份: ${ALL[$i]}"
      rm -rf "${ALL[$i]}"
    done
    echo "[$(date)] 已清理 $DELETE_COUNT 个旧备份"
  fi
}

case "$MODE" in
  backup)
    backup
    cleanup
    ;;
  snapshot)
    snapshot
    ;;
  restore)
    restore "$@"
    ;;
  *)
    echo "用法: bash scripts/backup_frontend.sh [backup|snapshot|restore <dir>]"
    echo ""
    echo "  backup          - 创建带时间戳的备份（默认）"
    echo "  snapshot        - 创建/更新快照（始终覆盖 snapshot_latest）"
    echo "  restore <dir>   - 从指定目录还原"
    exit 1
    ;;
esac
