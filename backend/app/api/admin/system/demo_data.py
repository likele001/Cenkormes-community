"""演示数据管理 API：一键安装/卸载/查看状态。

- GET  /admin/system/demo-data/status    查看演示数据安装状态
- POST /admin/system/demo-data/install   一键安装（幂等）
- POST /admin/system/demo-data/uninstall 一键卸载（幂等，只删演示数据）

权限：setting.manage（系统设置）
"""

import time

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.admin.system.common import write_op_log
from app.core.deps import get_current_user, get_db, require_permissions
from app.core.response import ok
from app.models.user import User


router = APIRouter(dependencies=[Depends(require_permissions(["setting.manage"]))])


def _run_install(db: Session, tenant_id: int) -> dict:
    """执行全部演示数据安装，返回各步骤结果。"""
    from scripts.seed_all_demo import INSTALL_STEPS

    results = {}
    for name, fn in INSTALL_STEPS:
        try:
            r = fn(db)
            results[name] = {"ok": True, **(r or {})}
        except Exception as e:  # noqa: BLE001
            db.rollback()
            results[name] = {"ok": False, "error": str(e)}
    return results


def _run_uninstall(tenant_id: int) -> dict:
    """执行演示数据卸载（只删演示租户数据，保留真实数据）。"""
    from scripts.unseed_demo import uninstall_all

    return uninstall_all(tenant_id)


@router.get("/status")
def status_api(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from scripts.seed_all_demo import status as demo_status

    st = demo_status(db)
    # 附带当前租户信息
    st["tenant_id"] = user.tenant_id
    return ok(st)


@router.post("/install")
def install_api(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    start = time.time()
    results = _run_install(db, user.tenant_id)
    elapsed = round(time.time() - start, 1)

    ok_count = sum(1 for r in results.values() if r.get("ok"))
    fail_count = len(results) - ok_count

    write_op_log(
        request,
        db,
        user.id,
        "demo_data_install",
        f"安装演示数据：成功 {ok_count}/{len(results)} 步，耗时 {elapsed}s",
    )
    return ok(
        {
            "installed": True,
            "results": results,
            "ok_count": ok_count,
            "fail_count": fail_count,
            "elapsed": elapsed,
        }
    )


@router.post("/uninstall")
def uninstall_api(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    start = time.time()
    result = _run_uninstall(user.tenant_id)
    elapsed = round(time.time() - start, 1)

    write_op_log(
        request,
        db,
        user.id,
        "demo_data_uninstall",
        f"卸载演示数据：{result.get('message', '完成')}，耗时 {elapsed}s",
    )
    return ok({**result, "elapsed": elapsed})
