from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_permissions, get_current_user, get_db
from app.core.portal_access import ADMIN_PORTAL_HEADER, ADMIN_PORTAL_VALUE, assert_admin_portal_user, is_h5_portal_user
from app.core.response import ok
from app.core.security import create_access_token, token_expire_minutes
from app.crud.user import authenticate, change_user_password, update_user_profile
from app.schemas.auth import LoginIn
from app.schemas.profile import ChangePasswordIn, ProfileUpdateIn
from app.services.login_captcha import assert_login_captcha
from app.services.profile import profile_fields_to_update


router = APIRouter()


@router.post("/login")
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    assert_login_captcha(db, payload.captcha_id, payload.captcha_code)
    from app.crud.tenant import get_tenant_by_code

    tenant = get_tenant_by_code(db, payload.tenant_code)
    if not tenant:
        raise HTTPException(status_code=400, detail="租户不存在")
    user = authenticate(db, tenant.id, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")
    if request.headers.get(ADMIN_PORTAL_HEADER) == ADMIN_PORTAL_VALUE and is_h5_portal_user(user):
        assert_admin_portal_user(user)
    minutes = token_expire_minutes(payload.remember_me)
    token = create_access_token(
        {"sub": str(user.id), "tenant_id": tenant.id, "username": user.username},
        expires_minutes=minutes,
    )
    return ok(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": minutes * 60,
            "remember_me": payload.remember_me,
        }
    )


def _user_me_out(user, roles: list[str], codes: list[str], tenant=None) -> dict:
    tenant_code = tenant.code if tenant else ""
    tenant_name = tenant.name if tenant else None
    logo_url = tenant.logo_url if tenant else None
    return {
        "id": user.id,
        "tenant_id": user.tenant_id,
        "tenant_code": tenant_code,
        "tenant_name": tenant_name,
        "logo_url": logo_url,
        "username": user.username,
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "roles": roles,
        "permissions": codes,
    }


@router.get("/me")
def me(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    codes: list[str] = Depends(get_current_permissions),
):
    if request.headers.get(ADMIN_PORTAL_HEADER) == ADMIN_PORTAL_VALUE:
        assert_admin_portal_user(user)
    from app.models.tenant import Tenant

    tenant = db.get(Tenant, user.tenant_id)
    roles = sorted({r.code for r in user.roles})
    return ok(_user_me_out(user, roles, codes, tenant))


@router.put("/profile")
def update_profile(
    payload: ProfileUpdateIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    fields = profile_fields_to_update(payload)
    if fields:
        update_user_profile(db, user, **fields)
        db.commit()
    return ok({"id": user.id, "full_name": user.full_name, "phone": user.phone, "email": user.email})


@router.post("/change-password")
def change_password(
    payload: ChangePasswordIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        change_user_password(db, user, payload.old_password, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    return ok({"changed": True})
