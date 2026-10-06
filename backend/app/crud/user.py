from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.models.tenant import Tenant
from app.models.saas_package import SaasPackage
from fastapi import HTTPException

# 套餐员工数上限：max_users <= 0 表示不限（与 scripts/seed_saas_packages.py 约定一致）
UNLIMITED_USER_THRESHOLD = 0

def _enforce_user_limit(db: Session, tenant_id: int) -> None:
    """新增员工前校验当前租户套餐的员工数上限；超限则拒绝。客户账号（role=customer）不计入。"""
    tenant = db.get(Tenant, tenant_id)
    if tenant is None or tenant.current_package_id is None:
        return  # 未绑定套餐（兼容老租户）不限制
    pkg = db.get(SaasPackage, tenant.current_package_id)
    if pkg is None or pkg.max_users <= UNLIMITED_USER_THRESHOLD:
        return  # 不限
    active_count = db.scalar(
        select(func.count())
        .select_from(User)
        .where(User.tenant_id == tenant_id, User.is_active.is_(True))
        .where(~User.roles.any(Role.code == "customer"))
    )
    if active_count is None:
        active_count = 0
    if active_count >= pkg.max_users:
        raise HTTPException(
            status_code=400,
            detail=f"已达当前版本员工数上限（{pkg.max_users} 人），请升级套餐或联系商务。",
        )



def get_user_by_id(db: Session, tenant_id: int, user_id: int) -> User | None:
    return db.scalar(select(User).where(User.tenant_id == tenant_id, User.id == user_id))


def get_user_by_tenant_and_username(db: Session, tenant_id: int, username: str) -> User | None:
    return db.scalar(select(User).where(User.tenant_id == tenant_id, User.username == username))


def list_users(
    db: Session,
    tenant_id: int,
    keyword: str | None = None,
    offset: int = 0,
    limit: int = 50,
    include_inactive: bool = False,
) -> list[User]:
    from sqlalchemy import or_

    stmt = select(User).where(User.tenant_id == tenant_id)
    if not include_inactive:
        stmt = stmt.where(User.is_active.is_(True))
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(or_(User.username.like(kw), User.full_name.like(kw)))
    stmt = stmt.order_by(User.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def create_user(db: Session, tenant_id: int, username: str, password: str, full_name: str | None = None, skip_limit: bool = False) -> User:
    if not skip_limit:
        _enforce_user_limit(db, tenant_id)
    user = User(
        tenant_id=tenant_id,
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.flush()
    return user


def set_user_roles(db: Session, user: User, roles: list[Role]) -> User:
    user.roles = roles
    db.flush()
    return user


def update_user(
    db: Session,
    user: User,
    full_name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    is_active: bool | None = None,
    is_superuser: bool | None = None,
    department_id: int | None = None,
    salary_type: str | None = None,
    hourly_rate: Decimal | float | None = None,
) -> User:
    if full_name is not None:
        user.full_name = full_name
    if phone is not None:
        user.phone = phone
    if email is not None:
        user.email = email
    if is_active is not None:
        user.is_active = is_active
    if is_superuser is not None:
        user.is_superuser = is_superuser
    if department_id is not None:
        user.department_id = department_id
    if salary_type is not None:
        user.salary_type = salary_type
    if hourly_rate is not None:
        user.hourly_rate = Decimal(str(hourly_rate))
    db.flush()
    return user


def update_user_profile(db: Session, user: User, **fields: str | None) -> User:
    allowed = {"full_name", "phone", "email"}
    for key, value in fields.items():
        if key in allowed:
            setattr(user, key, value)
    db.flush()
    return user


def change_user_password(db: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise ValueError("原密码不正确")
    set_password(db, user, new_password)


def set_password(db: Session, user: User, password: str) -> User:
    user.password_hash = hash_password(password)
    db.flush()
    return user


def authenticate(db: Session, tenant_id: int, username: str, password: str) -> User | None:
    user = get_user_by_tenant_and_username(db, tenant_id, username)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
