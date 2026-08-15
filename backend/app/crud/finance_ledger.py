from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.finance_ledger import FinanceLedger


def create_ledger(
    db: Session,
    tenant_id: int,
    direction: str,
    category: str,
    party_type: str,
    party_id: int | None,
    statement_type: str | None,
    statement_id: int | None,
    amount: Decimal,
    biz_date: date,
    remark: str | None,
    created_by: int | None,
) -> FinanceLedger:
    x = FinanceLedger(
        tenant_id=tenant_id,
        direction=direction,
        category=category,
        party_type=party_type,
        party_id=party_id,
        statement_type=statement_type,
        statement_id=statement_id,
        amount=amount,
        biz_date=biz_date,
        remark=remark,
        created_by=created_by,
    )
    db.add(x)
    db.flush()
    return x


def ledger_exists_for_statement(
    db: Session,
    tenant_id: int,
    statement_id: int,
    direction: str,
    category: str,
) -> bool:
    """校验某对账单是否已存在指定方向的流水（防重复记账）。"""
    return (
        db.scalar(
            select(func.count(FinanceLedger.id)).where(
                FinanceLedger.tenant_id == tenant_id,
                FinanceLedger.statement_id == statement_id,
                FinanceLedger.direction == direction,
                FinanceLedger.category == category,
            )
        )
        or 0
    ) > 0


def list_ledgers(
    db: Session,
    tenant_id: int,
    direction: str | None = None,
    category: str | None = None,
    party_type: str | None = None,
    party_id: int | None = None,
    biz_date_from: date | None = None,
    biz_date_to: date | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[FinanceLedger]:
    stmt = select(FinanceLedger).where(FinanceLedger.tenant_id == tenant_id)
    if direction:
        stmt = stmt.where(FinanceLedger.direction == direction)
    if category:
        stmt = stmt.where(FinanceLedger.category == category)
    if party_type:
        stmt = stmt.where(FinanceLedger.party_type == party_type)
    if party_id is not None:
        stmt = stmt.where(FinanceLedger.party_id == party_id)
    if biz_date_from:
        stmt = stmt.where(FinanceLedger.biz_date >= biz_date_from)
    if biz_date_to:
        stmt = stmt.where(FinanceLedger.biz_date <= biz_date_to)
    stmt = stmt.order_by(FinanceLedger.biz_date.desc(), FinanceLedger.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def sum_amount(
    db: Session,
    tenant_id: int,
    direction: str,
    category: str,
    biz_date_from: date,
    biz_date_to_exclusive: date,
) -> Decimal:
    v = db.scalar(
        select(func.coalesce(func.sum(FinanceLedger.amount), 0))
        .where(
            FinanceLedger.tenant_id == tenant_id,
            FinanceLedger.direction == direction,
            FinanceLedger.category == category,
            FinanceLedger.biz_date >= biz_date_from,
            FinanceLedger.biz_date < biz_date_to_exclusive,
        )
    )
    return Decimal(str(v or 0))

