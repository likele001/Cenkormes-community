# LightMes Community

面向中小型加工厂的轻量化生产管理：**扫码报工 + 派工 + 两级审核**。

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

完整算薪、CRM、财务等能力请使用 LightMes Pro，在社区版目录执行：

```bash
bash /path/to/lightmes-pro/scripts/install.sh "$(pwd)"
```
