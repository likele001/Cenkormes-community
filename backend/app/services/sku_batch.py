"""社区版：型号批量辅助（不含工价批量写入，完整版在 Pro）。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.process import list_processes
from app.crud.process_route import get_default_route_for_product
from app.models.process import Process
from app.models.sku import Sku
from app.services.display_label import process_display_name


def list_active_sku_names_for_product(db: Session, tenant_id: int, product_id: int) -> list[str]:
    rows = db.scalars(
        select(Sku.name).where(
            Sku.tenant_id == tenant_id,
            Sku.product_id == product_id,
            Sku.is_active.is_(True),
        )
    ).all()
    names: list[str] = []
    seen: set[str] = set()
    for raw in rows:
        name = str(raw).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def get_product_route_processes(
    db: Session,
    tenant_id: int,
    product_id: int,
) -> tuple[list[Process], str | None, str]:
    try:
        route = get_default_route_for_product(db, tenant_id, product_id)
        proc_ids = [s.process_id for s in sorted(route.steps, key=lambda x: x.seq)]
        if proc_ids:
            proc_map = {
                p.id: p
                for p in db.scalars(
                    select(Process).where(Process.tenant_id == tenant_id, Process.id.in_(proc_ids))
                ).all()
            }
            process_rows = [proc_map[pid] for pid in proc_ids if pid in proc_map]
            if process_rows:
                return process_rows, route.name, "default_route"
    except ValueError:
        pass
    process_rows = list_processes(db, tenant_id=tenant_id, offset=0, limit=500, include_inactive=False)
    return process_rows, None, "all"


def process_rows_to_dict(process_rows: list[Process]) -> list[dict]:
    return [
        {
            "process_id": p.id,
            "process_code": p.code,
            "process_name": p.name,
            "process_display_name": process_display_name(p.name, p.code),
        }
        for p in process_rows
    ]
