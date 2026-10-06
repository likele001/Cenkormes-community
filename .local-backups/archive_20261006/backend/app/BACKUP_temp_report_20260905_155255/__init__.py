from app.models.base import Base
from app.models.attachment import Attachment
from app.models.customer import Customer
from app.models.customer_product import CustomerProduct
from app.models.department import Department
from app.models.operation_log import OperationLog
from app.models.order import Order, OrderItem
from app.models.permission import Permission
from app.models.process import Process
from app.models.process_skill import ProcessSkillLink
from app.models.process_price import ProcessPrice
from app.models.process_route import ProcessRoute, ProcessRouteStep
from app.models.product import Product
from app.models.report import Report, ReportAudit
from app.models.report_unit import ReportUnit, ReportUnitAudit
from app.models.role import Role, role_permissions
from app.models.salary import SalaryItem
from app.models.sku import Sku
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.tenant import Tenant
from app.models.platform_setting import PlatformSetting
from app.models.platform_user import PlatformUser
from app.models.saas_package import SaasPackage
from app.models.subscription_order import SubscriptionOrder, TenantSubscription
from app.models.tenant_invite import TenantInvite
from app.models.trace import TraceCode
from app.models.finance import Statement, StatementItem
from app.models.finance_ledger import FinanceLedger
from app.models.shipment import Shipment, ShipmentItem, AfterSale
from app.models.production_plan import ProductionPlan
from app.models.equipment import Equipment, EquipmentCheck, EquipmentMaintenanceLog, EquipmentMaintenancePlan
from app.models.dictionary import DictType, DictItem
from app.models.salary_allowance import SalaryAllowance
from app.models.salary_slip import SalarySlip
from app.models.material import Supplier, Material, MaterialBom, MaterialBomItem
from app.models.warehouse import Warehouse, Stock, StockLog
from app.models.quality import InspectionTemplate, InspectionTemplateItem, DefectCode, InspectionRecord
from app.models.incoming_batch import IncomingBatch
from app.models.tenant_setting import TenantSetting
from app.models.user import User, user_roles
from app.models.work_order import WorkOrder
from app.models.work_order_piece import WorkOrderPiece
from app.models.purchase import PurchaseOrder, PurchaseOrderItem
from app.models.plan_purchase_link import PlanPurchaseLink
from app.models.supplier_statement import SupplierStatement, SupplierStatementItem
from app.models.crm import CustomerContact, CrmOpportunity, CrmOpportunityActivity, CustomerTag, CustomerTagLink
from app.models.export_job import ExportJob
from app.models.print_template import PrintTemplate
from app.models.notification import Notification
from app.models.attendance import AttendanceRecord
from app.models.employee_skill import Skill, UserSkillLink
from app.models.production_calendar import ProductionCalendarDay
from app.models.code_sequence import CodeSequence
from app.models.ai import AiAlertEvent, AiConversation, AiMessage, PlatformAiGateway, PlatformAiModel, PlatformAiProfile
from app.models.ai_employee import AiEmployee, AiEmployeeConversation, AiEmployeeLog, AiEmployeeMessage
from app.models.automation_log import AutomationLog
from app.models.mrp import MrpRun, MrpDemand
from app.models.quotation import Quotation, QuotationItem
from app.models.subcontract import SubcontractOrder, SubcontractOrderItem, SubcontractSendLog, SubcontractReceiveLog
from app.models.shift import Shift, ShiftSchedule
from app.models.system_version import SystemVersion

__all__ = [
    "Base",
    "Tenant",
    "PlatformSetting",
    "PlatformUser",
    "SaasPackage",
    "SubscriptionOrder",
    "TenantSubscription",
    "TenantInvite",
    "User",
    "Department",
    "Role",
    "Permission",
    "Attachment",
    "Customer",
    "CustomerProduct",
    "TenantSetting",
    "OperationLog",
    "Product",
    "Sku",
    "Process",
    "ProcessSkillLink",
    "ProcessRoute",
    "ProcessRouteStep",
    "ProcessPrice",
    "Order",
    "OrderItem",
    "WorkOrder",
    "WorkOrderPiece",
    "Task",
    "Report",
    "ReportAudit",
    "ReportUnit",
    "ReportUnitAudit",
    "SalaryItem",
    "TraceCode",
    "Warehouse",
    "Stock",
    "StockLog",
    "Statement",
    "StatementItem",
    "FinanceLedger",
    "Shipment",
    "AfterSale",
    "ProductionPlan",
    "Equipment",
    "EquipmentCheck",
    "EquipmentMaintenancePlan",
    "EquipmentMaintenanceLog",
    "DictType",
    "DictItem",
    "SalaryAllowance",
    "SalarySlip",
    "Supplier",
    "Material",
    "MaterialBom",
    "MaterialBomItem",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "PlanPurchaseLink",
    "SupplierStatement",
    "SupplierStatementItem",
    "CustomerContact",
    "CrmOpportunity",
    "CrmOpportunityActivity",
    "CustomerTag",
    "CustomerTagLink",
    "ExportJob",
    "PrintTemplate",
    "Notification",
    "AttendanceRecord",
    "ProductionCalendarDay",
    "Skill",
    "UserSkillLink",
    "user_roles",
    "role_permissions",
    "PlatformAiProfile",
    "AutomationLog",
    "ShipmentItem",
    "IncomingBatch",
    "CodeSequence",
    "Shift",
    "ShiftSchedule",
    "SystemVersion",
    "MrpRun",
    "MrpDemand",
    "Quotation",
    "QuotationItem",
    "SubcontractOrder",
    "SubcontractOrderItem",
    "SubcontractSendLog",
    "SubcontractReceiveLog",
    "AiEmployee",
    "AiEmployeeConversation",
    "AiEmployeeMessage",
    "AiEmployeeLog",
    "Invoice",
    "InvoiceItem",
    "AccountSubject",
    "Voucher",
    "VoucherEntry",
    "PeriodClosing",
    "WorkOrderCost",
    "WorkOrderCostItem",
    "FixedAsset",
    "DepreciationRecord",
    "AssetCheck",
    "AssetCheckItem",
]

from app.models.material_issue import MaterialIssue, MaterialIssueItem, MaterialReturn, MaterialReturnItem

from app.models.warehouse_entry import WarehouseEntry, WarehouseEntryItem
from app.models.erp_invoice import Invoice, InvoiceItem
from app.models.erp_ledger import AccountSubject, Voucher, VoucherEntry, PeriodClosing
from app.models.erp_cost import WorkOrderCost, WorkOrderCostItem
from app.models.erp_asset import FixedAsset, DepreciationRecord, AssetCheck, AssetCheckItem
