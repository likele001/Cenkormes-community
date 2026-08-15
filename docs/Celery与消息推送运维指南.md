# LightMes Celery 与消息推送运维指南

> 适用范围：宝塔部署（Linux），LightMes 后端为 FastAPI + Celery + Redis + MySQL 5.7
> 关联文档：[工厂日报飞书企微推送配置指南.md](./工厂日报飞书企微推送配置指南.md)、[宝塔部署.md](./宝塔部署.md)

## 一、服务架构

LightMes 后端由 3 个进程组成，各司其职：

```
┌─────────────────────────────────────────────────────────────┐
│  [宝塔面板 · Python项目管理器]                                 │
│  uvicorn app.main:app → 8000 端口（API / 页面请求）            │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  [systemd: lightmes-beat.service]                           │
│  celery beat -S DatabaseScheduler（定时调度器）                │
│  作用：到点把任务投递到 Redis 队列（AI预警/日报/工资/推送刷新）  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  [systemd: lightmes-celery.service]                         │
│  celery worker（任务执行器，默认 7 个子进程）                   │
│  作用：消费队列任务：发飞书/企微/钉钉、算工资、跑预警、导出       │
└─────────────────────────────────────────────────────────────┘
```

**核心关系**：
- API 收到请求 → 写库 → 通过 `enqueue_after_commit` 把推送任务投到 Redis 队列
- Beat 定时把「定时任务」投到队列
- Worker 从队列取任务执行（推送/计算/导出）

**只要 Worker 或 Beat 有一个不在，对应功能就停**。例如 Beat 假死 → 所有定时推送（AI预警/日报/逾期提醒）停摆，但 API 和报工类即时推送（依赖 Worker）不受影响。

## 二、服务管理（SSH 命令）

### 2.1 查看状态

```bash
systemctl status lightmes-beat lightmes-celery
# 应显示 Active: active (running)，且 Restart 计数（NRestarts）为 0 或很小
```

### 2.2 重启

```bash
# 重启调度器（改定时任务/调度代码后必做）
systemctl restart lightmes-beat

# 重启执行器（改推送/任务代码后必做）
systemctl restart lightmes-celery

# 两个一起（通常改代码后两个都要重启）
systemctl restart lightmes-beat lightmes-celery
```

### 2.3 开机自启

```bash
systemctl is-enabled lightmes-beat lightmes-celery   # 都应为 enabled
systemctl enable lightmes-beat lightmes-celery        # 若未启用则开启
```

### 2.4 API（8000）重启

在宝塔面板操作：**网站 → Python 项目 → LightMes → 重启**。
（LightMes 的 API 由宝塔 Python 项目管理器托管，不是 systemd 服务。）

## 三、日志查看

```bash
# 调度器日志（看是否正常发任务：应看到 "Sending due task xxx"）
journalctl -u lightmes-beat -n 50

# 执行器日志（看任务执行结果：received / succeeded / ERROR）
journalctl -u lightmes-celery -n 50

# 按时间过滤
journalctl -u lightmes-celery --since "10 minutes ago"

# 只看错误
journalctl -u lightmes-celery --since "1 hour ago" | grep -iE "error|failed|traceback"

# 宝塔自启脚本日志（如走 start-celery.sh 拉起的进程）
tail -50 /tmp/lightmes-celery/boot.log
```

## 四、日常健康检查

```bash
# 1. 三个进程是否都在
ps aux | grep -E "uvicorn app.main|app.celery_app (worker|beat)" | grep -v grep

# 2. Redis 队列积压（正常应 < 10，长时间 > 0 说明 worker 没消费）
redis-cli -n 2 llen celery

# 3. 调度器最近是否在发任务（应看到 Sending due task）
journalctl -u lightmes-beat --since "10 minutes ago" | grep "Sending due"

# 4. Worker 心跳
cd /www/wwwroot/lightmes/backend
/www/server/pyporject_evn/lightmes/bin/celery -A app.celery_app inspect ping
```

## 五、定时任务管理

### 5.1 任务存在哪

- **任务定义**（代码）：`backend/app/celery_app.py` 的 `DEFAULT_CRON_JOBS` 列表
- **运行配置**（数据库）：`cron_jobs` 表（15+ 条），Beat 用 `DatabaseScheduler` 读取
- **自动播种**：uvicorn 启动时执行 `seed_default_cron_jobs`（幂等）——**表里缺的任务会自动补上**，所以新装环境不会丢任务

### 5.2 查看/启停定时任务

管理后台：`/admin/cron-jobs`（需要 `setting.manage` 权限）。
修改后会自动发 Redis reload 信号，Beat 热加载，无需重启。

### 5.3 新增一个定时任务的标准流程

1. 在 `app/tasks/` 里写任务函数（`@shared_task` 装饰）
2. 在 `celery_app.py` 的 `DEFAULT_CRON_JOBS` 里加定义（这样新环境自动播种）
3. 可选：同时加进 `conf.beat_schedule`（DB 为空时的回退调度）
4. 重启 `lightmes-beat lightmes-celery`（让调度器加载；若当前库没有该任务，重启 API 触发 seeder 或手动跑一次 seeder）

## 六、故障排查：飞书/企微/钉钉不提醒

按顺序排查（**本次「好几天没提醒」就是按此定位的**）：

```bash
# ① 服务是否活着（注意：进程活着 ≠ 调度正常！）
systemctl status lightmes-beat lightmes-celery

# ② 调度器是否真在发任务（关键！假死时进程活着但这里没有输出）
journalctl -u lightmes-beat --since "20 minutes ago" | grep "Sending due"
#    无输出 = 调度器假死 → 直接 systemctl restart lightmes-beat

# ③ 队列是否积压
redis-cli -n 2 llen celery

# ④ 推送日志状态（连 MySQL 执行）
#    SELECT status, COUNT(*) FROM feishu_push_logs GROUP BY status;
#    大量 pending 且很久不变 = 发送卡住/Worker 异常
#    最近没有新记录 = 业务事件没触发（查 ②）

# ⑤ Worker 执行日志是否有报错
journalctl -u lightmes-celery --since "10 minutes ago" | grep -iE "error|failed"
```

**经验**：
- 「好几天没提醒」且推送日志**没有新记录** → 99% 是 Beat 定时调度停了（AI预警/日报/逾期提醒全走定时任务）
- 推送日志有大量 `failed` → 通道配置/凭证问题（查飞书 AppID/Secret、群 webhook）
- 推送日志全是 `pending` → Worker 不消费（查 ③⑤）

### 手动触发一次任务做验证

```bash
cd /www/wwwroot/lightmes/backend
/www/server/pyporject_evn/lightmes/bin/celery -A app.celery_app call ai.alerts.scan
# 然后看是否产生站内通知/推送（查 notifications 表或 worker 日志）
```

## 七、代码改动后重启对照

| 改了哪里 | 重启什么 |
|---------|---------|
| `app/services/`、`app/tasks/`、`app/celery_app.py`（推送/定时逻辑） | `systemctl restart lightmes-beat lightmes-celery` |
| `app/api/`、`app/crud/`、`app/core/`（接口/业务/安全） | 宝塔面板重启 uvicorn（8000） |
| 只改前端 | 无需重启后端 |

## 八、双保活机制说明

LightMes 存在**两套保活**，当前行为已统一（都使用 DatabaseScheduler）：

| 机制 | 方式 | 说明 |
|------|------|------|
| systemd | `Restart=always` | 进程崩溃自动拉起 |
| 宝塔计划任务 | `lightmes_celery_watchdog.sh` 每 5 分钟 | 调用 `start-celery.sh`，脚本内幂等检查（进程在跑就跳过） |

⚠️ 注意：进程级保活**检测不到「进程活着但调度器假死」**（本次故障）。若需要功能级自愈，可另加调度健康检查（检查 Beat 最近调度时间戳，超时则 `systemctl restart lightmes-beat`）。

## 九、本次修复涉及的关键点（历史记录）

- 2026-08：修复 Beat 调度器假死导致的定时推送停摆（根因：Redis MISCONF 故障期间调度器卡死）
- `schedulers/database.py`：调度表替换必须用 `_maybe_entry()` 转 Entry，否则报 `'dict' object has no attribute 'is_due'`
- 新任务 `push.scan_pending`（推送 pending 补偿，每 5 分钟）、`salary.recalc_piece`（工资按最新工价重算，每月 1 号 03:30）已加入 `DEFAULT_CRON_JOBS`，新装环境自动播种
