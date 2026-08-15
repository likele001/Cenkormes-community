# LightMes Docker 部署指南

> **定位**：本地开发（dev）与演示/测试（staging）的可选方案。  
> **生产环境**仍推荐 [宝塔部署.md](./宝塔部署.md) 裸机部署；Docker 与宝塔可并存（端口错开）。

---

## 前置条件

| 组件 | 版本 |
|------|------|
| Docker | 20.10+ |
| Docker Compose | v2+ |
| Node.js（dev 本机跑前端时） | 18+ |

---

## 1. 初始化配置

```bash
cd /www/wwwroot/lightmes
cp .env.docker.example .env.docker   # 可选，自定义 JWT 等
```

默认直接使用仓库内 [`.env.docker.example`](../.env.docker.example)；若创建了 `.env.docker`，启动时加 `--env-file .env.docker`。

**默认宿主机端口（901x，避开 8000/8080）：**

| 变量 | 默认 | 用途 |
|------|------|------|
| `DOCKER_API_PORT` | 9018 | API |
| `STAGING_PORT_ADMIN` | 9010 | staging 管理端 |
| `STAGING_PORT_H5` | 9011 | staging H5 |
| `STAGING_PORT_REGISTER` | 9012 | staging 注册页 |

---

## 2. dev profile — 本地开发

一键启动 MySQL、Redis、API（热重载）、Celery worker/beat：

```bash
docker compose --profile dev \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up -d --build
```

| 服务 | 宿主机端口 |
|------|-----------|
| API | http://localhost:9018（默认 `DOCKER_API_PORT`，避开宝塔 8000/8080） |
| MySQL | 3307 |
| Redis | 6380 |

验证：

```bash
curl -s http://localhost:9018/api/health
```

### 首次导入演示数据

```bash
docker compose --profile dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  exec api init-demo.sh
```

- 演示工厂：`DEMO` / `admin` / `admin123`
- 平台管理员：`platform` / `platform123`（可在 `.env.docker` 用 `PLATFORM_USER` / `PLATFORM_PASS` 覆盖）

### 本机跑前端（推荐）

API 已在容器内运行，三端 Vite dev 代理到 `localhost:8000`：

```bash
cd frontend-admin-pro && npm install && npm run dev   # http://localhost:5173，vite 代理改指向 localhost:9018
cd frontend-h5 && npm install && npm run dev         # http://localhost:5174
cd frontend-portal && npm install && npm run dev     # http://localhost:5175
```

### 停止

```bash
docker compose --profile dev \
  -f docker-compose.yml -f docker-compose.dev.yml down
```

---

## 3. staging profile — 演示/测试（含三端静态页）

构建 admin + H5 + portal 并经由 Nginx 提供访问：

```bash
docker compose --profile staging \
  -f docker-compose.yml \
  -f docker-compose.staging.yml \
  up -d --build
```

| 端 | URL |
|----|-----|
| 管理端 | http://localhost:9010/t/DEMO/login |
| H5 | http://localhost:9011 |
| 注册 portal | http://localhost:9012/register |
| API（直连） | http://localhost:9018/api/health |

首次同样执行 `init-demo.sh`（见上，将 `dev` 改为 `staging` profile）。

### 模拟线上多域名（可选）

编辑 `/etc/hosts`：

```
127.0.0.1 admin.lightmes.local
127.0.0.1 lightmes.local
127.0.0.1 register.lightmes.local
```

并在 `.env.docker` 中设置对应的 `PUBLIC_BASE_URL` / `H5_PUBLIC_BASE_URL`，配合宿主机 Nginx 反代 9010–9012（飞书/企微 OAuth 联调时使用）。

端口均可通过 `.env.docker` 覆盖：`DOCKER_API_PORT`、`STAGING_PORT_ADMIN`、`STAGING_PORT_H5`、`STAGING_PORT_REGISTER`。

---

## 4. 与宝塔生产并存

| 项 | Docker | 宝塔 |
|----|--------|------|
| MySQL | 3307 | 3306 |
| Redis | 6380 | 6379 |
| API | 9018（Docker，可改）/ 127.0.0.1:8000（宝塔生产） |

同一台机器可同时运行；**不要**让 Docker 与宝塔共用同一数据库目录。

---

## 5. 常见问题

### 点菜单没反应 / Failed to fetch dynamically imported module

部署后旧浏览器 tab 引用已删除的 JS chunk。刷新页面或依赖前端内置的 chunk 自动刷新；staging Nginx 已对 `/assets/` 配置 404 不回退 HTML。

### Celery 任务不执行

```bash
docker compose --profile dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  ps
# 确认 celery-worker、celery-beat 为 running
```

### 数据库迁移失败

```bash
docker compose --profile dev \
  -f docker-compose.yml -f docker-compose.dev.yml \
  exec api alembic upgrade head
```

### 清空 Docker 数据重来

```bash
docker compose --profile dev \
  -f docker-compose.yml -f docker-compose.dev.yml down -v
```

---

## 6. 文件说明

| 文件 | 说明 |
|------|------|
| [docker-compose.yml](../docker-compose.yml) | 基础服务定义 |
| [docker-compose.dev.yml](../docker-compose.dev.yml) | dev 热重载覆盖 |
| [docker-compose.staging.yml](../docker-compose.staging.yml) | staging Nginx 覆盖 |
| [backend/Dockerfile](../backend/Dockerfile) | API/Celery 镜像 |
| [docker/nginx/Dockerfile.staging](../docker/nginx/Dockerfile.staging) | 三前端 + Nginx |
| [docker/scripts/init-demo.sh](../docker/scripts/init-demo.sh) | 演示数据初始化 |

---

*关联：[宝塔部署.md](./宝塔部署.md) · [部署说明.md](./部署说明.md)*
