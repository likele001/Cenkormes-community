from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.purchase import PurchaseOrder, PurchaseOrderItem


def get_purchase_order_by_id(db: Session, tenant_id: int, order_id: int, with_items: bool = False) -> PurchaseOrder | None:
    stmt = select(PurchaseOrder).where(PurchaseOrder.tenant_id == tenant_id, PurchaseOrder.id == order_id)
    if with_items:
        stmt = stmt.options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.items).selectinload(PurchaseOrderItem.material),
        )
    return db.scalar(stmt)


def get_purchase_order_by_code(db: Session, tenant_id: int, code: str) -> PurchaseOrder | None:
    return db.scalar(select(PurchaseOrder).where(PurchaseOrder.tenant_id == tenant_id, PurchaseOrder.code == code))


def create_purchase_order(
    db: Session,
    tenant_id: int,
    supplier_id: int,
    code: str | None,
    remark: str | None,
    created_by: int | None,
    items: list[tuple[int, int, float | None, str | None]],
) -> PurchaseOrder:
    from app.services.code_generator import BizType, resolve_code

    po_code = resolve_code(
        db,
        tenant_id=tenant_id,
        biz_type=BizType.PURCHASE_ORDER,
        code=code,
        exists=lambda c: get_purchase_order_by_code(db, tenant_id, c) is not None,
        duplicate_msg="采购单号已存在",
    )
    po = PurchaseOrder(
        tenant_id=tenant_id,
        supplier_id=supplier_id,
        code=po_code,
        status="draft",
        remark=remark,
        created_by=created_by,
    )
    po.items = [
        PurchaseOrderItem(tenant_id=tenant_id, material_id=material_id, qty=qty, received_qty=0, unit_price=unit_price, remark=item_remark)
        for material_id, qty, unit_price, item_remark in items
    ]
    db.add(po)
    db.flush()
    return po


def list_purchase_orders(
    db: Session,
    tenant_id: int,
    keyword: str | None = None,
    supplier_id: int | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[PurchaseOrder]:
    stmt = select(PurchaseOrder).where(PurchaseOrder.tenant_id == tenant_id)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(or_(PurchaseOrder.code.like(kw), PurchaseOrder.remark.like(kw)))
    if supplier_id is not None:
        stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
    if status:
        stmt = stmt.where(PurchaseOrder.status == status)
    stmt = stmt.options(selectinload(PurchaseOrder.supplier)).order_by(PurchaseOrder.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def confirm_purchase_order(db: Session, po: PurchaseOrder, confirmer_user_id: int) -> PurchaseOrder:
    if po.status != "draft":
        raise ValueError("采购单状态不允许确认")
    po.status = "confirmed"
    po.confirmed_at = datetime.now()
    po.confirmed_by = confirmer_user_id
    db.flush()
    return po


def sum_purchase_order_qty(db: Session, tenant_id: int, order_id: int) -> int:
    v = db.scalar(select(func.sum(PurchaseOrderItem.qty)).where(PurchaseOrderItem.tenant_id == tenant_id, PurchaseOrderItem.order_id == order_id))
    return int(v or 0)
