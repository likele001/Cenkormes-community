"""用户微信小程序订阅消息状态表（一次性订阅/长期订阅）"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserWechatSubscription(Base):
    """记录用户对某个订阅消息模板的订阅状态

    微信"一次性订阅"：用户每次授权只能发一次。
    微信"长期订阅"：用户授权后可以发多次（需特殊申请）。

    这里统一记录 + 累计计数 + 最后订阅时间，方便后端判断是否还能发。
    """

    __tablename__ = "user_wechat_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_code: Mapped[str] = mapped_column(String(64), nullable=False)
    template_id: Mapped[str] = mapped_column(String(128), nullable=False)

    # 累计订阅次数
    accept_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # 最后订阅时间
    last_accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # 累计拒绝次数（用于判断用户是否反复拒绝）
    reject_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    last_rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "event_code", "template_id", name="uq_user_event_template"),
        Index("ix_user_wechat_subs_tenant_user", "tenant_id", "user_id"),
    )
