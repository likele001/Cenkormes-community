from fastapi import APIRouter

from app.api.h5.tasks import router as h5_tasks_router
from app.api.h5.notifications import router as h5_notifications_router
from app.api.h5.settings_media import router as h5_settings_media_router


router = APIRouter()
router.include_router(h5_settings_media_router)
router.include_router(h5_tasks_router)
router.include_router(h5_notifications_router)
