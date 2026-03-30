from sqlalchemy import Boolean, Column, String, JSON
from app.db.base import Base
from app.models.base import BaseMixin, VendorMixin


class Policy(Base, BaseMixin, VendorMixin):
    __tablename__ = "policies"

    name = Column(String)

    effect = Column(String)  # allow / deny

    action = Column(String)
    resource = Column(String)

    conditions = Column(JSON, nullable=True)

    enabled = Column(Boolean, default=True)


# {
#  "name": "housekeeping_room_update",
#  "effect": "allow",
#  "action": "room:update",
#  "resource": "room",
#  "conditions": {
#    "department": "housekeeping",
#    "location": "tower-a"
#  }
# }