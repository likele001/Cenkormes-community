# 0003- 迁移建表缺列报 UndefinedColumnError
- 日期：2026-09
- 模块：数据库 / Alembic 迁移
- 严重度：🔴 高
- 状态：已解决

## 症状
查询/计数触发 `UndefinedColumnError: column <X>.deleted_at does not exist`。

## 根因
模型是软删除（带 deleted_at 列），但 create_table 迁移里漏了该列，线上表结构跟不上模型。

## 解决方案
1. 建表迁移必须与模型字段完全一致（含 deleted_at 等软删列）
2. 对已上线缺列的表，写幂等补列脚本，并在全局 + 应用两处 alembic/versions 都放迁移文件：
```sql
ALTER TABLE <表> ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL;
```

## 涉及文件
- backend/alembic/versions/*.py 与各 app 的 alembic/versions

## 预防
模型新增列后，检查线上表是否缺列；缺则用幂等 ALTER 补齐，且迁移文件双路径放置保证安装包完整。
