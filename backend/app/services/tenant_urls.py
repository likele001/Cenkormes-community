"""租户对外入口 URL（依赖平台设置中的 admin / h5 站点地址）"""

from sqlalchemy.orm import Session

from app.crud.platform_setting import get_setting


def _base(db: Session, key: str) -> str:
    return (get_setting(db, key) or "").strip().rstrip("/")


def build_tenant_entry_urls(db: Session, tenant_code: str) -> dict[str, str]:
    code = tenant_code.strip().upper()
    admin_base = _base(db, "admin_site_url")
    h5_base = _base(db, "h5_site_url")

    admin_login = f"{admin_base}/t/{code}/login" if admin_base else f"/t/{code}/login"
    h5_login = f"{h5_base}/#/t/{code}/login" if h5_base else f"/#/t/{code}/login"
    customer = f"{h5_base}/#/t/{code}/customer/order" if h5_base else f"/#/t/{code}/customer/order"
    join = f"{admin_base}/t/{code}/join" if admin_base else f"/t/{code}/join"

    return {
        "admin": admin_login,
        "h5": h5_login,
        "customer": customer,
        "join": join,
    }
