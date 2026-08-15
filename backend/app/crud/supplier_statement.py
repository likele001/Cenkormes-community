from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.crud.finance_ledger import create_ledger
from app.models.material import Material
from app.models.purchase import PurchaseOrder, PurchaseOrderItem
from app.models.supplier_statement import SupplierStatement, SupplierStatementItem
from app.models.warehouse import StockLog


def get_supplier_statement_by_id(db: Session, tenant_id: int, statement_id: int, with_items: bool = False) -> SupplierStatement | None:
    stmt = select(SupplierStatement).where(SupplierStatement.tenant_id == tenant_id, SupplierStatement.id == statement_id)
    if with_items:
        stmt = stmt.options(
            selectinload(SupplierStatement.supplier),
            selectinload(SupplierStatement.items).selectinload(SupplierStatementItem.purchase_order),
        )
    return db.scalar(stmt)


def get_supplier_statement_by_code(db: Session, tenant_id: int, code: str) -> SupplierStatement | None:
    return db.scalar(select(SupplierStatement).where(SupplierStatement.tenant_id == tenant_id, SupplierStatement.code == code))


def list_supplier_statements(
    db: Session,
    tenant_id: int,
    keyword: str | None = None,
    supplier_id: int | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[SupplierStatement]:
    stmt = select(SupplierStatement).where(SupplierStatement.tenant_id == tenant_id)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(or_(SupplierStatement.code.like(kw)))
    if supplier_id is not None:
        stmt = stmt.where(SupplierStatement.supplier_id == supplier_id)
    if status:
        stmt = stmt.where(SupplierStatement.status == status)
    stmt = stmt.options(selectinload(SupplierStatement.supplier)).order_by(SupplierStatement.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def _calc_inbound_summary(
    db: Session,
    tenant_id: int,
    supplier_id: int,
    period_from: date | None,
    period_to: date | None,
) -> list[tuple[int, int, Decimal]]:
    from_dt = datetime.combine(period_from, time.min) if period_from else None
    to_dt = datetime.combine(period_to + timedelta(days=1), time.min) if period_to else None

    stmt = (
        select(
            StockLog.biz_id.label("purchase_order_id"),
            StockLog.sku_id.label("sku_id"),
            func.sum(StockLog.change_qty).label("qty"),
        )
        .join(PurchaseOrder, PurchaseOrder.id == StockLog.biz_id)
        .where(
            StockLog.tenant_id == tenant_id,
            StockLog.biz_type == "purchase_in",
            StockLog.change_qty > 0,
            StockLog.biz_id.is_not(None),
            PurchaseOrder.tenant_id == tenant_id,
            PurchaseOrder.supplier_id == supplier_id,
        )
        .group_by(StockLog.biz_id, StockLog.sku_id)
    )
    if from_dt:
        stmt = stmt.where(StockLog.created_at >= from_dt)
    if to_dt:
        stmt = stmt.where(StockLog.created_at < to_dt)

    rows = db.execute(stmt).all()
    if not rows:
        return []

    order_ids = sorted({int(r.purchase_order_id) for r in rows if r.purchase_order_id is not None})
    price_rows = db.execute(
        select(PurchaseOrderItem.order_id, Material.sku_id, PurchaseOrderItem.unit_price)
        .join(Material, Material.id == PurchaseOrderItem.material_id)
        .where(PurchaseOrderItem.tenant_id == tenant_id, PurchaseOrderItem.order_id.in_(order_ids))
    ).all()
    price_map: dict[tuple[int, int], Decimal | None] = {(int(r.order_id), int(r.sku_id)): r.unit_price for r in price_rows}

    qty_map: dict[int, int] = {}
    amt_map: dict[int, Decimal] = {}
    for r in rows:
        oid = int(r.purchase_order_id)
        sku_id = int(r.sku_id)
        qty = int(r.qty or 0)
        if qty <= 0:
            continue
        unit_price = price_map.get((oid, sku_id), None)
        if unit_price is None:
            raise ValueError(f"采购单 {oid} 存在未设置单价的物料，无法生成对账单")
        qty_map[oid] = qty_map.get(oid, 0) + qty
        amt_map[oid] = amt_map.get(oid, Decimal("0")) + (Decimal(qty) * Decimal(str(unit_price)))

    items = [(oid, qty_map[oid], amt_map[oid]) for oid in qty_map.keys()]
    items.sort(key=lambda x: x[0])
    return items


def create_supplier_statement(
    db: Session,
    tenant_id: int,
    supplier_id: int,
    code: str | None,
    period_from: date | None,
    period_to: date | None,
) -> SupplierStatement:
    from app.services.code_generator import BizType, resolve_code

    stmt_code = resolve_code(
        db,
        tenant_id=tenant_id,
        biz_type=BizType.SUPPLIER_STATEMENT,
        code=code,
        exists=lambda c: get_supplier_statement_by_code(db, tenant_id, c) is not None,
        duplicate_msg="对账单号已存在",
    )

    summary = _calc_inbound_summary(db, tenant_id=tenant_id, supplier_id=supplier_id, period_from=period_from, period_to=period_to)
    if not summary:
        raise ValueError("该期间无入库记录")

    total = sum(amt for _, _, amt in summary)
    stmt = SupplierStatement(
        tenant_id=tenant_id,
        supplier_id=supplier_id,
        code=stmt_code,
        period_from=period_from,
        period_to=period_to,
        amount=total,
        status="draft",
    )
    stmt.items = [
        SupplierStatementItem(tenant_id=tenant_id, purchase_order_id=po_id, received_qty=qty, amount=amt)
        for po_id, qty, amt in summary
    ]
    db.add(stmt)
    db.flush()
    return stmt


def confirm_supplier_statement(db: Session, stmt: SupplierStatement, confirmer_user_id: int) -> SupplierStatement:
    if stmt.status != "draft":
        raise ValueError("状态不允许确认")
    stmt.status = "confirmed"
    stmt.confirmed_at = datetime.now()
    stmt.confirmed_by = confirmer_user_id
    db.flush()
    return stmt


def mark_supplier_statement_paid(db: Session, stmt: SupplierStatement, payer_user_id: int) -> SupplierStatement:
    if stmt.status != "confirmed":
        raise ValueError("状态不允许标记已付款")
    stmt.status = "paid"
    stmt.paid_at = datetime.now()
    stmt.paid_by = payer_user_id
    create_ledger(
        db,
        tenant_id=stmt.tenant_id,
        direction="out",
        category="payment",
        party_type="supplier",
        party_id=stmt.supplier_id,
        statement_type="supplier_statement",
        statement_id=stmt.id,
        amount=stmt.amount,
        biz_date=stmt.paid_at.date(),
        remark=f"供应商对账单{stmt.code}付款",
        created_by=payer_user_id,
    )
    db.flush()
    return stmt
