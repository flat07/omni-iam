from sqlalchemy import Column, String
from app.db.base import Base
from app.models.base import BaseMixin, VendorMixin


class ApiKey(Base, BaseMixin, VendorMixin):
    __tablename__ = "api_keys"

    name = Column(String)
    key_hash = Column(String)