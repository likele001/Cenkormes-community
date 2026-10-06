from app.core.db import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.customer import Customer
db = SessionLocal()
t = db.query(Tenant).filter(Tenant.code == 'DEMO_FLOW').first()
print('tenant', t.id if t else None, t.name if t else None)
users = db.query(User).filter(User.tenant_id == t.id).all()
for u in users[:5]:
    print('  user', u.id, u.username, u.full_name)
cs = db.query(Customer).filter(Customer.tenant_id == t.id).all()
print('customers count:', len(cs))
for c in cs[:5]:
    print('  cust', c.id, c.code, c.name)