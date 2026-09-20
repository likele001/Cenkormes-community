# CenkorMES 社区版（开源）

CenkorMES 云端 SaaS 的开源社区档：面向中小型加工厂的轻量化生产管理，**扫码报工 + 派工 + 两级审核**。

> 品牌说明：社区版与云端 SaaS 版同属 CenkorMES 产品线。仓库名 `Cenkormes-community` 为历史命名，保留不变。

## 模块

- `backend/` — API 服务
- `frontend-admin-pro/` — PC 管理端
- `frontend-h5/` — 员工扫码报工

## 快速启动

```bash
cd backend && cp env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000

cd ../frontend-admin-pro && npm install && npm run dev
```

## 商业版

完整算薪、CRM、财务等能力请使用 CenkorMES 商业源码版（私有仓库 `lightmes-pro`），在社区版目录执行：

```bash
bash /path/to/lightmes-pro/scripts/install.sh "$(pwd)"
```
