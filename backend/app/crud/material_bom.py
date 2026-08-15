from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.material import (
    BOM_SCOPE_GLOBAL,
    BOM_SCOPE_PRODUCT,
    BOM_SCOPE_SKU,
    MaterialBom,
    MaterialBomItem,
)

__all__ = [
    "BOM_SCOPE_GLOBAL",
    "BOM_SCOPE_PRODUCT",
    "BOM_SCOPE_SKU",
    "get_bom_by_id",
    "get_bom_by_sku_id",
    "get_effective_bom_for_sku",
    "get_effective_bom_map_by_sku_ids",
    "get_boms_by_sku_ids",
    "get_global_default_bom",
    "get_product_bom",
    "get_sku_bom",
    "list_boms",
    "create_bom",
    "copy_bom_to_sku",
    "update_bom",
]
from app.models.sku import Sku


def _bom_options():
    return (
        selectinload(MaterialBom.sku),
        selectinload(MaterialBom.product),
        selectinload(MaterialBom.items).selectinload(MaterialBomItem.material),
    )


def get_bom_by_id(db: Session, tenant_id: int, bom_id: int) -> MaterialBom | None:
    return db.scalar(
        select(MaterialBom)
        .where(MaterialBom.tenant_id == tenant_id, MaterialBom.id == bom_id)
        .options(*_bom_options())
    )


def get_sku_bom(db: Session, tenant_id: int, sku_id: int) -> MaterialBom | None:
    """型号专属 BOM（scope=sku）。"""
    return db.scalar(
        select(MaterialBom)
        .where(
            MaterialBom.tenant_id == tenant_id,
            MaterialBom.scope == BOM_SCOPE_SKU,
            MaterialBom.sku_id == sku_id,
            MaterialBom.is_active.is_(True),
        )
        .options(*_bom_options())
    )


def get_bom_by_sku_id(db: Session, tenant_id: int, sku_id: int) -> MaterialBom | None:
    """兼容旧名：返回型号生效 BOM（含继承）。"""
    return get_effective_bom_for_sku(db, tenant_id, sku_id)[0]


def get_product_bom(db: Session, tenant_id: int, product_id: int) -> MaterialBom | None:
    return db.scalar(
        select(MaterialBom)
        .where(
            MaterialBom.tenant_id == tenant_id,
            MaterialBom.scope == BOM_SCOPE_PRODUCT,
            MaterialBom.product_id == product_id,
            MaterialBom.is_active.is_(True),
        )
        .options(*_bom_options())
    )


def get_global_default_bom(db: Session, tenant_id: int) -> MaterialBom | None:
    return db.scalar(
        select(MaterialBom)
        .where(
            MaterialBom.tenant_id == tenant_id,
            MaterialBom.scope == BOM_SCOPE_GLOBAL,
            MaterialBom.is_default.is_(True),
            MaterialBom.is_active.is_(True),
        )
        .options(*_bom_options())
    )


def get_effective_bom_for_sku(db: Session, tenant_id: int, sku_id: int) -> tuple[MaterialBom | None, str]:
    """
    解析型号生效 BOM，优先级：型号专属 > 产品默认 > 全厂默认。
    返回 (bom, source)，source 为 sku / product / global / none。
    """
    sku_bom = get_sku_bom(db, tenant_id, sku_id)
    if sku_bom:
        return sku_bom, BOM_SCOPE_SKU

    sku = db.get(Sku, sku_id)
    if sku and sku.tenant_id == tenant_id:
        product_bom = get_product_bom(db, tenant_id, sku.product_id)
        if product_bom:
            return product_bom, BOM_SCOPE_PRODUCT

    global_bom = get_global_default_bom(db, tenant_id)
    if global_bom:
        return global_bom, BOM_SCOPE_GLOBAL

    return None, "none"


def get_effective_bom_map_by_sku_ids(db: Session, tenant_id: int, sku_ids: list[int]) -> dict[int, MaterialBom]:
    out: dict[int, MaterialBom] = {}
    for sid in sku_ids:
        bom, source = get_effective_bom_for_sku(db, tenant_id, sid)
        if bom:
            out[sid] = bom
    return out


def get_boms_by_sku_ids(db: Session, tenant_id: int, sku_ids: list[int]) -> list[MaterialBom]:
    """兼容：按型号返回生效 BOM 列表（去重）。"""
    m = get_effective_bom_map_by_sku_ids(db, tenant_id, sku_ids)
    seen: set[int] = set()
    result: list[MaterialBom] = []
    for bom in m.values():
        if bom.id not in seen:
            seen.add(bom.id)
            result.append(bom)
    return result


def list_boms(
    db: Session,
    tenant_id: int,
    keyword: str | None = None,
    sku_id: int | None = None,
    product_id: int | None = None,
    scope: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[MaterialBom]:
    stmt = (
        select(MaterialBom)
        .where(MaterialBom.tenant_id == tenant_id, MaterialBom.is_active.is_(True))
        .options(selectinload(MaterialBom.sku), selectinload(MaterialBom.product))
        .order_by(MaterialBom.scope.asc(), MaterialBom.id.desc())
        .offset(offset)
        .limit(limit)
    )
    if scope:
        stmt = stmt.where(MaterialBom.scope == scope)
    if sku_id is not None:
        stmt = stmt.where(MaterialBom.sku_id == sku_id)
    if product_id is not None:
        stmt = stmt.where(MaterialBom.product_id == product_id)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.outerjoin(Sku, Sku.id == MaterialBom.sku_id).where(
            or_(
                MaterialBom.name.like(kw),
                MaterialBom.remark.like(kw),
                Sku.code.like(kw),
                Sku.name.like(kw),
            )
        )
    return db.scalars(stmt).all()


def _validate_scope_fields(scope: str, product_id: int | None, sku_id: int | None, is_default: bool) -> None:
    if scope == BOM_SCOPE_SKU:
        if not sku_id:
            raise ValueError("型号 BOM 必须选择型号")
        return
    if scope == BOM_SCOPE_PRODUCT:
        if not product_id:
            raise ValueError("产品默认 BOM 必须选择产品")
        if sku_id:
            raise ValueError("产品默认 BOM 不能绑定型号")
        return
    if scope == BOM_SCOPE_GLOBAL:
        if product_id or sku_id:
            raise ValueError("全厂默认 BOM 不能绑定产品或型号")
        if not is_default:
            raise ValueError("全厂默认 BOM 须勾选为默认模板")
        return
    raise ValueError("无效的 BOM 作用域")


def _assert_unique_scope(db: Session, tenant_id: int, scope: str, product_id: int | None, sku_id: int | None, exclude_id: int | None = None) -> None:
    stmt = select(MaterialBom.id).where(MaterialBom.tenant_id == tenant_id, MaterialBom.scope == scope, MaterialBom.is_active.is_(True))
    if exclude_id:
        stmt = stmt.where(MaterialBom.id != exclude_id)
    if scope == BOM_SCOPE_SKU and sku_id:
        stmt = stmt.where(MaterialBom.sku_id == sku_id)
    elif scope == BOM_SCOPE_PRODUCT and product_id:
        stmt = stmt.where(MaterialBom.product_id == product_id)
    elif scope == BOM_SCOPE_GLOBAL:
        stmt = stmt.where(MaterialBom.is_default.is_(True))
    if db.scalar(stmt):
        if scope == BOM_SCOPE_SKU:
            raise ValueError("该型号已有专属 BOM")
        if scope == BOM_SCOPE_PRODUCT:
            raise ValueError("该产品已有默认 BOM")
        raise ValueError("全厂默认 BOM 已存在，请先停用旧的")


def create_bom(
    db: Session,
    tenant_id: int,
    scope: str,
    version: int,
    remark: str | None,
    created_by: int | None,
    items: list[tuple[int, int, str | None]],
    *,
    sku_id: int | None = None,
    product_id: int | None = None,
    name: str | None = None,
    is_default: bool = False,
) -> MaterialBom:
    _validate_scope_fields(scope, product_id, sku_id, is_default)
    _assert_unique_scope(db, tenant_id, scope, product_id, sku_id)

    if scope == BOM_SCOPE_SKU and sku_id:
        sku = db.get(Sku, sku_id)
        if not sku or sku.tenant_id != tenant_id:
            raise ValueError("产品型号不存在")
        product_id = sku.product_id

    if scope == BOM_SCOPE_GLOBAL:
        for old in db.scalars(
            select(MaterialBom).where(
                MaterialBom.tenant_id == tenant_id,
                MaterialBom.scope == BOM_SCOPE_GLOBAL,
                MaterialBom.is_default.is_(True),
                MaterialBom.is_active.is_(True),
            )
        ).all():
            old.is_default = False

    bom = MaterialBom(
        tenant_id=tenant_id,
        scope=scope,
        product_id=product_id,
        sku_id=sku_id if scope == BOM_SCOPE_SKU else None,
        name=name,
        version=version,
        remark=remark,
        is_default=is_default if scope == BOM_SCOPE_GLOBAL else False,
        is_active=True,
        created_by=created_by,
    )
    bom.items = [
        MaterialBomItem(tenant_id=tenant_id, material_id=material_id, qty_per=qty_per, remark=item_remark)
        for material_id, qty_per, item_remark in items
    ]
    db.add(bom)
    db.flush()
    return bom


def copy_bom_to_sku(db: Session, tenant_id: int, source_bom: MaterialBom, target_sku_id: int, created_by: int | None) -> MaterialBom:
    """将模板/产品默认 BOM 复制为某型号专属 BOM。"""
    if get_sku_bom(db, tenant_id, target_sku_id):
        raise ValueError("该型号已有专属 BOM，请先停用或编辑")
    sku = db.get(Sku, target_sku_id)
    if not sku or sku.tenant_id != tenant_id:
        raise ValueError("产品型号不存在")
    items = [(bi.material_id, bi.qty_per, bi.remark) for bi in (source_bom.items or [])]
    return create_bom(
        db,
        tenant_id=tenant_id,
        scope=BOM_SCOPE_SKU,
        sku_id=target_sku_id,
        product_id=sku.product_id,
        version=source_bom.version,
        name=None,
        remark=f"从 BOM#{source_bom.id} 复制",
        is_default=False,
        created_by=created_by,
        items=items,
    )


def update_bom(
    db: Session,
    bom: MaterialBom,
    version: int | None = None,
    remark: str | None = None,
    name: str | None = None,
    is_active: bool | None = None,
    is_default: bool | None = None,
    items: list[tuple[int, int, str | None]] | None = None,
) -> MaterialBom:
    if version is not None:
        bom.version = version
    if remark is not None:
        bom.remark = remark
    if name is not None:
        bom.name = name
    if is_active is not None:
        bom.is_active = is_active
    if is_default is not None and bom.scope == BOM_SCOPE_GLOBAL:
        if is_default:
            for old in db.scalars(
                select(MaterialBom).where(
                    MaterialBom.tenant_id == bom.tenant_id,
                    MaterialBom.scope == BOM_SCOPE_GLOBAL,
                    MaterialBom.is_default.is_(True),
                    MaterialBom.is_active.is_(True),
                    MaterialBom.id != bom.id,
                )
            ).all():
                old.is_default = False
        bom.is_default = is_default
    if items is not None:
        bom.items = [
            MaterialBomItem(tenant_id=bom.tenant_id, material_id=material_id, qty_per=qty_per, remark=item_remark)
            for material_id, qty_per, item_remark in items
        ]
    db.flush()
    return bom
