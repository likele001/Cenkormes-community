from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.material_issue import MaterialIssue, MaterialIssueItem, MaterialReturn, MaterialReturnItem
from app.models.material import Material
from app.models.sku import Sku
from app.crud.warehouse import adjust_stock


def get_issue_by_id(db: Session, tenant_id: int, issue_id: int) -> MaterialIssue | None:
    return db.scalar(
        select(MaterialIssue)
        .where(MaterialIssue.id == issue_id, MaterialIssue.tenant_id == tenant_id)
        .options(
            selectinload(MaterialIssue.items).selectinload(MaterialIssueItem.material),
            selectinload(MaterialIssue.items).selectinload(MaterialIssueItem.sku),
            selectinload(MaterialIssue.warehouse),
            selectinload(MaterialIssue.work_order),
        )
    )


def list_issues(
    db: Session,
    tenant_id: int,
    warehouse_id: int | None = None,
    work_order_id: int | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[MaterialIssue]:
    stmt = select(MaterialIssue).options(
        selectinload(MaterialIssue.warehouse),
        selectinload(MaterialIssue.work_order),
    ).where(MaterialIssue.tenant_id == tenant_id)
    if warehouse_id is not None:
        stmt = stmt.where(MaterialIssue.warehouse_id == warehouse_id)
    if work_order_id is not None:
        stmt = stmt.where(MaterialIssue.work_order_id == work_order_id)
    if status:
        stmt = stmt.where(MaterialIssue.status == status)
    stmt = stmt.order_by(MaterialIssue.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def _resolve_cost(db: Session, tenant_id: int, sku_id: int) -> Decimal:
    cost = Decimal("0")
    if sku_id:
        sku = db.scalar(select(Sku).where(Sku.id == sku_id, Sku.tenant_id == tenant_id))
        if sku and sku.cost_price:
            cost = Decimal(str(sku.cost_price))
    return cost


def create_issue(
    db: Session,
    tenant_id: int,
    code: str,
    warehouse_id: int,
    items: list[dict],
    work_order_id: int | None = None,
    remark: str | None = None,
    created_by: int | None = None,
) -> MaterialIssue:
    issue = MaterialIssue(tenant_id=tenant_id, code=code, warehouse_id=warehouse_id,
                          work_order_id=work_order_id, remark=remark, created_by=created_by)
    issue_items = []
    total_qty = 0
    total_cost = Decimal("0")
    for it in items:
        material_id = it["material_id"]
        sku_id = it["sku_id"]
        qty = int(it["qty"])
        unit_cost = _resolve_cost(db, tenant_id, sku_id)
        total_qty += qty
        total_cost += unit_cost * qty
        issue_items.append(MaterialIssueItem(
            tenant_id=tenant_id, material_id=material_id, sku_id=sku_id,
            qty=qty, unit_cost=unit_cost, cost_amount=unit_cost * qty,
        ))
    issue.items = issue_items
    issue.total_qty = total_qty
    issue.total_cost = total_cost
    db.add(issue)
    db.flush()
    return issue


def issue_materials(db: Session, issue: MaterialIssue, issued_by: int | None = None) -> MaterialIssue:
    if issue.status != "draft":
        raise ValueError(f"领料单 {issue.code} 状态不允许领料")
    for it in issue.items:
        adjust_stock(
            db,
            tenant_id=issue.tenant_id,
            warehouse_id=issue.warehouse_id,
            sku_id=it.sku_id,
            change_qty=-it.qty,
            biz_type="material_issue",
            biz_id=issue.id,
            remark=f"领料单{issue.code}",
        )
    issue.status = "issued"
    issue.issued_at = datetime.now()
    issue.issue_by = issued_by
    db.flush()
    return issue


def cancel_issue(db: Session, issue: MaterialIssue) -> MaterialIssue:
    if issue.status != "draft":
        raise ValueError(f"领料单 {issue.code} 状态不允许取消")
    issue.status = "cancelled"
    db.flush()
    return issue


# ── 退料 ──

def get_return_by_id(db: Session, tenant_id: int, return_id: int) -> MaterialReturn | None:
    return db.scalar(
        select(MaterialReturn)
        .where(MaterialReturn.id == return_id, MaterialReturn.tenant_id == tenant_id)
        .options(
            selectinload(MaterialReturn.items).selectinload(MaterialReturnItem.material),
            selectinload(MaterialReturn.items).selectinload(MaterialReturnItem.sku),
            selectinload(MaterialReturn.warehouse),
            selectinload(MaterialReturn.work_order),
            selectinload(MaterialReturn.issue),
        )
    )


def list_returns(
    db: Session,
    tenant_id: int,
    warehouse_id: int | None = None,
    work_order_id: int | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[MaterialReturn]:
    stmt = select(MaterialReturn).options(
        selectinload(MaterialReturn.warehouse),
        selectinload(MaterialReturn.work_order),
    ).where(MaterialReturn.tenant_id == tenant_id)
    if warehouse_id is not None:
        stmt = stmt.where(MaterialReturn.warehouse_id == warehouse_id)
    if work_order_id is not None:
        stmt = stmt.where(MaterialReturn.work_order_id == work_order_id)
    if status:
        stmt = stmt.where(MaterialReturn.status == status)
    stmt = stmt.order_by(MaterialReturn.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def create_return(
    db: Session,
    tenant_id: int,
    code: str,
    warehouse_id: int,
    items: list[dict],
    work_order_id: int | None = None,
    issue_id: int | None = None,
    remark: str | None = None,
    created_by: int | None = None,
) -> MaterialReturn:
    ret = MaterialReturn(tenant_id=tenant_id, code=code, warehouse_id=warehouse_id,
                         work_order_id=work_order_id, issue_id=issue_id, remark=remark, created_by=created_by)
    ret_items = []
    total_qty = 0
    total_cost = Decimal("0")
    for it in items:
        material_id = it["material_id"]
        sku_id = it["sku_id"]
        qty = int(it["qty"])
        unit_cost = _resolve_cost(db, tenant_id, sku_id)
        total_qty += qty
        total_cost += unit_cost * qty
        ret_items.append(MaterialReturnItem(
            tenant_id=tenant_id, issue_item_id=it.get("issue_item_id"),
            material_id=material_id, sku_id=sku_id,
            qty=qty, unit_cost=unit_cost, cost_amount=unit_cost * qty,
        ))
    ret.items = ret_items
    ret.total_qty = total_qty
    ret.total_cost = total_cost
    db.add(ret)
    db.flush()
    return ret


def confirm_return(db: Session, ret: MaterialReturn, returned_by: int | None = None) -> MaterialReturn:
    if ret.status != "draft":
        raise ValueError(f"退料单 {ret.code} 状态不允许退料")
    for it in ret.items:
        adjust_stock(
            db,
            tenant_id=ret.tenant_id,
            warehouse_id=ret.warehouse_id,
            sku_id=it.sku_id,
            change_qty=it.qty,
            biz_type="material_return",
            biz_id=ret.id,
            remark=f"退料单{ret.code}",
        )
    ret.status = "returned"
    ret.returned_at = datetime.now()
    ret.return_by = returned_by
    db.flush()
    return ret


def cancel_return(db: Session, ret: MaterialReturn) -> MaterialReturn:
    if ret.status != "draft":
        raise ValueError(f"退料单 {ret.code} 状态不允许取消")
    ret.status = "cancelled"
    db.flush()
    return ret
