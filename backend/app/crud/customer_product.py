from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.customer_product import CustomerProduct
from app.models.product import Product


def list_customer_product_ids(db: Session, tenant_id: int, customer_id: int) -> list[int]:
    rows = db.scalars(
        select(CustomerProduct.product_id)
        .where(CustomerProduct.tenant_id == tenant_id, CustomerProduct.customer_id == customer_id)
        .order_by(CustomerProduct.product_id.asc())
    ).all()
    return list(rows)


def list_customer_products_with_detail(db: Session, tenant_id: int, customer_id: int) -> list[Product]:
    ids = list_customer_product_ids(db, tenant_id, customer_id)
    if not ids:
        return []
    return db.scalars(
        select(Product)
        .where(Product.tenant_id == tenant_id, Product.id.in_(ids), Product.is_active.is_(True))
        .order_by(Product.id.asc())
    ).all()


def set_customer_products(db: Session, tenant_id: int, customer_id: int, product_ids: list[int]) -> list[int]:
    db.execute(
        delete(CustomerProduct).where(
            CustomerProduct.tenant_id == tenant_id,
            CustomerProduct.customer_id == customer_id,
        )
    )
    seen: set[int] = set()
    for pid in product_ids:
        if pid in seen:
            continue
        seen.add(pid)
        prod = db.scalar(select(Product).where(Product.tenant_id == tenant_id, Product.id == pid, Product.is_active.is_(True)))
        if not prod:
            continue
        db.add(CustomerProduct(tenant_id=tenant_id, customer_id=customer_id, product_id=pid))
    db.flush()
    return list_customer_product_ids(db, tenant_id, customer_id)
