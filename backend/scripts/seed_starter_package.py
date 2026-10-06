# -*- coding: utf-8 -*-
"""
预置「试用基础版」(starter / saas 交付) 套餐
============================================
试用基础版仅开放生产闭环（订单/工单/派工）+ 扫码报工 + 自动计件工资 + 客户自助下单；
AI 智能化、多 IM 推送（飞书/企微/钉钉）、财务/仓库/设备/MRP 等高级能力按套餐隐藏（PackageGate + 前端菜单联动）。

幂等：已存在则确保 tier/delivery_mode 正确，否则创建。可重复执行。

运行：cd backend && PYTHONPATH=. python3 scripts/seed_starter_package.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.crud.saas_package import create_package, get_package_by_code
from app.models.saas_package import PACKAGE_DELIVERY_SAAS, PACKAGE_TIER_STARTER

STARTER_CODE = "starter-trial"
STARTER_NAME = "试用基础版"
STARTER_FEATURES = '{"modules":["production","report","salary","customer"]}'
STARTER_DESC = (
    "试用基础版：仅开放生产闭环(订单/工单/派工)+扫码报工+自动计件工资+客户自助下单；"
    "AI、多IM推送及财务/仓库/设备/MRP等高级能力按套餐隐藏。"
)


def ensure_starter_package(db: Session) -> dict:
    pkg = get_package_by_code(db, STARTER_CODE)
    if pkg is None:
        create_package(
            db, STARTER_CODE, STARTER_NAME, Decimal("0.00"), 30, 25,
            STARTER_FEATURES, STARTER_DESC, 1,
            tier=PACKAGE_TIER_STARTER, delivery_mode=PACKAGE_DELIVERY_SAAS,
        )
        return {"created": 1, "code": STARTER_CODE}
    updated = 0
    if pkg.tier != PACKAGE_TIER_STARTER:
        pkg.tier = PACKAGE_TIER_STARTER
        updated += 1
    if pkg.delivery_mode != PACKAGE_DELIVERY_SAAS:
        pkg.delivery_mode = PACKAGE_DELIVERY_SAAS
        updated += 1
    return {"created": 0, "code": STARTER_CODE, "updated_fields": updated}


def main() -> None:
    db = SessionLocal()
    try:
        r = ensure_starter_package(db)
        db.commit()
        print(f"[STARTER] 完成：{STARTER_CODE} 套餐就绪 {r}")
    except Exception as e:
        db.rollback()
        print(f"[STARTER] 失败: {e}")


if __name__ == "__main__":
    main()
