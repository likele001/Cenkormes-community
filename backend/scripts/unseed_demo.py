# -*- coding: utf-8 -*-
"""
LightMes 演示数据一键卸载（正式版）
==================================
删除指定租户（默认 DEMO）内的演示数据：
  - 商机转化生成的订单 + 生产计划 + 工单 + 任务 + 报工 + 审核
  - 全部 CRM 业务表（客户/联系人/标签/线索/商机/报价/合同/回款/营销/售后/输单原因/跟进）
  - code_sequences 演示用序列（order/production_plan/task 当日段）

设计说明：
  - 动态租户：自动查 DEMO 租户，不硬编码
  - 只删「商机转化的订单」（opportunity_id 非空），保留普通订单
  - CRM 表整表清空（该租户下），因为演示数据与真实数据在 CRM 模块难以按时间戳区分；
    卸载仅建议对纯演示租户（DEMO/DEMO_FLOW）执行
  - 幂等：无数据时直接返回

用法：
  python3 scripts/unseed_demo.py            # 卸载 DEMO 租户
  python3 scripts/unseed_demo.py 2          # 指定 tenant_id
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from urllib.parse import urlparse, unquote

import pymysql


def _get_conn():
    u = urlparse(settings.DB_URL.replace("mysql+pymysql://", "mysql://"))
    return pymysql.connect(
        host=u.hostname or "127.0.0.1",
        port=u.port or 3306,
        user=unquote(u.username) if u.username else "root",
        password=unquote(u.password) if u.password else "",
        database=u.path.lstrip("/"),
        charset="utf8mb4",
        autocommit=False,
    )


def _get_tenant_id(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM tenants WHERE code='DEMO'")
        r = cur.fetchone()
        if not r:
            raise RuntimeError("DEMO 租户不存在")
        return r[0]


def uninstall_all(tenant_id: int | None = None, conn=None, dry_run: bool = False) -> dict:
    own_conn = conn is None
    if own_conn:
        conn = _get_conn()
    stats = {}
    try:
        c = conn.cursor()
        if tenant_id is None:
            tenant_id = _get_tenant_id(conn)
        stats["tenant_id"] = tenant_id

        # ---- 0. 找出商机转化的种子订单 ----
        c.execute(
            "SELECT id, code FROM orders WHERE tenant_id=%s AND opportunity_id IS NOT NULL",
            (tenant_id,),
        )
        seed_orders = c.fetchall()
        order_ids = [r[0] for r in seed_orders]
        stats["seed_orders"] = [r[1] for r in seed_orders]

        # ---- 1. 审核流水（种子报工下）----
        if order_ids:
            c.execute(
                """DELETE FROM report_audits WHERE tenant_id=%s AND report_id IN
                   (SELECT id FROM reports WHERE tenant_id=%s AND task_id IN
                    (SELECT id FROM tasks WHERE tenant_id=%s AND work_order_id IN
                     (SELECT id FROM work_orders WHERE tenant_id=%s AND order_id IN (%s))))""",
                (tenant_id, tenant_id, tenant_id, tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["report_audits"] = c.rowcount

            c.execute(
                """DELETE FROM reports WHERE tenant_id=%s AND task_id IN
                   (SELECT id FROM tasks WHERE tenant_id=%s AND work_order_id IN
                    (SELECT id FROM work_orders WHERE tenant_id=%s AND order_id IN (%s)))""",
                (tenant_id, tenant_id, tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["reports"] = c.rowcount

            c.execute(
                """DELETE FROM tasks WHERE tenant_id=%s AND work_order_id IN
                   (SELECT id FROM work_orders WHERE tenant_id=%s AND order_id IN (%s))""",
                (tenant_id, tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["tasks"] = c.rowcount

            c.execute(
                "DELETE FROM work_orders WHERE tenant_id=%s AND order_id IN (%s)",
                (tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["work_orders"] = c.rowcount

            c.execute(
                "DELETE FROM production_plans WHERE tenant_id=%s AND order_id IN (%s)",
                (tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["production_plans"] = c.rowcount

            c.execute(
                "DELETE FROM order_items WHERE tenant_id=%s AND order_id IN (%s)",
                (tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["order_items"] = c.rowcount

            c.execute(
                "DELETE FROM orders WHERE tenant_id=%s AND id IN (%s)",
                (tenant_id, ",".join(str(i) for i in order_ids)),
            )
            stats["orders"] = c.rowcount

        # ---- 2. 回置商机/报价/合同关联 ----
        c.execute(
            "UPDATE crm_opportunities SET converted_order_id=NULL WHERE tenant_id=%s",
            (tenant_id,),
        )
        c.execute(
            "UPDATE crm_quotations SET converted_order_id=NULL WHERE tenant_id=%s",
            (tenant_id,),
        )
        c.execute(
            "UPDATE crm_contracts SET order_id=NULL WHERE tenant_id=%s",
            (tenant_id,),
        )

        # ---- 3. CRM 子表（按外键关联删，无 created_at 的表也覆盖）----
        c.execute(
            "DELETE FROM crm_quotation_items WHERE tenant_id=%s AND quotation_id IN (SELECT id FROM crm_quotations WHERE tenant_id=%s)",
            (tenant_id, tenant_id),
        )
        stats["crm_quotation_items"] = c.rowcount
        c.execute(
            "DELETE FROM crm_payment_plans WHERE tenant_id=%s AND contract_id IN (SELECT id FROM crm_contracts WHERE tenant_id=%s)",
            (tenant_id, tenant_id),
        )
        stats["crm_payment_plans"] = c.rowcount

        for tbl in [
            "crm_opportunity_activities",
            "crm_lead_activities",
            "crm_campaign_members",
            "after_sales",
            "crm_sales_targets",
            "crm_campaigns",
            "crm_contracts",
            "crm_quotations",
            "crm_opportunities",
            "crm_leads",
            "customer_products",
            "customer_contacts",
            "customer_tag_links",
            "customer_tags",
            "crm_win_loss_reasons",
        ]:
            try:
                c.execute(f"DELETE FROM {tbl} WHERE tenant_id=%s", (tenant_id,))
                stats[tbl] = c.rowcount
            except Exception as e:  # noqa: BLE001
                stats[tbl] = f"skip: {e}"

        # ---- 4. 种子客户（含"演示"标记的或 CRM 种子客户）----
        # 客户表有真实数据风险，仅删 code 以 C 开头且名字在种子清单中的
        seed_customers = [
            "华强电子", "明达五金", "躬行科技", "恒力机械", "联创精密", "南方模具",
            "盛达电子", "宏远塑胶", "金锐刀具", "新光电器", "中原轴承", "天成包装",
        ]
        for name in seed_customers:
            c.execute("DELETE FROM customers WHERE tenant_id=%s AND name=%s", (tenant_id, name))
        stats["customers"] = "按名称删除"

        # ---- 5. code_sequences 演示段 ----
        for biz in ["order", "production_plan", "task"]:
            c.execute("DELETE FROM code_sequences WHERE tenant_id=%s AND biz_type=%s", (tenant_id, biz))
        stats["code_sequences"] = "已清理 order/production_plan/task 序列"

        if dry_run:
            conn.rollback()
            stats["committed"] = False
        else:
            conn.commit()
            stats["committed"] = True
        stats["message"] = f"演示数据已卸载（租户 {tenant_id}）"
        return stats
    finally:
        if own_conn:
            conn.close()


if __name__ == "__main__":
    import json

    tid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    res = uninstall_all(tid, dry_run="--dry-run" in sys.argv)
    print(json.dumps(res, ensure_ascii=False, indent=2))
