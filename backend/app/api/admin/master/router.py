from fastapi import APIRouter

from app.api.admin.master.products import router as products_router
from app.api.admin.master.process_routes import router as process_routes_router
from app.api.admin.master.processes import router as processes_router
from app.api.admin.master.skus import router as skus_router


router = APIRouter()
router.include_router(products_router, prefix="/products", tags=["admin-master-products"])
router.include_router(skus_router, prefix="/skus", tags=["admin-master-skus"])
router.include_router(processes_router, prefix="/processes", tags=["admin-master-processes"])
router.include_router(process_routes_router, prefix="/process-routes", tags=["admin-master-process-routes"])
