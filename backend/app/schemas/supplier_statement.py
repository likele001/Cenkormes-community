from datetime import date

from pydantic import BaseModel, Field


class SupplierStatementCreateIn(BaseModel):
    supplier_id: int = Field(ge=1)
    code: str | None = Field(default=None, min_length=1, max_length=64)
    period_from: date | None = None
    period_to: date | None = None
