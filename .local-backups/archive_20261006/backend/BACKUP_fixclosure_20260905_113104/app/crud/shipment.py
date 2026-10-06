"""发货管理 CRUD"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.shipment import Shipment, ShipmentItem


def list_shipments(db: Session, tenant_id: int, *, order_id: int | None = None,
                   status: str | None = None, offset: int = 0, limit: int = 50) -> list[Shipment]:
    stmt = (
        select(Shipment)
        .where(Shipment.tenant_id == tenant_id)
        .options(selectinload(Shipment.items).selectinload(ShipmentItem.sku),
                 selectinload(Shipment.order))
        .order_by(Shipment.id.desc())
        .offset(offset).limit(limit)
    )
    if order_id:
        stmt = stmt.where(Shipment.order_id == order_id)
    if status:
        stmt = stmt.where(Shipment.status == status)
    return list(db.scalars(stmt).all())


def get_shipment(db: Session, tenant_id: int, shipment_id: int) -> Shipment | None:
    return db.scalar(
        select(Shipment)
        .where(Shipment.tenant_id == tenant_id, Shipment.id == shipment_id)
        .options(selectinload(Shipment.items).selectinload(ShipmentItem.sku),
                 selectinload(Shipment.order))
    )


def create_shipment(db: Session, tenant_id: int, data: dict) -> Shipment:
    items_data = data.pop("items", [])
    s = Shipment(tenant_id=tenant_id, **data)
    db.add(s)
    db.flush()
    for it in items_data:
        db.add(ShipmentItem(tenant_id=tenant_id, shipment_id=s.id, **it))
    db.flush()
    return s


def update_shipment(db: Session, tenant_id: int, shipment_id: int, data: dict) -> Shipment | None:
    s = get_shipment(db, tenant_id, shipment_id)
    if not s:
        return None
    for k, v in data.items():
        if k == "items":
            continue
        setattr(s, k, v)
    if "items" in data:
        from sqlalchemy import delete
        db.execute(delete(ShipmentItem).where(ShipmentItem.shipment_id == s.id))
        db.flush()
        for it in data["items"]:
            db.add(ShipmentItem(tenant_id=tenant_id, shipment_id=s.id, **it))
    db.flush()
    return s
