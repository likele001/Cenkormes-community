from fastapi import APIRouter, Depends

from app.core.deps import require_admin_portal_user

from app.api.admin.master.router import router as admin_master_router
from app.api.admin.production.router import router as admin_production_router
from app.api.admin.system.router import router as admin_system_router
from app.api.admin.dictionary.router import router as admin_dictionary_router
from app.api.h5.router import router as h5_router
from app.api.v1.auth import router as auth_router
from app.api.v1.captcha import router as captcha_router
from app.api.v1.files import router as files_router


api_router = APIRouter()
_admin_deps = [Depends(require_admin_portal_user)]
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(captcha_router, prefix="/auth/captcha", tags=["auth-captcha"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(admin_master_router, prefix="/admin/master", tags=["admin-master"], dependencies=_admin_deps)
api_router.include_router(admin_production_router, prefix="/admin/production", tags=["admin-production"], dependencies=_admin_deps)
api_router.include_router(admin_system_router, prefix="/admin/system", tags=["admin-system"], dependencies=_admin_deps)
api_router.include_router(admin_dictionary_router, prefix="/admin/dictionary", tags=["admin-dictionary"], dependencies=_admin_deps)
api_router.include_router(h5_router, prefix="/h5", tags=["h5"])
