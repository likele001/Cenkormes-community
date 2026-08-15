from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.sku import Sku
from app.services.sku_scope import apply_finished_product_sku_filter


def get_sku_by_id(db: Session, tenant_id: int, sku_id: int) -> Sku | None:
    return db.scalar(select(Sku).where(Sku.tenant_id == tenant_id, Sku.id == sku_id))


def get_sku_by_code(db: Session, tenant_id: int, code: str) -> Sku | None:
    return db.scalar(select(Sku).where(Sku.tenant_id == tenant_id, Sku.code == code))


def _norm_attr(value: str | None) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def find_sku_by_attrs(
    db: Session,
    tenant_id: int,
    product_id: int,
    name: str,
    color: str | None = None,
    material: str | None = None,
    spec: str | None = None,
) -> Sku | None:
    """同产品下按名称+颜色/材料/规格精确匹配（空值归一化为 None）。"""
    nc = _norm_attr(color)
    nm = _norm_attr(material)
    ns = _norm_attr(spec)
    stmt = select(Sku).where(
        Sku.tenant_id == tenant_id,
        Sku.product_id == product_id,
        Sku.name == name.strip(),
        Sku.is_active.is_(True),
    )
    items = db.scalars(stmt).all()
    for item in items:
        if _norm_attr(item.color) == nc and _norm_attr(item.material) == nm and _norm_attr(item.spec) == ns:
            return item
    return None


def list_skus(
    db: Session,
    tenant_id: int,
    product_id: int | None = None,
    keyword: str | None = None,
    offset: int = 0,
    limit: int = 50,
    include_inactive: bool = False,
    *,
    finished_products_only: bool = False,
) -> list[Sku]:
    stmt = select(Sku).where(Sku.tenant_id == tenant_id)
    if finished_products_only:
        stmt = apply_finished_product_sku_filter(stmt, tenant_id)
    if product_id is not None:
        stmt = stmt.where(Sku.product_id == product_id)
    if not include_inactive:
        stmt = stmt.where(Sku.is_active.is_(True))
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(or_(Sku.code.like(kw), Sku.name.like(kw)))
    stmt = stmt.order_by(Sku.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def create_sku(
    db: Session,
    tenant_id: int,
    product_id: int,
    code: str,
    name: str,
    color: str | None,
    material: str | None,
    spec: str | None,
    remark: str | None,
    is_active: bool,
) -> Sku:
    item = Sku(
        tenant_id=tenant_id,
        product_id=product_id,
        code=code,
        name=name,
        color=color,
        material=material,
        spec=spec,
        remark=remark,
        is_active=is_active,
    )
    db.add(item)
    db.flush()
    return item


def update_sku(
    db: Session,
    item: Sku,
    product_id: int | None = None,
    code: str | None = None,
    name: str | None = None,
    color: str | None = None,
    material: str | None = None,
    spec: str | None = None,
    remark: str | None = None,
    is_active: bool | None = None,
    cost_price: float | None = None,
) -> Sku:
    if product_id is not None:
        item.product_id = product_id
    if code is not None:
        item.code = code
    if name is not None:
        item.name = name
    if color is not None:
        item.color = color
    if material is not None:
        item.material = material
    if spec is not None:
        item.spec = spec
    if remark is not None:
        item.remark = remark
    if is_active is not None:
        item.is_active = is_active
    if cost_price is not None:
        item.cost_price = cost_price
    db.flush()
    return item
