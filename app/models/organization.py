# app/models/organization.py
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.base import BaseMixin, VendorMixin

class Vendor(Base, BaseMixin):
    __tablename__ = "vendors"

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)


class Location(Base, BaseMixin, VendorMixin):
    __tablename__ = "locations"

    name = Column(String, nullable=False)


class Department(Base, BaseMixin, VendorMixin):
    __tablename__ = "departments"

    name = Column(String, nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"))