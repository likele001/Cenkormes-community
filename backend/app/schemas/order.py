from datetime import date, datetime

from pydantic import BaseModel, Field


class CustomerOrderItemIn(BaseModel):
    sku_id: int = Field(ge=1)
    qty: int = Field(ge=1)
    remark: str | None = None


class CustomerPlaceOrderIn(BaseModel):
    items: list[CustomerOrderItemIn] = Field(min_length=1)
    due_date: date | None = None
    remark: str | None = None
    submit: bool = True


class OrderItemCreateIn(BaseModel):
    line_no: int = Field(ge=1)
    sku_id: int = Field(ge=1)
    qty: int = Field(ge=1)
    remark: str | None = None


class OrderCreateIn(BaseModel):
    customer_id: int = Field(ge=1)
    code: str | None = Field(default=None, max_length=64)
    due_date: date | None = None
    remark: str | None = None
    opportunity_id: int | None = Field(default=None, ge=1)
    items: list[OrderItemCreateIn] = Field(min_length=1)


class OrderItemUpsertIn(BaseModel):
    """更新订单明细：id 为空表示新增行（仅已确认且未整单锁计划时）"""

    id: int | None = Field(default=None, ge=1)
    line_no: int = Field(ge=1)
    sku_id: int = Field(ge=1)
    qty: int = Field(ge=1)
    remark: str | None = None


class OrderUpdateIn(BaseModel):
    customer_id: int | None = Field(default=None, ge=1)
    code: str | None = Field(default=None, min_length=1, max_length=64)
    due_date: date | None = None
    remark: str | None = None
    status: str | None = Field(default=None, max_length=32)
    items: list[OrderItemUpsertIn] | None = None


class OrderItemOut(BaseModel):
    id: int
    tenant_id: int
    order_id: int
    line_no: int
    sku_id: int
    qty: int
    remark: str | None
    created_at: datetime
    updated_at: datetime


class OrderOut(BaseModel):
    id: int
    tenant_id: int
    customer_id: int
    opportunity_id: int | None = None
    opportunity_code: str | None = None
    code: str
    status: str
    due_date: date | None
    remark: str | None
    confirmed_at: datetime | None
    confirmed_by: int | None
    created_at: datetime
    updated_at: datetime
