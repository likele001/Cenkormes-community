"""附件引用检查与删除（社区版）"""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.models.report import Report


def _id_in_csv_column(col, attachment_id: int):
    aid = str(attachment_id)
    return or_(
        col == aid,
        col.like(f"{aid},%"),
        col.like(f"%,{aid},%"),
        col.like(f"%,{aid}"),
    )


def attachment_is_referenced(db: Session, *, tenant_id: int, attachment_id: int) -> bool:
    return bool(
        db.scalar(
            select(Report.id).where(
                Report.tenant_id == tenant_id,
                _id_in_csv_column(Report.attachment_ids, attachment_id),
            ).limit(1)
        )
    )


def delete_attachment_record(db: Session, att: Attachment) -> None:
    db.delete(att)
    db.flush()
