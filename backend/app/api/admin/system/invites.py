from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.crud.tenant import get_tenant_by_id
from app.crud.tenant_invite import create_invite, list_invites
from app.schemas.platform import TenantInviteCreateIn
from app.services.tenant_urls import build_tenant_entry_urls


router = APIRouter(dependencies=[Depends(require_permissions(["user.manage"]))])


@router.get("")
def list_invites_api(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    tenant = get_tenant_by_id(db, user.tenant_id)
    items = list_invites(db, user.tenant_id)
    urls = build_tenant_entry_urls(db, tenant.code) if tenant else {}
    return ok(
        {
            "tenant_code": tenant.code if tenant else "",
            "entry_urls": urls,
            "items": [
                {
                    "id": i.id,
                    "token": i.token,
                    "role_code": i.role_code,
                    "max_uses": i.max_uses,
                    "used_count": i.used_count,
                    "expires_at": i.expires_at,
                    "join_url": f"{urls.get('join', '/join')}?invite={i.token}",
                    "created_at": i.created_at,
                }
                for i in items
            ],
        }
    )


@router.post("")
def create_invite_api(
    payload: TenantInviteCreateIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    tenant = get_tenant_by_id(db, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=400, detail="租户不存在")
    expires_at = None
    if payload.expires_days:
        expires_at = datetime.now() + timedelta(days=payload.expires_days)
    inv = create_invite(
        db,
        tenant_id=user.tenant_id,
        role_code=payload.role_code,
        max_uses=payload.max_uses,
        expires_at=expires_at,
        created_by=user.id,
    )
    db.commit()
    urls = build_tenant_entry_urls(db, tenant.code)
    return ok(
        {
            "id": inv.id,
            "token": inv.token,
            "join_url": f"{urls['join']}?invite={inv.token}",
        }
    )
