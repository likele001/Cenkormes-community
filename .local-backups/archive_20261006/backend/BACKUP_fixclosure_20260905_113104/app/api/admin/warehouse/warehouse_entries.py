from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.crud.warehouse_entry import (
    cancel_entry,
    confirm_entry,
    create_entry,
    get_entry_by_id,
    list_entries,
)
from app.models.user import User
from app.models.warehouse_entry import WarehouseEntry
from app.services.code_generator import BizType, resolve_code

router = APIRouter(dependencies=[Depends(require_permissions(["warehouse.manage"]))])


class EntryItemIn(BaseModel):
    material_id: int = Field(ge=1)
    sku_id: int = Field(ge=1)
    qty: int = Field(ge=1)


class EntryCreateIn(BaseModel):
    code: str | None = Field(default=None, max_length=64)
    source_type: str = Field(default="other")  # purchase/material_return/other
    warehouse_id: int = Field(ge=1)
    purchase_order_id: int | None = Field(default=None, ge=1)
    material_return_id: int | None = Field(default=None, ge=1)
    remark: str | None = Field(default=None, max_length=255)
    items: list[EntryItemIn] = Field(min_length=1)


def _entry_out(e: WarehouseEntry) -> dict:
    po = e.purchase_order
    mr = e.material_return
    return {
        "id": e.id,
        "code": e.code,
        "status": e.status,
        "source_type": e.source_type,
        "warehouse_id": e.warehouse_id,
        "warehouse_name": e.warehouse.name if e.warehouse else None,
        "purchase_order_id": e.purchase_order_id,
        "purchase_order_code": po.code if po else None,
        "material_return_id": e.material_return_id,
        "material_return_code": mr.code if mr else None,
        "total_qty": e.total_qty,
        "total_cost": float(e.total_cost),
        "confirmed_at": e.confirmed_at.isoformat() if e.confirmed_at else None,
        "remark": e.remark,
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "items": [
            {
                "id": it.id,
                "material_id": it.material_id,
                "material_name": it.material.name if it.material else None,
                "sku_id": it.sku_id,
                "sku_name": it.sku.name if it.sku else None,
                "qty": it.qty,
                "unit_cost": float(it.unit_cost),
                "cost_amount": float(it.cost_amount),
            }
            for it in e.items
        ],
    }


@router.get("/entries")
def api_list_entries(
    warehouse_id: int | None = Query(default=None),
    source_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list_entries(
        db, user.tenant_id,
        warehouse_id=warehouse_id, source_type=source_type, status=status,
        offset=offset, limit=limit,
    )
    return ok({"items": [_entry_out(r) for r in rows]})


@router.get("/entries/{entry_id}")
def api_get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    e = get_entry_by_id(db, user.tenant_id, entry_id)
    if not e:
        raise HTTPException(status_code=404, detail="入库单不存在")
    return ok(_entry_out(e))


@router.post("/entries")
def api_create_entry(
    payload: EntryCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.source_type not in ("purchase", "material_return", "other"):
        raise HTTPException(status_code=400, detail="入库类型不合法")
    if payload.source_type == "purchase" and not payload.purchase_order_id:
        raise HTTPException(status_code=400, detail="采购入库必须关联采购单")
    if payload.source_type == "material_return" and not payload.material_return_id:
        raise HTTPException(status_code=400, detail="退料入库必须关联退料单")

    code = resolve_code(
        db,
        tenant_id=user.tenant_id,
        biz_type=BizType.WAREHOUSE_ENTRY,
        code=payload.code,
        exists=lambda c: db.scalar(
            select(WarehouseEntry.id).where(
                WarehouseEntry.code == c,
                WarehouseEntry.tenant_id == user.tenant_id,
            )
        ) is not None,
        duplicate_msg="入库单号已存在",
    )
    entry = create_entry(
        db,
        tenant_id=user.tenant_id,
        code=code,
        source_type=payload.source_type,
        warehouse_id=payload.warehouse_id,
        items=[{"material_id": i.material_id, "sku_id": i.sku_id, "qty": i.qty} for i in payload.items],
        purchase_order_id=payload.purchase_order_id,
        material_return_id=payload.material_return_id,
        remark=payload.remark,
        created_by=user.id,
    )
    db.commit()
    return ok(_entry_out(entry))


@router.post("/entries/{entry_id}/confirm")
def api_confirm_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    e = get_entry_by_id(db, user.tenant_id, entry_id)
    if not e:
        raise HTTPException(status_code=404, detail="入库单不存在")
    try:
        e = confirm_entry(db, user.tenant_id, e, confirmed_by=user.id)
        db.commit()
    except ValueError as ex:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ex))
    return ok(_entry_out(e))


@router.post("/entries/{entry_id}/cancel")
def api_cancel_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    e = get_entry_by_id(db, user.tenant_id, entry_id)
    if not e:
        raise HTTPException(status_code=404, detail="入库单不存在")
    try:
        e = cancel_entry(db, e)
        db.commit()
    except ValueError as ex:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ex))
    return ok(_entry_out(e))
