"""社区版 ORM 导出（不含 Pro 专属表）。"""

from app.models.base import Base
from app.models.attachment import Attachment
from app.models.customer import Customer
from app.models.department import Department
from app.models.order import Order, OrderItem
from app.models.permission import Permission
from app.models.process import Process
from app.models.process_route import ProcessRoute, ProcessRouteStep
from app.models.product import Product
from app.models.report import Report, ReportAudit
from app.models.role import Role, role_permissions
from app.models.sku import Sku
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.tenant import Tenant
from app.models.platform_setting import PlatformSetting
from app.models.tenant_setting import TenantSetting
from app.models.user import User, user_roles
from app.models.work_order import WorkOrder
from app.models.work_order_piece import WorkOrderPiece
from app.models.dictionary import DictType, DictItem
from app.models.quality import InspectionTemplate, InspectionTemplateItem, DefectCode, InspectionRecord
from app.models.incoming_batch import IncomingBatch
from app.models.notification import Notification
from app.models.code_sequence import CodeSequence
from app.models.system_version import SystemVersion

__all__ = [
    "Base",
    "Tenant",
    "PlatformSetting",
    "User",
    "Department",
    "Role",
    "Permission",
    "Attachment",
    "Customer",
    "TenantSetting",
    "Product",
    "Sku",
    "Process",
    "ProcessRoute",
    "ProcessRouteStep",
    "Order",
    "OrderItem",
    "WorkOrder",
    "WorkOrderPiece",
    "Task",
    "TaskAssignment",
    "Report",
    "ReportAudit",
    "DictType",
    "DictItem",
    "InspectionTemplate",
    "InspectionTemplateItem",
    "DefectCode",
    "InspectionRecord",
    "IncomingBatch",
    "Notification",
    "CodeSequence",
    "SystemVersion",
    "user_roles",
    "role_permissions",
]
