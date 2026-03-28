# app/models/base.py
from sqlalchemy import Column, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from datetime import datetime, timezone
import uuid


class BaseMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)


class VendorMixin:
    @declared_attr
    def vendor_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False, index=True)