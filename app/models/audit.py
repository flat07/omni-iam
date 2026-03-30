from sqlalchemy import Column, String, JSON
from app.models.base import BaseMixin, VendorMixin
from app.db.base import Base


class AuditLog(Base, BaseMixin, VendorMixin):
    __tablename__ = "audit_logs"

    action = Column(String)
    actor_user_id = Column(String)
    target_type = Column(String)
    target_id = Column(String)
    meta = Column(JSON)