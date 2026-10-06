import datetime
from sqlalchemy import text
from app.core.db import SessionLocal

tbl = {
    "feishu": "feishu_push_logs",
    "wecom": "wecom_push_logs",
    "dingtalk": "dingtalk_push_logs",
}
cutoff5 = (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).isoformat()
cutoff1h = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat()

db = SessionLocal()
try:
    for ch, t in tbl.items():
        try:
            st = dict(db.execute(text(f"SELECT status, COUNT(*) FROM {t} WHERE DATE(created_at)=DATE(UTC_TIMESTAMP()) GROUP BY status")).all())
            stuck = db.execute(text(f"SELECT COUNT(*) FROM {t} WHERE status='pending' AND created_at < :c").params(c=cutoff5)).scalar()
            stuck_send = db.execute(text(f"SELECT COUNT(*) FROM {t} WHERE status='sending' AND created_at < :c").params(c=cutoff1h)).scalar()
            print(f"[{ch}] 今日状态={st} | pending卡>5min={stuck} | sending卡>1h={stuck_send}")
        except Exception as e:
            print(f"[{ch}] ERR {e}")
finally:
    db.close()
print("DONE")