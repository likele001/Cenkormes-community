#!/usr/bin/env bash
# 一键发布：拆分 → 导出社区版 + 专业版 → 提交并推送
# 用法:
#   bash scripts/release-all.sh "更新说明：修复报工审核"
#   bash scripts/release-all.sh --dry-run "更新说明"
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMMUNITY_DIR="${COMMUNITY_DIR:-$(dirname "$ROOT")/lightmes-community}"
PRO_DIR="${PRO_DIR:-$(dirname "$ROOT")/lightmes-pro}"
COMMUNITY_REMOTE="${COMMUNITY_REMOTE:-git@github.com:likele001/lightmes-community.git}"
PRO_REMOTE="${PRO_REMOTE:-git@github.com:likele001/lightmes-pro.git}"

DRY_RUN=0
# 存储 commit -m 参数，索引 0 为标题，1+ 为详情段落
COMMITS=()

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -m)        ;;                          # 跳过 -m 标志（下一 arg 是内容）
    -m=*)      COMMITS+=("${arg#-m=}") ;;   # 支持 -m=value 形式
    *)         COMMITS+=("$arg") ;;
  esac
done

if [[ ${#COMMITS[@]} -eq 0 ]]; then
  echo "用法: bash scripts/release-all.sh [-m \"标题\"] [-m \"详情 1\"] [-m \"详情 2\" ...]"
  echo "示例（多 -m）: bash scripts/release-all.sh \\"
  echo "    -m \"feat(platform): 支持套餐层级、交付方式及行业包权限控制\" \\"
  echo "    -m \"在套餐表中新增 tier、max_industries、allowed_industry_codes 和 delivery_mode 字段\" \\"
  echo "    -m \"平台接口新增套餐层级和交付方式字段的校验和保存逻辑\""
  echo "兼容（单 -m）: bash scripts/release-all.sh -m \"修复 H5 报工\""
  echo "试跑: bash scripts/release-all.sh --dry-run -m \"更新说明\""
  exit 1
fi

_run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

_push_repo() {
  local name="$1"
  local dir="$2"
  local remote="$3"
  local prefix="$4"

  echo ""
  echo "==> 发布 $name"
  echo "    目录: $dir"

  if [[ ! -d "$dir" ]]; then
    echo "错误: 目录不存在 $dir"
    exit 1
  fi

  cd "$dir"

  if [[ ! -d .git ]]; then
    echo "    初始化 Git 仓库..."
    _run git init
    _run git branch -M main
    _run git remote add origin "$remote"
  elif ! git remote get-url origin &>/dev/null; then
    _run git remote add origin "$remote"
  else
    local url
    url="$(git remote get-url origin)"
    if [[ "$url" != "$remote" ]]; then
      _run git remote set-url origin "$remote"
    fi
  fi

  _run git add -A

  if [[ "$DRY_RUN" -eq 1 ]]; then
    git status --short | head -20
    echo "    （dry-run 跳过 commit / push）"
    return 0
  fi

  if git diff --cached --quiet; then
    echo "    无变更，跳过提交"
  else
    # 构造多 -m commit 参数：prefix + COMMITS[0] 作为标题，后续 COMMITS 作为详情
    local m_args=()
    if [[ -n "$prefix" ]]; then
      m_args=(-m "${prefix}${COMMITS[0]}")
      local i
      for ((i = 1; i < ${#COMMITS[@]}; i++)); do
        m_args+=(-m "${COMMITS[$i]}")
      done
    else
      local c
      for c in "${COMMITS[@]}"; do
        m_args+=(-m "$c")
      done
    fi
    _run git commit "${m_args[@]}"
  fi

  git push -u origin main
  echo "    ✅ $name 已推送"
}

echo "========================================"
echo " LightMes 一键发布（社区版 + 专业版）"
echo "========================================"
echo "说明: ${COMMITS[0]}$([[ ${#COMMITS[@]} -gt 1 ]] && echo " (+ $((${#COMMITS[@]}-1)) 段详情)")"
echo "社区: $COMMUNITY_DIR"
echo "专业: $PRO_DIR"

cd "$ROOT"

# ---- 版本号自动递增 ----
VERSION_FILE="$ROOT/VERSION"
CHANGELOG_FILE="$ROOT/backend/CHANGELOG.json"
CURRENT_VER="$(cat "$VERSION_FILE" 2>/dev/null || echo "v0.0.0")"
# 提取版本号段：v1.2.3 → major=1 minor=2 patch=3
VER_NUM="${CURRENT_VER#v}"
MAJOR="${VER_NUM%%.*}"
REST="${VER_NUM#*.}"
MINOR="${REST%%.*}"
PATCH="${REST##*.}"
# 默认递增 patch，可通过 VERSION_BUMP=major|minor|patch 环境变量控制
BUMP="${VERSION_BUMP:-patch}"
case "$BUMP" in
  major) NEW_VER="v$((MAJOR+1)).0.0" ;;
  minor) NEW_VER="v$MAJOR.$((MINOR+1)).0" ;;
  *)     NEW_VER="v$MAJOR.$MINOR.$((PATCH+1))" ;;
esac
echo ""
echo "==> 版本号: $CURRENT_VER → $NEW_VER"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] echo $NEW_VER > $VERSION_FILE"
else
  echo "$NEW_VER" > "$VERSION_FILE"
fi

# ---- 追加本次开发日志到 CHANGELOG.json ----
# 将 COMMITS 拼接为一段完整说明，作为本次发布的开发日志描述
CHANGE_DESC="${COMMITS[0]}"
for ((i = 1; i < ${#COMMITS[@]}; i++)); do
  CHANGE_DESC="${CHANGE_DESC}；${COMMITS[$i]}"
done
TODAY="$(date +%Y-%m-%d)"
echo "==> 开发日志: [$NEW_VER] $CHANGE_DESC"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] 追加 $NEW_VER / $TODAY 到 backend/CHANGELOG.json"
else
  python3 - "$CHANGELOG_FILE" "$NEW_VER" "$TODAY" "$CHANGE_DESC" <<'PYEOF'
import json
import sys

path, ver, today, desc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
try:
    with open(path, "r", encoding="utf-8") as f:
        rows = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    rows = []
# 幂等：已存在同版本号则替换描述
rows = [r for r in rows if r.get("version") != ver]
rows.append({"version": ver, "release_date": today, "description": desc})
rows.sort(key=lambda r: r.get("release_date", ""))
with open(path, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
    f.write("\n")
PYEOF
fi

echo ""
echo "==> 1/5 拆分并校验"
_run bash "$ROOT/scripts/split-packages.sh"
_run bash "$ROOT/scripts/verify-community-clean.sh"

echo ""
echo "==> 2/5 提交 VERSION + CHANGELOG 到主仓库"
pushd "$ROOT" >/dev/null
if git diff --quiet "$VERSION_FILE" "$CHANGELOG_FILE" 2>/dev/null; then
  echo "    版本文件无变化，跳过提交"
else
  _run git add "$VERSION_FILE" "$CHANGELOG_FILE"
  _run git commit -m "chore: bump version to $NEW_VER"
fi
popd >/dev/null

echo ""
echo "==> 3/5 导出社区版"
SKIP_SPLIT=1 _run bash "$ROOT/scripts/export-community-repo.sh" "$COMMUNITY_DIR"

echo ""
echo "==> 4/5 导出专业版"
SKIP_SPLIT=1 _run bash "$ROOT/scripts/export-pro-repo.sh" "$PRO_DIR"

echo ""
echo "==> 5/5 推送到 GitHub"
_push_repo "社区版 (lightmes-community)" "$COMMUNITY_DIR" "$COMMUNITY_REMOTE" \
  "[$NEW_VER] 更新社区版："
_push_repo "专业版 (lightmes-pro)" "$PRO_DIR" "$PRO_REMOTE" \
  "[$NEW_VER] 更新专业版："

echo ""
echo "========================================"
echo " 发布完成"
echo " 社区: https://github.com/likele001/lightmes-community"
echo " 专业: https://github.com/likele001/lightmes-pro"
echo "========================================"
