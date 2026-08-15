# LightMes 完整安装部署指南

> **本文档为整合版**（结合项目检查、`docs/宝塔部署.md`、实际踩坑记录整理）。  
> **不覆盖**现有 `docs/宝塔部署.md`、`docs/部署说明.md`，可与它们对照使用。  
> 最后更新：2026-05-29

---

## 一、先搞懂：你要部署什么

LightMes = **1 个后端** + **2～3 个前端静态站**（宝塔/Nginx 托管）。

```text
                    ┌─────────────────────────────────────┐
                    │  MySQL 5.7+    Redis（可选，Celery） │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │  backend  FastAPI  :8000            │
                    │  /api/admin/*  /api/h5/*            │
                    │  /api/platform/*  /api/tenants/*    │
                    └─────────┬───────────┬─────────────┘
                              │ /api/ 反代  │
        ┌─────────────────────┼───────────┼─────────────────────┐
        │                     │           │                     │
   admin 站              h5 站        register 站（SaaS 才要）   │
 frontend-admin-pro    frontend-h5   frontend-portal          │
 厂长 + 平台运营         员工 + 客户      企业自助注册            │
```

### 部署模式怎么选

| | **路线 A：单厂** | **路线 B：SaaS** |
|---|------------------|------------------|
| 场景 | 一家厂自用 | 对外卖账号、多工厂 |
| `npm run build` 几个目录 | **2 个** | **3 个** |
| 平台 `/platform` | 可不使用 | **必须用** |
| 注册页 `/register` | 不部署 | 部署 portal |
| 新工厂开户 | 演示 `DEMO` 或平台手工建 | 手工建 **或** 自助注册 + 支付 |

> **生产环境只用 `npm run build`，不要用 `npm run dev` 上宝塔。**

---

## 二、速查：`npm run build` 跑哪些目录？

| # | 目录 | 路线 A | 路线 B | 产物 | 宝塔站点根目录 |
|---|------|:------:|:------:|------|----------------|
| — | `backend` | — | — | 无（Python） | 宝塔「Python 项目」 |
| 1 | `frontend-admin-pro` | ✅ | ✅ | `dist/` | **admin 域名** 站根 |
| 2 | `frontend-h5` | ✅ | ✅ | `dist/` | **h5 域名** 站根 |
| 3 | `frontend-portal` | ❌ | ✅ | `dist/` | **register 域名** 站根 |

### 一键构建脚本

**路线 A（2 个前端）：**

```bash
cd /www/wwwroot/lightmes/frontend-admin-pro && npm install && npm run build
cd /www/wwwroot/lightmes/frontend-h5 && npm install && npm run build
```

**路线 B（3 个前端）：**

```bash
cd /www/wwwroot/lightmes/frontend-admin-pro && npm install && npm run build
cd /www/wwwroot/lightmes/frontend-h5 && npm install && npm run build
cd /www/wwwroot/lightmes/frontend-portal && npm install && npm run build
```

### 示例：你的域名对照（可按此改）

| 宝塔站点 | 域名示例 | `dist` 来源 |
|----------|----------|-------------|
| 管理端 | `admin.lightmes.user.zuiger.cn` | `frontend-admin-pro/dist` |
| H5 | `lightmes.user.zuiger.cn` | `frontend-h5/dist` |
| 注册（SaaS） | `register.lightmes.user.zuiger.cn` | `frontend-portal/dist` |

---

## 三、环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Linux | Debian/Ubuntu/CentOS | 开发与宝塔部署 |
| Python | 3.10+ | 后端 |
| Node.js | 18+ | 前端构建 |
| MySQL | 5.7+ | **禁用 MySQL 8 专属语法** |
| Redis | 6+ | Celery 可选；不配也能跑核心业务 |
| Nginx | 任意 | 宝塔自带 |

检查命令：

```bash
python3 --version
node -v && npm -v
mysql --version
redis-server --version   # 可选
```

---

## 四、后端安装（必做）

### 4.1 创建数据库

```sql
CREATE DATABASE lightmes DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lightmes'@'127.0.0.1' IDENTIFIED BY '你的密码';
GRANT ALL ON lightmes.* TO 'lightmes'@'127.0.0.1';
FLUSH PRIVILEGES;
```

### 4.2 配置 `.env`

```bash
cd /www/wwwroot/lightmes/backend
cp .env.example .env
```

必改项：

```ini
DB_URL=mysql+pymysql://lightmes:你的密码@127.0.0.1:3306/lightmes?charset=utf8mb4
JWT_SECRET=请换成足够长的随机字符串
STORAGE_LOCAL_ROOT=./data/storage

# SaaS 支付回调跳转（路线 B 可选）
PUBLIC_BASE_URL=https://admin.你的域名
```

### 4.3 安装依赖与迁移

> **`bash: alembic: command not found`**：系统 PATH 无 alembic，必须用宝塔 Python 虚拟环境的**全路径**。在宝塔 → Python 项目 → 查看「环境路径」，使用其下 `bin/alembic`。

**本机示例（kele2，请按实际环境修改）：**

```bash
cd /www/wwwroot/lightmes/backend

# 安装依赖
/www/server/pyporject_evn/hightmes/bin/pip install -r requirements.txt

# 迁移到最新（含 code_sequences 等业务编号表）
/www/server/pyporject_evn/hightmes/bin/alembic upgrade head

# 查看当前版本（可选）
/www/server/pyporject_evn/hightmes/bin/alembic current
```

本地开发若用项目 `.venv`，则改为：

```bash
cd /www/wwwroot/lightmes/backend
.venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
```

**若报 `Table already exists` / 列已存在**（库曾用 `DB_AUTO_CREATE` 建过表）：

```bash
cd /www/wwwroot/lightmes/backend
/www/server/pyporject_evn/hightmes/bin/alembic current
# 确认 SaaS 相关表、code_sequences 等已存在后，标记到最新 revision：
/www/server/pyporject_evn/hightmes/bin/alembic stamp 0027_code_sequences
```

更完整的宝塔说明见 [`docs/宝塔部署.md`](宝塔部署.md) **二、2.2**。

### 4.4 宝塔添加 Python 项目

| 字段 | 值 |
|------|-----|
| 项目路径 | `/www/wwwroot/lightmes/backend` |
| 启动命令 | `uvicorn app.main:app --host 127.0.0.1 --port 8000` |
| 环境变量 | 从文件加载 → `backend/.env` |
| 启动用户 | `www` |
| 依赖 | `requirements.txt`（**含 httpx**，SaaS/支付需要） |

验证：

```bash
curl http://127.0.0.1:8000/api/health
# {"code":200,"msg":"","data":{"status":"ok"}}

curl -s -X POST http://127.0.0.1:8000/api/platform/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"platform","password":"platform123"}'
# 应返回 code:200；若 404 说明后端未重启或仍是旧代码
```

> **重要**：每次拉取/更新后端代码后，必须在宝塔里 **重启 Python 项目**，否则新接口（如 `/api/platform/*`）会 404。

### 4.5 SaaS：创建平台运营账号（路线 B 或需手工建厂时）

```bash
cd /www/wwwroot/lightmes/backend
PYTHONPATH=. python3 scripts/init_platform_admin.py platform 你的密码
```

- 默认用户名：`platform`
- 若脚本提示「已存在」，说明账号已创建过；忘记密码见 [第十章](#十常见问题排错)。
- **首次默认密码**（未自定义时）：`platform123`

### 4.6 演示数据（可选）

```bash
cd /www/wwwroot/lightmes/backend
PYTHONPATH=. python3 scripts/demo_data.py
```

---

## 五、前端构建与宝塔静态站

### 5.1 管理端 `frontend-admin-pro`

```bash
cd /www/wwwroot/lightmes/frontend-admin-pro
npm install
npm run build
```

- 产物：`frontend-admin-pro/dist`
- 内含：工厂管理后台 + **平台运营** `/platform/*`

### 5.2 H5 `frontend-h5`

```bash
cd /www/wwwroot/lightmes/frontend-h5
npm install
npm run build
```

- 产物：`frontend-h5/dist`
- 路由为 **Hash 模式**，地址里带 `#`

### 5.3 注册门户 `frontend-portal`（仅路线 B）

```bash
cd /www/wwwroot/lightmes/frontend-portal
npm install
npm run build
```

- 产物：`frontend-portal/dist`
- 若挂在 admin 同域 `/register/` 下，需：`VITE_BASE=/register/ npm run build`

---

## 六、Nginx / 宝塔：伪静态 + API 反代（每个静态站都要配）

### 6.1 伪静态（SPA）

网站 → 设置 → **伪静态**：

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 6.2 API 反代（必做）

网站 → 设置 → **配置文件**，在 `server { }` 内加入：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

> admin、h5、register **三个站**若都需要调接口，**每个站都要配** `/api/` 反代（或统一走独立 `api.域名`）。

### 6.3 HTTPS

宝塔 → SSL → Let's Encrypt → 开启强制 HTTPS。

### 6.4 portal 挂 admin 同域（可选，不新增域名）

1. `VITE_BASE=/register/ npm run build`
2. 在 admin 站 Nginx 中、`location /` 之前增加：

```nginx
location ^~ /register/ {
    alias /www/wwwroot/lightmes/frontend-portal/dist/;
    try_files $uri $uri/ /register/index.html;
}
location ^~ /register/assets/ {
    alias /www/wwwroot/lightmes/frontend-portal/dist/assets/;
}
```

---

## 七、所有人入口 URL（别混）

> 管理端为 **History 路由**；H5 为 **Hash 路由**（必须有 `#`）。  
> **没有** `/t/xxx/admin`、`/t/xxx/h5` 这种路径，以本节为准。

### 7.1 四种角色

| 角色 | 干什么 | 正确 URL（示例） |
|------|--------|------------------|
| **运营商（你）** | 管所有租户、套餐、开关售卖 | `https://admin域名/platform/login` |
| **租户管理员（厂长）** | 管本厂生产、订单、员工 | `https://admin域名/login`（租户编码 `DEMO`）或 `/t/DEMO/login` |
| **员工** | 报工、任务、工资 | `https://h5域名/#/t/DEMO/login` |
| **客户** | 下单、对账 | `https://h5域名/#/t/DEMO/customer/order`（登录后） |
| **新企业注册** | 自助开户（路线 B） | `https://register域名/register/` |

### 7.2 平台后台常用路径

| 功能 | URL |
|------|-----|
| 平台登录 | `/platform/login` |
| 租户管理 | `/platform/tenants` |
| 套餐管理 | `/platform/packages` |
| 订阅订单 | `/platform/subscription-orders` |
| 系统设置（售卖开关、虎皮椒） | `/platform/settings` |

### 7.3 租户业务路径

| 功能 | 管理端 | H5 |
|------|--------|-----|
| 登录 | `/t/{code}/login` | `#/t/{code}/login` |
| 生产订单（含客户单审核） | `/t/{code}/production/orders` | — |
| 客户下单 | — | `#/t/{code}/customer/order` |
| 员工邀请加入 | `/t/{code}/join?invite=token` | `#/t/{code}/join?invite=token` |

### 7.4 演示账号（`demo_data.py` 后，租户 `DEMO`）

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 班组长 | zhang | 123456 |
| 员工 | li | 123456 |
| 质检 | wang | 123456 |
| 客户 | customer1 | 123456 |

---

## 八、路线 A：单厂私有化（最短路径）

1. 完成 [第四节](#四后端安装必做) 后端 + `alembic upgrade head`
2. `npm run build`：**admin-pro**、**h5**（2 个目录）
3. 宝塔两个静态站 + [第六节](#六-nginx--宝塔伪静态--api-反代每个静态站都要配) 伪静态与反代
4. （可选）`demo_data.py`，用 `DEMO` / `admin` / `admin123` 登录
5. **不要**部署 portal、不必开「售卖租户」

---

## 九、路线 B：SaaS 商业化（在 A 基础上增加）

### 9.1 比路线 A 多做的事

| 步骤 | 说明 |
|------|------|
| build portal | 第 3 个前端 |
| `init_platform_admin.py` | **必须** |
| 部署 register 站 | 伪静态 + `/api/` 反代 |
| 平台「开启售卖租户」 | 才显示自助注册 |
| 虎皮椒（可选） | 在线支付套餐 |

### 9.2 开启自助注册

1. 登录 `https://admin域名/platform/login`
2. **系统设置** → 打开 **「开启售卖租户（SaaS 收费模式）」** → 保存  
3. 或数据库：`UPDATE platform_settings SET value='true' WHERE \`key\`='saas_mode_enabled';`

未开启时，注册页显示：**「暂未开放自助注册，请联系服务商开通租户。」**

关闭售卖时，只能在 **平台 → 租户管理 → 新建租户** 开户。

### 9.3 虎皮椒支付（可选）

1. 平台 → 系统设置：AppId、AppSecret  
2. `.env`：`PUBLIC_BASE_URL=https://admin.你的域名`  
3. 虎皮椒商户后台异步通知：

```text
https://admin.你的域名/api/payment/xunhu/notify
```

（必须 HTTPS）

### 9.4 客户下单（租户内业务）

1. 管理端 **CRM → 客户**：建档案并绑定用户（角色 `customer`）
2. 客户 H5 登录 → `#/t/{code}/customer/order` 提交
3. 订单状态 **待审核**；管理员 **生产 → 订单** 确认或驳回

---

## 十、常见问题排错

### 10.1 `/api/platform/auth/login` 返回 404

| 原因 | 处理 |
|------|------|
| 后端未重启，仍是旧代码 | 宝塔重启 Python 项目 |
| 缺少 `httpx` 导致新路由未加载 | `pip install -r requirements.txt` 后重启 |
| 静态站未配 `/api/` 反代 | 按 [6.2](#62-api-反代必做) 配置 |

验证：`curl http://127.0.0.1:8000/api/platform/public-config` 应返回 JSON。

### 10.2 H5 白屏 + `Maximum call stack size exceeded`

| 原因 | 处理 |
|------|------|
| 路由重复（`/` 与 `/t/:tenantCode` 共用子路由） | 使用最新代码并 **重新 build h5** |
| 未部署新 `dist` | 覆盖 `frontend-h5/dist`，Ctrl+F5 |

### 10.3 H5 白屏，URL 出现 `customer/customer/order`

| 原因 | 处理 |
|------|------|
| 错误 URL，无对应路由 | 应访问 `#/t/DEMO/customer/order`（只有一个 `customer`） |
| 底部 Tab 相对路径拼接错误 | 已修复：请部署最新 h5 build |

### 10.4 注册页「暂未开放自助注册」

平台 → 系统设置 → 开启「售卖租户」，或执行 SQL 见 [9.2](#92-开启自助注册)。

### 10.5 平台账号 `platform` 密码

- 默认：`platform123`（`init_platform_admin.py` 未改密码时）
- 重置：

```bash
cd /www/wwwroot/lightmes/backend
PYTHONPATH=. python3 -c "
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.crud.platform_user import get_platform_user_by_username
db = SessionLocal()
u = get_platform_user_by_username(db, 'platform')
u.password_hash = hash_password('你的新密码')
db.commit()
print('ok')
db.close()
"
```

### 10.6 前端页面空白、无报错

1. F12 → Network：看 `index-*.js` 是否 200  
2. 是否部署了最新 build（文件名 hash 会变）  
3. 是否配置了伪静态 `try_files`  
4. portal 若挂子目录，是否用了 `VITE_BASE=/register/` 构建

### 10.7 `alembic upgrade` 失败

| 现象 | 处理 |
|------|------|
| `bash: alembic: command not found` | 不要用裸命令 `alembic`，用虚拟环境全路径，见 [4.3](#43-安装依赖与迁移) |
| `Table already exists` | 勿重复 `upgrade`，用 `alembic stamp 0027_code_sequences`（见 4.3） |
| `Duplicate column` | 列已加过，执行 `alembic stamp` 到当前最新 revision |

### 10.8 Redis / Celery

工资异步导出、CRM 公海池回收、生产自动化 pipeline、AI 定时任务依赖 Redis + Celery。未装 Redis 时核心业务仍可用。

**方法一（推荐）：systemd 系统服务（开机自启）**

部署脚本会将 Celery 注册为 systemd 服务，随服务器自动启动，换服务器后也要重新执行：

```bash
bash /www/wwwroot/lightmes/scripts/deploy-celery.sh
```

**方法二：后台脚本（临时使用）**

```bash
bash /www/wwwroot/lightmes/scripts/start-celery.sh   # 启动 worker + beat
bash /www/wwwroot/lightmes/scripts/stop-celery.sh    # 停止
```

日志默认：`/tmp/lightmes-celery/`。详见 [宝塔部署.md](./宝塔部署.md) 第八节。

> ⚠️ **换服务器后务必重新部署 Celery 服务**（方法一），否则定时任务和消息推送不工作。
> 服务文件已纳入项目：`scripts/systemd/` 目录下，可直接参考。

### 10.9 设备保养功能（0043 迁移）

更新至 2026-05-29 后需执行 `alembic upgrade head`（含 `0043_equipment_maintenance`），并 rebuild admin-pro。  
操作说明见 **[设备管理操作指南.md](./设备管理操作指南.md)**。

---

## 十一、更新发布 checklist（改代码后）

```text
□ backend: pip install -r requirements.txt（有新依赖时）
□ backend: `.../bin/alembic upgrade head`（有新迁移时，全路径见 4.3）
□ backend: 宝塔【重启】Python 项目
□ frontend-admin-pro: npm run build → 覆盖 admin 站 dist
□ frontend-h5: npm run build → 覆盖 h5 站 dist
□ frontend-portal: npm run build → 覆盖 register 站 dist（若有）
□ 浏览器 Ctrl+F5 强刷
□ curl /api/health 与 /api/platform/public-config 抽查
```

---

## 十二、相关文档索引

| 文档 | 说明 |
|------|------|
| [宝塔部署.md](./宝塔部署.md) | 宝塔分步操作、路线 A/B 章节 |
| [部署说明.md](./部署说明.md) | 通用 Linux/Windows，无宝塔细节 |
| [../README.md](../README.md) | 项目概览与功能清单 |
| [../packs/cursor1_.md](../packs/cursor1_.md) | 历史对话导出、项目检查记录 |
| [../LightMes系统完整使用指南.md](../LightMes系统完整使用指南.md) | 业务操作说明（含第十一阶段设备与保养） |
| [设备管理操作指南.md](./设备管理操作指南.md) | 设备档案、点检、保养计划与记录、API 速查 |

---

## 十三、三种「人」一张图（防混）

```text
                    ┌─────────────────────────┐
                    │  运营商 platform 账号    │
                    │  admin站 /platform/*   │
                    │  建厂、套餐、开售卖     │
                    └───────────┬─────────────┘
                                │ 创建租户
                    ┌───────────▼─────────────┐
                    │  租户管理员 admin 账号   │
                    │  admin站 /t/厂编码/login │
                    │  生产、订单、员工、CRM    │
                    └───────────┬─────────────┘
                                │ 创建员工/客户账号
              ┌─────────────────┴─────────────────┐
              │                                   │
    ┌─────────▼─────────┐             ┌───────────▼──────────┐
    │  员工 li 等        │             │  客户 customer1 等    │
    │  h5 #/t/厂编码/…   │             │  h5 #/t/厂编码/       │
    │  报工、任务、工资   │             │  customer/order 下单  │
    └───────────────────┘             └──────────────────────┘

    新企业老板（路线B）→ register站 /register/ → 自动建新租户+管理员
```

---

**记住三句话：**

1. **后端不用 npm**，改完要 **重启** Python 项目。  
2. **单厂 build 2 个、SaaS build 3 个** 前端目录。  
3. **平台在 admin 的 `/platform`，员工客户在 h5 的 `#/t/编码/…`，不要混域名含义。**
