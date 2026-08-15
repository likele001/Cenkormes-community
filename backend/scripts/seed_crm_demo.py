# -*- coding: utf-8 -*-
"""
LightMes CRM + 生产链路演示数据种子（正式版）
=============================================
在指定租户（默认 DEMO 租户）内生成一条完整销售→生产链路：

  CRM 客户 → 联系人 → 标签 → 线索 → 商机 → 报价单 → 合同 → 回款计划
  → 营销活动 → 销售目标 → 售后
  → won 商机 → 订单 → 生产计划 → 工单 → 工序任务 → 报工 → 审核 → 工资

特点：
  - 幂等：已存在的数据跳过，不会重复创建
  - 动态租户：自动查找 DEMO 租户，不硬编码 tenant_id
  - 动态关联：通过名称/状态查找实体 id，不硬编码 id
  - 可 import：run(tenant_id) 供后台 API / 编排器调用

运行方式：
  python3 scripts/seed_crm_demo.py          # 自动找 DEMO 租户
  python3 scripts/seed_crm_demo.py 2        # 指定 tenant_id
"""

from __future__ import annotations

import json
import random
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pymysql

from app.core.db import SessionLocal
from app.models.tenant import Tenant


# ---------------------------------------------------------------------------
# 数据库连接
# ---------------------------------------------------------------------------
def _get_conn():
    """读取数据库配置，返回 pymysql 连接。"""
    from app.core.config import settings
    from urllib.parse import urlparse, unquote
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


def _get_tenant_id(db=None) -> int:
    """查找 DEMO 租户 id。"""
    if db is not None:
        t = db.query(Tenant).filter(Tenant.code == "DEMO").first()
        if t:
            return t.id
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM tenants WHERE code='DEMO'")
            r = cur.fetchone()
            if not r:
                raise RuntimeError("DEMO 租户不存在，请先执行 demo_data.py")
            return r[0]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------
def _code(prefix: str, tenant_id: int, seq: int) -> str:
    return f"{prefix}{tenant_id}{seq:06d}"


def _count(cur, table: str, tenant_id: int) -> int:
    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE tenant_id=%s", (tenant_id,))
    return cur.fetchone()[0]


# ---------------------------------------------------------------------------
# CRM 销售链路
# ---------------------------------------------------------------------------
def _seed_crm_link(conn, tenant_id: int) -> dict:
    """客户/联系人/标签/线索/商机/报价/合同/回款/营销/售后。"""
    c = conn.cursor()
    now = datetime.now()
    SALES_OWNER = _get_sales_owner(c, tenant_id)

    # ---- 0. 客户标签 ----
    tags = ["VIP客户", "老客户", "高潜力", "重点跟进", "新客户", "风险客户"]
    tag_colors = ["#f56c6c", "#e6a23c", "#409eff", "#67c23a", "#909399", "#b37feb"]
    tag_ids = {}
    if _count(c, "customer_tags", tenant_id) == 0:
        for i, name in enumerate(tags, 1):
            c.execute(
                "INSERT INTO customer_tags (tenant_id, name, color, is_active) VALUES (%s,%s,%s,1)",
                (tenant_id, name, tag_colors[i - 1]),
            )
            tag_ids[name] = c.lastrowid
    else:
        c.execute("SELECT id, name FROM customer_tags WHERE tenant_id=%s", (tenant_id,))
        tag_ids = {name: tid for tid, name in c.fetchall()}

    # ---- 1. 客户档案 ----
    customers_seed = [
        # (名称, 联系人, 电话, 地址, 行业, 规模, 等级, 阶段)
        ("华强电子", "张老板", "13800138001", "深圳市南山区科技园", "电子", "中型", "A", "customer"),
        ("明达五金", "李明", "13800138002", "东莞市长安镇工业区", "五金", "小型", "B", "prospect"),
        ("躬行科技", "李乐乐", "13323138978", "广州市天河区软件园", "软件", "小型", "A", "customer"),
        ("恒力机械", "王建国", "13900139001", "佛山市顺德区机械园", "机械", "中型", "A", "customer"),
        ("联创精密", "陈志强", "13900139002", "东莞市大朗镇", "精密加工", "中型", "B", "prospect"),
        ("南方模具", "刘德华", "13900139003", "深圳市宝安区模具城", "模具", "小型", "B", "prospect"),
        ("盛达电子", "赵丽", "13900139004", "惠州市仲恺高新区", "电子", "大型", "A", "customer"),
        ("宏远塑胶", "孙建军", "13900139005", "东莞市塘厦镇", "塑胶", "中型", "B", "prospect"),
        ("金锐刀具", "周文强", "13900139006", "深圳市龙岗区", "刀具", "小型", "C", "prospect"),
        ("新光电器", "吴秀英", "13900139007", "中山市小榄镇", "电器", "中型", "B", "prospect"),
        ("中原轴承", "郑海", "13900139008", "佛山市南海区", "轴承", "大型", "A", "customer"),
        ("天成包装", "冯建国", "13900139009", "广州市白云区", "包装", "小型", "C", "prospect"),
    ]
    c.execute("SELECT id, name FROM customers WHERE tenant_id=%s", (tenant_id,))
    existing_customers = {name: cid for cid, name in c.fetchall()}
    customer_ids = {}
    for name, contact, phone, addr, industry, scale, level, stage in customers_seed:
        if name in existing_customers:
            customer_ids[name] = existing_customers[name]
            continue
        seq = len(existing_customers) + len(customer_ids) + 1
        cc = f"C{seq:03d}"
        c.execute(
            """INSERT INTO customers (tenant_id, user_id, code, name, contact_name, contact_phone,
               address, is_active, lifecycle_stage, health_score, industry, scale, customer_level, owner_user_id)
               VALUES (%s,NULL,%s,%s,%s,%s,%s,1,%s,80,%s,%s,%s,%s)""",
            (tenant_id, cc, name, contact, phone, addr, stage, industry, scale, level, SALES_OWNER),
        )
        customer_ids[name] = c.lastrowid
    for name in customers_seed:
        if name[0] not in customer_ids:
            c.execute("SELECT id FROM customers WHERE tenant_id=%s AND name=%s", (tenant_id, name[0]))
            r = c.fetchone()
            if r:
                customer_ids[name[0]] = r[0]

    # ---- 2. 联系人 ----
    contacts_seed = [
        ("华强电子", "张老板", "13800138001", "采购经理", 1),
        ("华强电子", "刘敏", "13912345678", "技术总监", 0),
        ("明达五金", "李明", "13800138002", "老板", 1),
        ("躬行科技", "李乐乐", "13323138978", "创始人", 1),
        ("恒力机械", "王建国", "13900139001", "总经理", 1),
        ("恒力机械", "王芳", "13712345678", "采购主管", 0),
        ("联创精密", "陈志强", "13900139002", "总经理", 1),
        ("盛达电子", "赵丽", "13900139004", "采购总监", 1),
        ("盛达电子", "钱进", "13612345678", "品质主管", 0),
        ("中原轴承", "郑海", "13900139008", "副总", 1),
    ]
    if _count(c, "customer_contacts", tenant_id) == 0:
        for cname, contact, phone, title, primary in contacts_seed:
            if cname in customer_ids:
                c.execute(
                    """INSERT INTO customer_contacts (tenant_id, customer_id, name, phone, title, is_primary, is_active)
                       VALUES (%s,%s,%s,%s,%s,%s,1)""",
                    (tenant_id, customer_ids[cname], contact, phone, title, primary),
                )

    # ---- 3. 客户产品关联 ----
    if _count(c, "customer_products", tenant_id) == 0:
        c.execute("SELECT id FROM products WHERE tenant_id=%s", (tenant_id,))
        product_ids = [r[0] for r in c.fetchall()] or [1, 2, 3, 4, 5]
        for cname, cid in list(customer_ids.items())[:8]:
            for pid in random.sample(product_ids, min(3, len(product_ids))):
                c.execute(
                    "INSERT INTO customer_products (tenant_id, customer_id, product_id) VALUES (%s,%s,%s)",
                    (tenant_id, cid, pid),
                )

    # ---- 4. 线索 ----
    leads_seed = [
        ("王总", "苏州精密电子", "13911112222", "wang@szjd.com", "华东", "展会", "新客户", "A", "需要铝合金外壳定制加工，月需求 5000 件"),
        ("李经理", "东莞智联科技", "13922223333", "li@zlkj.com", "华南", "官网", "待跟进", "B", "咨询 CNC 加工报价，有 3 款零件"),
        ("陈总", "深圳创新电子", "13933334444", "chen@cxdz.com", "华南", "转介绍", "跟进中", "A", "老朋友介绍，需要精密零件加工，量大"),
        ("赵经理", "惠州新能源", "13944445555", "zhao@xny.com", "华南", "展会", "新客户", "B", "电池壳体加工需求，需开模"),
        ("孙总", "佛山陶瓷机械", "13955556666", "sun@tcjx.com", "华南", "B2B平台", "待跟进", "C", "咨询陶瓷机械配件加工"),
        ("周经理", "中山灯具厂", "13966667777", "zhou@dj.com", "华南", "广告投放", "跟进中", "B", "灯饰五金件采购，月需求 2000 件"),
        ("吴总", "宁波汽车配件", "13977778888", "wu@qc.com", "华东", "转介绍", "新客户", "A", "汽车零部件供应商，需要长期合作"),
        ("郑经理", "广州医疗器械", "13988889999", "zheng@yl.com", "华南", "展会", "待跟进", "B", "医疗器械精密件加工需求"),
    ]
    if _count(c, "crm_leads", tenant_id) == 0:
        lead_status_map = {"新客户": "new", "待跟进": "new", "跟进中": "working", "已转化": "converted"}
        for i, (contact, company, mobile, email, region, source, status, grade, remark) in enumerate(leads_seed, 1):
            c.execute(
                """INSERT INTO crm_leads (tenant_id, code, contact_name, company, email, mobile,
                   position, industry, province, source, interest_products, remark, status, score, grade,
                   owner_user_id, is_public_pool, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)""",
                (tenant_id, _code("LD", tenant_id, i), contact, company, email, mobile,
                 "采购经理", "制造业", region, source, json.dumps(["铝合金加工", "CNC"]), remark,
                 lead_status_map.get(status, "new"), random.randint(40, 90), grade,
                 SALES_OWNER if status != "待跟进" else None, 0 if status != "待跟进" else 1),
            )

    # ---- 5. 商机 ----
    opp_seed = [
        ("华强电子", "华强电子铝合金外壳年度采购", "quoted", "open", 186000.00, 60, "2026-08-30", "大客户年度框架订单，已报价待确认"),
        ("明达五金", "明达五金 CNC 加工合作", "qualified", "open", 45000.00, 40, "2026-09-15", "打样中，需要确认交期"),
        ("恒力机械", "恒力机械大型结构件加工", "prospecting", "open", 128000.00, 25, "2026-09-30", "刚接触，需求量大"),
        ("联创精密", "联创精密 3C 零件批量订单", "negotiation", "open", 86000.00, 75, "2026-08-20", "商务谈判中，主要卡在付款方式"),
        ("盛达电子", "盛达电子消费电子外壳", "won", "won", 320000.00, 100, "2026-07-15", "已成交，转入订单"),
        ("南方模具", "南方模具模架配件采购", "lost", "lost", 26000.00, 0, "2026-06-30", "价格过高流失"),
        ("中原轴承", "中原轴承精密轴承座", "qualified", "open", 96000.00, 50, "2026-09-10", "技术交流完成，等待对方预算"),
    ]
    if _count(c, "crm_opportunities", tenant_id) == 0:
        for i, (cname, title, stage, status, amount, prob, close_date, remark) in enumerate(opp_seed, 1):
            c.execute(
                """INSERT INTO crm_opportunities (tenant_id, customer_id, code, title, stage, status,
                   amount, probability, expected_close_date, owner_user_id, remark, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)""",
                (tenant_id, customer_ids[cname], _code("OP", tenant_id, i), title, stage, status,
                 amount, prob, close_date, SALES_OWNER, remark),
            )

    # ---- 6. 报价单 ----
    quot_seed = [
        ("华强电子", "铝合金外壳加工报价", "accepted", 186000.00, "华强电子铝合金外壳年度采购"),
        ("明达五金", "CNC 加工报价单", "sent", 45000.00, "明达五金 CNC 加工合作"),
        ("恒力机械", "大型结构件加工报价", "draft", 128000.00, "恒力机械大型结构件加工"),
        ("联创精密", "3C 零件批量报价", "sent", 86000.00, "联创精密 3C 零件批量订单"),
        ("盛达电子", "消费电子外壳报价", "accepted", 320000.00, "盛达电子消费电子外壳"),
    ]
    if _count(c, "crm_quotations", tenant_id) == 0:
        c.execute("SELECT id, customer_id, title FROM crm_opportunities WHERE tenant_id=%s", (tenant_id,))
        opp_by_customer = {}
        for oid, ocid, otitle in c.fetchall():
            opp_by_customer[ocid] = (oid, otitle)
        c.execute("SELECT id, name FROM products WHERE tenant_id=%s LIMIT 5", (tenant_id,))
        products = c.fetchall()
        for i, (cname, title, status, total, opp_title) in enumerate(quot_seed, 1):
            cid = customer_ids[cname]
            opp_id = next((oid for oid, ot in opp_by_customer.values() if ot == opp_title), None)
            now_dt = datetime.now()
            valid_from = now_dt - timedelta(days=7)
            valid_until = now_dt + timedelta(days=23)
            sent_at = now_dt - timedelta(days=5) if status in ("sent", "accepted") else None
            accepted_at = now_dt - timedelta(days=3) if status == "accepted" else None
            c.execute(
                """INSERT INTO crm_quotations (tenant_id, code, title, customer_id, opportunity_id, version,
                   status, valid_from, valid_until, currency, tax_rate, subtotal, tax_amount, total_amount,
                   payment_terms, delivery_terms, owner_user_id, sent_at, accepted_at, is_active)
                   VALUES (%s,%s,%s,%s,%s,1,%s,%s,%s,'CNY',0.13,%s,%s,%s,'月结30天','款到发货',%s,%s,%s,1)""",
                (tenant_id, _code("Q", tenant_id, i), title, cid, opp_id, status, valid_from, valid_until,
                 total / 1.13, total - total / 1.13, total, SALES_OWNER, sent_at, accepted_at),
            )
            qid = c.lastrowid
            for j, (pid, pname) in enumerate(products[:2], 1):
                qty = random.randint(100, 1000)
                price = round(total / (qty * 2), 4) if qty > 0 else 1
                amount = round(qty * price, 4)
                c.execute(
                    """INSERT INTO crm_quotation_items (tenant_id, quotation_id, product_id, product_name, spec,
                       quantity, unit_price, discount_rate, tax_rate, amount, delivery_date)
                       VALUES (%s,%s,%s,%s,'标准件',%s,%s,0,0.13,%s,%s)""",
                    (tenant_id, qid, pid, pname, qty, price, amount, (now_dt + timedelta(days=30)).date()),
                )

    # ---- 7. 合同 + 回款计划 ----
    contract_seed = [
        ("华强电子", "2026年铝合金外壳加工合同", "active", 186000.00, "2026-06-01", "2026-12-31", "30%预付款+月结"),
        ("盛达电子", "消费电子外壳供货合同", "active", 320000.00, "2026-05-01", "2026-11-30", "月结45天"),
        ("中原轴承", "精密轴承座年度合同", "expiring", 96000.00, "2026-01-01", "2026-08-31", "季度结算"),
        ("明达五金", "CNC 加工框架协议", "active", 45000.00, "2026-07-01", "2027-06-30", "月结30天"),
        ("南方模具", "模架配件采购合同", "expired", 26000.00, "2026-03-01", "2026-06-30", "货到付款"),
    ]
    if _count(c, "crm_contracts", tenant_id) == 0:
        for i, (cname, name, status, total, sign, end, terms) in enumerate(contract_seed, 1):
            c.execute(
                """INSERT INTO crm_contracts (tenant_id, code, name, customer_id, type, status,
                   sign_date, start_date, end_date, auto_renewal, renewal_notice_days, total_amount,
                   currency, payment_terms, owner_user_id, is_active)
                   VALUES (%s,%s,%s,%s,'sales',%s,%s,%s,%s,0,30,%s,'CNY',%s,%s,1)""",
                (tenant_id, _code("CT", tenant_id, i), name, customer_ids[cname], status, sign, sign, end,
                 total, terms, SALES_OWNER),
            )
            cid = c.lastrowid
            n_phases = random.randint(2, 3)
            phase_names = ["预付款", "进度款", "尾款"]
            for p in range(n_phases):
                due = datetime.strptime(sign, "%Y-%m-%d") + timedelta(days=30 * (p + 1))
                amt = round(total * (0.3 if p == 0 else (0.4 if p == 1 else 0.3)), 2)
                paid = 1 if (status == "active" and p < 1) or (status == "expired") else 0
                c.execute(
                    """INSERT INTO crm_payment_plans (tenant_id, contract_id, phase, phase_name, due_date,
                       amount, actual_amount, actual_date, status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (tenant_id, cid, f"phase_{p+1}", phase_names[p], due.date(), amt,
                     amt if paid else 0, due.date() if paid else None, "paid" if paid else "pending"),
                )

    # ---- 8. 营销活动 ----
    if _count(c, "crm_campaigns", tenant_id) == 0:
        campaigns = [
            ("2026年Q3华南制造业展会", "exhibition", "lead_gen", "2026-07-01", "2026-09-30", "completed", 30000, 26000, 450000, 120),
            ("CNC 加工线上推广", "online", "brand", "2026-06-01", "2026-08-31", "active", 15000, 8200, 180000, 80),
            ("老客户转介绍激励", "referral", "retention", "2026-05-01", "2026-07-31", "completed", 5000, 3800, 96000, 25),
        ]
        for i, (name, type_, obj, start, end, status, budget, cost, revenue, leads) in enumerate(campaigns, 1):
            c.execute(
                """INSERT INTO crm_campaigns (tenant_id, code, name, type, objective, target_audience, channel,
                   status, start_date, end_date, budget, actual_cost, expected_revenue, actual_revenue,
                   currency, target_leads_count, owner_user_id, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'CNY',%s,%s,1)""",
                (tenant_id, _code("CAM", tenant_id, i), name, type_, obj, "华南制造业企业", "展会/线上/口碑",
                 status, start, end, budget, cost, revenue, revenue, leads, SALES_OWNER),
            )

    # ---- 9. 销售目标 ----
    if _count(c, "crm_sales_targets", tenant_id) == 0:
        this_year = now.year
        month_start = f'{now.strftime("%Y-%m")}-01'
        month_end = (now.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m-%d")
        targets = [
            ("year", f"{this_year}-01-01", f"{this_year}-12-31", "team", None, "revenue", 2000000),
            ("month", month_start, month_end, "team", None, "revenue", 180000),
            ("month", month_start, month_end, "owner", SALES_OWNER, "revenue", 180000),
        ]
        for i, (ptype, pstart, pend, dim, dim_id, metric, value) in enumerate(targets, 1):
            c.execute(
                """INSERT INTO crm_sales_targets (tenant_id, period_type, period_start, period_end,
                   dimension, dimension_id, metric, target_value, currency, owner_user_id, created_by, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'CNY',%s,%s,1)""",
                (tenant_id, ptype, pstart, pend, dim, dim_id, metric, value, SALES_OWNER, SALES_OWNER),
            )

    # ---- 10. 售后 ----
    if _count(c, "after_sales", tenant_id) == 0:
        afters = [
            ("quality", "客户反馈外壳表面有划痕", "已安排重新加工并补发", "resolved"),
            ("delivery", "交期延误客户投诉", "已加急处理并致歉", "processing"),
            ("quality", "尺寸偏差超出公差", "已安排返工", "resolved"),
        ]
        c.execute("SELECT id FROM orders WHERE tenant_id=%s ORDER BY id LIMIT 3", (tenant_id,))
        order_ids = [r[0] for r in c.fetchall()]
        for i, (stype, reason, solution, status) in enumerate(afters, 1):
            if order_ids:
                c.execute(
                    """INSERT INTO after_sales (tenant_id, order_id, code, sale_type, reason, solution, status, created_by)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (tenant_id, order_ids[i - 1], _code("AS", tenant_id, i), stype, reason, solution, status, SALES_OWNER),
                )

    # ---- 11. 跟进记录 ----
    if _count(c, "crm_opportunity_activities", tenant_id) == 0:
        c.execute("SELECT id FROM crm_opportunities WHERE tenant_id=%s", (tenant_id,))
        opps = [r[0] for r in c.fetchall()]
        actions = ["call", "visit", "wechat", "email", "note"]
        notes = [
            "电话沟通，客户对报价比较满意，等待内部确认",
            "上门拜访，参观了客户工厂，确认了技术需求",
            "微信沟通，客户询问交期，已回复标准交期 30 天",
            "发送了最新报价单和产品资料",
            "客户反馈价格略高，正在内部协商预算",
        ]
        for oid in opps:
            for _ in range(random.randint(1, 3)):
                created = now - timedelta(days=random.randint(1, 30))
                c.execute(
                    """INSERT INTO crm_opportunity_activities (tenant_id, opportunity_id, action_type,
                       content, created_by, created_at)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (tenant_id, oid, random.choice(actions), random.choice(notes), SALES_OWNER, created),
                )
    if _count(c, "crm_lead_activities", tenant_id) == 0:
        c.execute("SELECT id FROM crm_leads WHERE tenant_id=%s", (tenant_id,))
        lead_ids = [r[0] for r in c.fetchall()]
        notes = ["初步电话联系，客户有意向，已发送资料", "微信添加成功，约定下周视频会议", "客户反馈需要先看样品"]
        for lid in lead_ids:
            for _ in range(random.randint(1, 2)):
                created = now - timedelta(days=random.randint(1, 20))
                c.execute(
                    """INSERT INTO crm_lead_activities (tenant_id, lead_id, action_type, content,
                       created_by, created_at, is_active)
                       VALUES (%s,%s,'call',%s,%s,%s,1)""",
                    (tenant_id, lid, random.choice(notes), SALES_OWNER, created),
                )

    # ---- 12. 输单原因 ----
    if _count(c, "crm_win_loss_reasons", tenant_id) == 0:
        WIN = ["价格有竞争力", "产品功能领先", "服务响应快", "方案契合度", "客户关系深度"]
        LOSS = ["价格过高", "预算不足", "客户选择竞品", "功能不满足", "服务响应慢", "未接触关键决策人", "项目延期", "内部组织变动", "其他"]
        for i, name in enumerate(WIN, 1):
            c.execute(
                """INSERT INTO crm_win_loss_reasons (tenant_id, type, category, code, name, sort_order, is_active)
                   VALUES (%s,'win','价格与商务',%s,%s,%s,1)""",
                (tenant_id, f"WIN{i:02d}", name, i),
            )
        for i, name in enumerate(LOSS, 1):
            c.execute(
                """INSERT INTO crm_win_loss_reasons (tenant_id, type, category, code, name, sort_order, is_active)
                   VALUES (%s,'loss','价格与商务',%s,%s,%s,1)""",
                (tenant_id, f"LOSS{i:02d}", name, i),
            )

    # ---- 13. 客户画像刷新 ----
    c.execute(
        """UPDATE customers SET
           open_opportunity_count = (SELECT COUNT(*) FROM crm_opportunities o WHERE o.customer_id = customers.id AND o.status = 'open'),
           active_contract_count = (SELECT COUNT(*) FROM crm_contracts ct WHERE ct.customer_id = customers.id AND ct.status IN ('active','expiring'))
           WHERE tenant_id=%s""",
        (tenant_id,),
    )
    conn.commit()
    return {"ok": True}


def _get_sales_owner(cur, tenant_id: int) -> int:
    """找该租户第一个有 CRM 销售权限的用户；找不到就用该租户 admin。"""
    cur.execute(
        """SELECT u.id FROM users u
           JOIN user_roles ur ON ur.user_id = u.id
           JOIN roles r ON r.id = ur.role_id
           WHERE u.tenant_id=%s AND (r.code='sales' OR r.name LIKE '%%销售%%')
           ORDER BY u.id LIMIT 1""",
        (tenant_id,),
    )
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute("SELECT id FROM users WHERE tenant_id=%s ORDER BY id LIMIT 1", (tenant_id,))
    r = cur.fetchone()
    if r:
        return r[0]
    raise RuntimeError(f"租户 {tenant_id} 无任何用户")


# ---------------------------------------------------------------------------
# won 商机 → 订单 → 生产计划 → 工单 → 任务 → 报工
# ---------------------------------------------------------------------------
def _seed_production_link(conn, tenant_id: int) -> dict:
    """把 won 商机转成订单，并打通生产链路。"""
    c = conn.cursor()
    today = date.today()
    today_str = today.strftime("%Y%m%d")

    # 找 won 商机（盛达电子消费电子外壳）
    c.execute(
        """SELECT o.id, o.customer_id, cu.name FROM crm_opportunities o
           JOIN customers cu ON cu.id = o.customer_id
           WHERE o.tenant_id=%s AND o.status='won' AND o.converted_order_id IS NULL
           ORDER BY o.id LIMIT 1""",
        (tenant_id,),
    )
    opp = c.fetchone()
    if not opp:
        return {"ok": True, "skipped": "无未转化的 won 商机"}
    opp_id, cust_id, cust_name = opp

    # 找该客户对应的报价单（accepted）
    c.execute(
        "SELECT id FROM crm_quotations WHERE tenant_id=%s AND customer_id=%s AND status='accepted' AND converted_order_id IS NULL ORDER BY id LIMIT 1",
        (tenant_id, cust_id),
    )
    q_row = c.fetchone()
    q_id = q_row[0] if q_row else None

    # 找该客户的合同（active）
    c.execute(
        "SELECT id FROM crm_contracts WHERE tenant_id=%s AND customer_id=%s AND status='active' AND order_id IS NULL ORDER BY id LIMIT 1",
        (tenant_id, cust_id),
    )
    ct_row = c.fetchone()
    ct_id = ct_row[0] if ct_row else None

    # 成品 SKU（铝合金支架系列，按产品 code 找）
    c.execute(
        """SELECT s.id, s.product_id, s.code FROM skus s
           JOIN products p ON p.id = s.product_id
           WHERE s.tenant_id=%s AND p.code='P001' AND s.is_active=1
           ORDER BY s.id LIMIT 3""",
        (tenant_id,),
    )
    skus = c.fetchall()
    if len(skus) < 3:
        # 回退：任意 3 个成品 SKU
        c.execute(
            """SELECT s.id, s.product_id, s.code FROM skus s
               WHERE s.tenant_id=%s AND s.is_active=1 AND s.code NOT LIKE 'MAT-%'
               ORDER BY s.id LIMIT 3""",
            (tenant_id,),
        )
        skus = c.fetchall()
    if not skus:
        return {"ok": False, "error": "无可用成品 SKU，请先执行 demo_data.py"}

    chosen = [(s[0], s[1], 200 if i == 0 else (150 if i == 1 else 100), 450.0 if i == 0 else (650.0 if i == 1 else 1350.0))
              for i, s in enumerate(skus[:3])]
    total = sum(q * p for _, _, q, p in chosen)

    # 订单编号
    c.execute(
        """INSERT INTO code_sequences (tenant_id, biz_type, period_key, `last_value`)
           VALUES (%s, 'order', %s, 1)
           ON DUPLICATE KEY UPDATE `last_value`=GREATEST(`last_value`, 1)""",
        (tenant_id, today_str),
    )
    c.execute(
        "SELECT `last_value` FROM code_sequences WHERE tenant_id=%s AND biz_type='order' AND period_key=%s",
        (tenant_id, today_str),
    )
    seq = c.fetchone()[0]
    order_code = f"ORD{today_str}{seq:04d}"
    now = datetime.now()

    # 找报工/审核用户（按角色：员工/班组长/质检）
    c.execute(
        """SELECT u.id, u.full_name, r.code FROM users u
           JOIN user_roles ur ON ur.user_id=u.id
           JOIN roles r ON r.id=ur.role_id
           WHERE u.tenant_id=%s ORDER BY r.code""",
        (tenant_id,),
    )
    role_map = {}
    for uid, uname, rcode in c.fetchall():
        role_map.setdefault(rcode, uid)
    emp_id = role_map.get("employee") or role_map.get("admin")
    leader_id = role_map.get("leader") or role_map.get("admin")
    qc_id = role_map.get("qc") or role_map.get("admin")
    if not emp_id:
        emp_id = leader_id = qc_id = 1

    # 创建订单
    c.execute(
        """INSERT INTO orders
           (tenant_id, customer_id, opportunity_id, code, status, amount, due_date, remark,
            confirmed_at, confirmed_by, created_at, updated_at)
           VALUES (%s,%s,%s,%s,'producing',%s,%s,'演示订单（商机转化）',%s,%s,%s,%s)""",
        (tenant_id, cust_id, opp_id, order_code, total, today + timedelta(days=14), now, emp_id, now, now),
    )
    ord_id = c.lastrowid

    # 订单明细
    for line_no, (sku_id, product_id, qty, unit_price) in enumerate(chosen, 1):
        c.execute(
            """INSERT INTO order_items (tenant_id, order_id, line_no, sku_id, qty, unit_price, subtotal)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (tenant_id, ord_id, line_no, sku_id, qty, unit_price, round(qty * unit_price, 2)),
        )
        c.execute("SELECT LAST_INSERT_ID()")
        item_id = c.fetchone()[0]

        # 工单（product_id 用 SKU 对应的产品 id，不是 sku_id）
        c.execute(
            """INSERT INTO work_orders (tenant_id, order_id, order_item_id, product_id, sku_id, qty,
               status, standard_hours, actual_hours, started_at, created_at, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,'in_progress',0,0,%s,%s,%s)""",
            (tenant_id, ord_id, item_id, product_id, sku_id, qty, now, now, now),
        )
        wo_id = c.lastrowid

        # 默认工艺路线（该产品，用 product_id 查）
        c.execute(
            "SELECT id FROM process_routes WHERE tenant_id=%s AND product_id=%s AND is_default=1 LIMIT 1",
            (tenant_id, product_id),
        )
        route_row = c.fetchone()
        route_steps = []
        if route_row:
            c.execute(
                "SELECT process_id FROM process_route_steps WHERE route_id=%s ORDER BY seq",
                (route_row[0],),
            )
            route_steps = [r[0] for r in c.fetchall()]
        if not route_steps:
            c.execute("SELECT id FROM processes WHERE tenant_id=%s ORDER BY id LIMIT 6", (tenant_id,))
            route_steps = [r[0] for r in c.fetchall()]
        if not route_steps:
            raise RuntimeError(f"租户 {tenant_id} 无工序，请先执行 demo_data.py")

        # 任务
        for seq_i, proc_id in enumerate(route_steps, 1):
            c.execute(
                "SELECT COALESCE(MAX(`last_value`),0) FROM code_sequences WHERE tenant_id=%s AND biz_type='task'",
                (tenant_id,),
            )
            max_seq = c.fetchone()[0] + 1
            task_code = f"TK{tenant_id:03d}{max_seq:06d}"
            c.execute(
                """INSERT INTO code_sequences (tenant_id, biz_type, period_key, `last_value`)
                   VALUES (%s,'task',%s,%s)
                   ON DUPLICATE KEY UPDATE `last_value`=GREATEST(`last_value`, %s)""",
                (tenant_id, "ALL", max_seq, max_seq),
            )
            status = "pending"
            if seq_i == 1:
                status = "in_progress"
            c.execute(
                """INSERT INTO tasks (tenant_id, work_order_id, process_id, seq, task_code, planned_qty,
                   status, assigned_user_id, assigned_at, assigned_by, created_at, updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (tenant_id, wo_id, proc_id, seq_i, task_code, qty, status, emp_id, now, leader_id, now, now),
            )

    # 商机/报价/合同挂接
    c.execute("UPDATE crm_opportunities SET converted_order_id=%s WHERE id=%s", (ord_id, opp_id))
    if q_id:
        c.execute("UPDATE crm_quotations SET converted_order_id=%s WHERE id=%s", (ord_id, q_id))
    if ct_id:
        c.execute("UPDATE crm_contracts SET order_id=%s WHERE id=%s", (ord_id, ct_id))

    conn.commit()
    return {"ok": True, "order_id": ord_id, "order_code": order_code, "customer": cust_name}


def _seed_reports(conn, tenant_id: int) -> dict:
    """给新工单造报工数据（qc_approved），推进任务/工单状态。"""
    c = conn.cursor()
    now = datetime.now()

    c.execute(
        """SELECT u.id, u.full_name, r.code FROM users u
           JOIN user_roles ur ON ur.user_id=u.id
           JOIN roles r ON r.id=ur.role_id
           WHERE u.tenant_id=%s ORDER BY r.code""",
        (tenant_id,),
    )
    role_map = {}
    for uid, uname, rcode in c.fetchall():
        role_map.setdefault(rcode, uid)
    emp_id = role_map.get("employee") or role_map.get("admin") or 1
    leader_id = role_map.get("leader") or role_map.get("admin") or 1
    qc_id = role_map.get("qc") or role_map.get("admin") or 1

    # 最近订单的工单（演示订单，无报工）
    c.execute(
        """SELECT w.id, w.sku_id, w.qty, w.order_item_id FROM work_orders w
           JOIN orders o ON o.id = w.order_id
           WHERE w.tenant_id=%s AND o.opportunity_id IS NOT NULL
             AND NOT EXISTS (SELECT 1 FROM reports r WHERE r.task_id IN
                             (SELECT t.id FROM tasks t WHERE t.work_order_id=w.id))
           ORDER BY w.id LIMIT 3""",
        (tenant_id,),
    )
    wos = c.fetchall()
    if not wos:
        return {"ok": True, "skipped": "无待报工的演示工单"}

    def add_report(task_id, good, bad, status="qc_approved", days_ago=0, remark=""):
        created = now - timedelta(days=days_ago, hours=2)
        audited = created + timedelta(hours=1)
        c.execute(
            """INSERT INTO reports (tenant_id, task_id, report_user_id, good_qty, bad_qty, remark, status, created_at, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (tenant_id, task_id, emp_id, good, bad, remark, status, created, audited),
        )
        rid = c.lastrowid
        c.execute(
            """INSERT INTO report_audits (tenant_id, report_id, auditor_id, audit_level, action, reason, created_at)
               VALUES (%s,%s,%s,'leader','approve','班组长审核通过',%s)""",
            (tenant_id, rid, leader_id, audited),
        )
        c.execute(
            """INSERT INTO report_audits (tenant_id, report_id, auditor_id, audit_level, action, reason, created_at)
               VALUES (%s,%s,%s,'qc','approve','质检合格',%s)""",
            (tenant_id, rid, qc_id, audited + timedelta(minutes=30)),
        )
        return rid

    def update_task(task_id):
        c.execute("SELECT COALESCE(SUM(good_qty),0) FROM reports WHERE task_id=%s AND status='qc_approved'", (task_id,))
        done_qty = c.fetchone()[0]
        c.execute("SELECT planned_qty FROM tasks WHERE id=%s", (task_id,))
        planned = c.fetchone()[0]
        if done_qty >= planned:
            c.execute("UPDATE tasks SET status='done' WHERE id=%s", (task_id,))
            return "done"
        elif done_qty > 0:
            c.execute("UPDATE tasks SET status='in_progress' WHERE id=%s", (task_id,))
            return "in_progress"
        return "pending"

    def sync_wo(wo_id):
        c.execute("SELECT COUNT(*), COALESCE(SUM(status='done'),0), COALESCE(SUM(status='in_progress'),0) FROM tasks WHERE work_order_id=%s", (wo_id,))
        total, done_n, prog_n = c.fetchone()
        if done_n == total:
            c.execute("UPDATE work_orders SET status='done', finished_at=%s WHERE id=%s", (now, wo_id))
            return "done"
        elif prog_n and prog_n > 0:
            c.execute("UPDATE work_orders SET status='in_progress', started_at=COALESCE(started_at,%s) WHERE id=%s", (now, wo_id))
            return "in_progress"
        return "open"

    for wo_id, sku_id, qty, item_id in wos[:3]:
        c.execute("SELECT id, seq FROM tasks WHERE work_order_id=%s ORDER BY seq", (wo_id,))
        tasks = c.fetchall()
        if len(tasks) < 2:
            continue
        # 工单A：前 3 道完成，后 2 道部分
        add_report(tasks[0][0], qty, 0, remark="下料完成")
        update_task(tasks[0][0])
        add_report(tasks[1][0], qty, 2, remark="冲压完成")
        update_task(tasks[1][0])
        if len(tasks) >= 3:
            add_report(tasks[2][0], qty, 0, remark="焊接完成")
            update_task(tasks[2][0])
        if len(tasks) >= 4:
            add_report(tasks[3][0], int(qty * 0.6), 1, remark="打磨进行中")
            update_task(tasks[3][0])
        if len(tasks) >= 5:
            add_report(tasks[4][0], int(qty * 0.3), 0, remark="表面处理进行中")
            update_task(tasks[4][0])
        sync_wo(wo_id)

    conn.commit()
    return {"ok": True, "work_orders": len(wos)}


# ---------------------------------------------------------------------------
# 统一入口
# ---------------------------------------------------------------------------
def run(tenant_id: int | None = None, conn=None) -> dict:
    """执行全部 CRM + 生产链路演示数据。返回结果 dict。"""
    own_conn = conn is None
    if own_conn:
        conn = _get_conn()
    try:
        if tenant_id is None:
            tenant_id = _get_tenant_id()
        result = {"tenant_id": tenant_id}
        result["crm"] = _seed_crm_link(conn, tenant_id)
        result["production"] = _seed_production_link(conn, tenant_id)
        result["reports"] = _seed_reports(conn, tenant_id)
        return result
    finally:
        if own_conn:
            conn.close()


if __name__ == "__main__":
    import json

    tid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    res = run(tid)
    print(json.dumps(res, ensure_ascii=False, indent=2))
