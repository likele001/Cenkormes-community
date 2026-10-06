from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant_setting import TenantSetting


def get_setting(db: Session, tenant_id: int, key: str) -> TenantSetting | None:
    return db.scalar(select(TenantSetting).where(TenantSetting.tenant_id == tenant_id, TenantSetting.key == key))


def list_settings(db: Session, tenant_id: int, offset: int = 0, limit: int = 200) -> list[TenantSetting]:
    stmt = select(TenantSetting).where(TenantSetting.tenant_id == tenant_id).order_by(TenantSetting.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def upsert_setting(db: Session, tenant_id: int, key: str, value: str | None) -> TenantSetting:
    item = get_setting(db, tenant_id, key)
    if item:
        item.value = value
        db.flush()
        return item
    item = TenantSetting(tenant_id=tenant_id, key=key, value=value)
    db.add(item)
    db.flush()
    return item


def delete_setting(db: Session, item: TenantSetting) -> None:
    db.delete(item)
    db.flush()
