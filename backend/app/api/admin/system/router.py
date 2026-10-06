from fastapi import APIRouter

from app.api.admin.system.attachments import router as attachments_router
from app.api.admin.system.departments import router as departments_router
from app.api.admin.system.notifications import router as notifications_router
from app.api.admin.system.permissions import router as permissions_router
from app.api.admin.system.roles import router as roles_router
from app.api.admin.system.settings import router as settings_router
from app.api.admin.system.report_media import router as report_media_router
from app.api.admin.system.report_mode import router as report_mode_router
from app.api.admin.system.users import router as users_router
from app.api.admin.system.codes import router as codes_router
from app.api.admin.system.version import router as version_router


router = APIRouter()
router.include_router(codes_router, prefix="/codes", tags=["admin-system-codes"])
router.include_router(permissions_router, prefix="/permissions", tags=["admin-system-permissions"])
router.include_router(roles_router, prefix="/roles", tags=["admin-system-roles"])
router.include_router(users_router, prefix="/users", tags=["admin-system-users"])
router.include_router(departments_router, prefix="/departments", tags=["admin-system-departments"])
router.include_router(settings_router, prefix="/settings", tags=["admin-system-settings"])
router.include_router(report_media_router, tags=["admin-system-report-media"])
router.include_router(report_mode_router, tags=["admin-system-report-mode"])
router.include_router(notifications_router, prefix="/notifications", tags=["admin-system-notifications"])
router.include_router(attachments_router, prefix="/attachments", tags=["admin-system-attachments"])
router.include_router(version_router, tags=["admin-system-version"])
