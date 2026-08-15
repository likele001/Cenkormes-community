# -*- coding: utf-8 -*-
"""
LightMes 全量演示数据一键安装编排器
====================================
按依赖顺序依次执行全部演示种子脚本（每个脚本自身幂等，可重复执行）：

  1. demo_data              演示工厂 DEMO：租户/用户/产品/SKU/工序/工艺路线/工价/客户/订单/工单/任务/报工/审核/工资
  2. demo_data_flow         流程演示工厂 DEMO_FLOW：单订单全流程闭环
  3. seed_print_templates   打印模板（task_label 等）
  4. seed_sofa_materials    沙发原材料 + BOM（可选，需要明确 with_bom）
  5. seed_crm_dictionaries  CRM 字典（输单原因等）
  6. seed_demo_finance_data 财务演示数据（订单金额/成本/财务流水）
  7. seed_crm_demo        CRM 销售链路 + 商机→订单→生产计划→工单→任务→报工（完整）

统一入口：install_all(db) 供后台 API 调用；main() 供命令行调用。
卸载入口：uninstall_all(db) 供后台 API 调用（见 unseed_demo.py）。
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.tenant import Tenant


# 依赖顺序：基础数据 → 流程演示 → 模板/字典 → CRM
# 每个步骤 (名称, 可调用函数, 是否需要 DEMO 租户)
def _find_demo_tenant(db: Session) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.code == "DEMO").first()


def _run_demo_data(db: Session) -> dict:
    from scripts.demo_data import run as _run
    _run()
    return {}


def _run_demo_data_flow(db: Session) -> dict:
    from scripts.demo_data_flow import run as _run
    _run()
    return {}


def _run_print_templates(db: Session) -> dict:
    from scripts.seed_print_templates import seed_for_tenant
    tenant = _find_demo_tenant(db)
    if tenant:
        n = seed_for_tenant(db, tenant.id)
        db.commit()
        return {"created": n}
    return {"created": 0}


def _run_sofa_materials(db: Session) -> dict:
    from scripts.seed_sofa_materials import run as _run
    _run("DEMO", with_bom=False)
    return {}


def _run_crm_dictionaries(db: Session) -> dict:
    from scripts.seed_crm_dictionaries import run as _run
    tenant = _find_demo_tenant(db)
    if tenant:
        result = _run(db, tenant.id)
        db.commit()
        return result or {}
    return {}


def _run_finance_data(db: Session) -> dict:
    from scripts.seed_demo_finance_data import main as _main
    _main()
    return {}


def _run_crm_demo(db: Session) -> dict:
    from scripts.seed_crm_demo import run as _run
    tenant = _find_demo_tenant(db)
    if not tenant:
        raise RuntimeError("DEMO 租户不存在，请先执行 demo_data")
    return _run(tenant.id)


# 安装步骤（按依赖顺序）
INSTALL_STEPS = [
    ("基础演示数据 (DEMO 租户)", _run_demo_data),
    ("完整流程演示 (DEMO_FLOW 租户)", _run_demo_data_flow),
    ("打印模板", _run_print_templates),
    ("沙发原材料", _run_sofa_materials),
    ("CRM 字典", _run_crm_dictionaries),
    ("财务演示数据", _run_finance_data),
    ("CRM 销售链路 + 生产闭环", _run_crm_demo),
]


def install_all(db: Session | None = None) -> dict:
    """安装全部演示数据（幂等）。返回各步骤结果。"""
    own_session = db is None
    if own_session:
        db = SessionLocal()
    results = {}
    try:
        for name, fn in INSTALL_STEPS:
            try:
                r = fn(db)
                results[name] = {"ok": True, **r}
            except Exception as e:  # noqa: BLE001
                db.rollback()
                results[name] = {"ok": False, "error": str(e)}
        return results
    finally:
        if own_session:
            db.close()


def status(db: Session | None = None) -> dict:
    """检查演示数据安装状态。"""
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        demo = _find_demo_tenant(db)
        from app.models.customer import Customer
        from app.models.order import Order
        from app.models.crm import CrmLead
        if not demo:
            return {"installed": False, "tenant_id": None,
                    "demo_flow_tenant_id": None, "detail": "未创建演示租户"}
        cust = db.query(Customer).filter(Customer.tenant_id == demo.id).count()
        order = db.query(Order).filter(Order.tenant_id == demo.id).count()
        lead = db.query(CrmLead).filter(CrmLead.tenant_id == demo.id).count()
        flow = db.query(Tenant).filter(Tenant.code == "DEMO_FLOW").first()
        installed = cust > 0 or order > 0 or lead > 0
        return {
            "installed": installed,
            "tenant_id": demo.id,
            "demo_flow_tenant_id": flow.id if flow else None,
            "counts": {"customers": cust, "orders": order, "leads": lead},
            "detail": "演示数据已安装" if installed else "演示租户已存在，业务数据为空",
        }
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    import json

    results = install_all()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("\n" + json.dumps(status(), ensure_ascii=False, indent=2))
