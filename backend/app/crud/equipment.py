from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipment import (
    Equipment,
    EquipmentCheck,
    EquipmentMaintenanceLog,
    EquipmentMaintenancePlan,
)


# ==================== 设备 ====================

def get_equipment_by_id(db: Session, tenant_id: int, equipment_id: int) -> Equipment | None:
    return db.scalar(select(Equipment).where(Equipment.tenant_id == tenant_id, Equipment.id == equipment_id))


def get_equipment_by_code(db: Session, tenant_id: int, code: str) -> Equipment | None:
    return db.scalar(select(Equipment).where(Equipment.tenant_id == tenant_id, Equipment.code == code))


def list_equipment(
    db: Session,
    tenant_id: int,
    status: str | None = None,
    offset: int = 0,
    limit: int = 200,
) -> list[Equipment]:
    stmt = select(Equipment).where(Equipment.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Equipment.status == status)
    stmt = stmt.order_by(Equipment.id).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def create_equipment(
    db: Session,
    tenant_id: int,
    code: str,
    name: str,
    model: str | None = None,
    workshop: str | None = None,
    remark: str | None = None,
) -> Equipment:
    item = Equipment(
        tenant_id=tenant_id,
        code=code,
        name=name,
        model=model,
        workshop=workshop,
        remark=remark,
    )
    db.add(item)
    db.flush()
    return item


def update_equipment(
    db: Session,
    item: Equipment,
    code: str | None = None,
    name: str | None = None,
    model: str | None = None,
    workshop: str | None = None,
    status: str | None = None,
    purchase_date: date | None = None,
    last_maintenance_date: date | None = None,
    next_maintenance_date: date | None = None,
    maintenance_interval_days: int | None = None,
    remark: str | None = None,
) -> Equipment:
    if code is not None:
        item.code = code
    if name is not None:
        item.name = name
    if model is not None:
        item.model = model
    if workshop is not None:
        item.workshop = workshop
    if status is not None:
        item.status = status
    if purchase_date is not None:
        item.purchase_date = purchase_date
    if last_maintenance_date is not None:
        item.last_maintenance_date = last_maintenance_date
    if next_maintenance_date is not None:
        item.next_maintenance_date = next_maintenance_date
    if maintenance_interval_days is not None:
        item.maintenance_interval_days = maintenance_interval_days
    if remark is not None:
        item.remark = remark
    db.flush()
    return item


# ==================== 设备巡检 ====================

def create_equipment_check(
    db: Session,
    tenant_id: int,
    equipment_id: int,
    check_type: str,
    result: str,
    description: str | None = None,
    checked_by: int | None = None,
) -> EquipmentCheck:
    ck = EquipmentCheck(
        tenant_id=tenant_id,
        equipment_id=equipment_id,
        check_type=check_type,
        result=result,
        description=description,
        checked_by=checked_by,
    )
    db.add(ck)
    db.flush()
    return ck


def list_equipment_checks(
    db: Session,
    tenant_id: int,
    equipment_id: int,
    limit: int = 50,
) -> list[EquipmentCheck]:
    stmt = (
        select(EquipmentCheck)
        .where(EquipmentCheck.tenant_id == tenant_id, EquipmentCheck.equipment_id == equipment_id)
        .order_by(EquipmentCheck.id.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


# ==================== 设备保养计划 ====================

def get_equipment_maintenance_plans(
    db: Session,
    tenant_id: int,
    plan_id: int,
) -> EquipmentMaintenancePlan | None:
    return db.scalar(
        select(EquipmentMaintenancePlan).where(
            EquipmentMaintenancePlan.tenant_id == tenant_id,
            EquipmentMaintenancePlan.id == plan_id,
        )
    )


def list_equipment_maintenance_plans(
    db: Session,
    tenant_id: int,
    equipment_id: int | None = None,
    offset: int = 0,
    limit: int = 200,
) -> list[EquipmentMaintenancePlan]:
    stmt = select(EquipmentMaintenancePlan).where(EquipmentMaintenancePlan.tenant_id == tenant_id)
    if equipment_id is not None:
        stmt = stmt.where(EquipmentMaintenancePlan.equipment_id == equipment_id)
    stmt = stmt.order_by(EquipmentMaintenancePlan.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def create_equipment_maintenance_plan(
    db: Session,
    tenant_id: int,
    equipment_id: int,
    plan_type: str,
    check_items: str | None = None,
    interval_days: int | None = None,
    responsible_user_id: int | None = None,
    next_date: date | None = None,
    remark: str | None = None,
) -> EquipmentMaintenancePlan:
    item = EquipmentMaintenancePlan(
        tenant_id=tenant_id,
        equipment_id=equipment_id,
        plan_type=plan_type,
        check_items=check_items,
        interval_days=interval_days,
        responsible_user_id=responsible_user_id,
        next_date=next_date,
        remark=remark,
    )
    db.add(item)
    db.flush()
    return item


def update_equipment_maintenance_plan(
    db: Session,
    item: EquipmentMaintenancePlan,
    equipment_id: int | None = None,
    plan_type: str | None = None,
    check_items: str | None = None,
    interval_days: int | None = None,
    responsible_user_id: int | None = None,
    next_date: date | None = None,
    remark: str | None = None,
) -> EquipmentMaintenancePlan:
    if equipment_id is not None:
        item.equipment_id = equipment_id
    if plan_type is not None:
        item.plan_type = plan_type
    if check_items is not None:
        item.check_items = check_items
    if interval_days is not None:
        item.interval_days = interval_days
    if responsible_user_id is not None:
        item.responsible_user_id = responsible_user_id
    if next_date is not None:
        item.next_date = next_date
    if remark is not None:
        item.remark = remark
    db.flush()
    return item


def delete_equipment_maintenance_plan(
    db: Session,
    item: EquipmentMaintenancePlan,
) -> None:
    db.delete(item)
    db.flush()


# ==================== 设备保养日志 ====================

def get_equipment_maintenance_logs(
    db: Session,
    tenant_id: int,
    log_id: int,
) -> EquipmentMaintenanceLog | None:
    return db.scalar(
        select(EquipmentMaintenanceLog).where(
            EquipmentMaintenanceLog.tenant_id == tenant_id,
            EquipmentMaintenanceLog.id == log_id,
        )
    )


def list_equipment_maintenance_logs(
    db: Session,
    tenant_id: int,
    equipment_id: int | None = None,
    offset: int = 0,
    limit: int = 200,
) -> list[EquipmentMaintenanceLog]:
    stmt = select(EquipmentMaintenanceLog).where(EquipmentMaintenanceLog.tenant_id == tenant_id)
    if equipment_id is not None:
        stmt = stmt.where(EquipmentMaintenanceLog.equipment_id == equipment_id)
    stmt = stmt.order_by(EquipmentMaintenanceLog.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def create_equipment_maintenance_log(
    db: Session,
    tenant_id: int,
    equipment_id: int,
    check_result: str,
    plan_id: int | None = None,
    description: str | None = None,
    attachments: str | None = None,
    checked_by: int | None = None,
) -> EquipmentMaintenanceLog:
    item = EquipmentMaintenanceLog(
        tenant_id=tenant_id,
        equipment_id=equipment_id,
        check_result=check_result,
        plan_id=plan_id,
        description=description,
        attachments=attachments,
        checked_by=checked_by,
    )
    db.add(item)
    db.flush()

    today = date.today()
    eq = get_equipment_by_id(db, tenant_id, equipment_id)
    if eq:
        eq.last_maintenance_date = today
        if plan_id:
            plan = get_equipment_maintenance_plans(db, tenant_id, plan_id)
            if plan and plan.interval_days:
                next_d = today + timedelta(days=plan.interval_days)
                plan.next_date = next_d
                eq.next_maintenance_date = next_d
        db.flush()
    return item
