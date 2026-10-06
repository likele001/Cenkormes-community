"""订单/采购 审批门禁端到端验证（S2-3）。
在独立测试租户构造最小主数据，验证：
- 开关开（有启用流程）时 submit_for_approval 建档，审批通过→单据确认，驳回→回草稿
- 开关关（无流程）时 order_approval_enabled 为 False
结束后清理测试租户。跑：cd backend && PYTHONPATH=. venv/bin/python /tmp/e2e_biz.py
"""
import sys
import traceback

from sqlalchemy import delete, select

from app.core.db import SessionLocal
from app.models.approval import ApprovalFlow, ApprovalStep
from app.models.customer import Customer
from app.models.material import Supplier
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.purchase import PurchaseOrder
from app.models.sku import Sku
from app.models.tenant import Tenant
from app.models.user import User
from app.models.workflow import ApprovalInstance, ApprovalRecord, ApprovalTask
from app.services.workflow import biz_hooks, engine

PASS, FAIL = [], []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")


def main():
    db = SessionLocal()
    try:
        for ot in db.execute(select(Tenant).where(Tenant.name == "S2Biz测试租户")).scalars().all():
            _clean(db, ot.id)
        db.commit()

        tn = Tenant(name="S2Biz测试租户", code="s2biztest")
        db.add(tn)
        db.flush()
        db.commit()
        tid = tn.id
        print(f"== 测试租户 tid={tid} ==")

        u = User(tenant_id=tid, username="s2bizadmin", password_hash="x", full_name="审批员", is_active=True)
        db.add(u)
        db.flush()
        c = Customer(tenant_id=tid, code="C01", name="测试客户")
        db.add(c)
        db.flush()
        sup = Supplier(tenant_id=tid, code="S01", name="测试供应商")
        db.add(sup)
        db.flush()
        prod = Product(tenant_id=tid, code="P01", name="测试产品")
        db.add(prod)
        db.flush()
        sku = Sku(tenant_id=tid, product_id=prod.id, code="SKU1", name="标准件", cost_price=0)
        db.add(sku)
        db.flush()
        db.commit()
        uid = u.id

        def mk_flow(biz, role="leader"):
            f = ApprovalFlow(tenant_id=tid, name=f"Biz-{biz}", biz_type=biz, is_active=True, version=1)
            db.add(f)
            db.flush()
            db.add(ApprovalStep(flow_id=f.id, step_order=1, approver_role=role, is_required=True,
                                can_skip=0, label="第一级", sign_mode="single", assignee_ids=[uid]))
            db.commit()
            return f

        mk_flow("order")
        mk_flow("purchase")
        check("开关: order_approval_enabled=True", biz_hooks.order_approval_enabled(db, tid) is True)
        check("开关: purchase_approval_enabled=True", biz_hooks.purchase_approval_enabled(db, tid) is True)

        # ---- 采购单 通过 与 驳回 ----
        print("\n== 采购单门禁 ==")
        po1 = PurchaseOrder(tenant_id=tid, supplier_id=sup.id, code="PO-APPROVE", status="draft")
        db.add(po1)
        db.flush()
        po1.status = "pending_confirm"
        db.flush()
        inst = biz_hooks.submit_for_approval(db, tid, "purchase", po1.id, initiator_id=uid, meta={"code": po1.code})
        db.commit()
        inst = db.scalar(select(ApprovalInstance).where(ApprovalInstance.id == inst.id))
        t = db.scalar(select(ApprovalTask).where(ApprovalTask.instance_id == inst.id, ApprovalTask.status == "pending"))
        engine.approve_task(db, t.id, operator_id=uid, comment="采购审批通过")
        db.expire_all()
        po1 = db.get(PurchaseOrder, po1.id)
        check("采购: 审批通过 → 确认", po1.status == "confirmed", f"status={po1.status}")

        po2 = PurchaseOrder(tenant_id=tid, supplier_id=sup.id, code="PO-REJECT", status="draft")
        db.add(po2)
        db.flush()
        po2.status = "pending_confirm"
        db.flush()
        inst2 = biz_hooks.submit_for_approval(db, tid, "purchase", po2.id, initiator_id=uid)
        db.commit()
        inst2 = db.scalar(select(ApprovalInstance).where(ApprovalInstance.id == inst2.id))
        t2 = db.scalar(select(ApprovalTask).where(ApprovalTask.instance_id == inst2.id, ApprovalTask.status == "pending"))
        engine.reject_task(db, t2.id, operator_id=uid, reason="价格不支持")
        db.expire_all()
        po2 = db.get(PurchaseOrder, po2.id)
        check("采购: 审批驳回 → 回草稿", po2.status == "draft", f"status={po2.status}")

        # ---- 销售订单 通过 与 驳回 ----
        print("\n== 销售订单门禁 ==")
        o1 = Order(tenant_id=tid, customer_id=c.id, code="ORD-APPROVE", status="draft", due_date=None)
        db.add(o1)
        db.flush()
        it1 = OrderItem(tenant_id=tid, order_id=o1.id, line_no=1, sku_id=sku.id, qty=2, unit_price=0, subtotal=0)
        db.add(it1)
        db.flush()
        o1.status = "pending_confirm"
        db.flush()
        inst3 = biz_hooks.submit_for_approval(db, tid, "order", o1.id, initiator_id=uid,
                                              meta={"code": o1.code, "amount": 0})
        db.commit()
        inst3 = db.scalar(select(ApprovalInstance).where(ApprovalInstance.id == inst3.id))
        t3 = db.scalar(select(ApprovalTask).where(ApprovalTask.instance_id == inst3.id, ApprovalTask.status == "pending"))
        engine.approve_task(db, t3.id, operator_id=uid, comment="订单审批通过")
        db.expire_all()
        o1 = db.scalar(select(Order).where(Order.id == o1.id))
        check("订单: 审批通过 → 确认", o1.status == "confirmed", f"status={o1.status}")

        o2 = Order(tenant_id=tid, customer_id=c.id, code="ORD-REJECT", status="draft", due_date=None)
        db.add(o2)
        db.flush()
        it2 = OrderItem(tenant_id=tid, order_id=o2.id, line_no=1, sku_id=sku.id, qty=1, unit_price=0, subtotal=0)
        db.add(it2)
        db.flush()
        o2.status = "pending_confirm"
        db.flush()
        inst4 = biz_hooks.submit_for_approval(db, tid, "order", o2.id, initiator_id=uid)
        db.commit()
        inst4 = db.scalar(select(ApprovalInstance).where(ApprovalInstance.id == inst4.id))
        t4 = db.scalar(select(ApprovalTask).where(ApprovalTask.instance_id == inst4.id, ApprovalTask.status == "pending"))
        engine.reject_task(db, t4.id, operator_id=uid, reason="交期不符")
        db.expire_all()
        o2 = db.scalar(select(Order).where(Order.id == o2.id))
        check("订单: 审批驳回 → 回草稿", o2.status == "draft", f"status={o2.status}")

        # ---- 开关关 ----
        print("\n== 开关关闭 ==")
        db.execute(delete(ApprovalStep).where(ApprovalStep.flow_id.in_(
            select(ApprovalFlow.id).where(ApprovalFlow.tenant_id == tid))))
        db.execute(delete(ApprovalFlow).where(ApprovalFlow.tenant_id == tid))
        db.commit()
        check("开关: 删除流程后 order_approval_enabled=False",
              biz_hooks.order_approval_enabled(db, tid) is False)
        check("开关: 删除流程后 purchase_approval_enabled=False",
              biz_hooks.purchase_approval_enabled(db, tid) is False)

        _clean(db, tid)
        print("== 清理测试租户 ==")
    except Exception:
        traceback.print_exc()
        FAIL.append("EXCEPTION")
        db.rollback()
    finally:
        db.close()

    print("\n======================================")
    print(f"通过 {len(PASS)} 项, 失败 {len(FAIL)} 项: {FAIL}")
    return 0 if not FAIL else 1


def _clean(db, tid):
    for model in (ApprovalRecord, ApprovalTask, ApprovalInstance, PurchaseOrder, Order, OrderItem,
                  Sku, Product, Customer, Supplier, ApprovalFlow, User):
        db.execute(delete(model).where(model.__table__.columns.get("tenant_id") == tid))
    db.execute(delete(Tenant).where(Tenant.id == tid))


if __name__ == "__main__":
    sys.exit(main())