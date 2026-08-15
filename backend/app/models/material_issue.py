from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MaterialIssue(Base):
    """领料单"""
    __tablename__ = "material_issues"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_material_issues_tenant_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="draft", index=True)  # draft/issued/cancelled
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    work_order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True)

    total_qty: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")

    issued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    issue_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    items = relationship("MaterialIssueItem", back_populates="issue", cascade="all, delete-orphan")
    warehouse = relationship("Warehouse")
    work_order = relationship("WorkOrder")


class MaterialIssueItem(Base):
    """领料明细"""
    __tablename__ = "material_issue_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_issues.id", ondelete="CASCADE"), nullable=False, index=True)

    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False, index=True)
    sku_id: Mapped[int] = mapped_column(Integer, ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False, index=True)

    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False, server_default="0")
    cost_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")

    issue = relationship("MaterialIssue", back_populates="items")
    material = relationship("Material")
    sku = relationship("Sku")


class MaterialReturn(Base):
    """退料单"""
    __tablename__ = "material_returns"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_material_returns_tenant_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="draft", index=True)  # draft/returned/cancelled
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    work_order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    issue_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("material_issues.id", ondelete="SET NULL"), nullable=True, index=True)

    total_qty: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")

    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    return_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    items = relationship("MaterialReturnItem", back_populates="return_", cascade="all, delete-orphan")
    warehouse = relationship("Warehouse")
    work_order = relationship("WorkOrder")
    issue = relationship("MaterialIssue")


class MaterialReturnItem(Base):
    """退料明细"""
    __tablename__ = "material_return_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    return_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_returns.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_item_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("material_issue_items.id", ondelete="SET NULL"), nullable=True)

    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False, index=True)
    sku_id: Mapped[int] = mapped_column(Integer, ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False, index=True)

    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False, server_default="0")
    cost_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")

    return_ = relationship("MaterialReturn", back_populates="items")
    material = relationship("Material")
    sku = relationship("Sku")
