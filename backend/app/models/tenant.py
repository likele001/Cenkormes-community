from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_package_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("saas_packages.id", ondelete="SET NULL"), nullable=True
    )
    custom_domain: Mapped[str | None] = mapped_column(String(64), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    industry_codes: Mapped[str | None] = mapped_column(String(256), nullable=True, default=None, comment="comma-separated industry codes")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    users = relationship("User", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")
