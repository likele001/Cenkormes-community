from io import BytesIO

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.crud.customer import get_customer_by_id, list_customers
from app.crud.notification import create_notification
from app.crud.order import (
    confirm_order,
    create_order,
    get_order_by_code,
    get_order_by_id,
    get_order_item_lock_info,
    list_orders,
    order_has_active_production_plan,
    order_has_work_orders,
    order_is_production_locked,
    reject_order,
    update_order,
    update_order_items,
)
from app.crud.sku import get_sku_by_id, list_skus
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.services.display_label import order_sku_option_label
from app.schemas.order import OrderCreateIn, OrderUpdateIn
from app.services.code_generator import BizType, resolve_code
router = APIRouter(dependencies=[Depends(require_permissions(["order.manage"]))])


def _sku_ref_out(sku) -> dict:
    product = sku.product if hasattr(sku, "product") and sku.product else None
    pn, sm, _ = order_sku_option_label(
        product_name=product.name if product else None,
        product_description=product.description if product else None,
        product_code=product.code if product else None,
        product_category=product.category if product else None,
        sku_name=sku.name,
        sku_code=sku.code,
        sku_color=sku.color,
        sku_material=sku.material,
        sku_spec=sku.spec,
    )
    return {
        "id": sku.id,
        "code": sku.code,
        "name": sku.name,
        "product_id": sku.product_id,
        "product_name": pn,
        "sku_name": sm,
        "display_label": f"{pn} · {sm}" if pn else sm,
    }


def _item_out(x, order=None, db: Session | None = None, tenant_id: int | None = None) -> dict:
    sku = x.sku if hasattr(x, "sku") else None
    out = {
        "id": x.id,
        "tenant_id": x.tenant_id,
        "order_id": x.order_id,
        "line_no": x.line_no,
        "sku_id": x.sku_id,
        "qty": x.qty,
        "remark": x.remark,
        "created_at": x.created_at,
        "updated_at": x.updated_at,
        "sku": _sku_ref_out(sku) if sku else None,
        "locked": False,
        "lock_reason": None,
    }
    if order is not None and db is not None and tenant_id is not None:
        lock = get_order_item_lock_info(db, tenant_id, order, x)
        out["locked"] = lock["locked"]
        out["lock_reason"] = lock["lock_reason"]
    return out


def _order_detail_out(db: Session, tenant_id: int, order) -> dict:
    data = _out(order)
    data["order_plan_locked"] = order_has_active_production_plan(db, tenant_id, order.id) if order.status != "draft" else False
    data["order_production_locked"] = order_is_production_locked(db, tenant_id, order.id) if order.status != "draft" else False
    data["has_work_orders"] = order_has_work_orders(db, tenant_id, order.id)
    data["items"] = [_item_out(x, order=order, db=db, tenant_id=tenant_id) for x in order.items]
    return data


def _out(x) -> dict:
    cust = x.customer if hasattr(x, "customer") else None
    opp = x.opportunity if hasattr(x, "opportunity") else None
    return {
        "id": x.id,
        "tenant_id": x.tenant_id,
        "customer_id": x.customer_id,
        "opportunity_id": getattr(x, "opportunity_id", None),
        "opportunity_code": opp.code if opp else None,
        "code": x.code,
        "status": x.status,
        "due_date": x.due_date,
        "remark": x.remark,
        "confirmed_at": x.confirmed_at,
        "confirmed_by": x.confirmed_by,
        "created_at": x.created_at,
        "updated_at": x.updated_at,
        "customer": {"id": cust.id, "name": cust.name, "code": cust.code} if cust else None,
    }


@router.get("")
def list_api(
    keyword: str | None = Query(default=None),
    customer_id: int | None = Query(default=None, ge=1),
    opportunity_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if customer_id is not None:
        c = get_customer_by_id(db, tenant_id=user.tenant_id, customer_id=customer_id)
        if not c:
            raise HTTPException(status_code=400, detail="客户不存在")
    items = list_orders(
        db,
        tenant_id=user.tenant_id,
        keyword=keyword,
        customer_id=customer_id,
        opportunity_id=opportunity_id,
        status=status,
        offset=offset,
        limit=limit,
    )
    return ok({"items": [_out(x) for x in items]})


@router.get("/meta/form-options")
def create_form_options_api(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """新建订单下拉：仅需 order.manage。路径使用 /meta/ 前缀，避免与 /{order_id} 整数路径冲突。"""
    customers = list_customers(db, tenant_id=user.tenant_id, keyword=None, offset=0, limit=200, include_inactive=False)
    skus = list_skus(
        db,
        tenant_id=user.tenant_id,
        product_id=None,
        keyword=None,
        offset=0,
        limit=200,
        include_inactive=False,
        finished_products_only=True,
    )
    product_ids = {s.product_id for s in skus}
    product_map: dict[int, Product] = {}
    if product_ids:
        products = db.scalars(
            select(Product).where(Product.tenant_id == user.tenant_id, Product.id.in_(product_ids))
        ).all()
        product_map = {p.id: p for p in products}
    sku_options = []
    for s in skus:
        p = product_map.get(s.product_id)
        pn, sm, label = order_sku_option_label(
            product_name=p.name if p else None,
            product_description=p.description if p else None,
            product_code=p.code if p else None,
            product_category=p.category if p else None,
            sku_name=s.name,
            sku_code=s.code,
            sku_color=s.color,
            sku_material=s.material,
            sku_spec=s.spec,
        )
        sku_options.append(
            {
                "id": s.id,
                "code": s.code,
                "product_id": s.product_id,
                "product_name": pn,
                "sku_name": sm,
                "display_label": label,
            }
        )
    return ok(
        {
            "customers": [{"id": c.id, "code": c.code, "name": c.name} for c in customers],
            "skus": sku_options,
        }
    )


@router.get("/{order_id}")
def get_api(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = get_order_by_id(db, tenant_id=user.tenant_id, order_id=order_id, with_items=True)
    if not item:
        raise HTTPException(status_code=400, detail="订单不存在")
    return ok(_order_detail_out(db, user.tenant_id, item))


@router.post("")
def create_api(
    payload: OrderCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = get_customer_by_id(db, tenant_id=user.tenant_id, customer_id=payload.customer_id)
    if not c:
        raise HTTPException(status_code=400, detail="客户不存在")
    order_code = resolve_code(
        db,
        tenant_id=user.tenant_id,
        biz_type=BizType.ORDER,
        code=payload.code,
        exists=lambda c: get_order_by_code(db, user.tenant_id, c) is not None,
        duplicate_msg="订单号已存在",
    )

    seen_line_no: set[int] = set()
    items: list[tuple[int, int, int, str | None]] = []
    for it in payload.items:
        if it.line_no in seen_line_no:
            raise HTTPException(status_code=400, detail="订单明细行号重复")
        seen_line_no.add(it.line_no)
        sku = get_sku_by_id(db, tenant_id=user.tenant_id, sku_id=it.sku_id)
        if not sku:
            raise HTTPException(status_code=400, detail="产品型号不存在")
        if not sku.is_active:
            raise HTTPException(status_code=400, detail="产品型号已停用")
        items.append((it.line_no, it.sku_id, it.qty, it.remark))

    if payload.opportunity_id is not None:
        raise HTTPException(status_code=400, detail="社区版不支持关联销售机会，请升级 Pro")

    order = create_order(
        db,
        tenant_id=user.tenant_id,
        customer_id=payload.customer_id,
        code=order_code,
        due_date=payload.due_date,
        remark=payload.remark,
        items=items,
        opportunity_id=None,
    )
    db.commit()
    item = get_order_by_id(db, tenant_id=user.tenant_id, order_id=order.id, with_items=True)
    if not item:
        raise HTTPException(status_code=500, detail="创建失败")
    return ok(_order_detail_out(db, user.tenant_id, item))


@router.put("/{order_id}")
def update_api(
    order_id: int,
    payload: OrderUpdateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = get_order_by_id(db, tenant_id=user.tenant_id, order_id=order_id, with_items=True)
    if not order:
        raise HTTPException(status_code=400, detail="订单不存在")
    if order.status != "draft":
        if payload.customer_id is not None or payload.code is not None or payload.due_date is not None or payload.status is not None:
            raise HTTPException(status_code=400, detail="非草稿订单不允许修改关键信息")
    if payload.customer_id is not None:
        c = get_customer_by_id(db, tenant_id=user.tenant_id, customer_id=payload.customer_id)
        if not c:
            raise HTTPException(status_code=400, detail="客户不存在")
    if payload.code is not None and payload.code != order.code:
        exists = get_order_by_code(db, tenant_id=user.tenant_id, code=payload.code)
        if exists and exists.id != order.id:
            raise HTTPException(status_code=400, detail="订单号已存在")
    update_order(
        db,
        order=order,
        customer_id=payload.customer_id if order.status == "draft" else None,
        code=payload.code if order.status == "draft" else None,
        due_date=payload.due_date if order.status == "draft" else None,
        remark=payload.remark,
        status=payload.status if order.status == "draft" else None,
    )
    if payload.items is not None:
        rows: list[tuple[int | None, int, int, int, str | None]] = []
        for it in payload.items:
            rows.append((it.id, it.line_no, it.sku_id, it.qty, it.remark))
        try:
            update_order_items(db, order, rows)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    item = get_order_by_id(db, tenant_id=user.tenant_id, order_id=order_id, with_items=True)
    if not item:
        raise HTTPException(status_code=500, detail="更新失败")
    return ok(_order_detail_out(db, user.tenant_id, item))


@router.post("/{order_id}/reject")
def reject_api(
    order_id: int,
    reason: str = Query(min_length=1, max_length=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.scalar(
        select(Order)
        .where(Order.tenant_id == user.tenant_id, Order.id == order_id)
        .options(selectinload(Order.customer))
    )
    if not order:
        raise HTTPException(status_code=400, detail="订单不存在")
    try:
        reject_order(db, order, reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    cust = order.customer
    if cust and cust.user_id:
        create_notification(
            db,
            tenant_id=user.tenant_id,
            user_id=cust.user_id,
            title="订单已驳回",
            content=f"订单 {order.code} 被驳回：{reason}",
            level="warning",
            biz_type="order",
            biz_id=order.id,
        )
    db.commit()
    return ok({"id": order.id, "status": order.status})


@router.post("/{order_id}/confirm")
def confirm_api(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = get_order_by_id(db, tenant_id=user.tenant_id, order_id=order_id, with_items=False)
    if not order:
        raise HTTPException(status_code=400, detail="订单不存在")
    try:
        confirm_order(db, order=order, confirmer_user_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    order_full = get_order_by_id(db, tenant_id=user.tenant_id, order_id=order.id, with_items=False)
    if order_full:
        cust = order_full.customer
        if cust and cust.user_id:
            create_notification(
                db,
                tenant_id=user.tenant_id,
                user_id=cust.user_id,
                title="订单已确认",
                content=f"您的订单 {order.code} 已确认，进入生产准备",
                level="info",
                biz_type="order",
                biz_id=order.id,
            )
        if cust and getattr(cust, "owner_user_id", None):
            create_notification(
                db,
                tenant_id=user.tenant_id,
                user_id=cust.owner_user_id,
                title="客户订单已确认",
                content=f"订单 {order.code} 已确认生产",
                level="info",
                biz_type="order",
                biz_id=order.id,
            )

    db.commit()
    return ok({
        "order_id": order.id,
        "status": order.status,
        "work_order_count": 0,
        "automation_plan_id": automation_plan_id,
        "automation_pipeline_ran": automation_pipeline_ran,
    })
